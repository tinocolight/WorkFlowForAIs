# Rejected workflows

The newest revision with evidence of a workflow in this folder failed, or the owner rejected the workflow. Nobody deletes a rejected workflow. Its record prevents the same error in the future.

## Folder structure

```
Rejected_WorkFlow/<Name>_WorkFlow/<Target>/
  README.md                 the scope of the target
  STATUS.md                 generated: the evaluations and the verdict of each Closed revision
  Evaluations/              one file for each evaluation
  Revision_<NNNN>_Closed/   permanent content
  Revision_<NNNN>_Working/  content that can change
```

## How a workflow enters and leaves this folder

The program `.github/scripts/evaluations.py` gives each workflow its stage from the evaluations.
Nobody moves a workflow by opinion. The rules are in `CONTRIBUTING.md`, section 9.

## Contribute

- Use a Closed revision in a project, then evaluate it: `CONTRIBUTING.md`, sections 7 and 8.
- Improve a workflow in its Working revision: `CONTRIBUTING.md`, section 5.
- Create a new workflow, also from a copy of a revision of any stage: `CONTRIBUTING.md`, section 4. Write the revision ID of the origin in its `README.md`.
