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
Each workflow declares its style in a table (section 5), so that users know what they get.

For this repository:

1. You MUST NOT push to `main`. The owner merges pull requests.
2. The first words of a pull request description MUST be "Merge allowed" or "Do not merge yet".
3. A pull request MUST pass the check "collector-checks" (section 12).

### Privacy

This repository is public. Each commit stays in the Git history, also after a later commit deletes the file.

1. You MUST NOT add parts of a conversation between a person and an AI: no prompts, no replies, no chat logs, and no screenshots of a chat.
2. You MUST NOT add personal information: real names, email addresses, telephone numbers, postal addresses, passwords, tokens, or keys.
3. To identify a person, use the Git account name (for example the GitHub user name), a role, or a pseudonym. Do not use the real name.
4. A file in a `kit/` folder MUST contain placeholders, not content from a real project.
5. To record a request or a decision, write a summary of actions in your own words, with no personal details. Do not quote the conversation.
6. If you added personal information by mistake, tell the owner immediately. A new commit does not remove it from the history.

The check of section 12 refuses a file that contains an email address.

## 4. Layout and names

```
Workflows/<Name>/
  README.md                  the problem, the claims, and the Style table of the workflow
  <Target>/                  the type of project, for example WebApp
    README.md                the scope of the target
    STATUS.md                generated after each merge: the revisions, their verdicts, and their roles
    YANKED.md                the yanked revisions, one line each (section 10)
    Evaluations/             one file for each evaluation (section 8)
    r0001/                   a revision: README.md and kit/
    r0002/
```

- The ID of a revision is `<Name>/<Target>/rNNNN`, for example `LimitedTokens/WebApp/r0002`. The ID is also its Git tag.
- The path of a revision never changes. The stage of a workflow is not in the path. The program computes it (section 9).

## 5. Add a workflow

1. Create `Workflows/<Name>/README.md` from `templates/WORKFLOW_README.md`.
2. Fill in the Style table. Write "yes" or "no" for each practice. The check refuses a table with a missing practice.
3. Create one folder for each target, with a `README.md` from `templates/TARGET_README.md`.
4. Add the first revision `r0001/` with "Based on: none" (section 6).

A new workflow starts in the stage Theorized.
The owner can start a workflow in Evaluating with this line in the workflow `README.md`:
`Entry: Evaluating, decided by the owner on YYYY-MM-DD: <evidence>`.

The Style table is a declaration, not a judgement. If a new revision adds a line that looks like a practice that the table
says "no", the check refuses it. Change the line, or change the table in the same pull request.

## 6. Propose a revision

Work on a revision in a branch and a pull request. The pull request is the place where the revision can change.
After the merge, the revision never changes. A correction is a new revision.

1. Copy the folder of the base revision to the next free number, for example `r0003/`.
2. In its `README.md`, use `templates/REVISION_README.md`. Write these lines:
   - `Based on: r0002` (one or more existing revisions, separated by ", ").
   - `Author: <your Git account name>`.
   - The section "Changes": one line for each change.
   - The section "Upgrade from the base": what a project that uses the base must do, or "No action.".
3. Change the files in `kit/`.
4. Open a pull request.

The check refuses a new revision in these cases:

- The number is not higher than every existing number of the target. If another pull request took the number first, rename your folder.
- The base is yanked or tainted (section 9). Use a different base, or add the line `Reverts: rNNNN` with the reason.
- A protected rule changed or disappeared. A protected rule is a line with an ID in square brackets, for example `[V3]`.
  Only the owner can accept the change, with the label "invariant-change" on the pull request.
- A new line looks like a practice that the Style table says "no" (section 5).
- A line `Workflow revision: <ID>` in the kit is not the ID of the revision.
- The target has more than 3 open candidates (section 9). Evaluate the existing candidates first, or create a derived workflow (section 11).

After the merge, GitHub Actions creates the tag and a release with a zip of the kit. Nobody does it by hand.

## 7. Use a revision

1. Select a revision on the web page, or in the index of `README.md`. Prefer the role "recommended".
2. Download the zip, and extract it into the root of your project.
3. Record the revision ID in your project.
4. To be told about a yanked revision, select "Watch", then "Custom", then "Releases" on GitHub.
5. Before you upgrade, read the section "Upgrade from the base" of each revision between yours and the new one.
   To read all the differences: `git diff <old-ID> <new-ID> -- Workflows/<Name>/<Target>`.

