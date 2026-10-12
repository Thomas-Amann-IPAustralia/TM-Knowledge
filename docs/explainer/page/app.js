(function () {
'use strict';

/* ================================================================ data and helpers */
const D = JSON.parse(document.getElementById('tmk-data').textContent);
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = (n) => Number(n).toLocaleString('en-AU');
const NS = 'http://www.w3.org/2000/svg';
const C = D.concepts;
const P = D.preds;
const REL = new Map(D.rels.map((r) => [r[0], { id: r[0], s: r[1], p: r[2], o: r[3], origin: r[4], ref: r[5], quote: r[6], modality: r[7] }]));
const RELS = Array.from(REL.values());
const KIND = new Map(D.kinds.map((k) => [k.id, k]));
const BY_LABEL = new Map(Object.entries(C).map(([id, c]) => [c.l, id]));
const PAGE = new Map(D.pages.map((p) => [p[0], p]));
const kc = (k) => `var(--k-${k})`;
const smooth = () => (matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth');
function idOf(label) {
  const id = BY_LABEL.get(label);
  if (!id) console.warn('No idea labelled', label);
  return id;
}

const SRC_WORD = { manual: 'Manual', act: 'Act', regs: 'Regulations', case: 'Case' };
function srcType(ref) {
  if (ref.startsWith('TMM/')) return 'manual';
  if (ref.startsWith('TMA1995')) return 'act';
  if (ref.startsWith('TMR1995')) return 'regs';
  return 'case';
}
function provShort(ref) {
  let m = /^TM[AR]1995\/([sr])([^/]+)(?:\/(.+))?$/.exec(ref);
  if (m) return `${m[1]} ${m[2]}${m[3] ? ` (${m[3].replace(/-/g, ' ')})` : ''}`;
  m = /^CASE\/(\d{4})\/([A-Za-z]+)\/(\d+)$/.exec(ref);
  if (m) return `[${m[1]}] ${m[2]} ${m[3]}`;
  return ref.replace(/^CASE\//, '').replace(/\//g, ' ');
}
const partNo = (ref) => (/^TMM\/Part(\w+)/.exec(ref) || [])[1] || '';
const pageTitle = (ref) => (D.ref_pages[ref] || D.passages[ref] || [''])[0] || '';
const pageUrl = (ref) => (D.ref_pages[ref] || [])[1] || (D.passages[ref] || [])[3] || '';
function manualLabel(ref) {
  const t = pageTitle(ref);
  return /^Part\s/.test(t) ? t : `Part ${partNo(ref)}${t ? ' · ' + t : ''}`;
}
const srcLabel = (ref) => (srcType(ref) === 'manual' ? manualLabel(ref) : provShort(ref));
function srcChip(ref) {
  if (!ref) return '';
  const t = srcType(ref);
  const url = t === 'manual' ? pageUrl(ref) : '';
  const inner = `<i class="mk mk-${t}" aria-hidden="true"></i><span class="src-k">${SRC_WORD[t]}</span> ${esc(srcLabel(ref))}`;
  return url
    ? `<a class="src src-${t}" href="${esc(url)}" target="_blank" rel="noopener" title="Open this page of the published Manual">${inner}</a>`
    : `<span class="src src-${t}">${inner}</span>`;
}
const nameOf = (x) => (C[x] ? C[x].l : `${SRC_WORD[srcType(x)]} ${srcLabel(x)}`);
function ideaChip(x) {
  const c = C[x];
  if (!c) return srcChip(x);
  return `<button type="button" class="idea${c.o === 'machine' ? ' mac' : ''}" data-idea="${esc(x)}" style="--c:${kc(c.k)}" title="${c.o === 'machine' ? 'Machine-written, unreviewed' : 'Reviewed by a trade marks expert'}: open this idea"><i></i>${esc(c.l)}</button>`;
}
const ideaByLabel = (label) => ideaChip(idOf(label));
const trust = (origin) => (origin === 'reviewed' ? '<span class="trust rev">Reviewed</span>' : '<span class="trust mac">Machine · unreviewed</span>');
const quote = (ref, text) => (text ? `<blockquote class="q q-${srcType(ref)}">“${esc(text)}”</blockquote>` : '');
function relLine(r) {
  return `<div class="rel-line">${ideaChip(r.s)}<span class="pred">${esc(P[r.p] || r.p)}</span>${ideaChip(r.o)}</div>`;
}
function relCard(r, extra) {
  return `<div class="rel-card">${relLine(r)}${quote(r.ref, r.quote)}<div class="rel-meta">${srcChip(r.ref)}${trust(r.origin)}</div>${extra || ''}</div>`;
}
function bar(label, n, max, colour) {
  return `<div class="bar-row"><span class="lab" title="${esc(label)}">${esc(label)}</span><span class="track"><span class="fill" style="display:block;width:${(n / max) * 100}%;--c:${colour || 'var(--manual)'}"></span></span><span class="num">${fmt(n)}</span></div>`;
}
function hilite(text, words) {
  const ws = words.filter(Boolean).sort((a, b) => b.length - a.length).map((w) => esc(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  if (!ws.length) return esc(text);
  return esc(text).replace(new RegExp(`(${ws.join('|')})`, 'gi'), '<mark>$1</mark>');
}
function scrollToEl(el) { el.scrollIntoView({ behavior: smooth(), block: 'start' }); }

/* ================================================================ page chrome */
(function chrome() {
  const root = document.documentElement;
  try { const t = localStorage.getItem('tmk-explainer-theme'); if (t === 'dark' || t === 'light') root.dataset.theme = t; } catch (e) { /* storage blocked */ }
  $('#theme').addEventListener('click', () => {
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('tmk-explainer-theme', root.dataset.theme); } catch (e) { /* storage blocked */ }
  });
  const k = D.counts;
  const N = {
    concepts: k.concepts.signed + k.concepts.machine, relations: k.relations.signed + k.relations.machine,
    'concepts-machine': k.concepts.machine, 'relations-machine': k.relations.machine,
    'concepts-signed': k.concepts.signed, 'relations-signed': k.relations.signed,
  };
  $$('[data-count]').forEach((e) => { e.textContent = fmt(N[e.dataset.count]); });
  $$('[data-asof]').forEach((e) => { e.textContent = D.asof; });
  $$('[data-snapshot]').forEach((e) => { e.textContent = D.snapshot; });
  $$('[data-events]').forEach((e) => { e.textContent = fmt(D.stability.events); });

  if ('IntersectionObserver' in window) {
    const links = new Map($$('.stops a').map((a) => [a.getAttribute('href').slice(1), a]));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        links.forEach((a) => a.classList.remove('on'));
        const a = links.get(en.target.id);
        if (a) { a.classList.add('on'); a.scrollIntoView({ block: 'nearest', inline: 'nearest' }); }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    $$('section.stop').forEach((s) => io.observe(s));
  }
})();

/* ================================================================ the idea inspector */
const dlg = $('#inspector');
function openIdea(id) {
  const c = C[id];
  if (!c) return;
  const k = KIND.get(c.k);
  $('#insp-kind').textContent = k ? `${k.label} · ${D.families[k.family] || ''}` : c.k;
  $('#insp-title').textContent = c.l;
  const parts = c.parts.map((p) => p.replace('Part', '')).join(', ');
  $('#insp-badges').innerHTML = `${trust(c.o)}<span class="tiny">Named in ${fmt(c.m)} passage${c.m === 1 ? '' : 's'}${parts ? `, in Parts including ${esc(parts)}` : ''}</span>`;
  const out = RELS.filter((r) => r.s === id);
  const inc = RELS.filter((r) => r.o === id);
  const sec = (title, html) => (html ? `<section><h4>${title}</h4>${html}</section>` : '');
  const chips = (xs) => `<div class="row">${xs.map((a) => `<span class="chip" style="cursor:default">${esc(a)}</span>`).join('')}</div>`;
  $('#insp-body').innerHTML =
    sec('What kind of thing it is', `<p class="small" style="margin:0">${esc(k ? k.plain : '')}.</p>`) +
    sec('Also written as', c.alt.length ? chips(c.alt) : '') +
    sec('Not the same as', c.not.length ? chips(c.not) : '') +
    sec('Rests on the law at', c.basis.length ? `<div class="row">${c.basis.map(srcChip).join('')}</div>` : '') +
    sec(`Connections from this idea (${out.length})`, out.length ? `<div class="stack">${out.map((r) => relCard(r)).join('')}</div>` : '') +
    sec(`Connections to this idea (${inc.length})`, inc.length ? `<div class="stack">${inc.map((r) => relCard(r)).join('')}</div>` : '') +
    (out.length || inc.length ? '' : '<p class="small muted" style="margin:0">No connections recorded yet.</p>') +
    '<p class="tiny" style="margin:0">Machine-written records carry the model that wrote them, the date and their reasoning. Reviewed records were checked by a trade marks expert. Neither name is shown here.</p>';
  if (!dlg.open) {
    try { dlg.showModal(); } catch (e) { dlg.setAttribute('open', ''); }
  }
  $('#insp-body').scrollTop = 0;
  dlg.scrollTop = 0;
}
function closeIdea() { try { dlg.close(); } catch (e) { dlg.removeAttribute('open'); } }
$('#insp-close').addEventListener('click', closeIdea);
dlg.addEventListener('click', (e) => { if (e.target === dlg) closeIdea(); });
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-idea]');
  if (b) { openIdea(b.dataset.idea); return; }
  const l = e.target.closest('[data-idea-label]');
  if (l) { const id = idOf(l.dataset.ideaLabel); if (id) openIdea(id); }
});

/* ================================================================ small maps (SVG) */
function wrap(label, max) {
  const lines = [];
  let cur = '';
  for (const w of label.split(' ')) {
    if (!cur) cur = w;
    else if ((cur + ' ' + w).length <= max) cur += ' ' + w;
    else { lines.push(cur); cur = w; }
  }
  if (cur) lines.push(cur);
  return lines;
}
function exitPoint(n, tx, ty) {
  const dx = tx - n.x, dy = ty - n.y;
  const s = Math.min((n.w / 2 + 3) / Math.abs(dx || 1e-6), (n.h / 2 + 3) / Math.abs(dy || 1e-6));
  return [n.x + dx * s, n.y + dy * s];
}
let graphSeq = 0;
function drawGraph(host, spec, opts) {
  opts = opts || {};
  const G = ++graphSeq;
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', `0 0 ${spec.w} ${spec.h}`);
  svg.setAttribute('class', 'graph');
  svg.setAttribute('role', 'group');
  svg.setAttribute('aria-label', spec.label || 'A small map of ideas and connections');
  if (spec.minW) svg.style.minWidth = spec.minW + 'px';
  const mk = (tag, attrs, parent) => {
    const e = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    (parent || svg).appendChild(e);
    return e;
  };
  const defs = mk('defs', {});
  [['a', 'arrowhead'], ['h', 'arrowhead hot']].forEach(([name, cls]) => {
    const m = mk('marker', { id: `ar${G}${name}`, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' }, defs);
    mk('path', { d: 'M0,0 L10,5 L0,10 z', class: cls }, m);
  });
  const nodes = new Map();
  spec.nodes.forEach((n) => {
    const id = n.ref || idOf(n.label);
    if (!id) return;
    const c = C[id];
    const lines = wrap(c ? c.l : nameOf(id), 18);
    const w = Math.max(...lines.map((l) => l.length)) * 7.1 + 36;
    const h = lines.length * 16 + 14;
    nodes.set(id, { id, x: n.x, y: n.y, w, h, lines, c, law: !c });
  });
  const gE = mk('g', {}), gN = mk('g', {}), gL = mk('g', {});
  const edges = [];
  spec.edges.forEach((e) => {
    const r = REL.get(e.rel);
    if (!r) { console.warn('No connection', e.rel); return; }
    const a = nodes.get(r.s), b = nodes.get(r.o);
    if (!a || !b) { console.warn('Connection ends not drawn', e.rel); return; }
    const dx = b.x - a.x, dy = b.y - a.y;
    const bend = e.bend || 0;
    const cx = (a.x + b.x) / 2 - dy * bend, cy = (a.y + b.y) / 2 + dx * bend;
    const p0 = exitPoint(a, cx, cy), p1 = exitPoint(b, cx, cy);
    const d = `M${p0[0].toFixed(1)},${p0[1].toFixed(1)} Q${cx.toFixed(1)},${cy.toFixed(1)} ${p1[0].toFixed(1)},${p1[1].toFixed(1)}`;
    const mx = 0.25 * p0[0] + 0.5 * cx + 0.25 * p1[0] + (e.lx || 0);
    const my = 0.25 * p0[1] + 0.5 * cy + 0.25 * p1[1] + (e.ly || 0);
    const path = mk('path', { d, class: `gedge ${r.origin === 'machine' ? 'mac' : 'rev'}`, 'marker-end': `url(#ar${G}a)` }, gE);
    const hit = mk('path', { d, class: 'ghit', tabindex: 0, role: 'button', 'aria-label': `${nameOf(r.s)}, ${P[r.p] || r.p}, ${nameOf(r.o)}. Show the sentence.` }, gE);
    const lab = mk('text', { x: mx.toFixed(1), y: (my + 4).toFixed(1), 'text-anchor': 'middle', class: 'glabel' }, gL);
    lab.textContent = P[r.p] || r.p;
    edges.push({ r, path, hit, lab });
  });
  nodes.forEach((n) => {
    const g = mk('g', {
      class: `gnode${n.c && n.c.o === 'machine' ? ' mac' : ''}${n.law ? ' law' : ''}`,
      transform: `translate(${n.x},${n.y})`, tabindex: 0, role: 'button',
      'aria-label': n.c ? `${n.c.l}. Open this idea.` : `${nameOf(n.id)}. Show the provision.`,
    }, gN);
    g.style.setProperty('--c', n.c ? kc(n.c.k) : 'var(--act)');
    mk('rect', { x: -n.w / 2, y: -n.h / 2, width: n.w, height: n.h, rx: 9, class: 'gn-box' }, g);
    if (n.law) mk('rect', { x: -n.w / 2 + 9, y: -4.5, width: 9, height: 9, class: 'gn-dot', transform: `rotate(45 ${-n.w / 2 + 13.5} 0)` }, g);
    else mk('circle', { cx: -n.w / 2 + 14, cy: 0, r: 4.5, class: 'gn-dot' }, g);
    n.lines.forEach((line, i) => {
      const t = mk('text', { x: 9, y: ((i - (n.lines.length - 1) / 2) * 16 + 4.5).toFixed(1), 'text-anchor': 'middle' }, g);
      t.textContent = line;
    });
    n.g = g;
  });
  host.innerHTML = '';
  host.appendChild(svg);

  const api = {
    edges, nodes,
    select(relId) {
      edges.forEach((e) => {
        const on = e.r.id === relId;
        e.path.classList.toggle('hot', on);
        e.path.setAttribute('marker-end', `url(#ar${G}${on ? 'h' : 'a'})`);
        e.lab.classList.toggle('hot', on);
      });
      if (opts.onEdge && relId) opts.onEdge(REL.get(relId));
    },
    hotNodes(ids) { nodes.forEach((n) => n.g.classList.toggle('hot', ids.includes(n.id))); },
  };
  const key = (fn) => (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); fn(); } };
  edges.forEach((e) => {
    const go = () => api.select(e.r.id);
    e.hit.addEventListener('click', go);
    e.hit.addEventListener('keydown', key(go));
    if (opts.onEdgeHover) {
      e.hit.addEventListener('mouseenter', () => opts.onEdgeHover(e.r.id, true));
      e.hit.addEventListener('mouseleave', () => opts.onEdgeHover(e.r.id, false));
    }
  });
  nodes.forEach((n) => {
    const go = () => { if (n.c) openIdea(n.id); else if (opts.onLaw) opts.onLaw(n.id); };
    n.g.addEventListener('click', go);
    n.g.addEventListener('keydown', key(go));
    if (opts.onNodeHover) {
      n.g.addEventListener('mouseenter', () => opts.onNodeHover(n.id, true));
      n.g.addEventListener('mouseleave', () => opts.onNodeHover(n.id, false));
    }
  });
  return api;
}
function lawCard(ref) {
  const p = D.provs[ref] || ['', '', ''];
  return `<div class="rel-card"><p class="small" style="margin:0 0 .3rem"><b>${esc(nameOf(ref))}</b>: ${esc(p[1] || p[0])}</p>${quote(ref, p[2])}<div class="rel-meta">${srcChip(ref)}<span class="tiny">The law itself, not a record anyone wrote.</span></div></div>`;
}

/* ================================================================ start: the same guidance, two ways */
(function twoWays() {
  const SENT = [
    { rel: 'GR-0686', marks: [['a name of a person (or group of people) which is well known', 'well-known person'], ['section 43', 'section 43 ground for rejection']] },
    { rel: 'GR-0688', marks: [['section 43 ground for rejection', 'section 43 ground for rejection'], ['image of a person', 'image of a person']] },
    { rel: 'GR-0687', marks: [['section 43 ground for rejection', 'section 43 ground for rejection'], ['well-known person', 'well-known person'], ['written permission', 'written permission']] },
    { rel: 'GR-0435', marks: [['written permission', 'written permission'], ['endorsement', 'endorsement']] },
  ];
  const text = $('#tw-text');
  text.innerHTML = SENT.map((s) => {
    const r = REL.get(s.rel);
    let html = '', pos = 0;
    const found = s.marks.map(([ph, label]) => [r.quote.indexOf(ph), ph, label]).filter((m) => m[0] >= 0).sort((a, b) => a[0] - b[0]);
    found.forEach(([at, ph, label]) => {
      if (at < pos) return;
      const id = idOf(label);
      html += esc(r.quote.slice(pos, at)) + `<span class="ph" tabindex="0" data-node="${id}" style="--c:${kc(C[id].k)}">${esc(ph)}</span>`;
      pos = at + ph.length;
    });
    html += esc(r.quote.slice(pos));
    return `<p data-rel="${s.rel}">“${html}”</p>`;
  }).join('') + `<div class="row" style="margin-top:.4rem">${srcChip('TMM/Part29/6#1~1')}<span class="trust mac">The arrows: machine · unreviewed</span></div>`;

  const spec = {
    w: 640, h: 330, minW: 520, label: 'A small map of names and images of persons under section 43',
    nodes: [
      { label: 'image of a person', x: 105, y: 55 },
      { label: 'well-known person', x: 105, y: 275 },
      { label: 'section 43 ground for rejection', x: 320, y: 165 },
      { label: 'written permission', x: 535, y: 80 },
      { label: 'endorsement', x: 535, y: 265 },
    ],
    edges: [{ rel: 'GR-0688' }, { rel: 'GR-0686' }, { rel: 'GR-0687', ly: -6 }, { rel: 'GR-0435' }],
  };
  const paras = new Map($$('p[data-rel]', text).map((p) => [p.dataset.rel, p]));
  const phrases = $$('.ph', text);
  let g = null;
  const lightNode = (id, on) => {
    phrases.forEach((p) => p.classList.toggle('hot', on && p.dataset.node === id));
    g.hotNodes(on ? [id] : []);
  };
  const lightRel = (rel, on) => {
    paras.forEach((p, k) => p.classList.toggle('hot', on && k === rel));
    g.select(on ? rel : null);
  };
  g = drawGraph($('#tw-map'), spec, {
    onNodeHover: lightNode,
    onEdgeHover: lightRel,
    onEdge: (r) => paras.forEach((p, k) => p.classList.toggle('hot', k === r.id)),
  });
  phrases.forEach((p) => {
    ['mouseenter', 'focus'].forEach((ev) => p.addEventListener(ev, () => lightNode(p.dataset.node, true)));
    ['mouseleave', 'blur'].forEach((ev) => p.addEventListener(ev, () => lightNode(p.dataset.node, false)));
    p.addEventListener('click', () => openIdea(p.dataset.node));
  });
  paras.forEach((p, rel) => {
    p.addEventListener('mouseenter', () => lightRel(rel, true));
    p.addEventListener('mouseleave', () => lightRel(rel, false));
  });
})();

/* ================================================================ waffles */
const PARTS = D.parts;
const partAt = [];
PARTS.forEach((p, pi) => { for (let j = 0; j < p[2]; j++) partAt.push(pi); });
const NP = partAt.length;
const partStart = PARTS.map((_, pi) => partAt.indexOf(pi));
function waffle(host, label) {
  const cols = 60, cell = 9, gap = 2, rows = Math.ceil(NP / cols);
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', `-2 -2 ${cols * (cell + gap) - gap + 4} ${rows * (cell + gap) - gap + 4}`);
  svg.setAttribute('class', 'waffle');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', label);
  const rects = new Array(NP);
  const frag = document.createDocumentFragment();
  for (let i = 0; i < NP; i++) {
    const r = document.createElementNS(NS, 'rect');
    r.setAttribute('x', (i % cols) * (cell + gap));
    r.setAttribute('y', Math.floor(i / cols) * (cell + gap));
    r.setAttribute('width', cell);
    r.setAttribute('height', cell);
    r.setAttribute('rx', 1.5);
    r.dataset.i = i;
    frag.appendChild(r);
    rects[i] = r;
  }
  svg.appendChild(frag);
  host.appendChild(svg);
  return { svg, rects };
}
function onCell(svg, fn) {
  const h = (e) => { const r = e.target.closest && e.target.closest('rect[data-i]'); if (r) fn(Number(r.dataset.i), e.type); };
  svg.addEventListener('mouseover', h);
  svg.addEventListener('click', h);
}
const partTitle = (id) => D.stability.part_titles[id] || id;

/* ================================================================ 1. text */
(function textStop() {
  const { svg, rects } = waffle($('#text-waffle'), 'Every passage of the Manual, one square each, shaded by Part');
  const sel = $('#part-pick');
  PARTS.forEach((p, pi) => {
    const o = document.createElement('option');
    o.value = pi;
    o.textContent = `${p[1]} (${fmt(p[2])})`;
    sel.appendChild(o);
  });
  function light(pi) {
    rects.forEach((r, i) => r.setAttribute('class', partAt[i] === pi ? 'hi' : partAt[i] % 2 ? 'pa' : ''));
  }
  function info(i) {
    const p = PARTS[partAt[i]];
    const pct = (p[2] / NP) * 100;
    $('#text-info').innerHTML = `<b>Passage ${fmt(i + 1)} of ${fmt(NP)}</b><br>${esc(p[1])}<br><span class="tiny">This Part holds ${fmt(p[2])} passage${p[2] === 1 ? '' : 's'}, ${pct < 1 ? pct.toFixed(1) : Math.round(pct)}% of the Manual.</span>`;
  }
  onCell(svg, (i, type) => {
    info(i);
    if (type === 'click') { sel.value = partAt[i]; light(partAt[i]); }
    else if (sel.value === '') light(partAt[i]);
  });
  svg.addEventListener('mouseleave', () => light(sel.value === '' ? -1 : Number(sel.value)));
  sel.addEventListener('change', () => {
    const pi = sel.value === '' ? -1 : Number(sel.value);
    light(pi);
    if (pi >= 0) info(partStart[pi]);
  });
  const p14 = PARTS.findIndex((p) => p[0] === 'Part14');
  sel.value = p14;
  light(p14);
  info(partStart[p14]);
})();

/* ================================================================ 2. words */
const showWords = (function wordsStop() {
  const COLS = ['var(--k-context)', 'var(--k-ground_of_refusal)', 'var(--k-legal_test)', 'var(--k-process_role)', 'var(--k-subject_matter)', 'var(--k-sign_content)'];
  const { svg, rects } = waffle($('#words-waffle'), 'Every passage of the Manual; coloured squares use a wording of the chosen idea');
  const SC = D.showcase;
  const consent = new Set(D.consent.idx);
  let mode = 'many', sc = 0, labels = [], owner = new Map(), active = new Set(), sel = -1;

  function setup() {
    const s = SC[sc];
    labels = Object.keys(s.wordings).sort((a, b) => (a === s.label ? -1 : b === s.label ? 1 : s.wordings[b].length - s.wordings[a].length));
    owner = new Map();
    labels.forEach((l, li) => s.wordings[l].forEach((i) => { if (!owner.has(i)) owner.set(i, li); }));
    (s.wordings[s.label] || []).forEach((i) => owner.set(i, 0));
    active = new Set(labels);
  }
  function paint() {
    rects.forEach((r, i) => {
      let fill = '';
      if (mode === 'many') { const li = owner.get(i); if (li !== undefined && active.has(labels[li])) fill = COLS[li % COLS.length]; }
      else if (consent.has(i)) fill = 'var(--glow)';
      r.setAttribute('class', (fill ? '' : 'off') + (i === sel ? ' sel' : ''));
      r.style.fill = fill;
    });
  }
  function side() {
    const host = $('#words-side');
    if (mode === 'many') {
      const s = SC[sc];
      host.innerHTML = `
        <p>Pick an idea. The coloured squares are the passages that name it; the colour shows which wording each one uses.</p>
        <div class="tabs" role="tablist" aria-label="Pick an idea">${SC.map((x, i) => `<button class="tab" role="tab" aria-selected="${i === sc}" data-sc="${i}">${esc(x.label)}</button>`).join('')}</div>
        <div class="facts">
          <div class="fact"><b>${fmt(s.named)}</b><span>passages use the formal term “${esc(s.label)}”</span></div>
          <div class="fact"><b>${fmt(s.total)}</b><span>passages name the idea, in ${labels.length} wordings</span></div>
          <div class="fact"><b style="color:var(--bad)">${fmt(s.missed)}</b><span>missed by a search for the formal term</span></div>
        </div>
        <p>The ontology records the wordings once, on the idea. Every passage using any of them is then linked to the same idea, whatever words it uses.</p>
        <p class="tiny" style="margin-bottom:.35rem">Turn a wording on or off:</p>
        <div class="row">${labels.map((l, li) => `<button type="button" class="chip" aria-pressed="${active.has(l)}" data-w="${li}"><span class="dot" style="--c:${COLS[li % COLS.length]}"></span>${esc(l)} · ${s.wordings[l].length}</button>`).join('')}</div>
        <p style="margin-top:1rem">${ideaByLabel(s.label)} <span class="small muted">Open everything the map holds about this idea.</span></p>
        <p class="small muted">People outside the office use other words again. An applicant might say "a famous person" where the Manual says "well-known person". The map can hold everyday phrasings too; in the demonstrator a machine wrote some for search, and they are labelled as machine-written.</p>`;
      $$('[data-sc]', host).forEach((b) => b.addEventListener('click', () => { sc = Number(b.dataset.sc); setup(); side(); pickDefault(); paint(); }));
      $$('[data-w]', host).forEach((b) => b.addEventListener('click', () => {
        const l = labels[Number(b.dataset.w)];
        if (active.size === labels.length) active = new Set([l]);
        else if (active.has(l) && active.size === 1) active = new Set(labels);
        else if (active.has(l)) active.delete(l);
        else active.add(l);
        $$('[data-w]', host).forEach((x) => x.setAttribute('aria-pressed', active.has(labels[Number(x.dataset.w)])));
        paint();
      }));
    } else {
      const bp = Object.entries(D.consent.by_part).sort((a, b) => b[1] - a[1]);
      const max = bp[0][1];
      const wp = C[idOf('written permission')];
      host.innerHTML = `
        <p><b>“Consent”</b> appears in ${D.consent.idx.length} passages. It can mean a well-known person's written permission to use their name (section 43), a letter of consent from another trade mark owner (section 44), the ACCC's consent, or a Minister's consent under another Act.</p>
        <p class="small" style="margin-bottom:.4rem">Where those ${D.consent.idx.length} passages sit:</p>
        <div class="bars">${bp.slice(0, 8).map(([p, n]) => bar(partTitle(p), n, max, 'var(--glow)')).join('')}</div>
        <p class="small muted" style="margin-top:.6rem">Part 29, where a well-known person's written permission is discussed, is not among them. There the Manual says “permission”.</p>
        <p>So the ontology records that “consent” on its own is too general to count as any one of these ideas. Each idea can also carry <b>“not” labels</b>: wordings that look close but mean something else. ${ideaByLabel('written permission')} is recorded as not the same as ${wp.not.map((x) => `<span class="chip" style="cursor:default">${esc(x)}</span>`).join(' ')}.</p>
        <h4>“Sign”: a legal term and an ordinary verb</h4>
        <blockquote class="q q-act">“A trade mark is a sign used, or intended to be used, to distinguish goods or services dealt with or provided in the course of trade by a person from goods or services so dealt with or provided by any other person.”</blockquote>
        <p class="row">${srcChip('TMA1995/s17')}</p>
        <p>The Act also says a sign <i>“includes … any letter, word, name, signature, numeral, device, brand, heading, label, ticket, aspect of packaging, shape, colour, sound or scent”</i> (section 6). In “who has to <i>sign</i> the declaration?” it is an ordinary verb. The demonstrator really did confuse the two; stop 10 lists it as a known limit.</p>`;
    }
  }
  function info(i) {
    const out = $('#words-info');
    if (mode === 'many') {
      const s = SC[sc];
      const li = owner.get(i);
      if (li === undefined) {
        out.innerHTML = `<b>Passage ${fmt(i + 1)}</b> · ${esc(PARTS[partAt[i]][1])}<br><span class="muted">Does not name <i>${esc(s.label)}</i> in any of its wordings.</span>`;
        return;
      }
      const sn = s.snips[i];
      const l = labels[li];
      out.innerHTML = `<b>${esc(sn[1])}</b>${sn[2] && sn[2] !== sn[1] ? ` <span class="muted">› ${esc(sn[2])}</span>` : ''}<br>
        <span class="tiny">Names <b>${esc(s.label)}</b> ${l === s.label ? 'by the formal term' : `as “${esc(l)}”: a search for the formal term misses it`}</span>
        <p class="snip" style="margin:.4rem 0">“${hilite(sn[3], labels)}”</p>${srcChip(sn[0])}`;
    } else {
      if (!consent.has(i)) {
        out.innerHTML = `<b>Passage ${fmt(i + 1)}</b> · ${esc(PARTS[partAt[i]][1])}<br><span class="muted">Does not use the word “consent”.</span>`;
        return;
      }
      const sn = D.consent.snips[i];
      out.innerHTML = `<b>${esc(sn[1])}</b>${sn[2] && sn[2] !== sn[1] ? ` <span class="muted">› ${esc(sn[2])}</span>` : ''}<br>
        <span class="tiny">${esc(PARTS[partAt[i]][1])}</span>
        <p class="snip" style="margin:.4rem 0">“${hilite(sn[3], ['consent'])}”</p>${srcChip(sn[0])}`;
    }
  }
  function pickDefault() {
    if (mode === 'many') {
      const other = [...owner.entries()].filter(([, li]) => li > 0).map(([i]) => i).sort((a, b) => a - b)[0];
      sel = other !== undefined ? other : [...owner.keys()][0];
    } else sel = D.consent.idx[0];
    info(sel);
  }
  onCell(svg, (i, type) => {
    if (type === 'click') { sel = i; paint(); }
    info(i);
  });
  svg.addEventListener('mouseleave', () => { if (sel >= 0) info(sel); });
  function setMode(m) {
    mode = m;
    $$('[data-wmode]').forEach((b) => b.setAttribute('aria-selected', b.dataset.wmode === m));
    side(); pickDefault(); paint();
  }
  $$('[data-wmode]').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.wmode)));
  setup();
  setMode('many');
  return setMode;
})();

