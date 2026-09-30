# kisti-2608-r4 PoC — llm-agent-optimization (2026-09-30)

corpus 를 `kisti-2608-r4` 로 바꾼 뒤의 첫 편. 입력 교체(DB·정책 파일)가 맞게 물렸는지와 25편 본배치의 편당 소요·비용을 확인하려고 1편만 돌렸다.
지시 원문은 corpus 측 `kisti_data/docs/asg/AGENT-HANDOFF.md` §0(2026-09-30 r4 채택).

## 1. 조건

| 항목 | 값 |
|---|---|
| topic | `A Survey on the Optimization of Large Language Model-based Agents` (`--topic_id llm-agent-optimization`) |
| GT | `10.1145/3789261` (CSUR, Crossref created 2026-01-24) · twin `2503.12434` (v1 2025-03-16) |
| cutoff | **2025-03-16** (twin v1) — 문헌 공개일 상한 < cutoff |
| DB | `database_kisti-kisti-2608-r4/` (1,697,512편, view papers.parquet sha `32a77a48…`) + sidecar `paper_dates.json`(r4 판) |
| 정책 파일 | `data/topic_policy.kisti-2608-r4.jsonl` (`1527a80`) |
| 채점 분모 | `n_gt_refs_cutoff` = **203** (pool 217) — 09-30 GT ref 식별자 보강 후. 실행 당시(보강 전) 190 / 197 |
| 백본·디코딩 | llama-3.3-70b-instruct @ OpenRouter akashml/fp8 핀, temperature 0.6, max_tokens 8192 + 잘림 재요청 |
| 인자 | `--section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200` (`--subsection_num` 미지정 — 본배치 논문 기본값) |
| 환경 | `AUTOSURVEY_MAX_THREADS=1`(8섹션 × 1 = 동시 8) · `AUTOSURVEY_MAX_RETRY=10` · `AUTOSURVEY_DEVICE=cpu`(GPU 전량 점유) · `setsid nohup` |
| 코드 | `1527a80` — 생성 경로는 `baa46cc`(잘림 재요청) + `7443c25`(검색 정책) + `839ff91`(TinyDB close, 동작 무관) |
| 결과 버전 열 | **`32a77a48 / 2026-09-30`** |

## 2. 실행 전 점검

main.py 와 같은 경로(`src.database.database(..., policy=policy_from_row(row))`)로 DB 만 올려 허용 집합을 계산했다(63초).

| 항목 | 기대 | 실측 |
|---|---|---|
| 허용 편수 | 1,541,302 | **1,541,302** / 1,697,512 |
| 지문(정렬 id 개행 연결 sha256) 앞 8자 | `efe95869` | **`efe95869`**ded411e2… |
| 제외 사유 | — | id 0 · 날짜없음 0 · cutoff 이후 day 98,272 / month 57,909 / year 29 · 날짜 출처 전부 sidecar |
| 인덱스에 남은 제외 id | 0 | 0 (GT·twin 이 view 에 없음) |
| 정책 행 | status ok, topic 문자열 일치 | 일치 |
| GT 목록 | `gap_to_80_refs.jsonl` `tier == in_view` = 190 (실행 당시) | 190 |

## 3. 결과

| 항목 | 값 |
|---|---|
| **recall** | **15 / 203 = 7.39%** (보강 전 분모로는 13 / 190 = 6.84%) |
| **precision** | **15 / 372 = 4.03%** (보강 전 13 / 372 = 3.49%) |
| refs | 372 (본문 인용 474회) |
| 구조 | 10섹션 / 34서브섹션 (`--section_num 8` 에서 +2 — 알려진 초과), 본문 약 22.8K단어(`.tex` 기준), 서브섹션당 694단어(계수 0.99) |
| PDF | 63쪽, 에러 0 · 미해결 인용 0 |
| 소요 | **30분 47초** (02:49:56 → 03:20:43 UTC) |
| 비용 | **$0.4729** (outline $0.0993 · writer $0.3736) — OpenRouter `/api/v1/key` usage 증가분과 일치 |
| 재시도 | 50회 — akashml 429 40건, 잘림 재요청 9건(버린 응답, 최종본 미포함) |

