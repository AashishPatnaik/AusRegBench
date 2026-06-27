---
title: AusRegBench
emoji: ⚖️
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.45.0"
app_file: dashboard/app.py
pinned: false
---

# AusRegBench

**An open, reproducible benchmark measuring where RAG systems fail on Australian
financial-services and prudential regulation.**

## The Finding

Across 119 evaluated queries per configuration, the grounded / citation-forced
config answers faithfully 88.2% of the time versus 76.5% for the naive
baseline — a 56% reduction in obligation misstatements. But citation-forcing
doesn't eliminate the problem: it still misstates the obligation in 5.9% of
cases, primarily by truncating a qualifying clause rather than dropping the
citation outright. The provision is retrieved and cited correctly; the
obligation is what gets distorted. The failure lives in generation, not
retrieval.

## Live Dashboard

[https://ausregbench-sat4lz4vjbqekjya9dy6t7.streamlit.app](https://ausregbench-sat4lz4vjbqekjya9dy6t7.streamlit.app)

## What This Measures

Two failure modes:

- **Fabricated citations** — the provision cited doesn't exist.
- **Misstated obligations** — the provision cited is real and relevant, but
  the obligation is broadened, narrowed, or otherwise distorted.

Five RAG configurations are tested: naive (embed → top-k → generate), hybrid
(BM25 + dense + Reciprocal Rank Fusion), reranking (retrieve 20 →
cross-encoder → top 5), KG-augmented (entity/relationship graph over
provisions), and grounded/citation-forced (model must quote the provision
verbatim and refuse if unsupported).

## Results

| Config | Faithful % | Misstated % | Missing Citation % |
| --- | --- | --- | --- |
| naive | 76.5% | 13.4% | 6.7% |
| hybrid | 80.7% | 10.9% | 4.2% |
| rerank | 79.8% | 11.8% | 4.2% |
| kg_augmented | 76.5% | 11.8% | 6.7% |
| grounded | 88.2% | 5.9% | 4.2% |

## Corpus

- Corporations Act 2001 (Cth) — from the Open Australian Legal Corpus (CC BY
  4.0)
- Banking Act 1959 (Cth)
- APRA Prudential Standards CPS 220, CPS 230, CPS 234
- 11,613 clause-aware chunks with paragraph ID preservation

## Gold Set

120 hand-verified queries across 5 strata: obligation fidelity,
retrievability stress, distractor stress, cross-reference stress, and
adversarial. Every gold answer is verified by a human against the primary
legislative or prudential source text — the LLM never defines its own ground
truth.

## Judge Validation

A two-layer pipeline: a deterministic citation regex checks every citation
against the corpus index (Layer 1), and Claude Sonnet, used as an
independent LLM judge from a different model family than every generator
under test, judges entailment between the cited provision text and the
answer's claim (Layer 2). The judge is validated at Cohen's κ = 0.78 against
human labels (24/25 agreement on the hand-labeled sample).

## Prior Art

The Monash AusLaw Citation Benchmark (Han, Burgess & Shareghi) evaluates
case-law and legislation **citation prediction**, finding that standalone
generative models fail almost entirely and that BM25 beats dense retrieval —
a result this benchmark's hybrid config corroborates. AusRegBench differs in
scope: rather than predicting citations, it measures whether a *correctly
cited* provision is faithfully restated, and attributes each failure to a
pipeline stage.

The Deakin "Seven Failure Points" report (Barnett et al., 2024) is a
qualitative engineering experience report cataloguing RAG failure modes
across research, education, and biomedical domains. AusRegBench takes one of
those failure points — faithfulness — and turns it into a reproducible
quantitative benchmark for a single high-stakes domain, with a human-verified
gold set and a validated judge.

## Reproduce

```
pip install -r requirements.txt
python scripts/pull_corpus.py
python scripts/pull_apra.py
python src/embed.py
python scripts/run_benchmark.py
streamlit run dashboard/app.py
```

## Disclaimer

Not legal or financial advice. This is a measurement artifact only.
