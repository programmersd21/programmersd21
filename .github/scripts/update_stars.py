import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SVG_PATH = ROOT / "profile.svg"
OWNER = "programmersd21"
REPOSITORIES = {
    "flow": "flow",
    "wallr": "wallr",
    "pyratatui": "pyratatui",
    "mew": "mew",
    "venti": "venti",
    "scribe": "scribe",
}

def fetch_stars(repository):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{repository}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)
    stars = data.get("stargazers_count")
    if not isinstance(stars, int) or stars < 0:
        raise ValueError(f"Invalid star count for {repository}")
    return stars

def main():
    svg = SVG_PATH.read_text(encoding="utf-8")
    counts = {key: fetch_stars(repository) for key, repository in REPOSITORIES.items()}

    for project, count in counts.items():
        pattern = re.compile(
            rf'(<text\b[^>]*\bdata-star-count="{re.escape(project)}"[^>]*>)[^<]*(</text>)'
        )
        svg, replacements = pattern.subn(rf"\g<1>{count}\g<2>", svg)
        if replacements != 2:
            raise RuntimeError(
                f"Expected 2 SVG labels for {project}, updated {replacements}"
            )

    total = sum(counts.values())
    svg, replacements = re.subn(
        r'(<text\b[^>]*\bdata-total-stars="true"[^>]*>)[^<]*(</text>)',
        rf"\g<1>{total} stars across six projects\g<2>",
        svg,
    )
    if replacements != 1:
        raise RuntimeError(f"Expected 1 total label, updated {replacements}")

    SVG_PATH.write_text(svg, encoding="utf-8")
    print("Updated project stars:", counts)
    print("Total:", total)

if __name__ == "__main__":
    main()
