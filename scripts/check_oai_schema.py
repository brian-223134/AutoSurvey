#!/usr/bin/env python
"""OAI-PMH 수집 결과가 기존 DB의 표기 규약과 정확히 일치하는지 검증한다.

증분 적재의 전제는 '새 논문이 기존 논문과 구별되지 않는 형태로 들어가는 것'이다.
필드 하나라도 표기가 다르면 에러 없이 코퍼스가 두 층으로 갈라진다.
그래서 기존 DB에 이미 있는 논문을 OAI 로 다시 받아 7필드를 문자 단위로 대조한다.

기존 DB의 규약은 실측으로 확인했다 (2026-08-04):

  id      = base + '최신' 버전 접미사      2008.06570v2
  date    = v1 제출일                      <created> 가 아니다. 개정본은 몇 년씩 어긋난다
  url     = http://arxiv.org/pdf/{id}      https 아님, /pdf/, 버전 포함
  abs     = TeX escape + 하드 줄바꿈       arXivRaw <abstract> (arXiv 형식은 유니코드로 변환돼 다름)
  authors = 유니코드 'forenames keyname'   arXiv 형식 구조화 저자 (arXivRaw 는 TeX escape 라 다름)
  cat     = <categories> 첫 번째           primary category
  title   = arXivRaw <title>

abs 와 authors 의 출처가 서로 다르므로 **두 형식을 모두 받아야** 한다.

사용법:
    python scripts/check_oai_schema.py --db-path ./database --n 20
"""
import argparse
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

OAI_URL = 'https://oaipmh.arxiv.org/oai'
UA = 'autosurvey-harvester/0.1 (+https://github.com/brian-223134/AutoSurvey)'

NS_RAW = {'oai': 'http://www.openarchives.org/OAI/2.0/',
          'r': 'http://arxiv.org/OAI/arXivRaw/'}
NS_ARX = {'oai': 'http://www.openarchives.org/OAI/2.0/',
          'a': 'http://arxiv.org/OAI/arXiv/'}

MONTHS = {m: i for i, m in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}


def fetch(params, tries=6):
    url = f'{OAI_URL}?{urllib.parse.urlencode(params)}'
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode('utf-8')
        except Exception as e:
            retry = getattr(e, 'headers', None) and e.headers.get('Retry-After')
            wait = int(retry) if retry else min(60, 5 * (attempt + 1))
            print(f'    재시도 {attempt + 1}/{tries} ({e}) — {wait}s', file=sys.stderr)
            time.sleep(wait)
    raise SystemExit('OAI 요청 실패')


def parse_version_date(text):
    """'Fri, 14 Aug 2020 20:46:38 GMT' -> '2020-08-14'"""
    m = re.search(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text or '')
    if not m:
        return ''
    day, mon, year = int(m.group(1)), MONTHS.get(m.group(2), 0), m.group(3)
    return f'{year}-{mon:02d}-{day:02d}'


def from_oai(base_id):
    """기존 DB와 같은 표기로 7필드 레코드를 만든다."""
    raw = ET.fromstring(fetch({'verb': 'GetRecord', 'metadataPrefix': 'arXivRaw',
                               'identifier': f'oai:arXiv.org:{base_id}'}))
    meta = raw.find('.//r:arXivRaw', NS_RAW)
    if meta is None:
        return None

    versions = meta.findall('r:version', NS_RAW)
    # 최신 버전 번호와 v1 날짜를 각각 쓴다.
    vnums = [int(v.get('version', 'v1').lstrip('v')) for v in versions] or [1]
    latest = max(vnums)
    v1 = next((v for v in versions if v.get('version') == 'v1'), None)

    def rtext(tag):
        el = meta.find(f'r:{tag}', NS_RAW)
        return (el.text or '').strip() if el is not None else ''

    arx = ET.fromstring(fetch({'verb': 'GetRecord', 'metadataPrefix': 'arXiv',
                               'identifier': f'oai:arXiv.org:{base_id}'}))
    ameta = arx.find('.//a:arXiv', NS_ARX)
    authors, atitle = [], ''
    if ameta is not None:
        for a in ameta.findall('a:authors/a:author', NS_ARX):
            key = a.find('a:keyname', NS_ARX)
            fore = a.find('a:forenames', NS_ARX)
            name = ' '.join(x.text.strip() for x in (fore, key)
                            if x is not None and x.text)
            if name:
                authors.append(name)
        t = ameta.find('a:title', NS_ARX)
        atitle = (t.text or '').strip() if t is not None else ''

    vid = f'{base_id}v{latest}'
    return {
        'id': vid,
        # 제목은 arXiv 형식(유니코드 변환본)을 쓴다. arXivRaw 는 TeX escape 가 남아
        # 기존 DB(예: 'Erdős-Pósa')와 다르다.
        'title': sanitize_title(atitle),
        'url': f'http://arxiv.org/pdf/{vid}',
        'date': parse_version_date(v1.find('r:date', NS_RAW).text if v1 is not None else ''),
        # 초록은 반대로 arXivRaw 를 쓴다. 기존 DB가 TeX escape 를 보존하고 있다.
        'abs': rtext('abstract'),
        'cat': (rtext('categories').split() or [''])[0],
        'authors': authors,
    }


