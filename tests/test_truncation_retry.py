"""max_tokens 가드에 걸린 응답(finish_reason=length)의 처리.

2026-09-07 temp 0.6 본편: draft 호출의 약 30%가 8K 가드까지 갔다(반복 루프). 가드는 시간·비용을
묶을 뿐 잘린 초안이 refine 으로 흘러가는 것은 못 막는다. 정상 호출은 가드에 닿을 수 없으므로
걸린 응답은 버리고 새 샘플을 받는 것이 맞다. 단 가드가 없으면(원본 동작) 그대로 받아들인다.
"""
import unittest
from unittest import mock

import src.model as model_mod
from src.model import APIModel


def _resp(content, finish_reason):
    r = mock.Mock()
    r.status_code = 200
    r.json.return_value = {'choices': [{'finish_reason': finish_reason,
                                        'message': {'content': content}}],
                           'usage': {'prompt_tokens': 10, 'completion_tokens': 5}}
    return r


def _model():
    return APIModel('m', 'k', 'https://example.invalid/v1/chat/completions')


class TruncationRetry(unittest.TestCase):

    def test_가드가_켜져_있으면_잘린_응답은_버리고_다시_받는다(self):
        m = _model()
        with mock.patch.object(model_mod, 'RETRY_TRUNCATED', True), \
             mock.patch.object(model_mod.time, 'sleep'), \
             mock.patch.object(model_mod.requests, 'post',
                               side_effect=[_resp('loop loop loop', 'length'), _resp('fine', 'stop')]):
            self.assertEqual(m.chat('q'), 'fine')
        self.assertEqual(m.truncation_retries, 1)
        self.assertEqual(m.truncated, 0, '버린 응답은 출력 잘림으로 세지 않는다')
        self.assertEqual(m.retry_count, 1, '재청구된 요청이므로 재시도로도 센다')

    def test_가드가_꺼져_있으면_원본처럼_잘린_내용을_그대로_쓴다(self):
        m = _model()
        with mock.patch.object(model_mod, 'RETRY_TRUNCATED', False), \
             mock.patch.object(model_mod.requests, 'post', side_effect=[_resp('cut', 'length')]) as post:
            self.assertEqual(m.chat('q'), 'cut')
        self.assertEqual(post.call_count, 1)
        self.assertEqual(m.truncated, 1)
        self.assertEqual(m.truncation_retries, 0)

    def test_재시도를_다_쓰면_마지막_잘린_내용을_받아들이고_잘림으로_센다(self):
        """None 을 돌려주면 writer 스레드가 죽는다. 부분 산출이라도 파이프라인은 살린다."""
        m = _model()
        with mock.patch.object(model_mod, 'RETRY_TRUNCATED', True), \
             mock.patch.object(model_mod.time, 'sleep'), \
             mock.patch.object(model_mod.requests, 'post',
                               side_effect=[_resp(f'cut{i}', 'length') for i in range(5)]) as post:
            self.assertEqual(m.chat('q'), 'cut4')      # chat() 은 max_try=5
        self.assertEqual(post.call_count, 5)
        self.assertEqual(m.truncation_retries, 4)
        self.assertEqual(m.truncated, 1)
        self.assertEqual(m.failed, 0, '잘림은 최종 실패가 아니다')

    def test_기본값은_MAX_TOKENS_유무를_따른다(self):
        import importlib
        import os
        saved = {k: os.environ.pop(k, None) for k in ('AUTOSURVEY_MAX_TOKENS', 'AUTOSURVEY_RETRY_TRUNCATED')}
        try:
            self.assertFalse(importlib.reload(model_mod).RETRY_TRUNCATED)
            os.environ['AUTOSURVEY_MAX_TOKENS'] = '8192'
            self.assertTrue(importlib.reload(model_mod).RETRY_TRUNCATED)
            os.environ['AUTOSURVEY_RETRY_TRUNCATED'] = '0'
            self.assertFalse(importlib.reload(model_mod).RETRY_TRUNCATED, '명시적으로 끄면 가드가 있어도 꺼진다')
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            importlib.reload(model_mod)


if __name__ == '__main__':
    unittest.main()
