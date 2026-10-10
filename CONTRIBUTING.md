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

## 3. Branches and pull requests

1. You MUST NOT push to `main`. The owner merges pull requests.
2. Create one branch for one change.
3. The first words of the pull request description MUST be "Merge allowed" or "Do not merge yet".
4. If the change is not complete, write "Do not merge yet" and the work that remains.
5. A pull request MUST NOT change a Closed revision. The automatic check refuses the change (section 9).

## 4. Add a new workflow

1. Create the folder `Theorized_WorkFlow/<Name>_WorkFlow/<Target>/Revision_0001_Working/`.
2. Put a `README.md` in the revision folder. Use the `README.md` of an existing revision as the model.
3. Put the files that a project copies in a `kit/` folder in the revision folder.
4. Put a `README.md` in the `<Name>_WorkFlow/` folder. Write the purpose of the workflow in two to five sentences.
5. Add the workflow to the table "Current workflows" in the root `README.md`.

## 5. Change a Working revision

1. Change the files in the `Revision_<NNNN>_Working/` folder only.
2. Add one line to the "Changes since the previous revision" list in the revision `README.md`.
3. Keep each file of the `kit/` folder as short as possible. Each line costs tokens for each agent in each session.

## 6. Close a revision

Close a revision when its content is ready for real projects.
After the close, nobody changes the Closed revision. A correction goes into the next revision.

Do all the steps in one commit:

1. In the revision `README.md`, change the status line to `Status: Closed on YYYY-MM-DD`.
2. Rename the folder: `git mv Revision_0002_Working Revision_0002_Closed`.
3. Copy the Closed folder to the next number: `cp -r Revision_0002_Closed Revision_0003_Working`.
4. In the new `README.md`, change the status line to `Status: Working`. Clear the list of changes.
5. Update the table "Current workflows" in the root `README.md`.

After the owner merges the commit, create a Git tag on the merge commit:

```
git tag LimitedTokens/WebApp/r0002 <merge-commit>
git push origin LimitedTokens/WebApp/r0002
```

The tag does not include the stage. The stage can change. The tag stays the same.

Why rename, and not keep a Working folder and a Closed folder with the same number:

- Two folders with the same number and different content cause confusion.
- After the rename, each number has one folder. The number identifies one content.
- The rename breaks links to the Working folder. This is correct: nobody can depend on Working content.
- The Git tag and the commit hash keep a permanent link to each Closed revision.

## 7. Move a workflow to a different stage

1. Move the full `<Name>_WorkFlow/` folder with `git mv`. Do not change any file in the same commit.
2. Write the reason for the move in the `README.md` of the `<Name>_WorkFlow/` folder, in a separate commit.
3. A move to `Rejected_WorkFlow/` MUST include the reason for the rejection.

The automatic check accepts a move of a Closed revision only if no file content changes.

## 8. Create an original workflow from a revision

You MAY use any revision as the start of a new workflow. Use a Closed revision.

1. Copy the `kit/` folder of the Closed revision.
2. Create a new workflow with a new `<Name>` (section 4).
3. In the new revision `README.md`, write the origin: the path and the tag of the revision that you copied.

## 9. Automatic check

The file `.github/scripts/check-closed.sh` refuses changes to Closed revisions.
GitHub Actions runs the check on each pull request and on each push.
Run the check on your computer before you push:

```
bash .github/scripts/check-closed.sh origin/main
```

The check accepts:

- new files in a new `Revision_<NNNN>_Closed/` folder (the close of a revision);
- the move of a Closed revision to a different stage, if no file content changes.

The check refuses all other changes inside a `Revision_<NNNN>_Closed/` folder that exists on the base.
The check is effective only if the owner protects `main` and requires the check to pass before a merge.
