#!/usr/bin/env python3
"""Evaluations, stages, and generated files of the collector (CONTRIBUTING.md, sections 7 to 10).

Usage:
  python3 .github/scripts/evaluations.py --write                 Write each STATUS.md and the index in README.md.
  python3 .github/scripts/evaluations.py --check [--base <commit>]
      Fail if an evaluation file is not valid (with --base: only the files that base..HEAD adds), if a workflow is not
      in the stage folder that the evaluations give, if a generated file is not current, or if a file contains an email
      address.
Python standard library only.
"""
import datetime
import os
import re
import statistics
import subprocess
import sys
from math import ceil, floor

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip() or os.getcwd()
STAGES = ['Theorized', 'Evaluating', 'Tested', 'Rejected']
RANK = {'Theorized': 0, 'Evaluating': 1, 'Tested': 2}
SLUG = r'[a-z0-9]+(?:-[a-z0-9]+)*'
SCORE = r'(?:-2|-1|0|\+1|\+2)'
WORK_TYPES = ['build', 'extend', 'fix', 'refactor', 'mixed']
STATES = ['active', 'paused', 'finished', 'stopped', 'switched']
REPOSITORIES = ['public', 'private', 'none']   # where the project that used the workflow is: a Git repository that all can see, one with restricted access, or no Git
MIN_PROJECTS = 3        # counted evaluations (one per project) before a revision can pass or fail
MIN_OWNERS = 2          # different project owners for a pass
BEGIN, END = '<!-- BEGIN GENERATED: revisions -->', '<!-- END GENERATED: revisions -->'


def sentence(v):
    return v == 'none' or (v.endswith('.') and 1 <= len(v.split()) <= 25)


FIELDS = [   # name, test of the value, rule for the error message
    ('Revision', lambda v: re.fullmatch(r'\d{4}', v), 'four digits, for example 0001'),
    ('Date', lambda v: re.fullmatch(r'\d{4}-\d{2}-\d{2}', v) and datetime.date.fromisoformat(v), 'YYYY-MM-DD'),
    ('Agents', lambda v: v == 'none' or all(re.fullmatch(r'[a-z0-9][a-z0-9.-]* in [a-z0-9][a-z0-9.-]*', a) for a in v.split(', ')),
     '"<model-id> in <tool>", separated by ", ", or "none"'),
    ('Project owner', lambda v: re.fullmatch(SLUG, v) and len(v) <= 39, 'lowercase letters, digits, and hyphens'),
    ('Project', lambda v: re.fullmatch(SLUG, v) and len(v) <= 30, 'lowercase letters, digits, and hyphens'),
    ('Repository', lambda v: v in REPOSITORIES, ' | '.join(REPOSITORIES)),
    ('Work type', lambda v: v in WORK_TYPES, ' | '.join(WORK_TYPES)),
    ('Project state', lambda v: v in STATES, ' | '.join(STATES)),
    ('Active days', lambda v: re.fullmatch(r'[1-9]\d*', v), 'an integer, 1 or more'),
    ('Ease of use', lambda v: re.fullmatch(SCORE, v), '-2 | -1 | 0 | +1 | +2'),
    ('Goal contribution', lambda v: re.fullmatch(SCORE, v), '-2 | -1 | 0 | +1 | +2'),
    ('Overall effect', lambda v: re.fullmatch(SCORE, v), '-2 | -1 | 0 | +1 | +2'),
    ('Strength', sentence, 'one sentence of 1 to 25 words that ends with a period, or "none"'),
    ('Problem', sentence, 'one sentence of 1 to 25 words that ends with a period, or "none"'),
]
FILE_NAME = re.compile(rf'R(\d{{4}})_(\d{{4}}-\d{{2}}-\d{{2}})_({SLUG})_({SLUG})\.md')
ENTRY = re.compile(r'^Entry: Evaluating, decided by the owner on \d{4}-\d{2}-\d{2}: \S.*$', re.M)
REJECTION = re.compile(r'^Rejection: \d{4}-\d{2}-\d{2}: decided by the owner: \S.*$', re.M)


