"""Flat, neutral visual style with light and dark palettes.

If a CSS selector stops matching in a newer Streamlit version, inspect the page (F12)
and adjust the selector."""

LIGHT_VARS = """
  --ink:#0f172a; --muted:#64748b; --accent:#1d4ed8; --accent2:#1e40af;
  --ok:#047857; --ok-bg:#ecfdf5; --ok-bd:#a7f3d0;
  --bad:#b91c1c; --bad-bg:#fef2f2; --bad-bd:#fecaca;
  --on-accent:#ffffff; --tint:#eff6ff; --tint-bd:#bfdbfe;
  --border:#e2e8f0; --surface:#ffffff; --surface2:#f1f5f9; --bg:#f8fafc;
"""

DARK_VARS = """
  --ink:#e2e8f0; --muted:#94a3b8; --accent:#60a5fa; --accent2:#93c5fd;
  --ok:#34d399; --ok-bg:#064e3b; --ok-bd:#047857;
  --bad:#f87171; --bad-bg:#450a0a; --bad-bd:#991b1b;
  --on-accent:#0b1220; --tint:#172554; --tint-bd:#1e40af;
  --border:#334155; --surface:#1e293b; --surface2:#0f172a; --bg:#0b1220;
"""

BASE_CSS = """
:root{
  --font-ui:"Inter","Segoe UI",system-ui,-apple-system,sans-serif;
  --font-mono:"JetBrains Mono",Consolas,"SFMono-Regular",Menlo,monospace;
}
html, body, .stApp, [data-testid="stAppViewContainer"]{ background:var(--bg) !important; }
.stApp, .stApp p, .stApp label, .stApp span, .stApp li, .stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp h5, .stApp h6, .stApp div[data-testid="stMarkdownContainer"]{ color:var(--ink); }
.stApp{ font-family:var(--font-ui); }
[data-testid="stHeader"]{ background:transparent !important; }
.block-container{ padding-top:2.2rem; padding-bottom:3rem; max-width:1360px; }

/* Cards: containers created with a key starting "card-" (see app.py) */
[class*="st-key-card-"]{
  background:var(--surface);
  border:1px solid var(--border) !important;
  border-radius:8px;
  box-shadow:0 1px 2px rgba(15,23,42,.05);
  padding:.7rem 1rem .9rem !important;
  margin-bottom:.9rem;
}
.st-key-logbox{
  background:var(--surface2) !important; border:1px solid var(--border) !important;
  border-radius:6px; padding:.5rem !important;
}

/* Headings */
h3{ font-size:1.02rem !important; font-weight:600 !important; padding:.2rem 0 .5rem !important;
    margin:0; border-bottom:1px solid var(--border); margin-bottom:.6rem !important; }
h5{ font-size:.85rem !important; font-weight:600 !important;
    letter-spacing:.01em; color:var(--muted) !important; margin:.4rem 0 .5rem !important; }

/* Brand header */
.brand{ display:flex; align-items:baseline; gap:.9rem; flex-wrap:wrap; }
.brand h1{ margin:0; padding:0; font-weight:700; letter-spacing:-.01em; font-size:1.6rem; }
.brand p{ margin:0; color:var(--muted) !important; font-size:.95rem; }

/* Labels */
[data-testid="stWidgetLabel"] p{ font-size:.82rem; font-weight:500; color:var(--muted) !important; }

/* Inputs */
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"],
[data-testid="stSelectbox"] [role="group"], [data-testid="stMultiSelect"] [role="group"],
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"]{
  background:var(--surface) !important; color:var(--ink) !important;
  border-color:var(--border) !important; border-radius:6px !important;
}
textarea{ background:transparent !important; }
[data-baseweb="select"] input{ background:transparent !important; }
input, textarea{ color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; }
[data-baseweb="select"] svg{ fill:var(--muted); }
[data-baseweb="tag"]{ background:var(--accent) !important; border-radius:4px !important; }
[data-baseweb="tag"], [data-baseweb="tag"] *, .stApp [data-testid="stMultiSelect"] span{ color:#fff !important; }
[data-baseweb="tag"] svg, [data-testid="stMultiSelect"] span svg{ fill:#fff !important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] ul{ background:var(--surface) !important; }
[data-baseweb="popover"] li{ color:var(--ink) !important; background:var(--surface) !important; }
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"]{ background:var(--tint) !important; }

/* Buttons */
.stButton>button, .stDownloadButton>button{
  border-radius:6px; font-weight:500; background:var(--surface); color:var(--ink);
  border:1px solid var(--border); box-shadow:none; min-height:2.4rem; white-space:nowrap;
}
.stButton>button:hover:not(:disabled), .stDownloadButton>button:hover:not(:disabled){
  border-color:var(--accent); color:var(--accent);
}
.stButton>button:disabled, .stDownloadButton>button:disabled{ opacity:.45; }
.stButton>button[kind="primary"]{ background:var(--accent); border:1px solid var(--accent); color:var(--on-accent); }
.stButton>button[kind="primary"]:hover:not(:disabled){ background:var(--accent2); border-color:var(--accent2); color:var(--on-accent); }
.stApp .stButton>button p, .stApp .stDownloadButton>button p{ color:var(--ink) !important; }
.stApp .stButton>button[kind="primary"] p, .stApp .stButton>button[kind="primary"] *{ color:var(--on-accent) !important; }
.stApp .stButton>button:hover:not(:disabled) p{ color:var(--accent) !important; }
.stApp .stButton>button[kind="primary"]:hover:not(:disabled) p{ color:var(--on-accent) !important; }
button:focus-visible, input:focus-visible, textarea:focus-visible, [role="slider"]:focus-visible{
  outline:2px solid var(--accent) !important; outline-offset:2px;
}

/* Mono for state names */
[data-testid="stTable"] td, [data-testid="stTable"] th, code{ font-family:var(--font-mono); }
.stTextInput input, textarea{ font-family:var(--font-mono); }
code{ background:var(--surface2) !important; color:var(--ink) !important; }

/* Tables */
[data-testid="stTable"]{ overflow-x:auto !important; max-width:100%; }
[data-testid="stTable"] table{ width:100% !important; border-collapse:collapse; background:var(--surface); }
[data-testid="stTable"] th{ background:var(--surface2) !important; font-weight:600; font-size:.8rem;
  color:var(--muted) !important; }
[data-testid="stTable"] td{ color:var(--ink) !important; font-size:.88rem; }
[data-testid="stTable"] th, [data-testid="stTable"] td{
  white-space:nowrap !important; padding:.5rem .8rem !important; border:1px solid var(--border) !important;
}

/* Transition-table editor grid: vertically centre every cell, uniform row height */
.grid-state{ font-family:var(--font-mono); font-weight:600; min-height:2.4rem; display:flex; align-items:center; }
.grid-head{ font-family:var(--font-mono); font-weight:600; font-size:.85rem; color:var(--muted);
  padding-bottom:.2rem; }

/* Alerts */
[data-testid="stAlert"]{ border-radius:6px; background:var(--surface2) !important; border:1px solid var(--border); }
[data-testid="stAlert"] *{ color:var(--ink) !important; }

/* Slider / radio accents */
[data-testid="stSlider"] [role="slider"]{ background:var(--accent) !important; }
[data-testid="stSlider"] [data-testid="stTickBarMin"], [data-testid="stSlider"] [data-testid="stTickBarMax"]{ color:var(--muted); }

/* Badges */
.test-result{ display:inline-block; padding:.3rem .8rem; border-radius:4px; font-weight:600; font-size:.95rem; margin:.4rem 0; }
.test-result.ok{ background:var(--ok-bg); color:var(--ok) !important; border:1px solid var(--ok-bd); }
.test-result.bad{ background:var(--bad-bg); color:var(--bad) !important; border:1px solid var(--bad-bd); }
.agree-badge{ display:inline-block; padding:.15rem .6rem; border-radius:4px; font-size:.82rem;
  background:var(--tint); color:var(--accent) !important; border:1px solid var(--tint-bd); }
.step-counter{ display:inline-block; font-family:var(--font-mono); font-weight:600; color:var(--accent) !important;
  background:var(--tint); border:1px solid var(--tint-bd); padding:.35rem .7rem; border-radius:6px; font-size:.9rem;
  min-height:2.4rem; line-height:1.6; }

/* Construction log */
.step-item{
  padding:.5rem .8rem; margin-bottom:.4rem; border-radius:4px;
  background:var(--surface); border:1px solid var(--border); border-left:3px solid var(--muted);
  font-size:.86rem; line-height:1.45; overflow-wrap:break-word;
}
.step-item.active{ background:var(--tint); border-color:var(--tint-bd); border-left:3px solid var(--accent); }
.step-item strong{ color:var(--ink); }

/* Graphviz area */
[data-testid="stGraphVizChart"]{ display:flex; justify-content:center; padding:.3rem 0; }
"""


def build_css(dark: bool) -> str:
    """Return the <style> block for the chosen theme."""
    return f"<style>:root{{{DARK_VARS if dark else LIGHT_VARS}}}{BASE_CSS}</style>"
