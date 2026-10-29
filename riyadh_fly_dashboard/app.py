"""
Riyadh Fly — RUH Flight Records Analytics
King Khalid International Airport · Q2 & Q3 2025 history · Q4 2025 forecast

Run with:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
DATA_FILE = Path(__file__).parent / "riyadh_fly_cleaned.csv"

# Historical quarters (computed from the dataset)
QUARTERS = {
    "Q2 2025": {"months": [4, 5, 6], "range": "Apr — Jun 2025"},
    "Q3 2025": {"months": [7, 8, 9], "range": "Jul — Sep 2025"},
}
# Forecast quarter (static results supplied from the project notebook)
FORECAST_Q = "Q4 2025"
FORECAST_RANGE = "Oct — Dec 2025"
QUARTER_OPTIONS = list(QUARTERS) + [FORECAST_Q]

VIEWS = {
    "monthly": {"code": "A1", "label": "Monthly Flight Records"},
    "destinations": {"code": "B2", "label": "Top 5 Destinations"},
    "airlines": {"code": "C3", "label": "Most Active Airlines"},
    "hours": {"code": "D4", "label": "Busiest Hours"},
}
FORECAST_VIEWS = {
    "monthly": {"code": "F1", "label": "Monthly Flight Forecast"},
    "destinations": {"code": "F2", "label": "Predicted Top 5 Destinations"},
    "airlines": {"code": "F3", "label": "Predicted Top 10 Airlines"},
    "hours": {"code": "F4", "label": "Predicted Busiest Hours"},
}


# Terminal palette: warm stone, ink, brushed brass, slate
STONE = "#F6F4EF"
PAPER = "#FFFFFF"
INK = "#121A26"
INK_SOFT = "#3A4454"
MUTED = "#8A8F98"
HAIRLINE = "#E5E1D8"
BRASS = "#A8834A"
BRASS_LIGHT = "#D9C7A6"
BRASS_WASH = "#F3EDE2"
SLATE = "#5B7086"
SLATE_LIGHT = "#C9D2DC"
GRID = "#EEEBE4"
TYPE_COLORS = {"Departure": INK, "Arrival": BRASS_LIGHT}

FONT_UI = "Manrope, Helvetica Neue, Arial, sans-serif"
FONT_MONO = "JetBrains Mono, SFMono-Regular, Menlo, monospace"

st.set_page_config(
    page_title="Riyadh Fly",
    page_icon=str(Path(__file__).parent / "favicon.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ─────────────────────────────────────────────────────────────
# Icons (stroke SVGs used as CSS masks so they inherit colour)
# ─────────────────────────────────────────────────────────────
def _svg(path: str) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'>"
        f"{path}</svg>"
    )
    return "url(\"data:image/svg+xml;utf8," + svg.replace("<", "%3C").replace(">", "%3E").replace("#", "%23") + "\")"


ICONS = [
    # calendar
    _svg("<rect x='3.5' y='5' width='17' height='15' rx='1.5'/><path d='M3.5 9.5h17M8 3v4M16 3v4'/>"
         "<path d='M8 13.5h2M14 13.5h2M8 16.5h2'/>"),
    # map pin / destination
    _svg("<path d='M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z'/><circle cx='12' cy='10' r='2.3'/>"),
    # airplane
    _svg("<path d='M12 2c.8 0 1.3.9 1.3 2v5.2l7.7 4.6v1.9l-7.7-2.3v4.6l2.2 1.7v1.5L12 20.2 8.5 21.2v-1.5l2.2-1.7v-4.6L3 15.7v-1.9l7.7-4.6V4c0-1.1.5-2 1.3-2z' stroke-width='1.3'/>"),
    # clock
    _svg("<circle cx='12' cy='12' r='8.5'/><path d='M12 7.5V12l3 2'/>"),
]
RAIL_ICONS = [
    # dashboard grid
    _svg("<rect x='3.5' y='3.5' width='7' height='7' rx='1'/><rect x='13.5' y='3.5' width='7' height='4.5' rx='1'/>"
         "<rect x='13.5' y='11' width='7' height='9.5' rx='1'/><rect x='3.5' y='13.5' width='7' height='7' rx='1'/>"),
    # dataset / table
    _svg("<ellipse cx='12' cy='5.5' rx='7.5' ry='2.5'/><path d='M4.5 5.5v13c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5v-13'/>"
         "<path d='M4.5 12c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5'/>"),
]

PLANE_FILL = ("url(\"data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E"
              "%3Cpath fill='black' d='" + ICONS[2].split("d='")[1].split("'")[0] + "'/%3E%3C/svg%3E\")")


# ─────────────────────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────────────────────
def inject_css() -> None:
    icon_rules = "\n".join(
        f".st-key-nav [data-testid='stRadioGroup'] > div:nth-child({i + 1}) [data-testid='stRadioOption']::before "
        f"{{ -webkit-mask-image: {uri}; mask-image: {uri}; }}"
        for i, uri in enumerate(ICONS)
    ) + "\n" + "\n".join(
        f".st-key-menu [data-testid='stRadioGroup'] > div:nth-child({i + 1}) [data-testid='stRadioOption']::before "
        f"{{ -webkit-mask-image: {uri}; mask-image: {uri}; }}"
        for i, uri in enumerate(RAIL_ICONS)
    )
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, .stApp, [class*="css"], .stMarkdown, label, input, button, p {{ font-family: {FONT_UI}; }}
        .stApp {{ background: {STONE}; color: {INK}; }}

        /* Strip Streamlit chrome (no Streamlit sidebar — the panel is part of the layout) */
        header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
        [data-testid="stExpandSidebarButton"], #MainMenu, footer, [data-testid="stDecoration"],
        [data-testid="stToolbar"], [data-testid="stStatusWidget"] {{ display: none !important; }}
        .block-container {{ padding: 28px 36px 56px !important; max-width: 1560px; }}
        [data-testid="stVerticalBlock"] {{ gap: 0.9rem; }}
        [data-testid="stElementContainer"]:has(.marker) {{ display: none; }}

        @keyframes rise {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}

        /* ── App shell: fixed-width left panel + main area ── */
        [data-testid="stColumn"]:has(.st-key-rail) {{
            flex: 0 0 284px !important; width: 284px !important; min-width: 284px !important;
            position: sticky; top: 28px; align-self: flex-start;
        }}
        [data-testid="stColumn"]:has(.st-key-main) {{ flex: 1 1 0 !important; width: auto !important; min-width: 0 !important; }}
        .st-key-main {{ container-type: inline-size; container-name: main; }}

        /* ── Left panel ─────────────────────────────────── */
        .st-key-rail {{
            background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; padding: 26px 22px 24px;
            gap: 0.75rem;
        }}
        .brand {{ display: flex; align-items: center; gap: 14px; }}
        .brand-mark {{
            width: 42px; height: 42px; border-radius: 3px; background: {INK}; flex: 0 0 auto;
            display: grid; place-items: center;
        }}
        .brand-mark span {{
            width: 21px; height: 21px; background: {BRASS_LIGHT};
            -webkit-mask-image: {PLANE_FILL}; mask-image: {PLANE_FILL};
            -webkit-mask-size: contain; mask-size: contain; transform: rotate(45deg);
        }}
        .brand-name {{
            font-size: 1rem; font-weight: 700; letter-spacing: 0.3em; text-transform: uppercase; color: {INK}; line-height: 1.1;
        }}
        .brand-sub {{
            font-family: {FONT_MONO}; font-size: 0.62rem; letter-spacing: 0.12em; color: {MUTED};
            text-transform: uppercase; margin-top: 5px;
        }}
        .rail-rule {{ height: 1px; background: {HAIRLINE}; margin: 8px 0 2px; }}
        .rail-head {{
            display: flex; align-items: center; gap: 10px; margin: 10px 0 0;
            font-family: {FONT_MONO}; font-size: 0.64rem; letter-spacing: 0.22em; text-transform: uppercase; color: {MUTED};
        }}
        .rail-head::before {{ content: ""; width: 18px; height: 1px; background: {BRASS}; }}
        .rail-head .scope {{
            margin-left: auto; padding: 2px 7px; border: 1px solid {HAIRLINE}; border-radius: 2px;
            font-size: 0.58rem; letter-spacing: 0.14em; color: {MUTED};
        }}
        .st-key-rail label p {{
            font-family: {FONT_MONO}; font-size: 0.64rem !important; letter-spacing: 0.16em; text-transform: uppercase;
            color: {MUTED};
        }}
        .st-key-rail [data-testid="stMultiSelect"]:has(input:disabled) {{ opacity: 0.45; }}

        /* Panel menu */
        .st-key-menu [data-testid="stRadioGroup"] {{ display: flex !important; flex-direction: column; gap: 4px; width: 100%; }}
        .st-key-menu [data-testid="stElementContainer"], .st-key-menu [data-testid="stRadio"] {{ width: 100% !important; }}
        .st-key-menu [data-testid="stRadioGroup"] > div {{ margin: 0 !important; width: 100%; }}
        .st-key-menu [data-testid="stRadioOption"] {{
            position: relative; width: 100%; margin: 0 !important; padding: 11px 12px 11px 44px; border-radius: 3px;
            cursor: pointer; transition: background .2s ease;
        }}
        .st-key-menu [data-testid="stRadioOption"] > div > div:first-child {{ display: none !important; }}
        .st-key-menu [data-testid="stRadioOption"]::before {{
            content: ""; position: absolute; left: 13px; top: 50%; width: 19px; height: 19px; margin-top: -9.5px;
            background: {MUTED}; -webkit-mask-size: contain; mask-size: contain;
            -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
        }}
        .st-key-menu [data-testid="stRadioOption"]::after {{
            content: ""; position: absolute; left: 0; top: 8px; bottom: 8px; width: 2px; background: {BRASS};
            transform: scaleY(0); transition: transform .25s ease;
        }}
        .st-key-menu [data-testid="stRadioOption"] p {{
            font-family: {FONT_UI} !important; font-size: 0.92rem !important; font-weight: 500;
            letter-spacing: 0 !important; text-transform: none !important; color: {INK_SOFT}; margin: 0;
        }}
        .st-key-menu [data-testid="stRadioOption"]:hover {{ background: {STONE}; }}
        .st-key-menu [data-testid="stRadioOption"][data-selected="true"] {{ background: {STONE}; }}
        .st-key-menu [data-testid="stRadioOption"][data-selected="true"]::after {{ transform: scaleY(1); }}
        .st-key-menu [data-testid="stRadioOption"][data-selected="true"]::before {{ background: {INK}; }}
        .st-key-menu [data-testid="stRadioOption"][data-selected="true"] p {{ color: {INK}; font-weight: 600; }}

        [data-testid="stMultiSelectTagsContainer"] [data-tag] {{
            background: {STONE} !important; border: 1px solid {HAIRLINE} !important; border-radius: 3px !important;
        }}
        [data-testid="stMultiSelectTagsContainer"] [data-tag] span {{ color: {INK} !important; font-weight: 500; }}
        [data-testid="stMultiSelectTagsContainer"] [data-tag] button {{ color: {MUTED} !important; }}

        /* ── Top bar ───────────────────────────────────── */
        .st-key-topbar {{ padding-bottom: 20px; border-bottom: 1px solid {HAIRLINE}; }}
        .page-tag {{
            font-family: {FONT_MONO}; font-size: 0.66rem; letter-spacing: 0.24em; text-transform: uppercase; color: {BRASS};
        }}
        .page-title {{ font-size: 2rem; font-weight: 500; letter-spacing: -0.02em; color: {INK}; margin-top: 8px; line-height: 1.1; }}

        /* Quarter selector — prominent tiles */
        .st-key-quarter {{ align-items: flex-end; }}
        .st-key-quarter .q-label {{
            display: flex; align-items: center; gap: 10px; justify-content: flex-end;
            font-family: {FONT_MONO}; font-size: 0.66rem; letter-spacing: 0.24em; text-transform: uppercase;
            color: {MUTED}; margin-bottom: 2px;
        }}
        .st-key-quarter .q-label::before {{ content: ""; width: 18px; height: 1px; background: {BRASS}; }}
        .st-key-quarter [data-testid="stElementContainer"] {{ align-self: flex-end; width: auto !important; }}
        .st-key-quarter [data-testid="stRadioGroup"] {{
            display: grid !important; grid-template-columns: repeat(3, 1fr); gap: 10px;
        }}
        .st-key-quarter [data-testid="stRadioGroup"] > div {{ margin: 0 !important; }}
        .st-key-quarter [data-testid="stRadioOption"] {{
            position: relative; overflow: hidden; margin: 0 !important; min-width: 170px; height: 100%;
            padding: 14px 20px 16px; cursor: pointer; border: 1px solid {HAIRLINE}; border-radius: 4px;
            background: {PAPER}; transition: background .25s ease, border-color .25s ease, box-shadow .25s ease;
        }}
        .st-key-quarter [data-testid="stRadioOption"]::after {{
            content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: {BRASS_LIGHT};
            transform: scaleX(0); transform-origin: left; transition: transform .3s ease;
        }}
        .st-key-quarter [data-testid="stRadioOption"]:hover {{ border-color: {INK}; }}
        .st-key-quarter [data-testid="stRadioOption"] > div > div:first-child {{ display: none !important; }}
        .st-key-quarter [data-testid="stRadioOption"] p {{
            font-size: 1.4rem !important; font-weight: 500; letter-spacing: -0.01em; line-height: 1.1;
            color: {INK}; margin: 0; white-space: nowrap;
        }}
        .st-key-quarter [data-testid="stRadioOption"] p code {{
            display: block; background: none; padding: 0; margin-bottom: 6px;
            font-family: {FONT_MONO}; font-size: 0.62rem; font-weight: 500; letter-spacing: 0.18em; color: {MUTED};
        }}
        .st-key-quarter [data-testid="stRadioOption"][data-selected="true"] {{
            background: {INK}; border-color: {INK}; box-shadow: 0 14px 30px -18px rgba(18,26,38,0.75);
        }}
        .st-key-quarter [data-testid="stRadioOption"][data-selected="true"]::after {{ transform: scaleX(1); }}
        .st-key-quarter [data-testid="stRadioOption"][data-selected="true"] p {{ color: {PAPER} !important; }}
        .st-key-quarter [data-testid="stRadioOption"][data-selected="true"] p code {{ color: {BRASS_LIGHT}; }}
        /* Q4 forecast tile */
        .st-key-quarter [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"] {{
            border-style: dashed; border-color: {BRASS_LIGHT}; background: {BRASS_WASH};
        }}
        .st-key-quarter [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"] p code {{ visibility: hidden; }}
        .st-key-quarter [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"]::before {{
            content: "FORECAST"; position: absolute; top: 11px; left: 20px; padding: 2px 6px; border-radius: 2px;
            font-family: {FONT_MONO}; font-size: 0.54rem; letter-spacing: 0.16em; color: {BRASS};
            border: 1px solid {BRASS_LIGHT};
        }}
        .st-key-quarter [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"][data-selected="true"] {{
            background: {INK}; border-style: solid; border-color: {BRASS};
        }}
        .st-key-quarter [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"][data-selected="true"]::before {{
            background: {BRASS}; color: {INK}; border-color: {BRASS};
        }}

        /* ── Wayfinding navigation ─────────────────────── */
        .st-key-nav {{ margin-top: 6px; background: {INK}; border-radius: 4px; padding: 0; overflow: hidden; }}
        .st-key-nav [data-testid="stHorizontalBlock"] {{ gap: 0 !important; align-items: stretch; }}
        .st-key-nav [data-testid="stColumn"]:first-child {{
            border-right: 1px solid rgba(255,255,255,0.12); padding: 20px 22px;
            display: flex; flex-direction: column; justify-content: center;
        }}
        .nav-airport {{ font-family: {FONT_MONO}; color: {BRASS_LIGHT}; font-size: 2rem; font-weight: 500;
                        letter-spacing: 0.08em; line-height: 1; }}
        .nav-airport-name {{ color: rgba(255,255,255,0.62); font-size: 0.66rem; letter-spacing: 0.16em;
                             text-transform: uppercase; margin-top: 8px; line-height: 1.6; }}
        .nav-badge {{
            display: inline-block; margin-top: 12px; padding: 3px 8px; border-radius: 2px; width: fit-content;
            background: {BRASS}; color: {INK}; font-family: {FONT_MONO}; font-size: 0.58rem; letter-spacing: 0.2em;
        }}
        .st-key-nav [data-testid="stElementContainer"]:has([data-testid="stRadio"]),
        .st-key-nav [data-testid="stRadio"] {{ width: 100% !important; }}
        .st-key-nav [data-testid="stRadio"] > div {{ width: 100%; }}
        .st-key-nav [data-testid="stRadioGroup"] {{
            display: grid !important; grid-template-columns: repeat(4, 1fr); gap: 0; width: 100%; height: 100%;
        }}
        .st-key-nav [data-testid="stRadioGroup"] > div {{ margin: 0 !important; width: 100%; }}
        .st-key-nav [data-testid="stRadioGroup"] > div + div [data-testid="stRadioOption"] {{
            border-left: 1px solid rgba(255,255,255,0.08);
        }}
        .st-key-nav [data-testid="stRadioOption"] {{
            position: relative; width: 100%; height: 100%; margin: 0 !important;
            padding: 22px 16px 22px 56px; cursor: pointer; align-items: center; transition: background .25s ease;
        }}
        .st-key-nav [data-testid="stRadioOption"]::before {{
            content: ""; position: absolute; left: 20px; top: 50%; width: 22px; height: 22px; margin-top: -11px;
            background: rgba(255,255,255,0.55); -webkit-mask-size: contain; mask-size: contain;
            -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat; transition: background .25s ease;
        }}
        .st-key-nav [data-testid="stRadioOption"]::after {{
            content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 3px;
            background: {BRASS_LIGHT}; transform: scaleX(0); transform-origin: left; transition: transform .3s ease;
        }}
        {icon_rules}
        .st-key-nav [data-testid="stRadioOption"] > div > div:first-child {{ display: none !important; }}
        .st-key-nav [data-testid="stRadioOption"] p {{
            color: rgba(255,255,255,0.62); font-size: 0.88rem !important; font-weight: 500; margin: 0; line-height: 1.3;
            text-wrap: balance; transition: color .25s ease;
        }}
        .st-key-nav [data-testid="stRadioOption"] p code {{
            display: block; background: none; padding: 0; margin-bottom: 4px;
            font-family: {FONT_MONO}; font-size: 0.66rem; letter-spacing: 0.2em; color: rgba(255,255,255,0.38);
        }}
        .st-key-nav [data-testid="stRadioOption"]:hover {{ background: rgba(255,255,255,0.04); }}
        .st-key-nav [data-testid="stRadioOption"]:hover p {{ color: #fff; }}
        .st-key-nav [data-testid="stRadioOption"][data-selected="true"] {{ background: rgba(255,255,255,0.07); }}
        .st-key-nav [data-testid="stRadioOption"][data-selected="true"]::after {{ transform: scaleX(1); }}
        .st-key-nav [data-testid="stRadioOption"][data-selected="true"]::before {{ background: {BRASS_LIGHT}; }}
        .st-key-nav [data-testid="stRadioOption"][data-selected="true"] p {{ color: #fff !important; font-weight: 600; }}
        .st-key-nav [data-testid="stRadioOption"][data-selected="true"] p code {{ color: {BRASS_LIGHT}; }}
        /* forecast mode: brass rail on the nav */
        .st-key-main:has(.mode-forecast) .st-key-nav {{ box-shadow: inset 0 3px 0 {BRASS}; }}
        .st-key-main:has(.mode-forecast) .st-key-nav [data-testid="stRadioOption"] p code {{ color: {BRASS}; }}

        /* Forecast ribbon */
        .fc-ribbon {{
            display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
            padding: 12px 18px; border: 1px dashed {BRASS_LIGHT}; border-radius: 4px; background: {BRASS_WASH};
            font-size: 0.86rem; color: {INK_SOFT};
        }}
        .fc-ribbon .badge, .badge {{
            padding: 3px 8px; border-radius: 2px; background: {BRASS}; color: {PAPER};
            font-family: {FONT_MONO}; font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase;
        }}
        .fc-ribbon b {{ color: {INK}; font-weight: 600; }}

        /* ── KPI strip ─────────────────────────────────── */
        .kpis {{
            display: grid; grid-template-columns: repeat(4, 1fr);
            border-top: 1px solid {HAIRLINE}; border-bottom: 1px solid {HAIRLINE}; margin: 4px 0 6px;
        }}
        .kpis.five {{ grid-template-columns: repeat(5, 1fr); }}
        .kpi {{ padding: 20px 24px; min-width: 0; }}
        .kpi + .kpi {{ border-left: 1px solid {HAIRLINE}; }}
        .kpi .label {{
            font-family: {FONT_MONO}; font-size: 0.64rem; letter-spacing: 0.2em; text-transform: uppercase; color: {MUTED};
        }}
        .kpi .value {{
            font-size: 2.1rem; font-weight: 300; letter-spacing: -0.02em; color: {INK}; margin-top: 8px; line-height: 1.05;
            font-variant-numeric: tabular-nums;
        }}
        .kpi .value.small {{ font-size: 1.45rem; }}
        .kpi .value.accent {{ color: {BRASS}; }}
        .kpis.forecast .value {{ color: {INK}; }}
        .kpis.forecast {{ border-top-style: dashed; border-bottom-style: dashed; border-color: {BRASS_LIGHT}; }}
        .kpis.forecast .kpi + .kpi {{ border-left-color: {BRASS_LIGHT}; border-left-style: dashed; }}

        /* ── Chart stage ───────────────────────────────── */
        .st-key-stage {{
            background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; padding: 30px 32px 10px;
            animation: rise .45s ease both;
        }}
        .st-key-main:has(.mode-forecast) .st-key-stage {{ border-top: 3px solid {BRASS}; }}
        .stage-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 16px;
                       padding-bottom: 6px; flex-wrap: wrap; }}
        .stage-code {{ display: flex; align-items: center; gap: 10px;
                       font-family: {FONT_MONO}; font-size: 0.7rem; letter-spacing: 0.22em; color: {BRASS}; }}
        .stage-title {{ font-size: 1.75rem; font-weight: 500; letter-spacing: -0.015em; color: {INK}; margin-top: 6px; }}
        .stage-meta {{ font-family: {FONT_MONO}; font-size: 0.7rem; letter-spacing: 0.16em; color: {MUTED};
                       text-transform: uppercase; }}

        /* ── Analysis (historical) ─────────────────────── */
        .analysis {{
            display: grid; grid-template-columns: 1fr 1.35fr; background: {PAPER};
            border: 1px solid {HAIRLINE}; border-radius: 4px; animation: rise .55s ease both;
        }}
        .analysis > div {{ padding: 26px 32px; }}
        .analysis > div + div {{ border-left: 1px solid {HAIRLINE}; }}
        .tag {{
            display: flex; align-items: center; gap: 10px;
            font-family: {FONT_MONO}; font-size: 0.66rem; letter-spacing: 0.2em; text-transform: uppercase; color: {MUTED};
        }}
        .tag::before {{ content: ""; width: 18px; height: 1px; background: {BRASS}; }}
        .analysis .q {{ font-size: 1.15rem; font-weight: 500; color: {INK}; line-height: 1.45; margin-top: 12px; }}
        .analysis .i {{ font-size: 0.98rem; color: {INK_SOFT}; line-height: 1.65; margin-top: 12px; }}
        .analysis .i b {{ color: {INK}; font-weight: 600; }}

        /* ── Prediction methodology (forecast) ─────────── */
        .method {{
            background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; animation: rise .55s ease both;
        }}
        .method-head {{
            display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
            padding: 22px 32px; border-bottom: 1px solid {HAIRLINE};
        }}
        .method-head .title {{ font-size: 1.15rem; font-weight: 600; color: {INK}; }}
        .method-kind {{
            font-family: {FONT_MONO}; font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase;
            padding: 4px 9px; border-radius: 2px; border: 1px solid {BRASS_LIGHT}; color: {BRASS};
        }}
        .method-kind.ml {{ background: {INK}; border-color: {INK}; color: {BRASS_LIGHT}; }}
        .method-body {{ display: grid; grid-template-columns: 1fr 1.5fr; }}
        .method-body > div {{ padding: 24px 32px 26px; }}
        .method-body > div + div {{ border-left: 1px solid {HAIRLINE}; }}
        .method-body.single {{ grid-template-columns: 1fr; }}
        .method-body.single .method-text {{ max-width: 980px; }}
        .method-name {{ font-size: 1.05rem; font-weight: 600; color: {INK}; margin: 12px 0 14px; }}
        .spec {{ display: grid; grid-template-columns: 96px 1fr; gap: 12px; padding: 9px 0; margin: 0;
                 border-top: 1px solid {GRID}; }}
        .spec dt {{ font-family: {FONT_MONO}; font-size: 0.62rem; letter-spacing: 0.16em; text-transform: uppercase;
                    color: {MUTED}; padding-top: 2px; }}
        .spec dd {{ margin: 0; font-size: 0.88rem; color: {INK}; }}
        .method-text {{ font-size: 0.98rem; color: {INK_SOFT}; line-height: 1.7; margin-top: 12px; }}

        /* ── Dataset page ──────────────────────────────── */
        .st-key-dshead {{ padding-bottom: 20px; border-bottom: 1px solid {HAIRLINE}; }}
        .st-key-back button {{
            border: 1px solid {INK} !important; border-radius: 3px !important; background: {PAPER} !important;
            color: {INK} !important; padding: 10px 18px !important; min-height: 0 !important; transition: all .2s ease;
        }}
        .st-key-back button:hover {{ background: {INK} !important; color: {PAPER} !important; }}
        .st-key-back button p {{ font-family: {FONT_MONO}; font-size: 0.74rem !important; letter-spacing: 0.14em;
                                 text-transform: uppercase; }}
        .st-key-back {{ align-items: flex-end; }}
        .ds-grid {{ display: grid; grid-template-columns: 1.25fr 1fr; gap: 14px; animation: rise .45s ease both; }}
        .ds-col {{ display: grid; gap: 14px; align-content: start; }}
        .ds-grid.single {{ grid-template-columns: 1fr; }}
        .card {{ background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; padding: 24px 28px; }}
        .card .lead {{ font-size: 0.96rem; color: {INK_SOFT}; line-height: 1.7; margin-top: 12px; }}
        .card .lead b {{ color: {INK}; font-weight: 600; }}
        .fields {{ width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 0.86rem; }}
        .fields th {{ text-align: left; font-family: {FONT_MONO}; font-size: 0.6rem; letter-spacing: 0.16em; font-weight: 500;
                      text-transform: uppercase; color: {MUTED}; padding: 8px 10px 8px 0; border-bottom: 1px solid {HAIRLINE}; }}
        .fields td {{ padding: 9px 10px 9px 0; border-bottom: 1px solid {GRID}; color: {INK_SOFT}; vertical-align: top; }}
        .fields td:first-child {{ font-family: {FONT_MONO}; font-size: 0.78rem; color: {INK}; white-space: nowrap; width: 240px; }}
        .fields td.num {{ text-align: right; font-variant-numeric: tabular-nums; color: {INK}; }}
        .checks {{ list-style: none; padding: 0; margin: 14px 0 0; }}
        .checks li {{ display: flex; gap: 12px; padding: 9px 0; border-top: 1px solid {GRID}; font-size: 0.9rem; color: {INK_SOFT}; }}
        .checks li::before {{
            content: ""; flex: 0 0 14px; height: 14px; margin-top: 3px; border-radius: 50%;
            border: 1px solid {BRASS}; background: radial-gradient(circle, {BRASS} 0 3px, transparent 3.5px);
        }}
        .checks li b {{ color: {INK}; font-weight: 600; }}
        .checks li > span {{ flex: 1; }}
        .fields, .fields th, .fields td {{ border-left: none !important; border-right: none !important; }}
        .fields {{ border: none !important; }}
        .fields th {{ border-top: none !important; background: none !important; }}
        .fields tr {{ background: none !important; }}
        .src {{ margin-top: 14px; }}
        .st-key-preview {{
            background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; padding: 24px 28px 20px;
            animation: rise .55s ease both;
        }}

        .empty {{
            background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; padding: 80px 20px;
            text-align: center; font-family: {FONT_MONO}; font-size: 0.75rem; letter-spacing: 0.2em;
            text-transform: uppercase; color: {MUTED};
        }}

        /* ── Responsive (main area width) ──────────────── */
        @container main (max-width: 1000px) {{
            .st-key-quarter [data-testid="stRadioOption"] {{ min-width: 0; padding: 12px 14px 14px; }}
            .st-key-quarter [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"]::before {{
                top: 9px; left: 14px;
            }}
            .st-key-quarter [data-testid="stRadioOption"] p {{ font-size: 1.2rem !important; }}
            .st-key-nav [data-testid="stColumn"]:first-child {{ padding: 18px; }}
            .nav-airport-name {{ letter-spacing: 0.1em; font-size: 0.62rem; }}
            .st-key-nav [data-testid="stRadioGroup"] {{ grid-template-columns: repeat(2, 1fr); }}
            .st-key-nav [data-testid="stRadioGroup"] > div:nth-child(n+3) [data-testid="stRadioOption"] {{
                border-top: 1px solid rgba(255,255,255,0.08);
            }}
            .st-key-nav [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"] {{ border-left: none; }}
            .kpis.five {{ grid-template-columns: repeat(3, 1fr); }}
            .kpis.five .kpi:nth-child(4) {{ border-left: none; }}
            .kpis.five .kpi:nth-child(n+4) {{ border-top: 1px solid {HAIRLINE}; }}
            .ds-grid {{ grid-template-columns: 1fr; }}
        }}
        @container main (max-width: 760px) {{
            .st-key-topbar [data-testid="stHorizontalBlock"], .st-key-dshead [data-testid="stHorizontalBlock"],
            .st-key-nav [data-testid="stHorizontalBlock"] {{ flex-direction: column; flex-wrap: nowrap; }}
            .st-key-topbar [data-testid="stColumn"], .st-key-dshead [data-testid="stColumn"],
            .st-key-nav [data-testid="stColumn"] {{ width: 100% !important; flex: 1 1 auto !important; min-width: 100%; }}
            .st-key-topbar [data-testid="stHorizontalBlock"] {{ gap: 18px; }}
            .page-title {{ font-size: 1.6rem; }}
            .st-key-quarter [data-testid="stElementContainer"],
            .st-key-quarter [data-testid="stRadio"] {{ align-self: stretch; width: 100% !important; }}
            .st-key-quarter {{ align-items: stretch; }}
            .st-key-quarter .q-label {{ justify-content: flex-start; }}
            .st-key-quarter [data-testid="stRadioGroup"] {{ width: 100%; gap: 8px; }}
            .st-key-quarter [data-testid="stRadioGroup"] > div {{ width: 100%; }}
            .st-key-quarter [data-testid="stRadioOption"] {{ width: 100%; padding: 12px 12px 13px; }}
            .st-key-quarter [data-testid="stRadioOption"] p {{ font-size: 1.05rem !important; }}
            .st-key-quarter [data-testid="stRadioOption"] p code {{ font-size: 0.55rem; letter-spacing: 0.08em; }}
            .st-key-quarter [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"]::before {{
                top: 8px; left: 12px; font-size: 0.5rem;
            }}
            .st-key-back {{ align-items: stretch; }}
            .st-key-nav [data-testid="stColumn"]:first-child {{ border-right: none;
                border-bottom: 1px solid rgba(255,255,255,0.12); padding: 16px 18px; }}
            .st-key-nav [data-testid="stRadioOption"] {{ padding: 16px 12px 16px 50px; }}
            .st-key-nav [data-testid="stRadioOption"]::before {{ left: 16px; width: 20px; height: 20px; margin-top: -10px; }}
            .st-key-nav [data-testid="stRadioOption"] p {{ font-size: 0.8rem !important; }}
            .kpis, .kpis.five {{ grid-template-columns: repeat(2, 1fr); }}
            .kpi {{ padding: 16px; }}
            .kpi:nth-child(odd) {{ border-left: none !important; }}
            .kpi:nth-child(even) {{ border-left: 1px solid {HAIRLINE}; }}
            .kpi:nth-child(n+3) {{ border-top: 1px solid {HAIRLINE}; }}
            .kpi .value {{ font-size: 1.6rem; }}
            .kpi .value.small {{ font-size: 1.2rem; }}
            .st-key-stage {{ padding: 20px 14px 6px; }}
            .stage-title {{ font-size: 1.3rem; }}
            .analysis, .method-body {{ grid-template-columns: 1fr; }}
            .analysis > div, .method-body > div, .method-head {{ padding: 20px; }}
            .analysis > div + div, .method-body > div + div {{ border-left: none; border-top: 1px solid {HAIRLINE}; }}
            .card, .st-key-preview {{ padding: 20px; }}
        }}
        @media (max-width: 1100px) {{ .block-container {{ padding: 24px 24px 48px !important; }} }}
        @media (max-width: 900px) {{
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-rail) {{
                flex-direction: column; flex-wrap: nowrap; gap: 16px;
            }}
            [data-testid="stColumn"]:has(.st-key-rail) {{
                position: static; flex: 1 1 auto !important; width: 100% !important; min-width: 100% !important;
            }}
            [data-testid="stColumn"]:has(.st-key-main) {{ width: 100% !important; min-width: 100% !important; }}
            .st-key-rail {{ padding: 20px; }}
            .st-key-menu [data-testid="stRadioGroup"] {{ flex-direction: row; }}
            .st-key-menu [data-testid="stRadioGroup"] > div {{ flex: 1; }}
        }}
        @media (max-width: 760px) {{ .block-container {{ padding: 16px 14px 40px !important; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# Data (unchanged logic)
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """Load the cleaned dataset and derive only the fields the dashboard needs."""
    df = pd.read_csv(path)

    for col in ["airline_name", "flight_type", "destination_airport"]:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    df["flight_type"] = df["flight_type"].str.capitalize()  # departure → Departure

    df["scheduled_date"] = pd.to_datetime(df["scheduled_date"], errors="coerce")
    times = pd.to_datetime(df["scheduled_time"], format="%H:%M:%S", errors="coerce")
    df["scheduled_hour"] = times.dt.hour

    df = df.dropna(subset=["scheduled_date", "scheduled_hour"])
    df["scheduled_hour"] = df["scheduled_hour"].astype(int)
    df["month_num"] = df["scheduled_date"].dt.month
    df["month"] = df["scheduled_date"].dt.strftime("%B")
    return df


@st.cache_data(show_spinner=False)
def load_preview(path: Path, n: int = 6) -> pd.DataFrame:
    """First rows of the cleaned CSV, with its original column names, for the sidebar preview."""
    preview = pd.read_csv(path, nrows=n)
    preview.columns = [c.replace("_", " ").title() for c in preview.columns]
    return preview


def filter_quarter(df: pd.DataFrame, quarter: str) -> pd.DataFrame:
    """Restrict to the quarter's months in 2025 only."""
    months = QUARTERS[quarter]["months"]
    mask = (df["scheduled_date"].dt.year == 2025) & (df["month_num"].isin(months))
    return df.loc[mask]


