"""
Config 4: KG-augmented RAG. RRF retrieve -> expand via cross-reference KG -> generate.

paragraph_id is only unique within a source (e.g. "5" exists in both
corporations_act_2001 and cps234), so the KG is keyed by "source:paragraph_id"
rather than paragraph_id alone to avoid cross-source collisions.
"""

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import get_connection
from retrieval import embed_query, rrf_search

load_dotenv()

GENERATION_MODEL = "gpt-4o"
CONFIG_NAME = "kg_augmented"
MAX_CONTEXT_CHUNKS = 10

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a precise legal research assistant for Australian financial regulation. "
    "Answer using ONLY the provided context. "
    "Every claim must cite the exact source and paragraph ID in the format "
    "[source | paragraph_id]. The source name must be the exact source identifier "
    "from the context (e.g. corporations_act_2001, cps234), not the word 'source'. "
    "If the context does not support the answer, "
    "say 'Not found in retrieved context.' "
    "Context marked [KG-EXPANDED] provides supporting provisions referenced by "
    "the primary retrieved provisions."
)

SECTION_REF_PATTERN = re.compile(r"section\s+(\d+[A-Z]*)", re.IGNORECASE)
SUBSECTION_REF_PATTERN = re.compile(r"subsection\s+\((\d+)\)", re.IGNORECASE)
CPS_REF_PATTERN = re.compile(r"CPS\s+(\d+)", re.IGNORECASE)
PARAGRAPH_REF_PATTERN = re.compile(r"paragraph\s+(\d+)", re.IGNORECASE)


def _base_section_id(paragraph_id: str) -> str:
    return paragraph_id.split("(")[0]


def build_kg(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT source, paragraph_id, text FROM corpus_chunks WHERE paragraph_id NOT LIKE %s",
            ("%_SCHEDULE",),
        )
        rows = cur.fetchall()

    ids_by_source: dict[str, set] = {}
    base_index_by_source: dict[str, dict] = {}
    for source, paragraph_id, _ in rows:
        ids_by_source.setdefault(source, set()).add(paragraph_id)
        base_index_by_source.setdefault(source, {}).setdefault(
            _base_section_id(paragraph_id), []
        ).append(paragraph_id)

    cps_source_by_number = {}
    for source in ids_by_source:
        match = re.fullmatch(r"cps(\d+)", source, re.IGNORECASE)
        if match:
            cps_source_by_number[match.group(1)] = source

    kg: dict[str, list[str]] = {}

    for source, paragraph_id, text in rows:
        referenced = set()
        base_id = _base_section_id(paragraph_id)

        for match in SECTION_REF_PATTERN.finditer(text):
            candidate = match.group(1)
            if candidate == base_id:
                continue
            for full_id in base_index_by_source.get(source, {}).get(candidate, ()):
                referenced.add(f"{source}:{full_id}")

        for match in SUBSECTION_REF_PATTERN.finditer(text):
            candidate = f"{base_id}({match.group(1)})"
            if candidate != paragraph_id and candidate in ids_by_source.get(source, ()):
                referenced.add(f"{source}:{candidate}")

        for match in CPS_REF_PATTERN.finditer(text):
            ref_source = cps_source_by_number.get(match.group(1))
            if ref_source and ref_source != source:
                first_id = min(ids_by_source[ref_source], key=lambda pid: (len(pid), pid))
                referenced.add(f"{ref_source}:{first_id}")

        for match in PARAGRAPH_REF_PATTERN.finditer(text):
            candidate = match.group(1)
            if candidate != paragraph_id and candidate in ids_by_source.get(source, ()):
                referenced.add(f"{source}:{candidate}")

        if referenced:
            kg[f"{source}:{paragraph_id}"] = sorted(referenced)

    return kg


def _fetch_chunk(conn, source: str, paragraph_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, text FROM corpus_chunks WHERE source = %s AND paragraph_id = %s LIMIT 1",
            (source, paragraph_id),
        )
        row = cur.fetchone()
    return {"id": row[0], "text": row[1]} if row else None


def expand_with_kg(chunks: list[dict], kg: dict, conn, max_hops: int = 1) -> list[dict]:
    expanded = []
    seen = set()

    for chunk in chunks:
        seen.add((chunk["source"], chunk["paragraph_id"]))
        expanded.append(
            {
                "id": chunk["id"],
                "source": chunk["source"],
                "paragraph_id": chunk["paragraph_id"],
                "text": chunk["text"],
                "kg_expanded": False,
                "referenced_by": None,
            }
        )

    frontier = [(chunk["source"], chunk["paragraph_id"]) for chunk in chunks]

    for _ in range(max_hops):
        if len(expanded) >= MAX_CONTEXT_CHUNKS:
            break
        next_frontier = []
        for source, paragraph_id in frontier:
            if len(expanded) >= MAX_CONTEXT_CHUNKS:
                break
            for ref in kg.get(f"{source}:{paragraph_id}", []):
                if len(expanded) >= MAX_CONTEXT_CHUNKS:
                    break
                ref_source, ref_paragraph_id = ref.split(":", 1)
                if (ref_source, ref_paragraph_id) in seen:
                    continue
                row = _fetch_chunk(conn, ref_source, ref_paragraph_id)
                if row is None:
                    continue
                seen.add((ref_source, ref_paragraph_id))
                expanded.append(
                    {
                        "id": row["id"],
                        "source": ref_source,
                        "paragraph_id": ref_paragraph_id,
                        "text": row["text"],
                        "kg_expanded": True,
                        "referenced_by": paragraph_id,
                    }
                )
                next_frontier.append((ref_source, ref_paragraph_id))
        frontier = next_frontier

    return expanded


_kg_conn = get_connection()
KG = build_kg(_kg_conn)
_kg_conn.close()


def _format_chunk(chunk: dict) -> str:
    if chunk["kg_expanded"]:
        return f"[KG-EXPANDED | {chunk['source']} | {chunk['paragraph_id']}]\n{chunk['text']}\n"
    return f"[{chunk['source']} | {chunk['paragraph_id']}]\n{chunk['text']}\n"


def run(query: str, source_filter: list[str] | None = None) -> dict:
    query_embedding = embed_query(query)
    retrieved_chunks = rrf_search(query, query_embedding, source_filter=source_filter, top_k=5)

    conn = get_connection()
    expanded_chunks = expand_with_kg(retrieved_chunks, KG, conn, max_hops=1)
    conn.close()

    context = "\n".join(_format_chunk(chunk) for chunk in expanded_chunks)

    user_prompt = context + "\n\nQuestion: " + query

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    answer = response.choices[0].message.content

    return {
        "query": query,
        "answer": answer,
        "retrieved_chunks": [
            {
                "source": chunk["source"],
                "paragraph_id": chunk["paragraph_id"],
                "text": chunk["text"][:200],
                "kg_expanded": chunk["kg_expanded"],
                "referenced_by": chunk["referenced_by"],
            }
            for chunk in expanded_chunks
        ],
        "model": GENERATION_MODEL,
        "config_name": CONFIG_NAME,
    }


if __name__ == "__main__":
    smoke_query = "What are the general obligations of a financial services licensee?"

    result = run(smoke_query)

    print(result["answer"])
    print("\nRetrieved paragraph IDs:")
    for chunk in result["retrieved_chunks"]:
        if chunk["kg_expanded"]:
            print(
                f"- [KG-EXPANDED] [{chunk['source']}] {chunk['paragraph_id']} "
                f"(referenced_by={chunk['referenced_by']})"
            )
        else:
            print(f"- [{chunk['source']}] {chunk['paragraph_id']}")
