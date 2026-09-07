# kisti-2512 sec #3 — temperature 0.6 프로파일 본편 2회 (2026-09-07)

디코딩 프로파일(temp 0.6 · max_tokens 8192)로 같은 topic을 2회 돌린 기록이다. 목적은 ① temp 0 편에서 본 반복 루프가 0.6에서 어떻게 되는지,
② 8K 가드와 **잘림 재요청**(커밋 `baa46cc`)이 최종본을 지키는지, ③ 같은 설정의 run-to-run 편차(recall·refs·분량)를 재는 것.
수치는 각 디렉터리의 `*.run.json`·`run.log`·sidecar JSON에서 가져왔다. topic·GT·twin·recall 계산은 [kisti-2512-sec3-physical-adversarial-attacks.md](kisti-2512-sec3-physical-adversarial-attacks.md)와 같다.

> **r1과 r2는 코드가 다르다.** r1은 가드만(잘린 응답 수용), r2는 가드 + 잘림 재요청. 순수한 run-to-run 편차 쌍은 r2와 같은 코드의 **r3**(§7, 2026-09-07 14:12 실행)다.

## 1. 실행 조건

공통: llama-3.3-70b @ akashml/fp8 · temperature 0.6 · max_tokens 8192 · `--section_num 8 --subsection_num 4 --subsection_len 520 --rag_num 60 --outline_reference_num 1200` · `MAX_THREADS=1` · `MAX_RETRY=10` · DB `database_kisti-kisti-2512` · 질의 임베딩 CPU(`AUTOSURVEY_DEVICE=cpu`, GPU 전량 점유) · `setsid nohup`.

| | temp 0 첫 편 (참고) | **t06-r1** | **t06-r2** |
|---|---|---|---|
| 코드 | `e9e49c3` 이전 | `cb1ba00` (가드 있음, 잘린 응답 수용) | **`baa46cc`** (가드 + 잘림 재요청) |
| 실행 (UTC) | 09:31 → 11:04 | 12:41 → 13:34 | 13:36 → 14:06 |
| 출력 디렉터리 | `…-physical-adversarial-attacks/` | `…-t06-r1/` | `…-t06-r2/` |

## 2. 결과

| 항목 | temp 0 첫 편 | t06-r1 | **t06-r2** |
|---|---:|---:|---:|
| 소요 | 93분 | 53분 | **30분** |
| 비용 (outline + writer) | $0.307 | $0.374 | **$0.338** ($0.097 + $0.241) |
| 구조 | 8섹 / 17서브 | 8섹 / 25서브 | **9섹 / 24서브** |
| 본문 단어 (md) | 36,619 | 22,824 | **14,273** |
| 루프 오염 서브섹션 | 1 (§2.1, 26.6K단어) | 2 (§6.1·6.2, 9.6K단어) | **0** |
| 정상 서브당 단어 (계수) | 626 (1.20×) | 575 (1.11×) | **595 (1.14×)**, 343~913 |
| 잘린 호출 — 수용 / 재요청 | 2 / — | 12 / — | **0 / 6** |
| 429 재시도 | 2 | 8 | 3 |
| refs (arXiv / DOI) | 156 (87/69) | 235 (142/93) | **184 (92/92)** |
| 인용 횟수 | 892 | 631 | 279 |
| GT recall (149 분모) | 12.8% (19) | 13.4% (20) | **8.1% (12)** |
| precision | 12.2% | 8.5% | 6.5% |
| 누수 (twin·GT) | 0 | 0 | **0** |
| check_survey | OK | OK | OK |
| PDF | 68쪽 | 55쪽 | **38쪽**, 미해결 인용 0 |

### 편 사이 겹침

| 쌍 | refs 겹침 (Jaccard) | GT 적중 겹침 |
|---|---|---|
| temp0 ∩ r1 | 59 (0.18) | 13 / 26 |
| temp0 ∩ r2 | 48 (0.16) | 9 / 22 |
| r1 ∩ r2 | 53 (0.14) | 11 / 21 |
| 세 편 합집합 GT 적중 | | **26 / 149** |

