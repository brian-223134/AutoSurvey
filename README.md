# AutoSurvey — 재현과 DB 최신화

[AutoSurvey (NeurIPS 2024)](https://arxiv.org/abs/2406.10252)의 포크입니다.
GPU 서버에서 **서베이 생성 파이프라인을 end-to-end로 재현**했고, 지금은
**2024-04에 멈춰 있는 논문 DB를 최신화하는 작업**을 준비하고 있습니다.

원본 README(논문 소개)는 맨 아래 [원본 프로젝트](#원본-프로젝트)로 옮겼습니다.

| 문서 | 역할 |
|---|---|
| **`README.md`** (이 문서) | 프로젝트가 무엇이고, 무엇이 나왔고, 다음에 무엇을 하는지 |
| [`HANDOFF.md`](HANDOFF.md) | 지금 어디까지 됐고 다음에 뭘 하면 되는지 — **작업 시작 전 필독** |
| [`REPRODUCTION.md`](REPRODUCTION.md) | 산출물 재현에 필요한 입력값 일체 (환경·DB 지문·커밋·하이퍼파라미터) |
| [`SETTING.md`](SETTING.md) | 세팅 **절차**와 각 패치의 근거 |
| [`output/README.md`](output/README.md) | 산출물의 결과 수치와 비교 시 주의점 |
| [`SURVEY_REPORT.md`](SURVEY_REPORT.md) | AutoSci·AutoSurvey·SurveyForge 3개 시스템 비교 리포트 |

---

## 1. 경로

**서버 작업 경로**: `/data2/chanjoong/survey-agent/AutoSurvey` (브랜치 `reproduce`)

같은 상위 디렉터리에 비교 대상 프로젝트가 함께 있습니다 —
`SurveyForge/`, `SurveyForge_data/`, `SurGE/`.
(AutoSci는 이 서버가 아니라 로컬 macOS에서 돌렸습니다. `SURVEY_REPORT.md` §1 참고.)

```
AutoSurvey/
├── main.py                  생성 진입점 — 검색 → 아웃라인 → 본문 → LCE
├── evaluation.py            평가 진입점 (미실행. judge.py 스레드 제한 선행 필요)
├── src/
│   ├── database.py          TinyDB + FAISS 검색, nomic 임베딩
│   ├── model.py             OpenRouter API 호출, 재시도·토큰 계측
│   ├── prompt.py            프롬프트 템플릿
│   └── agents/
│       ├── outline_writer.py   아웃라인 생성·파싱
│       ├── writer.py           서브섹션 병렬 작성 + LCE 정제
│       └── judge.py            LLM judge 평가 (미사용)
├── scripts/                 이 포크에서 추가한 도구 (§4)
├── database/                논문 DB 4파일, 3.9GB — git에 없음 (.gitignore)
├── output/                  생성된 서베이 — 모델별 디렉터리
│   ├── haiku/                  본편 3편
│   ├── deepseek-v4-pro/        본편 1편
│   ├── haiku-smoke/            파이프라인 점검용
│   └── deepseek-smoke/         파이프라인 점검용
├── examples/                원저자들이 생성한 서베이 3편 (대조용)
└── .env                     API 키 등 — git에 없음, 권한 600
```

### 데이터베이스

`database/`에 4개 파일. **git에 없으며 저자 배포본을 scp로 반입했습니다**
(이 서버에서 OneDrive는 차단). md5 지문은 `REPRODUCTION.md` §3.

| 파일 | 크기 | 내용 |
|---|---|---|
| `arxiv_paper_db.json` | 786MB | arXiv CS **537,665편** — `id`/`title`/`abs`/`date`/`cat`/`url`/`authors` |
| `faiss_paper_abs_embeddings.bin` | 1.65GB | 초록 임베딩 `IndexFlatL2` 537,665 × 768 |
| `faiss_paper_title_embeddings.bin` | 1.65GB | 제목 임베딩 (동일 규격) |
| `arxivid_to_index_abs.json` | 15MB | arXiv id → FAISS 인덱스 매핑 |

- 임베딩은 `nomic-ai/nomic-embed-text-v1`. **바꾸면 인덱스 전체가 무효**가 되고
  에러 없이 엉뚱한 논문이 검색됩니다.
- **수록 논문의 최신 날짜는 `2024-04-26`** 입니다. 이것이 §3의 출발점입니다.

---

## 2. 결과 요약

**서베이 6편 생성 완료** — 본편 4편 + 파이프라인 점검용 스모크 2편.
토픽당 `.md` / `.json` / `.tex` 3개가 나옵니다.

| 디렉터리 / 토픽 | 모델 | 섹션/서브섹션 | 단어 | 참고문헌 | 인용 | 비용 |
|---|---|---|---|---|---|---|
| `haiku-smoke/` In-context Learning | claude-3-haiku | 5 / 18 | 11,546 | 107 | 151 | $0.15 |
| `haiku/` In-context Learning | claude-3-haiku | 9 / 51 | 32,176 | 383 | 465 | $0.78 |
| `haiku/` Large Multi-Modal Language Models | claude-3-haiku | 8 / 48 | 30,709 | 378 | 467 | $0.75 |
| `haiku/` Evaluation of LLMs | claude-3-haiku | 8 / 48 | 30,439 | 368 | 425 | $0.75 |
| `deepseek-smoke/` In-context Learning | deepseek-v4-pro | 5 / 32 | 33,234 | 190 | 281 | $1.35 |
| `deepseek-v4-pro/` In-context Learning | deepseek-v4-pro | 14 / 117 | 92,707 | 644 | 884 | $3.39 |

6편 전부 `scripts/check_survey.py` 통과(댕글링 인용 0, json 매핑 일치).
haiku는 편당 6~8분. 결과 해석 시 주의점은 [`output/README.md`](output/README.md)에 있습니다 —
특히 **haiku 3편끼리만 통제된 비교**이고, deepseek 편의 섹션 수는 `.md` 헤딩 기준이라 부풀려져 있습니다.

**원본은 그대로 실행되지 않았습니다.** 패치 11종을 적용했고 그중 셋이 결정적이었습니다:

| 패치 | 없으면 |
|---|---|
| 죽은 `langchain.document_loaders` import 제거 (`src/utils.py`) | `ImportError`로 즉사 |
| `[[]] * n` aliasing 버그 (`src/agents/writer.py`) | **크래시 없이** 섹션 0을 뺀 전 섹션이 섹션 0의 참고문헌으로 본문을 씀 |
| TinyDB 선형 스캔 → dict 인덱스 (`src/database.py`) | 호출당 수 분 정지 |

전체 목록과 근거는 `REPRODUCTION.md` §4, `SETTING.md` §3·§4.

### 범위 밖

- **논문의 정량 수치 재현** — 논문은 각 논문 **본문 앞 1,500토큰**을 쓰는데 공개 DB에는
  초록만 있습니다. 입력이 근본적으로 다릅니다.
- **`evaluation.py` 기반 평가** — 돌리려면 `judge.py:202,216`의 무제한 스레드 생성을
  먼저 제한해야 합니다.
- **현재 크레딧 소진** — OpenRouter 키가 한도 $10을 다 썼습니다(2026-08-04 실측, 잔여 0).
  새 생성은 크레딧 확보가 선행돼야 합니다. 상세는 `HANDOFF.md`.

---

## 3. 개선 방향 — DB 최신화

### 3.1 문제

DB에 수록된 논문의 최신 날짜가 **2024-04-26**입니다. 현재(2026-08) 기준 **27개월**이
비어 있습니다. 그 사이에 부상한 주제는 검색 자체가 되지 않고, 기존 주제도 최근 2년치
후속 연구가 통째로 빠집니다. 서베이 생성기로서는 치명적인 노화입니다.

arXiv CS 월 1만 편 안팎을 감안하면 공백은 **25~30만 편, 기존 53.7만의 약 +50%**입니다.
"증분"이라고 부르기엔 큰 규모입니다.

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

근거는 `SURVEY_REPORT.md` §6.3에 정리돼 있습니다.

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
   다시 딸려옵니다. dedup하지 않으면 같은 논문이 중복 벡터로 들어가 top-k를 잡아먹습니다.

4. **파일 4개의 정합이 깨져도 에러가 나지 않습니다.** TinyDB / abs FAISS / title FAISS /
   id→index 매핑이 같은 순서로 커져야 하는데, 어긋나면 **조용히 엉뚱한 논문을 반환**합니다.
   append 후 `scripts/check_db.py` 실행이 필수입니다.

> **참고 — 문서 정정**: DB에 `authors` 필드가 **537,665편 전부** 채워져 있습니다(결측 0.000%).
> 일부 문서에 "저자 필드가 없다"고 적혀 있었으나 오기입니다. `.bib` 생성을 위해 저자를
> 외부에서 따로 받아올 필요가 없습니다.

### 3.5 스냅샷 버저닝 — 갱신하면 baseline이 바뀐다

임베딩 공간을 지켜도 **코퍼스가 +50% 되면 같은 토픽의 top-1200 자체가 달라집니다.**
기존 6편과의 통제 비교는 어차피 성립하지 않습니다. 이것을 손실이 아니라 **측정 대상**으로
다룹니다.

- **2024-04 스냅샷은 immutable로 보존**하고 새 스냅샷은 별도 파일로 만듭니다.
  `IndexFlatL2` append가 기존 순서를 보존하므로 옛 스냅샷은 새 스냅샷의 prefix가 됩니다.
  두 벌을 두어도 디스크는 +3.5GB뿐입니다.
- `REPRODUCTION.md`가 이미 DB를 **md5로 지문 관리**하므로, 새 스냅샷 = 새 md5 행 +
  cutoff 날짜. 기존 관례의 자연스러운 확장입니다.
- 그러면 **같은 토픽 × 두 스냅샷**으로 "DB 최신화의 효과"가 독립 변수 하나가 됩니다.
  단순 갱신보다 실험으로서 값어치가 큽니다.

### 3.6 작업 항목

DB 갱신은 GPU와 네트워크만 쓰므로 **크레딧 소진과 무관하게 진행할 수 있습니다.**
지금 DB를 만들어 두고 크레딧이 확보되면 바로 생성하는 순서가 맞습니다.

| # | 항목 | 상태 |
|---|---|---|
| 1 | `harvest_arxiv.py`를 7필드 스키마 + 버전 id 정책으로 정정 | 착수 전 |
| 2 | cutoff(2024-04-26) 이후 CS 논문 수집 — base id dedup 포함 | 착수 전 |
| 3 | append 스크립트 — 기존 인덱스 복사 → `add` → 매핑 확장 (원본 불변) | 착수 전 |
| 4 | `check_db.py` 정합 검사 + 재임베딩 일치 재검증 | 착수 전 |
| 5 | 같은 토픽 × 두 스냅샷 A/B 생성 | 크레딧 대기 |

미결 사항 — **수집 범위**를 전체 CS로 할지, 핵심 카테고리(`cs.CL`/`cs.LG`/`cs.AI`/`cs.CV`)로
한정할지 정해야 합니다. 현 DB의 카테고리 상위는 cs.CV(85,292) / cs.LG(74,835) /
cs.CL(42,393) / cs.IT(26,566) / cs.RO(20,498)입니다.

---

## 4. 스크립트

이 포크에서 추가한 도구입니다. 실행 방법은 `HANDOFF.md`와 `REPRODUCTION.md` §7.

**DB 준비용**

| 스크립트 | 용도 |
|---|---|
| `scripts/check_db.py` | DB 검증 — 파일 존재 / TinyDB 스키마 / FAISS·매핑 크기 정합 / 실검색 |
| `scripts/harvest_arxiv.py` | arXiv OAI-PMH 수집. **§3의 최신화 작업에서 주력으로 쓰게 됩니다** |
| `scripts/build_index.py` | `build_database.ipynb` 대체 (노트북은 `index_gpu_to_cpu` 에러로 실행 불가) |

**산출물 처리용**

| 스크립트 | 용도 |
|---|---|
| `scripts/check_survey.py` | 생성 결과 무결성 — 댕글링 인용 / json 매핑 / 포맷 누출 |
| `scripts/enrich_references.py` | `.json`에 arXiv 서지정보 채우기 (새 실행은 `main.py`가 자동 처리) |
| `scripts/md_to_tex.py` | `.md` → Overleaf용 `.tex` |

---

## 5. 빠른 시작

전제: conda 환경 `autosurvey`, `database/` 반입 완료, `.env` 작성 완료.
**환경 구축부터 필요하면 `REPRODUCTION.md` §2, §8을 따르세요.**

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

> `--api_key`는 일부러 넘기지 않습니다. 이 서버는 `/proc`에 hidepid가 없어 다른 사용자가
> `ps`로 명령줄을 읽을 수 있습니다. 키는 `.env`의 환경변수로 전달됩니다.

**시작 전에 `HANDOFF.md`의 "함정 모음"을 먼저 읽으세요.** `--api_url`에 경로를 빠뜨리거나
동시 요청 수를 올리면 바로 막힙니다.

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
