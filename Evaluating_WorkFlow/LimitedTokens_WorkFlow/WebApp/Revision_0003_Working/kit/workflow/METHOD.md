# METHOD.md: how the work is done

Read this file one time per session, before `STATE.md`. This file tells HOW to work.
`STATE.md` tells WHAT to do now.

## 1. Terms

Use each term with this meaning only. Do not use a synonym.

| Term | Meaning |
| --- | --- |
| owner | The human who directs the project and merges pull requests. |
| contributor | One AI agent that works in one branch. The table in section 3 lists the contributors. |
| session | One continuous conversation between the owner and one contributor. |
| interaction | One reply of a contributor to one message of the owner. |
| stage | One unit of work with a number, a request, and a "done when" text. |
| block | One step of a stage. Each block ends with a commit and a push. |
| backlog item | One request that is not started. It has a number `B-NNN`. |
| verification | The programs that check the project: build, tests, guards, and audit. |
| guard | A program that checks a rule of `ENGINEERING.md`. |
| ceiling | The maximum count of known violations of a rule in one file. It only goes down. |

## 2. The files

| File | Question that the file answers | When an agent reads it | Who writes it |
| --- | --- | --- | --- |
| `AGENTS.md` | Where do I start? | First, in each session | The owner, or a stage that the owner requests |
| `workflow/METHOD.md` | How is the work done? | One time per session | A stage that the owner requests |
| `workflow/STATE.md` | Where is the project? What is next? | One time per session, after METHOD | Each contributor, during the work |
| `workflow/ENGINEERING.md` | How is the code written? | Before a change to code | A stage that the owner requests |
| `workflow/HISTORY.md` | What was decided, and why? | Only for a specific question | Each contributor, when a stage closes |
| `workflow/GLOSSARY.md` | Which word do I use for the owner? | Search only | Each contributor, when a new term appears |

## 3. People and branches

1. Each contributor works in its own branch only. The table below lists the branches.
2. You MUST push after each block. Another session can continue from the push.
3. You MUST NOT push to `main`. You MUST NOT push to a branch of a different contributor.
4. The owner merges each pull request into `main`.
5. A tester branch (name `ux/*`) records user tests. Contributors read its folder only to find usability work.
6. Only the contributor with "yes" in the column "Evaluation" does the periodic evaluation (section 8).

### Contributors

| Branch | Role | Evaluation |
| --- | --- | --- |
| `<branch-name>` | first contributor | yes |

### A new contributor

1. Read `AGENTS.md`, then do the start of a session.
2. Open a stage with the next free number (section 4, step 1).
3. In the first block, add your branch to the table above, with "no" in "Evaluation".
4. Open a pull request. The owner merges it.

### Before you start work

1. Fetch all branches. If your branch has commits that you do not have, get them first.
2. Examine the open pull request of your branch. Its description starts with "Merge allowed" or "Do not merge yet".
3. If `main` has new commits, merge `main` into your branch.

## 4. A stage

### Open a stage

1. Find the highest stage number in all branches. Your stage number is that number plus one.
2. In `STATE.md`, section "Current stage", write the stage before any code:
   - the title, the number, the text "(IN PROGRESS, YYYY-MM-DD)";
   - the request, as a summary of actions in your words (section 13);
   - "Done when:" and the results that a person or a program can check;
   - one checkbox for each block, and one checkbox for the close.
3. Commit and push the stage record.

### Do a block

1. Make the change.
2. Write a test that fails before the change and passes after the change.
3. Run the targeted verification (section 5).
4. Mark the checkbox of the block in `STATE.md`. Write the measured result next to the checkbox.
5. Commit and push. The commit message starts with "Stage N, block M:".

### Close a stage

1. Run the full verification (section 5).
2. Move the full stage text from `STATE.md` to the end of `HISTORY.md`. Use the format in `HISTORY.md`.
3. Add one line to the index at the start of `HISTORY.md`.
4. Add one line for the owner to the change log of the project.
5. Write "None." in the section "Current stage" of `STATE.md`.
6. Commit, push, and open or update the pull request (section 6).

Only one stage is in progress in a branch at one time.

## 5. Verification

