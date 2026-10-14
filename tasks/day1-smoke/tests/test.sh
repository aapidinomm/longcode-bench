#!/bin/sh
set -u

reward_file=/logs/verifier/reward.json

if python /tests/verify.py > /logs/verifier/verify-output.json; then
    cp /logs/verifier/verify-output.json "$reward_file"
else
    status=$?
    printf '%s\n' \
        '{"reward":0.0,"agent_egress":0.0,"verifier_isolation":0.0}' \
        > "$reward_file"
    exit "$status"
fi

