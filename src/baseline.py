"""Frozen §10 baseline prompt and deterministic ingredient parser."""

from __future__ import annotations

import re

FROZEN_PROMPT = (
    "Suggest a berry drink recipe using any of blueberry, lingonberry, "
    "cloudberry, redcurrant, blackcurrant, water, and mineral water. The "
    "drink should emphasize: Data Expert {data}%, Genius {genius}%, Fit {fit}%, "
    "Cute {cute}%. Power Mode: {power_mode}. Stimulant Boost: {stimulant_boost}. "
    "Give exact grams of each ingredient for a 250g serving."
)

_ALIASES = {
    "blueberry": "blueberry", "lingonberry": "lingonberry", "cloudberry": "cloudberry",
    "redcurrant": "redcurrant", "red currant": "redcurrant", "blackcurrant": "blackcurrant",
    "black currant": "blackcurrant", "guarana": "guarana_g", "guarana powder": "guarana_g",
    "water": "liquid_g", "mineral water": "liquid_g",
}


def baseline_prompt(case: dict[str, object]) -> str:
    sliders = case["sliders"]
    return FROZEN_PROMPT.format(data=sliders.get("data", 0), genius=sliders.get("genius", 0),
                                fit=sliders.get("fit", 0), cute=sliders.get("cute", 0),
                                power_mode="on" if case.get("power_mode") else "off",
                                stimulant_boost="on" if case.get("stimulant_boost") else "off")


def parse_baseline_recipe(text: str) -> dict[str, float]:
    """Extract exact gram declarations without trying to repair an LLM recipe."""
    recipe: dict[str, float] = {}
    pattern = re.compile(r"(?P<name>blueberry|lingonberry|cloudberry|red\s*currant|black\s*currant|"
                         r"mineral\s*water|water|guarana(?:\s+powder)?)\s*[:\-]?\s*"
                         r"(?P<grams>\d+(?:\.\d+)?)\s*g(?:rams?)?\b", re.IGNORECASE)
    for match in pattern.finditer(text):
        normalized_name = " ".join(match.group("name").lower().split())
        key = _ALIASES[normalized_name]
        recipe[key] = recipe.get(key, 0.0) + float(match.group("grams"))
    return recipe
