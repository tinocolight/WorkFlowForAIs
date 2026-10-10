# WorkFlowForAIs

WorkFlowForAIs is a library of workflows for software projects that AI agents build.
A human owner directs the work. One or more AI agents do the work in Git branches.

A workflow is a set of Markdown files. You copy the files into a new project.
The files tell each AI agent how to start, how to work, how to record the work, and how to stop.
The files are for agents from all companies (Anthropic, OpenAI, Google, and others) and for humans.

## How the library is organized

Each workflow moves through four stages. The stage is the top folder.

| Folder | Stage | Meaning |
| --- | --- | --- |
| `Theorized_WorkFlow/` | Theorized | The workflow is a proposal. Nobody used it in a real project. |
| `Evaluating_WorkFlow/` | Evaluating | Real projects use the workflow now. The results are not complete. |
| `Tested_WorkFlow/` | Tested | The workflow completed the test criteria in its README. |
| `Rejected_WorkFlow/` | Rejected | The workflow failed. Its README records why. Nobody deletes it. |

The path to one revision of a workflow has five parts:

```
<Stage>_WorkFlow/<Name>_WorkFlow/<Target>/Revision_<NNNN>_<Status>/
```

- `<Name>`: the name of the workflow, for example `LimitedTokens`.
- `<Target>`: the type of project that the workflow is for, for example `WebApp`.
- `<NNNN>`: the revision number, four digits, from `0001` to `9999`.
- `<Status>`: `Closed` or `Working`.

## The two revision statuses

- **Closed:** the content is permanent. Nobody changes a Closed revision, even if it has errors.
  You can use a Closed revision in your project and know that it stays the same.
- **Working:** the content can change at any time. Do not use a Working revision for production work.

Each target has one Working revision at most.
The rules for closing a revision are in `CONTRIBUTING.md`, section "Close a revision".

## Use a workflow in your project

1. Select a Closed revision. A revision in `Tested_WorkFlow/` has the most evidence.
2. Read the `README.md` of the revision.
3. Copy the contents of its `kit/` folder into the root of your project.
4. Record the full path and the Git tag of the revision in your project. The tag is the permanent reference.

## Current workflows

| Workflow | Target | Stage | Last Closed revision | Working revision |
| --- | --- | --- | --- | --- |
| LimitedTokens | WebApp | Evaluating | `Revision_0001_Closed` | `Revision_0002_Working` |

## Contribute

Read `CONTRIBUTING.md`. All text in this repository is in English.

## License

MIT. See `LICENSE`.
