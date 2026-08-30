# Agent Trajectories

## Evidence status

This document indexes curated representative trajectory evidence. The linked
trace files preserve selected authentic project material, while complete CLI,
chat/conversation, and tool-channel histories remain private and are not
included. Exact quotations are used only where the corresponding trace or
committed project file contains them; connective summaries are labeled as
summaries rather than raw transcripts.

The trajectories distinguish agent activity from human checkpoints and from
later read-only interpretation of frozen results.

## Trajectory 1 — Initial design review

**Agent:** Claude
**Purpose:** Challenge the initial Nordic berry optimizer concept before implementation.
**Instruction / task:** Review the proposed sliders, Power Mode, Stimulant Boost, mineral water, verification, and baseline comparison.
**Agent actions:** The design review raised questions about Fit/Power Mode, stimulant functionality, deterministic verification, mineral-water representation, and baseline methodology.
**Tool / execution evidence:** A redacted representative excerpt from authentic conversation material is available in [Claude's trace](agent-traces/claude/01-specification-and-verification-review.md). The summarized design decisions are also recorded in `DESIGN-LOG.md` Iterations 1–3 and the early `SPEC.md` revisions.
**Feedback or finding:** The concept needed explicit constraints and an auditable comparison path.
**Human checkpoint / decision:** The human reviewed the suggestions before incorporating them into the specification.
**Resulting project change:** The initial product scope and constraint questions were formalized for later specification review.
**Evidence location:** [Claude's representative trace](agent-traces/claude/01-specification-and-verification-review.md), `DESIGN-LOG.md`, and `SPEC.md`. Complete conversation history is not included.

## Trajectory 2 — Mathematical specification review

**Agent:** ChatGPT
**Purpose:** Independently challenge the mathematical and architectural design before implementation.
**Instruction / task:** Review target normalization, stimulant/caffeine semantics, mineral-water treatment, and the antioxidant proxy.
**Agent actions:** The review identified excessive target scaling, an initially unmeasured Stimulant Boost, weak mineral-water representation, and an arbitrary antioxidant coefficient.
**Tool / execution evidence:** A representative project trace derived from the author's actual ChatGPT conversation is available in [ChatGPT's trace](agent-traces/chatgpt/01-mathematical-specification-review.md). The findings and resulting revisions are summarized in `DESIGN-LOG.md` Iterations 4–5 and commits `0d49eb4` and `2d3128c`.
**Feedback or finding:** Unsupported weighting and underspecified objectives were not suitable for a locked, reproducible evaluation.
**Human checkpoint / decision:** Implementation was held until the mathematical specification was reviewed and locked.
**Resulting project change:** The final pre-implementation design used normalized targets, explicit caffeine semantics, exclusive liquid bases, and equal weighting for the defined antioxidant components.
**Evidence location:** [ChatGPT's representative trace](agent-traces/chatgpt/01-mathematical-specification-review.md), `DESIGN-LOG.md`, `SPEC.md`, and commits `0d49eb4` and `2d3128c`. It is not a complete raw transcript.

## Trajectory 3 — Codex TASK 1 read-only review

**Agent:** OpenAI Codex
**Purpose:** Inspect the repository and locked specification before coding.
**Instruction / task:** Perform a read-only implementation review without changes, dependency installation, evaluation, or commit.
**Agent actions:** Codex proposed an optimizer approach and identified a stale Na reference in §7 and an underspecified recipe-level antioxidant aggregation rule, while noting the nonlinear objective's optimization difficulty.
**Tool / execution evidence:** The repository records the findings in `DESIGN-LOG.md` Iteration 5 and the subsequent `SPEC.md` revision. The Codex evidence index contains curated observable tool excerpts; complete terminal history is not included.
**Feedback or finding:** The specification needed correction before safe implementation.
**Human checkpoint / decision:** The findings were reviewed before implementation continued.
**Resulting project change:** The specification was revised and locked as v1.0-rev5 before implementation.
**Evidence location:** `DESIGN-LOG.md`, `SPEC.md`, commit `2d3128c`, and the [Codex verifier-audit trace](agent-traces/codex/01-verifier-audit.md).

## Trajectory 4 — Codex TASK 2 implementation

**Agent:** OpenAI Codex
**Purpose:** Implement the locked specification as a runnable project.
**Instruction / task:** Preserve frozen cases, use deterministic standard library code, write tests alongside implementation, and avoid unnecessary dependencies.
**Agent actions:** Codex implemented target construction, nutrient handling, deterministic optimization, verification, NNTD, baseline parsing, CLI, and the frozen evaluation harness.
**Tool / execution evidence:** The resulting `src/`, `tests/`, and commit `61a3b7a` are committed evidence. The [Codex verifier-audit trace](agent-traces/codex/01-verifier-audit.md) provides a curated observable session excerpt; the complete implementation session is not included. The implementation initially passed 20 tests before the audit.
**Feedback or finding:** A runnable deterministic path existed, but it still needed a pre-evaluation audit.
**Human checkpoint / decision:** The implementation was reviewed before the commit.
**Resulting project change:** `61a3b7a feat: implement Nordic Berry Optimizer`.
**Evidence location:** `src/`, `tests/`, commit `61a3b7a`, and the [Codex verifier-audit trace](agent-traces/codex/01-verifier-audit.md).

## Trajectory 5 — Pre-evaluation implementation audit

**Agent:** OpenAI Codex
**Purpose:** Audit TASK 2 against SPEC v1.0-rev5 without changing or running the evaluation.
**Instruction / task:** Perform a read-only compliance and implementation review.
**Agent actions:** The audit found weaknesses in finite numeric validation, verifier accounting independence, baseline liquid-base preservation, and concrete baseline configuration. It also recorded the lack of a formal global optimum guarantee for the deterministic coordinate search.
**Tool / execution evidence:** Findings are summarized in the committed design history and represented by the [Codex verifier-audit trace](agent-traces/codex/01-verifier-audit.md); complete raw tool history is not included.
**Feedback or finding:** Corrective work was needed before live evaluation.
**Human checkpoint / decision:** Changes were authorized only after review.
**Resulting project change:** A bounded corrective pass was prepared without changing the locked mathematical intent.
**Evidence location:** `DESIGN-LOG.md`, commit history, and the [Codex verifier-audit trace](agent-traces/codex/01-verifier-audit.md).

## Trajectory 6 — TASK 2.1 corrective pass

**Agent:** OpenAI Codex
**Purpose:** Correct the audited implementation issues before evaluation.
**Instruction / task:** Add finite-input validation, independent nutrient recalculation, faithful liquid-base handling, malformed-baseline reporting, and offline coverage without changing frozen semantics.
**Agent actions:** Codex made the corrective implementation and added tests; the corrected implementation passed 26 tests.
**Tool / execution evidence:** `src/`, `tests/`, `DESIGN-LOG.md`, and commit `ae0bbd4` are the available evidence. The [Codex verifier-audit trace](agent-traces/codex/01-verifier-audit.md) provides a curated observable excerpt. No network or frozen evaluation was run in this phase.
**Feedback or finding:** The baseline interface and verifier needed clearer failure categories and independent accounting.
**Human checkpoint / decision:** The corrective changes were reviewed before commit.
**Resulting project change:** `ae0bbd4 fix: harden verification and baseline evaluation`.

## Trajectory 7 — Baseline protocol and documentation checkpoints

**Agents:** OpenAI Codex, with Claude/ChatGPT design material
**Purpose:** Make the baseline identifiable, input-equivalent, and suitable for pre-evaluation use.
**Instruction / task:** Audit the baseline, document the Rule Book history, and correct only pre-evaluation protocol defects.
**Agent actions:** Codex added the OpenRouter adapter and tests; the audit found the missing baseline `liquid_base` input and produced rev6. Free-endpoint 429 responses, the paid 512-token empty-content smoke, and public reasoning metadata then led to rev7: paid `z-ai/glm-5.2`, `max_tokens=2048`, default reasoning. A final non-frozen smoke returned HTTP 200 with text but was `INVALID` under the committed parser, with no repair or retry.
**Tool / execution evidence:** Commits `4d06e7e`, `53a3cd4`, `aa02fe2`, and `300b60d`; `src/openrouter_baseline.py` and tests show the adapter shape. The [Codex verifier-audit trace](agent-traces/codex/01-verifier-audit.md) contains a curated baseline checkpoint excerpt; complete CLI/API traces and approval history are not included.
**Feedback or finding:** Input parity and paid-endpoint reliability had to be settled before frozen evaluation, without using frozen results to tune the protocol.
**Human checkpoint / decision:** The human approved rev6 and rev7 before evaluation.
**Resulting project change:** The locked baseline became a single user message to paid GLM 5.2 with fixed settings and no tools or context.

## Trajectory 8 — TASK 4.0A/4.1 recovery

**Agent:** OpenAI Codex
**Purpose:** Diagnose and harden an incomplete first frozen orchestration.
**Instruction / task:** Perform a read-only forensic audit, then preserve the failed run and add crash-safe per-case persistence and failure isolation.
**Agent actions:** The first run reached 9 provider-side requests; cases 1–8 returned text, case 9 had empty assistant content, and cases 10–14 were not attempted. Codex encountered ambiguous tool output, did not fabricate results or blindly retry, requested investigation, preserved the partial artifacts, and added rev8 checkpoint/failure-isolation behavior.
**Tool / execution evidence:** The incident archive `incidents/2026-08-29-partial-run-9-of-14/`, `SPEC.md` rev8, source/tests, and commit `94f97a4` provide the committed evidence. The [Codex frozen-run recovery trace](agent-traces/codex/02-frozen-run-recovery.md) provides a curated observable excerpt; the complete process/tool trace is not included.
**Feedback or finding:** A normal per-case `CALL_FAILED` must consume one attempt, persist safely, and allow the next case; only ambiguous runner or checkpoint failures stop the run.
**Human checkpoint / decision:** Run #1 was preserved as historical evidence; rev8 was reviewed and committed before run #2.
**Resulting project change:** Atomic per-case persistence and one-attempt failure isolation, with no retry, repair, fallback, or substitution.
**Evidence location:** [Codex frozen-run recovery trace](agent-traces/codex/02-frozen-run-recovery.md), `src/evaluation_runner.py`, `SPEC.md` rev8, and commit `94f97a4`.

## Trajectory 9 — Official frozen evaluation and audits

**Agent:** OpenAI Codex
**Purpose:** Execute the locked run #2 and audit its recorded outcomes without post-hoc tuning.
**Instruction / task:** Run all 14 cases under rev8, preserve artifacts, then perform read-only attribution audits.
**Agent actions:** Run #2 completed 14/14 with one baseline attempt each. Codex later audited agent boundary outcomes, Boost-off guarana, and raw baseline/parser attribution while leaving artifacts unchanged. It documented that case 11/12 matched pre-declared expectations, that four raw baseline recipes were mass-balanced but misrepresented by the parser, and that case 14 was an empty-response `CALL_FAILED`.
**Tool / execution evidence:** Committed artifacts under `evaluation/`, the incident archive, `DESIGN-LOG.md`, and commits `eac8463` and `9d5fda3` are available evidence. The [Codex frozen-run recovery trace](agent-traces/codex/02-frozen-run-recovery.md) provides a curated related session excerpt; no complete tool-channel history is included.
**Feedback or finding:** Interpretation must distinguish raw model output, parser/verifier outcomes, and the single paired NNTD comparison.
**Human checkpoint / decision:** The official artifacts were committed unchanged before documentation of the findings.
**Resulting project change:** A locked evidence set and qualified narrative, not a protocol change after observing results.

## Trajectory 10 — Reproduction guide and standalone demo

**Agent:** OpenAI Codex
**Purpose:** Make the local agent path and browser demonstration reproducible for reviewers.
**Instruction / task:** Audit clean-environment reproduction, clarify README requirements, and build an offline standalone demo without changing the frozen methodology.
**Agent actions:** The local agent path was verified in a fresh Python 3.11.2 environment with no packages, network, or API key; it produced verifier PASS and NNTD. Codex then added `demo.html` with inline logic/artwork, performed four non-frozen parity checks, added the Pages root redirect, and linked the public demo.
**Tool / execution evidence:** `README.md`, `demo.html`, `index.html`, tests, and commits `527d8e7`, `3a2cfe1`, `d1efa8b`, and `cbe85ab` are committed evidence. The [Codex reproducibility/final-audit trace](agent-traces/codex/03-reproducibility-final-audit.md) provides a curated observable excerpt; complete build/tool history is not included.
**Feedback or finding:** The agent-only path is local and cost-free; the paid baseline is a separate OpenRouter path.
**Human checkpoint / decision:** README/demo documentation and commits were reviewed before publication.
**Resulting project change:** An offline-capable interactive demo and a clean-environment reproduction guide.

## Human checkpoints

The committed history supports approval gates between major phases:

1. initial product direction and design review;
2. specification revisions and v1.0-rev5 lock;
3. Codex read-only review;
4. implementation and corrective-pass review;
5. baseline rev6/rev7 protocol corrections;
6. rev8 recovery protocol before run #2;
7. official results and documentation/demo review.

The curated trace files include selected human instructions and checkpoints,
but not the complete approval history. This remains summarized chronology
rather than a raw human-agent transcript.

## Evidence limitations

- The linked files are curated representative excerpts, not complete private
  session histories.
- Complete approval messages, intermediate tool events, hidden reasoning, and
  unrelated conversation material are intentionally omitted.
- Exact runtime, timestamps, provider routing details, and cost for historical
  agent interactions are available only where the committed evidence records
  them.

The excerpts are intended to satisfy the trajectory evidence requirement
without dumping complete private session histories. They should be submitted
alongside the repository as the selected representative evidence.
