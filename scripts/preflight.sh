#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

uv sync --frozen
uv run harbor --version
uv run python -c \
    'from importlib.metadata import version; print("opensandbox", version("opensandbox"))'
uv run python -m unittest discover -s unit_tests -v
uv run python scripts/validate_task.py

if [ -z "${OPENSANDBOX_DOMAIN:-}" ]; then
    echo "OPENSANDBOX_DOMAIN is not set; live OpenSandbox run is unavailable." >&2
    exit 2
fi

