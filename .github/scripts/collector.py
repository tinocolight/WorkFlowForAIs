#!/usr/bin/env python3
"""collector — the rules of the collector in one program (CONTRIBUTING.md, sections 6 to 12). Python standard library only.

Usage:
  python3 .github/scripts/collector.py --check [--base <commit>] [--author <login>] [--owner <login>] [--labels <a,b>]
      Fail if a pull request breaks a rule: a changed revision or evaluation, a file that is not valid, a new revision
      that does not follow section 6, hidden characters, or an email address. Without --base, only the files are checked.
  python3 .github/scripts/collector.py --write
      Write each STATUS.md and the index in README.md. GitHub Actions runs it after each merge (section 12).
  python3 .github/scripts/collector.py --json
      Print the computed model: workflows, targets, revisions, roles, and evaluations.
"""
import datetime
import json
import os
import re
import statistics
import subprocess
import sys
import unicodedata
from math import ceil, floor

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip() or os.getcwd()
WORKFLOWS = 'Workflows'
MIN_PROJECTS = 3       # counted evaluations (one for each project) before a revision can pass or fail
MIN_OWNERS = 2         # different project owners for a pass
MAX_CANDIDATES = 3     # open revisions with no newer revision, for each target
DORMANT_DAYS = 180     # an open revision with too few evaluations after this many days is dormant
SLUG = r'[a-z0-9]+(?:-[a-z0-9]+)*'
SCORE = r'(?:-2|-1|0|\+1|\+2)'
WORK_TYPES = ['build', 'extend', 'fix', 'refactor', 'mixed']
STATES = ['active', 'paused', 'finished', 'stopped', 'switched']
REPOSITORIES = ['public', 'private', 'none']
YANK_REASONS = ['broken', 'regression', 'harmful']
STAGE_RANK = {'Theorized': 0, 'Evaluating': 1, 'Tested': 2}
BEGIN, END = '<!-- BEGIN GENERATED: revisions -->', '<!-- END GENERATED: revisions -->'

# Style: practices that a workflow declares with "yes" or "no". A line that a new revision adds, and that looks like a
# practice the workflow declares "no", fails the check (section 6). It is a tripwire, not a proof.
STYLE = [
    ('Pushes directly to main', r'\bpush\b[^\n]*\b(main|master)\b'),
    ('Uses force push', r'--force\b|\bpush -f\b|\bforce[- ]push'),
    ('Skips or disables tests', r"\b(skip|disable|omit|without|don't run|do not run)\b[^\n]{0,40}\btests?\b"),
    ('Installs from the network', r'\b(curl|wget)\b[^\n]*\|\s*(ba|z)?sh\b|\bpip install\b|\bnpm (i|install)\b|\bnpx\b'),
    ('Bypasses permission prompts', r'dangerously|bypass[- ]?permissions|--yolo|skip[- ]permissions|auto[- ]approve'),
    ('Deletes files outside the project', r'\brm\s+-[a-z]*r[a-z]*f?\s+(/|~|\$HOME)'),
    ('Sends data to external services', r'\b(api[_ -]?key|secret|token|password|\.env)\b[^\n]{0,60}\b(send|post|upload|share|curl|webhook)\b'),
]
NEGATION = re.compile(r"\b(MUST NOT|SHOULD NOT|do not|don't|never|not)\b", re.I)
INVARIANT = re.compile(r'\[(V\d+)\]')
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}')
REV_DIR = re.compile(r'r(\d{4})')


def sentence(v):
    return v == 'none' or (v.endswith('.') and 1 <= len(v.split()) <= 25)


