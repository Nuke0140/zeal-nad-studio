# -*- coding: utf-8 -*-
"""
ZEAL NAD Data Processor — Reusable HTML UI Blocks
=================================================
Pure functions returning premium-styled HTML fragments rendered via
st.markdown(..., unsafe_allow_html=True). All user-provided values are
HTML-escaped before interpolation.
"""

from datetime import datetime
from html import escape


def _esc(v):
    return escape("" if v is None else str(v))


def fmt_size(n):
    n = int(n)
    if n < 1024:
        return f"{n} B"
    if n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024 ** 2:.2f} MB"


# ------------------------------------------------------------------ HERO
def hero():
    return (
        '<div class="hero">'
        '<div class="hero-badge"><span class="pd"></span>NAD COMPLIANT • ACADEMIC DEPOSITORY SUITE</div>'
        '<h1 class="hero-title">ZEAL <span class="grad">NAD DATA</span> PROCESSOR</h1>'
        '<p class="hero-sub">Turn raw semester exports into depository-ready Excel in seconds — '
        'generate NAD upload files with strict column sequencing, then merge re-exam updates back '
        'into the master sheet. Everything runs locally inside your browser session.</p>'
        '<div class="pills">'
        '<span class="pill">⚡ CSV → NAD EXCEL</span>'
        '<span class="pill">🔗 RE-EXAM MERGE ENGINE</span>'
        '<span class="pill">🛡 TEXT-SAFE IDS</span>'
        '<span class="pill">📊 LIVE INSIGHTS</span>'
        '<span class="pill">🔒 100% CLIENT-SIDE</span>'
        '</div></div>'
    )


# ------------------------------------------------------------------ SIDEBAR
def sidebar_logo():
    return (
        '<div class="side-logo">'
        '<div class="zl">⚡ ZEAL <span class="grad">NAD</span></div>'
        '<div class="zs">NAD DATA PROCESSOR • v2.0</div>'
        '<div class="side-status"><span class="pd"></span>ALL SYSTEMS OPERATIONAL</div>'
        '</div>'
    )


def sidebar_guide():
    return (
        '<div class="side-sec">QUICK GUIDE — GENERATE</div>'
        '<div class="step"><span class="n">1</span><span>Upload the raw semester result <b>CSV</b> exported from the ERP.</span></div>'
        '<div class="step"><span class="n">2</span><span>Hit <b>PROCESS FILE</b> — subjects auto-detect, reverse &amp; map to NAD slots.</span></div>'
        '<div class="step"><span class="n">3</span><span>Download the NAD-ready Excel with <b>text-safe IDs</b>.</span></div>'
        '<div class="side-sec">QUICK GUIDE — MERGE</div>'
        '<div class="step"><span class="n">1</span><span>Upload the <b>odd-semester master</b> Excel.</span></div>'
        '<div class="step"><span class="n">2</span><span>Upload the <b>re-exam update</b> Excel.</span></div>'
        '<div class="step"><span class="n">3</span><span>Merge — re-exam values overwrite rows matching <b>REGN_NO + RROLL</b>.</span></div>'
    )


def sidebar_credit():
    return (
        '<div class="credit">'
        '<div class="h">Made by Nil</div>'
        '<div class="s">ZEAL EDUCATION GROUP</div>'
        '<div class="tag">v2.0 • WEB EDITION</div>'
        '</div>'
    )


# ------------------------------------------------------------------ SECTIONS
def sec_head(n, title):
    return (
        f'<div class="sec-head"><span class="n">{_esc(n)}</span>'
        f'<span class="t">{_esc(title)}</span><span class="line"></span></div>'
    )


def file_chip(name, meta, badge="READY"):
    return (
        '<div class="file-chip">'
        f'<span class="ico">📄</span>'
        f'<div><div class="fn">{_esc(name)}</div><div class="fm">{_esc(meta)}</div></div>'
        f'<span class="ok">✓ {_esc(badge)}</span>'
        '</div>'
    )


