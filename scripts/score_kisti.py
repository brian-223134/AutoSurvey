#!/usr/bin/env python3
"""KISTI 벤치마크 편당 채점 — GT 참고문헌 대비 recall·precision + 누수 검사.

    python scripts/score_kisti.py --json "output/<dir>/<topic>.json" \
        --topic_policy data/topic_policy.kisti-2608-r4.jsonl --topic_id <slug> [--out <dir>/<topic>.score.json]

규약 (kisti_data/docs/asg/AGENT-HANDOFF.md §5, docs/retrieval-policy.md §5):
  분모     candidates/gap_to_80_refs.jsonl 의 slug == topic_id ∧ tier == in_view
           (= topics.kisti.jsonl 의 n_gt_refs_cutoff; 다르면 중단)
  매칭 키  doi ∨ 10.48550/arxiv.<base id> (arXiv id 는 버전 접미사 제거, DOI 는 소문자)
  recall   GT ref 중 산출물 refs 에 있는 편수 / 분모
  precision 산출물 refs(고유 id) 중 GT ref 인 편수 / refs 수
  누수     정책 행의 exclude_ids(GT DOI·twin arXiv id)와 GT 제목이 survey 본문·reference·reference_detail
           에 나오는 횟수. retrieval_policy 블록(제외 목록 자체를 기록)은 세지 않는다.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.retrieval_policy import load_policy_rows, select_row  # noqa: E402

KISTI_ROOT = os.environ.get('KISTI_DATA_ROOT', '/data2/chanjoong/kisti_data')
ARXIV_NEW = re.compile(r'^(?:10\.48550/arxiv\.)?(\d{4}\.\d{4,5})(?:v\d+)?$')
ARXIV_OLD = re.compile(r'^(?:10\.48550/arxiv\.)?([a-z\-.]+/\d{7})(?:v\d+)?$')


def keys_of(pid):
    """id 하나 → 매칭 키 집합. arXiv 는 base id 와 10.48550 DOI 둘 다, 그 외는 소문자 DOI."""
    p = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:)', '', str(pid).strip().lower())
    m = ARXIV_NEW.match(p) or ARXIV_OLD.match(p)
    if m:
        return {m.group(1), f'10.48550/arxiv.{m.group(1)}'}
    return {p}


def norm_title(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--json', required=True, help='main.py 산출 <topic>.json')
    ap.add_argument('--topic_policy', required=True)
    ap.add_argument('--topic_id', required=True)
    ap.add_argument('--refs', default=os.path.join(KISTI_ROOT, 'candidates', 'gap_to_80_refs.jsonl'))
    ap.add_argument('--topics', default=os.path.join(KISTI_ROOT, 'data', 'topics.kisti.jsonl'))
    ap.add_argument('--out', default='', help='결과 JSON 저장 경로(생략 시 출력만)')
    args = ap.parse_args()

    row = select_row(load_policy_rows(args.topic_policy), topic_id=args.topic_id)
    topics = {t['slug']: t for t in map(json.loads, open(args.topics))}
    denom = topics[args.topic_id]['n_gt_refs_cutoff']
    if row.get('n_gt_refs_cutoff') not in (None, denom):
        sys.exit(f'정책 파일 분모 {row["n_gt_refs_cutoff"]} ≠ topics.kisti.jsonl {denom} — 판이 다르다')

    gt = [r for r in map(json.loads, open(args.refs))
          if r['slug'] == args.topic_id and r['tier'] == 'in_view']
    if len(gt) != denom:
        sys.exit(f'in_view {len(gt)}편 ≠ n_gt_refs_cutoff {denom} — refs 파일과 분모의 판이 다르다')
    gt_keys = []
    for r in gt:
        k = set()
        for f in ('doi', 'kisti_doi', 'view_id', 'arxiv_id', 'key'):
            if r.get(f):
                k |= keys_of(r[f])
        gt_keys.append(k)

    d = json.load(open(args.json))
    ids = sorted(set(d['reference'].values()))
    id_keys = {i: keys_of(i) for i in ids}
    all_keys = set().union(*id_keys.values()) if ids else set()
    hit_gt = sum(1 for k in gt_keys if k & all_keys)
    hit_refs = sum(1 for i in ids if any(id_keys[i] & k for k in gt_keys))

    # 누수: 제외 목록 자체를 담는 retrieval_policy 블록은 빼고 센다
    body = {k: v for k, v in d.items() if k != 'retrieval_policy'}
    blob = json.dumps(body, ensure_ascii=False).lower()
    leaks = {x: blob.count(x.lower()) for x in row.get('exclude_ids', [])}
    gt_title = norm_title(row['topic'])
    detail = d.get('reference_detail') or {}
    detail = detail.values() if isinstance(detail, dict) else detail
    title_refs = sum(1 for x in detail if isinstance(x, dict) and norm_title(x.get('title')) == gt_title)
    body_lines = [ln for ln in d['survey'].splitlines() if gt_title and gt_title in norm_title(ln)]
    # 첫 줄 H1 제목은 topic 문자열 그대로라 누수가 아니다
    title_body = sum(1 for ln in body_lines if not ln.startswith('# '))

    rp = d.get('retrieval_policy') or {}
    res = {
        'topic_id': args.topic_id,
        'denominator': denom,
        'refs': len(ids),
        'gt_hit': hit_gt,
        'recall': round(hit_gt / denom, 4),
        'refs_in_gt': hit_refs,
        'precision': round(hit_refs / len(ids), 4) if ids else None,
        'leak_exclude_ids': leaks,
        'leak_title_in_refs': title_refs,
        'leak_title_in_body_excl_h1': title_body,
        'allowed': rp.get('allowed'),
        'allowed_fingerprint_sha256': rp.get('allowed_fingerprint_sha256'),
        'view': row.get('n_gt_refs_cutoff_view'),
    }
    leak_total = sum(leaks.values()) + title_refs + title_body
    print(f'recall {hit_gt}/{denom} = {res["recall"]:.2%} · precision {hit_refs}/{len(ids)} = '
          f'{(res["precision"] or 0):.2%} · refs {len(ids)}')
    print(f'누수 {"0" if leak_total == 0 else "‼ " + str(leak_total)} — exclude_ids {leaks}, '
          f'제목 refs {title_refs} · 본문(H1 제외) {title_body}')
    print(f'허용 {rp.get("allowed")} · 지문 {str(rp.get("allowed_fingerprint_sha256"))[:8]} · 분모 판 {res["view"]}')
    if args.out:
        with open(args.out, 'w') as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f'저장: {args.out}')
    return 1 if leak_total else 0


if __name__ == '__main__':
    sys.exit(main())
