"""
One-off: wipe corpus_chunks and rerun the full ingest.
Use after changing chunking logic in src/ingest.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import ingest
from db import get_connection

if __name__ == "__main__":
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE corpus_chunks RESTART IDENTITY CASCADE")
    conn.commit()
    conn.close()

    ingest.main()
