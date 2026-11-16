// Read the JSON files that dv_index/update.py and dv_index/news.py write.
// Runs at build time only (server components), so the files ship inside the
// static pages and the site needs no server or database.
import fs from "node:fs";
import path from "node:path";

const DIR = path.join(process.cwd(), "data");

function read(name, fallback) {
  const file = path.join(DIR, name);
  if (!fs.existsSync(file)) return fallback;
  const text = fs.readFileSync(file, "utf8");
  return name.endsWith(".json") ? JSON.parse(text) : text;
}

export const getMeta = () => read("meta.json", {});
export const getBills = () => read("bills.json", []);
export const getUpdates = () => read("updates.json", []);
export const getGaps = () => read("gaps.json", []);
export const getRelated = () => read("related.json", {});
export const getFederal = () => read("federal.json", []);
export const getLexicon = () => read("lexicon.json", []);
export const getCodebookHtml = () => read("codebook.html", "");
export const getNews = () => read("news.json", []);
