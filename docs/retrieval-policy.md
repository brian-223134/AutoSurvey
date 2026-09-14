# 검색 허용 정책 — GT survey 최초 공개일 이전 문헌만 검색 (2026-09-14)

**정본.** 교수님 지시(2026-09-14): reference cutoff 를 2025-12-31 로 고정하지 말고, **GT 로 쓰는 survey 의 최초
publish 날짜 이전까지만 retrieval** 할 수 있게 한다. 이 문서는 그 구현·근거·검증·한계를 적는다. 실험 방향 전체는
[`direction-2026-09.md`](direction-2026-09.md), 원본 파라미터 정리와 개선 계획 원문은 저장소 밖 문서(`origin_autosurvey_generation_parameters.md` §4).

## 0. 한눈에

| 항목 | 값 |
|---|---|
| 규칙 | 문헌 공개일의 **상한**(정밀도상 가장 늦은 날짜) `< retrieval_cutoff_at` 일 때만 허용. 당일 제외. 날짜 불명은 제외 |
| cutoff | topic 별 `gt_first_public_at` = GT 의 **가장 이른** 공개일(arXiv 선행판 v1 > Crossref created > published-online) |
| 구현 | `src/retrieval_policy.py`(규칙) · `src/database.py`(FAISS `IDSelectorBitmap` — 검색 **자체**가 허용 집합 안에서 돈다) · `main.py`(`--topic_policy/--topic_id`, `--retrieval_cutoff`, `--exclude_ids`) |
| 정책 파일 | `data/topic_policy.kisti-2512.jsonl` (25행, 전부 status ok) + 근거 캐시 `data/topic_policy.kisti-2512.sources.json` — `scripts/build_topic_policy.py --fetch` 산출 |
| 문헌 날짜 | DB 디렉터리의 sidecar `paper_dates.json`(`scripts/build_paper_dates.py`): arXiv id → 투고월(month), DOI → OpenAlex `publication_date`(day), 나머지 KISTI 연도(year). sidecar 없으면 arXiv 월 + 연 단위로 판정 |
| 기록 | `<topic>.json['retrieval_policy']`(정책·허용 편수·허용 집합 sha256·제외 사유별 편수) → `collect_run.py` 가 `run.json` 으로 |
| 영향 | 25 topic 중 **14편**은 arXiv 선행판 때문에 cutoff 가 2022-11 ~ 2025-07 로 앞당겨져 허용 corpus 가 72~96%; **2편**(llm-watermarking·wireless)은 2025-12 초순·하순; **9편**은 2026 이후라 현행 view 와 동일. §5 표 |

## 1. 왜 바꾸는가

기존 설계(`direction-2026-09.md` §1)는 view 를 `year ≤ 2025` 로 자르고 GT 본체·twin 40키를 빼는 것으로 누수를 막았다. 그런데 GT 25편 중 13편은 arXiv 선행판(twin)이 2022~2025년에 이미 공개돼 있었고, 그 선행판이 인용한 문헌은 물론 **선행판 이후에 나온 후속 연구**(선행판을 인용하며 같은 주제를 다루는 논문)까지 검색 풀에 들어 있었다. 사람이 그 survey 를 쓸 때는 볼 수 없었던 문헌이다. 교수님 지시대로 topic 별 cutoff 를 GT 최초 공개일로 두면 "그 survey 를 쓰던 시점의 문헌만" 검색된다.

## 2. 판정 규칙

문헌 공개일은 정밀도가 제각각이다. **불확실하면 제외**한다 — 누수 차단이 목적이므로 이른 쪽으로 틀리는 편이 안전하다.

| 정밀도 | 표기 | 상한(upper bound) | 예: cutoff 2022-11-03 |
|---|---|---|---|
| day | `2022-11-02` | 그 날짜 | 허용 (`2022-11-03` 당일부터 제외) |
| month | `2022-10` | 그 달 말일 | `2022-10` 허용, `2022-11` 제외(11-30 ≥ 11-03) |
| year | `2021` | 12-31 | `2021` 허용, `2022` 제외 |
| 없음 | — | — | 제외 (`no_date` 로 집계) |

제외 id(GT 본체·선행판·사본)는 날짜와 무관하게 막는다. view 가 이미 뺐지만 정책에도 넣어 두 겹으로 막고, 인덱스에 남아 있으면 경고를 찍는다.

