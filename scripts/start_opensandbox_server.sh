#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"
mkdir -p .state

if [ -z "${DOCKER_HOST:-}" ]; then
    colima_status_json=
    if command -v colima >/dev/null 2>&1; then
        colima_status_json=$(colima status --json 2>/dev/null || true)
    fi

    if [ -n "$colima_status_json" ]; then
        detected_docker_host=$(
            printf '%s' "$colima_status_json" |
                python3 -c '
import json
import sys

def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)

data = json.load(sys.stdin)
for candidate in strings(data):
    if candidate.startswith("unix://") and candidate.endswith("docker.sock"):
        print(candidate)
        break
    if candidate.endswith("docker.sock"):
        print("unix://" + candidate)
        break
'
        )
    else
        detected_docker_host=
    fi

    if [ -z "$detected_docker_host" ]; then
        xdg_config_dir=${XDG_CONFIG_HOME:-"${HOME}/.config"}
        for socket_path in \
            "$xdg_config_dir/colima/default/docker.sock" \
            "${HOME}/.colima/default/docker.sock"
        do
            if [ -S "$socket_path" ]; then
                detected_docker_host="unix://$socket_path"
                break
            fi
        done
    fi

    if [ -n "$detected_docker_host" ]; then
        export DOCKER_HOST=$detected_docker_host
    fi
fi

# This configuration binds only to loopback. Explicitly acknowledge the
# no-auth local development server required by OpenSandbox.
export OPENSANDBOX_INSECURE_SERVER=YES
exec uv tool run \
    --from opensandbox-server==0.2.1 \
    opensandbox-server \
    --config infrastructure/opensandbox/config.toml


