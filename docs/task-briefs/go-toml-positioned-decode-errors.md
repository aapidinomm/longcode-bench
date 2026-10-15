# BurntSushi TOML: unify positioned decode errors

## Candidate metadata

- Task ID: `go-toml-positioned-decode-errors`
- Language: Go
- Category: refactoring
- Repository: `BurntSushi/toml`
- Base commit: `d733fc535e4a9f3c454e421a87b90ade5d49bf31`
- Upstream test command: `go test -race ./...`
- Estimated human time: 3–5 hours

## Agent-facing problem

Decode failures currently originate through several paths: plain formatted
errors, metadata helpers, and wrapped custom-unmarshal errors. Refactor these
paths so failures tied to a TOML key expose one consistent, position-aware
typed error while preserving established error strings.

## Required behavior

- Add an exported decode-error type that exposes the TOML key, source
  position, destination Go type when available, and underlying cause.
- `errors.As` finds this type for all failures associated with a parsed key,
  including type mismatches, unsupported destinations reached during recursive
  decoding, array-length mismatches, and custom unmarshaler failures.
- `errors.Is` and `errors.As` continue through the underlying custom error.
- Existing `Error()` strings remain byte-for-byte compatible.
- Errors that occur before parsing or before a key is known remain ordinary
  errors.
- Nested structs, maps, arrays of tables, primitives, text unmarshaling, and
  TOML unmarshaling report the correct full key and source position.
- Parser syntax errors remain `ParseError` and retain existing formatted
  context methods.

## Compatibility and non-goals

- Do not change accepted TOML syntax or decode coercion rules.
- Do not change the public fields or formatting of `ParseError`.
- Do not expose the original TOML input through the new error.
- Collecting multiple decode errors is out of scope.

## Verifier design

Run the full suite and a table of nested destination mismatches, array and map
cases, tagged fields, primitives, and custom errors. Assert legacy strings,
typed fields, positions, and unwrap chains independently. Include failures
before key discovery to ensure they are not mislabeled.

## Anti-shortcut cases

- Wrap only `badtype` calls.
- Reuse `ParseError` for every decode failure.
- Preserve the message but lose the custom error in the unwrap chain.
- Report only the last path component.
- Use line-only metadata while leaving column and byte span unset.

## Packaging notes

Pin the source revision and Go module cache. The repository has no required
external service. Run all hidden tests and the race-enabled upstream suite in a
separate no-network verifier.

## Effort and risk

The work requires tracing reflection-heavy recursion and maintaining a mature
error contract. Before task publication, the author should enumerate exactly
which pre-parse errors remain untyped so the requirement is not overbroad.
