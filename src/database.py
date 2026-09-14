import glob
import os
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer,  AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import h5py
from src.utils import tokenCounter
from src.retrieval_policy import fingerprint, normalize, precision_of, record_date
import json
from tqdm import tqdm
import faiss
from tinydb import TinyDB, Query


def _resolve_device():
    # 'cuda' 하드코딩 대신 환경변수로 오버라이드 가능하게 (CPU 노드 디버깅용)
    name = os.environ.get('AUTOSURVEY_DEVICE', 'auto')
    if name != 'auto':
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device('cuda')
    if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')


def _db_date_precision(db_path):
    """레코드 `date` 필드의 정밀도. KISTI export 는 manifest 에 `date_precision: "year → YYYY-01-01"`
    을 적는다 — 그 'YYYY-01-01' 을 일 단위로 읽으면 1월 1일 공개로 오해한다. manifest 가 없는
    arXiv 수확 DB(`date` = 투고일)는 day."""
    for p in glob.glob(os.path.join(db_path, '*.manifest.json')):
        try:
            prec = str(json.load(open(p)).get('date_precision') or '')
        except Exception:
            continue
        if prec.lower().startswith('year'):
            return 'year'
        if prec.lower().startswith('month'):
            return 'month'
        if prec:
            return 'day'
    return 'day'


def _load_sidecar_dates(db_path):
    """scripts/build_paper_dates.py 가 만든 paper_dates.json — {id: 'YYYY[-MM[-DD]]'}.
    문자열 길이가 정밀도다. 있으면 레코드 date 보다 우선한다(OpenAlex 일 단위 등으로 보강한 값)."""
    p = os.path.join(db_path, 'paper_dates.json')
    if not os.path.exists(p):
        return None, None
    with open(p) as f:
        obj = json.load(f)
    return obj.get('dates') or {}, obj.get('meta') or {}


