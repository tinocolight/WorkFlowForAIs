# Template: evaluation

Copy the block below into `<Target>/Evaluations/R<NNNN>_<YYYY-MM-DD>_<project-owner>_<project>.md`.
Keep the order of the lines. Do not add lines. Replace each value. The program refuses other values.

```
# Evaluation

- Revision: 0001
- Date: 2026-10-12
- Agents: claude-opus-5-5 in claude-code
- Project owner: tinocolight
- Project: consonancia
- Work type: extend
- Project state: active
- Active days: 30
- Ease of use: +1
- Goal contribution: +1
- Overall effect: +1
- Strength: A new session continued the work from the files with no help.
- Problem: none
```

## Field rules

| Field | Allowed values |
| --- | --- |
| Revision | The four digits of a Closed revision of the target. |
| Date | The date that you write the file: YYYY-MM-DD. |
| Agents | Each AI that used the workflow, as `<model-id> in <tool>`, separated by `, `. Use the model ID of the provider API. Write `none` if no AI used it. |
| Project owner | The account or the name of the owner of the project: lowercase letters, digits, and hyphens. |
| Project | The name of the project: lowercase letters, digits, and hyphens. Use the same value in each evaluation of the project. |
| Work type | `build`: a new project. `extend`: new functions in an existing project. `fix`: corrections. `refactor`: a new structure, with no change in behavior. `mixed`: no type is more than half of the work. |
| Project state | `active`: work in the last 30 days. `paused`: no work for 30 days or more. `finished`: the project reached its goal. `stopped`: the project ended before its goal. `switched`: the project continues without this workflow. |
| Active days | The count of different dates with a commit since the project started to use the revision. Command: `git log --since=<start-date> --format=%ad --date=short \| sort -u \| wc -l`. |
| Ease of use | `-2`: the agents could not follow the files. `-1`: many errors or questions. `0`: some errors or questions. `+1`: few errors or questions. `+2`: no error and no question. |
| Goal contribution | How much the workflow helped the project to reach its goal. `-2`: it prevented progress. `-1`: it slowed progress. `0`: no effect. `+1`: it helped. `+2`: it was necessary for the progress. |
| Overall effect | The net effect, with all costs (time, tokens, errors), compared with your usual way of work. `-2`: much worse. `-1`: worse. `0`: the same. `+1`: better. `+2`: much better. |
| Strength | One sentence of 1 to 25 words that ends with a period, or `none`. |
| Problem | One sentence of 1 to 25 words that ends with a period, or `none`. |
