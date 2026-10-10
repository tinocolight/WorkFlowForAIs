# LimitedTokens / WebApp / Revision 0002

Status: Working
Tag: none. A revision receives its tag when it closes (`CONTRIBUTING.md`, section 6).
Origin: a copy of `Revision_0001_Closed/`.

The content of a Working revision can change at any time. Do not use it for production work.

## Contents

```
kit/                     Copy the contents of this folder into the root of your project.
  AGENTS.md              The entry point for all AI agents. It lists the rules that have no exceptions.
  CLAUDE.md              The entry point for Claude Code. It imports AGENTS.md.
  workflow/
    METHOD.md            How the work is done. Agents read it one time per session.
    STATE.md             Where the project is, and what comes next. Agents read it one time per session.
    ENGINEERING.md       The rules for code. Agents read it before they change code.
    HISTORY.md           The closed stages. Agents read it only for a specific question.
    GLOSSARY.md          The words for the owner. Agents search it. They do not read all of it.
```

## Adopt the revision in a new project

1. Copy the contents of `kit/` into the root of the project repository.
2. In `AGENTS.md`, complete the section "Project facts".
3. In `workflow/METHOD.md`, complete the table "Contributors" (section 3).
4. Start a session with an AI agent. Tell the agent: "Read AGENTS.md and start stage 0."
5. Stage 0 is "Adopt the method". The agent records the existing project in `workflow/STATE.md` before it changes code.

## Adopt the revision in an existing project

Do steps 1 to 4. In stage 0, the agent makes an inventory of the project. The agent MUST NOT change working code in stage 0.
For each rule that the existing code breaks, the agent records the current count as a ceiling. The ceiling only goes down.

## Changes since the previous revision

None yet. Add one line for each change.
