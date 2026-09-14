#!/usr/bin/env python3
"""DB 디렉터리에 `paper_dates.json` (id → 공개일, 정밀도 포함) sidecar 를 만든다.

    $ASG_PY scripts/build_paper_dates.py --db-path ./database_kisti-kisti-2512 \
        --openalex /data2/chanjoong/survey-agent/asg-common-corpus/data/upstream/cd87dd0/openalex/works/works.parquet

왜: KISTI export 의 `date` 는 연 단위(`YYYY-01-01`)뿐이라, topic cutoff 가 연중(예: 2025-12-05)이면
그 해 DOI 논문 전부가 "cutoff 이전임을 증명 못 함"으로 빠진다. OpenAlex 미러(works.parquet, 4.8억 편)의
`publication_date` 로 DOI 레코드에 일 단위 날짜를 붙이면 그 손실이 사라진다.

기록 형식: {"meta": {...}, "dates": {"<id>": "YYYY" | "YYYY-MM" | "YYYY-MM-DD"}} — 문자열 길이 = 정밀도.
src/database.py 는 이 파일이 있으면 레코드 `date` 대신 이 값을 쓴다(없는 id 는 기존 규칙으로 fallback).

날짜 결정 규칙 (보수적 — 상한이 늦은 쪽을 택한다):
  arXiv id 레코드   id 의 YYMM (v1 투고월). OpenAlex 는 보지 않는다 — KISTI arXiv 레코드의 버전은 v1 이 아닐 수
                    있어(초록이 최신판일 수 있음) 월 단위 상한이 안전하다.
  DOI 레코드        OpenAlex publication_date 가 있고 그 연도 ≥ KISTI year 이면 일 단위 채택.
                    OpenAlex 연도 < KISTI year 면(서로 다른 판을 가리킴) KISTI year 유지(연 단위).
                    OpenAlex 에 없으면 KISTI year(연 단위). year 도 없으면 기록하지 않음(→ 런타임에서 제외).

duckdb 가 필요하다(asg-corpus env: /data2/chanjoong/miniforge3/envs/asg-corpus/bin/python).
"""
import argparse
import datetime
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.retrieval_policy import arxiv_yymm, normalize, precision_of  # noqa: E402


def manifest_info(db_path):
    for p in glob.glob(os.path.join(db_path, '*.manifest.json')):
        try:
            m = json.load(open(p))
            return {'file': os.path.basename(p), 'content_sha256': m.get('content_sha256'),
                    'date_precision': m.get('date_precision'),
                    'view_papers_sha256': ((m.get('view') or {}).get('files_sha256') or {}).get('papers.parquet')}
        except Exception:
            pass
    return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--db-path', required=True)
    ap.add_argument('--openalex', help='OpenAlex works.parquet (doi, publication_date 컬럼). 없으면 arXiv 월 + KISTI 연도만')
    ap.add_argument('--out', help='기본 <db-path>/paper_dates.json')
    ap.add_argument('--threads', type=int, default=16)
    args = ap.parse_args()
    out = args.out or os.path.join(args.db_path, 'paper_dates.json')

    t0 = time.time()
    mi = manifest_info(args.db_path)
    db_prec = 'year' if str(mi.get('date_precision') or '').lower().startswith('year') else 'day'
    print(f'[1/4] {args.db_path}/arxiv_paper_db.json 로드 (date 정밀도={db_prec})', flush=True)
    with open(os.path.join(args.db_path, 'arxiv_paper_db.json')) as f:
        table = json.load(f)['cs_paper_info']
    recs = list(table.values())
    print(f'      {len(recs):,}편 {time.time() - t0:.0f}s', flush=True)

    dates, src = {}, {'arxiv_id': 0, 'db_date': 0, 'openalex': 0, 'openalex_year_conflict': 0, 'none': 0}
    doi_year = {}
    for r in recs:
        pid = r['id']
        ym = arxiv_yymm(pid)
        if ym:
            dates[pid] = ym
            src['arxiv_id'] += 1
            continue
        d = normalize(r.get('date'), db_prec)
        if d:
            dates[pid] = d
            src['db_date'] += 1
            doi_year[pid] = int(d[:4])
        else:
            doi_year[pid] = None
            src['none'] += 1
    print(f'[2/4] arXiv 월 단위 {src["arxiv_id"]:,} · DOI 연 단위 {src["db_date"]:,} · 날짜 없음 {src["none"]:,}', flush=True)

    oa_meta = None
    if args.openalex:
        import duckdb
        st = os.stat(args.openalex)
        oa_meta = {'path': args.openalex, 'size': st.st_size,
                   'mtime': datetime.datetime.utcfromtimestamp(st.st_mtime).isoformat(timespec='seconds') + 'Z'}
        con = duckdb.connect()
        con.execute(f'PRAGMA threads={args.threads}')
        con.execute('CREATE TABLE ids(doi VARCHAR)')
        con.executemany('INSERT INTO ids VALUES (?)', [(d,) for d in doi_year])
        print(f'[3/4] OpenAlex 조인 — DOI {len(doi_year):,}개 vs {args.openalex} …', flush=True)
        t1 = time.time()
        rows = con.execute(f"""
            SELECT i.doi, min(w.publication_date) AS pd
            FROM read_parquet('{args.openalex}') w
            JOIN ids i ON lower(replace(w.doi, 'https://doi.org/', '')) = i.doi
            WHERE w.publication_date IS NOT NULL
            GROUP BY i.doi""").fetchall()
        print(f'      매칭 {len(rows):,}개 {time.time() - t1:.0f}s', flush=True)
        for doi, pd in rows:
            pd = normalize(str(pd)[:10])
            if not pd or precision_of(pd) != 'day':
                continue
            ky = doi_year.get(doi)
            if ky is not None and int(pd[:4]) < ky:
                src['openalex_year_conflict'] += 1     # 다른 판(예: 학회판 vs 저널판) — KISTI 연도 유지
                continue
            dates[doi] = pd
            src['openalex'] += 1
        src['db_date'] -= src['openalex']
        oa_meta['matched'] = len(rows)
    else:
        print('[3/4] --openalex 없음: DOI 레코드는 연 단위로 남는다', flush=True)

    prec_count = {}
    for v in dates.values():
        p = precision_of(v)
        prec_count[p] = prec_count.get(p, 0) + 1
    meta = {
        'created_at': datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'builder': 'scripts/build_paper_dates.py',
        'db_path': os.path.abspath(args.db_path), 'db_manifest': mi, 'records': len(recs),
        'dated': len(dates), 'by_precision': prec_count, 'by_source': src, 'openalex': oa_meta,
        'rule': 'arXiv id → YYMM(month); DOI → OpenAlex publication_date(day, 연도≥KISTI year 일 때) else KISTI year',
    }
    print(f'[4/4] 기록 {len(dates):,}편 정밀도 {prec_count} 출처 {src} → {out}', flush=True)
    with open(out, 'w') as f:
        json.dump({'meta': meta, 'dates': dates}, f)
    print(f'완료 {time.time() - t0:.0f}s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