/* ================================================================ 3. ontology: ingredients and ladder */
(function ontologyStop() {
  const k = D.counts;
  const total = k.concepts.signed + k.concepts.machine;
  const s43 = C[idOf('section 43 ground for rejection')];
  const ING = [
    ['Ideas', `${total} of them`, () => `
      <p>An <b>idea</b> (or concept) is one thing people reason about, whatever words are used for it. The demonstrator holds <b>${total}</b>: a trade marks expert reviewed <b>${k.concepts.signed}</b>, and a machine drafted the other <b>${k.concepts.machine}</b> from the Manual's text.</p>
      <div class="row">${['section 41 ground for rejection', 'capable of distinguishing', 'likely to deceive or cause confusion', 'connotation', 'plant variety name', 'geographical reference', 'priority date', 'ordinary consumer', 'applicant', 'examiner', 'examination', 'acceptance', 'opposition', 'evidence of use', 'condition of registration', 'Register of Trade Marks'].map(ideaByLabel).join('')}</div>
      <p class="tiny" style="margin:.6rem 0 0">A solid outline means reviewed by an expert; dashed means machine-written and unreviewed. Click one to open it.</p>`],
    ['Wordings', 'labels, and what an idea is not', () => `
      <p>Each idea has one <b>preferred label</b>, any number of <b>alternative labels</b>, and <b>"not" labels</b>: lookalike wordings that mean something else.</p>
      <p>${ideaByLabel('section 43 ground for rejection')}</p>
      <p class="small" style="margin:.2rem 0">Also written as:</p><div class="row">${s43.alt.map((a) => `<span class="chip" style="cursor:default">${esc(a)}</span>`).join('')}</div>
      <p class="small" style="margin:.6rem 0 .2rem">Not the same as:</p><div class="row">${s43.not.map((a) => `<span class="chip" style="cursor:default">${esc(a)}</span>`).join('')}</div>
      <p class="small muted" style="margin:.8rem 0 0">Matching every idea's wordings against the text, with no AI involved, links ideas to passages <b>${fmt(k.links)}</b> times, across <b>${fmt(k.passages_linked)}</b> of the 2,460 passages.</p>`],
    ['Kinds', '11 kinds, 3 families', () => `
      <p>Every idea is sorted by <b>what it is</b> into one of eleven kinds, grouped into three families: the questions the law asks; what those questions are asked about; and the process around them.</p>
      <div class="row">${D.kinds.map((x) => `<span class="chip" style="cursor:default"><span class="dot" style="--c:${kc(x.id)}"></span>${esc(x.label)}</span>`).join('')}</div>
      <p style="margin:.8rem 0 0"><a class="btn" href="#kinds">Explore the kinds (stop 4)</a></p>`],
    ['Connections', 'named, never vague', () => {
      const r = REL.get('GR-0300');
      return `
      <p>A <b>connection</b> says how one idea bears on another, as a tiny sentence in three parts. Computer scientists call it a <b>triple</b>: subject, connection, object.</p>
      ${relCard(r)}
      <ol class="small" style="margin-top:.8rem">
        <li><b>Every connection type has a name and a meaning</b>, with a written definition, an example and a counter-example, and is marked as law or practice.</li>
        <li><b>There is no vague "is related to".</b> A passage that only mentions two ideas together is not a connection between them.</li>
        <li><b>Every type says which kinds it may join</b>, so a connection between the wrong kinds is caught automatically.</li>
        <li><b>Every connection is pinned to its evidence</b>: the exact sentence it rests on.</li>
      </ol>`;
    }],
    ['Evidence', 'a receipt for every statement', () => `
      <p>Every statement carries a receipt: <b>where</b> (a permanent address for the passage or provision), <b>what</b> (the exact words, checked by a computer letter for letter), and a <b>fingerprint</b> of the text, so a change is noticed (stop 7).</p>
      ${relCard(REL.get('GR-0692'))}
      <p class="small muted" style="margin:.7rem 0 0">This connection rests on the Act itself, so its source is marked with the amber diamond. Nothing in the map is "just known": if the Manual or the legislation does not support a statement, it is not written.</p>`],
    ['Who wrote it', 'reviewed, or machine-drafted', () => `
      <p>Every record is in one of three states, and they never mix: <b>machine-written and unreviewed</b>, <b>reviewed</b> by a named expert on a recorded date, or <b>rejected</b> by one.</p>
      <div class="row">${trust('machine')}<span class="small">${k.concepts.machine} ideas, ${k.relations.machine} connections</span></div>
      <div class="row" style="margin-top:.4rem">${trust('reviewed')}<span class="small">${k.concepts.signed} ideas, ${k.relations.signed} connections</span></div>
      <p class="small" style="margin:.8rem 0 0"><b>A machine-written record never becomes approved by being left alone.</b> Only a recorded human decision changes its state. <a href="#trust">More in stop 10.</a></p>`],
  ];
  const tabs = $('#ing-tabs');
  tabs.innerHTML = ING.map((x, i) => `<button class="ing" role="tab" aria-selected="${i === 0}" data-ing="${i}"><b>${esc(x[0])}</b><span>${esc(x[1])}</span></button>`).join('');
  const show = (i) => {
    $$('[data-ing]', tabs).forEach((b) => b.setAttribute('aria-selected', Number(b.dataset.ing) === i));
    $('#ing-panel').innerHTML = ING[i][2]();
  };
  $$('[data-ing]', tabs).forEach((b) => b.addEventListener('click', () => show(Number(b.dataset.ing))));
  show(0);

  const spec = idOf('specification of goods and services');
  const sc = C[spec];
  const kindOf = KIND.get(sc.k);
  const specRels = RELS.filter((r) => r.s === spec || r.o === spec);
  const isA = RELS.filter((r) => r.p === 'broader' && ['shape trade mark', 'non-traditional sign', 'colour trade mark'].includes(C[r.s] && C[r.s].l));
  const RUNGS = [
    ['An index', 'lists words and the pages they appear on.', () => `
      <p><b>specification</b> · named in ${fmt(sc.m)} passages, in Parts including ${sc.parts.map((p) => p.replace('Part', '')).join(', ')}</p>
      <p class="small muted" style="margin:0">Useful, but it knows nothing about meaning. A passage that says "goods/services claimed" is not listed.</p>`],
    ['A glossary', 'explains what each word means.', () => `
      <p><b>Specification of goods and services</b>: the list of goods and services an application covers.</p>
      <p class="small muted" style="margin:0">Now a reader knows what the term means, but not what else it is called or how it relates to anything.</p>`],
    ['A thesaurus', 'adds synonyms and "see also" links.', () => `
      <p>${ideaChip(spec)}</p>
      <p class="small" style="margin:.2rem 0">Also written as:</p><div class="row">${sc.alt.map((a) => `<span class="chip" style="cursor:default">${esc(a)}</span>`).join('')}</div>
      <p class="small" style="margin:.6rem 0 .2rem">Not the same as:</p><div class="row">${sc.not.map((a) => `<span class="chip" style="cursor:default">${esc(a)}</span>`).join('')}</div>
      <p class="small muted" style="margin:.6rem 0 0">This is what lets search find all 109 passages instead of 3 (stop 2).</p>`],
    ['A taxonomy', 'sorts things into a family tree.', () => `
      <p>The specification sits in the kind <b>${esc(kindOf.label)}</b>, in the family <b>${esc(D.families[kindOf.family])}</b>.</p>
      <p class="small" style="margin:.2rem 0">A taxonomy also records "is a kind of" links:</p>
      <div class="stack">${isA.map((r) => `<div class="rel-line">${ideaChip(r.s)}<span class="pred">${esc(P[r.p])}</span>${ideaChip(r.o)}</div>`).join('')}</div>
      <p class="small muted" style="margin:.6rem 0 0">A family tree, but only one kind of link.</p>`],
    ['An ontology', 'adds kinds, named connections of many types, and rules about what may connect to what.', () => `
      <p>Connections of many types, each pinned to its sentence:</p>
      <div class="stack">${specRels.slice(0, 3).map((r) => relCard(r)).join('')}</div>
      <p class="small muted" style="margin:.6rem 0 0">And rules: a type such as <i>operates on</i> says which kinds it may join, so a connection drawn the wrong way round is caught before anyone sees it.</p>`],
  ];
  const rungs = $('#rungs');
  rungs.innerHTML = RUNGS.map((x, i) => `<button class="rung" role="tab" aria-selected="${i === 4}" data-rung="${i}"><b>${i + 1}</b><span>${esc(x[0])}</span></button>`).join('');
  const showRung = (i) => {
    $$('[data-rung]', rungs).forEach((b) => b.setAttribute('aria-selected', Number(b.dataset.rung) === i));
    $('#rung-panel').innerHTML = `<p class="eyebrow">${esc(RUNGS[i][0])} ${esc(RUNGS[i][1])}</p>${RUNGS[i][2]()}`;
  };
  $$('[data-rung]', rungs).forEach((b) => b.addEventListener('click', () => showRung(Number(b.dataset.rung))));
  showRung(0);
})();

