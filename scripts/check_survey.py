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


def main():
    paths = sys.argv[1:] or sorted(glob.glob('output/*.md'))
    if not paths:
        print('검사할 .md 가 없습니다', file=sys.stderr)
        return 1
    return 0 if all([check(p) for p in paths]) else 1


if __name__ == '__main__':
    sys.exit(main())
