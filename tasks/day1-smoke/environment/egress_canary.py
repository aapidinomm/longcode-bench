#!/usr/bin/env python3
"""Probe outbound TCP access without downloading external content."""

from __future__ import annotations

import argparse
import json
import socket
from typing import Any


def probe(host: str, port: int, timeout: float) -> dict[str, Any]:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allowed")
    parser.add_argument("--blocked", action="append", default=[])
    parser.add_argument("--port", type=int, default=443)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    result: dict[str, Any] = {"allowed": None, "blocked": []}
    ok = True

    if args.allowed:
        allowed = probe(args.allowed, args.port, args.timeout)
        result["allowed"] = allowed
        ok = ok and allowed["connected"]

    for host in args.blocked:
        blocked = probe(host, args.port, args.timeout)
        result["blocked"].append(blocked)
        ok = ok and not blocked["connected"]

    print(json.dumps(result, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

