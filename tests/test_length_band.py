"""scripts/check_survey.py — 분량 구간 판정.

구간은 실측으로 잡았다 (README §4.4). 하드 컷이 아니라 경고이므로 '판정이
바뀌는 경계'가 곧 사양이다. 숫자를 조정하면 이 테스트가 먼저 알려준다.
"""
import unittest

from tests._loader import load_script

cs = load_script('check_survey')


class BandBoundaryTest(unittest.TestCase):

    def band(self, words):
        return cs.length_band(words)[0]

    def test_경계값(self):
        cases = [
            (11_999, '짧음'),
            (12_000, '표준'),
            (25_000, '표준'),
            (25_001, '광범위'),
            (50_000, '광범위'),
            (50_001, '초과'),
            (80_000, '초과'),
            (80_001, '비대'),
        ]
        for words, expected in cases:
            with self.subTest(words=words):
                self.assertEqual(self.band(words), expected)

    def test_광범위는_경고하지_않는다(self):
        """주제가 넓으면 25k~50k 는 정당하다. 여기서 경고하면 잔소리가 된다."""
        _, warn = cs.length_band(30_000)
        self.assertEqual(warn, '')

    def test_표준도_경고하지_않는다(self):
        self.assertEqual(cs.length_band(18_000)[1], '')

    def test_비대는_경고한다(self):
        band, warn = cs.length_band(84_012)
        self.assertEqual(band, '비대')
        self.assertTrue(warn)
        self.assertIn('100페이지', warn)

    def test_짧아도_경고한다(self):
        self.assertTrue(cs.length_band(10_194)[1])


class RealOutputTest(unittest.TestCase):
    """실제 산출물이 기대한 구간에 떨어지는가."""

    def test_실측값_판정(self):
        cases = [
            (25_503, '광범위'),   # haiku/Evaluation of LLMs
            (27_409, '광범위'),   # haiku/In-context Learning
            (30_530, '광범위'),   # deepseek-smoke
            (84_012, '비대'),     # deepseek-v4-pro — 약 105페이지
            (10_194, '짧음'),     # haiku-smoke (축소 설정이라 정상)
        ]
        for words, expected in cases:
            with self.subTest(words=words):
                self.assertEqual(cs.length_band(words)[0], expected)

    def test_페이지_환산(self):
        """저자 산출물 기준 약 800단어/페이지."""
        self.assertEqual(cs.WORDS_PER_PAGE, 800)
        # 84,012단어 -> 약 105페이지. 사용자가 기억한 88k/100+p 사례와 같은 규모.
        self.assertAlmostEqual(84_012 / cs.WORDS_PER_PAGE, 105, delta=1)


if __name__ == '__main__':
    unittest.main()
