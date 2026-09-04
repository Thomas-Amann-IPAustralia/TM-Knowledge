/* The decision form — the one page with state.

   It cannot write to the repository: this is a static page, and a page able to
   write would need a credential sitting in a browser. So it composes a GitHub
   issue instead. Submitting that issue runs a workflow that transcribes the
   answers into `review/rulings/`, comments with a link to the file and closes
   the issue. The owner's own words, their GitHub account, their timestamp —
   and no token anywhere near this page.

   A draft is kept in this browser only (localStorage), so a half-finished
   session survives a closed tab and never leaves the machine. */

import { render, inline, escape } from "./md.js";

const DRAFT_KEY = "tmk-answers-v1";
/* GitHub truncates a very long prefilled issue URL. Past this many encoded
   characters the form stops pretending and switches to copy-and-paste. */
const URL_BUDGET = 5800;

const readDraft = () => {
  try { return JSON.parse(localStorage.getItem(DRAFT_KEY) || "{}"); } catch { return {}; }
};
const writeDraft = (draft) => {
  try { localStorage.setItem(DRAFT_KEY, JSON.stringify(draft)); } catch { /* private window */ }
};

const el = (html) => {
  const wrap = document.createElement("div");
  wrap.innerHTML = html;
  return wrap.firstElementChild;
};

const URGENCY = {
  high: { label: "unblocks work", tone: "gap" },
  medium: { label: "worth settling", tone: "warn" },
  low: { label: "confirm when you can", tone: "note" },
};

const yaml = (draft, questions, updated) => {
  const lines = [`form: tmk-ruling/1`, `questions_updated: ${JSON.stringify(updated)}`, "answers:"];
  questions.forEach((question) => {
    const answer = draft[question.id];
    if (!answer) return;
    const kind = question.answer.kind;
    const filled =
      kind === "multi"
        ? (answer.values || []).length || (answer.notes || "").trim()
        : (answer.value || "").trim() || (answer.notes || "").trim();
    if (!filled) return;
    lines.push(`  - id: ${question.id}`);
    if (kind === "multi") {
      lines.push(`    values: [${(answer.values || []).map((v) => JSON.stringify(v)).join(", ")}]`);
    } else if (answer.value) {
      lines.push(`    value: ${JSON.stringify(answer.value)}`);
    }
    if ((answer.notes || "").trim()) lines.push(`    notes: ${JSON.stringify(answer.notes.trim())}`);
  });
  return lines.join("\n");
};

const summarise = (draft, questions) =>
  questions
    .filter((question) => draft[question.id])
    .map((question) => {
      const answer = draft[question.id];
      const kind = question.answer.kind;
      const options = question.answer.options || [];
      const labelFor = (value) => (options.find((o) => o.value === value) || {}).label || value;
      let chosen;
      if (kind === "multi") {
        const picked = answer.values || [];
        chosen = picked.length ? picked.map(labelFor).join("; ") : "nothing ticked — all confirmed";
      } else if (kind === "choice") {
        if (!answer.value) return null;
        chosen = labelFor(answer.value);
      } else {
        if (!(answer.value || "").trim()) return null;
        chosen = answer.value.trim();
      }
      const note = (answer.notes || "").trim();
      return `- **${question.id} — ${question.title}**\n  ${chosen}${note ? `\n  _Note: ${note}_` : ""}`;
    })
    .filter(Boolean)
    .join("\n");

const issueBody = (draft, questions, updated) => {
  const summary = summarise(draft, questions);
  const payload = yaml(draft, questions, updated);
  return (
    "<!-- tmk-ruling:v1 -->\n" +
    "Answers submitted from the TM-Knowledge dashboard.\n\n" +
    `${summary}\n\n` +
    "<details><summary>The machine-readable version (do not edit)</summary>\n\n" +
    "```yaml\n" +
    `${payload}\n` +
    "```\n\n</details>\n\n" +
    "_Submitting this issue records the decision: a workflow transcribes it into " +
    "`review/rulings/`, links the file back here and closes the issue._\n"
  );
};

/* ------------------------------------------------------------------ pieces */

function answeredPanel(records) {
  const rows = records
    .map(
      (record) =>
        `<li>${escape(record.label || record.value || "—")}` +
        (record.notes ? ` — <em>${escape(record.notes)}</em>` : "") +
        ` <span class="chip${record.applied ? " t-good" : " t-warn"}">` +
        `${record.applied ? "acted on" : "recorded, not yet acted on"}</span>` +
        (record.issue ? ` <a href="${escape(record.issue)}">the submission</a>` : "") +
        `</li>`
    )
    .join("");
  return `<div class="callout c-good answered"><h3>You answered this</h3><ul>${rows}</ul></div>`;
}

