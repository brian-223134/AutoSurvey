# 검색 허용 정책 — GT survey 최초 공개일 이전 문헌만 검색 (2026-09-14, 현행 판 r4 2026-09-30)

**정본.** 교수님 지시(2026-09-14): reference cutoff 를 2025-12-31 로 고정하지 말고, **GT 로 쓰는 survey 의 최초
publish 날짜 이전까지만 retrieval** 할 수 있게 한다. 이 문서는 그 구현·근거·검증·한계를 적는다. 실험 방향 전체는
[`direction-2026-09.md`](direction-2026-09.md), 원본 파라미터 정리와 개선 계획 원문은 저장소 밖 문서(`origin_autosurvey_generation_parameters.md` §4).

## 0. 한눈에

| 항목 | 값 |
|---|---|
| 규칙 | 문헌 공개일의 **상한**(정밀도상 가장 늦은 날짜) `< retrieval_cutoff_at` 일 때만 허용. 당일 제외. 날짜 불명은 제외 |
| cutoff | topic 별 `gt_first_public_at` = GT 의 **가장 이른** 공개일(arXiv 선행판 v1 > Crossref created > published-online) |
| 구현 | `src/retrieval_policy.py`(규칙) · `src/database.py`(FAISS `IDSelectorBitmap` — 검색 **자체**가 허용 집합 안에서 돈다) · `main.py`(`--topic_policy/--topic_id`, `--retrieval_cutoff`, `--exclude_ids`) |
| 정책 파일 | **`data/topic_policy.kisti-2608-r4.jsonl`**(현행 view r4, 25행 전부 status ok; cutoff 값은 view 무관, `corpus_snapshot_id` 와 corpus 측 분모 필드 `n_gt_refs_cutoff`·`_pool` 만 다름. **DB 와 같은 판끼리 짝**) · 이전 판 `topic_policy.kisti-2608{,-r2}.jsonl` · `data/topic_policy.kisti-2512.jsonl`(v2 기록) + 근거 캐시 `data/topic_policy.kisti-2512.sources.json` — `scripts/build_topic_policy.py` 산출 |
| 문헌 날짜 | DB 디렉터리의 sidecar `paper_dates.json`: arXiv id → 투고월(month), DOI → OpenAlex `publication_date`(day), 나머지 KISTI 연도(year). **현행은 corpus 측 `kisti_data/data/views/kisti-2608-r4/paper_dates.json` 사본**(4 agent 공통, `adapter/common/paper_dates.py`; AutoSurvey 의 `scripts/build_paper_dates.py` 와 같은 규칙·형식). sidecar 없으면 arXiv 월 + 연 단위로 판정 |
| 기록 | `<topic>.json['retrieval_policy']`(정책·허용 편수·허용 집합 sha256·제외 사유별 편수) → `collect_run.py` 가 `run.json` 으로 |
| corpus | **view `kisti-2608-r4`**(2026-09-30, 1,697,512편, **시간 컷 없음**) — corpus 는 스냅샷 전체를 두고 topic 정책이 자른다. AutoSurvey DB `database_kisti-kisti-2608-r4/` = kisti-2608 → r2(+32,550) → r4(+1,258) append. §10·§11 |
| 영향 | 25 topic 중 **18편**은 arXiv 판(선행판 v1·GT 자체) 날짜가 cutoff 라 2022-11 ~ 2026-04; **7편**은 Crossref 근거(2025-12 ~ 2026-07). 허용 corpus 70~100%. 분모 합 **4,010**(r4). §5 표 |

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
| arXiv id (신형·구형) | id 의 YYMM = v1 투고월. OpenAlex 는 보지 않는다 — KISTI 의 arXiv 레코드 초록이 v1 이 아닐 수 있어 월 상한이 안전 | month | 460,772 (v2 DB 454,958) |
| DOI | OpenAlex 미러 `works.parquet`(4.79억 편) `publication_date`, DOI 조인. **OpenAlex 연도 < KISTI 연도면 다른 판**이므로 KISTI 연도 유지 | day | 1,198,375 (v2 DB 1,191,972) |
| DOI (OpenAlex 연도 충돌 4,556 · 미매칭 1) | KISTI `year` | year | 4,557 |

