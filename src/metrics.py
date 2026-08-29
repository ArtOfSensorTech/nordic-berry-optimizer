"""NNTD calculation and §9 reporting."""

from __future__ import annotations

from .target import DIMENSION_SCALES

DIMENSIONS = ("vitc_mg", "k_mg", "mg_mg", "ca_mg", "na_mg", "sugar_g", "antioxidant_score")


def nntd_report(achieved: dict[str, float], target: dict[str, float]) -> dict[str, object]:
    deviations = {dimension: abs(float(achieved[dimension]) - float(target[dimension])) / DIMENSION_SCALES[dimension]
                  for dimension in DIMENSIONS}
    return {"per_dimension": deviations, "nntd": sum(deviations.values()) / len(DIMENSIONS)}
