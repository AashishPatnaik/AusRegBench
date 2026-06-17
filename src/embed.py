"""
Embeds corpus_chunks rows where embedding IS NULL using text-embedding-3-large,
and writes vectors back to the database. Does not chunk, does not change schema.
"""

import os

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg2 import register_vector

from db import get_connection

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072
BATCH_SIZE = 100
PROGRESS_EVERY = 500
COST_PER_MILLION_TOKENS = 0.13

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def fetch_batch(conn, limit: int) -> list[tuple[int, str]]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, text FROM corpus_chunks WHERE embedding IS NULL AND LENGTH(text) <= 8000 LIMIT %s",
            (limit,),
        )
        return cur.fetchall()


def embed_batch(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return [item.embedding for item in response.data]


def update_embeddings(conn, ids: list[int], vectors: list[list[float]]) -> None:
    with conn.cursor() as cur:
        for chunk_id, vector in zip(ids, vectors):
            cur.execute(
                "UPDATE corpus_chunks SET embedding = %s WHERE id = %s",
                (np.array(vector), chunk_id),
            )
    conn.commit()


def main() -> None:
    conn = get_connection()
    register_vector(conn)

    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM corpus_chunks WHERE embedding IS NULL AND LENGTH(text) <= 8000")
        total = cur.fetchone()[0]

    embedded = 0
    total_chars = 0

    while True:
        batch = fetch_batch(conn, BATCH_SIZE)
        if not batch:
            break

        ids = [row[0] for row in batch]
        texts = [row[1] for row in batch]

        vectors = embed_batch(texts)
        update_embeddings(conn, ids, vectors)

        embedded += len(ids)
        total_chars += sum(len(t) for t in texts)

        if embedded % PROGRESS_EVERY == 0 or embedded == total:
            print(f"Embedded {embedded}/{total} chunks")

    conn.close()

    estimated_tokens = total_chars / 4
    estimated_cost = (estimated_tokens / 1_000_000) * COST_PER_MILLION_TOKENS

    print(f"\nTotal embedded: {embedded}")
    print(f"Estimated tokens: {estimated_tokens:.0f}")
    print(f"Estimated cost: ${estimated_cost:.4f}")


if __name__ == "__main__":
    main()
