# 길이 계수 재측정 — temperature 0.6 · max_tokens 8192 (2026-09-07)

디코딩 프로파일을 바꾼 뒤(temperature 0 → 0.6, max_tokens 없음 → 8192) `--subsection_len` 역산에 쓰는
**서브섹션 길이 계수**를 다시 잰 기록이다. 08-31 프로브(temp 0)는 수기라 재현할 수 없었으므로,
이번부터는 `scripts/probe_length.py` + spec JSON으로 조건을 고정하고 산출 JSON을 `output/probes/`에 남긴다.
수치는 전부 그 JSON에서 가져왔다.

## 0. 프로파일 변경 — 왜

| 항목 | 이전 | 이후 | 커밋 | 근거 |
|---|---|---|---|---|
| `AUTOSURVEY_TEMPERATURE` | 0 (결정론 실험 계열) | **0.6** | `cb1ba00` | temp 0에서 llama-3.3-70b가 반복 루프에 빠져 호출 하나가 128K 토큰·45분 (kisti-2512 첫 편 100분, bench-2512 64분). 0.6은 Llama 3.x 제조사 권장 기본값 — 외부 근거가 있고 어느 agent의 원 설정(1.0 / 0.3·0.5 / provider 기본)도 아니라 중립 |
| `AUTOSURVEY_MAX_TOKENS` | 미전송 (provider 한도 128K) | **8192** | `aa98d14` | 원논문의 설계 전제가 "호출당 출력 <8K (GPT-4 8k, Claude 3 4k)". 정상 호출(서브섹션 ≈1K, 아웃라인 ≤2K 토큰)엔 안 걸리는 잘림 가드 |

원논문 코드는 temperature를 메시지 객체 안에 넣어 API가 무시했으므로(서버 기본 1.0으로 동작) max_tokens도 없었다. Haiku의 4K 한도가 사실상의 상한 역할을 했다.
다른 3개 agent(SurveyForge·SurveyX·LLM×MR-V2)에는 같은 프로파일을 **사용자가 직접 전달**한다.

## 1. 프로토콜

- 본편 writer와 같은 입력: `SUBSECTION_WRITING_PROMPT`, description → DB 검색 `rag_num 60`편 초록, paper_texts 조립, `citation_num 8`, `APIModel`(.env의 provider 핀·temperature 오버라이드·max_tokens).
- 다른 점: **1차 초안만** 잰다 (reflection·LCE 없음). 최종본은 이보다 짧아진다 — 유일한 앵커는 08-31 v4-pro의 초안→최종 비율 0.85.
- 호출 순차(429 회피), 임베딩 CPU(`AUTOSURVEY_DEVICE=cpu`), 서브섹션당 2회 반복으로 run-to-run 편차 동시 측정.
- 세트 A: 08-31 temp-0 프로브와 같은 조건(Edge Computing · `database_commoncorpus-2512` · 지시 700 · 같은 서브섹션 3개) → **temperature 효과 분리**. description은 08-31 기록에 없어 새로 썼다 (spec JSON에 고정).
- 세트 B: 앞으로 쓸 조건(`database_kisti-kisti-2512` · 지시 520 · kisti-2512 첫 편 아웃라인의 서브섹션 3개) → **본배치용 계수**.

```bash
source .env; export AUTOSURVEY_DEVICE=cpu
python scripts/probe_length.py --spec output/probes/edge-cc2512-len700.spec.json      --db_path ./database_commoncorpus-2512 --repeat 2
python scripts/probe_length.py --spec output/probes/physadv-kisti2512-len520.spec.json --db_path ./database_kisti-kisti-2512   --repeat 2
```

프로파일 실측(JSON `profile`): `meta-llama/llama-3.3-70b-instruct` · provider `akashml/fp8` · temperature_override 0.6 · max_tokens 8192 · reasoning 미전송.

## 2. 결과

### 세트 A — Edge Computing, 지시 700, common corpus DB (`edge-cc2512-len700.20260907T122752Z.json`)

| 서브섹션 | run1 | run2 | 평균 | 계수 | \|Δ\| | 08-31 temp 0 |
|---|---:|---:|---:|---:|---:|---:|
| Task Offloading Strategies | 1,084 | 976 | 1,030 | 1.47× | 108 | 1,263 (1.80×) |
| On-Device and Edge Inference | 1,079 | 1,214 | 1,146 | 1.64× | 135 | 960 (1.37×) |
| Privacy-Preserving Edge Computing | 849 | 1,133 | 991 | 1.42× | 284 | 762 (1.09×) |
| **전체** (n=6) | | | **1,056** | **1.51×** [1.21–1.73] | sd 117 (CV 11%) | 평균 1.42× [1.09–1.80] |

