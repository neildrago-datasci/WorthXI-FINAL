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
import os
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
}

.worth-brand-sub {
    font-size:11px;
    color:#8992a8;
    margin-top:5px;
    letter-spacing:1.5px;
    text-transform:uppercase;
}

.worth-brand-readable {
    align-items:center;
    gap:10px;
}

.worth-sidebar-icon {
    width:42px;
    height:42px;
    object-fit:contain;
    flex:0 0 42px;
}

.worth-brand-copy {
    min-width:0;
}

.worth-brand-title {
    font-size:25px;
    font-weight:900;
    letter-spacing:-1px;
    line-height:1;
    color:#fff;
}

.worth-brand-title span {
    background:linear-gradient(90deg,#4f8cff 0%,#22d3ee 48%,#34d399 100%);
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
}

.worth-brand-sub-readable {
    font-size:8px;
    line-height:1.35;
    color:#aab3c5;
    margin-top:6px;
    letter-spacing:.85px;
    white-space:nowrap;
}

.worth-brand-sub-readable b {
    color:#34d399;
    padding:0 2px;
}

.hero {
    position:relative;
    overflow:hidden;
    border:1px solid rgba(255,255,255,.09);
    border-radius:28px;
    padding:36px 40px;
    margin-bottom:22px;
    background:
        radial-gradient(circle at 85% 15%, rgba(99,102,241,.28), transparent 32%),
        radial-gradient(circle at 70% 100%, rgba(34,197,94,.14), transparent 28%),
        linear-gradient(135deg, rgba(17,24,39,.96), rgba(9,12,21,.98));
    box-shadow:0 25px 70px rgba(0,0,0,.28);
}

.hero:after {
    content:"WORTHXI";
    position:absolute;
    right:-20px;
    bottom:-45px;
    font-size:110px;
    font-weight:900;
    letter-spacing:-7px;
    color:rgba(255,255,255,.025);
    pointer-events:none;
}

.hero-kicker {
    color:#8b9cff;
    text-transform:uppercase;
    font-size:12px;
    font-weight:800;
    letter-spacing:2px;
    margin-bottom:10px;
}

.hero h1 {
    font-size:clamp(42px,6vw,76px);
    line-height:.92;
    letter-spacing:-5px;
    margin:0;
    font-weight:900;
    color:#fff;
}

.hero h1 .hero-xi {
    background:linear-gradient(90deg,#4f8cff 0%,#22d3ee 48%,#34d399 100%);
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
    color:transparent;
}

.hero p {
    color:#aab3c5;
    max-width:700px;
    font-size:16px;
    line-height:1.7;
    margin:18px 0 0;
}

.pill {
    display:inline-flex;
    align-items:center;
    gap:7px;
    margin-top:20px;
    padding:8px 13px;
    border-radius:999px;
    background:rgba(34,197,94,.10);
    border:1px solid rgba(34,197,94,.22);
    color:#86efac;
    font-size:12px;
    font-weight:700;
}

.section-title {
    display:flex;
    align-items:end;
    justify-content:space-between;
    margin:30px 0 14px;
}

.section-title h2 {
    font-size:22px;
    margin:0;
    color:#f7f8fb;
    letter-spacing:-.5px;
}

.section-title span {
    color:#747f95;
    font-size:12px;
}

.player-card {
    border:1px solid rgba(255,255,255,.09);
    border-radius:24px;
    padding:25px;
    background:linear-gradient(145deg, rgba(20,26,42,.94), rgba(11,15,25,.96));
    box-shadow:0 18px 50px rgba(0,0,0,.18);
    margin-bottom:18px;
}


.player-profile {
    display:grid;
    grid-template-columns:140px 1fr auto;
    gap:24px;
    align-items:center;
    border:1px solid rgba(255,255,255,.09);
    border-radius:26px;
    padding:22px 25px;
    margin-bottom:20px;
    background:
        radial-gradient(circle at 10% 20%, rgba(99,102,241,.12), transparent 30%),
        linear-gradient(145deg,rgba(18,24,39,.98),rgba(9,13,22,.98));
    box-shadow:0 20px 60px rgba(0,0,0,.22);
}

.profile-photo-wrap {
    width:140px;
    height:160px;
    border-radius:20px;
    overflow:hidden;
    background:linear-gradient(135deg,#151b31,#0c101c);
    border:1px solid rgba(255,255,255,.1);
    display:flex;
    align-items:center;
    justify-content:center;
}

.player-photo {
    width:100%;
    height:100%;
    object-fit:cover;
    object-position:center top;
}

.player-photo-fallback {
    font-size:38px;
    font-weight:900;
    color:#c7d2fe;
    letter-spacing:-2px;
}

.profile-eyebrow {
    color:#818cf8;
    font-size:10px;
    font-weight:900;
    letter-spacing:2px;
    margin-bottom:8px;
}

.dot {
    color:#4b5563;
    padding:0 5px;
}

.profile-tags {
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-top:17px;
}

.profile-tags span {
    color:#aeb8cb;
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.07);
    border-radius:999px;
    padding:7px 10px;
    font-size:11px;
    font-weight:700;
}

.profile-value {
    min-width:190px;
    padding-left:24px;
    border-left:1px solid rgba(255,255,255,.08);
}

.value-mini-label {
    color:#69758b;
    font-size:9px;
    font-weight:800;
    letter-spacing:1.4px;
}

.profile-price {
    color:#fff;
    font-size:37px;
    font-weight:900;
    letter-spacing:-2px;
    margin:5px 0 2px;
}

.compare-name {
    color:#fff;
    font-size:23px;
    font-weight:900;
    margin-top:7px;
}

@media (max-width: 800px) {
    .player-profile {
        grid-template-columns:90px 1fr;
    }
    .profile-photo-wrap {
        width:90px;
        height:110px;
    }
    .profile-value {
        grid-column:1 / -1;
        border-left:0;
        border-top:1px solid rgba(255,255,255,.08);
        padding:15px 0 0;
    }
}

.player-name {
    font-size:31px;
    font-weight:900;
    letter-spacing:-1.3px;
    color:#fff;
    margin-bottom:5px;
}

.player-meta {
    color:#8994a9;
    font-size:13px;
}

.position-badge {
    display:inline-block;
    padding:5px 10px;
    border-radius:999px;
    background:rgba(99,102,241,.15);
    color:#a5b4fc;
    font-weight:800;
    font-size:11px;
    margin-left:6px;
}

.metric-card {
    background:linear-gradient(145deg,rgba(19,25,40,.95),rgba(10,14,23,.96));
    border:1px solid rgba(255,255,255,.075);
    border-radius:18px;
    padding:17px 18px;
    min-height:100px;
    box-shadow:0 12px 35px rgba(0,0,0,.13);
}

.metric-label {
    color:#7f8ba3;
    font-size:11px;
    text-transform:uppercase;
    letter-spacing:1.15px;
    font-weight:700;
}

.metric-value {
    color:#f8fafc;
    font-size:27px;
    font-weight:850;
    margin-top:7px;
    letter-spacing:-1px;
}

.metric-accent {
    color:#8b9cff;
}

.value-card {
    border-radius:22px;
    padding:24px;
    border:1px solid rgba(255,255,255,.09);
    background:linear-gradient(145deg,rgba(19,25,40,.97),rgba(9,13,22,.97));
}

.value-label {
    color:#7f8ba3;
    font-size:11px;
    text-transform:uppercase;
    letter-spacing:1.2px;
    font-weight:800;
}

.value-number {
    color:white;
    font-size:38px;
    font-weight:900;
    letter-spacing:-1.8px;
    margin-top:5px;
}

.value-sub {
    color:#8994a9;
    font-size:12px;
    margin-top:4px;
}

.status-good {
    color:#86efac;
    background:rgba(34,197,94,.08);
    border:1px solid rgba(34,197,94,.18);
}

.status-watch {
    color:#fcd34d;
    background:rgba(245,158,11,.08);
    border:1px solid rgba(245,158,11,.18);
}

.status-neutral {
    color:#cbd5e1;
    background:rgba(148,163,184,.08);
    border:1px solid rgba(148,163,184,.18);
}

.status-box {
    border-radius:18px;
    padding:15px 18px;
    margin:18px 0;
    font-size:13px;
    line-height:1.55;
}

.insight {
    border-left:3px solid #6366f1;
    padding:13px 17px;
    background:rgba(99,102,241,.07);
    border-radius:0 14px 14px 0;
    color:#b7c0d3;
    font-size:13px;
    line-height:1.65;
    margin:14px 0;
}

.footer {
    margin-top:45px;
    padding-top:22px;
    border-top:1px solid rgba(255,255,255,.07);
    color:#667085;
    font-size:11px;
    text-align:center;
}

div[data-testid="stMetric"] {
    background:transparent;
}

.stTabs [data-baseweb="tab-list"] {
    gap:7px;
    background:rgba(255,255,255,.025);
    padding:6px;
    border-radius:14px;
}

.stTabs [data-baseweb="tab"] {
    border-radius:10px;
    color:#8d98ad;
    font-weight:700;
}

.stTabs [aria-selected="true"] {
    background:rgba(99,102,241,.15);
    color:#c7d2fe;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background:rgba(255,255,255,.045);
    border-color:rgba(255,255,255,.10);
    border-radius:12px;
}

.stSlider > div > div > div {
    color:#6366f1;
}

button[kind="secondary"] {
    border-radius:10px;
}

hr {
    border-color:rgba(255,255,255,.07);
}


.visual-stat {
    border:1px solid rgba(255,255,255,.075);
    background:rgba(255,255,255,.025);
    border-radius:16px;
    padding:15px;
    margin-bottom:10px;
}
.small-note {
    color:#69758b;
    font-size:11px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD MODEL + DATA
# -----------------------------
# Resolve assets relative to this app.py file. This is important when the
# Streamlit app is deployed from a subfolder of a GitHub repository.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_assets():
    model = joblib.load(os.path.join(BASE_DIR, "worthxi_model.pkl"))
    encoder = joblib.load(os.path.join(BASE_DIR, "worthxi_position_encoder.pkl"))
    features = joblib.load(os.path.join(BASE_DIR, "worthxi_features.pkl"))
    data = pd.read_csv(os.path.join(BASE_DIR, "WorthXI_expanded_player_data.csv"))
    return model, encoder, features, data

model, position_encoder, model_features, df = load_assets()

df["Position"] = df["Position"].fillna("").astype(str).str.strip()
df["Season"] = df["Season"].fillna("").astype(str).str.strip()
df["Player"] = df["Player"].fillna("Unknown").astype(str).str.strip()

# -----------------------------
# HELPERS
# -----------------------------
def money(v):
    return f"€{v/1_000_000:.1f}M"

def metric_card(label, value, accent=False):
    cls = "metric-value metric-accent" if accent else "metric-value"
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="{cls}">{value}</div></div>',
        unsafe_allow_html=True
    )

def chart_layout(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#aab3c5"),
        title_font=dict(size=17, color="#f8fafc"),
        margin=dict(l=20, r=25, t=65, b=25),
        xaxis=dict(
            gridcolor="rgba(148,163,184,.09)",
            zerolinecolor="rgba(148,163,184,.12)",
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,.09)",
            zerolinecolor="rgba(148,163,184,.12)",
        ),
    )
    return fig


# -----------------------------
# PLAYER IMAGE + EXTRA HELPERS
# -----------------------------
@st.cache_data(ttl=7 * 24 * 60 * 60, show_spinner=False)
def get_player_image(player_name, club_name=""):
    """
    Identity-safe footballer photo resolver.

    IMPORTANT DESIGN RULE:
    A wrong photo is worse than no photo.  This resolver therefore prefers
    verified Wikidata footballer identities and FAILS CLOSED when confidence
    is too low instead of showing a random same-name person, stadium, badge,
    stamp, or another sport.

    Priority:
    1. Explicit local player image, if supplied.
    2. Exact canonical identity overrides for known ambiguous/high-profile names.
    3. Wikidata identity search, requiring an association-football occupation
       and scoring the player's club against the selected dataset club.
    4. Wikipedia page image only after the Wikidata identity is established.
    """
    name = str(player_name).strip()
    club = str(club_name).strip()

    # These are deliberate identity overrides for names that are commonly
    # ambiguous.  The dataset itself supplies the club, so Pedro -> Pedro
    # Rodriguez is unambiguous here because every Pedro record is Chelsea.
    CANONICAL = {
        "marc guehi": "Marc Guéhi",
        "matheus nunes": "Matheus Nunes",
        "mohamed salah": "Mohamed Salah",
        "pedro": "Pedro Rodríguez",
        "petr cech": "Petr Čech",
        "rodri": "Rodri (footballer, born 1996)",
        "romeo lavia": "Roméo Lavia",
        "sadio mane": "Sadio Mané",
        "thiago alcantara": "Thiago Alcântara",
        "vincent kompany": "Vincent Kompany",
        "yaya toure": "Yaya Touré",
        "zlatan ibrahimovic": "Zlatan Ibrahimović",
        "cesc fabregas": "Cesc Fàbregas",
        "achraf hakimi": "Achraf Hakimi",
    }

    # 1) Optional local images always win.
    image_dir = Path(__file__).resolve().parent / "player_images"
    normalized = name.lower().replace(".", "").strip()
    local_names = [name, name.replace(" ", "_"), CANONICAL.get(normalized, "")]
    if image_dir.exists():
        for candidate_name in local_names:
            if not candidate_name:
                continue
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidate = image_dir / f"{candidate_name}{ext}"
                if candidate.exists():
                    return str(candidate)

    headers = {
        "User-Agent": "WorthXI/3.0 (student football analytics research project)"
    }

    def get_json(url, params, timeout=10):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    def norm_text(value):
        import unicodedata
        value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
        return " ".join(value.lower().replace("-", " ").replace("_", " ").split())

    target = norm_text(name)
    canonical = CANONICAL.get(normalized, name)
    canonical_norm = norm_text(canonical)
    club_norm = norm_text(club)

    # Common club aliases in the dataset versus Wikidata/Wikipedia.
    club_aliases = {
        "manchester city": ["manchester city", "manchester city fc"],
        "manchester united": ["manchester united", "manchester united fc"],
        "liverpool": ["liverpool", "liverpool fc"],
        "chelsea": ["chelsea", "chelsea fc"],
        "arsenal": ["arsenal", "arsenal fc"],
        "crystal palace": ["crystal palace", "crystal palace fc"],
    }
    club_terms = club_aliases.get(club_norm, [club_norm]) if club_norm else []

    # 2) Wikidata: identity + occupation + club + image.
    # Association football player is Wikidata Q937857.
    wd_search = get_json("https://www.wikidata.org/w/api.php", {
        "action": "wbsearchentities",
        "search": canonical,
        "language": "en",
        "uselang": "en",
        "format": "json",
        "limit": 10,
        "type": "item",
    })

    candidates = (wd_search or {}).get("search", [])
    ids = [c.get("id") for c in candidates if c.get("id", "").startswith("Q")]
    if ids:
        entity_data = get_json("https://www.wikidata.org/w/api.php", {
            "action": "wbgetentities",
            "ids": "|".join(ids),
            "format": "json",
            "languages": "en",
            "props": "labels|aliases|descriptions|claims",
        }, timeout=15)
        entities = (entity_data or {}).get("entities", {})

        # Collect all referenced club/occupation IDs, then fetch their labels.
        referenced_ids = set()
        for ent in entities.values():
            for claim in ent.get("claims", {}).get("P54", []):
                try:
                    referenced_ids.add(claim["mainsnak"]["datavalue"]["value"]["id"])
                except Exception:
                    pass
            for claim in ent.get("claims", {}).get("P106", []):
                try:
                    referenced_ids.add(claim["mainsnak"]["datavalue"]["value"]["id"])
                except Exception:
                    pass

        label_map = {}
        if referenced_ids:
            ref_data = get_json("https://www.wikidata.org/w/api.php", {
                "action": "wbgetentities",
                "ids": "|".join(list(referenced_ids)[:50]),
                "format": "json",
                "languages": "en",
                "props": "labels",
            }, timeout=15)
            for qid, ent in (ref_data or {}).get("entities", {}).items():
                label_map[qid] = ent.get("labels", {}).get("en", {}).get("value", "")

        scored = []
        for qid in ids:
            ent = entities.get(qid, {})
            label = ent.get("labels", {}).get("en", {}).get("value", "")
            aliases = [a.get("value", "") for a in ent.get("aliases", {}).get("en", [])]
            desc = ent.get("descriptions", {}).get("en", {}).get("value", "")
            label_norm = norm_text(label)
            alias_norms = [norm_text(a) for a in aliases]
            desc_norm = norm_text(desc)

            # Require football identity. P106 is the strongest signal.
            occupation_ids = set()
            for claim in ent.get("claims", {}).get("P106", []):
                try:
                    occupation_ids.add(claim["mainsnak"]["datavalue"]["value"]["id"])
                except Exception:
                    pass
            occupation_labels = [norm_text(label_map.get(q, "")) for q in occupation_ids]
            football_occupation = (
                "Q937857" in occupation_ids
                or any("association football" in x or "football player" in x or "footballer" in x or "soccer player" in x for x in occupation_labels)
                or "footballer" in desc_norm
                or "soccer player" in desc_norm
                or "football player" in desc_norm
            )
            if not football_occupation:
                continue

            # Club membership is a powerful disambiguator for short/common names.
            team_labels = []
            for claim in ent.get("claims", {}).get("P54", []):
                try:
                    team_qid = claim["mainsnak"]["datavalue"]["value"]["id"]
                    team_labels.append(norm_text(label_map.get(team_qid, "")))
                except Exception:
                    pass
            club_match = any(term and any(term in team for team in team_labels) for term in club_terms)

            score = 0
            if label_norm == canonical_norm or label_norm == target:
                score += 70
            elif target and (target in label_norm or label_norm in target):
                score += 45
            elif any(target == a for a in alias_norms):
                score += 55
            elif any(target in a or a in target for a in alias_norms if a):
                score += 30

            if club_match:
                score += 45
            elif club_terms:
                score -= 10

            # Prefer a real image claim. A verified identity without an image
            # is still preferable to a wrong image, but it should not display one.
            image_claims = ent.get("claims", {}).get("P18", [])
            image_file = None
            if image_claims:
                try:
                    image_file = image_claims[0]["mainsnak"]["datavalue"]["value"]
                except Exception:
                    pass
            if image_file:
                score += 10

            scored.append((score, label, qid, image_file, club_match, desc))

        scored.sort(key=lambda x: x[0], reverse=True)
        if scored:
            score, label, qid, image_file, club_match, desc = scored[0]
            # High-confidence rule. Club match is required for highly ambiguous
            # names such as Pedro; otherwise exact footballer identity is enough.
            exact_identity = norm_text(label) in {target, canonical_norm}
            if image_file and score >= 80 and (club_match or exact_identity):
                encoded = requests.utils.quote(str(image_file), safe="")
                return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=700"

            # For a non-exact but strong candidate, require club match.
            if image_file and score >= 90 and club_match:
                encoded = requests.utils.quote(str(image_file), safe="")
                return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=700"

    # 3) Exact Wikipedia page, but ONLY for our verified canonical title.
    # This prevents random search results from becoming photos.
    wiki_title = canonical
    encoded_title = requests.utils.quote(wiki_title.replace(" ", "_"), safe="")
    rest_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
    try:
        r = requests.get(rest_url, headers=headers, timeout=8)
        if r.ok:
            data = r.json()
            desc = norm_text(data.get("description", ""))
            thumb = data.get("thumbnail", {}).get("source")
            football_desc = any(k in desc for k in ["footballer", "football player", "soccer player"])
            if thumb and football_desc:
                return thumb
    except Exception:
        pass

    # FAIL CLOSED: do not return a random image.
    return None

def initials(name):
    parts = [p for p in str(name).split() if p]
    if not parts:
        return "⚽"
    return "".join(p[0] for p in parts[:2]).upper()

def money_exact(v):
    return f"€{v/1_000_000:.2f}M"

def get_player_history(player_name):
    h = df[df["Player"] == player_name].copy()
    if h.empty:
        return h
    h = h.sort_values("Season")
    return h

def encode_player_position(position_value):
    # The saved encoder is a MultiLabelBinarizer, so support both single
    # positions (e.g. "MF") and combined positions (e.g. "MF,FW").
    labels = [p.strip() for p in str(position_value).split(",") if p.strip()]
    if not labels:
        labels = [""]
    return position_encoder.transform([labels])[0]

def predict_row(row):
    x = pd.DataFrame({
        "Goal_Contribution": [row["Goal_Contribution"]],
        "Shot_Accuracy": [row["Shot_Accuracy"]],
        "Defensive_Contribution": [row["Defensive_Contribution"]],
        "Minutes_Per_Appearance": [row["Minutes_Per_Appearance"]],
        "Discipline_Score": [row["Discipline_Score"]],
        "Age": [row["Age"]],
    })
    enc = encode_player_position(row["Position"])
    for i, pos in enumerate(position_encoder.classes_):
        x[f"Position_{pos}"] = enc[i]
    x = x.reindex(columns=model_features, fill_value=0)
    return float(model.predict(x)[0])

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div class="worth-brand worth-brand-readable">
        <img src="data:image/png;base64,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" class="worth-sidebar-icon" alt="WORTHXI logo">
        <div class="worth-brand-copy">
            <div class="worth-brand-title">WORTH<span>XI</span></div>
            <div class="worth-brand-sub-readable">FOOTBALL ANALYTICS <b>•</b> VALUE INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Explore Players")

    positions = ["All Positions", "FW", "MF", "DF", "GK"]
    seasons = sorted(df["Season"].dropna().unique())
    min_age = int(df["Age"].dropna().min())
    max_age = int(df["Age"].dropna().max())

    selected_position = st.selectbox("Position", positions)
    selected_age_range = st.slider(
        "Age range",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age)
    )
    selected_season = st.selectbox(
        "Season",
        ["All Seasons"] + seasons
    )

    st.markdown("---")
    st.markdown("### Dataset")
    st.markdown(
        f"**{len(df):,}** player-season records  \n"
        f"**{df['Player'].nunique():,}** unique players  \n"
        f"**{df['Season'].nunique():,}** seasons"
    )

    st.markdown("---")
    st.caption("WorthXI • Football Performance × Market Value")
    st.caption("Machine-learning assisted analysis")
    st.caption("Player photos: Wikimedia + optional local images")

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-kicker">Football analytics · value intelligence</div>
    <h1>WORTH<span class="hero-xi">XI</span></h1>
    <p>
        Go beyond the headline price. Explore player performance, compare
        market value with a machine-learning estimate, and understand the
        statistical profile behind the number.
    </p>
    <div class="pill">● Gradient Boosting valuation engine</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# FILTER DATA
