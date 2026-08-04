# REPRODUCTION — 산출물 재현 정보

`output/` 아래 서베이 6편이 **어떤 환경 · 어떤 데이터 · 어떤 코드 · 어떤 입력값**으로
나왔는지를 한곳에 모은 문서입니다. 여기 적힌 것만으로 같은 조건을 다시 만들 수 있어야 합니다.

**최종 갱신**: 2026-08-03 / 브랜치 `reproduce` / HEAD `74f601d`

| 문서 | 역할 |
|---|---|
| **`REPRODUCTION.md`** (이 문서) | 재현에 필요한 입력값 일체 — 환경, DB 지문, 코드, 하이퍼파라미터, 명령 |
| `SETTING.md` | 세팅 **절차**와 각 패치의 근거. 왜 그렇게 했는지가 필요할 때 |
| `HANDOFF.md` | 지금 어디까지 됐고 다음에 뭘 하면 되는지 |
| `output/README.md` | 산출물의 **결과 수치**와 비교 시 주의점 |

---

## 0. ⚠ 무엇이 재현되고 무엇이 재현되지 않는가

**같은 파일이 다시 나오지는 않습니다.** 이 저장소에 비트 단위 재현성은 없습니다. 이유:

1. **`temperature=1`** — 아웃라인 작성(`outline_writer.py:147,184,243`)과 본문 작성
   (`writer.py:133,141,201`)이 전부 `temperature=1`입니다. `src/model.py`에 시드
   파라미터 자체가 없고, OpenRouter 경유 상용 모델이라 시드를 줘도 보장되지 않습니다.
2. **모델 스냅샷** — `anthropic/claude-3-haiku`, `deepseek/deepseek-v4-pro`는 버전 고정
   태그가 아닙니다. 제공자가 뒤에서 갱신하면 결과가 달라집니다.
3. **재시도 경로** — 네트워크 실패나 `JSONDecodeError` 시 최대 5회 재호출합니다
   (`model.py:44`). 재시도 여부에 따라 그 호출의 출력이 바뀝니다.
   실제로 deepseek 본편에서 재시도가 2회 있었습니다.

**반면 검색 단계는 결정적입니다.** FAISS 인덱스 + `nomic-embed-text-v1` 임베딩이라
같은 DB·같은 토픽이면 후보 논문 집합과 순위가 매번 동일합니다.

> 따라서 이 문서의 목적은 *같은 산출물을 복제하는 것*이 아니라
> **같은 조건에서 통계적으로 같은 수준의 결과를 얻는 것**입니다.
> 분량·참고문헌 수는 실행마다 몇 % 흔들립니다.

---

## 1. 하드웨어 · OS

| 항목 | 값 |
|---|---|
| OS | Ubuntu 22.04.5 LTS (Linux 5.15.0) |
| GPU | NVIDIA L40S 46GB × 8 — **실제로는 1장만 사용** (`CUDA_VISIBLE_DEVICES=0`) |
| 드라이버 / CUDA | 550.120 / 12.4 |
| RAM | 1TB (DB 상주 약 10GB라 여유) |

**GPU는 임베딩 인코딩에만 쓰입니다.** 생성은 전부 원격 API라 GPU 성능이 결과에
영향을 주지 않습니다. CPU만 있어도 느릴 뿐 동작합니다.

---

## 2. 소프트웨어

conda 환경 `autosurvey` (`$HOME/miniforge3/envs/autosurvey`), **Python 3.10.20**.

실행 시점 실측 버전입니다(`requirements-server.txt` 핀과 일치):

| 패키지 | 버전 |
|---|---|
| torch | 2.4.1+cu121 |
| transformers | 4.44.2 |
| sentence-transformers | 2.7.0 |
| numpy | 1.26.4 |
| faiss-cpu | 1.8.0 |
| tinydb | 4.8.0 |
| tiktoken | 0.7.0 |
| einops / h5py / requests / tqdm | 0.8.0 / 3.11.0 / 2.32.3 / 4.66.4 |

