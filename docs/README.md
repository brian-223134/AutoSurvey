# docs — 발표·공유용 정리

저장소의 작업 문서(`../README.md`, `../HANDOFF.md`, `../REPRODUCTION.md`, `../SETTING.md`)는
**작업자용**입니다. 이 디렉터리는 **밖에 설명하기 위한** 정리입니다.

| 문서 | 용도 |
|---|---|
| [`evaluation-note.md`](evaluation-note.md) | 평가를 어떻게 했고 **무엇을 못 쟀는지** — 발표에서 가장 방어가 필요한 부분 |
| [`commoncorpus-setup.md`](commoncorpus-setup.md) | Common Corpus DB 반입 × llama-3.3-70b 백본 셋업 — 재현 체인·검증·분량 캘리브레이션·첫 실행 기록 |

## experiments/ — 편별 실행 기록

| 문서 | 용도 |
|---|---|
| [`experiments/edge-computing-experiment.md`](experiments/edge-computing-experiment.md) | Edge Computing 4판 메트릭 — 분량 레버(section/subsection/len) 거동, 단계별 청구, 발표 멘트용 파생 지표 |
| [`experiments/bench-2512-ai1-instruction-tuning.md`](experiments/bench-2512-ai1-instruction-tuning.md) | **벤치마크 `bench-2512` 첫 편** — 누수 차단 end-to-end 검증, 인덱스 빌드 5회 실패 기록, 25편 본배치 전 미결 3건 |

수치는 전부 저장소의 실측값입니다. 출처를 각 표 아래에 적어 뒀으니
발표 중 근거를 물으면 그 파일·스크립트를 열면 됩니다.

> **재현 명령이 필요하면** `../REPRODUCTION.md`, 함정 모음은 `../HANDOFF.md`.