/* ================================================================ 4. kinds */
(function kindsStop() {
  const byKind = new Map(D.kinds.map((k) => [k.id, []]));
  Object.entries(C).forEach(([id, c]) => { if (byKind.has(c.k)) byKind.get(c.k).push(id); });
  const fams = ['reasoning', 'examined', 'process'];
  $('#families').innerHTML = fams.map((f) => `<div class="family"><h3>${esc(D.families[f])}</h3>${D.kinds.filter((k) => k.family === f).map((k) => {
    const ids = byKind.get(k.id);
    const rev = ids.filter((id) => C[id].o === 'reviewed').length;
    return `<button type="button" class="kind" aria-pressed="false" data-kind="${k.id}" style="--c:${kc(k.id)}"><i></i><b>${esc(k.label)}</b><span class="cnt">${ids.length}</span><span class="pl">${esc(k.plain)}</span></button>`;
  }).join('')}</div>`).join('');
  let kind = null;
  const search = $('#idea-search');
  function render() {
    const q = search.value.trim().toLowerCase();
    let ids = kind ? byKind.get(kind) : Object.keys(C);
    if (q) ids = ids.filter((id) => [C[id].l, ...C[id].alt].some((w) => w.toLowerCase().includes(q)));
    ids = ids.slice().sort((a, b) => C[a].l.localeCompare(C[b].l));
    const k = kind && KIND.get(kind);
    $('#kind-title').textContent = k ? `${k.label}` : 'All ideas';
    const rev = ids.filter((id) => C[id].o === 'reviewed').length;
    $('#kind-plain').innerHTML = `${k ? `${esc(k.plain[0].toUpperCase() + k.plain.slice(1))}. ` : 'Pick a kind above to narrow the list. '}${ids.length} idea${ids.length === 1 ? '' : 's'}${q ? ` matching “${esc(q)}”` : ''}: ${rev} reviewed, ${ids.length - rev} machine-written.`;
    $('#kind-ideas').innerHTML = ids.length ? ids.map(ideaChip).join('') : '<span class="small muted">No idea matches. Try another word.</span>';
  }
  $$('[data-kind]').forEach((b) => b.addEventListener('click', () => {
    kind = kind === b.dataset.kind ? null : b.dataset.kind;
    $$('[data-kind]').forEach((x) => x.setAttribute('aria-pressed', x.dataset.kind === kind));
    render();
  }));
  search.addEventListener('input', render);
  render();

  const FL = new Map(D.family_links.map((f) => [`${f.s}>${f.o}`, f]));
  const short = { reasoning: 'The law’s questions', examined: 'What they are asked about', process: 'The process' };
  $('#matrix').innerHTML = `<thead><tr><th>From ↓ · to →</th>${fams.map((f) => `<th>${short[f]}</th>`).join('')}</tr></thead><tbody>${fams.map((s) => `<tr><th>${short[s]}</th>${fams.map((o) => {
    const f = FL.get(`${s}>${o}`);
    return f ? `<td><b>${f.total}</b>${f.top.slice(0, 2).map(([p, n]) => `${esc(p)} ${n}`).join('<br>')}</td>` : '<td class="muted">0</td>';
  }).join('')}</tr>`).join('')}</tbody>`;

  const pc = new Map();
  RELS.forEach((r) => pc.set(r.p, (pc.get(r.p) || 0) + 1));
  const preds = [...pc.entries()].sort((a, b) => b[1] - a[1]);
  $('#pred-list').innerHTML = preds.map(([p, n]) => `<button type="button" class="chip" data-pred="${p}">${esc(P[p] || p)} · ${n}</button>`).join('');
  $$('[data-pred]').forEach((b) => b.addEventListener('click', () => {
    const p = b.dataset.pred;
    $$('[data-pred]').forEach((x) => x.setAttribute('aria-pressed', x.dataset.pred === p));
    const rs = RELS.filter((r) => r.p === p);
    $('#pred-rels').innerHTML = `<p class="small muted" style="margin:0">${rs.length} connection${rs.length === 1 ? '' : 's'} use <i>${esc(P[p] || p)}</i>.</p>` + rs.map((r) => relCard(r)).join('');
  }));
})();

