import unittest

from src.optimizer import optimize
from src.verify import verify_recipe


class OptimizerTests(unittest.TestCase):
    def test_joint_search_returns_independently_verifiable_recipe(self):
        sliders = {"data": 55, "genius": 0, "fit": 45, "cute": 0}
        result = optimize(sliders, liquid_base="mineral_water")
        checked = verify_recipe(result["recipe"], sliders, liquid_base="mineral_water")
        self.assertEqual(checked["status"], "PASS")
        self.assertGreaterEqual(result["recipe"]["liquid_g"], 40)

    def test_boost_tie_break_prefers_100mg_when_water_keeps_nntd_equal(self):
        sliders = {"data": 0, "genius": 60, "fit": 40, "cute": 0}
        result = optimize(sliders, stimulant_boost=True, liquid_base="water")
        caffeine = result["totals"]["caffeine_mg"]
        self.assertGreaterEqual(caffeine, 50)
        self.assertLessEqual(caffeine, 200)
        self.assertAlmostEqual(caffeine, 100, delta=.5)


if __name__ == "__main__":
    unittest.main()
