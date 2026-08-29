import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.evaluation_runner import run_frozen_evaluation
from src.verify import verify_recipe
from tests.frozen_eval import FROZEN_CASES


RECIPE_TEXT = "blueberry: 50 g, water: 200 g"


def _fake_agent(case):
    recipe = {"blueberry": 50.0, "liquid_g": 200.0}
    verification = verify_recipe(recipe, case["sliders"],
                                 power_mode=bool(case.get("power_mode", False)),
                                 stimulant_boost=bool(case.get("stimulant_boost", False)),
                                 liquid_base=case["liquid_base"])
    return {"case": case, "recipe": recipe, "verification": verification}


class EvaluationRunnerTests(unittest.TestCase):
    def run_runner(self, *, cases=FROZEN_CASES, failures=(), before_case=None):
        calls = []
        failure_ids = set(failures)

        def llm_call(prompt):
            case_id = len(calls) + 1
            calls.append(prompt)
            if case_id in failure_ids:
                raise RuntimeError(f"simulated failure for case {case_id}")
            return RECIPE_TEXT

        directory = tempfile.TemporaryDirectory()
        result = run_frozen_evaluation(
            cases, llm_call, provider="test-provider", model="test-model",
            output_dir=Path(directory.name), agent_callable=_fake_agent,
            before_case=before_case,
        )
        return directory, result, calls

    def load_json(self, directory, name):
        return json.loads((Path(directory.name) / name).read_text(encoding="utf-8"))

    def test_case_one_survives_case_two_call_failed(self):
        directory, result, calls = self.run_runner(cases=FROZEN_CASES[:3], failures=(2,))
        self.addCleanup(directory.cleanup)
        self.assertEqual(len(calls), 3)
        self.assertEqual([item["case"]["id"] for item in result["baseline"]], [1, 2, 3])
        self.assertEqual(result["baseline"][1]["parse_status"], "CALL_FAILED")

    def test_multiple_earlier_cases_survive_later_runner_failure(self):
        def fail_on_case_four(case):
            if case["id"] == 4:
                raise RuntimeError("simulated runner failure")

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        with self.assertRaisesRegex(RuntimeError, "simulated runner failure"):
            run_frozen_evaluation(
                FROZEN_CASES[:5], lambda _prompt: RECIPE_TEXT,
                provider="test-provider", model="test-model", output_dir=Path(directory.name),
                agent_callable=_fake_agent, before_case=fail_on_case_four,
            )
        baseline = self.load_json(directory, "baseline_results.json")
        agent = self.load_json(directory, "agent_results.json")
        status = self.load_json(directory, "run_status.json")
        self.assertEqual([item["case"]["id"] for item in baseline], [1, 2, 3])
        self.assertEqual([item["case"]["id"] for item in agent], [1, 2, 3])
        self.assertEqual(status["status"], "incomplete")
        self.assertEqual(status["completed_case_ids"], [1, 2, 3])

    def test_call_failed_persisted_and_execution_continues_without_retry(self):
        directory, result, calls = self.run_runner(cases=FROZEN_CASES[:4], failures=(2, 4))
        self.addCleanup(directory.cleanup)
        baseline = self.load_json(directory, "baseline_results.json")
        self.assertEqual(len(calls), 4)
        self.assertEqual([item["parse_status"] for item in baseline],
                         ["PASS", "CALL_FAILED", "PASS", "CALL_FAILED"])
        self.assertEqual(result["run_status"]["status"], "complete")
        self.assertIsNone(baseline[1]["baseline_text"])
        self.assertNotIn("metric", baseline[1]["verification"])

    def test_all_fourteen_cases_finish_with_selected_call_failures(self):
        directory, result, calls = self.run_runner(failures=(3, 7, 14))
        self.addCleanup(directory.cleanup)
        self.assertEqual(len(calls), 14)
        self.assertEqual(len(result["baseline"]), 14)
        self.assertEqual(result["run_status"]["status"], "complete")
        self.assertEqual(result["run_status"]["completed_case_ids"], list(range(1, 15)))

    def test_parser_invalid_is_distinct_from_call_failed(self):
        calls = []

        def llm_call(_prompt):
            case_id = len(calls) + 1
            calls.append(case_id)
            return "blueberry: 50 g" if case_id == 1 else (_ for _ in ()).throw(RuntimeError("provider failure"))

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        result = run_frozen_evaluation(
            FROZEN_CASES[:2], llm_call, provider="test-provider", model="test-model",
            output_dir=Path(directory.name), agent_callable=_fake_agent,
        )
        self.assertEqual(result["baseline"][0]["parse_status"], "INVALID")
        self.assertEqual(result["baseline"][1]["parse_status"], "CALL_FAILED")
        self.assertNotEqual(result["baseline"][0]["parse_status"], result["baseline"][1]["parse_status"])

    def test_request_ordinals_are_one_to_one_with_case_attempts(self):
        directory, result, calls = self.run_runner(failures=(2, 5))
        self.addCleanup(directory.cleanup)
        self.assertEqual(len(calls), 14)
        self.assertEqual([item["request_ordinal"] for item in result["baseline"]], list(range(1, 15)))
        self.assertEqual([item["api_requests_made"] for item in result["baseline"]], [1] * 14)

    def test_checkpoint_files_are_atomic_and_readable(self):
        directory, _result, _calls = self.run_runner(failures=(6,))
        self.addCleanup(directory.cleanup)
        path = Path(directory.name)
        for name in ("baseline_results.json", "agent_results.json", "run_status.json"):
            with (path / name).open(encoding="utf-8") as handle:
                json.load(handle)
        with (path / "comparison.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 14 * 7)

    def test_successful_scoring_matches_committed_verifier(self):
        directory, result, _calls = self.run_runner(cases=FROZEN_CASES[:1])
        self.addCleanup(directory.cleanup)
        expected = verify_recipe(
            {"blueberry": 50.0, "liquid_g": 200.0}, FROZEN_CASES[0]["sliders"],
            liquid_base="water",
        )
        self.assertEqual(result["baseline"][0]["verification"], expected)

    def test_run_status_is_complete_after_all_cases_and_incomplete_on_partial_run(self):
        directory, result, _calls = self.run_runner(cases=FROZEN_CASES[:2])
        self.addCleanup(directory.cleanup)
        self.assertEqual(result["run_status"]["status"], "complete")

        partial = tempfile.TemporaryDirectory()
        self.addCleanup(partial.cleanup)

        def fail_before_case_two(case):
            if case["id"] == 2:
                raise RuntimeError("stop before case two")

        with self.assertRaisesRegex(RuntimeError, "stop before case two"):
            run_frozen_evaluation(
                FROZEN_CASES[:3], lambda _prompt: RECIPE_TEXT,
                provider="test-provider", model="test-model", output_dir=Path(partial.name),
                agent_callable=_fake_agent, before_case=fail_before_case_two,
            )
        status = json.loads((Path(partial.name) / "run_status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "incomplete")
        self.assertEqual(status["completed_case_ids"], [1])


if __name__ == "__main__":
    unittest.main()
