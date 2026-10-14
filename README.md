# LongCode benchmark

This repository contains the Day 1 infrastructure proof for a public and
private long-horizon coding benchmark built with Harbor and OpenSandbox.

The proof has one deliberately trivial task. The agent environment uses a
default-deny hostname allowlist: `example.com` must be reachable and
`github.com` and direct-IP access to `1.1.1.1` must be blocked. Harbor then
stops that environment, copies only declared artifacts into a fresh verifier
environment, uploads hidden tests, and runs the verifier with no network
access.

## Pinned components

- Python 3.12.14
- uv 0.12.9
- Harbor 0.23.0
- OpenSandbox Python SDK 0.1.14
- OpenSandbox server 0.2.1
- OpenSandbox execd 1.0.20
- OpenSandbox egress 1.1.3
- Colima 0.10.3
- Docker CLI 29.6.2
- Python task image 3.12.7 slim-bookworm, pinned by manifest digest

`uv.lock` pins the full Python dependency graph. `versions.env` records the
container-side components.

## Bootstrap and static checks

```sh
uv sync --frozen
make test
```

## Live OpenSandbox proof

Start a Docker-compatible runtime. The tested local setup is:

```sh
brew install colima docker
colima start --cpu 4 --memory 8 --disk 40 --runtime docker
```

In one terminal, start the loopback-only OpenSandbox server:

```sh
make server
```

The launcher pins `opensandbox-server==0.2.1` and discovers the default Colima
Docker socket when `DOCKER_HOST` is unset. In another terminal, wait for the
health endpoint and run:

```sh
export OPENSANDBOX_DOMAIN=localhost:8080
export OPENSANDBOX_PROTOCOL=http
export OPENSANDBOX_API_KEY=
make ready
make smoke
```

The job succeeds only when all of these are true:

1. The oracle creates the expected answer.
2. `example.com:443` is reachable during the agent phase.
3. `github.com:443` is blocked during the agent phase.
4. Direct-IP access to `1.1.1.1:443` is blocked during the agent phase.
5. Hidden tests are absent during the agent phase.
6. The verifier runs in a separate environment.
7. All outbound access is blocked during verification.

The detailed verifier evidence is collected in
`jobs/.../verifier/separation.json`.
The wrapper independently parses Harbor's job and trial JSON and exits nonzero
if the trial raised an exception, used a shared verifier, or scored below 1.

## Why a custom adapter is present

Harbor 0.23.0's built-in `OpenSandboxEnvironment` passes an OpenSandbox
`NetworkPolicy` only for `network_mode = "no-network"`. Its capability flags
cause Harbor to reject `network_mode = "allowlist"` before sandbox creation.

`AllowlistOpenSandboxEnvironment` adds creation-time FQDN and wildcard-FQDN
rules. It keeps dynamic policy switching disabled, so the task uses a separate
verifier environment with its own deny-all policy.

