# HANDOFF — AutoSurvey 세팅 인수인계

**최종 갱신**: 2026-08-05
**목표**: 논문(초록 DB)을 토대로 **survey 문서가 실제로 생성되는 것까지**. 논문 수치 재현은 범위 밖.
평가는 **SurveyBench 인용 커버리지만** 씁니다 — LLM-as-Judge 는 하지 않기로 확정(2026-08-05).
**상세 배경**: `SETTING.md` (환경·패치·비용 전반) / `REPRODUCTION.md` (산출물 재현 정보).
이 문서는 "지금 어디까지 됐고 다음에 뭘 하면 되는지"만 다룹니다.

---

## 현재 상태 — 목표 달성

**서베이 8편 생성 완료** — 본편 5편(haiku 3 + v4-pro 1 + v4-flash 1) + 스모크 3편.
파이프라인이 end-to-end로 동작합니다. 아래 표는 본편 4편입니다(스모크 포함 전체 결과는
[`output/README.md`](output/README.md)).

> **2026-08-05**: 새 백본 `deepseek-v4-flash-0731` 로 RAG 스모크 + 본편 A 완료.
> 분량 계수 **1.76×** 측정, `--subsection_num` 은 작동하나 `--section_num` 은
> 1.25배 초과하는 것을 확인했습니다(아래 "분량 통제").

| 서베이 | 모델 | 섹션/서브섹션 | 단어 | 참고문헌 | 인용 | 비용 |
|---|---|---|---|---|---|---|
| In-context Learning | haiku | 9 / 51 | 32,176 | 383 | 465 | $0.78 |
| Large Multi-Modal Language Models | haiku | 8 / 48 | 30,709 | 378 | 467 | $0.75 |
| Evaluation of LLMs | haiku | 8 / 48 | 30,439 | 368 | 425 | $0.75 |
| In-context Learning | deepseek-v4-pro | 14 / 117 | 92,707 | 644 | 884 | $3.39 |
| **RAG for LLMs** | **v4-flash-0731** | **10 / 39** | **49,002** | **476** | **674** | **$0.38** |

전부 `scripts/check_survey.py` 통과 (댕글링 인용 0 / json 매핑 일치 / 포맷 누출 0).
haiku는 편당 6~8분, 3편 합계 약 $2.28.

> deepseek 편의 `rag_num`은 예산 제약으로 30(haiku는 60)이라 모델만 다른 통제 비교가
> 아닙니다. 또 섹션 수 14/117은 `.md`의 헤딩을 그대로 센 값이고, 중복 제목과 헤딩
> 레벨 오류를 바로잡은 실제 구조는 10섹션 / 72서브섹션 / 5서브서브섹션입니다.

**산출물은 모델별 디렉터리로 나뉘어 있습니다** — `output/haiku/`, `output/deepseek-v4-pro/`,
`output/haiku-smoke/`, `output/deepseek-smoke/`. 토픽당 `.md` / `.json` / `.tex` 3개.

**각 출력의 정확한 실행 조건 — 모델·하이퍼파라미터·환경·DB 지문·명령 — 은
[`REPRODUCTION.md`](REPRODUCTION.md)에 있습니다.** 결과 수치와 비교 시 주의점은
[`output/README.md`](output/README.md). 새 서베이를 만들면 두 표에 각각 한 줄 추가해 주세요.

**다음 토픽 — `Retrieval-Augmented Generation for Large Language Models` 권장**
(2026-08-05, 26개 후보를 `compare_snapshots.py` 로 재고 정했습니다).

LLM judge 를 안 쓰기로 한 이상 정량 수치가 나오는 길은 SurveyBench `ref_bench` 뿐이고,
그건 **10개 토픽에만** 있습니다. 그 밖의 토픽을 고르면 나오는 건 무결성 검사뿐입니다.
`ref_bench` 가 있는 토픽 중 미생성분을 커버리지 순으로 두면:

| 토픽 | d@1200 (배포본 → 최신화본) | 최신 비율 | 비고 |
|---|---|---|---|
| **RAG for Large Language Models** | 0.724 → **0.621** | 86.8% | SurveyForge 0.435 / 인간 0.542 와 직접 비교 |
| Hallucination in LLMs | 0.747 → **0.637** | 83.6% | 벤치 최신이 2024-01 로 이른 편 |
| Generative Diffusion Models | 0.737 → 0.678 | 61.1% | 비LLM |
| 3D Gaussian Splatting | **0.995 → 0.689** | 91.0% | 최신화 효과 최대. 비LLM |

**토픽 문자열은 `topics.txt` 와 글자 단위로 같아야 합니다.** `"Retrieval-Augmented
Generation"` 만 쓰면 d@1200 이 0.692 로 나빠지고(IR 쪽과 섞임), 무엇보다 채점기가
그 토픽을 못 찾습니다.

`ref_bench` 없이 커버리지만 보면 `Reasoning in Large Language Models`(0.643 → **0.574**,
감쇠 0.132)가 26개 중 최고입니다. 정량 평가를 포기할 때만 고려하세요.

**남은 일** (자세히는 아래 "남은 작업"):

| # | 항목 | 막는 것 |
|---|---|---|
| **C** | **새 백본(`deepseek-v4-flash-0731`)으로 첫 실행** — 스모크·계수 측정 완료. 본편 진행 중 | 없음 |
| A | PDF 컴파일 확인(`.tex`까지는 나와 있음) + `.bib` 생성 | 없음 — 로컬/Overleaf에서 가능 |
| B | 평가 — SurveyBench 인용 커버리지 (**LLM judge는 안 함**) | 없음 — `scripts/to_surveybench_ref.py` 로 지금 가능 (크레딧 불필요) |

**크레딧은 해소됐습니다** — 키 한도가 $10 → **$30**으로 상향됐습니다(2026-08-05).
확인은 `/api/v1/key`로 하세요(`/api/v1/credits`는 계정 잔액이라 키 한도가 안 보입니다).

---

## DB 최신화 — 2026-08-04 완료

DB에 2024-04-26 이후 논문이 없어 27개월치를 채웠습니다. **스냅샷이 이제 둘입니다.**