## 8. Evaluate a revision

1. Copy the block of `templates/EVALUATION.md` into `Workflows/<Name>/<Target>/Evaluations/`.
2. Name the file `R<NNNN>_<YYYY-MM-DD>_<project-owner>_<project>.md`.
3. Fill in each field. Use only the values that the template allows.
4. Open a pull request. The program updates `STATUS.md` after the merge.

The check refuses an evaluation in these cases:

- The file is not valid.
- "Project owner" is not the Git account name of the author of the pull request.
- One pull request adds evaluations of more than one project owner.

An evaluation file never changes. To correct it, add a new file with a later date. The newest file of a project counts.
An evaluation by the author of the revision does not count.

## 9. Verdicts, roles, and stages

The program `.github/scripts/collector.py` computes everything in this section. For each revision, one evaluation counts
for each project: the newest file. Let n be the count. "Harm" is an Overall effect of -1 or -2, or the state "switched".

| Verdict | Rule |
| --- | --- |
| Passed | n is 3 or more; two thirds or more have Overall effect +1 or +2; harm is one quarter or less; two or more project owners; the medians of Ease of use and Goal contribution are 0 or more. |
| Failed | n is 3 or more, and more than half of the evaluations are harm. |
| Open | All other cases. |

| Role | Rule, in this order |
| --- | --- |
| yanked | A line in `YANKED.md`, the verdict Failed, or a regression: three or more projects compared it with the previous revision, and the median is -1 or lower. |
| tainted | A revision that it is based on, directly or indirectly, is yanked, and its own verdict is not Passed. |
| recommended | The newest revision with the verdict Passed. |
| passed | An older revision with the verdict Passed. |
| superseded | An open revision that has a newer revision based on it. |
| dormant | An open revision with no newer revision, more than 180 days old, with fewer than 3 counted evaluations. |
| candidate | An open revision with no newer revision. |

| Stage of a target | Rule, in this order |
| --- | --- |
| Tested | A revision passed. |
| Evaluating | A project evaluated a revision, or the workflow `README.md` has an "Entry:" line of the owner. |
| Theorized | All other cases. |

The stage of a workflow is the highest stage of its targets. Only the owner rejects a full workflow, with this line in its
`README.md`: `Rejection: YYYY-MM-DD: decided by the owner: <reason>`. A bad revision does not reject the workflow.

When a revision works and the next one fails, the first one stays recommended. When ten people propose revisions from the
same base, each one is a candidate. The evaluations decide which ones pass. A candidate with no evaluations becomes dormant.

## 10. Yank a revision

Yank a revision that is broken or harmful. The revision stays in its place, because projects use it.
New projects do not get it, and new revisions cannot be based on it.

1. Add one line at the end of `Workflows/<Name>/<Target>/YANKED.md`: `- rNNNN: YYYY-MM-DD: broken|regression|harmful: <reason>`.
2. Open a pull request. The owner merges it.

After the merge, the release of the revision gets the mark "[YANKED]". The people who watch releases see it.
Lines in `YANKED.md` are never changed or removed.

## 11. Derived workflows

If your idea changes the problem or the claims of a workflow, create a new workflow (section 5).
Add the line `Derived from: <ID>` to its `README.md`. It starts in Theorized. Evaluations do not move to it.

## 12. Automatic checks and settings

The check "collector-checks" runs on each pull request and on each push. Run it before you push:

```
python3 .github/scripts/collector.py --check --base origin/main --author <your Git account name>
```

1. A pull request cannot change the rules that check it. The program runs from the base branch.
2. The check refuses a change to a merged revision or evaluation, and the cases of sections 6, 8, and 10.
3. The check refuses hidden characters (for example zero-width or bidirectional characters) and email addresses in any file.

After each merge, `.github/workflows/after-merge.yml` writes each `STATUS.md` and the index in `README.md`, and creates
the tags and the releases. Pull requests do not contain generated files.

The owner sets these options on GitHub:

- Settings, Rules: protect `main`, require a pull request and the check "collector-checks".
  Allow "GitHub Actions" to bypass the rule, so that the generated files can be written. Without it, the job opens a pull request.
- Settings, Pages: Source "GitHub Actions".
- Settings, Actions, General: "Read and write permissions", and "Allow GitHub Actions to create pull requests".