- **재채점(2026-09-30 후속)**: corpus 측이 식별자 없던 GT ref 를 제목 대조로 복구해 분모가 190 → 203 이 됐다(`kisti_data/analysis/gt-ref-resolve.md`). view·인덱스·cutoff 불변이라 재실행 없이 `score_kisti.py` 로 다시 채점했다 — 새로 식별된 13편 중 2편이 이미 refs 에 있었다. **이후 표에는 15/203 을 쓴다.**
- 제목 기준 대조 매칭은 12/203 으로 id 매칭(15)보다 적다 — id 매칭이 형식 차이로 놓친 것은 없다.
- pool 217 중 203 이 분모 — corpus 결손은 적고 recall 손실은 검색·인용 단계 몫이다.
- **r2 이전 결과와 같은 표에 놓지 않는다**(분모 합 2,543 → 4,010 → 4,173). run-to-run 편차 잠정 ±1.7%p.

## 4. 누수 검사 — 통과

`scripts/score_kisti.py` (retrieval_policy 블록 제외):

| 대상 | survey 본문 | reference | reference_detail |
|---|---:|---:|---:|
| GT DOI `10.1145/3789261` | 0 | 0 | 0 |
| twin `2503.12434` | 0 | 0 | 0 |
| GT 제목 | 0 (H1 제목 줄 제외) | — | 0 |

JSON 전체로는 두 문자열이 각각 5·4회 나오지만 전부 `retrieval_policy`(제외 목록·날짜 근거 기록) 안이다. 저장 직전 `verify_references_allowed` 도 통과(허용 집합 밖 ref 0).

## 5. 산출물

`output/kisti-2608-r4-llm-agent-optimization/` — `<topic>.md` · `.json` · `.tex` · `.pdf` · `.run.json`(manifest) · `.score.json`(채점) · `run.log`(gitignore).

## 6. 재현

```bash
source .env; export AUTOSURVEY_MAX_THREADS=1 AUTOSURVEY_MAX_RETRY=10 AUTOSURVEY_DEVICE=cpu
OUT=output/kisti-2608-r4-llm-agent-optimization
setsid nohup python -u main.py --topic "A Survey on the Optimization of Large Language Model-based Agents" \
  --topic_policy data/topic_policy.kisti-2608-r4.jsonl --topic_id llm-agent-optimization \
  --saving_path ./$OUT/ --db_path ./database_kisti-kisti-2608-r4 \
  --embedding_model "$AUTOSURVEY_EMBEDDING_MODEL" --model "$AUTOSURVEY_MODEL" --api_url "$AUTOSURVEY_API_URL" \
  --section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200 > $OUT/run.log 2>&1 < /dev/null &

# 후처리 (PDF 툴체인은 kisti-2512-sec3-physical-adversarial-attacks.md §7)
MD="$OUT/A Survey on the Optimization of Large Language Model-based Agents.md"
python scripts/check_survey.py "$MD"
PATH="/data2/chanjoong/miniforge3/envs/tex/bin:$PATH" python scripts/md_to_tex.py "$MD"
(cd $OUT && /usr/local/bin/latexmk -pdf -interaction=nonstopmode "$(basename "${MD%.md}").tex")
python scripts/collect_run.py --md "$MD" --log $OUT/run.log --db_path ./database_kisti-kisti-2608-r4 --args "<위 인자>"
python scripts/score_kisti.py --json "${MD%.md}.json" --topic_policy data/topic_policy.kisti-2608-r4.jsonl \
  --topic_id llm-agent-optimization --out "${MD%.md}.score.json"
```

## 7. 본배치(나머지 24편)에 주는 것

- 편당 약 31분·$0.47 — 이전 추정($0.35)보다 35% 높다(`--subsection_num` 미지정이라 34서브섹션). 24편 약 **$11.3** 인데 키 잔여 **$10.16**(2026-09-30 03:21 UTC) → **한도 상향 필요**.
- akashml 429 가 outline 단계부터 잦다(40건). 재시도 10 으로 전부 회복했지만 동시 8 을 올리지 말 것.
