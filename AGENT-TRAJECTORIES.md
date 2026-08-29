# Agent Trajectories

## Purpose

This document records representative agent-assisted development
trajectories used during the development of **Nordic Berry Optimizer**.

It is intentionally maintained as a living record and will be updated as
implementation, evaluation, and submission preparation continue.

The purpose is to make agent contributions, feedback loops, retries,
decisions, and human checkpoints transparent and reproducible.

---

## Trajectory 1 — Initial design review

### Agent
Claude

### Objective
Review and challenge the initial product concept before implementation.

### Context provided
The project concept was developed around Nordic forest berries,
user-defined preference sliders, recipe optimization, Power Mode,
Stimulant Boost, safety verification, and a baseline-vs-agent evaluation.

### Agent contribution
The design was iteratively reviewed and refined. Topics included:

- Power Mode for Fit;
- stimulant functionality;
- deterministic safety verification;
- mineral-water as a liquid-base option;
- baseline comparison;
- evaluation methodology.

### Human checkpoint
Design suggestions were reviewed by the human developer before being
incorporated into the specification.

### Evidence / source material
Conversation transcript to be linked or summarized in the final
submission package.

---

## Trajectory 2 — Mathematical specification review

### Agent
ChatGPT

### Objective
Independently review the mathematical and architectural design before
implementation.

### Key findings
The review identified several specification-level problems during the
pre-implementation iterations, including:

1. slider target scaling could exceed the intended normalization range;
2. Stimulant Boost initially had no optimization objective;
3. mineral water was not meaningfully represented in the optimization;
4. the initial antioxidant proxy contained an arbitrary coefficient.

### Feedback loop
The findings were discussed with the independent design reviewer and
incorporated into subsequent specification revisions.

### Result
The specification was progressively revised before implementation and
eventually locked as **v1.0-rev5**.

### Human checkpoint
No implementation was authorized until the mathematical specification
had been reviewed and locked.

---

## Trajectory 3 — Codex TASK 1 read-only review

### Agent
OpenAI Codex

### Objective
Inspect the repository and read the locked specification before coding.

### Constraints
- no source-code changes;
- no dependency installation;
- no evaluation;
- no commits.

### Agent contribution
Codex reviewed the specification and proposed an optimizer approach.
It identified two concrete specification issues:

1. a stale Na reference in §7;
2. an underspecified recipe-level antioxidant aggregation rule.

Codex also identified implementation considerations around the nonlinear
antioxidant objective.

### Human checkpoint
The findings were reviewed before further implementation.

### Result
The specification was revised before implementation continued.

---

## Trajectory 4 — Codex TASK 2 implementation

### Agent
OpenAI Codex

### Objective
Implement the locked specification as a runnable project.

### Constraints
- SPEC.md locked;
- frozen evaluation cases unchanged;
- tests written alongside implementation;
- deterministic implementation preferred;
- no unnecessary external dependencies.

### Agent contribution
Codex implemented:

- target generation;
- nutrient calculations;
- deterministic recipe optimization;
- verification;
- NNTD metrics;
- baseline parser/interface;
- CLI;
- unit tests;
- frozen evaluation harness.

### Verification
The initial implementation passed **20 tests** before the
pre-evaluation implementation audit.

### Human checkpoint
The implementation was reviewed before being committed.

### Git checkpoint
`61a3b7a feat: implement Nordic Berry Optimizer`

---

## Trajectory 5 — Pre-evaluation implementation audit

### Agent
OpenAI Codex

### Objective
Perform a read-only audit of TASK 2 against SPEC v1.0-rev5.

### Constraints
- no modifications;
- no dependency installation;
- no frozen evaluation;
- no evaluation artifacts;
- no commit.

### Agent findings
The audit identified:

- non-finite input validation weakness;
- insufficient verifier accounting independence;
- baseline liquid-base preservation weakness;
- missing concrete baseline LLM configuration.

The audit also noted the known limitation that the deterministic
coordinate-pattern optimizer does not provide a formal proof of global
optimality for the nonlinear antioxidant objective.

### Human checkpoint
The audit findings were reviewed before corrective changes were
authorized.

---

## Trajectory 6 — TASK 2.1 corrective pass

### Agent
OpenAI Codex

### Objective
Correct the implementation issues identified by the audit without
changing the locked mathematical specification.

### Corrections
The implementation was updated to:

