# Representative Codex traces

Agent: OpenAI Codex CLI
Codex CLI version: 0.149.1
Source sessions: authentic local Codex JSONL sessions listed in each excerpt
Evidence type: redacted representative excerpts
Integrity note: Original sessions remain unchanged.
Path note: Home/project paths were normalized for privacy; substantive command
content was not changed.

These Markdown files are small, submission-oriented excerpts from authentic
local session JSONL. They contain user-visible instructions, Codex responses,
and observable tool calls/outputs selected to show development progression.
They do not contain system/developer messages or reasoning records. Omitted
intermediate events are marked in each file; the excerpts are not complete
transcripts.

## Included trajectories

- `01-verifier-audit.md` — TASK 2.1 audit and corrective implementation.
- `02-frozen-run-recovery.md` — failed frozen run #1 and rev8 recovery.
- `03-reproducibility-final-audit.md` — clean-environment reproduction and
  final demo/repository audit.

## Redaction and provenance

Only repository-relevant material was selected. Credentials, authorization
data, environment dumps, unrelated context, and internal reasoning were
excluded. Paths are represented as `<PROJECT_ROOT>`, `<HOME>`, or `<TEMP>`.
The source JSONL remains the provenance record and was not edited.