| 스냅샷 | 경로 | 논문 수 | 수록 범위 |
|---|---|---|---|
| 배포본 | `./database` | 537,665 | ~2024-04-26 |
| **최신화본** | `./database_2026-08` | **909,293** | **~2026-08-03** (배포본 **전부 포함**) |

**`database_2026-08`은 "2026-08의 논문"이 아니라 "2026-08 시점의 스냅샷"입니다.**
배포본 537,665편을 그대로 담고 그 위에 2024-04-27 이후 371,628편을 얹은 **상위 집합**이라,
둘은 대체 관계지 분할이 아닙니다. 배포본은 **읽기만 했고 그대로**이고,
`IndexFlatL2` append가 기존 행 번호를 보존하므로 **배포본은 최신화본의 prefix**입니다
(인덱스 0~537,664 동일).

**어느 쪽을 쓸지는 `--db_path`로 고릅니다.**

- `output/`의 서베이 6편은 전부 **배포본**으로 만들었습니다. 재현하려면 배포본.
- 최신 논문이 필요하면 **최신화본**. 단 아래 주의를 보세요.

> ⚠ **최신화본으로 만든 서베이는 기존 6편과 통제 비교가 되지 않습니다.**
> 같은 토픽의 top-1200 교집합이 **16~35%뿐**입니다. 비교는 같은 스냅샷끼리 하세요.

**커버리지는 세 토픽 모두 개선됐습니다** (`d@1200`이 낮을수록 좋음):

| 토픽 | d@1200 (배포본 → 최신화본) | 2024-04 이후 비율 |
|---|---|---|
| In-context Learning | 0.853 → **0.796** | 64.4% |
| Evaluation of LLMs | 0.849 → **0.764** | 82.8% |
| Large Multi-Modal Language Models | 0.744 → **0.691** | 74.2% |

지문·구성·검증 결과는 [`REPRODUCTION.md`](REPRODUCTION.md) §3-B,
설계 근거와 실측 소요는 [`README.md`](README.md) §3. 실행 로그는
`database_2026-08/logs/`(`chain.log` / `harvest.log`)에 보존돼 있습니다.

**검증 통과** — 레코드/title FAISS/abs FAISS/id매핑 모두 909,293으로 일치,
저장 벡터 재현 20개 위치 × 2필드에서 최저 cos 1.000000, 검색 스모크 정상.

---

## 분량 통제 — `--subsection_num` (2026-08-05 추가)

같은 `--subsection_len 700`인데 모델에 따라 분량이 **3배** 벌어졌습니다
(haiku 서브섹션당 531~537단어 = 지시값의 0.77×, deepseek-v4-pro 1,167단어 = 1.67×).
`subsection_len`이 상한이 아니라 **하한**이기 때문입니다
(`"content more than [WORD NUM] words"`). 진단과 근거는 [`README.md`](README.md) §4.

```
총 분량 = section_num × subsection_num × (subsection_len × 모델 계수)
```

- **`--subsection_num N`** (신규) — 섹션당 서브섹션 상한.
  **기본값 0이면 원본 AutoSurvey 그대로**입니다(프롬프트 문구가 원본과 글자 단위로 동일).
- **`--subsection_len`** — **모델 계수로 역산**해 넣습니다.
  `max_tokens` 하드 컷은 쓰지 마세요. 생성 도중 잘려 인용이 깨집니다.

**새 백본은 계수부터 재세요.** 모델마다 2.2배까지 차이 납니다. 스모크 1편 뒤:

```bash
python scripts/check_survey.py "output/<모델>-smoke/<토픽>.md" \
  --subsection-len=700 --target-words=20000
```

계수와 다음 실행에 넣을 `--subsection_len` 값을 계산해 줍니다.
`deepseek-v4-flash-0731` **실측 = 1.76×** (2026-08-05, 두 실행에서 1.73 / 1.79).

**통제되지 않는 자유도가 둘인데 패치가 잡은 건 하나입니다.**

- `--subsection_num` ✅ 지켜집니다 (10개 섹션 전부 4개 이하)
- `--section_num` ❌ **7~12 로 흔들림.** 초과도 미달도 함 (8→10, 8→11, 8→12, 8→**7**)

그래서 `--subsection_num 4`를 걸었는데도 총 서브섹션이 37→39로 늘었습니다. 예측식에
섹션 초과를 넣어야 맞습니다:

```
총 분량 = section_num × (0.9~1.5) × subsection_num × (subsection_len × 1.8)
```

검산: `8 × 1.25 × 3.9 × (700 × 1.76)` = 48,000 ≈ 실측 **49,002**.
25,000단어대를 노린다면 `--section_num 6 --subsection_num 3` (≈27,700) 입니다.

### 분량 구간 — 하드 컷을 걸지 않습니다

주제가 넓으면 서베이는 정당하게 길어집니다. 목표치를 강제하는 대신 **구간을 두고
벗어나면 경고**만 띄웁니다(`scripts/check_survey.py --length`). 판단은 사람이 합니다.

실측 근거:

| 자료 | 단어 | 참고문헌 |
|---|---|---|
| AutoSurvey 원저자 예시 3편 (`examples/`) | 8,558~13,894 | **74~88** |
| SurveyForge 저자 산출물 29편 | 13,242~32,938 (20~39페이지) | — |
| 인간 작성 서베이 10편 (SurveyBench) | — | **173~345** |

저자 산출물 기준 **약 800단어/페이지**입니다.

| 구간 | 단어 | 페이지 | 판정 |
|---|---|---|---|
| 짧음 | < 12,000 | < 15p | 경고 |
| **표준** | 12,000~25,000 | 15~31p | ok |
| **광범위** | 25,000~50,000 | 31~62p | ok — 주제가 넓으면 정당 |
| 초과 | 50,000~80,000 | 62~100p | 경고 |
| **비대** | > 80,000 | > 100p | **경고 — 서베이가 아니다** |

**참고문헌 수는 분량과 독립된 신호입니다.** 인간 서베이가 173~345편인데 우리 haiku는
368~383편으로 이미 상한을 넘었고 deepseek-v4-pro는 644편입니다(원저자 예시는 74~88편).
644편을 인용한 문서는 읽은 게 아니라 나열한 것입니다. **refs 400 초과면 경고.**

