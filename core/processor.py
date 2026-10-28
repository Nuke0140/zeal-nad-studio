# -*- coding: utf-8 -*-
"""
ZEAL NAD Data Processor — Core Engine
======================================
1:1 port of the original desktop application logic (g6.py).

Every transformation rule, column sequence, dedup key, guard and Excel
formatting detail is preserved EXACTLY as in the desktop edition. Only the
I/O layer was adapted for the web: output workbooks are produced in
in-memory BytesIO buffers so they can be streamed straight to the browser
as downloads. Non-invasive additions: per-job statistics returned to the UI.
"""

import csv
import io
import re
from collections import OrderedDict
from datetime import datetime

import pandas as pd
from openpyxl.utils import get_column_letter

# ============================================================
# SHARED COLUMN DEFINITIONS
# ============================================================

BASE_COLUMNS = [
    "ORG_NAME","ACADEMIC_COURSE_ID","COURSE_NAME","STREAM","SESSION",
    "REGN_NO","RROLL","CNAME","AADHAAR_NAME","ADMISSION_YEAR",
    "GENDER","DOB","FNAME","MNAME","PHOTO","MRKS_REC_STATUS","RESULT",
    "YEAR","MONTH","PERCENT","DOI","CERT_NO","SEM","EXAM_TYPE",
    "TOT_CREDIT","TOT_CREDIT_POINTS","TOT_GRADE_POINTS","PREV_TOT_MRKS",
    "GRAND_TOT_MAX","GRAND_TOT_MIN","GRAND_TOT_MRKS","GRAND_TOT_CREDIT",
    "CGPA","REMARKS","SGPA","ABC_ACCOUNT_ID","TERM_TYPE","TOT_GRADE",
    "DEPARTMENT"
]

SUBJECT_SUFFIXES = ["", "NM", "GRADE", "GRADE_POINTS", "CREDIT",
                    "CREDIT_POINTS", "REMARKS", "CREDIT_ELIGIBILITY"]


def build_ordered_columns(pad_limit):
    """Build the strict column sequence (identical to the desktop edition).

    BASE columns first, then SUB1..SUBpad_limit with all suffix slots.
    Always pads to a minimum of 11 subject slots.
    """
    cols = BASE_COLUMNS.copy()
    for i in range(1, pad_limit + 1):
        for suffix in SUBJECT_SUFFIXES:
            if suffix == "":
                col = f"SUB{i}"
            elif suffix == "NM":
                col = f"SUB{i}NM"
            else:
                col = f"SUB{i}_{suffix}"
            if col not in cols:
                cols.append(col)
    return cols


# ============================================================
# FIELD NORMALIZERS (unchanged from desktop edition)
# ============================================================

def normalize_gender(g):
    g = (g or "").strip().lower()
    if g in ("male", "m"): return "M"
    if g in ("female", "f"): return "F"
    return "O"


def normalize_result(r):
    r = (r or "").strip().lower()
    if r == "sem_all_clear": return "Pass"
    if r == "sem_not_allclear": return "A. T. K. T"
    return r.title()


def clean_number(v):
    if v is None: return ""
    v = str(v).strip()
    if v == "" or v.lower() == "noe": return ""
    try:
        return float(v)
    except:
        return ""


def safe_text_id(v):
    if v is None:
        return ""
    v = str(v).strip()
    if v == "":
        return ""
    if "E+" in v.upper():
        try:
            return format(float(v), ".0f")
        except:
            return v
    return v


def extract_tags(custom_value):
    if not custom_value:
        return ""
    tags = []
    for part in custom_value.split():
        part_upper = part.upper()
        if "FINAL_EXT" in part_upper:
            tags.append("TH")
            continue
        if "INT_MARKS" in part_upper:
            tags.append("CIE")
            continue
        if ":" in part:
            tags.append(part.split(":")[0].upper())
    seen = set()
    final = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            final.append(t)
    return "+".join(final)


def extract_subject_map(headers):
    subjects = OrderedDict()
    for col in headers:
        if " - Subject - Subject Code" in col:
            sub = col.split(" - ")[0]
            subjects[sub] = {
                "code": f"{sub} - Subject - Subject Code",
                "name": f"{sub} - Subject - Subject Name",
                "grade": f"{sub} - Result - Grade",
                "grade_points": f"{sub} - Result - Grade Points",
                "credits": f"{sub} - Result - Credits for Result",
                "result": f"{sub} - Result - Result",
                "custom_result": f"{sub} - Result - Custom Passing Result List",
            }
    return subjects