FIELDS = [   # name, test of the value, rule for the error message
    ('Revision', lambda v: re.fullmatch(r'\d{4}', v), 'four digits, for example 0001'),
    ('Date', lambda v: re.fullmatch(r'\d{4}-\d{2}-\d{2}', v) and datetime.date.fromisoformat(v), 'YYYY-MM-DD'),
    ('Agents', lambda v: v == 'none' or all(re.fullmatch(r'[a-z0-9][a-z0-9.-]* in [a-z0-9][a-z0-9.-]*', a) for a in v.split(', ')),
     '"<model-id> in <tool>", separated by ", ", or "none"'),
    ('Project owner', lambda v: re.fullmatch(SLUG, v) and len(v) <= 39, 'your Git account name in lowercase'),
    ('Project', lambda v: re.fullmatch(SLUG, v) and len(v) <= 30, 'lowercase letters, digits, and hyphens'),
    ('Repository', lambda v: v in REPOSITORIES, ' | '.join(REPOSITORIES)),
    ('Work type', lambda v: v in WORK_TYPES, ' | '.join(WORK_TYPES)),
    ('Project state', lambda v: v in STATES, ' | '.join(STATES)),
    ('Active days', lambda v: re.fullmatch(r'[1-9]\d*', v), 'an integer, 1 or more'),
    ('Ease of use', lambda v: re.fullmatch(SCORE, v), '-2 | -1 | 0 | +1 | +2'),
    ('Goal contribution', lambda v: re.fullmatch(SCORE, v), '-2 | -1 | 0 | +1 | +2'),
    ('Overall effect', lambda v: re.fullmatch(SCORE, v), '-2 | -1 | 0 | +1 | +2'),
    ('Compared with previous revision', lambda v: v == 'none' or re.fullmatch(SCORE, v), '-2 | -1 | 0 | +1 | +2 | none'),
    ('Strength', sentence, 'one sentence of 1 to 25 words that ends with a period, or "none"'),
    ('Problem', sentence, 'one sentence of 1 to 25 words that ends with a period, or "none"'),
]
FILE_NAME = re.compile(rf'R(\d{{4}})_(\d{{4}}-\d{{2}}-\d{{2}})_({SLUG})_({SLUG})\.md')
ENTRY = re.compile(r'^Entry: Evaluating, decided by the owner on \d{4}-\d{2}-\d{2}: \S.*$', re.M)
REJECTION = re.compile(r'^Rejection: \d{4}-\d{2}-\d{2}: decided by the owner: \S.*$', re.M)
BASED_ON = re.compile(r'^Based on: (none|r\d{4}(?:, r\d{4})*)$', re.M)
AUTHOR = re.compile(r'^Author: (\S+)$', re.M)
LEGACY_ORIGIN = re.compile(r'^Origin: a copy of `Revision_(\d{4})_Closed/`', re.M)
YANK_LINE = re.compile(rf'^- r(\d{{4}}): (\d{{4}}-\d{{2}}-\d{{2}}): ({"|".join(YANK_REASONS)}): (\S.*)$')

# The identity of a protected path, in the old layout (stage folders, until October 2026) and in the new one.
ID_RULES = [
    (re.compile(r'^[A-Za-z]+_WorkFlow/([^/]+)_WorkFlow/([^/]+)/Revision_(\d{4})_Closed$'), 'rev'),
    (re.compile(rf'^{WORKFLOWS}/([^/]+)/([^/]+)/r(\d{{4}})$'), 'rev'),
    (re.compile(r'^[A-Za-z]+_WorkFlow/([^/]+)_WorkFlow/([^/]+)/Evaluations/([^/]+\.md)$'), 'eval'),
    (re.compile(rf'^{WORKFLOWS}/([^/]+)/([^/]+)/Evaluations/([^/]+\.md)$'), 'eval'),
]


def git(*args, check=True):
    return subprocess.run(['git', *args], capture_output=True, text=True, cwd=ROOT, check=check).stdout


def read(path):
    full = os.path.join(ROOT, path)
    return open(full, encoding='utf-8').read() if os.path.isfile(full) else ''


def score(v):
    return int(v)


def median(values):
    values = list(values)
    return statistics.median(values) if values else None


# ---------- reading the repository ----------

def parse_evaluation(text, name, numbers):
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
    if out['Revision'] not in numbers:
        raise ValueError(f'revision r{out["Revision"]} does not exist in this target')
    return out


def style_of(readme):
    """{practice: True or False} from the "## Style" table of a workflow README. A practice that is not declared is False."""
    declared = {}
    for label, _ in STYLE:
        m = re.search(rf'^\| {re.escape(label)} \| (yes|no) \|$', readme, re.M)
        declared[label] = (m.group(1) == 'yes') if m else None
    return declared


def first_added(path):
    out = git('log', '--diff-filter=A', '--follow', '--format=%cs', '--', path, check=False).split()
    return out[-1] if out else None


def head_date():
    return git('log', '-1', '--format=%cs', 'HEAD', check=False).strip() or datetime.date.today().isoformat()


