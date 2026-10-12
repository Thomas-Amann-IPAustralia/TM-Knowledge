# live-proxy/ — the answer service that holds the OpenAI key

"Ask the Manual" can send each live question straight to OpenAI, with the key
published in the page (ADR-0118), or here, to a small service that holds the key
and forwards the question. This is that service. Use it when:

- the key should not be in the page, or
- a reader's network blocks `api.openai.com` — common on work and government
  networks, where the page then says it "could not reach the model service". A
  proxy on another address gets through wherever that address is allowed.

## What belongs here

`server.mjs` (the service, no dependencies, Node 20 or later), `server.test.mjs`
(`node --test`, against a stand-in for OpenAI — no network, no key, no spend),
`package.json`, and this file. Nothing else: no key, no `.env`, no `node_modules`.

## What it does, and does not

It answers `POST /v1/responses` from the explorer's origin, for the allowed model,
passing on only the fields the page sends (`tools` and the like are dropped),
with `store: false` and output capped. A live question is two requests: a short reading of
the question against the map (`text.format.name` "reading", ADR-0132), then the answer.
Readings are counted apart from answers, so the limits below are per question. It streams
OpenAI's reply back unchanged,
with a comment line every 15 seconds while the model is quiet, which the page
ignores. OpenAI's own errors come back as they were; its own refusals use
OpenAI's error shape, so the page prints them after "No answer:". `GET /health`
answers without calling OpenAI.

It is not security. Anyone can forge an `Origin` header outside a browser, and
the per-address limit trusts `X-Forwarded-For`. **The OpenAI project's monthly
budget is the real limit** — set one.

| Setting (environment variable) | Default | |
|---|---|---|
| `OPENAI_API_KEY` | — | **Required.** Mark it secret on the host |
| `ALLOWED_ORIGINS` | `https://thomas-amann-ipaustralia.github.io` | Comma-separated |
| `ALLOWED_MODELS` | `gpt-6.1-sol` | Must include `CHAT_MODEL` in `src/tm_knowledge/explorer/build.py` |
| `MAX_OUTPUT_TOKENS` | `10000` | A higher request is lowered to this |
| `MAX_READING_OUTPUT_TOKENS` | `2000` | The same, for a reading |
| `PER_ADDRESS_PER_HOUR` | `30` | Per reader address; resets when the service restarts |
| `PER_DAY` | `300` | All readers together, per UTC day |
| `PORT` | `10000` | Set by the host |

## Deploying on Render (free plan)

1. **OpenAI.** At platform.openai.com make a key for this alone, in a project
   with a monthly budget. Do not reuse a key that has been in the page.
2. **Render.** New → Web Service → this GitHub repository. Name: e.g.
   `tmk-live-answers`. Language: Node. Branch: `main`. Region: Singapore.
   Root Directory: `live-proxy`. Build Command: `npm install`. Start Command:
   `npm start`. Instance type: Free. Environment variable `OPENAI_API_KEY` = the
   new key. Advanced → Health Check Path: `/health`. Create Web Service.
3. **Check it** from the network that blocked OpenAI: open
   `https://<name>.onrender.com/health`. `ok` means it is reachable and has its key.
4. **GitHub.** Settings → Secrets and variables → Actions → Variables → New
   repository variable `TMK_LIVE_ENDPOINT` = `https://<name>.onrender.com/v1/responses`.
   With it set, the build publishes no key even if the `OPENAI_API_KEY` secret is
   still there; delete that secret anyway (Settings → Environments → `github-pages`).
5. **Redeploy the site**: Actions → `pages` → Run workflow. The deploy summary
   should say "live chat: on, through the proxy at …". A secret or variable change
   does not redeploy by itself.
6. Ask a live question; then **revoke the old key** at OpenAI.

Render auto-deploys when something under `live-proxy/` changes on `main`. A free
service sleeps after 15 minutes without traffic and takes about a minute to wake:
the Ask page knocks on `/health` as it opens, and says so if an answer is slow to
start. Before a demonstration, open the health address a couple of minutes early.
Logs (Render → the service → Logs) show one line per question: time, status,
model, seconds and the day's count — never the question.

## Running it locally

```bash
cd live-proxy
node --test                                   # the tests; nothing leaves the machine
OPENAI_API_KEY=sk-… ALLOWED_ORIGINS=http://localhost:8000 npm start
```

Then build the explorer with `TMK_LIVE_ENDPOINT=http://localhost:10000/v1/responses`.
