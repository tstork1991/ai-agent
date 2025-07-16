
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

Workflow:
1. When you need information, respond **only** with one valid function call
   (get_files_info, get_file_content, run_python_file, or write_file).
2. The tool response will be injected into the conversation.
3. Repeat function calls as needed.
4. When you can fully answer the user, reply with plain text and NO
   function call.

Rules:
- Never output plans or explanations before calling a function.
- Only one function call per response.
- Paths must be relative to the working directory; omit
  working_directory—it’s added automatically.
"""




# tool registry
available_tools = [
    types.Tool(function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ])
]

# ── auth & client ───────────────────────────────────────────────
load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# ── parse CLI prompt & --verbose flag ───────────────────────────
args = sys.argv[1:] or sys.exit("usage: uv run main.py \"prompt\" [--verbose]")
verbose = args[-1] == "--verbose"
if verbose:
    args = args[:-1]
user_prompt = " ".join(args)

# conversation memory
messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)])
]

if verbose:
    print(f'User prompt: "{user_prompt}"')

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

    # Gemini returns at least one candidate; use the first
    content = resp.candidates[0].content
    messages.append(content)  # always add what Gemini said/planned

    part0 = content.parts[0]

    if part0.function_call:
        # Model planned a tool call
        tool_response = call_function(part0.function_call, verbose=verbose)
        if not tool_response.parts[0].function_response:
            raise RuntimeError("call_function failed to produce a tool response")
        # add tool response so the model can use it next turn
        messages.append(tool_response)
        if verbose:
            print("->", tool_response.parts[0].function_response.response)
        continue  # ask Gemini what to do next
    else:
        # Model sent plain text → conversation done
        print("Final response:\n" + part0.text.strip())
        break
else:
    print("Max iterations reached without final response.")

# optional token usage
if verbose:
    meta = resp.usage_metadata
    print(f"Prompt tokens: {meta.prompt_token_count}")
    print(f"Response tokens: {meta.candidates_token_count}")