def scan():
    """The workflows in Workflows/, with their targets, revisions, evaluations, and computed roles."""
    today = datetime.date.fromisoformat(head_date())
    workflows = []
    base_dir = os.path.join(ROOT, WORKFLOWS)
    for wname in sorted(os.listdir(base_dir)) if os.path.isdir(base_dir) else []:
        wpath = f'{WORKFLOWS}/{wname}'
        if not os.path.isdir(os.path.join(ROOT, wpath)):
            continue
        readme = read(f'{wpath}/README.md')
        wf = {'name': wname, 'path': wpath, 'entry': bool(ENTRY.search(readme)), 'rejection': bool(REJECTION.search(readme)),
              'style': style_of(readme), 'targets': []}
        for tname in sorted(os.listdir(os.path.join(ROOT, wpath))):
            tpath = f'{wpath}/{tname}'
            if tname.startswith('.') or not os.path.isdir(os.path.join(ROOT, tpath)):
                continue
            t = {'name': tname, 'path': tpath, 'revisions': {}, 'evals': [], 'invalid': [], 'yanks': {}, 'yank_errors': []}
            for r in sorted(os.listdir(os.path.join(ROOT, tpath))):
                m = REV_DIR.fullmatch(r)
                if m and os.path.isdir(os.path.join(ROOT, tpath, r)):
                    t['revisions'][m.group(1)] = revision(wf, t, m.group(1))
            numbers = set(t['revisions'])
            edir = os.path.join(ROOT, tpath, 'Evaluations')
            for f in sorted(os.listdir(edir)) if os.path.isdir(edir) else []:
                if not f.endswith('.md'):
                    continue
                rel = f'{tpath}/Evaluations/{f}'
                try:
                    t['evals'].append({**parse_evaluation(read(rel), f, numbers), 'file': f, 'rel': rel})
                except ValueError as e:
                    t['invalid'].append((f, rel, str(e)))
            for n, line in enumerate(read(f'{tpath}/YANKED.md').split('\n')):
                if line.startswith('- '):
                    m = YANK_LINE.match(line)
                    if m and m.group(1) in numbers:
                        t['yanks'][m.group(1)] = {'date': m.group(2), 'reason': m.group(3), 'text': m.group(4)}
                    else:
                        t['yank_errors'].append(f'{tpath}/YANKED.md, line {n + 1}: use "- rNNNN: YYYY-MM-DD: '
                                                f'{"|".join(YANK_REASONS)}: <reason>" with an existing revision')
            compute_target(wf, t, today)
            wf['targets'].append(t)
        compute_workflow(wf)
        workflows.append(wf)
    return workflows


def revision(wf, t, number):
    path = f'{t["path"]}/r{number}'
    text = read(f'{path}/README.md')
    m = BASED_ON.search(text)
    if m:
        bases = [] if m.group(1) == 'none' else [b[1:] for b in m.group(1).split(', ')]
    else:   # revisions from before October 2026: the "Origin:" line, or the previous number
        legacy = LEGACY_ORIGIN.search(text)
        bases = [legacy.group(1)] if legacy else ([f'{int(number) - 1:04d}'] if int(number) > 1 else [])
    a = AUTHOR.search(text)
    return {'number': number, 'id': f'{wf["name"]}/{t["name"]}/r{number}', 'path': path, 'bases': bases,
            'author': a.group(1).lower() if a else None, 'added': first_added(f'{path}/README.md'),
            'has_based_on': bool(m), 'readme': text}


def verdict(evals):
    """Passed, Failed, or Open for the counted evaluations of one revision (section 9)."""
    n = len(evals)
    if n < MIN_PROJECTS:
        return 'Open'
    harm = sum(1 for e in evals if score(e['Overall effect']) <= -1 or e['Project state'] == 'switched')
    if harm > n / 2:
        return 'Failed'
    helped = sum(1 for e in evals if score(e['Overall effect']) >= 1)
    if (helped >= ceil(2 * n / 3) and harm <= floor(n / 4) and len({e['Project owner'] for e in evals}) >= MIN_OWNERS
            and median(score(e['Ease of use']) for e in evals) >= 0 and median(score(e['Goal contribution']) for e in evals) >= 0):
        return 'Passed'
    return 'Open'


