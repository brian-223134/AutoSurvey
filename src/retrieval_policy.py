"""토픽별 retrieval cutoff — GT survey **최초 공개일 이전** 문헌만 검색 후보로 허용한다.

배경 (2026-09-14, 교수님 지시): 고정 cutoff(2025-12-31)를 따로 두지 않고, 생성할 topic의
GT survey가 처음 공개된 날짜(preprint가 게재보다 빠르면 preprint 날짜)를 그 topic의 cutoff로
쓴다. 검색·순위화·Top-K는 허용 집합 **안에서** 수행한다 — 전체 DB Top-K를 뽑은 뒤 금지
문헌을 빼는 방식이 아니다(src/database.py 가 FAISS IDSelector 로 구현).

판정 규칙 — 문헌 공개일을 정밀도와 함께 보고, **가능한 가장 늦은 날짜(upper bound)가
cutoff 보다 앞설 때만** 허용한다. cutoff 당일은 제외한다.

    정밀도   표기          upper bound
    day      YYYY-MM-DD    그 날짜
    month    YYYY-MM       그 달 말일     ← arXiv id 의 YYMM (v1 투고월)
    year     YYYY          12-31          ← KISTI DOI 레코드는 연 단위 `year` 뿐
    없음     -             허용하지 않음  (불확실하면 제외하고 사유를 센다)

날짜 문자열의 길이가 곧 정밀도다. 레코드의 날짜 출처 우선순위는 database.py 참조
(sidecar paper_dates.json > arXiv id YYMM > 레코드 date 필드).

이 모듈은 torch/faiss 를 끌어오지 않는다 — 테스트와 정책 빌더 스크립트가 가볍게 쓴다.
"""
import calendar
import datetime
import hashlib
import json
import re

PRECISIONS = ('day', 'month', 'year')

# 2211.01671 / 2211.01671v3 — YYMM 이 v1 투고월. 신형 id 는 2007-04(0704)부터.
_NEW_ARXIV = re.compile(r'^(\d{2})(\d{2})\.\d{4,5}(?:v\d+)?$')
# cs/0701001 / hep-th/9901001 / math.GT/0309136 — 7자리 중 앞 4자리가 YYMM.
_OLD_ARXIV = re.compile(r'^[a-zA-Z\-]+(?:\.[a-zA-Z]{2})?/(\d{2})(\d{2})\d{3}(?:v\d+)?$')
_DATE_RE = re.compile(r'^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?')


def arxiv_yymm(pid):
    """arXiv id → 'YYYY-MM' (v1 투고월). arXiv id 가 아니면 None."""
    if not pid:
        return None
    pid = str(pid).strip()
    m = _NEW_ARXIV.match(pid)
    if m:
        yy, mm = int(m.group(1)), int(m.group(2))
        year = 2000 + yy
    else:
        m = _OLD_ARXIV.match(pid)
        if not m:
            return None
        yy, mm = int(m.group(1)), int(m.group(2))
        year = 1900 + yy if yy >= 91 else 2000 + yy
    if not 1 <= mm <= 12:
        return None
    return f'{year:04d}-{mm:02d}'


def is_arxiv_id(pid):
    return arxiv_yymm(pid) is not None


def precision_of(date_str):
    """'YYYY' → year, 'YYYY-MM' → month, 'YYYY-MM-DD' → day. 그 외 None."""
    if not date_str:
        return None
    s = str(date_str).strip()
    if re.fullmatch(r'\d{4}', s):
        return 'year'
    if re.fullmatch(r'\d{4}-\d{2}', s):
        return 'month'
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        return 'day'
    return None


def normalize(date_str, precision=None):
    """날짜 문자열을 정밀도에 맞는 표기로 자른다.

    KISTI export 는 연 단위 값을 'YYYY-01-01' 로 적는다(manifest date_precision: year).
    그대로 두면 day 로 오해되므로 precision='year' 를 주면 'YYYY' 로 줄인다.
    precision 을 안 주면 문자열 길이대로 둔다. 파싱 불가면 None.
    """
    if not date_str:
        return None
    m = _DATE_RE.match(str(date_str).strip())
    if not m:
        return None
    y, mo, d = m.group(1), m.group(2), m.group(3)
    own = 'day' if d else ('month' if mo else 'year')
    target = precision or own
    if target not in PRECISIONS:
        raise ValueError(f'정밀도는 {PRECISIONS} 중 하나여야 합니다: {precision!r}')
    # 더 세밀한 정밀도를 요구해도 문자열에 없는 정보는 만들 수 없다.
    if PRECISIONS.index(target) < PRECISIONS.index(own):
        target = own
    if target == 'year':
        return y
    if target == 'month':
        return f'{y}-{mo}'
    return f'{y}-{mo}-{d}'


