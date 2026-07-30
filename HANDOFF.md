# HANDOFF — AutoSurvey 세팅 인수인계

**최종 갱신**: 2026-07-30
**목표**: 논문(초록 DB)을 토대로 **survey 문서가 실제로 생성되는 것까지**. 논문 수치 재현과 평가 파이프라인은 범위 밖.
**상세 배경**: `SETTING.md` (환경·패치·비용 전반), 이 문서는 "지금 어디까지 됐고 다음에 뭘 하면 되는지"만 다룹니다.

---

## TL;DR — 지금 바로 할 일

```bash
# 1) DB 반입 (로컬 PC에서 OneDrive zip 받아 scp — 서버는 OneDrive 차단됨)
unzip database.zip -d ./database/

# 2) 검증
conda activate autosurvey
python scripts/check_db.py --db-path ./database

# 3) 스모크 (축소 설정)
export CUDA_VISIBLE_DEVICES=0
export AUTOSURVEY_MAX_THREADS=4
python main.py \
  --topic "LLMs for education" \
  --saving_path ./output/ --db_path ./database \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --api_key "$OPENROUTER_API_KEY" \
  --section_num 4 --outline_reference_num 200 --rag_num 15
```

3번이 `./output/LLMs for education.md`를 만들면 목표 달성입니다.

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

### A. DB 반입 및 검증 ← **여기부터**

로컬 PC에서 README의 OneDrive 링크로 zip을 받아 서버로 scp → `unzip database.zip -d ./database/`

필요한 파일 4개 (이름이 정확히 일치해야 함):

| 파일 | 용도 |
|---|---|
| `arxiv_paper_db.json` | TinyDB 본체 (id/title/abs/date) |
| `faiss_paper_title_embeddings.bin` | 제목 인덱스 (인용 → 논문 매핑용) |
| `faiss_paper_abs_embeddings.bin` | 초록 인덱스 (검색용) |
| `arxivid_to_index_abs.json` | arXiv id ↔ FAISS 인덱스 매핑 |

`python scripts/check_db.py --db-path ./database` 로 확인. 상주 메모리 ~10GB 예상 (RAM 1TB라 여유).

### B. 스모크 실행

TL;DR의 3번. 확인할 것:
1. 시작 직후 `hello` 응답 — 실패하면 `[APIModel]` 로그와 함께 그 자리에서 죽습니다
2. `./output/{topic}.md`에 `#` 제목 / `##` 섹션 / `###` 서브섹션 / `## References`가 다 있는지
3. 본문의 `[n]` 번호가 References 항목과 대응하는지

### C. 본 실행

`--section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200` (논문 설정)

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
