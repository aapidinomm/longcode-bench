import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_smoke_result import validate_job


class ValidateSmokeResultTests(unittest.TestCase):
    def make_job(
        self,
        root: Path,
        *,
        errors: int = 0,
        exception=None,
        reward: float = 1.0,
        verifier_mode: str = "separate",
    ) -> Path:
        job_dir = root / "job"
        trial_dir = job_dir / "trial"
        trial_dir.mkdir(parents=True)
        (job_dir / "result.json").write_text(
            json.dumps(
                {
                    "n_total_trials": 1,
                    "stats": {
                        "n_completed_trials": 1,
                        "n_errored_trials": errors,
                    },
                }
            )
        )
        (trial_dir / "result.json").write_text(
            json.dumps(
                {
                    "exception_info": exception,
                    "verifier_environment_mode": verifier_mode,
                    "verifier_result": {"rewards": {"reward": reward}},
                }
            )
        )
        return job_dir

    def test_accepts_one_successful_separate_verifier_trial(self):
        with tempfile.TemporaryDirectory() as directory:
            job_dir = self.make_job(Path(directory))
            self.assertEqual(validate_job(job_dir), job_dir / "trial/result.json")

    def test_rejects_harbor_job_with_trial_error(self):
        with tempfile.TemporaryDirectory() as directory:
            job_dir = self.make_job(Path(directory), errors=1)
            with self.assertRaisesRegex(AssertionError, "zero errored trials"):
                validate_job(job_dir)

    def test_rejects_exception_even_if_job_summary_claims_success(self):
        with tempfile.TemporaryDirectory() as directory:
            job_dir = self.make_job(
                Path(directory),
                exception={"exception_type": "ExampleError"},
            )
            with self.assertRaisesRegex(AssertionError, "trial has exception"):
                validate_job(job_dir)

    def test_rejects_missing_reward(self):
        with tempfile.TemporaryDirectory() as directory:
            job_dir = self.make_job(Path(directory), reward=0.0)
            with self.assertRaisesRegex(AssertionError, "reward 1"):
                validate_job(job_dir)


if __name__ == "__main__":
    unittest.main()

