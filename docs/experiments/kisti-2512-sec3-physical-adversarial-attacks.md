# kisti-2512 첫 편 — Visual Adversarial Attacks and Defenses in the Physical World (2026-09-07)

KISTI Science Data Lake 파생 스토어를 corpus로 쓰는 view `kisti-2512`(1,651,701편)로 만든 **첫 산출물**의 기록이다.
목적은 품질 평가가 아니라 **KISTI DB × AutoSurvey 파이프라인 검증** — 인덱스·누수 차단·생성·DOI id 처리·컴파일이 end-to-end로 도는지 확인하고, 25편 본배치의 단가·소요를 실측하는 것이다.
수치는 `output/kisti-2512-sec3-physical-adversarial-attacks/Visual Adversarial Attacks and Defenses in the Physical World.run.json`에서 가져왔다.
corpus 설계·topic 선정은 `/data2/chanjoong/kisti_data/docs/{kisti-db.md, asg/autosurvey.md, topic-selection.md}` 참고.

> **corpus가 다르므로 bench-2512 편과 같은 표에 놓지 않는다.** 아래 병기는 거동 비교다.

## 0. 왜 이 토픽인가

25편 중 **security #3**. `docs/topic-selection.md` §7.3의 실제 view 기준 ceiling으로 골랐다.

| 기준 | 값 | 의미 |
|---|---|---|
| recall ceiling (cov_view) | **68%** (149/220) — 25편 중 최고 | 점수가 낮으면 corpus가 아니라 agent 탓임이 가장 확실 |
| twin | `2211.01671` — **KISTI에 실재**, view에서 제외됨 | 누수 차단을 end-to-end로 검증할 수 있는 토픽 |
| CC 대비 하락폭 | 75% → 68% (−7%p, 25편 중 최소급) | venue 논문(t3 44편)이 많은 topic이라 KISTI 강점을 보기 좋음 |
| 도메인 | security (bench-2512 첫 편은 ai) | 파이프라인 검증 범위 확장 |

