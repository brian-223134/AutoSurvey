"""main.py 파이프라인 end-to-end — 임의의 예시 논문 JSON 으로 가짜 서베이를 끝까지 만든다.

무엇을 확인하나
  · DB 디렉터리 계약(arxiv_paper_db.json · FAISS 2종 · id 매핑 · manifest · sidecar)을 **실제 database 클래스**로 읽는다
  · 검색 → 러프 아웃라인(chunk 2개) → merge → 서브아웃라인 → 최종 편집 → 서브섹션 초안 → 인용 점검
    → 인용 번호 매기기 → LCE 짝/홀 pass → 저장(md·json) 까지 `main.main()` 그대로
  · LLM 은 프롬프트 종류를 보고 형식에 맞는 답을 돌려주는 가짜(FakeLLM), 임베딩은 FakeEmbedder(결정적 bag-of-words)
  · 검색 정책(cutoff)이 걸리면 LLM 이 보는 논문 목록과 참고문헌 어디에도 cutoff 이후 논문이 없어야 하고,
    정책이 없으면 같은 논문이 실제로 나타난다(정책이 무의미하지 않다는 대조)

네트워크·GPU·모델 다운로드 없음. 전체 1초 안팎.
"""
import json
import os
import re
import shutil
import tempfile
import threading
import types
import unittest
from unittest import mock

from tests._loader import FakeEmbedder, FakeTokenCounter, load_database, load_main, load_script

try:
    import faiss
    HAVE_FAISS = True
except ImportError:
    HAVE_FAISS = False

TOPIC = 'Physical Adversarial Attacks on Vision Systems'
CUTOFF = '2022-11-03'      # 가상의 GT survey(2211.00001) 최초 공개일

