from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import streamlit as st


def resolve_project_root(start_dir: Path) -> Path:
    for candidate in [start_dir, *start_dir.parents]:
        if (candidate / "src" / "gamescope_ai").exists():
            return candidate
    return start_dir


ROOT = resolve_project_root(Path(__file__).resolve().parent)
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from gamescope_ai.predictor import GameScopePredictor
from gamescope_ai.train import main as train_models


def ensure_artifacts() -> None:
    required = [
        ROOT / "artifacts" / "success_classifier.joblib",
        ROOT / "artifacts" / "profit_regressor.joblib",
        ROOT / "artifacts" / "metadata.json",
    ]
    if all(path.exists() for path in required):
        return
    train_models()

st.set_page_config(page_title="GameScope AI", page_icon="🎮", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 85% 15%, rgba(0, 245, 255, 0.14), transparent 30%),
            radial-gradient(circle at 12% 8%, rgba(176, 91, 255, 0.2), transparent 32%),
            radial-gradient(circle at 60% 78%, rgba(56, 115, 255, 0.14), transparent 30%),
            linear-gradient(160deg, #0b0f23 0%, #080a1a 55%, #070812 100%);
        color: #f0f3ff;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1330 0%, #0c1027 100%);
        border-right: 1px solid #24326f;
    }
    .hero {
        padding: 1.25rem 1.35rem;
        border: 1px solid #2f3f90;
        border-radius: 16px;
        background: linear-gradient(120deg, rgba(50,73,162,0.42), rgba(19,23,46,0.82));
        box-shadow: 0 0 22px rgba(93, 132, 255, 0.23), inset 0 0 25px rgba(112, 75, 255, 0.12);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(110deg, transparent 30%, rgba(120, 195, 255, 0.2) 48%, transparent 66%);
        transform: translateX(-120%);
        animation: sweep 6s linear infinite;
        pointer-events: none;
    }
    .hero h1 {
        margin: 0;
        letter-spacing: 0.4px;
        text-shadow: 0 0 18px rgba(108, 224, 255, 0.28);
        background: linear-gradient(90deg, #8bf1ff, #b6d2ff, #9ef5dd, #8bf1ff);
        background-size: 220% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: titleFlow 8s linear infinite;
    }
    .hero p {
        margin: .45rem 0 0 0;
        color: #d8ddff;
    }
    .typewriter {
        width: fit-content;
        white-space: nowrap;
        overflow: hidden;
        border-right: 2px solid rgba(163, 231, 255, 0.85);
        animation: typing 3.6s steps(62, end) 1, caret .8s step-end infinite;
    }
    .live-text {
        margin-top: .55rem;
        font-size: .8rem;
        color: #8de9c9;
        letter-spacing: .3px;
        animation: pulseText 2.6s ease-in-out infinite;
    }
    .chip-row { margin-top: .75rem; }
    .chip {
        display: inline-block;
        margin: 0 .5rem .35rem 0;
        padding: .3rem .6rem;
        border-radius: 999px;
        font-size: .78rem;
        border: 1px solid #3550b4;
        background: rgba(41, 62, 148, 0.28);
        color: #b8ddff;
        animation: floatChip 3.2s ease-in-out infinite;
    }
    .chip:nth-child(2) { animation-delay: .35s; }
    .chip:nth-child(3) { animation-delay: .7s; }
    .game-feed {
        margin: .35rem 0 .95rem 0;
        border: 1px solid #294f8f;
        border-radius: 10px;
        padding: .55rem .75rem;
        background: rgba(12, 26, 45, .68);
        color: #b8ddff;
        font-size: .82rem;
        line-height: 1.35;
    }
    .section-card {
        border: 1px solid #2c3874;
        border-radius: 12px;
        padding: .85rem 1rem;
        margin-bottom: .9rem;
        background: rgba(13, 18, 37, .86);
        animation: fadeRise .5s ease-out both;
    }
    .confidence-wrap {
        margin-top: .35rem;
    }
    .confidence-item {
        margin-bottom: .7rem;
    }
    .confidence-head {
        display: flex;
        justify-content: space-between;
        font-size: .86rem;
        color: #cfe3ff;
        margin-bottom: .25rem;
    }
    .confidence-track {
        width: 100%;
        height: 12px;
        border-radius: 999px;
        background: rgba(26, 38, 79, 0.9);
        border: 1px solid #31499a;
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        width: 0%;
        border-radius: 999px;
        background: linear-gradient(90deg, #32a2ff, #6c8bff, #74c6ff);
        box-shadow: 0 0 12px rgba(88, 170, 255, .45);
        animation: fillBar 1.6s ease-out forwards;
    }
    .confidence-fill.top-confidence {
        box-shadow: 0 0 16px rgba(101, 208, 255, .8);
        animation: fillBar 1.7s ease-out forwards, softPulse 2.5s ease-in-out infinite 1.7s;
    }
    .metric-card {
        border: 1px solid #3f52b1;
        border-radius: 12px;
        padding: 0.95rem;
        background: linear-gradient(145deg, rgba(24,38,102,0.88), rgba(12,16,32,0.95));
        box-shadow: 0 0 15px rgba(83, 129, 255, 0.22);
        text-align: center;
        min-height: 112px;
        transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
        animation: fadeRise .45s ease-out both;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #79a1ff;
        box-shadow: 0 0 24px rgba(96, 157, 255, 0.34);
    }
    .reveal-1 { animation-delay: 0.08s; }
    .reveal-2 { animation-delay: 0.18s; }
    .reveal-3 { animation-delay: 0.28s; }
    .reveal-4 { animation-delay: 0.38s; }
    .rank-badge {
        border: 1px solid #5a71d7;
        border-radius: 14px;
        padding: 0.8rem 0.95rem;
        margin-bottom: 0.8rem;
        background: linear-gradient(140deg, rgba(40, 48, 111, 0.9), rgba(15, 21, 43, 0.96));
        box-shadow: 0 0 18px rgba(104, 126, 255, 0.25);
        animation: fadeRise .4s ease-out both;
    }
    .rank-label {
        color: #9cd2ff;
        font-size: .84rem;
    }
    .rank-value {
        font-size: 1.2rem;
        font-weight: 800;
        color: #fff;
    }
    .winner-card {
        border: 1px solid #4a67cf;
        border-radius: 12px;
        padding: .75rem .85rem;
        background: rgba(18, 25, 51, 0.88);
    }
    .winner-title {
        color: #9ad7ff;
        font-size: .85rem;
        margin-bottom: .25rem;
    }
    .winner-value {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .metric-title { color: #9ad7ff; font-size: 0.9rem; }
    .metric-value { color: #ffffff; font-size: 1.45rem; font-weight: 700; }
    .status-banner {
        border-radius: 12px;
        padding: .65rem .9rem;
        border: 1px solid #2e5a9c;
        background: linear-gradient(120deg, rgba(23,60,105,.7), rgba(13,27,46,.85));
        color: #c3e5ff;
        margin-bottom: .75rem;
        animation: softPulse 2.8s ease-in-out infinite;
    }
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #4d67dd;
        color: #f5f8ff;
        font-weight: 700;
        background: linear-gradient(95deg, #3154dd, #6b3df0);
        box-shadow: 0 0 18px rgba(92, 97, 255, .28);
    }
    .stButton > button:hover {
        border: 1px solid #7f96ff;
        box-shadow: 0 0 20px rgba(116, 167, 255, .34);
    }
    @keyframes titleFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    @keyframes caret {
        50% { border-color: transparent; }
    }
    @keyframes pulseText {
        0%,100% { opacity: .7; }
        50% { opacity: 1; text-shadow: 0 0 10px rgba(117, 255, 208, .35); }
    }
    @keyframes floatChip {
        0%,100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    @keyframes fadeRise {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fillBar {
        from { width: 0%; }
        to { width: var(--target); }
    }
    @keyframes softPulse {
        0%,100% { box-shadow: 0 0 0 rgba(70, 166, 255, 0.0); }
        50% { box-shadow: 0 0 18px rgba(70, 166, 255, 0.26); }
    }
    @keyframes sweep {
        0% { transform: translateX(-120%); }
        100% { transform: translateX(130%); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🎮 GameScope AI</h1>
        <p class="typewriter">Predict success, profit potential, and market alignment before your launch.</p>
        <div class="live-text">● LIVE ANALYTICS CORE ACTIVE</div>
        <div class="chip-row">
            <span class="chip">ML Battle-Tested</span>
            <span class="chip">What-If Simulator</span>
            <span class="chip">Steam Trend Aware</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "predictor" not in st.session_state:
    st.session_state.predictor = None
if "last_run" not in st.session_state:
    st.session_state.last_run = None

if st.session_state.predictor is None:
    try:
        with st.spinner("Preparing model artifacts (first run only)..."):
            ensure_artifacts()
        st.session_state.predictor = GameScopePredictor()
    except FileNotFoundError:
        st.error("Model artifacts are unavailable. Run `python train_model.py` and retry.")
        st.stop()

predictor = st.session_state.predictor

with st.sidebar:
    st.header("⚙️ Build Your Game Concept")
    st.caption("Tune assumptions and run what-if analysis.")
    preset = st.selectbox(
        "🎮 Concept Preset",
        ["Custom", "Indie Story Adventure", "Hardcore Souls-like", "Co-op Survival Crafter", "Competitive Arena"],
        index=0,
    )

    with st.expander("🎯 Core Profile", expanded=True):
        preset_defaults = {
            "Custom": ("My Next Indie Hit", "An atmospheric adventure with tactical combat."),
            "Indie Story Adventure": ("Echoes of Auroria", "A narrative-driven indie adventure with emotional branching choices."),
            "Hardcore Souls-like": ("Ashen Oath", "A punishing action RPG with precision combat and layered boss encounters."),
            "Co-op Survival Crafter": ("Frontier Foundry", "A co-op survival crafting game focused on base-building and long-term progression."),
            "Competitive Arena": ("Neon Clash Arena", "A fast-paced competitive arena with ranked ladder progression."),
        }
        default_name, default_desc = preset_defaults[preset]
        name = st.text_input("Game Name", value=default_name)
        release_period = st.selectbox(
            "Planned Release Window",
            ["Q1 2027", "Q2 2027", "Q3 2027", "Q4 2027", "2028+"],
            index=1,
        )
        release_map = {
            "Q1 2027": "Feb 15, 2027",
            "Q2 2027": "May 15, 2027",
            "Q3 2027": "Aug 15, 2027",
            "Q4 2027": "Nov 15, 2027",
            "2028+": "Jun 15, 2028",
        }
        release_date = release_map[release_period]
        developer = st.selectbox(
            "Developer Profile",
            ["Indie Studio", "Mid-size Studio", "AAA Studio", "Solo Developer"],
            index=0,
        )
        publisher = st.selectbox(
            "Publishing Model",
            ["Self Published", "Indie Publisher", "Global Publisher"],
            index=0,
        )
        short_description = st.text_area(
            "Short Description",
            value=default_desc,
        )

    with st.expander("💸 Market Setup", expanded=True):
        price_usd = st.number_input("Price (USD)", min_value=0.0, max_value=100.0, value=19.99, step=0.5)
        is_free = st.checkbox("Free to Play", value=False)
        selected_genres = st.multiselect(
            "Select Genres",
            ["Action", "Adventure", "RPG", "Strategy", "Simulation", "Casual", "Racing", "Sports", "Horror", "Indie"],
            default=["Action", "Adventure"],
        )
        selected_categories = st.multiselect(
            "Select Categories",
            ["Single-player", "Multi-player", "Co-op", "Online Co-op", "PvP", "Controller Support", "Steam Achievements"],
            default=["Single-player"],
        )
        selected_tags = st.multiselect(
            "Select Tags",
            [
                "Indie",
                "Story Rich",
                "Open World",
                "Survival",
                "Roguelike",
                "Souls-like",
                "Competitive",
                "Tactical",
                "Fantasy",
                "Sci-fi",
            ],
            default=["Indie", "Story Rich"],
        )
        custom_tags = st.text_input("Optional extra tags (comma-separated)", value="")
        genres = ", ".join(selected_genres) if selected_genres else "Action"
        categories = ", ".join(selected_categories) if selected_categories else "Single-player"
        all_tags = selected_tags + [t.strip() for t in custom_tags.split(",") if t.strip()]
        tags = ", ".join(all_tags) if all_tags else "Indie"

    with st.expander("🕹️ Platforms + Signals", expanded=True):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            platforms_win = st.checkbox("Windows", value=True)
        with col_p2:
            platforms_mac = st.checkbox("Mac", value=False)
        with col_p3:
            platforms_linux = st.checkbox("Linux", value=False)

        metacritic_score = st.slider("Expected Metacritic", 0, 100, 75)
        recommendations = st.number_input("Expected Recommendations", min_value=0, value=1000)
        positive_reviews = st.number_input("Expected Positive Reviews", min_value=0, value=2000)
        negative_reviews = st.number_input("Expected Negative Reviews", min_value=0, value=300)
        avg_playtime_forever = st.number_input("Expected Avg Playtime (minutes)", min_value=0, value=500)
        peak_ccu = st.number_input("Expected Peak CCU", min_value=0, value=1500)
        required_age = st.number_input("Required Age", min_value=0, max_value=21, value=0)
        dlc_count = st.number_input("Planned DLC Count", min_value=0, value=1)
        achievements = st.number_input("Achievement Count", min_value=0, value=25)

submitted = st.button("🚀 Run Prediction", use_container_width=True)

if submitted:
    payload = {
        "name": name,
        "release_date": release_date,
        "coming_soon": False,
        "price_usd": price_usd,
        "is_free": is_free,
        "developer": developer,
        "publisher": publisher,
        "genres": genres,
        "categories": categories,
        "tags": tags,
        "platforms_win": platforms_win,
        "platforms_mac": platforms_mac,
        "platforms_linux": platforms_linux,
        "metacritic_score": metacritic_score,
        "recommendations": recommendations,
        "positive_reviews": positive_reviews,
        "negative_reviews": negative_reviews,
        "estimated_owners": "0 .. 0",
        "avg_playtime_forever": avg_playtime_forever,
        "avg_playtime_2weeks": 0,
        "median_playtime": 0,
        "peak_ccu": peak_ccu,
        "required_age": required_age,
        "dlc_count": dlc_count,
        "achievements": achievements,
        "short_description": short_description,
    }
    progress = st.progress(0, text="Booting analysis engine...")
    for pct, msg in [(20, "Encoding concept..."), (45, "Running market simulation..."), (75, "Scoring launch viability..."), (100, "Finalizing recommendations...")]:
        time.sleep(0.08)
        progress.progress(pct, text=msg)
    prediction = predictor.predict(payload)
    insights = predictor.recommend(payload, prediction)
    progress.empty()
    previous = st.session_state.last_run
    st.session_state.last_run = {
        "payload": payload,
        "prediction": prediction,
        "insights": insights,
    }
    st.markdown(
        """
        <div class="game-feed">
            <b>Mission Feed:</b> Scanning market signals, balancing risk profile, and simulating launch viability...
        </div>
        """,
        unsafe_allow_html=True,
    )
    success_rank = {"Low Success": 1, "Medium Success": 2, "High Success": 3}
    score = success_rank.get(prediction["success_level"], 2) / 3
    confidence_max = max(prediction["success_confidence"].values())
    if score >= 0.95 and confidence_max >= 0.6:
        rank = "🏆 LEGEND"
    elif score >= 0.75:
        rank = "🥇 PLATINUM"
    elif score >= 0.55:
        rank = "🥈 GOLD"
    elif score >= 0.35:
        rank = "🥉 SILVER"
    else:
        rank = "🪨 BRONZE"
    st.markdown(
        f"""
        <div class="status-banner">
            Matchmaking Score: <b>{(score * 100):.0f}/100</b> | 
            Build: <b>{prediction["success_level"]}</b> | 
            Trend Sync: <b>{insights["trend_alignment"]}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="rank-badge reveal-1">
            <div class="rank-label">Competitive Launch Tier</div>
            <div class="rank-value">{rank}  |  Confidence Peak: {confidence_max:.1%}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card reveal-2">
                <div class="metric-title">Predicted Success</div>
                <div class="metric-value">{prediction["success_level"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card reveal-3">
                <div class="metric-title">Estimated Profit Potential</div>
                <div class="metric-value">${prediction["estimated_profit_usd"]:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card reveal-4">
                <div class="metric-title">Market Trend Alignment</div>
                <div class="metric-value">{insights["trend_alignment"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Confidence", "🧠 Recommendations", "⚡ Opportunities", "⚠️ Risks", "🆚 Delta"]
    )

    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Confidence Breakdown")
        confidence_rows = []
        ordered_conf = sorted(prediction["success_confidence"].items(), key=lambda x: x[1], reverse=True)
        for idx, (label, confidence) in enumerate(ordered_conf):
            fill_class = "confidence-fill top-confidence" if idx == 0 else "confidence-fill"
            confidence_rows.append(
                (
                    '<div class="confidence-item">'
                    '<div class="confidence-head">'
                    f"<span>{label}</span>"
                    f"<span>{confidence:.1%}</span>"
                    "</div>"
                    '<div class="confidence-track">'
                    f'<div class="{fill_class}" style="--target:{confidence * 100:.1f}%; animation-delay:{0.12 * idx:.2f}s;"></div>'
                    "</div>"
                    "</div>"
                )
            )
        st.markdown(f'<div class="confidence-wrap">{"".join(confidence_rows)}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Actionable Recommendations")
        for idx, item in enumerate(insights["recommendations"], start=1):
            st.write(f"{idx}. {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Opportunity Signals")
        if insights.get("opportunities"):
            for item in insights["opportunities"]:
                st.write(f"- {item}")
        else:
            st.write("- No strong upside signals detected yet. Try tuning tags, price, or platform strategy.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Risk Factors")
        if insights["risk_factors"]:
            for risk in insights["risk_factors"]:
                st.write(f"- {risk}")
        else:
            st.success("No major risk flags detected for the current concept.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Delta vs Previous Run")
        if previous:
            prev_pred = previous["prediction"]
            delta_profit = prediction["estimated_profit_usd"] - prev_pred["estimated_profit_usd"]
            left, right = st.columns(2)
            with left:
                st.markdown(
                    f"""
                    <div class="winner-card">
                        <div class="winner-title">Previous Scenario</div>
                        <div class="winner-value">{prev_pred['success_level']}</div>
                        <div>Profit: ${prev_pred['estimated_profit_usd']:,.0f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with right:
                st.markdown(
                    f"""
                    <div class="winner-card">
                        <div class="winner-title">Current Scenario</div>
                        <div class="winner-value">{prediction['success_level']}</div>
                        <div>Profit: ${prediction['estimated_profit_usd']:,.0f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            winner = "Current Scenario 👑" if delta_profit >= 0 else "Previous Scenario 👑"
            st.write(f"- Winner: **{winner}**")
            st.write(f"- Profit Delta: **${delta_profit:,.0f}**")
        else:
            st.write("- Run a second scenario to see side-by-side delta analysis.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🎛️ Strategic Levers")
    lev1, lev2, lev3 = st.columns(3)
    lev1.metric("Price Position", f"${price_usd:.2f}")
    lev2.metric("Platform Breadth", f"{int(platforms_win) + int(platforms_mac) + int(platforms_linux)} / 3")
    lev3.metric("Review Health", f"{(positive_reviews / max(positive_reviews + negative_reviews, 1)):.1%}")
    st.caption("Use these levers for quick what-if runs. Small changes here can move success class boundaries.")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.subheader("🧪 Model Snapshot")
metadata_path = ROOT / "artifacts" / "metadata.json"
if metadata_path.exists():
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    c1, c2, c3 = st.columns(3)
    c1.info(f"Training rows: {metadata['training_rows']}")
    c2.success(f"Classification accuracy: {metadata['metrics']['classification_accuracy']:.3f}")
    c3.warning(f"Profit R² (log-space): {metadata['metrics']['profit_r2_log']:.3f}")
