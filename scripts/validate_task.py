#!/usr/bin/env python3
"""Static validation for the Day 1 Harbor task."""

from pathlib import Path

from harbor.models.task.task import Task
from harbor.models.task.verifier_mode import (
    VerifierEnvironmentMode,
    resolve_task_verifier_mode,
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    task = Task(root / "tasks/day1-smoke")

    assert task.config.environment.network_mode.value == "allowlist"
    assert task.config.environment.allowed_hosts == ["example.com"]
    assert (
        resolve_task_verifier_mode(task.config)
        == VerifierEnvironmentMode.SEPARATE
    )
    assert task.config.verifier.environment is not None
    assert task.config.verifier.environment.network_mode.value == "no-network"
    assert "@sha256:" in task.config.environment.docker_image

    print("Task configuration is valid.")


if __name__ == "__main__":
    main()

