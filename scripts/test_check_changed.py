"""check_changed.py 시험 — Stop 훅이 두 번째 막기부터는 통과시키는지(stop_hook_active).

시험이 일부러 FAIL 인 상태(기대값을 바꾼 직후 · TDD RED)에서 가드가 없으면 종료를 끝없이 막는다
(10/24 실습 리허설: 9번 연속 막다 Claude Code 가 강제 종료).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_changed.py")


def git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8")


def make_repo(tmp_path):
    (tmp_path / "scripts").mkdir()
    shutil.copy(SCRIPT, tmp_path / "scripts" / "check_changed.py")
    (tmp_path / "harness.config.json").write_text(
        json.dumps({"checks": {"src/": f'"{sys.executable}" -c "import sys; sys.exit(1)"'}}), encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.c").write_text("int a;\n", encoding="utf-8")
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "init")
    (tmp_path / "src" / "a.c").write_text("int a = 1;\n", encoding="utf-8")  # 바뀐 경로 → 실패하는 확인 명령
    return tmp_path


def run(repo, stdin: bytes):
    return subprocess.run([sys.executable, str(repo / "scripts" / "check_changed.py")], input=stdin,
                          capture_output=True, cwd=repo)


def test_first_stop_blocks_on_failing_check(tmp_path):
    p = run(make_repo(tmp_path), json.dumps({"hook_event_name": "Stop", "stop_hook_active": False}).encode())
    assert p.returncode == 2


def test_second_stop_passes_when_hook_already_active(tmp_path):
    p = run(make_repo(tmp_path), json.dumps({"hook_event_name": "Stop", "stop_hook_active": True}).encode())
    assert p.returncode == 0, p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
    assert "stop_hook_active" in p.stdout.decode("utf-8", "replace")  # 그냥 통과가 아니라 까닭을 남긴다


def test_manual_run_without_stdin_still_checks(tmp_path):
    p = run(make_repo(tmp_path), b"")
    assert p.returncode == 2
