"""반입한 database 디렉터리가 src/database.py의 기대와 맞는지 검증한다.

main.py를 돌리기 전에 이걸로 먼저 확인하면, 몇 분 뒤 엉뚱한 KeyError로 죽는 걸 막을 수 있다.

    python scripts/check_db.py --db-path ./database
"""

import argparse
import json
import os
import sys

REQUIRED = {
    'arxiv_paper_db.json': 'TinyDB 본체 (database.py:21)',
    'faiss_paper_title_embeddings.bin': '제목 인덱스, 인용 매핑용 (database.py:26)',
    'faiss_paper_abs_embeddings.bin': '초록 인덱스, 검색용 (database.py:28)',
    'arxivid_to_index_abs.json': 'arXiv id ↔ FAISS 인덱스 매핑 (database.py:32)',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', default='./database')
    parser.add_argument('--embedding-model', default='nomic-ai/nomic-embed-text-v1')
    parser.add_argument('--query', default='large language models',
                        help='검색 스모크에 쓸 질의')
    parser.add_argument('--skip-search', action='store_true',
                        help='임베딩 모델 로딩 없이 파일 검사만')
    args = parser.parse_args()

    ok = True

    print('=== 1. 필수 파일 ===')
    missing = []
    for name, desc in REQUIRED.items():
        path = os.path.join(args.db_path, name)
        if os.path.exists(path):
            size = os.path.getsize(path) / (1024 ** 2)
            print(f'  OK   {name:38s} {size:9.1f} MB  {desc}')
        else:
            print(f'  없음 {name:38s} {"":9s}   {desc}')
            missing.append(name)
            ok = False
    if missing:
        print(f'\n파일명이 다를 수 있습니다. {args.db_path} 실제 내용:')
        for f in sorted(os.listdir(args.db_path)):
            print(f'  - {f}')
        print('\n위 이름으로 rename 하거나 src/database.py의 경로를 고치세요.')
        return 1

    print('\n=== 2. TinyDB 스키마 ===')
    with open(os.path.join(args.db_path, 'arxiv_paper_db.json')) as f:
        db = json.load(f)
    if 'cs_paper_info' not in db:
        print(f'  실패: 최상위 테이블 키가 cs_paper_info가 아님 → {list(db)[:5]}')
        return 1
    table = db['cs_paper_info']
    print(f'  cs_paper_info: {len(table)}편')
    sample_key = next(iter(table))
    sample = table[sample_key]
    for field in ('id', 'title', 'abs', 'date'):
        mark = 'OK  ' if field in sample else '없음'
        if field not in sample:
            ok = False
        print(f'  {mark} 필드 {field}')
    print(f'  샘플[{sample_key}]: id={sample.get("id")} date={sample.get("date")}')
    print(f'    title={str(sample.get("title"))[:70]}')

    print('\n=== 3. FAISS 인덱스 / id 매핑 정합성 ===')
    import faiss
    title_index = faiss.read_index(os.path.join(args.db_path, 'faiss_paper_title_embeddings.bin'))
    abs_index = faiss.read_index(os.path.join(args.db_path, 'faiss_paper_abs_embeddings.bin'))
    with open(os.path.join(args.db_path, 'arxivid_to_index_abs.json')) as f:
        id_to_index = json.load(f)

    print(f'  title index: {title_index.ntotal}벡터 dim={title_index.d}')
    print(f'  abs   index: {abs_index.ntotal}벡터 dim={abs_index.d}')
    print(f'  id 매핑    : {len(id_to_index)}개')

    if title_index.ntotal != abs_index.ntotal:
        print('  경고: title/abs 인덱스 크기가 다릅니다')
        ok = False
    if len(id_to_index) != abs_index.ntotal:
        print(f'  경고: id 매핑({len(id_to_index)})과 abs 인덱스({abs_index.ntotal}) 크기 불일치')
        ok = False

    max_index = max(int(v) for v in id_to_index.values())
    if max_index >= abs_index.ntotal:
        print(f'  실패: 매핑의 최대 인덱스 {max_index}가 인덱스 크기를 넘음 → 검색 시 KeyError')
        ok = False
    else:
        print(f'  OK   최대 인덱스 {max_index} < {abs_index.ntotal}')

    # database.py는 검색 결과 index를 id로 되돌린 뒤 TinyDB에서 논문을 찾는다.
    # 이 두 집합이 어긋나면 writer.py의 temp_title_dic 조회에서 KeyError가 난다.
    db_ids = {p['id'] for p in table.values()}
    map_ids = set(id_to_index)
    only_map = map_ids - db_ids
    print(f'  TinyDB id {len(db_ids)}개 / 매핑 id {len(map_ids)}개, '
          f'매핑에만 있는 id {len(only_map)}개')
    if only_map:
        print(f'    예: {list(only_map)[:3]} → 검색 결과가 TinyDB에 없어 유실됩니다')
        ok = False

    if not args.skip_search:
        print('\n=== 4. 검색 스모크 ===')
        sys.path.insert(0, os.getcwd())
        from src.database import database
        d = database(db_path=args.db_path, embedding_model=args.embedding_model)
        ids = d.get_ids_from_query(args.query, num=5)
        infos = d.get_paper_info_from_ids(ids)
        print(f'  질의: "{args.query}" → {len(ids)}건, 논문정보 {len(infos)}건')
        for p in infos:
            print(f'    [{p["id"]}] {p["title"][:70]}')
        if len(infos) != len(ids):
            print('  경고: 검색된 id 중 일부를 TinyDB에서 찾지 못했습니다')
            ok = False

    print('\n=== 결과: ' + ('통과' if ok else '문제 있음') + ' ===')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
