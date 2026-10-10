/* WorkFlowForAIs page. It reads the repository on GitHub when it opens: nothing about the workflows is written here.
   - What exists: the Git tree of the default branch (one GitHub API request), with the folder names as the only source.
   - Evaluations: the files in <Target>/Evaluations/, read as "- Field: value" lines.
   - Verdicts and levels: the STATUS.md of each target, which .github/scripts/evaluations.py generates (one set of rules).
   - Downloads: a zip built in the browser from the files of the revision, at the same commit.
   The repository comes from the address (<owner>.github.io/<repo>/) or from ?repo=<owner>/<repo>. */
'use strict';

const app = document.getElementById('app');
const SCORES = ['+2', '+1', '0', '-1', '-2'];
const SCORE_LABEL = { '+2': 'Much better', '+1': 'Better', '0': 'The same', '-1': 'Worse', '-2': 'Much worse' };
const PRIOR_VOTES = 3; // the score counts this many neutral votes (5.0) in addition to the real ones
const ROOT_DIR = 'Workflows';
const REVISION_DIR = /^r(\d{4})$/;
let REPO = null;
let SHA = null;
let DATA = null;

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const enc = (path) => path.split('/').map(encodeURIComponent).join('/');
const repoUrl = (path = '') => `https://github.com/${REPO}${path}`;
const treeUrl = (path) => repoUrl(`/tree/${SHA}/${enc(path)}`);
const raw = (path) => fetch(`https://raw.githubusercontent.com/${REPO}/${SHA}/${enc(path)}`).then((r) => {
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.text();
});

function repository() {
  const asked = new URLSearchParams(location.search).get('repo');
  if (asked && /^[\w.-]+\/[\w.-]+$/.test(asked)) return asked;
  const m = location.hostname.match(/^([\w-]+)\.github\.io$/i);
  const first = location.pathname.split('/').filter(Boolean)[0];
  return m && first ? `${m[1]}/${first}` : null;
}

async function api(path) {
  const r = await fetch(`https://api.github.com/repos/${REPO}${path}`, { headers: { Accept: 'application/vnd.github+json' } });
  if (!r.ok) throw new Error(`GitHub API ${path}: HTTP ${r.status}`);
  return r.json();
}

/* ---------- reading the repository ---------- */

function parseFields(text) {
  const fields = {};
  for (const line of text.split('\n')) {
    const m = line.match(/^- ([^:]+): (.*)$/);
    if (m) fields[m[1]] = m[2].trim();
  }
  return fields;
}

function summary(text) {
  const lines = text.split('\n').slice(1);
  const out = [];
  for (const line of lines) {
    if (line.startsWith('#')) { if (out.length) break; continue; }
    if (/^(Entry|Rejection): /.test(line)) continue;
    if (line.trim()) out.push(line.trim());
    else if (out.length) break;
  }
  return out.join(' ');
}

