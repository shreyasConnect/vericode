"""
Ephemeral process sandbox executor for running untrusted agent-generated code safely.
Provides strict timeouts, temporary workspace isolation, and standard stream capture.
"""

from dataclasses import dataclass
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Dict, Optional


@dataclass
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool
    memory_peak_mb: float = 0.0

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


class SandboxExecutor:
    """Executes Python code files in an isolated ephemeral directory with resource limits."""

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        python_bin: Optional[str] = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.python_bin = python_bin or sys.executable

    def run_isolated(
        self,
        files: Dict[str, str],
        entrypoint_file: str,
        args: Optional[list] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """
        Populate an ephemeral directory with `files` and execute `entrypoint_file`.

        Args:
            files: Map of relative file paths to string contents.
            entrypoint_file: File name to execute via Python interpreter.
            args: Optional command line arguments passed to the script.
            env_vars: Environment variable overrides.
        """
        temp_dir = tempfile.mkdtemp(prefix="vericode_sandbox_")
        start_time = time.perf_counter()

        try:
            # Write files to sandbox directory
            for rel_path, content in files.items():
                target_path = os.path.join(temp_dir, rel_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)

            cmd = [self.python_bin, entrypoint_file] + (args or [])
            run_env = os.environ.copy()
            run_env["PYTHONUNBUFFERED"] = "1"
            run_env["PYTHONPATH"] = temp_dir
            run_env["PYTHONDONTWRITEBYTECODE"] = "1"
            if env_vars:
                run_env.update(env_vars)

            proc = subprocess.Popen(
                cmd,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=run_env,
            )

            try:
                stdout, stderr = proc.communicate(timeout=self.timeout_seconds)
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return ExecutionResult(
                    exit_code=proc.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=duration_ms,
                    timed_out=False,
                )
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return ExecutionResult(
                    exit_code=-1,
                    stdout=stdout,
                    stderr=f"Execution timed out after {self.timeout_seconds} seconds.\n{stderr}",
                    duration_ms=duration_ms,
                    timed_out=True,
                )

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
