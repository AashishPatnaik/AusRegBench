# CLAUDE.md — AusRegBench

> This file is read by Claude Code at the start of every session.
> It is the source of truth for scope and rules. If a request conflicts with
> this file, **stop and ask the human** before proceeding.

## What this project is

**AusRegBench** is an open, reproducible **benchmark + diagnostic tool** that measures
where RAG systems get **Australian financial-services and prudential law** wrong —
specifically how often they (a) cite provisions that don't exist, and (b) cite real
provisions but misstate the obligation — and pinpoints **which pipeline stage**
(retrieve / augment / generate) caused each failure.

It is a **measurement instrument**, not a product. Its entire value is that its
ground truth is trustworthy. Treat it that way in every decision.

## Frozen scope — DO NOT EXPAND

- **One domain:** Australian financial-services & prudential regulation. No other verticals.
- **Five configs** (the only configs — no sixth): naive, hybrid, rerank, KG-augmented, grounded/citation-forced.
- **One finding:** a faithfulness/stage-attribution result, e.g. "the provision was retrieved but the obligation was misstated, so the failure lives in generation, not retrieval."

The temptation to add a vertical, a sixth config, MCP, multi-agent orchestration, or
cloud deployment **mid-build** is the single biggest risk to this project shipping.
All of those are **post-ship extensions only**, added one at a time, and only if they
sharpen the finding. **If a session would add any of them, STOP and ask the human.**

## The two human-verification non-negotiables