현 산출물: haiku 3편 25.5k~27.4k(광범위, ok) / deepseek-v4-pro **84,012단어 ≈ 105페이지
(비대, 경고)**. 출발점으로는 8섹션 × 4서브섹션 = 32서브섹션, 서브섹션당 약 600단어
(≈19,000단어)를 권합니다. 그 안에서 주제에 따라 흔들리는 건 정상입니다.

---

## git 상태

`reproduce` 브랜치. **push와 PR 생성은 사용자가 직접 합니다.**
origin은 SSH URL(`git@github.com:brian-223134/AutoSurvey.git`)로 전환돼 있습니다.
(서버 SSH 키에 passphrase가 있어 TTY 없는 도구에서는 push가 불가합니다.)

커밋: 서베이 1편당 1커밋 + 인프라/변환 커밋.

---

## 재실행 방법

DB와 `.env`는 준비돼 있습니다. 새 토픽 생성은 이 한 줄입니다.
아래는 **확정된 다음 백본**(`deepseek-v4-flash-0731`)과 **최신화본 DB** 기준입니다.

> `.env`가 없다면(git에 없으므로 새 클론에는 없습니다):
> `cp .env.example .env && chmod 600 .env` 후 `OPENROUTER_API_KEY`만 채우세요.
> 나머지 값은 실제로 쓰고 있는 설정 그대로입니다.

```bash
conda activate autosurvey
source .env
python main.py \
  --topic "Explainability for LLMs" \
  --saving_path ./output/deepseek-v4-flash/ --db_path ./database_2026-08 \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model deepseek/deepseek-v4-flash-0731 \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200

python scripts/check_survey.py "output/deepseek-v4-flash/Explainability for LLMs.md" --length
```

**`--db_path`는 스냅샷 선택입니다 — 기본값에 맡기지 마세요.** 인자를 빼면
`./database`(배포본)로 조용히 떨어집니다.

| 목적 | 경로 |
|---|---|
| 새 실험 | `./database_2026-08` — 909,293편 = **배포본 전부 + 신규 371,628편** |
| 기존 6편(`output/`)과 검색 조건을 맞춘 비교 | `./database` — 537,665편, ~2024-04-26 |

최신화본이 배포본의 **상위 집합**이라 둘을 함께 주는 경우는 없습니다. 하나만 고르세요.

**`--model`을 바꾸면 `.env`의 `AUTOSURVEY_PROVIDER`도 같이 바꾸거나 비우세요.**
`parasail/fp8`은 flash 전용 tag라, 그대로 둔 채 `--model anthropic/claude-3-haiku`로
돌리면(haiku는 `amazon-bedrock` 하나뿐) 전 요청이 실패합니다. `main.py`가 DB 로딩 전에
잡아 중단시킵니다.

`--saving_path`는 **모델별 디렉터리**로 주세요. 다른 모델을 쓰면 새 디렉터리를 만들고,
끝나면 `output/README.md` 표에 실행 조건을 한 줄 추가합니다.

축소 스모크가 필요하면 `--section_num 4 --outline_reference_num 200 --rag_num 15`
(flash 기준 약 **$0.06**, haiku는 $0.15). 결과는 `--saving_path ./output/<모델>-smoke/` 로
분리하세요. **새 백본의 첫 실행은 반드시 스모크입니다** — 분량 계수가 아직 미측정이라
`--subsection_len`을 얼마로 둘지 이 실행으로 정합니다.

생성 후에는 `.tex` 변환을 돌립니다:
```bash
PATH="$HOME/miniforge3/envs/tex/bin:$PATH" \
  python scripts/md_to_tex.py "output/haiku/Explainability for LLMs.md"
```
`scripts/enrich_references.py`(서지정보 채우기)는 **새 실행에는 필요 없습니다** —
`main.py`가 저장 시점에 `reference_detail`을 만듭니다. 옛 산출물을 손볼 때만 씁니다.

### 실행 설정 — provider 고정과 잘림 검사

OpenRouter는 같은 모델을 여러 provider로 라우팅하는데 **quantization이 제각각입니다.**
`deepseek-v4-flash-0731`은 엔드포인트 19개에 fp4 / fp8 / unknown이 섞여 있습니다.
고정하지 않으면 **한 서베이 안에서 서브섹션마다 다른 정밀도의 모델이 씁니다.**

```bash
# .env 에 추가
export AUTOSURVEY_PROVIDER=parasail/fp8
```

값은 OpenRouter의 **endpoint tag**입니다(provider와 quantization을 한 번에 고정).
`allow_fallbacks=false`가 함께 나가므로 그 provider가 붐벼도 다른 곳으로 넘어가지 않습니다.
확인:

```bash
curl -s "https://openrouter.ai/api/v1/models/deepseek/deepseek-v4-flash-0731/endpoints" \
  | python -c "import json,sys; [print(e['tag'], e['quantization'], e['max_completion_tokens']) for e in json.load(sys.stdin)['data']['endpoints']]"
```

`parasail/fp8`을 고른 이유 — fp8(deepseek 계열의 네이티브 정밀도에 가까움),
uptime 100%, `max_completion_tokens` 1,048,576으로 최대, 단가는 fp8 주류와 동일.

> **모델 단위로 표시되는 $0.09/$0.18은 fp4 엔드포인트(DeepInfra) 가격입니다.**
> fp8로 고정하면 실제 단가는 $0.14/$0.28입니다.

### 출력 잘림 검사

`max_tokens` 한도 자체는 문제가 아닙니다 — 호출당 서브섹션 하나(약 1,600토큰)이고
최소 provider 한도가 32,768이라 20배 여유입니다. 다만 **잘려도 조용히 넘어가던 것**을
막았습니다. `finish_reason='length'`면 경고를 찍고 실행 끝에 건수를 집계합니다.

```
[usage]  writer  ⚠ 출력 잘림 3건 — 해당 서브섹션은 문장 중간에서 끊겼습니다
```

이 경고가 뜨면 그 서베이는 문장이 끊긴 채 저장된 것입니다. `check_survey.py`는
인용만 보지 완결성은 보지 않으므로 여기서만 잡힙니다.

