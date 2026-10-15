# Insta: non-interactive snapshot review plans

## Candidate metadata

- Task ID: `rust-insta-review-plans`
- Language: Rust
- Category: feature development
- Repository: `mitsuhiko/insta`
- Base commit: `4b270ba4349f1f7b9d674852fb415d20bd8f205d`
- Upstream test command: `cargo test -p cargo-insta --locked`
- Estimated human time: 4–7 hours

## Agent-facing problem

`cargo insta` can list pending snapshots as JSON and can accept or reject
selected paths, but automation must issue many commands and cannot safely prove
that the pending set has not changed. Add a non-interactive review-plan
workflow that applies mixed accept, reject, and defer decisions in one checked
operation.

## Required behavior

- Add a command that writes a deterministic JSON plan for the current pending
  snapshot set.
- Each entry has a stable workspace-relative key, snapshot kind, content
  fingerprint, and an initially deferred decision.
- Add a command that validates and applies an edited plan.
- Supported decisions are accept, reject, and defer for both file and inline
  snapshots, including binary snapshots.
- Validate the complete plan before changing any file. Unknown keys, duplicate
  entries, invalid decisions, stale fingerprints, or newly missing snapshots
  fail without partial application.
- A dry-run mode performs the same validation and reports intended changes
  without writing.
- Application order and machine-readable results are deterministic across
  platforms.
- Existing interactive review, `--snapshot` filters, and
  `pending-snapshots --as-json` remain compatible.

## Compatibility and non-goals

- The plan is not a general scripting language.
- The feature does not run tests or regenerate snapshots.
- Plan keys must not contain absolute host paths.
- Recovering from an operating-system failure halfway through final file
  replacement is out of scope; logical validation must still be all-or-nothing.

## Verifier design

Exercise mixed decisions across file, inline, and binary snapshots; stale and
malformed plans; dry-run; path separator normalization; deterministic ordering;
and unchanged state after any validation failure. Run existing functional tests
and compare legacy command behavior.

## Anti-shortcut cases

- Loop over existing CLI commands without pre-validating the whole plan.
- Identify snapshots by path alone and ignore content changes.
- Support file snapshots but silently skip inline or binary snapshots.
- Write absolute paths to the plan.
- Apply entries in input order with nondeterministic output.

## Packaging notes

Bake the Rust toolchain and locked Cargo dependencies into the image. Hidden
fixtures should create a temporary Cargo workspace. Disable all networking and
run the verifier separately from the agent.

## Effort and risk

This crosses CLI parsing, snapshot discovery, stable identity, inline patching,
binary file handling, validation, and transactional sequencing. The main
platform risk is path normalization; hidden tests should use the repository's
existing path-storage conventions.
