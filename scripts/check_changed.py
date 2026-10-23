#!/usr/bin/env python3
"""Stop 훅 — 바뀐 경로에 맞는 확인 명령만 돌린다.

harness.config.json 의 "checks" 는 {경로 앞부분: 명령}. 예:
    {"checks": {"src/": "python scripts/run_tests.py", "tests/": "python scripts/run_tests.py"}}

바뀐 경로 = 커밋되지 않은 변경(git diff HEAD) + 추적 안 되는 새 파일.
종료 코드: 0 통과 또는 확인할 것 없음 · 2 확인 실패(출력이 Claude 에게 돌아간다).
이미 한 번 막은 뒤 다시 불리면(stdin 의 stop_hook_active) 실패가 남아도 0 — 시험이 일부러 FAIL 인 상태
(기대값을 바꾼 직후 · TDD RED)에서 종료를 끝없이 막지 않는다.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "harness.config.json"


def changed_paths() -> list[str]:
    # 첫 커밋 전에는 HEAD 가 없다 — 그때는 스테이징된 파일 전부가 바뀐 것이다
    has_head = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=ROOT,
                              capture_output=True).returncode == 0
    diff = ["git", "diff", "--name-only", "HEAD"] if has_head else ["git", "diff", "--name-only", "--cached"]
    out = []
    for args in (diff, ["git", "ls-files", "--others", "--exclude-standard"]):
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print(f"check_changed: {' '.join(args)} 실패 — {r.stderr.strip()}", file=sys.stderr)
            sys.exit(2)
        out += [p for p in r.stdout.splitlines() if p]
    return sorted(set(out))


def stop_hook_active() -> bool:
    """Claude Code 가 stdin JSON 에 넣는 stop_hook_active — 손으로 돌릴 때(터미널 · 빈 입력)는 거짓."""
    if sys.stdin is None or sys.stdin.isatty():
        return False
    try:
        raw = sys.stdin.buffer.read().decode("utf-8")
        return bool(json.loads(raw).get("stop_hook_active")) if raw.strip() else False
    except (ValueError, AttributeError):
        return False


def main() -> int:
    # Windows 콘솔 기본(cp949)으로는 한글 · 기호 출력이 깨진다
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    already_blocked = stop_hook_active()
    if not CONFIG.exists():
        print("check_changed: harness.config.json 없음 — 확인할 경로 없음")
        return 0
    try:
        checks = json.loads(CONFIG.read_text(encoding="utf-8")).get("checks") or {}
    except json.JSONDecodeError as e:
        print(f"check_changed: harness.config.json 을 읽지 못함 — {e}", file=sys.stderr)
        return 2

    paths = changed_paths()
    # 같은 명령은 한 번만 — 순서는 config 에 적힌 순서
    commands = []
    for prefix, cmd in checks.items():
        if cmd and cmd not in commands and any(p.startswith(prefix) for p in paths):
            commands.append(cmd)
    if not commands:
        print("check_changed: 바뀐 경로 중 확인할 것 없음")
        return 0

    failed = []
    for cmd in commands:
        r = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True, encoding="utf-8")
        print(f"check_changed: {cmd} → 종료 코드 {r.returncode}")
        if r.returncode != 0:
            failed.append(cmd)
            print(f"--- {cmd} ---\n{r.stdout}{r.stderr}", file=sys.stderr)
    if failed and already_blocked:
        print(f"check_changed: 실패 {len(failed)}건이 남았지만 이미 한 번 막았다(stop_hook_active) — 이번엔 통과")
        return 0
    if failed:
        print(f"check_changed: 실패 {len(failed)}건 — {', '.join(failed)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
