# 현재 실험 방향 — KISTI corpus 벤치마크 (2026-09-07 기준, 09-14 검색 정책, 09-30 corpus r4)

이 문서가 **현행 정본**이다. `README.md`·`HANDOFF.md`·`REPRODUCTION.md`·`SETTING.md`의 2026-08 단계 내용(배포본·최신화본 DB, 분량 통제, 백본 비교)은 기록으로 남기되, 지금 실험은 아래를 따른다. 결정이 바뀌면 이 문서의 §8 결정 로그부터 고친다.

## 0. 한눈에

| 항목 | 값 |
|---|---|
| 목표 | **4개 ASG agent**(AutoSurvey · SurveyForge · SurveyX · LLM×MapReduce-V2)를 **같은 corpus·같은 백본·같은 topic 25편**으로 돌려 GT survey 참고문헌 대비 recall·precision을 비교 |
| corpus | **KISTI Science Data Lake 파생 스토어**(14.8M편 전편 원문) → view **`kisti-2608-r4` 1,697,512편**(2026-09-30 ~, **시간 컷 없음** = kisti-2608 1,663,704 + arXiv 2026 초록 보강 32,550(r2) + GT survey reference 원문 확보분 1,258(r4); papers.parquet sha `32a77a48`). 이전: `kisti-2608-r2` 1,696,254(09-28~09-30), `kisti-2608` 1,663,704(09-14~09-28), `kisti-2512` v2 1,651,487, v1 1,651,701. asg-common-corpus(bench-2512)는 2026-09-07부로 **미사용** |
| AutoSurvey DB | **`database_kisti-kisti-2608-r4/`** — kisti-2608 → r2(+32,550) → r4(+1,258) 순으로 벡터 append(`scripts/append_snapshot.py`, `append_manifest.json`) + corpus 측 sidecar `paper_dates.json`(r4 판). **재빌드 금지.** 보존: `database_kisti-kisti-2608/`(LLM×MR pool). 09-30 삭제: `-2512/`·`-2512-v1/`·`-2608-r2/`(`docs/db-manifests/`). 지문 `REPRODUCTION.md` §3-C |
| topic | 5 domain × 5 = 25편 (`kisti_data/data/topics.kisti.jsonl`의 `title`). GT 본체 25 + twin·사본 18 = **43키** view에서 제외(09-28 twin 3편 등록 후) |
| 백본 | `meta-llama/llama-3.3-70b-instruct` @ OpenRouter, provider 핀 **akashml/fp8** |
| 디코딩 프로파일 | **temperature 0.6 · max_tokens 8192 · 잘림 재요청 on** (§3) |
| 출력 분량 | **통제하지 않는다** (§4). 본배치는 논문 기본값(8섹션, 서브섹션 상한 없음, `subsection_len` 700) |
| **검색 정책 (09-14)** | **topic 별 cutoff = GT survey 최초 공개일**(arXiv 선행판 v1 > Crossref created). 문헌 공개일 상한 < cutoff 일 때만 검색 후보. `--topic_policy data/topic_policy.kisti-2608-r4.jsonl --topic_id <slug>` (cutoff 값은 view 무관; `corpus_snapshot_id`·분모만 판 별 — **DB 와 같은 판끼리**). 정본 [`retrieval-policy.md`](retrieval-policy.md) |
| 평가 | recall + precision 병기, refs 수 공변량, run-to-run ±1.7%p(잠정), topic ceiling 병기 (§5). **분모 = `topics.kisti.jsonl` 의 `n_gt_refs_cutoff`**(topic cutoff ∧ view ∧ 레코드 날짜 허용; **r4 25편 합 4,173**(09-30 GT ref 식별자 보강 후; 보강 전 4,010) — r2 이전 2,543 과 같은 표 금지). 채점 `scripts/score_kisti.py` |
| 진행 | **r4 PoC 1편 완료**(llm-agent-optimization, recall 15/203 = 7.4% · precision 4.0%(보강 후 재채점) · 누수 0 · 31분 · $0.47, `docs/experiments/kisti-2608-r4-poc-llm-agent-optimization.md`). 나머지 **24편 본배치 미착수** — 약 $11.3 필요, OpenRouter 키 잔여 $10.16(09-30). sec #3 4편은 view v1·정책 없음 → 비교 대상 아님 |
| 워크스페이스 | corpus·adapter·topic 선정: `/data2/chanjoong/kisti_data/` (별도 git, remote 없음). AutoSurvey 쪽은 이 저장소 |

