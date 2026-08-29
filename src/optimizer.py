"""Deterministic joint ingredient search for SPEC.md §7."""

from __future__ import annotations

from .metrics import nntd_report
from .nutrients import BERRIES, CAFFEINE_MG_PER_G, MIN_LIQUID_G, TOTAL_MASS_G, liquid_mass, nutrient_totals
from .target import build_target

GUARANA_MAX_G = 4.2
CAFFEINE_TARGET_MG = 100.0
NNTD_TIE_TOLERANCE = 1e-9


def _feasible(recipe: dict[str, float], stimulant_boost: bool) -> bool:
    berries = [float(recipe[name]) for name in BERRIES]
    guarana = float(recipe["guarana_g"])
    if any(value < 0 or value > 80 for value in berries) or not 0 <= guarana <= GUARANA_MAX_G:
        return False
    if liquid_mass(recipe) < MIN_LIQUID_G - 1e-12:
        return False
    caffeine = guarana * CAFFEINE_MG_PER_G
    return not stimulant_boost or 50.0 - 1e-12 <= caffeine <= 200.0 + 1e-12


def _candidate(recipe: dict[str, float], target: dict[str, float], liquid_base: str) -> dict[str, object]:
    proposed = dict(recipe)
    proposed["liquid_g"] = liquid_mass(proposed)
    totals = nutrient_totals(proposed, liquid_base)
    report = nntd_report(totals, target)
    return {"recipe": proposed, "totals": totals, "metric": report}


def _better(candidate: dict[str, object], incumbent: dict[str, object], stimulant_boost: bool) -> bool:
    candidate_nntd = float(candidate["metric"]["nntd"])
    incumbent_nntd = float(incumbent["metric"]["nntd"])
    if candidate_nntd < incumbent_nntd - NNTD_TIE_TOLERANCE:
        return True
    if abs(candidate_nntd - incumbent_nntd) > NNTD_TIE_TOLERANCE:
        return False
    if stimulant_boost:
        candidate_gap = abs(float(candidate["totals"]["caffeine_mg"]) - CAFFEINE_TARGET_MG)
        incumbent_gap = abs(float(incumbent["totals"]["caffeine_mg"]) - CAFFEINE_TARGET_MG)
        if candidate_gap < incumbent_gap - 1e-12:
            return True
        if abs(candidate_gap - incumbent_gap) > 1e-12:
            return False
    # Stable lexicographic tie-break makes identical scores reproducible.
    return tuple(candidate["recipe"][name] for name in (*BERRIES, "guarana_g")) < tuple(
        incumbent["recipe"][name] for name in (*BERRIES, "guarana_g"))


def _seed_recipes(stimulant_boost: bool) -> list[dict[str, float]]:
    guarana_values = [100.0 / CAFFEINE_MG_PER_G] if stimulant_boost else [0.0]
    seeds: list[dict[str, float]] = []
    for guarana in guarana_values:
        base = {name: 0.0 for name in BERRIES} | {"guarana_g": guarana}
        seeds.append(base)
        for berry in BERRIES:
            seed = dict(base)
            seed[berry] = 80.0
            seeds.append(seed)
        equal = dict(base)
        for berry in BERRIES:
            equal[berry] = (TOTAL_MASS_G - MIN_LIQUID_G - guarana) / len(BERRIES)
        seeds.append(equal)
    return seeds


def optimize(sliders: dict[str, float], *, power_mode: bool = False,
             stimulant_boost: bool = False, liquid_base: str = "water") -> dict[str, object]:
    """Joint deterministic coordinate-pattern search over berries and guarana.

    The nutrient objective includes the nonlinear mass-weighted antioxidant
    ratio, so a standard linear least-squares formulation would not implement
    §2 exactly. This bounded multi-start search evaluates the authoritative
    nutrient calculator for every candidate and refines from 20 g to 0.01 g.
    """
    target, warnings = build_target(sliders, power_mode=power_mode,
                                    stimulant_boost=stimulant_boost, liquid_base=liquid_base)
    best: dict[str, object] | None = None
    variable_names = (*BERRIES, "guarana_g")
    for seed in _seed_recipes(stimulant_boost):
        if not _feasible(seed, stimulant_boost):
            continue
        current = _candidate(seed, target, liquid_base)
        for step in (20.0, 5.0, 1.0, 0.1, 0.01):
            improved = True
            while improved:
                improved = False
                for name in variable_names:
                    for direction in (-1.0, 1.0):
                        trial_recipe = dict(current["recipe"])
                        trial_recipe.pop("liquid_g", None)
                        trial_recipe[name] += direction * step
                        if not _feasible(trial_recipe, stimulant_boost):
                            continue
                        trial = _candidate(trial_recipe, target, liquid_base)
                        if _better(trial, current, stimulant_boost):
                            current = trial
                            improved = True
        if best is None or _better(current, best, stimulant_boost):
            best = current
    if best is None:  # Defensive: §6 bounds are feasible with §3 mass limits.
        raise RuntimeError("no feasible recipe exists for the requested constraints")
    best["target"] = target
    best["warnings"] = warnings
    best["algorithm"] = "deterministic multi-start coordinate-pattern search (20g to 0.01g)"
    return best
