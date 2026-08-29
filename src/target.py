"""Deterministic slider and toggle handling from SPEC.md §§5–6."""

from __future__ import annotations

DIMENSION_SCALES = {
    "vitc_mg": 150.0, "k_mg": 350.0, "mg_mg": 35.0, "ca_mg": 60.0,
    "na_mg": 100.0, "sugar_g": 25.0, "antioxidant_score": 1.0,
}
SLIDERS = ("data", "genius", "fit", "cute")
WEIGHTS = {
    "data": {"vitc_mg": .3, "k_mg": .9, "mg_mg": .9, "ca_mg": .2, "sugar_g": .1, "antioxidant_score": .4},
    "genius": {"vitc_mg": .6, "k_mg": .3, "mg_mg": .3, "ca_mg": .2, "sugar_g": .1, "antioxidant_score": .9},
    "fit": {"vitc_mg": .3, "k_mg": .9, "mg_mg": .9, "ca_mg": .2, "sugar_g": .6, "antioxidant_score": .2},
    "cute": {"vitc_mg": .4, "k_mg": .1, "mg_mg": .1, "ca_mg": .1, "sugar_g": .8, "antioxidant_score": .2},
}


class InputValidationError(ValueError):
    """Raised for a specified §5/§6 rejected input."""


def validate_inputs(sliders: dict[str, float], stimulant_boost: bool = False) -> None:
    values = {name: float(sliders.get(name, 0.0)) for name in SLIDERS}
    if any(value < 0 for value in values.values()):
        raise InputValidationError("slider values must be non-negative")
    if sum(values.values()) == 0:
        raise InputValidationError("select at least one goal")
    if stimulant_boost and values["cute"] >= 80:
        raise InputValidationError("Stimulant Boost is not allowed when Cute is 80 or higher")


def build_target(sliders: dict[str, float], *, power_mode: bool = False,
                 stimulant_boost: bool = False, liquid_base: str = "water") -> tuple[dict[str, float], list[str]]:
    """Return the §5 target vector and applicable §6 warnings."""
    validate_inputs(sliders, stimulant_boost)
    if liquid_base not in ("water", "mineral_water"):
        raise InputValidationError("liquid_base must be water or mineral_water")
    total = sum(float(sliders.get(name, 0.0)) for name in SLIDERS)
    normalized = {name: float(sliders.get(name, 0.0)) / total for name in SLIDERS}
    target = {dimension: DIMENSION_SCALES[dimension] * sum(
        normalized[name] * WEIGHTS[name][dimension] for name in SLIDERS)
        for dimension in ("vitc_mg", "k_mg", "mg_mg", "ca_mg", "sugar_g", "antioxidant_score")}
    target["na_mg"] = 0.0 if liquid_base == "water" else 25.0
    warnings: list[str] = []
    if power_mode:
        if float(sliders.get("fit", 0.0)) < 50:
            warnings.append("Power Mode ignored because Fit is below 50")
        else:
            target["sugar_g"] *= 1.40
    if liquid_base == "mineral_water" and float(sliders.get("cute", 0.0)) >= 80:
        warnings.append("mineral_water selected with Cute >= 80; sodium contribution noted")
    return target, warnings
