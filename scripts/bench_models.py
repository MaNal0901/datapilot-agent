import time
from google import genai
from datapilot.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]

for model in MODELS:
    t = time.time()
    try:
        client.models.generate_content(model=model, contents="Réponds juste : ok")
        print(f"{model:26s} OK   {time.time() - t:6.1f}s")
    except Exception as e:
        print(f"{model:26s} ERR  {time.time() - t:6.1f}s  {str(e)[:70]}")