시스템 간 비교를 위한 **통제 요인 전체**(백본·reasoning·provider 핀·목표 구조·분량·
검색 폭·DB 스냅샷)는 상위 디렉터리의 `SURVEY_REPORT.md` §7에 정리돼 있습니다.
GLM-4.6은 후보에서 내렸습니다.

**코드 수정은 불필요합니다** — OpenRouter가 OpenAI 호환이라 `--model` 값만 바꾸면 됩니다.
교체 시 확인할 것:

1. **reasoning(thinking) 모드** — 켜져 있으면 출력 토큰이 몇 배가 되어 비용·시간이 늘고,
   최악의 경우 thinking 내용이 본문에 섞입니다. `.env`의 `AUTOSURVEY_REASONING=off`로
   끄세요. 이 토글이 생기기 전에 켠 채로 돌린 `deepseek-smoke/`는 추론 토큰이 출력의 45%,
   비용이 토큰 추정의 3.5배였습니다.
2. **출력 포맷 준수** — 아웃라인 파서는 `8bfbc43`에서 정규식 기반으로 바꿔 모델
   비의존적입니다(deepseek 첫 시도가 `IndexError`로 죽어서 고쳤습니다).
   그래도 새 모델은 스모크부터 돌리세요.
3. 논문 Table 4가 writer를 GPT-4 / Gemini-1.5-Pro로 바꾼 ablation을 이미 다루므로,
   writer 교체 자체는 방법론을 벗어나지 않습니다 (세 모델 모두 4.58~4.70).

**예산은 확보됐습니다** — 키 한도가 $10 → **$30**으로 상향됐습니다(2026-08-05).

---

### 크레딧 — 한도 $30

```bash
source .env && curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/key        # 이 키의 한도/사용량
```

2026-08-05 실측: **한도 $30 / 사용 $10.035 / 잔여 $19.96**.
($10 한도를 전액 소진한 뒤 총무를 통해 상향받았습니다.)

**편당 실측 비용** — `deepseek-v4-flash-0731` @ `parasail/fp8`:

| | 비용 |
|---|---|
| 스모크 (4섹션 / oref 200 / rag 15, 44,803단어) | **$0.166** |
| 본편 (8섹션 / `--subsection_num 4` / rag 60 / oref 1200) | 약 $0.3 |
| SurveyBench 채점 | **$0** (LLM 호출 없음) |

비용의 90% 이상이 **입력**입니다(서브섹션당 검색 초록 60편). 분량을 줄여도 비용은
거의 안 줄고, 줄이려면 `--rag_num`·`--outline_reference_num`을 건드려야 합니다.

> **`/api/v1/credits`를 보지 마세요.** 그 엔드포인트는 **계정 전체** 잔액을 돌려주는데
> (2026-08-04 기준 잔여 $149.55) 이 키에 걸린 $10 상한은 보여주지 않습니다.
> 계정 잔액만 보고 "여유 있다"고 판단하면 실행이 402로 죽습니다. 키 한도는
> 위의 `/api/v1/key`로 확인하세요.

계정은 공용이므로 상향·발급 전에 확인이 필요합니다.

> **`--api_key`를 일부러 넘기지 않습니다.** 이 서버는 `/proc`에 hidepid가 없어
> 다른 사용자가 `ps -eo args`로 명령줄을 볼 수 있습니다. `main.py`/`evaluation.py`가
> `--api_key` → `OPENROUTER_API_KEY` → `AUTOSURVEY_API_KEY` 순으로 키를 찾고,
> 키가 없으면 **DB 로딩(수 분) 전에 즉시 중단**됩니다.
> `.env`는 `.gitignore`에 등록돼 있고 권한은 `600`입니다.

---

## 확정된 결정사항

| 항목 | 결정 | 이유 |
|---|---|---|
| LLM 백엔드 | **OpenRouter** (`https://openrouter.ai/api/v1/chat/completions`) | 논문도 상용 API(Claude-3-Haiku)로 생성. OpenAI 호환이라 **코드 수정 불필요** |
| 로컬 vLLM | **안 씀** | GPU 8장이 놀고 있어도 제안하지 말 것 — 사용자가 명시적으로 배제 |
| DB | **공식 배포본을 수동 scp 반입** | 서버에서 OneDrive 차단. 로컬 PC에서는 받을 수 있음 |
| 임베딩 | `nomic-ai/nomic-embed-text-v1` (기본값 유지) | 공식 DB가 이 벡터 공간. **바꾸면 인덱스 전체가 무효** |
| GPU 사용 | **1장만.** 번호는 고정하지 말고 `nvidia-smi`로 **빈 것을 골라** `CUDA_VISIBLE_DEVICES`에 | 임베딩 외엔 GPU를 안 씀. 공용 서버라 나머지는 안 건드림. 0번이 남의 작업으로 차 있을 때가 있다(2026-08-04 확인) |
| 평가 — LLM judge | **하지 않는다** (2026-08-05) | `evaluation.py`/`judge.py` 경로를 쓰지 않음. 그 안의 버그 2건도 고칠 필요 없음 |
| 평가 — 대체 경로 | **SurveyBench 인용 커버리지** | arXiv id 집합 교집합이라 **LLM 호출 0회 = 크레딧 불필요**. 단 `ref_bench`가 있는 10개 토픽에서만 가능 |
| 다음 백본 | **`deepseek/deepseek-v4-flash-0731`** | v4-pro의 1/3.1 단가, 1M 컨텍스트, 날짜 고정 태그 |
| provider | **`parasail/fp8` 고정** (`.env`) | 고정 안 하면 서브섹션마다 다른 quantization. fp8 / uptime 100% / max_out 최대 |
| 프롬프트 | **문구를 바꾸지 않는다.** 파라미터만 추가 | 다시 쓰면 원본 AutoSurvey와 다른 시스템이 되어 baseline 의미가 흐려짐 |
| 분량 | **하드 컷 없음.** 구간을 벗어나면 경고만 | 주제가 넓으면 정당하게 길어진다. 판단은 사람이 |

---

## 완료된 작업

### 1. 환경 — conda `autosurvey`

```bash
conda activate autosurvey       # ~/miniforge3/envs/autosurvey, Python 3.10
```

