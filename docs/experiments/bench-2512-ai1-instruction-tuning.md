# bench-2512 첫 편 — Instruction Tuning for LLMs (2026-09-03)

벤치마크 view `bench-2512`(947,451편)로 만든 **첫 산출물**의 기록이다.
목적은 품질 평가가 아니라 **파이프라인 검증** — DB·인덱스·누수 차단·생성·컴파일이
end-to-end로 도는지 확인하고, 25편 본배치의 단가·소요를 실측하는 것이다.

수치는 `output/bench-2512-ai1-instruction-tuning/Instruction Tuning for Large Language Models.run.json`
매니페스트에서 가져왔다. 벤치마크 설계와 GT 목록은
`../../../asg-common-corpus/candidates/{SELECTION.md,GT-SURVEYS.md}` 참고.

## 0. 왜 이 토픽인가

25편 중 **ai #1**을 첫 편으로 골랐다. "결과가 나쁘면 그게 곧 문제 신호"인 조건이 가장 깨끗하다.

| 기준 | 값 | 의미 |
|---|---|---|
| recall ceiling (cov) | **89%** — 25편 중 최고 | 점수가 낮으면 ceiling이 아니라 agent 탓임이 확정된다 |
| eligible ref | 153편 | 생성 refs 166 > 153이라 **분량이 recall을 구조적으로 누르지 않는다** |
| post-cutoff ref | 0.5% | 오염 사실상 없음 |
| twin | `2308.10792` | GT의 arXiv 선행판이 있어 **누수 차단을 검증할 수 있는** 토픽 |

