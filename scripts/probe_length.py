#!/usr/bin/env python3
"""서브섹션 길이 계수 프로브 — 본편 writer 와 같은 입력으로 1차 초안만 뽑아 단어 수를 잰다.

왜 필요한가: `--subsection_len` 은 하한 지시값이고 실제 분량은 백본·temperature 에 따라
1.1~1.8배로 달라진다(docs/commoncorpus-setup.md §4). 디코딩 프로파일이 바뀌면
(2026-09-07 temperature 0 → 0.6, max_tokens 8192) 계수를 다시 재야 역산이 맞는다.
08-31 프로브는 수기라 재현할 수 없었으므로, 이번부터는 이 스크립트와 spec JSON 으로
조건을 고정하고 산출 JSON 을 output/probes/ 에 남긴다.

본편과 같은 점: SUBSECTION_WRITING_PROMPT · DB 검색(description → rag_num 편 초록) ·
paper_texts 조립 · APIModel(.env 의 provider 핀 / temperature 오버라이드 / max_tokens).
다른 점: 1차 초안만 잰다(reflection·LCE 없음). 최종본은 이보다 짧아진다(08-31 앵커
비율 0.85). 호출은 순차(429 회피).

사용:
    python scripts/probe_length.py --spec output/probes/<name>.spec.json \
        --db_path ./database_kisti-kisti-2512 --repeat 2
spec JSON: {"label", "topic", "subsection_len", "rag_num", "probes": [{"section",
"subsection", "description"}, ...]}
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.model as model_mod  # noqa: E402
from src.database import database  # noqa: E402
from src.model import APIModel  # noqa: E402
from src.prompt import SUBSECTION_WRITING_PROMPT  # noqa: E402


def build_outline(topic, probes):
    """writer 가 받는 outline 문자열의 최소 형태 — 프로브에 든 섹션/서브섹션만 나열."""
    lines = [f'# {topic}']
    sections = []
    counts = {}
    for p in probes:
        if p['section'] not in sections:
            sections.append(p['section'])
            lines.append(f'## {len(sections)} {p["section"]}')
        si = sections.index(p['section']) + 1
        counts[si] = counts.get(si, 0) + 1
        lines.append(f'### {si}.{counts[si]} {p["subsection"]}')
    return '\n'.join(lines)


def paper_texts_for(db, description, rag_num):
    ids = db.get_ids_from_query(description, num=rag_num, shuffle=False)
    infos = {p['id']: p for p in db.get_paper_info_from_ids(ids)}
    text = ''
    for i in ids:
        p = infos[i]
        text += f'---\n\npaper_title: {p["title"]}\n\npaper_content:\n\n{p["abs"]}\n'
    text += '---\n'
    return ids, text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--spec', required=True)
    ap.add_argument('--db_path', required=True)
    ap.add_argument('--embedding_model', default=os.environ.get('AUTOSURVEY_EMBEDDING_MODEL', 'nomic-ai/nomic-embed-text-v1'))
    ap.add_argument('--model', default=os.environ.get('AUTOSURVEY_MODEL'))
    ap.add_argument('--api_url', default=os.environ.get('AUTOSURVEY_API_URL'))
    ap.add_argument('--repeat', type=int, default=1)
    ap.add_argument('--citation_num', type=int, default=8, help='writer 기본값 8')
    ap.add_argument('--out', default=None, help='기본 output/probes/<label>.<UTC시각>.json')
    args = ap.parse_args()

    spec = json.load(open(args.spec, encoding='utf-8'))
    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPENAI_API_KEY')
    if not (api_key and args.model and args.api_url):
        sys.exit('OPENROUTER_API_KEY / AUTOSURVEY_MODEL / AUTOSURVEY_API_URL 필요 — source .env')

    print(f'[probe] {spec["label"]} · db={args.db_path} · len={spec["subsection_len"]} · rag={spec["rag_num"]} · repeat={args.repeat}', flush=True)
    db = database(db_path=args.db_path, embedding_model=args.embedding_model)
    api = APIModel(args.model, api_key, args.api_url)
    extra = api._extra_payload()
    profile = {'model': args.model, 'provider': extra.get('provider', {}).get('order'),
               'temperature_override': model_mod.TEMPERATURE_OVERRIDE,
               'temperature_passed': 1, 'max_tokens': extra.get('max_tokens'),
               'reasoning': extra.get('reasoning')}
    print(f'[probe] profile {profile}', flush=True)

    outline = build_outline(spec['topic'], spec['probes'])
    records = []
    for p in spec['probes']:
        ids, texts = paper_texts_for(db, p['description'], spec['rag_num'])
        prompt = SUBSECTION_WRITING_PROMPT
        for k, v in {'OVERALL OUTLINE': outline, 'SUBSECTION NAME': p['subsection'], 'DESCRIPTION': p['description'],
                     'TOPIC': spec['topic'], 'PAPER LIST': texts, 'SECTION NAME': p['section'],
                     'WORD NUM': str(spec['subsection_len']), 'CITATION NUM': str(args.citation_num)}.items():
            prompt = prompt.replace(f'[{k}]', v)
        for r in range(args.repeat):
            before = dict(api.usage); trunc0 = api.truncated
            t0 = time.time()
            content = api.chat(prompt, temperature=1)   # writer 와 동일 — 오버라이드가 있으면 그 값
            dt = time.time() - t0
            if content is None:
                print(f'  !! {p["subsection"]} run{r + 1}: 응답 없음', flush=True)
                records.append({'subsection': p['subsection'], 'run': r + 1, 'failed': True}); continue
            content = content.replace('<format>', '').replace('</format>', '').strip()
            words = len(content.split())
            rec = {'section': p['section'], 'subsection': p['subsection'], 'run': r + 1,
                   'words': words, 'ratio': round(words / spec['subsection_len'], 3),
                   'in_tokens': api.usage['prompt'] - before['prompt'],
                   'out_tokens': api.usage['completion'] - before['completion'],
                   'cost_usd': round(api.usage['cost'] - before['cost'], 5),
                   'truncated': api.truncated > trunc0, 'elapsed_sec': round(dt, 1),
                   'rag_ids': ids, 'content': content}
            records.append(rec)
            print(f'  {p["subsection"][:40]:<40} run{r + 1}: {words:>5}단어 ({rec["ratio"]:.2f}×) '
                  f'out={rec["out_tokens"]} ${rec["cost_usd"]:.4f} {dt:.0f}s{"  ⚠잘림" if rec["truncated"] else ""}', flush=True)

    ok = [r for r in records if not r.get('failed')]
    ratios = [r['ratio'] for r in ok]
    summary = {'n': len(ok), 'mean_words': round(sum(r['words'] for r in ok) / len(ok), 1) if ok else None,
               'mean_ratio': round(sum(ratios) / len(ratios), 3) if ratios else None,
               'min_ratio': min(ratios) if ratios else None, 'max_ratio': max(ratios) if ratios else None,
               'truncated': sum(r['truncated'] for r in ok), 'cost_usd': round(sum(r['cost_usd'] for r in ok), 4)}
    out = {'label': spec['label'], 'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
           'spec': spec, 'db_path': args.db_path, 'profile': profile, 'citation_num': args.citation_num,
           'repeat': args.repeat, 'summary': summary, 'records': records}
    out_path = args.out or os.path.join('output', 'probes', f'{spec["label"]}.{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'[probe] summary {summary}\n[probe] wrote {out_path}', flush=True)


if __name__ == '__main__':
    main()