- reject non-finite numeric inputs;
- independently recompute nutrient values in the verifier;
- preserve and validate baseline liquid-base selection;
- explicitly classify malformed or ambiguous baseline output;
- retain a provider-agnostic baseline LLM interface;
- add tests covering the corrected behavior;
- improve Rule Book-oriented documentation.

### Verification
The corrected implementation passed **26 tests**.

The frozen evaluation was not run during this phase.

### Human checkpoint
The corrective changes were reviewed and committed.

### Git checkpoint
`ae0bbd4 fix: harden verification and baseline evaluation`

---

## Trajectory 7 — Pre-evaluation documentation and Rule Book alignment

### Agents
Claude, ChatGPT, and OpenAI Codex

### Objective
Improve the project's documentation and development trace before
running the frozen evaluation.

### Focus
The documentation process was aligned with the hackathon requirements,
including:

- Improvement Changelog;
- reproducibility;
- baseline methodology;
- safety/responsible use;
- failure modes;
- engineering insights;
- agent trajectories;
- human checkpoints.

### Important principle
The project distinguishes between:

- design history;
- implementation history;
- agent trajectories;
- evaluation evidence.

Evaluation results must not be fabricated or added before the actual
frozen evaluation is run.

### Current status
This section will be expanded with the final documentation work and
evaluation evidence.

---

## Human-in-the-loop checkpoints

The development process deliberately used human approval gates between
major agent phases.

Current checkpoints include:

1. approval of the initial product direction;
2. approval of specification revisions;
3. approval after Codex's read-only TASK 1 review;
4. approval of TASK 2 implementation;
5. review of the implementation audit;
6. approval of TASK 2.1 corrections;
7. approval before frozen evaluation.

Agents were not authorized to silently modify the locked specification
or the frozen evaluation methodology.

---

## Agent usage principles

Agents were used primarily for:

- independent design review;
- mathematical review;
- specification challenge;
- implementation;
- testing;
- verification;
- documentation.

Human decisions remained responsible for:

- project scope;
- mathematical specification changes;
- evaluation methodology;
- approval of implementation stages;
- approval of the frozen evaluation;
- final submission decisions.

---

## Evidence and trajectory completeness

The final submission should preserve representative evidence for each
agent used.

For each trajectory, the final version should include or link to
available evidence of:

- the instruction/prompt given to the agent;
- relevant agent output;
- tool actions where applicable;
- feedback and corrections;
- retries or failed approaches where applicable;
- human approval/checkpoint;
- resulting project change.

Missing information must be marked as unavailable rather than
reconstructed as fact.

---

## Evaluation phase — placeholder

### TASK 3
Frozen evaluation has not yet been run.

This section will be populated only after the frozen evaluation is
authorized and executed.

Planned evidence:

- baseline model/provider configuration;
- frozen evaluation command;
- baseline results;
- agent results;
- comparison metrics;
- safety/verification metrics;
- runtime;
- cost;
- reproducibility information.

No evaluation result should be entered here before it has actually
been observed.

### TASK 3 preparation — baseline adapter checkpoint

Human direction selected OpenRouter as the API gateway and GLM 5.2 Free as the
official named baseline model. The implementation agent verified the exact
fixed ID (`z-ai/glm-5.2:free`) from OpenRouter material, then added a
standard-library OpenAI-compatible adapter. It reads `OPENROUTER_API_KEY` only
from the environment, sends the frozen prompt as the sole user message, and
does not request tools, web search, file access, or project context. A fixed
ID was chosen over `openrouter/free` to keep the evaluated model identifiable
instead of allowing a changing free-model router. Mocked HTTP tests exercised
the adapter without credentials. Frozen evaluation remains unrun at this
checkpoint.

### Trajectory 7 — TASK 3.0 pre-evaluation input-parity correction

The pre-evaluation smoke/preflight audit compared the agent and baseline case
inputs. It found that the agent received and used `liquid_base`, but the
single-LLM baseline prompt did not communicate it. The baseline prompt was
updated and SPEC v1.0-rev6 records the correction before any frozen
evaluation was run and before any frozen evaluation result was observed.

The v1 contract remains exclusive: the selected liquid base is either
`water` or `mineral_water`. Mixing those liquids, or introducing more general
compositions such as milk, coffee, or mixtures, is future work and is not
part of v1 or the frozen evaluation. The 14 frozen cases were left unchanged.

---

## Final submission update — placeholder

To be completed after TASK 3 and final submission preparation.

Expected additions:

- representative final trajectories;
- final Improvement Changelog;
- measured baseline-vs-agent results;
- main failure mode;
- engineering hot take;
- reproducibility instructions;
- final evidence references.
