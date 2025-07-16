import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# schema imports
from functions.get_files_info   import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file       import schema_write_file
from functions.run_python       import schema_run_python_file

from functions.dispatcher import call_function  # ← NEW helper

# ── system prompt ───────────────────────────────────────────────
system_prompt = """
You are a helpful AI coding agent.

Choose exactly one function call that accomplishes the user's request.

Allowed operations:
- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you reference must be relative to the working directory.
Do not supply working_directory; it is injected automatically.
"""

# ── tool registry ────────────────────────────────────────────────
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# ── Gemini client setup ──────────────────────────────────────────
load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# ── CLI prompt & --verbose flag ─────────────────────────────────
args = sys.argv[1:] or sys.exit("usage: uv run main.py \"prompt\" [--verbose]")
verbose = args[-1] == "--verbose"
if verbose:
    args = args[:-1]
user_prompt = " ".join(args)
if verbose:
    print(f'User prompt: "{user_prompt}"')

messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

# ── first model call (planning) ─────────────────────────────────
resp = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[available_functions],
        temperature=0.0,
    ),
)

first_part = resp.candidates[0].content.parts[0]

# ── If LLM called a function, execute it ────────────────────────
if first_part.function_call:
    tool_response_content = call_function(first_part.function_call, verbose=verbose)

    # Show the result if verbose
    if verbose and tool_response_content.parts[0].function_response:
        print("->", tool_response_content.parts[0].function_response.response)

else:
    # LLM responded with plain text
    print(first_part.text.strip())

# optional usage metadata
if verbose:
    meta = resp.usage_metadata
    print(f"Prompt tokens: {meta.prompt_token_count}")
    print(f"Response tokens: {meta.candidates_token_count}")
