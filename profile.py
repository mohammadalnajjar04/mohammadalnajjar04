"""Refresh public GitHub stats inside the generated profile SVGs.

Uses only GitHub's public REST API. A token is optional and is supplied by the
workflow as GITHUB_TOKEN to increase rate limits.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USERNAME = "mohammadalnajjar04"
ROOT = Path(__file__).resolve().parent
SVG_FILES = [ROOT / "dark_mode.svg", ROOT / "light_mode.svg"]


def github_json(url: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USERNAME}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def fetch_stats() -> tuple[int, int, int]:
    user = github_json(f"https://api.github.com/users/{USERNAME}")
    repos = github_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")
    stars = sum(int(repo.get("stargazers_count", 0)) for repo in repos if not repo.get("fork"))
    return int(user["public_repos"]), int(user["followers"]), stars


def replace_id(svg: str, element_id: str, value: str) -> str:
    pattern = rf'(<tspan[^>]*id="{re.escape(element_id)}"[^>]*>)(.*?)(</tspan>)'
    return re.sub(pattern, rf"\g<1>{value}\g<3>", svg, count=1)


def main() -> None:
    repos, followers, stars = fetch_stats()
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
    for path in SVG_FILES:
        svg = path.read_text(encoding="utf-8")
        svg = replace_id(svg, "repo_data", str(repos))
        svg = replace_id(svg, "follower_data", str(followers))
        svg = replace_id(svg, "star_data", str(stars))
        svg = replace_id(svg, "updated_data", updated)
        path.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