def regression(evals):
    """True if three or more projects that compared it with the previous revision say, in the median, that it is worse."""
    compared = [score(e['Compared with previous revision']) for e in evals if e['Compared with previous revision'] != 'none']
    return len(compared) >= MIN_PROJECTS and median(compared) <= -1


def compute_target(wf, t, today):
    revs = t['revisions']
    latest = {}
    for e in sorted(t['evals'], key=lambda e: (e['Date'], e['file'])):
        latest[(e['Revision'], e['Project owner'], e['Project'])] = e     # one vote for each project and revision
    t['not_counted'] = [(e, 'a newer evaluation of the same project replaces it') for e in t['evals'] if e is not latest.get((e['Revision'], e['Project owner'], e['Project']))]
    counted = []
    for e in latest.values():
        if revs[e['Revision']]['author'] and e['Project owner'] == revs[e['Revision']]['author']:
            t['not_counted'].append((e, 'the author of a revision does not evaluate it'))
        else:
            counted.append(e)
    children = {n: [] for n in revs}
    for n, r in revs.items():
        for b in r['bases']:
            if b in children:
                children[b].append(n)
    for n, r in revs.items():
        r['counted'] = [e for e in counted if e['Revision'] == n]
        r['verdict'] = verdict(r['counted'])
        r['regression'] = regression(r['counted'])
        r['children'] = children[n]
        y = t['yanks'].get(n)
        r['yank'] = y or ({'reason': 'broken', 'text': 'the verdict is Failed'} if r['verdict'] == 'Failed'
                          else {'reason': 'regression', 'text': 'projects report that it is worse than the previous revision'} if r['regression'] else None)

    def has_yanked_ancestor(n, seen=()):
        return any(revs[b]['yank'] or has_yanked_ancestor(b, seen + (n,)) for b in revs[n]['bases'] if b in revs and b not in seen)

    for n, r in revs.items():
        age = (today - datetime.date.fromisoformat(r['added'])).days if r['added'] else 0
        if r['yank']:
            r['role'] = 'yanked'
        elif r['verdict'] != 'Passed' and has_yanked_ancestor(n):
            r['role'] = 'tainted'
        elif r['verdict'] == 'Passed':
            r['role'] = 'passed'
        elif r['children']:
            r['role'] = 'superseded'
        elif age > DORMANT_DAYS and len(r['counted']) < MIN_PROJECTS:
            r['role'] = 'dormant'
        else:
            r['role'] = 'candidate'
    passed = sorted(n for n, r in revs.items() if r['role'] == 'passed')
    if passed:
        revs[passed[-1]]['role'] = 'recommended'
    candidates = sorted(n for n, r in revs.items() if r['role'] == 'candidate')
    t['recommended'] = passed[-1] if passed else None
    t['base_for_new'] = passed[-1] if passed else (candidates[-1] if candidates else None)
    t['candidates'] = candidates
    t['counted'] = counted
    if passed:
        t['stage'], t['why'] = 'Tested', f'revision r{passed[-1]} passed'
    elif counted:
        t['stage'], t['why'] = 'Evaluating', 'a project evaluated a revision'
    elif wf['entry']:
        t['stage'], t['why'] = 'Evaluating', 'the "Entry:" line of the owner in the workflow README'
    else:
        t['stage'], t['why'] = 'Theorized', 'no project evaluated a revision'


def compute_workflow(wf):
    if wf['rejection']:
        wf['stage'], wf['why'] = 'Rejected', 'the "Rejection:" line of the owner in the workflow README'
    elif wf['targets']:
        best = max(wf['targets'], key=lambda t: STAGE_RANK[t['stage']])
        wf['stage'], wf['why'] = best['stage'], f'the highest stage of its targets ({best["name"]})'
    else:
        wf['stage'], wf['why'] = ('Evaluating', 'the "Entry:" line of the owner') if wf['entry'] else ('Theorized', 'no target')


# ---------- generated files ----------

def fmt(v):
    return '—' if v is None else f'{v:+g}'


