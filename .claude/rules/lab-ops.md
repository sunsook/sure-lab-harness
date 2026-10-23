# 실습 운영 규칙 — 배포본에 들어 있다

이 저장소에서 늘 지키는 형식 · 이름 · 브랜치 · 태그 규칙이다. 판단 기준(기대값 출처 · 고쳐도 되는 것)은 교육생이 2-① 에서 CLAUDE.md 에 적는다.

- 검사 결과 JSON: {"check", "status": PASS|FAIL|ERROR, "source", "findings": [{"id", "where", "expected", "actual", "fix_hint", "basis", "back_to"}]} · basis = 근거 요구사항 · 기준 · back_to = 코드 수정 | 시험 추가 | 요구사항 | 시험 연결 · 종료 코드 0 문제없음 · 1 문제 찾음 · 2 검사 실패 · 시험마다 첫 줄 주석 @req SR-xxx(꼴이 깨지면 검사 실패 · 없으면 추적 누락).
- Finding id = <요구사항 ID>-<종류>(예: SR-002-BOUNDARY) · 같은 문제는 어느 검사에서도 같은 id.
- 하네스 eval(정답 묶음) — 건 = 하네스에 주는 작업 → 하네스가 해야 할 행동. 검사 함수의 단위 시험은 eval 이 아니다.
- 작업은 main 에서 시작 · scenario/* 는 확인용, 끝나면 main 으로.
- 「모듈 끝 태그 남겨줘: <태그>」 → main 으로 → 바뀐 파일만 add → 커밋 「<태그>: 한 줄 요약」 → git tag <태그> → git push origin main --tags.
- 「<태그> 상태로 되돌려」 → 지금 상태를 backup/<시각> 브랜치로 → 이력을 지우지 않고 그 태그의 파일로 되돌린 커밋.
