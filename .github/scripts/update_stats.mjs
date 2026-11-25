import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const svgPath = path.join(root, "profile.svg");
const owner = "programmersd21";
const repositories = ["flow", "wallr", "pyratatui", "mew", "venti", "scribe"];
const token = process.env.GITHUB_TOKEN;

if (!token) {
  throw new Error("GITHUB_TOKEN is required");
}

async function fetchRepositoryStats(repository) {
  const response = await fetch(`https://api.github.com/repos/${owner}/${repository}`, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "programmersd21-profile-stats",
    },
    signal: AbortSignal.timeout(20000),
  });

  if (!response.ok) {
    throw new Error(`GitHub API returned ${response.status} for ${repository}: ${await response.text()}`);
  }

  const data = await response.json();

  if (!Number.isSafeInteger(data.stargazers_count) || !Number.isSafeInteger(data.forks_count)) {
    throw new Error(`GitHub returned invalid repository statistics for ${repository}`);
  }

  return {
    stars: data.stargazers_count,
    forks: data.forks_count,
  };
}

function replaceCount(svg, attribute, project, count, expected) {
  const pattern = new RegExp(
    '(<text[^>]*' + attribute + '="' + project + '"[^>]*>)[^<]*(</text>)',
    "g",
  );
  let replacements = 0;
  const updated = svg.replace(pattern, (_, opening, closing) => {
    replacements += 1;
    return opening + count + closing;
  });

  if (replacements !== expected) {
    throw new Error(`Expected ${expected} ${attribute} labels for ${project}; updated ${replacements}`);
  }

  return updated;
}

async function main() {
  const entries = await Promise.all(
    repositories.map(async (repository) => [
      repository,
      await fetchRepositoryStats(repository),
    ]),
  );
  const stats = Object.fromEntries(entries);
  let svg = await readFile(svgPath, "utf8");

  for (const repository of repositories) {
    svg = replaceCount(svg, "data-star-count", repository, stats[repository].stars, 2);
    svg = replaceCount(svg, "data-fork-count", repository, stats[repository].forks, 1);
  }

  const totalStars = Object.values(stats).reduce((sum, item) => sum + item.stars, 0);
  const totalForks = Object.values(stats).reduce((sum, item) => sum + item.forks, 0);

  svg = replaceCount(svg, "data-total-stars", "true", totalStars + " stars across six projects", 1);
  svg = replaceCount(svg, "data-total-forks", "true", totalForks + " forks across six projects", 1);

  await writeFile(svgPath, svg, "utf8");

  console.log("Updated GitHub profile statistics:");
  for (const repository of repositories) {
    const { stars, forks } = stats[repository];
    console.log(`  ${repository}: ${stars} stars, ${forks} forks`);
  }
  console.log(`  total: ${totalStars} stars, ${totalForks} forks`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
