"""
Downloads APRA prudential standard PDFs directly from apra.gov.au.
Download only — does NOT parse or chunk.
"""

from datetime import date
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

ATTRIBUTION = (
    "Crown copyright, Commonwealth of Australia (APRA), "
    "reproduced for research purposes."
)

STANDARDS = [
    {
        "name": "CPS 220 Risk Management",
        "url": "https://www.apra.gov.au/sites/default/files/Prudential-Standard-CPS-220-Risk-Management-(July-2017).pdf",
        "filename": "cps220.pdf",
    },
    {
        "name": "CPS 234 Information Security",
        "url": "https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf",
        "filename": "cps234.pdf",
    },
    {
        "name": "CPS 230 Operational Risk Management",
        "url": "https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf",
        "filename": "cps230.pdf",
    },
]

DATA_DIR.mkdir(exist_ok=True)

today = date.today().isoformat()
provenance_path = DATA_DIR / "provenance.md"

for standard in STANDARDS:
    response = requests.get(standard["url"], headers=HEADERS)
    response.raise_for_status()

    out_path = DATA_DIR / standard["filename"]
    out_path.write_bytes(response.content)

    print(f"{standard['name']}: saved {out_path} ({len(response.content)} bytes)")

    with open(provenance_path, "a") as f:
        f.write(f"## {standard['name']}\n\n")
        f.write(f"- url: {standard['url']}\n")
        f.write(f"- download date: {today}\n")
        f.write(f"- attribution: {ATTRIBUTION}\n\n")

print(f"\nAppended provenance entries to {provenance_path}")
