#!/usr/bin/env python
"""두 스냅샷에서 같은 토픽을 검색해 커버리지 차이를 잰다.

DB를 최신화하면 같은 토픽의 top-K 자체가 달라지므로 기존 산출물과의 통제 비교는
성립하지 않는다. 그것을 손실로 두지 않으려면 **두 스냅샷을 모두 남기고 차이를
측정 가능한 변수로 만들어야** 한다. 이 스크립트가 그 측정을 한다.

읽는 지표:

  d@1      가장 가까운 논문까지의 거리. 토픽이 코퍼스에 있는지
  d@K      K번째 논문까지의 거리. **낮을수록** K편을 채워도 관련성이 유지된다
  감쇠     d@K - d@1. 작을수록 관련 논문층이 두텁다
  최신 비율 검색된 논문 중 특정 연도 이후 비율
  중복률   두 스냅샷의 top-K 교집합. 낮을수록 최신화가 검색 결과를 많이 바꿨다

`--outline_reference_num` 이 기본 1200이므로 K도 1200을 기본값으로 둔다.

사용법:
    python scripts/compare_snapshots.py --old ./database --new ./database_2026-08 \\
        --topics "In-context Learning" "Evaluation of LLMs"
"""

import argparse
import os
import sys

import numpy as np


def load_db(path, model):
    sys.path.insert(0, os.getcwd())
    from src.database import database
    print(f'  로딩 {path} ...', flush=True)
    return database(db_path=path, embedding_model=model)


def probe(db, topic, k):
    """top-k 를 뽑고 거리·연도 분포를 돌려준다."""
    q = db.get_embeddings([topic])
    qv = np.array(q).astype('float32')
    dist, idx = db.abs_loaded_index.search(qv, k)
    dist, idx = dist[0], idx[0]
    ids = [db.index_to_id[int(i)] for i in idx if int(i) in db.index_to_id]
    dates = [r['date'] for r in db.get_paper_info_from_ids(ids) if r.get('date')]
    return {
        'ids': ids,
        'd1': float(dist[0]),
        'dk': float(dist[-1]),
        'dates': dates,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--old', default='./database')
    ap.add_argument('--new', required=True)
    ap.add_argument('--topics', nargs='+', required=True)
    ap.add_argument('-k', type=int, default=1200,
                    help='검색 깊이 (기본 1200 = main.py 의 outline_reference_num 기본값)')
    ap.add_argument('--since', default='2024-04-27',
                    help='"최신" 판정 기준일 (기본: 기존 스냅샷의 cutoff 다음날)')
    ap.add_argument('--embedding-model', default='nomic-ai/nomic-embed-text-v1')
    args = ap.parse_args()

    print('스냅샷 로딩 (각 수 분)')
    old = load_db(args.old, args.embedding_model)
    new = load_db(args.new, args.embedding_model)
    print(f'  기존 {len(old._by_id):,}편 / 신규 {len(new._by_id):,}편\n')

    hdr = (f'{"토픽":<34} {"스냅샷":<8} {"d@1":>7} {f"d@{args.k}":>8} '
           f'{"감쇠":>7} {f">={args.since[:7]}":>9} {"중복":>7}')
    print(hdr)
    print('-' * len(hdr))

    for topic in args.topics:
        ro = probe(old, topic, args.k)
        rn = probe(new, topic, args.k)
        overlap = len(set(ro['ids']) & set(rn['ids'])) / max(1, len(ro['ids']))
        for label, r in (('기존', ro), ('신규', rn)):
            recent = (sum(1 for d in r['dates'] if d >= args.since) /
                      max(1, len(r['dates'])))
            ov = f'{overlap*100:6.1f}%' if label == '신규' else '     -'
            print(f'{topic[:34]:<34} {label:<8} {r["d1"]:7.3f} {r["dk"]:8.3f} '
                  f'{r["dk"] - r["d1"]:7.3f} {recent*100:8.1f}% {ov:>7}')
        # 최신화가 제대로 됐다면 d@K 가 내려가고(관련성 유지) 최신 논문이 섞인다.
        if rn['dk'] > ro['dk']:
            print(f'{"":<34} !! 신규 스냅샷의 d@{args.k} 가 더 큽니다 — 확인 필요')
        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
