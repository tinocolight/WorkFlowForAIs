# LimitedTokens workflow

LimitedTokens is a workflow for a software project that AI agents build in Git branches.
A human owner directs the work and merges each pull request.
The workflow keeps the work correct when the context of each agent is limited and each token has a cost.

## Problem

- An AI agent loses its context between sessions, and sometimes during a session.
- Several agents work at the same time, in different branches, on the same project.
- Each file that an agent reads costs tokens, in each session.

## Solution in summary

- A small number of Markdown files hold the method, the current state, and the history.
- The agent reads the method and the state one time per session. The agent reads the history only for a specific question.
- Each stage of work is recorded before the first line of code. A new session continues from the record.
- Programs check the rules. A rule that only exists as text is forgotten.
- Verification is targeted for each step and complete before each merge.

## Test criteria

The workflow moves to `Tested_WorkFlow/` when all these criteria are true:

1. Three projects used a Closed revision for a minimum of 20 stages each.
2. In each project, a new session continued the work from the files, with no help from the owner.
3. In each project, two or more agents worked in parallel with no lost work.
4. No project restarted from zero.

## Targets

| Target | Meaning |
| --- | --- |
| `WebApp/` | A web application, built and tested by AI agents. |
