#!/usr/bin/env python3
"""topic 정책이 corpus 와 채점 분모에 무엇을 하는지 표로 뽑는다.

    python scripts/policy_report.py [--policy data/topic_policy.kisti-2512.jsonl] \
        [--db-path ./database_kisti-kisti-2512] [--refs /data2/chanjoong/kisti_data/candidates/gap_to_80_refs.jsonl]

열:
  cutoff            정책의 retrieval_cutoff_at
  allowed           DB 에서 cutoff 이전임이 확실한 편수 / 전체 (sidecar paper_dates.json 이 있으면 그 날짜로,
                    없으면 arXiv id YYMM + 레코드 연도로 — main.py 의 판정과 같은 규칙)
  GT in_view        GT ref 중 view 에 있는 것(기존 분모, gap_to_80_refs.jsonl tier=in_view)
  GT < cutoff       그중 S2 publicationDate(일 단위)가 cutoff 이전인 것 = **새 채점 분모(ceiling)**
  GT date?          in_view 인데 publicationDate 가 없어 판정 못 한 것
GT 쪽 날짜는 Semantic Scholar 의 publicationDate(ref 자체의 공개일)라 corpus 레코드 날짜와 출처가 다르다 —
채점기는 이 표가 아니라 같은 규칙을 자기 데이터로 다시 적용해야 한다. 여기서는 규모만 본다.
"""
import argparse
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.retrieval_policy import (RetrievalPolicy, load_policy_rows, normalize, record_date,  # noqa: E402
                                  upper_bound)

KISTI_ROOT = os.environ.get('KISTI_DATA_ROOT', '/data2/chanjoong/kisti_data')


def load_db_dates(db_path):
    """{id: date_str} — sidecar 우선, 없으면 arxiv_paper_db.json 에서 main.py 와 같은 규칙으로."""
    side = os.path.join(db_path, 'paper_dates.json')
    if os.path.exists(side):
        obj = json.load(open(side))
        return obj['dates'], f"sidecar {obj['meta'].get('created_at')} {obj['meta'].get('by_precision')}"
    prec = 'day'
    for p in glob.glob(os.path.join(db_path, '*.manifest.json')):
        if str(json.load(open(p)).get('date_precision', '')).lower().startswith('year'):
            prec = 'year'
    table = json.load(open(os.path.join(db_path, 'arxiv_paper_db.json')))['cs_paper_info']
    out = {}
    for r in table.values():
        d, _, _ = record_date(r, prec)
        if d:
            out[r['id']] = d
    return out, f'arxiv_paper_db.json (date 정밀도 {prec}, sidecar 없음)'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--policy', default='data/topic_policy.kisti-2512.jsonl')
    ap.add_argument('--db-path', default='./database_kisti-kisti-2512')
    ap.add_argument('--refs', default=os.path.join(KISTI_ROOT, 'candidates', 'gap_to_80_refs.jsonl'))
    ap.add_argument('--no-db', action='store_true', help='DB 허용 편수 계산 생략')
    args = ap.parse_args()

    rows = load_policy_rows(args.policy)
    refs = collections.defaultdict(list)
    if os.path.exists(args.refs):
        for line in open(args.refs, encoding='utf-8'):
            if line.strip():
                r = json.loads(line)
                if r.get('tier') == 'in_view':
                    refs[r['slug']].append(r)

    db_dates, db_src = (None, None)
    if not args.no_db:
        db_dates, db_src = load_db_dates(args.db_path)
        print(f'DB 날짜 출처: {db_src}, {len(db_dates):,}편')
        # 165만 편 × 25 topic 을 하나씩 판정하면 느리다 — 날짜 문자열은 수천 종뿐이므로 문자열별로 센다.
        date_count = collections.Counter(db_dates.values())
        ub = {d: upper_bound(d) for d in date_count}

    print(f'| topic_id | cutoff | 출처 | allowed / DB | GT in_view | GT < cutoff | GT date? | status |')
    print('|---|---|---|---:|---:|---:|---:|---|')
    for row in rows:
        pol = RetrievalPolicy(cutoff=row.get('retrieval_cutoff_at'), exclude_ids=row.get('exclude_ids') or [])
        allowed = '-'
        if db_dates is not None:
            n_ok = sum(c for d, c in date_count.items() if ub[d] is not None and ub[d] < pol.cutoff)
            n_ok -= sum(1 for e in pol.exclude_ids if e in db_dates and pol.allows_date(db_dates[e]))
            allowed = f'{n_ok:,} / {len(db_dates):,} ({n_ok / len(db_dates):.0%})'
        gt = refs.get(row['topic_id'], [])
        n_before = n_unknown = 0
        for r in gt:
            d = normalize(r.get('publicationDate'))
            if not d:
                n_unknown += 1
            elif pol.allows_date(d):
                n_before += 1
        src = (row.get('gt_first_public_source') or '-').split(' ')[0]
        print(f'| {row["topic_id"]} | {row.get("retrieval_cutoff_at") or "-"} | {src} | {allowed} | '
              f'{len(gt)} | {n_before} | {n_unknown} | {row.get("status")} |')
    return 0


if __name__ == '__main__':
    sys.exit(main())
