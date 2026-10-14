#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

: "${OPENSANDBOX_DOMAIN:?Set OPENSANDBOX_DOMAIN, for example localhost:8080}"

protocol=${OPENSANDBOX_PROTOCOL:-http}
api_key=${OPENSANDBOX_API_KEY:-}
job_name="day1-opensandbox-smoke-$(date -u +%Y%m%dT%H%M%SZ)-$$"
job_dir="jobs/$job_name"
export PYTHONPATH="$repo_root${PYTHONPATH:+:$PYTHONPATH}"

echo "Writing Harbor results to $job_dir"

uv run harbor run \
    --path tasks/day1-smoke \
    --agent oracle \
    --env longcode_bench.opensandbox_allowlist:AllowlistOpenSandboxEnvironment \
    --environment-kwarg "protocol=$protocol" \
    --environment-kwarg "api_key=$api_key" \
    --environment-kwarg "request_timeout_sec=600" \
    --environment-kwarg "sandbox_timeout_sec=7200" \
    --environment-kwarg "ready_timeout_sec=600" \
    --n-concurrent 1 \
    --job-name "$job_name" \
    --jobs-dir jobs \
    --yes

uv run python scripts/validate_smoke_result.py "$job_dir"


