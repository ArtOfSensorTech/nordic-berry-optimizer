"""Frozen §11 evaluation harness. TASK 3 invokes this; importing it has no side effects."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Callable

from src.baseline import baseline_prompt, parse_baseline_recipe
from src.metrics import DIMENSIONS
from src.optimizer import optimize
from src.verify import verify_recipe

FROZEN_CASES = (
    {"id": 1, "sliders": {"data": 100, "genius": 0, "fit": 0, "cute": 0}, "liquid_base": "water"},
    {"id": 2, "sliders": {"data": 0, "genius": 100, "fit": 0, "cute": 0}, "liquid_base": "water"},
    {"id": 3, "sliders": {"data": 0, "genius": 0, "fit": 100, "cute": 0}, "liquid_base": "water"},
    {"id": 4, "sliders": {"data": 0, "genius": 0, "fit": 0, "cute": 100}, "liquid_base": "water"},
    {"id": 5, "sliders": {"data": 25, "genius": 25, "fit": 25, "cute": 25}, "liquid_base": "water"},
    {"id": 6, "sliders": {"data": 100, "genius": 0, "fit": 0, "cute": 0}, "liquid_base": "mineral_water"},
    {"id": 7, "sliders": {"data": 0, "genius": 0, "fit": 100, "cute": 0}, "power_mode": True, "liquid_base": "water"},
    {"id": 8, "sliders": {"data": 0, "genius": 0, "fit": 100, "cute": 0}, "power_mode": True, "stimulant_boost": True, "liquid_base": "mineral_water"},
    {"id": 9, "sliders": {"data": 100, "genius": 0, "fit": 0, "cute": 0}, "stimulant_boost": True, "liquid_base": "water"},
    {"id": 10, "sliders": {"data": 0, "genius": 100, "fit": 0, "cute": 0}, "stimulant_boost": True, "liquid_base": "water"},
    {"id": 11, "sliders": {"data": 0, "genius": 0, "fit": 0, "cute": 100}, "stimulant_boost": True, "liquid_base": "water"},
    {"id": 12, "sliders": {"data": 0, "genius": 0, "fit": 0, "cute": 100}, "liquid_base": "mineral_water"},
    {"id": 13, "sliders": {"data": 100, "genius": 100, "fit": 100, "cute": 100}, "power_mode": True, "stimulant_boost": True, "liquid_base": "mineral_water"},
    {"id": 14, "sliders": {"data": 21, "genius": 0, "fit": 0, "cute": 79}, "stimulant_boost": True, "liquid_base": "water"},
)


def _verify(recipe: dict[str, float], case: dict[str, object]) -> dict[str, object]:
    return verify_recipe(recipe, case["sliders"], power_mode=bool(case.get("power_mode", False)), stimulant_boost=bool(case.get("stimulant_boost", False)), liquid_base=str(case.get("liquid_base", "water")))


def run_agent_cases() -> list[dict[str, object]]:
    results = []
    for case in FROZEN_CASES:
        try:
            optimized = optimize(case["sliders"], power_mode=bool(case.get("power_mode", False)), stimulant_boost=bool(case.get("stimulant_boost", False)), liquid_base=str(case.get("liquid_base", "water")))
            results.append({"case": case, "recipe": optimized["recipe"], "verification": _verify(optimized["recipe"], case)})
        except ValueError as exc:
            results.append({"case": case, "recipe": None, "verification": {"status": "REJECT", "errors": [str(exc)]}})
    return results


def run_baseline_cases(llm_call: Callable[[str], str]) -> list[dict[str, object]]:
    """Run the frozen prompt exactly once per case; caller supplies the same LLM."""
    results = []
    for case in FROZEN_CASES:
        text = llm_call(baseline_prompt(case))
        recipe = parse_baseline_recipe(text)
        results.append({"case": case, "baseline_text": text, "recipe": recipe, "verification": _verify(recipe, case)})
    return results


def save_results(baseline: list[dict[str, object]], agent: list[dict[str, object]], output_dir: Path) -> None:
    """TASK 3-only artifact writer; intentionally never called during TASK 2."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "baseline_results.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    (output_dir / "agent_results.json").write_text(json.dumps(agent, indent=2), encoding="utf-8")
    with (output_dir / "comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case", "dimension", "baseline_deviation", "agent_deviation", "baseline_nntd", "agent_nntd"])
        writer.writeheader()
        for baseline_result, agent_result in zip(baseline, agent):
            baseline_metric, agent_metric = baseline_result["verification"].get("metric", {}), agent_result["verification"].get("metric", {})
            for dimension in DIMENSIONS:
                writer.writerow({"case": baseline_result["case"]["id"], "dimension": dimension, "baseline_deviation": baseline_metric.get("per_dimension", {}).get(dimension), "agent_deviation": agent_metric.get("per_dimension", {}).get(dimension), "baseline_nntd": baseline_metric.get("nntd"), "agent_nntd": agent_metric.get("nntd")})