**검색 경로 전부에 같은 선택자를 건다** — outline 풀(topic → 1,200편), suboutline(섹션 설명 → 50편), subsection(서브섹션 설명 → 60편), 그리고 인용 문자열 → id 매핑(제목 인덱스 Top-1). `get_paper_info_from_ids` 같은 직접 조회도 허용 집합으로 제한한다. 전체 Top-K 를 뽑은 뒤 거르는 방식이 아니라 `IndexFlatL2.search(..., params=SearchParameters(sel=IDSelectorBitmap))` 로 후보 자체를 제한하므로, 금지 문헌이 상위에 몰려도 K 개가 허용 문헌으로 채워진다(`tests/test_database_policy.py`).

## 3. 문헌 공개일 — 출처와 정밀도

KISTI export 의 `date` 는 `YYYY-01-01`(manifest `date_precision: year`)뿐이다. 그대로 쓰면 cutoff 가 연중인 topic(예: 2025-12-05)에서 그 해 DOI 논문 전부가 빠진다. 그래서 sidecar 를 만든다.

| 레코드 | 출처 | 정밀도 | 편수 (v2 DB, 2026-09-14) |
|---|---|---|---|
| arXiv id (신형·구형) | id 의 YYMM = v1 투고월. OpenAlex 는 보지 않는다 — KISTI 의 arXiv 레코드 초록이 v1 이 아닐 수 있어 월 상한이 안전 | month | 454,958 |
| DOI | OpenAlex 미러 `works.parquet`(4.79억 편) `publication_date`, DOI 조인. **OpenAlex 연도 < KISTI 연도면 다른 판**이므로 KISTI 연도 유지 | day | 1,191,972 |
| DOI (OpenAlex 연도 충돌 4,556 · 미매칭 1) | KISTI `year` | year | 4,557 |

- 파일: `database_kisti-kisti-2512/paper_dates.json` (62,332,660 B, `{"meta":…, "dates": {id: "YYYY[-MM[-DD]]"}}`). 지문은 `REPRODUCTION.md` §3-C. 빌드 428초(asg-corpus env, duckdb). DB 디렉터리는 gitignore 라 **재현 시 다시 만든다**(`build_paper_dates.py`, 명령은 스크립트 docstring).
- KISTI `year` 가 arXiv id 월과 어긋나는 레코드가 1,245편 있었다(2601.* 가 year=2025 등). id 를 우선한다.
- arXiv 스냅샷(`survey-search/data/papers.duckdb`)의 `date` 는 **최신판 날짜**(2409.18169v6 → 2026-04-23)라 v1 날짜로 쓸 수 없다. `submitted_date` 는 월초로 뭉개져 있다. 쓰지 않았다.

## 4. GT 최초 공개일 — 결정 절차

`scripts/build_topic_policy.py --fetch` 가 topic 마다 후보를 모아 **가장 이른 날짜**를 고른다. 근거 응답은 `data/topic_policy.kisti-2512.sources.json` 에 그대로 남는다.

| 후보 | 출처 | 비고 |
|---|---|---|
| arXiv 선행판(twin) v1 | `arxiv.org/abs/<id>` Submission history `[v1]` 줄 (export.arxiv.org API 는 이 호스트에서 429) | 13편 + GT 자체가 arXiv 인 2편 + edge-slm 의 선행판 `2507.16731` |
| Crossref `created` | DOI 등록일 ≈ 온라인 최초 게시(ACM 은 Just-Accepted) | `published-online` 보다 1~2개월 빠르다. 이른 쪽을 택함 |
| Crossref `published-online` / `issued` | 게재일 | 참고 기록 |
| `candidate.yaml gt.published` | 선정 당시 기록 | Crossref 응답이 없는 DOI 에서만 폴백(`YYYY-01-01` 자리표시가 섞여 있어서) |

twin ↔ topic 매핑은 asg-common-corpus `candidates/GT-SURVEYS.md`(2026-09-02) twin 열을 스크립트에 옮겨 적고 view 의 `twin:<id>` 키 15개와 대조 검증한다. 일 단위 후보가 가장 이른 날짜가 아니면 `status=needs_review` 로 두고 **`main.py` 가 거부**한다(`--retrieval_cutoff` 로 명시할 때만 진행).

