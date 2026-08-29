# Nordic Berry Optimizer

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

`tests/frozen_eval.py` contains the 14 frozen §11 cases unchanged. Both agent and baseline recipes use deterministic verification and per-dimension NNTD reporting. Baseline output records parse/call failures explicitly. Frozen evaluation artifacts are intentionally not claimed here until an explicitly identified LLM callable is supplied and the evaluation is run.

## Reproduction Guide

Use a clean Python 3 environment; no external packages are required.

```bash
python3 -m unittest discover -s tests
python3 -m src.cli --data 100 --liquid-base water
```

Nutrient data is the locked Fineli table in `data/nutrients.json`. Export `OPENROUTER_API_KEY` outside the repository, then create the callable with `make_openrouter_baseline_callable()` and pass it to `run_baseline_cases(..., provider="OpenRouter", model="z-ai/glm-5.2")`. The adapter uses `temperature=0`, `top_p=1`, `max_tokens=2048`, and `stream=false`; model reasoning remains at its documented default because OpenRouter metadata reports reasoning enabled by default with `high`/`xhigh` efforts and does not advertise effort `none`. Zero temperature requests minimal sampling but does not promise bitwise-identical provider output. The key is never stored, printed, or committed.

## Improvement Changelog

The pre-implementation revisions in [DESIGN-LOG.md](DESIGN-LOG.md) document the specification review path. The TASK 2.1 corrective pass added finite numeric validation, a separate verifier accounting path, faithful baseline liquid-base parsing, explicit malformed-baseline reporting, and provider/model labels for baseline evaluation. A pre-evaluation smoke/preflight audit then found that the agent received `liquid_base` while the single-LLM baseline prompt did not; this was corrected in SPEC v1.0-rev6 before any frozen evaluation was run and before any frozen evaluation result was observed. Subsequent pre-evaluation smoke testing found repeated upstream HTTP 429 responses from the free endpoint, HTTP 200 connectivity from the paid endpoint, and a first paid 512-token response with `message.content=null`. Public metadata then showed default reasoning effort `high` with no advertised `none` effort. SPEC v1.0-rev7 therefore selects paid `z-ai/glm-5.2` with `max_tokens=2048` and default reasoning behavior. All changes occurred before frozen evaluation/results; no frozen evaluation result has driven them.

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

## Safety / Responsible Use

This tool optimizes toward a user-defined nutrient profile. It does not diagnose, treat, or promise health or cognitive outcomes. Slider names are nutrient-emphasis labels only. Guarana caffeine is an approximately 47 mg/g project estimate, not a laboratory result. Real-world use needs an appropriate human review boundary for ingredients, allergies, interactions, individual needs, and local guidance; no qualified reviewer approval is claimed here.

## Agent Trajectories

The submission will document representative agent trajectories: instructions, tool actions, feedback, retries, specification checkpoints, and human approval points. This repository records available design history but does not invent missing model transcripts, reviewers, runtime, cost, or evaluation results.
