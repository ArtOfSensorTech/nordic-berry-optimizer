"""OpenRouter adapter for the frozen text-only baseline request.

This adapter intentionally uses only Python's standard library. It sends the
provided prompt as the sole user message, does not send a tools field, and does
not read project files. The API key is read only from OPENROUTER_API_KEY.
"""

from __future__ import annotations

import json
import os
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"
OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_BASELINE_PROVIDER = "OpenRouter"
OPENROUTER_BASELINE_MODEL = "z-ai/glm-5.2:free"

# Explicit request settings: temperature 0 and top_p 1 request minimal sampling;
# 512 output tokens is ample for exact ingredient grams. The model/API may not
# guarantee bitwise deterministic output, so results retain raw baseline text.
GENERATION_SETTINGS = {"temperature": 0, "top_p": 1, "max_tokens": 512, "stream": False}


class OpenRouterConfigurationError(RuntimeError):
    """Raised before any HTTP call when the evaluation key is unavailable."""


class OpenRouterResponseError(RuntimeError):
    """Raised for an unusable OpenRouter response without exposing credentials."""


def make_openrouter_baseline_callable(
    *, opener: Callable[..., object] = urlopen,
) -> Callable[[str], str]:
    """Return the existing ``str -> str`` baseline callable.

    The caller must set OPENROUTER_API_KEY outside the repository. The returned
    callable makes a text-only OpenAI-compatible chat-completions request with
    exactly its input prompt as the user message.
    """
    api_key = os.environ.get(OPENROUTER_API_KEY_ENV)
    if not api_key:
        raise OpenRouterConfigurationError(f"set {OPENROUTER_API_KEY_ENV} before baseline evaluation")

    def call(prompt: str) -> str:
        if not isinstance(prompt, str):
            raise TypeError("baseline prompt must be a string")
        payload = {
            "model": OPENROUTER_BASELINE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            **GENERATION_SETTINGS,
        }
        request = Request(
            OPENROUTER_CHAT_COMPLETIONS_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with opener(request, timeout=60) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise OpenRouterResponseError(f"OpenRouter request failed with HTTP {exc.code}") from exc
        except URLError as exc:
            raise OpenRouterResponseError("OpenRouter request could not be completed") from exc
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OpenRouterResponseError("OpenRouter returned an unreadable response") from exc
        try:
            content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterResponseError("OpenRouter response had no assistant text") from exc
        if not isinstance(content, str) or not content.strip():
            raise OpenRouterResponseError("OpenRouter response had empty assistant text")
        return content

    return call
