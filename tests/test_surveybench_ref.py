"""scripts/to_surveybench_ref.py — SurveyBench 채점용 ref.json 변환.

LLM judge 를 쓰지 않기로 했으므로 정량 수치가 나오는 경로는 이것뿐이다
(HANDOFF 남은작업 B). 여기서 어긋나면 **에러 없이 coverage 만 낮게 나오고**,
그걸 서베이 품질 문제로 오독하게 된다. 그래서 변환 규약을 고정한다.

채점 자체는 SurveyBench 의 test.py 를 import 해서 쓰므로 여기서 검증하지 않는다.
그쪽은 옆 저장소라 새 클론에 없을 수 있고, 있다면 그 코드가 정답이다.
"""
import unittest

from tests._loader import load_script

sb = load_script('to_surveybench_ref')


def survey(reference, detail=None):
    s = {'reference': reference}
    if detail is not None:
        s['reference_detail'] = detail
    return s


class BuildRefsTest(unittest.TestCase):

    def test_번호를_id_로_뒤집는다(self):
        refs = sb.build_refs(survey({'1': '2005.14165', '2': '1810.04805'}))
        self.assertEqual(set(refs), {'2005.14165', '1810.04805'})
        self.assertEqual(refs['2005.14165'], {'arxivId': '2005.14165'})

    def test_버전_접미사를_뗀다(self):
        """ref_bench 는 버전 없는 id 를 쓴다. 붙어 있으면 하나도 매칭되지 않는다."""
        refs = sb.build_refs(survey({'1': '2307.06435v9'}))
        self.assertIn('2307.06435', refs)
        self.assertEqual(refs['2307.06435']['arxivId'], '2307.06435')

    def test_같은_논문의_다른_버전은_한_키로_접힌다(self):
        """분모가 부풀면 coverage 가 실제보다 낮게 나온다."""
        refs = sb.build_refs(survey({'1': '2005.14165v1', '2': '2005.14165v3'}))
        self.assertEqual(len(refs), 1)

    def test_reference_detail_의_제목을_붙인다(self):
        refs = sb.build_refs(survey(
            {'1': '1706.03762v5'},
            {'1': {'id': '1706.03762v5', 'title': 'Attention is All you Need'}}))
        self.assertEqual(refs['1706.03762']['title'], 'Attention is All you Need')

    def test_detail_이_없어도_동작한다(self):
        """옛 산출물에는 reference_detail 이 없다. title 은 채점에 쓰이지 않는다."""
        refs = sb.build_refs(survey({'1': '2005.14165'}))
        self.assertEqual(refs['2005.14165'], {'arxivId': '2005.14165'})

    def test_detail_이_null_이어도_죽지_않는다(self):
        s = {'reference': {'1': '2005.14165'}, 'reference_detail': None}
        self.assertIn('2005.14165', sb.build_refs(s))


class LegacyIdTest(unittest.TestCase):
    """구형 arXiv id 는 채점기의 날짜 파싱이 안 돼 분모에서 조용히 빠진다.

    스크립트는 그 개수를 보고한다 — 안 보이면 낮은 coverage 의 원인을 못 찾는다.
    """

    def test_신형_id_를_알아본다(self):
        for pid in ('2005.14165', '1810.04805', '2412.12345'):
            self.assertTrue(sb.MODERN_ID.match(pid), pid)

    def test_구형_id_를_걸러낸다(self):
        for pid in ('cs/0701001', 'math.GT/0309136'):
            self.assertFalse(sb.MODERN_ID.match(pid), pid)


class BenchCutoffTest(unittest.TestCase):
    """ref_bench 의 최신 논문. 이보다 새 인용은 채점 분모에서 빠진다."""

    def test_최신_연월을_찾는다(self):
        ym, seq = sb.bench_cutoff(['2005.14165', '2407.00001', '2312.09999'])
        self.assertEqual(ym, '2024-07')

    def test_같은_달이면_일련번호로_가른다(self):
        ym, seq = sb.bench_cutoff(['2407.00001', '2407.09999'])
        self.assertEqual((ym, seq), ('2024-07', 9999))

    def test_구형_id_만_있으면_None(self):
        self.assertEqual(sb.bench_cutoff(['cs/0701001']), (None, None))


if __name__ == '__main__':
    unittest.main()
