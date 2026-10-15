# Click: opt-in response-file argument expansion

## Candidate metadata

- Task ID: `python-click-response-files`
- Language: Python
- Category: feature development
- Repository: `pallets/click`
- Base commit: `2247b35ea1c47c727d7a06e51fa280e12a863ff6`
- Upstream test command: `uv run --frozen pytest -q`
- Estimated human time: 3–5 hours

## Agent-facing problem

Large command invocations are difficult to manage in shell history and process
launchers. Add an opt-in Click setting that lets applications place arguments
in response files and reference them with `@path`. The facility must compose
with groups and ordinary Click parsing without changing existing applications.

## Required behavior

- Response-file processing is disabled by default and can be enabled through
  normal Click context settings.
- An argument of the form `@path` loads tokens from that UTF-8 file before
  Click parses commands and options.
- Files support shell-like whitespace, single and double quotes, backslash
  escapes, blank lines, and `#` comments.
- Includes may be nested. A relative nested path is resolved from the directory
  of the file containing it, not from the process working directory.
- `@@value` produces the literal argument `@value`.
- Expansion stops at the first literal `--`; later `@` arguments remain
  literal. A `--` read from a response file has the same effect.
- Missing files, malformed quoting, include cycles, and excessive nesting
  produce a Click usage error that identifies the responsible file. Cycle
  errors include the include chain.
- The setting is inherited by subcommands unless explicitly overridden.
- Public types, documentation, and changelog material are updated.

## Compatibility and non-goals

- Default command-line behavior and the existing Windows glob, environment, and
  user-directory expansion behavior must remain unchanged.
- Reading response content from standard input is out of scope.
- Environment-variable interpolation inside response files is out of scope.
- The implementation must not fetch files over URLs.

## Verifier design

Run the full upstream suite plus isolated CLI-runner cases covering flat and
nested files, quoting, comments, escaping, groups, inherited settings, `--`,
missing files, malformed files, cycles, and maximum depth. Run agent and
verifier environments with no network and compare disabled-mode behavior with
the unmodified base revision.

## Anti-shortcut cases

- Expand only a single file and ignore nested includes.
- Resolve every path from the current working directory.
- Split on whitespace instead of applying the documented quoting rules.
- Expand arguments after `--`.
- Enable the behavior globally or by default.
- Detect only direct self-inclusion rather than longer cycles.

## Packaging notes

Bake the pinned repository, uv, and locked test dependencies into the image.
Give the agent a clean worktree and persist only the repository as an artifact.
Run hidden tests in a separate no-network verifier environment.

## Effort and risk

The feature touches context configuration, top-level argument handling,
recursive parsing, diagnostics, documentation, and tests. Avoid specifying a
helper name or exact module layout. The primary ambiguity to eliminate during
authoring is the exact parsing grammar on Windows; the task should define one
portable response-file grammar independent of the invoking shell.
