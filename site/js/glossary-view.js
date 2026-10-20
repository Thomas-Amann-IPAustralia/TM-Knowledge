/* The glossary — every term the site explains, from the one dictionary in glossary.js. */

import { esc } from "./app.js";
import { GLOSSARY, entryHtml } from "./glossary.js";

export async function render(root) {
  const keys = Object.keys(GLOSSARY).sort((a, b) => GLOSSARY[a].label.localeCompare(GLOSSARY[b].label));
  root.innerHTML = `
  <div class="wrap glossary">
    <p class="step-k">Layer 4 of 4 · plain words</p>
    <h1>Glossary</h1>
    <p class="lede">Every term the site uses, in three parts: what it means in plain words, what it does here, and what it is called
    technically. No term is assumed known.</p>
    <div class="gloss">${keys.map((key) => `<div class="gloss-entry" id="term-${esc(key)}">${entryHtml(key)}</div>`).join("")}</div>
  </div>`;
}
