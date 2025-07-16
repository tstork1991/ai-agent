import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# schema imports
from functions.get_files_info   import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file       import schema_write_file
from functions.run_python       import schema_run_python_file

# ── system prompt ────────────────────────────────────────────────
system_prompt = """
You are a helpful AI coding agent.

Choose exactly one function call that accomplishes the user's request.

Allowed operations:
- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you reference must be **relative** to the working directory. You
never include the working_directory parameter—it is injected automatically.
"""

# ── register all four functions ──────────────────────────────────
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# ── Gemini client ────────────────────────────────────────────────
load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# ── CLI parsing (prompt + optional --verbose) ────────────────────
args = sys.argv[1:] or sys.exit("usage: uv run main.py \"prompt\" [--verbose]")
verbose = args[-1] == "--verbose"
if verbose:
    args = args[:-1]
user_prompt = " ".join(args)
if verbose:
    print(f'User prompt: "{user_prompt}"')

messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

# ── model call with tools & system instructions ──────────────────
resp = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[available_functions],
        temperature=0.0,                # deterministic
    ),
)

part = resp.candidates[0].content.parts[0]
if part.function_call:
    fc = part.function_call
    print(f"Calling function: {fc.name}({fc.args})")
else:
    print(part.text.strip())

if verbose:
    meta = resp.usage_metadata
    print(f"Prompt tokens: {meta.prompt_token_count}")
    print(f"Response tokens: {meta.candidates_token_count}")