def apply_filters(df, flight_types, airlines, destinations) -> pd.DataFrame:
    out = df[df["flight_type"].isin(flight_types)]
    if airlines:
        out = out[out["airline_name"].isin(airlines)]
    if destinations:
        out = out[out["destination_airport"].isin(destinations)]
    return out


def other_quarter(quarter: str) -> str:
    return next(q for q in QUARTERS if q != quarter)


# ─────────────────────────────────────────────────────────────
# Charts (count = number of scheduled flight records)
# ─────────────────────────────────────────────────────────────
CHART_HEIGHT = 500


def base_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=8, r=48, t=36, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_UI, size=13, color=INK_SOFT),
        hoverlabel=dict(bgcolor=INK, bordercolor=INK, font=dict(family=FONT_UI, color="#FFFFFF", size=13)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None,
                    font=dict(size=12, color=INK_SOFT)),
        bargap=0.35,
        transition=dict(duration=400, easing="cubic-in-out"),
    )
    axis = dict(gridcolor=GRID, zeroline=False, linecolor=HAIRLINE, tickfont=dict(color=MUTED, size=12),
                title_font=dict(color=MUTED, size=11, family=FONT_MONO))
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    return fig


def chart_monthly(df: pd.DataFrame, quarter: str) -> go.Figure:
    months = QUARTERS[quarter]["months"]
    names = [pd.Timestamp(2025, m, 1).strftime("%B") for m in months]
    counts = df.groupby("month_num").size().reindex(months, fill_value=0)

    colors = [SLATE_LIGHT] * len(counts)
    if counts.max() > 0:
        colors[int(counts.values.argmax())] = INK
    fig = go.Figure(go.Bar(
        x=names, y=counts.values, width=0.42,
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:,}" for v in counts.values], textposition="outside", cliponaxis=False,
        textfont=dict(color=INK, size=16, family=FONT_UI),
        hovertemplate="<b>%{x}</b><br>%{y:,} flight records<extra></extra>",
    ))
    fig = base_layout(fig)
    fig.update_yaxes(title="FLIGHT RECORDS", range=[0, max(counts.max(), 1) * 1.15])
    fig.update_xaxes(showgrid=False, tickfont=dict(color=INK, size=14))
    return fig


