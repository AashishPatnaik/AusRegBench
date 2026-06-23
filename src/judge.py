"""
Two-layer ground-truth pipeline for AusRegBench.

Layer 1 (deterministic): regex-parses citations out of a RAG answer and
checks each one against corpus_chunks. Zero judgment involved — this is
what makes the fabrication rate publishable on its own.

Layer 2 (entailment): asks a Claude judge whether the gold provision text
entails the RAG answer's claim. Validated separately via Cohen's kappa
against human labels (see compute_cohen_kappa).

Layer 3 composes both into a single taxonomy bucket per (query, config).
"""

import json
import os
import re
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from langsmith import traceable
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import get_connection

load_dotenv()

JUDGE_MODEL = "claude-sonnet-4-6"

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# --- Layer 1: citation patterns -------------------------------------------

CORPORATIONS_ACT_CITATION = re.compile(r"\[corporations_act_2001\s*\|\s*([\w()]+)\]")
BANKING_ACT_CITATION = re.compile(r"\[banking_act_1959\s*\|\s*([\w()]+)\]")
CPS_CITATION = re.compile(r"\[cps(\d+)\s*\|\s*([\w()]+)\]")


def _exists_in_corpus(cur, cite_source: str, paragraph_id: str) -> bool:
    """Check exact match, then fall back by stripping trailing (x) groups."""
    candidates = [paragraph_id]
    # strip trailing parentheticals one at a time: 912A(1)(a) -> 912A(1) -> 912A
    p = paragraph_id
    while re.search(r"\([^()]+\)$", p):
        p = re.sub(r"\([^()]+\)$", "", p)
        candidates.append(p)
    for candidate in candidates:
        cur.execute(
            "SELECT COUNT(*) FROM corpus_chunks WHERE source = %s AND paragraph_id = %s",
            (cite_source, candidate),
        )
        if cur.fetchone()[0] > 0:
            return True
    return False


@traceable(name="check_citations_deterministic")
def check_citations_deterministic(answer: str, source: str, conn) -> dict:
    """
    Parse every citation in the answer text and check whether it exists
    in corpus_chunks.
    """
    citations_found = []

    for match in CORPORATIONS_ACT_CITATION.finditer(answer):
        citations_found.append(("corporations_act_2001", match.group(1)))

    for match in BANKING_ACT_CITATION.finditer(answer):
        citations_found.append(("banking_act_1959", match.group(1)))

    for match in CPS_CITATION.finditer(answer):
        citations_found.append((f"cps{match.group(1)}", match.group(2)))

    fabricated = []
    real = []

    with conn.cursor() as cur:
        for cite_source, paragraph_id in citations_found:
            citation_str = f"[{cite_source} | {paragraph_id}]"
            exists = _exists_in_corpus(cur, cite_source, paragraph_id)
            (real if exists else fabricated).append(citation_str)

    total = len(citations_found)

    return {
        "citations_found": [f"[{s} | {p}]" for s, p in citations_found],
        "fabricated": fabricated,
        "real": real,
        "fabrication_rate": len(fabricated) / total if total else 0.0,
    }


# --- Layer 2: LLM entailment judge -----------------------------------------

JUDGE_SYSTEM_PROMPT = """You are a precise legal entailment judge for Australian financial regulation. \
You will be given a provision text and a claim made about it. \
Judge whether the provision text entails the claim.

Respond in JSON only with these exact keys:
{
  "judgment": "ENTAILS" | "CONTRADICTS" | "INSUFFICIENT",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "reasoning": "one sentence explanation"
}

Rules:
- ENTAILS: the provision text directly supports the claim with no distortion
- CONTRADICTS: the claim misstates, broadens, narrows, or distorts the provision
- INSUFFICIENT: the provision text does not contain enough information to judge
- Be strict: a missing qualifying tail (e.g. 'as part of the financial services \
business') that changes legal scope = CONTRADICTS, not ENTAILS
- Never use external knowledge — judge only from the provided provision text"""


def _strip_markdown_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