## 1. 목표와 설계

- **GT-first 벤치마크**: cutoff 2025-12-31 **이후** 출판된 human survey(CSUR·COMST·TKDE 등)를 GT로 두고, 그 참고문헌이 corpus 안에 얼마나 있는지(ceiling)를 먼저 재고, agent가 그중 얼마나 인용하는지(recall)를 잰다. 선정 과정·게이트는 `kisti_data/docs/topic-selection.md`.
- **통제 변수 = 입력 쪽**: corpus·cutoff·GT/twin 제외·topic 문자열·백본·provider·temperature·max_tokens·검색 예산(AutoSurvey: `rag_num 60`, `outline_reference_num 1200`). 이것이 "인용할 기회"의 평등이다.
- **cutoff 는 topic 별**(2026-09-14, 교수님 지시): 고정 2025-12-31 이 아니라 GT survey 의 **최초 공개일**(arXiv 선행판이 있으면 그 v1 날짜). 25편 중 14편이 2022-11~2025-07 로 앞당겨진다. view(`year ≤ 2025`)는 그대로 두고 agent 검색 단계에서 topic 정책으로 자른다 — [`retrieval-policy.md`](retrieval-policy.md).
- **agent 속성 = 출력 쪽**: 섹션·서브섹션 수, 단어 수, refs 수는 각 agent 논문 기본값이 만드는 대로 두고 기록한다.
- 결과표는 corpus가 다른 실험(2026-08 배포본/최신화본, bench-2512)과 **같은 축에 놓지 않는다**.

## 2. corpus — KISTI DB와 view `kisti-2512`

| 항목 | 값 | 출처 |
|---|---|---|
| 패키지 | `/data2/chanjoong/kisti_data/science_datalake_260825/` — DuckDB 7종 + `body_store.sqlite`(원문, zlib) + tantivy BM25. **읽기 전용, 이동 금지** | `kisti_data/docs/kisti-db.md` |
| 전체 | 14,843,789편, DOI 키, 연 단위 `year`만 있음 | 〃 |
| universe `kisti` | year ≤ 2025 ∧ ¬철회 ∧ title ∧ abstract ≥ 50자 ∧ (en ∨ null) ∧ (CS topic ∨ arXiv cs.*) = 1,651,706 | `data/views/kisti-2512/view_manifest.json` |
| view **v2** (2026-09-08) | **1,651,487편** = v1 − GT 사본 2편(`2507.16731` edge-slm-cloud-llm 선행판, `10.1109/comst.2025.3648785` wireless-foundation-models 출판본) − arXiv `2601.*` 212편(KISTI `year=2025` 오기재). papers.parquet sha **`591b4325…`**. arXiv id 454,958 · DOI id 1,196,529 | 〃 |
| view v1 (2026-09-07) | 1,651,701편, sha `c7b8d4e7…`. `data/views/kisti-2512-v1/`에 보존. sec #3 4편은 전부 v1 | 〃 |
| view `kisti-2608` (2026-09-14) | **1,663,704편** = v2 + 2026년 12,005 + arXiv `2601.*` 212 복귀. **시간 컷 없음**(스냅샷 260825 전체) — topic cutoff 는 agent 정책이 담당. papers.parquet sha **`c1a0c6b3…`**, created_at `2026-09-14T13:18:56Z`. arXiv id 460,772 · DOI 1,202,932. `data/views/kisti-2608/`, sidecar `paper_dates.json` 동봉 | `kisti_data/docs/asg/AGENT-HANDOFF.md` §0 |
| view `kisti-2608-r2` (2026-09-28) | 1,696,254편 = kisti-2608 + KISTI arXiv 2026 초록 결손분 32,550(스냅샷 초록·v1 제출일 overlay 로 편입, non-CS 4,508 거부). sha `6727c7b8` | 〃 |
| **view `kisti-2608-r4` (2026-09-30, 현행)** | **1,697,512편** = r2 + GT survey reference 원문 확보분 1,258(arXiv v1 e-print 784 · OA/무료 proceedings PDF 114 · t0 구제 · 날짜 정밀화). GT 1-hop coverage 51.5% → 81.2%(80% 이상 17/25) → GT ref 식별자 보강 후 **79.84%(16/25)**. sha **`32a77a48`**, sidecar 동봉 | 〃 · `kisti_data/analysis/coverage-status.md` |
| id 규칙 B | `10.48550/arxiv.<id>` → arXiv base id, 그 외 DOI 소문자. url은 각각 arxiv.org/abs · doi.org | `adapter/common/ids.py` |
| export | `data/exports/kisti-2512.autosurvey.json` — v2 1,651,487 레코드, content_sha256 `1bca9e73…` (v1은 `54b4e7b4…`) | manifest |
| 특징 | 출판 venue 논문(IEEE·Springer·ACM…)이 72%, 전편 원문 보유. **2023–2025 arXiv 수록률 56–63%**라 LLM 시대 topic의 ceiling이 낮다(25편 21~68%) | `topic-selection.md` §7 |