def parse(text, name, closed):
    """The fields of one evaluation file, or raise ValueError with the reason."""
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    if lines[:2] != ['# Evaluation', '']:
        raise ValueError('the first line must be "# Evaluation", and the second line must be empty')
    body = lines[2:]
    if len(body) != len(FIELDS):
        raise ValueError(f'{len(body)} field lines; the template has {len(FIELDS)}')
    out = {}
    for line, (field, test, rule) in zip(body, FIELDS):
        prefix = f'- {field}: '
        if not line.startswith(prefix):
            raise ValueError(f'expected "{prefix}<value>", found "{line}"')
        value = line[len(prefix):]
        try:
            ok = test(value)
        except ValueError:
            ok = False
        if not ok:
            raise ValueError(f'{field}: "{value}" is not valid; use {rule}')
        out[field] = value
    m = FILE_NAME.fullmatch(name)
    if not m or m.groups() != (out['Revision'], out['Date'], out['Project owner'], out['Project']):
        raise ValueError(f'the file name must be R{out["Revision"]}_{out["Date"]}_{out["Project owner"]}_{out["Project"]}.md')
    if out['Revision'] not in closed:
        raise ValueError(f'Revision_{out["Revision"]}_Closed does not exist in this target')
    return out


def score(v):
    return int(v)


def verdict(evals):
    """Passed, Failed, or Open for the counted evaluations of one Closed revision (CONTRIBUTING.md, section 9)."""
    n = len(evals)
    if n < MIN_PROJECTS:
        return 'Open'
    harm = sum(1 for e in evals if score(e['Overall effect']) <= -1 or e['Project state'] == 'switched')
    if harm > n / 2:
        return 'Failed'
    helped = sum(1 for e in evals if score(e['Overall effect']) >= 1)
    owners = len({e['Project owner'] for e in evals})
    if (helped >= ceil(2 * n / 3) and harm <= floor(n / 4) and owners >= MIN_OWNERS
            and statistics.median(score(e['Ease of use']) for e in evals) >= 0
            and statistics.median(score(e['Goal contribution']) for e in evals) >= 0):
        return 'Passed'
    return 'Open'


def scan():
    """The workflows of the repository, with their targets, revisions, and evaluations."""
    workflows = []
    for stage in STAGES:
        sdir = os.path.join(ROOT, f'{stage}_WorkFlow')
        if not os.path.isdir(sdir):
            continue
        for wname in sorted(os.listdir(sdir)):
            wdir = os.path.join(sdir, wname)
            if not (os.path.isdir(wdir) and wname.endswith('_WorkFlow')):
                continue
            readme = os.path.join(wdir, 'README.md')
            text = open(readme, encoding='utf-8').read() if os.path.isfile(readme) else ''
            wf = {'name': wname[:-len('_WorkFlow')], 'stage': stage, 'path': os.path.relpath(wdir, ROOT),
                  'entry': bool(ENTRY.search(text)), 'rejection': bool(REJECTION.search(text)), 'targets': []}
            for tname in sorted(os.listdir(wdir)):
                tdir = os.path.join(wdir, tname)
                if tname.startswith('.') or not os.path.isdir(tdir):
                    continue
                revs = {}
                for r in os.listdir(tdir):
                    m = re.fullmatch(r'Revision_(\d{4})_(Closed|Working)', r)
                    if m and os.path.isdir(os.path.join(tdir, r)):
                        revs.setdefault(m.group(1), []).append(m.group(2))
                closed = sorted(k for k, v in revs.items() if 'Closed' in v)
                edir = os.path.join(tdir, 'Evaluations')
                files = sorted(f for f in os.listdir(edir) if f.endswith('.md')) if os.path.isdir(edir) else []
                evals, invalid = [], []
                for f in files:
                    rel = os.path.relpath(os.path.join(edir, f), ROOT)
                    try:
                        evals.append({**parse(open(os.path.join(edir, f), encoding='utf-8').read(), f, closed), 'file': f, 'rel': rel})
                    except ValueError as e:
                        invalid.append((f, rel, str(e)))
                wf['targets'].append({'name': tname, 'path': os.path.relpath(tdir, ROOT), 'revs': revs, 'closed': closed,
                                      'evals': evals, 'invalid': invalid})
            workflows.append(wf)
    for wf in workflows:
        for t in wf['targets']:
            level_of_target(wf, t)
        level_of_workflow(wf)
    return workflows


