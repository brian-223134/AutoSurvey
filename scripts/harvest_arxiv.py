"""arXiv OAI-PMH로 논문 메타데이터를 수집해 TinyDB 형식 DB를 만든다.

공식 배포 DB(OneDrive)가 막힌 환경을 위한 대체 경로다. build_database.ipynb는
arxiv_paper_db.json이 이미 있다고 가정하므로 그 앞단이 비어 있었다.

출력: <out_dir>/arxiv_paper_db.json
    {"cs_paper_info": {"0": {"id":..., "title":..., "abs":..., "date":...}, ...}}
    키는 0부터의 연속 정수 문자열이며 scripts/build_index.py가 만드는
    FAISS 인덱스 순서와 1:1로 대응한다.

중간 결과는 <out_dir>/_harvest/records.jsonl 에 append되고 resumptionToken이
<out_dir>/_harvest/state.json 에 저장되므로, 중단 후 같은 명령을 다시 실행하면
이어서 받는다.

예)
    python scripts/harvest_arxiv.py --sets cs:cs:CL cs:cs:LG --out-dir ./database
    python scripts/harvest_arxiv.py --sets cs:cs:CL --created-from 2018-01-01 --max-records 30000
"""

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

import requests

OAI_URL = 'http://export.arxiv.org/oai2'
NS = {
    'oai': 'http://www.openarchives.org/OAI/2.0/',
    'arxiv': 'http://arxiv.org/OAI/arXiv/',
}
WS = re.compile(r'\s+')


def norm(text):
    """OAI 응답의 title/abstract에는 줄바꿈과 들여쓰기가 섞여 있다."""
    return WS.sub(' ', (text or '')).strip()


def oai_request(params, session, max_try=8):
    """503 + Retry-After(arXiv의 레이트리밋 신호)를 존중하며 한 번 요청한다."""
    last_err = None
    for attempt in range(max_try):
        try:
            r = session.get(OAI_URL, params=params, timeout=120)
            if r.status_code == 503:
                wait = int(r.headers.get('Retry-After', 20))
                print(f'  503 rate limited, {wait}s 대기', flush=True)
                time.sleep(wait)
                continue
            if r.status_code != 200:
                last_err = f'HTTP {r.status_code}: {r.text[:200]}'
            else:
                return r.text
        except Exception as e:  # 네트워크 순단
            last_err = repr(e)
        wait = min(2 ** attempt, 60)
        print(f'  요청 실패({last_err}), {wait}s 후 재시도', flush=True)
        time.sleep(wait)
    raise RuntimeError(f'OAI 요청 {max_try}회 실패: {last_err}')


def parse_records(xml_text):
    """(records, resumption_token)을 돌려준다."""
    root = ET.fromstring(xml_text)

    error = root.find('oai:error', NS)
    if error is not None:
        code = error.get('code')
        # 지정한 윈도에 레코드가 없으면 정상 종료로 취급한다.
        if code == 'noRecordsMatch':
            return [], None
        raise RuntimeError(f'OAI error [{code}]: {error.text}')

    list_records = root.find('oai:ListRecords', NS)
    if list_records is None:
        return [], None

    records = []
    for rec in list_records.findall('oai:record', NS):
        header = rec.find('oai:header', NS)
        # 철회/삭제된 논문은 metadata가 없다.
        if header is not None and header.get('status') == 'deleted':
            continue
        meta = rec.find('oai:metadata/arxiv:arXiv', NS)
        if meta is None:
            continue

        def text(tag):
            node = meta.find(f'arxiv:{tag}', NS)
            return norm(node.text) if node is not None else ''

        paper_id = text('id')
        title = text('title')
        abstract = text('abstract')
        if not paper_id or not title or not abstract:
            continue

        records.append({
            'id': paper_id,
            'title': title,
            'abs': abstract,
            'date': text('created'),
            'categories': text('categories'),
        })

    token_node = list_records.find('oai:resumptionToken', NS)
    token = token_node.text.strip() if token_node is not None and token_node.text else None
    return records, token


