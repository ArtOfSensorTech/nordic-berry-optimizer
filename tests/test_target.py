import unittest

from src.target import DIMENSION_SCALES, InputValidationError, build_target


class TargetTests(unittest.TestCase):
    def test_formula_and_normalization(self):
        target, _ = build_target({"data": 100, "genius": 100, "fit": 0, "cute": 0})
        self.assertAlmostEqual(target["vitc_mg"], 150 * .45)
        self.assertAlmostEqual(target["k_mg"], 350 * .6)
        self.assertEqual(target["na_mg"], 0)

    def test_all_zero_rejected(self):
        with self.assertRaisesRegex(InputValidationError, "select at least one goal"):
            build_target({"data": 0, "genius": 0, "fit": 0, "cute": 0})

    def test_power_mode_sugar_boost(self):
        normal, _ = build_target({"data": 0, "genius": 0, "fit": 100, "cute": 0})
        powered, _ = build_target({"data": 0, "genius": 0, "fit": 100, "cute": 0}, power_mode=True)
        self.assertAlmostEqual(powered["sugar_g"], normal["sugar_g"] * 1.4)

    def test_power_mode_below_fit_threshold_warns(self):
        target, warnings = build_target({"data": 100, "genius": 0, "fit": 49, "cute": 0}, power_mode=True)
        self.assertIn("Power Mode ignored", warnings[0])
        self.assertLess(target["sugar_g"], DIMENSION_SCALES["sugar_g"])

    def test_liquid_base_na_target(self):
        sliders = {"data": 100, "genius": 0, "fit": 0, "cute": 0}
        self.assertEqual(build_target(sliders, liquid_base="water")[0]["na_mg"], 0)
        self.assertEqual(build_target(sliders, liquid_base="mineral_water")[0]["na_mg"], 25)


if __name__ == "__main__":
    unittest.main()
