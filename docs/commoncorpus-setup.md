# Common Corpus DB 반입 × llama-3.3-70b 백본 — 셋업 기록 (2026-08-31)

기존 실험(배포본·최신화본 DB × haiku·deepseek 백본)과 **두 축이 동시에** 바뀐다:
corpus 가 `asg-common-corpus` 반출본으로, 백본이 `meta-llama/llama-3.3-70b-instruct`
(akashml/fp8, temperature=0)로. 따라서 **이 축의 산출물은 기존 산출물과 같은 표에
놓지 않는다.**

절차 원문: `/data2/chanjoong/survey-agent/asg-common-corpus/docs/autosurvey-usage.md`
(경로 B — AutoSurvey 코드 수정 0줄, DB 디렉터리만 추가하고 `--db_path` 변경).

## 1. DB — `database_commoncorpus-2512/`

| 항목 | 값 |
|---|---|
| 원본 | `../asg-common-corpus/data/exports/example-2512.autosurvey.json` → `arxiv_paper_db.json` |
| 규모 | **947,463편** (TinyDB `cs_paper_info`, 필드 `id,title,url,date,abs,cat`) |
| view | `example-2512` — cutoff **2025-12-31** + GT 1건 제외(예시 view) |
| date 범위 실측 | 1991-08-01 ~ **2025-12-31** (cutoff 준수 확인) |
| manifest | `content_sha256: 3dece35bc085a280ce17eb08cbd06306bcb36d3873b4463988d346ce1d9ca75e` |
| | `base_corpus_sha256: 6bb204d15111f2edd944ac47112a0a46f9b9bf252d5e20d3a719a3c439d4285e` |

manifest 사본은 DB 디렉터리에 동봉(`example-2512.autosurvey.json.manifest.json`).
view→corpus→upstream 의 sha 체인이 이어져 있어 이 파일 하나로 재현 경로가 완성된다.

⚠ **실제 실험 전 재-export 필요**: 이 view 는 예시다. benchmark cutoff 와 GT survey
제외 목록이 확정되면 asg-common-corpus 쪽 `create-view` → `export-agent-db` 로 새로
만들 것 (위 절차 문서 §0).

**기존 DB 와 다른 점** (전부 런타임 무해, 상세는 절차 문서 §3):
`id` 가 버전 접미사 없는 base id (`1811.06122`) — 교차 비교 시 base id 로 정합.
`date` 는 first_public_date (53% day / 47% month 정밀도, month 는 월초).
`cat` 은 arXiv 카테고리가 아니라 OpenAlex subfield 명. `authors` 없음.
GT 제외는 view 단계에서 이미 적용 — retrieval 쪽 제외 로직 불필요.

## 2. 임베딩 인덱스 빌드

```bash
CUDA_VISIBLE_DEVICES=7 conda run -n autosurvey python scripts/build_index.py \
    --db-path ./database_commoncorpus-2512 --device cuda    # batch 256 (기본)
```

- 소요 **약 72분** (L40S 1장: title 임베딩 ~6분 + abstract ~62분 + FAISS/저장 ~4분).
  usage 문서의 "908K 약 30분"보다 길었다 — abstract 배치가 1.07s/it 로 title(9.6it/s)의
  1/10 속도. 다음에 예상 시간을 잡을 때는 abstract 쪽 기준으로.
- 산출: `faiss_paper_title_embeddings.bin` / `faiss_paper_abs_embeddings.bin`
  (각 2.9GB, 947,463 × dim 768) + `arxivid_to_index_abs.json`
- 검증: `check_db.py --verify-embeddings 20` → 파일·스키마·FAISS/id 매핑 정합·검색
  스모크 전부 OK. 단 **저장 벡터 재현이 최저 cos 0.9848**로 임계(0.999) 미달 경고.
  별도 판별로 **무해 판정**:
  - title 은 전 위치 cos 1.0000, abs 만 0.9875~0.9944 — 매핑 논문 vs 무관 논문
    (0.46~0.64)이 명확히 분리되어 **순서 어긋남 아님** (그 사고였다면 cos 가 무관
    수준으로 떨어짐)
  - 빌드와 동일한 배치 구성으로 재인코딩해도 0.9875 그대로 → 배치 패딩 가설 기각.
    단독/배치 재인코딩끼리는 완전 일치 → 95만 건을 지난 장시간 빌드 프로세스
    후반(abs 단계)의 GPU 커널 선택 차이로 인한 수치 변동으로 결론
  - 자기 자신과 0.99대 vs 무관 논문과 0.6대 — top-60 검색에 미치는 영향 무시 가능.
    (참고: `database_2026-08` 검증은 cos 1.000000 이었음 — 이 임계는 append 순서
    사고 검출용이라, 이 DB 처럼 처음부터 새로 빌드한 경우엔 과민할 수 있다)
