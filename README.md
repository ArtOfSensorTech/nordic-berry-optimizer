# Nordic Berry Optimizer

## Problem & Intended User

This is a deterministic optimizer for a 250 g Nordic berry drink. A user selects nutrient emphasis through Data Expert, Genius, Fit, and Cute sliders, then chooses a liquid base and optional toggles. The intended user is exploring a constrained recipe target profile, not seeking diagnosis or care.

## Bottleneck / Why It Matters

Ingredient amounts, liquid displacement, sodium, caffeine, and a mass-weighted antioxidant proxy interact. Manually comparing combinations is error-prone, particularly when a stimulant add-in changes the available liquid mass. The project makes that trade-off explicit and reproducible.

## Agent Solution

The agent builds the locked target vector, jointly searches five berries plus guarana, derives liquid mass, and minimizes seven-dimension NNTD. The search uses Python's standard library only and deterministic multi-start coordinate refinement (20 g through 0.01 g). Verification independently reloads `data/nutrients.json` and recalculates final totals instead of accepting optimizer-reported totals. Mass comparisons use a `1e-9 g` floating-point representation tolerance only.

The antioxidant figure is a project-specific equal-weight proxy constructed from normalized Fineli VitC, VitE, and VitK values. It is not a biological antioxidant-potency model.

## Baseline

The baseline is exactly the frozen §10 one-shot prompt, with no nutrient tools. At evaluation time an operator supplies a provider-agnostic callable plus explicit `provider` and `model` labels. No credentials, provider, or model are hardcoded. The parser preserves an LLM's stated water versus mineral-water choice; absent or conflicting liquid declarations are recorded as invalid, never guessed or repaired.

## Evaluation Method

`tests/frozen_eval.py` contains the 14 frozen §11 cases unchanged. Both agent and baseline recipes use deterministic verification and per-dimension NNTD reporting. Baseline output records parse/call failures explicitly. Frozen evaluation artifacts are intentionally not claimed here until an explicitly identified LLM callable is supplied and the evaluation is run.

## Reproduction Guide

Use a clean Python 3 environment; no external packages are required.

```bash
python3 -m unittest discover -s tests
python3 -m src.cli --data 100 --liquid-base water
```

Nutrient data is the locked Fineli table in `data/nutrients.json`. For baseline evaluation, provide a callable with signature `str -> str` to `run_baseline_cases`, together with truthful provider/model labels. The operator must choose the same LLM/model used elsewhere in the submission; that choice is an explicit evaluation configuration decision.

## Improvement Changelog

The pre-implementation revisions in [DESIGN-LOG.md](DESIGN-LOG.md) document the specification review path. The TASK 2.1 corrective pass added finite numeric validation, a separate verifier accounting path, faithful baseline liquid-base parsing, explicit malformed-baseline reporting, and provider/model labels for baseline evaluation. No frozen evaluation result has driven these changes.

## Main Failure Mode

The deterministic coordinate search is bounded and reproducible but is not a formal global-optimum proof for the nonlinear mass-weighted antioxidant ratio. Baseline evaluation also cannot begin until an operator supplies and identifies the required LLM callable.

## Hot Take / Engineering Insight

For an agentic optimization workflow, a separate verifier is more valuable than a persuasive recipe narrative: generation can propose, but only explicit data-backed checks should decide whether a constrained recipe is valid.

## Safety / Responsible Use

This tool optimizes toward a user-defined nutrient profile. It does not diagnose, treat, or promise health or cognitive outcomes. Slider names are nutrient-emphasis labels only. Guarana caffeine is an approximately 47 mg/g project estimate, not a laboratory result. Real-world use needs an appropriate human review boundary for ingredients, allergies, interactions, individual needs, and local guidance; no qualified reviewer approval is claimed here.

## Agent Trajectories

The submission will document representative agent trajectories: instructions, tool actions, feedback, retries, specification checkpoints, and human approval points. This repository records available design history but does not invent missing model transcripts, reviewers, runtime, cost, or evaluation results.