def chart_top_destinations(df: pd.DataFrame, n: int = 5) -> go.Figure:
    top = df["destination_airport"].value_counts().head(n).index.tolist()
    data = (
        df[df["destination_airport"].isin(top)]
        .groupby(["destination_airport", "flight_type"]).size().reset_index(name="records")
    )
    totals = data.groupby("destination_airport")["records"].sum()
    order = totals.sort_values(ascending=True).index.tolist()  # highest at top

    fig = px.bar(
        data, y="destination_airport", x="records", color="flight_type", orientation="h",
        color_discrete_map=TYPE_COLORS,
        category_orders={"destination_airport": order[::-1], "flight_type": ["Departure", "Arrival"]},
        custom_data=["flight_type"],
    )
    fig.update_traces(marker=dict(line=dict(width=0)),
                      hovertemplate="<b>%{y}</b> · %{customdata[0]}<br>%{x:,} flight records<extra></extra>")
    fig.add_trace(go.Scatter(
        y=order, x=totals[order].values, mode="text",
        text=[f"   {v:,}" for v in totals[order].values], textposition="middle right",
        showlegend=False, hoverinfo="skip", textfont=dict(size=15, color=INK, family=FONT_UI),
    ))
    fig = base_layout(fig)
    fig.update_layout(barmode="stack", bargap=0.45)
    fig.update_yaxes(title=None, showgrid=False, categoryorder="array", categoryarray=order,
                     tickfont=dict(color=INK, size=14))
    fig.update_xaxes(title="FLIGHT RECORDS", range=[0, max(totals.max(), 1) * 1.18])
    return fig


