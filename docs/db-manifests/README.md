# 삭제한 DB 디렉터리의 메타데이터 (2026-09-30)

2026-09-30 corpus 가 `kisti-2608-r4` 로 바뀌면서 더 쓰지 않는 AutoSurvey DB 3개(약 37 GB)를 지웠다.
인덱스·레코드(수 GB)는 버리고, 재현 체인을 닫는 데 필요한 작은 파일만 여기 옮겨 둔다.
파일 지문(md5)은 `REPRODUCTION.md` §3-C.

| 디렉터리 | 편수 | view sha | 쓰인 곳 | 남긴 파일 | 다시 만들려면 |
|---|---:|---|---|---|---|
| `database_kisti-kisti-2512-v1/` | 1,651,701 | `c7b8d4e7` | sec #3 physical-adversarial 4편(정책 없음) | export manifest 2 · `build_db.log.gz`(nomic 전체 빌드 2h17m) | v1 export 본문은 corpus 측에도 없다(manifest 만 `data/views/kisti-2512-v1/exports_v1/`). view `data/views/kisti-2512-v1/` 는 보존돼 있어 `export.py --format autosurvey` → `build_db.sh`(GPU 약 2h)로 재생성 가능 — 결과가 바이트 동일한지는 미검증 |
| `database_kisti-kisti-2512/` | 1,651,487 | `591b4325` | 정책 스모크(`docs/retrieval-policy.md` §8) · kisti-2608 의 base | export manifest 2 · `view_diff_manifest.json`(v1 → v2 차분) | `kisti_data/data/exports/kisti-2512.autosurvey.json` 으로 `kisti_data/adapter/autosurvey/build_db.sh`(GPU 약 2h) |
| `database_kisti-kisti-2608-r2/` | 1,696,254 | `6727c7b8` | 산출물 없음 · r4 의 base | `append_manifest.json`(base kisti-2608 + 32,550) · `append_source_manifest.json` · export manifest 2 · `build_db.log.gz` | `scripts/append_snapshot.py --base ./database_kisti-kisti-2608 --new kisti_data/data/exports/kisti-2608-r2.autosurvey.minus-kisti-2608.json` (7분) |

- 로그는 저장소 `.gitignore` 의 `*.log` 를 피하려고 gzip 으로 남겼다. `database_kisti-kisti-2512/build_db.v1.log` 는 v1 디렉터리의 `build_db.log` 와 바이트 동일이라 하나만 남겼다.
- r4(`database_kisti-kisti-2608-r4/`)는 r2 를 base 로 append 한 **독립 사본**이다(하드링크·심링크 없음) — r2 삭제의 영향이 없다. base 구간은 r2 와 바이트 동일로 검증됐다(corpus 측 AGENT-HANDOFF §0).
- 남겨 둔 DB: `database/`(저자 배포본, 재반입 불가) · `database_2026-08/`(`_harvest/` 가 kisti_data `build_arxiv_snapshot.py` 입력) · `database_kisti-kisti-2608/`(LLM×MapReduce-V2 kisti-2608 pool 의 `db_path`) · **`database_kisti-kisti-2608-r4/`(현행)**.
