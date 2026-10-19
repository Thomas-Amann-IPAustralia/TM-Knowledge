// Apply the browser's excerpt rules (engine.js `excerpt`) to (ref, question) pairs and
// print the results as JSON; tests/unit/test_explorer.py compares them with
// bulk.jobs.excerpt, character for character (A06).
import { readFileSync } from "node:fs";
import { Engine, excerpt } from "../site/js/engine.js";

const [dataDir, casesPath] = process.argv.slice(2);
const read = (name) => JSON.parse(readFileSync(`${dataDir}/${name}.json`, "utf8"));
const engine = new Engine(read("search"), read("passages"));
const chat = read("chat");
const out = [];
for (const [ref, question] of JSON.parse(readFileSync(casesPath, "utf8"))) {
  out.push(excerpt(ref, engine.text(ref), engine.legislation[ref]?.[4] || null, engine.terms(question), chat));
}
process.stdout.write(JSON.stringify(out));
