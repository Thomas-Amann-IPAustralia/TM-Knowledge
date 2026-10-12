/* The live model call, made from the reader's browser, streamed.

   The request is the one `bulk.client.respond` sends for the `answer` job — the
   same instructions, JSON schema and input shape (built by engine.prompt) — with
   `stream: true`, so the page can show the answer as it is written. When the site
   is built with a key, the key is in the page: the owner's decision (ADR-0118).
   It is masked against pattern-matching scrapers; that is not security, and
   anyone reading this file can recover it. */

function reveal(live) {
  if (!live.m || !live.x) return null;
  const bytes = (b64) => Uint8Array.from(atob(b64), (ch) => ch.charCodeAt(0));
  const mask = bytes(live.m), mixed = bytes(live.x).reverse();
  return new TextDecoder().decode(mixed.map((b, i) => b ^ mask[i]));
}

/** Whether answers go through a proxy (`live-proxy/`) rather than straight to OpenAI. */
export function viaProxy(live) {
  try { return !!live?.enabled && new URL(live.endpoint).hostname !== "api.openai.com"; } catch { return false; }
}

/** A proxy on a free host sleeps when idle and takes about a minute to wake; knock
    as the page opens, so it is awake by the time a question is asked. */
export function wake(live) {
  if (!viaProxy(live)) return;
  try { fetch(new URL("/health", live.endpoint), { mode: "no-cors", cache: "no-store" }).catch(() => {}); } catch { /* bad URL: the question will say so */ }
}

/** The value of a string field in JSON that may still be arriving. */
export function partialField(json, key) {
  const m = new RegExp(`"${key}"\\s*:\\s*"`).exec(json);
  if (!m) return null;
  const escapes = { n: "\n", t: "\t", r: "", b: "", f: "", '"': '"', "\\": "\\", "/": "/" };
  let out = "";
  for (let i = m.index + m[0].length; i < json.length;) {
    const ch = json[i];
    if (ch === '"') break;
    if (ch !== "\\") { out += ch; i++; continue; }
    if (i + 1 >= json.length) break;
    const next = json[i + 1];
    if (next === "u") {
      if (i + 5 >= json.length) break;
      out += String.fromCharCode(parseInt(json.slice(i + 2, i + 6), 16));
      i += 6;
    } else { out += escapes[next] ?? next; i += 2; }
  }
  return out;
}

export async function answer(live, chat, input, signal, onText = null) {
  const key = reveal(live);
  const body = {
    model: chat.model,
    instructions: chat.instructions,
    input,
    text: { format: { type: "json_schema", name: "answer", schema: chat.schema, strict: true } },
    max_output_tokens: chat.max_output_tokens,
    store: false,
    stream: true,
  };
  if (chat.effort && chat.effort !== "none") body.reasoning = { effort: chat.effort };
  const started = performance.now();
  const host = new URL(live.endpoint).host;
  let response;
  try {
    response = await fetch(live.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(key ? { Authorization: `Bearer ${key}` } : {}) },
      body: JSON.stringify(body),
      signal,
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    // fetch rejects only when no reply came back at all ("Failed to fetch"): the
    // request was stopped on the way. A wrong key, model or credit is a reply,
    // with OpenAI's own message, and is reported below.
    throw new Error(`your browser could not reach the model service (${host}) — the request was stopped before it arrived, so no reply came back. Work networks and some browser extensions block this address; on another network it may work`);
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data?.error?.message || `the model service answered ${response.status}`);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "", text = "", final = null;
  const handle = (block) => {
    const data = block.split("\n").filter((line) => line.startsWith("data:")).map((line) => line.slice(5).trimStart()).join("\n");
    if (!data || data === "[DONE]") return;
    let event;
    try { event = JSON.parse(data); } catch { return; }
    if (event.type === "response.output_text.delta") { text += event.delta || ""; if (onText) onText(text); }
    else if (event.type === "response.completed" || event.type === "response.incomplete") final = event.response;
    else if (event.type === "response.failed") throw new Error(event.response?.error?.message || "the model could not answer");
    else if (event.type === "error") throw new Error(event.message || event.error?.message || "the model service reported an error");
  };
  for (;;) {
    let chunk;
    try { chunk = await reader.read(); } catch (error) {
      if (signal?.aborted) throw error;
      throw new Error(`the connection to the model service (${host}) dropped while the answer was being written`);
    }
    const { value, done } = chunk;
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
    let cut;
    while ((cut = buffer.indexOf("\n\n")) >= 0) { handle(buffer.slice(0, cut)); buffer = buffer.slice(cut + 2); }
  }
  if (buffer.trim()) handle(buffer);
  let parsed = null;
  try { parsed = JSON.parse(text); } catch { /* reported below */ }
  if (!parsed || typeof parsed !== "object") {
    throw new Error(final?.status === "incomplete" ? "the answer was cut off before it finished" : "the model's reply was not in the expected shape");
  }
  return { parsed, model: final?.model || chat.model, usage: final?.usage || {}, seconds: (performance.now() - started) / 1000 };
}

/** What a call cost, from the usage the API reported and the prices in chat.json. */
export function cost(usage, prices) {
  if (!prices || !usage) return null;
  const cached = usage.input_tokens_details?.cached_tokens || 0;
  const input = (usage.input_tokens || 0) - cached;
  const output = usage.output_tokens || 0;
  return (input * prices.input + cached * (prices.cached_input ?? prices.input) + output * prices.output) / 1e6;
}
