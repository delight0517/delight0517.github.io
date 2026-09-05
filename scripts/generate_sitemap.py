#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime, timezone
import subprocess

REPO = Path(__file__).resolve().parent.parent
BASE_URL = "https://delight0517.github.io"

def git_lastmod(rel_path: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "log", "-1", "--format=%cI", "--", rel_path],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if out:
            return out[:10]
    except Exception:
        pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def generate():
    urls = []
    # Root index.html
    index_file = REPO / "index.html"
    if index_file.exists():
        urls.append((f"{BASE_URL}/", git_lastmod("index.html")))

    # We can also read other html files in root if needed
    for html_file in REPO.glob("*.html"):
        if html_file.name == "index.html":
            continue
        urls.append((f"{BASE_URL}/{html_file.name}", git_lastmod(html_file.name)))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    
    sitemap_path = REPO / "sitemap.xml"
    sitemap_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {sitemap_path} with {len(urls)} URLs")

if __name__ == "__main__":
    generate()
