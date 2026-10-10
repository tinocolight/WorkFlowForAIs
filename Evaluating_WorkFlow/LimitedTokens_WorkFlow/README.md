# LimitedTokens workflow

Entry: Evaluating, decided by the owner on 2026-10-10: two applications (Acervo, Consonância) use the origin method of revision 0001.

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

## Claims

An evaluation of this workflow SHOULD report on these claims in the fields Strength and Problem:

1. A new session continues the work from the files, with no help from the owner.
2. Two or more agents work in parallel with no lost work.
3. The project never restarts from zero.

The stage of the workflow follows the rules of the collector (`CONTRIBUTING.md`, section 9).

## Targets

| Target | Meaning |
| --- | --- |
| `WebApp/` | A web application, built and tested by AI agents. |
