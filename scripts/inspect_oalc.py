"""
Throwaway inspection script — DO NOT use in pipeline.
Streams OALC, finds first Corporations Act 2001 (Cth) primary-legislation record,
and prints enough of the text to judge how section/heading markers appear.
"""

from datasets import load_dataset

ds = load_dataset(
    "isaacus/open-australian-legal-corpus",
    split="corpus",
    streaming=True,
)

target = None
for i, record in enumerate(ds):
    if i % 5000 == 0:
        print(f"  scanned {i} records...")

    if (
        record.get("jurisdiction") == "commonwealth"
        and record.get("type") == "primary_legislation"
        and "Corporations Act 2001" in (record.get("citation") or "")
    ):
        target = record
        print(f"\nFound at record #{i}\n")
        break

if target is None:
    print("No matching record found.")
else:
    text = target.pop("text")

    print("=== FIELDS (excl. text) ===")
    for k, v in target.items():
        print(f"  {k}: {v!r}")

    print(f"\n=== TEXT LENGTH ===")
    print(f"  len(text) = {len(text)}")

    print(f"\n=== text[:3000] ===")
    print(text[:3000])

    print(f"\n=== text[50000:53000] ===")
    if len(text) >= 50000:
        print(text[50000:53000])
    else:
        print(f"  (text is only {len(text)} chars — no slice at 50000)")
