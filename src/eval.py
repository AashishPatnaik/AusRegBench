"""
Runs all five RAG configs against a single query and returns structured
results for comparison. No scoring/taxonomy logic here yet.
"""

import sys
from pathlib import Path

from langsmith import traceable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from configs.grounded import run as run_grounded
from configs.hybrid import run as run_hybrid
from configs.kg_augmented import run as run_kg
from configs.naive import run as run_naive
from configs.rerank import run as run_rerank

CONFIG_RUNNERS = {
    "naive": run_naive,
    "hybrid": run_hybrid,
    "rerank": run_rerank,
    "kg_augmented": run_kg,
    "grounded": run_grounded,
}


@traceable(name="evaluate_query")
def evaluate_query(query: str, source_filter: list[str] | None = None) -> dict:
    results = {}

    for config_name, run_fn in CONFIG_RUNNERS.items():
        try:
            results[config_name] = run_fn(query, source_filter=source_filter)
        except Exception as e:
            results[config_name] = {"error": str(e), "config_name": config_name}

    return {"query": query, "results": results}


if __name__ == "__main__":
    smoke_query = (
        "What are the obligations of an APRA-regulated entity under CPS 234 "
        "regarding information security incidents?"
    )

    evaluation = evaluate_query(smoke_query)

    for config_name, result in evaluation["results"].items():
        print(f"=== {config_name} ===")

        if "error" in result:
            print(f"ERROR: {result['error']}")
            print("-" * 60)
            continue

        print(result["answer"][:300])
        print("\nRetrieved paragraph IDs:")
        for chunk in result["retrieved_chunks"]:
            print(f"- [{chunk['source']}] {chunk['paragraph_id']}")

        print("-" * 60)