실측 검증: `torch 2.4.1+cu121 / cuda True / 8 GPU`, `faiss 1.8.0`, `transformers 4.44.2`, `sentence-transformers 2.7.0`, `numpy 1.26.4`
`nomic-embed-text-v1`도 다운로드 + GPU 로딩 확인 (768-dim). **로컬 설치가 필요한 모델은 이것뿐.**

> ⚠️ `python3.10 -m venv`는 이 서버에서 실패합니다 (ensurepip 없음, sudo 불가). conda를 쓰세요.
> ⚠️ `transformers`를 4.45 이상으로 올리지 마세요. nomic의 `trust_remote_code` 로딩이 깨집니다.

### 2. 코드 패치 — 원본은 그대로 실행 불가였음

| 파일 | 내용 |
|---|---|
| `src/utils.py` | 죽은 `langchain.document_loaders` import 제거 (**ImportError로 즉사하던 원인**) + 미사용 `load_pdf()` 삭제 |
| `src/database.py` | `torch.device('cuda')` 하드코딩 → `AUTOSURVEY_DEVICE` 기반 `_resolve_device()` |
| `src/database.py` | TinyDB `one_of()` 선형 스캔 → `self._by_id` dict 조회 (**53만 편에서 호출당 수 분 → O(1)**) |
| `src/model.py` | `temperature`를 messages 안 → 최상위 (원래 **실제로 적용되지 않았음**) |
| `src/model.py` | `except: pass` 은폐 → HTTP 상태/본문 노출 + 지수 백오프 + `timeout=300` |
| `src/model.py` | OpenRouter가 200에 `{"error":...}`를 실어보내는 경우 처리 |
| `src/model.py` | `max_threads`를 `AUTOSURVEY_MAX_THREADS` 환경변수로 |
| `src/agents/writer.py` | **`[[]] * n` aliasing 버그** — 아래 별도 설명 |
| `main.py` | `'a+'` → `'w'`, API 실패 시 즉시 `RuntimeError`, 토큰 사용량 출력 |
| `src/prompt.py`+`outline_writer.py` | 치환되지 않던 `[TOPIC]` |

**aliasing 버그 (가장 중요)** — `writer.py`의 `[[]] * n`은 빈 리스트 n개가 아니라 **같은 객체 참조 n개**입니다. 바로 아래에서 `.append()`로 쌓기 때문에 **섹션 0을 제외한 모든 섹션이 섹션 0의 참고문헌으로 본문을 씁니다.** 크래시가 없어서 조용히 품질만 망가집니다. `[[] for _ in range(n)]`로 교체했습니다.

### 3. 스크립트 9종 (`scripts/`)

**DB 준비·갱신용 5종**

- `check_db.py` — DB 검증. 파일 4개 존재 / TinyDB 스키마 / FAISS·매핑 크기 정합 / 실제 검색.
  `--verify-embeddings N`을 주면 **저장된 벡터를 실제로 다시 만들어 대조**합니다.
  크기가 맞는다고 벡터가 맞는 건 아니라서, append로 늘린 스냅샷에는 반드시 켜세요.
- `harvest_arxiv.py` — arXiv OAI-PMH 수집. **DB 최신화의 주력 도구**이자 OneDrive
  반입 실패 시의 폴백. 배포 DB의 표기 규약을 그대로 재현합니다(아래 `check_oai_schema.py`).
  `arXivRaw`·`arXiv` 두 형식을 훑어 조인하고, `--exclude-db`로 기존 논문을 제외합니다.
  페이지당 1300건, 503/Retry-After 처리, `state.json`으로 중단 후 재개.
- `check_oai_schema.py` — **수집기가 만든 레코드가 배포 DB와 같은 표기인지** 검사.
  기존 DB에 있는 논문을 OAI로 다시 받아 7필드를 문자 단위로 대조합니다.
  표기가 어긋나면 에러 없이 코퍼스가 두 층으로 갈라지므로 수집 전에 돌리세요.
- `append_snapshot.py` — 기존 스냅샷을 **읽기만 하고** 신규 논문을 더한 새 스냅샷을
  만듭니다. 레코드 순서 == FAISS 행 == id 매핑을 시작 전과 기록 직전에 두 번 확인하고,
  어긋나면 아무것도 쓰지 않습니다.
- `build_index.py` — 처음부터 인덱스를 만들 때. `build_database.ipynb` 대체
  (노트북은 `index_gpu_to_cpu` 에러 + 출력 파일명 불일치로 그대로 안 돎).

**산출물 처리용 3종** — 생성 후에 씁니다.

- `check_survey.py` — 생성된 `.md`/`.json` 무결성. 댕글링 인용 / json 매핑 일치 / 포맷 누출.
- `enrich_references.py` — `.json`에 arXiv 제목·날짜·링크를 채웁니다(`reference_detail`).
- `md_to_tex.py` — `.md` → Overleaf용 `.tex`.

**분석용 1종**

- `compare_snapshots.py` — 두 스냅샷에서 같은 토픽을 검색해 `d@1` / `d@K` / 감쇠 /
  최신 논문 비율 / top-K 교집합을 비교합니다. 스냅샷을 둘로 유지하는 이유가 이 측정입니다.

### 4. 기타

- `.gitignore` 신규 — 원본에 커밋돼 있던 `.pyc` 15개 추적 해제
- `requirements-server.txt` 신규 (원본 `requirements.txt`는 `faiss_gpu`/`torch 2.1.0`/langchain 때문에 이 서버에서 설치 불가)
- `SETTING.md` 갱신 — 초판의 "L40 48GB × 2"는 오기, 실측은 **L40S 46GB × 8**

### 5. DB 반입 및 검증

OneDrive zip을 scp로 반입해 `./database/`에 풀었고 `check_db.py` **통과**:

| 항목 | 결과 |
|---|---|
| 논문 수 | **537,665편** |
| FAISS | title/abs 각 537,665벡터, dim 768 |
| id 매핑 | 537,665개, TinyDB와 **100% 일치** (유실 0건) |
| 검색 스모크 | `"large language models"` → 관련 논문 5건 정상 |

arXiv id에 버전 접미사가 붙어 있고(`1811.06122v1`) **수록 논문의 최신 날짜는
`2024-04-26`** 입니다 (배포 파일 mtime 2024-05-27과 다릅니다 — 후자는 파일이 만들어진
날짜입니다).

