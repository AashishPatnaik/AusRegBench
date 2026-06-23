"""
Streamlit dashboard for AusRegBench benchmark results.

Reads results/raw_results.jsonl (per (query, config) judged outcomes).
All percentages shown are computed live from that file, never hardcoded,
so the dashboard stays correct if the benchmark is re-run.
"""

import html
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RAW_RESULTS_PATH = RESULTS_DIR / "raw_results.jsonl"

GITHUB_URL = "https://github.com/AashishPatnaik/AusRegBench"

CONFIG_ORDER = ["naive", "hybrid", "rerank", "kg_augmented", "grounded"]
CONFIG_LABELS = {
    "naive": "Naive",
    "hybrid": "Hybrid",
    "rerank": "Rerank",
    "kg_augmented": "KG-Augmented",
    "grounded": "Grounded",
}

BG = "#0A0E1A"
CARD_BG = "#131929"
BORDER = "#1E2D4A"
ACCENT = "#00C2FF"
SUCCESS = "#00D68F"
DANGER = "#FF4B4B"
WARNING = "#F5A623"
TEXT_PRIMARY = "#F0F4FF"
TEXT_MUTED = "#8B9BB4"

CONFIG_COLORS = {
    "naive": DANGER,
    "hybrid": WARNING,
    "rerank": WARNING,
    "kg_augmented": ACCENT,
    "grounded": SUCCESS,
}
TAXONOMY_BUCKETS = [
    "correct_and_faithful",
    "misstated_obligation",
    "missing_citation",
    "real_but_irrelevant",
    "fabricated_citation",
]
TAXONOMY_LABELS = {
    "correct_and_faithful": "Correct & faithful",
    "misstated_obligation": "Misstated obligation",
    "missing_citation": "Missing citation",
    "real_but_irrelevant": "Real but irrelevant",
    "fabricated_citation": "Fabricated citation",
}
TAXONOMY_COLORS = {
    "correct_and_faithful": SUCCESS,
    "misstated_obligation": WARNING,
    "missing_citation": TEXT_MUTED,
    "real_but_irrelevant": ACCENT,
    "fabricated_citation": DANGER,
}

