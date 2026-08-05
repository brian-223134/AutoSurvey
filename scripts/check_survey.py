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


def length_report(md_paths, asked_len=0, target_words=0):
    """분량이 무엇 때문에 그렇게 나왔는지 분해해서 보여준다.

    `--subsection_len` 은 프롬프트에서 상한이 아니라 **하한**("more than N words")이라
    모델마다 실제 분량이 크게 다르다. 같은 700 설정에서 실측 계수가
    haiku 0.77x / deepseek-v4-pro 1.67x 로 2.2배 벌어졌다. 그래서 새 백본을 쓸 때는
    스모크 1편으로 계수를 재고 목표 분량을 그 계수로 나눠 `--subsection_len` 에 넣어야 한다.

    구조는 `.tex` 가 있으면 그쪽을 센다. `.md` 헤딩 카운트는 중복 제목과 레벨 오류로
    부풀려진 전례가 있다 (deepseek 편 117 vs 72).
    """
    print(f'\n{"산출물":<44} {"섹션":>4} {"서브":>4} {"단어":>8} {"서브당":>7}', end='')
    print(f' {"계수":>7}' if asked_len else '')
    print('-' * (77 if asked_len else 69))
    for p in md_paths:
        tex = os.path.splitext(p)[0] + '.tex'
        if os.path.exists(tex):
            body = open(tex, encoding='utf-8').read().split(r'\begin{document}')[-1]
            body = re.split(r'\\begin\{thebibliography\}|\\section\*?\{References\}', body)[0]
            secs = len(re.findall(r'^\\section\{', body, re.M))
            subs = len(re.findall(r'^\\subsection\{', body, re.M))
            words = len(re.findall(r"[A-Za-z][A-Za-z'-]*",
                                   re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?', ' ', body)))
            src = ''
        else:
            md = open(p, encoding='utf-8').read().split('## References')[0]
            secs = len(re.findall(r'^## ', md, re.M))
            subs = len(re.findall(r'^### ', md, re.M))
            words = len(md.split())
            src = ' (.md 기준 — .tex 가 없어 부풀려졌을 수 있음)'
        per = words / subs if subs else 0
        name = os.path.splitext(p)[0].replace('output/', '')
        line = f'{name[:44]:<44} {secs:>4} {subs:>4} {words:>8,} {per:>7.0f}'
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