/* ================================================================ 5. three small maps */
const selectMap = (function mapsStop() {
  const MAPS = {
    A: {
      tab: 'A · A well-known person’s name', first: 'GR-0686',
      text: `<h3>A well-known person's name</h3>
        <p><b>The situation.</b> An application is for a trade mark that includes the name or image of a well-known person. What does the guidance say? It sits mainly in Part 29 of the Manual: section 43, trade marks likely to deceive or cause confusion.</p>
        <p><b>Read the map.</b> In a handful of arrows it shows when the ground may arise, when it does not, how it can be overcome and what record that leaves. Each arrow opens onto the sentence that supports it. A search box would return a list of passages and leave you to assemble the picture.</p>
        <p><b>The law, kept apart.</b> The ground comes from section 43 of the Act, the amber box. The detail about well-known persons, permission and endorsements is Manual practice.</p>
        <p><b>The “consent” trap.</b> The Manual often says “consent”, but a letter of consent under section 44 is a different idea altogether (stop 2).</p>`,
      spec: { w: 860, h: 470, minW: 640, label: 'Map: a well-known person’s name under section 43', nodes: [
        { ref: 'TMA1995/s43', x: 450, y: 50 },
        { label: 'well-known person', x: 135, y: 70 },
        { label: 'implied endorsement', x: 135, y: 200 },
        { label: 'image of a person', x: 135, y: 315 },
        { label: 'deceased person', x: 135, y: 425 },
        { label: 'section 43 ground for rejection', x: 450, y: 235 },
        { label: 'presumption of registrability', x: 450, y: 410 },
        { label: 'written permission', x: 720, y: 235 },
        { label: 'endorsement', x: 720, y: 410 },
      ], edges: [{ rel: 'GR-0678' }, { rel: 'GR-0686' }, { rel: 'GR-0040' }, { rel: 'GR-0688' }, { rel: 'GR-0700' }, { rel: 'GR-0682' }, { rel: 'GR-0687' }, { rel: 'GR-0435' }] },
    },
    B: {
      tab: 'B · “Not capable of distinguishing”', first: 'GR-0692',
      text: `<h3>An objection that a mark is “not capable of distinguishing”</h3>
        <p><b>The situation.</b> A common objection is that a trade mark is not capable of distinguishing the applicant's goods or services from other people's: section 41 of the Act. What does that mean, and what can be done about it?</p>
        <p><b>Read the map.</b> The top arrow rests on the Act itself. The rest is Manual practice: the three categories a mark can fall into, and how evidence of use can show a mark does distinguish. The Manual has a whole Part on overcoming this ground (Part 23), with an annex on how to supply evidence of use. The map links the objection, the test, the remedy and the how-to guide, though they sit in different Parts.</p>
        <p><b>Why it helps.</b> An examiner sees the route from the Act's test to the practice on evidence. An applicant can understand what an objection asks of them. Neither is told whether <i>their</i> evidence will be enough; that stays the examiner's judgement.</p>`,
      spec: { w: 860, h: 450, minW: 640, label: 'Map: section 41 and evidence of use', nodes: [
        { label: 'capable of distinguishing', x: 340, y: 60 },
        { label: 'section 41 ground for rejection', x: 700, y: 60 },
        { label: 'prima facie capable of distinguishing', x: 700, y: 250 },
        { label: 'no inherent adaptation to distinguish', x: 340, y: 250 },
        { label: 'evidence of use', x: 110, y: 155 },
        { label: 'trade mark attorney', x: 110, y: 395 },
        { label: 'use of a trade mark', x: 380, y: 400 },
      ], edges: [{ rel: 'GR-0692' }, { rel: 'GR-0088' }, { rel: 'GR-0575' }, { rel: 'GR-0300' }, { rel: 'GR-0206' }, { rel: 'GR-0668' }, { rel: 'GR-0248' }] },
    },
    C: {
      tab: 'C · Who does what, in what order', first: 'GR-0617',
      text: `<h3>The process: who does what, in what order</h3>
        <p><b>The situation.</b> The ontology is not only about legal tests. It also maps the process: roles, steps and records, joined by verbs that mean something.</p>
        <p><b>Read the map.</b> An applicant is party to an application; an examiner performs examination; examination precedes acceptance; a ground for rejection or a deferment prevents acceptance. An examiner is a kind of delegate, and a delegate holds delegation from the Registrar under section 206 of the Act. The Registrar keeps the Register of Trade Marks (section 207).</p>
        <p><b>Why it helps.</b> A newcomer, a new examiner or a first-time applicant, can see the process as a picture: who acts, what happens next, and what each step produces.</p>`,
      spec: { w: 900, h: 470, minW: 660, label: 'Map: the examination process', nodes: [
        { label: 'applicant', x: 105, y: 60 },
        { label: 'trade mark application', x: 120, y: 240 },
        { label: 'examiner', x: 370, y: 60 },
        { label: 'examination', x: 370, y: 240 },
        { label: 'acceptance', x: 630, y: 240 },
        { label: 'ground for rejection', x: 370, y: 410 },
        { label: 'deferment of acceptance', x: 640, y: 410 },
        { label: 'delegate', x: 570, y: 60 },
        { label: 'Registrar', x: 805, y: 60 },
        { label: 'Register of Trade Marks', x: 805, y: 250 },
      ], edges: [{ rel: 'GR-0675' }, { rel: 'GR-0619' }, { rel: 'GR-0460' }, { rel: 'GR-0617' }, { rel: 'GR-0394' }, { rel: 'GR-0259' }, { rel: 'GR-0643' }, { rel: 'GR-0639', ly: -10 }, { rel: 'GR-0713' }] },
    },
  };
  const tabs = $('#map-tabs');
  tabs.innerHTML = Object.entries(MAPS).map(([k, m]) => `<button class="tab" role="tab" aria-selected="${k === 'A'}" data-map="${k}">${esc(m.tab)}</button>`).join('');
  function show(key) {
    const m = MAPS[key];
    $$('[data-map]', tabs).forEach((b) => b.setAttribute('aria-selected', b.dataset.map === key));
    $('#map-text').innerHTML = m.text;
    const card = $('#map-card');
    const g = drawGraph($('#map-graph'), m.spec, {
      onEdge: (r) => { card.innerHTML = relCard(r); },
      onLaw: (ref) => { card.innerHTML = lawCard(ref); g.select(null); },
    });
    g.select(m.first);
  }
  $$('[data-map]', tabs).forEach((b) => b.addEventListener('click', () => show(b.dataset.map)));
  show('A');
  $$('[data-goto-map]').forEach((b) => b.addEventListener('click', () => { show(b.dataset.gotoMap); scrollToEl($('#maps')); }));
  return show;
})();

