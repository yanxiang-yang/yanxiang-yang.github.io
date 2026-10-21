import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

# Your publication IDs remain unchanged.
papers = {
    "leaderboards": "10.1016/j.chb.2024.108532",
    "gamification-review": "10.1016/j.amepre.2021.10.005",
    "fitness-app-usage": "10.2196/26063",
    "activity-maintenance": "10.1093/tbm/ibaa086",
    "interwalk": "10.2196/30602",
    "exercise-executive-function": "10.1136/bjsports-2018-099825",
    "accelerometer": "10.7717/peerj.5775",
    "transfer-fees": "10.1080/16184742.2022.2153898",
    "nonprofit-organizations": "10.1002/nml.21651",
    "athlete-activism": "10.1177/01937235251334584",
    "human-rights": "10.3727/152599522X16419948695323",
    "brand-positioning": "10.1123/jsm.2020-0426",
}

output_dir = Path("assets/citations")
output_dir.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "AcademicWebsiteCitationUpdater/1.0 "
        "(https://yanxiang-yang.github.io)"
    )
})

failed = []

for paper_id, doi in papers.items():
    try:
        response = session.get(
            f"https://api.crossref.org/works/{quote(doi, safe='')}",
            timeout=30,
        )
        response.raise_for_status()
        metadata = response.json()["message"]

        count = metadata.get("is-referenced-by-count")
        if (
            not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
        ):
            raise ValueError("Valid citation count unavailable.")

        updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        label = f"{count:,}"
        width = max(14, len(label) * 9 + 4)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
 width="{width}" height="20" role="img"
 aria-label="{count} Crossref citations">
 <title>{count} Crossref citations;
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

    time.sleep(1)

if failed:
    print("Failed papers:", ", ".join(failed))
    sys.exit(1)
