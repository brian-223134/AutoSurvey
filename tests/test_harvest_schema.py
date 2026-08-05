"""scripts/harvest_arxiv.py — 배포 DB 표기 규약 재현.

수집 결과가 배포 DB와 같은 표기여야 한다. 어긋나면 에러 없이 코퍼스가 두 층으로
갈라진다. 규약은 실측으로 역산했다 (scripts/check_oai_schema.py 상단).

특히 `date` 는 v1 제출일이어야 한다. arXiv 형식의 <created> 는 '최신 버전' 날짜라
그대로 쓰면 개정본이 몇 년씩 어긋난다 — 2208.01711 은 2022-08-02 여야 하는데
<created> 는 2023-12-12 이다.
"""
import unittest

from tests._loader import load_script

hv = load_script('harvest_arxiv')

RAW_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
 <ListRecords>
  <record>
   <header><identifier>oai:arXiv.org:2008.06570</identifier></header>
   <metadata>
    <arXivRaw xmlns="http://arxiv.org/OAI/arXivRaw/">
     <id>2008.06570</id>
     <version version="v1"><date>Fri, 14 Aug 2020 20:46:38 GMT</date></version>
     <version version="v2"><date>Sat, 30 Jan 2021 23:34:27 GMT</date></version>
     <title>Some Title</title>
     <categories>cs.LG stat.ML</categories>
     <abstract>We introduce a variant of the R\\'enyi entropy
that aligns it with the H\\"older mean.</abstract>
    </arXivRaw>
   </metadata>
  </record>
 </ListRecords>
</OAI-PMH>'''

ARXIV_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
 <ListRecords>
  <record>
   <header><identifier>oai:arXiv.org:2008.06570</identifier></header>
   <metadata>
    <arXiv xmlns="http://arxiv.org/OAI/arXiv/">
     <id>2008.06570</id>
     <created>2021-01-30</created>
     <authors>
      <author><keyname>Schölkopf</keyname><forenames>Bernhard</forenames></author>
      <author><keyname>Peláez-Moreno</keyname><forenames>Carmen</forenames></author>
     </authors>
     <title>Uni-Perceiver v2: A Generalist Model</title>
     <categories>cs.LG stat.ML</categories>
    </arXiv>
   </metadata>
  </record>
 </ListRecords>
</OAI-PMH>'''


class VersionDateTest(unittest.TestCase):

    def test_v1_날짜_파싱(self):
        self.assertEqual(
            hv.parse_version_date('Fri, 14 Aug 2020 20:46:38 GMT'), '2020-08-14')

    def test_한자리_일(self):
        self.assertEqual(
            hv.parse_version_date('Tue, 2 Aug 2022 19:47:43 GMT'), '2022-08-02')

    def test_모든_달(self):
        for mon, num in [('Jan', '01'), ('Jun', '06'), ('Dec', '12')]:
            self.assertEqual(
                hv.parse_version_date(f'Mon, 5 {mon} 2021 00:00:00 GMT'),
                f'2021-{num}-05')

    def test_파싱_실패는_빈_문자열(self):
        self.assertEqual(hv.parse_version_date('garbage'), '')
        self.assertEqual(hv.parse_version_date(None), '')


class TitleSanitizeTest(unittest.TestCase):
    """배포 DB 537,665편의 제목에 이 문자들이 하나도 없다(초록엔 ':' 가 22%)."""

    def test_금지문자가_공백으로(self):
        got = 'Uni-Perceiver v2: A Generalist'.translate(hv.TITLE_TRANS)
        self.assertNotIn(':', got)
        self.assertIn('v2  A Generalist', got)

    def test_전체_집합(self):
        got = 'a<b>c:d"e/f|g?h*i#j'.translate(hv.TITLE_TRANS)
        for ch in '<>:"/|?*#':
            self.assertNotIn(ch, got)

    def test_백슬래시는_남긴다(self):
        """배포 DB 제목의 0.368% 에 백슬래시가 있다. 제거 대상이 아니다."""
        self.assertIn('\\', r'Erd\H{o}s'.translate(hv.TITLE_TRANS))


class ParseRawTest(unittest.TestCase):

    def setUp(self):
        recs, _ = hv.parse_page(RAW_XML, 'arXivRaw')
        self.rec = recs[0]

    def test_최신_버전_번호(self):
        self.assertEqual(self.rec['v'], 2)

    def test_date_는_v1_제출일(self):
        """<created>(2021-01-30)가 아니라 v1 날짜여야 한다."""
        self.assertEqual(self.rec['date'], '2020-08-14')

    def test_cat_은_첫번째_카테고리(self):
        self.assertEqual(self.rec['cat'], 'cs.LG')

    def test_초록의_TeX_escape_보존(self):
        """배포 DB 초록의 14.4% 에 TeX escape 가 있다. 유니코드로 바꾸면 안 된다."""
        self.assertIn(r"R\'enyi", self.rec['abs'])


class ParseArxivTest(unittest.TestCase):

    def setUp(self):
        recs, _ = hv.parse_page(ARXIV_XML, 'arXiv')
        self.rec = recs[0]

    def test_저자는_forenames_keyname_순(self):
        self.assertEqual(self.rec['authors'],
                         ['Bernhard Schölkopf', 'Carmen Peláez-Moreno'])

    def test_저자_유니코드가_깨지지_않는다(self):
        """requests 가 charset 미지정 XML 을 latin-1 로 읽으면 SchÃ¶lkopf 가 된다."""
        self.assertNotIn('Ã', ''.join(self.rec['authors']))

    def test_제목에서_금지문자가_제거된다(self):
        self.assertNotIn(':', self.rec['title'])


class JoinKeyTest(unittest.TestCase):
    """두 형식은 id 로 조인된다. 양쪽 id 표기가 같아야 한다."""

    def test_두_형식의_id_가_일치(self):
        raw, _ = hv.parse_page(RAW_XML, 'arXivRaw')
        arx, _ = hv.parse_page(ARXIV_XML, 'arXiv')
        self.assertEqual(raw[0]['id'], arx[0]['id'])

    def test_id_에는_버전이_붙지_않는다(self):
        """버전은 finalize 에서 v 필드로 붙인다. 조인 키에는 없어야 한다."""
        raw, _ = hv.parse_page(RAW_XML, 'arXivRaw')
        self.assertEqual(raw[0]['id'], '2008.06570')


if __name__ == '__main__':
    unittest.main()
