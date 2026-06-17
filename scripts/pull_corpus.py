"""
Single streaming pass over isaacus/open-australian-legal-corpus.
Saves full records for the Corporations Act 2001 (Cth) and Banking Act 1959 (Cth),
and lists APRA prudential standard candidates for inspection (no text saved yet).
Does NOT chunk or embed — ingestion to disk only.
"""

import json
from pathlib import Path

from datasets import load_dataset

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

APRA_KEYWORDS = ["prudential standard", "cps 220", "cps 230", "cps 234"]

ds = load_dataset(
    "isaacus/open-australian-legal-corpus",
    split="corpus",
    streaming=True,
)

corporations_act = None
banking_act = None
apra_candidates = []

for i, record in enumerate(ds):
    if i % 5000 == 0:
        print(f"  scanned {i} records...")

    citation = record.get("citation") or ""
    jurisdiction = record.get("jurisdiction")
    rec_type = record.get("type")

    if (
        corporations_act is None
        and jurisdiction == "commonwealth"
        and rec_type == "primary_legislation"
        and "Corporations Act 2001" in citation
    ):
        corporations_act = record
        print(f"\nFound Corporations Act 2001 (Cth) at record #{i}\n")

    if (
        banking_act is None
        and jurisdiction == "commonwealth"
        and rec_type == "primary_legislation"
        and "Banking Act 1959" in citation
    ):
        banking_act = record
        print(f"\nFound Banking Act 1959 (Cth) at record #{i}\n")

    if any(kw in citation.lower() for kw in APRA_KEYWORDS):
        print(f"  APRA candidate at #{i}: {citation!r}")
        apra_candidates.append(citation)

print(f"\n  scan complete: {i + 1} records total\n")

DATA_DIR.mkdir(exist_ok=True)

provenance_entries = []

for name, record in [
    ("corporations_act_2001", corporations_act),
    ("banking_act_1959", banking_act),
]:
    if record is None:
        continue
    out_path = DATA_DIR / f"{name}.json"
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    provenance_entries.append(record)

apra_path = DATA_DIR / "apra_candidates.txt"
with open(apra_path, "w") as f:
    f.write("\n".join(apra_candidates))

provenance_path = DATA_DIR / "provenance.md"
with open(provenance_path, "w") as f:
    f.write("# Provenance\n\n")
    f.write(
        "Source: [isaacus/open-australian-legal-corpus]"
        "(https://huggingface.co/datasets/isaacus/open-australian-legal-corpus), "
        "licensed CC BY 4.0. Attribution: Open Australian Legal Corpus, "
        "© Umar Butler, licensed under CC BY 4.0.\n\n"
    )
    for record in provenance_entries:
        f.write(f"## {record.get('citation')}\n\n")
        f.write(f"- version_id: {record.get('version_id')}\n")
        f.write(f"- date: {record.get('date')}\n")
        f.write(f"- url: {record.get('url')}\n\n")

print("=== SUMMARY ===")
print(f"Corporations Act 2001 (Cth): {'found' if corporations_act else 'NOT FOUND'}", end="")
if corporations_act:
    print(f" — {len(corporations_act['text'])} chars")
else:
    print()

print(f"Banking Act 1959 (Cth): {'found' if banking_act else 'NOT FOUND'}", end="")
if banking_act:
    print(f" — {len(banking_act['text'])} chars")
else:
    print()

print(f"APRA candidates found: {len(apra_candidates)}")
print(f"\nWrote: {DATA_DIR / 'provenance.md'}")
