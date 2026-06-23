"""
Runs the full benchmark: all gold queries through all 5 RAG configs,
scored by the two-layer judge in src/judge.py.

Writes results/raw_results.jsonl (one line per (query, config) pair) and
results/summary.json (taxonomy bucket counts per config).

Resumable: on (re)start, already-written (query_id, config_name) pairs in
raw_results.jsonl are skipped, so a crash mid-run doesn't redo finished work.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from db import get_connection
from eval import evaluate_query
from judge import evaluate_answer

QUERIES_PATH = Path(__file__).resolve().parent.parent / "queries" / "gold_set.jsonl"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RAW_RESULTS_PATH = RESULTS_DIR / "raw_results.jsonl"
SUMMARY_PATH = RESULTS_DIR / "summary.json"

CONFIG_NAMES = ["naive", "hybrid", "rerank", "kg_augmented", "grounded"]
TAXONOMY_BUCKETS = [
    "correct_and_faithful",
    "fabricated_citation",
    "misstated_obligation",
    "missing_citation",
    "real_but_irrelevant",
]


def load_gold_queries() -> list[dict]:
    with open(QUERIES_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]


def load_completed_pairs() -> set[tuple[str, str]]:
    completed = set()
    if not RAW_RESULTS_PATH.exists():
        return completed

    with open(RAW_RESULTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if "taxonomy_bucket" in record:
                completed.add((record["query_id"], record["config_name"]))

    return completed


def compute_summary() -> dict:
    counts = {
        config_name: {bucket: 0 for bucket in TAXONOMY_BUCKETS}
        for config_name in CONFIG_NAMES
    }
    totals = {config_name: 0 for config_name in CONFIG_NAMES}

    with open(RAW_RESULTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            bucket = record.get("taxonomy_bucket")
            config_name = record["config_name"]
            if bucket is None or config_name not in counts:
                continue
            totals[config_name] += 1
            counts[config_name][bucket] += 1

    return {
        config_name: {"total": totals[config_name], **counts[config_name]}
        for config_name in CONFIG_NAMES
    }


def run_benchmark() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)

    gold_queries = load_gold_queries()
    total_queries = len(gold_queries)
    completed = load_completed_pairs()

    with open(RAW_RESULTS_PATH, "a") as out_f:
        for i, gold_query in enumerate(gold_queries, start=1):
            pending_configs = [
                config_name
                for config_name in CONFIG_NAMES
                if (gold_query["id"], config_name) not in completed
            ]

            if not pending_configs:
                print(f"[{i}/{total_queries}] {gold_query['id']} | SKIPPED (already complete)")
                continue

            evaluation = evaluate_query(gold_query["question"])

            conn = get_connection()
            try:
                for config_name in CONFIG_NAMES:
                    if (gold_query["id"], config_name) in completed:
                        print(f"[{i}/{total_queries}] {gold_query['id']} | {config_name} | SKIPPED (resume)")
                        continue

                    config_result = evaluation["results"][config_name]

                    if "error" in config_result:
                        record = {
                            "query_id": gold_query["id"],
                            "config_name": config_name,
                            "error": config_result["error"],
                        }
                        out_f.write(json.dumps(record) + "\n")
                        out_f.flush()
                        print(f"[{i}/{total_queries}] {gold_query['id']} | {config_name} | ERROR")
                        continue

                    try:
                        judged = evaluate_answer(
                            query_id=gold_query["id"],
                            question=gold_query["question"],
                            gold_answer=gold_query["gold_answer"],
                            gold_citations=gold_query["gold_citations"],
                            rag_answer=config_result["answer"],
                            config_name=config_name,
                            conn=conn,
                        )
                    except Exception as e:
                        record = {
                            "query_id": gold_query["id"],
                            "config_name": config_name,
                            "error": str(e),
                        }
                        out_f.write(json.dumps(record) + "\n")
                        out_f.flush()
                        print(f"[{i}/{total_queries}] {gold_query['id']} | {config_name} | ERROR")
                        continue

                    bucket = judged["taxonomy_bucket"]

                    record = {
                        "query_id": gold_query["id"],
                        "question": gold_query["question"],
                        "gold_answer": gold_query["gold_answer"],
                        "gold_citations": gold_query["gold_citations"],
                        "config_name": config_name,
                        "rag_answer": config_result["answer"],
                        "taxonomy_bucket": bucket,
                        "fabrication_rate": judged["layer1"]["fabrication_rate"],
                        "layer2_judgment": judged["layer2"]["judgment"],
                        "layer2_confidence": judged["layer2"]["confidence"],
                        "layer2_reasoning": judged["layer2"]["reasoning"],
                        "retrieved_paragraph_ids": [
                            chunk["paragraph_id"] for chunk in config_result["retrieved_chunks"]
                        ],
                        "stratum": gold_query["stratum"],
                    }
                    out_f.write(json.dumps(record) + "\n")
                    out_f.flush()

                    print(f"[{i}/{total_queries}] {gold_query['id']} | {config_name} | {bucket}")
            finally:
                conn.close()

    summary = compute_summary()

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print()
    header = f"{'config':<15}{'total':>8}" + "".join(f"{b:>22}" for b in TAXONOMY_BUCKETS)
    print(header)
    for config_name in CONFIG_NAMES:
        row = f"{config_name:<15}{summary[config_name]['total']:>8}" + "".join(
            f"{summary[config_name][b]:>22}" for b in TAXONOMY_BUCKETS
        )
        print(row)


if __name__ == "__main__":
    run_benchmark()
