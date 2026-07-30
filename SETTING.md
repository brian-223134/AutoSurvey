# AutoSurvey 연구실 서버 세팅 가이드

**대상 환경**: Linux 서버 + NVIDIA **L40S 46GB × 8** (Ada, `sm_89`), CUDA 12.4 / 드라이버 550.120, RAM 1TB

> **2026-07-30 갱신.** 초판은 환경을 "L40 48GB × 2"로 적었으나 실측은 **L40S 46GB × 8**입니다.
> 아래는 실제로 세팅을 마친 뒤의 상태를 반영한 문서입니다. 주요 변경:
> - **§3, §4 패치는 전부 적용 완료** (+ 초판에 없던 버그 1건 추가 발견·수정 → §3-4)
> - **LLM은 OpenRouter** 사용으로 확정. vLLM 로컬 서빙은 하지 않습니다 (§6)
> - **OneDrive 차단 확인** → DB는 로컬 PC에서 받아 scp 반입 (§5)
> - 실행 환경은 venv가 아니라 **conda `autosurvey`** (§2)
> - 검증/구축 스크립트 3종 추가 (`scripts/`)

이 문서는 [AutoSurvey (NeurIPS 2024)](https://arxiv.org/abs/2406.10252) 원본 저장소를 실제로 돌아가게 만드는 데 필요한 모든 단계를 담고 있습니다. 원본 코드는 그대로는 실행되지 않습니다 (§3).

---

## 0. 요약 — 무엇이 GPU를 쓰고 무엇이 안 쓰는가

먼저 이걸 짚고 가야 세팅 방향이 잡힙니다. AutoSurvey에서 GPU가 실제로 필요한 곳은 생각보다 적습니다.

| 구성 요소 | 어디서 도는가 | GPU 필요? |
|---|---|---|
| LLM (아웃라인/본문/인용검증/리파인) | **외부 HTTP API 호출** (`src/model.py`) | X — OpenRouter 사용 |
| 임베딩 (nomic-embed-text-v1) | 로컬 `SentenceTransformer` | **O** (단, 137M이라 1장으로 충분) |
| FAISS 검색 | **CPU** | X — 아래 설명 참고 |
| TinyDB 메타데이터 조회 | CPU (단일 스레드) | X |

→ **결론: 이 프로젝트에서 GPU는 임베딩 1장(`CUDA_VISIBLE_DEVICES=0`)이면 충분합니다.** 공용 서버이므로 나머지 7장은 건드리지 않습니다.

**FAISS는 GPU를 쓰지 않습니다.** `requirements.txt`에 `faiss_gpu`가 박혀 있어 오해하기 쉬운데, `src/database.py:26-28`은 `faiss.read_index()`로 인덱스를 읽은 뒤 그대로 `.search()`를 호출할 뿐, `index_cpu_to_gpu()`를 **어디서도 호출하지 않습니다**. 즉 원본 코드도 인덱스는 CPU에서 돌립니다. 게다가 인덱스가 `IndexFlatL2`(완전탐색)이고 전체 실행에서 발생하는 쿼리가 수백 건 수준이라, GPU로 올려도 체감 이득이 없습니다.

→ **`faiss-gpu` 설치를 시도하지 마세요.** pip의 `faiss-gpu`는 1.7.2에서 멈춘 CUDA 11 시절 패키지라 Ada(sm_89)에서 설치 지옥에 빠집니다. `faiss-cpu`로 가면 됩니다.

---

## 1. 사전 확인

```bash
nvidia-smi                                  # 드라이버 / GPU 2장 인식 / 여유 VRAM 확인
nvcc --version 2>/dev/null || echo "no nvcc (문제 없음, torch 휠에 런타임 포함)"
python3 --version
df -h ~                                     # DB 빌드 시 최소 20GB, 전체 DB 시 여유 있게
free -g                                     # TinyDB가 메모리를 많이 먹습니다 (§4)
```

체크 포인트:
- 드라이버가 **CUDA 12.1 이상**을 지원해야 합니다 (`nvidia-smi` 우상단 CUDA Version). L40은 sm_89라 CUDA 11.8 미만에서는 동작하지 않습니다.
- GPU 2장이 **다른 사람과 공유**인지 확인하세요. 로컬 LLM 서빙(§6-B)은 VRAM을 통째로 점유합니다.

---

## 2. 환경 구축 ✅ 완료

```bash
conda create -n autosurvey python=3.10 -y
conda activate autosurvey
```

> ⚠️ **`python3.10 -m venv`는 이 서버에서 실패합니다.** `ensurepip`(python3-venv 패키지)이 없어서 venv 생성 중 pip 부트스트랩이 깨집니다. sudo 권한이 없으므로 **miniforge conda를 쓰세요** (`~/miniforge3`에 이미 설치돼 있음). 시스템 python3에는 pip도 없습니다.

`requirements-server.txt` (저장소에 커밋돼 있음):

```txt
# 원본 requirements.txt 대비 변경 사항
#   faiss_gpu==1.7.2    -> faiss-cpu       (§0 참고: 원본 코드도 인덱스를 GPU에 안 올림)
#   torch==2.1.0        -> 2.4.1           (sm_89 안정 지원)
#   numpy==1.23.5       -> 1.26.4          (torch 2.4 호환, numpy<2 유지)
#   transformers 4.35.1 -> 4.44.2          (torch 2.4 호환. 상한 주의 ↓)
#   langchain*          -> 제거            (utils.load_pdf 전용, 실행 경로 미사용)

torch==2.4.1
numpy==1.26.4
transformers==4.44.2
sentence-transformers==2.7.0
einops==0.8.0
faiss-cpu==1.8.0.post1

tinydb==4.8.0
h5py==3.11.0
tiktoken==0.7.0
requests==2.32.3
tqdm==4.66.4
```

```bash
pip install --upgrade pip
pip install -r requirements-server.txt

# GPU 인식 확인
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.device_count())"
```

실측 결과 (2026-07-30):

```
torch 2.4.1+cu121   cuda True   n_gpu 8
faiss 1.8.0   transformers 4.44.2   sentence_transformers 2.7.0   numpy 1.26.4
```

임베딩 모델도 받아서 GPU 로딩까지 확인했습니다 (`nomic-embed-text-v1`, 768-dim). **로컬 설치가 필요한 모델은 이것뿐입니다.**

> ⚠️ **`transformers`를 4.45 이상으로 올리지 마세요.** `nomic-embed-text-v1`은 `trust_remote_code=True` 모델이라 상위 버전에서 원격 코드 로딩이 깨집니다. 그렇다고 다른 임베딩 모델로 교체하면 배포된 FAISS 인덱스(nomic 벡터 공간)가 통째로 무효화되므로 갈아탈 수도 없습니다.

---

## 3. 필수 코드 패치 ✅ 적용 완료

이걸 안 하면 **한 줄도 실행되지 않습니다.** 아래는 이미 저장소에 반영돼 있으니 기록용으로 읽으세요.
초판 작성 이후 **§3-4(참고문헌 aliasing 버그)를 추가로 발견**해 함께 고쳤습니다.

| # | 위치 | 증상 |
|---|---|---|
| 3-1 | `src/utils.py` | ImportError로 즉사 |
| 3-2 | `src/database.py` | CPU 노드에서 실행 불가 |
| 3-3 | `src/model.py` | temperature 미적용 + 에러 은폐 |
| **3-4** | `src/agents/writer.py` | **섹션 2번부터 잘못된 참고문헌으로 본문 작성 (조용히 품질 저하)** |
| 3-5 | `main.py` | 재실행 시 출력 파일 이어붙기 |
| 3-6 | `src/prompt.py` | 치환되지 않는 `[TOPIC]` |

### 3-1. `src/utils.py:10` — 죽은 langchain import 제거 (ImportError 차단)

`load_pdf()`는 실행 경로에서 전혀 쓰이지 않는데, 모듈 최상단 import라 `src.database` → `src.utils` 체인에서 바로 터집니다. langchain 0.2에서 이 경로는 삭제됐습니다.

```diff
- from langchain.document_loaders import PyPDFLoader
```

파일 맨 아래 `load_pdf()` 함수도 같이 지우면 깔끔합니다.

### 3-2. `src/database.py:19` — 디바이스 하드코딩 제거

서버에서는 `cuda`가 맞지만, CPU 노드나 노트북에서 디버깅할 때를 위해 환경변수로 빼두는 걸 권합니다.

```diff
+ import os
+
+ def _resolve_device():
+     name = os.environ.get('AUTOSURVEY_DEVICE', 'auto')
+     if name != 'auto':
+         return torch.device(name)
+     if torch.cuda.is_available():
+         return torch.device('cuda')
+     if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available():
+         return torch.device('mps')
+     return torch.device('cpu')
+
  class database():
      def __init__(self, db_path, embedding_model) -> None:
          self.embedding_model = SentenceTransformer(embedding_model, trust_remote_code=True)
-         self.embedding_model.to(torch.device('cuda'))
+         self.embedding_model.to(_resolve_device())
```

> 참고: `main.py`의 `--gpu` 인자는 **아무 데서도 사용되지 않습니다** (파싱만 하고 버림). GPU 지정은 `CUDA_VISIBLE_DEVICES=0` 환경변수로 하세요.

### 3-3. `src/model.py` — 페이로드 형식 + 에러 처리

두 가지 문제가 있습니다.

**(a) 비표준 페이로드.** `temperature`가 `messages` 배열 **안쪽**에 들어가 있습니다 (`src/model.py:16-19`). OpenAI는 무시하고 넘어가지만 vLLM 등 로컬 서버는 400을 낼 수 있고, 무엇보다 **temperature가 실제로 적용되지 않습니다** — 논문은 `temperature=1`로 실험했는데 지금 코드는 서버 기본값으로 돌고 있는 셈입니다.

**(b) 에러를 전부 삼킴.** `except: pass`로 6회 재시도 후 조용히 `None`을 반환합니다. 그 `None`이 `writer.py:132`의 `c.replace(...)`나 `judge.py:138`의 `res.lower()`에서 `AttributeError`로 터지는데, **원인이 전혀 드러나지 않습니다.** 인증 실패인지 레이트리밋인지 컨텍스트 초과인지 알 수 없어 디버깅이 매우 어렵습니다.

```diff
  def __req(self, text, temperature, max_try = 5):
      url = f"{self.__api_url}"
-     pay_load_dict = {"model": f"{self.model}","messages": [{
-             "role": "user",
-             "temperature":temperature,
-             "content": f"{text}"}]}
+     pay_load_dict = {
+         "model": self.model,
+         "temperature": temperature,
+         "messages": [{"role": "user", "content": text}],
+     }
      payload = json.dumps(pay_load_dict)
      headers = { ... }
-     try:
-         response = requests.request("POST", url, headers=headers, data=payload)
-         return json.loads(response.text)['choices'][0]['message']['content']
-     except:
-         for _ in range(max_try):
-             try:
-                 response = requests.request("POST", url, headers=headers, data=payload)
-                 return json.loads(response.text)['choices'][0]['message']['content']
-             except:
-                 pass
-             time.sleep(0.2)
-         return None
+     last_err = None
+     for attempt in range(max_try):
+         try:
+             r = requests.post(url, headers=headers, data=payload, timeout=300)
+             if r.status_code != 200:
+                 last_err = f"HTTP {r.status_code}: {r.text[:300]}"
+                 # 레이트리밋/과부하는 백오프 후 재시도할 가치가 있음
+                 time.sleep(min(2 ** attempt, 30))
+                 continue
+             return r.json()['choices'][0]['message']['content']
+         except Exception as e:
+             last_err = repr(e)
+             time.sleep(min(2 ** attempt, 30))
+     print(f"[APIModel] 재시도 {max_try}회 실패: {last_err}", flush=True)
+     return None
```

추가로 OpenRouter 대응 두 가지를 넣었습니다:
- OpenRouter는 업스트림 실패를 **HTTP 200 + `{"error": ...}`** 로 돌려줄 때가 있어, `choices` 키가 없으면 본문을 에러로 기록하고 재시도합니다
- 동시 요청 수를 `AUTOSURVEY_MAX_THREADS` 환경변수로 조절할 수 있게 했습니다 (기본 15, §6 참고)

### 3-4. `src/agents/writer.py:30-35` — 참고문헌 aliasing 버그 ⚠️ 초판 미수록

**크래시 없이 서베이 품질만 조용히 망가뜨리던 버그입니다.**

```python
section_content        = [[]] * len(sections)   # n개가 전부 '같은' 리스트 객체
section_paper_texts    = [[]] * len(sections)
section_references_ids = [[]] * len(sections)
```

`[[]] * n`은 빈 리스트 n개가 아니라 **같은 객체를 가리키는 참조 n개**를 만듭니다. 바로 아래에서 `section_references_ids[i].append(...)` / `section_paper_texts[i].append(...)`로 쌓기 때문에, 모든 섹션이 하나의 리스트를 공유하게 됩니다. 결과적으로 **섹션 0을 제외한 모든 섹션이 섹션 0의 참고문헌으로 본문을 씁니다.**

```python
>>> a = [[]] * 3; a[0].append('x'); a
[['x'], ['x'], ['x']]
```

→ 세 줄 모두 `[[] for _ in range(num_sections)]`로 교체했습니다.
(`section_content`는 `res_l[idx] = contents`로 **대입**만 하므로 원래도 무해했지만 일관성을 위해 같이 고쳤습니다.)

### 3-5. `main.py` — 출력 파일 모드와 조기 실패

- `'a+'` → `'w'`: 같은 토픽으로 재실행하면 기존 파일에 이어붙어 `evaluation.py`의 `json.loads()`가 깨집니다
- `chat('hello')`가 `None`이면 그 자리에서 `RuntimeError`를 냅니다. 원래는 한참 뒤 엉뚱한 `AttributeError`로 죽었습니다
- 끝에 토큰 사용량(`input_token_usage` / `output_token_usage`)을 출력합니다

### 3-6. `src/prompt.py` — 치환되지 않는 `[TOPIC]`

`EDIT_FINAL_OUTLINE_PROMPT`에 `[TOPIC]` 자리표시자가 있는데 `outline_writer.edit_final_outline()`이 `OVERALL OUTLINE`만 넘겨서, LLM이 리터럴 문자열 `[TOPIC]`을 그대로 보고 있었습니다. 호출부에 topic을 전달하도록 고쳤습니다.

---

## 4. 성능 패치 ✅ 적용 완료

### 4-1. TinyDB 선형 스캔 제거

`src/database.py:99`의 `get_paper_info_from_ids()`가 `Query().id.one_of(ids)`를 쓰는데, TinyDB는 이걸 **문서 하나마다 리스트 멤버십 검사**로 처리합니다. 530k 논문 × 후보 1500개 = 약 8억 번의 파이썬 레벨 비교이며, **호출 한 번에 10분 이상** 걸릴 수 있습니다. 이런 호출이 실행당 10회 가까이 발생합니다.

`__init__`에서 딕셔너리를 한 번 만들어두면 O(1)이 됩니다:

```diff
  self.User = Query()
  self.token_counter = tokenCounter()
+ # TinyDB의 one_of()는 전체 선형 스캔이라 실사용이 불가능합니다.
+ # 시작 시 1회 메모리 인덱스를 구축해 조회를 O(1)로 만듭니다.
+ self._by_id = {p['id']: p for p in self.table.all()}

  def get_paper_info_from_ids(self, ids):
-     result = self.table.search(self.User.id.one_of(ids))
-     return result
+     return [self._by_id[i] for i in ids if i in self._by_id]
```

> ⚠️ **주의**: 원본 `search()`는 결과 순서를 보장하지 않았고, 호출부(`writer.py:43-44`, `outline_writer.py:29-30`)는 id→title/abs 딕셔너리를 다시 만들어 쓰므로 순서 의존성이 없습니다. 위 패치는 안전합니다.

### 4-2. 평가 스크립트의 무제한 스레드 ❌ 미적용 (`evaluation.py` 실행 시 필수)

**평가는 현재 범위 밖이라 아직 고치지 않았습니다. `evaluation.py`를 돌리기 전에 반드시 먼저 적용하세요.**

`src/agents/judge.py:198-206`과 `:208-220`은 인용 문장 **하나당 스레드 하나**를 제한 없이 띄웁니다. `batch_chat`의 `max_threads` 같은 안전장치가 없어서, 32k 서베이 하나면 **수백 개 요청이 동시에** 나갑니다. OpenRouter 레이트리밋에 그대로 막힙니다.

`threading.Semaphore(15)`로 감싸거나 `concurrent.futures.ThreadPoolExecutor(max_workers=15)`로 바꾸세요.

### 4-3. 토큰 사용량 출력 ✅ 적용 완료 (비용 추적기 본체는 미복구)

`src/utils.py`의 `self.model_price = {}`가 비어 있어서 `compute_price()`는 호출 즉시 `KeyError`가 납니다. 다만 `main.py`가 호출조차 하지 않으므로 무해합니다. 누적값 자체는 정직하게 쌓이고 있어서, `main.py`에 아래 출력을 추가해 뒀습니다:

```
[tokens] outline in=... out=...
[tokens] writer  in=... out=...
```

실제 요금은 OpenRouter 대시보드에서 확인하는 편이 정확합니다.

---

## 5. 데이터베이스 준비

**DB 없이는 어떤 단계도 실행되지 않습니다.** 파이프라인 첫 줄이 `db.get_ids_from_query(topic, ...)`입니다.

필요한 파일 4개 (`--db_path` 디렉터리에 위치):

| 파일 | 용도 | 참조 위치 |
|---|---|---|
| `arxiv_paper_db.json` | TinyDB 본체 (id/title/abs/date) | `database.py:21` |
| `faiss_paper_title_embeddings.bin` | 제목 인덱스 (인용 매핑용) | `database.py:26` |
| `faiss_paper_abs_embeddings.bin` | 초록 인덱스 (검색용) | `database.py:28` |
| `arxivid_to_index_abs.json` | arXiv id ↔ FAISS 인덱스 매핑 | `database.py:32` |

반입 후에는 **반드시 검증부터** 하세요. 파일명이 하나만 달라도 몇 분 뒤 엉뚱한 곳에서 죽습니다:

```bash
conda activate autosurvey
python scripts/check_db.py --db-path ./database
```

파일 4개 존재 / TinyDB 스키마(`cs_paper_info` + id·title·abs·date) / FAISS 인덱스와 id 매핑의 크기 정합 / 실제 검색까지 확인합니다. 파일명이 다르면 디렉터리의 실제 목록을 출력해주니 그걸 보고 rename 하면 됩니다.

### 경로 A: 공식 배포본 (arXiv CS 53만 편 초록) — **채택**

**⚠️ 이 서버에서 OneDrive는 차단돼 있습니다** (실측: `1drv.ms` → SSL wrong version number(투명 프록시 개입), `onedrive.live.com` → 403). 서버에서 직접 다운로드할 수 없습니다.

→ **로컬 PC에서 README의 OneDrive 링크로 zip을 받아 서버로 scp** 한 뒤 `unzip database.zip -d ./database/`.

> 공식 배포본은 `nomic-embed-text-v1` 벡터 공간으로 만들어져 있습니다. **`--embedding_model` 기본값을 바꾸지 마세요.** 바꾸면 인덱스가 통째로 무효가 됩니다.

메모리 요구량 (§4-1 패치 적용 기준):
- FAISS 인덱스 2개: 530k × 768dim × 4B ≈ **1.6GB × 2 = 3.2GB**
- TinyDB + `_by_id` 인덱스: **약 4~6GB**
- 임베딩 모델: 1GB 미만
- **합계 상주 ~10GB** → 이 서버는 RAM 1TB라 여유롭습니다

### 경로 B: 전문(full-text) DB — 논문 재현에 필요

**이게 §8에서 설명할 핵심 갭입니다.** 공개 DB는 초록만 들어 있는데, 논문은 각 논문 본문 **앞 1,500 토큰**을 씁니다. 저자 문의로만 받을 수 있습니다:

> qguo@smail.nju.edu.cn (README 명시)

받으면 `paper_content.h5`로 저장하고, `database.py:104`의 하드코딩된 경로 `'./paper_content.h5'`를 `db_path` 기준으로 고쳐야 합니다.

### 경로 C: 직접 구축 — **폴백. 스크립트 준비 완료**

경로 A가 어그러졌을 때를 위해 `scripts/`에 구축 파이프라인을 만들어 뒀습니다. **cs.CL 97편으로 수집→인덱스→검증→검색까지 실제로 돌려 동작을 확인한 상태**입니다.

```bash
# 1) 메타데이터 수집 (관심 카테고리만)
python scripts/harvest_arxiv.py --sets cs:cs:CL cs:cs:LG --out-dir ./database

# 2) 임베딩 + FAISS 인덱스
CUDA_VISIBLE_DEVICES=0 python scripts/build_index.py --db-path ./database

# 3) 검증
python scripts/check_db.py --db-path ./database
```

`harvest_arxiv.py` 참고 사항:
- arXiv OAI-PMH는 **카테고리 단위 setSpec을 지원**합니다 (`cs:cs:CL`, `cs:cs:LG`, `cs:cs:AI` …). `verb=ListSets`로 전체 목록 확인 가능. 아카이브 전체(`cs`)를 받아 클라이언트에서 거를 필요가 없습니다
- 페이지당 1300건, resumptionToken 페이징. 503 + `Retry-After`(arXiv 레이트리밋 신호)를 존중합니다
- `_harvest/records.jsonl` + `state.json`에 체크포인트를 남겨 **중단 후 같은 명령으로 재개**됩니다
- OAI의 `from`/`until`은 **최종 수정일** 기준입니다. 투고일로 거르려면 `--created-from`을 쓰세요
- `export.arxiv.org/api/query`(REST API)는 이 서버에서 타임아웃납니다. OAI-PMH만 씁니다

`build_index.py`는 `build_database.ipynb`를 대체합니다. 노트북은 그대로 돌지 않습니다:
- 셀 14: `faiss.index_gpu_to_cpu(title_index)` — `title_index`는 CPU `IndexFlatL2`라 이 호출은 **에러**
- 출력 파일명이 `titles.index` / `abstracts.index` / `paperid_to_index.json`으로 `database.py`가 읽는 이름과 **불일치**
- 입력 `arxiv_paper_db.json`이 이미 있다고 가정 — **수집 단계 자체가 없음**

스크립트는 이 셋을 다 고쳤고, id↔index 매핑을 TinyDB 키가 아니라 **리스트상의 위치**로 만들기 때문에 키 번호 체계와 무관하게 항상 FAISS 순서와 맞습니다.

관심 분야만 3~5만 편으로 만들면 이점이 큽니다:
- TinyDB 병목이 사실상 사라지고, FAISS 인덱스가 100MB대로 줄어듭니다
- L40S 1장으로 5만 편 임베딩이 **수 분** 안에 끝납니다 (nomic 137M, batch 256 기준)
- 도메인 한정이라 검색 품질도 더 나을 수 있습니다

> ⚠️ **임베딩 모델 버전 불일치 주의**: 논문 Appendix B는 `nomic-embed-text-v1.5`를 썼다고 적고 있지만, 저장소 기본값은 `nomic-ai/nomic-embed-text-v1`입니다 (`main.py:59`). **인덱스를 만든 모델과 검색에 쓰는 모델이 반드시 같아야 합니다.** 배포 인덱스를 쓸 거면 코드 기본값(v1)을 그대로 두세요. 직접 만들면 아무거나 골라도 되지만 빌드/검색에서 동일하게 유지해야 합니다.

---

## 6. 실행 — OpenRouter

논문의 writer 모델은 **Claude-3-Haiku**(`claude-3-haiku-20240307`)입니다. 평가는 GPT-4 + Claude-3-Haiku + Gemini-1.5-Pro 혼합.

**OpenRouter를 씁니다.** `src/model.py`는 OpenAI 호환 `/v1/chat/completions`를 때리는 게 전부이고 OpenRouter가 그 규격이므로 **코드 수정 없이 그대로 붙습니다.** (Anthropic 네이티브 API `/v1/messages`는 요청·응답 스키마가 달라서 어댑터가 필요했을 텐데, OpenRouter 경유로 그 작업이 사라졌습니다.)

```bash
conda activate autosurvey
export CUDA_VISIBLE_DEVICES=0        # 임베딩용 1장이면 충분
export OPENROUTER_API_KEY=sk-or-v1-...

python main.py \
  --topic "LLMs for education" \
  --saving_path ./output/ \
  --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --api_key "$OPENROUTER_API_KEY" \
  --section_num 8 \
  --subsection_len 700 \
  --rag_num 60 \
  --outline_reference_num 1200
```

- `--api_url`은 **끝에 `/chat/completions`까지** 붙여야 합니다 (`src/model.py`가 경로를 덧붙이지 않고 그대로 씁니다)
- `--model`은 OpenRouter의 `provider/model` 형식입니다 (`anthropic/claude-3-haiku`, `openai/gpt-4o` 등)
- **컨텍스트 32k 이상인 모델**을 고르세요. `main.py`가 `chunk_size=30000`으로 아웃라인 청크를 만듭니다
- 크레딧이 떨어지거나 업스트림이 실패하면 OpenRouter가 **HTTP 200에 `{"error": ...}`** 를 실어 보낼 때가 있습니다. §3-3 패치가 이를 잡아 로그로 노출합니다

> `--section_num 8` / `--outline_reference_num 1200`은 **논문 설정**입니다 (저장소 기본값은 7 / 1500). 재현이 목적이면 논문 값을 쓰세요.

**첫 실행은 반드시 축소 설정으로** 파이프라인이 끝까지 도는지만 확인하세요:

```bash
--section_num 4 --outline_reference_num 200 --rag_num 15
```

`main.py`가 시작하자마자 `chat('hello')`를 던집니다. 실패하면 `[APIModel] 재시도 5회 실패: ...`와 함께 **그 자리에서 RuntimeError**를 냅니다 (원래는 조용히 넘어가 한참 뒤 엉뚱한 `AttributeError`로 죽었습니다).

### 동시성 튜닝 — OpenRouter에서 특히 중요

`src/agents/writer.py`가 섹션당 스레드 1개를 띄우고, 각 스레드가 `batch_chat`(`src/model.py`)을 호출합니다. 즉 **최대 `section_num × max_threads` 개 동시 요청**입니다. 기본값이면 `8 × 15 = 120`개가 한꺼번에 나갑니다 — OpenRouter 레이트리밋에 그대로 걸립니다.

환경변수로 조절하세요 (§3-3에서 추가):

```bash
export AUTOSURVEY_MAX_THREADS=4      # 8섹션 × 4 = 32 동시 요청
```

429가 뜨면 §3-3의 지수 백오프가 재시도하지만, 5회 안에 못 뚫으면 해당 서브섹션이 `None`이 되어 파이프라인이 죽습니다. **넉넉히 낮게 잡고 시작하는 편이 안전합니다.**

---

## 7. 평가 실행

```bash
python evaluation.py \
  --topic "LLMs for education" \
  --saving_path ./output/ \
  --db_path ./database \
  --model <JUDGE_MODEL_ID> \
  --api_url <ENDPOINT> \
  --api_key "$MY_API_KEY"
```

`./output/{topic}.json`이 있어야 합니다 (`main.py`가 생성).

**평가가 생성보다 비쌀 수 있습니다.** `judge.py:167`의 `citation_quality()`는 인용이 달린 문장마다 NLI 판정 1회, 통과한 문장은 **인용 출처 개수만큼 추가 호출**합니다. 32k 서베이 하나에 수백~1000회 이상 나갑니다. §4-2의 스레드 제한을 먼저 적용하세요.

파일 기록 모드는 §3-5에서 `'w'`로 고쳤으므로 재실행 시 이어붙기 문제는 해소됐습니다.

---

## 8. 논문과 코드의 갭 (재현 전 반드시 확인)

공개 저장소는 논문 실험을 **완전히 재현하지 못합니다.** 논문 수치를 인용하거나 비교 실험을 설계할 때 아래를 감안하세요.

| 논문 | 공개 코드 | 영향 |
|---|---|---|
| 논문 본문 앞 **1,500 토큰** 사용 (§3 Setup) | 공개 DB는 **초록만**. `writer.py:44`가 `abs` 필드만 읽음 | 입력 토큰이 대폭 줄어 **비용은 싸지지만**, 인용 품질(recall/precision)이 논문 수치보다 낮게 나올 수 있음 |
| **N = 2** 반복 후 최고 서베이 선택 (Algorithm 1, Phase 4) | `main.py`는 **1회만** 생성. best-of-N 선택 로직 없음 | 논문 Table 2는 2회 중 최선. 단일 실행과 직접 비교 불가 |
| 임베딩 `nomic-embed-text-v1.5` (Appendix B) | 기본값 `nomic-embed-text-v1` | 검색 결과가 달라짐. 인덱스 빌드 모델과 일치가 최우선 |
| 초기 검색 1,200편 / 8섹션 | 기본값 1,500편 / 7섹션 | CLI로 조정 가능 (§6) |
| `temperature = 1` (Appendix B) | 페이로드 위치 오류로 **실제 미적용** | ✅ §3-3 패치로 해결 |
| 섹션별 참고문헌 분리 | `[[]] * n` aliasing으로 **전 섹션이 섹션 0의 참고문헌 공유** | ✅ §3-4 패치로 해결. **패치 전 결과는 논문과 비교 불가** |

`database.py:102`의 `get_paper_from_ids()`(= 전문 로딩 함수)가 **코드 어디에서도 호출되지 않는다**는 점이 위 첫 번째 항목의 직접적인 증거입니다. 전문 DB를 입수하면 `writer.py:44`를 이 함수로 갈아끼워야 논문 설정이 됩니다.

---

## 9. 비용 · 시간 참고

논문 Appendix D, Table 7 (32k 토큰 서베이 1편 기준, **전문 DB + N=2**):

| 입력 토큰 | 출력 토큰 | Claude-haiku | Gemini-1.5-pro | GPT-4 |
|---|---|---|---|---|
| 3,009.7K | 112.9K | **$0.89** | $11.72 | $33.48 |

논문 본문의 "$1.2 / 3분per survey"가 이 표에 근거한 수치입니다.

**공개 DB(초록만)로 돌리면 입력 토큰이 이보다 훨씬 적습니다.** 저장소 기본 설정(1500편/7섹션/rag 60, 초록 230토큰 가정)으로 추정하면 **입력 ~1.5M / 출력 ~100K, 약 105회 호출**입니다.

비용의 85%는 세 지점에 몰려 있습니다:

| 지점 | 위치 | 호출 | 추정 입력 |
|---|---|---|---|
| 러프 아웃라인 (30k 청크 × 12) | `outline_writer.py:112` | ~12 | ~360K |
| 서브섹션 본문 작성 | `writer.py:130` | ~28 | ~480K |
| 인용 검증 (**같은 초록 60편 재전송**) | `writer.py:138` | ~28 | ~430K |

→ 줄이려면 `--outline_reference_num`, `--rag_num`, `--section_num` 이 세 개만 건드리면 됩니다. 첫 스모크(`4 / 200 / 15`)는 이보다 한참 싸게 끝납니다.

실제 요금은 OpenRouter 대시보드에서 확인하세요. 모델별 단가 차이가 위 표처럼 30배 넘게 벌어지므로, **모델 선택이 곧 비용**입니다.

---

## 10. 트러블슈팅

| 증상 | 원인 / 조치 |
|---|---|
| `RuntimeError: API 연결 실패` | `[APIModel]` 로그에 실제 HTTP 상태가 찍힙니다. 401이면 키, 404면 `--api_url` 끝의 `/chat/completions` 누락, 400이면 `--model` id 오타 |
| `[APIModel] ... 응답에 choices 없음` | OpenRouter가 200에 에러를 실어 보낸 경우. 본문에 크레딧 부족/모델 미가용 사유가 있습니다 |
| 429 / rate limit 폭주 | `AUTOSURVEY_MAX_THREADS`를 낮추세요 (§6 동시성 튜닝). 평가까지 돌린다면 §4-2도 |
| `KeyError` (writer의 `temp_title_dic`) | FAISS 인덱스와 TinyDB가 서로 다른 DB에서 왔을 수 있습니다. `scripts/check_db.py`로 확인 |
| 진행이 멈춘 듯 수십 분 정지 | TinyDB 선형 스캔 — §4-1이 적용된 코드인지 확인 (`self._by_id`가 있어야 함) |
| 트랜스포머가 nomic 모델 로딩 실패 | `transformers` 4.45+ 사용 중. 4.44.2로 내리기 (§2) |
| `python3.10 -m venv` 실패 | ensurepip 없음. conda를 쓰세요 (§2) |
| ~~`ImportError: langchain.document_loaders`~~ | ✅ §3-1로 해결됨 |
| ~~`AttributeError: 'NoneType' ... replace`~~ | ✅ §3-3/§3-5로 원인이 노출되고 조기 중단됨 |
| ~~`json.loads` 실패 (evaluation)~~ | ✅ §3-5로 해결됨 |

---

## 부록: 실행 순서 체크리스트

- [x] `nvidia-smi`로 GPU + CUDA 확인 → **L40S × 8, CUDA 12.4**
- [x] conda `autosurvey` 환경 생성, `requirements-server.txt` 설치
- [x] `torch.cuda.is_available()` → `True` (8 GPU)
- [x] §3 패치 적용 (utils / database / model / **writer** / main / prompt)
- [x] §4-1 TinyDB 인덱싱 패치 적용
- [x] `nomic-embed-text-v1` 다운로드 및 GPU 로딩 확인
- [ ] **DB 반입** — 로컬 PC에서 OneDrive zip 받아 scp → `unzip database.zip -d ./database/`
- [ ] `python scripts/check_db.py --db-path ./database` 통과
- [ ] OpenRouter 키 준비, `AUTOSURVEY_MAX_THREADS` 설정
- [ ] 축소 설정(`--section_num 4 --outline_reference_num 200 --rag_num 15`)으로 스모크
- [ ] `./output/{topic}.md` 내용 확인 (제목/섹션/서브섹션/References, 본문 `[n]`↔References 대응)
- [ ] 정상 확인 후 논문 설정(`--section_num 8 --outline_reference_num 1200 --rag_num 60`)으로 본 실행
- [ ] (평가까지 갈 경우) §4-2 스레드 제한 먼저 적용
- [ ] 평가 전 §4-2 스레드 제한 적용
