// node --test — the proxy against a stand-in for OpenAI. No network, no key, no spend.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { createProxy, configFrom } from "./server.mjs";

const SITE = "https://thomas-amann-ipaustralia.github.io";
const seen = [];
let reply = null; // (req, res) => void, set per test
let upstream, proxy, base;

const listen = (server) => new Promise((resolve) => server.listen(0, "127.0.0.1", () => resolve(server.address().port)));

before(async () => {
  upstream = http.createServer(async (req, res) => {
    let raw = "";
    for await (const chunk of req) raw += chunk;
    seen.push({ headers: req.headers, body: JSON.parse(raw) });
    reply(req, res);
  });
  const port = await listen(upstream);
  proxy = createProxy({
    ...configFrom({ OPENAI_API_KEY: "sk-test-key", UPSTREAM_URL: `http://127.0.0.1:${port}/v1/responses` }),
    perDay: 5, perAddressPerHour: 100, heartbeatMs: 50,
  });
  base = `http://127.0.0.1:${await listen(proxy)}`;
});
after(() => { proxy.close(); upstream.close(); });

const ask = (body, origin = SITE) => fetch(`${base}/v1/responses`, {
  method: "POST", headers: { "Content-Type": "application/json", ...(origin ? { Origin: origin } : {}) }, body: JSON.stringify(body),
});
const question = { model: "gpt-6.1-sol", instructions: "x", input: "q", stream: true, max_output_tokens: 10000, store: false, reasoning: { effort: "low" } };

test("a preflight from the explorer is allowed", async () => {
  const res = await fetch(`${base}/v1/responses`, {
    method: "OPTIONS", headers: { Origin: SITE, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type" },
  });
  assert.equal(res.status, 204);
  assert.equal(res.headers.get("access-control-allow-origin"), SITE);
  assert.match(res.headers.get("access-control-allow-headers"), /content-type/);
});

test("the key is added, extra fields dropped, output capped, and the stream passed through", async () => {
  const events = ['data: {"type":"response.output_text.delta","delta":"{\\"a\\":"}\n\n', 'data: {"type":"response.output_text.delta","delta":"1}"}\n\n'];
  reply = (req, res) => {
    res.writeHead(200, { "Content-Type": "text/event-stream" });
    res.write(events[0]);
    setTimeout(() => { res.write(events[1]); res.end(); }, 120); // long enough for a heartbeat
  };
  seen.length = 0;
  const res = await ask({ ...question, max_output_tokens: 999999, store: true, tools: [{ type: "web_search" }] });
  assert.equal(res.status, 200);
  assert.equal(res.headers.get("access-control-allow-origin"), SITE);
  const text = await res.text();
  assert.equal(text.replace(/:\n\n/g, ""), events.join(""), "only comment lines are added");
  const sent = seen[0];
  assert.equal(sent.headers.authorization, "Bearer sk-test-key");
  assert.equal(sent.body.max_output_tokens, 10000);
  assert.equal(sent.body.store, false);
  assert.equal("tools" in sent.body, false);
  assert.deepEqual(sent.body.reasoning, { effort: "low" });
});

test("OpenAI's own error comes back as it was, readable by the page", async () => {
  reply = (req, res) => {
    res.writeHead(401, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: { message: "Incorrect API key provided" } }));
  };
  const res = await ask(question);
  assert.equal(res.status, 401);
  assert.equal(res.headers.get("access-control-allow-origin"), SITE);
  assert.equal((await res.json()).error.message, "Incorrect API key provided");
});

test("another origin, another model, a bad body and another path are refused before OpenAI", async () => {
  seen.length = 0;
  let res = await ask(question, "https://elsewhere.example");
  assert.equal(res.status, 403);
  assert.match((await res.json()).error.message, /only answers the Trade Marks Manual explorer/);
  res = await ask(question, null);
  assert.equal(res.status, 403);
  res = await ask({ ...question, model: "gpt-something-dearer" });
  assert.equal(res.status, 400);
  assert.match((await res.json()).error.message, /only uses gpt-6.1-sol/);
  res = await fetch(`${base}/v1/responses`, { method: "POST", headers: { Origin: SITE }, body: "not json" });
  assert.equal(res.status, 400);
  res = await fetch(`${base}/v1/files`, { method: "POST", headers: { Origin: SITE }, body: "{}" });
  assert.equal(res.status, 404);
  res = await fetch(`${base}/v1/responses`, { method: "POST", headers: { Origin: SITE }, body: "x".repeat(300000) });
  assert.equal(res.status, 413);
  assert.equal(seen.length, 0, "nothing refused reached OpenAI");
});

test("the daily limit refuses with a message", async () => {
  reply = (req, res) => { res.writeHead(200, { "Content-Type": "application/json" }); res.end("{}"); };
  let last;
  for (let i = 0; i < 6; i++) { last = await ask(question); if (i < 5) await last.text(); }
  assert.equal(last.status, 429);
  assert.match((await last.json()).error.message, /daily limit/);
});

test("health answers without calling OpenAI", async () => {
  const res = await fetch(`${base}/health`);
  assert.equal(res.status, 200);
  assert.equal(await res.text(), "ok");
});

test("without a key it says so", async () => {
  const bare = createProxy(configFrom({}));
  const url = `http://127.0.0.1:${await listen(bare)}`;
  const res = await fetch(`${url}/v1/responses`, { method: "POST", headers: { Origin: SITE }, body: JSON.stringify(question) });
  assert.equal(res.status, 503);
  assert.match((await res.json()).error.message, /OPENAI_API_KEY/);
  bare.close();
});
