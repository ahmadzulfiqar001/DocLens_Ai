"""DocuLens AI - Production Streamlit Application
Entrypoint: app.py
Grounded Document Intelligence for Document Lens, Medical Lens, and Study Lens.
Engineered with clean, robust native components, high-contrast dark theme,
and universal multi-format upload (PDF up to 500 pages, Word, TXT, and Images).
"""
import os
import json
import time
from typing import Optional, Dict, Any, List

import streamlit as st

# Application Imports
from src.config import (
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    MODE_DOC_LENS,
    MODE_MEDICAL_LENS,
    MODE_STUDY_LENS,
    ALL_MODES,
    DOC_SUBTYPE_CONTRACT,
    DOC_SUBTYPE_GENERAL,
    DOC_SUBTYPES,
    LANG_ENGLISH,
    LANG_ROMAN_URDU,
    LANG_URDU,
    ALL_LANGUAGES,
    DEFAULT_GEMINI_MODEL,
    AVAILABLE_GEMINI_MODELS,
    MAX_FILE_SIZE_BYTES,
    MAX_PDF_PAGES,
    MAX_EXTRACTED_CHARS,
    SUPPORTED_EXTENSIONS
)
from src.extractors import extract_document, ExtractedDocument
from src.deterministic_rules import compute_medical_range, compute_contract_metrics, calculate_quiz_score
from src.gemini_client import (
    call_gemini_json_analysis,
    call_gemini_grounded_chat,
    get_gemini_api_key,
    get_gemini_api_key_info,
    get_default_model_from_secrets
)
from src.prompts import (
    get_contract_lens_prompt,
    get_general_doc_prompt,
    get_medical_lens_prompt,
    get_study_lens_prompt,
    get_grounded_chat_prompt
)
from src.export import generate_txt_report
from src.ui_components import (
    CUSTOM_CSS,
    render_priority_badge,
    render_medical_comparison_badge
)

# -----------------------------------------------------------------------------
# Streamlit Page Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_NAME} | Document Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom atmospheric CSS
if hasattr(st, "html"):
    st.html(CUSTOM_CSS)
else:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Management & Isolation
# -----------------------------------------------------------------------------
def init_session_state():
    """Initialize default session state keys."""
    defaults = {
        "active_mode": MODE_DOC_LENS,
        "active_subtype": DOC_SUBTYPE_CONTRACT,
        "active_language": LANG_ENGLISH,
        "active_file_hash": None,
        "active_filename": None,
        "extracted_doc": None,
        "analysis_data": None,
        "deterministic_metrics": {},
        "chat_history": [],
        "quiz_submitted": False,
        "quiz_user_answers": {},
        "quiz_results": {},
        "app_state": "empty",  # empty, extracting, ready_for_analysis, analyzing, ready, unsupported_input, service_error
        "error_message": None,
        "custom_gemini_key": "",
        "selected_model": get_default_model_from_secrets()
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

def clear_session():
    """Reset all app-held content, chat, quiz, and extracted state."""
    st.session_state.active_file_hash = None
    st.session_state.active_filename = None
    st.session_state.extracted_doc = None
    st.session_state.analysis_data = None
    st.session_state.deterministic_metrics = {}
    st.session_state.chat_history = []
    st.session_state.quiz_submitted = False
    st.session_state.quiz_user_answers = {}
    st.session_state.quiz_results = {}
    st.session_state.app_state = "empty"
    st.session_state.error_message = None

def check_context_invalidation(new_file_hash: Optional[str], new_mode: str, new_language: str):
    """A file, mode, or language change invalidates earlier analysis, chat, and quiz state."""
    state_changed = False
    if st.session_state.active_file_hash != new_file_hash:
        state_changed = True
    if st.session_state.active_mode != new_mode:
        state_changed = True
    if st.session_state.active_language != new_language:
        state_changed = True

    if state_changed and st.session_state.analysis_data is not None:
        st.session_state.analysis_data = None
        st.session_state.deterministic_metrics = {}
        st.session_state.chat_history = []
        st.session_state.quiz_submitted = False
        st.session_state.quiz_user_answers = {}
        st.session_state.quiz_results = {}
        st.session_state.app_state = "empty" if new_file_hash is None else "ready_for_analysis"

# -----------------------------------------------------------------------------
# Sidebar Navigation & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    # Clean Brand Header
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.svg")
    col_sb_logo, col_sb_text = st.columns([1, 4])
    with col_sb_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=42)
        else:
            st.markdown("🔍")
    with col_sb_text:
        st.markdown(f"### {APP_NAME}")
    st.caption(f"v{APP_VERSION} • Grounded Document Intelligence")
    st.divider()

    # 1. Mode Selector
    st.markdown("##### 🎯 1. Select Analysis Lens")
    selected_mode = st.radio(
        "Analysis Mode",
        options=ALL_MODES,
        index=ALL_MODES.index(st.session_state.active_mode),
        label_visibility="collapsed"
    )

    # Document Lens Subtype
    selected_subtype = st.session_state.active_subtype
    if selected_mode == MODE_DOC_LENS:
        st.caption("Document Type:")
        selected_subtype = st.selectbox(
            "Document Subtype",
            options=DOC_SUBTYPES,
            index=DOC_SUBTYPES.index(st.session_state.active_subtype),
            label_visibility="collapsed"
        )
        st.session_state.active_subtype = selected_subtype

    # 2. Language Selector
    st.markdown("##### 🌐 2. Output Language")
    selected_language = st.selectbox(
        "Output Language",
        options=ALL_LANGUAGES,
        index=ALL_LANGUAGES.index(st.session_state.active_language),
        label_visibility="collapsed"
    )

    # Invalidate on mode/language change
    if selected_mode != st.session_state.active_mode or selected_language != st.session_state.active_language:
        check_context_invalidation(st.session_state.active_file_hash, selected_mode, selected_language)
        st.session_state.active_mode = selected_mode
        st.session_state.active_language = selected_language
        st.rerun()

    st.divider()

    # 3. Demo Fixture Quick Loader
    st.markdown("##### 📁 3. Or Load Demo Fixture")
    fixture_files = {
        "None (Use File Uploader)": None,
        "01 Incomplete Contract (Vague/Missing)": "demo_fixtures/01_incomplete_contract.txt",
        "02 Complete Contract (Explicit clauses)": "demo_fixtures/02_complete_contract.txt",
        "03 General Document (Governance Policy)": "demo_fixtures/03_general_document.txt",
        "04 Medical Report (Standard with ranges)": "demo_fixtures/04_medical_report_standard.txt",
        "05 Medical Report (Ambiguous / Conflicts)": "demo_fixtures/05_medical_report_ambiguous.txt",
        "06 Study Notes (Compiler Design)": "demo_fixtures/06_study_notes_compiler.txt",
    }
    chosen_fixture_name = st.selectbox(
        "Quick Fixtures",
        options=list(fixture_files.keys()),
        index=0,
        label_visibility="collapsed"
    )

    st.divider()

    # 4. Gemini Configuration
    st.markdown("##### ⚡ 4. Gemini Configuration")
    configured_key, key_source = get_gemini_api_key_info(st.session_state.custom_gemini_key)

    if key_source == "secrets":
        st.success("● Connected via Streamlit Secrets")
    elif key_source == "env":
        st.success("● Connected via Environment Variable")
    elif key_source == "ui":
        st.success("● Connected via Custom UI Key")
    else:
        st.error("● Missing Gemini API Key")
        st.caption("On Streamlit Cloud: add GEMINI_API_KEY in Secrets. Or enter below.")

    with st.expander("API Key & Model Settings"):
        if key_source in ["secrets", "env"]:
            st.info("GEMINI_API_KEY is active from Secrets. No manual entry needed.")
            user_key = st.text_input(
                "Override Key (Optional)",
                type="password",
                value=st.session_state.custom_gemini_key,
                placeholder="Leave blank to use Secrets"
            )
        else:
            user_key = st.text_input(
                "Gemini API Key",
                type="password",
                value=st.session_state.custom_gemini_key,
                placeholder="AIzaSy..."
            )

        if user_key != st.session_state.custom_gemini_key:
            st.session_state.custom_gemini_key = user_key
            st.rerun()

        model_options = AVAILABLE_GEMINI_MODELS
        curr_model = st.session_state.selected_model
        if curr_model not in model_options:
            model_options = [curr_model] + model_options

        sel_model = st.selectbox(
            "Gemini Model",
            options=model_options,
            index=model_options.index(curr_model) if curr_model in model_options else 0
        )
        if sel_model != st.session_state.selected_model:
            st.session_state.selected_model = sel_model
            st.rerun()

    st.divider()

    # Session Reset & Export
    st.markdown("##### ⚙️ Session Controls")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🔄 Reset", use_container_width=True, help="Clear active document and start fresh"):
            clear_session()
            st.rerun()

    with c_btn2:
        if st.session_state.analysis_data and st.session_state.extracted_doc:
            try:
                fname = getattr(st.session_state.extracted_doc, "filename", "document")
                report_text = generate_txt_report(
                    filename=fname,
                    mode=st.session_state.active_mode,
                    language=st.session_state.active_language,
                    analysis_data=st.session_state.analysis_data,
                    deterministic_metrics=st.session_state.deterministic_metrics,
                    extracted_doc=st.session_state.extracted_doc
                )
                st.download_button(
                    label="📥 Export",
                    data=report_text.encode("utf-8"),
                    file_name=f"DocuLens_{fname}_Analysis.txt",
                    mime="text/plain; charset=utf-8",
                    use_container_width=True,
                    help="Download full UTF-8 analysis report"
                )
            except Exception as exp_err:
                st.button("📥 Export", disabled=True, use_container_width=True, help="Report export temporarily unavailable")
        else:
            st.button("📥 Export", disabled=True, use_container_width=True)

