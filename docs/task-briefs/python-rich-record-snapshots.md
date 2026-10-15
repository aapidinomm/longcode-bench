# Rich: immutable console recording snapshots

## Candidate metadata

- Task ID: `python-rich-record-snapshots`
- Language: Python
- Category: refactoring
- Repository: `Textualize/rich`
- Base commit: `9d8f9a372cc5916fd4781fec207ced7ddac2f08f`
- Upstream test command: `TERM=unknown pytest tests/ -q`
- Estimated human time: 2–4 hours

## Agent-facing problem

Rich currently performs similar lock, copy, render, and clear work separately
for text, HTML, and SVG exports. Refactor recording around an immutable
snapshot value so all exporters consume a stable view of the recorded segments
and buffer clearing is atomic.

## Required behavior

- Introduce a dedicated immutable recording value containing a stable sequence
  of segments.
- Taking a snapshot and optionally clearing the live record buffer is one
  operation protected by the existing recording synchronization.
- Text, HTML, and SVG exporters render from a snapshot rather than directly
  iterating the mutable live buffer.
- A single snapshot may be rendered into multiple formats without mutation.
- Existing `export_*` and `save_*` signatures, output, assertions, and clear
  defaults remain compatible.
- Control segments, styles, links, themes, SVG identifiers, and no-color
  behavior remain unchanged.
- Concurrent printing cannot add only part of a render batch to a snapshot.

## Compatibility and non-goals

- Do not change terminal output or recording enablement.
- Do not add serialization or persistence for recording snapshots.
- Do not redesign Rich's `Segment` type.
- A new public API is not required; the value may remain an internal
  abstraction.

## Verifier design

Run the full suite, byte-for-byte golden comparisons for all three exporters,
clear and non-clear sequences, reuse of one snapshot for multiple formats, and
a bounded concurrency test. A structural check should confirm exporters no
longer read or clear the live record list independently.

## Anti-shortcut cases

- Copy the buffer independently inside each existing exporter.
- Return a mutable list that shares state with the console.
- Clear after releasing the lock.
- Refactor text and HTML while leaving SVG on the old path.
- Preserve plain text while losing control filtering, links, or styles.

## Packaging notes

Pin the repository and Python dependencies in the task image. No network or
external services are needed. Keep golden fixtures private and run the verifier
in a separate environment.

## Effort and risk

The behavioral surface is broad despite a localized implementation. The main
risk is making this a trivial helper extraction; require one reusable snapshot
to drive multiple formats and verify atomic clear behavior.