# 임의의 예시 논문 13편 — 실제 DB 레코드와 같은 필드. 날짜는 arXiv id 의 YYMM(월) / DOI 는 연 단위 date.
PAPERS = [
    {'id': '1712.09665', 'title': 'Adversarial patch', 'date': '2017-01-01',
     'abs': 'We present a method to create universal, robust, targeted adversarial image patches in the real world. '
            'The patch can be printed, added to any scene, photographed, and presented to image classifiers; '
            'even when the patch is small it causes the classifier to ignore the other items in the scene.'},
    {'id': '1707.08945', 'title': 'Robust physical-world attacks on deep learning visual classification', 'date': '2017-01-01',
     'abs': 'We propose a general attack algorithm, Robust Physical Perturbations, to generate robust visual adversarial '
            'perturbations under different physical conditions. Black and white stickers on a stop sign cause '
            'targeted misclassification of road sign classifiers in the physical world.'},
    {'id': '1804.05810', 'title': 'ShapeShifter: robust physical adversarial attack on Faster R-CNN object detector', 'date': '2018-01-01',
     'abs': 'We present ShapeShifter, the first robust targeted physical adversarial attack that can fool the '
            'state-of-the-art Faster R-CNN object detector. Printed adversarial stop signs are consistently '
            'mis-detected as other objects from different distances and angles.'},
    {'id': '1904.08653', 'title': 'Fooling automated surveillance cameras: adversarial patches to attack person detection', 'date': '2019-01-01',
     'abs': 'We present an approach to generate adversarial patches that hide persons from person detectors. '
            'A printed patch held in front of the body makes a person invisible to automated surveillance '
            'cameras with a YOLO based detector in the physical world.'},
    {'id': '2009.00001', 'title': 'Adversarial camouflage: hiding physical-world attacks with natural styles', 'date': '2020-01-01',
     'abs': 'We propose adversarial camouflage to craft and camouflage physical-world adversarial examples into '
            'natural styles that appear legitimate to human observers. The camouflage texture transfers to '
            'printed objects and fools classifiers under varying viewpoints and lighting.'},
    {'id': '2103.00001', 'title': 'Dual attention suppression attack: generate adversarial camouflage in physical world', 'date': '2021-01-01',
     'abs': 'We propose a dual attention suppression attack that generates natural adversarial camouflage by '
            'suppressing model attention and human attention. The camouflage painted on vehicles evades '
            'detectors and classifiers in physical world experiments.'},
    {'id': '2205.00001', 'title': 'Segment and complete: defending object detectors against adversarial patch attacks', 'date': '2022-01-01',
     'abs': 'We propose a defense that detects and masks adversarial patches with a patch segmentation network, '
            'then completes the masked region. The defense protects object detectors against physical patch '
            'attacks without retraining the detector.'},
    {'id': '2211.00001', 'title': 'A decade survey of physical adversarial attacks in computer vision', 'date': '2022-01-01',
     'abs': 'This survey reviews physical adversarial attacks and defenses in computer vision over the past decade, '
            'covering patches, camouflage, clothing, and countermeasures for classifiers and detectors.'},
    {'id': '2303.00001', 'title': 'Diffusion-based purification against physical adversarial patches', 'date': '2023-01-01',
     'abs': 'We use diffusion models to purify images containing adversarial patches before detection. The '
            'purification removes physical patch perturbations and restores detector accuracy.'},
    {'id': '10.1109/tpami.2021.0001', 'title': 'Certified defenses against adversarial patches', 'date': '2021-01-01',
     'abs': 'We derive certified robustness guarantees against adversarial patches of bounded size using interval '
            'bound propagation, and show certified defenses for classifiers under patch attacks.'},
    {'id': '10.1145/3500000', 'title': 'Adversarial T-shirts: evading person detectors in the physical world', 'date': '2022-01-01',
     'abs': 'We design adversarial T-shirts whose printed patterns evade person detectors in the physical world '
            'despite non-rigid deformation of clothing, using thin plate spline modeling of the pattern.'},
    {'id': '10.1109/cvpr.2022.0002', 'title': 'Physical backdoor attacks on object detectors', 'date': '2022-01-01',
     'abs': 'We show physical backdoor attacks where a printed trigger object causes object detectors to miss or '
            'mislabel targets, and evaluate the attacks on cameras in the physical world.'},
    {'id': '1810.04805', 'title': 'BERT: pre-training of deep bidirectional transformers for language understanding', 'date': '2018-01-01',
     'abs': 'We introduce BERT, a language representation model that pre-trains deep bidirectional transformers '
            'from unlabeled text by jointly conditioning on left and right context in all layers.'},
]
# cutoff 2022-11-03 기준 제외돼야 하는 것: 2211(월 상한 11-30) · 2303 · cvpr 2022(연 단위)
# 10.1145/3500000 은 연 단위론 2022 라 제외지만 sidecar 가 2022-03-15 를 주면 허용된다.
SIDECAR = {'10.1145/3500000': '2022-03-15'}
EXCLUDED = {'2211.00001', '2303.00001', '10.1109/cvpr.2022.0002'}
ALLOWED = {p['id'] for p in PAPERS} - EXCLUDED
TITLE_TO_ID = {p['title']: p['id'] for p in PAPERS}


def build_fake_db(dirpath, papers, sidecar=None):
    """scripts/build_index.py 와 같은 규약으로 DB 디렉터리를 만든다 (TinyDB JSON · FAISS 2종 · 위치 매핑 · manifest)."""
    table = {str(i + 1): {**p, 'url': f'https://doi.org/{p["id"]}' if p['id'].startswith('10.') else f'http://arxiv.org/abs/{p["id"]}',
                          'cat': 'Computer Vision'} for i, p in enumerate(papers)}
    with open(os.path.join(dirpath, 'arxiv_paper_db.json'), 'w') as f:
        json.dump({'cs_paper_info': table}, f)
    emb = FakeEmbedder()
    for name, key in (('faiss_paper_title_embeddings.bin', 'title'), ('faiss_paper_abs_embeddings.bin', 'abs')):
        index = faiss.IndexFlatL2(FakeEmbedder.DIM)
        index.add(emb.encode(['search_document: ' + p[key] for p in papers]))
        faiss.write_index(index, os.path.join(dirpath, name))
    with open(os.path.join(dirpath, 'arxivid_to_index_abs.json'), 'w') as f:
        json.dump({p['id']: i for i, p in enumerate(papers)}, f)
    with open(os.path.join(dirpath, 'example.autosurvey.json.manifest.json'), 'w') as f:
        json.dump({'format': 'autosurvey', 'records': len(papers), 'content_sha256': 'fake',
                   'date_precision': 'year → YYYY-01-01'}, f)
    if sidecar:
        with open(os.path.join(dirpath, 'paper_dates.json'), 'w') as f:
            json.dump({'meta': {'created_at': 'test', 'builder': 'test'}, 'dates': sidecar}, f)