/* ================================================================ 6. ask the manual */
const selectAsk = (function askStop() {
  const TABS = { 'BN-0017': 'A well-known person’s name', 'BN-0077': 'A rose variety name', 'BN-0022': 'A wine region name' };
  const tabs = $('#ask-tabs');
  tabs.innerHTML = D.ask.map((a, i) => `<button class="tab" role="tab" aria-selected="${i === 0}" data-ask="${a.key}">${esc(TABS[a.key] || a.key)}</button>`).join('');
  const pips = (g) => `<span class="pips" title="Graded ${g == null ? 'not graded' : g + ' of 3'}">${[1, 2, 3].map((n) => `<i class="${(g || 0) >= n ? 'on' : ''}"></i>`).join('')}</span>`;
  function shortRef(ref) {
    const p = D.passages[ref];
    if (!p) return srcLabel(ref);
    const h = p[1] || p[0];
    return `Part ${partNo(ref)} · ${h.length > 70 ? h.slice(0, 68).replace(/\s+\S*$/, '') + ' …' : h}`;
  }
  function passageView(ref) {
    const p = D.passages[ref] || ['', '', '', ''];
    return `<div class="rel-card"><p class="small" style="margin:0"><b>${esc(p[0])}</b>${p[1] && p[1] !== p[0] ? ` › ${esc(p[1])}` : ''}</p>${quote(ref, p[2])}<div class="rel-meta">${srcChip(ref)}</div></div>`;
  }
  function inline(s) {
    let h = esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    h = h.replace(/\[([^\]]+)\]/g, (m, inner) => {
      const parts = inner.split(/;\s*/);
      if (parts.every((x) => /^(TMA1995|TMR1995|TMM)\/\S+$/.test(x))) return parts.map((x) => srcChip(x.replace(/&amp;/g, '&'))).join(' ');
      return m;
    });
    return h;
  }
  function renderAnswer(t) {
    return t.split(/\n\s*\n/).map((b) => {
      const lines = b.split('\n').map((x) => x.trim()).filter(Boolean);
      if (lines.length && lines.every((l) => /^[•\-*]\s/.test(l))) return `<ul>${lines.map((l) => `<li>${inline(l.replace(/^[•\-*]\s+/, ''))}</li>`).join('')}</ul>`;
      return `<p>${lines.map(inline).join('<br>')}</p>`;
    }).join('');
  }
  function show(key) {
    const a = D.ask.find((x) => x.key === key);
    $$('[data-ask]', tabs).forEach((b) => b.setAttribute('aria-selected', b.dataset.ask === key));
    // 1. recognise
    const ids = a.recognised.map(idOf).filter(Boolean);
    const words = [];
    ids.forEach((id) => {
      const c = C[id];
      const hit = [c.l, ...c.alt].sort((x, y) => y.length - x.length).find((w) => a.q.toLowerCase().includes(w.toLowerCase()));
      if (hit) words.push(hit);
    });
    $('#ask-q').innerHTML = `“${hilite(a.q, words)}”`;
    $('#ask-1').innerHTML = ids.length
      ? `<div class="row">${ids.map((id, i) => `${ideaChip(id)}${words[i] && words[i].toLowerCase() !== C[id].l.toLowerCase() ? `<span class="tiny">from “${esc(words[i])}”</span>` : ''}`).join('')}</div>
         <p class="tiny" style="margin:.4rem 0 0">Matched against every idea's wordings, including everyday phrasings.</p>`
      : `<p class="small" style="margin:0">No idea on the map matched these words, so this question fell back to ordinary search: here the ontology's results equal the meaning-based search's. An honest case: the map helps only where it recognises something.</p>`;
    // 2. follow
    $('#ask-2').innerHTML = a.paths.length
      ? `<div class="stack">${a.paths.map((p) => `<div class="rel-line">${ideaByLabel(p[0])}<span class="pred">${esc(p[1])}</span>${ideaByLabel(p[2])}${trust(p[3])}</div>`).join('')}</div>
         <p class="tiny" style="margin:.4rem 0 0">Connections as they stood when this answer was prepared. Following them brings in passages the question's own words do not reach.</p>`
      : '<p class="small muted" style="margin:0">Nothing to follow.</p>';
    // 3. gather and rank
    const kw = new Set(a.keyword.map((x) => x[0]));
    const hy = new Set(a.hybrid.map((x) => x[0]));
    const only = new Set(a.ontology.filter(([r, g]) => !kw.has(r) && !hy.has(r) && (g || 0) >= 2).map((x) => x[0]));
    const col = (title, list, score, mark) => `<div class="list"><h5>${title}<span>${Math.round(score * 100)}</span></h5><ol>${list.map(([r, g]) => `<li><span class="li">${pips(g)}<button type="button" data-pass="${esc(r)}">${esc(shortRef(r))}</button>${mark && only.has(r) ? '<span class="only">only the ontology found this</span>' : ''}</span></li>`).join('')}</ol></div>`;
    $('#ask-3').innerHTML = `<div class="lists">${col('Keyword search', a.keyword, a.ndcg.keyword, false)}${col('Meaning-based search', a.hybrid, a.ndcg.hybrid, false)}${col('With the ontology', a.ontology, a.ndcg.ontology, true)}</div>
      <p class="tiny" style="margin:.5rem 0 0">Each system's top ten. Green bars: how relevant a grading model judged each passage, 0 to 3. The number beside each heading is the top ten's quality out of 100. ${only.size ? `<b>${only.size}</b> relevant passage${only.size === 1 ? '' : 's'} appeared only in the ontology's top ten.` : 'No relevant passage appeared only in the ontology’s top ten here.'} Click a passage to read it.</p>
      <div class="passage-view" id="ask-pass"></div>`;
    const firstPass = [...only][0] || a.ontology[0][0];
    $('#ask-pass').innerHTML = passageView(firstPass);
    $$('[data-pass]', $('#ask-3')).forEach((b) => b.addEventListener('click', () => { $('#ask-pass').innerHTML = passageView(b.dataset.pass); }));
    // 4. answer
    const d = a.date.split('-');
    const when = new Date(Number(d[0]), Number(d[1]) - 1, Number(d[2])).toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });
    $('#ask-4').innerHTML = `
      <div class="stamp"><span class="trust mac">Machine · unreviewed</span><span>Written by a language model on ${esc(when)}, from the passages it was given. A computer then checked every quote word for word against the source.</span></div>
      ${a.declined ? `<div class="stamp declined" style="margin-top:.5rem"><b style="white-space:nowrap">Declined to predict.</b><span>${esc(a.decline_reason)}</span></div>` : ''}
      <div class="panel answer" style="margin-top:.6rem">${renderAnswer(a.answer)}</div>
      <details style="margin-top:.6rem"><summary class="small" style="cursor:pointer">The ${a.citations.length} quotes it relied on, each found word for word in the source</summary>
        <ol class="cites">${a.citations.map(([r, q]) => `<li>${srcChip(r)}<br><span class="muted">“${esc(q.length > 260 ? q.slice(0, 258).replace(/\s+\S*$/, '') + ' …' : q)}”</span></li>`).join('')}</ol></details>`;
  }
  $$('[data-ask]', tabs).forEach((b) => b.addEventListener('click', () => show(b.dataset.ask)));
  show(D.ask[0].key);
  return show;
})();

/* ================================================================ 7. change */
(function changeStop() {
  const years = Object.entries(D.stability.by_year);
  const max = Math.max(...years.map(([, n]) => n));
  const yb = $('#yearbars');
  yb.setAttribute('aria-label', `Amendments by year: ${years.map(([y, n]) => `${y}, ${n}`).join('; ')}`);
  yb.innerHTML = years.map(([y, n]) => `<div><span class="v">${fmt(n)}</span><i style="height:${Math.max(2, (n / max) * 120)}px"></i><span>${y}${y === '2026' ? '*' : ''}</span></div>`).join('');
  const rs = D.stability.reasons;
  const rmax = rs[0][1];
  $('#reasons').innerHTML = rs.map(([r, n]) => bar(r, n, rmax)).join('');

  const partSel = $('#chg-part'), pageSel = $('#chg-page');
  const parts = Object.entries(D.stability.part_titles);
  partSel.innerHTML = parts.map(([id, t]) => `<option value="${esc(id)}">${esc(t)}</option>`).join('');
  function fillPages(part) {
    const pages = D.pages.filter((p) => p[2] === part);
    pageSel.innerHTML = pages.map((p) => `<option value="${esc(p[0])}">${esc(p[1])}${p[5].length ? ` · ${p[5].length} connection${p[5].length === 1 ? '' : 's'}` : ''}</option>`).join('');
  }
  function showPage(ref) {
    const p = PAGE.get(ref);
    if (!p) return;
    const rels = p[5].map((id) => REL.get(id)).filter(Boolean);
    const last = p[8];
    $('#chg-out').innerHTML = `<div class="panel">
      <h4 style="margin:0 0 .2rem">${p[3] ? `<a href="${esc(p[3])}" target="_blank" rel="noopener">${esc(p[1])}</a>` : esc(p[1])}</h4>
      <p class="tiny" style="margin:0 0 .7rem">${esc(partTitle(p[2]))} · ${p[4]} passage${p[4] === 1 ? '' : 's'} · amended ${p[7]} time${p[7] === 1 ? '' : 's'}${last ? ` · last ${esc(last[0])}: “${esc(last[1].length > 110 ? last[1].slice(0, 108).replace(/\s+\S*$/, '') + ' …' : last[1])}”` : ''}</p>
      ${rels.length
        ? `<p class="small"><b>${rels.length} connection${rels.length === 1 ? '' : 's'} quote${rels.length === 1 ? 's' : ''} this page.</b> If it were rewritten, ${rels.length === 1 ? 'that one' : 'these'} would be flagged for a person to re-check. Everything else on the map stays as it is.</p><div class="stack">${rels.map((r) => relCard(r)).join('')}</div>`
        : `<p class="small" style="margin:0"><b>Nothing on the map quotes this page.</b> ${p[6] ? `${p[6]} idea${p[6] === 1 ? ' is' : 's are'} named on it; those links come from matching wordings, so a rewrite would simply be matched again.` : 'No idea is named on it either.'}</p>`}
    </div>`;
  }
  partSel.addEventListener('change', () => { fillPages(partSel.value); showPage(pageSel.value); });
  pageSel.addEventListener('change', () => showPage(pageSel.value));
  partSel.value = 'Part29';
  fillPages('Part29');
  pageSel.value = 'TMM/Part29/6';
  showPage('TMM/Part29/6');

  // fingerprint
  function fnv(s, seed) {
    let h = seed >>> 0;
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return h.toString(16).padStart(8, '0');
  }
  const fp = (s) => fnv(s, 2166136261) + fnv(s, 0x9e3779b9);
  const r = REL.get('GR-0687');
  const ta = $('#fp-text');
  ta.value = r.quote;
  const stored = fp(r.quote);
  function check() {
    const now = fp(ta.value);
    const same = now === stored;
    $('#fp-out').innerHTML = `<div class="small num" style="font-family:var(--mono)">stored&nbsp;&nbsp;${stored}<br>now&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:${same ? 'var(--ok)' : 'var(--bad)'}">${now}</span></div>
      ${same
        ? '<p class="small" style="margin:.5rem 0 0;color:var(--ok)"><b>Matches.</b> Nothing to re-check.</p>'
        : `<p class="small" style="margin:.5rem 0 .4rem;color:var(--bad)"><b>Changed.</b> This connection would be flagged for a person to re-check:</p>${relLine(r)}<p style="margin:.6rem 0 0"><button type="button" class="btn" id="fp-reset">Put the original back</button></p>`}`;
    const reset = $('#fp-reset');
    if (reset) reset.addEventListener('click', () => { ta.value = r.quote; check(); });
  }
  ta.addEventListener('input', check);
  check();
})();

/* ================================================================ 8. who it helps */
(function usesStop() {
  const BEST = [
    ['When two series marks use the same common surname and initial, is that usually the part people focus on to compare them?', 'Crosses Parts', 64.8, 91.0],
    ['What do I do if the goods and services wording in my international trade mark application does not fit the usual classification terms?', 'Everyday words', 76.0, 93.4],
    ['How long do I have to notify a provisional refusal if it is based on an opposition?', 'Looking something up', 69.1, 85.7],
  ];
  $('#best-cases').innerHTML = BEST.map(([q, k, h, o]) => `<div><p style="margin:0 0 .3rem;font-family:var(--serif)">“${esc(q)}”</p>
    <div class="bars">${bar('Meaning-based search', h, 100, 'var(--ink-3)')}${bar('With the ontology', o, 100, 'var(--accent)')}</div><span class="tiny">${esc(k)}</span></div>`).join('');
  $('#applicant-qs').innerHTML = D.ask.map((a) => `<button type="button" class="btn" style="text-align:left;border-radius:10px;justify-content:flex-start" data-open-ask="${a.key}">“${esc(a.q)}”</button>`).join('');
  $$('[data-open-ask]').forEach((b) => b.addEventListener('click', () => { selectAsk(b.dataset.openAsk); scrollToEl($('#ask')); }));
  $$('[data-use]').forEach((b) => b.addEventListener('click', () => {
    $$('[data-use]').forEach((x) => x.setAttribute('aria-selected', x === b));
    $('#use-examiners').hidden = b.dataset.use !== 'examiners';
    $('#use-applicants').hidden = b.dataset.use !== 'applicants';
  }));
})();

/* ================================================================ 9. measured */
(function measuredStop() {
  // nDCG@10 x 100 and paired-bootstrap 95% intervals, measured 9 October 2026 (data/derived/reports/measure.md).
  // est: whether the interval excludes zero, as the report marks it.
  const M = [
    ['All questions', 129, 72.5, 84.4, 80.3, [7.9, 4.2, 11.6, true], [-4.1, -6.7, -1.7, true]],
    ['Everyday problems', 29, 67.7, 84.8, 82.7, [15.1, 8.1, 22.8, true], [-2.1, -5.5, 1.0, false]],
    ['Looking something up', 30, 77.3, 89.4, 82.0, [4.6, -1.5, 11.0, false], [-7.5, -12.9, -2.5, true]],
    ['Questions that cross Parts', 30, 72.8, 83.2, 77.8, [5.0, -1.5, 12.5, false], [-5.4, -11.6, -0.0, true]],
    ['What a provision changes', 30, 73.2, 83.7, 80.2, [7.0, -2.3, 17.1, false], [-3.6, -9.9, 1.7, false]],
    ['The expert-reviewed 10', 10, 68.6, 73.5, 76.6, [8.0, -2.4, 17.7, false], [3.0, 0.8, 5.5, true]],
  ];
  const sgn = (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(1);
  function chart(which) {
    const W = 600, rowH = 48, top = 26, left = 8, right = 150, H = top + M.length * rowH + 8;
    const lo = -15, hi = 25;
    const x = (v) => left + ((v - lo) / (hi - lo)) * (W - left - right);
    let s = `<svg class="ci" viewBox="0 0 ${W} ${H}" role="img" aria-label="Difference in top-ten quality, ontology ${which === 'kw' ? 'minus keyword' : 'minus hybrid'}, with 95% intervals">`;
    for (let t = lo; t <= hi; t += 5) s += `<line class="${t === 0 ? 'zero' : 'grid'}" x1="${x(t)}" x2="${x(t)}" y1="${top - 6}" y2="${H - 4}"/><text x="${x(t)}" y="${top - 10}" text-anchor="middle">${t > 0 ? '+' + t : t === 0 ? '0' : '−' + Math.abs(t)}</text>`;
    M.forEach((m, i) => {
      const v = which === 'kw' ? m[5] : m[6];
      const y = top + i * rowH + 30;
      const cls = !v[3] ? 'unk' : v[0] > 0 ? 'pos' : 'neg';
      s += `<text class="lab" x="${left}" y="${y - 13}">${esc(m[0])} (${m[1]})</text>`;
      s += `<line class="iv ${cls}" x1="${x(v[1])}" x2="${x(v[2])}" y1="${y}" y2="${y}"/><circle class="${cls}" cx="${x(v[0])}" cy="${y}" r="5"/>`;
      s += `<text x="${W - right + 12}" y="${y + 4}">${sgn(v[0])} [${sgn(v[1])}, ${sgn(v[2])}]</text>`;
    });
    s += '</svg>';
    $('#ci-chart').innerHTML = s;
    $('#ci-note').innerHTML = which === 'kw'
      ? 'Right of zero: the ontology ranked better than keyword search. Green: a clear difference; grey: the interval crosses zero.'
      : 'Left of zero: the ontology ranked worse than good modern search. Red: clearly worse; green: clearly better; grey: no clear difference.';
  }
  $$('[data-cmp]').forEach((b) => b.addEventListener('click', () => {
    $$('[data-cmp]').forEach((x) => x.setAttribute('aria-selected', x === b));
    chart(b.dataset.cmp);
  }));
  chart('kw');
  $('#meas-table').innerHTML = `<thead><tr><th>Questions</th><th class="n">n</th><th class="n">Keyword</th><th class="n">Hybrid</th><th class="n">Ontology</th><th class="n">Ontology − keyword</th><th class="n">Ontology − hybrid</th></tr></thead><tbody>${M.map((m) => `<tr><td>${esc(m[0])}</td><td class="n">${m[1]}</td><td class="n">${m[2].toFixed(1)}</td><td class="n">${m[3].toFixed(1)}</td><td class="n">${m[4].toFixed(1)}</td><td class="n">${sgn(m[5][0])} <span class="tiny">[${sgn(m[5][1])}, ${sgn(m[5][2])}]</span></td><td class="n">${sgn(m[6][0])} <span class="tiny">[${sgn(m[6][1])}, ${sgn(m[6][2])}]</span></td></tr>`).join('')}</tbody>`;
})();

/* ================================================================ 11. build */
(function buildStop() {
  const R = [
    ['Start from the authoritative text, and freeze a copy', 'Give every passage and provision a permanent address. Never edit the source to suit the model.', 'A separate tool captured the Manual and the legislation with no AI involved: 2,460 passages and 763 provisions, each with a permanent address. 97% of the Manual’s references to a provision matched automatically.'],
    ['Say what it is for', 'Write down the questions it must help answer (competency questions) and the things it must never do (prohibited uses).', 'An expert reviewed test questions and a list of things the system must never do, such as stating an examination outcome.'],
    ['List the ideas, with every wording', 'The formal term, the variants and the everyday phrasings. Also record what each idea is not.', `${Object.keys(C).length} ideas. Matching their wordings against the text, with no AI, produced ${fmt(D.counts.links)} links across ${fmt(D.counts.passages_linked)} passages.`],
    ['Sort the ideas into a few kinds', 'Kinds say what an idea is; connections say what it does.', 'Eleven kinds in three families was enough for trade marks examination.'],
    ['Connect them with named relationships', 'Never a vague "related to". Each type has a definition and says which kinds it may join.', 'About fifty types. A catch-all "is related to" was tried and retired because it told the reader nothing.'],
    ['Pin every statement to its evidence', 'Quote the exact sentence, record its address, keep a fingerprint.', 'Software, not the model, found every quote letter for letter in the source and recorded its address and fingerprint, refusing any reply that failed.'],
    ['Label who wrote what', 'Keep machine drafts and expert approvals apart. Nothing becomes approved by being left alone.', 'Machine drafts are stamped "unreviewed" with the model and the date. The expert-reviewed set is frozen and kept separate as a yardstick.'],
    ['Check it automatically', 'Shape rules catch missing evidence, wrong-way connections and duplicate names before anything is published.', 'The shape checks (SHACL) report 0 defects, and all 164 ideas sit in one connected map.'],
    ['Put it to work', 'Search, question answering, a browsable map, training and impact analysis.', 'Ask the Manual, a map at three levels of detail, a guided tour, and “what would a rewrite touch”.'],
    ['Measure honestly', 'Compare against the best ordinary search, not a weak one, and report the results that go against you.', 'Both comparisons are reported: better than keyword search, slightly behind good modern search (stop 9).'],
    ['Review and maintain', 'Have experts review a sample first, for a measured error rate. Then re-check what the fingerprints flag as the text changes.', 'The next step for this demonstrator: examiners review a sample of the machine’s work.'],
  ];
  $('#recipe').innerHTML = R.map(([t, b, h], i) => `<li><details${i === 0 ? ' open' : ''}><summary><b>${esc(t)}</b></summary><div class="body"><p style="margin:0">${esc(b)}</p><p class="here" style="margin-bottom:0"><b>Here:</b> ${esc(h)}</p></div></details></li>`).join('');
})();

/* ================================================================ 12. check yourself */
(function quizStop() {
  const page = PAGE.get('TMM/Part29/6');
  const n = page ? page[5].length : 0;
  const Q = [
    ['Is the Trade Marks Manual law?', ['Yes, it is legislation', 'No. It records the Registrar’s practice; the Act and the Regulations are the law', 'Only the parts that quote the Act'], 1,
      'The Manual states practice and does not bind the Registrar’s discretion. The map keeps it visibly apart from the Act and the Regulations, including inside answers.'],
    ['A passage mentions “evidence of use” and “opposition” in the same sentence. Is that a connection between them?', ['Yes, appearing together is a connection', 'Only if a sentence supports a named relationship, such as “is overcome by”', 'Only if both ideas were reviewed'], 1,
      'A co-mention is not a relationship. Re-checking 226 vague or misfiled links kept 130 with a real meaning and withdrew 96.'],
    ['A machine-written connection has been on the map for a year and nobody has objected. What is its status?', ['Approved, by default', 'Still machine-written and unreviewed', 'Rejected'], 1,
      'Silence never approves anything. Only a recorded decision by a person changes a record’s state.'],
    ['An applicant asks: “Will my trade mark be accepted?” What should the system do?', ['Predict the outcome with a confidence score', 'Decline to predict, and explain the relevant practice and law with sources', 'Refuse to say anything'], 1,
      'It never states an examination outcome. The prepared answers do exactly this: “I cannot determine the outcome of your particular application”, followed by the test and the practice.'],
    ['Is “remedy” one of the kinds of idea?', ['Yes', 'No. Being a remedy is a role, recorded as a connection such as “is overcome by”', 'Only for section 43'], 1,
      'Kinds say what an idea is; connections say what it does. Evidence of use is an instrument or record; that it can overcome a ground is a connection.'],
    ['Part 29’s page on names of persons is rewritten. What can the map tell you?', ['Nothing until everything is rebuilt', 'Exactly which connections quote that page and need re-checking', 'That every idea must be reviewed again'], 1,
      `Each connection stores the address and a fingerprint of the text it quotes. On that page, ${n} connections would be flagged; everything else stays as it is.`],
  ];
  const answered = new Map();
  const host = $('#quiz');
  host.innerHTML = Q.map(([q, opts], qi) => `<div class="qz" id="qz${qi}"><p>${qi + 1}. ${esc(q)}</p><div class="opts">${opts.map((o, oi) => `<button type="button" class="opt" data-q="${qi}" data-o="${oi}">${esc(o)}</button>`).join('')}</div><div class="why" hidden></div></div>`).join('');
  $$('.opt', host).forEach((b) => b.addEventListener('click', () => {
    const qi = Number(b.dataset.q), oi = Number(b.dataset.o);
    const [, , right, why] = Q[qi];
    const box = $(`#qz${qi}`);
    $$('.opt', box).forEach((x) => x.classList.remove('right', 'wrong'));
    b.classList.add(oi === right ? 'right' : 'wrong');
    if (oi !== right) $(`.opt[data-o="${right}"]`, box).classList.add('right');
    const w = $('.why', box);
    w.hidden = false;
    w.innerHTML = `<b>${oi === right ? 'Right.' : 'Not quite.'}</b> ${esc(why)}`;
    if (!answered.has(qi)) answered.set(qi, oi === right);
    const got = [...answered.values()].filter(Boolean).length;
    $('#quiz-score').textContent = answered.size === Q.length ? `${got} of ${Q.length} right first time.` : `${answered.size} of ${Q.length} answered.`;
  }));
})();

