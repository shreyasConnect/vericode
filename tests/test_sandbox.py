"""
Tests for Sandbox Executor.
"""

from vericode.sandbox.executor import SandboxExecutor


def test_sandbox_runs_successfully():
    sandbox = SandboxExecutor(timeout_seconds=5.0)
    files = {
        "hello.py": "print('SANDBOX_OK')"
    }
    res = sandbox.run_isolated(files, "hello.py")
    assert res.passed is True
    assert "SANDBOX_OK" in res.stdout
    assert res.exit_code == 0
    assert not res.timed_out


def test_sandbox_times_out():
    sandbox = SandboxExecutor(timeout_seconds=1.0)
    files = {
        "loop.py": "import time; time.sleep(5); print('DONE')"
    }
    res = sandbox.run_isolated(files, "loop.py")
    assert res.timed_out is True
    assert res.passed is False
    assert "timed out" in res.stderr