# -----------------------------------------------------------------------------
# Main Application Content
# -----------------------------------------------------------------------------

# Top Header Banner (Clean Native Layout)
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    h_col_logo, h_col_text = st.columns([1, 8])
    with h_col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=48)
        else:
            st.markdown("🔍")
    with h_col_text:
        st.markdown(f"## {st.session_state.active_mode}")
        st.caption(f"{APP_TAGLINE} • Language: **{st.session_state.active_language}**")

with header_col2:
    status_map = {
        "empty": "⚪ Waiting for Document",
        "validating": "🟡 Validating File",
        "extracting": "⚙️ Extracting Sources",
        "analyzing": "✨ AI Analyzing...",
        "ready": "🟢 Analysis Ready",
        "ready_for_analysis": "📄 Extracted • Ready",
        "unsupported_input": "❌ Unsupported Input",
        "service_error": "⚠️ Service Error"
    }
    cur_state = st.session_state.app_state
    st.info(f"**Status:** {status_map.get(cur_state, 'Ready')}")

# Medical Lens Static Avatar Banner (PRD Section 4 - Clean Container)
if st.session_state.active_mode == MODE_MEDICAL_LENS:
    with st.container(border=True):
        col_med_icon, col_med_text = st.columns([1, 8])
        with col_med_icon:
            if os.path.exists(logo_path):
                st.image(logo_path, width=54)
            else:
                st.markdown("🩺")
        with col_med_text:
            st.subheader("AI Report Assistant • Non-Diagnostic")
            st.caption(
                "Objective laboratory observations and educational test explanations. "
                "Does not diagnose health conditions, prescribe therapy, or replace consultation with a qualified clinical physician."
            )

# -----------------------------------------------------------------------------
# Document Upload & Ingestion Section
# -----------------------------------------------------------------------------
file_bytes_to_process = None
filename_to_process = None

# Primary File Uploader (Always accessible & expanded limits)
uploaded_file = st.file_uploader(
    "Upload any Document or Image (PDF, Word DOCX/DOC, TXT, MD, JPEG, JPG, PNG, WEBP — up to 50 MB, no 15-page limit)",
    type=["pdf", "docx", "doc", "txt", "md", "jpeg", "jpg", "png", "webp"],
    key="main_file_uploader",
    help="Upload contracts, medical lab reports/photos, lecture notes, or textbooks."
)

if uploaded_file is not None:
    file_bytes_to_process = uploaded_file.getvalue()
    filename_to_process = uploaded_file.name
elif chosen_fixture_name != "None (Use File Uploader)" and fixture_files.get(chosen_fixture_name):
    rel_path = fixture_files[chosen_fixture_name]
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    if os.path.exists(abs_path):
        with open(abs_path, "rb") as f:
            file_bytes_to_process = f.read()
        filename_to_process = os.path.basename(abs_path)

# Extraction & Pre-Analysis Validation
if file_bytes_to_process and filename_to_process:
    from src.extractors import compute_sha256
    incoming_hash = compute_sha256(file_bytes_to_process)

    if st.session_state.active_file_hash != incoming_hash:
        st.session_state.active_file_hash = incoming_hash
        st.session_state.active_filename = filename_to_process
        st.session_state.analysis_data = None
        st.session_state.deterministic_metrics = {}
        st.session_state.chat_history = []
        st.session_state.quiz_submitted = False
        st.session_state.quiz_user_answers = {}
        st.session_state.quiz_results = {}
        st.session_state.app_state = "extracting"

        extracted, err = extract_document(file_bytes_to_process, filename_to_process)
        if err:
            st.session_state.extracted_doc = None
            st.session_state.app_state = "unsupported_input"
            st.session_state.error_message = err
        else:
            st.session_state.extracted_doc = extracted
            st.session_state.app_state = "ready_for_analysis"
            st.session_state.error_message = None

