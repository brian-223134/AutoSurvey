"""생성된 서베이의 구조와 인용 무결성을 검사한다.

    python scripts/check_survey.py output/*.md
    python scripts/check_survey.py            # 인자 없으면 output/*.md 전체

인용 번호가 References와 어긋나면(댕글링) 인용 지표 계산이 통째로 틀어지므로
서베이를 커밋하기 전에 이걸로 확인한다.
"""

import glob
import json
import os
import re
import sys

CITE_RUN = re.compile(r'\[([0-9;\s]+)\]')
REF_LINE = re.compile(r'^\[(\d+)\]', re.M)


def check(md_path):
    base = md_path[:-3]
    md = open(md_path).read()

    if '## References' not in md:
        print(f'{os.path.basename(base)}: ## References 절이 없습니다')
        return False
    body, refs = md.split('## References', 1)

    cited = set()
    for run in CITE_RUN.findall(body):
        for n in run.split(';'):
            n = n.strip()
            if n.isdigit():
                cited.add(int(n))
    listed = {int(n) for n in REF_LINE.findall(refs)}

    dangling = sorted(cited - listed)   # 본문이 참조하는데 References에 없음
    orphan = sorted(listed - cited)     # References에 있는데 본문에서 안 씀

    sections = len(re.findall(r'^## (?!References)', md, re.M))
    subsections = len(re.findall(r'^### ', md, re.M))
    n_cites = len(CITE_RUN.findall(body))

    fmt_leak = md.count('format>')
    fence_leak = md.count('```')
    desc_leak = len(re.findall(r'^Description:', md, re.M))

    ref_map = None
    if os.path.exists(base + '.json'):
        with open(base + '.json') as f:
            ref_map = json.load(f).get('reference')

    ok = (not dangling and not fmt_leak and not fence_leak and not desc_leak
          and (ref_map is None or len(ref_map) == len(listed)))

    print(f'{"OK  " if ok else "확인"} {os.path.basename(base)}')
    print(f'       {sections}섹션 / {subsections}서브섹션 / {len(md.split()):,}단어')
    print(f'       참고문헌 {len(listed)}개, 인용 {n_cites}회'
          + (f', json매핑 {len(ref_map)}개' if ref_map is not None else ''))
    if dangling:
        print(f'       ⚠ 댕글링 인용(References에 없음): {dangling[:10]}')
    if orphan:
        print(f'       - 인용되지 않은 참고문헌: {len(orphan)}개')
    if ref_map is not None and len(ref_map) != len(listed):
        print(f'       ⚠ json 매핑({len(ref_map)})과 References({len(listed)}) 불일치')
    if fmt_leak or fence_leak or desc_leak:
        print(f'       ⚠ 포맷 누출: format태그 {fmt_leak}, 코드펜스 {fence_leak}, Description {desc_leak}')
    return ok


# 실측으로 잡은 분량 구간 (2026-08-05).
#
#   AutoSurvey 원저자 예시 3편   8,558~13,894단어 / 19~29서브섹션 / refs 74~88
#   SurveyForge 저자 산출물 29편 13,242~32,938단어 / 20~39페이지(중앙값 31)
#   인간 서베이 10편(SurveyBench) refs 173~345 (중앙값 214)
#
# 저자 산출물 기준 약 800단어/페이지다. 광범위한 서베이는 45~70페이지까지 가므로
# 25k~50k 단어는 정당하다. 반면 100페이지(약 88k단어)를 넘긴 사례는 서베이라기보다
# 문서를 이어 붙인 것에 가까웠다. 그래서 상한은 '실패'가 아니라 '경고'로 둔다 —
# 주제에 따라 길어질 수 있고 판단은 사람이 한다.
WORDS_PER_PAGE = 800
BAND_STD = (12_000, 25_000)      # 표준적인 서베이
BAND_BROAD = 50_000              # 여기까지는 '광범위한 서베이'로 정당화 가능
BAND_BLOAT = 80_000              # 그 위는 비대
REFS_HUMAN = (150, 350)          # 인간 서베이 실측 범위
REFS_GUARD = 400


def length_band(words, refs=0):
    """구간 판정. (라벨, 경고문) 을 돌려준다. 경고문이 비어 있으면 정상."""
    pages = words / WORDS_PER_PAGE
    if words > BAND_BLOAT:
        return '비대', (f'{words:,}단어(약 {pages:.0f}p) — 100페이지를 넘는 규모다. '
                        f'서베이가 아니라 문서를 이어 붙인 것에 가깝다')
    if words > BAND_BROAD:
        return '초과', (f'{words:,}단어(약 {pages:.0f}p) — 광범위한 서베이의 상단'
                        f'({BAND_BROAD:,})도 넘었다. 주제가 그만큼 넓은지 확인할 것')
    if words > BAND_STD[1]:
        return '광범위', ''      # 25k~50k 는 정당한 구간이라 경고하지 않는다
    if words < BAND_STD[0]:
        return '짧음', f'{words:,}단어 — 표준 구간({BAND_STD[0]:,}) 미만이다'
    return '표준', ''