1. **The gold set is human-verified.** The LLM may do the heavy lifting — surface the
   relevant provision, summarise it, draft a candidate obligation, propose the citation.
   But a human verifies every gold item against the actual provision text. The LLM is
   never the source of truth for what the law says. (This is the whole point: we are
   testing LLMs, so an LLM cannot define the correct answers — that's circular.)
2. **The headline numbers are human-verified.** Fabrication rate, misstatement rate,
   Cohen's κ, stage-attribution — the human reads the code that produces these and
   spot-checks the outputs. These numbers are the findings; they cannot be vibe-checked.

## The 90/10 coding rule

- **Vibe-code the ~90% where a bug looks wrong** (Streamlit dashboard, config plumbing,
  DeepEval wiring, run scripts). Go fast, hands-off.
- **Human-verify the ~10% where a bug looks correct.** Specifically:
  - **Clause-aware chunking that preserves paragraph IDs.** A misaligned ID silently
    corrupts every downstream citation check. Spot-check chunks against the source by eye.
  - **The deterministic citation-checker (regex).** A parsing edge-case bug prints a
    clean, wrong number.
  - **The κ computation.** Verify label arrays are aligned before trusting the value.

## Locked stack

- **Language:** Python 3.11. Pin dependencies (lockfile). Set seeds for reproducibility.
- **Orchestration:** LangChain (pipelines) + LangGraph (the agentic / KG-augmented config).
- **Vector DB:** **Neon** (managed serverless Postgres) + **pgvector**. No local Docker.
- **Embeddings:** default `text-embedding-3-large` (OpenAI); plus **BGE-large** (open) for
  the "embedding choice changes results" comparison.
- **Retrieval:** BM25 (Postgres FTS or `rank_bm25`) + dense; combine with Reciprocal Rank Fusion.
- **Reranker:** a cross-encoder (e.g. `bge-reranker`) or Cohere Rerank.
- **Generation models (systems under test) — pick current versions at build time:**
  - Frontier closed: GPT-5.x (OpenAI API)
  - Strong open-weight, via API (not local): DeepSeek V4 (DeepSeek API or OpenRouter)
  - Cheap/small tier: a budget model, to establish the cost floor
- **Judge:** **Claude (Anthropic API)** — a different family from every generator, to avoid
  self-preference bias. Never use the same model to generate and to judge.
- **Eval metrics:** DeepEval (faithfulness, answer relevancy, contextual recall).
- **Tracing:** LangSmith — span-level retrieve→augment→generate, for stage-attribution.
- **Dashboard:** Streamlit, deployed on Streamlit Community Cloud or Hugging Face Spaces
  (NOT AWS — over-engineering for a static benchmark; cloud/MLOps skills live in coursework).

> Note: Claude Pro funds Claude Code + chat only. All pipeline model calls (OpenAI,
> Anthropic judge, DeepSeek) bill separately on API credits. Use prompt caching and
> batch endpoints to control cost and rate limits.

## The five configs

1. **Naive** — embed → top-k → generate. Baseline.
2. **Hybrid** — BM25 + dense + RRF. Hypothesis: lexical matching helps on exact citation tokens.
3. **Rerank** — retrieve 20 → cross-encoder → top 5. Hypothesis: higher precision cuts wrong-provision errors.
4. **KG-augmented** — entity/relationship graph over provisions (the differentiator).
   Hypothesis: helps where obligations cross-reference each other.
5. **Grounded / citation-forced** — model must quote the provision verbatim + cite the
   paragraph ID, and refuse if unsupported. Hypothesis: cuts fabrication/misstatement most.

## Failure taxonomy (exactly one bucket per (query, config))

1. **Fabricated citation** — provision doesn't exist. (Caught deterministically by regex.)
2. **Real-but-irrelevant** — provision exists but doesn't support the claim.
3. **Correct citation / misstated obligation** — exists and relevant, but the obligation is
   wrong or distorted. ← the wedge.
4. **Missing citation** — answer needed authority and gave none.
5. **Correct & faithful** — the pass bucket.

## Ground-truth pipeline (two layers)

- **Layer 1 — deterministic.** Regex-parse every citation; check against the corpus citation
  index. Catches bucket 1 with zero judgment. Fabrication rate is publishable on its own.
- **Layer 2 — entailment, validated.** LLM judge sees the *actual retrieved provision text*
  + the model's claim; decides entailment (buckets 2 & 3). **Validate the judge:** hand-label
  ≥100 items, run the judge on the same 100, report **Cohen's κ** + accuracy. Judge model
  must differ from the generator. This validation is the biggest credibility differentiator.

## Gold set design (quality over count — aim 80–120)

- Stratify by the failure mode each query targets: retrievability stress, distractor stress,
  obligation-fidelity stress (the largest stratum), cross-reference stress.
- Per query, record: question, gold answer, gold citation(s) with paragraph IDs, the supported
  proposition, the stratum, and a one-line rationale.
- **Anti-leakage:** NEVER put the gold answer or gold citation text into any prompt.
- Favour concrete obligations ("an APRA-regulated entity must…") over vague principles.

## Data

- **Statutory:** Open Australian Legal Corpus (`isaacus/open-australian-legal-corpus`, HF).
  Pull subset: Corporations Act 2001 (Cth), Banking Act 1959 (Cth), relevant regulations.
- **Regulator instruments:** APRA Prudential Standards (start CPS 220, CPS 230, CPS 234);
  a coherent handful of ASIC Regulatory Guides.
- **Keep clause/paragraph IDs as metadata on every chunk.** Most important ingestion decision.
- Attribute OALC (CC BY 4.0). Note provenance/licensing — it's on-theme for a compliance project.

## Repo structure

```
ausregbench/
  data/            # ingested corpus + provenance notes
  src/
    ingest.py      # clause-aware chunking, keeps paragraph IDs
    retrieval.py   # bm25, dense, hybrid (RRF), rerank
    configs/       # the 5 RAG configs
    eval.py        # taxonomy scoring + DeepEval metrics
    judge.py       # LLM-judge + kappa validation
  queries/         # gold set as versioned .jsonl
  results/         # raw runs + summary tables
  dashboard/       # Streamlit app
  README.md        # what/why/how + headline result + how to reproduce
  methodology.md   # taxonomy, judge protocol, kappa, limitations
  LICENSE
```

## Build phases

1. **Skeleton:** Neon + pgvector, OALC ingest + clause-aware chunking (IDs preserved),
   naive config end-to-end on ~10 queries.
2. **Breadth:** the other 4 configs + eval harness + LangSmith tracing.
3. **Ground truth:** full 80–120 gold set + two-layer judge + **validate the judge (κ)**.
4. **Ship:** run everything, build the Streamlit dashboard, write the report.
5. **(Optional, post-ship):** MCP wrapper, additional model, etc. — one at a time, only if it sharpens the finding.

## Prior art to engage (cite correctly)

- **Monash AusLaw Citation Benchmark** (Han, Burgess & Shareghi) — case-law/legislation
  **citation prediction**; found standalone generative models fail almost entirely and BM25
  beats dense retrieval. Cite as corroboration for the hybrid config AND as the "how is this
  different" contrast (they predict citations; we measure obligation faithfulness + stage).
- **Deakin "Seven Failure Points"** (Barnett et al., 2024, arXiv 2401.05856) — an engineering
  **experience report** of RAG failure points across research/education/biomedical. NOT
  case-law citation prediction. Contrast: they catalogued failures qualitatively; we built a
  reproducible quantitative benchmark for one high-stakes domain.

## When to STOP and ask the human

- Any request to add a vertical, a 6th config, MCP, multi-agent orchestration, or AWS/cloud deploy.
- Any change to chunking logic or how paragraph IDs are tracked.
- Anything that touches the gold set's correctness.
- Using the same model as both generator and judge.
- Putting gold answers/citations into a prompt (leakage).

## Done means done

When the report is written, the repo is clean, the dashboard runs, and the LinkedIn post is
drafted — **stop.** Resist infinite polishing. Shipped at 90% beats perfect-and-abandoned.
