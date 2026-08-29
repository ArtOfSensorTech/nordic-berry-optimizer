"""Simple command-line entry point for the Nordic Berry Optimizer."""

from __future__ import annotations

import argparse
import json

from .optimizer import optimize
from .verify import verify_recipe


def main() -> int:
    parser = argparse.ArgumentParser(description="Optimize a berry drink toward a nutrient target profile (no health claims).")
    for name in ("data", "genius", "fit", "cute"):
        parser.add_argument(f"--{name}", type=float, default=0.0)
    parser.add_argument("--power-mode", action="store_true")
    parser.add_argument("--stimulant-boost", action="store_true")
    parser.add_argument("--liquid-base", choices=("water", "mineral_water"), default="water")
    args = parser.parse_args()
    sliders = {name: getattr(args, name) for name in ("data", "genius", "fit", "cute")}
    result = optimize(sliders, power_mode=args.power_mode, stimulant_boost=args.stimulant_boost,
                      liquid_base=args.liquid_base)
    verification = verify_recipe(result["recipe"], sliders, power_mode=args.power_mode,
                                 stimulant_boost=args.stimulant_boost, liquid_base=args.liquid_base)
    print(json.dumps({"recipe": result["recipe"], "nutrients": result["totals"],
                      "target": result["target"], "metric": result["metric"],
                      "verification": verification}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