잘림 0 · 호출당 44~73초 · 출력 1,116~1,519 토큰 · 비용 $0.0208.

### 세트 B — Physical Adversarial, 지시 520, KISTI DB (`physadv-kisti2512-len520.20260907T123400Z.json`)

| 서브섹션 | run1 | run2 | 평균 | 계수 | \|Δ\| | kisti 첫 편 최종본 (temp 0, LCE 후) |
|---|---:|---:|---:|---:|---:|---:|
| Sticker Attacks and Camouflage Attacks | 1,098 | 931 | 1,014 | 1.95× | 167 | 401 |
| Adversarial Training and Input Preprocessing | 832 | 719 | 776 | 1.49× | 113 | 597 |
| Metrics for Evaluating Adversarial Attacks | 1,412 | 797 | 1,104 | 2.12× | 615 | 697 |
| **전체** (n=6) | | | **965** | **1.86×** [1.38–2.71] | sd 233 (CV 24%) | 평균 565 (1.09×) |

잘림 0 · 호출당 43~77초 · 출력 919~1,781 토큰 · 비용 $0.0236.
(오른쪽 열은 초안이 아니라 LCE까지 거친 최종본이라 직접 비교가 아니다. 단, 그 편은 temp 0이었다.)

## 3. 해석

1. **temperature 0.6은 분량을 크게 바꾸지 않는다.** 같은 조건(세트 A)에서 평균 계수 1.42× → 1.51×. 주제별 편차는 오히려 좁아졌다(1.09~1.80 → 1.42~1.64, 2회 평균 기준). 0.6으로 올려서 분량이 폭주하지는 않는다.
2. **지시값에 둔감하다.** 지시 700 → 평균 1,056단어, 지시 520 → 965단어. 기울기 약 0.5단어/지시단어. 초안은 주제와 무관하게 800~1,100단어 근처에 바닥이 있다(08-31의 "350 지시에도 530단어" 관측과 같은 현상, temp 0.6에서는 바닥이 더 높다). `--subsection_len`은 약한 레버이고 **총 분량은 서브섹션 수(section_num × subsection_num)가 지배**한다.
3. **run-to-run 편차는 실재한다.** 같은 프롬프트에서 797 vs 1,412단어(Metrics)까지 벌어진다. 서브섹션 단위 CV 11~24%. 서베이 한 편(17~32 서브)에서는 평균의 CV가 24%/√17 ≈ 6%로 줄어 총 분량 ±1.5k단어 수준이다. **편당 1회 실행이면 분량 ±6%를 오차로 안고 간다**는 뜻이며, recall 편차는 별도로 재야 한다(§4).
4. **잘림·루프 0/12.** 출력 최대 1,781 토큰으로 8,192 가드의 22%. 호출당 43~77초. temp 0에서 45분짜리 호출이 나오던 것과 대비된다. 가드가 정상 호출에 걸리지 않음을 실측으로 확인.
5. **초안→최종 비율은 0.6에서 아직 모른다.** 앵커 0.85(v4-pro, temp 0)를 적용하면 세트 B의 최종 서브당 약 820단어(1.58×). 8섹션 × 2~4서브 = 17~32서브 → 14k~26k단어. kisti 첫 편(temp 0)은 최종 626단어/서브였으므로 0.6에서의 실제 비율은 다음 본편에서 잰다.

## 4. 결정

- **`--subsection_len 520` 유지.** 지시값 둔감성 때문에 역산으로 얻을 게 적고, 최종 계수는 본편 1회로 실측하는 편이 정확하다. 다음 본편의 run.json `coefficient`가 0.6 프로파일의 첫 최종 계수가 된다.
- 다음 본편은 **같은 topic 2회**(각 약 15분·$0.3 예상)로 돌려 recall·refs 겹침의 run-to-run 편차를 잰다. 그 편차가 agent 간 차이보다 작으면 25편은 편당 1회.
- 분량 대역을 조정할 일이 생기면 `--subsection_len`이 아니라 `--subsection_num`·`--section_num`으로 한다.

## 5. 산출물

| 파일 | 내용 |
|---|---|
| `scripts/probe_length.py` | 프로브 스크립트 (writer와 동일 입력, 1차 초안, 순차 호출) |
| `output/probes/*.spec.json` | 프로브 조건 (topic·지시값·rag·서브섹션·description) |
| `output/probes/<label>.<UTC>.json` | 결과 — profile 실측, 호출별 단어·토큰·비용·소요·잘림·검색 id·본문 전문, summary |
| `output/probes/probe_run.log` | 실행 로그 (`*.log`라 git 미추적) |