필드는 `id` / `title` / `abs` / `date` / `cat` / `url` / `authors` 7개이고
`authors`는 전편에 채워져 있습니다.

> 예전에 여기 "`harvest_arxiv.py`는 버전 없는 id를 쓰므로 두 DB를 섞지 마세요"라고
> 적혀 있었는데 **더 이상 맞지 않습니다.** 2026-08-04에 수집기를 배포 DB의 표기 규약에
> 맞춰 다시 썼습니다(버전 접미사 포함). 규약 전체와 역산 근거는 `README.md` §3.4와
> `scripts/check_oai_schema.py` 상단에 있습니다.

### 6. 토픽 선정과 생성

토픽은 **DB에서 직접 커버리지를 측정해** 골랐습니다 (top-1200 검색 후 거리 분포 비교).
`d@1200`이 낮을수록 1200번째까지 관련성이 유지된다는 뜻이고, 감쇠(`d@1200 − d@1`)가
작을수록 관련 논문층이 두텁습니다.

| 토픽 | d@1200 | 감쇠 | 2023+ | 선정 이유 |
|---|---|---|---|---|
| **In-context Learning** | 0.853 | 0.382 | 48% | `examples/In-context Learning.md`에 **저자들의 생성 결과**가 있어 직접 대조 가능. 논문 Table 6 중 인간 서베이 인용수 최고(323) |
| **Large Multi-Modal Language Models** | **0.744** | **0.238** | 88% | 측정한 24개 중 커버리지 1위 |
| **Evaluation of LLMs** | 0.849 | 0.254 | 96% | 안정적 커버리지 + 최신성 최고. 인간 서베이 183 인용 |

스모크 → 본 실행 순으로 돌렸습니다. 본편은 논문 설정
(`--section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200`)을 썼고,
deepseek 편만 예산 때문에 `--rag_num 30`입니다.

새 토픽을 고를 때 참고:

- In-context Learning은 감쇠가 커서 `--outline_reference_num`을 800으로 낮추는 안을
  검토했지만, 논문 설정과의 비교를 위해 1200으로 돌렸습니다
- 피할 토픽: Parameter-Efficient Fine-Tuning(0.958), Chain of Thought(0.942),
  Hallucination in LLMs(0.940), LLMs for Recommendation(0.946).
  d@1은 괜찮지만 1200편을 채우면 뒤쪽이 노이즈입니다
- DB에 **2024-04-26 이후 논문이 없어** 그 뒤에 부상한 주제는 검색이 되지 않습니다
  (해소 방안은 `README.md` §3)

### 7. 후처리 — 서지정보와 `.tex` 변환

`main.py`가 만드는 것은 `.md` / `.json` 2개뿐이고, `.tex`는 뒤에 붙인 단계입니다.

- `enrich_references.py`가 `.json`에 arXiv 제목·날짜·링크를 `reference_detail`로 채웁니다.
  기존 6편은 이 스크립트로 뒤늦게 채웠지만 **`main.py`가 이제 저장 시점에 같은 필드를
  만듭니다**(`build_reference_detail`). 새 실행은 이 단계를 건너뛰어도 됩니다.
- `reference` 필드는 건드리지 않습니다 — `judge.py`의 `citation_quality()`가 그 구조에
  의존하므로 바꾸면 `evaluation.py`가 깨집니다.
- `md_to_tex.py`는 제목 중복 제거, 헤딩 레벨 교정, `\cite` 변환, pdflatex 미지원
  유니코드 치환을 거칩니다.
- **서버에서 LaTeX 컴파일은 불가능합니다.** 시스템 MiKTeX는 `pdflatex.fmt` 빌드에 실패하고
  (admin 권한 필요), conda `tex` env의 `texlive-core`도 매크로 트리(`latex.ltx`)가 없습니다.
  같은 env의 pandoc 3.10.1은 정상이라 **변환까지만** 서버에서 합니다.

---

## 남은 작업

### A. LaTeX·PDF 확인 — 사용자 로컬에서

`.tex`까지는 6편 전부 나와 있습니다. Overleaf 업로드 절차와 deepseek 편
(92,707단어 / 참고문헌 644개)의 컴파일 타임아웃 대응은 [`output/README.md`](output/README.md).

남은 간극은 **`.bib`이 없다는 것** 하나입니다. `.tex`의 `\cite{}`가 가리키는 서지 항목이
제목 기반입니다.

> ⚠ 예전에 이 자리에 "DB에 저자 필드가 없어 arXiv OAI-PMH `GetRecord`로 저자를 따로
> 받아야 한다"고 적혀 있었는데 **오기였습니다.** `authors`가 537,665편 전부에 채워져
> 있습니다(결측 0.000%). 외부 조회가 전혀 필요 없습니다.

그래서 `.bib` 작업은 다음 두 단계로 줄어듭니다:

1. `reference_detail`에 `authors` 추가 — 지금은 `id`/`title`/`date`/`url` 4개뿐입니다.
   `main.py`의 `build_reference_detail()`과 `scripts/enrich_references.py` **두 곳** 모두
   같은 필드 집합을 만들므로 양쪽을 고칩니다. `get_paper_info_from_ids()`가 레코드
   전체를 돌려주므로 각각 한 줄입니다. 기존 6편은 enrich 스크립트로 재적용.
2. `reference_detail`(id·제목·날짜·링크·저자)에서 `.bib`을 찍어내고 `md_to_tex.py`가
   그 키를 쓰도록 연결.

### B. 평가 — LLM judge 는 하지 않습니다 (2026-08-05 확정)

**`evaluation.py` / `judge.py` 경로는 쓰지 않기로 했습니다.** 아래 두 버그는 그래서
고칠 필요가 없어졌습니다. 마음이 바뀌면 이것부터 보라는 뜻으로만 남깁니다.

1. `judge.py:202,216`의 무제한 스레드 생성 — 인용 문장 하나당 스레드 하나.
2. `src/utils.py::compute_price()`가 `KeyError`로 즉사 — `self.model_price = {}`가
   비어 있는데 `self.model_price[model][0]`을 조회합니다. `judge.py:46`이 호출하므로
   어떤 모델을 쓰든 터집니다. `main.py`는 이 경로를 타지 않아 드러나지 않았습니다.