/* ================================================================ 13. reference */
(function referenceStop() {
  const k = D.counts;
  const FAQ = [
    ['Is this just AI?', 'No. The ontology is a structured map that people can read, check and correct. AI helped draft parts of it, and every AI-drafted part says so. An AI assistant can use the map to find better evidence and show its working, but the map is useful on its own.'],
    ['Does it make decisions about trade marks?', 'No. It never states an examination outcome, never predicts whether an application will be accepted and never says how likely it is that a ground applies. When asked, it declines and explains the general practice instead.'],
    ['Does it replace the Manual?', 'No. It points into the Manual and the legislation, which remain the authority. Every statement it makes cites the exact sentence it rests on.'],
    ['Is the Manual the law?', 'No. The Manual is the Registrar’s practice. The Trade Marks Act 1995 and the Trade Marks Regulations 1995 are the law. The ontology keeps them visibly apart, including inside answers.'],
    ['Who checked it?', `A trade marks expert reviewed ${k.concepts.signed} of the ${k.concepts.signed + k.concepts.machine} ideas, ${k.relations.signed} of the ${k.relations.signed + k.relations.machine} connections and ten test questions. Everything else was drafted by a machine and is labelled unreviewed. The next step would be examiners reviewing it, starting with a sample.`],
    ['What happens when the Manual changes?', 'Every connection stores a fingerprint of the exact text it quotes. When a page changes, the system lists exactly which connections need re-checking and leaves the rest alone.'],
    ['How is this different from a search engine?', 'A search engine matches words. The ontology knows that different words can name the same idea, that one word can name different ideas, how ideas affect one another, and where each of those facts is written down. It can also show why a passage was found.'],
    ['Why not just ask a chatbot?', 'A chatbot on its own can sound confident without showing where its answer came from. Grounding it in the ontology means the answer is built only from real passages, follows visible connections, keeps practice and law apart, and has every quote checked word for word by a computer.'],
    ['What did it cost?', 'About US$8.40 in AI model calls for the whole demonstrator. The real cost of an ontology is expert time to review it and keep it current.'],
    ['Could applicants use it?', 'The same ontology could power plain-language guidance for applicants: what the requirements are, how the process works and what an objection means. It would always show its sources and never predict an outcome. This has not been built yet.'],
  ];
  $('#faq').innerHTML = FAQ.map(([q, a]) => `<details class="faq"><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join('');
  const F = [
    ['Manual pages / Parts / passages', '500 / 54 / 2,460'],
    ['Act provisions / Regulations provisions', '316 / 447 (763 in all)'],
    ['Manual references to provisions matched automatically', '97% (2,611 of 2,687)'],
    ['Ideas (concepts)', `${k.concepts.signed + k.concepts.machine}: ${k.concepts.signed} expert-reviewed, ${k.concepts.machine} machine-written and unreviewed`],
    ['Kinds of idea', '11, in 3 families'],
    ['Named connection types', 'about 50'],
    ['Connections between ideas', `${k.relations.signed + k.relations.machine}: ${k.relations.signed} expert-reviewed, ${k.relations.machine} machine-written and unreviewed`],
    ['Links from ideas to passages (matching wordings)', `${fmt(k.links)}, across ${fmt(k.passages_linked)} passages`],
    ['Ideas in one connected map', `${k.concepts.signed + k.concepts.machine} of ${k.concepts.signed + k.concepts.machine}`],
    ['Automatic quality-check (SHACL) defects', '0'],
    ['Amendments recorded on Manual pages since 2021', fmt(D.stability.events)],
    ['Pages holding a passage some connection quotes', `${D.pages.filter((p) => p[5].length).length} of ${D.pages.length}`],
    ['Benchmark questions', '129 (119 machine-written, 10 expert-reviewed)'],
    ['Prepared answers', '129; each has at least one computer-verified citation, 4.7 on average; 86 also cite the Act or Regulations; 16 declined the part asking for an outcome'],
    ['Top-ten quality, all questions (keyword / hybrid / ontology)', '72.5 / 84.4 / 80.3'],
    ['Ontology vs keyword', '+7.9 (95% interval +4.2 to +11.6); everyday questions +15.1'],
    ['Ontology vs hybrid', '−4.1 (95% interval −6.7 to −1.7)'],
    ['Recorded AI model spend, whole demonstrator', 'about US$8.40'],
  ];
  $('#facts').innerHTML = `<tbody>${F.map(([a, b]) => `<tr><td>${esc(a)}</td><td class="n" style="white-space:normal">${esc(b)}</td></tr>`).join('')}</tbody>`;
  const G = [
    ['Ontology', 'A shared, explicit description of a field: its ideas, what kind of thing each is, and how they relate.'],
    ['Knowledge graph', 'The actual content held in the shape the ontology describes: the specific ideas, connections, passages and provisions.'],
    ['Idea (concept)', 'One thing people reason about, whatever words are used for it.'],
    ['Label (wording)', 'A word or phrase used for an idea. One is preferred; others are alternatives. A "not" label is a lookalike wording that means something else.'],
    ['Kind', 'What sort of thing an idea is, such as a ground of refusal, a legal test or a procedural step.'],
    ['Connection (relationship)', 'A named link saying how one idea bears on another, such as "is overcome by" or "may give rise to".'],
    ['Triple', 'One statement in three parts: subject, connection, object.'],
    ['Evidence (source span)', 'The exact quoted sentence a statement rests on, with its address.'],
    ['Fingerprint (content hash)', 'A short code computed from exact text. It changes if the text changes.'],
    ['Unreviewed', 'Written by a machine and not yet checked by a person.'],
    ['Reviewed (approved)', 'Checked and accepted by a named expert on a recorded date.'],
    ['Impact analysis', 'Working out what is affected when a passage or provision changes.'],
    ['The Manual', 'The Trade Marks Manual of Practice and Procedure: the Registrar’s examination practice. Not law.'],
    ['The Act, the Regulations', 'The Trade Marks Act 1995 and the Trade Marks Regulations 1995. Together, the law.'],
    ['Ground for rejection', 'A reason in the Act for which an application can be refused, such as section 41 (not capable of distinguishing) or section 43 (likely to deceive or cause confusion).'],
    ['Adverse report', 'The examiner’s written report of problems with an application, including any grounds for rejection.'],
    ['Specification of goods and services', 'The list of goods and services an application covers.'],
    ['Competency question', 'A question the finished system must be able to help answer, written before it is built.'],
    ['Prohibited use', 'Something the system must never do, tested as carefully as what it should do.'],
    ['RDF, SKOS, OWL, SHACL', 'Open W3C standards for storing statements as triples, for vocabularies, for ontologies, and for checking data quality.'],
    ['nDCG@10', 'A standard score, here out of 100, for how good a search system’s top ten results are.'],
  ];
  const dl = $('#gloss');
  const render = () => {
    const q = $('#gloss-q').value.trim().toLowerCase();
    const rows = G.filter(([t, d]) => !q || t.toLowerCase().includes(q) || d.toLowerCase().includes(q));
    dl.innerHTML = rows.length ? rows.map(([t, d]) => `<dt>${esc(t)}</dt><dd>${esc(d)}</dd>`).join('') : '<dd class="muted">No term matches.</dd>';
  };
  $('#gloss-q').addEventListener('input', render);
  render();
})();
})();
