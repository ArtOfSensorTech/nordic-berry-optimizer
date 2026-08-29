# Design Log

## Pre-implementation design phase

### Iteration 1 — Initial concept

The project started as a Nordic berry drink recipe generator based
on four user preference sliders:

- Data Expert
- Genius
- Fit
- Cute

The initial goal was to generate recipes from Nordic forest berries.

### Iteration 2 — Power Mode and Stimulant Boost

The concept was expanded with:

- Power Mode for Fit
- optional stimulant functionality
- deterministic safety verification

The stimulant concept introduced the need for explicit safety
constraints rather than relying on LLM judgment alone.

### Iteration 3 — Mineral water

Mineral water was introduced as an explicit liquid-base option.

This created an additional optimization dimension through potassium,
magnesium, calcium and sodium contributions.

### Iteration 4 — Mathematical review

The specification was reviewed iteratively with two independent
AI-assisted reviewers before implementation.

Several mathematical and architectural issues were identified and
corrected:

1. Slider weights could produce targets exceeding the intended
   normalization scale.
2. Stimulant Boost had no optimization objective because caffeine was
   not part of the nutrient target vector.
3. Mineral water was not meaningfully represented in the optimization.
4. The antioxidant proxy initially contained an arbitrary VitE ×10
   coefficient.
5. Further consistency checks addressed mass balance, sodium
   normalization, stimulant boundaries and zero-slider input.

### Iteration 5 — Codex specification review

A read-only Codex review of v1.0-rev4 identified four remaining
specification ambiguities:

1. stimulant verification behavior below the minimum caffeine threshold
2. undefined tolerance for the "near-equal NNTD" tie-break
3. inconsistency between Stimulant Boost availability and frozen case #10
4. unspecified verifier behavior when liquid mass falls below the minimum

These were resolved before implementation to preserve deterministic
evaluation and a clean separation between optimization and verification.

### Design principle

The final architecture separates:

1. target generation
2. recipe optimization
3. nutrient calculation
4. deterministic verification
5. evaluation

The key engineering principle is:

> Generation proposes a solution; deterministic verification decides
> whether the solution satisfies the defined constraints.

### Baseline vs. agent

The baseline is a single LLM recipe-generation call without nutrient
calculation or optimization.

The agent solution adds explicit nutrient data, target calculation,
optimization and deterministic verification.

Both are evaluated using the same frozen evaluation set and metrics.

### External review

The design was iteratively reviewed using:
- Claude as an independent design/review perspective
- ChatGPT as a mathematical and architectural reviewer

The final specification was revised based on concrete issues found
during these reviews rather than on stylistic preferences.

## Status

Pre-implementation design complete.

The mathematical specification is frozen before implementation.