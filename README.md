# sure-lab-harness — SDD 하네스 엔진 (실습 배포판)

> 교육용 배포판 — 개인 용도로 쓰고 재배포는 문의 바랍니다.

`/harness` 로 같이 설계하고 `scripts/execute.py` 로 step 마다 새 세션에서 실행하는 하네스 엔진이다. 실습 저장소 셋에 모두 설치한다.

| 쓰는 저장소 | 설치하는 때 |
|---|---|
| 예제코드저장소(lab1-code) · 개발 브랜치 | 2-2-준비-1 |
| PR리뷰어저장소(lab2-reviewer) | 2-4-준비-2 |
| CICD저장소(lab3-cicd) | 3-2-1 전 |

## 들어 있는 것

| 경로 | 무엇 |
|---|---|
| `.claude/commands/harness.md` · `review.md` | `/harness`(설계 → step 파일) · `/review` |
| `.claude/rules/lab-ops.md` | 실습 운영 규칙(결과 형식 · 브랜치 · 태그 · 되돌리기) |
| `.claude/settings.json` | Stop 훅(`scripts/check_changed.py`) · 위험 명령 차단 훅 |
| `harness.config.json` | 경로별 확인 명령(빈 칸은 건너뜀) |
| `scripts/execute.py` · `check_changed.py` · `test_execute.py` | 엔진 · Stop 훅 · 엔진 시험 |
| `docs/PRD.md` · `ARCHITECTURE.md` · `ADR.md` | 문서 틀(`/harness` 가 채운다) |

## 설치 — 대상 저장소 루트에서

1. 위 표의 파일을 같은 경로로 복사한다. 대상에 같은 이름의 `docs/*.md` 가 이미 있으면 덮어쓰지 않는다.
2. `.claude/settings.json` 이 대상에 이미 있으면 통째로 바꾸지 말고 `hooks` 항목만 합친다(`language` 등 기존 값은 둔다).
3. 새 Claude Code 세션을 연다(훅 · 명령은 새 세션부터 잡힌다).

확인: `python -m pytest scripts/test_execute.py -q` 가 종료 코드 0 · `/hooks` 에 Stop · PreToolUse 훅이 보인다 · `/harness` 가 명령 목록에 보인다.

## 쓰는 법

`/harness` → 같이 설계(빠진 것은 AI 가 묻는다) → step 승인 → `python scripts/execute.py <task>`. task 의 `phases/<task>/index.json` 의 `docs` 에 그 흐름의 문서 폴더를 적는다.

## 출처

`vsm-lab-template` 커밋 `1c7e47e` 의 하네스 엔진 부분을 그대로 옮겼다. 엔진은 jha0313/harness_framework 를 바탕으로 실습에 맞게 고친 판이다.
