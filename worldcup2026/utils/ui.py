"""
utils/ui.py — FIFA World Cup 2026 — UI helpers, CSS, palette
v3.0 — Forced dark theme, dynamic top bar, profile settings, avatar SVG fixes
"""
import os
import base64
import streamlit as st
from datetime import datetime, date

# ── Colour tokens ──────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── FORCE DARK MODE regardless of OS / browser preference ── */
:root {
    color-scheme: dark !important;
    --primary:#E11D2E;
    --primary-dk:#B0121F;
    --primary-lt:#FF3B4D;
    --secondary:#F2C14E;
    --secondary-dk:#C99A1F;
    --bg:#0B0D11;
    --surface:#13161C;
    --surface2:#1A1E26;
    --surface3:#222732;
    --border:#262C36;
    --border-lt:#39414F;
    --hover:rgba(255,255,255,0.04);
    --text:#F5F7FA;
    --text-muted:#9AA3B2;
    --text-dim:#5F6776;
    --success:#22C55E;
    --warning:#F59E0B;
    --info:#3B82F6;
    --danger:#EF4444;
    --radius:14px;
    --radius-sm:10px;
    --radius-lg:20px;
    --radius-pill:999px;
    --font-display:'Bebas Neue',sans-serif;
    --font-body:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
    --shadow:0 12px 40px rgba(0,0,0,0.55);
    --shadow-sm:0 2px 8px rgba(0,0,0,0.35);
    --shadow-glow:0 6px 24px rgba(225,29,46,0.30);
}

/* Force dark on everything */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    -webkit-font-smoothing: antialiased;
}
@media (prefers-color-scheme: light) {
    html, body, [data-testid="stApp"] {
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }
}

/* Hide all Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .viewerBadge_container__1QSob,
button[title="View fullscreen"] {
    display: none !important;
    visibility: hidden !important;
}

/* Sidebar collapse toggle — always visible */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
section[data-testid="stSidebarCollapsedControl"],
div[data-testid="collapsedControl"],
button[aria-label="open sidebar"],
button[aria-label="Open sidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: all !important;
    z-index: 99999 !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    stroke: #9AA3B2 !important;
    fill: none !important;
}

/* Main content area */
[data-testid="stAppViewContainer"] > .main {
    background:
      radial-gradient(900px 500px at 50% -240px, rgba(225,29,46,0.08) 0%, transparent 70%),
      var(--bg) !important;
    padding-top: 0 !important;
}
.block-container {
    padding: 1.25rem 1.25rem 5rem 1.25rem !important;
    max-width: 900px !important;
}
@media (min-width: 1100px){
    .block-container { padding: 1.5rem 2.25rem 5rem 2.25rem !important; }
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #080A0E !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .block-container {
    padding: 0.75rem 0.75rem 1.5rem 0.75rem !important;
}

/* Typography */
h1,h2 { font-family:var(--font-display)!important; letter-spacing:1.2px; color:var(--text)!important; font-weight:400!important; }
h3,h4,h5 { font-family:var(--font-body)!important; font-weight:600!important; color:var(--text)!important; }
h1 { font-size:2.2rem!important; margin:0 0 0.2rem 0!important; line-height:1.05; }
h2 { font-size:1.5rem!important; margin-top:0.4rem!important; }
h3 { font-size:1.05rem!important; }
h4 { font-size:0.92rem!important; }
p  { color:var(--text-muted); line-height:1.62; font-size:0.93rem; }
a  { color:var(--secondary); text-decoration:none; }
a:hover { color:var(--primary-lt); }

/* Buttons */
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button {
    background:var(--primary)!important; color:#FFF!important; border:none!important;
    border-radius:var(--radius-pill)!important; font-weight:600!important; font-size:0.9rem!important;
    padding:11px 22px!important; min-height:44px!important;
    transition:transform 0.12s,background 0.15s,box-shadow 0.15s!important;
    box-shadow:var(--shadow-glow)!important; letter-spacing:0.2px!important;
}
.stButton>button:hover,.stDownloadButton>button:hover {
    background:var(--primary-dk)!important; transform:translateY(-1px)!important;
    box-shadow:0 10px 28px rgba(225,29,46,0.42)!important;
}
.stButton>button:active { transform:translateY(0)!important; }
.stButton>button[kind="secondary"] {
    background:var(--surface2)!important; color:var(--text)!important;
    border:1px solid var(--border-lt)!important; box-shadow:none!important;
}
.stButton>button[kind="secondary"]:hover {
    background:var(--surface3)!important; border-color:var(--primary-lt)!important; color:#FFF!important;
}

