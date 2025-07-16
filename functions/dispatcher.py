# functions/dispatcher.py
from __future__ import annotations
from google.genai import types

from functions.get_files_info   import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file       import write_file
from functions.run_python       import run_python_file

WORKING_DIR = "calculator"  # hard-coded per assignment

# Map function-name → Python callable
FUNC_MAP = {
    "get_files_info":   get_files_info,
    "get_file_content": get_file_content,
    "write_file":       write_file,
    "run_python_file":  run_python_file,
}


def call_function(function_call_part: types.FunctionCall, verbose: bool = False) -> types.Content:
    """
    Execute one of the allowed functions based on the LLM's FunctionCall part
    and wrap the result in a `types.Content` tool response.
    """
    fn_name: str = function_call_part.name
    fn_args: dict = dict(function_call_part.args or {})  # copy → mutate safely

    if verbose:
        print(f"Calling function: {fn_name}({fn_args})")
    else:
        print(f" - Calling function: {fn_name}")

    # Guard-rails: ensure function exists
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

    # Inject working_directory arg that LLM cannot set
    fn_args["working_directory"] = WORKING_DIR

    try:
        result = FUNC_MAP[fn_name](**fn_args)
    except Exception as exc:  # capture runtime errors
        result = f"Error: {exc}"

    # Wrap result in tool response
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=fn_name,
                response={"result": result},
            )
        ],
    )
