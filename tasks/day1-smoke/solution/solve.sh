#!/bin/sh
set -eu

# Harbor must not upload hidden tests until the verifier phase.
if [ -e /tests/verifier-only.txt ]; then
    echo "Verifier files were visible during the agent phase" >&2
    exit 20
fi

python /app/egress_canary.py \
    --allowed example.com \
    --blocked github.com \
    --blocked 1.1.1.1 \
    > /app/agent-egress.json

printf 'longcode-day1-ok\n' > /app/answer.txt

