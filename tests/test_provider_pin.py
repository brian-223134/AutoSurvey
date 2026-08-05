"""main.py — provider 핀과 모델의 정합 검사.

모델은 `--model` 인자로, provider 는 `AUTOSURVEY_PROVIDER` 환경변수로 들어온다.
서로 다른 곳에서 오는데 provider tag 는 **모델마다 다르다.** `.env` 에 deepseek 용
`parasail/fp8` 을 둔 채 haiku 로 돌리면(haiku 는 amazon-bedrock 하나뿐)
allow_fallbacks=false 때문에 요청이 전부 실패한다. DB 로딩(수 분) 전에 잡아야 한다.

네트워크를 쓰지 않도록 requests.get 을 대체한다.
"""
import os
import unittest
from unittest import mock

from tests._loader import load_main

main = load_main()


def fake_endpoints(*tags):
    """OpenRouter /endpoints 응답 흉내."""
    class R:
        @staticmethod
        def json():
            return {'data': {'endpoints': [{'tag': t} for t in tags]}}
    return R()


class ProviderPinTest(unittest.TestCase):

    def setUp(self):
        self._saved = os.environ.pop('AUTOSURVEY_PROVIDER', None)

    def tearDown(self):
        if self._saved is None:
            os.environ.pop('AUTOSURVEY_PROVIDER', None)
        else:
            os.environ['AUTOSURVEY_PROVIDER'] = self._saved

    def test_핀이_없으면_조회조차_하지_않는다(self):
        with mock.patch.object(main.requests, 'get') as g:
            main.check_provider_pin('anthropic/claude-3-haiku')
            g.assert_not_called()

    def test_맞는_조합은_통과(self):
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8'
        with mock.patch.object(main.requests, 'get',
                               return_value=fake_endpoints('parasail/fp8', 'novita/fp8')):
            main.check_provider_pin('deepseek/deepseek-v4-flash-0731')  # 예외 없음

    def test_어긋난_조합은_중단(self):
        """haiku 에는 parasail/fp8 이 없다. 실제로 확인한 조합이다."""
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8'
        with mock.patch.object(main.requests, 'get',
                               return_value=fake_endpoints('amazon-bedrock')):
            with self.assertRaises(RuntimeError) as cm:
                main.check_provider_pin('anthropic/claude-3-haiku')
        msg = str(cm.exception)
        self.assertIn('parasail/fp8', msg)
        self.assertIn('amazon-bedrock', msg)   # 쓸 수 있는 tag 를 알려줘야 한다

    def test_여러_개_중_하나만_없어도_중단(self):
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8,없는것/fp8'
        with mock.patch.object(main.requests, 'get',
                               return_value=fake_endpoints('parasail/fp8')):
            with self.assertRaises(RuntimeError):
                main.check_provider_pin('deepseek/deepseek-v4-flash-0731')

    def test_조회_실패는_막지_않는다(self):
        """검증 때문에 실행을 못 하면 곤란하다. 네트워크 장애는 통과시킨다."""
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8'
        with mock.patch.object(main.requests, 'get',
                               side_effect=OSError('네트워크 없음')):
            main.check_provider_pin('deepseek/deepseek-v4-flash-0731')  # 예외 없음

    def test_응답_형식이_이상해도_막지_않는다(self):
        os.environ['AUTOSURVEY_PROVIDER'] = 'parasail/fp8'
        class Bad:
            @staticmethod
            def json():
                return {'error': 'nope'}
        with mock.patch.object(main.requests, 'get', return_value=Bad()):
            main.check_provider_pin('deepseek/deepseek-v4-flash-0731')  # 예외 없음


if __name__ == '__main__':
    unittest.main()