st.set_page_config(page_title="AusRegBench", layout="wide")


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {BG};
            color: {TEXT_PRIMARY};
        }}
        html, body, [class*="css"] {{
            font-size: 16px;
        }}
        #MainMenu, header, footer {{ visibility: hidden; }}

        .hero-title {{
            font-size: 3.4rem;
            font-weight: 800;
            color: {TEXT_PRIMARY};
            letter-spacing: -0.02em;
            margin-bottom: 0.1rem;
        }}
        .hero-subhead {{
            font-size: 1.3rem;
            color: {TEXT_MUTED};
            margin-bottom: 1.8rem;
        }}
        .hero-sentence {{
            font-size: 1.15rem;
            color: {TEXT_PRIMARY};
            margin-top: 1.2rem;
            line-height: 1.6;
        }}

        .section-title {{
            font-size: 1.7rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-top: 2.2rem;
            margin-bottom: 0.3rem;
        }}
        .section-subtitle {{
            font-size: 1.05rem;
            color: {TEXT_MUTED};
            margin-bottom: 1.2rem;
        }}

        .metric-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.4rem 1.2rem;
            text-align: center;
            height: 100%;
        }}
        .metric-value {{
            font-size: 2.6rem;
            font-weight: 800;
            line-height: 1.1;
        }}
        .metric-label {{
            font-size: 1rem;
            color: {TEXT_MUTED};
            margin-top: 0.5rem;
        }}

        .config-card {{
            background-color: {CARD_BG};
            border: 2px solid {BORDER};
            border-radius: 12px;
            padding: 1.2rem 1rem;
            height: 100%;
        }}
        .config-card-name {{
            font-size: 1.2rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-bottom: 0.8rem;
        }}
        .config-stat-row {{
            display: flex;
            justify-content: space-between;
            font-size: 1rem;
            margin-bottom: 0.35rem;
            color: {TEXT_PRIMARY};
        }}
        .config-stat-label {{
            color: {TEXT_MUTED};
        }}

        .badge-red {{
            display: inline-block;
            background-color: rgba(255, 75, 75, 0.15);
            color: {DANGER};
            border: 1px solid {DANGER};
            border-radius: 6px;
            padding: 0.2rem 0.7rem;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            margin-bottom: 0.8rem;
        }}
        .example-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.4rem;
            margin-bottom: 1.4rem;
        }}
        .example-question {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin: 0.6rem 0 1rem 0;
        }}
        .example-flex {{
            display: flex;
            gap: 1.2rem;
        }}
        .example-box {{
            flex: 1;
            border-radius: 8px;
            padding: 1rem;
            background-color: {BG};
            font-size: 0.95rem;
            color: {TEXT_PRIMARY};
            line-height: 1.5;
        }}
        .example-box-rag {{
            border-left: 3px solid {DANGER};
        }}
        .example-box-reasoning {{
            border-left: 3px solid {ACCENT};
        }}
        .example-box-title {{
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            color: {TEXT_MUTED};
            margin-bottom: 0.5rem;
        }}

        .stat-list {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.4rem;
            height: 100%;
        }}
        .stat-list-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: {ACCENT};
            margin-bottom: 0.8rem;
        }}
        .stat-list-item {{
            font-size: 1rem;
            color: {TEXT_PRIMARY};
            margin-bottom: 0.5rem;
        }}
        .stat-list-item b {{
            color: {TEXT_PRIMARY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_raw_results() -> pd.DataFrame:
    records = []
    with open(RAW_RESULTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if "taxonomy_bucket" in record:
                records.append(record)
    return pd.DataFrame(records)


def build_metrics_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for config_name in CONFIG_ORDER:
        config_df = df[df["config_name"] == config_name]
        total = len(config_df)
        bucket_counts = config_df["taxonomy_bucket"].value_counts()

        def pct(bucket: str) -> float:
            return round(100 * bucket_counts.get(bucket, 0) / total, 1) if total else 0.0

        rows.append(
            {
                "config_name": config_name,
                "total": total,
                "faithful_pct": pct("correct_and_faithful"),
                "misstated_pct": pct("misstated_obligation"),
                "missing_pct": pct("missing_citation"),
                "fabricated_pct": pct("fabricated_citation"),
            }
        )
    return pd.DataFrame(rows)


def metric_card(value: str, label: str, color: str) -> str:
    return (
        f'<div class="metric-card">'
        f'<div class="metric-value" style="color:{color};">{html.escape(value)}</div>'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f"</div>"
    )


def config_card(row: pd.Series) -> str:
    border_color = (
        SUCCESS if row["config_name"] == "grounded"
        else DANGER if row["config_name"] == "naive"
        else BORDER
    )
    name = CONFIG_LABELS[row["config_name"]]
    return (
        f'<div class="config-card" style="border-color:{border_color};">'
        f'<div class="config-card-name">{html.escape(name)}</div>'
        f'<div class="config-stat-row"><span class="config-stat-label">Faithful</span>'
        f'<b style="color:{SUCCESS};">{row["faithful_pct"]}%</b></div>'
        f'<div class="config-stat-row"><span class="config-stat-label">Misstated</span>'
        f'<b style="color:{WARNING};">{row["misstated_pct"]}%</b></div>'
        f'<div class="config-stat-row"><span class="config-stat-label">Missing citation</span>'
        f'<b style="color:{TEXT_MUTED};">{row["missing_pct"]}%</b></div>'
        f"</div>"
    )


def example_card(row: pd.Series) -> str:
    rag_answer = html.escape(row["rag_answer"][:400]).replace("\n", "<br>")
    reasoning = html.escape(row["layer2_reasoning"])
    question = html.escape(row["question"])
    return (
        f'<div class="example-card">'
        f'<span class="badge-red">MISSTATED OBLIGATION</span>'
        f'<div class="example-question">{question}</div>'
        f'<div class="example-flex">'
        f'<div class="example-box example-box-rag">'
        f'<div class="example-box-title">RAG ANSWER</div>{rag_answer}</div>'
        f'<div class="example-box example-box-reasoning">'
        f'<div class="example-box-title">JUDGE REASONING</div>{reasoning}</div>'
        f"</div></div>"
    )


inject_css()

raw_df = load_raw_results()
metrics_df = build_metrics_table(raw_df)

grounded = metrics_df[metrics_df["config_name"] == "grounded"].iloc[0]
naive = metrics_df[metrics_df["config_name"] == "naive"].iloc[0]
reduction_pct = (
    round(100 * (naive["misstated_pct"] - grounded["misstated_pct"]) / naive["misstated_pct"])
    if naive["misstated_pct"]
    else 0
)

# --- Hero ---

st.markdown('<div class="hero-title">AusRegBench</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subhead">RAG Faithfulness Benchmark for Australian Financial Regulation</div>',
    unsafe_allow_html=True,
)

hero_cols = st.columns(3)
with hero_cols[0]:
    st.markdown(
        metric_card(f'{grounded["faithful_pct"]}%', "Grounded config faithful rate", SUCCESS),
        unsafe_allow_html=True,
    )
with hero_cols[1]:
    st.markdown(
        metric_card(f'{naive["faithful_pct"]}%', "Naive baseline faithful rate", DANGER),
        unsafe_allow_html=True,
    )
with hero_cols[2]:
    st.markdown(
        metric_card(f"{reduction_pct}%", "Reduction in misstatements", ACCENT),
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="hero-sentence">Citation-forcing cuts obligation misstatements by '
    f'{reduction_pct}% — but still misstates in {grounded["misstated_pct"]}% of cases, '
    f"primarily through obligation truncation.</div>",
    unsafe_allow_html=True,
)

# --- Section 1: results by configuration ---

st.markdown('<div class="section-title">Results by Configuration</div>', unsafe_allow_html=True)

config_cols = st.columns(5)
for col, (_, row) in zip(config_cols, metrics_df.iterrows()):
    with col:
        st.markdown(config_card(row), unsafe_allow_html=True)

# --- Section 2: key finding chart ---

st.markdown(
    '<div class="section-title">Faithful answers by RAG configuration (n=119 per config)</div>',
    unsafe_allow_html=True,
)

faithful_fig = px.bar(
    metrics_df,
    x="faithful_pct",
    y="config_name",
    orientation="h",
    color="config_name",
    color_discrete_map=CONFIG_COLORS,
    category_orders={"config_name": CONFIG_ORDER},
)
faithful_fig.update_traces(
    texttemplate="%{x:.1f}%", textposition="outside"
)
faithful_fig.update_yaxes(
    title="",
    ticktext=[CONFIG_LABELS[c] for c in CONFIG_ORDER],
    tickvals=CONFIG_ORDER,
)
faithful_fig.update_xaxes(title="Faithful %", range=[0, 100])
faithful_fig.add_vline(
    x=grounded["faithful_pct"],
    line_dash="dash",
    line_color=SUCCESS,
    annotation_text=f'Grounded: {grounded["faithful_pct"]}%',
    annotation_position="bottom right",
    annotation_font_color=SUCCESS,
)
faithful_fig.update_layout(
    template="plotly_dark",
    plot_bgcolor=CARD_BG,
    paper_bgcolor=BG,
    font_color=TEXT_PRIMARY,
    showlegend=False,
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(faithful_fig, use_container_width=True)

# --- Section 3: failure breakdown ---

st.markdown(
    '<div class="section-title">Failure taxonomy across configurations</div>',
    unsafe_allow_html=True,
)

bucket_counts_df = (
    raw_df.groupby(["config_name", "taxonomy_bucket"]).size().reset_index(name="count")
)
bucket_counts_df["taxonomy_label"] = bucket_counts_df["taxonomy_bucket"].map(TAXONOMY_LABELS)

taxonomy_fig = px.bar(
    bucket_counts_df,
    x="config_name",
    y="count",
    color="taxonomy_bucket",
    barmode="stack",
    color_discrete_map=TAXONOMY_COLORS,
    category_orders={"config_name": CONFIG_ORDER, "taxonomy_bucket": TAXONOMY_BUCKETS},
)
for trace in taxonomy_fig.data:
    bucket_key = trace.name
    trace.name = TAXONOMY_LABELS.get(bucket_key, bucket_key)
taxonomy_fig.update_xaxes(
    title="",
    ticktext=[CONFIG_LABELS[c] for c in CONFIG_ORDER],
    tickvals=CONFIG_ORDER,
)
taxonomy_fig.update_yaxes(title="Queries")
taxonomy_fig.update_layout(
    template="plotly_dark",
    plot_bgcolor=CARD_BG,
    paper_bgcolor=BG,
    font_color=TEXT_PRIMARY,
    legend_title_text="",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(taxonomy_fig, use_container_width=True)

# --- Section 4: example failures ---

st.markdown(
    '<div class="section-title">How obligation misstatements happen</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">Three real examples from the naive config — '
    "same provision, different ways RAG gets it wrong</div>",
    unsafe_allow_html=True,
)

misstated_naive = raw_df[
    (raw_df["config_name"] == "naive") & (raw_df["taxonomy_bucket"] == "misstated_obligation")
].head(3)

for _, row in misstated_naive.iterrows():
    st.markdown(example_card(row), unsafe_allow_html=True)

# --- Section 5: corpus & methodology ---

st.markdown(
    '<div class="section-title">Corpus & Methodology</div>', unsafe_allow_html=True
)

method_cols = st.columns(2)
with method_cols[0]:
    st.markdown(
        f"""
        <div class="stat-list">
            <div class="stat-list-title">Corpus</div>
            <div class="stat-list-item"><b>5</b> sources — Corporations Act 2001,
                Banking Act 1959, CPS 220, CPS 230, CPS 234</div>
            <div class="stat-list-item"><b>11,613</b> clause-aware chunks, paragraph
                IDs preserved</div>
            <div class="stat-list-item"><b>120</b> hand-verified gold queries</div>
            <div class="stat-list-item"><b>5</b> stress strata</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with method_cols[1]:
    st.markdown(
        f"""
        <div class="stat-list">
            <div class="stat-list-title">Judge Validation</div>
            <div class="stat-list-item">Cohen's <b>κ = 0.78</b> vs. human labels</div>
            <div class="stat-list-item"><b>24/25</b> agreement on hand-labeled sample</div>
            <div class="stat-list-item">Two-layer pipeline: deterministic citation
                check + LLM entailment judge</div>
            <div class="stat-list-item">Judge model differs from every generator
                model under test</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.link_button("View source on GitHub", GITHUB_URL)
