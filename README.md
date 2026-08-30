# Nordic Berry Optimizer

**[▶ Launch the Interactive Demo](https://artofsensortech.github.io/nordic-berry-optimizer/)**

Hackathon Video: https://vimeo.com/1222496888

Deterministic Nordic berry drink optimization with independent verification — built as an auditable AI-agent engineering workflow.

## Problem & Intended User

This is a deterministic optimizer for a 250 g Nordic berry drink. A user selects nutrient emphasis through Data Expert, Genius, Fit, and Cute sliders, then chooses a liquid base and optional toggles. The intended user is exploring a constrained recipe target profile, not seeking diagnosis or care.

## Bottleneck / Why It Matters

Ingredient amounts, liquid displacement, sodium, caffeine, and a mass-weighted antioxidant proxy interact. Manually comparing combinations is error-prone, particularly when a stimulant add-in changes the available liquid mass. The project makes that trade-off explicit and reproducible.

## Agent Solution

The agent builds the locked target vector, jointly searches five berries plus guarana, derives liquid mass, and minimizes seven-dimension NNTD. The search uses Python's standard library only and deterministic multi-start coordinate refinement (20 g through 0.01 g). Verification independently reloads `data/nutrients.json` and recalculates final totals instead of accepting optimizer-reported totals. Mass comparisons use a `1e-9 g` floating-point representation tolerance only.

The antioxidant figure is a project-specific equal-weight proxy constructed from normalized Fineli VitC, VitE, and VitK values. It is not a biological antioxidant-potency model.

## Baseline

The baseline is exactly the frozen §10 one-shot prompt, with no nutrient tools. The official adapter uses OpenRouter's OpenAI-compatible endpoint and the fixed model ID `z-ai/glm-5.2` (Z.ai GLM 5.2), not `openrouter/free`. It sends the frozen prompt as the sole user message and omits all tool declarations, project files, web search, and file access. SPEC v1.0-rev7 explicitly supplies each case's `liquid_base` in that prompt. v1 uses an exclusive liquid-base choice: `water` or `mineral_water`; mixtures are not supported. More general liquid compositions, such as milk, coffee, or mixtures, are future work and are outside v1 and the frozen evaluation. The parser preserves an LLM's stated water versus mineral-water choice; absent or conflicting liquid declarations are recorded as invalid, never guessed or repaired.

### Pre-evaluation live checkpoint

After rev7 was committed, exactly one deliberately non-frozen smoke case was
run with Data Expert 37, Genius 61, Fit 22, Cute 14, Power Mode off,
Stimulant Boost off, and liquid base water. Using the committed configuration
(OpenRouter, `z-ai/glm-5.2`, `temperature=0`, `top_p=1`, `max_tokens=2048`,
`stream=false`, default reasoning), the request returned HTTP 200 with
non-empty assistant text. This confirmed paid endpoint and live transport/
model-response connectivity end-to-end, but not the full parser/verifier/NNTD
success path: the committed parser classified the response `INVALID` because
the model used parenthesized ingredient labels it did not recognize, and NNTD
was not scorable. The raw response also specified both 100 g water and 100 g
mineral water despite `Liquid base: water.`, violating v1's exclusive choice.
No retry, repair, reinterpretation, parser adaptation, or protocol change was
made after observing this output. No frozen case or result had been observed.

## Evaluation Method

`tests/frozen_eval.py` contains the 14 frozen §11 cases unchanged. Both agent and baseline recipes use deterministic verification and per-dimension NNTD reporting. Baseline output records parse/call failures explicitly. The official run completed all 14 cases with one baseline attempt per case; its committed artifacts are `evaluation/baseline_results.json`, `evaluation/agent_results.json`, `evaluation/comparison.csv`, and `evaluation/run_status.json`.

### Official frozen run #2

The deterministic agent produced PASS=11, WARN=1, and REJECT=2, with 12 of 14 outputs scorable. The baseline produced parse PASS=5, parse INVALID=8, and CALL_FAILED=1; verifier results were PASS=1, WARN=0, and REJECT=13, with 1 of 14 attempts scorable. The baseline figure is a result of the locked parser/verifier pipeline, not a pure model-capability score: some raw responses were internally mass-balanced or named a supported liquid, but the deliberately simple free-text parser did not preserve their structure.

In cases 1, 2, 9, and 10, the raw baseline responses visibly stated ingredient quantities totaling 250 g. The locked parser omitted berry quantities, and cases 1 and 9 also double-counted repeated water quantities; deterministic verification then rejected the resulting structured recipes for mass balance. The raw responses themselves satisfied the 250 g mass requirement; the structured recipes passed to verification did not, because of limitations in the locked free-text parser. Other baseline failures were liquid-base parsing failures: cases 3, 7, and 11 explicitly used both bases, case 5 had no usable explicit base, and cases 4, 8, 12, and 13 stated one supported base in formatting the locked parser did not recognize. Case 14 had an empty assistant response recorded as CALL_FAILED. No repair, retry, or reinterpretation was performed.

Only case 6 was scorable for both systems. Its agent NNTD was approximately 0.176 versus 0.288 for the baseline. This is paired n=1 and does not establish general NNTD superiority. Case 6 used Boost=off and the recorded agent recipe contained 4.2 g guarana; this is legal under rev8, has no direct Boost-off caffeine objective, and can affect NNTD indirectly through the fixed 250 g mass allocation. It was classified as SEARCH_ARTIFACT_WITHIN_SPEC, with no implementation defect found.

Cases 11 and 12 matched their pre-declared expectations in the pre-implementation SPEC: Cute=100 plus Stimulant Boost was expected to REJECT, while Cute=100 plus mineral water was expected to WARN rather than reject. Those predictions were already present in `2d3128c` (`docs: lock SPEC v1.0-rev5 after second pre-implementation review`), before `61a3b7a` (`feat: implement Nordic Berry Optimizer`) and before the frozen evaluation.

## Reproduction Guide

Use Python 3.10 or newer in a clean environment; no external packages are required. Run the following commands from the repository root:

```bash
python3 -m unittest discover -s tests
python3 -m src.cli --data 100 --liquid-base water
```

The CLI command runs the agent path locally—target construction, optimization, and independent verification—with no LLM/API call, network access, credentials, or monetary cost.

Nutrient data is the locked Fineli table in `data/nutrients.json`. Export `OPENROUTER_API_KEY` outside the repository, then create the callable with `make_openrouter_baseline_callable()` and pass it to `run_baseline_cases(..., provider="OpenRouter", model="z-ai/glm-5.2")`. The adapter uses `temperature=0`, `top_p=1`, `max_tokens=2048`, and `stream=false`; model reasoning remains at its documented default because OpenRouter metadata reports reasoning enabled by default with `high`/`xhigh` efforts and does not advertise effort `none`. Zero temperature requests minimal sampling but does not promise bitwise-identical provider output. The key is never stored, printed, or committed.

The agent-only path has no API cost; baseline reproduction uses the paid OpenRouter model and therefore incurs provider charges.

## Improvement Changelog

The important experiments and decisions are summarized below; detailed
specification history is in [DESIGN-LOG.md](DESIGN-LOG.md).

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Simple baseline | Started with a single one-shot LLM recipe request to establish a transparent comparator without tools or project context. | [SPEC.md](SPEC.md) §10; commit `4d06e7e` | Keep the baseline simple and auditable, while treating free-text parsing as a separate failure surface. |
| Target model and normalization | Reviewed slider-to-target construction so four preferences remain normalized and comparable. | [SPEC.md](SPEC.md) §5; commits `0d49eb4`, `2d3128c`; [DESIGN-LOG.md](DESIGN-LOG.md) | Lock the target construction before implementation rather than tune it from evaluation output. |
| Stimulant/caffeine objective | Added a measurable Boost objective and feasibility rule instead of leaving Stimulant Boost as a label: caffeine 50–200 mg, with a 100 mg target/tie-break. | [SPEC.md](SPEC.md) §§6–7; [DESIGN-LOG.md](DESIGN-LOG.md) | Make Boost behavior explicit and deterministic. Cute ≥80 plus Boost remains a hard reject. |
| Mineral-water representation | Added an explicit, exclusive `water`/`mineral_water` choice and its sodium treatment. | [SPEC.md](SPEC.md) §§5–6; [DESIGN-LOG.md](DESIGN-LOG.md) | Preserve the selected liquid base as a real task input; mixtures remain outside v1. |
| Antioxidant proxy | Challenged the early arbitrary VitE ×10 coefficient because it had no defensible basis; removed it before implementation and used equal weighting of the defined vitamin components. | [SPEC.md](SPEC.md) §2; [DESIGN-LOG.md](DESIGN-LOG.md) Iteration 4 | Prefer a documented, reproducible proxy over an unsupported weighting. |
| Mass balance and guarana | Corrected the serving equation to include guarana and derived liquid, with liquid ≥40 g. | [SPEC.md](SPEC.md) §§3, 7; [DESIGN-LOG.md](DESIGN-LOG.md) Iteration 5 | Make mass balance an explicit verifier constraint; do not infer quality from optimizer totals alone. |
| Independent verifier | Separated nutrient reloading/recalculation and verification from optimizer-reported accounting. | [src/verify.py](src/verify.py); commit `ae0bbd4`; tests | Generation proposes a recipe; deterministic verification decides whether the defined constraints hold. |
| Input parity | Found that the agent received `liquid_base` while the baseline prompt did not, and added it before any frozen evaluation. | [SPEC.md](SPEC.md) rev6; commit `53a3cd4` | Baseline and agent receive the same frozen liquid-base input; frozen cases were unchanged. |
| Paid baseline protocol | Free endpoint smoke requests returned upstream 429; paid connectivity returned 200, while the first paid 512-token response had empty content. Metadata showed default high reasoning and no advertised `none` effort. | [SPEC.md](SPEC.md) rev7; commit `aa02fe2`; [DESIGN-LOG.md](DESIGN-LOG.md) | Lock paid `z-ai/glm-5.2`, `max_tokens=2048`, and default reasoning for reliability/reproducibility before evaluation. |
| Recovery protocol | Frozen run #1 reached 9/14 requests, with case 9 empty content; per-case checkpointing and failure isolation were added. | [incidents/2026-08-29-partial-run-9-of-14/](incidents/2026-08-29-partial-run-9-of-14/); [SPEC.md](SPEC.md) rev8; commit `94f97a4` | Keep exactly one attempt per case, persist `CALL_FAILED`, and continue without retry, repair, fallback, or substitution. |
| Final frozen evaluation | Ran all 14 cases under the locked protocol after the recovery correction. | [evaluation/](evaluation/); commit `eac8463` | Agent 12/14 and baseline 1/14 are end-to-end workflow results under deterministic verification and the locked parser, not a pure model-capability comparison. Only one case was paired/scorable; no broad NNTD superiority or global-optimum claim follows. |

Frozen run #1 was an incomplete failed run: cases 1–8 returned baseline text,
case 9 produced empty assistant content and was recorded `CALL_FAILED`, and
cases 10–14 were never attempted. Its artifacts are preserved under
`incidents/2026-08-29-partial-run-9-of-14/`. The initial apparent absence of
artifacts was a timing/tool-output race; partial results were eventually
persisted. The diagnosis was read-only, with no retry and no raw frozen output
used to tune methodology.

SPEC v1.0-rev8 changes whole-run fail-fast behavior to per-case failure
isolation: every frozen case receives exactly one baseline attempt, and a
`CALL_FAILED` case is retained and followed by the next case without retry,
repair, fallback, or substitution. Per-case atomic checkpoints now update the
normal evaluation artifacts and `evaluation/run_status.json` immediately after
each attempted case. The model, prompts, parser, verifier, optimizer, NNTD,
scoring, and generation settings remain unchanged. OpenRouter automatically
routes requests for the same model ID across backend providers; minor response
variation between reproduction runs is possible. Backend pinning was not
introduced after run #1 because it would change the locked transport
configuration. Two run #1 requests reached the 2048-token generation ceiling;
`max_tokens` was deliberately not changed.

## Main Failure Mode

The deterministic coordinate search is bounded and reproducible but is not a formal global-optimum proof for the nonlinear mass-weighted antioxidant ratio. Baseline evaluation also cannot begin until an operator supplies and identifies the required LLM callable.

## Hot Take / Engineering Insight

For an agentic optimization workflow, a separate verifier is more valuable than a persuasive recipe narrative: generation can propose, but only explicit data-backed checks should decide whether a constrained recipe is valid.

The interface between free-text LLM output and structured verification is itself a failure surface. Several raw baseline recipes were internally mass-balanced, yet the deliberately simple locked parser failed to preserve their ingredient quantities correctly. Verification can only be as reliable as the structured representation it receives. The agent path passes the optimizer's structured recipe dictionary directly to deterministic verification, without an equivalent prose-to-regex reconstruction step; this is an implementation distinction, not proof that structured-output agents are universally superior.

## Future Work

Future work includes more robust structured-output handling for the baseline. The v1 parser was not modified after frozen results were observed, preserving evaluation integrity. The deterministic optimizer is reproducible but provides no formal global-optimum guarantee. A future demo could also add an inverse “Analyze my recipe” mode that accepts ingredient quantities and estimates the resulting Data Expert, Genius, Fit, and Cute profile; that is outside frozen v1 semantics.

## Safety / Responsible Use

This tool optimizes toward a user-defined nutrient profile. It does not diagnose, treat, or promise health or cognitive outcomes. Slider names are nutrient-emphasis labels only. Guarana caffeine is an approximately 47 mg/g project estimate, not a laboratory result. Real-world use needs an appropriate human review boundary for ingredients, allergies, interactions, individual needs, and local guidance; no qualified reviewer approval is claimed here.

## Agent Trajectories

Representative summarized trajectories, reconstructed from committed design
history, source, tests, artifacts, and Git history, are recorded in
[AGENT-TRAJECTORIES.md](AGENT-TRAJECTORIES.md). Raw CLI/conversation
transcripts are not committed; missing raw traces are identified rather than
invented.
