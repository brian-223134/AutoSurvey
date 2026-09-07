# docs — 발표·공유용 정리

저장소의 작업 문서(`../README.md`, `../HANDOFF.md`, `../REPRODUCTION.md`, `../SETTING.md`)는
**작업자용**입니다. 이 디렉터리는 **밖에 설명하기 위한** 정리입니다.

| 문서 | 용도 |
|---|---|
| **[`direction-2026-09.md`](direction-2026-09.md)** | **현재 실험 방향(정본)** — KISTI corpus 벤치마크: DB·디코딩 프로파일·분량 비통제·평가 규약·실측·결정 로그 |
| [`evaluation-note.md`](evaluation-note.md) | 평가를 어떻게 했고 **무엇을 못 쟀는지** — 발표에서 가장 방어가 필요한 부분 |
| [`commoncorpus-setup.md`](commoncorpus-setup.md) | (기록) Common Corpus DB 반입 × llama-3.3-70b 백본 셋업 — **asg-common-corpus는 2026-09-07부로 미사용** |

## experiments/ — 편별 실행 기록

| 문서 | 용도 |
|---|---|
| [`experiments/edge-computing-experiment.md`](experiments/edge-computing-experiment.md) | Edge Computing 4판 메트릭 — 분량 레버(section/subsection/len) 거동, 단계별 청구, 발표 멘트용 파생 지표 |
| [`experiments/bench-2512-ai1-instruction-tuning.md`](experiments/bench-2512-ai1-instruction-tuning.md) | **벤치마크 `bench-2512` 첫 편** — 누수 차단 end-to-end 검증, 인덱스 빌드 5회 실패 기록, 25편 본배치 전 미결 3건 |
| [`experiments/kisti-2512-sec3-physical-adversarial-attacks.md`](experiments/kisti-2512-sec3-physical-adversarial-attacks.md) | **KISTI DB `kisti-2512` 첫 편** — 인덱스 빌드·argmax 검증, DOI/arXiv 혼합 id 처리, 누수 차단, §2.1 반복 루프 결함과 본배치 전 미결 4건 |
| [`experiments/probe-temp06-length-coefficient.md`](experiments/probe-temp06-length-coefficient.md) | **디코딩 프로파일 변경(temp 0.6 · max_tokens 8K) 근거 + 길이 계수 재측정** — 프로브 12회, 초안 계수 1.51×/1.86×, run-to-run CV 11~24%, 잘림 0, `--subsection_len 520` 유지 결정 |
| [`experiments/kisti-2512-sec3-temp06-runs.md`](experiments/kisti-2512-sec3-temp06-runs.md) | **temp 0.6 본편 3회(r1 가드만 / r2·r3 가드+잘림 재요청)** — 루프 오염 2→0, 같은 코드 쌍 recall 8.1 vs 11.4%(±1.7%p 잠정), refs Jaccard 0.11~0.18, 분량은 통제하지 않기로 결정 |

수치는 전부 저장소의 실측값입니다. 출처를 각 표 아래에 적어 뒀으니
발표 중 근거를 물으면 그 파일·스크립트를 열면 됩니다.

> **재현 명령이 필요하면** `../REPRODUCTION.md`, 함정 모음은 `../HANDOFF.md`.
