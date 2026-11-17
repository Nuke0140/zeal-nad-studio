# -*- coding: utf-8 -*-
"""
ZEAL NAD Data Processor — Premium Theme Engine
==============================================
Two hand-tuned palettes (dark / light) expressed purely as CSS variables,
plus a static stylesheet consumed by app.py. Toggling the theme simply
swaps the :root variables — every component restyles instantly.
"""

DARK_VARS = {
    "--bg": "#06060f",
    "--glow-a": "rgba(0,240,255,.055)",
    "--glow-b": "rgba(188,19,254,.065)",
    "--card": "rgba(255,255,255,.032)",
    "--card-2": "rgba(255,255,255,.065)",
    "--border": "rgba(255,255,255,.09)",
    "--border-strong": "rgba(255,255,255,.17)",
    "--text": "#eef2fa",
    "--text-2": "#9aa7c1",
    "--text-3": "#5d6a86",
    "--cyan": "#00f0ff",
    "--purple": "#bc13fe",
    "--cyan-dim": "rgba(0,240,255,.32)",
    "--cyan-soft": "rgba(0,240,255,.08)",
    "--hero-bg": "linear-gradient(135deg, rgba(255,255,255,.045), rgba(255,255,255,.012))",
    "--cyan-glow": "rgba(0,240,255,.17)",
    "--purple-glow": "rgba(188,19,254,.15)",
    "--th-bg": "rgba(13,15,30,.97)",
    "--side-bg": "linear-gradient(180deg, #08081a 0%, #0a0c20 100%)",
}

LIGHT_VARS = {
    "--bg": "#eef2f9",
    "--glow-a": "rgba(0,193,255,.09)",
    "--glow-b": "rgba(188,19,254,.08)",
    "--card": "#ffffff",
    "--card-2": "#f1f5fc",
    "--border": "#dde5f2",
    "--border-strong": "#c2cfe4",
    "--text": "#141c31",
    "--text-2": "#4a5673",
    "--text-3": "#8a95ac",
    "--cyan": "#0092b8",
    "--purple": "#9a0ed1",
    "--cyan-dim": "rgba(0,146,184,.35)",
    "--cyan-soft": "rgba(0,146,184,.07)",
    "--hero-bg": "linear-gradient(135deg, #ffffff, #f3f7ff)",
    "--cyan-glow": "rgba(0,200,235,.16)",
    "--purple-glow": "rgba(188,19,254,.10)",
    "--th-bg": "rgba(243,247,255,.98)",
    "--side-bg": "linear-gradient(180deg, #ffffff 0%, #f2f6fd 100%)",
}


def get_palette(dark=True):
    return dict(DARK_VARS if dark else LIGHT_VARS)


_FONT_IMPORT = ("@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900"
                "&family=JetBrains+Mono:wght@400;500;600;700&display=swap');")


def inject_css(palette):
    """Return a single <style> payload: fonts + palette variables + base sheet.

    NOTE: blank lines are stripped — Streamlit's markdown parser ends an HTML
    block at a blank line, which would otherwise break the <style> payload
    apart and render the tail as plain text.
    """
    root = "".join(f"{k}:{v};" for k, v in palette.items())
    css = "\n".join(line for line in BASE_CSS.splitlines() if line.strip())
    return f"<style>{_FONT_IMPORT}:root{{{root}}}{css}</style>"


