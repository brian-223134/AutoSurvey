"""AutoSurvey 산출물을 SurveyBench 인용 커버리지로 채점한다.

    python scripts/to_surveybench_ref.py "output/haiku/Evaluation of LLMs.json" \
        --topic "Evaluation of Large Language Models"

LLM judge 를 쓰지 않기로 했으므로(HANDOFF 남은작업 B) 정량 수치가 나오는 경로는
이것 하나다. 채점은 arXiv id 집합의 교집합이라 **LLM 호출이 0회**다.

    coverage = |생성 참고문헌 ∩ ref_bench| / |날짜 필터를 통과한 생성 참고문헌|

채점은 SurveyBench 의 `test.py::compute_citation_coverage` 를 **그대로 import 해서**
쓴다. 같은 식을 다시 구현하면 그쪽이 바뀔 때 조용히 어긋나고, 그러면 SurveyForge 와의
비교가 무의미해진다.

이 스크립트가 하는 일은 두 가지다.

1. `reference`(번호 → arXiv id)를 뒤집어 SurveyBench 배치로 `ref.json` 을 쓴다.
   `test.py` 는 `<dir>/<토픽>/exp_<n>/ref.json` 을 읽고, 키만 사용한다.
2. **분모에서 빠진 인용을 세어 보고한다.** 채점기는 두 부류를 조용히 버리는데,
   그걸 모르면 낮은 coverage 를 품질 문제로 오독한다:
     - 구형 arXiv id (`cs/0701001`) — 날짜 파싱이 안 된다
     - `ref_bench` 의 최신 논문보다 새 논문 — 벤치마크가 알 수 없는 논문이라 제외.
       **최신화본 DB 로 돌리면 여기서 대부분이 빠진다.**
"""

import argparse
import json
import os
import re
import sys

SURVEYBENCH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', '..', 'SurveyForge', 'SurveyBench')

# 참고용 기준값 (2026-08-05 실측). 낸 숫자가 어느 위치인지 바로 보이게 함께 찍는다.
BASELINES = {
    'Retrieval-Augmented Generation for Large Language Models':
        [('인간 작성', 191, 0.542), ('SurveyForge(저자)', 85, 0.435)],
    'Evaluation of Large Language Models':
        [('인간 작성', 214, 0.463), ('SurveyForge(저자)', 116, 0.336)],
}

VERSION = re.compile(r'v\d+$')
MODERN_ID = re.compile(r'\d{4}\.\d{4,5}$')


def load_surveybench(root):
    """SurveyBench 의 채점 함수와 토픽 목록을 가져온다."""
    if not os.path.isdir(root):
        sys.exit(f'SurveyBench 를 찾지 못했습니다: {root}\n'
                 f'--surveybench 로 경로를 주세요.')
    sys.path.insert(0, root)
    try:
        from test import compute_citation_coverage   # noqa: E402
    except ImportError as e:
        sys.exit(f'SurveyBench/test.py 를 import 하지 못했습니다: {e}')
    with open(os.path.join(root, 'topics.txt')) as f:
        topics = [ln.strip() for ln in f if ln.strip()]
    return compute_citation_coverage, topics


def build_refs(survey):
    """`reference`(번호 → arXiv id)를 SurveyBench 의 `{id: {arxivId, title}}` 로 뒤집는다.

    버전 접미사는 뗀다. 채점기도 어차피 떼지만, 그대로 두면 같은 논문의 v1/v2 가 두 키가
    되어 분모가 부풀 수 있다. dict 라 중복 id 는 자연히 하나로 접힌다.
    """
    detail = survey.get('reference_detail') or {}
    titles = {VERSION.sub('', d['id']): d.get('title', '')
              for d in detail.values() if isinstance(d, dict) and d.get('id')}
    refs = {}
    for raw in survey['reference'].values():
        pid = VERSION.sub('', raw)
        entry = {'arxivId': pid}
        if titles.get(pid):
            entry['title'] = titles[pid]
        refs[pid] = entry
    return refs


