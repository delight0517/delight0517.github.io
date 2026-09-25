#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parent.parent
BASE_URL = "https://delight0517.github.io"
SITEMAP = REPO / "sitemap.xml"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def git_lastmod(path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO), "log", "-1", "--format=%cI", "--", path],
            capture_output=True, text=True, timeout=10, check=True,
        )
        if result.stdout.strip():
            return result.stdout.strip()[:10]
    except (OSError, subprocess.SubprocessError):
        pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def local_public_pages() -> list[tuple[str, str]]:
    paths = [REPO / "index.html"]
    paths += sorted(path for path in REPO.glob("*.html") if not path.name.startswith("google"))
    help_dir = REPO / "everytime-reminder"
    paths += sorted(path for path in help_dir.glob("*.html") if path.name != "privacy.html")
    pages = []
    for path in paths:
        if not path.is_file():
            continue
        relative = path.relative_to(REPO).as_posix()
        url_path = "/" if relative == "index.html" else f"/{relative}"
        if relative == "everytime-reminder/index.html":
            url_path = "/everytime-reminder/"
        pages.append((BASE_URL + url_path, relative))
    return pages


def generate() -> None:
    existing: dict[str, dict[str, str]] = {}
    if SITEMAP.exists():
        root = ET.parse(SITEMAP).getroot()
        for item in root.findall("s:url", NS):
            loc = item.findtext("s:loc", namespaces=NS)
            if not loc or not loc.startswith(BASE_URL + "/"):
                continue
            entry = {}
            for tag in ("lastmod", "priority"):
                value = item.findtext(f"s:{tag}", namespaces=NS)
                if value:
                    entry[tag] = value
            existing[loc] = entry

    for url, path in local_public_pages():
        existing.setdefault(url, {})["lastmod"] = git_lastmod(path)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, fields in existing.items():
        entry = f"  <url><loc>{escape(url)}</loc>"
        for tag in ("lastmod", "priority"):
            if fields.get(tag):
                entry += f"<{tag}>{escape(fields[tag])}</{tag}>"
        lines.append(entry + "</url>")
    lines.append("</urlset>")
    SITEMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {SITEMAP} with {len(existing)} URLs")


if __name__ == "__main__":
    generate()
