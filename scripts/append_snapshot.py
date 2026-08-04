#!/usr/bin/env python
"""기존 스냅샷에 신규 논문을 덧붙여 새 스냅샷을 만든다.

`scripts/harvest_arxiv.py` 가 만든 신규 논문 DB를 받아, 기존 스냅샷의 4파일을
**읽기만 하고** 새 디렉터리에 확장본 4파일을 쓴다. 기존 스냅샷은 그대로 남으므로
같은 토픽을 두 스냅샷에서 돌려 "DB 최신화의 효과"를 비교할 수 있다.

## 왜 append 가 안전한가

인덱스가 `IndexFlatL2` 라 학습된 양자화기가 없다. `index.add()` 는 기존 벡터의
행 번호(0~N-1)를 건드리지 않고 뒤에만 붙인다. 따라서 **옛 스냅샷은 새 스냅샷의
prefix** 가 되고, 기존 논문의 검색 결과는 신규분이 끼어드는 것 말고는 바뀌지 않는다.

임베딩 절차가 원본과 동일함은 실측으로 확인했다 — DB 수록 논문을 현 환경에서
다시 임베딩하면 저장 벡터와 `cos 1.000000 / L2 0.0000` 으로 일치한다.

## 정합성 — 이게 이 스크립트의 핵심이다

TinyDB 레코드 순서 == FAISS 행 번호 == id→index 매핑, 셋이 같아야 한다.
어긋나도 **에러가 나지 않고 조용히 엉뚱한 논문을 반환**하므로, 시작 전에 기존
스냅샷의 정합을 확인하고 끝난 뒤 결과를 다시 확인한다.

사용법:
    # 정합성만 확인 (임베딩 없음, 수 분)
    python scripts/append_snapshot.py --base ./database \\
        --new ./database_2026-08/arxiv_paper_db.json --out ./database_2026-08 --check-only

    # 실제 생성
    python scripts/append_snapshot.py --base ./database \\
        --new ./database_2026-08/arxiv_paper_db.json --out ./database_2026-08
"""

import argparse
import hashlib
import json
import os
import shutil
import sys

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import trange

TITLE_BIN = 'faiss_paper_title_embeddings.bin'
ABS_BIN = 'faiss_paper_abs_embeddings.bin'
DB_JSON = 'arxiv_paper_db.json'
MAP_JSON = 'arxivid_to_index_abs.json'


def get_embeddings(model, texts, batch_size):
    """nomic 은 'search_document: ' 프리픽스로 색인한다 (build_index.py 와 동일).

    src/database.py 의 get_embeddings() 가 검색 시 'search_query: ' 를 붙인다.
    이 비대칭이 nomic 의 규약이므로 어느 쪽도 바꾸면 안 된다.
    """
    out = []
    for i in trange(0, len(texts), batch_size):
        batch = ['search_document: ' + t for t in texts[i:i + batch_size]]
        out.append(model.encode(batch, show_progress_bar=False))
    return np.concatenate(out, axis=0).astype('float32')


def md5(path, chunk=1 << 24):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_table(path):
    with open(path) as f:
        return json.load(f)['cs_paper_info']