def bench_cutoff(bench_ids):
    """ref_bench 의 최신 논문 (YYYY-MM). 이보다 새 인용은 분모에서 빠진다."""
    dates = []
    for pid in bench_ids:
        m = re.match(r'(\d{2})(\d{2})\.(\d{4,5})', VERSION.sub('', pid))
        if m:
            dates.append((f'20{m.group(1)}-{m.group(2)}', int(m.group(3))))
    return max(dates) if dates else (None, None)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('survey_json', help='AutoSurvey 산출물 {topic}.json')
    ap.add_argument('--topic', help='SurveyBench 토픽 문자열. 생략하면 파일명을 쓴다')
    ap.add_argument('--out-dir', default='./output/surveybench_ref',
                    help='ref.json 을 쓸 곳 (기본 ./output/surveybench_ref)')
    ap.add_argument('--exp', type=int, default=1, help='실험 번호 (기본 1)')
    ap.add_argument('--surveybench', default=SURVEYBENCH)
    args = ap.parse_args()

    root = os.path.normpath(args.surveybench)
    score, topics = load_surveybench(root)

    topic = args.topic or os.path.splitext(os.path.basename(args.survey_json))[0]
    if topic not in topics:
        # 문자열이 어긋나면 검색 쿼리부터 달라져 비교가 성립하지 않는다.
        # 실제로 우리 "Evaluation of LLMs" 산출물이 이 함정에 걸렸다(coverage 0.054).
        sys.exit(f'"{topic}" 은 SurveyBench 토픽이 아닙니다.\n'
                 f'--topic 으로 아래 중 하나를 정확히 주세요:\n  ' + '\n  '.join(topics))

    with open(args.survey_json, encoding='utf-8') as f:
        survey = json.load(f)
    if 'reference' not in survey:
        sys.exit(f'{args.survey_json} 에 reference 필드가 없습니다.')

    refs = build_refs(survey)

    out = os.path.join(args.out_dir, topic, f'exp_{args.exp}')
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, 'ref.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(refs, f, ensure_ascii=False, indent=1)
    print(f'{path}  ({len(refs)}편)')

    bench_path = os.path.join(root, 'ref_bench', f'{topic}_bench.json')
    with open(bench_path, encoding='utf-8') as f:
        bench = json.load(f)

    n, ratio, matched = score(list(refs), [bench.keys()])
    valid = round(n / ratio) if ratio else 0

    # 채점기가 버린 것을 드러낸다. 안 보이면 낮은 수치를 품질 문제로 오독하게 된다.
    legacy = [p for p in refs if not MODERN_ID.match(p)]
    cut_ym, _ = bench_cutoff(bench)
    dropped = len(refs) - valid

    print()
    print(f'토픽        {topic}')
    print(f'벤치마크    {len(bench)}편, 최신 {cut_ym}')
    print(f'인용        {len(refs)}편 → 날짜 필터 통과 {valid}편 (제외 {dropped}편'
          + (f', 그중 구형 id {len(legacy)}편' if legacy else '') + ')')
    print(f'매칭        {n}편')
    print(f'coverage    {ratio:.3f}')

    if dropped > len(refs) * 0.5:
        print(f'\n⚠ 인용의 {dropped/len(refs)*100:.0f}%가 분모에서 빠졌습니다. '
              f'벤치마크가 {cut_ym} 까지만 알기 때문입니다.\n'
              f'  최신화본(./database_2026-08)으로 생성했다면 예상된 결과이고, '
              f'표본이 작아 수치가 흔들립니다.\n'
              f'  SurveyForge·인간 산출물과 비교하려면 배포본(./database)으로 다시 '
              f'생성하세요.')

    if topic in BASELINES:
        print(f'\n{"산출물":<20} {"인용":>5} {"coverage":>9}')
        for name, cites, cov in BASELINES[topic]:
            print(f'{name:<20} {cites:>5} {cov:>9.3f}')
        print(f'{"이 산출물":<20} {len(refs):>5} {ratio:>9.3f}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