**원본 `requirements.txt`로는 이 서버에서 돌지 않습니다.** 변경 사유는
`requirements-server.txt` 상단 주석과 `SETTING.md` §2에 있습니다. 특히:

- `transformers`는 **4.45 이상이면 안 됩니다.** nomic 임베딩의 원격 코드 로딩이 깨집니다.
- `faiss_gpu` → `faiss-cpu`. 원본 코드도 인덱스를 GPU에 올리지 않습니다.

```bash
conda create -n autosurvey python=3.10 -y
conda activate autosurvey
pip install -r requirements-server.txt
```

---

## 3. 데이터베이스 — 지문

`--db_path ./database` 에 아래 4개 파일. **md5까지 같아야 같은 데이터입니다.**

| 파일 | 크기 | md5 | 원본 mtime |
|---|---|---|---|
| `arxiv_paper_db.json` | 786,171,607 B | `e1fd7c7d0f271271d68e6c5755337d21` | 2024-05-27 |
| `faiss_paper_abs_embeddings.bin` | 1,651,706,925 B | `e5e43fc05958f3312c1af3f2c5dc7ae7` | 2024-05-27 |
| `faiss_paper_title_embeddings.bin` | 1,651,706,925 B | `96c45f10e346706f76b06ab1dd553444` | 2024-05-27 |
| `arxivid_to_index_abs.json` | 14,906,253 B | `b45b94bb3cba573ffd75a9488ae741a2` | 2024-06-11 |

- **내용**: arXiv CS **537,665편의 초록**. 필드는 7개입니다 —
  `id` / `title` / `abs` / `date` / `cat` / `url` / `authors`.
  `authors`는 **537,665편 전부** 채워져 있습니다(결측 0.000%). venue 정보는 없습니다.
- **수록 논문의 최신 날짜는 `2024-04-26`** 입니다. 위 표의 mtime(2024-05-27)은
  배포 파일이 만들어진 날짜이지 논문 수록 범위가 아닙니다.
- **출처**: 저자 배포본(원본 README의 OneDrive 링크).
  **이 서버에서 OneDrive는 차단돼 있어** 로컬 PC로 받아 `scp`로 반입했습니다.
- **DB는 git에 없습니다** (`.gitignore`). 4GB라 저장소에 넣지 않습니다.
- 반입 후 검증:
  ```bash
  python scripts/check_db.py --db-path ./database
  ```
  파일 존재 / TinyDB 스키마 / FAISS·id매핑 크기 정합 / 실검색까지 확인합니다.

> ⚠ **임베딩 모델을 바꾸면 안 됩니다.** 이 인덱스는 `nomic-ai/nomic-embed-text-v1`
> 벡터 공간으로 만들어져 있습니다. `--embedding_model`을 바꾸면 인덱스가 통째로
> 무효가 되고, 에러 없이 엉뚱한 논문이 검색됩니다.

> ⚠ **논문 수치와 직접 비교할 수 없습니다.** 논문은 각 논문 **본문 앞 1,500 토큰**을
> 쓰는데 이 공개 DB에는 초록만 있습니다. 전문 DB는 저자 문의로만 얻을 수 있습니다
> (`SETTING.md` §5 경로 B, §8).

DB를 직접 구축해야 한다면 `scripts/harvest_arxiv.py` → `scripts/build_index.py`
(폴백 경로, `SETTING.md` §5 경로 C). **단, 그렇게 만든 DB로는 위 산출물이 재현되지 않습니다.**

---

## 4. 코드

- **upstream**: AutoSurvey (NeurIPS 2024). fork 기준 커밋 `5e8f389`
- **이 저장소**: 브랜치 `reproduce`

산출물별로 그 시점의 코드가 다릅니다. 재현하려면 **해당 커밋을 체크아웃**하세요.

