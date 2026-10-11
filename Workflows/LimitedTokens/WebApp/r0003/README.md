# LimitedTokens / WebApp / r0003

Based on: r0002
Author: tinocolight

This revision adds lessons from a project that used r0002: how to find a cause with few tokens, when to use sub-agents,
and how to make tests and audits show what they did not check.

## Changes

- New `METHOD.md` section 14, "Find a cause": go back from the wrong result to its cause, and stop at the cause.
- New `METHOD.md` section 10, rules 10 to 12: the cost of sub-agents before their start, and the model by difficulty.
- New `METHOD.md` section 5, rules 5 and 6: no change to the project during a full verification.
- New `ENGINEERING.md` section 4, rules 7 and 8: a test checks the changed part, and does not copy the source.
- New `ENGINEERING.md` section 4, rules 9 and 10: an audit counts its cases, and does not skip a case.
- New `ENGINEERING.md` section 4, rule 11: a new file goes into the file list of the build in the same commit.

## Upgrade from the base

1. Replace `workflow/METHOD.md` and `workflow/ENGINEERING.md` with the files of this revision.
2. Keep your table "Contributors" in `METHOD.md` section 3. Copy it into the new file.
3. Keep the commands of your project in `ENGINEERING.md` section 6. Copy them into the new file.

No other file changed.

## Contents

```
kit/                     Extract into the root of the project.
  AGENTS.md              The entry point for all AI agents, with the rules that have no exceptions (project-owned: never replace)
  CLAUDE.md              The entry point for Claude Code. It imports AGENTS.md (project-owned: never replace)
  workflow/
    METHOD.md            How the work is done. Agents read it one time per session (replace on upgrade)
    STATE.md             Where the project is, and what comes next (project-owned: never replace)
    ENGINEERING.md       The rules for code. Agents read it before they change code (replace on upgrade)
    HISTORY.md           The closed stages. Agents read it only for a specific question (project-owned: never replace)
    GLOSSARY.md          The words for the owner. Agents search it (project-owned: never replace)
```
