import requests

from app.core.config import settings


class LLMUnavailableError(RuntimeError):
    pass


def generate(prompt: str) -> str:
    try:
        response = requests.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMUnavailableError(
            f"Could not reach local LLM (Ollama) at {settings.ollama_base_url} "
            f"with model '{settings.ollama_model}'. Is `ollama serve` running? ({exc})"
        ) from exc

    return response.json()["response"].strip()
