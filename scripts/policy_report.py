#!/usr/bin/env python3
"""topic 정책이 corpus 와 채점 분모에 무엇을 하는지 표로 뽑는다.

    python scripts/policy_report.py [--policy data/topic_policy.kisti-2512.jsonl] \
        [--db-path ./database_kisti-kisti-2512] [--refs /data2/chanjoong/kisti_data/candidates/gap_to_80_refs.jsonl]

열:
  cutoff            정책의 retrieval_cutoff_at
  allowed           DB 에서 cutoff 이전임이 확실한 편수 / 전체 (sidecar paper_dates.json 이 있으면 그 날짜로,
                    없으면 arXiv id YYMM + 레코드 연도로 — main.py 의 판정과 같은 규칙)
  n_gt_refs_cutoff  corpus 측이 topic cutoff 로 재계산한 채점 분모 (data/topics.kisti.jsonl, 2026-09-14 gap_to_80.py)
  in_view           gap_to_80_refs.jsonl 의 tier == in_view (= 정책이 실제로 허용하는 분모; 위와 같아야 함, 다르면 ‼)
  blocked           tier == in_view_blocked — view 엔 있지만 레코드 날짜가 거칠어 정책이 막는 ref (날짜 정밀화로 회수 가능)
  undated           tier == undated — 날짜가 전혀 없어 분모 밖
  pool              n_gt_refs_cutoff_pool — cutoff 이전 identifiable ref 전체 (이론적 ceiling 분모)
구 형식(2026-09-14 이전, tier 에 in_view_blocked 가 없고 publicationDate 만 있는) refs 파일도 읽는다.
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
    ap.add_argument('--topics', default=os.path.join(KISTI_ROOT, 'data', 'topics.kisti.jsonl'),
                    help='n_gt_refs_cutoff·pool 열의 출처')
    ap.add_argument('--no-db', action='store_true', help='DB 허용 편수 계산 생략')
    args = ap.parse_args()

    rows = load_policy_rows(args.policy)
    tiers = collections.defaultdict(collections.Counter)      # slug → tier → 수
    legacy = collections.defaultdict(list)                    # 구 형식: in_view 행의 publicationDate 로 직접 판정
    new_format = False
    if os.path.exists(args.refs):
        for line in open(args.refs, encoding='utf-8'):
            if line.strip():
                r = json.loads(line)
                tiers[r['slug']][r.get('tier')] += 1
                if r.get('tier') == 'in_view':
                    legacy[r['slug']].append(r)
                if r.get('tier') == 'in_view_blocked' or 'record_date' in r:
                    new_format = True
    topics = {}
    if os.path.exists(args.topics):
        for line in open(args.topics, encoding='utf-8'):
            if line.strip():
                t = json.loads(line)
                topics[t['slug']] = t

    db_dates, db_src = (None, None)
    if not args.no_db:
        db_dates, db_src = load_db_dates(args.db_path)
        print(f'DB 날짜 출처: {db_src}, {len(db_dates):,}편')
        # 165만 편 × 25 topic 을 하나씩 판정하면 느리다 — 날짜 문자열은 수천 종뿐이므로 문자열별로 센다.
        date_count = collections.Counter(db_dates.values())
        ub = {d: upper_bound(d) for d in date_count}

    if new_format:
        print('| topic_id | cutoff | 출처 | allowed / DB | n_gt_refs_cutoff | in_view | blocked | undated | pool | status |')
        print('|---|---|---|---:|---:|---:|---:|---:|---:|---|')
    else:
        print('| topic_id | cutoff | 출처 | allowed / DB | GT in_view | GT < cutoff | GT date? | status |')
        print('|---|---|---|---:|---:|---:|---:|---|')
    for row in rows:
        pol = RetrievalPolicy(cutoff=row.get('retrieval_cutoff_at'), exclude_ids=row.get('exclude_ids') or [])
        allowed = '-'
        if db_dates is not None:
            n_ok = sum(c for d, c in date_count.items() if ub[d] is not None and ub[d] < pol.cutoff)
            n_ok -= sum(1 for e in pol.exclude_ids if e in db_dates and pol.allows_date(db_dates[e]))
            allowed = f'{n_ok:,} / {len(db_dates):,} ({n_ok / len(db_dates):.0%})'
        src = (row.get('gt_first_public_source') or '-').split(' ')[0]
        tc = tiers.get(row['topic_id'], collections.Counter())
        if new_format:
            t = topics.get(row['topic_id'], {})
            n_cut = t.get('n_gt_refs_cutoff')
            mark = '' if n_cut is None or n_cut == tc['in_view'] else ' ‼'
            print(f'| {row["topic_id"]} | {row.get("retrieval_cutoff_at") or "-"} | {src} | {allowed} | '
                  f'{n_cut if n_cut is not None else "-"} | {tc["in_view"]}{mark} | {tc["in_view_blocked"]} | {tc["undated"]} | '
                  f'{t.get("n_gt_refs_cutoff_pool", "-")} | {row.get("status")} |')
            continue
        gt = legacy.get(row['topic_id'], [])
        n_before = n_unknown = 0
        for r in gt:
            d = normalize(r.get('publicationDate'))
            if not d:
                n_unknown += 1
            elif pol.allows_date(d):
                n_before += 1
        print(f'| {row["topic_id"]} | {row.get("retrieval_cutoff_at") or "-"} | {src} | {allowed} | '
              f'{len(gt)} | {n_before} | {n_unknown} | {row.get("status")} |')
    return 0


if __name__ == '__main__':
    sys.exit(main())
