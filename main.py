import os
from dotenv import load_dotenv
from google import genai            # comes from google-genai==1.12.1

# ── 1. load the API key ─────────────────────────────────────────────
load_dotenv()                        # reads .env into os.environ
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing – check your .env file")

# ── 2. create a Gemini client ───────────────────────────────────────
client = genai.Client(api_key=api_key)

# ── 3. send the prompt ──────────────────────────────────────────────
prompt = (
    "Why is Boot.dev such a great place to learn backend development? "
    "Use one paragraph maximum."
)

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=prompt,
)

# ── 4. print answer + token usage ───────────────────────────────────
print(response.text)
print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

