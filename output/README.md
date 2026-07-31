# 생성된 서베이 — 실행 조건 기록

각 디렉터리가 어떤 조건으로 생성됐는지 정리한 문서입니다.
지금까지 이 정보는 커밋 메시지에 흩어져 있었고 스모크 2편은 수치 자체가
기록돼 있지 않았습니다. 실제 실행 명령을 복원해 여기에 모았습니다.

**새 서베이를 생성하면 아래 표에 한 줄 추가해 주세요.**

---

## 한눈에 보기

| 디렉터리 | writer 모델 | section_num | subsection_len | rag_num | outline_reference_num | 추론 | 비용 |
|---|---|---|---|---|---|---|---|
| `haiku-smoke/` | anthropic/claude-3-haiku | 4 | 700 (기본) | 15 | 200 | 해당없음 | $0.15 |
| `haiku/` (3편) | anthropic/claude-3-haiku | 8 | 700 | 60 | 1200 | 해당없음 | 편당 $0.75~0.78 |
| `deepseek-smoke/` | deepseek/deepseek-v4-pro | 4 | 700 (기본) | 15 | 200 | **ON** | $1.35 |
| `deepseek-v4-pro/` | deepseek/deepseek-v4-pro | 8 | 700 | **30** | 1200 | **OFF** | $3.39 |

모든 실행의 공통 조건:

- API: OpenRouter (`https://openrouter.ai/api/v1/chat/completions`)
- 임베딩: `nomic-ai/nomic-embed-text-v1` — **공식 DB가 이 벡터 공간이라 바꾸면 안 됩니다**
- DB: `./database` (arXiv CS 초록 537,665편)
- `AUTOSURVEY_MAX_THREADS=4` (`.env`)
- 키는 `source .env`로 환경변수 전달 (`--api_key`는 `ps`에 노출돼 사용 금지)

---

## 결과

| 디렉터리 / 토픽 | 섹션/서브섹션 | 단어 | 참고문헌 | 인용 |
|---|---|---|---|---|
| `haiku-smoke/` In-context Learning | 5 / 18 | 11,546 | 107 | 151 |
| `haiku/` In-context Learning | 9 / 51 | 32,176 | 383 | 465 |
| `haiku/` Large Multi-Modal Language Models | 8 / 48 | 30,709 | 378 | 467 |
| `haiku/` Evaluation of LLMs | 8 / 48 | 30,439 | 368 | 425 |
| `deepseek-smoke/` In-context Learning | 5 / 32 | 33,234 | 190 | 281 |
| `deepseek-v4-pro/` In-context Learning | 14 / 117 | 92,707 | 644 | 884 |

`scripts/check_survey.py` 기준입니다(6편 전부 통과 — 댕글링 인용 0, json 매핑 일치).

> ⚠ **deepseek 편의 섹션 수는 이 표 기준으로는 부풀려져 있습니다.**
> `check_survey.py`는 `.md`의 `##` / `###` 를 그대로 세는데, deepseek는
> 서브섹션을 `## 2.5` 로 쓰거나 제목을 두 번 쓴 곳이 있습니다.
> 중복을 제거하고 번호 깊이로 레벨을 다시 매긴 `.tex` 기준 실제 구조는
> **10섹션 / 72서브섹션 / 5서브서브섹션**, `deepseek-smoke/`는 **5 / 29** 입니다.
> haiku 편은 두 기준이 일치합니다.

---

## 실행 명령 (실제로 돌린 것)

### 스모크 — 파이프라인이 끝까지 도는지만 확인

축소 설정이라 **품질 비교용이 아닙니다.** 본편과 나란히 놓고 평가하지 마세요.
`--subsection_len`을 주지 않아 기본값 700이 쓰였습니다.

```bash
source .env && $HOME/miniforge3/envs/autosurvey/bin/python main.py \
  --topic "In-context Learning" \
  --saving_path ./output/haiku-smoke/ \
  --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --section_num 4 --outline_reference_num 200 --rag_num 15
```