# -----------------------------
filtered_df = df.copy()

if selected_position != "All Positions":
    filtered_df = filtered_df[
        filtered_df["Position"].apply(
            lambda value: selected_position in [p.strip() for p in str(value).split(",")]
        )
    ]

filtered_df = filtered_df[
    (filtered_df["Age"] >= selected_age_range[0]) &
    (filtered_df["Age"] <= selected_age_range[1])
]

if selected_season != "All Seasons":
    filtered_df = filtered_df[filtered_df["Season"] == selected_season]

if filtered_df.empty:
    st.error("No players match these filters. Try widening the age range or changing the position.")
    st.stop()

players = sorted(filtered_df["Player"].unique())

st.markdown('<div class="section-title"><h2>Find a player</h2><span>Filter → select → analyse</span></div>', unsafe_allow_html=True)

selected_player = st.selectbox(
    "Player",
    players,
    label_visibility="collapsed"
)

# Selected player row: respect season filter, otherwise use latest season.
player_rows = filtered_df[filtered_df["Player"] == selected_player].copy()
if player_rows.empty:
    player_rows = df[df["Player"] == selected_player].copy()

player_rows = player_rows.sort_values("Season")
player = player_rows.iloc[-1]

# -----------------------------
# QUICK DATASET STATS
# -----------------------------
q1, q2, q3, q4 = st.columns(4)
with q1:
    metric_card("Players in current view", f"{len(players):,}")