| 산출물 | 생성 커밋 | 날짜 |
|---|---|---|
| `haiku-smoke/` | `2497048` | 2026-07-30 |
| `haiku/` In-context Learning | `e188706` | 2026-07-30 |
| `haiku/` Large Multi-Modal Language Models | `7e96cf5` | 2026-07-30 |
| `haiku/` Evaluation of LLMs | `8013657` | 2026-07-30 |
| `deepseek-smoke/` | `8bfbc43` | 2026-07-30 |
| `deepseek-v4-pro/` | `0466486` | 2026-07-30 |

> `5a4ed4a`에서 `output/` 을 모델별 디렉터리로 재배치했습니다. 그 이전 커밋의
> 경로는 `output/{topic}.md`, `output/smoke/` 입니다.

### 원본 대비 패치 — 없으면 실행 자체가 안 됩니다

| 패치 | 위치 | 없으면 |
|---|---|---|
| 죽은 langchain import 제거 | `src/utils.py` | `ImportError`로 즉사 |
| 디바이스 하드코딩 제거 | `src/database.py` | GPU 지정 불가 |
| API 페이로드/에러 처리 | `src/model.py` | `temperature`가 무시됨, 실패 원인이 안 보임 |
| 참고문헌 aliasing 버그 | `src/agents/writer.py` | 인용 번호가 어긋남 |
| 출력 파일 모드 `a+`→`w`, 조기 실패 | `main.py` | 재실행 시 파일이 이어붙어 json이 깨짐 |
| TinyDB 선형 스캔 → `_by_id` 인덱스 | `src/database.py` | 수십 분 정지 |
| 아웃라인 파서 모델 비의존화 | `src/agents/outline_writer.py`, `writer.py` | haiku 외 모델에서 `IndexError` |
| 토큰/비용 계측, 추론 토글 | `src/model.py`, `main.py` | 비용을 알 수 없음 |
| API 키 환경변수화 | `main.py`, `evaluation.py` | 키가 `ps`에 노출 |
| `reference_detail` 저장 | `main.py` | json에 arXiv 서지정보 없음 |

각 패치의 상세 근거는 `SETTING.md` §3·§4. 미적용 항목 하나가 남아 있습니다 —
`judge.py`의 무제한 스레드 생성(§4-2). **`evaluation.py`를 돌리기 전에 반드시 제한**하세요.

---

## 5. 실행 설정

### 5-1. 환경변수 (`.env`)

`.env`는 **커밋되지 않습니다**(`.gitignore`, 권한 600). 값은 아래와 같습니다.

| 변수 | 값 | 의미 |
|---|---|---|
| `OPENROUTER_API_KEY` | *(비밀)* | OpenRouter 키 |
| `AUTOSURVEY_REASONING` | `off` | 추론 토큰 비활성 (deepseek 계열은 기본 ON) |
| `AUTOSURVEY_TIMEOUT` | `900` | 호출 타임아웃(초). 추론 모델은 호출당 1분을 넘김 |
| `AUTOSURVEY_MAX_THREADS` | `4` | 동시 API 호출 수. 높이면 429 폭주 |
| `CUDA_VISIBLE_DEVICES` | `0` | 임베딩에 쓸 GPU |

```bash
source .env      # export 형식으로 작성돼 있음
```

> ⚠ **`--api_key`로 키를 넘기지 마세요.** 이 서버는 `/proc`에 `hidepid`가 없어
> 다른 사용자가 `ps`로 명령줄을 읽을 수 있습니다. `/proc/<pid>/environ`은
> 소유자만 읽을 수 있으므로 환경변수가 안전합니다.

> ⚠ **`deepseek-smoke/`는 `AUTOSURVEY_REASONING` 토글이 생기기 전에 돌았습니다.**
> 즉 추론이 켜진 상태였고, 이것이 그 실행 비용이 토큰 추정의 3.5배로 튄 원인입니다
> (추론 토큰이 출력의 45%). 본편은 추론을 끄고 돌렸습니다.

