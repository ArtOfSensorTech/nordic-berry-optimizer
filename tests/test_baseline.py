import unittest

from src.baseline import FROZEN_PROMPT, baseline_prompt, parse_baseline_recipe


class BaselineTests(unittest.TestCase):
    def test_prompt_matches_frozen_template(self):
        case = {"sliders": {"data": 100, "genius": 0, "fit": 0, "cute": 0}, "power_mode": False, "stimulant_boost": False}
        self.assertEqual(baseline_prompt(case), FROZEN_PROMPT.format(data=100, genius=0, fit=0, cute=0, power_mode="off", stimulant_boost="off"))

    def test_parser_extracts_ingredient_grams(self):
        recipe = parse_baseline_recipe("Blueberry: 50 g; mineral water 190 grams; guarana powder 2 g.")
        self.assertEqual(recipe, {"blueberry": 50.0, "liquid_g": 190.0, "guarana_g": 2.0})


if __name__ == "__main__":
    unittest.main()