with q2:
    metric_card("Records in current view", f"{len(filtered_df):,}")
with q3:
    metric_card("Selected season", str(player["Season"]))
with q4:
    metric_card("Position", str(player["Position"]), accent=True)

# -----------------------------
# PLAYER HEADER — WOW PROFILE
# -----------------------------
st.markdown('<div class="section-title"><h2>WorthXI Player Profile</h2><span>Scouting profile</span></div>', unsafe_allow_html=True)

club = str(player["Club"])
player_image = get_player_image(selected_player, club)
position = str(player["Position"])
age = int(player["Age"])
season = str(player["Season"])

if player_image:
    image_html = f'<img src="{player_image}" class="player-photo" alt="{selected_player}">'
else:
    image_html = f'<div class="player-photo-fallback">{initials(selected_player)}</div>'

st.markdown(
    f"""
    <div class="player-profile">
        <div class="profile-photo-wrap">{image_html}</div>
        <div class="profile-main">
            <div class="profile-eyebrow">PLAYER PROFILE</div>
            <div class="player-name">{selected_player}</div>
            <div class="player-meta">
                {club} <span class="dot">•</span> Age {age}
                <span class="dot">•</span> {season}
                <span class="position-badge">{position}</span>
            </div>
            <div class="profile-tags">
                <span>⚽ {int(player['Goals'])} goals</span>
                <span>🎯 {int(player['Assists'])} assists</span>
                <span>📈 {int(player['Goal_Contribution'])} contributions</span>
            </div>
        </div>
        <div class="profile-value">
            <div class="value-mini-label">MARKET VALUE</div>
            <div class="profile-price">{money_exact(float(player['Market_Value_EUR']))}</div>
            <div class="value-mini-label">OBSERVED VALUE</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# PREDICTION
# -----------------------------
prediction_input = pd.DataFrame({
    "Goal_Contribution": [player["Goal_Contribution"]],
    "Shot_Accuracy": [player["Shot_Accuracy"]],
    "Defensive_Contribution": [player["Defensive_Contribution"]],
    "Minutes_Per_Appearance": [player["Minutes_Per_Appearance"]],
    "Discipline_Score": [player["Discipline_Score"]],
    "Age": [player["Age"]],
})

position_data = encode_player_position(player["Position"])
position_columns = position_encoder.classes_

for i, position in enumerate(position_columns):
    prediction_input[f"Position_{position}"] = position_data[i]

prediction_input = prediction_input.reindex(columns=model_features, fill_value=0)
predicted_value = float(model.predict(prediction_input)[0])
actual_value = float(player["Market_Value_EUR"])
value_gap = actual_value - predicted_value

# -----------------------------
# TABS
# -----------------------------
tab_overview, tab_value, tab_performance, tab_visuals, tab_history, tab_compare, tab_model = st.tabs([
    "Overview",
    "💰 Valuation",
    "📊 Performance",
    "📉 Visualizations",
    "📈 History",
    "⚔️ Compare",
    "🧠 Model"
])

# ============================================================
# OVERVIEW
# ============================================================
with tab_overview:
    st.markdown('<div class="section-title"><h2>Performance snapshot</h2><span>Core match metrics</span></div>', unsafe_allow_html=True)

    cols = st.columns(4)
    overview_metrics = [
        ("Goals", f"{int(player['Goals'])}"),
        ("Assists", f"{int(player['Assists'])}"),
        ("Goal contribution", f"{int(player['Goal_Contribution'])}"),
        ("Shot accuracy", f"{player['Shot_Accuracy']:.1f}%"),
    ]
    for col, (label, value) in zip(cols, overview_metrics):
        with col:
            metric_card(label, value, accent=True)

    cols = st.columns(3)
    overview_metrics_2 = [
        ("Defensive contribution", f"{int(player['Defensive_Contribution'])}"),
        ("Minutes / appearance", f"{player['Minutes_Per_Appearance']:.1f}"),
        ("Discipline score", f"{player['Discipline_Score']:.1f}"),
    ]
    for col, (label, value) in zip(cols, overview_metrics_2):
        with col:
            metric_card(label, value)

    st.markdown('<div class="section-title"><h2>At a glance</h2><span>Actual vs model estimate</span></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="value-card"><div class="value-label">Actual market value</div>'
            f'<div class="value-number">{money(actual_value)}</div>'
            f'<div class="value-sub">Observed value in the dataset</div></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div class="value-card"><div class="value-label">WorthXI estimate</div>'
            f'<div class="value-number">{money(predicted_value)}</div>'
            f'<div class="value-sub">Gradient Boosting estimate</div></div>',
            unsafe_allow_html=True
        )
    with c3:
        direction = "above" if value_gap > 0 else "below" if value_gap < 0 else "aligned with"
        st.markdown(
            f'<div class="value-card"><div class="value-label">Model gap</div>'
            f'<div class="value-number">{money(abs(value_gap))}</div>'
            f'<div class="value-sub">Actual value is {direction} the estimate</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="insight"><b>WorthXI lens:</b> The estimate is generated from the performance '
        'features used by the trained model. It should be read as a statistical estimate, not a '
        'replacement for real-world transfer-market judgement.</div>',
        unsafe_allow_html=True
    )

# ============================================================
# VALUATION
# ============================================================
with tab_value:
    st.markdown('<div class="section-title"><h2>Market value intelligence</h2><span>Actual × predicted</span></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Actual market value", money(actual_value), accent=True)
    with c2:
        metric_card("WorthXI estimated", money(predicted_value), accent=True)
    with c3:
        metric_card("Absolute gap", money(abs(value_gap)))

    if value_gap > 0:
        st.markdown(
            f'<div class="status-box status-good"><b>Actual value is higher than the model estimate.</b><br>'
            f'The observed market value exceeds the WorthXI estimate by <b>{money(value_gap)}</b>.</div>',
            unsafe_allow_html=True
        )
    elif value_gap < 0:
        st.markdown(
            f'<div class="status-box status-watch"><b>Model estimate is higher than the actual value.</b><br>'
            f'The WorthXI estimate exceeds the observed market value by <b>{money(abs(value_gap))}</b>.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-box status-neutral"><b>Values are approximately aligned.</b><br>'
            'The model estimate and observed market value are effectively equal.</div>',
            unsafe_allow_html=True
        )

    value_chart = pd.DataFrame({
        "Value": ["Actual Market Value", "WorthXI Estimate"],
        "Market Value (€M)": [actual_value/1e6, predicted_value/1e6]
    })

    fig = px.bar(
        value_chart,
        x="Value",
        y="Market Value (€M)",
        text="Market Value (€M)",
        title=f"{selected_player} · Value comparison",
    )
    fig.update_traces(
        texttemplate="€%{text:.1f}M",
        textposition="outside",
        marker_line_width=0
    )
    chart_layout(fig, 470)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ============================================================
# PERFORMANCE
# ============================================================
with tab_performance:
    st.markdown('<div class="section-title"><h2>Performance profile</h2><span>Percentile vs dataset</span></div>', unsafe_allow_html=True)

    profile_metrics = {
        "Goal Contribution": "Goal_Contribution",
        "Shot Accuracy": "Shot_Accuracy",
        "Defensive Contribution": "Defensive_Contribution",
        "Minutes / Appearance": "Minutes_Per_Appearance",
        "Discipline Score": "Discipline_Score"
    }

    profile_values = []
    for display_name, column_name in profile_metrics.items():
        valid = df[column_name].dropna()
        rank_pct = valid.rank(pct=True) * 100
        matches = rank_pct[valid == player[column_name]]
        score = float(matches.mean()) if not matches.empty else 0.0
        profile_values.append((display_name, score, float(player[column_name])))

    profile_df = pd.DataFrame(profile_values, columns=["Metric", "Score", "Raw"])

    theta = profile_df["Metric"].tolist()
    values = profile_df["Score"].tolist()

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=theta + [theta[0]],
        fill="toself",
        name="Percentile",
        hovertemplate="<b>%{theta}</b><br>Percentile: %{r:.1f}<extra></extra>"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0,100],
                tickvals=[20,40,60,80,100],
                gridcolor="rgba(148,163,184,.12)",
                linecolor="rgba(148,163,184,.18)"
            ),
            angularaxis=dict(
                gridcolor="rgba(148,163,184,.10)",
                linecolor="rgba(148,163,184,.16)"
            )
        ),
        showlegend=False,
        title=f"{selected_player} · Performance percentile profile"
    )
    chart_layout(fig_radar, 610)
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-title"><h2>Metric breakdown</h2><span>Raw value + percentile</span></div>', unsafe_allow_html=True)

    breakdown = profile_df.copy()
    breakdown["Percentile"] = breakdown["Score"].map(lambda x: f"{x:.1f}%")
    breakdown["Raw Value"] = breakdown["Raw"].map(lambda x: f"{x:.1f}")
    st.dataframe(
        breakdown[["Metric", "Raw Value", "Percentile"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        '<div class="small-note">Percentiles compare the selected player with the complete player dataset. '
        'They describe relative standing, not causal impact on market value.</div>',
        unsafe_allow_html=True
    )

# ============================================================
# VISUALIZATIONS
# ============================================================
with tab_visuals:
    st.markdown(
        '<div class="section-title"><h2>Visual analytics</h2>'
        '<span>Explore the dataset from multiple angles</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="insight"><b>Analytics lab:</b> These views use the full WorthXI '
        'dataset to reveal relationships between performance, age, position and market value. '
        'Use the hover tools to inspect individual observations.</div>',
        unsafe_allow_html=True
    )

    # 1. Performance vs market value
    scatter_df = df[[
        "Goal_Contribution", "Market_Value_EUR", "Position", "Age", "Player"
    ]].dropna().copy()
    scatter_df["Market Value (€M)"] = scatter_df["Market_Value_EUR"] / 1e6

    fig_scatter = px.scatter(
        scatter_df,
        x="Goal_Contribution",
        y="Market Value (€M)",
        size="Age",
        hover_name="Player",
        hover_data=["Position", "Age"],
        title="Goal contribution vs market value",
        opacity=0.65
    )
    fig_scatter.update_layout(
        xaxis_title="Goal contribution",
        yaxis_title="Market value (€M)"
    )
    chart_layout(fig_scatter, 500)
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

    # 2. Market value distribution
    st.markdown(
        '<div class="section-title"><h2>Market value distribution</h2>'
        '<span>How player values are spread</span></div>',
        unsafe_allow_html=True
    )
    dist_df = df[["Market_Value_EUR"]].dropna().copy()
    dist_df["Market Value (€M)"] = dist_df["Market_Value_EUR"] / 1e6

    fig_dist = px.histogram(
        dist_df,
        x="Market Value (€M)",
        nbins=35,
        title="Distribution of player market values"
    )
    fig_dist.update_layout(xaxis_title="Market value (€M)", yaxis_title="Player-season records")
    chart_layout(fig_dist, 430)
    st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})

    # 3. Market value by position
    st.markdown(
        '<div class="section-title"><h2>Value by position</h2>'
        '<span>Distribution across playing roles</span></div>',
        unsafe_allow_html=True
    )
    box_df = df[["Position", "Market_Value_EUR"]].dropna().copy()
    box_df["Market Value (€M)"] = box_df["Market_Value_EUR"] / 1e6

    fig_box = px.box(
        box_df,
        x="Position",
        y="Market Value (€M)",
        points=False,
        title="Market value distribution by position"
    )
    chart_layout(fig_box, 470)
    st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})

    # 4. Age vs market value
    age_df = df[["Age", "Market_Value_EUR", "Player", "Position"]].dropna().copy()
    age_df["Market Value (€M)"] = age_df["Market_Value_EUR"] / 1e6

    fig_age = px.scatter(
        age_df,
        x="Age",
        y="Market Value (€M)",
        hover_name="Player",
        hover_data=["Position"],
        title="Age vs market value",
        opacity=0.55,
        trendline="ols"
    )
    fig_age.update_layout(xaxis_title="Age", yaxis_title="Market value (€M)")
    chart_layout(fig_age, 500)
    st.plotly_chart(fig_age, use_container_width=True, config={"displayModeBar": False})

    # 5. Average performance metrics by position
    st.markdown(
        '<div class="section-title"><h2>Performance by position</h2>'
        '<span>Average profile across the dataset</span></div>',
        unsafe_allow_html=True
    )
    pos_perf = df.groupby("Position", as_index=False)[[
        "Goals", "Assists", "Goal_Contribution",
        "Shot_Accuracy", "Defensive_Contribution"
    ]].mean()

    metric_choice = st.selectbox(
        "Choose a metric",
        ["Goals", "Assists", "Goal_Contribution", "Shot_Accuracy", "Defensive_Contribution"],
        key="visual_metric"
    )

    fig_pos = px.bar(
        pos_perf.sort_values(metric_choice, ascending=False),
        x="Position",
        y=metric_choice,
        text=metric_choice,
        title=f"Average {metric_choice.replace('_', ' ')} by position"
    )
    fig_pos.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    chart_layout(fig_pos, 430)
    st.plotly_chart(fig_pos, use_container_width=True, config={"displayModeBar": False})

# ============================================================
# HISTORY
# ============================================================
with tab_history:
    history = get_player_history(selected_player)
    st.markdown('<div class="section-title"><h2>Career trajectory</h2><span>Available player-season records</span></div>', unsafe_allow_html=True)

    if len(history) >= 2:
        history = history.copy()
        history["WorthXI Estimate"] = history.apply(predict_row, axis=1)
        history["Market Value (€M)"] = history["Market_Value_EUR"] / 1e6
        history["WorthXI Estimate (€M)"] = history["WorthXI Estimate"] / 1e6

        hist = history[["Season", "Market Value (€M)", "WorthXI Estimate (€M)"]]

        fig_hist = go.Figure()
        actual_labels = history["Market_Value_EUR"].map(money).tolist()
        estimate_labels = history["WorthXI Estimate"].map(money).tolist()

        fig_hist.add_trace(go.Scatter(
            x=hist["Season"], y=hist["Market Value (€M)"],
            mode="lines+markers", name="Actual market value",
            customdata=actual_labels,
            hovertemplate="%{x}<br>Actual market value: %{customdata}<extra></extra>",
            line=dict(width=3), marker=dict(size=7)
        ))
        fig_hist.add_trace(go.Scatter(
            x=hist["Season"], y=hist["WorthXI Estimate (€M)"],
            mode="lines+markers", name="WorthXI estimate",
            customdata=estimate_labels,
            hovertemplate="%{x}<br>WorthXI estimate: %{customdata}<extra></extra>",
            line=dict(width=3, dash="dot"), marker=dict(size=7)
        ))
        fig_hist.update_layout(
            title=f"{selected_player} · Market value trajectory",
            yaxis=dict(ticksuffix="M", tickprefix="€")
        )
        chart_layout(fig_hist, 500)
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

        history_display = history[[
            "Season", "Age", "Goals", "Assists",
            "Goal_Contribution", "Market_Value_EUR", "WorthXI Estimate"
        ]].copy()
        history_display["Market_Value_EUR"] = history_display["Market_Value_EUR"].map(money)
        history_display["WorthXI Estimate"] = history_display["WorthXI Estimate"].map(money)
        history_display = history_display.rename(columns={
            "Market_Value_EUR": "Actual Value",
            "WorthXI Estimate": "WorthXI Estimate"
        })

        st.dataframe(
            history_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.markdown(
            '<div class="status-box status-neutral"><b>History is limited for this player.</b><br>'
            'The dataset contains only one player-season record matching this profile.</div>',
            unsafe_allow_html=True
        )

# ============================================================
# COMPARE
# ============================================================
with tab_compare:
    st.markdown('<div class="section-title"><h2>Head-to-head comparison</h2><span>Same dataset · same model lens</span></div>', unsafe_allow_html=True)

    compare_candidates = [p for p in players if p != selected_player]
    if compare_candidates:
        comparison_player = st.selectbox(
            "Compare with",
            compare_candidates,
            key="comparison_player"
        )
        other_rows = df[df["Player"] == comparison_player].sort_values("Season")
        other = other_rows.iloc[-1]

        other_pred = predict_row(other)
        other_actual = float(other["Market_Value_EUR"])

        left, right = st.columns(2)
        for col, name, row, pred, actual in [
            (left, selected_player, player, predicted_value, actual_value),
            (right, comparison_player, other, other_pred, other_actual)
        ]:
            with col:
                img = get_player_image(name, row.get("Club", "") if isinstance(row, pd.Series) else "")
                if img:
                    st.image(img, width=170)
                st.markdown(
                    f'<div class="compare-name">{name}</div>'
                    f'<div class="player-meta">{row["Club"]} · {row["Position"]} · Age {int(row["Age"])}</div>',
                    unsafe_allow_html=True
                )

        compare_metrics = pd.DataFrame({
            "Metric": [
                "Goals", "Assists", "Goal Contribution",
                "Shot Accuracy", "Defensive Contribution",
                "Minutes / Appearance", "Actual Value (€M)", "WorthXI (€M)"
            ],
            selected_player: [
                float(player["Goals"]), float(player["Assists"]), float(player["Goal_Contribution"]),
                float(player["Shot_Accuracy"]), float(player["Defensive_Contribution"]),
                float(player["Minutes_Per_Appearance"]), actual_value/1e6, predicted_value/1e6
            ],
            comparison_player: [
                float(other["Goals"]), float(other["Assists"]), float(other["Goal_Contribution"]),
                float(other["Shot_Accuracy"]), float(other["Defensive_Contribution"]),
                float(other["Minutes_Per_Appearance"]), other_actual/1e6, other_pred/1e6
            ]
        })
        st.dataframe(compare_metrics, use_container_width=True, hide_index=True)

        comp_chart = pd.DataFrame({
            "Metric": ["Goals", "Assists", "Goal Contribution", "Shot Accuracy"],
            selected_player: [
                float(player["Goals"]), float(player["Assists"]),
                float(player["Goal_Contribution"]), float(player["Shot_Accuracy"])
            ],
            comparison_player: [
                float(other["Goals"]), float(other["Assists"]),
                float(other["Goal_Contribution"]), float(other["Shot_Accuracy"])
            ]
        })
        fig_comp = px.bar(
            comp_chart, x="Metric", y=[selected_player, comparison_player],
            barmode="group", title="Performance comparison"
        )
        chart_layout(fig_comp, 450)
        st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Choose a broader filter to compare this player with another player.")

# ============================================================
# MODEL
# ============================================================
with tab_model:
    st.markdown('<div class="section-title"><h2>Model intelligence</h2><span>Feature importance</span></div>', unsafe_allow_html=True)

    model_feature_names = list(getattr(model, "feature_names_in_", model_features))

    # Gradient Boosting provides tree-based feature importance rather than
    # linear coefficients. Convert the raw importances into percentages so
    # they remain easy to read in the existing WorthXI interface.
    importances = pd.Series(
        model.feature_importances_,
        index=model_feature_names
    )

    total_importance = importances.sum()
    feature_analysis = pd.DataFrame({
        "Feature": model_feature_names,
        "Relative Influence": (
            importances / total_importance * 100
            if total_importance != 0 else 0
        )
    })

    feature_name_map = {
        "Goal_Contribution": "Goal Contribution",
        "Shot_Accuracy": "Shot Accuracy",
        "Defensive_Contribution": "Defensive Contribution",
        "Minutes_Per_Appearance": "Minutes / Appearance",
        "Discipline_Score": "Discipline Score",
        "Age": "Age",
        "Position_DF": "Position — DF",
        "Position_FW": "Position — FW",
        "Position_GK": "Position — GK",
        "Position_MF": "Position — MF"
    }

    feature_analysis["Feature"] = feature_analysis["Feature"].map(feature_name_map)
    feature_analysis = feature_analysis.sort_values("Relative Influence", ascending=True)

    fig_inf = px.bar(
        feature_analysis,
        x="Relative Influence",
        y="Feature",
        orientation="h",
        text="Relative Influence",
        title="Relative importance of modelling features",
    )
    fig_inf.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        marker_line_width=0
    )
    chart_layout(fig_inf, 570)
    fig_inf.update_xaxes(range=[0, max(10, feature_analysis["Relative Influence"].max()*1.25)])
    st.plotly_chart(fig_inf, use_container_width=True, config={"displayModeBar": False})

    display_influence = feature_analysis[["Feature","Relative Influence"]].copy()
    display_influence["Relative Influence"] = display_influence["Relative Influence"].map(lambda x: f"{x:.1f}%")
    st.dataframe(display_influence, use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="insight"><b>How to read this:</b> Relative importance shows how much '
        'each input feature contributes to the Gradient Boosting model prediction process. '
        'It describes model behaviour and does not establish causation.</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(
    '<div class="footer">WORTHXI · Football Player Performance × Market Value · '
    'Built with Python, Streamlit, Plotly and Machine Learning</div>',
    unsafe_allow_html=True
)