| topic_id | cutoff | 근거 | 비고 |
|---|---|---|---|
| instruction-tuning-llms | 2023-08-21 | twin 2308.10792 v1 | 게재 2026-01-08 |
| llm-function-calling | 2026-01-14 | Crossref created | twin 없음 — 선행판 미확인 |
| model-merging | 2024-08-14 | twin 2408.07666 v1 | |
| diffusion-model-alignment | 2026-02-10 | Crossref created | twin 없음 |
| llm-agent-optimization | 2025-03-16 | twin 2503.12434 v1 | |
| retrieval-explainability | 2022-12-14 | twin 2212.07126 v1 | |
| trustworthy-rag | 2025-02-08 | twin 2502.06872 v1 | |
| large-models-timeseries | 2023-10-16 | twin 2310.10196 v1 | |
| deep-graph-clustering | 2022-11-23 | twin 2211.12875 v1 | |
| negative-sampling-recsys | 2026-01-28 | Crossref created | twin 없음 |
| mllm-adversarial-attacks | 2026-03-30 | GT arXiv 2603.27918 v1 | |
| llm-training-data-detection | 2026-01-07 | Crossref created | twin 없음 |
| physical-adversarial-attacks | 2022-11-03 | twin 2211.01671 v1 | 게재 2026-04-01. **기존 4편은 정책 없이 생성** |
| harmful-finetuning | 2024-09-26 | twin 2409.18169 v1 | |
| llm-watermarking | 2025-12-05 | Crossref created | twin 없음. 2025년 DOI 논문은 sidecar 일 단위 날짜로 판정 |
| moe-inference-optimization | 2024-12-18 | twin 2412.14219 v1 | |
| kv-cache-serving | 2026-07-01 | Crossref created | twin 없음 (ACL Findings — 선행판 가능성 높음, 미확인) |
| edge-slm-cloud-llm | 2025-07-22 | 선행판 2507.16731 v1 | v2 에서 view 제외된 그 사본 |
| llm-edge-inference | 2026-04-24 | Crossref created | twin 없음 |
| llm-distributed-training | 2024-07-29 | twin 2407.20018 v1 | |
| edge-cloud-collaboration | 2025-05-03 | twin 2505.01821 v1 | |
| wireless-foundation-models | 2025-12-26 | Crossref created (COMST early access) | arXiv 2601.03181 은 2026-01-06 |
| ai-wireless-reasoning | 2026-04-23 | Crossref created | twin 없음 |
| agentic-satellite-networks | 2026-02-03 | Crossref created | twin 없음 |
| ai-video-streaming | 2024-06-04 | twin 2406.02302 v1 | |

## 5. corpus 와 채점 분모에 미치는 영향 (`scripts/policy_report.py`, 2026-09-14)

allowed = 허용 편수 / 1,651,487. GT in_view = 기존 분모(`gap_to_80_refs.jsonl` tier in_view). GT < cutoff = 그중 S2 `publicationDate` 가 cutoff 이전 = **새 분모 후보**. date? = in_view 인데 날짜가 없어 판정 못 한 ref.

| topic_id | cutoff | allowed | GT in_view | GT < cutoff | date? |
|---|---|---:|---:|---:|---:|
| instruction-tuning-llms | 2023-08-21 | 1,304,896 (79%) | 110 | 96 | 1 |
| llm-function-calling | 2026-01-14 | 1,651,487 (100%) | 74 | 74 | 0 |
| model-merging | 2024-08-14 | 1,460,094 (88%) | 165 | 141 | 1 |
| diffusion-model-alignment | 2026-02-10 | 1,651,487 (100%) | 139 | 139 | 0 |
| llm-agent-optimization | 2025-03-16 | 1,540,142 (93%) | 112 | 105 | 1 |
| retrieval-explainability | 2022-12-14 | 1,202,448 (73%) | 127 | 114 | 1 |
| trustworthy-rag | 2025-02-08 | 1,528,223 (93%) | 86 | 78 | 0 |
| large-models-timeseries | 2023-10-16 | 1,326,717 (80%) | 213 | 191 | 1 |
| deep-graph-clustering | 2022-11-23 | 1,191,055 (72%) | 108 | 89 | 2 |
| negative-sampling-recsys | 2026-01-28 | 1,651,487 (100%) | 138 | 137 | 1 |
| mllm-adversarial-attacks | 2026-03-30 | 1,651,487 (100%) | 52 | 51 | 1 |
| llm-training-data-detection | 2026-01-07 | 1,651,487 (100%) | 56 | 56 | 0 |
| physical-adversarial-attacks | 2022-11-03 | 1,186,466 (72%) | 149 | 130 | 2 |
| harmful-finetuning | 2024-09-26 | 1,472,911 (89%) | 120 | 87 | 0 |
| llm-watermarking | 2025-12-05 | 1,641,322 (99%) | 44 | 0 | 44 |
| moe-inference-optimization | 2024-12-18 | 1,503,417 (91%) | 113 | 111 | 0 |
| kv-cache-serving | 2026-07-01 | 1,651,487 (100%) | 60 | 60 | 0 |
| edge-slm-cloud-llm | 2025-07-22 | 1,591,193 (96%) | 136 | 134 | 1 |
| llm-edge-inference | 2026-04-24 | 1,651,487 (100%) | 85 | 83 | 2 |
| llm-distributed-training | 2024-07-29 | 1,451,432 (88%) | 174 | 167 | 1 |
| edge-cloud-collaboration | 2025-05-03 | 1,561,520 (95%) | 167 | 166 | 1 |
| wireless-foundation-models | 2025-12-26 | 1,643,688 (100%) | 119 | 118 | 1 |
| ai-wireless-reasoning | 2026-04-23 | 1,651,487 (100%) | 72 | 71 | 1 |
| agentic-satellite-networks | 2026-02-03 | 1,651,487 (100%) | 66 | 59 | 7 |
| ai-video-streaming | 2024-06-04 | 1,431,447 (87%) | 79 | 69 | 7 |

