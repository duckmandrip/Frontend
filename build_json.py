import csv
import json
import os
import re

INPUT_FILE = "links.txt"
OUTPUT_FILE = "GAMES.json"

def parse_size(size_str):
    # Converts strings like "34.9MB" or "1.5GB" into exact bytes
    match = re.match(r"([\d.]+)\s*(B|KB|MB|GB|TB)", size_str.strip(), re.IGNORECASE)
    if not match:
        return 0
    num = float(match.group(1))
    unit = match.group(2).upper()
    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    return int(num * multipliers.get(unit, 1))

def main():
    if not os.path.exists(INPUT_FILE):
        return

    catalog = {"DATA": {}}

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue

            # Find the .pkg URL anywhere in the row
            pkg_url = next((col.strip() for col in row if ".pkg" in col.lower() and col.strip().startswith("http")), None)
            if not pkg_url:
                continue

            # Keep HTTP for PS4 SSL compatibility
            pkg_url = pkg_url.replace("https://", "http://", 1)

            # Extract Title ID (e.g., CUSA00001)
            tid_match = re.search(r"(CUSA\d{5})", ",".join(row), re.IGNORECASE)
            title_id = tid_match.group(1).upper() if tid_match else "CUSA00000"

            # Pull name, version, and size from your CSV columns if present
            name = row[1].strip() if len(row) > 1 and row[1].strip() else title_id
            version = row[4].strip() if len(row) > 4 and row[4].strip() else "01.00"
            size_bytes = parse_size(row[6]) if len(row) > 6 else 0

            # Format version to 01.07 style if needed
            if re.match(r"^\d+\.\d+$", version):
                major, minor = version.split(".")
                version = f"{int(major):02d}.{minor}"

            catalog["DATA"][pkg_url] = {
                "title_id": title_id,
                "region": "USA",
                "name": name,
                "version": version,
                "release": "2024-01-01",
                "size": size_bytes,
                "min_fw": "9.00",
                "cover_url": ""
            }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(catalog, out, indent=2)

if __name__ == "__main__":
    main()
            
