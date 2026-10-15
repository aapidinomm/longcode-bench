# Repository selection rubric

This rubric is for selecting open-source repositories that can support
repeatable, long-horizon coding tasks in Harbor. A candidate must pass every
gate and score at least 75 out of 100.

## Mandatory gates

1. The source license permits modification and redistribution.
2. The exact base revision can be pinned by a full commit SHA.
3. The repository has an automated test suite that can run without external
   credentials or paid services.
4. Dependencies can be baked into the task image so agent and verifier phases
   can run with no network.
5. The task can be verified from repository state and deterministic tests.
6. The proposed behavior is not already present at the pinned revision.
7. A competent maintainer should need at least one hour to implement and test
   the change.

## Scored criteria

| Criterion | Weight | Full-score evidence |
| --- | ---: | --- |
| Hermeticity | 20 | Tests and build run locally; all dependencies can be pinned and cached. |
| Verifier determinism | 20 | Correctness has stable, observable behavior with low timing or platform sensitivity. |
| Task depth | 20 | Work crosses meaningful modules or abstractions and requires design, implementation, and tests. |
| Maintainability | 15 | The repository is understandable, active, and neither toy-sized nor prohibitively large. |
| Novelty | 15 | Static inspection shows the feature is absent and the task is not a transcription of an open issue or merged patch. |
| Build speed | 10 | Clean build and targeted verification should fit comfortably inside the benchmark timeout. |

Scores recorded during repository discovery are preliminary. Before publishing
a task, the task author must replace assumptions with measurements from the
pinned container image.

## Task-level release gates

A repository score alone is insufficient. Each task must also have:

- a public specification containing behavior and compatibility requirements;
- a private verifier plan with independently written hidden cases;
- an oracle patch that passes both upstream and hidden tests;
- at least four deliberately broken implementations that hidden tests reject;
- a clean-slate solve by a second author or agent;
- no network during agent or verifier execution, unless an allowlist is
  explicitly justified;
- a measured expert solve time of at least 60 minutes;
- a resettable repository state and a separately executed verifier.

## Contamination controls

- Do not copy an upstream issue, pull request, commit message, or patch.
- Search the pinned tree for equivalent APIs and behavior before approving a
  brief.
- Record the base SHA and research date.
- Keep hidden fixtures, mutation patches, and oracle details out of the public
  task package.
- Prefer synthetic requirements assembled from several ordinary maintenance
  needs over a single recognizable upstream request.
