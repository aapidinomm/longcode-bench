#!/bin/sh
set -eu

domain=${OPENSANDBOX_DOMAIN:-127.0.0.1:8080}
protocol=${OPENSANDBOX_PROTOCOL:-http}
health_url="$protocol://$domain/health"
attempts=${OPENSANDBOX_READY_ATTEMPTS:-60}

attempt=1
while [ "$attempt" -le "$attempts" ]; do
    if curl -fsS --max-time 2 "$health_url" >/dev/null; then
        echo "OpenSandbox is ready at $health_url"
        exit 0
    fi
    sleep 1
    attempt=$((attempt + 1))
done

echo "OpenSandbox did not become ready at $health_url" >&2
exit 1