# ============================================================
# SCRIPT 1 — NAD REPORT GENERATOR (CSV -> NAD Excel)
# ============================================================

def run_generate_report(input_file, log_func, progress_func=None, source_label=None):
    """Generate a NAD upload Excel from a raw semester result CSV.

    input_file : local path (str) | bytes | BytesIO | StringIO
    Returns dict: {ok, buffer, filename, stats}
    """
    result = {"ok": False, "buffer": None, "filename": None, "stats": {}}

    if input_file is None:
        log_func("❌ Please upload an input CSV file first.")
        return result

    output_file = f"nad_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    log_func(f"⏳ Processing: {source_label or 'uploaded CSV'}")

    # --- normalize input to a text stream (desktop used a plain file path) ---
    if isinstance(input_file, bytes):
        stream = io.StringIO(input_file.decode("utf-8-sig"))
    elif isinstance(input_file, io.StringIO):
        stream = input_file
    elif hasattr(input_file, "read"):
        stream = io.TextIOWrapper(input_file, encoding="utf-8-sig")
    else:
        stream = open(input_file, "r", encoding="utf-8-sig")

    rows_to_write = []
    seen_keys = set()
    stats = {"total_rows": 0, "unique_records": 0, "duplicates": 0,
             "max_subjects": 0, "pass": 0, "atkt": 0, "warnings": 0}

    try:
        reader = csv.DictReader(stream)
        subject_map = extract_subject_map(reader.fieldnames)
        rows = list(reader)
        total_rows = len(rows)
        stats["total_rows"] = total_rows
        max_subjects_found = 0

        if not reader.fieldnames:
            log_func("❌ Error generating report: CSV file is empty or unreadable.")
            return result

        log_func(f"📋 Parsed {total_rows:,} rows • {len(subject_map)} subject groups detected in header")

        for i, row in enumerate(rows):
            prn = row.get("Username")
            course = row.get("Course Code")
            sem = "I"

            unique_key = (prn, course, sem)
            if unique_key in seen_keys:
                continue
            seen_keys.add(unique_key)

            nad = {col: "" for col in BASE_COLUMNS}

            nad["ORG_NAME"] = ""
            nad["ACADEMIC_COURSE_ID"] = course
            nad["COURSE_NAME"] = "Bachelor of Technology"
            nad["STREAM"] = row.get("Course Name")
            nad["SESSION"] = "2024-25"

            regn = safe_text_id(row.get("Username"))
            nad["REGN_NO"] = regn if regn else ""  # Removed apostrophe

            rroll = safe_text_id(row.get("Univ Roll Number"))
            nad["RROLL"] = rroll if rroll else ""  # Removed apostrophe

            nad["CNAME"] = row.get("Full Name")
            nad["AADHAAR_NAME"] = row.get("Full Name")
            nad["ADMISSION_YEAR"] = row.get("Admission Year")
            nad["GENDER"] = normalize_gender(row.get("Gender"))
            nad["DOB"] = row.get("Date of Birth")
            nad["FNAME"] = ""
            nad["MNAME"] = row.get("Mother's First Name")

            nad["MRKS_REC_STATUS"] = "O"
            nad["RESULT"] = normalize_result(row.get("Promotion Note"))
            nad["YEAR"] = "2025"
            nad["DOI"] = "18-02-2025"
            nad["SEM"] = sem
            nad["EXAM_TYPE"] = "Regular"
            nad["TERM_TYPE"] = "Odd"
            nad["TOT_CREDIT"] = row.get("Completed Credits") or row.get("Total Completed Credits")
            nad["TOT_CREDIT_POINTS"] = ""
            nad["CGPA"] = row.get("CGPA")
            nad["SGPA"] = row.get("SGPA")

            if nad["RESULT"] == "A. T. K. T":
                nad["CGPA"] = ""
                nad["SGPA"] = ""
            elif nad["RESULT"] == "Pass":
                if not nad["CGPA"] or not nad["SGPA"]:
                    stats["warnings"] += 1
                    log_func(f"⚠️ Warning: Student {nad['REGN_NO']} is Pass but missing CGPA/SGPA")

            if nad["RESULT"] == "Pass":
                stats["pass"] += 1
            elif nad["RESULT"] == "A. T. K. T":
                stats["atkt"] += 1

            nad["ABC_ACCOUNT_ID"] = safe_text_id(row.get("ABC Id"))

            student_subjects = []
            total_grade_points = 0.0
            total_credit_points = 0.0

            for sub, cols in subject_map.items():
                gp = clean_number(row.get(cols["grade_points"]))
                cr = clean_number(row.get(cols["credits"]))
                grade = row.get(cols["grade"], "")
                res = (row.get(cols["result"]) or "").upper()

                if gp != "":
                    total_grade_points += gp
                if gp != "" and cr != "":
                    total_credit_points += gp * cr

                if grade or gp != "" or cr != "" or res:
                    student_subjects.append((sub, cols))

            nad["TOT_GRADE_POINTS"] = round(total_grade_points, 2) if total_grade_points > 0 else ""
            nad["TOT_CREDIT_POINTS"] = round(total_credit_points, 2) if total_credit_points > 0 else ""

            # --- REVERSE THE ACTUAL SUBJECT ORDER FROM THE CSV: last subject becomes SUB1 ---
            student_subjects.reverse()

            max_subjects_found = max(max_subjects_found, len(student_subjects))

            for idx, (sub, cols) in enumerate(student_subjects, start=1):
                base_code = row.get(cols["code"], "")
                custom = row.get(cols["custom_result"], "")

                if base_code.upper().endswith("P"):
                    base_code = base_code[:-1]

                if base_code.upper().endswith("FINAL_EXT"):
                    base_code = base_code.rsplit("-", 1)[0]
                    tags = "TH"
                elif base_code.upper().endswith("INT_MARKS"):
                    base_code = base_code.rsplit("-", 1)[0]
                    tags = "CIE"
                else:
                    tags = extract_tags(custom)

                nad[f"SUB{idx}"] = f"{base_code}-{tags}" if tags else base_code
                nad[f"SUB{idx}NM"] = row.get(cols["name"], "")
                nad[f"SUB{idx}_GRADE"] = row.get(cols["grade"], "")

                gp = clean_number(row.get(cols["grade_points"]))
                cr = clean_number(row.get(cols["credits"]))
                res = (row.get(cols["result"]) or "").upper()

                nad[f"SUB{idx}_GRADE_POINTS"] = gp
                nad[f"SUB{idx}_CREDIT"] = cr
                nad[f"SUB{idx}_CREDIT_POINTS"] = gp * cr if gp != "" and cr != "" else ""
                nad[f"SUB{idx}_REMARKS"] = ""
                nad[f"SUB{idx}_CREDIT_ELIGIBILITY"] = "Y" if res == "PASS" else "N"

            if any(nad.get(f"SUB{j}_GRADE") == "F" for j in range(1, len(student_subjects) + 1)):
                nad["CGPA"] = ""
                nad["SGPA"] = ""

            rows_to_write.append(nad)

            # Throttled Progress Update
            if progress_func and total_rows > 0:
                if (i + 1) % 10 == 0 or (i + 1) == total_rows:
                    progress_func((i + 1) / total_rows)

        # --- ENFORCE STRICT COLUMN SEQUENCE ---
        stats["duplicates"] = total_rows - len(rows_to_write)
        stats["unique_records"] = len(rows_to_write)
        stats["max_subjects"] = max_subjects_found

        pad_limit = max(11, max_subjects_found)
        final_ordered_columns = build_ordered_columns(pad_limit)

        # dtype=object keeps mixed ""/float columns stable (no dtype coercion)
        df = pd.DataFrame(rows_to_write, columns=final_ordered_columns, dtype=object)
        df[df.isna()] = ""

        # --- produce the workbook in an in-memory buffer (was: local file) ---
        output_buffer = io.BytesIO()
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")

            # --- FORCE EXCEL TEXT FORMAT FOR IDs ---
            worksheet = writer.sheets["Sheet1"]
            text_columns = ["REGN_NO", "RROLL", "ABC_ACCOUNT_ID"]
            for col_name in text_columns:
                if col_name in df.columns:
                    col_idx = df.columns.get_loc(col_name) + 1
                    col_letter = get_column_letter(col_idx)
                    for cell in worksheet[col_letter]:
                        cell.number_format = '@'  # '@' is Excel format for Text

        result["ok"] = True
        result["buffer"] = output_buffer
        result["filename"] = output_file
        result["stats"] = stats

        log_func("✅ NAD EXCEL GENERATED SUCCESSFULLY")
        log_func(f"📁 File: {output_file}")
        log_func(f"🧹 Unique records: {len(df):,} • Duplicates removed: {stats['duplicates']:,}")

    except Exception as e:
        log_func(f"❌ Error generating report: {str(e)}")

    return result


