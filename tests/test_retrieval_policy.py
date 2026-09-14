"""src/retrieval_policy.py — topic 별 cutoff 판정 규칙과 정책 파일 해석.

핵심 불변식: 문헌 공개일의 **상한**(정밀도상 가장 늦은 날짜)이 cutoff 보다 앞설 때만 허용한다.
연 단위 레코드(KISTI DOI)는 cutoff 연도 안이면 무조건 제외, arXiv id 는 투고월 말일로 판정,
cutoff 당일은 제외, 날짜 불명은 제외. 이 규칙이 무너지면 GT 이후 문헌이 검색 풀에 섞인다.
"""
import json
import os
import tempfile
import unittest

from tests._loader import ROOT  # noqa: F401
from src import retrieval_policy as rp


class ArxivMonthTest(unittest.TestCase):

    def test_신형_id(self):
        self.assertEqual(rp.arxiv_yymm('2211.01671'), '2022-11')
        self.assertEqual(rp.arxiv_yymm('2211.01671v5'), '2022-11')
        self.assertEqual(rp.arxiv_yymm('0704.0050'), '2007-04')

    def test_구형_id(self):
        self.assertEqual(rp.arxiv_yymm('cs/0701001'), '2007-01')
        self.assertEqual(rp.arxiv_yymm('hep-th/9901001'), '1999-01')
        self.assertEqual(rp.arxiv_yymm('math.GT/0309136'), '2003-09')

    def test_DOI_는_아니다(self):
        self.assertIsNone(rp.arxiv_yymm('10.1145/3793659'))
        self.assertIsNone(rp.arxiv_yymm('10.48550/arxiv.2211.01671'))
        self.assertIsNone(rp.arxiv_yymm(''))
        self.assertIsNone(rp.arxiv_yymm(None))


class DateBoundTest(unittest.TestCase):

    def test_정밀도는_문자열_길이(self):
        self.assertEqual(rp.precision_of('2025'), 'year')
        self.assertEqual(rp.precision_of('2025-03'), 'month')
        self.assertEqual(rp.precision_of('2025-03-07'), 'day')
        self.assertIsNone(rp.precision_of('2025/03/07'))

    def test_KISTI_연단위_표기는_year_로_줄인다(self):
        """export 는 'YYYY-01-01' 로 적는다 — 그대로 두면 1월 1일 공개로 오해한다."""
        self.assertEqual(rp.normalize('2025-01-01', 'year'), '2025')
        self.assertEqual(rp.normalize('2025-01-01'), '2025-01-01')
        # 없는 정보를 만들어내지는 않는다
        self.assertEqual(rp.normalize('2025-03', 'day'), '2025-03')

    def test_상한(self):
        import datetime
        self.assertEqual(rp.upper_bound('2022'), datetime.date(2022, 12, 31))
        self.assertEqual(rp.upper_bound('2024-02'), datetime.date(2024, 2, 29))
        self.assertEqual(rp.upper_bound('2024-02-10'), datetime.date(2024, 2, 10))
        self.assertIsNone(rp.upper_bound('2024-13'))
        self.assertIsNone(rp.upper_bound(None))

    def test_record_date_는_arXiv_id_를_우선한다(self):
        """KISTI year 가 틀린 사례(2601.* 가 year=2025)를 id 의 YYMM 이 잡는다."""
        self.assertEqual(rp.record_date({'id': '2601.00001', 'date': '2025-01-01'}, 'year'),
                         ('2026-01', 'month', 'arxiv_id'))
        self.assertEqual(rp.record_date({'id': '10.1145/x', 'date': '2025-01-01'}, 'year'),
                         ('2025', 'year', 'db_date'))
        self.assertEqual(rp.record_date({'id': '10.1145/x', 'date': '2025-06-01'}, 'day'),
                         ('2025-06-01', 'day', 'db_date'))
        self.assertEqual(rp.record_date({'id': '10.1145/x'}, 'year'), (None, None, 'none'))


