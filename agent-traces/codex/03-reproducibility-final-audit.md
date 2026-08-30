# Reproducibility and final repository audit

Agent: OpenAI Codex CLI
Codex CLI version: 0.149.1
Source session ID: 01a04cc5-319d-7942-9d53-bcab68558266
Source format: authentic local Codex JSONL session
Evidence type: redacted representative excerpt
Integrity note: Original session remains unchanged.
Path note: Home/project paths were normalized for privacy; substantive command
content was not changed.

## Human instruction

The following is a verbatim excerpt from TASK 4.7.

> TASK 4.7 — Verify the Reproduction Guide from a clean-environment
> perspective.
>
> Goal:
> Verify that an external reviewer can reproduce the AGENT path from the
> README without relying on hidden local state.
>
> Do NOT:
> - touch evaluation/
> - touch incidents/
> - modify SPEC.md
> - make any OpenRouter/API/network request
> - rerun the frozen evaluation
> - run the paid baseline

## Agent action

Codex created an isolated local environment and attempted the documented
non-frozen CLI path. The first timing wrapper was unavailable. The session
records this user-visible failure and the decision to retry only the local
smoke command without that wrapper:

> The isolated environment was created successfully with Python 3.11.2, but
> the first smoke command did not reach the project because this machine lacks
> `/usr/bin/time`; it produced no result and made no network call. I’ll rerun
> the same non-frozen CLI example without that unavailable timing utility,
> using the shell’s built-in timing instead.

## Tool call

```text
<TEMP>/venv/bin/python -m src.cli --data 37 --genius 61 --fit 22 --cute 14 --liquid-base water
```

Path normalization changes only the temporary absolute path to `<TEMP>`.

## Tool output

```text
VERIFIER_STATUS PASS
NNTD_PRESENT True
NNTD 0.057192565048950525
```

## Feedback / finding

Codex reported:

> The agent-only reproduction passed in a fresh Python 3.11.2 virtual
> environment: verifier PASS, NNTD produced, approximately 1.013 seconds.
> I found documentation gaps around the minimum Python version, explicit
> agent-only/no-cost wording, and the absence of a committed baseline cost
> estimate; I will propose the smallest wording additions without editing
> README.

## Human checkpoint / resulting change

The follow-up documentation task was approved and committed as
`d1efa8b docs: clarify reproduction requirements`. Subsequent demo and Pages
work was committed as `527d8e7` and `3a2cfe1`; the live-demo link followed in
`cbe85ab`.

## Evidence location

`README.md`, `demo.html`, `index.html`, tests, and the source session above.
The excerpt shows the reproducibility failure/recovery and successful local
result; it does not contain a baseline call or frozen-evaluation rerun.