function control(question, draft, onChange) {
  const answer = question.answer;
  const current = draft[question.id] || {};
  const node = document.createElement("div");

  if (answer.kind === "choice" || answer.kind === "multi") {
    const multi = answer.kind === "multi";
    node.innerHTML =
      `<h4>${escape(answer.prompt || "Your answer")}</h4><div class="opts">` +
      answer.options
        .map((option) => {
          const checked = multi
            ? (current.values || []).includes(option.value)
            : current.value === option.value;
          return (
            `<label class="opt${checked ? " picked" : ""}">` +
            `<input type="${multi ? "checkbox" : "radio"}" name="${escape(question.id)}" ` +
            `value="${escape(option.value)}"${checked ? " checked" : ""}>` +
            `<span><span class="t">${inline(option.label)}</span>` +
            (option.help ? `<span class="h">${inline(option.help)}</span>` : "") +
            `</span></label>`
          );
        })
        .join("") +
      `</div>`;

    node.addEventListener("change", () => {
      const inputs = [...node.querySelectorAll("input")];
      const value = multi
        ? { values: inputs.filter((input) => input.checked).map((input) => input.value) }
        : { value: (inputs.find((input) => input.checked) || {}).value };
      inputs.forEach((input) => input.closest(".opt").classList.toggle("picked", input.checked));
      onChange(value);
    });
  } else {
    const long = answer.kind === "long_text";
    node.innerHTML =
      `<h4>${escape(answer.prompt || "Your answer")}</h4>` +
      (long
        ? `<textarea rows="4" placeholder="${escape(answer.placeholder || "")}">${escape(current.value || "")}</textarea>`
        : `<input type="text" value="${escape(current.value || "")}" placeholder="${escape(answer.placeholder || "")}">`);
    node.addEventListener("input", (event) => onChange({ value: event.target.value }));
  }

  if (question.notes_prompt) {
    const notes = el(
      `<div><h4>${escape(question.notes_prompt)}</h4>` +
        `<textarea rows="2" placeholder="Optional — anything in your own words">${escape(current.notes || "")}</textarea></div>`
    );
    notes.querySelector("textarea").addEventListener("input", (event) =>
      onChange({ notes: event.target.value })
    );
    node.appendChild(notes);
  }
  return node;
}

function questionCard(question, state, onChange, answeredRecords) {
  const urgency = URGENCY[question.urgency] || URGENCY.low;
  const parked = question.status !== "open" || question.needs !== "owner";
  const card = el(
    `<details class="q"${answeredRecords ? "" : ""}>` +
      `<summary><span class="q-state" aria-hidden="true"></span><span class="q-head">` +
      `<h3>${inline(question.title)}</h3><div class="q-meta">` +
      `<span class="chip t-${urgency.tone}">${escape(urgency.label)}</span>` +
      (parked
        ? `<span class="chip">needs a trade marks expert</span>`
        : "") +
      `<span class="chip">${escape(question.id)}</span>` +
      (question.tracked_as || []).map((ref) => `<span class="chip">${escape(ref)}</span>`).join("") +
      `</div></span></summary><div class="q-body"></div></details>`
  );

  const body = card.querySelector(".q-body");
  body.appendChild(el(`<div class="prose">${render(question.plain)}</div>`));
  body.appendChild(
    el(
      `<div class="callout c-note"><h3>Why this one is yours</h3>` +
        `<div class="prose">${render(question.why_you)}</div></div>`
    )
  );
  body.appendChild(
    el(
      `<div class="block prose"><h4>What stays stuck until it is answered</h4>` +
        `${render(question.if_unanswered)}</div>`
    )
  );
  if (question.background && question.background.length) {
    body.appendChild(
      el(
        `<div class="block prose"><h4>Have a look at</h4><ul>` +
          question.background
            .map((link) => `<li><a href="${escape(link.href)}">${escape(link.label)}</a></li>`)
            .join("") +
          `</ul></div>`
      )
    );
  }
  if (answeredRecords) body.appendChild(el(answeredPanel(answeredRecords)));
  if (!parked) body.appendChild(control(question, state, onChange));

  return card;
}

/* ------------------------------------------------------------------- page */