- GT in_view 가 `topics.kisti.jsonl` 의 `n_gt_refs` 와 ±1~2 다른 topic 이 있다(감사 매칭 방식 차이). 분모 확정은 채점 측 몫이다 — **채점기는 같은 규칙(ref 공개일 상한 < cutoff)을 자기 데이터로 다시 적용**해야 한다. 이 표는 규모 확인용.
- `llm-watermarking` 은 refs.json 이 Crossref 기탁 목록(날짜 없음)이라 44편 전부 판정 불가 — S2 재추출이 필요하다(`topic-selection.md` 결정 6).
- 선행판이 있는 topic 에서 GT 게재본에 나중에 추가된 ref(선행판 이후 문헌)는 분모에서 빠진다. 예: harmful-finetuning 120 → 87.

## 6. 실행·기록

```bash
# 정책 생성(네트워크; 캐시가 있으면 --fetch 생략 가능)
python scripts/build_topic_policy.py --fetch
# 문헌 날짜 sidecar (DB 디렉터리마다 1회, asg-corpus env)
$ASG_PY scripts/build_paper_dates.py --db-path ./database_kisti-kisti-2512 \
    --openalex /data2/chanjoong/survey-agent/asg-common-corpus/data/upstream/cd87dd0/openalex/works/works.parquet
# 생성 — 정책 행은 --topic_id 로 고른다 (없으면 --topic 문자열 완전 일치)
python main.py --topic "Visual Adversarial Attacks and Defenses in the Physical World" \
    --topic_policy data/topic_policy.kisti-2512.jsonl --topic_id physical-adversarial-attacks \
    --db_path ./database_kisti-kisti-2512 --embedding_model nomic-ai/nomic-embed-text-v1 \
    --section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200 ...
# 영향 표
python scripts/policy_report.py
```

- 로그: `[policy] topic_id=… cutoff<… 제외 id N개` 와 `허용 a/b편 — 제외: id / 날짜없음 / cutoff 이후 day·month·year; 날짜 출처 {...}`.
- `<topic>.json['retrieval_policy']`: 정책 dict(`topic_id`·`gt_first_public_at`·`gt_first_public_source`·`retrieval_cutoff_at`·`exclude_ids`·`corpus_snapshot_id`·override 여부), `allowed`, `allowed_fingerprint_sha256`(허용 id 정렬 sha256 — 같은 DB·같은 정책이면 같다), 제외 사유별 편수, 날짜 출처별 편수, sidecar meta. `reference_detail` 의 각 ref 에 `date`·`date_precision`·`date_source`.
- 저장 직전 `verify_references_allowed` 가 최종 참고문헌 전부가 허용 집합 안인지 확인하고 아니면 저장하지 않는다.
- `collect_run.py` 가 위 블록을 `run.json['retrieval_policy']` 로 옮긴다. `retrieval_policy: null` 이면 정책 없이 돌린 실행(2026-09-14 이전 산출물 전부).
- 인자를 주지 않으면 **원본 동작 그대로**(전체 인덱스 검색). `--retrieval_cutoff YYYY-MM-DD` 만 주면 정책 파일 없이 날짜만 건다.

## 7. 검증

- 단위 테스트 38개(`tests/test_retrieval_policy.py`·`test_database_policy.py`·`test_main_policy.py`): 상한 규칙 경계(당일·월말·연말·불명), arXiv 구형/신형 id, KISTI `YYYY-01-01` 을 연 단위로 읽는지, 선택자 검색이 k > 허용 편수일 때 허용분만 돌려주는지(사후 필터였다면 새는 경우), 제목 인덱스·직접 조회 제한, sidecar 우선, needs_review 거부, 저장 전 검증. 전체 123개 통과.
- 실 DB 스모크(§8 에 결과): physical-adversarial cutoff 2022-11-03 로 세 검색 경로 + 인용 매핑을 돌려 반환 id 의 공개일 상한이 전부 cutoff 이전인지, 정책 없는 결과의 허용분 순서가 보존되는지 확인.

