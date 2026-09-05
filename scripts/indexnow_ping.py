#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

HOST = "delight0517.github.io"
KEY = "8f3a5e8c9d2b4f6a9e1c2d3b4f5a6e7d" # generated random hex for indexnow
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

def ping():
    url = "https://api.indexnow.org/indexnow"
    data = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": [
            f"https://{HOST}/",
            f"https://{HOST}/index.html"
        ]
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(req)
        print(f"IndexNow Ping Successful: {response.status}")
    except Exception as e:
        print(f"IndexNow Ping Failed: {e}")

if __name__ == "__main__":
    ping()
