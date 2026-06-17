"""
Clause-aware chunking that preserves paragraph IDs.

Loads raw text chunks + metadata into corpus_chunks (embedding left NULL).
Does NOT embed, does NOT call any embedding API.
"""

import json
import re
from pathlib import Path

import pdfplumber
from dotenv import load_dotenv
from psycopg2.extras import execute_values

from db import get_connection

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SECTION_PATTERN = re.compile(r"\n(\d+[A-Z]{0,4})\s{2,}")
SUBSECTION_PATTERN = re.compile(r"\n\s+\((\d+)\)")
APRA_PARAGRAPH_PATTERN = re.compile(r"\n(\d+)\.\s")

MAX_CHUNK_CHARS = 1500
MIN_CHUNK_CHARS = 50

ACT_SOURCES = [
    {"filename": "corporations_act_2001.json", "source": "corporations_act_2001"},
    {"filename": "banking_act_1959.json", "source": "banking_act_1959"},
]

APRA_SOURCES = [
    {
        "filename": "cps220.pdf",
        "source": "cps220",
        "version_id": "CPS220-July2017",
        "compilation_date": "2017-07-01",
        "url": "https://www.apra.gov.au/sites/default/files/Prudential-Standard-CPS-220-Risk-Management-(July-2017).pdf",
    },
    {
        "filename": "cps234.pdf",
        "source": "cps234",
        "version_id": "CPS234-July2019",
        "compilation_date": "2019-07-01",
        "url": "https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf",
    },
    {
        "filename": "cps230.pdf",
        "source": "cps230",
        "version_id": "CPS230-July2025",
        "compilation_date": "2025-07-01",
        "url": "https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf",
    },
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS corpus_chunks (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    paragraph_id TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    version_id TEXT,
    compilation_date TEXT,
    url TEXT,
    chunk_index INTEGER,
    text TEXT NOT NULL,
    embedding vector(3072)
);
"""

CREATE_INDEX_SOURCE_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_chunks_source ON corpus_chunks(source);"
)
CREATE_INDEX_PARAGRAPH_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_chunks_paragraph_id ON corpus_chunks(paragraph_id);"
)

INSERT_SQL = """
INSERT INTO corpus_chunks
    (source, paragraph_id, doc_type, jurisdiction, version_id, compilation_date, url, chunk_index, text)
VALUES %s
"""


def _split_long_chunk(paragraph_id: str, text: str) -> list[tuple[str, str]]:
    """Split an oversized Act chunk at subsection boundaries. Returns (paragraph_id, text) pairs."""
    matches = list(SUBSECTION_PATTERN.finditer(text))
    if not matches:
        return [(paragraph_id, text)]

    header = text[:matches[0].start()]
    pieces = []
    for idx, match in enumerate(matches):
        sub_start = match.start()
        sub_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sub_id = f"{paragraph_id}({match.group(1)})"
        pieces.append((sub_id, header + text[sub_start:sub_end]))
    return pieces


def chunk_act(record: dict) -> list[dict]:
    text = record["text"]

    start_match = re.search(r"^An Act", text, re.MULTILINE)
    if start_match is None:
        print("  WARNING: no 'An Act' marker found — skipping entire document")
        return []

    body = text[start_match.start():]

    section_matches = list(SECTION_PATTERN.finditer(body))
    if not section_matches:
        print("  WARNING: no section markers found in body")
        return []

    raw_sections = []
    for idx, match in enumerate(section_matches):
        sec_start = match.start()
        sec_end = section_matches[idx + 1].start() if idx + 1 < len(section_matches) else len(body)
        paragraph_id = match.group(1)
        raw_sections.append((paragraph_id, body[sec_start:sec_end]))

    chunks = []
    skipped = 0
    for paragraph_id, section_text in raw_sections:
        if len(section_text) > MAX_CHUNK_CHARS:
            pieces = _split_long_chunk(paragraph_id, section_text)
        else:
            pieces = [(paragraph_id, section_text)]

        for sub_id, piece_text in pieces:
            if len(piece_text) > 8000:
                sub_id = f"{paragraph_id}_SCHEDULE"

            if len(piece_text.strip()) < MIN_CHUNK_CHARS:
                skipped += 1
                continue
            chunks.append({"paragraph_id": sub_id, "text": piece_text})

    if skipped:
        print(f"  skipped {skipped} sub-50-char chunks")

    return chunks


def chunk_apra_pdf(path: Path) -> list[dict]:
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    matches = list(APRA_PARAGRAPH_PATTERN.finditer(text))
    if not matches:
        print("  WARNING: no paragraph markers found")
        return []

    chunks = []
    skipped = 0
    for idx, match in enumerate(matches):
        para_start = match.start()
        para_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        paragraph_id = match.group(1)

        if int(paragraph_id) > 150:
            skipped += 1
            continue

        chunk_text = text[para_start:para_end]

        if len(chunk_text.strip()) < MIN_CHUNK_CHARS:
            skipped += 1
            continue
        chunks.append({"paragraph_id": paragraph_id, "text": chunk_text})

    if skipped:
        print(f"  skipped {skipped} sub-50-char chunks")

    return chunks


def ensure_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
        cur.execute(CREATE_INDEX_SOURCE_SQL)
        cur.execute(CREATE_INDEX_PARAGRAPH_SQL)
    conn.commit()


def insert_chunks(conn, source: str, doc_type: str, version_id: str, compilation_date: str, url: str, chunks: list[dict]) -> None:
    rows = [
        (
            source,
            chunk["paragraph_id"],
            doc_type,
            "commonwealth",
            version_id,
            compilation_date,
            url,
            chunk_index,
            chunk["text"],
        )
        for chunk_index, chunk in enumerate(chunks)
    ]
    with conn.cursor() as cur:
        execute_values(cur, INSERT_SQL, rows)
    conn.commit()


def main() -> None:
    conn = get_connection()
    ensure_schema(conn)

    summary = []

    for act in ACT_SOURCES:
        path = DATA_DIR / act["filename"]
        print(f"\n=== {act['source']} ===")
        record = json.loads(path.read_text())

        chunks = chunk_act(record)
        print(f"  {len(chunks)} chunks")

        insert_chunks(
            conn,
            source=act["source"],
            doc_type="primary_legislation",
            version_id=record.get("version_id"),
            compilation_date=record.get("date"),
            url=record.get("url"),
            chunks=chunks,
        )

        summary.append((act["source"], chunks))

    for apra in APRA_SOURCES:
        path = DATA_DIR / apra["filename"]
        print(f"\n=== {apra['source']} ===")

        chunks = chunk_apra_pdf(path)
        print(f"  {len(chunks)} chunks")

        insert_chunks(
            conn,
            source=apra["source"],
            doc_type="prudential_standard",
            version_id=apra["version_id"],
            compilation_date=apra["compilation_date"],
            url=apra["url"],
            chunks=chunks,
        )

        summary.append((apra["source"], chunks))

    conn.close()

    print("\n=== SUMMARY ===")
    print(f"{'source':<25}{'chunks':>8}{'min_chars':>12}{'max_chars':>12}{'avg_chars':>12}")
    for source, chunks in summary:
        if not chunks:
            print(f"{source:<25}{0:>8}{'-':>12}{'-':>12}{'-':>12}")
            continue
        lengths = [len(c["text"]) for c in chunks]
        print(
            f"{source:<25}{len(chunks):>8}{min(lengths):>12}{max(lengths):>12}{sum(lengths) / len(lengths):>12.1f}"
        )


if __name__ == "__main__":
    main()
