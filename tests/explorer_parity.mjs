// Run the browser's search engine over questions and print what it found as JSON.
// tests/unit/test_explorer.py compares this with search.index.Systems and with
// the answer prompt bulk.jobs builds, question by question.
import { readFileSync } from "node:fs";
import { Engine } from "../site/js/engine.js";

const [dataDir, questionsPath] = process.argv.slice(2);
const read = (name) => JSON.parse(readFileSync(`${dataDir}/${name}.json`, "utf8"));
const engine = new Engine(read("search"), read("passages"));
const chat = read("chat");
const out = {};
for (const q of JSON.parse(readFileSync(questionsPath, "utf8"))) {
  const { hits, trace } = engine.ontology(q.question, 10);
  const prepared = engine.prepare(q.question, chat);
  out[q.key] = {
    keyword: engine.keyword(q.question, 10).map((h) => h.ref),
    ontology: hits.map((h) => h.ref),
    recognised: trace.ids,
    neighbours: trace.neighbours,
    paths: trace.paths.map((p) => p[3]),
    passages: prepared.passages,
    legislation: prepared.legislation,
    prompt: q.prompt ? engine.prompt(prepared, chat) : null,
  };
}
process.stdout.write(JSON.stringify(out));
