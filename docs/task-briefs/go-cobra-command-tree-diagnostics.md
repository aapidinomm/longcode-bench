# Cobra: deterministic command-tree diagnostics

## Candidate metadata

- Task ID: `go-cobra-command-tree-diagnostics`
- Language: Go
- Category: feature development
- Repository: `spf13/cobra`
- Base commit: `adbc8813901bba65827259daa8e22ff94ec1f30e`
- Upstream test command: `go test ./...`
- Estimated human time: 3–5 hours

## Agent-facing problem

Large Cobra applications can assemble invalid or ambiguous command trees across
many packages, with problems surfacing only when a user invokes a particular
path. Add a read-only validation API that returns all command-tree diagnostics
in a deterministic form before execution.

## Required behavior

- Provide an exported diagnostic type with a stable code, command path, and
  human-readable message.
- Provide an exported method that walks the receiver and all descendants and
  returns every detected problem rather than stopping at the first.
- Detect sibling collisions across names and aliases, duplicate aliases on a
  command, duplicate or empty command-group IDs, commands assigned to unknown
  groups, and ambiguous sibling prefixes when prefix matching is enabled.
- Report cycles or a child registered under inconsistent parents without
  recursing forever.
- Return diagnostics in command-path then diagnostic-code order regardless of
  command insertion order or global command sorting.
- Validation must not sort or mutate commands, flags, called-as state, parent
  pointers, or execution state.
- A valid tree returns an empty, non-nil result.

## Compatibility and non-goals

- Existing `AddCommand`, lookup, help, completion, and execution behavior must
  remain compatible.
- Validation does not automatically run during `Execute`.
- Do not change the package globals controlling sorting or prefix matching.
- Runtime validation of user-provided argument values is out of scope.

## Verifier design

Use synthetic deep trees with multiple simultaneous defects, aliases that
collide with names, ambiguous prefixes, invalid groups, deliberate internal
cycles created by package-level tests, and different insertion orders. Compare
the tree before and after validation and run the full suite with the race
detector where feasible.

## Anti-shortcut cases

- Return one opaque `error`.
- Validate only direct children.
- Depend on `Commands()`, thereby sorting and mutating the tree.
- Detect name collisions but ignore aliases.
- Recurse without a visited set.
- Produce ordering that changes with insertion order.

## Packaging notes

Bake the Go module cache for the pinned revision into the image. Both agent and
verifier can run without network. Package-level hidden tests may inspect
unexported state to construct malformed trees and prove non-mutation.

## Effort and risk

The task spans API design, graph traversal, command matching semantics, groups,
deterministic ordering, and compatibility. The main authoring risk is requiring
diagnostics for impossible states without giving tests package-level access.
