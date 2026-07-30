# HANDOFF — AutoSurvey 세팅 인수인계

**최종 갱신**: 2026-07-30
**목표**: 논문(초록 DB)을 토대로 **survey 문서가 실제로 생성되는 것까지**. 논문 수치 재현과 평가 파이프라인은 범위 밖.
**상세 배경**: `SETTING.md` (환경·패치·비용 전반), 이 문서는 "지금 어디까지 됐고 다음에 뭘 하면 되는지"만 다룹니다.

---

## git 상태

작업은 `reproduce` 브랜치 커밋 `d59c213`에 있습니다. **push와 PR 생성은 사용자가 직접 합니다.**
origin은 SSH URL(`git@github.com:brian-223134/AutoSurvey.git`)로 전환돼 있습니다.
(서버 SSH 키에 passphrase가 있어 TTY 없는 도구에서는 push가 불가합니다.)

---

## TL;DR — 지금 바로 할 일

**DB 반입·검증은 완료됐습니다** (537,665편, check_db 통과). 남은 건 API 키뿐입니다.

```bash
# 1) .env 의 OPENROUTER_API_KEY 를 실제 키로 채운다 (에디터로 직접)
#    ⚠️ 값 끝에 개행/공백이 붙지 않도록 주의 (붙어도 코드가 strip 하지만)

# 2) 환경변수로 올리고 스모크 (축소 설정)
conda activate autosurvey
source .env
python main.py \
  --topic "LLMs for education" \
  --saving_path ./output/ --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --section_num 4 --outline_reference_num 200 --rag_num 15
```

`./output/LLMs for education.md`가 만들어지면 목표 달성입니다.

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
| GPU 사용 | **1장만** (`CUDA_VISIBLE_DEVICES=0`) | 임베딩 외엔 GPU를 안 씀. 공용 서버라 나머지는 안 건드림 |
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

### 3. 스크립트 3종 (`scripts/`)

cs.CL 97편 샘플로 **수집 → 인덱스 → 검증 → 검색까지 끝까지 돌려 동작 확인 완료**.

- **`check_db.py`** — 반입할 DB 검증용. **다음 단계에서 바로 씁니다.**
  파일 4개 존재 / TinyDB 스키마 / FAISS·매핑 크기 정합 / 실제 검색. 파일명이 다르면 실제 목록을 출력해줍니다.
- `harvest_arxiv.py` — arXiv OAI-PMH 수집. **OneDrive 반입이 실패할 경우의 폴백.**
  카테고리 단위 setSpec(`cs:cs:CL` 등) 지원, 페이지당 1300건, 503/Retry-After 처리, 중단 후 재개.
- `build_index.py` — `build_database.ipynb` 대체 (노트북은 `index_gpu_to_cpu` 에러 + 출력 파일명 불일치로 그대로 안 돎).

### 4. 기타

- `.gitignore` 신규 — 원본에 커밋돼 있던 `.pyc` 15개 추적 해제
- `requirements-server.txt` 신규 (원본 `requirements.txt`는 `faiss_gpu`/`torch 2.1.0`/langchain 때문에 이 서버에서 설치 불가)
- `SETTING.md` 갱신 — 초판의 "L40 48GB × 2"는 오기, 실측은 **L40S 46GB × 8**

---

## 남은 작업

### A. ~~DB 반입 및 검증~~ ✅ 완료

OneDrive zip을 scp로 반입해 `./database/`에 풀었고 `check_db.py` **통과**:

| 항목 | 결과 |
|---|---|
| 논문 수 | **537,665편** |
| FAISS | title/abs 각 537,665벡터, dim 768 |
| id 매핑 | 537,665개, TinyDB와 **100% 일치** (유실 0건) |
| 검색 스모크 | `"large language models"` → 관련 논문 5건 정상 |

arXiv id에 버전 접미사가 붙어 있고(`1811.06122v1`) 스냅샷은 **2024-05** 기준입니다.
`scripts/harvest_arxiv.py`는 버전 없는 id를 쓰므로 두 DB를 섞지 마세요.

### B. 스모크 실행 ← **여기부터**

TL;DR의 3번. 확인할 것:
1. 시작 직후 `hello` 응답 — 실패하면 `[APIModel]` 로그와 함께 그 자리에서 죽습니다
2. `./output/{topic}.md`에 `#` 제목 / `##` 섹션 / `###` 서브섹션 / `## References`가 다 있는지
3. 본문의 `[n]` 번호가 References 항목과 대응하는지

### C. 본 실행 — 확정된 3개 토픽

`--section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200` (논문 설정)

토픽은 **DB에서 직접 커버리지를 측정해** 골랐다 (top-1200 검색 후 거리 분포 비교).
`d@1200`이 낮을수록 1200번째까지 관련성이 유지된다는 뜻이고, 감쇠(`d@1200 − d@1`)가
작을수록 관련 논문층이 두텁다.

| 토픽 | d@1200 | 감쇠 | 2023+ | 선정 이유 |
|---|---|---|---|---|
| **In-context Learning** | 0.853 | 0.382 | 48% | `examples/In-context Learning.md`에 **저자들의 생성 결과**가 있어 직접 대조 가능. 논문 Table 6 중 인간 서베이 인용수 최고(323) |
| **Large Multi-Modal Language Models** | **0.744** | **0.238** | 88% | 측정한 24개 중 커버리지 1위 |
| **Evaluation of LLMs** | 0.849 | 0.254 | 96% | 안정적 커버리지 + 최신성 최고. 인간 서베이 183 인용 |