class FakeLLM:
    """APIModel 대역. 프롬프트 종류를 알아보고 그 단계가 기대하는 형식으로 답한다.

    실제 모델처럼 <format> 태그를 섞고, 초안은 제공된 paper_title 중 앞 3편을 '[]' 로 인용한다.
    LCE 는 원문 끝에 '(refined)' 를 붙여 돌려줘 정제 pass 가 실제로 돌았음을 남긴다.
    """
    calls = []
    instances = []
    _lock = threading.Lock()
    SECTIONS = [('Attack Methods', 'Physical adversarial patches, stickers and camouflage that fool classifiers and detectors'),
                ('Defense Methods', 'Defenses against physical patch attacks including masking, purification and certified robustness'),
                ('Evaluation', 'Benchmarks and evaluation protocols for physical adversarial attacks'),
                ('Open Problems', 'Open problems and future directions')]
    SUBS = {'Attack Methods': [('Adversarial Patches and Stickers', 'Universal adversarial patch stickers against classification and detection'),
                               ('Camouflage and Clothing', 'Adversarial camouflage textures and printed clothing evading person detectors')],
            'Defense Methods': [('Detection and Masking', 'Detecting and masking adversarial patches with segmentation'),
                                ('Certified and Purification Defenses', 'Certified defenses and purification against adversarial patches')]}

    def __init__(self, model, api_key, api_url):
        self.model, self.api_key, self.api_url = model, api_key, api_url
        self.usage = {'prompt': 0, 'completion': 0, 'reasoning': 0, 'cost': 0.0}
        self.retry_count = self.truncated = self.truncation_retries = self.failed = 0
        with self._lock:
            self.instances.append(self)

    def chat(self, text, temperature=1):
        kind, out = self._answer(text)
        with self._lock:
            self.calls.append((kind, text))
            self.usage['prompt'] += len(text.split())
            self.usage['completion'] += len(out.split())
        return out

    def batch_chat(self, text_batch, temperature=0):
        return [self.chat(t, temperature) for t in text_batch]

    @staticmethod
    def titles_in(prompt):
        return re.findall(r'^paper_title: (.+)$', prompt, re.M)

    def _section_outline(self, n):
        lines = ['Title: A Survey of Physical Adversarial Attacks']
        for i, (name, desc) in enumerate(self.SECTIONS[:n], 1):
            lines += [f'Section {i}: {name}', f'Description {i}: {desc}', '']
        return '\n'.join(lines)

    def _answer(self, p):
        if p == 'hello':
            return 'hello', 'Hello!'
        if 'You need to draft a outline based on the given papers' in p:
            n = int(re.search(r'contains (\d+) sections', p).group(1))
            return 'rough', '<format>\n' + self._section_outline(n) + '</format>'
        if 'You are provided with a list of outlines as candidates' in p:
            # 제약 문장(--enforce_section_num)이 있으면 그 수, 없으면 후보 아웃라인의 섹션 수 평균.
            # <format> 예시의 'Section 1: [NAME OF SECTION 1]' 줄은 세지 않는다.
            m = re.search(r'supposed to contain (\d+) sections', p)
            n = int(m.group(1)) if m else len(re.findall(r'^Section \d+: (?!\[NAME)', p, re.M)) // p.count('outline_id:')
            return 'merge', self._section_outline(n)
        if 'You need to enrich the section' in p:
            sec = re.search(r'You need to enrich the section (.+?)\.\n', p).group(1)
            subs = self.SUBS.get(sec, [(f'{sec} Basics', f'Basics of {sec}'), (f'{sec} Advances', f'Advances in {sec}')])
            lines = []
            for i, (name, desc) in enumerate(subs, 1):
                lines += [f'Subsection {i}: {name}', f'Description {i}: {desc}', '']
            return 'suboutline', '\n'.join(lines)
        if 'You have created a draft outline below' in p:
            body = p.split('You have created a draft outline below:\n---\n', 1)[1].split('\n---\n', 1)[0]
            body = re.sub(r'^(#{2,3}) [\d.]+ ', r'\1 ', body, flags=re.M)   # '## 1 X' → '## X' (실제 모델도 번호를 뗀다)
            return 'edit', '<format>\n' + body + '\n</format>'
        if 'Now you need to write the content for the subsection' in p:
            name = re.search(r'write the content for the subsection:\n"(.+?)" under', p).group(1)
            t = self.titles_in(p)[:3]
            cites = [f'[{t[0]}]' if t else '', f'[{t[1]}; {t[2]}]' if len(t) > 2 else '']
            text = (f'{name} has been studied extensively in the physical world {cites[0]}. Later work extended these '
                    f'ideas to detectors and camouflage {cites[1]}. We summarize the main threads below.')
            return 'draft', '<format>\n' + text + '\n</format>'
        if 'Now you need to check whether the citations' in p:
            body = p.split('You have written a subsection below:\n---\n', 1)[1].split('\n---\n<instruction>', 1)[0]
            return 'check', body
        if 'Now you need to help to refine one of the subsection' in p:
            body = p.split('Subsection to Refine: \n---\n', 1)[1].split('\n---\n', 1)[0]
            return 'lce', body + ' (refined)'
        raise AssertionError('알 수 없는 프롬프트: ' + p[:200])


