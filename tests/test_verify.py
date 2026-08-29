import unittest

from src.optimizer import optimize
from src.verify import verify_recipe


SLIDERS = {"data": 100, "genius": 0, "fit": 0, "cute": 0}


def recipe(**changes):
    base = {"blueberry": 40.0, "lingonberry": 0.0, "cloudberry": 0.0,
            "redcurrant": 0.0, "blackcurrant": 0.0, "guarana_g": 0.0, "liquid_g": 210.0}
    base.update(changes)
    return base


class VerificationTests(unittest.TestCase):
    def test_step_zero_all_zero_rejected(self):
        result = verify_recipe(recipe(), {"data": 0, "genius": 0, "fit": 0, "cute": 0})
        self.assertEqual(result["status"], "REJECT")

    def test_step_zero_cute_80_stimulant_rejected(self):
        result = verify_recipe(recipe(), {"data": 20, "genius": 0, "fit": 0, "cute": 80}, stimulant_boost=True)
        self.assertEqual(result["status"], "REJECT")

    def test_step_one_recomputes_totals(self):
        result = verify_recipe(recipe(), SLIDERS)
        self.assertAlmostEqual(result["totals"]["vitc_mg"], 7.16 * .4)

    def test_step_two_mass_balance_rejected(self):
        result = verify_recipe(recipe(liquid_g=200), SLIDERS)
        self.assertEqual(result["status"], "REJECT")

    def test_step_three_low_liquid_rejected(self):
        result = verify_recipe(recipe(blueberry=80, lingonberry=80, cloudberry=51, liquid_g=39), SLIDERS)
        self.assertEqual(result["status"], "REJECT")
        self.assertIn("liquid below", result["errors"][0])

    def test_step_four_caffeine_low_warns_invalid_for_boost(self):
        result = verify_recipe(recipe(guarana_g=1.0, liquid_g=209.0), SLIDERS, stimulant_boost=True)
        self.assertEqual(result["status"], "WARN")
        self.assertTrue(result["invalid_for_boost"])

    def test_step_four_caffeine_at_guarana_bound_is_in_range(self):
        result = verify_recipe(recipe(guarana_g=4.2, liquid_g=205.8), SLIDERS, stimulant_boost=True)
        self.assertEqual(result["status"], "PASS")

    def test_step_six_cute_mineral_warns(self):
        result = verify_recipe(recipe(), {"data": 0, "genius": 0, "fit": 0, "cute": 100}, liquid_base="mineral_water")
        self.assertEqual(result["status"], "WARN")

    def test_step_seven_na_not_reported_unreachable(self):
        result = verify_recipe(recipe(), SLIDERS)
        self.assertNotIn("na_mg", result["unreachable_dimensions"])

    def test_bounds_reject_negative_and_over_berry(self):
        self.assertEqual(verify_recipe(recipe(blueberry=-1, liquid_g=251), SLIDERS)["status"], "REJECT")
        self.assertEqual(verify_recipe(recipe(blueberry=81, liquid_g=169), SLIDERS)["status"], "REJECT")
        self.assertEqual(verify_recipe(recipe(guarana_g=4.21, liquid_g=205.79), SLIDERS)["status"], "REJECT")

    def test_non_finite_ingredient_amounts_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                self.assertEqual(verify_recipe(recipe(blueberry=value), SLIDERS)["status"], "REJECT")

    def test_verifier_recomputes_not_optimizer_reported_totals(self):
        sliders = {"data": 55, "genius": 0, "fit": 45, "cute": 0}
        optimized = optimize(sliders)
        optimized["totals"]["vitc_mg"] = -99999.0
        result = verify_recipe(optimized["recipe"], sliders)
        self.assertNotEqual(result["totals"]["vitc_mg"], optimized["totals"]["vitc_mg"])

    def test_cute_79_boundary_allowed(self):
        result = verify_recipe(recipe(guarana_g=2.0, liquid_g=208), {"data": 21, "genius": 0, "fit": 0, "cute": 79}, stimulant_boost=True)
        self.assertNotEqual(result["status"], "REJECT")


if __name__ == "__main__":
    unittest.main()