def chart_airlines(df: pd.DataFrame, n: int = 10) -> go.Figure:
    counts = df["airline_name"].value_counts().head(n).sort_values(ascending=True)
    colors = [SLATE_LIGHT] * len(counts)
    if len(counts):
        colors[-1] = INK  # most active airline highlighted
    fig = go.Figure(go.Bar(
        y=counts.index, x=counts.values, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:,}" for v in counts.values], textposition="outside", cliponaxis=False,
        textfont=dict(color=INK, size=13, family=FONT_UI),
        hovertemplate="<b>%{y}</b><br>%{x:,} flight records<extra></extra>",
    ))
    fig = base_layout(fig)
    fig.update_layout(bargap=0.4)
    fig.update_yaxes(title=None, showgrid=False, tickfont=dict(color=INK, size=13))
    fig.update_xaxes(title="FLIGHT RECORDS",
                     range=[0, max(counts.max() if len(counts) else 1, 1) * 1.15])
    return fig


def chart_hours(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby("scheduled_hour").size().reindex(range(24), fill_value=0)
    peak = int(counts.idxmax()) if counts.max() > 0 else None
    quiet = int(counts.idxmin())
    avg = counts.mean()

    colors = []
    for h, v in counts.items():
        if h == peak:
            colors.append(BRASS)
        elif v >= avg:
            colors.append(INK)
        else:
            colors.append(SLATE_LIGHT)

    labels = [f"{h:02d}:00" for h in range(24)]
    fig = go.Figure(go.Bar(
        x=labels, y=counts.values, marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{y:,} flight records<extra></extra>",
    ))
    fig.add_hline(y=avg, line_dash="dot", line_color=MUTED, line_width=1,
                  annotation_text=f"AVG {avg:,.0f}", annotation_position="top left",
                  annotation_font=dict(size=11, color=MUTED, family=FONT_MONO),
                  annotation_bgcolor="rgba(255,255,255,0.9)")
    if peak is not None:
        fig.add_annotation(x=labels[peak], y=counts[peak], text=f"PEAK {labels[peak]}",
                           showarrow=True, arrowhead=0, arrowcolor=BRASS, ay=-30,
                           font=dict(color=BRASS, size=12, family=FONT_MONO))
        fig.add_annotation(x=labels[quiet], y=counts[quiet], text=f"QUIETEST {labels[quiet]}",
                           showarrow=True, arrowhead=0, arrowcolor=MUTED, ay=-40,
                           font=dict(color=INK_SOFT, size=11, family=FONT_MONO),
                           bgcolor="rgba(255,255,255,0.9)")
    fig = base_layout(fig)
    fig.update_layout(bargap=0.25)
    fig.update_yaxes(title="FLIGHT RECORDS", range=[0, max(counts.max(), 1) * 1.2])
    fig.update_xaxes(title=None, showgrid=False, tickangle=0, tickvals=labels[::2], ticktext=labels[::2])
    return fig


# ─────────────────────────────────────────────────────────────
# Analytical questions & data-driven insights
# ─────────────────────────────────────────────────────────────
def pct(a: float, b: float) -> float:
    return (a / b * 100) if b else 0.0


def signed(p: float) -> str:
    return f"{p:+.1f}%"


def insight_monthly(view: pd.DataFrame, comp: pd.DataFrame, quarter: str) -> tuple[str, str]:
    q = "How did scheduled flight volume evolve across the three months of the quarter?"
    months = QUARTERS[quarter]["months"]
    counts = view.groupby("month_num").size().reindex(months, fill_value=0)
    name = {m: pd.Timestamp(2025, m, 1).strftime("%B") for m in months}
    hi, lo = int(counts.idxmax()), int(counts.idxmin())
    parts = [f"<b>{name[hi]}</b> was the busiest month with <b>{counts[hi]:,}</b> records"]
    if hi != lo and counts[lo] > 0:
        parts[0] += f", <b>{pct(counts[hi] - counts[lo], counts[lo]):.1f}%</b> more than {name[lo]} ({counts[lo]:,})"
    parts[0] += "."
    if len(comp):
        oq = other_quarter(quarter)
        diff = pct(len(view) - len(comp), len(comp))
        parts.append(f"Total quarterly volume is <b>{signed(diff)}</b> against {oq} ({len(comp):,} records).")
    return q, " ".join(parts)


def insight_destinations(view: pd.DataFrame, comp: pd.DataFrame, quarter: str) -> tuple[str, str]:
    q = "Which destinations dominate RUH's schedule, and how concentrated is traffic among them?"
    vc = view["destination_airport"].value_counts()
    top, top_n = vc.index[0], int(vc.iloc[0])
    share5 = pct(vc.head(5).sum(), len(view))
    parts = [f"<b>{top}</b> leads with <b>{top_n:,}</b> records"]
    if len(vc) > 1:
        parts[0] += f", <b>{top_n / vc.iloc[1]:.1f}×</b> the second-ranked {vc.index[1]}"
    parts[0] += "."
    if len(vc) > 5:
        parts.append(f"The top five account for <b>{share5:.1f}%</b> of all {len(view):,} records in view.")
    if len(comp):
        oq = other_quarter(quarter)
        comp_top = comp["destination_airport"].value_counts().index[0]
        parts.append(f"{oq}'s leader was {'also ' + comp_top if comp_top == top else comp_top}.")
    return q, " ".join(parts)


def insight_airlines(view: pd.DataFrame, comp: pd.DataFrame, quarter: str) -> tuple[str, str]:
    q = "How concentrated is airline activity — do a few carriers drive most of the schedule?"
    vc = view["airline_name"].value_counts()
    top, top_n = vc.index[0], int(vc.iloc[0])
    if len(vc) == 1:
        text = f"Only <b>{top}</b> appears in the current selection, with <b>{top_n:,}</b> records."
    else:
        parts = [f"<b>{top}</b> holds <b>{pct(top_n, len(view)):.1f}%</b> of records."]
        if len(vc) >= 3:
            names = ", ".join(vc.index[:3][:-1]) + " and " + vc.index[2]
            parts.append(f"Together, {names} account for <b>{pct(vc.head(3).sum(), len(view)):.1f}%</b> "
                         f"of all records in view.")
        if len(comp):
            comp_n = int((comp["airline_name"] == top).sum())
            if comp_n:
                parts.append(f"{top}'s volume is <b>{signed(pct(top_n - comp_n, comp_n))}</b> "
                             f"against {other_quarter(quarter)}.")
        text = " ".join(parts)
    return q, text


def insight_hours(view: pd.DataFrame, comp: pd.DataFrame, quarter: str) -> tuple[str, str]:
    q = "At what times of day is the schedule busiest, and when does activity drop off?"
    counts = view.groupby("scheduled_hour").size().reindex(range(24), fill_value=0)
    peak, quiet = int(counts.idxmax()), int(counts.idxmin())
    # busiest consecutive three-hour block (within the day)
    block = counts.rolling(3).sum().shift(-2).dropna()
    b0 = int(block.idxmax())
    parts = [f"Activity peaks at <b>{peak:02d}:00</b> with <b>{counts[peak]:,}</b> records"]
    if counts[quiet] > 0:
        parts[0] += f" — <b>{counts[peak] / counts[quiet]:.1f}×</b> the quietest hour, {quiet:02d}:00"
    else:
        parts[0] += f"; {quiet:02d}:00 has no records"
    parts[0] += "."
    parts.append(f"The busiest three-hour block, <b>{b0:02d}:00–{b0 + 2:02d}:59</b>, carries "
                 f"<b>{pct(block[b0], len(view)):.1f}%</b> of the day's records.")
    if len(comp):
        cp = int(comp.groupby("scheduled_hour").size().idxmax())
        oq = other_quarter(quarter)
        parts.append(f"{oq} also peaked at {cp:02d}:00." if cp == peak else f"{oq} peaked at {cp:02d}:00.")
    return q, " ".join(parts)


CHARTS = {
    "monthly": lambda v, q: chart_monthly(v, q),
    "destinations": lambda v, q: chart_top_destinations(v),
    "airlines": lambda v, q: chart_airlines(v),
    "hours": lambda v, q: chart_hours(v),
}
INSIGHTS = {
    "monthly": insight_monthly,
    "destinations": insight_destinations,
    "airlines": insight_airlines,
    "hours": insight_hours,
}




# ─────────────────────────────────────────────────────────────
# Q4 2025 forecast — exact results supplied from the project notebook (static, not recalculated)
# ─────────────────────────────────────────────────────────────
FORECAST_MONTHLY = {"October": 23144, "November": 22413, "December": 23155}

FORECAST_DESTINATIONS = {
    "Jeddah": 12197, "Dubai": 5481, "Cairo": 4434, "Abha": 4057, "Ad Dammam": 3283,
}

FORECAST_AIRLINES = {
    "Saudi Arabian": 27053, "flynas": 15073, "flyadeal": 11051, "Gulf Air": 971, "flydubai": 906,
    "EgyptAir": 845, "Qatar": 793, "Etihad": 692, "Emirates": 596, "Turkish": 566,
}

FORECAST_HOURS = [
    2586, 1953, 2307, 1515, 2100, 1936, 2692, 2451, 2777, 3030, 3151, 2992,
    2446, 2729, 2980, 3063, 3563, 3274, 3475, 3518, 3788, 3419, 3420, 3454,
]  # index = scheduled hour 00:00 … 23:00

METHODOLOGY = {
    "monthly": {
        "kind": "Machine learning", "ml": True, "name": "Random Forest Regressor",
        "specs": [("Target", "Daily flight counts"), ("Features", "Day · weekday · month"),
                  ("Training", "Q2 – Q3 2025"), ("Validation", "Last 30 days"),
                  ("Output", "Daily Q4 forecast, summed by month")],
        "text": "A Random Forest Regressor was trained on daily flight counts from Q2 and Q3, using time-based "
                "features — day, weekday and month. It was evaluated on the last 30 days, then retrained on all "
                "available data to predict daily flight counts for Q4, which were aggregated by month.",
    },
    "destinations": {
        "kind": "Historical average", "ml": False, "name": "Average daily flights × 92 days",
        "specs": [("Base", "Q2 – Q3 2025 counts per destination"), ("Period", "183 days (Apr 1 – Sep 30)"),
                  ("Horizon", "92 days (Oct 1 – Dec 31)")],
        "text": "Each destination's flight count across Q2 and Q3 was divided by the number of days in the "
                "historical period to give its average daily flights. That average was multiplied by the 92 days "
                "of Q4 to estimate the quarter's total. This is an average-based estimate, not a machine-learning "
                "prediction.",
    },
    "airlines": {
        "kind": "Historical average", "ml": False, "name": "Average daily flights × 92 days",
        "specs": [("Base", "Q2 – Q3 2025 counts per airline"), ("Period", "183 days (Apr 1 – Sep 30)"),
                  ("Horizon", "92 days (Oct 1 – Dec 31)")],
        "text": "The same historical-average method was applied to each airline: its Q2 and Q3 flight count was "
                "converted to an average daily figure and scaled to the 92 days of Q4. This is an average-based "
                "estimate, not a machine-learning prediction.",
    },
    "hours": {
        "kind": "Machine learning", "ml": True, "name": "Random Forest Regressor",
        "specs": [("Target", "Flight counts per date and hour"),
                  ("Features", "Hour · weekday · month · day of year"),
                  ("Training", "Q2 – Q3 2025"), ("Validation", "Last 30 days"),
                  ("Output", "Hourly Q4 forecast, summed by hour")],
        "text": "A Random Forest Regressor was trained on flight counts grouped by date and hour, using hour, "
                "weekday, month and day of year as features. It was evaluated on the last 30 days, retrained on all "
                "available data, and used to predict hourly flight counts throughout Q4. The predictions were then "
                "summed for each hour of the day across the quarter.",
    },
}


# ─────────────────────────────────────────────────────────────
# Forecast charts (hatched bars = predicted values)
# ─────────────────────────────────────────────────────────────
FC_FILL = "#F1EADC"


def forecast_marker(n: int, highlight: list[int]) -> dict:
    return dict(
        color=[BRASS if i in highlight else FC_FILL for i in range(n)],
        line=dict(color=[BRASS if i in highlight else BRASS_LIGHT for i in range(n)], width=1),
        pattern=dict(shape=["" if i in highlight else "/" for i in range(n)],
                     fgcolor=BRASS_LIGHT, size=7, solidity=0.25),
    )


def chart_fc_monthly() -> go.Figure:
    months, values = list(FORECAST_MONTHLY), list(FORECAST_MONTHLY.values())
    top = values.index(max(values))
    fig = go.Figure(go.Bar(
        x=months, y=values, width=0.42, marker=forecast_marker(3, [top]),
        text=[f"{v:,}" for v in values], textposition="outside", cliponaxis=False,
        textfont=dict(color=INK, size=16, family=FONT_UI),
        hovertemplate="<b>%{x} 2025</b><br>%{y:,} predicted flights<extra></extra>",
    ))
    fig = base_layout(fig)
    fig.update_yaxes(title="PREDICTED FLIGHTS", range=[0, max(values) * 1.15])
    fig.update_xaxes(showgrid=False, tickfont=dict(color=INK, size=14))
    return fig


def chart_fc_ranked(data: dict, label: str) -> go.Figure:
    items = sorted(data.items(), key=lambda kv: kv[1])  # ascending → highest drawn at top
    names, values = [k for k, _ in items], [v for _, v in items]
    fig = go.Figure(go.Bar(
        y=names, x=values, orientation="h", marker=forecast_marker(len(values), [len(values) - 1]),
        text=[f"{v:,}" for v in values], textposition="outside", cliponaxis=False,
        textfont=dict(color=INK, size=14 if len(values) <= 5 else 13, family=FONT_UI),
        hovertemplate="<b>%{y}</b><br>%{x:,} " + label + "<extra></extra>",
    ))
    fig = base_layout(fig)
    fig.update_layout(bargap=0.45 if len(values) <= 5 else 0.36)
    fig.update_yaxes(title=None, showgrid=False, tickfont=dict(color=INK, size=14 if len(values) <= 5 else 13))
    fig.update_xaxes(title="ESTIMATED FLIGHTS", range=[0, max(values) * 1.15])
    return fig


def chart_fc_hours() -> go.Figure:
    values = FORECAST_HOURS
    labels = [f"{h:02d}:00" for h in range(24)]
    peak, quiet = values.index(max(values)), values.index(min(values))
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker=forecast_marker(24, [peak]),
        hovertemplate="<b>%{x}</b><br>%{y:,} predicted flights<extra></extra>",
    ))
    fig.add_annotation(x=labels[peak], y=values[peak], text=f"PEAK {labels[peak]}",
                       showarrow=True, arrowhead=0, arrowcolor=BRASS, ay=-30,
                       font=dict(color=BRASS, size=12, family=FONT_MONO))
    fig.add_annotation(x=labels[quiet], y=values[quiet], text=f"QUIETEST {labels[quiet]}",
                       showarrow=True, arrowhead=0, arrowcolor=MUTED, ay=-40,
                       font=dict(color=INK_SOFT, size=11, family=FONT_MONO), bgcolor="rgba(255,255,255,0.9)")
    fig = base_layout(fig)
    fig.update_layout(bargap=0.25)
    fig.update_yaxes(title="PREDICTED FLIGHTS", range=[0, max(values) * 1.2])
    fig.update_xaxes(title=None, showgrid=False, tickangle=0, tickvals=labels[::2], ticktext=labels[::2])
    return fig