## 8. 실 DB 스모크 결과 (2026-09-14)

(스크립트: 세션 스크래치 `smoke_policy.py` — LLM 호출 없이 `database` 만 로드)

- DB 로드 88초(질의 임베딩 CPU), 인덱스 1,651,487. 정책 `physical-adversarial-attacks`: cutoff < 2022-11-03, 제외 id 2개(view 에 이미 없음 → 인덱스 잔존 0).
- **허용 1,186,466 / 1,651,487 (71.8%)**. 제외: cutoff 이후 day 326,446 · month 136,822 · year 1,753; 날짜 없음 0; 날짜 출처 전부 sidecar. 허용 집합 sha256 `4bee99cd9f46c4fc…`.
- 세 검색 경로(1,200 / 50 / 60) + 인용 매핑 4건: 반환 id 의 공개일 상한이 cutoff 이후이거나 제외 id 인 경우 **0건**. 가장 늦은 허용 날짜 2022-10-31(`2210.17140`, 월 단위).
- 정책 없는 검색과 대조: outline 풀 1,200편 중 허용은 **674편뿐**(526편이 cutoff 이후 — 고정 cutoff 로 돌린 기존 4편에는 이 문헌이 섞여 있었다), suboutline 50 중 30, subsection 60 중 32. 정책 결과는 각각 1,200 / 50 / 60 을 허용 문헌으로 채웠고, 정책 없는 결과의 허용분이 정책 결과의 **접두어**(순서 보존) — 선택자 검색이 "허용 집합 안의 정확한 Top-K" 임을 뜻한다.
- 인용 → id 매핑: 정책 없이는 "Physical adversarial attack meets computer vision: a decade survey" 가 `10.1109/tpami.2024.3430860`(2024 게재판)로 매핑됐고, 정책에서는 `2209.14262`(2022-09 arXiv 판)로 매핑됐다 — 제목 인덱스 제한이 동작한다. 나머지 3건(`1712.09665`·`1707.08945`·`1707.07397`)은 양쪽 동일.
- 제외 id 직접 조회 0건.

## 9. 한계·미결

1. **arXiv 레코드의 버전** — KISTI 의 arXiv 레코드(`10.48550/arxiv.<id>`)는 버전 없는 키라 초록이 최신판일 수 있다. 월 단위 상한으로 "v1 이 cutoff 이전"임은 보장하지만 제공하는 초록이 v1 것이라는 보장은 없다(origin 문서 §4.4 "v1 만 허용되는 경우 원문·파생자료도 v1 인지"). 해결하려면 arXiv 판별 재수확이 필요 — 미착수.
2. **OpenAlex `publication_date` 의 의미** — 저널판의 게재일이다. 같은 논문의 arXiv 판이 corpus 에 따로 있으면 그 레코드는 자기 월로 판정되므로 판별 규칙과 어긋나지 않는다.
3. **twin 없는 GT 12편** — 등록된 선행판이 없을 뿐, 존재하지 않는다는 확인은 아니다(kv-cache-serving 등 ACL 논문은 있을 가능성이 높다). 발견되면 `candidate.yaml gt.arxiv_id` 또는 TWIN 표에 등록하고 정책을 재생성한다. view 에서의 제외(누수)는 corpus 측 재작업.
4. **채점 분모** — §5 표대로 topic 별로 줄어든다. 채점 측이 같은 규칙으로 분모를 다시 계산해야 하고, `llm-watermarking` 은 ref 날짜부터 확보해야 한다.
5. **기존 산출물** — sec #3 4편은 정책 없이(cutoff 2025-12-31 view) 생성됐다. 새 규약에서는 비교 대상이 아니므로 재실행한다.
6. **GT reference 보강**(origin 문서 §4.3) — corpus 에 없는 GT ref 추가는 이번 범위 밖. 추가하더라도 cutoff 이전 판만 허용된다는 규칙은 이 코드가 그대로 적용한다(sidecar 에 날짜만 넣으면 됨).
7. 다른 3개 agent(SurveyForge·SurveyX·LLM×MR)에도 같은 topic 정책 파일을 적용해야 통제 실험이 성립한다 — 정책 JSONL 은 agent 무관 형식이고, 문헌 날짜 sidecar 규칙(§3)도 같은 export 에서 재사용 가능.
