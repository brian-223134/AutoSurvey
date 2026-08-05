"""src/model.py — 페이로드 구성과 잘림 집계.

여기서 지켜야 할 핵심은 **환경변수를 주지 않으면 원본 AutoSurvey 와 똑같은 요청이
나가야 한다**는 것이다. 이 저장소를 baseline 으로 쓰는 근거가 거기 있다.
"""
import os
import unittest

from tests._loader import ROOT  # noqa: F401  (sys.path 설정)
from src.model import APIModel

ENV_KEYS = ('AUTOSURVEY_REASONING', 'AUTOSURVEY_PROVIDER')


class ExtraPayloadTest(unittest.TestCase):

    def setUp(self):
        self._saved = {k: os.environ.pop(k, None) for k in ENV_KEYS}
        self.model = APIModel('m', 'k', 'u')

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_기본값은_아무것도_추가하지_않는다(self):
        """원본 동작 보장. 이게 깨지면 baseline 이 아니게 된다."""
        self.assertEqual(self.model._extra_payload(), {})

    def test_reasoning_off(self):
        os.environ['AUTOSURVEY_REASONING'] = 'off'
        self.assertEqual(self.model._extra_payload(),
                         {'reasoning': {'enabled': False}})

    def test_reasoning_는_여러_표기를_받는다(self):
        for v in ('off', 'FALSE', '0', 'disabled'):
            os.environ['AUTOSURVEY_REASONING'] = v
            self.assertIn('reasoning', self.model._extra_payload(), f'값={v}')

    def test_reasoning_on_이면_보내지_않는다(self):
        # 켜는 것은 제공자 기본값에 맡긴다. 명시적으로 enabled=True 를 보내지 않는다.
        os.environ['AUTOSURVEY_REASONING'] = 'on'
        self.assertEqual(self.model._extra_payload(), {})

    def test_provider_핀은_fallback_을_끈다(self):
        """allow_fallbacks 가 True 면 붐빌 때 다른 quantization 으로 새어나간다."""
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8'
        got = self.model._extra_payload()
        self.assertEqual(got['provider']['order'], ['parasail/fp8'])
        self.assertIs(got['provider']['allow_fallbacks'], False)

    def test_provider_는_쉼표로_여러_개(self):
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8, novita/fp8'
        self.assertEqual(self.model._extra_payload()['provider']['order'],
                         ['parasail/fp8', 'novita/fp8'])

    def test_provider_공백만_있으면_무시(self):
        os.environ['AUTOSURVEY_PROVIDER'] = '   '
        self.assertEqual(self.model._extra_payload(), {})

    def test_둘_다_설정되면_둘_다_나간다(self):
        os.environ['AUTOSURVEY_REASONING'] = 'off'
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8'
        got = self.model._extra_payload()
        self.assertIn('reasoning', got)
        self.assertIn('provider', got)


class TruncationCounterTest(unittest.TestCase):

    def test_초기값은_0(self):
        self.assertEqual(APIModel('m', 'k', 'u').truncated, 0)

    def test_누적된다(self):
        m = APIModel('m', 'k', 'u')
        for _ in range(3):
            m._note_truncation()
        self.assertEqual(m.truncated, 3)

    def test_병렬_증가에도_유실되지_않는다(self):
        """batch_chat 이 스레드로 도므로 카운터가 락으로 보호돼야 한다."""
        import threading
        m = APIModel('m', 'k', 'u')
        threads = [threading.Thread(target=lambda: [m._note_truncation()
                                                    for _ in range(200)])
                   for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(m.truncated, 8 * 200)


if __name__ == '__main__':
    unittest.main()
