# main.py
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# tool schemas
from functions.get_files_info   import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file       import schema_write_file
from functions.run_python       import schema_run_python_file
from functions.dispatcher       import call_function

# ── system prompt ───────────────────────────────────────────────
system_prompt = """
You are a helpful AI coding agent.

You are working in a repository that has a **calculator package** at
`calculator/pkg/`.  The main logic lives in `pkg/calculator.py`.

When a user reports a bug in the calculator:

1. Call **get_files_info(directory='pkg')** to confirm the file list.
2. Call **get_file_content(file_path='pkg/calculator.py')** to inspect the
   source.
3. Patch ONLY that file with **write_file(file_path='pkg/calculator.py', …)**.
   Never create new files (e.g. script.py).
4. Optionally run **run_python_file(file_path='tests.py')** or
   **run_python_file(file_path='calculator/main.py', args=[...])** to verify.
5. After it works, answer in plain text.

Exactly ONE function call per response, no free-text plans.
Paths must stay relative; `working_directory` is added automatically.
"""


# ── tool registry ────────────────────────────────────────────────
available_tools = [
    types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )
]

# ── auth & client ────────────────────────────────────────────────
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

# conversation memory
messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)])
]

# ── dialogue loop ───────────────────────────────────────────────
for iteration in range(20):
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=available_tools,
                temperature=0.0,
            ),
        )
    except Exception as e:
        print(f"Fatal error calling model: {e}")
        sys.exit(1)

    content = resp.candidates[0].content
    messages.append(content)                # keep conversation state
    part0 = content.parts[0]

    # ── branch: model produced a tool call ──────────────────────
    if part0.function_call:
        tool_response = call_function(part0.function_call, verbose=verbose)

        # ensure dispatcher produced a tool response
        if not tool_response.parts[0].function_response:
            raise RuntimeError("call_function failed to produce a tool response")

        if verbose:
            print("->", tool_response.parts[0].function_response.response)

        messages.append(tool_response)      # feed tool result back to LLM
        continue                            # next turn

    # ── branch: model produced plain text (final answer) ────────
    print("Final response:\n" + part0.text.strip())
    break
else:
    print("Max iterations reached without final response.")

# ── optional token usage summary ────────────────────────────────
if verbose:
    meta = resp.usage_metadata
    print(f"Prompt tokens: {meta.prompt_token_count}")
    print(f"Response tokens: {meta.candidates_token_count}")
