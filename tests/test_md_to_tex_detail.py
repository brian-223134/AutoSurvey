"""참고문헌 집계가 유니코드 경고 때문에 깨지지 않는지 검사한다.

2026-08-18: 잔여 비ASCII 경고를 넣으면서 메시지 문자열을 detail 이라는 이름에
담았는데, 그게 아래 참고문헌 집계가 쓰는 detail(dict)을 덮어썼다.
잔여 문자가 있을 때만 터지므로 RAG 편에서는 안 보이다가 3DGS 편에서 드러났다.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'md_to_tex.py')

spec = importlib.util.spec_from_file_location('md_to_tex', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class UnhandledUnicode(unittest.TestCase):
    def test_known_symbols_are_not_reported(self):
        self.assertEqual(mod.unhandled_unicode('α ω ℓ → ² and é—“”'), {})

    def test_unknown_symbol_is_reported(self):
        self.assertEqual(mod.unhandled_unicode('a ☃ b ☃'), {'☃': 2})

    def test_cjk_is_reported(self):
        """pdflatex 은 CJK 를 추가 패키지 없이 찍지 못한다. 경고가 맞다."""
        self.assertEqual(mod.unhandled_unicode('한글'), {'한': 1, '글': 1})

    def test_greek_table_is_not_built_by_codepoint_arithmetic(self):
        """그리스 블록에는 ς 와 예약된 빈 자리가 있어 오프셋이 σ 부터 어긋난다."""
        self.assertEqual(mod.UNICODE_FIXES['σ'], r'$\sigma$')
        self.assertEqual(mod.UNICODE_FIXES['ω'], r'$\omega$')
        self.assertEqual(mod.UNICODE_FIXES['Ω'], r'$\Omega$')


# 나머지 테스트는 외부 도구 없이 돈다. 이 두 개만 pandoc 이 필요하므로,
# 없으면 건너뛴다 — 테스트 전체가 pandoc 설치를 요구하게 만들지 않는다.
@unittest.skipUnless(shutil.which('pandoc'), 'pandoc 없음')
class ReferenceCountSurvivesUnicodeWarning(unittest.TestCase):
    """잔여 비ASCII 가 있어도 참고문헌 집계가 정상 동작해야 한다."""

    def _run(self, body):
        d = tempfile.mkdtemp()
        md = os.path.join(d, 'T.md')
        with open(md, 'w', encoding='utf-8') as f:
            f.write('# T\n\n## 1 A\n\n' + body + ' [1]\n\n'
                    '## References\n\n[1] Some Paper\n')
        with open(os.path.join(d, 'T.json'), 'w', encoding='utf-8') as f:
            json.dump({'reference_detail': {
                '1': {'id': '2401.00001', 'title': 'Some Paper',
                      'date': '2024-01-01', 'url': 'https://arxiv.org/abs/2401.00001'}}}, f)
        p = subprocess.run([sys.executable, SCRIPT, md],
                           capture_output=True, text=True, cwd=ROOT)
        return p

    def test_with_leftover_unicode(self):
        p = self._run('본문에 알 수 없는 기호 ☃ 가 있다.')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('치환표에 없는 비ASCII', p.stdout)
        self.assertIn('arXiv ID/링크 1개', p.stdout)   # ← 덮어쓰기 회귀

    def test_without_leftover_unicode(self):
        p = self._run('평범한 본문이다.')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('arXiv ID/링크 1개', p.stdout)


if __name__ == '__main__':
    unittest.main()
