# 현재 실험 방향 — KISTI corpus 벤치마크 (2026-09-07 기준)

이 문서가 **현행 정본**이다. `README.md`·`HANDOFF.md`·`REPRODUCTION.md`·`SETTING.md`의 2026-08 단계 내용(배포본·최신화본 DB, 분량 통제, 백본 비교)은 기록으로 남기되, 지금 실험은 아래를 따른다. 결정이 바뀌면 이 문서의 §8 결정 로그부터 고친다.

## 0. 한눈에

| 항목 | 값 |
|---|---|
| 목표 | **4개 ASG agent**(AutoSurvey · SurveyForge · SurveyX · LLM×MapReduce-V2)를 **같은 corpus·같은 백본·같은 topic 25편**으로 돌려 GT survey 참고문헌 대비 recall·precision을 비교 |
| corpus | **KISTI Science Data Lake 파생 스토어**(14.8M편 전편 원문) → view `kisti-2512` **1,651,701편**. asg-common-corpus(bench-2512)는 2026-09-07부로 **미사용** |
| AutoSurvey DB | `database_kisti-kisti-2512/` (12.3GB, 2026-09-07 빌드·argmax 검증) — 지문은 `REPRODUCTION.md` §3-C |
| topic | 5 domain × 5 = 25편 (`kisti_data/data/topics.kisti.jsonl`의 `title`). GT 본체 25 + twin 15 = 38키 view에서 제외 |
| 백본 | `meta-llama/llama-3.3-70b-instruct` @ OpenRouter, provider 핀 **akashml/fp8** |
| 디코딩 프로파일 | **temperature 0.6 · max_tokens 8192 · 잘림 재요청 on** (§3) |
| 출력 분량 | **통제하지 않는다** (§4). 본배치는 논문 기본값(8섹션, 서브섹션 상한 없음, `subsection_len` 700) |
| 평가 | GT in-view refs 분모의 recall + precision 병기, refs 수 공변량, run-to-run ±1.7%p(잠정), topic ceiling 병기 (§5) |
| 진행 | sec #3(physical-adversarial) 4편 완료(§6). 25편 본배치 **미착수**, OpenRouter 키 잔여 약 $5.4 |
| 워크스페이스 | corpus·adapter·topic 선정: `/data2/chanjoong/kisti_data/` (별도 git, remote 없음). AutoSurvey 쪽은 이 저장소 |

## 1. 목표와 설계

- **GT-first 벤치마크**: cutoff 2025-12-31 **이후** 출판된 human survey(CSUR·COMST·TKDE 등)를 GT로 두고, 그 참고문헌이 corpus 안에 얼마나 있는지(ceiling)를 먼저 재고, agent가 그중 얼마나 인용하는지(recall)를 잰다. 선정 과정·게이트는 `kisti_data/docs/topic-selection.md`.
- **통제 변수 = 입력 쪽**: corpus·cutoff·GT/twin 제외·topic 문자열·백본·provider·temperature·max_tokens·검색 예산(AutoSurvey: `rag_num 60`, `outline_reference_num 1200`). 이것이 "인용할 기회"의 평등이다.
- **agent 속성 = 출력 쪽**: 섹션·서브섹션 수, 단어 수, refs 수는 각 agent 논문 기본값이 만드는 대로 두고 기록한다.
- 결과표는 corpus가 다른 실험(2026-08 배포본/최신화본, bench-2512)과 **같은 축에 놓지 않는다**.

## 2. corpus — KISTI DB와 view `kisti-2512`

