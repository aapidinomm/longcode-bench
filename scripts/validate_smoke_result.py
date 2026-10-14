#!/usr/bin/env python3
"""Fail unless a Harbor smoke job contains one successful verified trial."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AssertionError(f"missing result file: {path}")
    return json.loads(path.read_text())


def validate_job(job_dir: Path) -> Path:
    job_result = read_json(job_dir / "result.json")
    if job_result.get("n_total_trials") != 1:
        raise AssertionError(
            f"expected one total trial, got {job_result.get('n_total_trials')!r}"
        )

    stats = job_result.get("stats") or {}
    if stats.get("n_errored_trials") != 0:
        raise AssertionError(
            f"expected zero errored trials, got {stats.get('n_errored_trials')!r}"
        )
    if stats.get("n_completed_trials") != 1:
        raise AssertionError(
            "expected one completed trial, "
            f"got {stats.get('n_completed_trials')!r}"
        )

    trial_result_paths = sorted(
        path / "result.json"
        for path in job_dir.iterdir()
        if path.is_dir() and (path / "result.json").is_file()
    )
    if len(trial_result_paths) != 1:
        raise AssertionError(
            f"expected exactly one trial result, found {len(trial_result_paths)}"
        )

    trial_path = trial_result_paths[0]
    trial = read_json(trial_path)
    if trial.get("exception_info") is not None:
        raise AssertionError(f"trial has exception: {trial['exception_info']}")
    if trial.get("verifier_environment_mode") != "separate":
        raise AssertionError(
            "verifier did not use a separate environment: "
            f"{trial.get('verifier_environment_mode')!r}"
        )

    verifier_result = trial.get("verifier_result") or {}
    rewards = verifier_result.get("rewards") or {}
    if rewards.get("reward") != 1:
        raise AssertionError(f"expected verifier reward 1, got {rewards!r}")

    return trial_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("job_dir", type=Path)
    args = parser.parse_args()

    trial_path = validate_job(args.job_dir)
    print(f"OpenSandbox smoke proof passed: {trial_path}")


if __name__ == "__main__":
    main()