def upper_bound(date_str):
    """정밀도상 가능한 가장 늦은 날짜. 파싱 불가·비정상 값이면 None."""
    prec = precision_of(date_str)
    if prec is None:
        return None
    parts = [int(p) for p in date_str.split('-')]
    try:
        if prec == 'year':
            return datetime.date(parts[0], 12, 31)
        if prec == 'month':
            last = calendar.monthrange(parts[0], parts[1])[1]
            return datetime.date(parts[0], parts[1], last)
        return datetime.date(parts[0], parts[1], parts[2])
    except ValueError:
        return None


def lower_bound(date_str):
    """정밀도상 가능한 가장 이른 날짜 (cutoff 쪽을 보수적으로 잡을 때 쓴다)."""
    prec = precision_of(date_str)
    if prec is None:
        return None
    parts = [int(p) for p in date_str.split('-')]
    try:
        if prec == 'year':
            return datetime.date(parts[0], 1, 1)
        if prec == 'month':
            return datetime.date(parts[0], parts[1], 1)
        return datetime.date(parts[0], parts[1], parts[2])
    except ValueError:
        return None


def parse_day(s):
    """'YYYY-MM-DD' 만 받는다. cutoff 는 일 단위로 확정돼 있어야 한다."""
    if precision_of(s) != 'day':
        raise ValueError(f'cutoff 는 YYYY-MM-DD 여야 합니다: {s!r}')
    return upper_bound(s)


def record_date(rec, db_precision='day'):
    """DB 레코드 하나의 공개일 → (date_str, precision, source).

    arXiv id 면 id 의 YYMM 을 쓴다(월 단위, v1 투고월 — KISTI year 보다 믿을 만하다:
    2601.* 212편이 year=2025 로 적혀 있었다). 아니면 레코드 `date` 를 db_precision 으로 해석.
    """
    pid = rec.get('id')
    ym = arxiv_yymm(pid)
    if ym:
        return ym, 'month', 'arxiv_id'
    d = normalize(rec.get('date'), db_precision)
    if d:
        return d, precision_of(d), 'db_date'
    return None, None, 'none'


def fingerprint(ids):
    """허용 집합의 지문 — 정렬한 id 를 개행으로 이어 sha256. 같은 DB·같은 정책이면 같다."""
    h = hashlib.sha256()
    for i in sorted(ids):
        h.update(str(i).encode())
        h.update(b'\n')
    return h.hexdigest()


class RetrievalPolicy:
    """한 topic 의 검색 허용 정책.

    cutoff       datetime.date — 허용 조건 upper_bound(문헌 공개일) < cutoff. None 이면 날짜 제한 없음
    exclude_ids  DB id 집합 — cutoff 와 무관하게 제외 (GT 본체·preprint·사본)
    """

    def __init__(self, cutoff=None, exclude_ids=(), topic_id=None, topic=None,
                 gt_first_public_at=None, gt_first_public_source=None, corpus_snapshot_id=None,
                 status='ok', extra=None):
        if isinstance(cutoff, str):
            cutoff = parse_day(cutoff)
        self.cutoff = cutoff
        self.exclude_ids = frozenset(str(i).strip() for i in exclude_ids if str(i).strip())
        self.topic_id = topic_id
        self.topic = topic
        self.gt_first_public_at = gt_first_public_at
        self.gt_first_public_source = gt_first_public_source
        self.corpus_snapshot_id = corpus_snapshot_id
        self.status = status
        self.extra = dict(extra or {})

    def is_excluded(self, pid):
        return str(pid) in self.exclude_ids

    def allows_date(self, date_str):
        """공개일(정밀도 포함 문자열)이 cutoff 이전임이 **확실**할 때만 True."""
        if self.cutoff is None:
            return True
        ub = upper_bound(date_str) if date_str else None
        if ub is None:
            return False
        return ub < self.cutoff

    def allows(self, pid, date_str):
        return (not self.is_excluded(pid)) and self.allows_date(date_str)

    @property
    def active(self):
        return self.cutoff is not None or bool(self.exclude_ids)

    def describe(self):
        c = self.cutoff.isoformat() if self.cutoff else '없음'
        return (f'topic_id={self.topic_id or "-"} cutoff<{c} '
                f'(gt_first_public_at={self.gt_first_public_at or "-"} '
                f'출처={self.gt_first_public_source or "-"}) 제외 id {len(self.exclude_ids)}개 '
                f'status={self.status}')

    def to_dict(self):
        return {
            'topic_id': self.topic_id,
            'topic': self.topic,
            'gt_first_public_at': self.gt_first_public_at,
            'gt_first_public_source': self.gt_first_public_source,
            'retrieval_cutoff_at': self.cutoff.isoformat() if self.cutoff else None,
            'rule': 'upper_bound(document_public_at) < retrieval_cutoff_at; 날짜 불명은 제외',
            'exclude_ids': sorted(self.exclude_ids),
            'corpus_snapshot_id': self.corpus_snapshot_id,
            'status': self.status,
            **self.extra,
        }