`deepseek-smoke/`는 `--model deepseek/deepseek-v4-pro`, `--saving_path ./output/deepseek-smoke/`
만 다르고 나머지는 동일합니다.

### 본편 — 논문 설정

```bash
source .env && $HOME/miniforge3/envs/autosurvey/bin/python main.py \
  --topic "In-context Learning" \
  --saving_path ./output/haiku/ \
  --db_path ./database \
  --embedding_model nomic-ai/nomic-embed-text-v1 \
  --model anthropic/claude-3-haiku \
  --api_url https://openrouter.ai/api/v1/chat/completions \
  --section_num 8 --subsection_len 700 --rag_num 60 --outline_reference_num 1200
```

`haiku/`의 나머지 두 편은 `--topic`만 바꿔 같은 설정으로 돌렸습니다
(`Large Multi-Modal Language Models`, `Evaluation of LLMs`).

`deepseek-v4-pro/`는 위에서 `--model deepseek/deepseek-v4-pro`,
`--rag_num 30`(예산 제약), `--saving_path ./output/deepseek-v4-pro/`로 바꾼 것입니다.

---

## 비교할 때 주의할 점

**haiku 3편끼리만 통제된 비교가 됩니다.** 나머지는 조건이 겹치지 않습니다.

- **`deepseek-v4-pro/` vs `haiku/` (같은 토픽)** — `rag_num`이 30 대 60으로 다릅니다.
  모델 차이만 보는 비교가 아닙니다. 그런데도 deepseek 쪽이 분량 2.9배,
  참고문헌 1.7배였습니다.
- **`deepseek-smoke/` vs `deepseek-v4-pro/`** — 축소 설정인 데다 **추론 설정도 다릅니다.**
  스모크는 `AUTOSURVEY_REASONING` 토글이 생기기 전에 돌아서 추론이 켜진 상태였고,
  이것이 스모크 비용이 토큰 추정의 3.5배로 튄 원인입니다(추론 토큰이 출력의 45%).
  본편은 추론을 끄고 돌렸습니다.
- **`deepseek-smoke/`는 두 번째 시도 결과입니다.** 첫 시도는 아웃라인 파서가
  `IndexError`로 죽었습니다(`8bfbc43` 참고). 파서를 고친 뒤 다시 돌린 산출물입니다.
- **haiku는 추론 모델이 아니므로** 추론 설정이 결과에 영향을 주지 않습니다.

---

## 산출물 형식

디렉터리마다 토픽당 3개 파일이 있습니다.

| 파일 | 내용 |
|---|---|
| `{topic}.md` | 본문 + `## References`(번호와 제목) |
| `{topic}.json` | `survey` / `reference`(번호→arXiv id) / `reference_detail`(id·제목·날짜·링크) |
| `{topic}.tex` | Overleaf용. `scripts/md_to_tex.py`가 생성 |

- `reference` 필드는 `src/agents/judge.py`의 `citation_quality()`가 쓰는 구조라
  **바꾸면 `evaluation.py`가 깨집니다.** 서지정보는 `reference_detail`에 있습니다.
- `.tex`는 `.md`에서 만들되 제목 중복 제거, 헤딩 레벨 교정, `\cite` 변환,
  pdflatex 미지원 유니코드 치환을 거칩니다. 자세한 내용은 `scripts/md_to_tex.py`.
- 서버에서는 컴파일이 불가능합니다(TeX 매크로 트리 없음). Overleaf에서 확인하세요.

---

## 재생성 / 재변환

```bash
# .json에 서지정보 채우기 (DB 750MB 로딩, 1~2분. 전체 일괄 처리)
python scripts/enrich_references.py

# .md -> .tex
export PATH="$HOME/miniforge3/envs/tex/bin:$PATH"        # pandoc
for f in output/*/*.md; do
  $HOME/miniforge3/envs/autosurvey/bin/python scripts/md_to_tex.py "$f"
done

# 구조·인용 무결성 검사
python scripts/check_survey.py "output/haiku/In-context Learning.md"
```

`tex` env에는 python이, `autosurvey` env에는 pandoc이 없어 PATH로 섞어 씁니다.