if st.session_state.app_state == "unsupported_input" and st.session_state.error_message:
    st.error(f"❌ Input Validation Error: {st.session_state.error_message}")
    st.info("💡 Guidance: Please upload an unencrypted PDF, Word document, TXT, or Image (JPEG/PNG) under 50 MB.")

if st.session_state.extracted_doc:
    doc = st.session_state.extracted_doc
    with st.expander(f"📑 Document Extracted: {doc.filename} ({doc.total_chars:,} chars, {len(doc.sections)} sections)", expanded=(st.session_state.analysis_data is None)):
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        with meta_col1:
            st.metric("Format", doc.file_type.upper())
        with meta_col2:
            st.metric("Sections / Sources", len(doc.sections))
        with meta_col3:
            st.metric("Character Count", f"{doc.total_chars:,}")

        if doc.formatting_warnings:
            for w in doc.formatting_warnings:
                st.warning(f"⚠️ {w}")

        st.text_area(
            "Extracted Source Text Preview (with Grounded Source Anchors)",
            value=doc.preview_snippet,
            height=140,
            disabled=True
        )

        st.caption("🔒 Privacy Notice: Text fragments are securely processed in ephemeral memory and sent to Google Gemini for analysis. No permanent server storage.")

        if not configured_key:
            st.warning("🔑 **Gemini API Key Required:** Please add `GEMINI_API_KEY` to your Streamlit Secrets (or enter it in the left sidebar settings).")

        col_act, col_retry = st.columns([2, 1])
        with col_act:
            analyze_clicked = st.button(
                "🚀 Analyze Document",
                type="primary",
                use_container_width=True,
                disabled=not bool(configured_key)
            )
        with col_retry:
            if st.session_state.app_state == "service_error":
                retry_clicked = st.button("🔄 Retry Analysis", use_container_width=True)
            else:
                retry_clicked = False

        if analyze_clicked or retry_clicked:
            st.session_state.app_state = "analyzing"
            st.rerun()

# -----------------------------------------------------------------------------
# AI Analysis Execution via Google Gemini
# -----------------------------------------------------------------------------
if st.session_state.app_state == "analyzing" and st.session_state.extracted_doc:
    doc = st.session_state.extracted_doc
    mode = st.session_state.active_mode
    lang = st.session_state.active_language

    with st.spinner(f"Analyzing {doc.filename} with Gemini {st.session_state.selected_model} in {lang}..."):
        if mode == MODE_DOC_LENS:
            if st.session_state.active_subtype == DOC_SUBTYPE_CONTRACT:
                prompt = get_contract_lens_prompt(doc.full_text_with_sources, lang)
            else:
                prompt = get_general_doc_prompt(doc.full_text_with_sources, lang)
        elif mode == MODE_MEDICAL_LENS:
            prompt = get_medical_lens_prompt(doc.full_text_with_sources, lang)
        else:
            prompt = get_study_lens_prompt(doc.full_text_with_sources, lang)

        parsed_json, error = call_gemini_json_analysis(
            prompt=prompt,
            model=st.session_state.selected_model,
            api_key=st.session_state.custom_gemini_key
        )

        if error:
            st.session_state.app_state = "service_error"
            st.session_state.error_message = error
            st.rerun()
        else:
            st.session_state.analysis_data = parsed_json
            st.session_state.app_state = "ready"

            # Deterministic Application Code Calculations (PRD Section 6)
            if mode == MODE_DOC_LENS:
                if st.session_state.active_subtype == DOC_SUBTYPE_CONTRACT:
                    findings = parsed_json.get("contract_findings", [])
                    if not isinstance(findings, list):
                        findings = []
                    st.session_state.deterministic_metrics = compute_contract_metrics(findings, is_complete=True)
                else:
                    g_findings = parsed_json.get("general_findings", [])
                    if not isinstance(g_findings, list):
                        g_findings = []
                    st.session_state.deterministic_metrics = {
                        "general_findings_count": len(g_findings),
                        "actions_count": len([f for f in g_findings if isinstance(f, dict) and f.get("suggested_action")])
                    }

            elif mode == MODE_MEDICAL_LENS:
                results = parsed_json.get("test_results", [])
                if not isinstance(results, list):
                    results = []
                attention_count = 0
                unassessed_count = 0
                augmented_results = []

                for r in results:
                    if not isinstance(r, dict):
                        continue
                    raw_val = r.get("raw_result", "")
                    raw_int = r.get("raw_interval", "")
                    rep_flag = r.get("reported_flag", "None")

                    eval_res = compute_medical_range(raw_val, raw_int, rep_flag)
                    r["computed_comparison"] = eval_res["comparison"]
                    r["comparison_reason"] = eval_res["reason"]
                    r["is_outside_range"] = eval_res["is_outside_range"]
                    r["has_conflict"] = eval_res["has_conflict"]
                    r["flag_conflict_note"] = eval_res["verification_note"]

                    if eval_res["is_outside_range"]:
                        attention_count += 1
                    if "Cannot assess" in eval_res["comparison"]:
                        unassessed_count += 1

                    augmented_results.append(r)

                parsed_json["test_results"] = augmented_results
                st.session_state.deterministic_metrics = {
                    "total_analytes": len(augmented_results),
                    "attention_count": attention_count,
                    "unassessed_count": unassessed_count
                }

            elif mode == MODE_STUDY_LENS:
                quiz_items = parsed_json.get("quiz", [])
                if not isinstance(quiz_items, list):
                    quiz_items = []
                rev_notes = parsed_json.get("revision_notes", [])
                if not isinstance(rev_notes, list):
                    rev_notes = []
                st.session_state.quiz_user_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_results = {}
                st.session_state.deterministic_metrics = {
                    "total_quiz_questions": len(quiz_items),
                    "revision_notes_count": len(rev_notes)
                }

            st.rerun()