def load_policy_rows(path):
    """topic policy JSONL → 행 목록. 빈 줄·`#` 주석 줄은 건너뛴다."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            try:
                rows.append(json.loads(s))
            except json.JSONDecodeError as e:
                raise ValueError(f'{path}:{ln} JSON 파싱 실패: {e}')
    return rows


def select_row(rows, topic_id=None, topic=None):
    """topic_id 우선, 없으면 topic 문자열 완전 일치. 못 찾으면 KeyError."""
    if topic_id:
        for r in rows:
            if r.get('topic_id') == topic_id:
                return r
        raise KeyError(f'topic_id={topic_id!r} 가 정책 파일에 없습니다. '
                       f'있는 것: {[r.get("topic_id") for r in rows]}')
    if topic:
        hits = [r for r in rows if (r.get('topic') or '').strip() == topic.strip()]
        if len(hits) == 1:
            return hits[0]
        if not hits:
            raise KeyError(f'topic={topic!r} 와 일치하는 행이 정책 파일에 없습니다. '
                           f'--topic_id 로 지정하세요')
        raise KeyError(f'topic={topic!r} 가 정책 파일에 {len(hits)}번 있습니다. --topic_id 로 지정하세요')
    raise KeyError('topic_id 나 topic 중 하나는 있어야 합니다')


def policy_from_row(row, cutoff_override=None, extra_exclude=()):
    """정책 파일 행 → RetrievalPolicy.

    status 가 'ok' 가 아닌 행(최초 공개일 미확정)은 cutoff_override 없이는 쓰지 않는다 —
    불확실한 cutoff 로 조용히 돌아가면 누수인지 아닌지 알 수 없는 산출물이 남는다.
    """
    status = row.get('status', 'ok')
    cutoff = cutoff_override or row.get('retrieval_cutoff_at')
    if status != 'ok' and not cutoff_override:
        raise ValueError(
            f'topic_id={row.get("topic_id")} 의 정책 status={status!r} — 최초 공개일이 확정되지 않았습니다 '
            f'(review_notes={row.get("review_notes")}). 정책 파일을 확정하거나 --retrieval_cutoff 로 '
            f'명시적으로 넘기세요.')
    if not cutoff:
        raise ValueError(f'topic_id={row.get("topic_id")} 행에 retrieval_cutoff_at 이 없습니다')
    excl = list(row.get('exclude_ids') or []) + list(extra_exclude)
    extra = {k: row[k] for k in ('gt_doi', 'gt_arxiv_id', 'twin_arxiv_id', 'date_sources', 'review_notes')
             if k in row}
    if cutoff_override and row.get('retrieval_cutoff_at') and cutoff_override != row['retrieval_cutoff_at']:
        extra['cutoff_override'] = {'policy_file': row['retrieval_cutoff_at'], 'cli': cutoff_override}
    return RetrievalPolicy(
        cutoff=cutoff, exclude_ids=excl, topic_id=row.get('topic_id'), topic=row.get('topic'),
        gt_first_public_at=row.get('gt_first_public_at'),
        gt_first_public_source=row.get('gt_first_public_source'),
        corpus_snapshot_id=row.get('corpus_snapshot_id'), status=status, extra=extra)


def load_exclude_file(path):
    """한 줄에 id 하나. `#` 뒤는 주석, 탭 뒤(사유 열)는 무시."""
    ids = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            s = line.split('#', 1)[0].split('\t', 1)[0].strip()
            if s:
                ids.append(s)
    return ids