export function renderInbox(data, context) {
  const fragment = document.createDocumentFragment();
  const draft = readDraft();
  const asked = data.questions.filter((q) => q.status === "open" && q.needs === "owner");

  const bar = el(
    `<div class="submit"><span class="progress"><i style="width:0%"></i></span>` +
      `<span class="tally"></span>` +
      `<button class="btn ghost" type="button" data-act="clear">Clear my draft</button>` +
      `<button class="btn ghost" type="button" data-act="copy">Copy the answers</button>` +
      `<a class="btn" data-act="send" href="#" target="_blank" rel="noopener">Send my answers →</a>` +
      `</div>`
  );

  const answeredCount = () =>
    asked.filter((question) => {
      const answer = draft[question.id];
      if (!answer) return false;
      return question.answer.kind === "multi"
        ? true
        : Boolean((answer.value || "").trim() || (answer.notes || "").trim());
    }).length;

  const refresh = () => {
    const count = answeredCount();
    const body = issueBody(draft, asked, data.updated);
    const title = `Decisions from the dashboard — ${count} answer${count === 1 ? "" : "s"}`;
    const url =
      `${data.repo}/issues/new?labels=owner-ruling` +
      `&title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
    const send = bar.querySelector('[data-act="send"]');
    const tooLong = encodeURIComponent(body).length > URL_BUDGET;

    bar.querySelector(".progress i").style.width = `${(count / Math.max(1, asked.length)) * 100}%`;
    bar.querySelector(".tally").innerHTML = count
      ? `<strong>${count}</strong> of ${asked.length} answered${
          tooLong ? " — too long to prefill, use <em>Copy the answers</em>" : ""
        }`
      : `Answer as many as you like — nothing is sent until you press the button.`;
    send.href = tooLong ? `${data.repo}/issues/new?labels=owner-ruling` : url;
    send.toggleAttribute("aria-disabled", count === 0);
    send.classList.toggle("ghost", count === 0);
    bar.dataset.body = body;
  };

  const cards = new Map();
  const markAnswered = (id) => {
    const card = cards.get(id);
    if (!card) return;
    const answer = draft[id] || {};
    const question = asked.find((entry) => entry.id === id);
    const filled =
      question && question.answer.kind === "multi"
        ? Boolean(answer.values || (answer.notes || "").trim())
        : Boolean((answer.value || "").trim() || (answer.notes || "").trim());
    card.classList.toggle("is-answered", filled);
  };

  const onChange = (id) => (patch) => {
    draft[id] = { ...(draft[id] || {}), ...patch };
    writeDraft(draft);
    markAnswered(id);
    refresh();
  };

  /* Opening summary. */
  fragment.appendChild(
    el(
      `<div class="block"><div class="stats">` +
        `<div class="stat t-warn"><span class="value">${asked.length}</span>` +
        `<span class="label">Waiting on you</span>` +
        `<span class="sub">each one answerable without reading anything else</span></div>` +
        `<div class="stat"><span class="value">${
          data.questions.filter((q) => q.status === "parked").length
        }</span><span class="label">Parked for an expert</span>` +
        `<span class="sub">shown so nothing quietly disappears</span></div>` +
        `<div class="stat t-good"><span class="value">${data.rulings.length}</span>` +
        `<span class="label">Answers recorded so far</span>` +
        `<span class="sub">each one a file in the repository</span></div>` +
        `</div></div>`
    )
  );

  fragment.appendChild(
    el(
      `<div class="block"><div class="callout c-note"><h3>How this works</h3><div class="prose">` +
        render(
          "Pick answers below. Your draft is kept **in this browser only** until you press " +
          "*Send my answers* — that opens a new GitHub issue with everything filled in, and " +
          "you press submit. A workflow then writes your answers into the repository as a " +
          "file, links it back to the issue and closes it, and the next working session picks " +
          "it up.\n\nNothing is sent anywhere until you press that button, and you can answer " +
          "one question or all of them."
        ) +
        `</div></div></div>`
    )
  );

  data.themes.forEach((theme) => {
    const inTheme = data.questions.filter((question) => question.theme === theme.id);
    if (!inTheme.length) return;
    fragment.appendChild(
      el(
        `<div class="theme-head"><h2>${escape(theme.title)}</h2><p>${inline(theme.blurb)}</p></div>`
      )
    );
    inTheme.forEach((question) => {
      const answered = data.answered[question.id];
      const card = questionCard(question, draft, onChange(question.id), answered);
      cards.set(question.id, card);
      if (context.open === question.id) card.open = true;
      card.addEventListener("toggle", () => card.classList.toggle("is-open", card.open));
      fragment.appendChild(card);
      if (context.open === question.id) {
        requestAnimationFrame(() => card.scrollIntoView({ block: "start", behavior: "smooth" }));
      }
    });
  });

  fragment.appendChild(bar);

  bar.addEventListener("click", async (event) => {
    const action = event.target.closest("[data-act]")?.dataset.act;
    if (action === "clear") {
      event.preventDefault();
      if (!confirm("Clear every answer you have drafted in this browser?")) return;
      Object.keys(draft).forEach((key) => delete draft[key]);
      writeDraft(draft);
      location.reload();
    }
    if (action === "copy") {
      event.preventDefault();
      try {
        await navigator.clipboard.writeText(bar.dataset.body);
        event.target.textContent = "Copied — paste it into a new issue";
        setTimeout(() => { event.target.textContent = "Copy the answers"; }, 4000);
      } catch {
        event.target.textContent = "Could not copy — select the preview below";
      }
    }
    if (action === "send" && answeredCount() === 0) event.preventDefault();
  });

  const preview = el(
    `<details class="report"><summary>See exactly what gets sent <small>nothing hidden</small></summary>` +
      `<div class="body"><pre><code></code></pre></div></details>`
  );
  preview.addEventListener("toggle", () => {
    if (preview.open) preview.querySelector("code").textContent = bar.dataset.body;
  });
  fragment.appendChild(el('<div class="block"></div>')).appendChild(preview);

  asked.forEach((question) => markAnswered(question.id));
  refresh();
  return fragment;
}
