"""Frozen §10 baseline prompt and deterministic ingredient parser."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

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


@dataclass(frozen=True)
class BaselineParseResult:
    """A deterministic parse outcome; no missing amounts or liquid are guessed."""

    status: str
    recipe: dict[str, float]
    liquid_base: str | None
    reason: str | None = None


BaselineLLMCallable = Callable[[str], str]


def validate_llm_configuration(provider: str, model: str) -> None:
    """Require truthful labels before an operator runs the injected baseline callable."""
    if not provider.strip() or not model.strip():
        raise ValueError("baseline evaluation requires explicit provider and model labels")


def baseline_prompt(case: dict[str, object]) -> str:
    sliders = case["sliders"]
    return FROZEN_PROMPT.format(data=sliders.get("data", 0), genius=sliders.get("genius", 0),
                                fit=sliders.get("fit", 0), cute=sliders.get("cute", 0),
                                power_mode="on" if case.get("power_mode") else "off",
                                stimulant_boost="on" if case.get("stimulant_boost") else "off")


def parse_baseline_recipe(text: str) -> BaselineParseResult:
    """Parse natural ingredient/grams forms and preserve the stated liquid base."""
    recipe: dict[str, float] = {}
    ingredient = r"blueberry|lingonberry|cloudberry|red\s*currant|black\s*currant|mineral\s*water|water|guarana(?:\s+powder)?"
    number = r"\d+(?:\.\d+)?"
    patterns = (
        re.compile(rf"\b(?P<name>{ingredient})\b\s*(?:[:\-]|is)?\s*(?P<grams>{number})\s*g(?:rams?)?\b", re.IGNORECASE),
        re.compile(rf"(?P<grams>{number})\s*g(?:rams?)?\s*(?:of\s+)?(?P<name>{ingredient})\b", re.IGNORECASE),
    )
    liquid_names: set[str] = set()
    matches = []
    for pattern in patterns:
        matches.extend(pattern.finditer(text))
    for match in sorted(matches, key=lambda item: item.start()):
        normalized_name = " ".join(match.group("name").lower().split())
        key = _ALIASES[normalized_name]
        recipe[key] = recipe.get(key, 0.0) + float(match.group("grams"))
        if normalized_name in ("water", "mineral water"):
            liquid_names.add("mineral_water" if normalized_name == "mineral water" else "water")
    if len(liquid_names) != 1:
        reason = "baseline output does not specify a supported liquid base" if not liquid_names else "baseline output specifies both water and mineral water"
        return BaselineParseResult("INVALID", recipe, None, reason)
    if not recipe:
        return BaselineParseResult("INVALID", recipe, None, "baseline output contains no supported ingredient quantities")
    return BaselineParseResult("PASS", recipe, liquid_names.pop())
