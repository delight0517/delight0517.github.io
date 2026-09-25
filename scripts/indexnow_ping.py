#!/usr/bin/env python3
import os
import urllib.request
import json
import xml.etree.ElementTree as ET

HOST = "delight0517.github.io"
KEY = "8f3a5e8c9d2b4f6a9e1c2d3b4f5a6e7d" # generated random hex for indexnow
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
SITEMAP = os.environ.get("INDEXNOW_SITEMAP_URL", f"https://{HOST}/sitemap.xml")

def ping():
    url = "https://api.indexnow.org/indexnow"
    with urllib.request.urlopen(SITEMAP, timeout=20) as response:
        root = ET.fromstring(response.read())
    urls = [node.text for node in root.iter() if node.tag.endswith("}loc") and node.text]
    if not urls:
        raise ValueError(f"No URLs found in {SITEMAP}")
    data = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"IndexNow accepted {len(urls)} sitemap URLs: HTTP {response.status}")
    except Exception as e:
        print(f"IndexNow submission failed: {e}")
        raise

if __name__ == "__main__":
    ping()
