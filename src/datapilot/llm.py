import os
import time

from google import genai
from google.genai import types

from datapilot.config import GEMINI_API_KEY, MODEL_NAME


def _make_client():
    """Client sans nouvelles tentatives cachées et avec un délai maximum de 60 s par appel."""
    try:
        options = types.HttpOptions(
            timeout=60_000,
            retry_options=types.HttpRetryOptions(attempts=1),
        )
        return genai.Client(api_key=GEMINI_API_KEY, http_options=options)
    except Exception:
        # version de la bibliothèque qui ne connaît pas ces options : client standard
        return genai.Client(api_key=GEMINI_API_KEY)


_client = _make_client()

# Modèles de secours, modifiables dans .env : FALLBACK_MODELS=modele1,modele2
FALLBACKS = [
    m.strip()
    for m in os.getenv("FALLBACK_MODELS", "gemini-3.5-flash-lite,gemini-3.5-flash").split(",")
    if m.strip()
]

USED = []   # modèles qui ont réellement répondu (pour tracer l'évaluation)


def _is_quota(error: Exception) -> bool:
    return "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error)


def _is_overloaded(error: Exception) -> bool:
    return any(k in str(error) for k in ("503", "UNAVAILABLE", "504", "DEADLINE_EXCEEDED", "timed out", "Timeout"))


def _call(model: str, prompt: str, retries: int = 2) -> str:
    """Appelle un modèle. Surcharge (503) : un nouvel essai court. Quota (429) : on remonte tout de suite."""
    for attempt in range(retries):
        try:
            return _client.models.generate_content(model=model, contents=prompt).text
        except Exception as e:
            if _is_overloaded(e) and attempt < retries - 1:
                wait = 3 * 2 ** attempt
                print(f"   ({model} surchargé, nouvel essai dans {wait}s)")
                time.sleep(wait)
                continue
            raise


def llm(prompt: str) -> str:
    """Point d'entrée unique vers le LLM : bascule vers un modèle de secours en cas d'échec temporaire."""
    models = [MODEL_NAME] + [m for m in FALLBACKS if m != MODEL_NAME]
    last_error = None
    for model in models:
        try:
            text = _call(model, prompt)
            USED.append(model)
            return text
        except Exception as e:
            if not (_is_quota(e) or _is_overloaded(e)):
                raise                      # ex. 404 : inutile de continuer
            kind = "quota épuisé" if _is_quota(e) else "surchargé"
            print(f"   ({model} indisponible : {kind}, bascule vers le modèle suivant)")
            last_error = e
    raise last_error