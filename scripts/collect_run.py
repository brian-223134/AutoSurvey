#!/usr/bin/env python3
"""실행 로그 + 산출물에서 편당 <topic>.run.json 매니페스트를 만들고, 집계 표를 뽑는다.

왜 필요한가: 실행 로그는 휘발성이고(세션 임시 디렉터리에 쌓임) 문서 수기는
누락된다(llama 4편에서 단계별 비용이 로그에만 남았던 사례, 2026-08-31).
run.json 은 산출물 옆에 앉아 같은 커밋으로 들어가므로 재현 체인이 파일 단위로 닫힌다.

사용:
    # 1) 생성 직후, 로그가 살아있을 때 매니페스트 작성
    python scripts/collect_run.py --md "output/<dir>/<topic>.md" --log <run.log> \
        --args "--section_num 5 --subsection_len 350 ..." [--db_path ./database_...]

    # 2) 집계 표 (output/*/*.run.json 전부)
    python scripts/collect_run.py --table

기록 항목: 모델·provider 핀(로그), 단계별 토큰/비용/재시도(로그의 [usage] 줄),
잘림 경고 수, 실행 인자(--args 그대로), DB manifest sha, 구조(check_survey.measure
와 동일 계산), 참고문헌/인용 수, PDF 쪽수(pdfinfo), 계수, 소요시간(로그 birth →
.md mtime — birth 를 못 얻는 파일시스템에서는 생략).

한계: --args 는 검증 없이 그대로 기록한다(로그에 CLI 인자가 안 남으므로 호출자가
넘겨야 한다). 로그가 이미 사라진 과거 실행은 만들 수 없다 — haiku/deepseek 편은
REPRODUCTION.md §5 가 기록처다.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_survey import CITE_RUN, REF_LINE, measure  # noqa: E402

USAGE_RE = re.compile(
    r'\[usage\]\s+(\w+)\s+청구 in=([\d,]+) out=([\d,]+) \(추론 ([\d,]+)\) '
    r'비용 \$([\d.]+) 재시도 (\d+)회')
PROVIDER_RE = re.compile(r'\[provider\] (\S+) → (\S+) 고정')


def _n(s):
    return int(s.replace(',', ''))


def parse_log(log_path):
    text = open(log_path, encoding='utf-8', errors='replace').read()
    stages = {}
    for m in USAGE_RE.finditer(text):
        stages[m.group(1)] = {
            'in_tokens': _n(m.group(2)), 'out_tokens': _n(m.group(3)),
            'reasoning_tokens': _n(m.group(4)),
            'cost_usd': float(m.group(5)), 'retries': int(m.group(6)),
        }
    prov = PROVIDER_RE.search(text)
    return {
        'model': prov.group(1) if prov else None,
        'provider_pin': prov.group(2) if prov else None,
        'stages': stages,
        'cost_total_usd': round(sum(s['cost_usd'] for s in stages.values()), 4),
        'retries_total': sum(s['retries'] for s in stages.values()),
        # finish_reason=length 로 잘린 호출 수. 0이 아니면 그 서베이는 어딘가
        # 문장이 끊긴 채로 들어간 것이다 (model.py 의 경고와 같은 신호).
        'truncated_calls': text.count('출력이 잘렸습니다'),
    }


def file_birth_epoch(path):
    # os.stat 은 리눅스에서 birth 를 안 주지만 coreutils stat 은 statx 로 얻는다.
    try:
        out = subprocess.check_output(['stat', '-c', '%W', path], text=True).strip()
        return int(out) or None
    except Exception:
        return None


def db_manifest_sha(db_path):
    for p in glob.glob(os.path.join(db_path, '*.manifest.json')):
        try:
            return json.load(open(p)).get('content_sha256')
        except Exception:
            pass
    return None


def pdf_pages(pdf_path):
    try:
        out = subprocess.check_output(['pdfinfo', pdf_path], text=True)
        m = re.search(r'^Pages:\s+(\d+)', out, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def arg_value(args_str, name):
    m = re.search(rf'{name}[= ]+(\S+)', args_str or '')
    return m.group(1) if m else None


def build_manifest(md_path, log_path, args_str, db_path):
    base = os.path.splitext(md_path)[0]
    md = open(md_path, encoding='utf-8').read()
    body, _, refs = md.partition('## References')

    st = measure(md_path)
    info = parse_log(log_path)

    manifest = {
        'topic': os.path.basename(base),
        'md': md_path,
        'generated_at_epoch': int(os.stat(md_path).st_mtime),
        'args': args_str or None,
        'db_path': db_path,
        'db_manifest_sha256': db_manifest_sha(db_path) if db_path else None,
        **info,
        'structure': {
            **st,
            'references': len(REF_LINE.findall(refs)),
            'citation_runs': len(CITE_RUN.findall(body)),
            'pdf_pages': pdf_pages(base + '.pdf'),
        },
    }

    birth = file_birth_epoch(log_path)
    if birth:
        manifest['duration_sec'] = manifest['generated_at_epoch'] - birth

    # 계수 = 실제 서브섹션당 단어 / 지시한 subsection_len (하한). check_survey 와 동일 정의.
    asked = arg_value(args_str, '--subsection_len')
    if asked and st['subsections']:
        per = st['words'] / st['subsections']
        manifest['coefficient'] = {
            'subsection_len_asked': int(asked),
            'words_per_subsection': round(per),
            'ratio': round(per / int(asked), 2),
        }
    return manifest


def write_manifest(md_path, log_path, args_str, db_path):
    out = os.path.splitext(md_path)[0] + '.run.json'
    manifest = build_manifest(md_path, log_path, args_str, db_path)
    with open(out, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f'생성: {out}')
    s = manifest['structure']
    dur = manifest.get('duration_sec')
    print(f"  {s['sections']}섹션/{s['subsections']}서브/{s['words']:,}단어"
          f"/refs {s['references']}/{s['pdf_pages'] or '?'}쪽  "
          f"${manifest['cost_total_usd']}  재시도 {manifest['retries_total']}"
          f"{f'  {dur//60}분{dur%60}초' if dur else ''}")
    if manifest['truncated_calls']:
        print(f"  ⚠ 잘린 호출 {manifest['truncated_calls']}건 — 산출물에 끊긴 문장이 있다")


def table():
    rows = []
    for p in sorted(glob.glob('output/*/*.run.json')):
        m = json.load(open(p))
        s = m['structure']
        dur = m.get('duration_sec')
        rows.append((
            os.path.dirname(p).replace('output/', ''),
            m['topic'],
            f"{arg_value(m.get('args'), '--section_num') or '?'}"
            f"/{arg_value(m.get('args'), '--subsection_num') or '-'}"
            f"/{arg_value(m.get('args'), '--subsection_len') or '?'}",
            f"{s['sections']}/{s['subsections']}",
            f"{s['words']:,}",
            str(s['references']),
            str(s['pdf_pages'] or '?'),
            f"${m['cost_total_usd']:.3f}",
            f"{dur // 60}분" if dur else '?',
            str(m['retries_total']),
        ))
    if not rows:
        print('output/*/*.run.json 이 없습니다. --md/--log 로 먼저 생성하세요.',
              file=sys.stderr)
        return 1
    header = ('디렉터리', '토픽', 'sec/cap/len', '섹/서브', '단어', 'refs', '쪽', '비용', '시간', '재시도')
    print('| ' + ' | '.join(header) + ' |')
    print('|' + '---|' * len(header))
    for r in rows:
        print('| ' + ' | '.join(r) + ' |')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--md', help='산출물 .md 경로')
    ap.add_argument('--log', help='그 실행의 로그 파일')
    ap.add_argument('--args', default='', help='main.py 에 넘겼던 인자 문자열 (그대로 기록)')
    ap.add_argument('--db_path', default='', help='DB 디렉터리 (manifest sha 기록용)')
    ap.add_argument('--table', action='store_true', help='run.json 집계 표 출력')
    a = ap.parse_args()

    if a.table:
        return table()
    if not (a.md and a.log):
        ap.error('--md 와 --log 를 함께 주거나 --table 을 쓰세요')
    write_manifest(a.md, a.log, a.args, a.db_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