- 파일: 현행 `database_kisti-kisti-2608-r4/paper_dates.json` = corpus 측 `kisti_data/data/views/kisti-2608-r4/paper_dates.json` 사본(63,693,838 B, md5 `f8fa28e3917bd91bf225300dcde9e508`, created_at `2026-09-30T02:11:54Z`, 4 agent 공통; r2 이후 overlay 문헌은 `published_at` 을 쓴다). 이전: `database_kisti-kisti-2608/paper_dates.json`(kisti-2608 판, 62,744,411 B, md5 `aa145cc4…`), v2 DB 용 AutoSurvey 자체 생성본(62,332,660 B, 428초 — 디렉터리와 함께 09-30 삭제). 형식 `{"meta":…, "dates": {id: "YYYY[-MM[-DD]]"}}`. 지문은 `REPRODUCTION.md` §3-C. DB 디렉터리는 gitignore 라 **재현 시 복사하거나 다시 만든다**(`build_paper_dates.py`).
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
| diffusion-model-alignment | **2024-09-11** | twin 2409.07253 v1 | 09-28 twin 등록(이전 2026-02-10 Crossref) — §11 |
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
| llm-edge-inference | 2026-04-24 | twin 2604.22906 v1 | 09-28 twin 등록(날짜 동일) — §11 |
| llm-distributed-training | 2024-07-29 | twin 2407.20018 v1 | |
| edge-cloud-collaboration | 2025-05-03 | twin 2505.01821 v1 | |
| wireless-foundation-models | 2025-12-26 | Crossref created (COMST early access) | arXiv 2601.03181 은 2026-01-06 |
| ai-wireless-reasoning | **2025-09-11** | twin 2509.09193 v1 | 09-28 twin 등록(이전 2026-04-23 Crossref) — §11 |
| agentic-satellite-networks | 2026-02-03 | Crossref created | twin 없음 |
| ai-video-streaming | 2024-06-04 | twin 2406.02302 v1 | |

## 5. corpus 와 채점 분모에 미치는 영향 (view `kisti-2608-r4`, `scripts/policy_report.py`, 2026-09-30)

allowed = 허용 편수 / 1,697,512. **n_gt_refs_cutoff** = corpus 측이 재계산한 채점 분모(`kisti_data/data/topics.kisti.jsonl`, `n_gt_refs_cutoff_view` = `kisti-2608-r4 32a77a48`; 규칙 identifiable ∧
ref 공개일 상한 < cutoff ∧ view 안 ∧ 레코드 날짜 상한 < cutoff). `gap_to_80_refs.jsonl` 의 `tier == in_view` 와 **25/25 일치**.
blocked = view 엔 있지만 레코드 날짜가 거칠어 정책이 막는 ref(`in_view_blocked`, 합 2). undated = 날짜 없는 ref(합 3). pool = cutoff 이전 identifiable
ref 전체(이론적 ceiling 분모). 출처 = cutoff 근거.

