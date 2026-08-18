"""최종 실패한 요청이 조용히 산출물로 흘러가지 않는지 검사한다.

2026-08-18 본편 B 실행에서 429가 재시도를 소진해 __req 가 None 을 돌려줬고,
그 None 이 토큰 카운터에서 TypeError 를 냈다. 죽은 곳이 워커 스레드라
본 실행은 계속됐고, 결과는 섹션 하나가 통째로 빈 서베이였다. 밖에서는 조용하다.
"""
import os
import unittest
from unittest import mock

from src.model import APIModel


def _model():
    return APIModel('m', 'k', 'https://example.invalid/v1/chat/completions')


class BatchChatFailure(unittest.TestCase):
    def test_batch_chat_raises_when_a_request_finally_fails(self):
        """None 이 하나라도 섞이면 조용히 통과시키지 않는다."""
        m = _model()
        with mock.patch.object(APIModel, '_APIModel__req',
                               side_effect=['ok', None, 'ok']):
            with self.assertRaises(RuntimeError) as cm:
                m.batch_chat(['a', 'b', 'c'])
        self.assertIn('최종 실패', str(cm.exception))

    def test_batch_chat_passes_when_all_succeed(self):
        m = _model()
        with mock.patch.object(APIModel, '_APIModel__req', return_value='ok'):
            self.assertEqual(m.batch_chat(['a', 'b']), ['ok', 'ok'])

    def test_failed_counter_starts_at_zero(self):
        self.assertEqual(_model().failed, 0)


class Backoff(unittest.TestCase):
    def test_429_waits_much_longer_than_other_errors(self):
        """429는 초 단위로 풀리지 않는다. 다른 에러와 같은 백오프를 쓰면 안 된다."""
        import src.model as M
        delays = []
        with mock.patch.object(M.time, 'sleep', delays.append), \
             mock.patch.object(M.requests, 'post') as post:
            post.return_value = mock.Mock(status_code=429, text='rate limited')
            _model()._APIModel__req('x', temperature=1, max_try=2)
        self.assertTrue(all(d >= 10 for d in delays), delays)

    def test_backoff_is_jittered(self):
        """지터가 없으면 동시 요청이 같은 순간에 함께 깨어나 다시 몰린다.

        재시도가 소진된 실제 원인이 이것이었다.
        """
        import src.model as M
        runs = []
        for _ in range(6):
            delays = []
            with mock.patch.object(M.time, 'sleep', delays.append), \
                 mock.patch.object(M.requests, 'post') as post:
                post.return_value = mock.Mock(status_code=429, text='rate limited')
                _model()._APIModel__req('x', temperature=1, max_try=1)
            runs.append(delays[0])
        self.assertGreater(len(set(runs)), 1, f'백오프가 고정값이다: {runs}')


class RetryLimitIsConfigurable(unittest.TestCase):
    def test_env_overrides_default(self):
        import importlib
        import src.model as M
        with mock.patch.dict(os.environ, {'AUTOSURVEY_MAX_RETRY': '3'}):
            importlib.reload(M)
            self.assertEqual(M.MAX_RETRY, 3)
        importlib.reload(M)


if __name__ == '__main__':
    unittest.main()
