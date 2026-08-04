# HANDOFF — AutoSurvey 세팅 인수인계

**최종 갱신**: 2026-08-04
**목표**: 논문(초록 DB)을 토대로 **survey 문서가 실제로 생성되는 것까지**. 논문 수치 재현과 평가 파이프라인은 범위 밖.
**상세 배경**: `SETTING.md` (환경·패치·비용 전반) / `REPRODUCTION.md` (산출물 재현 정보).
이 문서는 "지금 어디까지 됐고 다음에 뭘 하면 되는지"만 다룹니다.

---

## 현재 상태 — 목표 달성

**서베이 6편 생성 완료** — 본편 4편(haiku 3 + deepseek-v4-pro 1) + 스모크 2편.
파이프라인이 end-to-end로 동작합니다. 아래 표는 본편 4편입니다(스모크 포함 전체 결과는
[`output/README.md`](output/README.md)).

| 서베이 | 모델 | 섹션/서브섹션 | 단어 | 참고문헌 | 인용 | 비용 |
|---|---|---|---|---|---|---|
| In-context Learning | haiku | 9 / 51 | 32,176 | 383 | 465 | $0.78 |
| Large Multi-Modal Language Models | haiku | 8 / 48 | 30,709 | 378 | 467 | $0.75 |
| Evaluation of LLMs | haiku | 8 / 48 | 30,439 | 368 | 425 | $0.75 |
| In-context Learning | deepseek-v4-pro | 14 / 117 | 92,707 | 644 | 884 | $3.39 |

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

**다음 후보** (추가 생성 시): 논문 20개 토픽 중 커버리지 상위 —
Explainability for LLMs (d@1200 0.811) / LLM-Generated Texts Detection (0.823) /
LLMs for Information Retrieval (0.833) / Bias and Fairness in LLMs (0.839).

**남은 일**: PDF 컴파일 확인(`.tex`까지는 나와 있음, 사용자 로컬/Overleaf), `.bib` 생성,
벤치마크 평가. **새 생성은 크레딧 소진으로 막혀 있습니다** (아래 "크레딧" 참고).

---

## ⚠ 지금 백그라운드로 돌고 있는 작업 — DB 최신화

**2026-08-04 시작.** DB에 2024-04-26 이후 논문이 없어서 27개월치를 채우는 중입니다.
설계 근거와 실측값은 [`README.md`](README.md) §3, 절차는 아래 "남은 작업 D".

| 프로세스 | PID | 하는 일 |
|---|---|---|
| 수집 | `384550` | arXiv OAI-PMH 전체 CS, cutoff 이후 |
| 후속 체인 | `974423` | 수집 종료를 기다렸다가 append → 검증까지 자동 실행 |

둘 다 **터미널에서 분리돼 있어 SSH를 닫아도 계속됩니다**(PPID 1 / 자체 세션,
제어 터미널 없음, `KillUserProcesses=no` 확인).

```bash
# 진행 상황
tail -3 /tmp/claude-1024/-data2-chanjoong-survey-agent-AutoSurvey/*/scratchpad/harvest.log
# 후속 단계 로그 (append·검증 결과와 md5 지문이 여기 남습니다)
cat  /tmp/claude-1024/-data2-chanjoong-survey-agent-AutoSurvey/*/scratchpad/chain.log
```

- 결과는 **`./database_2026-08/`** 에 만들어집니다. **기존 `./database/`는 읽기만 하고
  건드리지 않습니다** — 두 스냅샷을 모두 남겨 A/B 비교를 할 수 있게 하려는 것입니다.
- `chain.log`가 `완료.`로 끝나 있으면 4파일이 완성된 것입니다. 그 위에 출력된
  **md5 지문을 `REPRODUCTION.md` §3 표에 한 줄 추가**해 주세요.
- 중간에 죽었다면 같은 명령을 다시 실행하면 `state.json`으로 이어받습니다
  (명령은 "남은 작업 D" 참고).
- **`append_snapshot.py`는 정합성이 어긋나면 아무것도 쓰지 않고 중단합니다.**
  실패로 끝나 있어도 기존 DB는 안전합니다.

---

## git 상태

`reproduce` 브랜치. **push와 PR 생성은 사용자가 직접 합니다.**
origin은 SSH URL(`git@github.com:brian-223134/AutoSurvey.git`)로 전환돼 있습니다.
(서버 SSH 키에 passphrase가 있어 TTY 없는 도구에서는 push가 불가합니다.)

커밋: 서베이 1편당 1커밋 + 인프라/변환 커밋.

---

## 재실행 방법

DB(537,665편)와 `.env`는 준비돼 있습니다. 새 토픽 생성은 이 한 줄입니다.

```bash
conda activate autosurvey
source .env
python main.py \
  --topic "Explainability for LLMs" \
  --saving_path ./output/haiku/ --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200

python scripts/check_survey.py "output/haiku/Explainability for LLMs.md"
```

`--saving_path`는 **모델별 디렉터리**로 주세요. 다른 모델을 쓰면 새 디렉터리를 만들고,
끝나면 `output/README.md` 표에 실행 조건을 한 줄 추가합니다.

축소 스모크가 필요하면 `--section_num 4 --outline_reference_num 200 --rag_num 15`
(약 $0.15, 2분). 결과는 `--saving_path ./output/<모델>-smoke/` 로 분리하세요.

생성 후에는 `.tex` 변환을 돌립니다:
```bash
PATH="$HOME/miniforge3/envs/tex/bin:$PATH" \
  python scripts/md_to_tex.py "output/haiku/Explainability for LLMs.md"
```
`scripts/enrich_references.py`(서지정보 채우기)는 **새 실행에는 필요 없습니다** —
`main.py`가 저장 시점에 `reference_detail`을 만듭니다. 옛 산출물을 손볼 때만 씁니다.