| topic_id | cutoff | 출처 | allowed | n_gt_refs_cutoff | blocked | undated | pool |
|---|---|---|---:|---:|---:|---:|---:|
| instruction-tuning-llms | 2023-08-21 | arxiv:2308.10792 | 1,305,390 (77%) | 131 | 0 | 0 | 138 |
| llm-function-calling | 2026-01-14 | crossref:10.1145/3788284 | 1,655,800 (98%) | 153 | 0 | 0 | 157 |
| model-merging | 2024-08-14 | arxiv:2408.07666 | 1,461,094 (86%) | 211 | 1 | 1 | 222 |
| diffusion-model-alignment | 2024-09-11 | arxiv:2409.07253 | 1,470,953 (87%) | 179 | 0 | 0 | 189 |
| llm-agent-optimization | 2025-03-16 | arxiv:2503.12434 | 1,541,302 (91%) | 190 | 0 | 0 | 197 |
| retrieval-explainability | 2022-12-14 | arxiv:2212.07126 | 1,202,705 (71%) | 141 | 0 | 0 | 171 |
| trustworthy-rag | 2025-02-08 | arxiv:2502.06872 | 1,529,357 (90%) | 116 | 0 | 0 | 133 |
| large-models-timeseries | 2023-10-16 | arxiv:2310.10196 | 1,327,286 (78%) | 281 | 0 | 1 | 325 |
| deep-graph-clustering | 2022-11-23 | arxiv:2211.12875 | 1,191,311 (70%) | 110 | 0 | 0 | 142 |
| negative-sampling-recsys | 2026-01-28 | crossref:10.1145/3793855 | 1,658,303 (98%) | 172 | 0 | 0 | 249 |
| mllm-adversarial-attacks | 2026-03-30 | arxiv:2603.27918 | 1,676,337 (99%) | 106 | 0 | 0 | 109 |
| llm-training-data-detection | 2026-01-07 | crossref:10.1145/3779430 | 1,654,323 (97%) | 87 | 0 | 0 | 109 |
| physical-adversarial-attacks | 2022-11-03 | arxiv:2211.01671 | 1,186,719 (70%) | 158 | 0 | 0 | 183 |
| harmful-finetuning | 2024-09-26 | arxiv:2409.18169 | 1,473,965 (87%) | 144 | 0 | 0 | 145 |
| llm-watermarking | 2025-12-05 | crossref:10.1145/3773028 | 1,642,570 (97%) | 80 | 0 | 0 | 105 |
| moe-inference-optimization | 2024-12-18 | arxiv:2412.14219 | 1,504,520 (89%) | 174 | 1 | 0 | 191 |
| kv-cache-serving | 2026-07-01 | crossref:10.18653/v1/2026.findings-acl.1916 | 1,696,084 (100%) | 135 | 0 | 0 | 142 |
| edge-slm-cloud-llm | 2025-07-22 | arxiv:2507.16731 | 1,592,410 (94%) | 231 | 0 | 1 | 262 |
| llm-edge-inference | 2026-04-24 | arxiv:2604.22906 | 1,682,901 (99%) | 135 | 0 | 0 | 163 |
| llm-distributed-training | 2024-07-29 | arxiv:2407.20018 | 1,452,414 (86%) | 223 | 0 | 0 | 310 |
| edge-cloud-collaboration | 2025-05-03 | arxiv:2505.01821 | 1,562,699 (92%) | 240 | 0 | 0 | 346 |
| wireless-foundation-models | 2025-12-26 | crossref:10.1109/comst.2025.3648785 | 1,644,939 (97%) | 238 | 0 | 0 | 284 |
| ai-wireless-reasoning | 2025-09-11 | arxiv:2509.09193 | 1,611,575 (95%) | 127 | 0 | 0 | 154 |
| agentic-satellite-networks | 2026-02-03 | crossref:10.1109/comst.2026.3660854 | 1,665,588 (98%) | 151 | 0 | 0 | 307 |
| ai-video-streaming | 2024-06-04 | arxiv:2406.02302 | 1,432,358 (84%) | 97 | 0 | 0 | 204 |

- 25편 분모 합 **4,010**(kisti-2608 2,559 → 09-28 twin 등록 2,541 → r2 2,543 → r4 4,010). r4 가 GT survey reference 원문 확보분 1,258편을 넣어 topic 별로 최대 2배 넘게 커졌다(예: agentic-satellite-networks 66 → 151, llm-agent-optimization 102 → 190). **r2 이전 결과와 recall 을 같은 표에 놓지 않는다.**
- 09-28 twin 등록(§11)으로 diffusion-model-alignment(2026-02-10 → 2024-09-11)·ai-wireless-reasoning(2026-04-23 → 2025-09-11)의 cutoff 가 앞당겨졌다. 두 topic 의 이전 허용 집합은 무효.
- `in_view_blocked` 합 37(09-14) → 2(r4). r4 는 corpus 측 날짜 정밀화(overlay `published_at`)를 포함한다.
- 2026년 cutoff topic 은 2026년 문헌을 본다(예: kv-cache-serving 07-01 → 1,696,084). arXiv 2026 논문은 월 단위라 cutoff 달의 것은 제외된다(보수적).
- 선행판이 있는 topic 에서 GT 게재본에 나중에 추가된 ref(선행판 이후 문헌)는 분모에서 빠진다(pool 과 분모의 차이 일부).
- kisti-2608 판(2026-09-14) 표는 이 파일의 git 이력(`1527a80` 이전)에 있다. 그 판에서 v2 기준 추정치(S2 `publicationDate` 직접 판정)는 corpus 측 재계산과 ±3 이내였다.

## 6. 실행·기록

현행 판(r4) 기준. 판이 바뀌면 DB·sidecar·정책 파일을 **같은 판으로** 함께 바꾼다.

