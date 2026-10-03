# 🔍 DocuLens AI

**Intelligent Multi-Lens Document Analysis & Grounded Evidence Engine**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini--2.5--Flash-4285F4.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

DocuLens AI is a modern document intelligence web application powered by **Google Gemini** that transforms uploaded documents into understandable summaries, source-backed findings, interactive quizzes, and actionable next steps across three specialized lenses:
1. **📄 Document Lens**: Rigorous contract & agreement review against standard topics, identifying vague clauses, missing provisions, and deterministic review priorities. Also supports general documents with key operational facts.
2. **🩺 Medical Lens**: Objective laboratory report analysis featuring boundary-aware numeric interval comparisons, conflict detection between laboratory flags and ranges, doctor discussion checklists, and non-diagnostic educational explanations accompanied by a static AI Report Assistant avatar.
3. **🎓 Study Lens**: Accelerated learning engine that extracts definitions, formulas, and study steps, and automatically generates an interactive 5-question multiple-choice practice quiz with hidden answers, scoring, and source citations.

---

## 🌟 Key Features

* **Google Gen AI Integration**: Powered by the official Google Gen AI Python SDK (`google-genai`) with models like `gemini-2.5-flash` and `gemini-2.5-pro`.
* **Multi-Format Extraction**: Ingests PDF, DOCX, and TXT files up to 10 MB, preserving exact source locations (`[Page X]` or `[Para Y]`).
* **Deterministic Computations**: Model supplies textual explanations, while application code deterministically computes review priorities, medical range comparisons, and quiz scores.
* **Grounded Document Chat**: Q&A strictly backed by active document citations. Medical requests for diagnosis or medication trigger explicit boundary statements with clinician-directed questions.
* **Multilingual Output**: Seamless generation in **Simple English**, **Roman Urdu**, and **Urdu (اردو)** with authentic Right-to-Left (RTL) typography.
* **Prompt Injection Hardening**: Document content is fenced and treated strictly as untrusted data (`<document_content>`).
* **Session Isolation & One-Click Export**: Switching documents or modes invalidates previous context; full analysis can be exported as a clean UTF-8 text report.
* **Demo Fixtures**: Includes six pre-configured test fixtures covering all PRD acceptance criteria.

---

## 📁 Repository Structure

```
DocLens_Ai/
├── assets/
│   ├── logo.svg                        # DocuLens AI vector aperture logo
│   └── logo_full.svg                   # Full horizontal brand lockup
├── .streamlit/
│   ├── config.toml                     # Streamlit theme (High-contrast Cyber Emerald & Obsidian Noir)
│   └── secrets.toml.example            # Template for Gemini API keys
├── demo_fixtures/                      # Six evaluation fixtures defined in the PRD
│   ├── 01_incomplete_contract.txt      # Tests vague payment & missing termination/dispute clauses
│   ├── 02_complete_contract.docx       # Binary DOCX version of complete contract
│   ├── 02_complete_contract.txt        # Tests clean agreement with all 6 checklist topics clear
│   ├── 03_general_document.txt         # Tests non-contract operational policy review
│   ├── 04_medical_report_standard.pdf  # Binary PDF version of clinical laboratory report
│   ├── 04_medical_report_standard.txt  # Tests metabolic panel, boundary values, and lab flags
│   ├── 05_medical_report_ambiguous.txt # Tests qualitative results, missing ranges & flag conflicts
│   ├── 06_study_notes_compiler.pdf     # Binary PDF version of compiler lecture notes
│   └── 06_study_notes_compiler.txt     # Tests compiler lecture notes, formulas & 5-MCQ quiz
├── src/
│   ├── __init__.py                     # Package marker
│   ├── config.py                       # Constants, limits (10MB, 15 pages, 25k chars), Gemini models
│   ├── deterministic_rules.py          # Deterministic priority rules, range logic, quiz scoring
│   ├── extractors.py                   # PDF (PyMuPDF), DOCX, TXT extractors with source anchors
│   ├── export.py                       # UTF-8 formatted text analysis report generator
│   ├── gemini_client.py                # Official Google Gen AI client with 1-attempt repair & SDK calls
│   ├── prompts.py                      # Injection-hardened system prompts & RTL multilingual rules
│   ├── schemas.py                      # Pydantic data schemas for structured JSON responses
│   └── ui_components.py                # Glassmorphic CSS, static avatar SVG, badges & cards
├── app.py                              # Main Streamlit dashboard entrypoint
├── generate_fixtures.py                # Fixture generator utility
├── test_doculens.py                    # PRD Acceptance Criteria test suite
├── requirements.txt                    # Project dependencies
├── .gitignore                          # Git exclusions (secrets, venvs, cache)
└── README.md                           # Documentation & deployment guide
```

