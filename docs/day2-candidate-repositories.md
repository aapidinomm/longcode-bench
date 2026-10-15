# Day 2 repository shortlist

Research date: 2026-10-15.

The machine-readable record is in `candidates/repositories.toml`. Scores are
based on static inspection of the pinned revisions and must be re-measured in
the final task images.

| Language | Repository | Pinned revision | License | Source / test LOC | Task | Score |
| --- | --- | --- | --- | ---: | --- | ---: |
| Python | pallets/click | `2247b35` | BSD-3-Clause | 12,930 / 16,294 | Opt-in response-file expansion | **93** |
| Python | Textualize/rich | `9d8f9a3` | MIT | 38,515 / 11,217 | Immutable recording snapshots | 83 |
| Go | spf13/cobra | `adbc881` | Apache-2.0 | 6,955 / 9,810 | Command-tree diagnostics | 90 |
| Go | BurntSushi/toml | `d733fc5` | MIT | 6,032 / 4,481 | Positioned decode errors | 91 |
| Rust | mitsuhiko/insta | `4b270ba` | Apache-2.0 | 16,203 / 9,741 | Non-interactive review plans | 82 |
| Rust | sharkdp/fd | `14dcd92` | MIT OR Apache-2.0 | 5,168 / 3,499 | Pure entry-filter pipeline | 86 |

## Pilot nomination

`python-click-response-files` is the first task to package.

It exercises configuration inheritance, argument preprocessing, recursive file
loading, path resolution, diagnostics, documentation, and tests while keeping
the runtime hermetic. The pinned Click tree has Windows-only shell expansion
but no general response-file facility. The feature is opt-in, so compatibility
can be checked precisely against the existing suite.

The intended human effort is three to five hours. The main scope risk is an
implementation that supports only one flat file; nested relative includes,
cycle diagnostics, escaping, the `--` boundary, and unchanged default behavior
make that shortcut insufficient.

The exact pinned revision has a green local baseline: 2,261 tests passed, 25
were skipped, and one was expected to fail in 4.00 seconds with
`uv run --frozen pytest -q`.

## Packaging order

1. Build a pinned Click source image with all Python test dependencies already
   installed.
2. Write the agent-facing instruction from the public requirements only.
3. Implement the oracle independently.
4. Write hidden tests from the behavior matrix, not from the oracle structure.
5. Create broken patches for flat-only expansion, current-working-directory
   resolution, expansion past `--`, missing cycle checks, and default-on
   behavior.
6. Run the task through OpenSandbox with agent and verifier networking disabled.
7. Calibrate with multiple models and one clean human solve before publication.