def level_of_target(wf, t):
    latest = {}
    for e in sorted(t['evals'], key=lambda e: (e['Date'], e['file'])):
        latest[(e['Revision'], e['Project owner'], e['Project'])] = e   # one vote per project and revision: the newest file
    counted = set(id(e) for e in latest.values())
    t['superseded'] = [e for e in t['evals'] if id(e) not in counted]
    t['by_rev'] = {r: [e for e in latest.values() if e['Revision'] == r] for r in t['closed']}
    t['verdicts'] = {r: verdict(t['by_rev'][r]) for r in t['closed']}
    evidenced = [r for r in t['closed'] if len(t['by_rev'][r]) >= MIN_PROJECTS]
    if evidenced and t['verdicts'][evidenced[-1]] == 'Failed':
        t['level'], t['why'] = 'Rejected', f'revision {evidenced[-1]} failed, and it is the newest revision with evidence'
    elif any(v == 'Passed' for v in t['verdicts'].values()):
        t['level'], t['why'] = 'Tested', 'revision ' + ', '.join(r for r, v in t['verdicts'].items() if v == 'Passed') + ' passed'
    elif latest:
        t['level'], t['why'] = 'Evaluating', 'a project evaluated a Closed revision'
    elif wf['entry']:
        t['level'], t['why'] = 'Evaluating', 'the "Entry:" line of the owner in the workflow README'
    else:
        t['level'], t['why'] = 'Theorized', 'no evaluation of a Closed revision'


def level_of_workflow(wf):
    levels = [t['level'] for t in wf['targets']]
    if wf['rejection']:
        wf['level'], wf['why'] = 'Rejected', 'the "Rejection:" line of the owner in the workflow README'
    elif any(lv in RANK and lv != 'Theorized' for lv in levels):
        best = max((lv for lv in levels if lv in RANK), key=RANK.get)
        wf['level'], wf['why'] = best, 'the highest level of its targets'
    elif 'Rejected' in levels:
        wf['level'], wf['why'] = 'Rejected', 'each target with evidence failed'
    else:
        wf['level'], wf['why'] = 'Theorized', 'no target has a higher level'


def status_text(wf, t):
    out = [f'# Status: {wf["name"]} / {t["name"]}', '',
           'Generated by `python3 .github/scripts/evaluations.py --write`. Do not edit this file.',
           'The rules are in `CONTRIBUTING.md`, section 9.', '',
           f'- Stage folder: {wf["stage"]}',
           f'- Level of this target: {t["level"]} ({t["why"]})',
           f'- Stage that the rules give to the workflow: {wf["level"]} ({wf["why"]})', '',
           '## Closed revisions', '',
           '| Revision | Tag | Counted evaluations | Project owners | Overall effect +1 or +2 | Harm (-1, -2, or switched) '
           '| Median ease of use | Median goal contribution | Verdict |',
           '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in t['closed']:
        ev = t['by_rev'][r]
        med = lambda f: f'{statistics.median(score(e[f]) for e in ev):+g}' if ev else '—'
        harm = sum(1 for e in ev if score(e['Overall effect']) <= -1 or e['Project state'] == 'switched')
        out.append(f'| {r} | `{wf["name"]}/{t["name"]}/r{r}` | {len(ev)} | {len({e["Project owner"] for e in ev})} '
                   f'| {sum(1 for e in ev if score(e["Overall effect"]) >= 1)} | {harm} | {med("Ease of use")} '
                   f'| {med("Goal contribution")} | {t["verdicts"][r]} |')
    if not t['closed']:
        out.append('| — | — | 0 | 0 | 0 | 0 | — | — | — |')
    out += ['', '## Evaluations that do not count', '']
    rows = [f'- `{e["file"]}`: a newer evaluation of the same project and revision replaces it.' for e in t['superseded']]
    rows += [f'- `{f}`: not valid: {why}.' for f, _, why in t['invalid']]
    out += rows or ['None.']
    out += ['', '## Reports of harm', '']
    harmful = [e for evs in t['by_rev'].values() for e in evs if score(e['Overall effect']) <= -1 or e['Project state'] == 'switched']
    out += [f'- `{e["file"]}` ({e["Overall effect"]}, {e["Project state"]}): {e["Problem"]}' for e in harmful] or ['None.']
    return '\n'.join(out) + '\n'


def index_text(workflows):
    rows = ['| Revision ID (also the Git tag) | Status | Stage | Path | Counted evaluations | Verdict |',
            '| --- | --- | --- | --- | --- | --- |']
    for wf in workflows:
        for t in wf['targets']:
            for r in sorted(t['revs']):
                for status in sorted(t['revs'][r]):
                    ev = len(t['by_rev'].get(r, [])) if status == 'Closed' else '—'
                    v = t['verdicts'].get(r, '—') if status == 'Closed' else '—'
                    rows.append(f'| `{wf["name"]}/{t["name"]}/r{r}` | {status} | {wf["stage"]} '
                                f'| `{t["path"]}/Revision_{r}_{status}/` | {ev} | {v} |')
    if len(rows) == 2:
        rows.append('| — | — | — | — | — | — |')
    return '\n'.join(rows)


def generated(workflows):
    """{path: text} of each generated file."""
    out = {os.path.join(t['path'], 'STATUS.md'): status_text(wf, t) for wf in workflows for t in wf['targets']}
    readme = os.path.join(ROOT, 'README.md')
    text = open(readme, encoding='utf-8').read()
    a, b = text.index(BEGIN) + len(BEGIN), text.index(END)
    out['README.md'] = text[:a] + '\n' + index_text(workflows) + '\n' + text[b:]
    return out


def added_files(base):
    res = subprocess.run(['git', 'diff', '--name-status', '-M', base, 'HEAD'], capture_output=True, text=True, cwd=ROOT, check=True)
    return {line.split('\t')[1] for line in res.stdout.splitlines() if line.startswith('A\t')}


EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}')


