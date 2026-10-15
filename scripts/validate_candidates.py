#!/usr/bin/env python3
"""Validate the Day 2 candidate catalog and task briefs."""

from __future__ import annotations

import re
import tomllib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "candidates" / "repositories.toml"
LANGUAGES = {"python", "go", "rust"}
CATEGORIES = {"feature", "refactoring"}
SCORE_KEYS = {
    "hermeticity",
    "verifier_determinism",
    "task_depth",
    "maintainability",
    "novelty",
    "build_speed",
}
REQUIRED_HEADINGS = {
    "## Candidate metadata",
    "## Agent-facing problem",
    "## Required behavior",
    "## Compatibility and non-goals",
    "## Verifier design",
    "## Anti-shortcut cases",
    "## Packaging notes",
    "## Effort and risk",
}


def main() -> None:
    with CATALOG.open("rb") as catalog_file:
        catalog = tomllib.load(catalog_file)

    repositories = catalog["repositories"]
    minimum_score = catalog["minimum_score"]
    pilot = catalog["pilot"]
    pilot_baseline = catalog["pilot_baseline"]

    assert len(repositories) == 6, "expected exactly six repository candidates"

    ids = [candidate["id"] for candidate in repositories]
    assert len(ids) == len(set(ids)), "candidate IDs must be unique"
    assert pilot in ids, "pilot must identify one candidate"
    pilot_candidate = next(candidate for candidate in repositories if candidate["id"] == pilot)
    assert pilot_baseline["commit"] == pilot_candidate["commit"]
    assert pilot_baseline["test_command"] == pilot_candidate["test_command"]
    assert pilot_baseline["duration_sec"] > 0
    assert pilot_baseline["result"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", pilot_baseline["verified_at"])

    language_counts = Counter(candidate["language"] for candidate in repositories)
    assert language_counts == Counter({language: 2 for language in LANGUAGES})

    category_pairs: dict[str, set[str]] = {
        language: set() for language in LANGUAGES
    }

    for candidate in repositories:
        language = candidate["language"]
        category = candidate["category"]
        assert language in LANGUAGES
        assert category in CATEGORIES
        category_pairs[language].add(category)

        assert candidate["upstream"].startswith("https://github.com/")
        assert re.fullmatch(r"[0-9a-f]{40}", candidate["commit"])
        assert candidate["license"]
        assert candidate["source_loc"] > 0
        assert candidate["test_loc"] > 0
        assert candidate["test_command"]

        scores = candidate["scores"]
        assert set(scores) == SCORE_KEYS
        assert all(isinstance(value, int) and value >= 0 for value in scores.values())
        assert sum(scores.values()) == candidate["score"]
        assert candidate["score"] >= minimum_score

        brief = ROOT / candidate["brief"]
        assert brief.is_file(), f"missing brief: {brief}"
        brief_text = brief.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            assert heading in brief_text, f"{brief}: missing {heading}"
        assert candidate["id"] in brief_text
        assert candidate["commit"] in brief_text

    for language, categories in category_pairs.items():
        assert categories == CATEGORIES, (
            f"{language} must have one feature and one refactoring task"
        )

    print(
        "Candidate catalog is valid: "
        "6 repositories, 3 languages, balanced task categories."
    )


if __name__ == "__main__":
    main()
