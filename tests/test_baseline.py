import unittest

from src.baseline import FROZEN_PROMPT, baseline_prompt, parse_baseline_recipe, validate_llm_configuration


class BaselineTests(unittest.TestCase):
    def test_prompt_matches_frozen_template(self):
        case = {"sliders": {"data": 100, "genius": 0, "fit": 0, "cute": 0}, "power_mode": False, "stimulant_boost": False}
        self.assertEqual(baseline_prompt(case), FROZEN_PROMPT.format(data=100, genius=0, fit=0, cute=0, power_mode="off", stimulant_boost="off"))

    def test_parser_extracts_ingredient_grams(self):
        parsed = parse_baseline_recipe("Blueberry: 50 g; mineral water 190 grams; guarana powder 2 g.")
        self.assertEqual(parsed.status, "PASS")
        self.assertEqual(parsed.liquid_base, "mineral_water")
        self.assertEqual(parsed.recipe, {"blueberry": 50.0, "liquid_g": 190.0, "guarana_g": 2.0})

    def test_parser_accepts_natural_orderings_and_water(self):
        parsed = parse_baseline_recipe("50 g blueberry, lingonberry 10g, and 190 grams of water")
        self.assertEqual(parsed.status, "PASS")
        self.assertEqual(parsed.liquid_base, "water")
        self.assertEqual(parsed.recipe, {"blueberry": 50.0, "lingonberry": 10.0, "liquid_g": 190.0})

    def test_parser_rejects_missing_or_conflicting_liquid(self):
        missing = parse_baseline_recipe("blueberry: 50 g")
        conflicting = parse_baseline_recipe("blueberry 50g, water 100g, mineral water 100g")
        self.assertEqual(missing.status, "INVALID")
        self.assertIn("does not specify", missing.reason)
        self.assertEqual(conflicting.status, "INVALID")
        self.assertIn("both", conflicting.reason)

    def test_llm_configuration_requires_provider_and_model_labels(self):
        with self.assertRaisesRegex(ValueError, "provider and model"):
            validate_llm_configuration("", "example-model")
        with self.assertRaisesRegex(ValueError, "provider and model"):
            validate_llm_configuration("example-provider", "")


if __name__ == "__main__":
    unittest.main()
