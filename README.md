# AutoSurvey — 재현 · DB 최신화 · 분량 통제

[AutoSurvey (NeurIPS 2024)](https://arxiv.org/abs/2406.10252)의 포크입니다.
GPU 서버에서 **서베이 생성 파이프라인을 end-to-end로 재현**했고,
**2024-04에 멈춰 있던 논문 DB를 2026-08까지 최신화**했으며(53.7만 → 90.9만편, §3),
모델에 따라 3배까지 벌어지던 **출력 분량에 통제 수단**을 붙였습니다(§4).

원본 README(논문 소개)는 맨 아래 [원본 프로젝트](#원본-프로젝트)로 옮겼습니다.

| 문서 | 역할 |
|---|---|
| **`README.md`** (이 문서) | 프로젝트가 무엇이고, 무엇이 나왔고, 다음에 무엇을 하는지 |
| [`HANDOFF.md`](HANDOFF.md) | 지금 어디까지 됐고 다음에 뭘 하면 되는지 — **작업 시작 전 필독** |
| [`REPRODUCTION.md`](REPRODUCTION.md) | 산출물 재현에 필요한 입력값 일체 (환경·DB 지문·커밋·하이퍼파라미터) |
| [`SETTING.md`](SETTING.md) | 세팅 **절차**와 각 패치의 근거 |
| [`output/README.md`](output/README.md) | 산출물의 결과 수치와 비교 시 주의점 |
| [`.env.example`](.env.example) | 환경변수 템플릿 — `cp .env.example .env` 후 키만 채우면 됩니다 |
| [`tests/`](tests/) | `python -m unittest discover -s tests -t .` — 78개, 0.3초. 네트워크·GPU 불필요 |

> 세 프로젝트(AutoSci·AutoSurvey·SurveyForge) 비교와 **시스템 간 통제 프로토콜**은
> 이 저장소 밖 `../SURVEY_REPORT.md`에 있습니다(§7). git 추적 대상이 아닙니다.

---

## 1. 경로

**서버 작업 경로**: `/data2/chanjoong/survey-agent/AutoSurvey` (브랜치 `reproduce`)

같은 상위 디렉터리에 비교 대상 프로젝트가 함께 있습니다 —
`SurveyForge/`, `SurveyForge_data/`, `SurGE/`.
(AutoSci는 이 서버가 아니라 로컬 macOS에서 돌렸습니다.)

```
AutoSurvey/
├── main.py                  생성 진입점 — 검색 → 아웃라인 → 본문 → LCE
├── evaluation.py            LLM judge 평가 진입점 — **쓰지 않기로 확정**
├── src/
│   ├── database.py          TinyDB + FAISS 검색, nomic 임베딩
│   ├── model.py             OpenRouter API 호출, 재시도·토큰 계측
│   ├── prompt.py            프롬프트 템플릿
│   └── agents/
│       ├── outline_writer.py   아웃라인 생성·파싱
│       ├── writer.py           서브섹션 병렬 작성 + LCE 정제
│       └── judge.py            LLM judge 평가 (미사용)
├── scripts/                 이 포크에서 추가한 도구 (§5)
├── database/                논문 DB — 저자 배포본, 3.9GB. git에 없음 (.gitignore)
├── database_2026-08/        논문 DB — 최신화본, 6.9GB. 위를 확장한 것 (§3)
├── output/                  생성된 서베이 — 모델별 디렉터리
│   ├── haiku/                  본편 3편
│   ├── deepseek-v4-pro/        본편 1편
│   ├── deepseek-v4-flash/      본편 — 새 백본
│   ├── deepseek-v4-flash-newdb/  본편 3편 — 새 백본 × 최신화 DB
│   ├── haiku-smoke/            파이프라인 점검용
│   ├── deepseek-smoke/         파이프라인 점검용
│   └── deepseek-v4-flash-smoke/  파이프라인 점검용 + 분량 계수 측정
├── examples/                원저자들이 생성한 서베이 3편 (대조용)
├── tests/                   unittest 78개, 0.3초. 네트워크·GPU 불필요
├── .env.example             환경변수 템플릿 (커밋됨)
└── .env                     API 키 등 — git에 없음, 권한 600
```

### 데이터베이스 — 스냅샷 2개

**둘 다 git에 없습니다**(`.gitignore`). 배포본은 저자 배포본을 scp로 반입한 것이고
(이 서버에서 OneDrive는 차단), 최신화본은 거기에 arXiv에서 받은 신규 논문을 더한 것입니다.
md5 지문은 [`REPRODUCTION.md`](REPRODUCTION.md) §3.

| 스냅샷 | 경로 | 논문 수 | 수록 범위 | 크기 |
|---|---|---|---|---|
| 배포본 | `database/` | 537,665 | ~2024-04-26 | 3.9GB |
| **최신화본** | `database_2026-08/` | **909,293** | **~2026-08-03** (배포본 537,665편 **전부 포함**) | 6.9GB |

> **`database_2026-08`은 "2026-08의 논문"이 아니라 "2026-08 시점의 스냅샷"입니다.**
> 배포본을 통째로 담고 그 위에 2024-04-27 이후 논문 371,628편을 얹은 **상위 집합**입니다.
> 두 스냅샷은 대체 관계지 분할이 아닙니다 — 둘을 합쳐 쓰는 일은 없습니다.

각 디렉터리에 같은 이름의 4파일이 들어 있습니다.

| 파일 | 내용 |
|---|---|
| `arxiv_paper_db.json` | 논문 레코드 — `id`/`title`/`abs`/`date`/`cat`/`url`/`authors` |
| `faiss_paper_abs_embeddings.bin` | 초록 임베딩 `IndexFlatL2` N × 768 |
| `faiss_paper_title_embeddings.bin` | 제목 임베딩 (동일 규격) |
| `arxivid_to_index_abs.json` | arXiv id → FAISS 인덱스 매핑 |

- 임베딩은 `nomic-ai/nomic-embed-text-v1`. **바꾸면 인덱스 전체가 무효**가 되고
  에러 없이 엉뚱한 논문이 검색됩니다.
- **`output/` 의 11편 중 8편은 배포본, 3편(`deepseek-v4-flash-newdb/`)은 최신화본입니다.**
  기존 8편을 재현하려면 배포본을 쓰세요.
- 최신화본은 배포본을 **읽기만 하고** 만들었고, `IndexFlatL2` append가 기존 행 번호를
  보존하므로 **배포본은 최신화본의 prefix**입니다. 만든 과정은 §3.

---

## 2. 결과 요약

**서베이 11편 생성 완료** — 본편 8편 + 파이프라인 점검용 스모크 3편.
토픽당 `.md` / `.json` / `.tex` / `.pdf` 가 나옵니다.

### 본편 8편

| 디렉터리 / 토픽 | 모델 | DB | 섹션/서브 | 단어 | 참고문헌 | 쪽 | 비용 |
|---|---|---|---|---|---|---|---|
| `haiku/` In-context Learning | claude-3-haiku | 배포본 | 9 / 51 | 28,161 | 383 | 74 | $0.78 |
| `haiku/` Large Multi-Modal LM | claude-3-haiku | 배포본 | 8 / 48 | 26,410 | 378 | 72 | $0.75 |
| `haiku/` Evaluation of LLMs | claude-3-haiku | 배포본 | 8 / 48 | 26,294 | 368 | 71 | $0.75 |
| `deepseek-v4-pro/` In-context Learning | deepseek-v4-pro | 배포본 | 10 / 72 | 86,121 | 644 | **184** | $3.39 |
| `deepseek-v4-flash/` RAG for LLMs | v4-flash-0731 | 배포본 | 10 / 39 | 49,002 | 476 | 111 | $0.376 |
| **`deepseek-v4-flash-newdb/` RAG for LLMs** | v4-flash-0731 | **최신화본** | 11 / 44 | 56,273 | 632 | 137 | $0.420 |
| **`deepseek-v4-flash-newdb/` 3D Gaussian Splatting** | v4-flash-0731 | **최신화본** | 12 / 48 | 59,980 | 804 | 153 | $0.456 |
| **`deepseek-v4-flash-newdb/` LLM-based Multi-Agent** | v4-flash-0731 | **최신화본** | 7 / 28 | 40,599 | 486 | 103 | $0.286 |

<sub>**기준 (2026-08-18 통일)**: 섹션·서브섹션은 번호 중복 헤딩 제거 후, 단어는 인용
표기 `[1; 2]` 제외, 쪽수는 pdflatex 컴파일 후 `pdfinfo` 실측(목차·참고문헌 포함).
스모크 3편과 각 편의 해석 주의점은 [`output/README.md`](output/README.md).</sub>

**11편 전부 `scripts/check_survey.py` 통과**(댕글링 인용 0, json 매핑 일치)이고
**전부 PDF 로 컴파일됩니다**(에러 0, 미해결 인용 0). 컴파일 절차는 §6.

> **최신화본으로 만든 산출물 3편이 생겼습니다 (2026-08-18).**
> 세 토픽 모두 인용의 **82~92% 가 2024-07 이후** — 배포본에는 존재조차 하지 않던
> 논문입니다. 나머지 8편은 배포본이고 그 비율이 전부 0.0% 입니다.
> 같은 토픽 A/B 통제 비교와 토픽별 상세는 [`output/README.md`](output/README.md).

**통제 실험에서 확인된 것** (v4-flash 본편 4편, 파라미터 동일 · 토픽과 DB 만 다름):

| 인자 | 결과 |
|---|---|
| `--subsection_num 4` | ✅ **정확히 지켜짐** — 네 편 모두 섹션당 3.9~4.0 |
| `--section_num 8` | ❌ **7~12 로 흔들림.** 초과도 미달도 하며 방향이 예측되지 않음 |
| 분량 계수 | ✅ **1.79 / 1.83 / 1.79 / 2.07 로 안정적** — 토픽·DB 가 바뀌어도 거의 같음 |
| 참고문헌 수 | ⚠ **486~804편.** 인간 서베이(173~271)의 **2.8~3.3배**, 가드 400 초과 |

**분량이 40,599~59,980단어(103~153쪽)로 벌어지는 주된 원인은 `--section_num` 입니다.**
서브섹션 개수와 길이는 통제되는데 섹션 수가 안 잡힙니다.

### 새 백본 실행 기록 — `deepseek-v4-flash-0731` (2026-08-05)

토픽은 `Retrieval-Augmented Generation for Large Language Models`(SurveyBench 문자열
그대로), DB는 둘 다 배포본입니다.

| | 스모크 | 본편 A |
|---|---|---|
| 설정 | `--section_num 4 --outline_reference_num 200 --rag_num 15` | `--section_num 8 --outline_reference_num 1200 --rag_num 60 --subsection_num 4` |
| `MAX_THREADS` | 4 (동시 16) | 2 (동시 16) |
| **소요** | **8분 21초** | **9분 32초** |
| 입력 토큰 | 836,762 | 2,295,924 |
| 출력 토큰 | 194,344 | 227,508 |
| **비용** | **$0.166** | **$0.376** |
| 재시도(429) | 5회 | 4회 |
| 최종 실패 | 0건 | 0건 |
| 출력 잘림 | 0건 | 0건 |
| 추론 토큰 | 0 | 0 |

단계별 청구:

| | outline | writer | 합계 |
|---|---|---|---|
| 스모크 | $0.0221 | $0.1443 | $0.166 |
| 본편 A | $0.0759 | $0.3003 | $0.376 |

**비용은 분량이 아니라 입력이 정합니다.** 두 실행의 단어 수는 44,803 대 49,002으로 9%
차이인데 비용은 2.3배입니다. 입력이 2.7배(`rag_num` 15→60, `outline_reference_num`
200→1200)이기 때문입니다. 비용의 **85%가 입력**입니다. 줄이려면 분량이 아니라 이 두 인자를
건드려야 합니다.

**시간은 거의 같습니다.** 비용이 2.3배인데 소요는 8분 21초 → 9분 32초입니다. 동시 요청 수를
16으로 맞췄기 때문입니다(스모크 4섹션×4스레드, 본편 8섹션×2스레드). 실행 시간은 토큰량이
아니라 동시성이 지배합니다.

확인된 것:

| 항목 | 결과 |
|---|---|
| provider 고정 | ✅ 실제로 Parasail에서 응답 (429 에러가 `"provider_name":"Parasail"`을 실어 옴) |
| 단가 | ✅ 청구 $0.0221 = 139,932×$0.14/M + 9,383×$0.28/M — **`parasail/fp8` 단가 그대로** |
| 추론 토큰 | ✅ 0 — `AUTOSURVEY_REASONING=off`가 이 모델에서 작동 |
| 출력 잘림 | ✅ 0건 |
| **`--subsection_num 4`** | ✅ **10개 섹션 전부 4개 이하** (4,4,3,4,4,4,4,4,4,4) — 코드 상한이 지켜짐 |
| `--section_num 8` | ⚠ **10섹션이 나왔습니다.** 섹션 수는 통제되지 않습니다 |
| 재시도 | ⚠ 429 5회 / 4회 — Parasail 레이트리밋. 최종 실패는 0건 |
| 참고문헌 | ⚠ **476편** — 가드(400)를 넘었습니다 (인간 RAG 서베이는 191편) |

**`--subsection_num`은 작동하지만 `--section_num`은 아닙니다.** 자유도가 둘인데 우리 패치가
잡은 건 하나입니다. **초과만 하는 게 아니라 미달도 합니다 — 방향조차 예측되지 않습니다.**

| 실행 | 지시 | 실제 | 배율 |
|---|---|---|---|
| v4-flash 스모크 | 4 | 5 | 1.25× |
| 본편 A (RAG, 배포본) | 8 | 10 | 1.25× |
| 본편 B (RAG, 최신화본) | 8 | 11 | 1.38× |
| 본편 B (3DGS, 최신화본) | 8 | 12 | **1.50×** |
| 본편 B (Multi-Agent) | 8 | **7** | **0.88× (미달)** |

그래서 **개수를 묶었는데 총 서브섹션은 거의 그대로였습니다**: 스모크 5×7.4=37 →
본편 10×3.9=39. 섹션이 두 배로 늘어 서브섹션 상한을 상쇄했습니다. 분량 예측을
35,000으로 잡았는데 49,002가 나온 것이 이 때문입니다(섹션 초과 1.25× × 계수 보정 1.15×).

> **429는 `allow_fallbacks=false`의 대가입니다.** 붐빌 때 다른 provider로 넘어가지 않으므로
> 레이트리밋을 정면으로 맞습니다. 통제 실험을 위해 감수하고, `AUTOSURVEY_MAX_THREADS`로
> 완화합니다. 두 실행 모두 백오프(1·2·4·8·16초) 안에서 전부 뚫렸습니다.

> **v4-pro의 비용 실측이 예상의 2.3배였던 원인이 확정됐습니다.** 모델이 아니라 **라우팅**
> 이었습니다. v4-pro는 엔드포인트 단가가 $0.435~$1.740로 4배 벌어져 있는데 그 실행에는
> provider 핀이 없었습니다. 핀이 걸린 지금은 청구액이 단가표와 소수점까지 맞습니다.

### 원본 대비 코드 변경

두 종류입니다. **버그 수정**은 없으면 실행 자체가 안 되던 것이고,
**기능 추가**는 기본값이 원본과 동일해 켜지 않으면 아무것도 달라지지 않습니다.

**버그 수정 11종** ([`REPRODUCTION.md`](REPRODUCTION.md) §4 표가 정본) — 그중 셋이 결정적이었습니다:

| 패치 | 없으면 |
|---|---|
| 죽은 `langchain.document_loaders` import 제거 (`src/utils.py`) | `ImportError`로 즉사 |
| `[[]] * n` aliasing 버그 (`src/agents/writer.py`) | **크래시 없이** 섹션 0을 뺀 전 섹션이 섹션 0의 참고문헌으로 본문을 씀 |
| TinyDB 선형 스캔 → dict 인덱스 (`src/database.py`) | 호출당 수 분 정지 |

**기능 추가** — 전부 **기본값이 원본 동작**입니다(환경변수·인자를 주지 않으면 무효):

| 변경 | 내용 | 켜는 법 |
|---|---|---|
| `src/prompt.py` | `several subsections` → `[SUBSECTION NUM] subsections`. 값을 안 주면 `several`이 들어가 **원본과 글자 단위로 동일** | `--subsection_num` |
| `src/agents/outline_writer.py` | `subsection_num` 인자, `process_outlines`에서 초과 서브섹션 절단 | 〃 |
| `src/model.py` | **provider 고정** — `{"provider": {"order": [...], "allow_fallbacks": false}}`. 안 하면 서브섹션마다 다른 quantization이 씀 | `AUTOSURVEY_PROVIDER` |
| `src/model.py` | **출력 잘림 검사** — `finish_reason='length'`를 집계·경고. 원본은 잘린 응답을 그대로 반환했음 | 항상 |
| `main.py` | `--subsection_num` / 모델·provider 정합 검사(DB 로딩 전 중단) / 잘림 건수 리포트 | — |

이 다섯 가지는 `tests/`가 지킵니다 — 특히 **"환경변수 없으면 원본과 동일"**을 회귀
테스트로 고정했습니다(변이 테스트로 실효성 확인).

> **프롬프트 "내용"은 바꾸지 않았습니다.** 문구를 다시 쓰면 원본 AutoSurvey와 다른
> 시스템이 되어 baseline으로서의 의미가 흐려집니다. placeholder만 넣었습니다.

전체 목록과 근거는 `REPRODUCTION.md` §4, `SETTING.md` §3·§4.

### 범위 밖

- **논문의 정량 수치 재현** — 논문은 각 논문 **본문 앞 1,500토큰**을 쓰는데 공개 DB에는
  초록만 있습니다. 입력이 근본적으로 다릅니다.
- **LLM-as-Judge 평가** — `evaluation.py` / `judge.py` 경로는 **쓰지 않기로 확정**했습니다
  (2026-08-05). 평가는 `../SurveyForge/SurveyBench/`의 **인용 커버리지**로 합니다 —
  arXiv id 집합 교집합이라 LLM 호출이 0회이고 크레딧이 필요 없습니다. 상세와 기준값은
  [`HANDOFF.md`](HANDOFF.md) 남은작업 B.
> **크레딧**: 키 한도가 $10 → **$30**으로 상향됐습니다(2026-08-05). 잔여는
> `curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/key`
> 로 확인하세요 — `/api/v1/credits`는 계정 잔액이라 키 한도가 보이지 않습니다.

---

## 3. 개선 방향 — DB 최신화

### 3.1 문제

DB에 수록된 논문의 최신 날짜가 **2024-04-26**입니다. 현재(2026-08) 기준 **27개월**이
비어 있습니다. 그 사이에 부상한 주제는 검색 자체가 되지 않고, 기존 주제도 최근 2년치
후속 연구가 통째로 빠집니다. 서베이 생성기로서는 치명적인 노화입니다.

공백의 크기는 arXiv OAI-PMH로 **직접 셌습니다**(2026-08-04, `set=cs&from=2024-04-27`):

| 항목 | 실측 |
|---|---|
| 반환 레코드 | **419,246건** |
| ├ 신규 논문 (cutoff 이후 최초 제출) | **350,805편** ← 실제 추가 분량 |
| └ 기존 논문의 v2/v3 갱신 | 68,441건 ← dedup으로 걸러야 함 |
| 월 평균 | 12,529편 (28개월). 최근일수록 증가 — 2026-05는 18,975편 |

DB가 **537,665 → 888,470편(+65%)**이 됩니다. "증분"이라 부르기엔 큰 규모이고,
월 1.2~1.9만 편씩 계속 벌어지므로 일회성 작업이 아니라 갱신 절차로 만들어야 합니다.

### 3.2 설계 원칙 — 수집과 검색을 분리한다

**online search를 에이전트에 넣지 않고 DB에 넣습니다.** 최신성은 생성 시작 전의
수집 단계가 담당하고, 생성 단계는 지금 그대로 둡니다.

```
① 수집 (신규 — run 시작 전 1회 배치, 여기만 온라인)
   arXiv에서 cutoff 이후 CS 논문 수집
   → 동일 모델(nomic-embed-text-v1)로 임베딩
   → 기존 FAISS 인덱스에 append
   → 스냅샷 확정: md5 지문 + cutoff 날짜 발행

② 생성 (기존 파이프라인 무변경 — 완전 오프라인)
   아웃라인 → 서브섹션별 FAISS 검색 → 작성 → LCE 정제
```

생성 루프 안에 실시간 검색을 넣는 대안은 **택하지 않습니다.** AutoSurvey를 baseline으로
쓰는 근거인 세 불변식이 전부 깨지기 때문입니다:

| 불변식 | 실시간 검색을 넣으면 |
|---|---|
| **결정적 검색** — 고정 스냅샷 + 동일 임베딩 + FAISS | 같은 설정으로 재실행해도 결과가 달라져 통제 실험 불가 |
| **DB 내 인용** — 검색해 꺼낸 논문만 인용 | 댕글링 인용 0 보장과 무결성 검사가 무의미해짐 |
| **파이프라인 통제** — 로컬에서 닫힌 실행 | 서브섹션 수십 개 × 라이브 호출로 rate limit·지연이 실행 시간에 직접 얹힘 |

같은 이유로, 비교 실험에서 "모델·파이프라인 차이"와 "그날의 검색 결과 차이"를
분리할 수 없게 되는 것도 실시간 검색을 배제하는 근거입니다.

### 3.3 전제 검증 — 실측 완료

증분 적재의 전제는 "**새 논문을 우리 코드로 임베딩했을 때 기존 벡터와 같은 공간에
놓이는가**"입니다. 절차가 어긋나면 **에러 없이** 검색 품질만 무너지므로 먼저 확인했습니다.

| 확인 항목 | 결과 |
|---|---|
| 인덱스 타입 | `IndexFlatL2` — 학습된 양자화기가 없어 **append에 재학습 불필요**. 기존 벡터 인덱스 0~537,664가 그대로 보존 |
| 임베딩 절차 재현 | DB 수록 논문 8편 재임베딩 → **cos 1.000000 / L2 0.0000** (title·abs 모두) |
| 벡터 정규화 | 저장 벡터가 이미 단위 정규화 (`\|v\| = 1.000`) |
| 프리픽스 규약 | 색인 `search_document: ` / 검색 `search_query: ` — 원본 노트북·`build_index.py`·`database.py` 3자 일치 |
| 임베딩 처리량 | L40S 1장 **247편/s** (초록 평균 166단어) → 30만 편 abs 약 20분, title 포함 30분 안쪽 |

**결론: 동일 공간 유지가 성립합니다.** 임베딩은 병목도 위험 요소도 아닙니다.

### 3.4 실제 위험 요소

임베딩이 아니라 **스키마와 정합**이 위험합니다.

1. **수집 스크립트의 스키마가 실제 DB와 다릅니다.**
   실제 DB 필드는 7개(`id`/`title`/`abs`/`date`/`cat`/`url`/`authors`)인데
   `scripts/harvest_arxiv.py`는 4개(`id`/`title`/`abs`/`date`)만 만듭니다.
   그대로 합치면 새 논문만 필드가 비는 반쪽 DB가 됩니다. **먼저 맞춰야 합니다.**

2. **arXiv id의 버전 접미사.** 기존 DB는 `1811.06122v1` 형식이고
   `harvest_arxiv.py`는 버전 없는 id를 씁니다. 정책을 통일하고 base id로 dedup해야 합니다.

3. **OAI-PMH `from=`은 "수정일" 기준입니다.** cutoff 이전 논문이 v2/v3로 갱신되면
   다시 딸려옵니다 — 실측으로 **68,441건**이 여기 해당합니다(전체 반환의 16%).
   dedup하지 않으면 같은 논문이 중복 벡터로 들어가 top-k를 잡아먹습니다.
   갱신본을 반영할지도 정해야 하는데, **기존 판을 유지하고 건너뛰는 쪽**을 권합니다 —
   옛 스냅샷의 벡터를 그대로 두어야 두 스냅샷 비교가 성립합니다.

4. **파일 4개의 정합이 깨져도 에러가 나지 않습니다.** TinyDB / abs FAISS / title FAISS /
   id→index 매핑이 같은 순서로 커져야 하는데, 어긋나면 **조용히 엉뚱한 논문을 반환**합니다.
   append 후 `scripts/check_db.py` 실행이 필수입니다.

5. **수집 엔드포인트가 이전됐습니다.** `harvest_arxiv.py:30`이
   `http://export.arxiv.org/oai2`를 하드코딩하고 있는데 지금은
   `https://oaipmh.arxiv.org/oai`로 **301 리다이렉트**됩니다. `requests`가 GET
   리다이렉트를 따라가므로 당장은 동작하지만, 매 요청 왕복이 늘고 리다이렉트가
   끊기면 조용히 실패합니다. 새 URL로 고쳐야 합니다.

> **참고 — 문서 정정**: DB에 `authors` 필드가 **537,665편 전부** 채워져 있습니다(결측 0.000%).
> 일부 문서에 "저자 필드가 없다"고 적혀 있었으나 오기입니다. `.bib` 생성을 위해 저자를
> 외부에서 따로 받아올 필요가 없습니다.

### 3.5 수집에 필요한 것 — API 키는 없어도 됩니다

**arXiv OAI-PMH는 인증이 없습니다.** 키·토큰·계정 모두 불필요하고, 2026-08-04에
이 서버에서 `User-Agent`만 붙여 200 응답을 확인했습니다. 대신 지켜야 할 것이 있습니다.

| 항목 | 실측 / 요구사항 |
|---|---|
| 인증 | **없음** — API 키 불필요 |
| 엔드포인트 | `https://oaipmh.arxiv.org/oai` (구 `export.arxiv.org/oai2`는 301) |
| `User-Agent` | 식별 가능한 값 필수. 연락처 포함 권장 |
| 페이지 크기 | `ListRecords` **1,300건**(약 3.8MB) / `ListIdentifiers` 20,000건 |
| 요청 간 지연 | 3초 (`--delay`, 503 + `Retry-After` 처리는 구현돼 있음) |
| `metadataPrefix` | `arXiv` — **`<authors>`·`<categories>` 포함**, 7필드 스키마를 채울 수 있음 |

키가 필요한 경로는 쓰지 않습니다 — Semantic Scholar(rate limit 상향용 키),
Kaggle arXiv 덤프(계정 토큰). OAI-PMH만으로 충분합니다.

**예상 소요** (전체 CS 기준):

| 단계 | 추정 |
|---|---|
| 수집 | 419,246건 ÷ 1,300 = **약 323요청** × (3초 지연 + 전송) ≈ **40분~1시간**, 전송량 약 1.2GB |
| 임베딩 | 350,805편 × 2(초록·제목). 초록은 247편/s 실측이라 24분, 제목은 더 빠름 → **30분 안쪽** |
| 디스크 | FAISS +2.15GB, TinyDB +0.5GB → 새 스냅샷 약 6.6GB. 옛 스냅샷을 함께 보관해도 10.5GB |

**LLM API 비용은 0입니다.** 수집·임베딩 어디에도 생성 모델을 쓰지 않으므로,
현재 크레딧이 소진된 상태에서도 이 작업 전체를 진행할 수 있습니다.

### 3.6 스냅샷 버저닝 — 갱신하면 baseline이 바뀐다

임베딩 공간을 지켜도 **코퍼스가 +65% 되면 같은 토픽의 top-1200 자체가 달라집니다.**
기존 6편과의 통제 비교는 어차피 성립하지 않습니다. 이것을 손실이 아니라 **측정 대상**으로
다룹니다.

- **2024-04 스냅샷은 immutable로 보존**하고 새 스냅샷은 별도 파일로 만듭니다.
  `IndexFlatL2` append가 기존 순서를 보존하므로 옛 스냅샷은 새 스냅샷의 prefix가 됩니다.
  두 벌을 두어도 디스크는 10.5GB뿐입니다.
- `REPRODUCTION.md`가 이미 DB를 **md5로 지문 관리**하므로, 새 스냅샷 = 새 md5 행 +
  cutoff 날짜. 기존 관례의 자연스러운 확장입니다.
- 그러면 **같은 토픽 × 두 스냅샷**으로 "DB 최신화의 효과"가 독립 변수 하나가 됩니다.
  단순 갱신보다 실험으로서 값어치가 큽니다.

### 3.7 수집 범위 — 전체 CS

핵심 카테고리(`cs.CL`/`cs.LG`/`cs.AI`/`cs.CV`)만 받는 안과 비교해 **둘 다 실측했습니다.**

| | 전체 CS | 핵심 4개 |
|---|---|---|
| 신규 논문 | **350,805편** | 243,999편 (교차 게재 제거 후) |
| 카테고리별 단순 합 | — | 344,180편 → 중복 10만 편 |
| 수집 요청 수 | 약 323회 | 약 316회 |

**전체 CS를 권합니다.** 근거 둘:

1. **비용이 사실상 같습니다.** 4개 카테고리를 받으려면 set별로 따로 요청해야 하는데
   교차 게재 때문에 같은 논문을 여러 번 받습니다. 요청 수가 316 대 323으로 거의
   같은데 수록량만 30% 적습니다.
2. **기존 DB가 전체 CS입니다.** 4개로 한정하면 신규분만 좁아져 코퍼스가 시기별로
   비대칭이 됩니다. 예컨대 `cs.IR`은 2024-04 이전 논문만 있고 이후는 없는 상태가 되어,
   정보검색 계열 토픽에서 **최신 논문이 없는 게 아니라 수집하지 않은 것**이 되는데
   검색 결과만 봐서는 구분되지 않습니다. 현 DB 상위 분포가
   cs.CV(85,292) / cs.LG(74,835) / cs.CL(42,393) / **cs.IT(26,566)** / **cs.RO(20,498)**
   인 것을 보면 4개 밖 카테고리도 무시할 수 없습니다.

### 3.8 실행 결과 — 2026-08-04 완료

DB 갱신은 GPU와 네트워크만 쓰고 **LLM API를 전혀 쓰지 않아** 크레딧이 소진된 상태에서
그대로 진행했습니다.

| # | 항목 | 상태 |
|---|---|---|
| 1 | `harvest_arxiv.py` 정정 — 7필드 스키마 / 버전 id 정책 / 새 OAI 엔드포인트 | ✅ |
| 2 | cutoff 이후 전체 CS 수집 — 419,246건 반환, 2시간 | ✅ |
| 3 | `append_snapshot.py` — 임베딩 후 인덱스 확장 (배포본 불변) | ✅ |
| 4 | 정합 검사 + 재임베딩 일치 검증 | ✅ |
| 5 | 같은 토픽 × 두 스냅샷 서베이 생성 | **크레딧 대기** |

**결과: `./database_2026-08/` — 537,665 → 909,293편 (+69%).**
파일 지문·구성·검증 결과는 [`REPRODUCTION.md`](REPRODUCTION.md) §3-B에 있습니다.

| 실측 | 값 |
|---|---|
| 수집 | 419,246건 / 646요청 / **2시간** (페이지당 11.3초, 재시도·503 **0건**) |
| 추가 | **371,628편** = cutoff 이후 350,805 + 배포본 결손분 20,823 |
| 제외 | 47,618건 (기존 논문의 v2/v3 개정본) |
| 임베딩 + 병합 | **30분** (L40S 1장) |
| 디스크 | 새 스냅샷 6.9GB. 배포본과 합쳐 10.8GB |

예측이 잘 맞았습니다 — 사전에 `ListIdentifiers`로 센 419,246건과 실제 수집량이
**정확히 일치**했고, cutoff 이후 신규분도 예측 350,805편 그대로였습니다.
예측에 없던 것은 **배포본 결손분 20,823편**입니다. 배포 DB가 arXiv CS 전체를
담고 있지 않아, 수정일 기준으로 딸려온 옛 논문 중 배포본에 없던 것들이 함께 들어갔습니다
(1991~2024에 분포).

**커버리지 효과** — `scripts/compare_snapshots.py` 실측. `d@1200`이 낮을수록 좋습니다.

| 토픽 | d@1200 (배포본 → 최신화본) | B의 2024-04 이후 비율 | top-1200 교집합 |
|---|---|---|---|
| In-context Learning | 0.853 → **0.796** | 64.4% | 34.9% |
| Evaluation of LLMs | 0.849 → **0.764** | 82.8% | 16.2% |
| Large Multi-Modal Language Models | 0.744 → **0.691** | 74.2% | 25.5% |

교집합이 16~35%뿐이라는 것은 **검색 결과가 대부분 바뀌었다**는 뜻입니다. §3.6에서 예상한
대로 기존 산출물과의 통제 비교는 성립하지 않으므로, 두 스냅샷을 모두 남긴 판단이
결과적으로 맞았습니다.

---

## 4. 개선 방향 — 분량 통제

### 4.1 문제

같은 `--subsection_len 700`인데 모델에 따라 분량이 **3배** 벌어집니다.
`deepseek-v4-pro` 편은 92,707단어 — **실측 184페이지**로, 서베이라기보다 문서를 이어
붙인 것에 가깝습니다.

전부 **중복 헤딩을 제거한** 기준입니다(`.tex` 변환이 하는 것과 같은 처리).
`.md`의 `##`/`###`를 그대로 세면 모델이 본문에 다시 쓴 제목까지 잡혀 부풀려집니다.

| 산출물 | 섹션 | 서브섹션 | 섹션당 | 서브당 단어 | 지시값 대비 |
|---|---|---|---|---|---|
| haiku × 3편 | 8~9 | 48~51 | 6.0 | 531~537 | **0.76~0.77×** |
| deepseek-v4-pro | 10 | 72 | 7.2 | 1,167 | **1.67×** |
| v4-flash 스모크 (`rag 15`, 통제 없음) | 5 | 37 | 7.4 | 1,211 | **1.73×** |
| v4-flash 본편 (`rag 60`, `subsec 4`) | 10 | 39 | **3.9** | 1,256 | **1.79×** |

**두 자유도가 곱해집니다.** 어느 쪽이 주범인지는 모델마다 다릅니다:

- haiku → v4-pro: 개수 1.41× / **길이 2.17×** → **길이**가 주범
- v4-pro → v4-flash: 개수 1.03× / 길이 1.06× → 둘 다 조금씩

`deepseek-v4-flash-0731`의 **길이 계수는 1.76×**입니다(두 실행 1.73 / 1.79의 평균).

> **`--rag_num`은 분량을 밀어올리지 않습니다 — 실측으로 확인했습니다.** 서브섹션당 논문을
> **15편에서 60편으로 4배** 늘렸는데 서브섹션당 단어는 1,211 → 1,256으로 **4% 늘었을
> 뿐**입니다. 분량을 만드는 것은 입력량이 아니라 프롬프트의 하한 + `"comprehensive"`
> 프레이밍입니다. `rag_num`은 **비용**만 3배로 올립니다.

### 4.2 원인 — 통제되지 않는 자유도가 셋

| 자유도 | 현재 | 위치 |
|---|---|---|
| 섹션 수 | `--section_num`으로 통제됨 | — |
| 서브섹션 수 | `"containing several subsections … Subsection K"` — 모델 재량 | `src/prompt.py` |
| 서브섹션 길이 | `"content more than [WORD NUM] words"` — **하한만 있고 상한 없음** | `src/prompt.py` |
| `max_tokens` | 코드 어디에도 없음 | — |

핵심은 `subsection_len`이 상한이 아니라 **하한**이라는 점입니다. 지시를 잘 따르는 모델일수록
넘겨 쓰고 약한 모델은 미달합니다.

> **계수는 (모델 × 시스템) 쌍의 성질입니다.** SurveyForge는 같은 자리를
> `"approximately [WORD NUM] words"`로 쓰는데, 같은 `deepseek-v4-pro`가 거기서는
> 1.25×입니다. 한쪽에서 잰 계수를 다른 쪽에 쓰면 안 됩니다.

### 4.3 대응 — 프롬프트 "내용"은 바꾸지 않습니다

문구를 다시 쓰면 원본 AutoSurvey와 다른 시스템이 되어 baseline으로서의 의미가 흐려집니다.
그래서 **파라미터화만** 했습니다.

| 변경 | 내용 |
|---|---|
| `src/prompt.py` | `several subsections` → `[SUBSECTION NUM] subsections`. **값을 주지 않으면 `several`이 들어가 원본과 글자 단위로 같습니다** |
| `src/agents/outline_writer.py` | `subsection_num` 인자 + `process_outlines`에서 초과 서브섹션 절단 (프롬프트 지시를 모델이 넘길 수 있으므로 코드로 상한 보장) |
| `main.py` | `--subsection_num`, **기본값 0 = 원본 동작** |
| `--enforce_section_num` (2026-08-31) | `[SECTION NUM]`이 러프 아웃라인 프롬프트에만 있고 merge 프롬프트에는 없어 **최종 섹션 수가 드리프트**한다(5 지시 → 8 관측, retrieval shuffle 때문에 확률적). 플래그를 주면 merge 프롬프트에 개수 문장을 삽입해 관철 — 논문 §2 "The outline predetermines the number of sections" 서술의 구현. **플래그 없으면 merge 프롬프트는 원본과 글자 단위로 같다** (렌더 바이트 동일성 테스트로 확인) |
| `scripts/check_survey.py` | `--length` 구간 판정, `--subsection-len=N --target-words=W` 계수 역산 |

길이는 프롬프트가 아니라 **캘리브레이션**으로 맞춥니다 — 목표를 모델 계수로 나눠
`--subsection_len`에 넣습니다. `max_tokens` 하드 컷은 쓰지 않습니다. 생성 도중 잘려
인용이 깨지고 무결성 검사가 무너집니다.

```
총 분량 = section_num × subsection_num × (subsection_len × 모델 계수)
```

### 4.4 가드레일 — 하드 컷이 아니라 구간

주제가 넓으면 서베이는 정당하게 길어집니다. 목표를 강제하지 않고 **구간을 벗어나면
경고**만 띄웁니다(`scripts/check_survey.py --length`). 판단은 사람이 합니다.

실측 근거(2026-08-05):

| 자료 | 단어 | 참고문헌 |
|---|---|---|
| AutoSurvey 원저자 예시 3편 (`examples/`) | 8,558~13,894 | **74~88** |
| SurveyForge 저자 산출물 29편 | 13,242~32,938 (20~39페이지) | — |
| 인간 작성 서베이 10편 (SurveyBench) | — | **173~345** |

**페이지 환산은 우리 템플릿 실측 457단어/쪽을 씁니다** (2026-08-18, 8편 전부 pdflatex
컴파일해 `pdfinfo` 로 셈. 427~504 범위). 예전에 적어 둔 800단어/쪽은 SurveyForge 저자
PDF 기준이라 우리 `md_to_tex.py` 산출물(11pt, 1in 여백, 단일 단, 목차·참고문헌 포함)에는
**1.75배 어긋납니다.**

| 구간 | 단어 | 페이지 | 판정 |
|---|---|---|---|
| 짧음 | < 12,000 | < 26p | 경고 |
| **표준** | 12,000~25,000 | 26~55p | ok |
| **광범위** | 25,000~50,000 | 55~109p | ok — 주제가 넓으면 정당 |
| 초과 | 50,000~80,000 | 109~175p | 경고 |
| **비대** | > 80,000 | > 175p | **경고 — 서베이가 아니다** |

<sub>페이지에는 목차와 참고문헌이 포함됩니다. 참고문헌이 476편이면 그것만으로 10쪽이
넘으므로, 페이지 수는 본문 분량보다 항상 큽니다. 판정 기준은 **단어 수**입니다.</sub>

**참고문헌 수는 분량과 독립된 신호입니다.** 인간 서베이가 173~345편인데 우리 haiku는
368~383편으로 이미 상한을 넘었고 deepseek-v4-pro는 644편입니다. 644편을 인용한 문서는
읽은 게 아니라 나열한 것입니다. **refs 400 초과면 경고.**

현 산출물 판정: haiku 3편 30.4k~32.2k(광범위, ok, 실측 71~74p) /
v4-flash 본편 49,002(광범위 상단, 실측 **111p**) /
deepseek-v4-pro **92,707단어 = 실측 184p (비대, 경고)**.

### 4.5 다음 백본

`deepseek/deepseek-v4-flash-0731`, 엔드포인트 **`parasail/fp8` 고정** — 입력 $0.14/M ·
출력 $0.28/M로 `v4-pro`의 **1/3.1**,
컨텍스트 1M, 날짜 고정 태그라 제공자 갱신에 흔들리지 않습니다.

**계수 실측 완료 (2026-08-05): 1.76×** — 두 실행에서 1.73 / 1.79. 실행 기록은 §2.

**예측식에 섹션 초과를 넣어야 맞습니다.** `--section_num`이 지켜지지 않고 두 실행 모두
**0.88~1.5배**로 흔들립니다 — 초과도 하고 미달도 합니다:

| 실행 | 지시 | 실제 | 배율 |
|---|---|---|---|
| v4-flash 스모크 | 4 | 5 | 1.25× |
| 본편 A (RAG, 배포본) | 8 | 10 | 1.25× |
| 본편 B (RAG, 최신화본) | 8 | 11 | 1.38× |
| 본편 B (3DGS, 최신화본) | 8 | **12** | **1.50×** |

```
총 분량 = section_num × (0.9~1.5) × subsection_num × (subsection_len × 1.8)
```

검산: 실제 섹션 수를 알면 잘 맞습니다 —
`10 × 3.9 × 1,232` = 48,000 ≈ 실측 **49,002** (본편 A),
`12 × 4.0 × 1,250` = 60,000 ≈ 실측 **59,980** (3DGS).
**초과 배율 자체는 예측이 안 되므로 상한을 잡으려면 1.5배로 보수적으로 잡으세요.**

| 설정 | 예상 분량 | 판정 |
|---|---|---|
| 통제 없음 | ~91,000 (~199p) | **비대** |
| `--subsection_num 4` — 길이 700 | **49,002 (실측 111p)** | 광범위 |
| `--subsection_num 3` | ~37,000 (~81p) | 광범위 |
| **`--section_num 6 --subsection_num 3`** | **~27,700 (~61p)** | 표준 |
| `--subsection_num 4 --subsection_len 350` | ~24,000 (~53p) | 표준 |

**개수를 먼저 줄이세요.** `--subsection_num`은 아웃라인 단계에서 주제를 병합·탈락시키므로
남은 서브섹션의 밀도는 그대로입니다. `--subsection_len`을 내리면 **모든** 서브섹션이
얕아집니다. 서브섹션당 1,256단어는 SurveyForge(627)·haiku(535)에 비해 이미 넉넉합니다.

> **`--subsection_num`만으로는 부족합니다.** 상한은 지켜지지만(10개 섹션 전부 4개 이하)
> 섹션이 8→10으로 늘어 총 서브섹션이 37→39로 오히려 늘었습니다. 25,000단어대를 노린다면
> **`--section_num`을 함께 낮추세요.**

**엔드포인트를 고정합니다** — `.env`에 `AUTOSURVEY_PROVIDER=parasail/fp8`.
OpenRouter는 같은 모델을 19개 provider로 라우팅하는데 quantization이 fp4/fp8/unknown으로
제각각입니다. 고정하지 않으면 **한 서베이 안에서 서브섹션마다 다른 정밀도가 씁니다.**
`allow_fallbacks=false`가 함께 나가 그 provider가 붐벼도 넘어가지 않습니다.

출력 한도 자체는 병목이 아닙니다 — 호출당 서브섹션 하나(약 1,600토큰)이고 최소 provider
한도가 32,768이라 20배 여유입니다. 다만 `finish_reason='length'`를 검사해 **잘림이
조용히 넘어가지 않도록** 했습니다(`src/model.py`).

시스템 간 비교를 위한 통제 요인 전체는 상위 디렉터리 `SURVEY_REPORT.md` §7에 있습니다.

---

## 5. 스크립트

이 포크에서 추가한 도구입니다. 실행 방법은 `HANDOFF.md`와 `REPRODUCTION.md` §7.

**DB 준비용**

| 스크립트 | 용도 |
|---|---|
| `scripts/check_db.py` | DB 검증 — 파일 존재 / TinyDB 스키마 / FAISS·매핑 크기 정합 / 실검색 |
| `scripts/harvest_arxiv.py` | arXiv OAI-PMH 수집. **§3의 최신화 작업에서 주력으로 쓰게 됩니다** |
| `scripts/build_index.py` | `build_database.ipynb` 대체 (노트북은 `index_gpu_to_cpu` 에러로 실행 불가) |
| `scripts/check_oai_schema.py` | 수집 결과가 배포 DB와 **같은 표기인지** 문자 단위 대조. 수집 전에 돌릴 것 |
| `scripts/append_snapshot.py` | 기존 스냅샷을 **읽기만 하고** 신규 논문을 더한 새 스냅샷 생성 |

**산출물 처리용**

| 스크립트 | 용도 |
|---|---|
| `scripts/check_survey.py` | 생성 결과 무결성 — 댕글링 인용 / json 매핑 / 포맷 누출. `--subsection-len=N --target-words=W`로 **분량 계수 캘리브레이션** |
| `scripts/enrich_references.py` | `.json`에 arXiv 서지정보 채우기 (새 실행은 `main.py`가 자동 처리) |
| `scripts/md_to_tex.py` | `.md` → `.tex` (Overleaf 업로드 / 서버 로컬 컴파일 둘 다 가능 — 아래) |
| `scripts/collect_run.py` (2026-08-31) | 실행 로그+산출물 → 편당 `<topic>.run.json` 매니페스트(단계별 토큰·비용·재시도, 구조, DB manifest sha, 계수, 소요시간). `--table`로 전 산출물 집계 표. **로그가 살아있을 때(생성 직후) 바로 만들 것** — 로그는 휘발성이다 |

**분석용**

| 스크립트 | 용도 |
|---|---|
| `scripts/compare_snapshots.py` | 두 스냅샷의 토픽 커버리지 비교 (`d@1` / `d@K` / 감쇠 / 교집합) |
| `scripts/to_surveybench_ref.py` | SurveyBench 인용 커버리지 채점 — **LLM 호출 0회**. `ref.json` 변환 + 채점 + 분모에서 빠진 인용 보고 |

---

## 6. 빠른 시작

전제: conda 환경 `autosurvey`, DB 반입 완료, `.env` 작성 완료.
**환경 구축부터 필요하면 `REPRODUCTION.md` §2, §8을 따르세요.**

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

python scripts/check_survey.py "output/v4-flash/Explainability for LLMs.md" --length
```

> `--api_key`는 일부러 넘기지 않습니다. 이 서버는 `/proc`에 hidepid가 없어 다른 사용자가
> `ps`로 명령줄을 읽을 수 있습니다. 키는 `.env`의 환경변수로 전달됩니다.

### PDF로 뽑기 — 이 서버에서 됩니다

Overleaf에 올리지 않아도 됩니다. **시스템에 MiKTeX 25.4가 깔려 있습니다**
(`/usr/local/bin/pdflatex`).

```bash
python scripts/md_to_tex.py "output/deepseek-v4-flash/<토픽>.md"

# 목차와 인용을 해결하려면 3회 돌려야 합니다 (aux 파일이 두 번 갱신됨)
cd /tmp/build && cp "output/deepseek-v4-flash/<토픽>.tex" survey.tex
for i in 1 2 3; do /usr/local/bin/pdflatex -interaction=nonstopmode survey.tex; done
```

> ⚠ **conda 의 `tex` 환경(`~/miniforge3/envs/tex/bin/pdflatex`)은 쓰지 마세요.**
> 포맷 파일(`pdflatex.fmt`)이 없고 `mktexfmt` 가 깨져 있어 즉시 실패합니다.
> `pandoc` 은 그 환경 것을 써도 됩니다 — `md_to_tex.py` 가 필요로 하는 건 pandoc 뿐입니다.

**8편 전부 에러 0 / 미해결 인용 0 으로 컴파일됩니다** (2026-08-18 실측).
빌드 산출물(`.aux` / `.log` / `.out` / `.toc`)은 `.gitignore` 에 있으니
저장소 안에서 돌려도 되지만, 임시 디렉터리에서 돌리는 쪽이 깔끔합니다.

### 두 인자는 반드시 의식하고 고르세요

**`--model`은 `.env`의 `AUTOSURVEY_PROVIDER`와 짝입니다.** `.env`에는
`parasail/fp8`이 박혀 있는데 이 tag는 `deepseek-v4-flash-0731`에만 있습니다.
`--model anthropic/claude-3-haiku`로 바꾸면(haiku는 `amazon-bedrock` 하나뿐)
`allow_fallbacks=false`라 요청이 전부 실패합니다. `main.py`가 DB 로딩 전에
이 조합을 검사해 중단시키니, 모델을 바꿀 때는 provider도 같이 바꾸거나 비우세요.

**`--db_path`는 스냅샷 선택입니다.** 기본값 `./database`가 아니라 **명시적으로** 주세요.

| 목적 | 경로 |
|---|---|
| 새 실험 — 2026-08까지의 논문이 필요 | `./database_2026-08` — 909,293편 (배포본 + 신규) |
| 기존 6편(`output/`)과 비교 — 검색 결과를 맞춰야 함 | `./database` — 537,665편 (~2024-04-26) |

최신화본이 배포본을 **포함**하므로 둘을 함께 주는 일은 없습니다. 하나만 고르세요.

같은 토픽이라도 스냅샷이 다르면 검색되는 논문이 달라집니다. **DB 최신화의 효과를
재려면 두 경로로 각각 돌려** `scripts/compare_snapshots.py`와 함께 보세요.

**시작 전에 `HANDOFF.md`의 "함정 모음"을 먼저 읽으세요.** `--api_url`에 경로를 빠뜨리거나
동시 요청 수를 올리면 바로 막힙니다.

> `deepseek-v4-flash-0731`의 **분량 계수는 아직 측정 전입니다.** 위 `--subsection_len 700`은
> 논문 설정 그대로일 뿐 이 모델에 맞춘 값이 아닙니다. 첫 실행은 스모크
> (`--section_num 4 --outline_reference_num 200 --rag_num 15`, 약 $0.06)로 계수부터 재고,
> 목표 분량을 그 계수로 나눠 `--subsection_len`에 넣으세요 (§4.3).

---

## 원본 프로젝트

이 저장소는 아래 프로젝트의 포크입니다. 방법론과 코드의 원저작권은 원저자에게 있습니다.

> **AutoSurvey: Large Language Models Can Automatically Write Surveys**
> Yidong Wang, Qi Guo, Wenjin Yao, Hongbo Zhang, Xin Zhang, Zhen Wu, Meishan Zhang,
> Xinyu Dai, Min Zhang, Qingsong Wen, Wei Ye, Shikun Zhang, Yue Zhang
> NeurIPS 2024 — [arXiv:2406.10252](https://arxiv.org/abs/2406.10252) ·
> [AutoSurveys/AutoSurvey](https://github.com/AutoSurveys/AutoSurvey)

![Overview](figs/overview.png)

```bibtex
@inproceedings{2024autosurvey,
  title={AutoSurvey: Large Language Models Can Automatically Write Surveys},
  author={Wang, Yidong and Guo, Qi and Yao, Wenjin and Zhang, Hongbo and Zhang, Xin
          and Wu, Zhen and Zhang, Meishan and Dai, Xinyu and Zhang, Min and Wen, Qingsong
          and Ye, Wei and Zhang, Shikun and Zhang, Yue},
  booktitle={The Thirty-eighth Annual Conference on Neural Information Processing Systems},
  year={2024}
}
```

원본 DB는 저자 배포본(OneDrive)입니다. 전문(full-text)을 포함한 DB는 저자 문의로만
얻을 수 있습니다 — `qguo@smail.nju.edu.cn`.

License: MIT (원본과 동일)