def measure(md_path):
    """한 산출물의 구조를 잰다: 섹션/서브섹션/단어 수.

    `.tex` 가 있으면 그쪽을 센다 — `.md` 헤딩 카운트는 중복 제목과 레벨 오류로
    부풀려진 전례가 있다 (deepseek 편 117 vs 72). length_report 와 collect_run.py 가
    같은 계산을 쓰도록 여기로 추출했다 (두 벌이면 반드시 어긋난다).
    """
    tex = os.path.splitext(md_path)[0] + '.tex'
    if os.path.exists(tex):
        body = open(tex, encoding='utf-8').read().split(r'\begin{document}')[-1]
        body = re.split(r'\\begin\{thebibliography\}|\\section\*?\{References\}', body)[0]
        secs = len(re.findall(r'^\\section\{', body, re.M))
        subs = len(re.findall(r'^\\subsection\{', body, re.M))
        words = len(re.findall(r"[A-Za-z][A-Za-z'-]*",
                               re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?', ' ', body)))
        from_tex = True
    else:
        md = open(md_path, encoding='utf-8').read().split('## References')[0]
        secs = len(re.findall(r'^## ', md, re.M))
        subs = len(re.findall(r'^### ', md, re.M))
        words = len(md.split())
        from_tex = False
    return {'sections': secs, 'subsections': subs, 'words': words, 'from_tex': from_tex}


def length_report(md_paths, asked_len=0, target_words=0):
    """분량이 무엇 때문에 그렇게 나왔는지 분해해서 보여준다.

    `--subsection_len` 은 프롬프트에서 상한이 아니라 **하한**("more than N words")이라
    모델마다 실제 분량이 크게 다르다. 같은 700 설정에서 실측 계수가
    haiku 0.77x / deepseek-v4-pro 1.67x 로 2.2배 벌어졌다. 그래서 새 백본을 쓸 때는
    스모크 1편으로 계수를 재고 목표 분량을 그 계수로 나눠 `--subsection_len` 에 넣어야 한다.

    구조는 `.tex` 가 있으면 그쪽을 센다. `.md` 헤딩 카운트는 중복 제목과 레벨 오류로
    부풀려진 전례가 있다 (deepseek 편 117 vs 72).
    """
    bands = []
    print(f'\n{"산출물":<44} {"섹션":>4} {"서브":>4} {"단어":>8} {"서브당":>7}', end='')
    print(f' {"계수":>7}' if asked_len else '')
    print('-' * (77 if asked_len else 69))
    for p in md_paths:
        m = measure(p)
        secs, subs, words = m['sections'], m['subsections'], m['words']
        src = '' if m['from_tex'] else ' (.md 기준 — .tex 가 없어 부풀려졌을 수 있음)'
        per = words / subs if subs else 0
        name = os.path.splitext(p)[0].replace('output/', '')
        band, warn = length_band(words)
        line = f'{name[:44]:<44} {secs:>4} {subs:>4} {words:>8,} {per:>7.0f}'
        bands.append((name, band, warn, words))
        if asked_len:
            # 계수 = 실제 서브섹션 길이 / 지시한 subsection_len.
            # 1.0 을 넘으면 하한을 초과해 쓴 것이고, 밑돌면 지시를 못 지킨 것이다.
            coef = per / asked_len
            print(f'{line} {coef:>6.2f}x{src}')
            if target_words:
                # 목표를 맞추려면 다음 실행에서 어떤 값을 줘야 하는지 역산한다.
                need = (target_words / subs) / coef if coef else 0
                print(f'{"":<44} -> 같은 구조({subs}서브섹션)로 {target_words:,}단어를 노리면 '
                      f'--subsection_len {need:.0f}')
        else:
            print(f'{line}{src}')
    print(f'\n분량 구간  표준 {BAND_STD[0]:,}~{BAND_STD[1]:,} / '
          f'광범위 ~{BAND_BROAD:,} / 비대 {BAND_BLOAT:,}~  (약 {WORDS_PER_PAGE}단어/페이지)')
    for name, band, warn, words in bands:
        mark = '경고' if warn else 'ok  '
        print(f'  {mark} {band:<5} {name[:52]}')
        if warn:
            print(f'         {warn}')
    if not asked_len:
        print('\n계수를 보려면 그 실행에서 쓴 값을 알려주세요: --subsection-len=700')
        print('총 분량 = section_num x subsection_num x (subsection_len x 계수) 입니다.')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    target = asked = 0
    for f in flags:
        if f.startswith('--target-words='):
            target = int(f.split('=', 1)[1])
        elif f.startswith('--subsection-len='):
            asked = int(f.split('=', 1)[1])

    paths = args or sorted(glob.glob('output/*/*.md'))
    if not paths:
        print('검사할 .md 가 없습니다', file=sys.stderr)
        return 1
    ok = all([check(p) for p in paths])
    if '--length' in flags or target or asked:
        length_report(paths, asked, target)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