def status_text(wf, t):
    out = [f'# Status: {wf["name"]} / {t["name"]}', '',
           'Generated after each merge by `.github/workflows/after-merge.yml`. Do not edit this file.',
           'The rules are in `CONTRIBUTING.md`, section 9.', '',
           f'- Stage of this target: {t["stage"]} ({t["why"]})',
           f'- Stage of the workflow: {wf["stage"]} ({wf["why"]})',
           f'- Recommended for new projects: {"r" + t["recommended"] if t["recommended"] else "none (no revision passed)"}',
           f'- Base for new revisions: {"r" + t["base_for_new"] if t["base_for_new"] else "none"}',
           f'- Open candidates: {len(t["candidates"])} of {MAX_CANDIDATES}', '',
           '## Revisions', '',
           '| Revision | Based on | Author | Added | Counted evaluations | Project owners | Help | Harm | Median ease of use '
           '| Median goal contribution | Median compared with previous | Verdict | Role |',
           '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for n in sorted(t['revisions'], reverse=True):
        r = t['revisions'][n]
        ev = r['counted']
        cmp = [score(e['Compared with previous revision']) for e in ev if e['Compared with previous revision'] != 'none']
        out.append(f'| r{n} | {", ".join("r" + b for b in r["bases"]) or "none"} | {r["author"] or "—"} | {r["added"] or "—"} '
                   f'| {len(ev)} | {len({e["Project owner"] for e in ev})} | {sum(1 for e in ev if score(e["Overall effect"]) >= 1)} '
                   f'| {sum(1 for e in ev if score(e["Overall effect"]) <= -1 or e["Project state"] == "switched")} '
                   f'| {fmt(median(score(e["Ease of use"]) for e in ev))} | {fmt(median(score(e["Goal contribution"]) for e in ev))} '
                   f'| {fmt(median(cmp))} | {r["verdict"]} | {r["role"]} |')
    out += ['', '## Yanked revisions', '']
    out += [f'- r{n}: {r["yank"]["reason"]}: {r["yank"]["text"]}' for n, r in sorted(t['revisions'].items()) if r['yank']] or ['None.']
    out += ['', '## Evaluations that do not count', '']
    rows = [f'- `{e["file"]}`: {why}.' for e, why in t['not_counted']] + [f'- `{f}`: not valid: {why}.' for f, _, why in t['invalid']]
    out += rows or ['None.']
    out += ['', '## Reports of harm', '']
    harmful = [e for e in t['counted'] if score(e['Overall effect']) <= -1 or e['Project state'] == 'switched']
    out += [f'- `{e["file"]}` ({e["Overall effect"]}, {e["Project state"]}): {e["Problem"]}' for e in harmful] or ['None.']
    return '\n'.join(out) + '\n'


def index_text(workflows):
    rows = ['| Revision ID (also the Git tag) | Workflow stage | Role | Verdict | Counted evaluations | Path |',
            '| --- | --- | --- | --- | --- | --- |']
    for wf in workflows:
        for t in wf['targets']:
            for n in sorted(t['revisions'], reverse=True):
                r = t['revisions'][n]
                rows.append(f'| `{r["id"]}` | {wf["stage"]} | {r["role"]} | {r["verdict"]} | {len(r["counted"])} | `{r["path"]}/` |')
    if len(rows) == 2:
        rows.append('| — | — | — | — | — | — |')
    return '\n'.join(rows)


def generated(workflows):
    out = {f'{t["path"]}/STATUS.md': status_text(wf, t) for wf in workflows for t in wf['targets']}
    text = read('README.md')
    if BEGIN in text and END in text:
        a, b = text.index(BEGIN) + len(BEGIN), text.index(END)
        out['README.md'] = text[:a] + '\n' + index_text(workflows) + '\n' + text[b:]
    return out


def model(workflows):
    keep = ('number', 'id', 'path', 'bases', 'author', 'added', 'verdict', 'role', 'yank')
    return [{'name': wf['name'], 'path': wf['path'], 'stage': wf['stage'], 'targets': [
        {'name': t['name'], 'path': t['path'], 'stage': t['stage'], 'recommended': t['recommended'],
         'revisions': [{k: r[k] for k in keep} | {'counted': len(r['counted'])} for r in t['revisions'].values()]}
        for t in wf['targets']]} for wf in workflows]


# ---------- checks ----------

def identity(path):
    for rx, kind in ID_RULES:
        m = rx.match(path)
        if m:
            return f'{kind}:{m.group(1)}/{m.group(2)}/{m.group(3)}'
    return None


def protected(ref):
    """{identity: (path, object)} of each revision folder and evaluation file in a commit."""
    out = {}
    for line in git('ls-tree', '-r', '-t', ref).splitlines():
        meta, path = line.split('\t', 1)
        ident = identity(path)
        if ident:
            out[ident] = (path, meta.split()[2])
    return out


def check_immutable(base):
    before, now = protected(base), protected('HEAD')
    errors = []
    for ident, (path, obj) in before.items():
        if ident not in now:
            errors.append(f'{path} was deleted. Revisions and evaluations never change (section 6).')
        elif now[ident][1] != obj:
            errors.append(f'{now[ident][0]} changed. Revisions and evaluations never change: add a new revision or a new evaluation.')
    for path in git('ls-tree', '-r', '--name-only', base).splitlines():
        if path.endswith('/YANKED.md') and path.startswith(f'{WORKFLOWS}/'):
            old, new = git('show', f'{base}:{path}'), read(path)
            if not new.startswith(old):
                errors.append(f'{path}: lines can only be added at the end (section 10).')
    return errors, before


def kit_files(path):
    out = {}
    kit = os.path.join(ROOT, path, 'kit')
    for base, _, files in os.walk(kit):
        for f in files:
            full = os.path.join(base, f)
            try:
                out[os.path.relpath(full, kit)] = open(full, encoding='utf-8').read()
            except UnicodeDecodeError:
                out[os.path.relpath(full, kit)] = ''
    return out


def invariants(files):
    found = {}
    for text in files.values():
        for line in text.split('\n'):
            for vid in INVARIANT.findall(line):
                found[vid] = ' '.join(line.split())
    return found


def check_new_revisions(workflows, before, author, owner, labels):
    errors = []
    for wf in workflows:
        for t in wf['targets']:
            old_numbers = [ident.rsplit('/', 1)[1] for ident in before if ident.startswith(f'rev:{wf["name"]}/{t["name"]}/')]
            for n, r in t['revisions'].items():
                if f'rev:{r["id"].replace("/r" + n, "/" + n)}' in before:
                    continue
                where = r['path']
                if old_numbers and int(n) <= max(int(x) for x in old_numbers):
                    errors.append(f'{where}: the number must be higher than r{max(old_numbers)}. Rename the folder (section 6).')
                if not r['has_based_on']:
                    errors.append(f'{where}/README.md: add the line "Based on: rNNNN" (or "Based on: none" for a first revision).')
                for b in r['bases']:
                    if b not in t['revisions']:
                        errors.append(f'{where}/README.md: "Based on" names r{b}, which does not exist.')
                    elif t['revisions'][b]['role'] in ('yanked', 'tainted') and f'Reverts: r{b}' not in r['readme']:
                        errors.append(f'{where}: its base r{b} is {t["revisions"][b]["role"]}. Use a different base, or add the line "Reverts: r{b}" with the reason.')
                if not r['author']:
                    errors.append(f'{where}/README.md: add the line "Author: <your Git account name>".')
                elif author and author.lower() != (owner or '').lower() and r['author'] != author.lower():
                    errors.append(f'{where}/README.md: "Author: {r["author"]}" is not the author of the pull request ({author}).')
                if not os.path.isdir(os.path.join(ROOT, where, 'kit')):
                    errors.append(f'{where}: the revision has no kit/ folder.')
                new_kit = kit_files(where)
                for name, text in new_kit.items():
                    for m in re.finditer(r'^Workflow revision: (\S+)$', text, re.M):
                        if m.group(1) != r['id']:
                            errors.append(f'{where}/kit/{name}: "Workflow revision: {m.group(1)}" must be "{r["id"]}".')
                base_kit = kit_files(t['revisions'][r['bases'][0]]['path']) if r['bases'] and r['bases'][0] in t['revisions'] else {}
                old_inv, new_inv = invariants(base_kit), invariants(new_kit)
                if 'invariant-change' not in labels:
                    for vid, line in old_inv.items():
                        if vid not in new_inv:
                            errors.append(f'{where}: the protected rule [{vid}] of r{r["bases"][0]} was removed. The owner must add the label "invariant-change" (section 6).')
                        elif new_inv[vid] != line:
                            errors.append(f'{where}: the protected rule [{vid}] changed. The owner must add the label "invariant-change" (section 6).')
                old_lines = {line.strip() for text in base_kit.values() for line in text.split('\n')}
                for name, text in new_kit.items():
                    for line in text.split('\n'):
                        if not line.strip() or line.strip() in old_lines or NEGATION.search(line):
                            continue
                        for label, rx in STYLE:
                            if wf['style'][label] is not True and re.search(rx, line, re.I):
                                errors.append(f'{where}/kit/{name}: the new line "{line.strip()[:80]}" looks like "{label}", but the '
                                              f'Style table of the workflow says "{"no" if wf["style"][label] is False else "not declared"}". '
                                              'Change the line, or declare the practice (section 5).')
            if len(t['candidates']) > MAX_CANDIDATES:
                errors.append(f'{t["path"]}: {len(t["candidates"])} open candidates; the maximum is {MAX_CANDIDATES}. Evaluate the '
                              'existing candidates first, or create a derived workflow (section 11).')
    return errors


def check_text_files():
    errors = []
    for f in filter(None, git('ls-files').split('\n')):
        try:
            text = open(os.path.join(ROOT, f), encoding='utf-8').read()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        for m in EMAIL.finditer(text):
            if m.group(0).endswith('@users.noreply.github.com'):
                continue   # the address of the GitHub Actions bot is not personal information
            errors.append(f'{f}: contains the email address "{m.group(0)}". Remove it (section 3, "Privacy").')
        for i, ch in enumerate(text):
            cat = unicodedata.category(ch)
            hidden = (cat in ('Cf', 'Co', 'Cn', 'Cs') or (cat == 'Cc' and ch not in '\t\n\r')
                      or (cat == 'Zs' and ch not in '  ') or 0xFE00 <= ord(ch) <= 0xFE0F or 0xE0100 <= ord(ch) <= 0xE01EF)
            if hidden:
                line = text.count('\n', 0, i) + 1
                errors.append(f'{f}, line {line}: hidden character U+{ord(ch):04X} ({unicodedata.name(ch, "no name")}). Remove it (section 12).')
                break
    return errors


def check(workflows, base, author, owner, labels):
    errors = []
    for wf in workflows:
        missing = [label for label in wf['style'] if wf['style'][label] is None]
        if missing:
            errors.append(f'{wf["path"]}/README.md: the Style table must declare "yes" or "no" for: {", ".join(missing)} (section 5).')
        for t in wf['targets']:
            errors += t['yank_errors']
    added = None
    if base:
        imm, before = check_immutable(base)
        errors += imm
        errors += check_new_revisions(workflows, before, author, owner, labels)
        added = {line.split('\t')[1] for line in git('diff', '--name-status', '--no-renames', base, 'HEAD').splitlines() if line.startswith('A\t')}
        evaluators = set()
        for wf in workflows:
            for t in wf['targets']:
                for e in t['evals']:
                    if e['rel'] in added:
                        evaluators.add(e['Project owner'])
                        if author and author.lower() != (owner or '').lower() and e['Project owner'] != author.lower():
                            errors.append(f'{e["rel"]}: "Project owner: {e["Project owner"]}" must be your Git account name ({author.lower()}) (section 8).')
        if len(evaluators) > 1 and author and author.lower() != (owner or '').lower():
            errors.append(f'One pull request adds evaluations of one project owner only; found: {", ".join(sorted(evaluators))} (section 8).')
    for wf in workflows:
        for t in wf['targets']:
            for f, rel, why in t['invalid']:
                if added is None or rel in added:
                    errors.append(f'{rel}: {why}')
    errors += check_text_files()
    return errors


def main(argv):
    opt = lambda name: argv[argv.index(name) + 1] if name in argv else None
    workflows = scan()
    if '--write' in argv:
        for path, text in generated(workflows).items():
            with open(os.path.join(ROOT, path), 'w', encoding='utf-8') as fh:
                fh.write(text)
        print('Written: each STATUS.md and the index in README.md.')
        return 0
    if '--json' in argv:
        print(json.dumps(model(workflows), indent=1))
        return 0
    if '--check' in argv:
        labels = set(filter(None, (opt('--labels') or '').split(',')))
        errors = check(workflows, opt('--base'), opt('--author'), opt('--owner'), labels)
        for e in errors:
            print(f'ERROR: {e}')
        print(f'{len(errors)} error(s).' if errors else 'OK: all the rules of the collector pass.')
        return 1 if errors else 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