def harvest_set(set_spec, state, out_f, session, args, seen):
    """한 세트를 끝까지(또는 max-records까지) 수집한다. 수집한 신규 건수를 반환."""
    token = state.get(set_spec, {}).get('token')
    done = state.get(set_spec, {}).get('done', False)
    if done:
        print(f'[{set_spec}] 이미 완료됨, 건너뜀')
        return 0

    added = 0
    page = state.get(set_spec, {}).get('page', 0)
    while True:
        if token:
            # resumptionToken을 쓸 때는 다른 인자를 함께 보내면 badArgument가 된다.
            params = {'verb': 'ListRecords', 'resumptionToken': token}
        else:
            params = {'verb': 'ListRecords', 'set': set_spec, 'metadataPrefix': 'arXiv'}
            if args.oai_from:
                params['from'] = args.oai_from
            if args.oai_until:
                params['until'] = args.oai_until

        xml_text = oai_request(params, session)
        records, token = parse_records(xml_text)
        page += 1

        for rec in records:
            if rec['id'] in seen:
                continue
            # OAI의 from/until은 '최종 수정일' 기준이라 오래된 논문도 딸려 온다.
            # 실제 투고일 기준으로 거르고 싶으면 --created-from 을 쓴다.
            if args.created_from and rec['date'] < args.created_from:
                continue
            seen.add(rec['id'])
            out_f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            added += 1

        out_f.flush()
        state[set_spec] = {'token': token, 'page': page, 'done': token is None}
        save_state(args.out_dir, state)

        print(f'[{set_spec}] page {page}: +{len(records)}건 (누적 신규 {len(seen)}) '
              f'{"완료" if token is None else ""}', flush=True)

        if token is None:
            return added
        if args.max_records and len(seen) >= args.max_records:
            print(f'[{set_spec}] --max-records {args.max_records} 도달, 중단')
            return added
        time.sleep(args.delay)


def state_path(out_dir):
    return os.path.join(out_dir, '_harvest', 'state.json')


def save_state(out_dir, state):
    with open(state_path(out_dir), 'w') as f:
        json.dump(state, f, indent=2)


def load_state(out_dir):
    if os.path.exists(state_path(out_dir)):
        with open(state_path(out_dir)) as f:
            return json.load(f)
    return {}


def load_seen(records_path):
    """중단 후 재개 시 이미 받은 id를 복원한다."""
    seen = set()
    if not os.path.exists(records_path):
        return seen
    with open(records_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                seen.add(json.loads(line)['id'])
            except (json.JSONDecodeError, KeyError):
                continue
    return seen


def finalize(records_path, out_dir, max_records):
    """jsonl → TinyDB 형식 arxiv_paper_db.json"""
    papers = {}
    idx = 0
    seen = set()
    with open(records_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec['id'] in seen:
                continue
            seen.add(rec['id'])
            papers[str(idx)] = {
                'id': rec['id'],
                'title': rec['title'],
                'abs': rec['abs'],
                'date': rec['date'],
            }
            idx += 1
            if max_records and idx >= max_records:
                break

    db_path = os.path.join(out_dir, 'arxiv_paper_db.json')
    with open(db_path, 'w') as f:
        json.dump({'cs_paper_info': papers}, f, ensure_ascii=False)
    print(f'\n{db_path} 작성 완료: {idx}편')
    return idx


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sets', nargs='+', default=['cs:cs:CL'],
                        help='OAI setSpec 목록 (예: cs:cs:CL cs:cs:LG cs:cs:AI). '
                             'verb=ListSets로 전체 목록 확인 가능')
    parser.add_argument('--out-dir', default='./database', help='출력 디렉터리')
    parser.add_argument('--oai-from', default=None,
                        help='OAI from (최종 수정일 기준, YYYY-MM-DD)')
    parser.add_argument('--oai-until', default=None, help='OAI until (YYYY-MM-DD)')
    parser.add_argument('--created-from', default=None,
                        help='투고일(created) 기준 클라이언트 측 필터 (YYYY-MM-DD)')
    parser.add_argument('--max-records', type=int, default=0,
                        help='수집 상한 (0이면 무제한)')
    parser.add_argument('--delay', type=float, default=3.0,
                        help='페이지 사이 대기 초 (arXiv 권장 간격)')
    parser.add_argument('--finalize-only', action='store_true',
                        help='수집은 건너뛰고 기존 records.jsonl만 DB로 변환')
    args = parser.parse_args()

    work_dir = os.path.join(args.out_dir, '_harvest')
    os.makedirs(work_dir, exist_ok=True)
    records_path = os.path.join(work_dir, 'records.jsonl')

    if not args.finalize_only:
        state = load_state(args.out_dir)
        seen = load_seen(records_path)
        if seen:
            print(f'기존 {len(seen)}건 발견, 이어서 수집합니다')

        session = requests.Session()
        session.headers['User-Agent'] = 'autosurvey-harvester/0.1'

        with open(records_path, 'a') as out_f:
            for set_spec in args.sets:
                if args.max_records and len(seen) >= args.max_records:
                    print(f'--max-records 도달, 남은 세트 건너뜀')
                    break
                print(f'\n=== {set_spec} 수집 시작 ===')
                harvest_set(set_spec, state, out_f, session, args, seen)

    total = finalize(records_path, args.out_dir, args.max_records)
    if total == 0:
        print('경고: 수집된 논문이 0편입니다. --sets / 날짜 필터를 확인하세요', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