function parseStatus(text) {
  const line = (label) => (text.match(new RegExp(`^- ${label}: (\\w+)`, 'm')) || [])[1] || null;
  const revisions = {};
  for (const m of text.matchAll(/^\| r(\d{4}) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|.*\| (\w+) \| (\w+) \|$/gm)) {
    revisions[m[1]] = { basedOn: m[2].trim(), author: m[3].trim(), added: m[4].trim(), verdict: m[5], role: m[6] };
  }
  const yanks = {};
  const yankPart = text.split('## Yanked revisions')[1] || '';
  for (const m of yankPart.split('##')[0].matchAll(/^- r(\d{4}): ([^:]+): (.*)$/gm)) yanks[m[1]] = `${m[2]}: ${m[3]}`;
  const notCountedPart = (text.split('## Evaluations that do not count')[1] || '').split('##')[0];
  const notCounted = new Set([...notCountedPart.matchAll(/^- `([^`]+)`: /gm)].map((m) => m[1]));
  return { stage: line('Stage of this target'), workflowStage: line('Stage of the workflow'), recommended: line('Recommended for new projects'), revisions, yanks, notCounted };
}

async function load() {
  const commit = await api('/commits/HEAD');
  SHA = commit.sha;
  const tree = (await api(`/git/trees/${SHA}?recursive=1`)).tree;
  const files = tree.filter((e) => e.type === 'blob').map((e) => e.path);
  const workflows = new Map();
  for (const e of tree) {
    const parts = e.path.split('/');
    if (parts[0] !== ROOT_DIR || parts.length < 2 || e.type !== 'tree') continue;
    if (parts.length === 2) workflows.set(parts[1], { name: parts[1], path: e.path, targets: new Map() });
    const w = workflows.get(parts[1]);
    if (!w) continue;
    if (parts.length === 3) w.targets.set(parts[2], { name: parts[2], path: e.path, revisions: [], evaluations: [], status: null });
    const rev = parts.length === 4 && parts[3].match(REVISION_DIR);
    if (rev && w.targets.has(parts[2])) w.targets.get(parts[2]).revisions.push({ number: rev[1], path: e.path });
  }
  const jobs = [];
  for (const w of workflows.values()) {
    w.summary = '';
    jobs.push(raw(`${w.path}/README.md`).then((t) => { w.summary = summary(t); w.derived = (t.match(/^Derived from: (\S+)/m) || [])[1] || null; }).catch(() => {}));
    for (const t of w.targets.values()) {
      if (files.includes(`${t.path}/STATUS.md`)) jobs.push(raw(`${t.path}/STATUS.md`).then((s) => { t.status = parseStatus(s); }).catch(() => {}));
      for (const f of files.filter((p) => p.startsWith(`${t.path}/Evaluations/`) && p.endsWith('.md'))) {
        jobs.push(raw(f).then((text) => t.evaluations.push({ file: f.split('/').pop(), ...parseFields(text) })).catch(() => {}));
      }
      t.files = files.filter((p) => p.startsWith(`${t.path}/r`));
    }
  }
  await Promise.all(jobs);
  const list = [];
  for (const w of workflows.values()) {
    const targets = [...w.targets.values()].filter((t) => t.revisions.length || t.status);
    let stage = null;
    for (const t of targets) {
      const st = t.status || { revisions: {}, yanks: {}, notCounted: new Set() };
      stage = stage || st.workflowStage;
      t.level = st.stage;
      t.recommended = st.recommended && st.recommended !== 'none' ? st.recommended.replace(/^r/, '') : null;
      t.evaluations.forEach((e) => { e.counted = !st.notCounted.has(e.file); });
      t.evaluations.sort((a, b) => (b.Date || '').localeCompare(a.Date || ''));
      t.revisions.sort((a, b) => b.number.localeCompare(a.number));
      for (const r of t.revisions) {
        const info = st.revisions[r.number] || {};
        r.id = `${w.name}/${t.name}/r${r.number}`;
        r.verdict = info.verdict || 'Open';
        r.role = info.role || 'new';
        r.basedOn = info.basedOn || '';
        r.yank = st.yanks[r.number] || null;
        const evs = t.evaluations.filter((e) => e.counted && e.Revision === r.number);
        r.rating = rating(evs);
        r.medians = Object.fromEntries(['Ease of use', 'Goal contribution', 'Overall effect'].map((f) => [f, median(evs.map((e) => Number(e[f])))]));
      }
    }
    const counted = targets.flatMap((t) => t.evaluations.filter((e) => e.counted));
    list.push({
      ...w, stage: stage || 'Theorized', targets, rating: rating(counted), distribution: distribution(counted),
      agents: [...new Set(counted.flatMap((e) => (e.Agents || '').split(', ').filter((a) => a && a !== 'none').map((a) => a.split(' in ')[0])))].sort(),
    });
  }
  const order = ['Tested', 'Evaluating', 'Theorized', 'Rejected'];
  const stages = [...new Set(list.map((w) => w.stage))].sort((a, b) => order.indexOf(a) - order.indexOf(b));
  return { workflows: list, stages };
}

/* ---------- numbers ---------- */

function median(values) {
  const v = values.filter((x) => Number.isFinite(x)).sort((a, b) => a - b);
  if (!v.length) return null;
  const mid = Math.floor(v.length / 2);
  return v.length % 2 ? v[mid] : (v[mid - 1] + v[mid]) / 2;
}

function rating(evals) {
  const scores = evals.map((e) => Number(e['Overall effect'])).filter(Number.isFinite).map((s) => (s + 2) * 2.5);
  if (!scores.length) return { score: null, votes: 0 };
  const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
  return { score: Math.round(((scores.length * mean + PRIOR_VOTES * 5) / (scores.length + PRIOR_VOTES)) * 10) / 10, votes: scores.length };
}

function distribution(evals) {
  const d = Object.fromEntries(SCORES.map((s) => [s, 0]));
  evals.forEach((e) => { if (e['Overall effect'] in d) d[e['Overall effect']] += 1; });
  return d;
}

/* ---------- zip, built in the browser (method "store", no compression) ---------- */

const CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();
const crc32 = (bytes) => {
  let c = 0xffffffff;
  for (const b of bytes) c = CRC[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};

function zip(entries) {
  const enc8 = new TextEncoder();
  const parts = [];
  const central = [];
  let offset = 0;
  const now = new Date();
  const time = (now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1);
  const date = ((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate();
  for (const { name, data } of entries) {
    const n = enc8.encode(name);
    const crc = crc32(data);
    const local = new DataView(new ArrayBuffer(30));
    [[0, 0x04034b50, 4], [4, 20, 2], [6, 0x0800, 2], [8, 0, 2], [10, time, 2], [12, date, 2], [14, crc, 4],
      [18, data.length, 4], [22, data.length, 4], [26, n.length, 2], [28, 0, 2]]
      .forEach(([o, v, s]) => (s === 4 ? local.setUint32(o, v, true) : local.setUint16(o, v, true)));
    const head = new DataView(new ArrayBuffer(46));
    [[0, 0x02014b50, 4], [4, 20, 2], [6, 20, 2], [8, 0x0800, 2], [10, 0, 2], [12, time, 2], [14, date, 2], [16, crc, 4],
      [20, data.length, 4], [24, data.length, 4], [28, n.length, 2], [30, 0, 2], [32, 0, 2], [34, 0, 2], [36, 0, 2],
      [38, 0, 4], [42, offset, 4]]
      .forEach(([o, v, s]) => (s === 4 ? head.setUint32(o, v, true) : head.setUint16(o, v, true)));
    parts.push(new Uint8Array(local.buffer), n, data);
    central.push(new Uint8Array(head.buffer), n);
    offset += 30 + n.length + data.length;
  }
  const size = central.reduce((a, p) => a + p.length, 0);
  const end = new DataView(new ArrayBuffer(22));
  [[0, 0x06054b50, 4], [4, 0, 2], [6, 0, 2], [8, entries.length, 2], [10, entries.length, 2], [12, size, 4], [16, offset, 4], [20, 0, 2]]
    .forEach(([o, v, s]) => (s === 4 ? end.setUint32(o, v, true) : end.setUint16(o, v, true)));
  return new Blob([...parts, ...central, new Uint8Array(end.buffer)], { type: 'application/zip' });
}

async function download(button) {
  const { target, number } = button.dataset;
  const w = DATA.workflows.find((x) => x.targets.some((t) => t.path === target));
  const t = w.targets.find((x) => x.path === target);
  const folder = `${target}/r${number}`;
  const label = button.textContent;
  button.textContent = 'Preparing…';
  button.disabled = true;
  try {
    const paths = t.files.filter((p) => p.startsWith(`${folder}/kit/`) || p === `${folder}/README.md`);
    const enc8 = new TextEncoder();
    const entries = await Promise.all(paths.map(async (p) => ({
      name: p === `${folder}/README.md` ? 'WORKFLOW-REVISION.md' : p.slice(`${folder}/kit/`.length),
      data: enc8.encode(await raw(p)),
    })));
    const url = URL.createObjectURL(zip(entries));
    const a = document.createElement('a');
    a.href = url;
    a.download = `${w.name}-${t.name}-r${number}.zip`;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    button.textContent = label;
  } catch (err) {
    button.textContent = 'Download failed';
  } finally {
    button.disabled = false;
  }
}

/* ---------- views ---------- */

function chip(r) {
  if (r.score === null) return '<div class="score"><span class="score-chip none" title="No evaluations yet">new</span><span class="votes">0 evaluations</span></div>';
  const cls = r.score >= 6.5 ? 'good' : r.score >= 4 ? 'mid' : 'bad';
  return `<div class="score"><span class="score-chip ${cls}" title="Weighted score from 0 to 10">${r.score.toFixed(1)}</span>`
    + `<span class="votes">${r.votes} evaluation${r.votes === 1 ? '' : 's'}</span></div>`;
}
const pill = (text) => `<span class="pill ${esc(text)}">${esc(text)}</span>`;
const latestClosed = (w) => w.targets.flatMap((t) => t.revisions.filter((r) => r.role === 'recommended'))[0]
  || w.targets.flatMap((t) => t.revisions.filter((r) => !['yanked', 'tainted'].includes(r.role))).sort((a, b) => b.number.localeCompare(a.number))[0];
const signed = (v) => `<b class="${String(v).startsWith('+') ? 'pos' : String(v).startsWith('-') ? 'neg' : ''}">${esc(v)}</b>`;

function chart() {
  app.innerHTML = `
    <h1>Workflows for AI agents, rated by real projects</h1>
    <p class="lead">A workflow is a small set of Markdown files that tells AI agents how to work in a project.
      Pick one, download its recommended revision, use it, and then add your evaluation.</p>
    <div class="tools" role="search">
      <input id="q" type="search" placeholder="Search workflows" aria-label="Search workflows">
      <select id="stage" aria-label="Stage"><option value="">All stages</option>${DATA.stages.map((s) => `<option>${esc(s)}</option>`).join('')}</select>
      <select id="sort" aria-label="Sort">
        <option value="score">Sort: score</option>
        <option value="votes">Sort: most evaluations</option>
        <option value="name">Sort: name</option>
      </select>
    </div>
    <ol class="chart" id="list"></ol>`;
  const draw = () => {
    const q = document.getElementById('q').value.trim().toLowerCase();
    const stage = document.getElementById('stage').value;
    const sort = document.getElementById('sort').value;
    const list = DATA.workflows.filter((w) => (!stage || w.stage === stage)
      && (!q || `${w.name} ${w.summary} ${w.targets.map((t) => t.name).join(' ')}`.toLowerCase().includes(q)));
    if (sort === 'score') list.sort((a, b) => (b.rating.score ?? -1) - (a.rating.score ?? -1) || a.name.localeCompare(b.name));
    if (sort === 'votes') list.sort((a, b) => b.rating.votes - a.rating.votes || a.name.localeCompare(b.name));
    if (sort === 'name') list.sort((a, b) => a.name.localeCompare(b.name));
    document.getElementById('list').innerHTML = list.length ? list.map((w, i) => {
      const last = latestClosed(w);
      return `<li><a class="row" href="#/w/${encodeURIComponent(w.name)}">
        <span class="rank">${i + 1}</span>
        <div class="row-main">
          <div class="row-title"><h3>${esc(w.name)}</h3>${pill(w.stage)}</div>
          <p class="row-sum">${esc(w.summary)}</p>
          <div class="meta"><span>Targets: ${w.targets.map((t) => esc(t.name)).join(', ') || '—'}</span>
            ${last ? `<span>${last.role === 'recommended' ? 'Recommended' : 'Newest'}: r${esc(last.number)}</span>` : ''}
            ${w.agents.length ? `<span>Used with: ${w.agents.map(esc).join(', ')}</span>` : ''}</div>
        </div>
        ${chip(w.rating)}
      </a></li>`;
    }).join('') : '<li class="empty">No workflow matches the search.</li>';
  };
  ['q', 'stage', 'sort'].forEach((id) => document.getElementById(id).addEventListener('input', draw));
  draw();
}

function bars(dist) {
  const total = Object.values(dist).reduce((a, b) => a + b, 0);
  return `<div class="bars">${SCORES.map((s) => {
    const n = dist[s] || 0;
    const pct = total ? Math.round((100 * n) / total) : 0;
    return `<div class="bar"><span>${SCORE_LABEL[s]}</span><span class="bar-track"><span class="bar-fill" style="width:${pct}%"></span></span><span>${n}</span></div>`;
  }).join('')}</div>`;
}

const SHOWN = new Set(['Revision', 'Date', 'Project', 'Project owner', 'Agents', 'Overall effect', 'Goal contribution', 'Ease of use', 'Strength', 'Problem']);

function review(e) {
  const extra = Object.entries(e).filter(([k]) => !SHOWN.has(k) && !['file', 'counted'].includes(k));
  return `<article class="review${e.counted ? '' : ' superseded'}">
    <div class="review-head">
      <div><strong>${esc(e.Project)}</strong> <span class="muted">by ${esc(e['Project owner'])}</span></div>
      <div class="muted">r${esc(e.Revision)} · ${esc(e.Date)}${e.counted ? '' : ' · does not count'}</div>
    </div>
    <div class="scores">
      ${['Overall effect', 'Goal contribution', 'Ease of use'].filter((f) => f in e).map((f) => `<span class="chip">${f} ${signed(e[f])}</span>`).join('')}
      ${extra.map(([k, v]) => `<span class="chip">${esc(k)}: ${esc(v)}</span>`).join('')}
    </div>
    ${e.Agents ? `<div class="muted">Agents: ${esc(e.Agents)}</div>` : ''}
    ${e.Strength && e.Strength !== 'none' ? `<p class="quote"><b>Strength:</b> ${esc(e.Strength)}</p>` : ''}
    ${e.Problem && e.Problem !== 'none' ? `<p class="quote"><b>Problem:</b> ${esc(e.Problem)}</p>` : ''}
  </article>`;
}

function detail(name) {
  const w = DATA.workflows.find((x) => x.name === name);
  if (!w) { app.innerHTML = '<p class="empty">This workflow does not exist. <a href="#/">See all workflows</a>.</p>'; return; }
  const evals = w.targets.flatMap((t) => t.evaluations);
  const last = latestClosed(w);
  app.innerHTML = `
    <p><a href="#/">← All workflows</a></p>
    <section class="hero">
      <div>
        <div class="row-title"><h1>${esc(w.name)}</h1>${pill(w.stage)}</div>
        <p class="lead">${esc(w.summary)}</p>
        <a class="btn ghost" href="${treeUrl(w.path)}">Read the workflow on GitHub</a>
      </div>
      ${chip(w.rating)}
    </section>
    <div class="grid2" style="margin-top:20px">
      <div class="panel"><h3>Overall effect, by evaluation</h3><p class="muted" style="margin:4px 0 12px">Compared with the usual way of work of each project.</p>${bars(w.distribution)}</div>
      <div class="panel"><h3>Before you use a revision</h3>
        <ol class="steps">
          <li>Prefer the revision with the role <b>recommended</b>. A revision never changes after the merge.</li>
          <li>Extract the zip into the root of your project.</li>
          <li>Record the revision ID in your project${last ? `, for example <code>${esc(last.id)}</code>` : ''}.</li>
          <li>After some work, <a href="${repoUrl('/blob/HEAD/CONTRIBUTING.md')}">add an evaluation</a>.</li>
        </ol>
      </div>
    </div>
    ${w.targets.map((t) => `
      <h2>${esc(t.name)}${t.level ? ` <span class="muted" style="font-weight:500;font-size:15px">· level: ${esc(t.level)}</span>` : ''}</h2>
      <div class="panel table-wrap"><table class="revisions">
        <thead><tr><th>Revision</th><th>Role</th><th>Based on</th><th>Score</th><th>Medians: ease / goal / overall</th><th></th></tr></thead>
        <tbody>${t.revisions.map((r) => `<tr>
          <td><a href="${treeUrl(r.path)}">${esc(r.id)}</a></td>
          <td data-label="Role">${pill(r.role)}${r.yank ? `<div class="muted small">${esc(r.yank)}</div>` : ''}</td>
          <td data-label="Based on">${esc(r.basedOn || '—')}</td>
          <td data-label="Score">${r.rating.score === null ? '<span class="muted">—</span>' : `${r.rating.score.toFixed(1)} <span class="muted">(${r.rating.votes})</span>`}</td>
          <td data-label="Medians: ease / goal / overall">${['Ease of use', 'Goal contribution', 'Overall effect'].map((f) => (r.medians[f] === null ? '—' : (r.medians[f] > 0 ? '+' : '') + r.medians[f])).join(' / ')}</td>
          <td><button class="btn${['yanked', 'tainted'].includes(r.role) ? ' ghost' : ''}" data-target="${esc(t.path)}" data-number="${esc(r.number)}"
            ${['yanked', 'tainted'].includes(r.role) ? 'title="Do not use this revision in a new project"' : ''}>Download zip</button></td>
        </tr>`).join('')}</tbody>
      </table></div>
      ${t.revisions.some((r) => ['yanked', 'tainted'].includes(r.role)) ? '<p class="notice">A yanked or tainted revision stays here for the projects that use it. Do not use it in a new project.</p>' : ''}
    `).join('')}
    <h2>Evaluations</h2>
    <div class="reviews">${evals.length ? evals.map(review).join('')
      : `<div class="empty">No evaluation yet. Use a revision in a project, then
         <a href="${repoUrl('/blob/HEAD/templates/EVALUATION.md')}">add the first evaluation</a>.</div>`}</div>`;
  app.querySelectorAll('button[data-target]').forEach((b) => b.addEventListener('click', () => download(b)));
}

function how() {
  app.innerHTML = `
    <h1>How it works</h1>
    <p class="lead">The collector accepts workflows of all kinds. Evidence from real projects decides which ones rise.
      This page reads the repository each time it opens.</p>
    <div class="grid2">
      <div class="panel"><h3>Revisions</h3><p>Each workflow has numbered revisions. A revision never changes after the merge, and it has a Git tag with its ID.
        Each revision has a role: ${['recommended', 'candidate', 'superseded', 'dormant', 'tainted', 'yanked'].map(pill).join(' ')}</p></div>
      <div class="panel"><h3>Evaluations</h3><p>A project that uses a revision adds one short file with fixed fields. Each project counts one time for each revision.</p></div>
      <div class="panel"><h3>Score</h3><p>The score is the mean "Overall effect" on a scale from 0 to 10. With few evaluations, the score
        moves toward 5, so that one enthusiastic project cannot put a workflow at the top.</p></div>
      <div class="panel"><h3>Stages</h3><p>${DATA.stages.map(pill).join(' ')} A program computes the stage from the evaluations.
        The rules are in <a href="${repoUrl('/blob/HEAD/CONTRIBUTING.md')}">CONTRIBUTING.md</a>.</p></div>
    </div>`;
}

function route() {
  const hash = location.hash || '#/';
  document.querySelectorAll('.top-nav a').forEach((a) => a.removeAttribute('aria-current'));
  const m = hash.match(/^#\/w\/(.+)$/);
  if (m) detail(decodeURIComponent(m[1]));
  else if (hash === '#/how') { how(); document.querySelector('.top-nav a[href="#/how"]').setAttribute('aria-current', 'page'); }
  else { chart(); document.querySelector('.top-nav a[href="#/"]').setAttribute('aria-current', 'page'); }
  window.scrollTo(0, 0);
}

REPO = repository();
if (!REPO) {
  app.innerHTML = '<p class="empty">Open this page with <code>?repo=owner/name</code>, or publish it on GitHub Pages.</p>';
} else {
  document.getElementById('repo-link').href = repoUrl();
  load().then((d) => {
    DATA = d;
    window.addEventListener('hashchange', route);
    route();
  }).catch((err) => {
    app.innerHTML = `<p class="empty">The page could not read the repository ${esc(REPO)} on GitHub. ${esc(err.message)}</p>`;
  });
}