- In-context Learning은 감쇠가 커서 `--outline_reference_num`을 **800 정도로 낮추는 걸 고려**
- 피할 토픽: Parameter-Efficient Fine-Tuning(0.958), Chain of Thought(0.942),
  Hallucination in LLMs(0.940), LLMs for Recommendation(0.946).
  d@1은 괜찮지만 1200편을 채우면 뒤쪽이 노이즈다
- DB 스냅샷이 **2024-05**라 그 이후 부상한 주제는 논문이 거의 없다

### D-2. 출력 형식과 PDF 변환 (출력이 나온 뒤 진행)

목적: **품질 체크용 PDF + 원문 둘 다** 필요.

현재 출력은 **Markdown**이다. LaTeX 기능은 없다.

| 항목 | 현재 |
|---|---|
| `{topic}.md` | `#`/`##`/`###` 헤딩, 인용은 본문에 `[1; 2]` **평문** |
| `{topic}.json` | `{"survey": 본문, "reference": {번호 → arXiv id}}` |
| 참고문헌 | `[n] 논문 제목` — **제목만**. 저자·연도·venue 없음 |
| `.bib` | 없음 |

변환 시 유의:
- DB에 **저자 필드가 없다** (`id`/`title`/`abs`/`date`뿐). 제대로 된 `.bib`을 만들려면
  인용된 논문(서베이당 74~90편)의 저자를 arXiv **OAI-PMH `GetRecord`** 로 따로 받아야 한다
  (이 서버에서 arXiv REST API는 타임아웃, OAI-PMH는 정상)
- 시스템 MiKTeX는 `pdflatex.fmt` 포맷 빌드에 실패해 **쓸 수 없다** (admin 권한 필요).
  대신 conda 환경 **`tex`** 에 pandoc + texlive-core를 설치해 뒀다 → `conda activate tex`
- pandoc으로 바로 PDF를 뽑으면 인용이 `[1]` 평문으로 남는다. 읽기용으로는 충분하고,
  `\cite{}` + `.bib`이 필요하면 `.json`의 reference 매핑을 쓰는 변환기를 별도로 만든다

### D. (추후) writer 모델을 open model로 교체

교수님 의견: closed model(Claude-3-Haiku)보다 **비슷한 성능의 open model API**를 쓰는 편이 좋겠다.
후보는 **GLM-4.6** (OpenRouter 슬러그 확인 필요, `z-ai/glm-4.6` 추정).
일단 Haiku로 파이프라인을 확인한 뒤 교체한다.

**코드 수정은 불필요** — OpenRouter가 OpenAI 호환이라 `--model` 값만 바꾸면 된다.
교체 시 확인할 것:

1. **reasoning(thinking) 모드** — 켜져 있으면 출력 토큰이 몇 배가 되어 비용·시간이 늘고,
   최악의 경우 thinking 내용이 본문에 섞인다. `src/model.py`는 `reasoning` 파라미터를
   보내지 않으므로 OpenRouter 기본값을 따른다. 문제가 보이면 페이로드에
   `"reasoning": {"enabled": false}`를 추가한다
2. **출력 포맷 준수** — 프롬프트가 Haiku에 맞춰 튜닝돼 있고 파서가 문자열 매칭이라 취약하다.
   `extract_title_sections_descriptions`는 `split('Title: ')[1]`이라 서두 한 줄만 붙어도
   IndexError로 즉사한다. 아래 "함정 모음" 참고
3. 논문 Table 4가 writer를 GPT-4 / Gemini-1.5-Pro로 바꾼 ablation을 이미 다루므로,
   writer 교체 자체는 방법론을 벗어나지 않는다 (세 모델 모두 4.58~4.70)

---

## 함정 모음

- **`--api_url`은 끝에 `/chat/completions`까지** 붙여야 합니다. `src/model.py`가 경로를 덧붙이지 않고 그대로 씁니다
- **`--model`은 OpenRouter의 `provider/model` 형식** (`anthropic/claude-3-haiku`)
- **컨텍스트 32k 이상 모델**을 고르세요. `main.py`가 `chunk_size=30000`으로 아웃라인 청크를 만듭니다
- **동시 요청이 `section_num × AUTOSURVEY_MAX_THREADS`** 입니다. 기본값이면 8×15=120개가 한꺼번에 나가 429를 맞습니다. 낮게 잡고 시작하세요
- **`main.py --gpu` 인자는 아무 데서도 안 쓰입니다** (파싱만 하고 버림). `CUDA_VISIBLE_DEVICES`를 쓰세요
- **`evaluation.py`를 돌릴 거면 `judge.py`부터 고치세요.** 인용 문장 하나당 스레드 하나를 **제한 없이** 띄웁니다 (`judge.py:198-220`). 32k 서베이면 수백 개가 동시에 나갑니다
- `database.py`의 `get_paper_from_ids()`(전문 로딩)는 **코드 어디에서도 호출되지 않습니다.** 공개 DB는 초록만 있고, 논문은 본문 앞 1500토큰을 씁니다 — 이게 논문과의 가장 큰 갭입니다 (`SETTING.md` §8)

---

## 서버 환경 메모

- **L40S 46GB × 8**, CUDA 12.4 / 드라이버 550.120, RAM 1TB, `/data2` 여유 2.8TB. **공용 서버**
- 네트워크: OneDrive **차단** (`1drv.ms` SSL 오류, `onedrive.live.com` 403) / `export.arxiv.org` OAI-PMH 가능 / HuggingFace 가능 / `export.arxiv.org/api/query`(REST)는 타임아웃
- 시스템 python3에는 pip이 없습니다. 패키지는 conda env에 설치하세요
