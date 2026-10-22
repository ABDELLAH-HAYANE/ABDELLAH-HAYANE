"""Génère les stats GitHub et les insère entre les marqueurs du README."""
import json
import os
import re
import urllib.request

USER = os.environ["GH_USER"]
TOKEN = os.environ["GH_TOKEN"]
API = "https://api.github.com"


def get(path):
    req = urllib.request.Request(
        API + path,
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def bar(pct, width=25):
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


user = get(f"/users/{USER}")
repos = [r for r in get(f"/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
stars = sum(r["stargazers_count"] for r in repos)
commits = get(f"/search/commits?q=author:{USER}&per_page=1")["total_count"]

langs = {}
for r in repos:
    for lang, size in get(f"/repos/{USER}/{r['name']}/languages").items():
        langs[lang] = langs.get(lang, 0) + size
total = sum(langs.values()) or 1

lines = [
    f"{'Public repos':<24}{user['public_repos']}",
    f"{'Total commits':<24}{commits}",
    f"{'Stars earned':<24}{stars}",
    f"{'Followers':<24}{user['followers']}",
]
lang_lines = [
    f"{name:<24}{bar(size / total * 100)}   {size / total * 100:5.2f} %"
    for name, size in sorted(langs.items(), key=lambda kv: -kv[1])[:6]
]

block = (
    "**GitHub in numbers**\n\n```text\n" + "\n".join(lines) + "\n```\n\n"
    "**Top languages (by code size)**\n\n```text\n" + "\n".join(lang_lines) + "\n```"
)

readme = open("README.md", encoding="utf-8").read()
new = re.sub(
    r"(<!--START_SECTION:ghstats-->).*?(<!--END_SECTION:ghstats-->)",
    lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}",
    readme,
    flags=re.S,
)
open("README.md", "w", encoding="utf-8").write(new)
