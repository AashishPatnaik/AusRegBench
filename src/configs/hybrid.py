"""
Config 2: hybrid RAG. Embed query -> BM25 + dense + RRF -> generate with citations.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retrieval import embed_query, rrf_search

load_dotenv()

GENERATION_MODEL = "gpt-4o"
CONFIG_NAME = "hybrid"

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a precise legal research assistant for Australian financial regulation. "
    "Answer using ONLY the provided context. "
    "Every claim must cite the exact source and paragraph ID in the format "
    "[source | paragraph_id]. The source name must be the exact source identifier "
    "from the context (e.g. corporations_act_2001, cps234), not the word 'source'. "
    "If the context does not support the answer, "
    "say 'Not found in retrieved context.'"
)


def run(query: str, source_filter: list[str] | None = None) -> dict:
    query_embedding = embed_query(query)
    retrieved_chunks = rrf_search(query, query_embedding, source_filter=source_filter, top_k=5)

    context = "\n".join(
        f"[{chunk['source']} | {chunk['paragraph_id']}]\n{chunk['text']}\n"
        for chunk in retrieved_chunks
    )

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
                "rrf_score": chunk["rrf_score"],
                "dense_rank": chunk["dense_rank"],
                "bm25_rank": chunk["bm25_rank"],
            }
            for chunk in retrieved_chunks
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
        print(
            f"- [{chunk['source']}] {chunk['paragraph_id']} "
            f"(dense_rank={chunk['dense_rank']}, bm25_rank={chunk['bm25_rank']})"
        )