/* Inputs — forced dark */
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input {
    background:var(--surface2)!important; border:1px solid var(--border)!important;
    color:var(--text)!important; border-radius:var(--radius-sm)!important;
    padding:12px 14px!important; font-size:0.95rem!important; min-height:46px!important;
    transition:border-color 0.15s,box-shadow 0.15s!important;
}
.stTextInput input:focus,.stTextArea textarea:focus {
    border-color:var(--primary-lt)!important;
    box-shadow:0 0 0 3px rgba(225,29,46,0.18)!important; outline:none!important;
}
.stTextInput input::placeholder,.stTextArea textarea::placeholder { color:var(--text-dim)!important; }
.stSelectbox [data-baseweb="select"]>div {
    background:var(--surface2)!important; border-color:var(--border)!important;
    color:var(--text)!important; border-radius:var(--radius-sm)!important; min-height:46px!important;
}
[data-baseweb="popover"],[data-baseweb="menu"] {
    background:var(--surface2)!important; border:1px solid var(--border-lt)!important;
}
[data-baseweb="option"] { background:var(--surface2)!important; color:var(--text)!important; }
[data-baseweb="option"]:hover,[data-baseweb="option"][aria-selected="true"] { background:var(--surface3)!important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background:var(--surface)!important; border:1px solid var(--border)!important;
    border-radius:var(--radius-pill)!important; border-bottom:1px solid var(--border)!important;
    gap:4px!important; padding:4px!important; overflow-x:auto!important;
    scrollbar-width:none!important; flex-wrap:nowrap!important;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display:none; }