FORECAST_CHARTS = {
    "monthly": chart_fc_monthly,
    "destinations": lambda: chart_fc_ranked(FORECAST_DESTINATIONS, "estimated flights"),
    "airlines": lambda: chart_fc_ranked(FORECAST_AIRLINES, "estimated flights"),
    "hours": chart_fc_hours,
}


# ─────────────────────────────────────────────────────────────
# State helpers — keep selections when a widget is temporarily not shown
# ─────────────────────────────────────────────────────────────
def keep(key: str, default) -> None:
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get(f"_keep_{key}", default)


def save(*keys: str) -> None:
    for k in keys:
        if k in st.session_state:
            st.session_state[f"_keep_{k}"] = st.session_state[k]


def go_dashboard() -> None:
    st.session_state["page"] = "dashboard"


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────
def render_rail(hist: pd.DataFrame, filters_active: bool):
    with st.container(key="rail"):
        st.markdown(
            '<div class="brand"><div class="brand-mark"><span></span></div><div>'
            '<div class="brand-name">Riyadh Fly</div>'
            '<div class="brand-sub">Flight Records Analytics</div></div></div>'
            '<div class="rail-rule"></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="menu"):
            keep("page", "dashboard")
            page = st.radio("Page", ["dashboard", "dataset"], key="page", label_visibility="collapsed",
                            format_func=lambda p: "Dashboard" if p == "dashboard" else "Dataset Description")

        scope = "" if filters_active else '<span class="scope">Q2 · Q3 only</span>'
        st.markdown(f'<div class="rail-head">Filters{scope}</div>', unsafe_allow_html=True)

        type_options = sorted(hist["flight_type"].unique())
        airline_options = hist["airline_name"].value_counts().index.tolist()
        dest_options = hist["destination_airport"].value_counts().index.tolist()
        keep("f_types", type_options)
        keep("f_airlines", [])
        keep("f_dests", [])
        flight_types = st.multiselect("Flight type", type_options, key="f_types", disabled=not filters_active)
        airlines = st.multiselect("Airline", airline_options, key="f_airlines", placeholder="All airlines",
                                  disabled=not filters_active)
        destinations = st.multiselect("Destination", dest_options, key="f_dests", placeholder="All destinations",
                                      disabled=not filters_active)
        save("page", "f_types", "f_airlines", "f_dests")
    return page, flight_types, airlines, destinations


def render_topbar(quarter: str) -> str:
    forecast = quarter == FORECAST_Q
    with st.container(key="topbar"):
        left, right = st.columns([1, 1.65], vertical_alignment="bottom")
        with left:
            st.markdown(
                f'<div class="page-tag">RUH · {"Forecast" if forecast else "Historical Analysis"}</div>'
                f'<div class="page-title">{"Q4 2025 Outlook" if forecast else "Flight Records"}</div>',
                unsafe_allow_html=True,
            )
        with right:
            with st.container(key="quarter"):
                st.markdown('<div class="q-label">Reporting Quarter</div>', unsafe_allow_html=True)
                ranges = {**{q: QUARTERS[q]["range"] for q in QUARTERS}, FORECAST_Q: FORECAST_RANGE}
                quarter = st.radio(
                    "Quarter", QUARTER_OPTIONS, key="qsel", horizontal=True, label_visibility="collapsed",
                    format_func=lambda q: f"`{ranges[q].upper()}` {q.replace(' 2025', ' · 2025')}",
                )
    return quarter


def render_nav(forecast: bool) -> str:
    views = FORECAST_VIEWS if forecast else VIEWS
    with st.container(key="nav"):
        c1, c2 = st.columns([1, 5.2], gap=None)
        with c1:
            badge = '<div class="nav-badge">FORECAST</div>' if forecast else ""
            st.markdown(
                '<div class="nav-airport">RUH</div>'
                f'<div class="nav-airport-name">King Khalid International Airport</div>{badge}',
                unsafe_allow_html=True,
            )
        with c2:
            view = st.radio(
                "View", list(VIEWS), key="view", horizontal=True, label_visibility="collapsed",
                format_func=lambda k: f"`{views[k]['code']}` {views[k]['label']}",
            )
    return view


def kpi_strip(items: list[tuple[str, str, str]], extra_cls: str = "") -> None:
    cells = "".join(
        f'<div class="kpi"><div class="label">{label}</div><div class="value{cls}">{value}</div></div>'
        for label, value, cls in items
    )
    st.markdown(f'<div class="kpis {extra_cls}">{cells}</div>', unsafe_allow_html=True)


def render_kpis(df: pd.DataFrame) -> None:
    hours = df.groupby("scheduled_hour").size()
    kpi_strip([
        ("Flight Records", f"{len(df):,}", ""),
        ("Destinations", f"{df['destination_airport'].nunique():,}", ""),
        ("Active Airlines", f"{df['airline_name'].nunique():,}", ""),
        ("Busiest Hour", f"{int(hours.idxmax()):02d}:00", " accent"),
    ])


def stage_head(code: str, title: str, quarter: str, rng: str, forecast: bool = False) -> None:
    badge = '<span class="badge">Forecast</span>' if forecast else ""
    st.markdown(
        f'<div class="stage-head"><div><div class="stage-code">{code} · {quarter.upper()}{badge}</div>'
        f'<div class="stage-title">{title}</div></div>'
        f'<div class="stage-meta">{rng}</div></div>',
        unsafe_allow_html=True,
    )


def render_stage(view_key: str, view: pd.DataFrame, comp: pd.DataFrame, quarter: str) -> None:
    meta = VIEWS[view_key]
    with st.container(key="stage"):
        stage_head(meta["code"], meta["label"], quarter, QUARTERS[quarter]["range"])
        st.plotly_chart(CHARTS[view_key](view, quarter), width="stretch",
                        config={"displayModeBar": False, "responsive": True},
                        key=f"chart-{view_key}-{quarter}")

    question, insight = INSIGHTS[view_key](view, comp, quarter)
    st.markdown(
        f'<div class="analysis">'
        f'<div><div class="tag">Analytical Question</div><div class="q">{question}</div></div>'
        f'<div><div class="tag">Key Insight</div><div class="i">{insight}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_forecast(view_key: str) -> None:
    st.markdown('<div class="marker mode-forecast"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="fc-ribbon"><span class="badge">Forecast</span>'
        f'<span>Predicted values for <b>{FORECAST_RANGE}</b>, generated from Q2 – Q3 2025 records. '
        f'Not actual historical data.</span></div>',
        unsafe_allow_html=True,
    )
    meta, method = FORECAST_VIEWS[view_key], METHODOLOGY[view_key]
    with st.container(key="stage"):
        stage_head(meta["code"], meta["label"], FORECAST_Q, FORECAST_RANGE, forecast=True)
        st.plotly_chart(FORECAST_CHARTS[view_key](), width="stretch",
                        config={"displayModeBar": False, "responsive": True}, key=f"fc-{view_key}")

    st.markdown(
        f'<div class="method">'
        f'<div class="method-head"><span class="title">Prediction Methodology</span>'
        f'<span class="method-kind{" ml" if method["ml"] else ""}">{method["kind"]}</span></div>'
        f'<div class="method-body single">'
        f'<div><div class="tag">How it was generated</div><div class="method-text">{method["text"]}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


FIELD_NOTES = {
    "flight_number": "Flight identifier",
    "aircraft_model": "Scheduled aircraft type",
    "airline_name": "Operating airline",
    "flight_type": "Arrival or departure",
    "destination_airport": "Destination city as recorded",
    "scheduled_date": "Scheduled date (YYYY-MM-DD)",
    "scheduled_time": "Scheduled time (HH:MM:SS)",
}


@st.cache_data(show_spinner=False)
def dataset_profile(path: Path) -> dict:
    """Facts about the cleaned file, computed directly from it."""
    raw = pd.read_csv(path)
    dates = pd.to_datetime(raw["scheduled_date"], format="%Y-%m-%d", errors="coerce")
    times = pd.to_datetime(raw["scheduled_time"], format="%H:%M:%S", errors="coerce")
    return {
        "rows": len(raw), "cols": raw.shape[1], "columns": list(raw.columns),
        "distinct": raw.nunique().to_dict(),
        "missing": int(raw.isna().sum().sum()), "duplicates": int(raw.duplicated().sum()),
        "bad_dates": int(dates.isna().sum()), "bad_times": int(times.isna().sum()),
        "start": dates.min(), "end": dates.max(), "days": int(dates.nunique()),
        "types": sorted(raw["flight_type"].dropna().unique().tolist()),
        "airlines": int(raw["airline_name"].nunique()), "destinations": int(raw["destination_airport"].nunique()),
    }


def render_dataset_page() -> None:
    p = dataset_profile(DATA_FILE)
    with st.container(key="dshead"):
        left, right = st.columns([3, 1], vertical_alignment="bottom")
        with left:
            st.markdown('<div class="page-tag">RUH · Dataset</div><div class="page-title">Dataset Description</div>',
                        unsafe_allow_html=True)
        with right:
            with st.container(key="back"):
                st.button("←  Back to Dashboard", on_click=go_dashboard, key="back_btn")

    kpi_strip([
        ("Records", f"{p['rows']:,}", ""),
        ("Columns", f"{p['cols']}", ""),
        ("Coverage", f"{p['start']:%b} – {p['end']:%b %Y}", " small"),
        ("Airlines", f"{p['airlines']}", ""),
        ("Destinations", f"{p['destinations']}", ""),
    ], "five")

    rows = "".join(
        f'<tr><td>{c}</td><td>{FIELD_NOTES.get(c, "")}</td></tr>'
        for c in p["columns"]
    )
    st.markdown(
        f'<div class="ds-grid single">'
        f'<div class="ds-col"><div class="card"><div class="tag">Overview</div>'
        f'<div class="lead">Scheduled flight records for <b>King Khalid International Airport (RUH)</b>, Riyadh. '
        f'Each row is one scheduled arrival or departure, with its flight number, aircraft, airline, '
        f'destination and scheduled date and time. The dashboard analyses Q2 and Q3 2025 from these records; '
        f'the Q4 2025 section shows forecasts derived from them.</div>'
        f'<table class="fields"><thead><tr><th>Column</th><th>Description</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.container(key="preview"):
        st.markdown('<div class="tag">Sample Data</div>', unsafe_allow_html=True)
        st.dataframe(load_preview(DATA_FILE, 10), hide_index=True, width="stretch")


def render_dashboard(df: pd.DataFrame, quarter: str, flight_types, airlines, destinations) -> None:
    quarter = render_topbar(quarter)
    forecast = quarter == FORECAST_Q
    view_key = render_nav(forecast)
    save("qsel", "view")

    if forecast:
        render_forecast(view_key)
        return

    q_df = filter_quarter(df, quarter)
    view = apply_filters(q_df, flight_types, airlines, destinations)
    comp = apply_filters(filter_quarter(df, other_quarter(quarter)), flight_types, airlines, destinations)
    if view.empty:
        st.markdown('<div class="empty">No records match the selected filters</div>', unsafe_allow_html=True)
        return
    render_kpis(view)
    render_stage(view_key, view, comp, quarter)


def main() -> None:
    inject_css()

    if not DATA_FILE.exists():
        st.error(f"Dataset not found: `{DATA_FILE.name}`")
        st.stop()

    df = load_data(DATA_FILE)
    hist = pd.concat([filter_quarter(df, q) for q in QUARTERS])

    keep("qsel", QUARTER_OPTIONS[0])
    keep("view", "monthly")
    keep("page", "dashboard")
    on_dashboard = st.session_state["page"] == "dashboard"
    filters_active = on_dashboard and st.session_state["qsel"] != FORECAST_Q

    rail_col, main_col = st.columns([1, 4], gap="medium")
    with rail_col:
        page, flight_types, airlines, destinations = render_rail(hist, filters_active)
    with main_col:
        with st.container(key="main"):
            if page == "dataset":
                save("qsel", "view")
                render_dataset_page()
            else:
                render_dashboard(df, st.session_state["qsel"], flight_types, airlines, destinations)


if __name__ == "__main__":
    main()