GT: *Instruction Tuning for Large Language Models: A Survey* (ACM CSUR, 2026-01-08,
[10.1145/3777411](https://doi.org/10.1145/3777411)).

## 1. 실행 조건

| 항목 | 값 |
|---|---|
| 백본 | `meta-llama/llama-3.3-70b-instruct` @ OpenRouter, provider 핀 **akashml/fp8**, temp 0 |
| DB | `database_commoncorpus-bench-2512` — 947,451편, manifest sha `7393bef6…` |
| 인덱스 | 2026-09-03 신규 빌드 (§4) · `nomic-ai/nomic-embed-text-v1`, dim 768 |
| 파라미터 | `--section_num 8 --subsection_num 4 --subsection_len 520` (판 A 본편 대역) |
| 검색 | `--rag_num 60 --outline_reference_num 1200` |
| 동시성 | `MAX_THREADS=1` (8섹션 × 1 = 동시 8) + `MAX_RETRY=10` |
| 실행 | 2026-09-03 01:53 → 02:57 (UTC), `setsid nohup` 분리 |

```bash
source .env
export AUTOSURVEY_MAX_THREADS=1 AUTOSURVEY_MAX_RETRY=10
setsid nohup conda run --no-capture-output -n autosurvey python -u main.py \
  --topic "Instruction Tuning for Large Language Models" \
  --saving_path ./output/bench-2512-ai1-instruction-tuning/ \
  --db_path ./database_commoncorpus-bench-2512 \
  --embedding_model "$AUTOSURVEY_EMBEDDING_MODEL" \
  --model "$AUTOSURVEY_MODEL" --api_url "$AUTOSURVEY_API_URL" \
  --section_num 8 --subsection_num 4 --subsection_len 520 \
  --rag_num 60 --outline_reference_num 1200 > <log> 2>&1 < /dev/null &
```

## 2. 결과 — 08-31 Edge Computing 판 A와 비교

판 A는 같은 파라미터(8/4/520)·같은 백본이나 **DB가 다르다**(`example-2512`).
corpus가 다르므로 품질 비교가 아니라 **거동 비교**로만 읽을 것.

| 항목 | 이번 편 (bench-2512) | 판 A (example-2512, 08-31) |
|---|---|---|
| 구조 | 8섹션 / **23**서브 | 8섹 / 25서브 |
| 단어 (tex 본문) | **12,914** | 15,206 |
| refs / 인용 | **166 / 281** | 219 / 324 |
| PDF | **35쪽** | 42쪽 |
| 비용 | **$0.3449** | $0.2958 |
| 소요 | **64분 7초** | 12분 21초 |
| 재시도 | 2회 (전부 429) | 3회 |
| **잘린 호출** | **2건** ⚠ | 0건 |
| 서브당 단어 계수 | 561 (520 지시, **1.08×**) | 608 (1.17×) |

### 단계별 청구

| 단계 | in / out 토큰 | 비용 | 재시도 |
|---|---|---:|---:|
| outline | 428,077 / 7,650 | $0.0891 | 0 |
| writer | 994,287 / **271,846** | $0.2558 | 2 |
| **합계** | | **$0.3449** | 2 |

**outline 비용이 판 A($0.0885)와 거의 같다** — `outline_reference_num 1200`이 지배하는
고정비라 토픽이 바뀌어도 상수라는 08-31 관측이 다른 corpus·다른 토픽에서 재확인됐다.

## 3. 검증

| 검사 | 결과 |
|---|---|
| `check_survey.py` | **OK** — 댕글링 인용 0, 포맷 누출 0, json 매핑 166/166 |
| **누수 차단** (`2308.10792`) | **본문 등장 0회 ✅** |
| 서브섹션 끊김 (23개 전수) | **0건** — 전부 온전한 문장으로 종료 |
| PDF 컴파일 | latexmk 3패스, **최종 로그 미해결 인용 0**, `\bibitem` 166개, 35쪽 |

### 누수 차단이 end-to-end로 증명됐다

`bench-2512` view는 GT 선행판 13건을 제외한다. 인덱스 단계와 산출물 단계 양쪽에서 확인했다.

```
구 DB(example-2512, 947,463편) : 13건 전부 잔존  ← 누수
신 DB(bench-2512,  947,451편) : 0건            ← 차단
산출물 본문의 2308.10792       : 0회            ← 차단
```

구 DB로 돌렸다면 agent가 *"Instruction Tuning for LLMs: A Survey"* 자체를 검색해
목차와 인용을 그대로 베낄 수 있었다. **cutoff(2025-12-31)만으로는 못 막는다** —
선행판 13건이 2022-11~2025-05로 전부 cutoff 이전이기 때문이다.

## 4. 인덱스 빌드 — 5회 실패 후 성공

`bench-2512` 인덱스를 새로 빌드해야 했다. 인덱스는 **위치 기반**이라
(`id_to_index = {id: i for i, p in enumerate(papers_l)}`) 레코드 13개만 빠져도
그 뒤 전체 위치가 밀린다. 구 인덱스를 신 DB에 쓰면 **에러 없이 엉뚱한 논문이 검색된다.**

| 시도 | GPU | batch | 결과 |
|---|---|---|---|
| 1 | 2 | 256 | OOM — 타 사용자 프로세스가 39.55GB 점유 (**진짜 경합**) |
| 2~5 | 0 | 128 | OOM — **4회 전부 abstract 158/7402에서 바이트 단위 동일** (결정론적) |
| **6** | **6** | **256** | **성공** — 1시간 18분 (title 7분 + abstract 1시간 10분 + 저장 4분) |

### 배운 것 — `--batch-size`는 GPU 메모리를 바꾸지 않는다

`build_index.py:34`가 `model.encode(batch, ...)`에 `batch_size`를 넘기지 않아
SentenceTransformer 기본값 32가 항상 쓰인다. `--batch-size`는 **바깥쪽 청크 크기만**
바꾼다. 그래서 256→128 조정이 무의미했고 4회 재시도가 전량 낭비였다.

- `nomic-bert-2048`의 `max_seq_length`가 **8192**라, 긴 abstract 32개가 한 배치에
  모이면 MLP activation만 1.52GB가 뜬다. 여유 7.9GB로는 부족했다.
- ⚠ **`asg-common-corpus/docs/autosurvey-usage.md` §4의 "임베딩 OOM → `--batch-size 128`"
  처방은 실제로 듣지 않는다.** 08-31 빌드가 성공한 건 GPU 한 장이 통째로 비어 있어서다.
- **재시도 전에 실패 지점이 같은지부터 확인할 것.** 같으면 경합이 아니라 결정론적
  OOM이므로 재시도는 낭비다.
- 실제 처방은 `model.encode(batch, batch_size=batch_size, ...)` 한 줄 수정.
  임베딩 값은 배치와 무관하므로 검색 품질에 영향이 없다. **미적용**(재현 경로 보존).

### `check_db.py` 검증 — cos 0.999 경고는 무해

| 항목 | 결과 |
|---|---|
| 필수 파일 4종 / TinyDB 스키마 | OK |
| FAISS ↔ id 매핑 | OK — title·abs 각 947,451벡터, 불일치 0 |
| 저장 벡터 재현 | ⚠ 최저 cos **0.987738** (임계 0.999 미달) |
| 검색 스모크 | OK |

12개 위치에서 자기 자신 vs 무관 논문을 대조해 판별했다:

| | title | abs 자기자신 | abs 무관논문 |
|---|---|---|---|
| 최저/최고 | **1.000000** (전 위치) | 0.981057 | 0.657015 |
| 평균 | 1.000000 | 0.991316 | 0.556109 |

**분리 간격 0.324.** 순서가 어긋났다면 자기 자신과의 cos가 무관 논문 수준(0.5~0.6)으로
떨어져야 한다. 매핑은 정상이고 abs 임베딩의 미세한 수치 변동이다. 08-31 빌드(cos 0.9848)와
같은 현상이며, 0.999 임계는 append 확장 시 순서 사고를 잡으려는 것이라
처음부터 새로 빌드한 DB에는 과민하다.

## 5. 미결 — 25편 본배치 전에 풀어야 할 것

### ① 잘린 호출 2건 + 64분 — 원인 미규명

writer 출력 토큰이 **271,846개**로 판 A(70,229)의 **3.9배**다. 최종 문서는 오히려
더 짧은데(12,914 vs 15,206단어) 출력만 4배라, 어느 호출이 **반복 루프에 빠져
출력 한도(128K)까지 생성**한 것으로 보인다. temperature 0의 degenerate repetition으로
추정된다. **64분이 걸린 것도 스로틀(재시도 2회)이 아니라 이 runaway 생성 때문이다.**

최종 산출물은 23개 서브섹션 전수 검사에서 끊김이 없었다 — writer가 초안 → refine → LCE로
여러 번 생성하므로 중간 호출이 잘려도 이후 단계가 온전한 결과를 냈다. 다만 잘린 초안이
refine 입력이 됐으므로 **품질에 미세한 영향은 있을 수 있다.**

**25편 중 다수에서 재현되면 편당 64분 × 25편 = 26시간**이 되어 계획이 크게 달라진다.
본배치 전에 1편을 더 돌려 재현성을 확인할 것.

### ② 예산

| | 값 |
|---|---|
| OpenRouter 키 한도 | $30 (계정 잔액은 별도로 $36.44) |
| 이 편 실행 전 잔여 | $8.01 |
| **실행 후 잔여** | **$7.67** (이 편 $0.34) |
| 남은 24편 예상 | $0.34 × 24 = **$8.28** |

**잔여로는 부족하다.** 충전이 아니라 **키 한도 상향**(예: $40)이나 새 키 발급이 필요하다.
단가가 판 A($0.296) 대비 15% 높은 것도 ①의 runaway 때문이므로, ①이 해소되면 함께 내려간다.

### ③ 다른 3개 agent와 분량 대역 정합

AutoSurvey만 35쪽/refs 166으로 돌리고 다른 agent가 기본 설정으로 짧게 나오면,
agent 간 recall 차이에 분량 효과가 섞인다. SurveyForge·SurveyX·LLM×MapReduce-V2의
산출 분량을 먼저 맞춘 뒤 25편을 일괄로 돌리는 편이 안전하다.

## 6. 사건 기록

- **`run.log` 소실**: PDF 컴파일 후 보조 파일을 `rm -f *.log`로 지울 때 `run.log`도
  같이 지워졌다. `run.json`(삭제 전 생성)에 전 수치가 남아 있었고, 캡처해 둔 원본
  출력으로 `[provider]/[tokens]/[usage]` 줄을 복원해 매니페스트를 재생성했다.
  재생성본은 stages·비용·재시도·잘린 호출·db sha가 원본과 **전 필드 일치**를 확인했다.
  `duration_sec`만 로그 birth time 기준이라 복원 불가여서 원본값(3847)을 옮겼고,
  run.json의 `note` 필드에 그 사실을 남겼다.
  → 보조 파일 정리 시 `*.log` 와일드카드를 쓰지 말 것 (`*.aux *.fls *.fdb_latexmk *.out *.toc` 로 명시).
- **PDF 툴체인**: `pandoc`은 `conda env tex`에만 있고, 그 env의 `pdflatex`는 format 파일이
  깨져 있다(mktexfmt perl @INC 오류). **pandoc은 tex env, latexmk/pdflatex는 `/usr/local/bin`**
  을 써야 한다.
  ```bash
  PATH="/data2/chanjoong/miniforge3/envs/tex/bin:$PATH" \
    /data2/chanjoong/miniforge3/envs/autosurvey/bin/python scripts/md_to_tex.py "<md>"
  /usr/local/bin/latexmk -pdf -interaction=nonstopmode "<tex>"
  ```