- 임베딩 모델 `nomic-ai/nomic-embed-text-v1` — **검색 시 `--embedding_model` 을
  반드시 동일하게** (다르면 에러 없이 검색 품질만 무너짐)

## 3. 백본 프로파일 — llama-3.3-70b @ akashml/fp8, temperature 0

`.env` 가 백본 프로파일 구조로 바뀌었다(커밋 `2622d28`) — 모델·provider 핀·
temperature·reasoning·길이 계수를 한 블록으로 묶어 블록째 갈아끼운다.

| 항목 | 값 | 근거 |
|---|---|---|
| 모델 | `meta-llama/llama-3.3-70b-instruct` | — |
| provider 핀 | `AUTOSURVEY_PROVIDER=akashml/fp8` | 실호출로 `provider=AkashML` 응답 확인. fp8, max_out **128K**(잘림 여유), ctx 131K, **$0.20/$0.52 per M** (2026-08-31) |
| temperature | `AUTOSURVEY_TEMPERATURE=0` | 이번에 도입한 전역 오버라이드(`src/model.py`). 원본은 아웃라인·본문 1 하드코딩. 비우면 원본 동작 |
| reasoning | 비움 (필드 미전송) | 비추론 모델. `off` 를 보내도 무해함은 확인했으나 원본 페이로드 유지 |

**함정 (실측)**: llama-3.3-70b 에는 이전 백본의 핀 `parasail/fp8` 도 **존재**한다.
main.py 사전 검사는 tag 존재만 보므로, `.env` 를 안 바꾸고 돌리면 에러 없이 엉뚱한
provider 로 나간다. 백본 전환 시 `.env` 프로파일 블록부터 바꿀 것.