## 3. 해석

1. **반복 루프는 temp 0.6에서도 난다.** r1에서 writer 호출 약 50건 중 12건이 8K 가드까지 갔다(프로브 12회는 0건 — 본편은 전체 outline이 프롬프트에 들어가고 reflection 프롬프트가 있다). 가드 덕에 호출당 손실은 128K·45분 → 8K·2분으로 묶였고, 최종본 오염도 26.6K → 9.6K단어로 줄었지만 0은 아니었다.
2. **잘림 재요청이 최종본을 지켰다.** r2는 재요청 6회(한 프롬프트는 4회 연속 잘림 → 5회째 정상), 수용 0, 루프 오염 0. 추가 비용 약 6 × 8K 토큰 ≈ $0.025, 추가 시간 약 12분. 같은 프롬프트가 연속으로 루프에 빠진 것은 **루프가 프롬프트 의존적**이라는 뜻이라, 재요청이 10회를 다 쓰는 경우가 생기면 재요청 시 temperature 상향이나 프롬프트 변형(논문 목록 축소 등)을 검토한다.
3. **recall의 run-to-run 편차가 크다.** 8.1 ~ 13.4% (3편 평균 11.4%, 범위 5.3%p). refs Jaccard 0.14~0.18로 writer가 고르는 논문이 편마다 대부분 다르고, 세 편 합집합은 26/149(17.4%)다. retrieval 풀(1,200편)이 같아도 인용 선택이 샘플링에 크게 좌우된다. **편당 1회로 agent 간 recall을 비교하려면 차이가 5%p 이상이어야 의미 있다**는 잠정 결론이며, 같은 코드 2회(r2·r3)로 다시 잰다.
4. **분량이 대역(20~25k단어) 아래로 내려갔다.** r2는 14.3K단어·38쪽. 정상 서브당 595단어는 temp 0 편(626)과 비슷하므로 원인은 서브섹션 수(24)와 인용 밀도(279회, r1의 절반)다. 프로브의 초안 965단어 → 최종 595단어로 **초안→최종 비율은 0.62**(08-31 앵커 0.85보다 낮음). 분량을 올리려면 `--subsection_len`이 아니라 `--enforce_section_num`·`--subsection_num`으로 서브섹션 수를 잡아야 한다(프로브 문서 §4 결정과 일치).
5. **KISTI 특성은 유지된다.** DOI id 논문이 refs의 40~50%, 누수 0, DOI 링크 정상. Elsevier 제목의 각주 표식 ☆이 pdflatex를 죽여 md_to_tex에 제거 규칙을 추가했다(`☆`·`★` → 삭제).

## 4. 코드 변경 (이 실험에서)

| 커밋 | 내용 |
|---|---|
| `baa46cc` | `src/model.py` — 가드에 걸린 응답(finish_reason=length)은 버리고 재요청. `AUTOSURVEY_RETRY_TRUNCATED` (MAX_TOKENS 설정 시 기본 on). 재시도 소진 시 마지막 잘린 내용 수용·잘림으로 집계. `main.py` 보고 줄 "잘림 재요청 N회", `collect_run.py` `truncation_retries` 필드, 테스트 4개 |
| r2 커밋 | `scripts/md_to_tex.py` — `☆`·`★` 제거 |

## 5. 결정 필요

1. ~~**r3 실행**~~ → 완료(§7). 같은 코드 쌍 r2·r3의 recall 차이 3.4%p.
2. **재요청 소진 대비**: 재요청 시 temperature 상향(예: +0.2) 또는 프롬프트 변형. r2에서는 5회 안에 다 풀렸으므로 당장은 불필요.
3. **분량 대역**: 20~25k를 유지할지, 14k대(38쪽)를 새 기준으로 둘지. 유지하려면 `--enforce_section_num` + `--subsection_num 4` 강제 또는 `--section_num 10`.
4. **결과표 병기 규약**: recall 옆에 run-to-run 범위(잠정 ±2.7%p)와 ceiling(68%)을 함께 적는다.

