import json
import os
import unittest
from unittest.mock import patch

from src.baseline import FROZEN_PROMPT
from src.openrouter_baseline import (GENERATION_SETTINGS, OPENROUTER_API_KEY_ENV,
                                     OPENROUTER_BASELINE_MODEL, OpenRouterConfigurationError,
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

        prompt = FROZEN_PROMPT.format(data=100, genius=0, fit=0, cute=0, power_mode="off", stimulant_boost="off")
        with patch.dict(os.environ, {OPENROUTER_API_KEY_ENV: "test-key"}, clear=True):
            result = make_openrouter_baseline_callable(opener=opener)(prompt)
        self.assertEqual(result, "blueberry: 50 g, water: 200 g")
        self.assertEqual(captured["timeout"], 60)
        payload = json.loads(captured["request"].data.decode("utf-8"))
        self.assertEqual(payload["model"], OPENROUTER_BASELINE_MODEL)
        self.assertEqual(payload["messages"], [{"role": "user", "content": prompt}])
        self.assertNotIn("tools", payload)
        for name, value in GENERATION_SETTINGS.items():
            self.assertEqual(payload[name], value)
        self.assertNotIn("test-key", repr(payload))


if __name__ == "__main__":
    unittest.main()
