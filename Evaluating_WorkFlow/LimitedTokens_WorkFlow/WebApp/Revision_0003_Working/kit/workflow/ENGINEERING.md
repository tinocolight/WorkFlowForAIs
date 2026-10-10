# ENGINEERING.md: how the code is written

Read this file before you change code. Each rule has a guard (section 5), or a backlog item for its guard.

## 1. The map of the project

1. Each file starts with a header comment. The first line of the comment is the identity line.
2. The identity line has the format `<module id> — <one sentence>.` The sentence ends with a period.
3. If you cannot describe the file in one sentence without "and", the file does two things. Divide it.
4. A program generates the map of the project from the identity lines. Nobody edits the map by hand.
5. The map generator MUST fail if a file has no identity line.

## 2. Central files: no loose text, no loose numbers

| Content | Where it goes | Example |
| --- | --- | --- |
| Text that a person reads | A dictionary, one for each language. The code uses the key. | `labels.en.js`, `labels.pt.js` |
| A number that decides (a limit, a time, a size) | The settings registry, in a group. Each value has its reason. | `settings.group('gallery').minWidth` |
| A number of a published formula | In the line, with the comment `// structure: <reason>`. | the sRGB gamma curve |
| A constant of one module | A block `STRUCTURE = { … }` at the start of the module. | the steps of a search |

Only 0, 1, and 2 can be loose in the code. A number in a text (`'8px'`) is also a number.

Each value of the settings registry has:

- `$value`: the value.
- `$description`: what the value does, and what changes if the value goes up or down.
- `$unit`: the unit, if it is different from the unit of the group.

A request for a group or a value that does not exist MUST fail at the request, with the name.

## 3. Layers

1. Each module has a position in the layer order. The build file lists the order.
2. A module MUST use only the modules that come before it in the order.
3. If a module needs a function from a later module, the later module gives the function as a parameter.

## 4. Files and tests

1. A source module has a maximum of 300 lines.
2. One file has one responsibility.
3. A rule of behavior is one function with a name. All places that need the rule call the function.
4. Each change has a test that fails before the change and passes after the change.
5. If a change must not change a result, prove it. Record the outputs before the change, and compare them after the change.
6. Nobody edits a generated file by hand. Change the generator, then generate the file again.

## 5. Guards

A rule that only exists as text is forgotten. If a program can check a rule, a program MUST check the rule.

1. Each guard runs in the verification.
2. Each guard has at least one mutant: a small wrong change that the guard MUST detect. The verification proves that each guard detects its mutants.
3. If existing code breaks a rule, the guard records the count for each file as a ceiling.
4. The guard fails if a count goes above its ceiling.
5. The guard fails if a count goes below its ceiling. Then lower the ceiling with the command of the guard.
6. A ceiling only goes down.

## 6. Verification steps

The full verification runs these steps, in this order. Complete the commands for the project.

| Step | What it checks | Command |
| --- | --- | --- |
| Build | The application builds. | |
| Generated files | The generated files are current. | |
| Guards | Each rule of this file, with its ceilings. | |
| Guard mutants | Each guard detects its mutants. | |
| Tests | All unit tests pass. | |
| Audit | The application in a browser: screens, interaction, contrast, performance. | |
| No change | The steps did not change files that Git tracks. | |

The targeted verification runs all steps, but only the audit parts that the changed files touch (`METHOD.md` section 5).