BASE_CSS = r"""
/* ---------------- GLOBAL ---------------- */
.stApp {
  background:
    radial-gradient(1100px 700px at 85% -10%, var(--glow-a), transparent 60%),
    radial-gradient(900px 650px at -12% 110%, var(--glow-b), transparent 60%),
    var(--bg);
  color: var(--text);
  font-family: 'Outfit', 'Segoe UI', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
div.block-container, [data-testid="stMainBlockContainer"] { padding: 2.3rem 2.2rem 3rem; max-width: 1280px; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::selection { background: rgba(0,240,255,.28); }
.stMarkdown, .stMarkdown p { color: var(--text-2); }
[data-testid="stWidgetLabel"] p { color: var(--text-2) !important; font-family: 'Outfit', sans-serif; font-size: .86rem; }

/* ---------------- SIDEBAR ---------------- */
section[data-testid="stSidebar"] { background: var(--side-bg); border-right: 1px solid var(--border); }
[data-testid="stSidebarContent"] { padding: 1.5rem 1.25rem; }
[data-testid="stSidebar"] hr { border: none; height: 1px; background: var(--border); margin: 1.1rem 0; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: var(--text-2); }

.side-logo { padding: .2rem 0 .4rem; }
.side-logo .zl { font-size: 1.55rem; font-weight: 900; letter-spacing: -.02em; color: var(--text); line-height: 1.1; }
.grad { background: linear-gradient(90deg, var(--cyan), var(--purple), var(--cyan)); background-size: 200% auto; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: shine 7s linear infinite; }
.side-logo .zs { font-family: 'JetBrains Mono', monospace; font-size: .62rem; letter-spacing: .22em; color: var(--text-3); margin-top: 4px; }
.side-status { display: inline-flex; align-items: center; gap: 8px; margin-top: 14px; font-family: 'JetBrains Mono', monospace; font-size: .62rem; letter-spacing: .14em; color: #34d399; border: 1px solid rgba(52,211,153,.3); background: rgba(52,211,153,.07); padding: 6px 12px; border-radius: 999px; }
.side-status .pd { width: 6px; height: 6px; border-radius: 50%; background: #34d399; animation: pulse 2s infinite; }

.side-sec { margin: 1.15rem 0 .45rem; font-family: 'JetBrains Mono', monospace; font-size: .64rem; letter-spacing: .2em; color: var(--text-3); }
.step { display: flex; gap: 10px; align-items: flex-start; padding: 6px 0; color: var(--text-2); font-size: .85rem; line-height: 1.5; }
.step .n { flex: none; width: 21px; height: 21px; border-radius: 7px; background: var(--cyan-soft); border: 1px solid var(--cyan-dim); color: var(--cyan); font-family: 'JetBrains Mono', monospace; font-size: .64rem; font-weight: 700; display: flex; align-items: center; justify-content: center; margin-top: 2px; }
.step b { color: var(--text); font-weight: 600; }

.credit { margin-top: 1.3rem; padding: 16px 14px; border-radius: 16px; background: var(--card); border: 1px solid var(--border); text-align: center; }
.credit .h { font-size: .9rem; font-weight: 700; color: var(--text); }
.credit .s { font-family: 'JetBrains Mono', monospace; font-size: .62rem; color: var(--text-3); margin-top: 5px; letter-spacing: .08em; }
.credit .tag { display: inline-block; margin-top: 10px; font-family: 'JetBrains Mono', monospace; font-size: .6rem; letter-spacing: .14em; color: var(--cyan); border: 1px solid var(--cyan-dim); background: var(--cyan-soft); border-radius: 999px; padding: 4px 12px; }

/* ---------------- HERO ---------------- */
.hero { position: relative; padding: 2.3rem 2.5rem 2.1rem; border-radius: 26px; background: var(--hero-bg); border: 1px solid var(--border); overflow: hidden; animation: fadeUp .65s ease both; }
.hero::before { content: ''; position: absolute; width: 460px; height: 460px; border-radius: 50%; top: -240px; right: -100px; background: radial-gradient(circle, var(--cyan-glow), transparent 70%); filter: blur(70px); pointer-events: none; }
.hero::after { content: ''; position: absolute; width: 420px; height: 420px; border-radius: 50%; bottom: -260px; left: -120px; background: radial-gradient(circle, var(--purple-glow), transparent 70%); filter: blur(70px); pointer-events: none; }
.hero-badge { position: relative; display: inline-flex; align-items: center; gap: 9px; font-family: 'JetBrains Mono', monospace; font-size: .68rem; letter-spacing: .16em; color: var(--cyan); padding: 7px 15px; border-radius: 999px; border: 1px solid var(--cyan-dim); background: var(--cyan-soft); margin-bottom: 1.15rem; }
.hero-badge .pd { width: 7px; height: 7px; border-radius: 50%; background: var(--cyan); animation: pulse 2s infinite; }
.hero-title { position: relative; font-size: clamp(2.05rem, 4.6vw, 3.45rem); font-weight: 800; letter-spacing: -.025em; line-height: 1.04; margin: 0 0 .85rem; color: var(--text); }
.hero-sub { position: relative; color: var(--text-2); font-size: 1.02rem; max-width: 680px; line-height: 1.65; margin: 0 0 1.35rem; }
.pills { position: relative; display: flex; flex-wrap: wrap; gap: 9px; }
.pill { font-family: 'JetBrains Mono', monospace; font-size: .72rem; color: var(--text-2); padding: 8px 15px; border-radius: 999px; border: 1px solid var(--border); background: var(--card); transition: all .25s ease; }
.pill:hover { color: var(--cyan); border-color: var(--cyan-dim); transform: translateY(-1px); }

/* ---------------- SECTION HEADS / BOXES / CHIPS ---------------- */
.sec-head { display: flex; align-items: center; gap: 12px; margin: 1.5rem 0 .95rem; }
.sec-head .n { font-family: 'JetBrains Mono', monospace; font-size: .68rem; font-weight: 700; color: var(--cyan); border: 1px solid var(--cyan-dim); background: var(--cyan-soft); min-width: 27px; height: 27px; padding: 0 6px; border-radius: 9px; display: flex; align-items: center; justify-content: center; }
.sec-head .t { font-weight: 700; font-size: 1rem; letter-spacing: .015em; color: var(--text); }
.sec-head .line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }

.file-chip { display: flex; align-items: center; gap: 14px; padding: 14px 18px; border-radius: 15px; background: var(--card); border: 1px solid var(--border); animation: fadeUp .4s ease both; }
.file-chip .ico { font-size: 1.45rem; }
.file-chip .fn { font-weight: 600; color: var(--text); font-size: .93rem; word-break: break-all; }
.file-chip .fm { font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: var(--text-3); margin-top: 3px; }
.file-chip .ok { margin-left: auto; flex: none; font-family: 'JetBrains Mono', monospace; font-size: .66rem; letter-spacing: .08em; color: #34d399; border: 1px solid rgba(52,211,153,.35); background: rgba(52,211,153,.09); padding: 5px 11px; border-radius: 999px; }

.chip { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: .67rem; padding: 5px 11px; border-radius: 999px; margin: 3px 5px 3px 0; border: 1px solid var(--border); }
.chip.ok { color: #34d399; border-color: rgba(52,211,153,.4); background: rgba(52,211,153,.08); }
.chip.miss { color: #f87171; border-color: rgba(248,113,113,.4); background: rgba(248,113,113,.08); }
.chip.dim { color: var(--text-2); border-color: var(--border); background: var(--card); }

.warnbox { border: 1px solid rgba(251,191,36,.4); background: rgba(251,191,36,.07); color: #fbbf24; padding: 13px 17px; border-radius: 13px; font-size: .88rem; line-height: 1.55; animation: fadeUp .4s ease both; }
.errbox { border: 1px solid rgba(248,113,113,.45); background: rgba(248,113,113,.07); color: #f87171; padding: 13px 17px; border-radius: 13px; font-size: .88rem; line-height: 1.55; animation: fadeUp .4s ease both; }
.infobox { border: 1px solid var(--cyan-dim); background: var(--cyan-soft); color: var(--text-2); padding: 14px 17px; border-radius: 13px; font-size: .88rem; line-height: 1.6; animation: fadeUp .4s ease both; }
.warnbox b, .errbox b, .infobox b { color: inherit; }

/* ---------------- PREVIEW TABLE ---------------- */
.ptable-wrap { border: 1px solid var(--border); border-radius: 15px; overflow: auto; background: var(--card); }
.ptable-wrap .inner-max { max-height: 300px; overflow-y: auto; }
table.ptable { width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; font-size: .71rem; }
.ptable th { position: sticky; top: 0; background: var(--th-bg); color: var(--cyan); text-align: left; padding: 10px 13px; font-weight: 600; letter-spacing: .05em; border-bottom: 1px solid var(--border); white-space: nowrap; z-index: 2; }
.ptable td { padding: 8px 13px; color: var(--text-2); border-bottom: 1px solid var(--border); white-space: nowrap; max-width: 230px; overflow: hidden; text-overflow: ellipsis; }
.ptable tr:last-child td { border-bottom: none; }
.ptable tbody tr:hover td { background: var(--card-2); }
.ptable-more { font-family: 'JetBrains Mono', monospace; font-size: .68rem; color: var(--text-3); padding: 9px 14px; border-top: 1px solid var(--border); }

/* ---------------- STAT CARDS ---------------- */
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(165px, 1fr)); gap: 13px; }
.stat-card { position: relative; padding: 17px 18px 15px; border-radius: 17px; background: var(--card); border: 1px solid var(--border); overflow: hidden; animation: fadeUp .5s ease both; transition: transform .25s ease, border-color .25s ease; }
.stat-card:hover { transform: translateY(-3px); border-color: var(--border-strong); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2.5px; background: linear-gradient(90deg, var(--cyan), var(--purple)); }
.stat-card .ic { font-size: 1.1rem; margin-bottom: 9px; }
.stat-card .v { font-size: 1.8rem; font-weight: 800; color: var(--text); letter-spacing: -.02em; line-height: 1; }
.stat-card .l { font-family: 'JetBrains Mono', monospace; font-size: .64rem; color: var(--text-3); letter-spacing: .12em; margin-top: 7px; text-transform: uppercase; }

/* ---------------- TERMINAL (always dark — premium console) ---------------- */
.term { border-radius: 17px; overflow: hidden; border: 1px solid #232741; background: #0a0b18; box-shadow: 0 22px 50px rgba(0,0,0,.38); animation: fadeUp .5s ease both; }
.term-head { display: flex; align-items: center; gap: 7px; padding: 11px 16px; background: rgba(255,255,255,.03); border-bottom: 1px solid #1c2038; }
.term .dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.term .dot.r { background: #ff5f57; } .term .dot.y { background: #febc2e; } .term .dot.g { background: #28c840; }
.term-title { font-family: 'JetBrains Mono', monospace; font-size: .71rem; color: #7f89a3; margin-left: 9px; }
.term-live { margin-left: auto; font-family: 'JetBrains Mono', monospace; font-size: .64rem; letter-spacing: .12em; color: #00f0ff; display: flex; align-items: center; gap: 7px; }
.term-live .pd { width: 6px; height: 6px; border-radius: 50%; background: currentColor; animation: pulse 1.5s infinite; }
.term-live.done { color: #4ade80; } .term-live.fail { color: #f87171; } .term-live.idle { color: #566079; }
.term-body { padding: 15px 18px; font-family: 'JetBrains Mono', monospace; font-size: .77rem; line-height: 1.8; min-height: 118px; max-height: 300px; overflow-y: auto; }
.tl { white-space: pre-wrap; word-break: break-word; color: #c9d2e3; }
.tl .pre { color: #3d4763; margin-right: 9px; user-select: none; }
.tl.ok { color: #4ade80; } .tl.err { color: #f87171; } .tl.warn { color: #fbbf24; } .tl.sys { color: #38e1ff; }
.term-empty { color: #454f6d; }
.cursor { display: inline-block; width: 8px; height: 14px; background: #00f0ff; margin-left: 4px; vertical-align: middle; animation: blink 1.1s steps(1) infinite; }

/* ---------------- STREAMLIT WIDGETS ---------------- */
[data-testid="stTabs"] [role="tablist"] { gap: 8px; border-bottom: 1px solid var(--border) !important; }
[data-testid="stTab"] { color: var(--text-3) !important; border-radius: 13px 13px 0 0; padding: 12px 24px !important; font-size: .93rem; font-family: 'Outfit', sans-serif; letter-spacing: .04em; }
[data-testid="stTab"] p { color: inherit !important; }
[data-testid="stTab"]:hover { color: var(--text-2) !important; background: var(--card); }
[data-testid="stTab"][aria-selected="true"], [data-testid="stTab"][aria-selected="true"] p { color: var(--text) !important; }
[data-testid="stTab"] .react-aria-SelectionIndicator { background: linear-gradient(90deg, var(--cyan), var(--purple)) !important; height: 3px !important; border-radius: 99px !important; }
[data-testid="stTabPanel"] { padding-top: 1.1rem; }

[data-testid="stFileUploaderDropzone"] { border: 1.5px dashed var(--border-strong) !important; border-radius: 16px !important; background: var(--card) !important; transition: all .25s ease; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--cyan) !important; background: var(--cyan-soft) !important; }
[data-testid="stFileUploaderDropzone"] button { background: var(--card-2) !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: 10px !important; font-weight: 600 !important; font-family: 'JetBrains Mono', monospace !important; font-size: .76rem !important; padding: 8px 18px !important; transition: all .2s ease; }
[data-testid="stFileUploaderDropzone"] button:hover { border-color: var(--cyan) !important; color: var(--cyan) !important; }
[data-testid="stFileUploaderDropzone"] span, [data-testid="stFileUploaderDropzone"] small { color: var(--text-3) !important; }
[data-testid="stFileUploaderFile"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; color: var(--text-2) !important; }
[data-testid="stFileUploaderFile"] button { background: transparent !important; border: none !important; color: var(--text-2) !important; }

.stButton > button { width: 100%; border: none !important; border-radius: 14px !important; color: #fff !important; font-weight: 700 !important; font-size: 1.02rem !important; letter-spacing: .05em; padding: 1rem 1.2rem !important; font-family: 'Outfit', sans-serif !important; transition: all .25s ease !important; }
.stButton > button[data-testid="stBaseButton-primary"] { background: linear-gradient(135deg, #00e5ff -15%, #0091ff 45%, #7a1fff 115%) !important; box-shadow: 0 10px 30px rgba(0,180,255,.28) !important; }
.stButton > button[data-testid="stBaseButton-primary"]:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(0,200,255,.4) !important; filter: brightness(1.07); }
.stButton > button[data-testid="stBaseButton-tertiary"] { background: linear-gradient(135deg, #e14dff -10%, #8a15e8 55%, #5b0fd1 110%) !important; box-shadow: 0 10px 30px rgba(180,40,255,.28) !important; }
.stButton > button[data-testid="stBaseButton-tertiary"]:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(200,60,255,.4) !important; filter: brightness(1.07); }
.stButton > button:disabled { opacity: .55 !important; filter: saturate(.6); transform: none !important; box-shadow: none !important; }

[data-testid="stBaseButton-secondary"] { background: var(--card) !important; border: 1px solid var(--border-strong) !important; color: var(--text-2) !important; border-radius: 12px !important; font-family: 'JetBrains Mono', monospace !important; font-size: .78rem !important; box-shadow: none !important; padding: .55rem .9rem !important; }
[data-testid="stBaseButton-secondary"]:hover { color: var(--cyan) !important; border-color: var(--cyan) !important; background: var(--cyan-soft) !important; }

.stDownloadButton > button { width: 100%; border-radius: 14px !important; border: 1px solid rgba(52,211,153,.45) !important; background: rgba(52,211,153,.1) !important; color: #34d399 !important; font-weight: 700 !important; font-size: 1rem !important; letter-spacing: .04em; padding: 1rem 1.2rem !important; font-family: 'Outfit', sans-serif !important; transition: all .25s ease !important; }
.stDownloadButton > button:hover { background: linear-gradient(135deg, #34d399, #0ea5a0) !important; color: #04120e !important; border-color: transparent !important; box-shadow: 0 14px 36px rgba(52,211,153,.35) !important; transform: translateY(-2px); }

[data-testid="stProgress"] { margin-top: 12px !important; }
[data-testid="stProgressBarTrack"] { height: 12px !important; border-radius: 99px !important; background: var(--card-2) !important; border: 1px solid var(--border); overflow: hidden !important; }
[data-testid="stProgressBarTrack"] > div { background: linear-gradient(90deg, var(--cyan), var(--purple)) !important; border-radius: 99px !important; }
[data-testid="stProgress"] p { color: var(--text-2) !important; font-family: 'JetBrains Mono', monospace !important; font-size: .74rem !important; margin: 0 0 7px !important; }

/* ---------------- FOOTER ---------------- */
.app-foot { margin-top: 2.4rem; padding-top: 1.15rem; border-top: 1px solid var(--border); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: .67rem; letter-spacing: .06em; color: var(--text-3); }
.app-foot .cy { color: var(--cyan); font-weight: 600; }

/* ---------------- ANIMATIONS ---------------- */
@keyframes shine { to { background-position: 200% center; } }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: .4; transform: scale(.75); } }
@keyframes blink { 50% { opacity: 0; } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }

/* ---------------- MOBILE ---------------- */
@media (max-width: 640px) {
  .hero { padding: 1.6rem 1.3rem; }
  div.block-container, [data-testid="stMainBlockContainer"] { padding: 1.4rem 1rem 2rem; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  [data-baseweb="tab"] { padding: 10px 14px !important; }
}
"""
