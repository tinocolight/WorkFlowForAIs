# How to contribute

This file tells humans and AI agents how to change this repository.
Read `README.md` first. It defines the stages, the revisions, and the folder names.

## 1. Key words

The words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY have the meanings in RFC 2119 and RFC 8174.
They have these meanings only when they are in capital letters.

- MUST: an absolute requirement.
- MUST NOT: an absolute prohibition.
- SHOULD: do this, unless you have a reason. Write the reason in the pull request.
- MAY: optional.

## 2. Writing rules

All text in this repository MUST be in English.
The rules below are MUST for the files of the collector. They are SHOULD for the files in a `kit/` folder.
Humans and AI agents read the text. Many readers do not have English as their first language.
These rules come from ASD-STE100 (Simplified Technical English), the Federal Plain Language Guidelines,
and the Google developer documentation style guide.

1. Write one instruction in one sentence.
2. Write instructions with a maximum of 20 words. Write descriptions with a maximum of 25 words.
3. Write instructions in the imperative: "Read the file." Do not write "The file should be read."
4. Use the active voice. The subject does the action.
5. Put a condition before the instruction: "If the test fails, stop."
6. Use one term for one concept. Use the terms in the "Terms" table of the workflow. Do not use synonyms.
7. Use words that have one meaning. The table below gives the replacements.
8. Do not omit articles ("the", "a"), verbs, or subjects to make a sentence shorter.
9. Write numbered steps for a procedure. Write one action in one step.
10. Do not use idioms, jokes, or cultural references.
11. Write a paragraph about one topic, with a maximum of six sentences.

| Do not use | Use | Reason |
| --- | --- | --- |
| shall, will (for a rule) | MUST | "shall" and "will" can also mean a prediction. |
| should (lowercase, for a rule) | SHOULD or MUST | Lowercase "should" has no defined force. |
| once | after, or one time | "once" means "after" or "one time". |
| since | because, or after | "since" means "because" or "after". |
| while | during, or but | "while" means "during" or "but". |
| as (for a reason) | because | "as" has many meanings. |
| may (for a possibility) | can, or it is possible that | "may" is for permission only (key word). |
| e.g., i.e., etc. | for example, that is | Abbreviations are not clear to all readers. |
| it, this, that (unclear) | the name of the thing | The reader must not guess the reference. |
| set up, carry out, look into | create, do, examine | Phrasal verbs have many meanings. |

## 3. The collector does not restrict a workflow

A workflow can have any style of work. For example, it can push directly to `main`, or it can have no tests.
The rules of this file are for this repository only. They are not rules for the projects that use a workflow.

For this repository:

1. You MUST NOT push to `main`. The owner merges pull requests.
2. The first words of a pull request description MUST be "Merge allowed" or "Do not merge yet".
3. A pull request MUST pass the checks of section 10.

### Privacy

This repository is public. Each commit stays in the Git history, also after a later commit deletes the file.

1. You MUST NOT add parts of a conversation between a person and an AI: no prompts, no replies, no chat logs, and no screenshots of a chat.
2. You MUST NOT add personal information: real names, email addresses, telephone numbers, postal addresses, passwords, tokens, or keys.
3. To identify a person, use the Git account name, for example the GitHub user name. Do not use the real name.
4. A file in a `kit/` folder MUST contain placeholders, not content from a real project.
5. To record a decision, describe the decision in your own words. Do not quote the conversation.
6. If you added personal information by mistake, tell the owner immediately. A new commit does not remove it from the history.

The check of section 10 refuses a file that contains an email address.

## 4. Add a new workflow

1. Create `Theorized_WorkFlow/<Name>_WorkFlow/`. Copy `templates/WORKFLOW_README.md` to its `README.md`.
2. Create one folder for each target, for example `WebApp/`. Copy `templates/TARGET_README.md` to its `README.md`.
3. Create `Revision_0001_Working/` in the target. Copy `templates/REVISION_README.md` to its `README.md`.
4. Put the files that a project copies in `Revision_0001_Working/kit/`.
5. Run `python3 .github/scripts/evaluations.py --write`.

A new workflow starts in `Theorized_WorkFlow/`.
The owner can put a new workflow in `Evaluating_WorkFlow/` with this line in the workflow `README.md`:
`Entry: Evaluating, decided by the owner on YYYY-MM-DD: <evidence>`.