def check_consistency(label, table_list, mapping, ntotal_title, ntotal_abs):
    """레코드 순서 / FAISS 행 / 매핑 셋이 일치하는지 본다."""
    n = len(table_list)
    problems = []
    if ntotal_title != n:
        problems.append(f'title FAISS {ntotal_title:,} != 레코드 {n:,}')
    if ntotal_abs != n:
        problems.append(f'abs FAISS {ntotal_abs:,} != 레코드 {n:,}')
    if len(mapping) != n:
        problems.append(f'id 매핑 {len(mapping):,} != 레코드 {n:,}')

    # 매핑이 '리스트상의 위치'를 가리키는지 표본으로 확인한다.
    probe = [0, n // 3, n // 2, n - 1] if n else []
    for i in probe:
        rid = table_list[i]['id']
        if mapping.get(rid) != i:
            problems.append(f'매핑 어긋남: 위치 {i} 의 {rid} -> {mapping.get(rid)}')

    print(f'  [{label}] 레코드 {n:,} / title {ntotal_title:,} / abs {ntotal_abs:,} / 매핑 {len(mapping):,}')
    for p in problems:
        print(f'    !! {p}')
    return not problems


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='./database', help='기존 스냅샷 디렉터리 (읽기 전용)')
    ap.add_argument('--new', required=True, help='신규 논문 arxiv_paper_db.json')
    ap.add_argument('--out', required=True, help='새 스냅샷을 쓸 디렉터리')
    ap.add_argument('--embedding-model', default='nomic-ai/nomic-embed-text-v1')
    ap.add_argument('--batch-size', type=int, default=128)
    ap.add_argument('--device', default=None)
    ap.add_argument('--check-only', action='store_true',
                    help='정합성만 확인하고 임베딩·기록은 하지 않는다')
    args = ap.parse_args()

    if os.path.abspath(args.base) == os.path.abspath(args.out):
        print('--base 와 --out 이 같습니다. 기존 스냅샷을 덮어쓸 수 없습니다.', file=sys.stderr)
        return 1

    base_db = os.path.join(args.base, DB_JSON)
    print(f'[1/6] 기존 스냅샷 로딩 {args.base}', flush=True)
    base_table = load_table(base_db)
    base_list = list(base_table.values())
    with open(os.path.join(args.base, MAP_JSON)) as f:
        base_map = {k: int(v) for k, v in json.load(f).items()}
    title_index = faiss.read_index(os.path.join(args.base, TITLE_BIN))
    abs_index = faiss.read_index(os.path.join(args.base, ABS_BIN))

    if not check_consistency('기존', base_list, base_map,
                             title_index.ntotal, abs_index.ntotal):
        print('\n기존 스냅샷이 이미 어긋나 있습니다. append 하면 안 됩니다.', file=sys.stderr)
        return 1

    print(f'\n[2/6] 신규 논문 로딩 {args.new}', flush=True)
    new_list = list(load_table(args.new).values())
    print(f'  {len(new_list):,}편')

    # 중복 차단. harvest 의 --exclude-db 로 이미 걸렀어야 하지만, 여기서 다시 본다.
    # 버전 접미사가 달라도 같은 논문이므로 base id 로 비교한다.
    base_ids = {r['id'] for r in base_list}
    base_stems = {i.split('v')[0] for i in base_ids}
    fresh, dup, seen = [], 0, set()
    for r in new_list:
        stem = r['id'].split('v')[0]
        if stem in base_stems or stem in seen:
            dup += 1
            continue
        seen.add(stem)
        fresh.append(r)
    if dup:
        print(f'  기존 스냅샷과 겹치거나 중복이라 제외: {dup:,}편')
    print(f'  실제 추가 대상: {len(fresh):,}편')
    if not fresh:
        print('추가할 논문이 없습니다.', file=sys.stderr)
        return 1

    missing = [f for f in ('id', 'title', 'abs', 'date', 'url', 'cat', 'authors')
               if any(f not in r for r in fresh[:1000])]
    if missing:
        print(f'  !! 신규 레코드에 없는 필드: {missing}', file=sys.stderr)
        return 1

    n_base, n_new = len(base_list), len(fresh)
    print(f'\n  {n_base:,} + {n_new:,} = {n_base + n_new:,}편')
    if args.check_only:
        print('\n--check-only 이므로 여기서 종료합니다.')
        return 0

    device = args.device or ('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'\n[3/6] 임베딩 모델 로딩 (device={device})', flush=True)
    model = SentenceTransformer(args.embedding_model, trust_remote_code=True)
    model.to(torch.device(device))

    print('\n[4/6] 신규 title 임베딩', flush=True)
    title_emb = get_embeddings(model, [r['title'] for r in fresh], args.batch_size)
    print('신규 abstract 임베딩', flush=True)
    abs_emb = get_embeddings(model, [r['abs'] for r in fresh], args.batch_size)

    # IndexFlatL2 는 학습이 필요 없고 기존 행 번호를 보존한다.
    title_index.add(title_emb)
    abs_index.add(abs_emb)

    print(f'\n[5/6] 병합 후 기록 -> {args.out}', flush=True)
    os.makedirs(args.out, exist_ok=True)

    merged_list = base_list + fresh
    merged_table = {str(i): r for i, r in enumerate(merged_list)}
    merged_map = dict(base_map)
    for i, r in enumerate(fresh, start=n_base):
        merged_map[r['id']] = i

    if not check_consistency('병합', merged_list, merged_map,
                             title_index.ntotal, abs_index.ntotal):
        print('\n병합 결과가 어긋납니다. 기록하지 않고 중단합니다.', file=sys.stderr)
        return 1

    # 신규 DB json 이 --out 안에 있으면 덮어쓰기 전에 치운다.
    out_db = os.path.join(args.out, DB_JSON)
    if os.path.abspath(args.new) == os.path.abspath(out_db):
        shutil.move(args.new, out_db + '.new-only')
        print(f'  신규분 원본을 {out_db}.new-only 로 옮김')

    with open(out_db, 'w') as f:
        json.dump({'cs_paper_info': merged_table}, f, ensure_ascii=False)
    with open(os.path.join(args.out, MAP_JSON), 'w') as f:
        json.dump(merged_map, f)
    faiss.write_index(title_index, os.path.join(args.out, TITLE_BIN))
    faiss.write_index(abs_index, os.path.join(args.out, ABS_BIN))

    print('\n[6/6] 지문 (REPRODUCTION.md §3 에 기록할 값)', flush=True)
    newest = max(r['date'] for r in merged_list if r.get('date'))
    print(f'  수록 논문 최신일: {newest}')
    print(f'  {"파일":<38} {"크기(B)":>16}  md5')
    for name in (DB_JSON, ABS_BIN, TITLE_BIN, MAP_JSON):
        p = os.path.join(args.out, name)
        print(f'  {name:<38} {os.path.getsize(p):>16,}  {md5(p)}')

    print(f'\n완료: {n_base:,} -> {len(merged_list):,}편')
    print(f'검증: python scripts/check_db.py --db-path {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
