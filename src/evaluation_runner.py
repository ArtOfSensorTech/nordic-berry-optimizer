"""Crash-safe frozen-evaluation orchestration with per-case failure isolation."""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

from .baseline import baseline_prompt, parse_baseline_recipe, validate_llm_configuration
from .metrics import DIMENSIONS
from .openrouter_baseline import (
    GENERATION_SETTINGS,
    OPENROUTER_BASELINE_MODEL,
    OPENROUTER_BASELINE_PROVIDER,
)
from .optimizer import optimize
from .verify import verify_recipe

PROTOCOL_REVISION = "v1.0-rev8"
ARTIFACT_NAMES = ("baseline_results.json", "agent_results.json", "comparison.csv")


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _comparison_csv(baseline: list[dict[str, object]], agent: list[dict[str, object]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=("case", "dimension", "baseline_deviation", "agent_deviation", "baseline_nntd", "agent_nntd"),
    )
    writer.writeheader()
    for baseline_result, agent_result in zip(baseline, agent):
        baseline_metric = baseline_result.get("verification", {}).get("metric", {})
        agent_metric = agent_result.get("verification", {}).get("metric", {})
        for dimension in DIMENSIONS:
            writer.writerow({
                "case": baseline_result["case"]["id"],
                "dimension": dimension,
                "baseline_deviation": baseline_metric.get("per_dimension", {}).get(dimension),
                "agent_deviation": agent_metric.get("per_dimension", {}).get(dimension),
                "baseline_nntd": baseline_metric.get("nntd"),
                "agent_nntd": agent_metric.get("nntd"),
            })
    return output.getvalue()


def _write_artifacts(output_dir: Path, baseline: list[dict[str, object]], agent: list[dict[str, object]]) -> None:
    _atomic_write(output_dir / "baseline_results.json", json.dumps(baseline, indent=2))
    _atomic_write(output_dir / "agent_results.json", json.dumps(agent, indent=2))
    _atomic_write(output_dir / "comparison.csv", _comparison_csv(baseline, agent))


def _write_run_status(output_dir: Path, status: dict[str, object]) -> None:
    _atomic_write(output_dir / "run_status.json", json.dumps(status, indent=2))


def _agent_result(case: dict[str, object]) -> dict[str, object]:
    power_mode = bool(case.get("power_mode", False))
    stimulant_boost = bool(case.get("stimulant_boost", False))
    liquid_base = str(case.get("liquid_base", "water"))
    try:
        optimized = optimize(case["sliders"], power_mode=power_mode,
                             stimulant_boost=stimulant_boost, liquid_base=liquid_base)
        verification = verify_recipe(optimized["recipe"], case["sliders"],
                                     power_mode=power_mode, stimulant_boost=stimulant_boost,
                                     liquid_base=liquid_base)
        return {"case": case, "recipe": optimized["recipe"], "verification": verification}
    except ValueError as exc:
        return {"case": case, "recipe": None,
                "verification": {"status": "REJECT", "warnings": [], "errors": [str(exc)]}}


def run_frozen_evaluation(
    cases: Iterable[dict[str, object]],
    llm_call: Callable[[str], str],
    *,
    provider: str,
    model: str,
    output_dir: Path,
    agent_callable: Callable[[dict[str, object]], dict[str, object]] | None = None,
    before_case: Callable[[dict[str, object]], None] | None = None,
) -> dict[str, object]:
    """Run one baseline attempt per case and atomically checkpoint each case.

    ``before_case`` exists for offline crash-recovery tests and is not used by
    the production evaluation invocation.
    """
    frozen_cases = list(cases)
    expected_ids = list(range(1, len(frozen_cases) + 1))
    actual_ids = [case.get("id") for case in frozen_cases]
    if actual_ids != expected_ids:
        raise ValueError("frozen case identity is inconsistent")
    validate_llm_configuration(provider, model)
    agent_results: list[dict[str, object]] = []
    baseline_results: list[dict[str, object]] = []
    attempted_ids: list[int] = []
    start = _timestamp()
    current_case_id: int | None = None

    def status(state: str, last_case_id: int | None = None) -> dict[str, object]:
        return {
            "protocol_revision": PROTOCOL_REVISION,
            "intended_cases": len(frozen_cases),
            "attempted_cases": len(attempted_ids),
            "completed_case_ids": list(attempted_ids),
            "baseline_request_count": len(attempted_ids),
            "current_case_id": current_case_id,
            "last_case_id": last_case_id,
            "status": state,
            "provider": provider,
            "model": model,
            "generation_settings": dict(GENERATION_SETTINGS),
            "run_start_timestamp": start,
            "last_checkpoint_timestamp": _timestamp(),
        }

    _write_artifacts(output_dir, baseline_results, agent_results)
    _write_run_status(output_dir, status("running"))
    try:
        for ordinal, case in enumerate(frozen_cases, start=1):
            current_case_id = int(case["id"])
            if before_case is not None:
                before_case(case)
            agent_results.append((agent_callable or _agent_result)(case))
            power_mode = bool(case.get("power_mode", False))
            stimulant_boost = bool(case.get("stimulant_boost", False))
            prompt = baseline_prompt(case)
            record: dict[str, object] = {
                "case": case,
                "provider": provider,
                "model": model,
                "generation_settings": dict(GENERATION_SETTINGS),
                "prompt": prompt,
                "timestamp": _timestamp(),
                "request_ordinal": ordinal,
                "api_requests_made": 1,
                "baseline_text": None,
                "raw_response": None,
                "parse_status": None,
                "recipe": None,
                "liquid_base": None,
            }
            try:
                raw = llm_call(prompt)
            except Exception as exc:
                record["parse_status"] = "CALL_FAILED"
                record["verification"] = {
                    "status": "REJECT",
                    "warnings": [],
                    "errors": [f"baseline LLM call failed: {exc}"],
                }
            else:
                record["baseline_text"] = raw
                record["raw_response"] = raw
                parsed = parse_baseline_recipe(raw)
                record["parse_status"] = parsed.status
                record["recipe"] = parsed.recipe
                record["liquid_base"] = parsed.liquid_base
                if parsed.status != "PASS":
                    record["verification"] = {
                        "status": "REJECT", "warnings": [], "errors": [parsed.reason],
                    }
                else:
                    record["verification"] = verify_recipe(
                        parsed.recipe, case["sliders"], power_mode=power_mode,
                        stimulant_boost=stimulant_boost, liquid_base=parsed.liquid_base,
                    )
            baseline_results.append(record)
            attempted_ids.append(current_case_id)
            _write_artifacts(output_dir, baseline_results, agent_results)
            _write_run_status(output_dir, status("running", current_case_id))
        current_case_id = None
        _write_run_status(output_dir, status("complete", attempted_ids[-1] if attempted_ids else None))
    except BaseException:
        _write_run_status(output_dir, status("incomplete", attempted_ids[-1] if attempted_ids else None))
        raise
    return {"agent": agent_results, "baseline": baseline_results, "run_status": status("complete", attempted_ids[-1])}
