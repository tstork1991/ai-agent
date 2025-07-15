# functions/run_python.py
from __future__ import annotations
import os, sys, subprocess


def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    """
    Execute a Python file inside *working_directory* with optional CLI *args*.

    Returns a formatted string that always begins with either:
      • "STDOUT:" / "STDERR:" / "Process exited …", or
      • "Error:" on failure / guard-rail breach.
    """
    args = args or []

    try:
        work_abs = os.path.abspath(working_directory)
        target_abs = os.path.abspath(os.path.join(work_abs, file_path))

        # ── Guard-rails ────────────────────────────────────────────
        if not target_abs.startswith(work_abs):
            return (
                f'Error: Cannot execute "{file_path}" as it is outside the '
                "permitted working directory"
            )

        if not os.path.isfile(target_abs):
            return f'Error: File "{file_path}" not found.'

        if not target_abs.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        # ── Run the subprocess ────────────────────────────────────
        cp = subprocess.run(
            [sys.executable, target_abs, *args],
            cwd=work_abs,
            capture_output=True,
            text=True,
            timeout=30,
        )

        chunks: list[str] = []
        if cp.stdout.strip():
            chunks.append("STDOUT:\n" + cp.stdout.rstrip())
        if cp.stderr.strip():
            chunks.append("STDERR:\n" + cp.stderr.rstrip())
        if cp.returncode != 0:
            chunks.append(f"Process exited with code {cp.returncode}")

        return "\n".join(chunks) if chunks else "No output produced."

    except Exception as e:
        return f"Error: executing Python file: {e}"
