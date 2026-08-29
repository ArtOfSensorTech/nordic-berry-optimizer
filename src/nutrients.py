"""Fixed nutrient accounting from SPEC.md §§2–3."""

from __future__ import annotations

import json
from pathlib import Path

BERRIES = ("blueberry", "lingonberry", "cloudberry", "redcurrant", "blackcurrant")
LIQUID_BASES = ("water", "mineral_water")
CAFFEINE_MG_PER_G = 47.0
TOTAL_MASS_G = 250.0
MIN_LIQUID_G = 40.0

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "nutrients.json"
with _DATA_PATH.open(encoding="utf-8") as _data_file:
    NUTRIENTS = json.load(_data_file)


def _minmax(field: str) -> dict[str, float]:
    values = {berry: NUTRIENTS[berry][field] for berry in BERRIES}
    low, high = min(values.values()), max(values.values())
    return {berry: (value - low) / (high - low) for berry, value in values.items()}


_VITC, _VITE, _VITK = (_minmax(field) for field in ("vitc_mg", "vite_mg", "vitk_ug"))
ANTIOXIDANT_SCORES = {berry: (_VITC[berry] + _VITE[berry] + _VITK[berry]) / 3 for berry in BERRIES}


def liquid_mass(recipe: dict[str, float]) -> float:
    return TOTAL_MASS_G - sum(float(recipe.get(name, 0.0)) for name in BERRIES) - float(recipe.get("guarana_g", 0.0))


def nutrient_totals(recipe: dict[str, float], liquid_base: str) -> dict[str, float]:
    """Independently calculate final recipe totals; all table values are per 100 g."""
    if liquid_base not in LIQUID_BASES:
        raise ValueError("liquid_base must be water or mineral_water")
    liquid_g = float(recipe.get("liquid_g", liquid_mass(recipe)))
    amounts = {berry: float(recipe.get(berry, 0.0)) for berry in BERRIES}
    amounts[liquid_base] = liquid_g
    field_map = {"vitc_mg": "vitc_mg", "k_mg": "k_mg", "mg_mg": "mg_mg", "ca_mg": "ca_mg", "na_mg": "na_mg", "sugar_g": "sugar_g"}
    totals = {dimension: sum(amounts.get(item, 0.0) * NUTRIENTS[item][field] / 100.0 for item in amounts)
              for dimension, field in field_map.items()}
    berry_mass = sum(amounts[berry] for berry in BERRIES)
    totals["antioxidant_score"] = (sum(amounts[berry] * ANTIOXIDANT_SCORES[berry] for berry in BERRIES) / berry_mass
                                   if berry_mass else 0.0)
    totals["kcal"] = sum(amounts.get(item, 0.0) * NUTRIENTS[item]["kcal"] / 100.0 for item in amounts)
    totals["fiber_g"] = sum(amounts.get(item, 0.0) * NUTRIENTS[item]["fiber_g"] / 100.0 for item in amounts)
    totals["caffeine_mg"] = float(recipe.get("guarana_g", 0.0)) * CAFFEINE_MG_PER_G
    return totals
