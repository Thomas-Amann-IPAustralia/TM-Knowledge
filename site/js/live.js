/* The live model calls, made from the reader's browser, streamed.

   The answer is the request `bulk.client.respond` sends for the `answer` job — the
   same instructions, JSON schema and input shape (built by engine.prompt) — with
   `stream: true`, so the page can show the answer as it is written. Before it, the
   reading (ADR-0132) asks the same model which ideas on the map a typed question
   is about, with the prompt `bulk.jobs` keeps for it. Every call goes to the
   proxy (`live-proxy/`), which holds the key; the page holds none. Until ADR-0136
   a site built without a proxy carried the key, masked, and this file unmasked
   it; the owner removed that fallback once the proxy served. */

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
  return m ? readString(json, m.index + m[0].length) : null;
}

/** Every value of a string field in JSON that may still be arriving, the last perhaps
    cut short: the claims of an answer-v4 reply, as they stream (A08). */
export function partialFields(json, key) {
  return [...json.matchAll(new RegExp(`"${key}"\\s*:\\s*"`, "g"))].map((m) => readString(json, m.index + m[0].length));
}

function readString(json, from) {
  const escapes = { n: "\n", t: "\t", r: "", b: "", f: "", '"': '"', "\\": "\\", "/": "/" };
  let out = "";
  for (let i = from; i < json.length;) {
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

/** The cited answer, from the prompt engine.prompt builds. */
export function answer(live, chat, input, signal, onText = null) {
  return respond(live, {
    model: chat.model, instructions: chat.instructions, schema: chat.schema, name: "answer",
    input, max_output_tokens: chat.max_output_tokens, effort: chat.effort,
  }, signal, onText);
}

/** The reading's input — `bulk.jobs.reading_input`, character for character. */
export const readingInput = (chat, question) => `ONTOLOGY (one line per concept):\n${chat.ontology_map}\n\nQUESTION: ${question}`;

/** Which ideas on the map a typed question is about, in the model's reading. */
export function read(live, chat, question, signal) {
  const r = chat.reading;
  return respond(live, {
    model: chat.model, instructions: r.instructions, schema: r.schema, name: "reading",
    input: readingInput(chat, question), max_output_tokens: r.max_output_tokens, effort: r.effort,
  }, signal);
}

async function respond(live, request, signal, onText = null) {
  const body = {
    model: request.model,
    instructions: request.instructions,
    input: request.input,
    text: { format: { type: "json_schema", name: request.name, schema: request.schema, strict: true } },
    max_output_tokens: request.max_output_tokens,
    store: false,
    stream: true,
  };
  if (request.effort && request.effort !== "none") body.reasoning = { effort: request.effort };
  const started = performance.now();
  const host = new URL(live.endpoint).host;
  let response;
  try {
    response = await fetch(live.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
      throw new Error(`the connection to the model service (${host}) dropped while the reply was being written`);
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
    throw new Error(final?.status === "incomplete" ? "the reply was cut off before it finished" : "the model's reply was not in the expected shape");
  }
  return { parsed, model: final?.model || request.model, usage: final?.usage || {}, seconds: (performance.now() - started) / 1000 };
}

/** What a call cost, from the usage the API reported and the prices in chat.json. */
export function cost(usage, prices) {
  if (!prices || !usage) return null;
  const cached = usage.input_tokens_details?.cached_tokens || 0;
  const input = (usage.input_tokens || 0) - cached;
  const output = usage.output_tokens || 0;
  return (input * prices.input + cached * (prices.cached_input ?? prices.input) + output * prices.output) / 1e6;
}
