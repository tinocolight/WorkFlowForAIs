# AGENTS.md

This file is the entry point for each AI agent that works in this project. Read this file first.

## Key words

The words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY have the meanings in RFC 2119 and RFC 8174.
They have these meanings only when they are in capital letters.

## Start of a session

Do these steps at the start of each session, and after each loss of context:

1. Read `workflow/METHOD.md` from the start to the end.
2. Read `workflow/STATE.md` from the start to the end.
3. Before you change code, read `workflow/ENGINEERING.md`.
4. Do steps 1 to 3 one time per session. If you read the files in this session, do not read them again.

Do not read these files at the start:

- `workflow/HISTORY.md`. Read it only to answer a specific question about a past decision. Start at its index.
- `workflow/GLOSSARY.md`. Search it for a word. Do not read all of it.
- The source files, one by one. Use the map of the project (see "Project facts") to find the file that you need.

## Rules that have no exceptions

Each rule has one explanation, in the file that the arrow shows.

1. You MUST NOT push to `main`. You MUST NOT push to the branch of a different contributor. The owner merges. → `METHOD.md` section 3.
2. You MUST record a stage in `STATE.md` before you write the first line of code. → `METHOD.md` section 4.
3. You MUST NOT write text for people or decision numbers directly in the code. → `ENGINEERING.md` section 2.
4. A module MUST use only the modules that come before it in the layer order. → `ENGINEERING.md` section 3.
5. If a program can check a rule, a program MUST check the rule. → `ENGINEERING.md` section 5.
6. If you do not find what you expect, stop and tell the owner what you did not find. You MUST NOT restart the project from zero. → `METHOD.md` section 9.
7. You MUST NOT copy a conversation or personal information into a file. Record requests as summaries of actions. → `METHOD.md` section 13.

## Project facts

Complete this section when you adopt the method. Write "none" if a fact does not apply.

| Fact | Value |
| --- | --- |
| Project name | |
| Language for messages to the owner | |
| Default branch | `main` |
| Map of the project (one line for each file) | |
| Command that shows the state at the start of a session | |
| Build command | |
| Targeted verification command (for each block) | |
| Full verification command (before each merge) | |