### 크레딧 — ⚠ 현재 키는 소진 상태

```bash
source .env && curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/key        # 이 키의 한도/사용량
```

2026-08-04 실측: **한도 $10 / 사용 $10.035 / 잔여 0**. 새 실행은 들어가지 않습니다.
크레딧 상향이나 새 키 발급이 선행돼야 합니다.

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
| 평가(`evaluation.py`) | **범위 밖** | 돌리려면 `judge.py` 스레드 제한 선행 필요 (아래 참고) |

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

### B. 벤치마크 평가 — 착수 전

범위 밖으로 둔 항목입니다. 돌린다면 `judge.py:202,216`의 **무제한 스레드 생성부터
제한**하세요. 인용 문장 하나당 스레드 하나를 만들어 32k 서베이면 수백 개가 동시에 나갑니다.

### C. writer 모델 추가 교체 (선택)

교수님 의견은 closed model(Claude-3-Haiku)보다 **비슷한 성능의 open model API**를 쓰자는
것이었고, `deepseek/deepseek-v4-pro`로 한 편 생성해 **이미 확인했습니다**.
남은 후보는 **GLM-4.6**(OpenRouter 슬러그 확인 필요, `z-ai/glm-4.6` 추정) — 미시도입니다.

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

**예산이 선행 조건입니다** — 현재 키는 $10 한도를 다 썼습니다(2026-08-04 실측, 잔여 0).
크레딧 상향이나 새 키 없이는 스모크 한 편도 돌지 않습니다.

### D. DB 최신화 — **진행 중** (위 "지금 백그라운드로 돌고 있는 작업" 참고)

DB에 2024-04-26 이후 논문이 없습니다. 실측으로 **신규 350,805편**(기존 53.7만의 +65%)이
비어 있습니다. **LLM API를 쓰지 않으므로 크레딧 소진과 무관하게 진행됩니다.**

설계 근거·실측값·표기 규약은 [`README.md`](README.md) §3에 있습니다. 요지만 적으면:
online search를 생성 루프가 아니라 **수집 단계**에 넣어, 생성 파이프라인은 그대로 둔 채
DB만 갱신합니다. 결정적 검색 / DB 내 인용 / 파이프라인 통제가 보존됩니다.

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

끝나면 새 스냅샷의 md5 지문을 `REPRODUCTION.md` §3 표에 한 줄 추가하세요.

**하지 않기로 한 것** — 기존 논문의 개정본 68,441건은 반영하지 않습니다. 옛 스냅샷의
벡터를 그대로 둬야 두 스냅샷 비교가 성립합니다(`IndexFlatL2` append가 기존 행 번호를
보존하므로 **옛 스냅샷이 새 스냅샷의 prefix**가 됩니다).

새 스냅샷으로 서베이를 생성할 때는 `--db_path ./database_2026-08` 만 바꾸면 됩니다.
같은 토픽을 두 스냅샷에서 각각 돌리면 "DB 최신화의 효과"가 독립 변수 하나가 됩니다.

---

## 함정 모음

- **`--api_url`은 끝에 `/chat/completions`까지** 붙여야 합니다. `src/model.py`가 경로를 덧붙이지 않고 그대로 씁니다
- **`--model`은 OpenRouter의 `provider/model` 형식** (`anthropic/claude-3-haiku`)
- **컨텍스트 32k 이상 모델**을 고르세요. `main.py`가 `chunk_size=30000`으로 아웃라인 청크를 만듭니다
- **동시 요청이 `section_num × AUTOSURVEY_MAX_THREADS`** 입니다. 코드 기본값이면 8×15=120개가 한꺼번에 나가 429를 맞습니다. `.env`에 `AUTOSURVEY_MAX_THREADS=4`로 잡아 뒀습니다 — 올리지 마세요
- **`main.py --gpu` 인자는 아무 데서도 안 쓰입니다** (파싱만 하고 버림). `CUDA_VISIBLE_DEVICES`를 쓰세요
- **GPU 번호를 고정하지 마세요.** `.env`에 `CUDA_VISIBLE_DEVICES=0`이 들어 있지만 공용 서버라 0번이 차 있을 수 있습니다. 실행 전 `nvidia-smi`로 빈 것을 고르세요 (`nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | sort -t, -k2 -n | head -1`)
- **크레딧은 `/api/v1/key`로 확인하세요.** `/api/v1/credits`는 **계정 전체** 잔액이라 이 키에 걸린 $10 상한이 보이지 않습니다. 잔액이 있어 보여도 키가 소진됐으면 실행이 죽습니다
- **`evaluation.py`를 돌릴 거면 `judge.py`부터 고치세요.** 인용 문장 하나당 스레드 하나를 **제한 없이** 띄웁니다 (`judge.py:198-220`). 32k 서베이면 수백 개가 동시에 나갑니다
- `database.py`의 `get_paper_from_ids()`(전문 로딩)는 **코드 어디에서도 호출되지 않습니다.** 공개 DB는 초록만 있고, 논문은 본문 앞 1500토큰을 씁니다 — 이게 논문과의 가장 큰 갭입니다 (`SETTING.md` §8)

---

## 서버 환경 메모

- **L40S 46GB × 8**, CUDA 12.4 / 드라이버 550.120, RAM 1TB, `/data2` 여유 2.8TB. **공용 서버**
- 네트워크: OneDrive **차단** (`1drv.ms` SSL 오류, `onedrive.live.com` 403) / `export.arxiv.org` OAI-PMH 가능 / HuggingFace 가능 / `export.arxiv.org/api/query`(REST)는 타임아웃
- 시스템 python3에는 pip이 없습니다. 패키지는 conda env에 설치하세요