def chips(found=(), missing=(), dim=()):
    h = "".join(f'<span class="chip ok">✓ {_esc(c)}</span>' for c in found)
    h += "".join(f'<span class="chip miss">✕ {_esc(c)}</span>' for c in missing)
    h += "".join(f'<span class="chip dim">{_esc(c)}</span>' for c in dim)
    return h


def info_box(msg):
    return f'<div class="infobox">💡 {_esc(msg)}</div>'


def warn_box(msg):
    return f'<div class="warnbox">⚠️ {_esc(msg)}</div>'


def error_box(msg):
    return f'<div class="errbox">✕ {_esc(msg)}</div>'


# ------------------------------------------------------------------ PREVIEW TABLE
def preview_table(headers, rows, more_cols=0):
    th = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    body = ""
    if rows:
        body = "".join(
            "<tr>" + "".join(f"<td>{_esc(v)}</td>" for v in row) + "</tr>" for row in rows
        )
    else:
        body = f'<tr><td colspan="{max(len(headers), 1)}" style="color:var(--text-3)">no data rows</td></tr>'
    more = f'<div class="ptable-more">+ {more_cols} more columns in file…</div>' if more_cols > 0 else ""
    return (
        '<div class="ptable-wrap"><div class="inner-max">'
        f'<table class="ptable"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'
        f'</div>{more}</div>'
    )


# ------------------------------------------------------------------ STAT CARDS
def stat_cards(cards):
    """cards: list of (icon, value, label) tuples."""
    cells = []
    for i, (icon, val, label) in enumerate(cards):
        cells.append(
            f'<div class="stat-card" style="animation-delay:{i * 80}ms">'
            f'<div class="ic">{icon}</div><div class="v">{_esc(val)}</div>'
            f'<div class="l">{_esc(label)}</div></div>'
        )
    return '<div class="stats-row">' + "".join(cells) + "</div>"


# ------------------------------------------------------------------ TERMINAL
def _classify(line):
    if "❌" in line or "Error" in line:
        return "err"
    if "✅" in line:
        return "ok"
    if "⚠️" in line:
        return "warn"
    if line.startswith("⏳"):
        return "sys"
    return ""


_BADGES = {
    "LIVE": '<span class="term-live"><span class="pd"></span>PROCESSING</span>',
    "DONE": '<span class="term-live done"><span class="pd"></span>COMPLETED</span>',
    "FAIL": '<span class="term-live fail"><span class="pd"></span>FAILED</span>',
    "IDLE": '<span class="term-live idle"><span class="pd" style="animation:none"></span>IDLE</span>',
}


def terminal(logs, status="IDLE"):
    lines = []
    n = 1
    for msg in logs:
        for j, part in enumerate(str(msg).split("\n")):
            if not part.strip():
                continue
            cls = _classify(part)
            pre = f"{n:02d} ▸" if j == 0 else "   ·"
            lines.append(f'<div class="tl {cls}"><span class="pre">{pre}</span>{_esc(part)}</div>')
        n += 1
    if lines:
        body = "".join(lines[-200:])
    else:
        body = '<div class="tl term-empty">▸ awaiting job — upload a file and hit process <span class="cursor"></span></div>'
    badge = _BADGES.get(status, _BADGES["IDLE"])
    return (
        '<div class="term"><div class="term-head">'
        '<span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>'
        f'<span class="term-title">nad_processor — session.log</span>{badge}'
        f'</div><div class="term-body">{body}</div></div>'
    )


# ------------------------------------------------------------------ FOOTER
def footer():
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        '<div class="app-foot">'
        '<span>ZEAL NAD DATA PROCESSOR • v2.0 WEB</span>'
        f'<span>SESSION {stamp}</span>'
        '<span>CRAFTED BY <span class="cy">NIL</span> ⚡</span>'
        '</div>'
    )
