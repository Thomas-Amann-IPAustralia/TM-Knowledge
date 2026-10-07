/* Markdown-lite. Enough for the prose the generator writes and for the four
   generated reports, and nothing more: headings, paragraphs, lists, tables,
   blockquotes, rules, fenced code, and inline bold / italic / code / links.
   Everything is escaped before any markup is added, so a report can contain
   angle brackets without becoming markup. */

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export const escape = (text) => String(text ?? "").replace(/[&<>"']/g, (c) => ESC[c]);

/* `{{Term}}` becomes a glossary button. The lookup happens at render time in
   app.js, which owns the glossary; this only marks the spot. */
const glossary = (text) =>
  text.replace(/\{\{([^{}]+)\}\}/g, (_, term) => {
    const name = term.trim();
    return `<button class="term" type="button" data-term="${escape(name)}">${escape(name)}</button>`;
  });

export function inline(text) {
  let out = escape(text);
  out = out.replace(/`([^`]+)`/g, (_, code) => `<code>${code}</code>`);
  out = out.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label, href) => {
    const external = /^https?:/.test(href);
    const rel = external ? ' target="_blank" rel="noopener"' : "";
    return `<a href="${href}"${rel}>${label}</a>`;
  });
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  out = out.replace(/(^|[\s(])_([^_\n]+)_/g, "$1<em>$2</em>");
  return glossary(out);
}

const cells = (row) =>
  row.replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());

export function render(source) {
  const lines = String(source ?? "").replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let list = null;
  let paragraph = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      out.push(`<p>${inline(paragraph.join(" "))}</p>`);
      paragraph = [];
    }
  };
  const flushList = () => {
    if (list) {
      out.push(`</${list}>`);
      list = null;
    }
  };
  const flush = () => { flushParagraph(); flushList(); };

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed.startsWith("<!--")) {                       // generator banners
      while (i < lines.length && !lines[i].includes("-->")) i += 1;
      continue;
    }
    if (!trimmed) { flush(); continue; }

    if (trimmed.startsWith("```")) {                        // fenced code
      flush();
      const code = [];
      i += 1;
      while (i < lines.length && !lines[i].trim().startsWith("```")) code.push(lines[i++]);
      out.push(`<pre><code>${escape(code.join("\n"))}</code></pre>`);
      continue;
    }

    if (/^\|.*\|$/.test(trimmed) && /^\|[\s:|-]+\|$/.test((lines[i + 1] || "").trim())) {
      flush();                                              // table
      const head = cells(trimmed);
      i += 2;
      const body = [];
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) body.push(cells(lines[i++].trim()));
      i -= 1;
      out.push(
        '<div class="scroll"><table><thead><tr>' +
        head.map((cell) => `<th>${inline(cell)}</th>`).join("") +
        "</tr></thead><tbody>" +
        body.map((row) => `<tr>${row.map((cell) => `<td>${inline(cell)}</td>`).join("")}</tr>`).join("") +
        "</tbody></table></div>"
      );
      continue;
    }

    const heading = /^(#{1,6})\s+(.*)$/.exec(trimmed);
    if (heading) {
      flush();
      const level = Math.min(heading[1].length + 1, 6);     // h1 in a doc -> h2 on the page
      out.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }

    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmed)) { flush(); out.push("<hr>"); continue; }

    if (trimmed.startsWith("> ")) {
      flush();
      const quote = [trimmed.slice(2)];
      while (i + 1 < lines.length && lines[i + 1].trim().startsWith("> ")) quote.push(lines[++i].trim().slice(2));
      out.push(`<blockquote>${inline(quote.join(" "))}</blockquote>`);
      continue;
    }

    const bullet = /^[-*+]\s+(.*)$/.exec(trimmed);
    const numbered = /^\d+[.)]\s+(.*)$/.exec(trimmed);
    if (bullet || numbered) {
      flushParagraph();
      const want = bullet ? "ul" : "ol";
      if (list !== want) { flushList(); out.push(`<${want}>`); list = want; }
      out.push(`<li>${inline((bullet || numbered)[1])}</li>`);
      continue;
    }

    flushList();
    paragraph.push(trimmed);
  }

  flush();
  return out.join("\n");
}
