#!/usr/bin/env python3
"""topic 별 검색 정책(JSONL) 생성 — GT survey **최초 공개일** = retrieval cutoff.

    python scripts/build_topic_policy.py --fetch                      # 네트워크 조회 + 캐시 저장 + JSONL
    python scripts/build_topic_policy.py                              # 캐시만으로 JSONL 재생성
    python main.py --topic "<title>" --topic_policy data/topic_policy.kisti-2512.jsonl --topic_id <slug> ...

배경 (2026-09-14): 교수님 지시 — cutoff 를 2025-12-31 로 고정하지 않고, 생성할 topic 의 GT survey 가
처음 공개된 날짜 이전 문헌만 검색하게 한다. preprint(arXiv 선행판)가 게재보다 빠르면 그 날짜다.

입력 (kisti_data 워크스페이스 — 읽기만 한다):
  data/topics.kisti.jsonl                    25편 topic 문자열(agent 입력 그대로)·slug·gt_doi·n_gt_refs
  candidates/<domain>/<slug>/candidate.yaml  gt.doi / gt.arxiv_id / gt.published(선정 당시 기록한 게재일)
  data/views/<view>/exclude_keys.txt         `gt:<domain>/<slug>` 사유의 키 = 그 topic 의 GT 출판본·선행판 (제외 id)
  data/views/<view>/view_manifest.json       corpus_snapshot_id (papers.parquet sha256)
  TWIN 표(아래)                               GT 의 arXiv 선행판. 출처: asg-common-corpus candidates/GT-SURVEYS.md
                                             (2026-09-02 확정) twin 열. view 의 `twin:<id>` 키와 대조 검증한다.

날짜 출처 (--fetch; 결과는 캐시 파일에 그대로 남겨 근거를 추적할 수 있게 한다):
  arXiv API   twin·GT arXiv id 의 <published> = v1 공개일 (일 단위). export.arxiv.org 는 429 가 잦다 → 백오프
  Crossref    gt_doi 의 created(DOI 등록일 ≈ 온라인 최초 게시, ACM 은 Just-Accepted 시점) ·
              published-online · issued
규칙:
  gt_first_public_at = 후보 중 **가장 이른 날짜** (누수 차단이 목적이므로 이른 쪽이 안전하다)
  retrieval_cutoff_at = gt_first_public_at  (당일 제외는 런타임 규칙: upper_bound(문헌) < cutoff)
  일 단위 후보가 하나도 없으면 arXiv id YYMM 의 월초로 두고 status=needs_review — main.py 가 거부한다.
  twin 이 없는 topic 은 "arXiv 선행판 존재 여부 미확인" 을 review_notes 에 남긴다(status 는 ok).
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.retrieval_policy import arxiv_yymm, lower_bound, precision_of  # noqa: E402

KISTI_ROOT = os.environ.get('KISTI_DATA_ROOT', '/data2/chanjoong/kisti_data')
ARXIV_DOI = '10.48550/arxiv.'

# GT ↔ arXiv 선행판. asg-common-corpus candidates/GT-SURVEYS.md (2026-09-02) twin 열 그대로.
TWIN = {
    'instruction-tuning-llms': '2308.10792',
    'model-merging': '2408.07666',
    'llm-agent-optimization': '2503.12434',
    'retrieval-explainability': '2212.07126',
    'trustworthy-rag': '2502.06872',
    'large-models-timeseries': '2310.10196',
    'deep-graph-clustering': '2211.12875',
    'physical-adversarial-attacks': '2211.01671',
    'harmful-finetuning': '2409.18169',
    'moe-inference-optimization': '2412.14219',
    'llm-distributed-training': '2407.20018',
    'edge-cloud-collaboration': '2505.01821',
    'ai-video-streaming': '2406.02302',
}

UA = 'AutoSurvey-topic-policy/0.1 (research; mailto:kimchanjoong54@gmail.com)'


def key_to_id(key):
    """view 키(DOI 형식) → DB id (규칙 B)."""
    k = key.strip().lower()
    if k.startswith(ARXIV_DOI):
        return re.sub(r'v\d+$', '', k[len(ARXIV_DOI):])
    return k


def read_jsonl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def http_get(url, retries=5, backoff=8.0):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:      # 429/503 포함
            last = e
            wait = backoff * (i + 1)
            print(f'  [http] {url[:80]}… 실패({e}); {wait:.0f}s 후 재시도 {i + 1}/{retries}', flush=True)
            time.sleep(wait)
    raise RuntimeError(f'조회 실패: {url} ({last})')


def fetch_crossref(doi):
    m = json.loads(http_get('https://api.crossref.org/works/' + urllib.parse.quote(doi) +
                            '?mailto=kimchanjoong54@gmail.com'))['message']

    def d(k):
        parts = ((m.get(k) or {}).get('date-parts') or [[None]])[0]
        if not parts or parts[0] is None:
            return None
        return '-'.join(f'{x:02d}' if i else f'{x:04d}' for i, x in enumerate(parts))
    return {'created': d('created'), 'published-online': d('published-online'),
            'published-print': d('published-print'), 'issued': d('issued'),
            'type': m.get('type'), 'container': (m.get('container-title') or [''])[0],
            'title': (m.get('title') or [''])[0], 'fetched_at': datetime.datetime.utcnow().isoformat(timespec='seconds')}


_MONTHS = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}


def fetch_arxiv_abs(aid):
    """arxiv.org/abs/<id> 페이지의 Submission history `[v1] Thu, 3 Nov 2022 …` 줄 — API 가 429 일 때의 폴백.
    citation_date 메타태그(같은 날짜여야 함)도 함께 적어 둔다."""
    time.sleep(3)
    html = http_get(f'https://arxiv.org/abs/{aid}', retries=3, backoff=10.0)
    #   <strong>[v6]</strong> Mon, 12 Jan 2026 …            (현재판)
    #   <strong><a href="/abs/…v1">[v1]</a></strong> Thu, 3 Nov 2022 …   (구판)
    m = re.search(r'\[v1\](?:</a>)?</strong>\s*[A-Za-z]{3}, (\d{1,2}) ([A-Za-z]{3}) (\d{4})', html)
    if not m:
        raise RuntimeError(f'{aid}: abs 페이지에서 [v1] 줄을 찾지 못함')
    v1 = f'{int(m.group(3)):04d}-{_MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}'
    cd = re.search(r'name="citation_date" content="(\d{4})/(\d{2})/(\d{2})"', html)
    title = re.search(r'name="citation_title" content="([^"]*)"', html)
    versions = re.findall(r'\[v(\d+)\](?:</a>)?</strong>', html)
    return {'published': v1, 'citation_date': '-'.join(cd.groups()) if cd else None,
            'latest_version': f'{aid}v{max(int(v) for v in versions)}' if versions else None,
            'title': (title.group(1) if title else '').strip(), 'source': 'arxiv.org/abs submission history [v1]',
            'fetched_at': datetime.datetime.utcnow().isoformat(timespec='seconds')}


def fetch_arxiv(ids):
    """id_list 일괄 조회. <published> = v1 공개일, <updated> = 최신판. API 429 가 계속되면 abs 페이지로 폴백."""
    out = {}
    if not ids:
        return out
    time.sleep(3)   # arXiv API 예절: 요청 간 3초
    try:
        xml = http_get('https://export.arxiv.org/api/query?id_list=' + ','.join(ids) + f'&max_results={len(ids) + 5}',
                       retries=2, backoff=10.0)
    except RuntimeError as e:
        print(f'  [arxiv] API 실패({e}) → abs 페이지 폴백', flush=True)
        for aid in ids:
            try:
                out[aid] = fetch_arxiv_abs(aid)
                print(f'  [arxiv] {aid} v1 {out[aid]["published"]} (citation_date {out[aid]["citation_date"]}) {out[aid]["title"][:60]}', flush=True)
            except Exception as e2:
                print(f'  [arxiv] {aid}: {e2}', flush=True)
        return out
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml)
    for e in root.findall('a:entry', ns):
        full = e.find('a:id', ns).text.rsplit('/', 1)[-1]
        base = re.sub(r'v\d+$', '', full)
        out[base] = {'published': e.find('a:published', ns).text[:10],
                     'updated': e.find('a:updated', ns).text[:10],
                     'latest_version': full,
                     'title': ' '.join((e.find('a:title', ns).text or '').split()),
                     'source': 'export.arxiv.org API <published>',
                     'fetched_at': datetime.datetime.utcnow().isoformat(timespec='seconds')}
    missing = [i for i in ids if i not in out]
    if missing:
        print(f'  [arxiv] 응답에 없는 id: {missing}', flush=True)
    return out


def build(args):
    root = args.kisti_root
    topics = read_jsonl(os.path.join(root, 'data', 'topics.kisti.jsonl'))
    vdir = os.path.join(root, 'data', 'views', args.view)
    vm = json.load(open(os.path.join(vdir, 'view_manifest.json')))
    snapshot = f"{args.view} papers.parquet sha256:{vm['files_sha256']['papers.parquet']}"

    # exclude_keys.txt: "<key>\t<reason>" — gt:<domain>/<slug> 사유로 topic 별 GT id 를 모은다.
    gt_keys, twin_keys = {}, set()
    for line in open(os.path.join(vdir, 'exclude_keys.txt'), encoding='utf-8'):
        if not line.strip():
            continue
        key, _, reason = line.rstrip('\n').partition('\t')
        if reason.startswith('gt:'):
            gt_keys.setdefault(reason[3:].split('/', 1)[1], []).append(key.strip())
        elif reason.startswith('twin:'):
            twin_keys.add(reason[5:].strip())
    if set(TWIN.values()) != twin_keys:
        raise SystemExit(f'TWIN 표와 view 의 twin 키가 다릅니다: 표에만 {set(TWIN.values()) - twin_keys}, '
                         f'view 에만 {twin_keys - set(TWIN.values())}')

    import yaml
    cache = json.load(open(args.sources_cache)) if os.path.exists(args.sources_cache) else {'crossref': {}, 'arxiv': {}}

    rows_pre = []
    for t in topics:
        slug, dom = t['slug'], t['domain']
        y = yaml.safe_load(open(os.path.join(root, 'candidates', dom, slug, 'candidate.yaml')))
        g = y.get('gt') or {}
        gt_doi = (g.get('doi') or '').strip().lower() or None
        gt_arxiv = (g.get('arxiv_id') or '').strip() or None
        ids = {key_to_id(k) for k in gt_keys.get(slug, [])}
        if gt_doi:
            ids.add(gt_doi)
        if gt_arxiv:
            ids.add(gt_arxiv)
        twin = TWIN.get(slug)
        if twin:
            ids.add(twin)
        arxiv_ids = sorted(i for i in ids if arxiv_yymm(i))
        dois = sorted(i for i in ids if not arxiv_yymm(i))
        rows_pre.append({'t': t, 'y': y, 'slug': slug, 'domain': dom, 'gt_doi': gt_doi, 'gt_arxiv': gt_arxiv,
                         'twin': twin, 'ids': sorted(ids), 'arxiv_ids': arxiv_ids, 'dois': dois,
                         'published_yaml': str(g.get('published') or '') or None})

    if args.fetch:
        need_ax = sorted({i for r in rows_pre for i in r['arxiv_ids'] if i not in cache['arxiv']})
        for i in range(0, len(need_ax), 20):
            cache['arxiv'].update(fetch_arxiv(need_ax[i:i + 20]))
        for r in rows_pre:
            for doi in r['dois']:
                if doi not in cache['crossref']:
                    try:
                        cache['crossref'][doi] = fetch_crossref(doi)
                    except Exception as e:
                        print(f'  [crossref] {doi}: {e}', flush=True)
                        cache['crossref'][doi] = {'error': str(e)}
                    time.sleep(1)
        cache['fetched_at'] = datetime.datetime.utcnow().isoformat(timespec='seconds')
        os.makedirs(os.path.dirname(args.sources_cache) or '.', exist_ok=True)
        json.dump(cache, open(args.sources_cache, 'w'), indent=1, ensure_ascii=False)
        print(f'캐시 저장: {args.sources_cache}', flush=True)

    out = []
    for r in rows_pre:
        cands, notes = [], []
        for aid in r['arxiv_ids']:
            a = cache['arxiv'].get(aid)
            label = 'twin' if aid == r['twin'] else 'gt-arxiv'
            if a and a.get('published'):
                cands.append({'date': a['published'], 'precision': 'day',
                              'source': f'arxiv:{aid} v1 published ({label})', 'title': a.get('title')})
            else:
                cands.append({'date': arxiv_yymm(aid) + '-01', 'precision': 'month-floor',
                              'source': f'arxiv:{aid} id YYMM 월초 ({label}; API 미조회)'})
        for doi in r['dois']:
            c = cache['crossref'].get(doi) or {}
            for k in ('created', 'published-online', 'issued'):
                v = c.get(k)
                if v and precision_of(v) == 'day':
                    cands.append({'date': v, 'precision': 'day', 'source': f'crossref:{doi} {k}'})
                elif v:
                    cands.append({'date': v, 'precision': precision_of(v), 'source': f'crossref:{doi} {k} (일 단위 아님)'})
        # candidate.yaml 의 published 는 선정 당시 Crossref/OpenAlex 에서 옮겨 적은 값이고 'YYYY-01-01' 자리표시
        # (issued 가 연 단위인 IEEE·ACL)가 섞여 있다 → Crossref 응답이 없는 DOI 에서만 폴백으로 쓴다.
        if r['published_yaml'] and precision_of(r['published_yaml']) == 'day' and \
                not any(cache['crossref'].get(d, {}).get('created') for d in r['dois']):
            cands.append({'date': r['published_yaml'], 'precision': 'day',
                          'source': 'candidate.yaml gt.published (Crossref 미조회 폴백)'})

        # 최초 공개일 = 모든 후보의 **하한** 중 최소. 월초(month-floor) 후보는 실제 v1 날짜보다 이르거나 같으므로
        # 일 단위 후보보다 앞서면 그것이 이긴다 — 그 경우 확정이 아니라 needs_review 다.
        usable = [c for c in cands if c['precision'] in ('day', 'month-floor')]
        if usable:
            best = min(usable, key=lambda c: c['date'])
            status = 'ok' if best['precision'] == 'day' else 'needs_review'
            if status != 'ok':
                notes.append(f'최초 공개일 후보 중 가장 이른 것이 월 단위({best["source"]}) — arXiv v1 날짜 조회 필요')
        else:
            best = None
            status = 'needs_review'
            notes.append('최초 공개일 후보가 없음 — --fetch 로 arXiv/Crossref 조회 필요')
        if not r['twin'] and not r['gt_arxiv']:
            notes.append('arXiv 선행판(twin) 미등록 — 존재 여부 미확인. 존재하면 cutoff 를 그 v1 날짜로 앞당겨야 함')
        if best and best['source'].endswith('created') :
            po = next((c['date'] for c in cands if c['source'].endswith('published-online')), None)
            if po and po > best['date']:
                notes.append(f'Crossref created(DOI 등록일) {best["date"]} 채택 — published-online {po} 보다 이름')
        # 후보 사이의 큰 간극(선행판 vs 게재)은 정상이지만, 기록해 둔다.
        day_cands = [c for c in cands if c['precision'] == 'day']
        if best and day_cands:
            span = (datetime.date.fromisoformat(max(c['date'] for c in day_cands)) -
                    datetime.date.fromisoformat(best['date'])).days
            if span > 365:
                notes.append(f'선행판과 게재 사이 {span}일 — GT 게재본에 그 사이 추가된 ref 는 채점 분모에서 빠져야 함')
        t = r['t']
        if t.get('retrieval_cutoff_at') and best and t['retrieval_cutoff_at'] != best['date']:
            notes.append(f"topics.kisti.jsonl 의 retrieval_cutoff_at={t['retrieval_cutoff_at']} 과 다름 — 분모 재계산 필요")
        out.append({
            'topic_id': r['slug'], 'topic': t['title'], 'domain': r['domain'],
            'gt_doi': r['gt_doi'], 'gt_arxiv_id': r['gt_arxiv'], 'twin_arxiv_id': r['twin'],
            'gt_first_public_at': best['date'] if best else None,
            'gt_first_public_source': best['source'] if best else None,
            'retrieval_cutoff_at': best['date'] if best else None,
            'date_sources': sorted(cands, key=lambda c: c['date']),
            'exclude_ids': r['ids'],
            'corpus_snapshot_id': snapshot, 'view': args.view,
            'n_gt_refs_year_cutoff': t.get('n_gt_refs'),   # 기존(연 단위 2025 cutoff) 분모 — 호환용
            # corpus 측이 topic cutoff 로 재계산한 분모(2026-09-14, gap_to_80.py): 분모 · 이론적 ceiling 분모 · 기준 view
            'n_gt_refs_cutoff': t.get('n_gt_refs_cutoff'),
            'n_gt_refs_cutoff_pool': t.get('n_gt_refs_cutoff_pool'),
            'n_gt_refs_cutoff_view': t.get('n_gt_refs_cutoff_view'),
            'status': status, 'review_notes': notes,
        })

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(f'# topic retrieval policy — view {args.view} — 생성 {datetime.datetime.utcnow().isoformat(timespec="seconds")}Z '
                f'by scripts/build_topic_policy.py. 근거 캐시: {os.path.basename(args.sources_cache)}\n')
        for row in out:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'정책 {len(out)}행 → {args.out}')
    print(f'{"topic_id":32} {"cutoff":11} {"status":12} source')
    for row in out:
        print(f'{row["topic_id"]:32} {row["retrieval_cutoff_at"] or "-":11} {row["status"]:12} {row["gt_first_public_source"]}')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--kisti-root', default=KISTI_ROOT)
    ap.add_argument('--view', default='kisti-2512')
    ap.add_argument('--out', default='data/topic_policy.kisti-2512.jsonl')
    ap.add_argument('--sources-cache', default='data/topic_policy.kisti-2512.sources.json',
                    help='arXiv/Crossref 응답 캐시 — 근거 파일. --fetch 없이도 이 파일로 정책을 재생성한다')
    ap.add_argument('--fetch', action='store_true', help='캐시에 없는 id 를 arXiv API·Crossref 에서 조회')
    args = ap.parse_args()
    return build(args)


if __name__ == '__main__':
    sys.exit(main())