def personal_data():
    """An email address in a tracked text file is personal information (CONTRIBUTING.md, section 3)."""
    files = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=ROOT, check=True).stdout.split('\n')
    errors = []
    for f in filter(None, files):
        try:
            text = open(os.path.join(ROOT, f), encoding='utf-8').read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for m in EMAIL.finditer(text):
            errors.append(f'{f}: contains the email address "{m.group(0)}". Remove it (CONTRIBUTING.md, section 3, "Privacy")')
    return errors


def check(workflows, base):
    errors = []
    added = added_files(base) if base else None
    names = {}
    for wf in workflows:
        names.setdefault(wf['name'], []).append(wf['stage'])
        if wf['stage'] != wf['level']:
            errors.append(f'{wf["path"]} is in {wf["stage"]}_WorkFlow, but the rules give {wf["level"]} ({wf["why"]}). '
                          f'Run: git mv {wf["path"]} {wf["level"]}_WorkFlow/{wf["name"]}_WorkFlow')
        for t in wf['targets']:
            working = [r for r, s in t['revs'].items() if 'Working' in s]
            if len(working) > 1:
                errors.append(f'{t["path"]} has {len(working)} Working revisions; the maximum is 1')
            for r, s in t['revs'].items():
                if len(s) > 1:
                    errors.append(f'{t["path"]}: revision {r} is Closed and Working; rename the Working folder (CONTRIBUTING.md, section 6)')
            for f, rel, why in t['invalid']:
                if added is None or rel in added:
                    errors.append(f'{rel}: {why}')
    errors += [f'the workflow {n} is in more than one stage: {", ".join(s)}' for n, s in names.items() if len(s) > 1]
    errors += personal_data()
    for path, text in generated(workflows).items():
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full) or open(full, encoding='utf-8').read() != text:
            errors.append(f'{path} is not current. Run: python3 .github/scripts/evaluations.py --write')
    return errors


def main(argv):
    workflows = scan()
    if '--write' in argv:
        for path, text in generated(workflows).items():
            with open(os.path.join(ROOT, path), 'w', encoding='utf-8') as fh:
                fh.write(text)
        print('Written: each STATUS.md and the index in README.md.')
        return 0
    if '--check' in argv:
        base = argv[argv.index('--base') + 1] if '--base' in argv else None
        errors = check(workflows, base)
        for e in errors:
            print(f'ERROR: {e}')
        print(f'{len(errors)} error(s).' if errors else 'OK: evaluations, stages, and generated files are correct.')
        return 1 if errors else 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
