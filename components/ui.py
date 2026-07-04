from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from typing import Iterable, Union

import streamlit as st


APP_NAME = "Sports Analytics Dashboard"


def init_state() -> None:
    defaults = {
        "theme_mode": "Dark",
        "prediction_history": [],
        "latest_prediction": None,
        "global_search": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def page_config(title: str = APP_NAME) -> None:
    st.set_page_config(
        page_title=title,
        page_icon="SA",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def _asset_data_uri(path: str) -> str:
    asset = Path(path)
    if not asset.exists():
        return ""
    encoded = base64.b64encode(asset.read_bytes()).decode("ascii")
    suffix = asset.suffix.lower().replace(".", "")
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    return f"data:image/{mime};base64,{encoded}"


def inject_css() -> None:
    mode = st.session_state.get("theme_mode", "Dark")
    is_light = mode == "Light"
    bg = "#f7f8fc" if is_light else "#060810"
    panel = "rgba(255,255,255,.76)" if is_light else "rgba(13,18,33,.72)"
    panel_border = "rgba(24,30,54,.12)" if is_light else "rgba(255,255,255,.10)"
    text = "#111827" if is_light else "#f8fbff"
    muted = "#4b5563" if is_light else "#a8b3cf"
    shadow = "0 18px 55px rgba(31,41,55,.12)" if is_light else "0 20px 65px rgba(0,0,0,.34)"
    hero_uri = _asset_data_uri("assets/davinci_football_hero.png") or _asset_data_uri("assets/hero_pitch.png")
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {bg};
            --panel: {panel};
            --panel-border: {panel_border};
            --text: {text};
            --muted: {muted};
            --shadow: {shadow};
            --purple: #7c3aed;
            --blue: #38bdf8;
            --gold: #d6a84f;
            --green: #22c55e;
            --radius: 20px;
        }}
        html, body, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at 14% 6%, rgba(214,168,79,.14), transparent 30%),
                radial-gradient(circle at 86% 4%, rgba(56,189,248,.14), transparent 30%),
                linear-gradient(180deg, rgba(6,8,16,.98), var(--bg));
            color: var(--text);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(9,13,25,.98), rgba(13,19,34,.96));
            border-right: 1px solid rgba(214,168,79,.18);
        }}
        [data-testid="stSidebar"] * {{ color: #eef4ff; }}
        h1, h2, h3 {{ letter-spacing: 0; color: var(--text); }}
        p, li, label, span {{ color: inherit; }}
        .hero {{
            position: relative;
            min-height: 430px;
            border-radius: 28px;
            overflow: hidden;
            padding: 48px;
            background-image:
                linear-gradient(105deg, rgba(6,8,16,.98) 0%, rgba(13,18,33,.82) 48%, rgba(13,18,33,.18) 100%),
                url("{hero_uri}");
            background-size: cover;
            background-position: center right;
            box-shadow: var(--shadow);
            border: 1px solid rgba(214,168,79,.30);
        }}
        .hero h1 {{
            max-width: 870px;
            margin: 0;
            font-size: clamp(2.25rem, 5vw, 4.8rem);
            line-height: 1.02;
            color: #fff;
        }}
        .hero h1 span {{
            background: linear-gradient(90deg, #f8fafc, var(--gold) 42%, var(--blue));
            -webkit-background-clip: text;
            color: transparent;
        }}
        .hero p {{
            max-width: 710px;
            margin-top: 20px;
            color: #dbeafe;
            font-size: 1.08rem;
        }}
        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 9px 14px;
            margin-bottom: 22px;
            border-radius: 999px;
            color: #fff7df;
            background: rgba(214,168,79,.13);
            border: 1px solid rgba(214,168,79,.30);
            backdrop-filter: blur(14px);
        }}
        .glass-card {{
            padding: 22px;
            border-radius: var(--radius);
            background: var(--panel);
            border: 1px solid var(--panel-border);
            box-shadow: var(--shadow);
            backdrop-filter: blur(18px);
            transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
            height: 100%;
        }}
        .glass-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(214,168,79,.40);
            box-shadow: 0 24px 70px rgba(56,189,248,.10);
        }}
        .metric-card {{
            min-height: 126px;
            animation: riseIn .55s ease both;
        }}
        .metric-value {{
            font-size: 2.05rem;
            line-height: 1;
            font-weight: 800;
            background: linear-gradient(90deg, var(--gold), var(--blue));
            -webkit-background-clip: text;
            color: transparent;
        }}
        .metric-label {{ color: var(--muted); margin-top: 8px; }}
        .section-title {{
            margin: 24px 0 14px;
            font-size: 1.35rem;
            font-weight: 800;
        }}
        .chip {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin: 6px 7px 6px 0;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(214,168,79,.12);
            border: 1px solid rgba(214,168,79,.23);
            color: var(--text);
            font-size: .9rem;
        }}
        .footer {{
            margin-top: 42px;
            padding: 24px;
            border-radius: 18px;
            background: rgba(13,18,33,.78);
            border: 1px solid rgba(214,168,79,.18);
            color: #dbeafe;
            text-align: center;
        }}
        .floating-help {{
            position: fixed;
            right: 24px;
            bottom: 24px;
            z-index: 999;
            width: 52px;
            height: 52px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, var(--gold), var(--blue));
            color: #08111f;
            font-weight: 900;
            box-shadow: 0 15px 35px rgba(56,189,248,.28);
        }}
        .back-top {{
            position: fixed;
            right: 88px;
            bottom: 28px;
            z-index: 999;
            padding: 10px 13px;
            border-radius: 999px;
            background: rgba(255,255,255,.11);
            border: 1px solid rgba(255,255,255,.16);
            color: #fff;
            text-decoration: none;
        }}
        .stButton > button, .stDownloadButton > button {{
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,.12);
            background: linear-gradient(135deg, var(--purple), #0ea5e9);
            color: white;
            font-weight: 700;
            transition: transform .18s ease, filter .18s ease;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-2px);
            filter: brightness(1.08);
            border-color: rgba(214,168,79,.55);
        }}
        [data-testid="stDataFrame"] {{
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--panel-border);
        }}
        @keyframes riseIn {{
            from {{ opacity: 0; transform: translateY(14px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @media (max-width: 768px) {{
            .hero {{ min-height: 460px; padding: 28px; }}
            .hero h1 {{ font-size: 2.35rem; }}
            .glass-card {{ padding: 18px; }}
            .back-top {{ display: none; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_page_link(page: str, label: str, icon: str) -> None:
    try:
        st.page_link(page, label=label)
    except Exception:
        st.markdown(f"{escape(icon)} {escape(label)}")


def sidebar() -> None:
    with st.sidebar:
        st.image("assets/project_logo.png", width=102)
        st.markdown("### Sports Analytics")
        st.caption("Premier League analytics and tournament prediction.")
        st.session_state["global_search"] = st.text_input(
            "Global search",
            value=st.session_state.get("global_search", ""),
            placeholder="Search clubs, signals, pages",
        )
        st.session_state["theme_mode"] = st.radio(
            "Theme",
            ["Dark", "Light"],
            horizontal=True,
            index=0 if st.session_state.get("theme_mode") == "Dark" else 1,
        )
        st.divider()
        safe_page_link("app.py", "Home", "[H]")
        safe_page_link("pages/1_Dataset_Overview.py", "Dataset Overview", "[D]")
        safe_page_link("pages/2_Data_Visualization.py", "Data Visualization", "[V]")
        safe_page_link("pages/3_Team_Comparison.py", "Team Comparison", "[C]")
        safe_page_link("pages/4_Match_Prediction.py", "Match Prediction", "[M]")
        safe_page_link("pages/7_World_Cup_Prediction.py", "World Cup Prediction", "[W]")
        safe_page_link("pages/5_Model_Performance.py", "Model Performance", "[P]")
        safe_page_link("pages/6_About_Project.py", "About Project", "[A]")


def render_shell(title: str) -> None:
    page_config(title)
    init_state()
    inject_css()
    sidebar()
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)


def card(title: str, body: str, icon: str = "*") -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="chip">{escape(icon)} {escape(title)}</div>
            <p>{escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: Union[str, int, float], detail: str = "") -> None:
    st.markdown(
        f"""
        <div class="glass-card metric-card">
            <div class="metric-value">{escape(str(value))}</div>
            <div class="metric-label">{escape(label)}</div>
            <small>{escape(detail)}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)


def chips(items: Iterable[str]) -> None:
    html = "".join(f'<span class="chip">{escape(str(item))}</span>' for item in items)
    st.markdown(html, unsafe_allow_html=True)


def footer() -> None:
    st.markdown(
        """
        <a class="back-top" href="#top">Top</a>
        <div class="floating-help" title="Help">?</div>
        <div class="footer">
            Sports Analytics Dashboard and Match Outcome Prediction | University Capstone Project | Streamlit, Plotly, Scikit-learn
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_config(name: str) -> dict:
    return {
        "displaylogo": False,
        "responsive": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": name.lower().replace(" ", "_"),
            "height": 720,
            "width": 1100,
            "scale": 2,
        },
        "modeBarButtonsToAdd": ["drawline", "drawrect", "eraseshape"],
    }


def empty_state(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>{escape(title)}</h3>
            <p>{escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