**대신 SurveyBench 인용 커버리지를 씁니다. LLM 호출이 0회라 크레딧이 필요 없습니다.**

`../SurveyForge/SurveyBench/`에 10개 토픽의 정답 참고문헌(`ref_bench/`), 인간 작성
서베이(`human_written_ref/`), SurveyForge 산출물(`generated_surveys_ref/`)이 있습니다.
채점은 arXiv id 집합의 교집합입니다:

```
coverage = |생성 참고문헌 ∩ ref_bench| / |날짜 필터를 통과한 생성 참고문헌|
```

```bash
python scripts/to_surveybench_ref.py "output/<모델>/<토픽>.json" \
  --topic "Retrieval-Augmented Generation for Large Language Models"
```

변환·채점·진단을 한 번에 합니다. 채점은 SurveyBench의 `test.py::compute_citation_coverage`를
**그대로 import 해서** 씁니다 — 같은 식을 다시 구현하면 그쪽이 바뀔 때 조용히 어긋나고
SurveyForge와의 비교가 무의미해집니다. 공식 러너로 직접 돌려도 같은 값이 나옵니다:

```bash
cd ../SurveyForge/SurveyBench && python test.py \
  --generated_surveys_ref_dir ../../AutoSurvey/output/surveybench_ref \
  --topic_list_path <우리 토픽만 적은 파일>
```

> **`--topic`은 벤치마크 문자열과 글자 단위로 같아야 합니다.** 다르면 스크립트가 10개
> 목록을 보여주며 중단합니다. 검색 쿼리부터 달라져 비교가 성립하지 않기 때문입니다 —
> 아래 0.054가 정확히 그 경우입니다.

**채점 완료 (2026-08-18)** — RAG 토픽, 벤치마크 정답 608편. 배포본 DB.

| 산출물 | 인용 | 적중 | coverage(정밀도) | 재현율 |
|---|---|---|---|---|
| 인간 작성 | 191 | 103 | **0.539** | **0.169** |
| SurveyForge (저자) | 85 | 37 | 0.435 | 0.061 |
| **우리 본편 A** (`rag 60`) | **476** | **48** | **0.101** | **0.079** |
| 우리 스모크 (`rag 15`) | 268 | 22 | 0.082 | 0.036 |

> **지표는 정밀도입니다 — 분모가 "우리가 인용한 편수"입니다.** 많이 인용하면 기계적으로
> 내려갑니다. **재현율로 보면 우리가 SurveyForge보다 높습니다**(48편 대 37편 적중).
> 문제는 못 찾은 게 아니라 476편을 인용해 **428편이 군더더기**라는 것입니다.
> 재현율은 벤치마크 공식 지표가 아니라 지표 성질을 드러내려고 따로 계산한 값입니다.

**군더더기는 무작위가 아닙니다.** 476편 중 제목에 검색/RAG 관련어가 있는 건 **28%**
(134편)이고, 벗어난 것들이 **hallucination 에 몰려 있습니다**(SurveyBench 의 별도 토픽).
임베딩 검색이 인접 주제로 샜습니다. **coverage 0.101 의 실질 원인입니다.**

**`rag_num` 을 15 → 60 으로 올린 효과**: 재현율 0.036 → 0.079(2.2배), 정밀도 0.082 →
0.101(1.2배). 검색을 늘리면 정답을 더 찾긴 하는데 군더더기가 같이 늘어 정밀도는 제자리다.
**다음 실험은 "찾은 뒤 걸러내기"** — 검색량은 두고 인용 수를 줄인다.

| 참고 (다른 토픽) | 인용 | coverage |
|---|---|---|
| SurveyForge (저자), Evaluation of LLMs | 116 | 0.336 |
| 우리 haiku, Evaluation of LLMs | 368 | **0.054** |

> haiku 의 0.054 는 **공정한 비교가 아닙니다.** 토픽 문자열이 `"Evaluation of LLMs"` 라
> 벤치마크의 `"Evaluation of Large Language Models"` 와 달라 검색 쿼리부터 다릅니다.
> 정확한 문자열로 재생성해야 비교가 성립합니다.

**두 가지 제약이 토픽 선택을 좌우합니다.**

1. `ref_bench`는 **10개 토픽에만** 있습니다. LLM judge를 안 쓰기로 한 이상,
   그 밖의 토픽으로는 정량 수치가 하나도 나오지 않습니다.
2. 채점기가 **`ref_bench`의 최신 논문보다 새 인용을 분모에서 뺍니다**(RAG는 2024-07).
   최신화본으로 돌리면 인용 대부분이 걸러져 표본이 작아집니다. **벤치마크 비교는
   배포본으로, 최신화 효과 시연은 최신화본으로** 나눠 돌리세요.

### C. 새 백본으로 첫 실행 — **크레딧 확보 후 바로 이것부터**

교수님 의견은 closed model(Claude-3-Haiku)보다 **비슷한 성능의 open model API**를 쓰자는
것이었고, `deepseek/deepseek-v4-pro`로 한 편 생성해 확인했습니다.
**다음 백본은 `deepseek/deepseek-v4-flash-0731`로 확정**했습니다 (2026-08-05).

순서는 이렇습니다:

1. **스모크 1편** — 축소 설정(`--section_num 4 --outline_reference_num 200 --rag_num 15`).
   확인할 것: 응답의 provider가 실제로 Parasail인지, 잘림 경고가 뜨지 않는지.
2. **계수 측정** — `check_survey.py <md> --subsection-len=700 --target-words=20000`.
   `v4-flash-0731`의 계수는 **1.76× 로 측정 완료**입니다(2026-08-05, 두 실행).
3. **본 실행** — 2에서 얻은 `--subsection_len`과 `--subsection_num 4`로.

| 항목 | 값 |
|---|---|
| 단가 | 입력 **$0.14/M** · 출력 **$0.28/M** — `v4-pro`($0.435/$0.870)의 **1/3.1** (핀한 fp8 기준) |
| 컨텍스트 | 1,048,576 |
| 태그 | **날짜 고정**이라 제공자 갱신에 흔들리지 않음 (`v4-flash`·`-latest`는 갱신됨) |
| 엔드포인트 | **`parasail/fp8` 고정** — `.env`에 `AUTOSURVEY_PROVIDER=parasail/fp8` |

