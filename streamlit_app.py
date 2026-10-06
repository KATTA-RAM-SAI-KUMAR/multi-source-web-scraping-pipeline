import csv
import json
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "output" / "final_dataset.csv"
SUMMARY_PATH = BASE_DIR / "output" / "summary_report.json"

st.set_page_config(
    page_title="Scraping Pipeline | Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* ---------- App shell ---------- */
    .stApp {
        background: #0b1020;
        color: #e7ecf7;
    }
    [data-testid="stHeader"] {
        background: rgba(11,16,32,0.92);
    }
    [data-testid="stSidebar"] {
        background: #080d1a;
        border-right: 1px solid #202b43;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1; }
    .block-container {
        max-width: 1380px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* ---------- Typography ---------- */
    h1, h2, h3 { color: #f8fafc !important; }
    p, label, .stCaption { color: #94a3b8 !important; }
    code {
        background: #111a2e !important;
        color: #7dd3fc !important;
        border: 1px solid #263653;
    }

    /* ---------- Hero ---------- */
    .hero {
        padding: 1.8rem 2rem;
        border: 1px solid #263653;
        border-radius: 18px;
        background: linear-gradient(135deg, #111a30 0%, #0d1629 55%, #101b34 100%);
        box-shadow: 0 18px 45px rgba(0,0,0,.28);
        margin-bottom: 1.25rem;
    }
    .eyebrow {
        color: #67e8f9;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }
    .hero-title {
        color: #f8fafc;
        font-size: 2.15rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
    }
    .hero-subtitle {
        color: #94a3b8;
        margin: .7rem 0 0;
        font-size: 1rem;
    }

    /* ---------- Cards ---------- */
    div[data-testid="stMetric"] {
        background: #111a2e;
        border: 1px solid #263653;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 28px rgba(0,0,0,.16);
    }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    div[data-testid="stMetricValue"] { color: #f8fafc !important; }

    .section-card {
        background: #0f172a;
        border: 1px solid #202d47;
        border-radius: 16px;
        padding: 1.15rem 1.25rem;
        margin: .7rem 0 1rem;
    }
    .section-label {
        color: #67e8f9;
        font-size: .74rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }
    .section-title {
        color: #f8fafc;
        font-size: 1.25rem;
        font-weight: 750;
        margin-bottom: .8rem;
    }

    /* ---------- Pipeline ---------- */
    .pipeline {
        display: flex;
        gap: .55rem;
        align-items: center;
        flex-wrap: wrap;
        margin-top: .8rem;
    }
    .step {
        background: #111a2e;
        border: 1px solid #2b3b5c;
        border-radius: 999px;
        padding: .45rem .8rem;
        color: #dbeafe;
        font-size: .82rem;
        font-weight: 650;
    }
    .arrow { color: #64748b; font-weight: 700; }

    /* ---------- Buttons ---------- */
    .stButton > button[kind="primary"] {
        border: 1px solid #22d3ee;
        background: linear-gradient(135deg, #0891b2, #2563eb);
        color: white;
        font-weight: 750;
        border-radius: 10px;
        padding: .55rem 1.15rem;
        box-shadow: 0 8px 22px rgba(8,145,178,.22);
    }
    .stButton > button[kind="primary"]:hover {
        border-color: #67e8f9;
        background: linear-gradient(135deg, #0e7490, #1d4ed8);
    }
    .stDownloadButton > button {
        background: #111a2e;
        color: #e2e8f0;
        border: 1px solid #334766;
        border-radius: 10px;
    }

    /* ---------- Dataframe ---------- */
    [data-testid="stDataFrame"] {
        border: 1px solid #263653;
        border-radius: 12px;
        overflow: hidden;
    }

    /* ---------- Status ---------- */
    .status {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        background: #0d211e;
        border: 1px solid #155e57;
        color: #86efac;
        border-radius: 999px;
        padding: .38rem .75rem;
        font-size: .78rem;
        font-weight: 700;
    }
    .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #34d399;
        display: inline-block;
    }

    /* ---------- Sidebar ---------- */
    .side-title { color:#f8fafc; font-weight:800; font-size:1rem; }
    .side-note { color:#64748b; font-size:.78rem; line-height:1.55; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_summary():
    if not SUMMARY_PATH.exists():
        return {}
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


def load_rows():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


summary = load_summary()
rows = load_rows()

books = summary.get("collected_per_source", {}).get("Books to Scrape", 0)
quotes = summary.get("collected_per_source", {}).get("Quotes to Scrape", 0)
duplicates = summary.get("duplicates_detected", 0)
final_count = summary.get("final_record_count", len(rows))

# Sidebar
with st.sidebar:
    st.markdown('<div class="side-title">Scraper Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-note">A lightweight presentation layer for the Python scraping pipeline.</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Sources**")
    st.caption("• Books to Scrape")
    st.caption("• Quotes to Scrape")
    st.markdown("**Pipeline**")
    st.caption("Scrape → Clean → Validate → Deduplicate → Consolidate")
    st.divider()
    st.caption("CLI: `python main.py`")
    st.caption("Tests: `pytest -q`")

# Hero
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Python Data Engineering Assignment</div>
        <div class="hero-title">Multi-Source Web Scraping & Data Consolidation</div>
        <div class="hero-subtitle">Reliable scraping, cleaning, validation and deduplication across two public practice sources.</div>
        <div class="pipeline">
            <span class="step">Scrape</span><span class="arrow">→</span>
            <span class="step">Clean</span><span class="arrow">→</span>
            <span class="step">Validate</span><span class="arrow">→</span>
            <span class="step">Deduplicate</span><span class="arrow">→</span>
            <span class="step">Consolidate</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

run_col, status_col = st.columns([1, 4])
with run_col:
    run_clicked = st.button("Run scraper", type="primary", use_container_width=True)
with status_col:
    if summary:
        st.markdown('<div class="status"><span class="dot"></span>Latest run available</div>', unsafe_allow_html=True)
    else:
        st.caption("No generated output found yet. Run the scraper to build the dataset.")

if run_clicked:
    with st.spinner("Scraping both sources and rebuilding the dataset..."):
        from main import run
        run()
    summary = load_summary()
    rows = load_rows()
    books = summary.get("collected_per_source", {}).get("Books to Scrape", 0)
    quotes = summary.get("collected_per_source", {}).get("Quotes to Scrape", 0)
    duplicates = summary.get("duplicates_detected", 0)
    final_count = summary.get("final_record_count", len(rows))
    st.success("Scraper completed successfully.")
    st.rerun()

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Books collected", f"{books:,}")
m2.metric("Quotes collected", f"{quotes:,}")
m3.metric("Duplicates removed", f"{duplicates:,}")
m4.metric("Final records", f"{final_count:,}")

# Summary
st.markdown('<div class="section-card"><div class="section-label">Execution</div><div class="section-title">Run summary</div></div>', unsafe_allow_html=True)
if summary:
    st.json(summary, expanded=False)
else:
    st.info("No run summary is available yet.")

# Dataset
st.markdown('<div class="section-card"><div class="section-label">Output</div><div class="section-title">Dataset preview</div></div>', unsafe_allow_html=True)
if rows:
    st.dataframe(rows[:50], use_container_width=True, hide_index=True, height=520)
    st.download_button(
        "Download final_dataset.csv",
        data=CSV_PATH.read_bytes(),
        file_name="final_dataset.csv",
        mime="text/csv",
        use_container_width=False,
    )
else:
    st.info("Run the scraper or add the generated output files to the repository.")

st.divider()
st.caption("CLI: `python main.py`  ·  Tests: `pytest -q`  ·  Sources: Books to Scrape + Quotes to Scrape")