| 항목 | 값 | 출처 |
|---|---|---|
| 패키지 | `/data2/chanjoong/kisti_data/science_datalake_260825/` — DuckDB 7종 + `body_store.sqlite`(원문, zlib) + tantivy BM25. **읽기 전용, 이동 금지** | `kisti_data/docs/kisti-db.md` |
| 전체 | 14,843,789편, DOI 키, 연 단위 `year`만 있음 | 〃 |
| universe `kisti` | year ≤ 2025 ∧ ¬철회 ∧ title ∧ abstract ≥ 50자 ∧ (en ∨ null) ∧ (CS topic ∨ arXiv cs.*) = 1,651,706 | `data/views/kisti-2512/view_manifest.json` |
| view | 1,651,701편 (GT/twin 5편 제외 실적용). arXiv id 455,171 (27.6%) · DOI id 1,196,530 | 〃 |
| id 규칙 B | `10.48550/arxiv.<id>` → arXiv base id, 그 외 DOI 소문자. url은 각각 arxiv.org/abs · doi.org | `adapter/common/ids.py` |
| export | `data/exports/kisti-2512.autosurvey.json` 2.35GB, content_sha256 `54b4e7b4…` | manifest |
| 특징 | 출판 venue 논문(IEEE·Springer·ACM…)이 72%, 전편 원문 보유. **2023–2025 arXiv 수록률 56–63%**라 LLM 시대 topic의 ceiling이 낮다(25편 21~68%) | `topic-selection.md` §7 |

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
| 분모 | GT refs 중 identifiable ∧ pre-cutoff ∧ **view 안에 있는 것**(in_view). `kisti_data/candidates/gap_to_80_refs.jsonl`의 `tier == in_view`. sec #3은 149편 |
| 매칭 키 | 생성 refs의 id → `doi` ∨ `10.48550/arxiv.<base id>` (감사와 동일) |
| 지표 | **recall**(분량 의존) + **precision**(인용 1편당 GT 적중, 분량 중립) + refs 수. 25편 × 4 agent가 쌓이면 recall 대 refs 수 산점도 |
| 병기 | run-to-run 오차 **±1.7%p(잠정, 같은 코드 2회 차이 3.4%p)** · topic ceiling(예: sec #3 68%) · 잘림 재요청 수 |
| 누수 | GT DOI·twin arXiv id·twin 제목이 본문·refs에 0회여야 함. 인덱스 id 매핑에서도 부재 확인 |
| 기록 | 편당 `<topic>.run.json`(`scripts/collect_run.py`) — 모델·provider·비용·재시도·잘림·DB manifest sha·구조·쪽수 |

## 6. 지금까지의 실측 — sec #3 physical-adversarial-attacks (ceiling 68%)

| 편 | 프로파일 | 소요 / 비용 | 구조 / 본문 단어 | 루프 오염 | refs (arXiv/DOI) | recall / precision |
|---|---|---:|---|---|---|---|
| 첫 편 | temp 0, 가드 없음 | 93분 / $0.307 | 8/17 · 36.6K | 1서브 (26.6K단어) | 156 (87/69) | 12.8% / 12.2% |
| t06-r1 | 0.6 + 8K 가드 | 53분 / $0.374 | 8/25 · 22.8K | 2서브 (9.6K) | 235 (142/93) | 13.4% / 8.5% |
| t06-r2 | 0.6 + 가드 + 재요청 | 30분 / $0.338 | 9/24 · 14.3K | **0** | 184 (92/92) | 8.1% / 6.5% |
| t06-r3 | 〃 (같은 코드) | 19분 / $0.347 | 8/28 · 16.5K | **0** | 240 (118/122) | 11.4% / 7.1% |

네 편 합집합 GT 적중 29/149. refs 겹침은 편 사이 Jaccard 0.11~0.18 — 검색 풀이 같아도 writer의 인용 선택이 샘플링에 크게 좌우된다. 상세: `docs/experiments/kisti-2512-sec3-*.md`.

## 7. 다음 단계

1. **25편 본배치** — 조건 §3·§4. 편당 약 20~30분·$0.35 → 24편 약 $8.4. **OpenRouter 키 한도 상향 필요**(잔여 약 $5.4). 실행 템플릿은 `docs/experiments/kisti-2512-sec3-temp06-runs.md` §6에서 `--subsection_num 4 --subsection_len 520`을 `--subsection_len 700`으로 바꾼 것.
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

## 9. 관련 문서

- corpus·adapter: `kisti_data/docs/kisti-db.md` · `kisti_data/docs/asg/README.md` · `kisti_data/adapter/README.md` · 다른 agent용 인수인계 `kisti_data/docs/asg/AGENT-HANDOFF.md`
- topic 선정·ceiling: `kisti_data/docs/topic-selection.md` · `kisti_data/candidates/README.md`
- 실행 기록: `docs/experiments/kisti-2512-sec3-physical-adversarial-attacks.md`(첫 편) · `kisti-2512-sec3-temp06-runs.md`(r1~r3) · `probe-temp06-length-coefficient.md`
- 2026-08 단계(기록): `docs/commoncorpus-setup.md` · `docs/experiments/bench-2512-ai1-instruction-tuning.md` · `README.md` §3·§4
