/* The live-answer proxy: it holds the OpenAI key so the published page does not
   (ADR-0118, "a proxy that holds the key").

   "Ask the Manual" posts here the Responses request it would otherwise send to
   OpenAI; this adds the key, forwards it and streams the reply back unchanged. It
   answers only what the page asks: POST /v1/responses, from the explorer's origin,
   for the allowed model, carrying only the fields the page sends, capped in size,
   output and count. A live question is two requests — a short reading of the
   question against the map (ADR-0132), then the answer — so readings are counted
   apart and capped lower, and a question takes one place in each allowance. None of that stops someone determined — an Origin header can
   be forged outside a browser — so the OpenAI project's own monthly budget is the
   real limit. No dependencies; Node 20 or later. Deployment: README.md. */

import http from "node:http";
import { pathToFileURL } from "node:url";

const PATH = "/v1/responses";
/** The fields `site/js/live.js` sends. Anything else (tools, background, …) is dropped. */
const FIELDS = ["model", "instructions", "input", "text", "max_output_tokens", "store", "stream", "reasoning"];

const list = (value, fallback) => (value || fallback).split(",").map((s) => s.trim()).filter(Boolean);

export function configFrom(env) {
  return {
    key: env.OPENAI_API_KEY || "",
    upstream: env.UPSTREAM_URL || "https://api.openai.com/v1/responses",
    origins: new Set(list(env.ALLOWED_ORIGINS, "https://thomas-amann-ipaustralia.github.io")),
    models: new Set(list(env.ALLOWED_MODELS, "gpt-6.1-sol")),
    maxOutputTokens: Number(env.MAX_OUTPUT_TOKENS || 10000),
    maxReadingOutputTokens: Number(env.MAX_READING_OUTPUT_TOKENS || 2000),
    maxBodyBytes: Number(env.MAX_BODY_BYTES || 200000),
    perAddressPerHour: Number(env.PER_ADDRESS_PER_HOUR || 30),
    perDay: Number(env.PER_DAY || 300),
    heartbeatMs: Number(env.HEARTBEAT_MS || 15000),
  };
}

