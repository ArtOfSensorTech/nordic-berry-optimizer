"""Independent deterministic verification for SPEC.md §8."""

from __future__ import annotations

from .metrics import nntd_report
from .nutrients import (ANTIOXIDANT_SCORES, BERRIES, CAFFEINE_MG_PER_G, LIQUID_BASES,
                        MIN_LIQUID_G, NUTRIENTS, TOTAL_MASS_G, liquid_mass, nutrient_totals)
from .target import DIMENSION_SCALES, build_target, validate_inputs

MASS_TOLERANCE_G = 1e-9
GUARANA_MAX_G = 4.2
USER_DIMENSIONS = ("vitc_mg", "k_mg", "mg_mg", "ca_mg", "sugar_g", "antioxidant_score")


def _reject(result: dict[str, object], message: str) -> dict[str, object]:
    result["status"] = "REJECT"
    result["errors"].append(message)
    return result


def _maximum(dimension: str, liquid_base: str) -> float:
    """Upper bound over the §3 berry/liquid capacity; used only for reporting."""
    if dimension == "antioxidant_score":
        return max(ANTIOXIDANT_SCORES.values())
    field = dimension
    # At most 210g may be berries; liquid must be at least 40g. Greedily
    # allocate positive linear contributions to the highest-valued berry.
    capacity = TOTAL_MASS_G - MIN_LIQUID_G
    berry_values = sorted(((NUTRIENTS[berry][field], berry) for berry in BERRIES), reverse=True)
    total = MIN_LIQUID_G * NUTRIENTS[liquid_base][field] / 100.0
    for value, _berry in berry_values:
        amount = min(80.0, capacity)
        total += amount * value / 100.0
        capacity -= amount
        if capacity <= 0:
            break
    return total


def verify_recipe(recipe: dict[str, float], sliders: dict[str, float], *, power_mode: bool = False,
                  stimulant_boost: bool = False, liquid_base: str = "water") -> dict[str, object]:
    """Classify a recipe without altering it; all totals are freshly recomputed."""
    result: dict[str, object] = {"status": "PASS", "warnings": [], "errors": [], "invalid_for_boost": False}
    try:
        validate_inputs(sliders, stimulant_boost)
        target, target_warnings = build_target(sliders, power_mode=power_mode,
                                                stimulant_boost=stimulant_boost, liquid_base=liquid_base)
    except ValueError as exc:
        return _reject(result, str(exc))
    if liquid_base not in LIQUID_BASES:
        return _reject(result, "invalid liquid_base")
    result["warnings"].extend(target_warnings)
    normalized = {name: float(recipe.get(name, 0.0)) for name in (*BERRIES, "guarana_g")}
    if any(value < 0 for value in normalized.values()):
        return _reject(result, "ingredient amounts must be non-negative")
    if any(normalized[berry] > 80.0 + MASS_TOLERANCE_G for berry in BERRIES):
        return _reject(result, "berry amount exceeds 80 g bound")
    if normalized["guarana_g"] > GUARANA_MAX_G + MASS_TOLERANCE_G:
        return _reject(result, "guarana amount exceeds 4.2 g bound")
    derived_liquid = liquid_mass(normalized)
    declared_liquid = float(recipe.get("liquid_g", derived_liquid))
    if abs(sum(normalized.values()) + declared_liquid - TOTAL_MASS_G) > MASS_TOLERANCE_G:
        return _reject(result, "mass balance failed")
    if abs(declared_liquid - derived_liquid) > MASS_TOLERANCE_G:
        return _reject(result, "liquid_g must equal derived mass-balance liquid")
    if declared_liquid < MIN_LIQUID_G - MASS_TOLERANCE_G:
        return _reject(result, "liquid below 40 g: optimizer constraint violation")
    accounted_recipe = dict(normalized) | {"liquid_g": declared_liquid}
    totals = nutrient_totals(accounted_recipe, liquid_base)
    result["totals"] = totals
    result["target"] = target
    result["metric"] = nntd_report(totals, target)
    caffeine = totals["caffeine_mg"]
    if stimulant_boost:
        result["caffeine_achieved_mg"] = caffeine
        result["caffeine_in_range"] = 50.0 <= caffeine <= 200.0
        if caffeine > 200.0 + MASS_TOLERANCE_G:
            return _reject(result, "caffeine exceeds 200 mg hard safety maximum")
        if caffeine < 50.0 - MASS_TOLERANCE_G:
            result["status"] = "WARN"
            result["invalid_for_boost"] = True
            result["warnings"].append("stimulant boost requested but negligible caffeine achieved")
    if float(sliders.get("cute", 0.0)) >= 80 and liquid_base == "mineral_water":
        result["warnings"].append("mineral_water selected with Cute >= 80; sodium contribution noted")
        if result["status"] == "PASS":
            result["status"] = "WARN"
    result["unreachable_dimensions"] = [dimension for dimension in USER_DIMENSIONS
                                         if target[dimension] > _maximum(dimension, liquid_base) + 1e-12]
    return result
