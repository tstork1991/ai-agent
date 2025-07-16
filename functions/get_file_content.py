# functions/get_file_content.py
from __future__ import annotations
import os
from .config import MAX_CHARS


def get_file_content(working_directory: str, file_path: str) -> str:
    """
    Safely read a file inside `working_directory`.

    Returns either:
      * the file's text (possibly truncated to MAX_CHARS), or
      * an error string starting with "Error:".
    """
    try:
        work_abs = os.path.abspath(working_directory)
        target_abs = os.path.abspath(os.path.join(work_abs, file_path))

        # Guard-rail: stay inside working directory
        if not target_abs.startswith(work_abs):
            return (
                f'Error: Cannot read "{file_path}" as it is outside the '
                "permitted working directory"
            )

        # Must be a regular file
        if not os.path.isfile(target_abs):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_abs, "r", encoding="utf-8", errors="replace") as f:
            data = f.read(MAX_CHARS + 1)

        if len(data) > MAX_CHARS:
            data = (
                data[:MAX_CHARS]
                + f'\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            )

        return data

    except Exception as exc:  # catch any unexpected issues
        return f"Error: {exc}"

from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of a file (truncated to 10 000 chars).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file (relative to working directory).",
            ),
        },
    ),
)
