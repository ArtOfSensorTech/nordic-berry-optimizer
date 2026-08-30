# Frozen run #1 failure and rev8 recovery

Agent: OpenAI Codex CLI
Codex CLI version: 0.149.1
Source session ID: 01a04cc5-319d-7942-9d53-bcab68558266
Source format: authentic local Codex JSONL session
Evidence type: redacted representative excerpt
Integrity note: Original session remains unchanged.
Path note: Home/project paths were normalized for privacy; substantive command
content was not changed.

## Human instruction

The following is a verbatim excerpt from the TASK 4.1 instruction.

> TASK 4.1 — Preserve failed frozen run #1, lock SPEC rev8 recovery protocol,
> and add per-case crash-safe persistence.
>
> Context:
> - SPEC v1.0-rev7 is currently locked.
> - Frozen run #1 was incomplete.
> - intended cases: 14
> - OpenRouter requests made: 9
> - cases 1–8 returned baseline text
> - case 9 returned empty assistant content and was recorded CALL_FAILED
> - cases 10–14 were never requested
>
> OLD:
> one baseline failure stops the entire 14-case run.
>
> NEW:
> each frozen case receives exactly ONE baseline attempt;
> if that attempt fails, record CALL_FAILED for that case and continue to the
> next frozen case.
>
> There is still:
> - no retry
> - no repair
> - no fallback
> - no model substitution
> - no second attempt for a failed case.

## Agent action

Codex first inspected the existing failed-run files and the evaluation
orchestration without running the evaluation again.

## Tool call

```text
git status --short --branch
find evaluation -maxdepth 1 -type f -printf '%f %s bytes\n' 2>/dev/null | sort
rg --files src tests | sort
```

## Tool output

```text
## main
?? evaluation/
agent_results.json 14235 bytes
baseline_results.json 27304 bytes
comparison.csv 3331 bytes
```

## Agent action

The recorded workflow then preserved the partial artifacts, added factual
run-status provenance, implemented atomic per-case checkpoints, and changed
ordinary baseline failure handling to per-case isolation. Intermediate tool
events are omitted; no retry or inference was initiated in this recovery
task.

## Feedback / human checkpoint

The session includes the explicit requirement that rev8 be locked before any
rerun, and later approval of the recovery commit. The resulting checkpoint
was committed as:

```text
94f97a4 fix: harden frozen evaluation recovery protocol
```

## Resulting project change

Each frozen case retained its one allowed baseline attempt. A normal
`CALL_FAILED` became a persisted case outcome that permits continuation;
checkpoint or provenance failures remained whole-run stop conditions.

## Evidence location

`incidents/2026-08-29-partial-run-9-of-14/`, `src/evaluation_runner.py`,
`tests/test_evaluation_runner.py`, `SPEC.md` rev8, and commit `94f97a4`.
This is a redacted representative excerpt, not a complete transcript.
