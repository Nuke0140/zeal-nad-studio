# ⚡ ZEAL NAD Data Processor — Web Edition

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-%E2%89%A51.49-ff4b4b)
![License](https://img.shields.io/badge/license-MIT-green)

A **premium Streamlit web app** that converts raw semester result exports into
**NAD-ready Excel files** and merges re-exam updates back into the master sheet —
a full web rebuild of the original CustomTkinter desktop tool, with every
processing rule preserved 1:1.

- ⚡ **NAD Report Generator** — CSV ➜ strict-column NAD upload Excel
- 🔗 **Re-exam Merge Engine** — overwrite matching `REGN_NO + RROLL` rows
- 🖥 **Live session terminal** — color-coded processing logs in real time
- 📊 **Rich job summaries** — records, duplicates, subjects, pass/ATKT, warnings
- 🎨 **Premium UI** — glassmorphism, animated gradients, dark / light themes
- 🔒 **100% client-side** — data never leaves the machine running the app

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## ☁️ Deploy on Streamlit Community Cloud (Free)

1. Push this folder to a **GitHub** repository (it is deployment-ready as-is).
2. Go to **https://share.streamlit.io** and sign in with GitHub.
3. Click **Create app → Deploy a public app from GitHub**.
4. Pick your repository, branch `main`, and set **Main file path** to `app.py`.
5. Click **Deploy** — your app is live in ~2 minutes. ✅

No secrets, no environment variables, no external services are required.

---

## 🗂 Project Structure

```
zeal-nad-streamlit/
├── app.py                    # Streamlit UI + orchestration
├── core/
│   ├── __init__.py
│   └── processor.py          # NAD generation + merge logic (1:1 from desktop)
├── styles/
│   ├── __init__.py
│   ├── theme.py              # Dark/light palettes + premium CSS engine
│   └── blocks.py             # Reusable HTML components (hero, terminal, cards…)
├── .streamlit/
│   └── config.toml           # Streamlit theme & server config
├── sample_data/
│   ├── sample_result.csv             # Raw semester export (6 students + 1 duplicate)
│   ├── sample_odd_master.xlsx        # Master file produced by Tab 1
│   └── sample_reexam_update.xlsx     # Re-exam update file for Tab 2
├── requirements.txt
├── LICENSE
├── README.md
└── .gitignore
```

## 🧪 Test Drive (sample data)

Both tabs can be tested instantly with the bundled `sample_data/` files:

1. **Tab 1** — upload `sample_result.csv` → **PROCESS FILE** → expect
   6 unique records, 1 duplicate removed, 4 subjects per student,
   5 Pass / 1 A.T.K.T, with the A.T.K.T student's CGPA/SGPA cleared.
2. **Tab 2** — upload `sample_odd_master.xlsx` (master) and
   `sample_reexam_update.xlsx` (update) → **MERGE DATA** → expect
   6 rows overwritten, 1 row added (`241099 • Kiran Joshi`), and the
   A.T.K.T student flipped to **Pass** by the re-exam update.

## 🧠 Business Rules Preserved (1:1 from the desktop edition)

- Duplicate `(Username, Course Code)` rows are removed — first occurrence wins
- Subjects are **reversed**: the last subject in the CSV becomes `SUB1`
- `FINAL_EXT` ➜ `TH` tag, `INT_MARKS` ➜ `CIE` tag; otherwise tags are derived
  from the *Custom Passing Result List* (e.g. `TH+CIE`)
- Subject codes ending in `P` are stripped (practical components)
- `A. T. K. T` students get CGPA/SGPA cleared; students with any `F` grade too
- "Pass without CGPA/SGPA" raises a data warning
- Overall `RESULT` uses `Promotion Note` (or an overall/final result column);
  if unavailable, it is inferred from subject results and failing grades.
- `REGN_NO`, `RROLL`, `ABC_ACCOUNT_ID` are forced to Excel **text format**
- A minimum of **11 subject column slots** is always generated
- Merge keys are `REGN_NO + RROLL`; non-null re-exam values overwrite the
  master; unmatched re-exam students are appended to the output

## 🎨 UI Notes

- The **🌙 Dark Mode** toggle in the sidebar switches the entire theme instantly
  (dark is the default and the flagship look).
- Typography: *Outfit* (UI) + *JetBrains Mono* (terminal, labels) via Google Fonts.
- The processing terminal intentionally stays dark in both themes — it is the app's console.

## 🛠 Tech Stack

Streamlit · Pandas · OpenPyXL · pure CSS design system (no heavy frontend deps)

---

Made by **Nil** ⚡ · ZEAL Education Group