@unittest.skipUnless(HAVE_FAISS, 'faiss 없음')
class PipelineEndToEndTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbmod = load_database()
        cls.main = load_main()
        import src.agents.outline_writer as ow
        import src.agents.writer as w
        cls.ow, cls.w = ow, w
        cls.check_survey = load_script('check_survey')

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.dbdir = os.path.join(self.tmp, 'db'); os.mkdir(self.dbdir)
        self.outdir = os.path.join(self.tmp, 'out')
        build_fake_db(self.dbdir, PAPERS, SIDECAR)
        FakeLLM.calls, FakeLLM.instances = [], []
        # 논문 13편 짜리 DB 로도 아웃라인 chunking 이 2조각으로 갈리게 토큰을 부풀린다 → merge 경로가 실제로 돈다.
        FakeTokenCounter.scale = 150
        self.addCleanup(setattr, FakeTokenCounter, 'scale', 1)
        # check_provider_pin 이 네트워크를 타지 않게. AUTOSURVEY_DEVICE 는 스텁 torch 라 무엇이든 무해.
        self._env = {k: os.environ.pop(k, None) for k in ('AUTOSURVEY_PROVIDER',)}
        self.addCleanup(lambda: [os.environ.__setitem__(k, v) for k, v in self._env.items() if v is not None])

    def args(self, **kw):
        base = dict(gpu='0', saving_path=self.outdir, model='fake-model', topic=TOPIC, section_num=2,
                    subsection_len=50, subsection_num=0, enforce_section_num=False, outline_reference_num=1200,
                    rag_num=5, api_url='http://fake', api_key='fake-key', db_path=self.dbdir, embedding_model='fake',
                    topic_policy='', topic_id='', retrieval_cutoff='', exclude_ids='')
        base.update(kw)
        return types.SimpleNamespace(**base)

    def run_pipeline(self, **kw):
        with mock.patch.object(self.main, 'database', self.dbmod.database), \
                mock.patch.object(self.ow, 'APIModel', FakeLLM), mock.patch.object(self.w, 'APIModel', FakeLLM), \
                mock.patch.object(self.ow, 'tokenCounter', FakeTokenCounter), \
                mock.patch.object(self.w, 'tokenCounter', FakeTokenCounter):
            self.main.main(self.args(**kw))
        with open(os.path.join(self.outdir, f'{TOPIC}.md'), encoding='utf-8') as f:
            md = f.read()
        with open(os.path.join(self.outdir, f'{TOPIC}.json'), encoding='utf-8') as f:
            js = json.load(f)
        return md, js

    def seen_ids(self, kinds):
        """LLM 프롬프트의 PAPER LIST 에 실제로 들어간 논문 id."""
        ids = set()
        for kind, prompt in FakeLLM.calls:
            if kind in kinds:
                ids.update(TITLE_TO_ID[t] for t in FakeLLM.titles_in(prompt))
        return ids

    # ------------------------------------------------------------------ 정책 있는 실행
    def test_정책_실행_끝까지_돌고_cutoff_이후_논문은_어디에도_없다(self):
        md, js = self.run_pipeline(retrieval_cutoff=CUTOFF)

        # 1) 구조: 제목 1, 섹션 2, 서브섹션 4, References 절, 번호 인용만 남고 제목 인용·<format>·Description 누출 없음
        self.assertTrue(md.startswith('# A Survey of Physical Adversarial Attacks'))
        body, refs = md.split('## References', 1)
        self.assertEqual(len(re.findall(r'^## ', body, re.M)), 2)
        self.assertEqual(len(re.findall(r'^### ', body, re.M)), 4)
        self.assertRegex(body, r'\[\d+(; \d+)*\]')
        self.assertNotIn('format>', md)
        self.assertNotRegex(body, r'\[[A-Za-z]')          # 제목 인용이 번호로 전부 치환됨
        self.assertEqual(body.count('(refined)'), 4)      # LCE 가 서브섹션마다 한 번
        self.assertTrue(self.check_survey.check(os.path.join(self.outdir, f'{TOPIC}.md')))   # 댕글링 0 · json 매핑 일치

        # 2) LLM 호출 순서·횟수: 러프 2(chunk) → merge 1 → 서브아웃라인 2 → 편집 1 → 초안 4 → 점검 4 → LCE 4
        kinds = [k for k, _ in FakeLLM.calls]
        self.assertEqual(kinds[:1], ['hello'])
        counts = {k: kinds.count(k) for k in set(kinds)}
        self.assertEqual(counts, {'hello': 1, 'rough': 2, 'merge': 1, 'suboutline': 2, 'edit': 1,
                                  'draft': 4, 'check': 4, 'lce': 4})
        self.assertLess(kinds.index('merge'), kinds.index('suboutline'))
        self.assertLess(kinds.index('edit'), kinds.index('draft'))
        self.assertLess(max(i for i, k in enumerate(kinds) if k == 'check'), kinds.index('lce'))
        self.assertEqual({i.model for i in FakeLLM.instances}, {'fake-model'})

        # 3) 누수 차단: LLM 이 본 논문 목록(아웃라인·서브아웃라인·초안·점검) 과 최종 참고문헌 어디에도 cutoff 이후 논문 없음
        seen = self.seen_ids({'rough', 'suboutline', 'draft', 'check'})
        self.assertTrue(seen)
        self.assertFalse(seen & EXCLUDED, seen & EXCLUDED)
        self.assertEqual(seen, ALLOWED)                   # k=1200 이라 허용 논문은 전부 아웃라인 단계에 나타난다
        ref_ids = set(js['reference'].values())
        self.assertTrue(ref_ids)
        self.assertFalse(ref_ids & EXCLUDED)
        self.assertTrue(ref_ids <= ALLOWED)

        # 4) 기록: 정책 블록 · 참고문헌 상세(날짜 정밀도·출처·링크)
        rp = js['retrieval_policy']
        self.assertEqual(rp['policy']['retrieval_cutoff_at'], CUTOFF)
        self.assertEqual((rp['index_total'], rp['allowed']), (13, 10))
        self.assertEqual(rp['excluded'], {'excluded_id': 0, 'no_date': 0,
                                          'after_cutoff': {'day': 0, 'month': 2, 'year': 1}})
        self.assertEqual(rp['allowed_date_source'], {'arxiv_id': 8, 'db_date': 1, 'sidecar': 1})
        self.assertEqual(len(rp['allowed_fingerprint_sha256']), 64)
        self.assertEqual(rp['date_precision_default'], 'year')
        for num, d in js['reference_detail'].items():
            self.assertEqual(d['id'], js['reference'][num])
            self.assertIn(d['date_precision'], ('day', 'month', 'year'))
            self.assertIn(d['date_source'], ('arxiv_id', 'db_date', 'sidecar'))
            self.assertTrue(d['url'].startswith('https://doi.org/') if d['id'].startswith('10.')
                            else d['url'].startswith('https://arxiv.org/abs/'))
            self.assertEqual(d['title'], TITLE_TO_ID and next(p['title'] for p in PAPERS if p['id'] == d['id']))

    def test_enforce_section_num_은_merge_프롬프트까지_관철된다(self):
        md, js = self.run_pipeline(retrieval_cutoff=CUTOFF, section_num=3, enforce_section_num=True)
        body = md.split('## References', 1)[0]
        self.assertEqual(len(re.findall(r'^## ', body, re.M)), 3)
        merge_prompt = next(p for k, p in FakeLLM.calls if k == 'merge')
        self.assertIn('The final outline is supposed to contain 3 sections.', merge_prompt)
        kinds = [k for k, _ in FakeLLM.calls]
        self.assertEqual((kinds.count('suboutline'), kinds.count('draft'), kinds.count('lce')), (3, 6, 6))

    def test_정책_파일과_topic_id_로도_같은_결과(self):
        policy = os.path.join(self.tmp, 'policy.jsonl')
        with open(policy, 'w') as f:
            f.write(json.dumps({'topic_id': 'fake-topic', 'topic': TOPIC, 'retrieval_cutoff_at': CUTOFF,
                                'gt_first_public_at': CUTOFF, 'gt_first_public_source': 'test',
                                'exclude_ids': ['1712.09665'], 'corpus_snapshot_id': 'fake', 'status': 'ok'}) + '\n')
        md, js = self.run_pipeline(topic_policy=policy, topic_id='fake-topic')
        rp = js['retrieval_policy']
        self.assertEqual(rp['policy']['topic_id'], 'fake-topic')
        self.assertEqual(rp['policy']['corpus_snapshot_id'], 'fake')
        self.assertEqual(rp['allowed'], 9)                                    # 제외 id 1편이 더 빠진다
        self.assertEqual(rp['excluded']['excluded_id'], 1)
        self.assertEqual(rp['exclude_ids_present_in_index'], ['1712.09665'])  # view 가 못 뺀 id 를 정책이 막음
        self.assertNotIn('1712.09665', self.seen_ids({'rough', 'suboutline', 'draft', 'check'}))
        self.assertNotIn('1712.09665', set(js['reference'].values()))

    def test_미확정_정책은_DB_를_열기_전에_거부(self):
        policy = os.path.join(self.tmp, 'policy.jsonl')
        with open(policy, 'w') as f:
            f.write(json.dumps({'topic_id': 'x', 'topic': TOPIC, 'retrieval_cutoff_at': CUTOFF,
                                'status': 'needs_review', 'review_notes': ['월 단위']}) + '\n')
        with self.assertRaises(ValueError):
            self.run_pipeline(topic_policy=policy, topic_id='x')
        self.assertEqual(FakeLLM.calls, [])
        self.assertFalse(os.path.exists(self.outdir))

    # ------------------------------------------------------------------ 정책 없는 실행 (대조)
    def test_정책_없으면_원본_동작_cutoff_이후_논문이_실제로_보인다(self):
        md, js = self.run_pipeline()
        self.assertIsNone(js['retrieval_policy'])
        seen = self.seen_ids({'rough'})
        self.assertEqual(seen, {p['id'] for p in PAPERS})     # 13편 전부(BERT 포함) 아웃라인 풀에 들어간다
        self.assertTrue(seen & EXCLUDED)
        self.assertTrue(self.check_survey.check(os.path.join(self.outdir, f'{TOPIC}.md')))
        # 정책 유무와 무관하게 참고문헌 상세는 날짜 정밀도를 적는다 (연 단위 DB 라 DOI 는 year, arXiv 는 month)
        precs = {d['id']: d['date_precision'] for d in js['reference_detail'].values()}
        for pid, prec in precs.items():
            self.assertEqual(prec, 'month' if not pid.startswith('10.') else ('day' if pid in SIDECAR else 'year'))


if __name__ == '__main__':
    unittest.main()