**문헌 공개일 sidecar** (2026-09-14, 현행 r4 판 2026-09-30): `database_kisti-kisti-2608-r4/paper_dates.json` = corpus 측 `data/views/kisti-2608-r4/paper_dates.json` 사본(4 agent 공통, md5 `f8fa28e3…`; kisti-2608 판은 md5 `aa145cc4…`) — arXiv id 는 투고월, DOI 는 OpenAlex `publication_date`(일 단위), r2 이후 overlay 문헌은 `published_at`, 나머지는 KISTI 연도. r4 판 1,697,512편 = month 462,193 · day 1,230,756 · year 4,563(kisti-2608 판: 460,772 · 1,198,375 · 4,557). 같은 규칙의 AutoSurvey 빌더는 `scripts/build_paper_dates.py`. gitignore 대상이라 재현 시 복사하거나 다시 만든다. 지문 `REPRODUCTION.md` §3-C.

AutoSurvey 쪽 함정: refs id가 arXiv/DOI 혼합이라 `main.py`·`md_to_tex.py`가 DOI 링크를 분기한다(`068c4e9`). `enrich_references.py`(arXiv API)는 DOI id에 동작하지 않는다 — view `authors.parquet`로 대체 후처리 **미구현**. Elsevier 제목의 `☆`는 md_to_tex가 제거한다.

## 3. 디코딩 프로파일 (`.env` 활성 블록)

```
AUTOSURVEY_MODEL=meta-llama/llama-3.3-70b-instruct
AUTOSURVEY_PROVIDER=akashml/fp8
AUTOSURVEY_TEMPERATURE=0.6
AUTOSURVEY_MAX_TOKENS=8192          # 잘림 가드 — 설정 시 AUTOSURVEY_RETRY_TRUNCATED 기본 on
AUTOSURVEY_REASONING=               # 비추론 모델
AUTOSURVEY_MAX_THREADS=1  AUTOSURVEY_MAX_RETRY=10   # 실행 시 export (akashml 429 대비)
AUTOSURVEY_DEVICE=cpu               # GPU 전량 점유 시 질의 임베딩만 CPU — 결과 무관
```

| 값 | 근거 |
|---|---|
| temperature **0.6** | temp 0에서 llama-3.3-70b가 반복 루프에 빠져 호출 하나가 128K 토큰·45분(첫 편 100분). 0.6은 Meta의 Llama 3.x 권장 기본값 — 외부 근거가 있고 어느 agent의 원 설정(1.0 / 0.3·0.5 / provider 기본)도 아니라 중립. **temp 0 금지** |
| max_tokens **8192** | 원논문의 설계 전제("호출당 출력 <8K", GPT-4 8k·Claude 3 4k). 정상 호출(서브섹션 ≈1K, 아웃라인 ≤2K 토큰)엔 안 걸림. 잘림 가드이지 분량 통제가 아님 |
| 잘림 재요청 | 가드에 걸린 응답은 정상일 수 없으므로 버리고 새 샘플(`baa46cc`). temp 0.6에서도 draft 호출의 약 30%가 루프에 빠지는데, 재요청으로 최종본 오염 0을 두 편 연속 확인 |
| top_p 등 | 건드리지 않음(손잡이 1개) |