| When | What to run | Result |
| --- | --- | --- |
| After each block | The targeted verification: all tests, all guards, and only the audit parts that the changed files touch. | "incomplete" if it passes. |
| Before each "Merge allowed" | The full verification: all steps. | "all pass", or "Do not merge yet". |

Redundancy rules:

1. If you are not sure which audit parts a change touches, run all parts.
2. A change to a file that many parts use runs all parts.
3. Three fast audit parts (sentinels) run after each change to application code.
4. A "Merge allowed" MUST follow a full verification that passed on the last commit.

## 6. Pull requests

1. The first words of the description MUST be "Merge allowed" or "Do not merge yet".
2. "Merge allowed" means: the full verification passed on the last commit, and the stage is closed.
3. Write the results with numbers: tests, time, sizes.
4. If a different branch changes the same lines, write the files and the resolution in the description.

## 7. Continuous review

In each interaction, each contributor reviews three files that nobody reviewed.

1. Select the files: first the files that have no description line, then the files that nobody reviewed, then the oldest review.
2. Read each file from the start to the end.
3. Make sure that the description line tells what the file does now. If the description is wrong, correct it.
4. If you find a small error in the code, correct it. If the error is large, add a backlog item.
5. Add the line `Reviewed: YYYY-MM-DD.` after the header comment of the file.
6. Commit the review separately. The commit message names the three files.

Do not review generated files. Review the program that generates them.

## 8. Periodic evaluation

One contributor (section 3) does the evaluation after each four interactions.

1. Measure the project: size of the build, count of tests, duration of the full verification, counts of each ceiling.
2. Compare the numbers with the previous evaluation.
3. For each number that became worse, add a backlog item with the reason.
4. Record the evaluation in the file that `STATE.md` names.

## 9. Stop rules

1. If you do not find a file or a result that you expect, stop. Tell the owner what you expected and what you found.
2. You MUST NOT restart the project from zero.
3. If a decision belongs to the owner, stop and ask. Give the options and your recommendation.
4. If the owner gives a decision, record the decision and the date in the backlog item, in your words (section 13).

## 10. Token rules

Each line that an agent reads costs tokens in each session. Use these rules to read less.

1. Read `METHOD.md` and `STATE.md` one time per session.
2. Use the map of the project to find a file. Do not open files to find a file.
3. Search a file before you read all of it. Read only the lines that you need.
4. Do not read a file again after you edit it. The edit tool reports a failure.
5. Do independent actions together, in one step.
6. Keep `STATE.md` below its maximum (section 11). Move closed work to `HISTORY.md`.
7. Run a long verification in the background. Do other work during the verification.
8. If the context is almost full, close what is open. Write in `STATE.md` where you stopped. Commit and push.
9. After a loss of context, do the start of a session again (`AGENTS.md`).

## 11. Limits

| Limit | Value | Reason |
| --- | --- | --- |
| Lines in `STATE.md` | 450 | Each session reads the full file. |
| Lines in a source module | 300 | A longer module usually does more than one thing. |
| Files reviewed in each interaction | 3 | The review continues without a large stage. |
| Interactions between evaluations | 4 | The numbers stay visible. |

## 12. Messages to the owner

1. Write in the language of the owner (see `AGENTS.md`, "Project facts").
2. Use the words of `GLOSSARY.md`. Search the glossary before you name a part of the application.
3. Write the result first. Then write the evidence.
4. If you need a decision, ask one question with options.

## 13. Privacy

The files of the project can become public. Each commit stays in the Git history, also after a later commit deletes the text.

1. You MUST NOT copy a conversation into a file. Do not quote the owner or an AI.
2. Record a request or a decision as a summary of actions: "Add X", "Remove Y", "Use Z because W".
3. Remove personal details from the summary: names, places, dates of birth, health, money, and opinions about people.
4. Identify a person by role ("owner", "contributor"), by Git account name, or by a pseudonym. You MUST NOT write a real name.
5. You MUST NOT write email addresses, telephone numbers, postal addresses, passwords, tokens, or keys.
6. If personal information enters a commit, stop and tell the owner. A new commit does not remove it from the history.
