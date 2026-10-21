import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

papers = json.loads(
    Path("_data/citation-papers.json").read_text(encoding="utf-8")
)

output_dir = Path("assets/citations")
output_dir.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0"

failed = []

for paper in papers:
    paper_id = paper["id"]
    url = paper["url"].strip()

    if not url:
        print(f"Skipped {paper_id}: no URL supplied.")
        continue

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        if not soup.select_one("#gsc_oci_title"):
            raise ValueError("Article page unavailable or blocked.")

        count = None

        for link in soup.select('a[href*="cites="]'):
            match = re.fullmatch(
                r"Cited by\s+([\d,]+)",
                link.get_text(" ", strip=True),
            )

            if match:
                count = int(match.group(1).replace(",", ""))
                break

        if count is None:
            raise ValueError(
                "Count unavailable; previous value retained."
            )

        updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        label = f"{count:,}"
        width = max(14, len(label) * 9 + 4)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
 width="{width}" height="20" role="img"
 aria-label="{count} Google Scholar citations">
 <title>{count} Google Scholar citations;
 checked {updated} UTC</title>
 <text x="1" y="15" font-family="Arial,sans-serif"
  font-size="14" fill="#00407A">{label}</text>
</svg>
"""

        (output_dir / f"{paper_id}.svg").write_text(
            svg, encoding="utf-8"
        )

        print(f"Updated {paper_id}: {count}")

    except Exception as error:
        failed.append(paper_id)
        print(f"Failed {paper_id}: {error}")

    time.sleep(5)

if failed:
    print("Failed papers:", ", ".join(failed))
    sys.exit(1)