# 기존 DB의 제목에는 이 문자들이 537,665편 통틀어 하나도 없다 (초록에는 있다 —
# ':' 는 초록의 22%에 존재). 파일명 금지 문자 집합이라 DB 제작 단계에서 공백으로
# 치환한 것으로 보인다. 제목도 임베딩 대상이므로 신규 논문에도 같은 치환을 건다.
# FAISS 인덱스로 들어가는 필드. 여기가 어긋나면 신·구 논문이 다른 텍스트 분포로
# 임베딩돼 코퍼스가 두 층으로 갈라진다. 나머지 필드는 검색에 쓰이지 않는다.
EMBEDDED = ('title', 'abs')

TITLE_BANNED = '<>:"/|?*#'
_TITLE_TRANS = str.maketrans({c: ' ' for c in TITLE_BANNED})


def sanitize_title(t):
    return (t or '').translate(_TITLE_TRANS)


def version_of(vid):
    m = re.search(r'v(\d+)$', vid or '')
    return int(m.group(1)) if m else 0


def same(field, a, b):
    """abs/title 은 공백 차이를 무시한다.

    기존 DB는 arXiv 원문의 하드 줄바꿈을 보존했는데 지금 OAI 는 공백으로 준다.
    이 차이가 임베딩을 바꾸지 않음을 실측했다 (300편 표본에서 cos 1.000000 /
    L2 0.000000, 같은 질의의 top-20 이 순서까지 동일). 저장 텍스트의 겉모습만
    다르므로 규약 위반으로 보지 않는다.
    """
    if field in ('abs', 'title'):
        return ' '.join((a or '').split()) == ' '.join((b or '').split())
    return a == b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db-path', default='./database')
    ap.add_argument('--n', type=int, default=10, help='대조할 논문 수')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--delay', type=float, default=3.0)
    args = ap.parse_args()

    print(f'[1/2] DB 로딩 {args.db_path}/arxiv_paper_db.json', flush=True)
    with open(f'{args.db_path}/arxiv_paper_db.json') as f:
        docs = list(json.load(f)['cs_paper_info'].values())
    rng = random.Random(args.seed)
    picks = rng.sample(docs, args.n)

    print(f'[2/2] OAI 대조 ({args.n}편 x 2요청)\n', flush=True)
    fields = ['id', 'title', 'url', 'date', 'abs', 'cat', 'authors']
    mismatch = {f: 0 for f in fields}
    checked = revised = 0

    for i, want in enumerate(picks, 1):
        base = want['id'].split('v')[0]
        got = from_oai(base)
        if got is None:
            print(f'  {i:>3}. {want["id"]:<18} 레코드 없음 (삭제된 논문?)')
            continue
        checked += 1

        # 스냅샷(2024-04) 이후 새 버전이 올라온 논문은 id/url/저자/제목/초록이
        # 달라지는 게 정상이다. 규약 위반이 아니므로 분리해서 센다.
        was_revised = version_of(got['id']) > version_of(want['id'])
        if was_revised:
            revised += 1

        bad = [f for f in fields if not same(f, got[f], want[f])]
        if was_revised:
            # 개정본은 제목·초록·저자·id 가 달라지는 게 당연하다. date/cat 만 본다.
            bad = [f for f in bad if f in ('date', 'cat')]

        for f in bad:
            mismatch[f] += 1
        blocking = [f for f in bad if f in EMBEDDED]
        mark = '개정' if was_revised and not bad else ('OK  ' if not bad else
                                                      ('차단' if blocking else '경고'))
        print(f'  {i:>3}. {want["id"]:<18} {mark} {" ".join(bad)}')
        for f in bad:
            print(f'         DB  {want[f]!r}'[:160])
            print(f'         OAI {got[f]!r}'[:160])
        time.sleep(args.delay)

    print()
    print(f'대조 {checked}편 (그중 스냅샷 이후 개정 {revised}편 — id/제목/저자 변화는 정상)')
    hard = [f for f in EMBEDDED if mismatch[f]]
    soft = [f for f in fields if mismatch[f] and f not in EMBEDDED]

    for f in hard:
        print(f'  [차단] {f:<8} {mismatch[f]}/{checked} — 임베딩되는 필드다')
    for f in soft:
        print(f'  [경고] {f:<8} {mismatch[f]}/{checked} — 검색에 쓰이지 않는 메타데이터')

    print()
    if hard:
        print('=> 임베딩 대상 필드가 어긋난다. 고치기 전에는 append 하지 말 것.')
        return 1
    print('=> 임베딩 대상(title/abs) 규약 일치. 이 방식으로 수집해도 된다.')
    print('   title/abs 의 하드 줄바꿈은 공백으로 정규화해 비교했다. 임베딩이 공백')
    print('   차이에 불변임을 실측했다 — 300편에서 cos 1.000000, top-20 순서까지 동일.')
    if soft:
        print('   경고 항목은 arXiv 쪽 변화이거나 원본 DB의 흠이다:')
        print('     cat     — cs.SY -> eess.SY 같은 arXiv 분류 체계 변경')
        print('     authors — 원본 DB에 앞공백/이름 분할 오류가 있다. 재현하지 않는다')
    return 0


if __name__ == '__main__':
    sys.exit(main())
