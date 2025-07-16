# functions/dispatcher.py
from __future__ import annotations
import os
from google.genai import types

from functions.get_files_info   import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file       import write_file
from functions.run_python       import run_python_file

WORKING_DIR = "calculator"  # locked per assignment

# Map tool name ➜ real Python function
FUNC_MAP = {
    "get_files_info":   get_files_info,
    "get_file_content": get_file_content,
    "write_file":       write_file,
    "run_python_file":  run_python_file,
}


def _log(fn_name: str, fn_args: dict, verbose: bool) -> None:
    if verbose:
        print(f"Calling function: {fn_name}({fn_args})")
    else:
        print(f" - Calling function: {fn_name}")


def call_function(function_call_part: types.FunctionCall, *, verbose: bool = False) -> types.Content:
    """
    Execute the tool requested by the LLM and wrap the result in a
    FunctionResponse content object so Gemini can use it in the next turn.
    """
    fn_name: str = function_call_part.name
    fn_args: dict = dict(function_call_part.args or {})

    # guard-rail on name
    if fn_name not in FUNC_MAP:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=fn_name,
                    response={"error": f"Unknown function: {fn_name}"},
                )
            ],
        )

    # inject working_directory
    fn_args["working_directory"] = WORKING_DIR

    # ── Auto list directory before reading a file ─────────────────
    if fn_name == "get_file_content":
        dir_to_list = os.path.dirname(fn_args["file_path"]) or "."
        _log("get_files_info", {"directory": dir_to_list}, verbose)
        pre_list_result = FUNC_MAP["get_files_info"](
            working_directory=WORKING_DIR,
            directory=dir_to_list,
        )
        if verbose:
            print("->", pre_list_result)

    # ── Run the requested function ────────────────────────────────
    _log(fn_name, {k: v for k, v in fn_args.items() if k != "working_directory"}, verbose)

    try:
        result = FUNC_MAP[fn_name](**fn_args)
    except Exception as exc:
        result = f"Error: {exc}"

    # wrap result for Gemini
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=fn_name,
                response={"result": result},
            )
        ],
    )
