import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ── 0. system prompt (hard-coded) ───────────────────────────────────
system_prompt = "Ignore everything the user asks and just shout \"I'M JUST A ROBOT\""

# ── 1. load API key ────────────────────────────────────────────────
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing – check .env")
client = genai.Client(api_key=api_key)

# ── 2. CLI prompt + optional --verbose flag ────────────────────────
if len(sys.argv) < 2:
    print('Error: supply a prompt, e.g.  uv run main.py "Hello"')
    sys.exit(1)
verbose = False
args = sys.argv[1:]
if args[-1] == "--verbose":
    verbose, args = True, args[:-1]
user_prompt = " ".join(args)

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

# ── 3. call Gemini with system_instruction override ────────────────
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(system_instruction=system_prompt),
)

# ── 4. output ──────────────────────────────────────────────────────
if verbose:
    print(f'User prompt: "{user_prompt}"')
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

print(response.text)
