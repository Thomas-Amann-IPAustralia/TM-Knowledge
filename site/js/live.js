/* The live model call, made from the reader's browser.

   The request is the one `bulk.client.respond` sends for the `answer` job: the
   same instructions, the same JSON schema, the same input shape (built by
   engine.prompt). When the site is built with a key, the key is in the page —
   the owner's decision (ADR-0118). It is masked against pattern-matching
   scrapers; that is not security, and anyone reading this file can recover it. */

function reveal(live) {
  if (!live.m || !live.x) return null;
  const bytes = (b64) => Uint8Array.from(atob(b64), (ch) => ch.charCodeAt(0));
  const mask = bytes(live.m), mixed = bytes(live.x).reverse();
  return new TextDecoder().decode(mixed.map((b, i) => b ^ mask[i]));
}

function outputText(response) {
  const parts = [];
  for (const item of response.output || []) {
    if (item.type !== "message") continue;
    for (const content of item.content || []) if (content.type === "output_text") parts.push(content.text || "");
  }
  return parts.join("");
}

export async function answer(live, chat, input, signal) {
  const key = reveal(live);
  const body = {
    model: chat.model,
    instructions: chat.instructions,
    input,
    text: { format: { type: "json_schema", name: "answer", schema: chat.schema, strict: true } },
    max_output_tokens: chat.max_output_tokens,
    store: false,
  };
  if (chat.effort && chat.effort !== "none") body.reasoning = { effort: chat.effort };
  const started = performance.now();
  const response = await fetch(live.endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(key ? { Authorization: `Bearer ${key}` } : {}) },
    body: JSON.stringify(body),
    signal,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data?.error?.message || `the model service answered ${response.status}`;
    throw new Error(message);
  }
  const text = outputText(data);
  let parsed = null;
  try { parsed = JSON.parse(text); } catch { /* reported below */ }
  if (!parsed || typeof parsed !== "object") {
    throw new Error(data.status === "incomplete" ? "the answer was cut off before it finished" : "the model's reply was not in the expected shape");
  }
  return { parsed, model: data.model || chat.model, usage: data.usage || {}, seconds: (performance.now() - started) / 1000 };
}

/** What a call cost, from the usage the API reported and the prices in chat.json. */
export function cost(usage, prices) {
  if (!prices || !usage) return null;
  const cached = usage.input_tokens_details?.cached_tokens || 0;
  const input = (usage.input_tokens || 0) - cached;
  const output = usage.output_tokens || 0;
  return (input * prices.input + cached * (prices.cached_input ?? prices.input) + output * prices.output) / 1e6;
}
