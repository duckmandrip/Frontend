import json
import os
import re
from urllib.parse import unquote, urlparse
import requests

INPUT_FILE = "links.txt"
OUTPUT_FILE = "GAMES.json"
FORCE_HTTP = True

def get_remote_size(url):
    try:
        res = requests.head(url, allow_redirects=True, timeout=10)
        if res.status_code == 200 and "Content-Length" in res.headers:
            return int(res.headers["Content-Length"])
    except Exception:
        pass
    return 0

def get_title_metadata(title_id):
    api_url = f"https://serialstation.com{title_id}"
    try:
        res = requests.get(api_url, timeout=10)
        if res.status_code == 200:
            info = res.json()
            return info.get("name"), info.get("region", "USA"), info.get("icon_url")
    except Exception:
        pass
    return None, "USA", None

def main():
    if not os.path.exists(INPUT_FILE):
        return

    catalog = {"DATA": {}}

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip().lower().endswith(".pkg")]

    for url in urls:
        filename = unquote(os.path.basename(urlparse(url).path))
        match = re.search(r"(CUSA\d{5})", filename, re.IGNORECASE)
        title_id = match.group(1).upper() if match else "CUSA00000"

        size_bytes = get_remote_size(url)
        official_name, region, cover_url = get_title_metadata(title_id) if title_id != "CUSA00000" else (None, "USA", None)

        if not official_name:
            official_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")

        final_url = url.replace("https://", "http://", 1) if FORCE_HTTP else url

        catalog["DATA"][final_url] = {
            "title_id": title_id,
            "region": region,
            "name": official_name,
            "version": "01.00",
            "release": "2024-01-01",
            "size": size_bytes,
            "min_fw": "9.00",
            "cover_url": cover_url
        }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(catalog, out, indent=2)

if __name__ == "__main__":
    main()
      
