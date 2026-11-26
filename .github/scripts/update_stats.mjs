import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const svgPath = path.join(root, "showcase.svg");
const owner = "programmersd21";
const repositories = {
  flow: {
    stars: { x: "413.89", y: "718", legacy: "M413.89 718" },
    forks: { x: "487.35", y: "718", legacy: "M487.35 718" },
  },
  wallr: {
    stars: { x: "924.35", y: "718", legacy: "M924.35 718" },
    forks: { x: "1000.23", y: "718", legacy: "M1000.23 718" },
  },
  pyratatui: {
    stars: { x: "411.35", y: "1092", legacy: "M411.35 1092" },
    forks: { x: "488.35", y: "1092.2", legacy: "M488.35 1092.2" },
  },
  mew: {
    stars: { x: "925.77", y: "1092.2", legacy: "M925.77 1092.2" },
    forks: { x: "998.75", y: "1092", legacy: "M998.75 1092" },
  },
  "ratatui-skill": {
    stars: { x: "411.35", y: "1466", legacy: "M411.35 1466" },
    forks: { x: "489.14", y: "1466.2", legacy: "M489.14 1466.2" },
  },
  scribe: {
    stars: { x: "925.77", y: "1466.2", legacy: "M925.77 1466.2" },
    forks: { x: "1002.14", y: "1466.2", legacy: "M1002.14 1466.2" },
  },
};

const token = process.env.GITHUB_TOKEN;
const number = new Intl.NumberFormat("en-US");

if (!token) throw new Error("GITHUB_TOKEN is required");

const headers = {
  Accept: "application/vnd.github+json",
  Authorization: "Bearer " + token,
  "X-GitHub-Api-Version": "2022-11-28",
  "User-Agent": "programmersd21-profile-stats",
};

async function fetchRepositoryStats(repository) {
  const response = await fetch("https://api.github.com/repos/" + owner + "/" + repository, {
    headers,
    signal: AbortSignal.timeout(20000),
  });

  if (!response.ok) {
    throw new Error("GitHub API returned " + response.status + " for " + repository + ": " + await response.text());
  }

  const data = await response.json();

  if (
    data.full_name?.toLowerCase() !== (owner + "/" + repository).toLowerCase() ||
    !Number.isSafeInteger(data.stargazers_count) ||
    !Number.isSafeInteger(data.forks_count) ||
    data.stargazers_count < 0 ||
    data.forks_count < 0
  ) {
    throw new Error("GitHub returned invalid repository statistics for " + repository);
  }

  return { stars: data.stargazers_count, forks: data.forks_count };
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function metricPattern(attribute, repository) {
  return new RegExp(
    "<text\\b(?=[^>]*\\b" + attribute + "=\\\"" + escapeRegExp(repository) + "\\\")[^>]*>[\\s\\S]*?</text>",
    "g",
  );
}

function ensureMetric(svg, repository, kind, metric) {
  const attribute = kind === "stars" ? "data-star-count" : "data-fork-count";
  const existing = [...svg.matchAll(metricPattern(attribute, repository))];

  if (existing.length > 1) throw new Error("Duplicate " + attribute + " marker for " + repository);
  if (existing.length === 1) return svg;

  const legacyPattern = new RegExp(
    "<path\\b(?=[^>]*\\bd=\\\"" + escapeRegExp(metric.legacy) + "[^\\\"]*\\\")[^>]*/>",
    "g",
  );
  const legacy = [...svg.matchAll(legacyPattern)];

  if (legacy.length !== 1) {
    throw new Error("Expected exactly one legacy " + kind + " path for " + repository + "; found " + legacy.length);
  }

  const value = kind === "stars" ? "0" : "0 forks";
  const text = '<text ' + attribute + '="' + repository + '" x="' + metric.x + '" y="' + metric.y + '" fill="#f2f2f2" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="500">' + value + "</text>";
  return svg.replace(legacyPattern, text);
}

function updateMetric(svg, repository, kind, value) {
  const attribute = kind === "stars" ? "data-star-count" : "data-fork-count";
  const pattern = new RegExp(
    "(<text\\b(?=[^>]*\\b" + attribute + "=\\\"" + escapeRegExp(repository) + "\\\")[^>]*>)[\\s\\S]*?(</text>)",
    "g",
  );
  let replacements = 0;
  const updated = svg.replace(pattern, (_, opening, closing) => {
    replacements += 1;
    return opening + value + closing;
  });

  if (replacements !== 1) {
    throw new Error("Expected one " + attribute + " marker for " + repository + "; updated " + replacements);
  }

  return updated;
}

async function main() {
  const entries = await Promise.all(
    Object.keys(repositories).map(async (repository) => [repository, await fetchRepositoryStats(repository)]),
  );
  const stats = Object.fromEntries(entries);
  let svg = await readFile(svgPath, "utf8");

  if (!svg.startsWith("<svg")) throw new Error("showcase.svg is not a valid SVG document");

  const oldShimmer = ".shim{animation:shim 8s cubic-bezier(.45,0,.55,1) var(--dl,0s) infinite}\\n@keyframes shim{0%{transform:translateX(-200px) skewX(-18deg)}55%,100%{transform:translateX(700px) skewX(-18deg)}}";
  const newShimmer = ".shim{animation:shim 5s linear var(--dl,0s) infinite}\\n@keyframes shim{from{transform:translateX(-200px) skewX(-18deg)}to{transform:translateX(700px) skewX(-18deg)}}";
  if (svg.split(oldShimmer).length !== 2 && !svg.includes(newShimmer)) {
    throw new Error("Expected exactly one original shimmer definition");
  }
  svg = svg.replace(oldShimmer, newShimmer);

  for (const [repository, metrics] of Object.entries(repositories)) {
    svg = ensureMetric(svg, repository, "stars", metrics.stars);
    svg = ensureMetric(svg, repository, "forks", metrics.forks);
  }

  for (const [repository, item] of Object.entries(stats)) {
    svg = updateMetric(svg, repository, "stars", number.format(item.stars));
    svg = updateMetric(svg, repository, "forks", number.format(item.forks) + " forks");
  }

  await writeFile(svgPath, svg, "utf8");

  console.log("Updated GitHub repository statistics:");
  for (const [repository, item] of Object.entries(stats)) {
    console.log("  " + repository + ": " + number.format(item.stars) + " stars, " + number.format(item.forks) + " forks");
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