@traceable(name="judge_entailment", run_type="llm")
def judge_entailment(
    provision_text: str,
    claim: str,
    paragraph_id: str,
    source: str,
) -> dict:
    """
    Ask Claude whether provision_text entails the claim.
    """
    user_prompt = (
        f"PROVISION TEXT:\n{provision_text}\n\n"
        f"CLAIM:\n{claim}\n\n"
        f"Paragraph ID: {paragraph_id}\n"
        f"Source: {source}"
    )

    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=300,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_response = response.content[0].text
    parsed = json.loads(_strip_markdown_fence(raw_response))

    return {
        "judgment": parsed["judgment"],
        "confidence": parsed["confidence"],
        "reasoning": parsed["reasoning"],
        "raw_response": raw_response,
    }


# --- Layer 3: full query evaluation -----------------------------------------

@traceable(name="evaluate_answer")
def evaluate_answer(
    query_id: str,
    question: str,
    gold_answer: str,
    gold_citations: list[str],
    rag_answer: str,
    config_name: str,
    conn,
) -> dict:
    """
    Run both layers on one (query, config) pair.
    """
    layer1 = check_citations_deterministic(rag_answer, source=config_name, conn=conn)

    gold_source, gold_paragraph_id = (
        part.strip() for part in gold_citations[0].split("|", 1)
    )

    with conn.cursor() as cur:
        cur.execute(
            "SELECT text FROM corpus_chunks WHERE source = %s AND paragraph_id = %s",
            (gold_source, gold_paragraph_id),
        )
        row = cur.fetchone()

    if row is None:
        raise ValueError(
            f"Gold citation '{gold_citations[0]}' for {query_id} not found in corpus_chunks"
        )

    provision_text = row[0]

    layer2 = judge_entailment(
        provision_text=provision_text,
        claim=rag_answer,
        paragraph_id=gold_paragraph_id,
        source=gold_source,
    )

    if layer1["fabricated"]:
        taxonomy_bucket = "fabricated_citation"
    elif not layer1["citations_found"]:
        taxonomy_bucket = "missing_citation"
    elif layer2["judgment"] == "ENTAILS":
        taxonomy_bucket = "correct_and_faithful"
    elif layer2["judgment"] == "CONTRADICTS":
        taxonomy_bucket = "misstated_obligation"
    else:
        taxonomy_bucket = "real_but_irrelevant"

    return {
        "query_id": query_id,
        "config_name": config_name,
        "question": question,
        "layer1": layer1,
        "layer2": layer2,
        "taxonomy_bucket": taxonomy_bucket,
    }


# --- Kappa validation --------------------------------------------------------

def compute_cohen_kappa(human_labels: list[str], judge_labels: list[str]) -> float:
    """
    Compute Cohen's kappa between human labels and judge labels.
    """
    return float(cohen_kappa_score(human_labels, judge_labels))


if __name__ == "__main__":
    from eval import evaluate_query

    gold_path = Path(__file__).resolve().parent.parent / "queries" / "gold_set.jsonl"
    with open(gold_path) as f:
        gold_query = json.loads(f.readline())

    evaluation = evaluate_query(gold_query["question"])
    naive_result = evaluation["results"]["naive"]

    if "error" in naive_result:
        print(f"naive config failed: {naive_result['error']}")
    else:
        conn = get_connection()
        try:
            result = evaluate_answer(
                query_id=gold_query["id"],
                question=gold_query["question"],
                gold_answer=gold_query["gold_answer"],
                gold_citations=gold_query["gold_citations"],
                rag_answer=naive_result["answer"],
                config_name="naive",
                conn=conn,
            )
        finally:
            conn.close()

        print(f"Taxonomy bucket: {result['taxonomy_bucket']}")
        print(f"\nLayer 1 (deterministic): {result['layer1']}")
        print(f"\nLayer 2 judgment: {result['layer2']['judgment']} ({result['layer2']['confidence']})")
        print(f"Layer 2 reasoning: {result['layer2']['reasoning']}")

    kappa = compute_cohen_kappa(
        ["ENTAILS", "CONTRADICTS", "INSUFFICIENT", "ENTAILS", "CONTRADICTS"],
        ["ENTAILS", "CONTRADICTS", "INSUFFICIENT", "CONTRADICTS", "CONTRADICTS"],
    )
    print(f"\nKappa smoke test (expected ~0.55): {kappa:.4f}")