GT: *Visual Adversarial Attacks and Defenses in the Physical World: A Survey* (ACM CSUR, 2026-04, [10.1145/3793659](https://doi.org/10.1145/3793659)). GT 본체는 KISTI에 없다.

## 1. 실행 조건

| 항목 | 값 |
|---|---|
| 백본 | `meta-llama/llama-3.3-70b-instruct` @ OpenRouter, provider 핀 **akashml/fp8**, temp 0 |
| DB | `database_kisti-kisti-2512` — 1,651,701편, export manifest sha `54b4e7b4…` (view `kisti-2512`, 패키지 `science_datalake_260825`) |
| 인덱스 | 2026-09-07 신규 빌드 (§4) · `nomic-ai/nomic-embed-text-v1`, dim 768 |
| 파라미터 | `--section_num 8 --subsection_num 4 --subsection_len 520` (bench-2512 첫 편과 동일) |
| 검색 | `--rag_num 60 --outline_reference_num 1200` |
| 동시성 | `AUTOSURVEY_MAX_THREADS=1` + `AUTOSURVEY_MAX_RETRY=10` (단, refine 단계에는 미적용 — §5-②) |
| 임베딩 GPU | `CUDA_VISIBLE_DEVICES=4` (27GB 여유) |
| 실행 | 2026-09-07 09:31 → 11:04 (UTC), `setsid nohup` 분리 |

```bash
source .env
export AUTOSURVEY_MAX_THREADS=1 AUTOSURVEY_MAX_RETRY=10 CUDA_VISIBLE_DEVICES=4
setsid nohup /data2/chanjoong/miniforge3/envs/autosurvey/bin/python -u main.py \
  --topic "Visual Adversarial Attacks and Defenses in the Physical World" \
  --saving_path ./output/kisti-2512-sec3-physical-adversarial-attacks/ \
  --db_path ./database_kisti-kisti-2512 \
  --embedding_model "$AUTOSURVEY_EMBEDDING_MODEL" \
  --model "$AUTOSURVEY_MODEL" --api_url "$AUTOSURVEY_API_URL" \
  --section_num 8 --subsection_num 4 --subsection_len 520 \
  --rag_num 60 --outline_reference_num 1200 > <out>/run.log 2>&1 < /dev/null &
```

## 2. 결과 — bench-2512 첫 편(09-03, ai #1)과 거동 비교

| 항목 | 이번 편 (kisti-2512) | bench-2512 ai #1 |
|---|---|---|
| 구조 | 8섹션 / **17**서브 | 8섹 / 23서브 |
| 단어 (tex 본문) | **35,542** — 그중 §2.1 반복 루프 약 25,700 (§5-①) → 실질 약 10,000 | 12,914 |
| refs / 인용 | **156 / 892** | 166 / 281 |
| refs id 구성 | **arXiv 87 · DOI 69 (44%)** | arXiv 166 |
| PDF | **68쪽** (루프 포함) | 35쪽 |
| 비용 | **$0.3066** (outline $0.0909 + writer $0.2157) | $0.3449 |
| 소요 | **92분 37초** (run.json) · 로그 기준 100분 | 64분 7초 |
| 재시도 | 2회 (전부 429, refine 단계) | 2회 (429) |
| **잘린 호출** | **2건** ⚠ | 2건 ⚠ |
| 서브당 단어 계수 | 루프 제외 16서브 기준 약 626 (**1.2×**) | 561 (1.08×) |

- **outline 비용이 세 편 연속 $0.089~0.091**로 고정 — `outline_reference_num 1200`이 지배하는 고정비라는 관측이 corpus를 바꿔도 유지된다.
- writer 출력 토큰 326,380은 정상치(약 60~70K)의 4.7배. 잘린 호출 2건이 각각 출력 한도 128K까지 생성한 것과 일치한다(bench-2512 ai #1의 271,846과 같은 패턴).
- 참고문헌 연도: 2018–2025에 고르게 분포(2021 22 · 2022 24 · 2023 24 · 2024 19 · 2025 19). 2014~2017은 3편.

### GT 참고문헌 대비 (참고치)

생성 refs 156 ∩ GT in-view 149 = **19편** → recall 12.8%(ceiling 분모) · 8.6%(pre-cutoff 220 분모) · precision 12.2%.
매칭 키는 감사와 같은 `doi` ∨ `10.48550/arxiv.<id>`. 채점 규약이 확정되기 전의 참고치이며, 다른 3개 agent와 같은 채점기로 다시 잰다.

## 3. 검증

| 검사 | 결과 |
|---|---|
| `check_survey.py` | **OK** — 댕글링 인용 0, 포맷 누출 0, json 매핑 156/156 |
| **누수 차단** (`2211.01671`, GT DOI, twin 제목) | 인덱스 id 매핑 부재 ✅ · **본문 등장 0회** ✅ |
| PDF 컴파일 | latexmk 정상 종료, **미해결 인용 0**, `\bibitem` 156개 (arXiv 87 + doi 69 링크 정상) |
| 단위 테스트 (main.py·md_to_tex.py 패치 후) | 78개 OK (skipped 2) |

누수 차단은 인덱스와 산출물 양쪽에서 확인했다. KISTI DB에는 twin이 `10.48550/arxiv.2211.01671`로 실재하지만(`view_manifest.excluded_present`), view 생성기가 제외했고 인덱스 id 매핑에도 없다.

## 4. 인덱스 빌드 — 1회 성공

| 항목 | 값 |
|---|---|
| 명령 | `kisti_data/adapter/autosurvey/build_db.sh` (GPU 3, setsid) |
| 소요 | **2h17m** (05:29 → 07:46 UTC): title 약 12분 + abstract 약 2시간 4분 |
| 산출 | FAISS title/abs 각 4.84GB (1,651,701 × 768), id 매핑 54MB |
| `check_db.py` | 파일·스키마·매핑·검색 OK. §4 저장 벡터 재현 최저 cos **0.975** (임계 0.999 미달 → "문제 있음" 종료) |

cos 경고는 별도 판별로 **무해 판정**: arXiv id 15 + DOI id 15편을 재인코딩해 전체 인덱스에서 k=1 검색한 argmax가 **60/60 자기 위치**(title cos 1.0000, abs 0.936~0.999). 순서가 어긋났다면 0.5~0.6대로 떨어진다. bench-2512(0.988)보다 낮은 것은 편수가 1.7배라 장시간 빌드의 수치 변동이 누적된 결과로 본다. **재빌드 금지.**

## 5. 미결 — 25편 본배치 전에 풀어야 할 것

### ① degenerate loop가 최종본에 들어갔다 (bench-2512 때와 다른 점)

§2.1 "Introduction to Adversarial Examples"이 **26,607단어**다. 고유 본문 857단어 뒤에 9줄짜리 문단 블록이 **43회 반복**된다(60자+ 고유 줄 14개뿐). temperature 0의 반복 루프가 잘린 초안 → refine 입력으로 흘러 LCE를 거치고도 남았다. bench-2512 ai #1은 같은 잘림 2건이 있었지만 최종본 23서브 전수에서 끊김·반복이 없었다 — **운이 좋았던 것이고, 재현 시 최종본이 오염될 수 있음이 이번에 확인됐다.**

25편 본배치 전 대책 후보 (결정 필요):
- 응답에서 n-gram 반복을 감지하면 temperature를 올려 재요청 (`src/model.py`, 코드 수정)
- 서브섹션 호출에 `max_tokens` 상한(예: 8K)을 걸어 runaway를 싸게 자르기 — 단 잘린 초안 문제는 남음
- 이 편만 재실행 ($0.31, 약 100분, 재발 가능)

### ② `chat()`의 재시도 한도 5 하드코딩

`src/model.py:154` `chat()`은 `max_try=5`를 고정으로 넘겨 `AUTOSURVEY_MAX_RETRY`를 무시한다. refine(LCE)·outline 단계가 이 경로다. 이번에 refine 호출(프롬프트 233,651자)에서 429가 2회 났고 3회째에 회복했지만, 5회 소진 시 `None`이 반환되어 `writer.py:201`의 `.replace()`가 죽는다. `main.py`가 안내하는 "AUTOSURVEY_MAX_RETRY로 올릴 수 있습니다"와 어긋나므로 `max_try=None`(환경변수 따름)으로 바꾸는 한 줄 수정을 권한다.

### ③ 예산

| | 값 |
|---|---|
| 실행 전 잔여 | $6.78 |
| **실행 후 잔여** | **$6.48** (이 편 $0.31) |
| 남은 24편 예상 | $0.31 × 24 ≈ **$7.4** → 키 한도 상향 필요 (bench 문서 §5-②와 동일) |

### ④ DOI id 논문의 저자 보강

`scripts/enrich_references.py`는 arXiv API 기반이라 refs의 44%(DOI id)에 동작하지 않는다. view의 `authors.parquet`(kisti_data)로 대체하는 후처리가 미구현이다.

## 6. 이번 편에서 고친 것

- **`main.py` `build_reference_detail`**: url을 `arxiv.org/abs/{id}`로 하드코딩하던 것을 id 규칙에 따라 분기 — DOI id(`10.`으로 시작)는 DB 레코드 url(doi.org). arXiv id는 기존 그대로.
- **`scripts/md_to_tex.py` `format_bibitem`**: DOI id 라벨을 `arXiv:` 대신 `doi:`로.
- **이번 산출물 sidecar JSON**: 패치 전에 생성된 `reference_detail`의 DOI url 69건을 같은 규칙으로 보정 (원본은 `.json.bak`). tex/PDF는 보정 후 재생성.
- **DB 디렉터리**: `collect_run.py`가 `*.manifest.json`만 찾으므로 export manifest를 `kisti-2512.autosurvey.json.manifest.json`으로 한 부 더 두었다 (`corpus_export_manifest.json`과 동일 내용).

## 7. 재현

PDF 툴체인은 bench-2512 문서 §6과 같다 — pandoc은 `tex` env, latexmk는 `/usr/local/bin`. 보조 파일 정리 시 `*.log` 와일드카드 금지.

```bash
OUT=output/kisti-2512-sec3-physical-adversarial-attacks
MD="$OUT/Visual Adversarial Attacks and Defenses in the Physical World.md"
PATH="/data2/chanjoong/miniforge3/envs/tex/bin:$PATH" \
  /data2/chanjoong/miniforge3/envs/autosurvey/bin/python scripts/md_to_tex.py "$MD"
/usr/local/bin/latexmk -pdf -interaction=nonstopmode "${MD%.md}.tex"
/data2/chanjoong/miniforge3/envs/autosurvey/bin/python scripts/collect_run.py --md "$MD" \
  --log "$OUT/run.log" --db_path ./database_kisti-kisti-2512 \
  --args "--section_num 8 --subsection_num 4 --subsection_len 520 --rag_num 60 --outline_reference_num 1200 --db_path ./database_kisti-kisti-2512 --embedding_model nomic-ai/nomic-embed-text-v1"
```
