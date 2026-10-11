# WorkFlowForAIs

WorkFlowForAIs collects workflows for software projects that AI agents build.
A workflow is a small set of Markdown files that you copy into a project.
The files tell each AI agent how to start, how to work, how to record the work, and when to stop.

**Web page:** [tinocolight.github.io/WorkFlowForAIs](https://tinocolight.github.io/WorkFlowForAIs/) shows the workflows with
their scores and evaluations, and a zip of each revision. The page reads this repository each time it opens.

The collector accepts workflows of all kinds. A workflow can use branches and tests, or it can push directly to `main`
with no tests. Each workflow declares its style. The evaluations from real projects judge the result.

## How the collector works

1. Each workflow has numbered **revisions**, for example `LimitedTokens/WebApp/r0002`. A revision never changes after the merge.
2. Each project that uses a revision adds one **evaluation**: a short file with fixed fields.
3. A program computes a **verdict** for each revision (Passed, Failed, Open), a **role** (recommended, candidate, yanked,
   and others), and a **stage** for each workflow (Theorized, Evaluating, Tested, Rejected).
4. A bad revision is **yanked**: it stays in its place for the projects that use it, and new projects do not get it.

The rules are in [`CONTRIBUTING.md`](CONTRIBUTING.md), section 9.

## Use a workflow in your project

1. On the web page, select a workflow, then the revision with the role "recommended". If no revision passed yet, select a candidate.
2. Download its zip, and extract it into the root of your project.
3. Record the revision ID in your project.
4. After some work, add an evaluation ([`CONTRIBUTING.md`](CONTRIBUTING.md), section 8).

## Contribute

| You want to | Read |
| --- | --- |
| Evaluate a workflow that you used | [`CONTRIBUTING.md`](CONTRIBUTING.md), section 8, and [`templates/EVALUATION.md`](templates/EVALUATION.md) |
| Propose a new revision | [`CONTRIBUTING.md`](CONTRIBUTING.md), section 6 |
| Add a new workflow | [`CONTRIBUTING.md`](CONTRIBUTING.md), section 5, and [`templates/`](templates/) |
| Report a broken or harmful revision | [`CONTRIBUTING.md`](CONTRIBUTING.md), section 10 |

All text in this repository is in English. AI agents start at [`AGENTS.md`](AGENTS.md).

## Index of revisions

Written after each merge by GitHub Actions. Do not edit the table by hand.

<!-- BEGIN GENERATED: revisions -->
| Revision ID (also the Git tag) | Workflow stage | Role | Verdict | Counted evaluations | Path |
| --- | --- | --- | --- | --- | --- |
| `LimitedTokens/WebApp/r0003` | Evaluating | candidate | Open | 0 | `Workflows/LimitedTokens/WebApp/r0003/` |
| `LimitedTokens/WebApp/r0002` | Evaluating | superseded | Open | 0 | `Workflows/LimitedTokens/WebApp/r0002/` |
| `LimitedTokens/WebApp/r0001` | Evaluating | superseded | Open | 0 | `Workflows/LimitedTokens/WebApp/r0001/` |
<!-- END GENERATED: revisions -->

## License

MIT. See [`LICENSE`](LICENSE).