### 5-2. 하이퍼파라미터 — 산출물별

| 산출물 | `--model` | `section_num` | `subsection_len` | `rag_num` | `outline_reference_num` | 추론 |
|---|---|---|---|---|---|---|
| `haiku-smoke/` | `anthropic/claude-3-haiku` | 4 | 700 *(기본값)* | 15 | 200 | 해당없음 |
| `haiku/` (3편) | `anthropic/claude-3-haiku` | 8 | 700 | 60 | 1200 | 해당없음 |
| `deepseek-smoke/` | `deepseek/deepseek-v4-pro` | 4 | 700 *(기본값)* | 15 | 200 | **ON** |
| `deepseek-v4-pro/` | `deepseek/deepseek-v4-pro` | 8 | 700 | **30** | 1200 | **OFF** |

- `haiku/` 3편은 `--topic`만 다릅니다: `In-context Learning`,
  `Large Multi-Modal Language Models`, `Evaluation of LLMs`.
- 스모크 2편은 `--subsection_len`을 주지 않아 파서 기본값 700이 쓰였습니다.
- `deepseek-v4-pro/`의 `rag_num` 30은 **예산 제약**입니다. 커버리지를 결정하는
  `outline_reference_num`은 논문 설정 1200을 유지했습니다.
- haiku는 추론 모델이 아니라 추론 설정이 결과에 영향을 주지 않습니다.

**모든 실행 공통:**

| 항목 | 값 |
|---|---|
| `--api_url` | `https://openrouter.ai/api/v1/chat/completions` |
| `--embedding_model` | `nomic-ai/nomic-embed-text-v1` |
| `--db_path` | `./database` |

**코드에 고정돼 CLI로 못 바꾸는 값** (재현 시 함께 맞춰야 함):

| 값 | 위치 |
|---|---|
| `temperature=1` (아웃라인·본문) | `outline_writer.py:147,184,243` / `writer.py:133,141,201` |
| 러프 아웃라인 청크 30,000 토큰 | `main.py:36` |
| 재시도 최대 5회 | `model.py:44` |
| `refinement=True` | `main.py:132` — `write_subsection` 기본값 |

### 5-3. 실행 명령 — 실제로 돌린 것

**본편** (논문 설정):

```bash
conda activate autosurvey
source .env
python main.py \
  --topic "In-context Learning" \
  --saving_path ./output/haiku/ \
  --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200
```

`deepseek-v4-pro/`는 위에서 `--model deepseek/deepseek-v4-pro`,
`--rag_num 30`, `--saving_path ./output/deepseek-v4-pro/` 로 바꾼 것입니다.

**스모크** (파이프라인이 끝까지 도는지만 확인 — 품질 비교용 아님):

```bash
source .env
python main.py \
  --topic "In-context Learning" \
  --saving_path ./output/haiku-smoke/ \
  --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --section_num 4 --outline_reference_num 200 --rag_num 15
```

`deepseek-smoke/`는 `--model deepseek/deepseek-v4-pro`,
`--saving_path ./output/deepseek-smoke/` 만 다릅니다.

> `deepseek-smoke/`는 **두 번째 시도 결과**입니다. 첫 시도는 아웃라인 파서가
> `IndexError`로 죽었고(`8bfbc43`), 파서를 고친 뒤 다시 돌렸습니다.

---

## 6. 비용 · 토큰 실측

| 산출물 | 입력 토큰 | 출력 토큰 | 비용 | 소요 |
|---|---|---|---|---|
| `haiku-smoke/` | 341K | 51K | $0.149 | 약 2분 |
| `haiku/` In-context Learning | 2.41M | 142K | $0.78 | 6~8분 |
| `haiku/` Large Multi-Modal LM | 2.32M | 138K | $0.75 | 6~8분 |
| `haiku/` Evaluation of LLMs | 2.29M | 138K | $0.75 | 6~8분 |
| `deepseek-smoke/` | — | — | $1.35 | *(미기록)* |
| `deepseek-v4-pro/` | — | — | $3.39 | *(미기록)* |

