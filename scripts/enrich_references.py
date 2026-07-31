#!/usr/bin/env python3
"""생성된 서베이 .json에 참고문헌 서지정보를 채워 넣는다.

main.py가 저장하는 'reference' 필드는 {번호: arxiv_id} 뿐이라 제목도 링크도 없다.
반대로 .md/.tex의 References에는 제목만 있고 arXiv ID가 없다. 둘 다 반쪽이라
어느 쪽을 봐도 실제 논문을 찾아갈 수가 없다.

DB(arxiv_paper_db.json)에 id/title/url/date가 모두 있으므로 조인해서
'reference_detail' 필드를 새로 추가한다.

⚠ 'reference' 필드는 절대 건드리지 않는다. src/agents/judge.py 의
   citation_quality()가 references.values()를 arXiv id 목록으로,
   references.items()를 (번호, id) 쌍으로 쓰기 때문에 구조를 바꾸면
   evaluation.py가 깨진다.

DB가 750MB라 로딩에 시간이 걸리므로 한 번만 읽고 전체 서베이를 일괄 처리한다.

사용법:
    python scripts/enrich_references.py                    # output/ 전체
    python scripts/enrich_references.py output/haiku/*.json
"""

import argparse
import glob
import json
import os
import sys

DB_FILE = 'arxiv_paper_db.json'
TABLE = 'cs_paper_info'


def collect_ids(json_paths):
    """서베이 json들에서 필요한 arXiv id를 모은다. (경로별 refs, 전체 id 집합)"""
    per_file, needed = {}, set()
    for p in json_paths:
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
        refs = data.get('reference') or {}
        if not refs:
            print(f'  건너뜀 (reference 없음): {p}')
            continue
        per_file[p] = refs
        needed.update(str(v) for v in refs.values())
    return per_file, needed


def load_meta(db_path, needed):
    """DB에서 필요한 id의 서지정보만 뽑는다."""
    path = os.path.join(db_path, DB_FILE)
    if not os.path.exists(path):
        sys.exit(f'DB를 찾을 수 없습니다: {path}')

    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f'DB 로딩 중… {path} ({size_mb:,.0f}MB) — 1~2분 걸립니다', flush=True)
    with open(path, encoding='utf-8') as f:
        db = json.load(f)

    table = db.get(TABLE) or {}
    print(f'DB {len(table):,}편 중 필요한 {len(needed):,}편을 찾는 중…', flush=True)

    meta = {}
    for rec in table.values():
        rid = rec.get('id')
        if rid in needed:
            meta[rid] = {
                'id': rid,
                # arXiv 제목에는 줄바꿈과 들여쓰기가 들어 있다.
                'title': ' '.join((rec.get('title') or '').split()),
                'date': (rec.get('date') or '').strip(),
                # DB의 url은 /pdf/ 링크다. 사람이 보기엔 초록 페이지가 낫다.
                'url': f'https://arxiv.org/abs/{rid}',
            }
            if len(meta) == len(needed):
                break
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('json_paths', nargs='*', help='기본값: output/*/*.json')
    ap.add_argument('--db-path', default='./database')
    ap.add_argument('--dry-run', action='store_true', help='파일을 쓰지 않고 결과만 보고')
    args = ap.parse_args()

    paths = args.json_paths or sorted(glob.glob('output/*/*.json'))
    if not paths:
        sys.exit('대상 json이 없습니다.')

    per_file, needed = collect_ids(paths)
    if not needed:
        sys.exit('참고문헌이 있는 json이 없습니다.')

    meta = load_meta(args.db_path, needed)
    missing_all = needed - set(meta)
    print(f'조회 완료: {len(meta):,}/{len(needed):,}편'
          + (f'  ⚠ DB에 없는 id {len(missing_all)}개' if missing_all else ''))
    print()

    for path, refs in per_file.items():
        detail, missing = {}, []
        for num, rid in sorted(refs.items(), key=lambda kv: int(kv[0])):
            rid = str(rid)
            if rid in meta:
                detail[str(num)] = meta[rid]
            else:
                missing.append(num)
                # DB에 없어도 id는 남겨둔다. 최소한 arXiv에서 찾아갈 수는 있다.
                detail[str(num)] = {'id': rid, 'title': '', 'date': '',
                                    'url': f'https://arxiv.org/abs/{rid}'}

        if not args.dry_run:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            data['reference_detail'] = detail       # 'reference'는 그대로 둔다
            with open(path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, indent=4, ensure_ascii=False))

        flag = '  ⚠ 제목 없음 %d개' % len(missing) if missing else ''
        print(f'{"(dry-run) " if args.dry_run else ""}{path}: {len(detail)}개{flag}')


if __name__ == '__main__':
    main()
