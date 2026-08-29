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

## TASK 3 preparation — OpenRouter baseline adapter

OpenRouter was selected as the evaluation API gateway, with Z.ai GLM 5.2 as
the named baseline model (`z-ai/glm-5.2`). A fixed model ID is used rather
than `openrouter/free` so the baseline does not silently route among changing
models. The standard-library adapter sends only the exact frozen §10
prompt as a user message and makes no tool, web, file, or project-context
request. Authentication is read only from `OPENROUTER_API_KEY` outside the
repository. The protocol uses `temperature=0`, `top_p=1`, `max_tokens=2048`,
and `stream=false`; it leaves the model's documented default reasoning
behavior in place and sends no unsupported `none` effort. Focused mocked-HTTP
tests validate the request shape without a real key. The frozen evaluation has
not yet been run.

### TASK 3.0 — Pre-evaluation input-parity correction

A read-only smoke/preflight audit found that every frozen case supplied
`liquid_base` to the agent, while the single-LLM baseline prompt omitted that
case input. This was an input-parity defect, not an observed evaluation
result. The prompt and its validation were corrected in SPEC v1.0-rev6 before
any frozen evaluation was run and before any frozen evaluation result was
observed.

For v1, `liquid_base` is exclusive: the derived liquid portion is either
`water` or `mineral_water`. Water/mineral-water mixtures and more general
liquid compositions such as milk, coffee, or mixtures are outside v1 scope,
 outside the frozen evaluation, and reserved for possible future work. The
 frozen cases themselves were not changed.

### TASK 3.7 — Paid baseline protocol lock

Pre-evaluation smoke testing repeatedly received upstream HTTP 429 from the
free `z-ai/glm-5.2:free` endpoint. A paid `z-ai/glm-5.2` connectivity smoke
then returned HTTP 200, but its first request with `max_tokens=512` returned
`message.content=null`. Public model metadata reported reasoning enabled by
default, default effort `high`, non-mandatory reasoning, and supported efforts
`high` and `xhigh`; effort `none` was not advertised.

Before any frozen evaluation was run or any frozen result was observed, rev7
therefore selected paid `z-ai/glm-5.2`, increased `max_tokens` to 2048, and
retained the default reasoning behavior. This is a reliability and
reproducibility correction, not a change based on evaluation performance. The
14 frozen cases, prompts, objectives, verifier, optimizer, NNTD, nutrient
data, constraints, and evaluation semantics remain unchanged.

### TASK 4.1 — Failed-run preservation and rev8 recovery protocol

Frozen run #1 made 9 baseline requests: cases 1–8 returned text, case 9
produced empty assistant content and was recorded `CALL_FAILED`, and cases
10–14 were not attempted. The original apparent absence of artifacts was a
timing/tool-output race; the partial artifacts eventually appeared and were
preserved byte-for-byte under
`incidents/2026-08-29-partial-run-9-of-14/`. The forensic diagnosis was
read-only; no retry occurred and no raw frozen output was used to tune the
methodology.

SPEC v1.0-rev8 changes only failure isolation: each frozen case receives one
baseline attempt, a normal `CALL_FAILED` is preserved and the next case is
attempted, and failed cases are never retried, repaired, or substituted. The
run stops only when an infrastructure/configuration failure makes safe
continuation ambiguous. Per-case atomic same-filesystem checkpoints now write
the three normal artifacts and `evaluation/run_status.json` after each
attempted case, with monotonic request ordinals and completed case IDs. This
improves completeness and persistence, not model performance; prompts, model,
generation settings, routing, parser, verifier, optimizer, NNTD, scoring,
nutrient data, and frozen cases remain unchanged.

OpenRouter automatically routes requests for the same model ID across backend
providers; minor response variation between reproduction runs is possible.
Backend pinning was deliberately not introduced after run #1 because it would
change the already locked transport configuration. Two requests in run #1
reached the locked 2048-token generation ceiling, and `max_tokens` was not
changed.

### TASK 3.8 — Final paid baseline smoke checkpoint

After rev7 was committed, exactly one deliberately non-frozen smoke case was
run: Data Expert 37, Genius 61, Fit 22, Cute 14, Power Mode off, Stimulant
Boost off, liquid base water. The committed OpenRouter configuration used
`z-ai/glm-5.2`, `temperature=0`, `top_p=1`, `max_tokens=2048`, `stream=false`,
and default model reasoning. It returned HTTP 200 with non-empty assistant
text, confirming paid endpoint and transport/model-response connectivity.

The committed parser classified the response `INVALID` because the model used
parenthesized ingredient labels that it did not recognize; NNTD was therefore
not scorable. The raw response also specified both 100 g water and 100 g
mineral water despite `Liquid base: water.`, violating v1's exclusive
liquid-base contract. No retry, repair, manual reinterpretation, parser
adaptation, or evaluation-protocol change followed the output. No frozen case
was run and no frozen result was observed. The smoke validated the live
pre-evaluation pipeline while preserving malformed or contract-violating
baseline output for rejection.

### TASK 4.2C/4.4/4.4B — Post-run read-only audits

After run #2 completed, read-only audits examined the three non-PASS agent
cases and the baseline failure attribution. Cases 11 and 13 were intentionally
rejected by the locked Cute≥80 plus Stimulant Boost input rule; case 12 was the
pre-declared Cute=100 plus mineral-water WARN case. The agent path passes a
native structured recipe dictionary from the optimizer directly to the
verifier. The case-6 Boost-off 4.2 g guarana observation is legal under rev8:
guarana remains a search variable, has no direct Boost-off caffeine objective,
and can change nutrient totals indirectly through fixed-mass liquid
allocation. It was classified as SEARCH_ARTIFACT_WITHIN_SPEC, not an
implementation defect.

The baseline raw-response audit found that cases 1, 2, 9, and 10 visibly
stated 250 g ingredient totals, while the locked parser omitted berry amounts
and double-counted repeated water mentions in cases 1 and 9. Verification
correctly rejected the resulting structured recipes for mass balance. The
other INVALID cases comprised three responses explicitly using both liquid
bases (3, 7, 11), one with no usable explicit base (5), and four that stated
one supported base in formatting the locked parser did not recognize (4, 8,
12, 13). Case 14 was an empty assistant response recorded as CALL_FAILED.
These audits attributed failures without changing results,
parser behavior, scoring, or protocol.

The audits were deliberately read-only: no frozen result, raw response, or
parser behavior was changed after observation. The committed run remains the
authoritative record, and later interpretation is kept separate from frozen
evaluation data.

### Official frozen run #2 result

Run #2 completed all 14 cases with exactly one baseline attempt per case. The
agent outcomes were PASS=11, WARN=1, REJECT=2, with 12 scorable cases. The
baseline outcomes were parse PASS=5, parse INVALID=8, CALL_FAILED=1, verifier
PASS=1, WARN=0, REJECT=13, with 1 scorable case. Only case 6 was paired and
scorable: agent NNTD ≈0.176 and baseline NNTD ≈0.288 (paired n=1, not a
general superiority claim). The artifacts were committed unchanged in
`eac8463`.
