# -*- coding: utf-8 -*-
"""
⚡ ZEAL NAD DATA PROCESSOR — Premium Web Edition
================================================
Streamlit rebuild of the original CustomTkinter desktop tool.

Run locally:   streamlit run app.py
Deploy:        share.streamlit.io  (main file path: app.py)
"""

import csv as csv_mod
import io

import pandas as pd
import streamlit as st

from core.processor import run_generate_report, run_merge_files
from styles.blocks import (chips, error_box, file_chip, footer, fmt_size, hero,
                           info_box, preview_table, sec_head, sidebar_credit,
                           sidebar_guide, sidebar_logo, stat_cards, terminal,
                           warn_box)
from styles.theme import get_palette, inject_css

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

st.set_page_config(
    page_title="Zeal • NAD Data Processor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# THEME + SIDEBAR
# ------------------------------------------------------------------
dark_mode = st.session_state.get("dark_mode", True)
st.markdown(inject_css(get_palette(dark_mode)), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(sidebar_logo(), unsafe_allow_html=True)
    st.toggle("🌙  Dark Mode", value=dark_mode, key="dark_mode")
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(sidebar_guide(), unsafe_allow_html=True)
    st.markdown(sidebar_credit(), unsafe_allow_html=True)

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
st.markdown(hero(), unsafe_allow_html=True)
tab_gen, tab_merge = st.tabs(["⚡  GENERATE REPORT", "🔗  MERGE FILES"])

# ==================================================================
# TAB 1 — GENERATE NAD REPORT
# ==================================================================
with tab_gen:
    st.markdown(sec_head("01", "UPLOAD SEMESTER RESULT CSV"), unsafe_allow_html=True)
    up = st.file_uploader("Semester result CSV", type=["csv"], key="csv_up",
                          label_visibility="collapsed")

    ready = False
    if up is not None:
        raw = up.getvalue()
        text = raw.decode("utf-8-sig", errors="replace")

        headers, sample_rows = [], []
        try:
            reader = csv_mod.reader(io.StringIO(text))
            headers = next(reader, [])
            for k, row in enumerate(reader):
                sample_rows.append(row)
                if k >= 5:
                    break
        except csv_mod.Error:
            pass

        est_rows = max(text.count("\n") - 1, 0)
        st.markdown(file_chip(up.name, f"{fmt_size(len(raw))} • ~{est_rows:,} data rows • UTF-8 CSV"),
                    unsafe_allow_html=True)

        core_cols = ["Username", "Course Code", "Full Name"]
        missing_core = [c for c in core_cols if c not in headers]
        subject_groups = sum(1 for h in headers if " - Subject - Subject Code" in str(h))

        st.markdown(
            "<div style='margin-top:10px'>"
            + chips(found=[c for c in core_cols if c in headers],
                    missing=missing_core,
                    dim=[f"{subject_groups} subject groups", f"{len(headers)} columns detected"])
            + "</div>",
            unsafe_allow_html=True,
        )

        if missing_core:
            st.markdown(
                warn_box(f"Required columns missing: {', '.join(missing_core)}. "
                         "Please upload the raw ERP export containing these fields."),
                unsafe_allow_html=True)
        elif subject_groups == 0:
            st.markdown(
                warn_box("No subject column groups found in the header — the generated report "
                         "will contain student details only."),
                unsafe_allow_html=True)

        if sample_rows:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            st.markdown(preview_table(headers[:9], [r[:9] for r in sample_rows],
                                      more_cols=max(len(headers) - 9, 0)),
                        unsafe_allow_html=True)

        ready = not missing_core
    else:
        st.markdown(info_box("Upload the raw semester result CSV exported from your ERP. "
                             "Subject columns are auto-detected from the header row — "
                             "zero configuration needed."), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    run_gen = st.button("⚡  PROCESS FILE  —  GENERATE NAD EXCEL", key="gen_run",
                        type="primary", width="stretch", disabled=not ready)

    if run_gen and up is not None:
        st.session_state.gen_logs = []
        st.session_state.gen_status = "LIVE"
        st.session_state.gen_progress = 0.0
        st.session_state.gen_ptext = "Initializing engine…"
        st.session_state.gen_result = None

        live_log = st.empty()
        live_log.markdown(terminal([], "LIVE"), unsafe_allow_html=True)
        pbar = st.progress(0.0, text=st.session_state.gen_ptext)

        def log_func(msg):
            st.session_state.gen_logs.append(msg)
            live_log.markdown(terminal(st.session_state.gen_logs, "LIVE"), unsafe_allow_html=True)

        def prog(v):
            st.session_state.gen_progress = float(v)
            st.session_state.gen_ptext = f"Transforming rows… {int(v * 100)}%"
            pbar.progress(min(float(v), 1.0), text=st.session_state.gen_ptext)

        res = run_generate_report(io.StringIO(text), log_func, prog, source_label=up.name)

        if res["ok"]:
            st.session_state.gen_result = {
                "bytes": res["buffer"].getvalue(),
                "filename": res["filename"],
                "stats": res["stats"],
            }
            st.session_state.gen_status = "DONE"
            st.session_state.gen_ptext = "✓ Completed — NAD file ready for download"
        else:
            st.session_state.gen_status = "FAIL"
            st.session_state.gen_ptext = "✗ Processing failed — inspect the log below"
        st.session_state.gen_progress = 1.0
        pbar.progress(1.0, text=st.session_state.gen_ptext)

    if (not run_gen) and st.session_state.get("gen_status") in ("LIVE", "DONE", "FAIL"):
        st.progress(st.session_state.get("gen_progress", 0.0),
                    text=st.session_state.get("gen_ptext", ""))
        st.markdown(terminal(st.session_state.get("gen_logs", []),
                             st.session_state.get("gen_status", "IDLE")), unsafe_allow_html=True)

    if st.session_state.get("gen_status") == "FAIL" and not run_gen:
        st.markdown(error_box("Processing failed — review the terminal log above, fix the "
                              "input file and try again."), unsafe_allow_html=True)

    gen_result = st.session_state.get("gen_result")
    if gen_result:
        s = gen_result["stats"]
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown(sec_head("02", "JOB SUMMARY"), unsafe_allow_html=True)
        st.markdown(stat_cards([
            ("🎓", f"{s.get('unique_records', 0):,}", "Unique Records"),
            ("🧹", f"{s.get('duplicates', 0):,}", "Duplicates Removed"),
            ("📚", str(s.get("max_subjects", 0)), "Subjects (Max)"),
            ("✅", f"{s.get('pass', 0):,}", "Pass"),
            ("⚠️", f"{s.get('atkt', 0):,}", "A.T.K.T."),
            ("🔔", str(s.get("warnings", 0)), "Data Warnings"),
        ]), unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(file_chip(gen_result["filename"],
                              f"{fmt_size(len(gen_result['bytes']))} • NAD upload format • 11+ subject slots"),
                    unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        dlc, rst = st.columns([4, 1])
        with dlc:
            st.download_button("⬇️  DOWNLOAD NAD EXCEL FILE", data=gen_result["bytes"],
                               file_name=gen_result["filename"], mime=XLSX_MIME,
                               key="gen_dl", type="primary", width="stretch")
        with rst:
            if st.button("↺ RESET", key="gen_reset", type="secondary", width="stretch"):
                for k in ("gen_logs", "gen_status", "gen_progress", "gen_ptext", "gen_result"):
                    st.session_state.pop(k, None)
                st.rerun()

# ==================================================================
# TAB 2 — MERGE FILES
# ==================================================================
with tab_merge:
    mc1, mc2 = st.columns(2, gap="medium")

    with mc1:
        st.markdown(sec_head("01", "ODD SEMESTER MASTER FILE"), unsafe_allow_html=True)
        odd_up = st.file_uploader("Odd semester master", type=["xlsx"], key="odd_up",
                                  label_visibility="collapsed")
        odd_ready = False
        if odd_up is not None:
            odd_bytes = odd_up.getvalue()
            odd_cols = [str(c).strip() for c in pd.read_excel(io.BytesIO(odd_bytes), nrows=0).columns]
            odd_missing = [c for c in ("REGN_NO", "RROLL") if c not in odd_cols]

            st.markdown(file_chip(odd_up.name, f"{fmt_size(len(odd_bytes))} • {len(odd_cols)} columns • XLSX"),
                        unsafe_allow_html=True)
            st.markdown(
                "<div style='margin-top:10px'>"
                + chips(found=[c for c in ("REGN_NO", "RROLL") if c in odd_cols],
                        missing=odd_missing, dim=[f"{len(odd_cols)} columns"])
                + "</div>",
                unsafe_allow_html=True)

            if odd_missing:
                st.markdown(warn_box(f"Merge keys missing: {', '.join(odd_missing)} — "
                                     "this file cannot be merged."), unsafe_allow_html=True)

            odd_prev = pd.read_excel(io.BytesIO(odd_bytes), nrows=5).fillna("")
            if len(odd_prev):
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.markdown(preview_table(list(odd_prev.columns[:7]),
                                          odd_prev.iloc[:, :7].values.tolist(),
                                          more_cols=max(len(odd_prev.columns) - 7, 0)),
                            unsafe_allow_html=True)
            odd_ready = not odd_missing
        else:
            st.markdown(info_box("Upload the master NAD Excel generated in Tab 1 "
                                 "(or your previously merged master sheet)."), unsafe_allow_html=True)

    with mc2:
        st.markdown(sec_head("02", "RE-EXAM / UPDATE FILE"), unsafe_allow_html=True)
        re_up = st.file_uploader("Re-exam update", type=["xlsx"], key="re_up",
                                 label_visibility="collapsed")
        re_ready = False
        if re_up is not None:
            re_bytes = re_up.getvalue()
            re_cols = [str(c).strip() for c in pd.read_excel(io.BytesIO(re_bytes), nrows=0).columns]
            re_missing = [c for c in ("REGN_NO", "RROLL") if c not in re_cols]

            st.markdown(file_chip(re_up.name, f"{fmt_size(len(re_bytes))} • {len(re_cols)} columns • XLSX"),
                        unsafe_allow_html=True)
            st.markdown(
                "<div style='margin-top:10px'>"
                + chips(found=[c for c in ("REGN_NO", "RROLL") if c in re_cols],
                        missing=re_missing, dim=[f"{len(re_cols)} columns"])
                + "</div>",
                unsafe_allow_html=True)

            if re_missing:
                st.markdown(warn_box(f"Merge keys missing: {', '.join(re_missing)} — "
                                     "this file cannot be merged."), unsafe_allow_html=True)

            re_prev = pd.read_excel(io.BytesIO(re_bytes), nrows=5).fillna("")
            if len(re_prev):
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.markdown(preview_table(list(re_prev.columns[:7]),
                                          re_prev.iloc[:, :7].values.tolist(),
                                          more_cols=max(len(re_prev.columns) - 7, 0)),
                            unsafe_allow_html=True)
            re_ready = not re_missing
        else:
            st.markdown(info_box("Upload the re-exam result file — rows matching "
                                 "REGN_NO + RROLL will overwrite the master."), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    run_mrg = st.button("🔗  MERGE DATA  —  OVERWRITE & CONSOLIDATE", key="merge_run",
                        type="tertiary", width="stretch",
                        disabled=not (odd_ready and re_ready))

    if run_mrg and odd_ready and re_ready:
        st.session_state.merge_logs = []
        st.session_state.merge_status = "LIVE"
        st.session_state.merge_progress = 0.0
        st.session_state.merge_ptext = "Initializing merge engine…"
        st.session_state.merge_result = None

        live_log = st.empty()
        live_log.markdown(terminal([], "LIVE"), unsafe_allow_html=True)
        pbar = st.progress(0.0, text=st.session_state.merge_ptext)

        def log_func(msg):
            st.session_state.merge_logs.append(msg)
            live_log.markdown(terminal(st.session_state.merge_logs, "LIVE"), unsafe_allow_html=True)

        def prog(v):
            st.session_state.merge_progress = float(v)
            st.session_state.merge_ptext = f"Merging records… {int(v * 100)}%"
            pbar.progress(min(float(v), 1.0), text=st.session_state.merge_ptext)

        res = run_merge_files(io.BytesIO(odd_bytes), io.BytesIO(re_bytes), log_func, prog,
                              odd_label=odd_up.name, re_label=re_up.name)

        if res["ok"]:
            st.session_state.merge_result = {
                "bytes": res["buffer"].getvalue(),
                "filename": res["filename"],
                "stats": res["stats"],
            }
            st.session_state.merge_status = "DONE"
            st.session_state.merge_ptext = "✓ Completed — merged file ready for download"
        else:
            st.session_state.merge_status = "FAIL"
            st.session_state.merge_ptext = "✗ Merge failed — inspect the log below"
        st.session_state.merge_progress = 1.0
        pbar.progress(1.0, text=st.session_state.merge_ptext)

    if (not run_mrg) and st.session_state.get("merge_status") in ("LIVE", "DONE", "FAIL"):
        st.progress(st.session_state.get("merge_progress", 0.0),
                    text=st.session_state.get("merge_ptext", ""))
        st.markdown(terminal(st.session_state.get("merge_logs", []),
                             st.session_state.get("merge_status", "IDLE")), unsafe_allow_html=True)

    if st.session_state.get("merge_status") == "FAIL" and not run_mrg:
        st.markdown(error_box("Merge failed — review the terminal log above and verify both "
                              "files contain the REGN_NO and RROLL columns."), unsafe_allow_html=True)

    merge_result = st.session_state.get("merge_result")
    if merge_result:
        m = merge_result["stats"]
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown(sec_head("03", "MERGE SUMMARY"), unsafe_allow_html=True)
        st.markdown(stat_cards([
            ("🔁", f"{m.get('matched', 0):,}", "Rows Overwritten"),
            ("➕", f"{m.get('added', 0):,}", "Rows Added"),
            ("🧾", f"{m.get('total', 0):,}", "Total Output Rows"),
            ("🗂️", str(m.get("columns", 0)), "Columns Preserved"),
        ]), unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(file_chip(merge_result["filename"],
                              f"{fmt_size(len(merge_result['bytes']))} • master + re-exam consolidated • text-safe IDs"),
                    unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        dlc, rst = st.columns([4, 1])
        with dlc:
            st.download_button("⬇️  DOWNLOAD MERGED EXCEL FILE", data=merge_result["bytes"],
                               file_name=merge_result["filename"], mime=XLSX_MIME,
                               key="merge_dl", type="primary", width="stretch")
        with rst:
            if st.button("↺ RESET", key="merge_reset", type="secondary", width="stretch"):
                for k in ("merge_logs", "merge_status", "merge_progress", "merge_ptext", "merge_result"):
                    st.session_state.pop(k, None)
                st.rerun()

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
st.markdown(footer(), unsafe_allow_html=True)