.stTabs [data-baseweb="tab"] {
    color:var(--text-muted)!important; font-weight:500!important;
    border-radius:var(--radius-pill)!important; padding:8px 16px!important;
    font-size:0.83rem!important; white-space:nowrap!important;
    transition:all 0.15s!important; background:transparent!important;
}
.stTabs [data-baseweb="tab"]:hover { color:var(--text)!important; background:var(--hover)!important; }
.stTabs [aria-selected="true"] { color:#FFF!important; background:var(--primary)!important; box-shadow:var(--shadow-glow)!important; }
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"] { display:none!important; }
.stTabs [data-testid="stTabsContent"] { background:transparent!important; padding-top:12px!important; }

/* Expanders */
[data-testid="stExpander"] { border:none!important; border-radius:var(--radius)!important; background:transparent!important; margin-bottom:10px!important; }
.streamlit-expanderHeader,[data-testid="stExpander"] summary {
    background:var(--surface2)!important; border:1px solid var(--border)!important;
    border-radius:var(--radius)!important; color:var(--text)!important;
    font-weight:600!important; padding:14px 18px!important;
}
[data-testid="stExpander"] summary:hover { background:var(--surface3)!important; border-color:var(--border-lt)!important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"],.streamlit-expanderContent {
    background:var(--surface)!important; border:1px solid var(--border)!important;
    border-top:none!important; border-radius:0 0 var(--radius) var(--radius)!important; padding:18px!important;
}

/* Metrics */
[data-testid="metric-container"],[data-testid="stMetric"] {
    background:linear-gradient(180deg,var(--surface2) 0%,var(--surface) 100%)!important;
    border:1px solid var(--border)!important; border-radius:var(--radius)!important;
    padding:18px 20px!important; box-shadow:var(--shadow-sm)!important;
}
[data-testid="stMetricValue"] { color:var(--secondary)!important; font-family:var(--font-display)!important; font-size:2.1rem!important; }
[data-testid="stMetricLabel"] { color:var(--text-muted)!important; font-size:0.72rem!important; text-transform:uppercase!important; letter-spacing:1.2px!important; font-weight:600!important; }

/* Alerts */
.stSuccess{background:rgba(34,197,94,0.10)!important;border:1px solid rgba(34,197,94,0.35)!important;color:#BBF7D0!important;border-radius:var(--radius)!important;}
.stInfo{background:rgba(59,130,246,0.10)!important;border:1px solid rgba(59,130,246,0.35)!important;color:#BFDBFE!important;border-radius:var(--radius)!important;}
.stWarning{background:rgba(245,158,11,0.10)!important;border:1px solid rgba(245,158,11,0.35)!important;color:#FDE68A!important;border-radius:var(--radius)!important;}
.stError{background:rgba(239,68,68,0.10)!important;border:1px solid rgba(239,68,68,0.40)!important;color:#FECACA!important;border-radius:var(--radius)!important;}

/* Sidebar nav */
[data-testid="stSidebar"] [data-testid="stRadio"]>div { gap:2px!important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background:transparent!important; border-radius:10px!important; padding:10px 14px!important;
    cursor:pointer!important; color:var(--text-muted)!important; font-size:0.92rem!important;
    width:100%!important; transition:all 0.15s!important; margin-bottom:1px!important;
    display:flex!important; align-items:center!important; min-height:42px!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:var(--hover)!important; color:var(--text)!important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background:linear-gradient(90deg,var(--primary) 0%,var(--primary-dk) 100%)!important;
    color:#fff!important; font-weight:600!important; box-shadow:0 4px 14px rgba(225,29,46,0.35)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]>label>div:first-child,
[data-testid="stSidebar"] [data-testid="stRadio"] span[data-baseweb="radio"] { display:none!important; }
[data-testid="stSidebar"] .stButton>button {
    background:transparent!important; color:#9AA3B2!important; border:1px solid #262C36!important;
    border-radius:10px!important; font-size:0.85rem!important; font-weight:500!important;
    width:100%!important; min-height:40px!important; box-shadow:none!important;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background:rgba(225,29,46,0.10)!important; color:#FF3B4D!important;
    border-color:#FF3B4D!important; transform:none!important;
}

/* Divider */
hr { border-color:var(--border)!important; margin:12px 0!important; opacity:0.8; }

/* Scrollbar */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--border-lt); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:var(--text-dim); }

/* Labels */
label,.stSelectbox label,.stTextInput label,.stTextArea label,.stNumberInput label {
    color:var(--text-muted)!important; font-size:0.74rem!important; font-weight:600!important;
    letter-spacing:0.7px!important; text-transform:uppercase!important;
}

/* Card utilities */
.wc-card {
    background:linear-gradient(180deg,var(--surface2) 0%,var(--surface) 100%);
    border:1px solid var(--border); border-radius:var(--radius);
    padding:20px; margin-bottom:14px; box-shadow:var(--shadow-sm);
    transition:border-color 0.15s,transform 0.15s;
}
.wc-card:hover { border-color:var(--border-lt); }
.wc-card-flat { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px 18px; margin-bottom:10px; }
.wc-chip { display:inline-block; padding:4px 12px; border-radius:var(--radius-pill); font-size:0.7rem; font-weight:700; letter-spacing:0.6px; text-transform:uppercase; }
.wc-chip-primary { background:var(--primary); color:#fff; }
.wc-chip-gold    { background:var(--secondary); color:#1A0F02; }
.wc-chip-muted   { background:var(--surface3); color:var(--text-muted); border:1px solid var(--border-lt); }

/* Tables */
[data-testid="stDataFrame"],[data-testid="stTable"] { border-radius:var(--radius)!important; overflow:hidden!important; border:1px solid var(--border)!important; }
[data-testid="stTable"] table { background:var(--surface)!important; }
[data-testid="stTable"] th { background:var(--surface2)!important; color:var(--text-muted)!important; font-size:0.72rem!important; text-transform:uppercase!important; }
[data-testid="stTable"] td { color:var(--text)!important; border-bottom:1px solid var(--border)!important; font-size:0.9rem!important; }

/* Progress bar */
.stProgress>div>div>div { background:var(--surface2)!important; border-radius:999px!important; }
.stProgress>div>div>div>div { background:linear-gradient(90deg,var(--primary) 0%,var(--secondary) 100%)!important; border-radius:999px!important; }

/* Caption */
.stCaption,[data-testid="stCaptionContainer"] { color:var(--text-dim)!important; font-size:0.78rem!important; }

/* Code */
code { background:var(--surface2)!important; color:var(--secondary)!important; padding:2px 7px!important; border-radius:6px!important; font-size:0.85em!important; border:1px solid var(--border)!important; }

/* Responsive */
@media (max-width:720px){
    [data-testid="column"] { padding:0 4px!important; }
    h1 { font-size:1.7rem!important; }
    .block-container { padding:0.75rem 0.75rem 5rem 0.75rem!important; }
}

/* Page-header utility */
.wc-page-header {
    display:flex; align-items:flex-end; justify-content:space-between;
    gap:16px; flex-wrap:wrap; padding:4px 0 14px 0; margin-bottom:18px;
    border-bottom:1px solid var(--border); position:relative;
}
.wc-page-header::after {
    content:""; position:absolute; left:0; bottom:-1px;
    width:64px; height:3px; border-radius:2px;
    background:linear-gradient(90deg,var(--primary) 0%,var(--secondary) 100%);
}
.wc-page-header h1 { margin:0!important; }
.wc-page-header .wc-sub { color:var(--text-muted); margin-top:6px; font-size:0.92rem; }
.wc-page-header .wc-eyebrow { color:var(--secondary); font-size:0.7rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px; }

/* Section title */
.wc-section-title {
    display:flex; align-items:center; gap:10px; margin:22px 0 12px 0;
    color:var(--text); font-weight:600; font-size:0.95rem;
    text-transform:uppercase; letter-spacing:1.1px;
}
.wc-section-title::before { content:""; width:4px; height:18px; border-radius:2px; background:var(--primary); display:inline-block; }

/* Top App Bar */
.wc-top-bar {
    background:rgba(8,10,14,0.96);
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    border-bottom:1px solid var(--border);
    display:flex; align-items:center; justify-content:space-between;
    padding:0 16px; gap:10px; height:56px;
    margin-bottom:18px; margin-left:-1.25rem; margin-right:-1.25rem;
}
@media (min-width:1100px){
    .wc-top-bar { margin-left:-2.25rem; margin-right:-2.25rem; }
}
.wc-top-bar-left {
    display:flex; align-items:center; gap:10px; cursor:pointer;
    padding:6px 10px; border-radius:var(--radius-sm); transition:background 0.15s; flex-shrink:0;
}
.wc-top-bar-left:hover { background:var(--hover); }
.wc-top-bar-brand { font-family:var(--font-display); font-size:1.05rem; letter-spacing:2px; color:var(--text); line-height:1; }
.wc-top-bar-tagline { color:var(--secondary); font-size:0.6rem; letter-spacing:2px; font-weight:700; margin-top:2px; }
.wc-top-bar-center { display:flex; align-items:center; gap:8px; flex:1; justify-content:center; flex-wrap:wrap; }
.wc-context-chip {
    display:inline-flex; align-items:center; gap:5px;
    background:var(--surface2); border:1px solid var(--border); border-radius:var(--radius-pill);
    padding:4px 12px; font-size:0.72rem; font-weight:600; color:var(--text-muted);
    letter-spacing:0.3px; white-space:nowrap;
}
.wc-context-chip.live { background:rgba(225,29,46,0.12); border-color:rgba(225,29,46,0.4); color:#FF5F6D; }
.wc-context-chip.gold { background:rgba(242,193,78,0.10); border-color:rgba(242,193,78,0.35); color:var(--secondary); }
.wc-top-bar-right { display:flex; align-items:center; gap:8px; flex-shrink:0; }
.wc-avatar-btn {
    width:36px; height:36px; border-radius:50%; background:var(--surface2);
    border:2px solid var(--border-lt); display:flex; align-items:center; justify-content:center;
    cursor:pointer; transition:border-color 0.15s; overflow:hidden;
}
.wc-avatar-btn:hover { border-color:var(--primary); }
</style>
"""


# ── Football avatar SVGs ───────────────────────────────────────────────
FOOTBALL_AVATARS = [
    ("Ball",    """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="21" fill="#f0f0f0" stroke="#222" stroke-width="2"/>
      <polygon points="24,8 28,18 20,18" fill="#222"/><polygon points="24,40 28,30 20,30" fill="#222"/>
      <polygon points="8,24 18,20 18,28" fill="#222"/><polygon points="40,24 30,20 30,28" fill="#222"/>
      <polygon points="13,13 20,18 18,27 13,27" fill="#222"/><polygon points="35,13 28,18 30,27 35,27" fill="#222"/>
      <polygon points="13,35 20,30 28,30 35,35 24,40" fill="#222"/>
      <circle cx="24" cy="24" r="21" fill="none" stroke="#222" stroke-width="2"/>
    </svg>"""),
    ("Trophy",  """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 6h20v16a10 10 0 0 1-20 0V6z" fill="#D4AF37" stroke="#B8960C" stroke-width="2"/>
      <path d="M8 8h6v10a6 6 0 0 1-6 0V8z" fill="#D4AF37" stroke="#B8960C" stroke-width="1.5"/>
      <path d="M40 8h-6v10a6 6 0 0 0 6 0V8z" fill="#D4AF37" stroke="#B8960C" stroke-width="1.5"/>
      <rect x="19" y="32" width="10" height="6" fill="#D4AF37" stroke="#B8960C" stroke-width="1.5"/>
      <rect x="14" y="38" width="20" height="4" rx="2" fill="#D4AF37" stroke="#B8960C" stroke-width="1.5"/>
      <path d="M20 14 l4 6 l4-6" stroke="#fff" stroke-width="1.5" fill="none"/>
    </svg>"""),
    ("Boot",    """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 34 Q10 20 18 16 L28 14 Q34 13 36 18 L38 28 Q40 34 36 36 L12 38 Q8 38 10 34z" fill="#C0392B" stroke="#7F0000" stroke-width="2"/>
      <rect x="10" y="35" width="26" height="5" rx="2" fill="#222" stroke="#111" stroke-width="1"/>
      <circle cx="34" cy="20" r="2" fill="#D4AF37"/>
    </svg>"""),
    ("Goal",    """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="10" width="40" height="28" rx="2" fill="none" stroke="#fff" stroke-width="2.5"/>
      <line x1="4" y1="14" x2="44" y2="14" stroke="#aaa" stroke-width="1" stroke-dasharray="4,4"/>
      <line x1="4" y1="20" x2="44" y2="20" stroke="#aaa" stroke-width="1" stroke-dasharray="4,4"/>
      <line x1="4" y1="26" x2="44" y2="26" stroke="#aaa" stroke-width="1" stroke-dasharray="4,4"/>
      <line x1="4" y1="32" x2="44" y2="32" stroke="#aaa" stroke-width="1" stroke-dasharray="4,4"/>
      <line x1="16" y1="10" x2="16" y2="38" stroke="#aaa" stroke-width="1" stroke-dasharray="4,4"/>
      <line x1="32" y1="10" x2="32" y2="38" stroke="#aaa" stroke-width="1" stroke-dasharray="4,4"/>
      <circle cx="24" cy="26" r="5" fill="#f0f0f0" stroke="#222" stroke-width="1.5"/>
    </svg>"""),
    ("Jersey",  """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 6 L8 12 L12 20 L16 16 L16 42 L32 42 L32 16 L36 20 L40 12 L32 6 Q28 10 24 10 Q20 10 16 6z" fill="#B71C1C" stroke="#7F0000" stroke-width="2"/>
      <text x="24" y="30" text-anchor="middle" font-size="10" fill="#fff" font-family="Arial" font-weight="bold">10</text>
    </svg>"""),
    ("Whistle", """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="20" width="22" height="12" rx="6" fill="#D4AF37" stroke="#B8960C" stroke-width="2"/>
      <circle cx="34" cy="26" r="10" fill="#f0f0f0" stroke="#888" stroke-width="2"/>
      <circle cx="34" cy="26" r="5" fill="#B71C1C"/>
      <rect x="26" y="23" width="8" height="6" fill="#D4AF37"/>
    </svg>"""),
    ("Flag",    """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <line x1="10" y1="6" x2="10" y2="44" stroke="#888" stroke-width="3" stroke-linecap="round"/>
      <path d="M10 8 L38 14 L10 26z" fill="#B71C1C" stroke="#7F0000" stroke-width="1.5"/>
    </svg>"""),
    ("Gloves",  """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 28 Q10 26 10 20 L10 14 Q10 10 14 10 L16 10 L16 8 Q16 6 18 6 Q20 6 20 8 L20 10 L22 10 L22 8 Q22 6 24 6 Q26 6 26 8 L26 22 Q28 18 30 18 Q33 18 33 22 L33 28 Q33 36 24 38 L18 38 Q12 38 12 32z" fill="#ff9800" stroke="#e65100" stroke-width="2"/>
      <line x1="18" y1="10" x2="18" y2="22" stroke="#e65100" stroke-width="1.5"/>
      <line x1="22" y1="10" x2="22" y2="22" stroke="#e65100" stroke-width="1.5"/>
    </svg>"""),
]

AVATAR_LABELS = [lbl for lbl, _ in FOOTBALL_AVATARS]


def get_avatar_svg(label: str, size: int = 36) -> str:
    """Return a sized inline element with the SVG for this avatar label."""
    for lbl, svg in FOOTBALL_AVATARS:
        if lbl == label:
            return (f'<span style="display:inline-flex;align-items:center;'
                    f'justify-content:center;width:{size}px;height:{size}px;">{svg}</span>')
    return (f'<span style="display:inline-flex;align-items:center;'
            f'justify-content:center;width:{size}px;height:{size}px;">{FOOTBALL_AVATARS[0][1]}</span>')


# ── Icon helper ───────────────────────────────────────────────────────
def svg_icon(name, size=18, color="#E11D2E"):
    s = str(size)
    icons = {
        "dashboard":   f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>',
        "predictions": f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
        "matches":     f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><line x1="2" y1="12" x2="22" y2="12"/></svg>',
        "teams":       f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "leaderboard": f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
        "rooms":       f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
        "news":        f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>',
        "admin":       f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93l-1.41 1.41M5.34 17.66l-1.41 1.41M20 12h-2M6 12H4M19.07 19.07l-1.41-1.41M5.34 6.34L3.93 4.93M12 2v2M12 20v2"/></svg>',
        "trophy":      f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2"/><rect x="6" y="18" width="12" height="4"/></svg>',
        "lock":        f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
        "check":       f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
        "x":           f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
        "star":        f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
        "globe":       f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "clock":       f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
        "link":        f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
        "edit":        f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
        "user":        f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
        "settings":    f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93l-1.41 1.41M5.34 17.66l-1.41 1.41M20 12h-2M6 12H4M19.07 19.07l-1.41-1.41M5.34 6.34L3.93 4.93M12 2v2M12 20v2"/></svg>',
    }
    return icons.get(name, "")


# ── Badge helpers ─────────────────────────────────────────────────────
def match_result_badge(result):
    cfg = {"home": ("#E11D2E","HOME WIN"), "draw": ("#6B6052","DRAW"), "away": ("#1E5A8A","AWAY WIN")}
    c, l = cfg.get(result, ("#333","UNKNOWN"))
    return f'<span style="background:{c};color:#fff;padding:4px 11px;border-radius:999px;font-size:0.7rem;font-weight:700;letter-spacing:0.5px;">{l}</span>'

def stage_badge(stage):
    labels = {"group":"GROUP","round_of_32":"R32","round_of_16":"R16",
              "quarter_final":"QF","semi_final":"SF","final":"FINAL"}
    l = labels.get(stage, stage.upper().replace("_"," "))
    return f'<span style="background:var(--surface3);color:var(--text-muted);padding:3px 9px;border-radius:999px;font-size:0.66rem;font-weight:600;border:1px solid var(--border-lt);">{l}</span>'

def points_badge(pts):
    return f'<span style="background:var(--secondary);color:#1A0F02;padding:4px 11px;border-radius:999px;font-size:0.7rem;font-weight:800;">{int(pts)} PTS</span>'

def format_kickoff(dt):
    if dt is None: return "TBD"
    from datetime import timedelta
    try:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        portugal_time = dt + timedelta(hours=1)
        return portugal_time.strftime("%d %b  %H:%M")
    except:
        return str(dt)

def flag_emoji(team_name):
    FLAGS = {"Brazil":"🇧🇷","Argentina":"🇦🇷","France":"🇫🇷","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Germany":"🇩🇪",
             "Spain":"🇪🇸","Portugal":"🇵🇹","Netherlands":"🇳🇱","USA":"🇺🇸","Mexico":"🇲🇽",
             "Canada":"🇨🇦","Japan":"🇯🇵","South Korea":"🇰🇷","Morocco":"🇲🇦","Senegal":"🇸🇳",
             "Colombia":"🇨🇴","Uruguay":"🇺🇾","Ecuador":"🇪🇨","Switzerland":"🇨🇭","Belgium":"🇧🇪",
             "Croatia":"🇭🇷","Serbia":"🇷🇸","Denmark":"🇩🇰","Austria":"🇦🇹","Poland":"🇵🇱",
             "Australia":"🇦🇺","Iran":"🇮🇷","Saudi Arabia":"🇸🇦","Cameroon":"🇨🇲","Nigeria":"🇳🇬",
             "Ghana":"🇬🇭","Ivory Coast":"🇨🇮","Venezuela":"🇻🇪","Bolivia":"🇧🇴","Paraguay":"🇵🇾",
             "Qatar":"🇶🇦","Wales":"🏴󠁧󠁢󠁷󠁬󠁳󠁿","Tunisia":"🇹🇳","Costa Rica":"🇨🇷"}
    return FLAGS.get(team_name, "🏳️")

def ordinal(n):
    if 11<=n<=13: return f"{n}th"
    return {1:f"{n}st",2:f"{n}nd",3:f"{n}rd"}.get(n%10,f"{n}th")


# ── CSS injection ─────────────────────────────────────────────────────
def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown("""
        <script>
        (function() {
            var styleId = 'wc-sidebar-fix';
            if (document.getElementById(styleId)) return;
            var style = document.createElement('style');
            style.id = styleId;
            style.textContent = `
                [data-testid="collapsedControl"],
                [data-testid="stSidebarCollapsedControl"],
                button[aria-label="open sidebar"],
                button[aria-label="Open sidebar"] {
                    display: flex !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    pointer-events: all !important;
                    z-index: 99999 !important;
                }
            `;
            document.head.appendChild(style);
            setInterval(function() {
                var el = document.querySelector(
                    '[data-testid="collapsedControl"], ' +
                    '[data-testid="stSidebarCollapsedControl"], ' +
                    'button[aria-label="open sidebar"]'
                );
                if (el) {
                    el.style.setProperty('display', 'flex', 'important');
                    el.style.setProperty('visibility', 'visible', 'important');
                }
            }, 800);
        })();
        </script>
    """, unsafe_allow_html=True)


# ── Tournament context ────────────────────────────────────────────────
WC_START = date(2026, 6, 11)
WC_END   = date(2026, 7, 19)

def _get_tournament_context() -> list[dict]:
    today = date.today()
    chips = []
    if today < WC_START:
        days = (WC_START - today).days
        chips.append({"text": f"🗓 {days} days to kickoff", "cls": "gold"})
    elif today > WC_END:
        chips.append({"text": "🏆 Tournament ended", "cls": ""})
    else:
        day_num = (today - WC_START).days + 1
        chips.append({"text": f"⚽ Day {day_num}", "cls": "gold"})
        if day_num <= 18:
            chips.append({"text": "Group Stage", "cls": ""})
        elif day_num <= 22:
            chips.append({"text": "Round of 32", "cls": ""})
        elif day_num <= 26:
            chips.append({"text": "Round of 16", "cls": ""})
        elif day_num <= 30:
            chips.append({"text": "Quarter-Finals", "cls": ""})
        elif day_num <= 34:
            chips.append({"text": "Semi-Finals", "cls": ""})
        else:
            chips.append({"text": "🏆 Final Week", "cls": "gold"})
    return chips


def render_top_bar():
    """Render the persistent top bar: branding left, context center, profile right."""
    user = st.session_state.get("user")
    if not user:
        return

    username   = user.get("username", "")
    avatar_lbl = user.get("avatar_emoji", "Ball")
    avatar_svg = get_avatar_svg(avatar_lbl, 26)

    chips_html = " ".join(
        f'<span class="wc-context-chip {c["cls"]}">{c["text"]}</span>'
        for c in _get_tournament_context()
    )

    go_dash = st.button("__go_dashboard__", key="_topbar_db")
    if go_dash:
        st.session_state.nav = "Dashboard"
        st.rerun()

    open_profile = st.button("__open_profile__", key="_topbar_pf")
    if open_profile:
        st.session_state["show_profile_modal"] = not st.session_state.get("show_profile_modal", False)
        st.rerun()

    st.markdown(f"""
    <div class="wc-top-bar">
        <div class="wc-top-bar-left" onclick="(function(){{
            for(var b of document.querySelectorAll('button')){{
                if(b.innerText.trim()==='__go_dashboard__'){{b.click();break;}}
            }}
        }})()">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                stroke="#F2C14E" stroke-width="2">
                <polyline points="6 9 6 2 18 2 18 9"/>
                <path d="M6 18H4a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2"/>
                <rect x="6" y="18" width="12" height="4"/>
            </svg>
            <div>
                <div class="wc-top-bar-brand">WORLD CUP 2026</div>
                <div class="wc-top-bar-tagline">PREDICTOR</div>
            </div>
        </div>
        <div class="wc-top-bar-center">{chips_html}</div>
        <div class="wc-top-bar-right">
            <span style="color:var(--text-muted);font-size:0.78rem;font-weight:500;">{username}</span>
            <div class="wc-avatar-btn" onclick="(function(){{
                for(var b of document.querySelectorAll('button')){{
                    if(b.innerText.trim()==='__open_profile__'){{b.click();break;}}
                }}
            }})()" title="Profile settings">
                {avatar_svg}
            </div>
        </div>
    </div>
    <script>
    (function(){{
        function hide(){{
            for(var b of document.querySelectorAll('button')){{
                if(b.innerText.trim()==='__go_dashboard__'||b.innerText.trim()==='__open_profile__'){{
                    b.style.display='none';
                    if(b.parentElement)b.parentElement.style.display='none';
                    var gp=b.parentElement&&b.parentElement.parentElement;
                    if(gp)gp.style.display='none';
                }}
            }}
        }}
        hide();setTimeout(hide,200);setTimeout(hide,700);
    }})();
    </script>
    """, unsafe_allow_html=True)

    if st.session_state.get("show_profile_modal"):
        _render_profile_modal(user)


def _render_profile_modal(user: dict):
    st.markdown(f"""
    <div style="background:var(--surface2);border:1px solid var(--border-lt);
        border-radius:var(--radius);padding:20px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
            {get_avatar_svg(user.get('avatar_emoji','Ball'), 40)}
            <div>
                <div style="font-weight:700;font-size:1rem;">{user['username']}</div>
                <div style="color:var(--text-muted);font-size:0.78rem;">{user.get('email','')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_a, tab_u = st.tabs(["Change Avatar", "Change Username"])

    with tab_a:
        current = user.get("avatar_emoji", "Ball")
        for row_start in range(0, len(FOOTBALL_AVATARS), 4):
            row_items = FOOTBALL_AVATARS[row_start:row_start+4]
            cols = st.columns(len(row_items))
            for col, (lbl, svg) in zip(cols, row_items):
                with col:
                    is_sel = current == lbl
                    border = "2px solid var(--primary)" if is_sel else "1px solid var(--border)"
                    bg     = "var(--surface3)" if is_sel else "var(--surface)"
                    st.markdown(
                        f"""<div style="background:{bg};border:{border};border-radius:10px;
                            padding:8px;text-align:center;margin-bottom:4px;">
                            <div style="width:32px;height:32px;margin:0 auto;">{svg}</div>
                            <div style="font-size:0.58rem;color:var(--text-muted);margin-top:3px;">{lbl}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    if st.button(lbl, key=f"pm_av_{lbl}", use_container_width=True):
                        _save_avatar(user["id"], lbl)

    with tab_u:
        new_uname = st.text_input("New username", value=user.get("username",""), key="pm_uname")
        if st.button("Save Username", key="pm_save_uname", use_container_width=True):
            _save_username(user["id"], new_uname)

    if st.button("✕ Close", key="pm_close", use_container_width=True):
        st.session_state["show_profile_modal"] = False
        st.rerun()


def _save_avatar(user_id: int, new_avatar: str):
    from database import get_db
    from models import User as UserModel
    with get_db() as db:
        u = db.get(UserModel, user_id)
        if u:
            u.avatar_emoji = new_avatar
    st.session_state.user["avatar_emoji"] = new_avatar
    st.session_state["show_profile_modal"] = False
    st.toast(f"Avatar changed to {new_avatar}!")
    st.rerun()


def _save_username(user_id: int, new_username: str):
    import re
    from database import get_db
    from models import User as UserModel
    new_username = new_username.strip()
    if not re.match(r'^[a-zA-Z0-9_\-\.]{3,30}$', new_username):
        st.error("Username: 3–30 chars, letters/numbers/_ - . only.")
        return
    with get_db() as db:
        existing = db.query(UserModel).filter(UserModel.username == new_username).first()
        if existing and existing.id != user_id:
            st.error("Username already taken.")
            return
        u = db.get(UserModel, user_id)
        if u:
            u.username = new_username
    st.session_state.user["username"] = new_username
    st.session_state["show_profile_modal"] = False
    st.toast("Username updated!")
    st.rerun()


def page_header(title, subtitle="", eyebrow=""):
    render_top_bar()
    eyebrow_html = f'<div class="wc-eyebrow">{eyebrow}</div>' if eyebrow else ""
    sub = f'<div class="wc-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="wc-page-header"><div>{eyebrow_html}'
        f'<h1>{title}</h1>{sub}</div></div>',
        unsafe_allow_html=True
    )

def section_title(label):
    st.markdown(f'<div class="wc-section-title">{label}</div>', unsafe_allow_html=True)

def require_login():
    if not st.session_state.get("user"):
        st.markdown(
            f'<div style="text-align:center;padding:80px 20px;">'
            f'<div style="margin-bottom:16px;">{svg_icon("lock",52,"#E11D2E")}</div>'
            f'<h2 style="color:var(--text);">Sign in required</h2>'
            f'<p style="color:var(--text-muted);">Please log in to access this page.</p></div>',
            unsafe_allow_html=True
        )
        st.stop()

def require_room():
    if not st.session_state.get("room"):
        st.warning("No room selected — please join or create a room first.")
        st.info("Head to the **Rooms** page to get started.")
        if st.button("Go to Rooms", key="_require_room_btn"):
            st.session_state.nav = "Rooms"
            st.rerun()
        st.stop()
