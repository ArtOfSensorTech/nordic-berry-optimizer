"""Independent deterministic verification for SPEC.md §8."""

from __future__ import annotations

import json
import math
from pathlib import Path

from .metrics import nntd_report
from .target import DIMENSION_SCALES, build_target, validate_inputs

MASS_TOLERANCE_G = 1e-9
GUARANA_MAX_G = 4.2
BERRIES = ("blueberry", "lingonberry", "cloudberry", "redcurrant", "blackcurrant")
LIQUID_BASES = ("water", "mineral_water")
CAFFEINE_MG_PER_G = 47.0
TOTAL_MASS_G = 250.0
MIN_LIQUID_G = 40.0
USER_DIMENSIONS = ("vitc_mg", "k_mg", "mg_mg", "ca_mg", "sugar_g", "antioxidant_score")

# This module intentionally owns a second calculation path.  The optimizer may
# use src.nutrients while verification reloads the authoritative JSON and
# recomputes every total from final grams, so optimizer accounting is never
# treated as verification evidence.
_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "nutrients.json"
with _DATA_PATH.open(encoding="utf-8") as _data_file:
    _VERIFY_NUTRIENTS = json.load(_data_file)


def _minmax(field: str) -> dict[str, float]:
    values = {berry: _VERIFY_NUTRIENTS[berry][field] for berry in BERRIES}
    low, high = min(values.values()), max(values.values())
    return {berry: (value - low) / (high - low) for berry, value in values.items()}


_VERIFY_VITC, _VERIFY_VITE, _VERIFY_VITK = (_minmax(field) for field in ("vitc_mg", "vite_mg", "vitk_ug"))
_VERIFY_ANTIOXIDANT = {berry: (_VERIFY_VITC[berry] + _VERIFY_VITE[berry] + _VERIFY_VITK[berry]) / 3 for berry in BERRIES}


def _derived_liquid(recipe: dict[str, float]) -> float:
    return TOTAL_MASS_G - sum(recipe[name] for name in BERRIES) - recipe["guarana_g"]


def _verified_totals(recipe: dict[str, float], liquid_base: str) -> dict[str, float]:
    """Independent §8.1 recomputation, deliberately separate from src.nutrients."""
    amounts = {berry: recipe[berry] for berry in BERRIES}
    amounts[liquid_base] = recipe["liquid_g"]
    dimensions = ("vitc_mg", "k_mg", "mg_mg", "ca_mg", "na_mg", "sugar_g")
    totals = {dimension: sum(amounts[name] * _VERIFY_NUTRIENTS[name][dimension] / 100.0 for name in amounts)
              for dimension in dimensions}
    berry_mass = sum(amounts[berry] for berry in BERRIES)
    totals["antioxidant_score"] = (sum(amounts[berry] * _VERIFY_ANTIOXIDANT[berry] for berry in BERRIES) / berry_mass
                                   if berry_mass else 0.0)
    totals["kcal"] = sum(amounts[name] * _VERIFY_NUTRIENTS[name]["kcal"] / 100.0 for name in amounts)
    totals["fiber_g"] = sum(amounts[name] * _VERIFY_NUTRIENTS[name]["fiber_g"] / 100.0 for name in amounts)
    totals["caffeine_mg"] = recipe["guarana_g"] * CAFFEINE_MG_PER_G
    return totals


def _reject(result: dict[str, object], message: str) -> dict[str, object]:
    result["status"] = "REJECT"
    result["errors"].append(message)
    return result


def _maximum(dimension: str, liquid_base: str) -> float:
    """Upper bound over the §3 berry/liquid capacity; used only for reporting."""
    if dimension == "antioxidant_score":
        return max(_VERIFY_ANTIOXIDANT.values())
    field = dimension
    # At most 210g may be berries; liquid must be at least 40g. Greedily
    # allocate positive linear contributions to the highest-valued berry.
    capacity = TOTAL_MASS_G - MIN_LIQUID_G
    berry_values = sorted(((_VERIFY_NUTRIENTS[berry][field], berry) for berry in BERRIES), reverse=True)
    total = MIN_LIQUID_G * _VERIFY_NUTRIENTS[liquid_base][field] / 100.0
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
    try:
        normalized = {name: float(recipe.get(name, 0.0)) for name in (*BERRIES, "guarana_g")}
        declared_liquid = float(recipe.get("liquid_g", _derived_liquid(normalized)))
    except (TypeError, ValueError) as exc:
        return _reject(result, "ingredient amounts must be finite numeric values")
    if not all(math.isfinite(value) for value in (*normalized.values(), declared_liquid)):
        return _reject(result, "ingredient amounts must be finite numeric values")
    if any(value < 0 for value in normalized.values()):
        return _reject(result, "ingredient amounts must be non-negative")
    if any(normalized[berry] > 80.0 + MASS_TOLERANCE_G for berry in BERRIES):
        return _reject(result, "berry amount exceeds 80 g bound")
    if normalized["guarana_g"] > GUARANA_MAX_G + MASS_TOLERANCE_G:
        return _reject(result, "guarana amount exceeds 4.2 g bound")
    derived_liquid = _derived_liquid(normalized)
    if abs(sum(normalized.values()) + declared_liquid - TOTAL_MASS_G) > MASS_TOLERANCE_G:
        return _reject(result, "mass balance failed")
    if abs(declared_liquid - derived_liquid) > MASS_TOLERANCE_G:
        return _reject(result, "liquid_g must equal derived mass-balance liquid")
    if declared_liquid < MIN_LIQUID_G - MASS_TOLERANCE_G:
        return _reject(result, "liquid below 40 g: optimizer constraint violation")
    accounted_recipe = dict(normalized) | {"liquid_g": declared_liquid}
    totals = _verified_totals(accounted_recipe, liquid_base)
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
