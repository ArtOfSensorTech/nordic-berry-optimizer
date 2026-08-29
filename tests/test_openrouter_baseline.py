import json
from io import BytesIO
import os
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

from src.baseline import FROZEN_PROMPT
from src.openrouter_baseline import (GENERATION_SETTINGS, OPENROUTER_API_KEY_ENV,
                                     OPENROUTER_BASELINE_MODEL, OPENROUTER_BASELINE_PROVIDER,
                                     OpenRouterConfigurationError, OpenRouterResponseError,
                                     make_openrouter_baseline_callable)


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class OpenRouterAdapterTests(unittest.TestCase):
    def test_fixed_provider_label(self):
        self.assertEqual(OPENROUTER_BASELINE_PROVIDER, "OpenRouter")
        self.assertEqual(OPENROUTER_BASELINE_MODEL, "z-ai/glm-5.2")
        self.assertEqual(GENERATION_SETTINGS, {"temperature": 0, "top_p": 1, "max_tokens": 2048, "stream": False})

    def test_missing_key_fails_before_http(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OpenRouterConfigurationError):
                make_openrouter_baseline_callable()

    def test_request_is_text_only_fixed_model_and_exact_user_prompt(self):
        captured = {}

        def opener(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return _Response({"choices": [{"message": {"content": "blueberry: 50 g, water: 200 g"}}]})

        prompt = FROZEN_PROMPT.format(data=100, genius=0, fit=0, cute=0, power_mode="off", stimulant_boost="off", liquid_base="mineral_water")
        with patch.dict(os.environ, {OPENROUTER_API_KEY_ENV: "test-key"}, clear=True):
            result = make_openrouter_baseline_callable(opener=opener)(prompt)
        self.assertEqual(result, "blueberry: 50 g, water: 200 g")
        self.assertEqual(captured["timeout"], 60)
        payload = json.loads(captured["request"].data.decode("utf-8"))
        self.assertEqual(payload["model"], OPENROUTER_BASELINE_MODEL)
        self.assertEqual(len(payload["messages"]), 1)
        self.assertEqual(payload["messages"], [{"role": "user", "content": prompt}])
        self.assertNotIn("tools", payload)
        for name, value in GENERATION_SETTINGS.items():
            self.assertEqual(payload[name], value)
        self.assertNotIn("test-key", repr(payload))

    def test_http_429_retains_safe_diagnostics_without_retry_or_credentials(self):
        calls = []

        def opener(request, timeout):
            calls.append((request, timeout))
            raise HTTPError(
                request.full_url,
                429,
                "Too Many Requests",
                {
                    "Retry-After": "30",
                    "X-RateLimit-Remaining": "0",
                    "X-Request-ID": "request-123",
                    "Authorization": "Bearer test-key",
                    "Set-Cookie": "secret-cookie",
                },
                BytesIO(json.dumps({"error": {"message": "quota exceeded for test-key", "code": 429}}).encode()),
            )

        with patch.dict(os.environ, {OPENROUTER_API_KEY_ENV: "test-key"}, clear=True):
            with self.assertRaises(OpenRouterResponseError) as raised:
                make_openrouter_baseline_callable(opener=opener)("smoke prompt")

        message = str(raised.exception)
        self.assertIn("HTTP 429", message)
        self.assertIn("quota exceeded", message)
        self.assertIn('"Retry-After": "30"', message)
        self.assertIn('"X-Request-ID": "request-123"', message)
        self.assertNotIn("test-key", message)
        self.assertNotIn("Authorization", message)
        self.assertNotIn("secret-cookie", message)
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