### D. DB 재갱신 (필요해지면)

DB 최신화 자체는 **완료됐습니다**(위 "DB 최신화" 절). 아래는 스냅샷이 또 낡았을 때
쓰는 절차입니다. `--oai-from`을 직전 스냅샷의 수록 최신일 다음날로, `--exclude-db`를
직전 스냅샷으로, `--out-dir`을 새 날짜 디렉터리로 바꾸면 됩니다.
**LLM API를 쓰지 않아 크레딧과 무관합니다.**

```bash
# 1) 수집 — arXiv OAI-PMH 는 API 키가 필요 없습니다 (약 646요청, 2시간)
python scripts/harvest_arxiv.py --sets cs --oai-from 2024-04-27 \
  --exclude-db ./database/arxiv_paper_db.json --out-dir ./database_2026-08 --delay 3

# 2) append — 기존 스냅샷은 읽기만 합니다 (임베딩 약 30분)
python scripts/append_snapshot.py --base ./database \
  --new ./database_2026-08/arxiv_paper_db.json --out ./database_2026-08

# 3) 검증
python scripts/check_db.py --db-path ./database_2026-08 --verify-embeddings 20

# 4) 두 스냅샷 비교 — 최신화의 효과 측정
python scripts/compare_snapshots.py --old ./database --new ./database_2026-08 \
  --topics "In-context Learning" "Evaluation of LLMs"
```

끝나면 새 스냅샷의 md5 지문을 `REPRODUCTION.md` §3에 행으로 추가하세요.

---

## 테스트

```bash
conda activate autosurvey
python -m unittest discover -s tests -t .
```

**설치할 것이 없습니다** — `unittest`는 표준 라이브러리이고, 66개가 **0.2초**에 끝납니다.
네트워크·GPU·DB·API를 전혀 쓰지 않습니다(`requests.get`은 mock).

무엇을 지키는지:

| 파일 | 지키는 것 |
|---|---|
| `test_model_payload.py` (11) | **환경변수 없으면 페이로드가 `{}`** — 원본과 같은 요청이 나간다는 보장 / provider 핀의 `allow_fallbacks=False` |
| `test_outline_parser.py` (15) | **`--subsection_num` 기본값이 원본 프롬프트를 글자 단위로 복원** / 서브섹션 절단 / 파서가 마크다운 장식·누락 설명·순서 뒤섞임을 견딤 |
| `test_harvest_schema.py` (16) | 배포 DB 표기 규약 — **`date`가 `<created>`가 아니라 v1 제출일** / 초록의 TeX escape 보존 / 제목 금지문자 제거 / 저자 유니코드 |
| `test_length_band.py` (7) | 분량 구간 경계와 실측값 판정 |
| `test_provider_pin.py` (6) | 모델·provider 어긋나면 중단, 네트워크 장애는 막지 않음 |

**변이 테스트로 실제로 잡는지 확인했습니다** — 프롬프트 기본값 변경, 절단 로직 제거,
구간 경계 변경, `allow_fallbacks` 반전, `date`를 `<created>`로 바꾸기 5가지를 넣어
전부 FAILED가 났습니다.

특히 앞의 둘은 **baseline 신뢰성의 근거**입니다. 누가 프롬프트나 기본값을 건드리면
"원본과 동일"이라는 주장이 조용히 깨지는데, 이제 테스트가 먼저 알려줍니다.

---

## 함정 모음

- **`--api_url`은 끝에 `/chat/completions`까지** 붙여야 합니다. `src/model.py`가 경로를 덧붙이지 않고 그대로 씁니다
- **`--model`은 OpenRouter의 `provider/model` 형식** (`anthropic/claude-3-haiku`)
- **컨텍스트 32k 이상 모델**을 고르세요. `main.py`가 `chunk_size=30000`으로 아웃라인 청크를 만듭니다
- **동시 요청이 `section_num × AUTOSURVEY_MAX_THREADS`** 입니다. 코드 기본값이면 8×15=120개가 한꺼번에 나가 429를 맞습니다. `.env`에 `AUTOSURVEY_MAX_THREADS=4`로 잡아 뒀습니다 — 올리지 마세요
- **`main.py --gpu` 인자는 아무 데서도 안 쓰입니다** (파싱만 하고 버림). `CUDA_VISIBLE_DEVICES`를 쓰세요
- **GPU 번호를 고정하지 마세요.** `.env`에 `CUDA_VISIBLE_DEVICES=0`이 들어 있지만 공용 서버라 0번이 차 있을 수 있습니다. 실행 전 `nvidia-smi`로 빈 것을 고르세요 (`nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | sort -t, -k2 -n | head -1`)
- **크레딧은 `/api/v1/key`로 확인하세요.** `/api/v1/credits`는 **계정 전체** 잔액이라 이 키에 걸린 한도($30)가 보이지 않습니다. 잔액이 있어 보여도 키가 소진됐으면 실행이 죽습니다
- **`evaluation.py`를 돌릴 거면 `judge.py`부터 고치세요.** 인용 문장 하나당 스레드 하나를 **제한 없이** 띄웁니다 (`judge.py:198-220`). 32k 서베이면 수백 개가 동시에 나갑니다
- `database.py`의 `get_paper_from_ids()`(전문 로딩)는 **코드 어디에서도 호출되지 않습니다.** 공개 DB는 초록만 있고, 논문은 본문 앞 1500토큰을 씁니다 — 이게 논문과의 가장 큰 갭입니다 (`SETTING.md` §8)

---

## 서버 환경 메모

- **L40S 46GB × 8**, CUDA 12.4 / 드라이버 550.120, RAM 1TB, `/data2` 여유 2.8TB. **공용 서버**
- 네트워크: OneDrive **차단** (`1drv.ms` SSL 오류, `onedrive.live.com` 403) / `export.arxiv.org` OAI-PMH 가능 / HuggingFace 가능 / `export.arxiv.org/api/query`(REST)는 타임아웃
- 시스템 python3에는 pip이 없습니다. 패키지는 conda env에 설치하세요
