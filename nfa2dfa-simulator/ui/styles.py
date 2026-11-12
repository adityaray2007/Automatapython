"""The glassmorphism look. If a CSS selector stops matching in a newer Streamlit version,
inspect the page (F12) and adjust the selector — do not remove the design."""

GLASS_CSS = """
<style>
:root{
  --ink:#1f2340; --muted:#5d6285; --accent:#5b5bd6; --accent2:#8b5cf6;
  --teal:#0d9488; --rose:#e11d48;
  --font-ui:"Plus Jakarta Sans","Segoe UI",system-ui,-apple-system,sans-serif;
  --font-mono:"JetBrains Mono",Consolas,"SFMono-Regular",Menlo,monospace;
}
.stApp{ background:#f6f3ff; color:var(--ink); font-family:var(--font-ui); }
[data-testid="stAppViewContainer"], [data-testid="stHeader"]{ background:transparent; }

/* Aurora: four big blurred blobs drifting very slowly (transform only) */
.stApp::before{
  content:""; position:fixed; inset:-25%; z-index:0; pointer-events:none;
  background:
    radial-gradient(38% 38% at 15% 20%, #c9f2e4 0%, transparent 70%),
    radial-gradient(38% 38% at 85% 15%, #d9ccff 0%, transparent 70%),
    radial-gradient(38% 38% at 20% 85%, #ffd9c7 0%, transparent 70%),
    radial-gradient(38% 38% at 80% 80%, #cfe6ff 0%, transparent 70%);
  filter:blur(30px);
  animation:drift 50s ease-in-out infinite alternate;
}
@keyframes drift{ from{transform:translate3d(0,0,0) scale(1);} to{transform:translate3d(-4%,3%,0) scale(1.08);} }
@media (prefers-reduced-motion: reduce){ .stApp::before{ animation:none; } }
.block-container{ position:relative; z-index:1; padding-top:1.5rem; max-width:1440px; }

/* Glass cards = bordered containers */
[data-testid="stVerticalBlockBorderWrapper"]{
  background:rgba(255,255,255,.58);
  border:1px solid rgba(255,255,255,.75) !important;
  border-radius:22px;
  backdrop-filter:blur(18px) saturate(140%);
  -webkit-backdrop-filter:blur(18px) saturate(140%);
  box-shadow:0 10px 30px rgba(80,70,140,.10), inset 0 1px 0 rgba(255,255,255,.85);
  padding:.5rem .7rem;
  margin-bottom: 0.8rem;
}
@supports not (backdrop-filter: blur(1px)){
  [data-testid="stVerticalBlockBorderWrapper"]{ background:rgba(255,255,255,.88); }
}

/* Brand header */
.brand h1{ margin:0; font-weight:800; letter-spacing:-.02em;
  background:linear-gradient(90deg,var(--accent),var(--accent2)); -webkit-background-clip:text;
  background-clip:text; color:transparent; }
.brand p{ margin:.1rem 0 1rem; color:var(--muted); font-size:1.05rem; }

/* Buttons */
.stButton>button[kind="primary"]{
  background:linear-gradient(90deg,var(--accent),var(--accent2)); border:none; color:#fff;
  border-radius:14px; box-shadow:0 6px 18px rgba(91,91,214,.35);
}
.stButton>button{ border-radius:14px; }
button:focus-visible, input:focus-visible, textarea:focus-visible, [role="slider"]:focus-visible{
  outline:3px solid var(--accent2) !important; outline-offset:2px;
}

/* Mono for sets / tables / inputs that hold state names */
[data-testid="stTable"] td, [data-testid="stTable"] th, code{ font-family:var(--font-mono); }
.stTextInput input{ font-family:var(--font-mono); }

/* Table wrapping & clean horizontal scroll */
[data-testid="stTable"] {
  overflow-x: auto !important;
  max-width: 100%;
}
[data-testid="stTable"] table {
  width: 100% !important;
}
[data-testid="stTable"] th, [data-testid="stTable"] td {
  white-space: nowrap !important;
  padding: 0.45rem 0.75rem !important;
}

/* Result badges */
.test-result{ display:inline-block; padding:.45rem 1rem; border-radius:999px; font-weight:800;
  font-size:1.05rem; margin:.4rem 0; }
.test-result.ok{ background:rgba(13,148,136,.14); color:#0b6f66; border:1px solid rgba(13,148,136,.4); }
.test-result.bad{ background:rgba(225,29,72,.10); color:#b4143b; border:1px solid rgba(225,29,72,.35); }
.agree-badge{ display:inline-block; padding:.2rem .7rem; border-radius:999px; font-size:.85rem;
  background:rgba(91,91,214,.10); color:#4343b5; border:1px solid rgba(91,91,214,.3); }
.step-counter{ font-family:var(--font-mono); font-weight:700; color:var(--accent);
  background:rgba(91,91,214,.10); padding:.2rem .7rem; border-radius:10px; font-size:1.05rem; }

/* Construction step items */
.step-item {
  padding: 0.5rem 0.8rem;
  margin-bottom: 0.4rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(91, 91, 214, 0.12);
  border-left: 4px solid var(--muted);
  font-size: 0.88rem;
  line-height: 1.45;
  word-break: normal;
  overflow-wrap: break-word;
}
.step-item.active {
  background: rgba(91, 91, 214, 0.10);
  border: 1px solid rgba(91, 91, 214, 0.35);
  border-left: 4px solid var(--accent);
  box-shadow: 0 2px 8px rgba(91, 91, 214, 0.12);
}
</style>
"""
