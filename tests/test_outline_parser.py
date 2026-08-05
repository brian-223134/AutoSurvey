"""src/agents/outline_writer.py — 아웃라인 파싱과 서브섹션 개수 통제.

파서는 한 번 깨진 적이 있다. 원본이 `outline.split('Subsection 1: ')[1]` 처럼
정확한 문자열 일치에 의존해서, deepseek 이 `**Subsection 1:**` 로 답하자
IndexError 로 즉사했다(커밋 8bfbc43). 정규식 기반으로 바꿨지만 그걸 지키는
장치가 없었으므로 여기서 고정한다.
"""
import unittest

from tests._loader import ROOT  # noqa: F401  (sys.path 설정)
from src.agents.outline_writer import outlineWriter
from src.prompt import SUBSECTION_OUTLINE_PROMPT


def writer(subsection_num=0):
    # APIModel 은 생성만으로는 네트워크를 쓰지 않고, database 는 파싱에 안 쓰인다.
    return outlineWriter(model='m', api_key='k', api_url='u', database=None,
                         subsection_num=subsection_num)


SECTION_OUTLINE = 'Title: A Survey of X\nSection 1: Intro\nDescription 1: 서론'


class PromptFidelityTest(unittest.TestCase):
    """기본값에서 원본 프롬프트가 글자 단위로 복원되는가."""

    def test_기본값은_원본_문구_그대로(self):
        filled = SUBSECTION_OUTLINE_PROMPT.replace(
            '[SUBSECTION NUM]', writer()._subsection_num_phrase())
        self.assertIn('containing several subsections', filled)
        self.assertNotIn('[SUBSECTION NUM]', filled)

    def test_값을_주면_개수가_박힌다(self):
        filled = SUBSECTION_OUTLINE_PROMPT.replace(
            '[SUBSECTION NUM]', writer(4)._subsection_num_phrase())
        self.assertIn('containing exactly 4 subsections', filled)
        self.assertNotIn('[SUBSECTION NUM]', filled)

    def test_placeholder_가_템플릿에_실제로_있다(self):
        """치환 대상이 사라지면 개수 지시가 조용히 무시된다."""
        self.assertIn('[SUBSECTION NUM]', SUBSECTION_OUTLINE_PROMPT)


class SubsectionCapTest(unittest.TestCase):

    SUB = ('Subsection 1: A\nDescription 1: a\n\nSubsection 2: B\nDescription 2: b\n\n'
           'Subsection 3: C\nDescription 3: c\n\nSubsection 4: D\nDescription 4: d\n\n'
           'Subsection 5: E\nDescription 5: e\n\nSubsection 6: F\nDescription 6: f')

    def test_상한이_없으면_전부_남는다(self):
        out = writer().process_outlines(SECTION_OUTLINE, [self.SUB])
        self.assertEqual(out.count('### '), 6)

    def test_상한을_넘으면_잘린다(self):
        out = writer(4).process_outlines(SECTION_OUTLINE, [self.SUB])
        self.assertEqual(out.count('### '), 4)

    def test_앞에서부터_남긴다(self):
        """아웃라인은 논리 순서로 생성되므로 뒤쪽을 버린다.

        출력은 '### 1.3 C' 형태이므로 원문 'Subsection 3' 로 검사하면
        항상 통과하는 헛단언이 된다. 실제 헤딩 번호로 본다.
        """
        out = writer(2).process_outlines(SECTION_OUTLINE, [self.SUB])
        self.assertIn('### 1.1 A', out)
        self.assertIn('### 1.2 B', out)
        self.assertNotIn('### 1.3', out)
        self.assertNotIn('C', out.replace('Description', ''))

    def test_상한보다_적으면_그대로(self):
        few = 'Subsection 1: A\nDescription 1: a'
        out = writer(4).process_outlines(SECTION_OUTLINE, [few])
        self.assertEqual(out.count('### '), 1)

    def test_잘린_뒤에도_제목과_설명이_짝을_유지한다(self):
        """이름만 자르고 설명을 안 자르면 zip 에서 밀려 엉뚱한 설명이 붙는다."""
        out = writer(2).process_outlines(SECTION_OUTLINE, [self.SUB])
        self.assertIn('### 1.1 A\nDescription: a', out)
        self.assertIn('### 1.2 B\nDescription: b', out)


class ParserRobustnessTest(unittest.TestCase):
    """모델이 형식을 조금씩 어겨도 살아남아야 한다."""

    def test_마크다운_장식(self):
        w = writer()
        t, s, d = w.extract_title_sections_descriptions(
            '**Title:** A Survey\n### Section 1: Intro\n**Description 1:** 서론')
        self.assertEqual(t, 'A Survey')
        self.assertEqual(s, ['Intro'])
        self.assertEqual(d, ['서론'])

    def test_구분자가_점이나_하이픈(self):
        w = writer()
        _, s, _ = w.extract_title_sections_descriptions(
            'Title: T\nSection 1 - Intro\nDescription 1 . 서론')
        self.assertEqual(s, ['Intro'])

    def test_Title_줄이_없으면_첫_줄을_쓴다(self):
        w = writer()
        t, s, _ = w.extract_title_sections_descriptions(
            'A Survey of X\nSection 1: Intro\nDescription 1: 서론')
        self.assertEqual(t, 'A Survey of X')

    def test_Section_을_못_찾으면_원본을_담아_에러(self):
        """조용히 빈 아웃라인으로 진행하면 뒤에서 엉뚱한 곳이 터진다."""
        w = writer()
        with self.assertRaises(RuntimeError) as cm:
            w.extract_title_sections_descriptions('아무 형식도 아닌 응답')
        self.assertIn('아무 형식도 아닌 응답', str(cm.exception))

    def test_Subsection_이_Section_으로_오인되지_않는다(self):
        """SECTION_RE 의 (?<!Sub) 가 하는 일."""
        w = writer()
        _, s, _ = w.extract_title_sections_descriptions(
            'Title: T\nSection 1: Intro\nDescription 1: d\nSubsection 1: Sub\n')
        self.assertEqual(s, ['Intro'])

    def test_설명이_빠져도_길이가_어긋나지_않는다(self):
        """원본은 여기서 두 리스트 길이가 달라져 IndexError 를 냈다."""
        w = writer()
        subs, descs = w.extract_subsections_subdescriptions(
            'Subsection 1: A\nDescription 1: a\nSubsection 2: B\n')
        self.assertEqual(len(subs), len(descs))
        self.assertEqual(descs[1], '')

    def test_번호_순서가_뒤섞여도_번호로_묶인다(self):
        w = writer()
        subs, descs = w.extract_subsections_subdescriptions(
            'Subsection 2: B\nDescription 2: b\nSubsection 1: A\nDescription 1: a')
        self.assertEqual(subs, ['A', 'B'])
        self.assertEqual(descs, ['a', 'b'])


if __name__ == '__main__':
    unittest.main()
