"""
Retrieval only: dense (pgvector cosine), BM25 (Postgres FTS), and RRF combiner.
No RAG pipeline here — that's a separate stage.
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

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def embed_query(query: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query],
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return np.array(response.data[0].embedding)


def dense_search(
    query_embedding: list[float],
    source_filter: list[str] | None = None,
    top_k: int = 20,
) -> list[dict]:
    conn = get_connection()
    register_vector(conn)

    sql = """
        SELECT id, source, paragraph_id, text, 1 - (embedding <=> %s) AS score
        FROM corpus_chunks
        WHERE embedding IS NOT NULL
          AND paragraph_id NOT LIKE %s
    """
    params: list = [query_embedding, "%_SCHEDULE"]

    if source_filter:
        sql += " AND source = ANY(%s)"
        params.append(source_filter)

    sql += " ORDER BY embedding <=> %s LIMIT %s"
    params.extend([query_embedding, top_k])

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    conn.close()

    return [
        {"id": row[0], "source": row[1], "paragraph_id": row[2], "text": row[3], "score": row[4]}
        for row in rows
    ]


def bm25_search(
    query: str,
    source_filter: list[str] | None = None,
    top_k: int = 20,
) -> list[dict]:
    conn = get_connection()

    sql = """
        SELECT id, source, paragraph_id, text,
               ts_rank(to_tsvector('english', text), plainto_tsquery('english', %s)) AS score
        FROM corpus_chunks
        WHERE to_tsvector('english', text) @@ plainto_tsquery('english', %s)
          AND paragraph_id NOT LIKE %s
    """
    params: list = [query, query, "%_SCHEDULE"]

    if source_filter:
        sql += " AND source = ANY(%s)"
        params.append(source_filter)

    sql += " ORDER BY score DESC LIMIT %s"
    params.append(top_k)

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    conn.close()

    return [
        {"id": row[0], "source": row[1], "paragraph_id": row[2], "text": row[3], "score": row[4]}
        for row in rows
    ]


def rrf_search(
    query: str,
    query_embedding: list[float],
    source_filter: list[str] | None = None,
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    dense_results = dense_search(query_embedding, source_filter=source_filter, top_k=20)
    bm25_results = bm25_search(query, source_filter=source_filter, top_k=20)

    dense_ranks = {row["id"]: i + 1 for i, row in enumerate(dense_results)}
    bm25_ranks = {row["id"]: i + 1 for i, row in enumerate(bm25_results)}

    chunks_by_id = {row["id"]: row for row in dense_results}
    for row in bm25_results:
        chunks_by_id.setdefault(row["id"], row)

    rrf_scores = {}
    for chunk_id in chunks_by_id:
        score = 0.0
        if chunk_id in dense_ranks:
            score += 1 / (k + dense_ranks[chunk_id])
        if chunk_id in bm25_ranks:
            score += 1 / (k + bm25_ranks[chunk_id])
        rrf_scores[chunk_id] = score

    ranked_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)[:top_k]

    return [
        {
            "id": chunk_id,
            "source": chunks_by_id[chunk_id]["source"],
            "paragraph_id": chunks_by_id[chunk_id]["paragraph_id"],
            "text": chunks_by_id[chunk_id]["text"],
            "rrf_score": rrf_scores[chunk_id],
            "dense_rank": dense_ranks.get(chunk_id),
            "bm25_rank": bm25_ranks.get(chunk_id),
        }
        for chunk_id in ranked_ids
    ]


if __name__ == "__main__":
    smoke_query = "What are the general obligations of a financial services licensee?"

    query_embedding = embed_query(smoke_query)
    results = rrf_search(smoke_query, query_embedding, top_k=5)

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. [{result['source']}] {result['paragraph_id']} "
            f"(rrf={result['rrf_score']:.5f}) {result['text'][:150]!r}"
        )
