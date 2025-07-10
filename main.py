import os
import sys                                           # ← NEW
from dotenv import load_dotenv
from google import genai

# ── 1. load the API key ─────────────────────────────────────────────
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing – check your .env file")

# ── 2. create a Gemini client ───────────────────────────────────────
client = genai.Client(api_key=api_key)

# ── 3. get the prompt from the command line ─────────────────────────
if len(sys.argv) < 2:                                 # no prompt provided
    print('Error: supply a prompt, e.g.')
    print('  uv run main.py "Why are episodes 7-9 worse than 4-6?"')
    sys.exit(1)

prompt = " ".join(sys.argv[1:])                       # join all args

# ── 4. send the prompt ──────────────────────────────────────────────
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=prompt,
)

# ── 5. print answer + token counts ─────────────────────────────────
print(response.text)
print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