## 6. 재현

```bash
source .env; export AUTOSURVEY_MAX_THREADS=1 AUTOSURVEY_MAX_RETRY=10 AUTOSURVEY_DEVICE=cpu
setsid nohup python -u main.py --topic "Visual Adversarial Attacks and Defenses in the Physical World" \
  --saving_path ./output/kisti-2512-sec3-physical-adversarial-attacks-t06-r3/ --db_path ./database_kisti-kisti-2512 \
  --embedding_model "$AUTOSURVEY_EMBEDDING_MODEL" --model "$AUTOSURVEY_MODEL" --api_url "$AUTOSURVEY_API_URL" \
  --section_num 8 --subsection_num 4 --subsection_len 520 --rag_num 60 --outline_reference_num 1200 > <out>/run.log 2>&1 < /dev/null &
```

검증·PDF·run.json 명령은 첫 편 문서 §7과 같다. recall은 `kisti_data/candidates/gap_to_80_refs.jsonl`의 `tier == in_view`(149편)를 분모로, 키 `doi` ∨ `10.48550/arxiv.<id>`로 매칭한다.

## 7. r3 — r2와 같은 코드의 두 번째 실행 (2026-09-07 14:12 → 14:31 UTC)

코드 `da4e87c`(모델 코드는 r2와 동일한 `baa46cc`), 조건 §1과 동일. 산출물 `…-t06-r3/`.

| 항목 | t06-r2 | **t06-r3** | 같은 코드 쌍의 차이 |
|---|---:|---:|---|
| 소요 / 비용 | 30분 / $0.338 | **19분 / $0.347** | |
| 구조 / 본문 단어 (md) | 9섹 24서브 / 14,273 | **8섹 28서브 / 16,509** | 서브 수 ±4 |
| 정상 서브당 단어 (계수) | 595 (1.14×) | **590 (1.11×)**, 458~874 | 안정 |
| 루프 오염 / 잘림 수용 / 재요청 | 0 / 0 / 6 | **0 / 0 / 3** | 재요청이 두 편 모두 최종본을 지킴 |
| 429 재시도 | 3 | 0 | |
| refs (arXiv / DOI) | 184 (92/92) | **240 (118/122)** | refs 수 ±56 |
| 인용 횟수 | 279 | 317 | |
| GT recall (149 분모) | 8.1% (12) | **11.4% (17)** | **3.4%p** |
| precision | 6.5% | 7.1% | 0.6%p |
| refs 겹침 (Jaccard) · GT 적중 겹침 | | 42 (0.11) · 11/18 | |
| 누수 / check_survey / PDF | 0 / OK / 38쪽 | **0 / OK / 45쪽**, 미해결 인용 0 | |

네 편(temp0·r1·r2·r3) 합집합 GT 적중 29/149 (19.5%). recall 순서는 r1 13.4 > temp0 12.8 > r3 11.4 > r2 8.1.

**같은 코드 쌍(r2·r3)에서 얻은 잠정 오차**: recall ±1.7%p(차이 3.4%p), refs 수 ±28, 서브섹션 수 ±2, 서브당 단어 ±3. precision은 6.5 vs 7.1%로 recall보다 안정적이다 — 분량 중립 지표로서의 장점이 편차 면에서도 확인된다. n=2라 표준편차가 아니라 "1회 실행의 차이가 이 정도"라는 앵커이며, 결과표에는 recall 옆에 ±1.7%p(잠정)를 병기한다.

**분량**: 재요청 코드에서 두 편 모두 14~17K단어(38~45쪽)로 temp 0 편(정상분 10K)보다 길고 20~25k 대역보다 짧다. 2026-09-07 사용자 결정으로 **분량은 통제하지 않는다** — 25편 본배치는 AutoSurvey 논문 기본값(8섹션, 서브섹션 상한 없음, `subsection_len` 700)으로 돌리고 분량·refs 수는 agent 속성으로 기록, 평가는 recall과 precision을 병기한다(§5-3 대체).
