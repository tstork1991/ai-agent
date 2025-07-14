import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ── 1. load the API key ─────────────────────────────────────────────
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing – check your .env")

client = genai.Client(api_key=api_key)

# ── 2. parse CLI args (prompt [+ --verbose]) ───────────────────────
if len(sys.argv) < 2:
    print('Error: supply a prompt, e.g.')
    print('  uv run main.py "What is the meaning of life?" --verbose')
    sys.exit(1)

verbose = False
args = sys.argv[1:]                # everything after the script name

if args[-1] == "--verbose":
    verbose = True
    args = args[:-1]               # drop the flag from the prompt parts

user_prompt = " ".join(args)

# ── 3. build the messages list ─────────────────────────────────────
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

# ── 4. call Gemini ─────────────────────────────────────────────────
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
)

# ── 5. console output  ─────────────────────────────────────────────
if verbose:
    print(f'User prompt: "{user_prompt}"')
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

print(response.text)               # always show the model’s answer

