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

### Iteration 6 — TASK 2.1 implementation audit corrective pass

A read-only audit of the initial implementation found four risks before frozen
evaluation:

1. non-finite slider and ingredient values could evade ordinary comparisons;
2. verification recomputed totals but shared the optimizer's accounting path;
3. baseline parsing discarded whether the LLM chose water or mineral water;
4. baseline evaluation required a concrete, explicitly identified LLM adapter
   but the repository did not yet describe that configuration boundary.

The corrective pass added finite-number rejection, a JSON-backed verifier
calculation path separate from optimizer accounting, explicit baseline parse
statuses with preserved liquid base, malformed-output reporting, and an
injected provider-agnostic LLM callable requiring provider/model labels. It
also expanded the Rule Book documentation. No TASK 3 frozen evaluation result
was generated or used during this pass.

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

## TASK 2.1 — Pre-evaluation corrective pass

The TASK 2 implementation was subjected to a read-only audit before the
frozen evaluation.

The audit identified four material implementation issues:

1. Non-finite numeric inputs such as NaN and infinity were not explicitly
   rejected.
2. Verifier nutrient accounting was not sufficiently independent from
   the optimizer's accounting path.
3. Baseline liquid-base selection was not faithfully preserved during
   parsing and scoring.
4. The baseline runner required an injected LLM callable, but the actual
   provider/model configuration remained an evaluation-time decision.

### Corrections

The implementation was updated to:

- reject non-finite slider and ingredient values;
- independently recompute nutrient and caffeine values in the verifier;
- preserve and validate the baseline's declared water/mineral-water
  selection;
- explicitly classify malformed or ambiguous baseline output;
- keep the baseline LLM interface provider-agnostic;
- improve tests covering the corrected behavior;
- improve README documentation for reproducibility, safety,
  improvement history, failure modes, and agent trajectories.

### Verification

The corrected implementation passed:

- 26 unit/integration tests
- `git diff --check`
- credential/secret scan

The locked SPEC.md remained byte-for-byte unchanged.

No frozen evaluation was performed during this corrective pass, and no
evaluation artifacts were generated.

### Checkpoint

TASK 2.1 was committed as:

`ae0bbd4 fix: harden verification and baseline evaluation`

The Git working tree was clean after the commit.

## Pre-evaluation status

The implementation is now frozen for the evaluation phase.

Remaining evaluation configuration:
- select and document the actual LLM/provider/model used for the
  baseline;
- run the frozen evaluation set;
- collect baseline vs. agent results without changing the frozen cases.