if st.session_state.app_state == "service_error" and st.session_state.error_message:
    st.error(f"⚠️ Analysis Request Failed: {st.session_state.error_message}")
    st.info("You can retry the analysis using the button in the document preview panel above.")

# -----------------------------------------------------------------------------
# Render Ready Dashboards (Clean Native Containers)
# -----------------------------------------------------------------------------
if st.session_state.app_state == "ready" and st.session_state.analysis_data:
    data = st.session_state.analysis_data
    metrics = st.session_state.deterministic_metrics
    is_urdu = st.session_state.active_language == LANG_URDU
    rtl_class = "rtl-text" if is_urdu else ""

    # =========================================================================
    # 1. DOCUMENT LENS DASHBOARD
    # =========================================================================
    if st.session_state.active_mode == MODE_DOC_LENS:
        subtype = st.session_state.active_subtype
        doc_title = data.get("document_title", st.session_state.extracted_doc.filename)

        with st.container(border=True):
            col_cov1, col_cov2 = st.columns([3, 1])
            with col_cov1:
                st.caption(f"{subtype.upper()} • COVERAGE: {data.get('coverage_statement', 'Full document evaluated')}")
                st.subheader(f"📄 {doc_title}")
            with col_cov2:
                if subtype == DOC_SUBTYPE_CONTRACT:
                    render_priority_badge(metrics.get('overall_priority', 'Low'))
                else:
                    st.success("General Document Mode")
            st.write(data.get('summary', 'No summary generated.'))

        if subtype == DOC_SUBTYPE_CONTRACT:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Review Priority", metrics.get('overall_priority', 'Low'))
            with m2:
                st.metric("Flagged Issues", metrics.get('unique_issues_count', 0))
            with m3:
                st.metric("Missing Topics", metrics.get('missing_topics_count', 0))
            with m4:
                st.metric("Action Items", metrics.get('actions_count', 0))

            st.info(f"📌 **Review Priority Rule:** {metrics.get('priority_rule', '')}")

        tab_findings, tab_details, tab_chat = st.tabs([
            "📋 Checklist Findings & Actions",
            "ℹ️ Key Extracted Details",
            "💬 Grounded Document Chat"
        ])

        with tab_findings:
            if subtype == DOC_SUBTYPE_CONTRACT:
                findings = data.get("contract_findings", [])
                for f in findings:
                    topic = f.get("topic", "Topic")
                    status = f.get("status", "Present")
                    src_id = f.get("source_id", "Source")
                    quote = f.get("source_passage", "")
                    expl = f.get("explanation", "")
                    clarify = f.get("clarification_question", "")
                    action = f.get("suggested_action", "")
                    prio = f.get("review_priority", "Low")

                    with st.container(border=True):
                        fc1, fc2 = st.columns([3, 1])
                        with fc1:
                            st.markdown(f"### {topic}")
                            st.caption(f"Status: **{status}** | Priority: **{prio}**")
                        with fc2:
                            st.caption(f"Source: `{src_id}`")

                        st.info(f"\"{quote}\"")
                        st.write(expl)
                        if clarify:
                            st.warning(f"**Suggested Question:** {clarify}")
                        if action:
                            st.success(f"**Recommended Action:** {action}")
            else:
                gen_findings = data.get("general_findings", [])
                for gf in gen_findings:
                    with st.container(border=True):
                        g1, g2 = st.columns([3, 1])
                        with g1:
                            st.markdown(f"### {gf.get('topic', 'Topic')}")
                        with g2:
                            st.caption(f"Source: `{gf.get('source_id', 'Source')}`")
                        st.write(gf.get('key_fact', ''))
                        st.info(f"\"{gf.get('source_passage', '')}\"")
                        if gf.get("suggested_action"):
                            st.success(f"**Action:** {gf.get('suggested_action')}")

        with tab_details:
            kd = data.get("key_details", {})
            if not isinstance(kd, dict):
                kd = {}
            col_k1, col_k2 = st.columns(2)
            with col_k1:
                with st.container(border=True):
                    st.markdown("#### 👥 Parties & Entities")
                    st.write(kd.get('parties', 'Not found'))
                    st.markdown("#### 📅 Dates & Effective Term")
                    st.write(kd.get('effective_date', 'Not found'))
                    st.markdown("#### 💰 Amounts & Currency")
                    st.write(kd.get('amounts_and_currency', 'Not found'))
            with col_k2:
                with st.container(border=True):
                    st.markdown("#### 💳 Payment Terms")
                    st.write(kd.get('payment_terms', 'Not found'))
                    st.markdown("#### ⏱️ Deadlines & Milestones")
                    st.write(kd.get('deadlines', 'Not found'))
                    st.markdown("#### 📋 Core Responsibilities")
                    st.write(kd.get('responsibilities', 'Not found'))

        with tab_chat:
            st.markdown("##### 💬 Ask the Document")
            st.caption("Answers are strictly grounded in the active document text with verifiable source references.")

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_question = st.chat_input("Ask a question about this document...")
            if user_question:
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                with st.chat_message("user"):
                    st.markdown(user_question)

                with st.chat_message("assistant"):
                    with st.spinner("Searching document evidence with Gemini..."):
                        ans, err = call_gemini_grounded_chat(
                            document_text=st.session_state.extracted_doc.full_text_with_sources,
                            chat_history=st.session_state.chat_history,
                            user_query=user_question,
                            mode=st.session_state.active_mode,
                            language=st.session_state.active_language,
                            model=st.session_state.selected_model,
                            api_key=st.session_state.custom_gemini_key
                        )
                        if err:
                            st.error(err)
                        else:
                            st.markdown(ans)
                            st.session_state.chat_history.append({"role": "assistant", "content": ans})

    # =========================================================================
    # 2. MEDICAL LENS DASHBOARD
    # =========================================================================
    elif st.session_state.active_mode == MODE_MEDICAL_LENS:
        patient_raw = data.get("patient_context", "")
        if isinstance(patient_raw, dict):
            patient_str = patient_raw.get("summary") or patient_raw.get("description") or "De-identified"
            report_date = patient_raw.get("report_date") or data.get("report_date", "Not stated")
        else:
            patient_str = str(patient_raw) if patient_raw else "De-identified"
            report_date = data.get("report_date", "Not stated")

        lab_name = data.get("lab_name") or data.get("report_title") or "Clinical Laboratory"
        summary_text = data.get("overall_summary") or data.get("summary") or "No summary available."

        with st.container(border=True):
            mc1, mc2 = st.columns([3, 1])
            with mc1:
                st.caption(f"LAB REPORT • {lab_name}")
                st.subheader("🔬 Diagnostic Laboratory Overview")
                if patient_str and patient_str != "De-identified":
                    st.caption(f"Patient Context: {patient_str}")
            with mc2:
                st.caption(f"Date: {report_date}")
            st.write(summary_text)

        med1, med2, med3 = st.columns(3)
        with med1:
            st.metric("Total Analytes Evaluated", metrics.get('total_analytes', 0))
        with med2:
            st.metric("Values Outside Range", metrics.get('attention_count', 0))
        with med3:
            st.metric("Unassessed Values", metrics.get('unassessed_count', 0))

        st.info(
            "ℹ️ **Clinical Safety Standard:** 'No abnormal values identified' means only that no validated numeric result was outside its supplied interval. "
            "It must never be presented as a declaration that the patient is healthy. This application is an educational AI Report Assistant and does not provide clinical diagnoses."
        )

        med_tab_results, med_tab_questions, med_tab_chat = st.tabs([
            "📊 Analyte Results & Ranges",
            "🩺 Questions for Clinician",
            "💬 AI Report Assistant Chat"
        ])

        with med_tab_results:
            results = data.get("test_results", [])
            if not isinstance(results, list):
                results = []
            for r in results:
                if not isinstance(r, dict):
                    continue
                t_name = r.get("test_name", "Test Analyte")
                raw_val = r.get("raw_result", "")
                unit = r.get("unit", "")
                raw_int = r.get("raw_interval", "")
                rep_flag = r.get("reported_flag", "None")
                src_id = r.get("source_id", "Source")
                quote = r.get("source_passage", "")
                comp = r.get("computed_comparison", "Cannot assess from range")
                expl = r.get("general_explanation", "")
                doctor_q = r.get("doctor_question", "")
                conflict = r.get("has_conflict", False)
                conflict_note = r.get("flag_conflict_note")

                with st.container(border=True):
                    rc1, rc2 = st.columns([3, 1])
                    with rc1:
                        st.markdown(f"### {t_name}")
                        st.caption(f"Result: **{raw_val} {unit}** | Normal Range: **{raw_int}** | Lab Flag: **{rep_flag}**")
                    with rc2:
                        st.caption(f"Source: `{src_id}`")

                    render_medical_comparison_badge(comp, conflict)
                    if conflict:
                        st.error(f"⚡ Conflict: {conflict_note}")

                    st.info(f"\"{quote}\"")
                    st.write(f"**Educational Description:** {expl}")
                    st.warning(f"**Question for Doctor:** {doctor_q}")

        with med_tab_questions:
            checklist = data.get("doctor_discussion_checklist", [])
            if not isinstance(checklist, list):
                checklist = []
            st.markdown("##### 🩺 Doctor Discussion Checklist")
            for idx, q in enumerate(checklist, 1):
                with st.container(border=True):
                    st.markdown(f"**{idx}.** {q}")

        with med_tab_chat:
            st.markdown("##### 💬 Medical Report Assistant Chat")
            st.caption("Ask questions about analyte meanings and report values. Prescriptions and medical diagnoses are strictly restricted.")

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_q = st.chat_input("Ask about your lab report...")
            if user_q:
                st.session_state.chat_history.append({"role": "user", "content": user_q})
                with st.chat_message("user"):
                    st.markdown(user_q)

                with st.chat_message("assistant"):
                    with st.spinner("Consulting report evidence with Gemini..."):
                        ans, err = call_gemini_grounded_chat(
                            document_text=st.session_state.extracted_doc.full_text_with_sources,
                            chat_history=st.session_state.chat_history,
                            user_query=user_q,
                            mode=st.session_state.active_mode,
                            language=st.session_state.active_language,
                            model=st.session_state.selected_model,
                            api_key=st.session_state.custom_gemini_key
                        )
                        if err:
                            st.error(err)
                        else:
                            st.markdown(ans)
                            st.session_state.chat_history.append({"role": "assistant", "content": ans})

    # =========================================================================
    # 3. STUDY LENS DASHBOARD
    # =========================================================================
    elif st.session_state.active_mode == MODE_STUDY_LENS:
        with st.container(border=True):
            st.caption(f"{data.get('course_or_subject', 'Study Material')} • COVERAGE: {data.get('coverage_statement', 'Module Analyzed')}")
            st.subheader("📚 Learning Overview & Concept Synthesis")
            st.write(data.get('summary', 'No summary available.'))
            if data.get('topic_overview'):
                st.info(f"**Topic Interplay:** {data.get('topic_overview')}")

        study_tab_notes, study_tab_quiz, study_tab_chat = st.tabs([
            "📚 Revision Notes & Concepts",
            "📝 Practice Quiz (5 MCQs)",
            "💬 Ask the Notes"
        ])

        with study_tab_notes:
            notes = data.get("revision_notes", [])
            if not isinstance(notes, list):
                notes = []
            for n in notes:
                if not isinstance(n, dict):
                    continue
                cat = n.get("category", "Key Concept")
                title = n.get("title", "Concept")
                content = n.get("content", "")
                src = n.get("source_id", "Source")
                quote = n.get("source_passage", "")
                ex = n.get("assistant_example")

                with st.container(border=True):
                    sc1, sc2 = st.columns([3, 1])
                    with sc1:
                        st.markdown(f"### 📖 [{cat.upper()}] {title}")
                    with sc2:
                        st.caption(f"Source: `{src}`")

                    st.write(content)
                    st.info(f"\"{quote}\"")
                    if ex:
                        st.success(f"**Assistant Example:** {ex}")

        with study_tab_quiz:
            quiz_list = data.get("quiz", [])
            if not isinstance(quiz_list, list):
                quiz_list = []
            st.markdown("##### 📝 Grounded Practice Quiz (5 Questions)")
            st.caption("Multiple-choice questions generated strictly from your notes. Correct answers are hidden until submission.")

            with st.form("study_quiz_form"):
                current_choices = {}
                for q in quiz_list:
                    if not isinstance(q, dict):
                        continue
                    q_id = q.get("question_id", 1)
                    q_stem = q.get("question", "")
                    options = q.get("options", [])

                    st.markdown(f"**Q{q_id}. {q_stem}**")
                    choice = st.radio(
                        f"Select your answer for Q{q_id}:",
                        options=range(len(options)),
                        format_func=lambda i, opts=options: f"[{chr(65+i)}] {opts[i]}",
                        key=f"quiz_q_{q_id}",
                        label_visibility="collapsed"
                    )
                    current_choices[q_id] = choice
                    st.divider()

                submit_quiz = st.form_submit_button("Submit Quiz for Evaluation", type="primary")

            if submit_quiz:
                st.session_state.quiz_user_answers = current_choices
                st.session_state.quiz_submitted = True
                st.session_state.quiz_results = calculate_quiz_score(quiz_list, current_choices)
                st.rerun()

            if st.session_state.quiz_submitted and st.session_state.quiz_results:
                res = st.session_state.quiz_results
                score = res.get("score", 0)
                tot = res.get("total", 5)
                pct = res.get("percentage", 0.0)

                with st.container(border=True):
                    st.subheader("Quiz Results")
                    st.metric("Final Score", f"{score} / {tot}", f"{pct}%")
                    if pct >= 80:
                        st.success("🌟 Excellent mastery of the study material!")
                    elif pct >= 60:
                        st.info("👍 Good effort! Review the detailed answer keys below to strengthen weak areas.")
                    else:
                        st.warning("📖 Review the revision notes and cited passages to reinforce key concepts.")

                st.markdown("#### 🎯 Answer Breakdown & Citations")
                for item in res.get("details", []):
                    q_num = item["question_id"]
                    is_corr = item["is_correct"]
                    u_pick = item["user_choice"]
                    c_pick = item["correct_choice"]
                    opts = item["options"]
                    expl = item["explanation"]
                    src = item["source_id"]
                    passage = item["source_passage"]

                    with st.container(border=True):
                        st.markdown(f"**Q{q_num}: {item['question']}**")
                        if is_corr:
                            st.success(f"Your Answer: [{chr(65+u_pick)}] {opts[u_pick]} (Correct)")
                        else:
                            st.error(f"Your Answer: [{chr(65+u_pick)}] {opts[u_pick]} (Incorrect)")
                            st.success(f"Correct Answer: [{chr(65+c_pick)}] {opts[c_pick]}")

                        st.write(f"**Explanation:** {expl}")
                        st.info(f"Source ({src}): \"{passage}\"")

        with study_tab_chat:
            st.markdown("##### 💬 Ask the Study Notes")
            st.caption("Ask questions about definitions, formulas, or steps. The assistant will answer using only your uploaded notes.")

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            s_question = st.chat_input("Ask a concept or formula question...")
            if s_question:
                st.session_state.chat_history.append({"role": "user", "content": s_question})
                with st.chat_message("user"):
                    st.markdown(s_question)

                with st.chat_message("assistant"):
                    with st.spinner("Reviewing study material with Gemini..."):
                        ans, err = call_gemini_grounded_chat(
                            document_text=st.session_state.extracted_doc.full_text_with_sources,
                            chat_history=st.session_state.chat_history,
                            user_query=s_question,
                            mode=st.session_state.active_mode,
                            language=st.session_state.active_language,
                            model=st.session_state.selected_model,
                            api_key=st.session_state.custom_gemini_key
                        )
                        if err:
                            st.error(err)
                        else:
                            st.markdown(ans)
                            st.session_state.chat_history.append({"role": "assistant", "content": ans})

# -----------------------------------------------------------------------------
# Empty State Landing (When no file uploaded or analyzed yet)
# -----------------------------------------------------------------------------
elif st.session_state.app_state in ["empty", "ready_for_analysis"] and not st.session_state.analysis_data:
    st.subheader("📑 Welcome to DocuLens AI", anchor=False)
    st.caption("Upload any contract, clinical report, lecture notes, textbook, or photo above — or pick a demo fixture in the sidebar.")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### 📄 Document Lens")
            st.write("Contract audit against 6-topic checklist. Detects vague wording, missing provisions, and deterministic review priorities.")
    with c2:
        with st.container(border=True):
            st.markdown("### 🩺 Medical Lens")
            st.write("Clinical analyte extraction, numeric reference range comparisons, conflict detection, and clinician discussion questions.")
    with c3:
        with st.container(border=True):
            st.markdown("### 🎓 Study Lens")
            st.write("Revision notes, key formula synthesis, and interactive 5-question multiple choice quizzes with instant scoring.")
