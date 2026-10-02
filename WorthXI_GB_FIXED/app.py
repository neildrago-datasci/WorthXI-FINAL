import streamlit as st

def format_market_value(value):
    """Display EUR market values compactly (e.g. €105.5M, €950K)."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}€{value / 1_000_000:.1f}M".replace(".0M", "M")
    if value >= 1_000:
        return f"{sign}€{value / 1_000:.1f}K".replace(".0K", "K")
    return f"{sign}€{value:,.0f}"

import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
import requests
from pathlib import Path

# ============================================================
# WORTHXI — PREMIUM PLAYER PERFORMANCE DASHBOARD
# ============================================================

st.set_page_config(
    page_title="WorthXI | Football Value Lab",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# PREMIUM UI
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 85% 5%, rgba(99,102,241,.13), transparent 28%),
        radial-gradient(circle at 8% 35%, rgba(16,185,129,.09), transparent 25%),
        #070a12;
}

[data-testid="stHeader"] {
    background: rgba(7,10,18,.75);
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1020 0%, #080b13 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] * {
    color: #e8ecf5;
}

.worth-brand {
    display:flex;
    align-items:center;
    gap:14px;
    margin-bottom: 2rem;
}

.worth-ball {
    width:52px;
    height:52px;
    border-radius:16px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:26px;
    background:linear-gradient(135deg,#6366f1,#22c55e);
    box-shadow:0 12px 35px rgba(99,102,241,.28);
}

.worth-brand-title {
    font-size:25px;
    font-weight:900;
    letter-spacing:-1px;
    line-height:1;