class PolicyRuleTest(unittest.TestCase):

    def setUp(self):
        self.p = rp.RetrievalPolicy(cutoff='2022-11-03', exclude_ids=['2211.01671', '10.1145/3793659'])

    def test_당일과_이후는_제외(self):
        self.assertTrue(self.p.allows_date('2022-11-02'))
        self.assertFalse(self.p.allows_date('2022-11-03'))
        self.assertFalse(self.p.allows_date('2022-11-04'))

    def test_월단위는_말일로_판정(self):
        self.assertTrue(self.p.allows_date('2022-10'))
        self.assertFalse(self.p.allows_date('2022-11'))   # 11-30 ≥ 11-03

    def test_연단위는_그_해_전체가_불확실(self):
        self.assertTrue(self.p.allows_date('2021'))
        self.assertFalse(self.p.allows_date('2022'))

    def test_날짜_불명은_제외(self):
        self.assertFalse(self.p.allows_date(None))
        self.assertFalse(self.p.allows_date(''))
        self.assertFalse(self.p.allows_date('unknown'))

    def test_제외_id_는_날짜와_무관(self):
        self.assertFalse(self.p.allows('2211.01671', '2000-01-01'))
        self.assertTrue(self.p.allows('2211.01670', '2000-01-01'))

    def test_cutoff_없는_정책은_전부_허용(self):
        p = rp.RetrievalPolicy()
        self.assertFalse(p.active)
        self.assertTrue(p.allows_date(None))
        p2 = rp.RetrievalPolicy(exclude_ids=['a'])
        self.assertTrue(p2.active)
        self.assertTrue(p2.allows_date(None))
        self.assertFalse(p2.allows('a', None))

    def test_cutoff_는_일단위만(self):
        with self.assertRaises(ValueError):
            rp.RetrievalPolicy(cutoff='2022-11')

    def test_to_dict_에_cutoff_와_제외가_남는다(self):
        d = self.p.to_dict()
        self.assertEqual(d['retrieval_cutoff_at'], '2022-11-03')
        self.assertEqual(d['exclude_ids'], ['10.1145/3793659', '2211.01671'])


class PolicyFileTest(unittest.TestCase):

    ROW = {'topic_id': 'physical-adversarial-attacks',
           'topic': 'Visual Adversarial Attacks and Defenses in the Physical World',
           'gt_first_public_at': '2022-11-03', 'gt_first_public_source': 'arxiv:2211.01671 v1 published (twin)',
           'retrieval_cutoff_at': '2022-11-03', 'exclude_ids': ['2211.01671', '10.1145/3793659'],
           'corpus_snapshot_id': 'kisti-2512 papers.parquet sha256:591b', 'status': 'ok'}

    def _write(self, rows):
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        with os.fdopen(fd, 'w') as f:
            f.write('# 주석 줄\n\n')
            for r in rows:
                f.write(json.dumps(r) + '\n')
        self.addCleanup(os.remove, path)
        return path

    def test_주석과_빈줄을_건너뛰고_읽는다(self):
        rows = rp.load_policy_rows(self._write([self.ROW]))
        self.assertEqual(len(rows), 1)

    def test_topic_id_로_고르고_topic_문자열로도_고른다(self):
        rows = [self.ROW, {**self.ROW, 'topic_id': 'other', 'topic': 'Other'}]
        self.assertIs(rp.select_row(rows, topic_id='other'), rows[1])
        self.assertIs(rp.select_row(rows, topic=self.ROW['topic']), rows[0])
        with self.assertRaises(KeyError):
            rp.select_row(rows, topic_id='nope')
        with self.assertRaises(KeyError):
            rp.select_row(rows, topic='no such topic')

    def test_행에서_정책이_만들어진다(self):
        p = rp.policy_from_row(self.ROW)
        self.assertEqual(p.cutoff.isoformat(), '2022-11-03')
        self.assertIn('10.1145/3793659', p.exclude_ids)
        self.assertEqual(p.topic_id, 'physical-adversarial-attacks')
        self.assertEqual(p.corpus_snapshot_id, self.ROW['corpus_snapshot_id'])

    def test_미확정_행은_명시적_override_없이는_거부(self):
        """불확실한 cutoff 로 조용히 돌면 누수 여부를 알 수 없는 산출물이 남는다."""
        row = {**self.ROW, 'status': 'needs_review', 'review_notes': ['일 단위 후보 없음']}
        with self.assertRaises(ValueError):
            rp.policy_from_row(row)
        p = rp.policy_from_row(row, cutoff_override='2022-11-01')
        self.assertEqual(p.cutoff.isoformat(), '2022-11-01')
        self.assertEqual(p.to_dict()['cutoff_override'], {'policy_file': '2022-11-03', 'cli': '2022-11-01'})

    def test_추가_제외는_합쳐진다(self):
        p = rp.policy_from_row(self.ROW, extra_exclude=['extra.1'])
        self.assertIn('extra.1', p.exclude_ids)

    def test_exclude_파일_형식(self):
        fd, path = tempfile.mkstemp(suffix='.txt')
        with os.fdopen(fd, 'w') as f:
            f.write('2211.01671\tgt:security/x\n# comment\n\n10.1145/3793659  # inline\n')
        self.addCleanup(os.remove, path)
        self.assertEqual(rp.load_exclude_file(path), ['2211.01671', '10.1145/3793659'])


class FingerprintTest(unittest.TestCase):

    def test_순서_무관_결정적(self):
        self.assertEqual(rp.fingerprint(['b', 'a']), rp.fingerprint(['a', 'b']))
        self.assertNotEqual(rp.fingerprint(['a']), rp.fingerprint(['a', 'b']))


if __name__ == '__main__':
    unittest.main()