```bash
# 정책 생성 — 캐시만으로(네트워크 불필요). 새 twin 이 생기면 --fetch
python scripts/build_topic_policy.py --view kisti-2608-r4 --out data/topic_policy.kisti-2608-r4.jsonl
# DB: 이전 판 인덱스에 corpus 측 추가분 export 를 append (임베딩 GPU 수 분) — 먼저 --check-only
python scripts/append_snapshot.py --base ./database_kisti-kisti-2608-r2 \
    --new /data2/chanjoong/kisti_data/data/exports/kisti-2608-r4.autosurvey.minus-kisti-2608-r2.json --out ./database_kisti-kisti-2608-r4
#   (r2 디렉터리는 09-30 삭제 — 다시 만들려면 docs/db-manifests/README.md)
# 문헌 날짜 sidecar — corpus 측 파일 복사(4 agent 공통). 다른 DB 는 build_paper_dates.py 로 생성(asg-corpus env)
cp /data2/chanjoong/kisti_data/data/views/kisti-2608-r4/paper_dates.json ./database_kisti-kisti-2608-r4/
# 생성 — 정책 행은 --topic_id 로 고른다 (없으면 --topic 문자열 완전 일치)
python main.py --topic "A Survey on the Optimization of Large Language Model-based Agents" \
    --topic_policy data/topic_policy.kisti-2608-r4.jsonl --topic_id llm-agent-optimization \
    --db_path ./database_kisti-kisti-2608-r4 --embedding_model nomic-ai/nomic-embed-text-v1 \
    --section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200 ...
# 채점 — 분모 n_gt_refs_cutoff, 누수 검사 포함
python scripts/score_kisti.py --json "output/<dir>/<topic>.json" \
    --topic_policy data/topic_policy.kisti-2608-r4.jsonl --topic_id <slug> --out "output/<dir>/<topic>.score.json"
# 영향 표
python scripts/policy_report.py --policy data/topic_policy.kisti-2608-r4.jsonl --db-path ./database_kisti-kisti-2608-r4
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

### 8-2. kisti-2608 DB 스모크 (2026-09-14, append 직후)

- DB 로드 48초, 인덱스 = id 매핑 = TinyDB = sidecar 1,663,704. append 구간(위치 1,651,487 이후) 표본은 전부 2026-01 문헌(`10.1001/jamanetworkopen.2025.52099` 2026-01-16, `2601.22158` 2026-01), base 구간 표본은 v2 그대로.
- `check_db.py --skip-search` 통과.

| topic | cutoff | 허용 (기대) | 제외 day / month / year | outline 풀 1,200 위반 | 가장 늦은 허용 | 2026년 문헌 |
|---|---|---:|---|---:|---|---:|
| physical-adversarial-attacks | 2022-11-03 | **1,186,466** (1,186,466) | 332,849 / 142,636 / 1,753 | 0 | 2022-10-31 (`2210.17140`) | 0 |
| kv-cache-serving | 2026-07-01 | **1,663,704** (1,663,704) | 0 / 0 / 0 | 0 | 2026-01-31 (`2601.21420`) | 48 |
| llm-training-data-detection | 2026-01-07 | **1,653,071** (1,653,071) | 4,819 / 5,814 / 0 | 0 | 2025-12-31 (`2512.24265`) | 0 |

- physical-adversarial 의 허용 집합 sha256 `4bee99cd9f46c4fc…` 는 v2 DB 스모크(§8)와 **같다** — v2 prefix 가 바이트 그대로이고 추가분 12,217편이 이 topic 에는 하나도 허용되지 않는다는 뜻.
- kv-cache-serving 의 outline 풀에 2026년 문헌 48편이 들어왔다 — 시간 컷 없는 view 로 바꾼 효과. llm-training-data-detection(01-07)은 2026년 문헌이 날짜 상한(1월 말·1-16 등) 때문에 전부 제외됐다 — 보수적 규칙대로.

## 9. 한계·미결

1. **arXiv 레코드의 버전** — KISTI 의 arXiv 레코드(`10.48550/arxiv.<id>`)는 버전 없는 키라 초록이 최신판일 수 있다. 월 단위 상한으로 "v1 이 cutoff 이전"임은 보장하지만 제공하는 초록이 v1 것이라는 보장은 없다(origin 문서 §4.4 "v1 만 허용되는 경우 원문·파생자료도 v1 인지"). 해결하려면 arXiv 판별 재수확이 필요 — 미착수.
2. **OpenAlex `publication_date` 의 의미** — 저널판의 게재일이다. 같은 논문의 arXiv 판이 corpus 에 따로 있으면 그 레코드는 자기 월로 판정되므로 판별 규칙과 어긋나지 않는다.
3. **twin 없는 GT — 12편 → 7편**(09-28 에 3편 등록, §11; 남은 7편은 cutoff 가 Crossref 근거) — 등록된 선행판이 없을 뿐, 존재하지 않는다는 확인은 아니다(kv-cache-serving 등 ACL 논문은 있을 가능성이 높다). 발견되면 `candidate.yaml gt.arxiv_id` 또는 TWIN 표에 등록하고 정책을 재생성한다. view 에서의 제외(누수)는 corpus 측 재작업.
4. **채점 분모** — corpus 측이 09-14 에 재계산 완료(`n_gt_refs_cutoff`, §5). 남은 것: `in_view_blocked` 37건을 ceiling 손실로 둘지 날짜를 정밀화할지, `llm-watermarking` S2 재추출. → **09-30 r4 로 재계산(합 4,010, `in_view_blocked` 2)**, §5.
5. **기존 산출물** — sec #3 4편은 정책 없이(cutoff 2025-12-31 view) 생성됐다. 새 규약에서는 비교 대상이 아니므로 재실행한다.
6. **GT reference 보강**(origin 문서 §4.3) — corpus 에 없는 GT ref 추가는 이번 범위 밖. 추가하더라도 cutoff 이전 판만 허용된다는 규칙은 이 코드가 그대로 적용한다(sidecar 에 날짜만 넣으면 됨). → **09-30 r4 가 GT reference 원문 확보분 1,258편을 corpus 에 넣었다**(§11). 규칙은 그대로 적용됐다.
7. 다른 3개 agent(SurveyForge·SurveyX·LLM×MR)에도 같은 topic 정책 파일을 적용해야 통제 실험이 성립한다 — corpus 측이 공통 판정 모듈 `adapter/common/retrieval_policy.py` 와 공통 sidecar 를 마련했고(09-14), 각 agent 의 검색 경로 적용은 그쪽 세션 몫(`AGENT-HANDOFF.md` §0).
8. **2026년 arXiv 초록 결손** — KISTI 의 arXiv `2602.*`~`2606.*` 36,697편은 초록이 없어 view 규칙(abstract ≥ 50)에서 빠진다(`2601.*` 만 초록 있음). 2026년 cutoff 9 topic 에 직접 영향. 회수 여부는 corpus 측 결정 대기 — AutoSurvey 는 시도하지 않는다. → **09-28 r2 가 스냅샷 초록으로 32,550편을 편입해 해소**(§11; non-CS 4,508편은 거부).

## 10. 2026-09-14 후속 — 시간 컷 없는 view `kisti-2608` 로 전환

> 기록. 현행 판은 r4(§11). `database_kisti-kisti-2608/` 은 보존, 그 base 였던 `database_kisti-kisti-2512/` 는 09-30 삭제.

corpus 측(`kisti_data`, `docs/asg/AGENT-HANDOFF.md` §0)이 `view.py --no-year-cutoff` 로 **`kisti-2608`**(1,663,704편 = kisti-2512 v2 + 2026년 12,005 + arXiv 2601.* 212 복귀,
papers.parquet sha `c1a0c6b3…`, created_at `2026-09-14T13:18:56Z`)을 만들고, 추가분 export(`kisti-2608.autosurvey.minus-kisti-2512.json`, 12,217편)·공통 sidecar·분모 재계산을 끝냈다. AutoSurvey 쪽 적용:

| 항목 | 내용 |
|---|---|
| DB | `database_kisti-kisti-2608/` = v2 4파일을 읽어 추가분 12,217편을 nomic 으로 임베딩해 **뒤에 append**(`scripts/append_snapshot.py`, IndexFlatL2 라 기존 행 번호 보존, TinyDB 순서 = v2 prefix + 추가분). 출처 `append_manifest.json`, 전체 export manifest `kisti-2608.autosurvey.json.manifest.json`, 추가분 manifest `append_source_manifest.json`. 지문 `REPRODUCTION.md` §3-C |
| append_snapshot.py 수정 | KISTI 레코드엔 `authors` 가 없어 필수 필드에서 뺌(런타임 무관); 중복 판정을 `id.split('v')` 에서 arXiv base id / DOI 전체 비교로 바꿈(DOI 안의 'v' 에서 서로 다른 DOI 가 뭉치던 결함); 출처 manifest 기록 |
| sidecar | corpus 측 `data/views/kisti-2608/paper_dates.json` 을 그대로 복사(md5 `aa145cc4…`). 4 agent 가 같은 파일로 판정 |
| 정책 파일 | `data/topic_policy.kisti-2608.jsonl` — 캐시만으로 재생성(네트워크 없음). cutoff 25행 전부 corpus 측 `topics.kisti.jsonl` 의 `retrieval_cutoff_at` 과 일치. 행에 `n_gt_refs_cutoff`·`_pool`·`_view` 추가 |
| 검증 | §5 표(sidecar 기준)가 corpus 측 표와 25/25 일치. 실 DB 스모크 §8-2: 3 topic 허용 편수 기대치와 일치, 위반 0 |
| 실행 | `--db_path ./database_kisti-kisti-2608 --topic_policy data/topic_policy.kisti-2608.jsonl --topic_id <slug>`. 결과 버전 열 `c1a0c6b3 / 2026-09-14T13:18:56Z` |
| 하지 않은 것 | `KISTI_VIEW` 기본값 변경(corpus 측), 2026년 arXiv 초록 결손 회수 — 둘 다 결정 대기 |

## 11. 2026-09-28 ~ 09-30 — twin 3편 등록, r2 · r4 판

corpus 측 이력은 `kisti_data/docs/asg/AGENT-HANDOFF.md` §0. AutoSurvey 쪽에서 바뀐 것만 적는다. **cutoff 규칙·코드(`src/retrieval_policy.py`·`src/database.py`)는 그대로**이고, 정책 파일·DB·sidecar 만 판을 따라 바뀌었다.

| 날짜 | 변경 | AutoSurvey 산출 |
|---|---|---|
| 09-28 | **twin 3편 등록**(CSUR 2026 GT pool 수확에서 발견): diffusion-model-alignment ↔ `2409.07253`(v1 2024-09-11) · ai-wireless-reasoning ↔ `2509.09193`(v1 2025-09-11) · llm-edge-inference ↔ `2604.22906`(v1 2026-04-24, 날짜 동일). 두 topic 의 cutoff 가 앞당겨지고 제외 키 40 → 43. 세 twin 은 KISTI 에 없어 view 편수 불변 | `build_topic_policy.py` 에 TWIN 3행, 근거 캐시 갱신, `topic_policy.kisti-2608.jsonl` 재생성 (`6cef3d7`) |
| 09-28 | **view `kisti-2608-r2`**(1,696,254편, sha `6727c7b8`) = kisti-2608 + KISTI arXiv 2026 초록 결손분 32,550편(스냅샷 초록·v1 제출일 overlay). cutoff 불변, 분모는 kv-cache-serving 61 → 63 만 | `topic_policy.kisti-2608-r2.jsonl`(`0c5f0c6`) · `database_kisti-kisti-2608-r2/`(append 32,550, 7분 26초) — **09-30 삭제**, 지문 `REPRODUCTION.md` §3-C |
| 09-30 | **view `kisti-2608-r4`**(1,697,512편, sha `32a77a48`) = r2 + GT survey reference 원문 확보분 1,258편(arXiv v1 e-print 784 · OA/무료 proceedings PDF 114 · t0 구제 · 날짜 정밀화). GT 1-hop coverage 51.5% → 81.2%. cutoff 불변, **분모 합 2,543 → 4,010**. r3(`ae27f069`)는 발행만 되고 채택되지 않았다 | `topic_policy.kisti-2608-r4.jsonl`(`1527a80`) · `database_kisti-kisti-2608-r4/`(r2 + 1,258 append, **현행**) · sidecar r4 판 복사 |

- **r4 검증**(corpus 측): title·abs 1,697,512벡터 정합, 검색 스모크 OK. `check_db.py` §4 최저 cos 0.9798 '문제 있음' 은 기록된 nomic 오탐 — base 구간은 r2 와 바이트 동일(표본 5,002행), 추가분은 재임베딩 cos 1.0. **재빌드 금지.**
- **r4 PoC**(AutoSurvey, 09-30): llm-agent-optimization 허용 1,541,302 · 지문 `efe95869`(corpus 측 기대치와 일치) · recall 13/190 · 누수 0. `docs/experiments/kisti-2608-r4-poc-llm-agent-optimization.md`.
- 다른 agent 주의(corpus 측 기록): SurveyForge 는 `SURVEYFORGE_PAPER_DATES` 를 r4 sidecar 로 지정하지 않으면 r4 에 새로 들어온 문헌이 '날짜 불명'으로 빠진다. AutoSurvey 는 DB 디렉터리의 `paper_dates.json` 을 읽으므로 해당 없음 — **DB 디렉터리에 같은 판 sidecar 가 있는지가 전부다.**