export function createProxy(config = configFrom(process.env)) {
  // Per kind of request: address → times of its requests in the last hour, and today's count.
  const counts = { answer: { recent: new Map(), today: 0 }, reading: { recent: new Map(), today: 0 } };
  let day = "";

  function cors(req) {
    const origin = req.headers.origin;
    return config.origins.has(origin) ? { "Access-Control-Allow-Origin": origin, Vary: "Origin" } : {};
  }

  // Errors use OpenAI's shape, so the page prints the message after "No answer:".
  // They are readable from any origin: they say nothing, and a blank CORS failure
  // would read "Failed to fetch". The connection closes, since a refusal may leave
  // part of the request unread.
  function fail(res, status, message) {
    if (res.headersSent) { res.end(); return; }
    res.writeHead(status, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", Connection: "close" });
    res.end(JSON.stringify({ error: { message, type: "proxy_error" } }));
  }

  function allow(address, kind) {
    const now = Date.now(), date = new Date(now).toISOString().slice(0, 10);
    if (date !== day) { day = date; for (const c of Object.values(counts)) { c.today = 0; c.recent.clear(); } }
    const count = counts[kind];
    if (count.today >= config.perDay) return `the answer service has answered ${config.perDay} questions today, its daily limit`;
    const times = (count.recent.get(address) || []).filter((t) => now - t < 3600000);
    if (times.length >= config.perAddressPerHour) return `${config.perAddressPerHour} questions have come from this address in the last hour, the limit`;
    times.push(now);
    count.recent.set(address, times);
    count.today += 1;
    return null;
  }

  async function readBody(req) {
    const chunks = [];
    let size = 0;
    for await (const chunk of req) {
      size += chunk.length;
      if (size > config.maxBodyBytes) return null;
      chunks.push(chunk);
    }
    return Buffer.concat(chunks).toString("utf8");
  }

  async function answer(req, res) {
    if (!config.origins.has(req.headers.origin)) return fail(res, 403, "this answer service only answers the Trade Marks Manual explorer");
    if (!config.key) return fail(res, 503, "the answer service has no OpenAI key (set OPENAI_API_KEY on the service)");
    const raw = await readBody(req);
    if (raw === null) return fail(res, 413, "the question was too large for the answer service");
    let asked;
    try { asked = JSON.parse(raw); } catch { return fail(res, 400, "the answer service could not read the request"); }
    if (!asked || typeof asked !== "object" || !config.models.has(asked.model)) {
      return fail(res, 400, `the answer service only uses ${[...config.models].join(", ")}`);
    }
    const address = String(req.headers["x-forwarded-for"] || req.socket.remoteAddress || "").split(",")[0].trim();
    const kind = asked.text?.format?.name === "reading" ? "reading" : "answer";
    const refused = allow(address, kind);
    if (refused) return fail(res, 429, refused);

    const body = Object.fromEntries(FIELDS.filter((f) => f in asked).map((f) => [f, asked[f]]));
    body.store = false;
    const cap = kind === "reading" ? config.maxReadingOutputTokens : config.maxOutputTokens;
    body.max_output_tokens = Math.min(Number(asked.max_output_tokens) || cap, cap);
    if (asked.reasoning) body.reasoning = { effort: String(asked.reasoning.effort || "low") };

    const abort = new AbortController();
    res.on("close", () => { if (!res.writableEnded) abort.abort(); });
    const started = Date.now();
    let upstream;
    try {
      upstream = await fetch(config.upstream, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${config.key}` },
        body: JSON.stringify(body),
        signal: abort.signal,
      });
    } catch (error) {
      if (abort.signal.aborted) return;
      return fail(res, 502, `the answer service could not reach OpenAI (${error.cause?.code || error.message})`);
    }
    const type = upstream.headers.get("content-type") || "application/json";
    res.writeHead(upstream.status, {
      "Content-Type": type, "Cache-Control": "no-cache", "X-Accel-Buffering": "no", ...cors(req),
    });
    // While the model reasons nothing may arrive for a while; a comment line between
    // events keeps an idle connection open and is ignored by the page.
    const streaming = type.startsWith("text/event-stream");
    let between = true;
    const beat = streaming ? setInterval(() => { if (between) res.write(":\n\n"); }, config.heartbeatMs) : null;
    try {
      if (upstream.body) {
        for await (const chunk of upstream.body) {
          res.write(chunk);
          between = chunk.length >= 2 && chunk[chunk.length - 2] === 10 && chunk[chunk.length - 1] === 10;
        }
      }
    } catch { /* the reply was cut off upstream or by the reader; end what was sent */ }
    finally {
      if (beat) clearInterval(beat);
      res.end();
      console.log(`${new Date().toISOString()} ${upstream.status} ${kind} ${asked.model} ${((Date.now() - started) / 1000).toFixed(1)}s · ${counts[kind].today} today`);
    }
  }

  return http.createServer(async (req, res) => {
    const url = new URL(req.url, "http://proxy");
    try {
      if (req.method === "GET" && url.pathname === "/health") {
        res.writeHead(200, { "Content-Type": "text/plain", "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" });
        return res.end(config.key ? "ok" : "running, but no OPENAI_API_KEY is set");
      }
      if (url.pathname !== PATH) return fail(res, 404, `the answer service answers POST ${PATH} only`);
      if (req.method === "OPTIONS") {
        // Any origin may ask; the POST refuses a wrong one with a message it can read.
        res.writeHead(204, {
          "Access-Control-Allow-Origin": req.headers.origin || "*", Vary: "Origin", "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "content-type, authorization", "Access-Control-Max-Age": "600",
        });
        return res.end();
      }
      if (req.method !== "POST") return fail(res, 405, `the answer service answers POST ${PATH} only`);
      await answer(req, res);
    } catch (error) {
      console.error(error);
      fail(res, 500, "the answer service failed");
    }
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT || 10000);
  const config = configFrom(process.env);
  createProxy(config).listen(port, "0.0.0.0", () => {
    console.log(`live-answer proxy on :${port} · origins ${[...config.origins].join(", ")} · models ${[...config.models].join(", ")}`
      + (config.key ? "" : " · NO OPENAI_API_KEY SET"));
  });
}
