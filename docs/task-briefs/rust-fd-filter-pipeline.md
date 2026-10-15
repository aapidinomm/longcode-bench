# fd: extract a pure entry-filter pipeline

## Candidate metadata

- Task ID: `rust-fd-filter-pipeline`
- Language: Rust
- Category: refactoring
- Repository: `sharkdp/fd`
- Base commit: `14dcd92fb76ca0ebc2e82671a275f67c790d25fc`
- Upstream test command: `cargo test --locked`
- Estimated human time: 3–5 hours

## Agent-facing problem

The parallel walk closure currently mixes traversal control, matching,
metadata acquisition, entry filtering, styling, and channel delivery. Refactor
post-walk acceptance into a testable pipeline while preserving fd's command
line behavior and traversal performance.

## Required behavior

- Introduce a dedicated entry-filter abstraction that owns post-walk matching
  for minimum depth, search patterns, extensions, file types, owner, size, and
  modification time.
- Return a typed decision that distinguishes accepted entries from the reason
  an entry was rejected.
- Evaluate cheap checks before metadata-dependent checks and acquire metadata
  at most once per entry.
- Unit tests can exercise filter decisions directly without running the
  parallel walker or writing output.
- The walker remains responsible for ignore-file traversal, root skipping,
  ignore-containing-directory pruning, error delivery, styling, channel
  delivery, and `--prune`.
- CLI output, ordering, exit codes, broken-symlink behavior, filesystem-error
  handling, and all filter combinations remain compatible.
- The hot path does not introduce per-entry dynamic dispatch or unnecessary
  path allocation.

## Compatibility and non-goals

- Do not add a new CLI option or expose rejection reasons to users.
- Do not replace the `ignore` crate or redesign configuration parsing.
- Do not move output formatting or command execution into the filter.
- Performance improvements are welcome but no specific speedup is required.

## Verifier design

Run the upstream suite plus direct decision tests for every filter and
combinations that share metadata. Use an instrumented entry test double to
prove a single metadata lookup. Add black-box CLI golden cases for symlinks,
missing metadata, `--prune`, quiet mode, errors, and deterministic sorted
output. A structural check should keep the worker closure focused on traversal
and delivery.

## Anti-shortcut cases

- Wrap the existing closure in one large function without a decision type.
- Fetch metadata independently for owner, size, and time.
- Move ignore traversal into the post-walk filter.
- Change missing-metadata behavior from rejection to acceptance.
- Preserve ordinary output but break quiet-mode exit status or pruning.

## Packaging notes

Pin Rust 1.90, the base revision, and the locked Cargo dependency cache. Use
temporary filesystem fixtures only. Agent and verifier environments require no
network.

## Effort and risk

This is a behavior-preserving architecture task in concurrency-sensitive code.
The largest benchmark risk is relying only on structural assertions; combine
them with broad black-box equivalence tests and mutation patches.
