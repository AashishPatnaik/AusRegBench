"""
Fetches raw provision text for a fixed list of candidate paragraph_ids,
for human review when hand-constructing the gold query set.

Does NOT generate questions. Read-only against corpus_chunks.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from db import get_connection

TARGETS: dict[str, list[str]] = {
    "corporations_act_2001": [
        "674(2)", "675", "677", "1017A", "1017B", "1017C", "1017D",
        "1017E", "1017G", "766A", "766B", "766C", "911A", "911B",
        "912C", "912D", "912F", "913B", "915B", "916A",
        "961G", "961H", "961J", "961K", "962", "962G",
        "992A", "1041A", "1041B", "1041C", "1041E",
        "1308", "1309", "1317E",
    ],
    "banking_act_1959": [
        "9", "11", "11A", "11B", "11C", "11D", "11F",
        "13A", "14", "16", "62", "63", "66",
    ],
    "cps220": ["21", "22", "23", "26", "27", "28", "29", "30", "31", "32"],
    "cps234": ["10", "11", "12", "13", "15", "16", "17", "18", "19", "20", "21", "22", "26", "27", "28", "29", "30"],
    "cps230": [
        "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25",
        "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "37", "38", "39",
        "40", "41", "42", "43", "44", "45", "46", "48", "49", "50",
    ],
}

# Strips a trailing "(...)" group, e.g. "961B(1)" -> "961B", to fall back
# to the parent section if the chunker didn't split out the subsection.
SUBSECTION_SUFFIX = re.compile(r"^(.*?)(\([^()]+\))+$")


def fetch_exact(cur, source: str, paragraph_id: str) -> list[tuple[int, str]]:
    cur.execute(
        """
        SELECT chunk_index, text FROM corpus_chunks
        WHERE source = %s AND paragraph_id = %s
        ORDER BY chunk_index NULLS FIRST
        """,
        (source, paragraph_id),
    )
    return cur.fetchall()


def main() -> None:
    conn = get_connection()

    with conn.cursor() as cur:
        for source, paragraph_ids in TARGETS.items():
            for paragraph_id in paragraph_ids:
                rows = fetch_exact(cur, source, paragraph_id)
                note = None

                if not rows:
                    match = SUBSECTION_SUFFIX.match(paragraph_id)
                    if match:
                        base_id = match.group(1)
                        fallback_rows = fetch_exact(cur, source, base_id)
                        if fallback_rows:
                            rows = fallback_rows
                            note = (
                                f"NOTE: '{paragraph_id}' was not chunked separately; "
                                f"showing full section '{base_id}' instead — "
                                f"find subsection ({match.group(2)[1:-1] if match.group(2) else '?'}) within."
                            )

                print(f"{source} | {paragraph_id}")
                if note:
                    print(note)
                if not rows:
                    print("[NOT FOUND]")
                else:
                    text = "\n".join(text for _, text in rows)
                    print(text.strip())
                print("---")

    conn.close()


if __name__ == "__main__":
    main()
