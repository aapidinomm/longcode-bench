#!/usr/bin/env python3
"""Verify the task result, network policy, and verifier separation."""

from __future__ import annotations

import json
import socket
from pathlib import Path


def probe(host: str, port: int, timeout: float) -> dict[str, object]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"host": host, "port": port, "connected": True, "error": None}
    except OSError as exc:
        return {
            "host": host,
            "port": port,
            "connected": False,
            "error": type(exc).__name__,
        }


def main() -> dict[str, float]:
    answer = Path("/app/answer.txt").read_text()
    if answer != "longcode-day1-ok\n":
        raise AssertionError(f"unexpected answer: {answer!r}")

    if not Path("/tests/verifier-only.txt").is_file():
        raise AssertionError("hidden verifier marker is missing")

    agent_egress = json.loads(Path("/app/agent-egress.json").read_text())
    if not agent_egress["allowed"]["connected"]:
        raise AssertionError(f"allowed destination failed: {agent_egress}")
    if any(entry["connected"] for entry in agent_egress["blocked"]):
        raise AssertionError(f"blocked destination was reachable: {agent_egress}")

    # The verifier has its own environment with network_mode=no-network.
    verifier_probe = probe("example.com", 443, 3.0)
    if verifier_probe["connected"]:
        raise AssertionError(
            f"verifier unexpectedly reached the internet: {verifier_probe}"
        )

    details = {
        "agent_egress": agent_egress,
        "verifier_egress": verifier_probe,
        "verifier_marker_visible": True,
    }
    Path("/logs/verifier/separation.json").write_text(
        json.dumps(details, indent=2, sort_keys=True) + "\n"
    )
    return {
        "reward": 1.0,
        "agent_egress": 1.0,
        "verifier_isolation": 1.0,
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True))

