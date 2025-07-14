"""
Return a one-line-per-entry listing for any directory *inside* a permitted
working directory.  All errors are returned as strings that start with
"Error:" so the LLM can read them and try again.
"""
from __future__ import annotations
import os
from typing import Optional


def get_files_info(working_directory: str, directory: Optional[str] = None) -> str:
    """
    Parameters
    ----------
    working_directory : str
        The root folder the LLM is allowed to inspect.
    directory : Optional[str]
        A *relative* path inside `working_directory` whose contents will be
        listed.  `None` or "." means the working directory itself.

    Returns
    -------
    str
        Either a nicely-formatted listing or an error string that begins with
        "Error:".
    """
    try:
        # Canonical absolute paths
        working_dir_abs = os.path.abspath(working_directory)
        target_rel = directory or "."
        target_abs = os.path.abspath(os.path.join(working_dir_abs, target_rel))

        # Guard-rails: stay *inside* the working directory
        if not target_abs.startswith(working_dir_abs):
            return (
                f'Error: Cannot list "{directory}" as it is outside the '
                "permitted working directory"
            )

        # Ensure the target is a directory
        if not os.path.isdir(target_abs):
            return f'Error: "{directory}" is not a directory'

        # Build listing lines
        lines = []
        for name in sorted(os.listdir(target_abs)):
            item_abs = os.path.join(target_abs, name)
            is_dir = os.path.isdir(item_abs)
            size = os.path.getsize(item_abs)
            lines.append(
                f"- {name}: file_size={size} bytes, is_dir={is_dir}"
            )

        # Join with newlines exactly like the spec
        return "\n".join(lines) if lines else "(empty directory)"

    except Exception as exc:  # catch *all* unexpected issues
        return f"Error: {exc}"
