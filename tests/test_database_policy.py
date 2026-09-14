"""src/database.py — 정책이 FAISS 검색 자체를 허용 집합 안으로 제한하는가.

전체 Top-K 를 뽑고 거르는 방식이면 k 보다 허용 문헌이 적을 때·금지 문헌이 상위에 몰릴 때
결과가 비거나 새는데, IDSelectorBitmap 은 검색 단계에서 후보를 제한하므로 그런 일이 없다.
torch/sentence_transformers 는 스텁으로 갈아끼운다(임베딩은 이 테스트의 관심사가 아니다).
"""
import sys
import types
import unittest

import numpy as np

from tests._loader import ROOT  # noqa: F401


def _stub(name, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


def _import_database():
    if 'src.database' in sys.modules:
        return sys.modules['src.database']
    saved = {k: sys.modules.get(k) for k in
             ('torch', 'transformers', 'sentence_transformers', 'h5py', 'tinydb', 'src.utils')}
    torch = _stub('torch', device=lambda n: n, cuda=types.SimpleNamespace(is_available=lambda: False),
                  backends=types.SimpleNamespace())
    sys.modules['torch'] = torch
    sys.modules['transformers'] = _stub('transformers', AutoModel=object, AutoTokenizer=object,
                                        AutoModelForSequenceClassification=object)
    sys.modules['sentence_transformers'] = _stub('sentence_transformers', SentenceTransformer=object)
    sys.modules['h5py'] = _stub('h5py')
    sys.modules['tinydb'] = _stub('tinydb', TinyDB=object, Query=object)
    sys.modules['src.utils'] = _stub('src.utils', tokenCounter=object)
    try:
        import src.database as db
        return db
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


try:
    import faiss  # noqa: F401
    HAVE_FAISS = True
except ImportError:
    HAVE_FAISS = False


@unittest.skipUnless(HAVE_FAISS, 'faiss 없음')
class SelectorSearchTest(unittest.TestCase):

    def setUp(self):
        import faiss
        self.dbmod = _import_database()
        from src.retrieval_policy import RetrievalPolicy
        # 6편: 1차원 벡터 = 위치. 질의 0.0 에 가까운 순 = id 순.
        ids = ['10.1/a', '2210.00001', '2211.00001', '10.1/b', '10.1/c', '2301.00001']
        recs = [
            {'id': '10.1/a', 'date': '2021-01-01', 'title': 'a'},   # 연 단위 2021 → 허용
            {'id': '2210.00001', 'date': '2022-01-01', 'title': 'b'},  # 2022-10 → 허용
            {'id': '2211.00001', 'date': '2022-01-01', 'title': 'c'},  # 2022-11 → 말일 ≥ cutoff → 제외
            {'id': '10.1/b', 'date': '2022-01-01', 'title': 'd'},   # 연 단위 2022 → 제외
            {'id': '10.1/c', 'title': 'e'},                          # 날짜 없음 → 제외
            {'id': '2301.00001', 'date': '2023-01-01', 'title': 'f'},  # 2023-01 → 제외
        ]
        vecs = np.array([[i * 1.0] for i in range(6)], dtype='float32')
        d = object.__new__(self.dbmod.database)
        d.abs_loaded_index = faiss.IndexFlatL2(1); d.abs_loaded_index.add(vecs)
        d.title_loaded_index = faiss.IndexFlatL2(1); d.title_loaded_index.add(vecs)
        d.id_to_index = {pid: i for i, pid in enumerate(ids)}
        d.index_to_id = {i: pid for i, pid in enumerate(ids)}
        d._by_id = {r['id']: r for r in recs}
        d.date_precision_default = 'year'
        d._sidecar_dates, d.sidecar_meta = None, None
        d.policy = None; d._search_params = None; d._allowed_bits = None; d.policy_report = None
        self.d = d
        self.RetrievalPolicy = RetrievalPolicy
        self.q = np.array([0.0], dtype='float32')

    def test_정책_없으면_원본_그대로(self):
        self.assertEqual(self.d.search(self.q, top_k=6), ['10.1/a', '2210.00001', '2211.00001', '10.1/b', '10.1/c', '2301.00001'])
        self.assertEqual(len(self.d.get_paper_info_from_ids(['10.1/c'])), 1)

    def test_검색이_허용_집합_안에서만_돈다(self):
        rep = self.d.set_policy(self.RetrievalPolicy(cutoff='2022-11-03'))
        self.assertEqual(rep['allowed'], 2)
        self.assertEqual(rep['excluded'], {'excluded_id': 0, 'no_date': 1,
                                           'after_cutoff': {'day': 0, 'month': 2, 'year': 1}})
        # k=6 을 요구해도 허용 2편만 돌아온다 (-1 은 걸러짐) — 사후 필터라면 여기서 금지 문헌이 샜을 것
        self.assertEqual(self.d.search(self.q, top_k=6), ['10.1/a', '2210.00001'])
        self.assertEqual(self.d.search(self.q, top_k=6, title=True), ['10.1/a', '2210.00001'])
        self.assertEqual(self.d.batch_search(np.array([[0.0], [5.0]], dtype='float32'), top_k=1),
                         [['10.1/a'], ['2210.00001']])

    def test_직접_조회도_허용_집합으로_제한(self):
        self.d.set_policy(self.RetrievalPolicy(cutoff='2022-11-03'))
        infos = self.d.get_paper_info_from_ids(['10.1/a', '2211.00001', '10.1/c'])
        self.assertEqual([p['id'] for p in infos], ['10.1/a'])
        self.assertTrue(self.d.is_allowed('10.1/a'))
        self.assertFalse(self.d.is_allowed('2211.00001'))
        self.assertFalse(self.d.is_allowed('없는 id'))

    def test_제외_id_는_날짜와_무관하게_막힌다(self):
        rep = self.d.set_policy(self.RetrievalPolicy(cutoff='2022-11-03', exclude_ids=['10.1/a']))
        self.assertEqual(rep['excluded']['excluded_id'], 1)
        self.assertEqual(rep['exclude_ids_present_in_index'], ['10.1/a'])
        self.assertEqual(self.d.search(self.q, top_k=6), ['2210.00001'])

    def test_sidecar_가_레코드_date_보다_우선(self):
        """OpenAlex 일 단위 보강: 2022 연 단위였던 10.1/b 가 2022-05-01 이면 허용된다."""
        self.d._sidecar_dates = {'10.1/b': '2022-05-01'}
        rep = self.d.set_policy(self.RetrievalPolicy(cutoff='2022-11-03'))
        self.assertEqual(rep['allowed'], 3)
        self.assertEqual(rep['allowed_date_source'], {'db_date': 1, 'arxiv_id': 1, 'sidecar': 1})
        self.assertEqual(self.d.date_of('10.1/b'), ('2022-05-01', 'day', 'sidecar'))
        self.assertIn('10.1/b', self.d.search(self.q, top_k=6))

    def test_허용_0편이면_멈춘다(self):
        with self.assertRaises(RuntimeError):
            self.d.set_policy(self.RetrievalPolicy(cutoff='1900-01-01'))

    def test_지문은_허용_집합에만_의존(self):
        r1 = self.d.set_policy(self.RetrievalPolicy(cutoff='2022-11-03'))
        r2 = self.d.set_policy(self.RetrievalPolicy(cutoff='2022-11-15'))   # 같은 허용 집합
        r3 = self.d.set_policy(self.RetrievalPolicy(cutoff='2022-12-31'))   # 2211 이 들어옴
        self.assertEqual(r1['allowed_fingerprint_sha256'], r2['allowed_fingerprint_sha256'])
        self.assertNotEqual(r1['allowed_fingerprint_sha256'], r3['allowed_fingerprint_sha256'])


if __name__ == '__main__':
    unittest.main()