**akashml 레이트리밋 (실측)**: **순차** 요청 3개째에서 429("temporarily rate-limited
upstream")가 났다. parasail(동시 8 안정)보다 빡빡하다. 본편은 `MAX_THREADS=1`
(8섹션 × 1 = 동시 8) + `MAX_RETRY=10` 으로 시작할 것.

## 4. 분량 통제 — 목표 20k~25k 단어

v4-flash 산출물이 46k~69k 단어(계수 1.76×)로 표준 구간(12k~25k, `check_survey.py`)을
크게 벗어난 것이 확인되어, 이 축부터 **20k~25k 를 조준**한다. 방법은 README §4 의
캘리브레이션 — 프롬프트는 바꾸지 않고 `--subsection_len`(하한 지시값)을 모델 계수로
나눠 넣는다.

**llama-3.3-70b 프로브** (본편과 같은 SUBSECTION_WRITING_PROMPT, corpus 초록 60편,
temp 0, akashml/fp8, 지시 700단어):

| 프로브 | 본문 | 계수 |
|---|---|---|
| Task Offloading Strategies | 1,263단어 | 1.80× |
| On-Device and Edge Inference | 960단어 | 1.37× |
| Privacy-Preserving Edge Computing | 762단어 | 1.09× |

프로브 평균 **1.42×** (n=3, 편차 1.09~1.80 — 서브섹션 주제에 따라 실제로 크게
다르다는 뜻. 총 분량은 ~36개 평균이므로 평균값을 쓴다. 비용 $0.011).
프로브는 1차 작성 직후 값이라 반영·LCE 를 거친 최종본은 짧아진다 — 유일한 실측
앵커인 v4-pro(프로브 1.96× → 최종 1.67×, 비율 0.85)를 적용해 **추정 최종 계수 1.21×**.

역산: 섹션 수는 지시를 넘길 수 있고(8 지시 → v4-flash 10 관측) 서브섹션 상한 4 는
코드가 보장하므로, 서브섹션 32~40개를 가정해 서브당 625단어를 조준 →
`subsection_len = 625 / 1.21 ≈ **520**`.

| 총 분량 (520 × 1.21 = 629단어/서브) | 서브 32개 | 36개 | 40개 |
|---|---|---|---|
| | 20.1k | 22.6k | 25.2k |

계수 추정이 ±0.2 어긋나면 구간을 벗어날 수 있다 — 결과로 실측 계수를 갱신하고,
빗나가면 그 값으로 1회 재역산한다.

## 5. 토픽 — "Edge Computing" (corpus 지원도 실측)

제목 매칭 기준: 합집합 **2,097편** (edge computing 943 / MEC 410 / edge
inference·on-device 449 / edge intelligence·AI 224 / edge-cloud 193 / fog 178).
2024 년 이후 607편(29%) — 고전 주제 + 최근 활동(edge inference·intelligence 쪽).
outline_reference_num 1200 / rag_num 60 을 받치기에 충분.

참고로 잰 다른 후보(2024~ 비중): LLM agent 965편(96%), Multimodal LLM 2,423편(86%),
Test-time scaling 115편(100%), VLA 97편(97%).

## 6. 실행 기록 — Edge Computing 1편 (2026-08-31)

```bash
export CUDA_VISIBLE_DEVICES=7 && source .env          # llama 프로파일 (akashml/fp8, temp 0)
export AUTOSURVEY_MAX_THREADS=1 AUTOSURVEY_MAX_RETRY=10
setsid nohup conda run --no-capture-output -n autosurvey python -u main.py \
  --topic "Edge Computing" --saving_path ./output/llama-3.3-70b-cc2512/ \
  --db_path ./database_commoncorpus-2512 --embedding_model "$AUTOSURVEY_EMBEDDING_MODEL" \
  --model "$AUTOSURVEY_MODEL" --api_url "$AUTOSURVEY_API_URL" \
  --section_num 8 --subsection_len 520 --rag_num 60 \
  --outline_reference_num 1200 --subsection_num 4 > <log> 2>&1 < /dev/null &
```

| 항목 | 값 |
|---|---|
| 산출물 | `output/llama-3.3-70b-cc2512/Edge Computing.{md,json}` |
| 결과 | **8섹션 / 25서브섹션 / 18,264단어**(.md) · 15,794단어(중복 헤딩 제거) |
| 참고문헌 | 219개, 인용 324회, 댕글링 0, 포맷 누출 0 — `check_survey.py` **OK** |
| 계수 실측 | **1.21×** (서브당 지시 520 → 실제 632단어) — §4 추정 1.21×가 그대로 적중 |
| 비용 | **$0.2958** (outline $0.0885 + writer $0.2073), 재시도 3회(전부 429, 1~2차에 성공), 잘림·실패 0 |
| 시간 | **13분** (06:17 → 06:30) |
| DB | `database_commoncorpus-2512` (manifest sha `3dece35b…`, §1) |

**분량 판정**: 저장소 기준 표준 구간(12k~25k) **ok**. 단 이번 목표(20k~25k)에는
미달 — 원인은 계수가 아니라 **서브섹션 개수**다. `--subsection_num 4`는 상한이라
llama 가 섹션당 평균 3.1개(25개)만 썼고, 역산은 32~40개를 가정했다.
→ 같은 구조(25서브)로 22.5k 를 노리면 `check_survey.py` 역산대로
**`--subsection_len 741`** (25 × 741 × 1.21 ≈ 22.4k). 서브가 32개로 나오면 28.7k로
초과할 수 있으니, 상한을 정확히 채우게 하려면 개수 미달분을 감안해 700 안팎이 안전.

**사건 기록** (재현 시 참고):
- 1차 시도(05:20)는 아웃라인+본문 대부분 진행 중 **Claude Code 재시작에 프로세스가
  휘말려 강제 종료** — 저장 전이라 산출물 없이 ~$0.22 매몰. AutoSurvey 는 체크포인트가
  없으므로 **장시간 실행은 반드시 `setsid nohup … &` 로 세션과 분리해서 띄울 것.**
- 1차 시도 때 akashml 이 심하게 조여(순차 요청도 429, 낙오 섹션 2개가 10분+ 응답 대기)
  40분+ 이 걸리고 있었으나, 2차(06:17)는 같은 설정으로 **13분** — 스로틀은 시간대
  변수다.
- **provider 방침 (2026-08-31 결정): `akashml/fp8` 유지.** `nebius/fp8` 은 단가는
  낮지만($0.13/$0.40) **동시처리량이 제일 낮아 제외** (다운타임은 적음 — 실사용 경험).
  부득이 바꾼다면 `parasail/fp8` (v4-flash 시리즈에서 동시 8 안정 실적). 바꾸는 경우
  통제 변수가 달라지므로 .env 프로파일 블록과 run 기록에 반드시 남길 것.

## 7. 분량 대역 실험 — 같은 토픽 3판 (2026-08-31)

배경: 42쪽(§6)에 대해 "독자가 안 읽는다, 20쪽 근방이어야"는 피드백. 원 논문 자체가
8k/16k/32k/64k **토큰**을 실험 축으로 썼으므로(§3, Table 2 — 품질 차이는 근소했음),
짧은 설정은 시스템 변형이 아니라 **저자들이 평가한 설정 공간 안의 선택**이다.
8k 토큰(≈6천 단어)을 조준하며 레버들의 실제 거동을 쟀다.

**레버 실측 — 셋 중 하드는 하나뿐:**

| 레버 | 거동 |
|---|---|
| `--subsection_len` | **~540단어에서 포화.** 350을 지시해도 서브당 514~538단어(프로브: 지시 350 → 530·605단어). llama 의 서브섹션 자연 바닥. 지시 520(→632단어)까지는 1.21× 선형이었음 |
| `--section_num` | **soft + 확률적.** `[SECTION NUM]` 이 러프 아웃라인 프롬프트에만 있고 **merge 프롬프트에는 개수 제약이 없다.** 5 지시 → 한 번은 8(판 B), 한 번은 5(판 C). temp 0 이어도 retrieval shuffle 로 러프 아웃라인이 매번 달라 merge 가 흔들린다. (v4-flash 의 8→10 도 같은 원인) |
| `--subsection_num` | **하드** (코드가 초과분 절단). 충족률: 상한 4→3.1 / 상한 3→2.75 / 상한 2→2.0 |

**3판 비교** (전부 llama-3.3-70b @ akashml/fp8, temp 0, rag 60, outline_ref 1200,
DB `commoncorpus-2512`, check_survey 인용 무결성 전부 OK):

| 판 | 디렉터리 (`output/`) | 파라미터 (sec/cap/len) | 실제 구조 | 단어(.md) | refs | PDF | 비용 | 시간 |
|---|---|---|---|---|---|---|---|---|
| A 본편 | `llama-3.3-70b-cc2512` | 8 / 4 / **520** | 8섹 25서브 | 18,264 | 219 | **42쪽** | $0.296 | 13분 |
| B 시도1 | `llama-3.3-70b-cc2512-8k` | 5 / 3 / 350 | **8섹**(드리프트) 22서브 | 13,531 | 161 | **32쪽** | $0.258 | 11분 |
| C 시도2 | `llama-3.3-70b-cc2512-20p` | 5 / 2 / 350 | 5섹 10서브 | **6,033** | 83 | **15쪽** | $0.154 | 7분 |
| D 관철검증 | `llama-3.3-70b-cc2512-8k-v2` | **5(관철)** / 2 / 350 | 5섹 10서브 | 5,619 | 73 | **14쪽** | $0.153 | 7분 |

- **판 C 가 8k 토큰 목표 달성**: 6,033단어 ≈ 8k 토큰, 15쪽(≤20쪽), refs 83은
  원저자 예시 3편(74~88)과 같은 대역. ⚠ 디렉터리명 주의 — `-8k` 는 목표였다가
  섹션 드리프트로 32쪽이 된 판 B 이고, 실제 8k 토큰 달성판은 `-20p`(판 C)다.
  saving_path 를 실행 당시 그대로 보존하느라 이름과 결과가 어긋났다.
- `check_survey.py --length` 는 B·C 에 "짧음" 경고를 낸다 — 표준 구간(12k~25k)은
  본편 대역 기준이므로, **의도된 8k/16k 대역 산출물에는 무시**하고 이 표를 근거로 볼 것.
- 분량이 절반이면 비용도 절반 근방으로 준다 (writer 입력이 서브섹션 수에 비례).
- 단계별 청구 (outline + writer, 재시도 포함): A $0.0885+$0.2073(재시도 3) /
  B $0.0872+$0.1705(재시도 2) / C $0.0782+$0.0762(0) / D $0.0778+$0.0750(0).
  추정치와 청구치 오차는 전부 1% 미만 — provider 핀 + 추론 0 이라 단가표대로 맞는다.

**대역별 레시피** (llama-3.3-70b 실측 기반):

| 목표 | 파라미터 | 기대 |
|---|---|---|
| 8k 토큰 / ~15쪽 | `--section_num 5 --subsection_num 2 --subsection_len 350` | ~10서브 × ~520 ≈ 5~6k단어. 섹션 드리프트(→8) 시 ~16서브/8.5k로 벗어날 수 있음 — 결과 확인 필수 |
| 16k 토큰 / ~30쪽 | `--section_num 8 --subsection_num 3 --subsection_len 350` | ~22서브 × ~540 ≈ 12k단어 (판 B 가 사실상 이 대역) |
| 20k~25k / ~50쪽 | `--section_num 8 --subsection_num 4 --subsection_len 741` | §6 역산 |

**→ 해소 (2026-08-31, 커밋 `64be6f3`)**: `--enforce_section_num` 도입. 논문 §2 의
"The outline predetermines the number of sections" 서술을 근거로, 플래그를 주면
merge 프롬프트에 개수 문장을 삽입해 관철한다. 플래그가 없으면(기본) merge 프롬프트가
원본과 **글자 단위로 같음**을 렌더 바이트 동일성 테스트로 확인했다.
판 D 가 검증 실행: 섹션 5 고정 성공. (단 판 C 도 우연히 5 였으므로 1회 실행은
통계적 증명이 아니라 정합성 확인이다 — 드리프트 재발 시 이 플래그가 기본 처방)
**짧은 대역(8k/16k) 실행에서만 켜고, 본편 대역은 원본 동작을 유지**하는 것을 규약으로 한다.