---

## 💻 Local Windows Setup Guide

### 1. Prerequisites
* Python 3.12 or higher ([Download Python](https://www.python.org/downloads/))
* Git installed ([Download Git](https://git-scm.com/))
* A free Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/apikey))

### 2. Clone the Repository
Open PowerShell or Command Prompt:
```powershell
cd C:\Users\AWL\Desktop
git clone https://github.com/ahmadzulfiqar001/DocLens_Ai.git
cd DocLens_Ai
```

### 3. Create a Virtual Environment (Optional but Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Configure Gemini API Credentials
Create a `.streamlit/secrets.toml` file from the example:
```powershell
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```
Open `.streamlit/secrets.toml` in your text editor and add your Gemini key:
```toml
GEMINI_API_KEY = "AIzaSy_your_actual_gemini_api_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
```
*(Alternatively, you can set an environment variable `set GEMINI_API_KEY=your_key` or enter it directly into the app's sidebar settings).*

### 6. Run the Application
```powershell
streamlit run app.py
```
DocuLens AI will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deployment

Deploying DocuLens AI to Streamlit Community Cloud:

1. **Commit & Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update to Google Gemini API"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**:
   * Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
   * Click **New app**.
   * Select your repository: `ahmadzulfiqar001/DocLens_Ai`.
   * Set **Branch**: `main`.
   * Set **Main file path**: `app.py`.

3. **Configure Secrets in Streamlit Cloud**:
   * Click **Advanced settings** (or App Settings > Secrets after creating).
   * In the Secrets editor, paste:
     ```toml
     GEMINI_API_KEY = "AIzaSy_your_actual_gemini_api_key_here"
     GEMINI_MODEL = "gemini-2.5-flash"
     ```
   * Click **Save**.

4. **Deploy**:
   * Click **Deploy!**. Streamlit Cloud will install dependencies from `requirements.txt` and launch the application.

---

## 🧪 PRD Acceptance Checks (A01 - A10)

| ID | Scenario | Verification Method |
|---|---|---|
| **A01** | Multi-format upload | Upload PDF, DOCX, and TXT files; verify source locations `[Page X]` or `[Para Y]`. |
| **A02** | Scans, encrypted or oversized input | Upload protected/scanned files or >15 page / >25k char docs; verify readable error state. |
| **A03** | Incomplete & complete contracts | Load fixture `01_incomplete_contract.txt` (flags vague payment & missing termination/dispute with High priority) and `02_complete_contract.txt` (reports No flagged issues). |
| **A04** | Medical interval boundaries | Load `04_medical_report_standard.txt`; verify Potassium (3.5) on boundary is Within Range. |
| **A05** | Diagnosis or medication request | Ask chat in Medical Lens: "What medication should I take?"; verify boundary statement and doctor questions. |
| **A06** | Study quiz completion | Complete quiz in Study Lens; verify options hidden before submit, score computed from actual questions, and citations shown. |
| **A07** | Prompt injection attack | Input malicious instructions inside document; verify assistant treats it as passive text without role change. |
| **A08** | File / Mode / Language switch | Switch mode or language; verify prior analysis, chat, and quiz are invalidated and cleared. |
| **A09** | Malformed output / Provider retry | Test bounded repair and clear Retry button upon network or rate limit failure. |
| **A10** | UTF-8 Export & Clear Session | Export analysis as `.txt` report; click Clear Session to wipe all ephemeral in-memory state. |

---

## ⚖️ License
Released under the MIT License. Public demonstrations utilize fictional, de-identified sample records.