다른 3개 agent에는 같은 프로파일(temperature 0.6, 출력 가드)을 **사용자가 직접 전달**한다. SurveyForge·LLM×MR은 환경변수, SurveyX는 단계별 하드코딩(0.3/0.5)이라 전역 오버라이드 훅이 필요하다.

## 4. 출력 분량 — 통제하지 않는다 (2026-09-07 결정)

- 실측: `--subsection_len`은 하한 지시값이고 모델이 둔감하다(지시 700 → 1,056단어, 520 → 965단어, 초안 기준). run-to-run CV 11~24%. 총 분량은 서브섹션 수와 인용 밀도가 지배한다(`docs/experiments/probe-temp06-length-coefficient.md`).
- 억지로 맞추면 agent 설계를 왜곡하면서도 맞춰지지 않는다 → **분량·refs 수는 agent 속성으로 기록**하고 평가를 분량 인식형으로 한다(§5).
- 본배치 AutoSurvey 인자: `--section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200` (`--subsection_num` 미지정 = 상한 없음). 2026-08의 20~25k 대역 목표와 `--subsection_num 4 --subsection_len 520` 캘리브레이션은 폐기.

## 5. 평가 규약

| 항목 | 규약 |
|---|---|
| 분모 | GT refs 중 identifiable ∧ **topic cutoff 이전**(ref 공개일 상한 < `retrieval_cutoff_at`) ∧ **view 안에 있는 것**(in_view). `gap_to_80_refs.jsonl`의 `tier == in_view` 에 날짜 조건을 추가 — 규모는 `retrieval-policy.md` §5 (sec #3 149 → 130). 채점기가 같은 규칙으로 재계산 |
| 매칭 키 | 생성 refs의 id → `doi` ∨ `10.48550/arxiv.<base id>` (감사와 동일) |
| 지표 | **recall**(분량 의존) + **precision**(인용 1편당 GT 적중, 분량 중립) + refs 수. 25편 × 4 agent가 쌓이면 recall 대 refs 수 산점도 |
| 병기 | run-to-run 오차 **±1.7%p(잠정, 같은 코드 2회 차이 3.4%p)** · topic ceiling(예: sec #3 68%) · 잘림 재요청 수 |
| 누수 | GT DOI·twin arXiv id·twin 제목이 본문·refs에 0회여야 함. 인덱스 id 매핑에서도 부재 확인. **정책 실행분은 `run.json['retrieval_policy']`의 `retrieval_cutoff_at`·`allowed_fingerprint_sha256` 기록 + 참고문헌 전부 허용 집합 안(저장 전 자동 검증)** |
| 기록 | 편당 `<topic>.run.json`(`scripts/collect_run.py`) — 모델·provider·비용·재시도·잘림·DB manifest sha·구조·쪽수 |
| **view 버전 표기** | 결과마다 view sha 앞 8자(**kisti-2608 `c1a0c6b3` / 2026-09-14T13:18:56Z**, v2 `591b4325`, v1 `c7b8d4e7`)와 인덱스 `view_diff_manifest.json`/`append_manifest.json`의 `created_at`을 적는다. 2026-09-08 08:08 UTC 이전 실행분은 v1 |

## 6. 지금까지의 실측 — sec #3 physical-adversarial-attacks (ceiling 68%, **view v1 `c7b8d4e7`**)

네 편 모두 v2 교체(2026-09-08) 전 실행이다. 제거된 216편(GT 사본 2 + 2601.* 212)은 이 topic과 무관하고 in_view 분모 149도 그대로라 수치는 유효하다.

| 편 | 프로파일 | 소요 / 비용 | 구조 / 본문 단어 | 루프 오염 | refs (arXiv/DOI) | recall / precision |
|---|---|---:|---|---|---|---|
| 첫 편 | temp 0, 가드 없음 | 93분 / $0.307 | 8/17 · 36.6K | 1서브 (26.6K단어) | 156 (87/69) | 12.8% / 12.2% |
| t06-r1 | 0.6 + 8K 가드 | 53분 / $0.374 | 8/25 · 22.8K | 2서브 (9.6K) | 235 (142/93) | 13.4% / 8.5% |
| t06-r2 | 0.6 + 가드 + 재요청 | 30분 / $0.338 | 9/24 · 14.3K | **0** | 184 (92/92) | 8.1% / 6.5% |
| t06-r3 | 〃 (같은 코드) | 19분 / $0.347 | 8/28 · 16.5K | **0** | 240 (118/122) | 11.4% / 7.1% |

네 편 합집합 GT 적중 29/149. refs 겹침은 편 사이 Jaccard 0.11~0.18 — 검색 풀이 같아도 writer의 인용 선택이 샘플링에 크게 좌우된다. 상세: `docs/experiments/kisti-2512-sec3-*.md`.

## 7. 다음 단계

1. **나머지 24편 본배치** — 조건 §3·§4 + **topic 정책**(`--db_path ./database_kisti-kisti-2608-r4 --topic_policy data/topic_policy.kisti-2608-r4.jsonl --topic_id <slug>`). r4 PoC 실측 편당 약 31분·$0.47 → 24편 약 $11.3(sec #3 도 정책으로 재실행). **OpenRouter 키 한도 상향 필요**(잔여 $10.16, 09-30). 실행·후처리·채점 템플릿은 `docs/experiments/kisti-2608-r4-poc-llm-agent-optimization.md` §6.
1-1. ~~채점 분모 재계산~~ — corpus 측 완료(09-14, r4 판 09-30 합 4,010 → GT ref 식별자 보강 4,173). `in_view_blocked` 37 → 2(r4). `llm-watermarking` S2 재추출은 여전히 권장.
1-2. **twin 미확인 GT 7편의 선행판 확인** — 09-28 에 3편 등록(`retrieval-policy.md` §11). 남은 7편(cutoff 가 Crossref 근거)도 있으면 등록 후 정책 재생성(`retrieval-policy.md` §9-3).
2. **DOI id 저자 보강** 후처리(`authors.parquet`) — 참고문헌 표기 품질용, 채점에는 무관.
3. **재요청 소진 대비** — 10회 다 쓰는 경우가 나오면 재요청 시 temperature 상향/프롬프트 변형.
4. 다른 agent 진행(`kisti_data/adapter/README.md` §5): SurveyForge 임베딩 빌드 미실행(GPU 약 4h), SurveyX 훅 적용 완료(`.env` 한 줄), LLM×MR stage 1은 이제 AutoSurvey KISTI DB가 있으므로 실행 가능.
5. 80% 커버리지 보강(스냅샷 합집합·GT 특정 추가·DOI-only)은 교수님 결정 대기 — `topic-selection.md` §5·§7.6.

## 8. 결정 로그

| 날짜 | 결정 | 근거·커밋 |
|---|---|---|
| 09-07 | asg-common-corpus 폐기, KISTI DB 채택. view `kisti-2512` | kisti_data `docs/topic-selection.md` §7 |
| 09-07 | AutoSurvey KISTI 인덱스 빌드(2h17m, GPU 3), argmax 60/60 검증 | `docs/experiments/kisti-2512-sec3-physical-adversarial-attacks.md` §4 |
| 09-07 | DOI id 링크 분기 | `068c4e9` |
| 09-07 | max_tokens 8192 가드 | `aa98d14` |
| 09-07 | temperature 0 → 0.6 | `cb1ba00` |
| 09-07 | 길이 계수 재측정, `subsection_len` 역산 폐기 | `cbc7b23`, `docs/experiments/probe-temp06-length-coefficient.md` |
| 09-07 | 잘림 재요청 | `baa46cc` |
| 09-07 | 분량 비통제, 본배치 논문 기본값, recall+precision 병기 | `docs/experiments/kisti-2512-sec3-temp06-runs.md` §7 |
| 09-07 | `☆`·`★` 제거 | `537886f` |
| 09-08 | view `kisti-2512` **v2** 교체(kisti_data 측): GT 사본 2편 + arXiv 2601.* 212편 제거, exclude 40키, AutoSurvey DB 같은 경로에서 차분 적용. 이후 실행은 v2, 이전 4편은 v1로 표기 | kisti_data `32c130d`·`cf1e9ba`, `AGENT-HANDOFF.md` §0 |
| **09-14** | **topic 별 retrieval cutoff = GT 최초 공개일**(교수님 지시). 문헌 공개일 상한 < cutoff 규칙, FAISS 선택자로 검색 자체 제한, 정책 파일 25행(전부 일 단위 근거), DOI 일 단위 날짜 sidecar(OpenAlex). 기존 4편은 정책 없음 → 재실행 | `docs/retrieval-policy.md`, `src/retrieval_policy.py`, `data/topic_policy.kisti-2512.jsonl` |
| **09-14** | corpus 측 후속: **시간 컷 없는 view `kisti-2608`**(1,663,704편)·sidecar·분모 재계산(`n_gt_refs_cutoff`). AutoSurvey 는 v2 인덱스에 추가분 12,217편 append → `database_kisti-kisti-2608/`, 정책 파일 `topic_policy.kisti-2608.jsonl`. 결과 버전 열 `c1a0c6b3 / 2026-09-14T13:18:56Z` | `kisti_data/docs/asg/AGENT-HANDOFF.md` §0, `retrieval-policy.md` §10 |
| 09-28 | twin 3편 등록(diffusion-model-alignment·ai-wireless-reasoning cutoff 앞당김, llm-edge-inference 날짜 동일), 제외 키 43 | `6cef3d7`, `retrieval-policy.md` §11 |
| 09-28 | view `kisti-2608-r2` 채택(arXiv 2026 초록 보강 32,550) — 정책 파일·DB append | `0c5f0c6` |
| **09-30** | **view `kisti-2608-r4` 채택**(GT reference 원문 1,258편, 분모 합 4,010, coverage 81.2%). 정책 파일 `topic_policy.kisti-2608-r4.jsonl`, DB `database_kisti-kisti-2608-r4/`. 결과 버전 열 `32a77a48 / 2026-09-30`. PoC 1편(llm-agent-optimization) 통과 | `1527a80`, `3827687`, `docs/experiments/kisti-2608-r4-poc-llm-agent-optimization.md` |
| 09-30 | 쓰지 않는 AutoSurvey DB 3개 삭제(`-2512-v1`·`-2512`·`-2608-r2`, 37 GB). 지문·메타데이터 보존 | `REPRODUCTION.md` §3-C, `docs/db-manifests/` |
| 09-30 | corpus 측 **GT ref 식별자 보강**(870건 중 371 복구, 499 채점 제외 규칙) → 분모 합 4,010 → **4,173**, coverage 79.84%(16/25). 정책 파일은 `n_gt_refs_cutoff`·`_pool` 만 갱신(cutoff·허용 편수 불변). PoC 재채점 13/190 → **15/203** | kisti_data `99cb340`·`067a125`, `kisti_data/analysis/gt-ref-resolve.md` |

## 9. 관련 문서

- **검색 정책(정본)**: [`retrieval-policy.md`](retrieval-policy.md) — 규칙·GT 날짜 근거·영향 표·검증·한계
- corpus·adapter: `kisti_data/docs/kisti-db.md` · `kisti_data/docs/asg/README.md` · `kisti_data/adapter/README.md` · 다른 agent용 인수인계 `kisti_data/docs/asg/AGENT-HANDOFF.md`
- topic 선정·ceiling: `kisti_data/docs/topic-selection.md` · `kisti_data/candidates/README.md`
- 실행 기록: `docs/experiments/kisti-2512-sec3-physical-adversarial-attacks.md`(첫 편) · `kisti-2512-sec3-temp06-runs.md`(r1~r3) · `probe-temp06-length-coefficient.md`
- 2026-08 단계(기록): `docs/commoncorpus-setup.md` · `docs/experiments/bench-2512-ai1-instruction-tuning.md` · `README.md` §3·§4
