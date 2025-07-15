# functions/write_file.py
from __future__ import annotations
import os


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """
    Safely write *content* to *file_path* as long as the path stays inside
    *working_directory*.  Returns a success or error string (never raises).
    """
    try:
        work_abs = os.path.abspath(working_directory)
        target_abs = os.path.abspath(os.path.join(work_abs, file_path))

        # Guard-rail: must stay inside working_directory
        if not target_abs.startswith(work_abs):
            return (
                f'Error: Cannot write to "{file_path}" as it is outside '
                "the permitted working directory"
            )

        # Ensure parent dirs exist
        parent_dir = os.path.dirname(target_abs)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Write (overwriting if file exists)
        with open(target_abs, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            f'Successfully wrote to "{file_path}" '
            f'({len(content)} characters written)'
        )

    except Exception as exc:
        return f"Error: {exc}"
