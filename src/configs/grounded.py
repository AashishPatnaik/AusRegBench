"""
Config 5: grounded / citation-forced RAG. Model must quote the provision
verbatim and cite the paragraph ID, and refuse if unsupported.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langsmith import traceable
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retrieval import embed_query, rrf_search

load_dotenv()

GENERATION_MODEL = "gpt-4o"
CONFIG_NAME = "grounded"
UNSUPPORTED_PREFIX = "UNSUPPORTED:"

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a precise legal research assistant for Australian financial regulation.\n"
    "You must answer using ONLY the provided context, following these strict rules:\n"
    "1. For every obligation or legal requirement you state, you MUST include:\n"
    "   a) The exact verbatim quote from the provision (in quotation marks)\n"
    "   b) The citation in format [source | paragraph_id]\n"
    "2. Do NOT paraphrase obligations — quote them exactly as written.\n"
    "3. If the provided context does not contain sufficient information to answer "
    "the question with verbatim quotes, respond with exactly:\n"
    "'UNSUPPORTED: The retrieved context does not contain sufficient information "
    "to answer this question with required citations.'\n"
    "4. Never invent, infer, or extrapolate obligations not explicitly stated "
    "in the provided context.\n"
    "The source name must be the exact source identifier from the context "
    "(e.g. corporations_act_2001, cps234), not the word 'source'."
)


@traceable(name="grounded")
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
    unsupported = answer.strip().startswith(UNSUPPORTED_PREFIX)

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
        "unsupported": unsupported,
    }


if __name__ == "__main__":
    smoke_query = "What are the general obligations of a financial services licensee?"

    result = run(smoke_query)

    print(result["answer"])
    print("\nRetrieved paragraph IDs:")
    for chunk in result["retrieved_chunks"]:
        print(f"- [{chunk['source']}] {chunk['paragraph_id']}")
