"""main.py — 정책 인자 해석과 저장 직전 검증.

정책 파일의 미확정 행은 DB 로딩(수 분) 전에 거부돼야 하고, 최종 참고문헌이 허용 집합 밖이면
저장하지 않아야 한다.
"""
import json
import os
import tempfile
import types
import unittest

from tests._loader import load_main

main = load_main()


def args(**kw):
    base = dict(topic='', topic_policy='', topic_id='', retrieval_cutoff='', exclude_ids='')
    base.update(kw)
    return types.SimpleNamespace(**base)


class ResolvePolicyTest(unittest.TestCase):

    def _policy_file(self, rows):
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        with os.fdopen(fd, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        self.addCleanup(os.remove, path)
        return path

    ROW = {'topic_id': 'x', 'topic': 'Topic X', 'retrieval_cutoff_at': '2023-08-21',
           'exclude_ids': ['2308.10792'], 'status': 'ok'}

    def test_인자_없으면_정책_없음(self):
        self.assertIsNone(main.resolve_retrieval_policy(args(topic='t')))

    def test_cutoff_만으로_정책(self):
        p = main.resolve_retrieval_policy(args(topic='t', retrieval_cutoff='2024-01-01'))
        self.assertEqual(p.cutoff.isoformat(), '2024-01-01')
        self.assertEqual(p.gt_first_public_source, 'cli:--retrieval_cutoff')

    def test_잘못된_cutoff_형식은_즉시_실패(self):
        with self.assertRaises(ValueError):
            main.resolve_retrieval_policy(args(topic='t', retrieval_cutoff='2024-01'))

    def test_정책_파일_topic_id(self):
        pf = self._policy_file([self.ROW])
        p = main.resolve_retrieval_policy(args(topic='Topic X', topic_policy=pf, topic_id='x'))
        self.assertEqual(p.cutoff.isoformat(), '2023-08-21')
        self.assertIn('2308.10792', p.exclude_ids)

    def test_정책_파일_topic_문자열_일치(self):
        pf = self._policy_file([self.ROW])
        p = main.resolve_retrieval_policy(args(topic='Topic X', topic_policy=pf))
        self.assertEqual(p.topic_id, 'x')

    def test_없는_topic_은_DB_로딩_전에_실패(self):
        pf = self._policy_file([self.ROW])
        with self.assertRaises(RuntimeError):
            main.resolve_retrieval_policy(args(topic='Other', topic_policy=pf))

    def test_미확정_행은_거부하되_override_는_허용(self):
        pf = self._policy_file([{**self.ROW, 'status': 'needs_review'}])
        with self.assertRaises(ValueError):
            main.resolve_retrieval_policy(args(topic='Topic X', topic_policy=pf, topic_id='x'))
        p = main.resolve_retrieval_policy(args(topic='Topic X', topic_policy=pf, topic_id='x',
                                               retrieval_cutoff='2023-08-01'))
        self.assertEqual(p.cutoff.isoformat(), '2023-08-01')


class VerifyReferencesTest(unittest.TestCase):

    def test_정책_없으면_통과(self):
        db = types.SimpleNamespace(policy=None)
        main.verify_references_allowed({1: 'a'}, db)

    def test_허용_밖_참고문헌이_있으면_중단(self):
        db = types.SimpleNamespace(policy=object(), is_allowed=lambda i: i != 'bad')
        main.verify_references_allowed({1: 'ok'}, db)
        with self.assertRaises(RuntimeError):
            main.verify_references_allowed({1: 'ok', 2: 'bad'}, db)


if __name__ == '__main__':
    unittest.main()
