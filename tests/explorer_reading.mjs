// Check the page's reading of a typed question (ADR-0132) without calling a model:
// a stand-in reply goes through Engine.reading, and the result comes back as JSON.
// tests/unit/test_explorer.py runs this.
import { readFileSync } from "node:fs";
import { Engine } from "../site/js/engine.js";
import { readingInput } from "../site/js/live.js";

const [dataDir, casesPath] = process.argv.slice(2);
const read = (name) => JSON.parse(readFileSync(`${dataDir}/${name}.json`, "utf8"));
const engine = new Engine(read("search"), read("passages"));
const chat = read("chat");
const out = [];
for (const c of JSON.parse(readFileSync(casesPath, "utf8"))) {
  const checked = engine.reading(c.question, c.reply, chat.reading.max_ideas);
  const prepared = engine.prepare(c.question, chat, checked.kept);
  out.push({
    kept: checked.kept.map((k) => [k.id, c.question.slice(k.start, k.end)]),
    ontology: engine.ontology(c.question, 10, checked.kept).hits.map((h) => h.ref),
    dropped: checked.dropped.map((d) => [d.id, d.reason]),
    recognised: prepared.trace.ids, paths: prepared.trace.paths.length,
    plain: engine.prepare(c.question, chat).passages, passages: prepared.passages,
    input: readingInput(chat, c.question),
  });
}
process.stdout.write(JSON.stringify(out));
