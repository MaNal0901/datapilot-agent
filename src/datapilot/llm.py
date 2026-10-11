import os
import time
from google import genai
from datapilot.config import GEMINI_API_KEY, MODEL_NAME

_client = genai.Client(api_key=GEMINI_API_KEY)

# Modèles de secours, modifiables dans .env : FALLBACK_MODELS=modele1,modele2
FALLBACKS = [
    m.strip()
    for m in os.getenv("FALLBACK_MODELS", "gemini-3.5-flash,gemini-3.1-flash-lite").split(",")
    if m.strip()
]
RETRYABLE = ("429", "503", "UNAVAILABLE", "RESOURCE_EXHAUSTED")


def _is_retryable(error: Exception) -> bool:
    return any(k in str(error) for k in RETRYABLE)


def _call(model: str, prompt: str, retries: int = 3) -> str:
    """Appelle un modèle, avec attente croissante si le serveur est surchargé."""
    for attempt in range(retries):
        try:
            return _client.models.generate_content(model=model, contents=prompt).text
        except Exception as e:
            if _is_retryable(e) and attempt < retries - 1:
                wait = 5 * 2 ** attempt          # 5 s, puis 10 s
                print(f"   ({model} surchargé, nouvel essai dans {wait}s)")
                time.sleep(wait)
                continue
            raise


def llm(prompt: str) -> str:
    """Point d'entrée unique vers le LLM : retry + bascule vers un modèle de secours."""
    models = [MODEL_NAME] + [m for m in FALLBACKS if m != MODEL_NAME]
    last_error = None
    for model in models:
        try:
            return _call(model, prompt)
        except Exception as e:
            if not _is_retryable(e):
                raise                              # ex. 404 : inutile de réessayer
            last_error = e
            print(f"   ({model} indisponible, bascule vers le modèle suivant)")
    raise last_error