- deepseek 편의 토큰 총계는 실행 로그에 남지 않았습니다. 비용 내역만 확인됩니다
  (본편: 아웃라인 $0.55 + 본문 $2.84).
- 비용의 85%는 세 지점에 몰립니다 — 러프 아웃라인 / 본문 작성 / 인용 검증
  (같은 초록 60편 재전송). 줄이려면 `outline_reference_num`, `rag_num`,
  `section_num` 셋만 건드리면 됩니다. `SETTING.md` §9.
- **모델 선택이 곧 비용입니다.** 논문 Table 7 기준 모델 간 30배 이상 벌어집니다.

---

## 7. 후처리 — 산출물이 지금 형태가 된 과정

`main.py`가 만드는 것은 `.md` / `.json` 2개뿐입니다. 나머지는 뒤에 붙인 단계입니다.

```bash
# 1) 무결성 검사 — 댕글링 인용이 있으면 인용 지표가 통째로 틀어진다
python scripts/check_survey.py "output/haiku/In-context Learning.md"

# 2) .json에 arXiv 제목·날짜·링크 채우기 (DB 750MB 로딩, 1~2분. 전체 일괄)
python scripts/enrich_references.py

# 3) .md -> Overleaf용 .tex
export PATH="$HOME/miniforge3/envs/tex/bin:$PATH"        # pandoc 3.10.1
for f in output/*/*.md; do
  $HOME/miniforge3/envs/autosurvey/bin/python scripts/md_to_tex.py "$f"
done
```

- `tex` env에는 python이, `autosurvey` env에는 pandoc이 없어 PATH로 섞어 씁니다.
- `enrich_references.py`는 **`reference` 필드를 건드리지 않습니다.**
  `judge.py`의 `citation_quality()`가 그 구조에 의존하므로 바꾸면 `evaluation.py`가 깨집니다.
  서지정보는 새 필드 `reference_detail`에 들어갑니다.
- 기존 6편은 2번 스크립트로 뒤늦게 채워 넣었지만, `main.py`가 이제 저장 시점에
  같은 필드를 만듭니다(`build_reference_detail`). **새 실행은 2번을 건너뛰어도 됩니다.**
- **서버에서 LaTeX 컴파일은 불가능합니다.** conda `texlive-core`에 매크로 트리가
  없고(`latex.ltx` 부재) `fmtutil`도 깨져 있습니다. Overleaf에서 확인하세요.

---

## 8. 처음부터 재현하는 순서

1. conda 환경 생성 + `requirements-server.txt` 설치 (§2)
2. DB 4파일 반입 → `scripts/check_db.py`로 검증, **md5 대조** (§3)
3. 재현할 산출물의 커밋 체크아웃 (§4 표)
4. `.env` 작성 (§5-1) — 권한 600, 커밋 금지
5. §5-3의 명령 실행
6. `scripts/check_survey.py`로 무결성 확인
7. `output/README.md` 표에 결과 한 줄 추가

**결과가 이전과 다르더라도 정상입니다** (§0). 분량·참고문헌 수가 비슷한 범위에
들어오면 재현된 것으로 봅니다.

---

## 9. 재현 범위 밖

- **논문의 정량 수치** — 전문(full-text) DB가 필요하고 저자 문의로만 얻습니다.
  현재 DB는 초록만 있어 입력이 근본적으로 다릅니다 (`SETTING.md` §8).
- **`evaluation.py` 기반 평가** — 이 프로젝트의 목표는 "서베이가 생성되는지"까지입니다.
  돌리려면 `judge.py:202,216`의 무제한 스레드 생성을 먼저 제한해야 합니다
  (인용 개수만큼 스레드를 만듭니다).
- **비트 단위 동일 출력** — §0.