## 5. Change a Working revision

1. Change the files in the `Revision_<NNNN>_Working/` folder only.
2. Add one line to the list "Changes since the previous revision" in the revision `README.md`.
3. Keep each file of the `kit/` folder short. Each line costs tokens for each agent in each session.

## 6. Close a revision

After the close, nobody changes the Closed revision. A correction goes into the next revision. Do all the steps in one commit:

1. In the revision `README.md`, change the status line to `Status: Closed on YYYY-MM-DD`.
2. Rename the folder: `git mv Revision_0002_Working Revision_0002_Closed`.
3. Copy the Closed folder to the next number: `cp -r Revision_0002_Closed Revision_0003_Working`.
4. In the new `README.md`, change the status line to `Status: Working`. Clear the list of changes.
5. Run `python3 .github/scripts/evaluations.py --write`.

After the owner merges the commit, the owner creates the Git tag. The tag is the revision ID:
`git tag LimitedTokens/WebApp/r0002 <merge-commit>` and `git push origin LimitedTokens/WebApp/r0002`.

Rename the Working folder. Do not keep a Working folder and a Closed folder with the same number.
Each number then has one folder and one content.

## 7. A project that uses a Closed revision

1. Record the revision ID in the project, for example `LimitedTokens/WebApp/r0001`.
2. The content of the revision never changes. If the workflow moves to a different stage, only the path changes.
3. To find the revision, use the index in `README.md`, or the Git tag with the same name as the ID.
4. A rejected workflow stays in `Rejected_WorkFlow/`. Nobody deletes it.

## 8. Evaluate a workflow

Evaluate only a Closed revision. One person or one AI agent writes one file for one project.

1. Copy the block of `templates/EVALUATION.md` into a new file in `<Target>/Evaluations/`.
2. Name the file `R<NNNN>_<YYYY-MM-DD>_<project-owner>_<project>.md`, with the values of the fields.
3. Fill in each field. Use only the values that `templates/EVALUATION.md` allows.
4. Run `python3 .github/scripts/evaluations.py --write`. The program updates `STATUS.md`.
5. If the program changes the stage of the workflow, move the folder in the same pull request (section 9).

An evaluation file never changes. To correct it, add a new file with a later date. The newest file of a project counts.

## 9. Stages, verdicts, and moves

The program `.github/scripts/evaluations.py` gives each workflow its stage. The pull request moves the folder.

For each Closed revision, one evaluation counts for each project: the newest file. Let n be the count.
"Harm" is an evaluation with Overall effect -1 or -2, or with Project state "switched".

| Verdict of a Closed revision | Rule |
| --- | --- |
| Open | n is less than 3, or the revision is not Passed and not Failed. |
| Failed | n is 3 or more, and more than half of the evaluations are harm. |
| Passed | n is 3 or more; two thirds or more have Overall effect +1 or +2; harm is one quarter or less; two or more project owners; the medians of Ease of use and Goal contribution are 0 or more. |

| Level of a target | Rule, in this order |
| --- | --- |
| Rejected | The newest Closed revision with n of 3 or more failed. |
| Tested | A Closed revision passed. |
| Evaluating | A project evaluated a Closed revision, or the workflow `README.md` has an "Entry:" line of the owner. |
| Theorized | All other cases. |

The stage of the workflow is the highest level of its targets (Theorized, Evaluating, Tested).
The stage is Rejected if each target with a verdict is Rejected and no target is higher, or if the workflow `README.md` has this line:
`Rejection: YYYY-MM-DD: decided by the owner: <reason>`.

If the stage and the folder are different, the check fails and prints the `git mv` command. Move the full `<Name>_WorkFlow/` folder.

## 10. Automatic checks

GitHub Actions runs these checks on each pull request and on each push. Run them before you push:

```
bash .github/scripts/check-closed.sh origin/main
python3 .github/scripts/evaluations.py --check --base origin/main
```

1. `check-closed.sh` refuses a change to a Closed revision or to an existing evaluation file. A stage move is accepted.
2. `evaluations.py --check` refuses an evaluation file that is not valid, a workflow in the wrong stage folder, a generated file that is not current, and a file that contains an email address.

The checks are effective only if the owner protects `main` and requires the check "collector-checks" before a merge.
