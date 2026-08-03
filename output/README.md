# 생성된 서베이 — 결과

각 디렉터리에 어떤 결과물이 있고, 볼 때 무엇을 주의해야 하는지 정리한 문서입니다.

**실행 조건(모델·하이퍼파라미터·환경·명령)은 [`../REPRODUCTION.md`](../REPRODUCTION.md)에 있습니다.**
새 서베이를 만들면 아래 결과 표와 `REPRODUCTION.md` §5-2 조건 표에 각각 한 줄씩 추가해 주세요.

---

## 결과

| 디렉터리 / 토픽 | 모델 | 섹션/서브섹션 | 단어 | 참고문헌 | 인용 | 비용 |
|---|---|---|---|---|---|---|
| `haiku-smoke/` In-context Learning | haiku | 5 / 18 | 11,546 | 107 | 151 | $0.15 |
| `haiku/` In-context Learning | haiku | 9 / 51 | 32,176 | 383 | 465 | $0.78 |
| `haiku/` Large Multi-Modal Language Models | haiku | 8 / 48 | 30,709 | 378 | 467 | $0.75 |
| `haiku/` Evaluation of LLMs | haiku | 8 / 48 | 30,439 | 368 | 425 | $0.75 |
| `deepseek-smoke/` In-context Learning | deepseek-v4-pro | 5 / 32 | 33,234 | 190 | 281 | $1.35 |
| `deepseek-v4-pro/` In-context Learning | deepseek-v4-pro | 14 / 117 | 92,707 | 644 | 884 | $3.39 |

`scripts/check_survey.py` 기준입니다(6편 전부 통과 — 댕글링 인용 0, json 매핑 일치).

> ⚠ **deepseek 편의 섹션 수는 이 표 기준으로는 부풀려져 있습니다.**
> `check_survey.py`는 `.md`의 `##` / `###` 를 그대로 세는데, deepseek는
> 서브섹션을 `## 2.5` 로 쓰거나 제목을 두 번 쓴 곳이 있습니다.
> 중복을 제거하고 번호 깊이로 레벨을 다시 매긴 `.tex` 기준 실제 구조는
> **10섹션 / 72서브섹션 / 5서브서브섹션**, `deepseek-smoke/`는 **5 / 29** 입니다.
> haiku 편은 두 기준이 일치합니다.

---

## 비교할 때 주의할 점

**haiku 3편끼리만 통제된 비교가 됩니다.** 나머지는 조건이 겹치지 않습니다.

- **`deepseek-v4-pro/` vs `haiku/` (같은 토픽)** — `rag_num`이 30 대 60으로 다릅니다.
  모델 차이만 보는 비교가 아닙니다. 그런데도 deepseek 쪽이 분량 2.9배,
  참고문헌 1.7배였습니다.
- **스모크 2편은 품질 비교용이 아닙니다.** 축소 설정(`section_num 4` /
  `outline_reference_num 200` / `rag_num 15`)으로 파이프라인이 끝까지 도는지만
  확인한 것입니다. 본편과 나란히 놓고 평가하지 마세요.
- **`deepseek-smoke/`는 추론이 켜진 채로 돌았습니다.** `AUTOSURVEY_REASONING`
  토글이 생기기 전 실행이라 본편(추론 OFF)과 설정이 다릅니다. 스모크 비용이
  토큰 추정의 3.5배로 튄 원인이기도 합니다(추론 토큰이 출력의 45%).
- **`deepseek-smoke/`는 두 번째 시도 결과입니다.** 첫 시도는 아웃라인 파서가
  `IndexError`로 죽었습니다(`8bfbc43`).
- **haiku는 추론 모델이 아니므로** 추론 설정이 결과에 영향을 주지 않습니다.
- **논문 수치와는 비교할 수 없습니다.** 논문은 전문(full-text) DB를 쓰는데
  이 DB에는 초록만 있습니다. `../SETTING.md` §8.

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

### Overleaf에 올리기

Overleaf → New Project → Blank Project → `.tex` 업로드 → main document 지정 → Recompile.
여러 편을 한 번에 보려면 `output/`을 zip으로 묶어 **Upload Project**.

> deepseek 편은 92,707단어 + 참고문헌 644개라 무료 Overleaf 제한시간(약 20초)을
> 넘길 수 있습니다. 걸리면 `\tableofcontents` 주석 처리부터 시도하세요.

---

## 재실행 / 재변환

실행 명령과 후처리 절차는 [`../REPRODUCTION.md`](../REPRODUCTION.md) §5-3, §7에 있습니다.