class database():

    def __init__(self, db_path, embedding_model, policy=None) -> None:

        self.db_path = db_path
        self.embedding_model = SentenceTransformer(embedding_model, trust_remote_code=True)

        self.embedding_model.to(_resolve_device())

        self.db = TinyDB(f'{db_path}/arxiv_paper_db.json')
        self.table = self.db.table('cs_paper_info')

        self.User = Query()
        self.token_counter = tokenCounter()
        # TinyDB의 one_of()는 문서 전체 선형 스캔이라 53만 편 규모에서 호출당 수 분이 걸린다.
        # 시작 시 1회 메모리 인덱스를 만들어 id 조회를 O(1)로 바꾼다.
        self._by_id = {p['id']: p for p in self.table.all()}
        self.title_loaded_index = faiss.read_index(f'{db_path}/faiss_paper_title_embeddings.bin')

        self.abs_loaded_index = faiss.read_index(f'{db_path}/faiss_paper_abs_embeddings.bin')
        self.id_to_index, self.index_to_id = self.load_index_arxivid(db_path)

        # 날짜 출처: sidecar(paper_dates.json) > arXiv id 의 YYMM > 레코드 date(manifest 정밀도로 해석)
        self.date_precision_default = _db_date_precision(db_path)
        self._sidecar_dates, self.sidecar_meta = _load_sidecar_dates(db_path)

        # 검색 허용 정책. None 이면 원본 그대로(전체 인덱스 검색).
        self.policy = None
        self._search_params = None
        self._allowed_bits = None
        self.policy_report = None
        if policy is not None and getattr(policy, 'active', False):
            self.set_policy(policy)

    def load_index_arxivid(self, db_path):
        with open(f'{db_path}/arxivid_to_index_abs.json','r') as f:
            id_to_index = json.loads(f.read())
        id_to_index = {id: int(index) for id, index in id_to_index.items()}
        index_to_id = {int(index): id for id, index in id_to_index.items()}
        return id_to_index, index_to_id

    # ------------------------------------------------------------------ 날짜·정책
    def date_of(self, pid):
        """레코드 공개일 → (date_str, precision, source). 없으면 (None, None, 'none')."""
        if self._sidecar_dates is not None:
            d = self._sidecar_dates.get(pid)
            if d:
                d = normalize(d)
                if d:
                    return d, precision_of(d), 'sidecar'
        rec = self._by_id.get(pid)
        if rec is None:
            return None, None, 'none'
        return record_date(rec, self.date_precision_default)

    def set_policy(self, policy):
        """허용 집합을 FAISS 위치 비트맵으로 만들어 이후 모든 검색·조회에 적용한다.

        전체 Top-K 를 뽑고 나서 거르는 게 아니라, 검색 자체가 허용 집합 안에서 돈다
        (IndexFlatL2 + IDSelectorBitmap). 제목 인덱스(인용 → id 매핑)에도 같은 선택자를 건다 —
        인용 문자열이 금지 문헌 제목에 가장 가까워도 금지 문헌으로는 매핑되지 않는다.
        """
        n = self.abs_loaded_index.ntotal
        if self.title_loaded_index.ntotal != n:
            raise RuntimeError(f'title/abs 인덱스 크기가 다릅니다({self.title_loaded_index.ntotal} vs {n}) — '
                               f'하나의 위치 매핑으로 두 인덱스를 제한할 수 없습니다')
        bits = np.zeros((n + 7) // 8, dtype=np.uint8)
        allowed_ids = []
        reasons = {'excluded_id': 0, 'no_date': 0, 'after_cutoff': {'day': 0, 'month': 0, 'year': 0}}
        sources = {}
        for pid, idx in self.id_to_index.items():
            if idx < 0 or idx >= n:
                continue
            if policy.is_excluded(pid):
                reasons['excluded_id'] += 1
                continue
            d, prec, src = self.date_of(pid)
            if d is None:
                reasons['no_date'] += 1
                continue
            if not policy.allows_date(d):
                reasons['after_cutoff'][prec] += 1
                continue
            bits[idx >> 3] |= np.uint8(1 << (idx & 7))
            allowed_ids.append(pid)
            sources[src] = sources.get(src, 0) + 1
        if not allowed_ids:
            raise RuntimeError(f'정책 적용 후 허용 문헌이 0편입니다: {policy.describe()}')
        self._allowed_bits = bits            # swig_ptr 이 가리키는 버퍼 — 반드시 살아 있어야 한다
        sel = faiss.IDSelectorBitmap(len(bits), faiss.swig_ptr(bits))
        self._selector = sel
        self._search_params = faiss.SearchParameters(sel=sel)
        self.policy = policy
        excluded_present = sorted(i for i in policy.exclude_ids if i in self.id_to_index)
        self.policy_report = {
            'policy': policy.to_dict(),
            'index_total': n,
            'allowed': len(allowed_ids),
            'allowed_fingerprint_sha256': fingerprint(allowed_ids),
            'excluded': reasons,
            'allowed_date_source': sources,
            'exclude_ids_present_in_index': excluded_present,
            'date_precision_default': self.date_precision_default,
            'sidecar': self.sidecar_meta,
        }
        print(f'[policy] {policy.describe()}', flush=True)
        print(f'[policy] 허용 {len(allowed_ids):,}/{n:,}편 — 제외: id {reasons["excluded_id"]}, '
              f'날짜없음 {reasons["no_date"]:,}, cutoff 이후 day {reasons["after_cutoff"]["day"]:,} / '
              f'month {reasons["after_cutoff"]["month"]:,} / year {reasons["after_cutoff"]["year"]:,}; '
              f'날짜 출처 {sources}; 인덱스에 남아 있던 제외 id {len(excluded_present)}개', flush=True)
        if excluded_present:
            print(f'[policy] ⚠ 제외 id 가 인덱스에 있었습니다(view 단계 누락) — 검색에서 차단됨: '
                  f'{excluded_present[:10]}', flush=True)
        return self.policy_report

    def is_allowed(self, pid):
        if self._allowed_bits is None:
            return True
        idx = self.id_to_index.get(pid)
        if idx is None:
            return False
        return bool(self._allowed_bits[idx >> 3] & (1 << (idx & 7)))

    def _search(self, index, query_vectors, top_k):
        if self._search_params is not None:
            return index.search(query_vectors, top_k, params=self._search_params)
        return index.search(query_vectors, top_k)

    # ------------------------------------------------------------------ 검색
    def get_embeddings(self, batch_text):
        batch_text = ['search_query: ' + _ for _ in batch_text]
        embeddings = self.embedding_model.encode(batch_text)
        return embeddings

    def get_embeddings_documents(self, batch_text):
        batch_text = ['search_document: ' + _ for _ in batch_text]
        embeddings = self.embedding_model.encode(batch_text)
        return embeddings
        
    def batch_search(self, query_vectors, top_k=1, title=False):
        query_vectors = np.array(query_vectors).astype('float32')
        index = self.title_loaded_index if title else self.abs_loaded_index
        distances, indices = self._search(index, query_vectors, top_k)
        results = []
        for i, query in tqdm(enumerate(query_vectors)):
            result = [(self.index_to_id[idx], distances[i][j]) for j, idx in enumerate(indices[i]) if idx != -1]
            results.append([_[0] for _ in result])
        return results

    def search(self, query_vector, top_k=1, title=False):
        query_vector = np.array([query_vector]).astype('float32')
        index = self.title_loaded_index if title else self.abs_loaded_index
        distances, indices = self._search(index, query_vector, top_k)
        results = [(self.index_to_id[idx], distances[0][i]) for i, idx in enumerate(indices[0]) if idx != -1]
        return [_[0] for _ in results]

    def get_ids_from_query(self, query, num,  shuffle = False):
        q = self.get_embeddings([query])[0]
        return self.search(q, top_k=num)
    
    def get_titles_from_citations(self, citations):
        q = self.get_embeddings_documents(citations)
        ids = self.batch_search(q,1, True)
        return [_[0] for _ in ids]

    def get_ids_from_queries(self, queries, num,  shuffle = False):
        q = self.get_embeddings(queries)
        ids = self.batch_search(q,num)
        return ids
    
    def get_date_from_ids(self, ids):
        return [r['date'] for r in self.get_paper_info_from_ids(ids)]

    def get_title_from_ids(self, ids):
        return [r['title'] for r in self.get_paper_info_from_ids(ids)]

    def get_abs_from_ids(self, ids):
        return [r['abs'] for r in self.get_paper_info_from_ids(ids)]

    def get_paper_info_from_ids(self, ids):
        # 정책이 걸려 있으면 직접 조회도 허용 집합으로 제한한다 — 검색을 거치지 않는 경로
        # (참고문헌 상세, judge)에서 금지 문헌 메타데이터가 새어 나가지 않게.
        if self._allowed_bits is not None:
            return [self._by_id[i] for i in ids if i in self._by_id and self.is_allowed(i)]
        return [self._by_id[i] for i in ids if i in self._by_id]

    def get_paper_from_ids(self, ids, max_len = 1500):
        loaded_data = {}
        with h5py.File(f'{self.db_path}/paper_content.h5', 'r') as f:
            for key in f.keys():
                if key in ids:
                    loaded_data[key] = str(f[key][()])
                if len(ids) == len(loaded_data):
                    break
        print(loaded_data[list(loaded_data.keys())[0]])
        return [self.token_counter.text_truncation(loaded_data[_], max_len) for _ in ids]