# ============================================================
# SCRIPT 2 — MERGE TWO FILES (odd semester master + re-exam update)
# ============================================================

def run_merge_files(odd_sem_file, re_exam_file, log_func, progress_func=None,
                    odd_label=None, re_label=None):
    """Merge a re-exam update workbook back into the odd-semester master.

    Re-exam values overwrite master rows matching (REGN_NO, RROLL);
    unmatched re-exam rows are appended. Keys/behaviour unchanged.

    Returns dict: {ok, buffer, filename, stats}
    """
    result = {"ok": False, "buffer": None, "filename": None, "stats": {}}

    if odd_sem_file is None or re_exam_file is None:
        log_func("❌ Please upload both Excel files first.")
        return result

    output_file = f"final_odd_sem_updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    KEY_COLS = ["REGN_NO", "RROLL"]

    log_func("⏳ Starting merge process...")
    log_func(f"⏳ Master file: {odd_label or 'odd_semester.xlsx'}")
    log_func(f"⏳ Update file: {re_label or 're_exam.xlsx'}")

    try:
        odd_df = pd.read_excel(odd_sem_file, engine="openpyxl")
        re_df = pd.read_excel(re_exam_file, engine="openpyxl")

        odd_df.columns = odd_df.columns.str.strip()
        re_df.columns = re_df.columns.str.strip()

        for col in KEY_COLS:
            if col in odd_df.columns:
                odd_df[col] = odd_df[col].astype(str).str.strip()
            if col in re_df.columns:
                re_df[col] = re_df[col].astype(str).str.strip()

        # --- DYNAMIC COLUMN GENERATION FOR MERGE ---
        max_sub = 0
        for col in set(odd_df.columns).union(re_df.columns):
            match = re.match(r'^SUB(\d+)', col)
            if match:
                max_sub = max(max_sub, int(match.group(1)))

        pad_limit = max(11, max_sub)
        final_columns = build_ordered_columns(pad_limit)

        # Append any extra unrecognized columns from both dataframes
        for col in list(odd_df.columns) + list(re_df.columns):
            if col not in final_columns:
                final_columns.append(col)

        odd_df.set_index(KEY_COLS, inplace=True)
        re_df.set_index(KEY_COLS, inplace=True)

        cols_no_index = [c for c in final_columns if c not in KEY_COLS]
        odd_df = odd_df.reindex(columns=cols_no_index)
        re_df = re_df.reindex(columns=cols_no_index)

        common_index = odd_df.index.intersection(re_df.index)
        total_ops = len(common_index)

        for i, idx in enumerate(common_index):
            for col in odd_df.columns:
                val = re_df.at[idx, col]
                if pd.notna(val):
                    odd_df.at[idx, col] = val

            # Throttled Progress Update
            if progress_func and total_ops > 0:
                if (i + 1) % 5 == 0 or (i + 1) == total_ops:
                    progress_func((i + 1) / total_ops)

        extra = re_df.loc[~re_df.index.isin(odd_df.index)]
        final_df = pd.concat([odd_df, extra])

        final_df.reset_index(inplace=True)
        final_df = final_df[final_columns]

        # --- produce the workbook in an in-memory buffer (was: local file) ---
        output_buffer = io.BytesIO()
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            final_df.to_excel(writer, index=False, sheet_name="Sheet1")

            # --- FORCE EXCEL TEXT FORMAT FOR IDs ---
            worksheet = writer.sheets["Sheet1"]
            text_columns = ["REGN_NO", "RROLL", "ABC_ACCOUNT_ID"]
            for col_name in text_columns:
                if col_name in final_df.columns:
                    col_idx = final_df.columns.get_loc(col_name) + 1
                    col_letter = get_column_letter(col_idx)
                    for cell in worksheet[col_letter]:
                        cell.number_format = '@'

        stats = {
            "matched": int(total_ops),
            "added": int(len(extra)),
            "total": int(len(final_df)),
            "columns": int(len(final_columns)),
        }
        result["ok"] = True
        result["buffer"] = output_buffer
        result["filename"] = output_file
        result["stats"] = stats

        log_func("✅ MERGE COMPLETED SUCCESSFULLY")
        log_func(f"📁 Output file: {output_file}")
        log_func(f"🧩 Rows overwritten: {total_ops:,} • Rows added: {len(extra):,} • Total: {len(final_df):,}")
        log_func(f"📊 Columns preserved: {len(final_columns)}")

    except Exception as e:
        log_func(f"❌ Error merging files: {str(e)}")

    return result
