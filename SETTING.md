# AutoSurvey 연구실 서버 세팅 가이드

**대상 환경**: Linux 서버 + NVIDIA L40 48GB × 2 (Ada, `sm_89`, PCIe / NVLink 없음)

이 문서는 [AutoSurvey (NeurIPS 2024)](https://arxiv.org/abs/2406.10252) 원본 저장소를 실제로 돌아가게 만드는 데 필요한 모든 단계를 담고 있습니다. 원본 코드는 그대로는 실행되지 않으며, **반드시 고쳐야 하는 지점이 3곳** 있습니다 (§3).

---

## 0. 요약 — 무엇이 GPU를 쓰고 무엇이 안 쓰는가

먼저 이걸 짚고 가야 세팅 방향이 잡힙니다. AutoSurvey에서 GPU가 실제로 필요한 곳은 생각보다 적습니다.

| 구성 요소 | 어디서 도는가 | L40 필요? |
|---|---|---|
| LLM (아웃라인/본문/인용검증/리파인) | **외부 HTTP API 호출** (`src/model.py:28`) | 상용 API면 불필요 / **로컬 서빙하면 여기서 씀** |
| 임베딩 (nomic-embed-text-v1) | 로컬 `SentenceTransformer` | O (단, 137M이라 1장으로 충분) |
| FAISS 검색 | **CPU** | X — 아래 설명 참고 |
| TinyDB 메타데이터 조회 | CPU (단일 스레드) | X |

**FAISS는 GPU를 쓰지 않습니다.** `requirements.txt`에 `faiss_gpu`가 박혀 있어 오해하기 쉬운데, `src/database.py:26-28`은 `faiss.read_index()`로 인덱스를 읽은 뒤 그대로 `.search()`를 호출할 뿐, `index_cpu_to_gpu()`를 **어디서도 호출하지 않습니다**. 즉 원본 코드도 인덱스는 CPU에서 돌립니다. 게다가 인덱스가 `IndexFlatL2`(완전탐색)이고 전체 실행에서 발생하는 쿼리가 수백 건 수준이라, GPU로 올려도 체감 이득이 없습니다.

→ **결론: `faiss-gpu` 설치를 시도하지 마세요.** pip의 `faiss-gpu`는 1.7.2에서 멈춘 CUDA 11 시절 패키지라 Ada(sm_89)에서 설치 지옥에 빠집니다. `faiss-cpu`로 가면 됩니다. L40 2장은 **임베딩과 (선택 시) 로컬 LLM 서빙**에 쓰는 게 맞습니다.

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

## 2. 환경 구축

> **중요**: AutoSurvey 환경과 vLLM 환경을 **반드시 분리**하세요. vLLM은 torch 버전을 공격적으로 핀하기 때문에 한 환경에 섞으면 거의 확실히 깨집니다.

```bash
# conda가 있다면
conda create -n autosurvey python=3.10 -y
conda activate autosurvey

# 없다면
python3.10 -m venv ~/venvs/autosurvey
source ~/venvs/autosurvey/bin/activate
```

`requirements-server.txt`를 새로 만듭니다:

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
# 기대: 2.4.1+cu121 True 2
```

> ⚠️ **`transformers`를 4.45 이상으로 올리지 마세요.** `nomic-embed-text-v1`은 `trust_remote_code=True` 모델이라 상위 버전에서 원격 코드 로딩이 깨집니다. 그렇다고 다른 임베딩 모델로 교체하면 배포된 FAISS 인덱스(nomic 벡터 공간)가 통째로 무효화되므로 갈아탈 수도 없습니다.

---

## 3. 필수 코드 패치 (3곳)

이걸 안 하면 **한 줄도 실행되지 않습니다.**

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

---

## 4. 강력 권장 패치 (성능 — 안 하면 몇 시간 날립니다)

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

### 4-2. 평가 스크립트의 무제한 스레드 (`evaluation.py` 실행 시 필수)

`src/agents/judge.py:200-206`과 `:210-218`은 인용 문장 **하나당 스레드 하나**를 제한 없이 띄웁니다. `batch_chat`의 `max_threads=15` 같은 안전장치가 없어서, 32k 서베이 하나면 **수백 개 요청이 동시에** 나갑니다. 상용 API면 레이트리밋에 그대로 막히고, 로컬 vLLM이면 큐가 폭발합니다.

`threading.Semaphore(15)`로 감싸거나 `concurrent.futures.ThreadPoolExecutor(max_workers=15)`로 바꾸세요.

### 4-3. 비용 추적기 복구 (선택)

`src/utils.py:16`의 `self.model_price = {}`가 비어 있어서 `compute_price()`는 호출 즉시 `KeyError`가 납니다. 애초에 `main.py`에서 호출조차 하지 않아 **실행해도 토큰을 얼마 썼는지 안 나옵니다.** 누적값 자체(`input_token_usage`)는 정직하게 쌓이고 있으니, `main.py` 끝에 아래만 추가해도 유용합니다:

```python
print(f"[tokens] outline in={outline_writer.input_token_usage} out={outline_writer.output_token_usage}")
print(f"[tokens] writer  in={subsection_writer.input_token_usage} out={subsection_writer.output_token_usage}")
```

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

### 경로 A: 공식 배포본 (arXiv CS 53만 편 초록)

README의 OneDrive 링크에서 받아 `unzip database.zip -d ./database/`.

> 학내망에서 OneDrive(`1drv.ms`)가 차단된 사례가 있습니다. 서버에서 `curl -I https://1drv.ms` 로 먼저 확인하세요. 막혀 있으면 경로 C로 가면 됩니다.

메모리 요구량 (§4-1 패치 적용 기준):
- FAISS 인덱스 2개: 530k × 768dim × 4B ≈ **1.6GB × 2 = 3.2GB**
- TinyDB + `_by_id` 인덱스: **약 4~6GB**
- 임베딩 모델: 1GB 미만
- **합계 상주 ~10GB** → 서버 RAM 32GB 이상 권장

### 경로 B: 전문(full-text) DB — 논문 재현에 필요

**이게 §8에서 설명할 핵심 갭입니다.** 공개 DB는 초록만 들어 있는데, 논문은 각 논문 본문 **앞 1,500 토큰**을 씁니다. 저자 문의로만 받을 수 있습니다:

> qguo@smail.nju.edu.cn (README 명시)

받으면 `paper_content.h5`로 저장하고, `database.py:104`의 하드코딩된 경로 `'./paper_content.h5'`를 `db_path` 기준으로 고쳐야 합니다.

### 경로 C: 직접 구축 (권장 — 오히려 실용적)

`build_database.ipynb`가 이 용도인데 **그대로는 안 돌아갑니다**:
- 셀 2: `.to(torch.device('cuda'))` — 서버에선 OK
- 셀 14: `faiss.index_gpu_to_cpu(title_index)` — `title_index`는 CPU `IndexFlatL2`로 만들어졌으므로 이 호출은 **에러**입니다. `faiss.write_index(title_index, ...)`로 바꾸세요.
- 출력 파일명이 `titles.index` / `abstracts.index` / `paperid_to_index.json`인데 `database.py`가 읽는 이름과 **다릅니다.** 위 표의 이름으로 맞추거나 `database.py`를 고쳐야 합니다.

관심 분야만 3~5만 편으로 만들면 이점이 큽니다:
- TinyDB 병목이 사실상 사라지고, FAISS 인덱스가 100MB대로 줄어듭니다
- L40 1장으로 5만 편 임베딩이 **수 분** 안에 끝납니다 (nomic 137M, batch 256 기준)
- 도메인 한정이라 검색 품질도 더 나을 수 있습니다

메타데이터 수집은 arXiv OAI-PMH(`https://export.arxiv.org/oai2`)가 무난합니다. TinyDB 스키마는 `{"cs_paper_info": {"0": {"id":..., "title":..., "abs":..., "date":...}, ...}}` 형태여야 합니다 (노트북 셀 4 참고).

> ⚠️ **임베딩 모델 버전 불일치 주의**: 논문 Appendix B는 `nomic-embed-text-v1.5`를 썼다고 적고 있지만, 저장소 기본값은 `nomic-ai/nomic-embed-text-v1`입니다 (`main.py:59`). **인덱스를 만든 모델과 검색에 쓰는 모델이 반드시 같아야 합니다.** 배포 인덱스를 쓸 거면 코드 기본값(v1)을 그대로 두세요. 직접 만들면 아무거나 골라도 되지만 빌드/검색에서 동일하게 유지해야 합니다.

---

## 6. 실행

### 경로 A: 상용 API 사용 (재현성 우선)

논문의 writer 모델은 **Claude-3-Haiku**(`claude-3-haiku-20240307`)입니다. 평가는 GPT-4 + Claude-3-Haiku + Gemini-1.5-Pro 혼합.

```bash
export CUDA_VISIBLE_DEVICES=0        # 임베딩용 1장이면 충분

python main.py \
  --topic "LLMs for education" \
  --saving_path ./output/ \
  --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model <MODEL_ID> \
  --api_url <OPENAI_HOSPITABLE_ENDPOINT> \
  --api_key "$MY_API_KEY" \
  --section_num 8 \
  --subsection_len 700 \
  --rag_num 60 \
  --outline_reference_num 1200
```

> `--section_num 8` / `--outline_reference_num 1200`은 **논문 설정**입니다 (저장소 기본값은 7 / 1500). 재현이 목적이면 논문 값을 쓰세요.

**첫 실행은 반드시 축소 설정으로** 파이프라인이 끝까지 도는지만 확인하세요:

```bash
--section_num 4 --outline_reference_num 200 --rag_num 15
```

`main.py:32`에 `print(outline_writer.api_model.chat('hello'))`가 있어서, 여기서 `None`이 찍히면 API 연결이 실패한 것입니다. **`None`이 보이면 즉시 중단하세요** — 그대로 두면 한참 뒤에 엉뚱한 `AttributeError`로 죽습니다.

### 경로 B: L40 2장으로 로컬 LLM 서빙 (비용 0)

`src/model.py`는 OpenAI 호환 `/v1/chat/completions`를 때리는 게 전부라, **vLLM을 띄우면 그대로 붙습니다.** 논문이 쓴 Claude-3-Haiku가 소형·고속 모델이므로, 30B급 로컬 모델이면 성격상 비슷한 체급입니다.

**별도 환경에** vLLM을 설치하세요:

```bash
conda create -n vllm python=3.10 -y && conda activate vllm
pip install vllm
```

```bash
# GPU 2장 모두 사용, 텐서 병렬
CUDA_VISIBLE_DEVICES=0,1 vllm serve <MODEL_ID> \
  --tensor-parallel-size 2 \
  --max-model-len 40960 \
  --gpu-memory-utilization 0.90 \
  --port 8000
```

핵심 제약 세 가지:

1. **`--max-model-len`은 32k 이상이어야 합니다.** `main.py:33`이 `chunk_size=30000`으로 아웃라인 청크를 만듭니다. 이보다 짧으면 요청이 거부되거나 잘립니다. 여유를 둬서 40k를 권합니다.
2. **L40은 NVLink가 없습니다.** TP=2 통신이 PCIe를 타므로 단일 요청 지연은 다소 늘지만, AutoSurvey는 최대 105개 요청을 동시에 던지는 워크로드라 vLLM의 continuous batching이 이를 충분히 상쇄합니다. **처리량 관점에서는 오히려 유리한 구조입니다.**
3. **VRAM 96GB 배분** — bf16 32B급(가중치 ~64GB)이면 KV 캐시가 빠듯합니다. 4bit 양자화 70B급(~40GB)이 컨텍스트 여유 면에서 더 안전합니다.

AutoSurvey 쪽 실행:

```bash
python main.py \
  --topic "..." \
  --model <MODEL_ID> \
  --api_url http://localhost:8000/v1/chat/completions \
  --api_key dummy \
  ... (나머지 동일)
```

> §3-3 패치를 **반드시 먼저** 적용하세요. 원본의 페이로드 형식은 vLLM에서 거부될 수 있고, 거부되면 `None`이 조용히 흘러 들어갑니다.

### 동시성 튜닝

`src/agents/writer.py:60`이 섹션당 스레드 1개를 띄우고, 각 스레드가 `batch_chat`(`model.py:51`, `max_threads=15`)을 호출합니다. 즉 **최대 `section_num × 15 = 120`개 동시 요청**입니다. 상용 API면 레이트리밋에 걸리므로 `max_threads`를 낮추고, 로컬 vLLM이면 그대로 두거나 오히려 올려도 됩니다.

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

또한 `main.py`에 파일 기록이 `'a+'` 모드입니다 (`main.py:76`, `:78`). **같은 토픽으로 재실행하면 기존 파일에 이어붙습니다.** 그러면 `evaluation.py`의 `json.loads()`가 깨집니다. 재실행 전에 출력 파일을 지우세요.

---

## 8. 논문과 코드의 갭 (재현 전 반드시 확인)

공개 저장소는 논문 실험을 **완전히 재현하지 못합니다.** 논문 수치를 인용하거나 비교 실험을 설계할 때 아래를 감안하세요.

| 논문 | 공개 코드 | 영향 |
|---|---|---|
| 논문 본문 앞 **1,500 토큰** 사용 (§3 Setup) | 공개 DB는 **초록만**. `writer.py:44`가 `abs` 필드만 읽음 | 입력 토큰이 대폭 줄어 **비용은 싸지지만**, 인용 품질(recall/precision)이 논문 수치보다 낮게 나올 수 있음 |
| **N = 2** 반복 후 최고 서베이 선택 (Algorithm 1, Phase 4) | `main.py`는 **1회만** 생성. best-of-N 선택 로직 없음 | 논문 Table 2는 2회 중 최선. 단일 실행과 직접 비교 불가 |
| 임베딩 `nomic-embed-text-v1.5` (Appendix B) | 기본값 `nomic-embed-text-v1` (`main.py:59`) | 검색 결과가 달라짐. 인덱스 빌드 모델과 일치가 최우선 |
| 초기 검색 1,200편 / 8섹션 | 기본값 1,500편 / 7섹션 | CLI로 조정 가능 (§6-A) |
| `temperature = 1` (Appendix B) | 페이로드 위치 오류로 **실제 미적용** | §3-3 패치로 해결 |

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

→ 줄이려면 `--outline_reference_num`, `--rag_num`, `--section_num` 이 세 개만 건드리면 됩니다. 로컬 vLLM으로 가면 이 전부가 전기요금으로 치환됩니다.

---

## 10. 트러블슈팅

| 증상 | 원인 / 조치 |
|---|---|
| `ImportError: langchain.document_loaders` | §3-1 미적용 |
| `AssertionError: Torch not compiled with CUDA` 또는 `cuda` 관련 에러 | §3-2 미적용 |
| `main.py` 실행 직후 `None` 출력 | API 연결 실패. §3-3 패치 후 실제 HTTP 상태 확인 |
| `AttributeError: 'NoneType' object has no attribute 'replace'` | LLM 호출이 조용히 실패. §3-3 패치가 원인을 노출시켜 줌 |
| 진행이 멈춘 듯 수십 분 정지 | TinyDB 선형 스캔. §4-1 적용 |
| `KeyError` in `compute_price` | `model_price = {}`. §4-3 참고 (호출하지 않으면 무해) |
| 429 / rate limit 폭주 | §6 동시성 튜닝 + §4-2 |
| `json.loads` 실패 (evaluation) | `'a+'` 이어쓰기. 출력 파일 삭제 후 재실행 (§7) |
| 트랜스포머가 nomic 모델 로딩 실패 | `transformers` 4.45+ 사용 중. 4.44.2로 내리기 (§2) |

---

## 부록: 실행 순서 체크리스트

- [ ] `nvidia-smi`로 L40 2장 + CUDA 12.1+ 확인
- [ ] `autosurvey` 환경 생성, `requirements-server.txt` 설치
- [ ] `torch.cuda.is_available()` → `True` 확인
- [ ] §3 패치 3곳 적용 (utils / database / model)
- [ ] §4-1 TinyDB 인덱싱 패치 적용
- [ ] DB 준비 (경로 A/B/C 중 택1), 파일명 4개 일치 확인
- [ ] 축소 설정(`--section_num 4 --outline_reference_num 200 --rag_num 15`)으로 스모크 테스트
- [ ] `hello` 응답이 `None`이 아닌지 확인
- [ ] 정상 확인 후 논문 설정(`--section_num 8 --outline_reference_num 1200 --rag_num 60`)으로 본 실행
- [ ] 평가 전 §4-2 스레드 제한 적용
