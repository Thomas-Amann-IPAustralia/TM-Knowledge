/* Third-party libraries, loaded on demand from site/vendor/ (ADR-0119).

   Each view asks for what it uses, so the home page never downloads the map's
   graph library. Global builds (d3, Plot, Cytoscape) are added as
   classic scripts, once; ES-module builds are imported. Versions and checksums
   are in vendor/manifest.json. */

const scripts = new Map();

function script(file) {
  if (!scripts.has(file)) {
    scripts.set(file, new Promise((resolve, reject) => {
      const tag = document.createElement("script");
      tag.src = `vendor/${file}`;
      tag.async = false;
      tag.onload = resolve;
      tag.onerror = () => reject(new Error(`could not load vendor/${file}`));
      document.head.appendChild(tag);
    }));
  }
  return scripts.get(file);
}

export async function d3() {
  await script("d3.min.js");
  return window.d3;
}

export async function plot() {
  await script("d3.min.js");
  await script("plot.umd.min.js");
  return window.Plot;
}

export async function cytoscape() {
  await script("cytoscape.min.js");
  return window.cytoscape;
}

export const fuse = () => import("../vendor/fuse.min.mjs").then((m) => m.default);

let renderer = null;
/** Markdown → sanitised HTML. Model-written text never reaches the page unsanitised. */
export async function markdown() {
  if (!renderer) {
    const [{ marked }, { default: purify }] = await Promise.all([import("../vendor/marked.esm.js"), import("../vendor/purify.es.mjs")]);
    marked.setOptions({ gfm: true, breaks: false });
    renderer = (text) => purify.sanitize(marked.parse(String(text || "")), { USE_PROFILES: { html: true } });
  }
  return renderer;
}
