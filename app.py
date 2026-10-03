"""DocuLens AI - Production Streamlit Application
Entrypoint: app.py
Complies with PRD requirements for Document Lens, Medical Lens, and Study Lens.
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
    MAX_EXTRACTED_CHARS
)
from src.extractors import extract_document, ExtractedDocument
from src.deterministic_rules import compute_medical_range, compute_contract_metrics, calculate_quiz_score
from src.gemini_client import call_gemini_json_analysis, call_gemini_grounded_chat, get_gemini_api_key
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
    render_medical_avatar_banner,
    get_priority_badge,
    get_medical_comparison_badge
)

# -----------------------------------------------------------------------------
# Streamlit Page Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_NAME} | Multi-Lens Document Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Management & Isolation (PRD Section 2, 6 & Acceptance A08, A10)
# -----------------------------------------------------------------------------
def init_session_state():
    """Initialize default session state keys if not already present."""
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
        "app_state": "empty",  # empty, validating, extracting, analyzing, ready, unsupported_input, service_error
        "error_message": None,
        "last_raw_prompt": None,
        "custom_gemini_key": "",
        "selected_model": DEFAULT_GEMINI_MODEL
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

def clear_session():
    """PRD C05 & A10: Clear all app-held content, chat, quiz, and extracted state."""
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
    """
    PRD C03, C04 & A08:
    A file, mode, or language change invalidates earlier analysis, chat, and quiz state.
    """
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
    st.markdown(
        f"""
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <span style="font-size: 1.8rem;">🔍</span>
                <span style="font-size: 1.45rem; font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF;">{APP_NAME}</span>
            </div>
            <div style="font-size: 0.76rem; color: #94A3B8; margin-top: 0.2rem;">
                v{APP_VERSION} • Grounded Document Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()

    # Mode Selector
    st.markdown("##### 🎯 1. Select Analysis Lens")
    selected_mode = st.radio(
        "Analysis Mode",
        options=ALL_MODES,
        index=ALL_MODES.index(st.session_state.active_mode),
        label_visibility="collapsed"
    )

    # Document Lens Subtype (PRD: Must not silently infer legal category)
    selected_subtype = st.session_state.active_subtype
    if selected_mode == MODE_DOC_LENS:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #CBD5E1; margin: 0.5rem 0 0.2rem 0;'>Document Type:</div>", unsafe_allow_html=True)
        selected_subtype = st.selectbox(
            "Document Subtype",
            options=DOC_SUBTYPES,
            index=DOC_SUBTYPES.index(st.session_state.active_subtype),
            label_visibility="collapsed"
        )
        st.session_state.active_subtype = selected_subtype

    # Language Selector (PRD C03)
    st.markdown("##### 🌐 2. Output Language")
    selected_language = st.selectbox(
        "Output Language",
        options=ALL_LANGUAGES,
        index=ALL_LANGUAGES.index(st.session_state.active_language),
        label_visibility="collapsed"
    )

    # Check for mode or language change invalidation
    if selected_mode != st.session_state.active_mode or selected_language != st.session_state.active_language:
        check_context_invalidation(st.session_state.active_file_hash, selected_mode, selected_language)
        st.session_state.active_mode = selected_mode
        st.session_state.active_language = selected_language
        st.rerun()

    st.divider()

    # Demo Fixture Quick Loader
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

    # Gemini Model & API Key Configuration
    st.markdown("##### ⚡ 4. Gemini Configuration")
    configured_key = get_gemini_api_key(st.session_state.custom_gemini_key)
    if configured_key:
        st.markdown(
            '<div style="font-size: 0.75rem; color: #34D399; margin-bottom: 0.5rem;">'
            '● Gemini API Key Connected</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="font-size: 0.75rem; color: #F87171; margin-bottom: 0.5rem;">'
            '● Missing Gemini API Key</div>',
            unsafe_allow_html=True
        )

    with st.expander("API Key & Model Settings"):
        user_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.custom_gemini_key,
            placeholder="AIzaSy..."
        )
        if user_key != st.session_state.custom_gemini_key:
            st.session_state.custom_gemini_key = user_key
            st.rerun()

        model_choice = st.selectbox(
            "Gemini Model",
            options=AVAILABLE_GEMINI_MODELS,
            index=AVAILABLE_GEMINI_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_GEMINI_MODELS else 0
        )
        st.session_state.selected_model = model_choice

    st.divider()

    # Session Reset & Controls
    col_reset, col_down = st.columns([1, 1])
    with col_reset:
        if st.button("🗑️ Clear", use_container_width=True, help="Reset session and delete in-memory data"):
            clear_session()
            st.rerun()

    with col_down:
        if st.session_state.analysis_data is not None and st.session_state.extracted_doc is not None:
            report_text = generate_txt_report(
                filename=st.session_state.extracted_doc.filename,
                mode=st.session_state.active_mode,
                language=st.session_state.active_language,
                analysis_data=st.session_state.analysis_data,
                deterministic_metrics=st.session_state.deterministic_metrics
            )
            st.download_button(
                label="📥 Export",
                data=report_text.encode("utf-8"),
                file_name=f"DocuLens_{st.session_state.extracted_doc.filename}_Analysis.txt",
                mime="text/plain; charset=utf-8",
                use_container_width=True,
                help="Download full UTF-8 analysis report"
            )
        else:
            st.button("📥 Export", disabled=True, use_container_width=True)

# -----------------------------------------------------------------------------
# Main Application Content
# -----------------------------------------------------------------------------

# Top Header Banner
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    mode_emoji = "📄" if st.session_state.active_mode == MODE_DOC_LENS else ("🩺" if st.session_state.active_mode == MODE_MEDICAL_LENS else "🎓")
    st.markdown(
        f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #FFFFFF;">
                    {st.session_state.active_mode}
                </h1>
                <span class="badge-pill badge-source">{st.session_state.active_language}</span>
            </div>
            <p style="margin: 0.35rem 0 0 0; color: #94A3B8; font-size: 0.92rem;">
                {APP_TAGLINE}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with header_col2:
    state_pill_map = {
        "empty": '<span class="badge-pill badge-low">⚪ Waiting for Document</span>',
        "validating": '<span class="badge-pill badge-med">🟡 Validating File</span>',
        "extracting": '<span class="badge-pill badge-med">⚙️ Extracting Sources</span>',
        "analyzing": '<span class="badge-pill badge-high">✨ AI Analyzing...</span>',
        "ready": '<span class="badge-pill badge-clear">🟢 Analysis Ready</span>',
        "ready_for_analysis": '<span class="badge-pill badge-low">📄 Extracted • Ready</span>',
        "unsupported_input": '<span class="badge-pill badge-high">❌ Unsupported Input</span>',
        "service_error": '<span class="badge-pill badge-high">⚠️ Service Error</span>'
    }
    cur_state = st.session_state.app_state
    pill_html = state_pill_map.get(cur_state, state_pill_map["empty"])
    st.markdown(f"<div style='text-align: right; padding-top: 0.5rem;'>{pill_html}</div>", unsafe_allow_html=True)

# Medical Lens Static Avatar Banner (PRD Section 4)
if st.session_state.active_mode == MODE_MEDICAL_LENS:
    st.markdown(render_medical_avatar_banner(), unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Document Upload & Ingestion Section
# -----------------------------------------------------------------------------
file_bytes_to_process = None
filename_to_process = None

# Check if a fixture was selected from dropdown
if chosen_fixture_name != "None (Use File Uploader)" and fixture_files.get(chosen_fixture_name):
    rel_path = fixture_files[chosen_fixture_name]
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    if os.path.exists(abs_path):
        with open(abs_path, "rb") as f:
            file_bytes_to_process = f.read()
        filename_to_process = os.path.basename(abs_path)
        
        # Auto-align mode with fixture if appropriate for best demo UX
        if "incomplete_contract" in filename_to_process or "complete_contract" in filename_to_process:
            if st.session_state.active_mode != MODE_DOC_LENS:
                st.session_state.active_mode = MODE_DOC_LENS
                st.session_state.active_subtype = DOC_SUBTYPE_CONTRACT
                st.rerun()
        elif "general_document" in filename_to_process:
            if st.session_state.active_mode != MODE_DOC_LENS or st.session_state.active_subtype != DOC_SUBTYPE_GENERAL:
                st.session_state.active_mode = MODE_DOC_LENS
                st.session_state.active_subtype = DOC_SUBTYPE_GENERAL
                st.rerun()
        elif "medical_report" in filename_to_process:
            if st.session_state.active_mode != MODE_MEDICAL_LENS:
                st.session_state.active_mode = MODE_MEDICAL_LENS
                st.rerun()
        elif "study_notes" in filename_to_process:
            if st.session_state.active_mode != MODE_STUDY_LENS:
                st.session_state.active_mode = MODE_STUDY_LENS
                st.rerun()

# File Uploader
if not file_bytes_to_process:
    uploaded_file = st.file_uploader(
        "Upload a document (PDF, DOCX, or TXT — Max 10 MB, 15 PDF pages)",
        type=["pdf", "docx", "txt"],
        help="Upload text-based agreements, medical test reports, or study materials."
    )
    if uploaded_file:
        file_bytes_to_process = uploaded_file.read()
        filename_to_process = uploaded_file.name

# -----------------------------------------------------------------------------
# Extraction & Pre-Analysis Validation (PRD C01, C02)
# -----------------------------------------------------------------------------
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
    st.info("💡 Guidance: Please upload an unencrypted, text-based PDF (under 15 pages), standard DOCX, or UTF-8 TXT under 10 MB and 25,000 characters.")

if st.session_state.extracted_doc:
    doc = st.session_state.extracted_doc
    with st.expander(f"📑 Document Extracted: {doc.filename} ({doc.total_chars:,} chars, {len(doc.sections)} sections)", expanded=(st.session_state.analysis_data is None)):
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        with meta_col1:
            st.markdown(f"**Format:** `{doc.file_type.upper()}`")
        with meta_col2:
            st.markdown(f"**Sections / Sources:** `{len(doc.sections)}`")
        with meta_col3:
            st.markdown(f"**Character Count:** `{doc.total_chars:,} / 25,000`")

        if doc.formatting_warnings:
            for w in doc.formatting_warnings:
                st.warning(f"⚠️ {w}")

        st.text_area(
            "Extracted Source Text Preview (with Grounded Source Anchors)",
            value=doc.preview_snippet,
            height=140,
            disabled=True
        )

        st.markdown(
            '<div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.4rem;">'
            '🔒 Privacy Notice: Text fragments are securely processed in ephemeral memory and sent to Google Gemini for analysis. No permanent server storage.'
            '</div>',
            unsafe_allow_html=True
        )

        col_act, col_retry = st.columns([2, 1])
        with col_act:
            analyze_clicked = st.button("🚀 Analyze Document", type="primary", use_container_width=True)
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

        st.session_state.last_raw_prompt = prompt

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
                    st.session_state.deterministic_metrics = compute_contract_metrics(findings, is_complete=True)
                else:
                    st.session_state.deterministic_metrics = {
                        "general_findings_count": len(parsed_json.get("general_findings", [])),
                        "actions_count": len([f for f in parsed_json.get("general_findings", []) if f.get("suggested_action")])
                    }

            elif mode == MODE_MEDICAL_LENS:
                results = parsed_json.get("test_results", [])
                attention_count = 0
                unassessed_count = 0
                augmented_results = []

                for r in results:
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
                st.session_state.quiz_user_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_results = {}
                st.session_state.deterministic_metrics = {
                    "total_quiz_questions": len(quiz_items),
                    "revision_notes_count": len(parsed_json.get("revision_notes", []))
                }

            st.rerun()

if st.session_state.app_state == "service_error" and st.session_state.error_message:
    st.error(f"⚠️ Analysis Request Failed: {st.session_state.error_message}")
    st.info("You can retry the analysis using the button in the document preview panel above.")

# -----------------------------------------------------------------------------
# Render Ready Dashboards
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

        st.markdown(
            f"""
            <div class="dl-card dl-card-glow-indigo">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
                    <div>
                        <div style="font-size: 0.78rem; text-transform: uppercase; color: #818CF8; font-weight: 700; letter-spacing: 0.05em;">
                            {subtype.upper()} • COVERAGE: {data.get('coverage_statement', 'Full document evaluated')}
                        </div>
                        <h2 style="margin: 0.2rem 0; font-size: 1.55rem; color: #FFFFFF; font-weight: 700;">
                            {doc_title}
                        </h2>
                    </div>
                    <div>
                        {get_priority_badge(metrics.get('overall_priority', 'Low')) if subtype == DOC_SUBTYPE_CONTRACT else '<span class="badge-pill badge-clear">General Document Mode</span>'}
                    </div>
                </div>
                <div class="{rtl_class}" style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.7;">
                    {data.get('summary', 'No summary generated.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if subtype == DOC_SUBTYPE_CONTRACT:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                p_text = metrics.get('overall_priority', 'Low')
                st.markdown(
                    f"""
                    <div class="stat-box">
                        <div class="stat-label">Review Priority</div>
                        <div class="stat-value">{p_text}</div>
                        <div style="font-size: 0.72rem; color: #94A3B8;">Rule-calculated</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m2:
                st.markdown(
                    f"""
                    <div class="stat-box">
                        <div class="stat-label">Flagged Issues</div>
                        <div class="stat-value">{metrics.get('unique_issues_count', 0)}</div>
                        <div style="font-size: 0.72rem; color: #94A3B8;">Vague or unclear</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m3:
                st.markdown(
                    f"""
                    <div class="stat-box">
                        <div class="stat-label">Missing Topics</div>
                        <div class="stat-value">{metrics.get('missing_topics_count', 0)}</div>
                        <div style="font-size: 0.72rem; color: #94A3B8;">Absent checklist items</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m4:
                st.markdown(
                    f"""
                    <div class="stat-box">
                        <div class="stat-label">Action Items</div>
                        <div class="stat-value">{metrics.get('actions_count', 0)}</div>
                        <div style="font-size: 0.72rem; color: #94A3B8;">Recommended steps</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.info(f"📌 **Review Priority Rule:** {metrics.get('priority_rule', '')}")

        tab_findings, tab_details, tab_chat = st.tabs([
            "📋 Checklist Findings & Actions",
            "ℹ️ Key Extracted Details",
            "💬 Grounded Document Chat"
        ])

        with tab_findings:
            if subtype == DOC_SUBTYPE_CONTRACT:
                findings = data.get("contract_findings", [])
                if not findings:
                    st.success("All 6 standard contract checklist topics were evaluated.")
                for f in findings:
                    topic = f.get("checklist_topic", "General Topic")
                    status = f.get("status", "Found")
                    src_id = f.get("source_id", "Not found")
                    quote = f.get("source_passage", "Not found in the analyzed text")
                    expl = f.get("explanation", "")
                    clarify = f.get("clarification_question", "")
                    action = f.get("suggested_action", "")
                    prio = f.get("review_priority", "Low")

                    glow_class = "dl-card-glow-rose" if prio == "High" else ("dl-card-glow-amber" if prio == "Medium" else "dl-card-glow-indigo")

                    st.markdown(
                        f"""
                        <div class="dl-card {glow_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <div style="display: flex; align-items: center; gap: 0.6rem;">
                                    <span style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">{topic}</span>
                                    {get_priority_badge(prio)}
                                </div>
                                <span class="badge-pill badge-source">{src_id}</span>
                            </div>
                            <div style="margin-bottom: 0.5rem; font-size: 0.85rem; color: #94A3B8;">
                                Status: <strong style="color: #F1F5F9;">{status}</strong>
                            </div>
                            <div class="quote-callout">
                                "{quote}"
                            </div>
                            <div class="{rtl_class}" style="color: #CBD5E1; font-size: 0.92rem; margin: 0.5rem 0;">
                                {expl}
                            </div>
                            {f'<div style="background: rgba(99, 102, 241, 0.1); border-left: 3px solid #818CF8; padding: 0.5rem 0.8rem; border-radius: 4px; font-size: 0.86rem; color: #C7D2FE; margin-top: 0.5rem;"><strong>Suggested Question:</strong> {clarify}</div>' if clarify else ''}
                            {f'<div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #34D399; padding: 0.5rem 0.8rem; border-radius: 4px; font-size: 0.86rem; color: #A7F3D0; margin-top: 0.4rem;"><strong>Recommended Action:</strong> {action}</div>' if action else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                gen_findings = data.get("general_findings", [])
                for gf in gen_findings:
                    st.markdown(
                        f"""
                        <div class="dl-card dl-card-glow-indigo">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">{gf.get('topic', 'Topic')}</span>
                                <span class="badge-pill badge-source">{gf.get('source_id', 'Source')}</span>
                            </div>
                            <div class="{rtl_class}" style="color: #E2E8F0; font-size: 0.95rem; margin-bottom: 0.5rem;">
                                {gf.get('key_fact', '')}
                            </div>
                            <div class="quote-callout">
                                "{gf.get('source_passage', '')}"
                            </div>
                            {f'<div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #34D399; padding: 0.5rem 0.8rem; border-radius: 4px; font-size: 0.86rem; color: #A7F3D0; margin-top: 0.4rem;"><strong>Action:</strong> {gf.get("suggested_action")}</div>' if gf.get("suggested_action") else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        with tab_details:
            kd = data.get("key_details", {})
            col_k1, col_k2 = st.columns(2)
            with col_k1:
                st.markdown(
                    f"""
                    <div class="dl-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #818CF8;">👥 Parties & Entities</h4>
                        <p style="color: #F1F5F9; font-size: 0.92rem;">{kd.get('parties', 'Not found')}</p>
                        
                        <h4 style="margin: 1rem 0 0.5rem 0; color: #818CF8;">📅 Dates & Effective Term</h4>
                        <p style="color: #F1F5F9; font-size: 0.92rem;">{kd.get('effective_date', 'Not found')}</p>
                        
                        <h4 style="margin: 1rem 0 0.5rem 0; color: #818CF8;">💰 Amounts & Currency</h4>
                        <p style="color: #F1F5F9; font-size: 0.92rem;">{kd.get('amounts_and_currency', 'Not found')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_k2:
                st.markdown(
                    f"""
                    <div class="dl-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #818CF8;">💳 Payment Terms</h4>
                        <p style="color: #F1F5F9; font-size: 0.92rem;">{kd.get('payment_terms', 'Not found')}</p>
                        
                        <h4 style="margin: 1rem 0 0.5rem 0; color: #818CF8;">⏱️ Deadlines & Milestones</h4>
                        <p style="color: #F1F5F9; font-size: 0.92rem;">{kd.get('deadlines', 'Not found')}</p>
                        
                        <h4 style="margin: 1rem 0 0.5rem 0; color: #818CF8;">📋 Core Responsibilities</h4>
                        <p style="color: #F1F5F9; font-size: 0.92rem;">{kd.get('responsibilities', 'Not found')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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
        st.markdown(
            f"""
            <div class="dl-card dl-card-glow-emerald">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
                    <div>
                        <div style="font-size: 0.78rem; text-transform: uppercase; color: #2DD4BF; font-weight: 700; letter-spacing: 0.05em;">
                            REPORT DATE: {data.get('report_date', 'Not stated')} • {data.get('coverage_statement', 'Report Evaluated')}
                        </div>
                        <h2 style="margin: 0.2rem 0; font-size: 1.55rem; color: #FFFFFF; font-weight: 700;">
                            {data.get('report_title', 'Clinical Laboratory Report')}
                        </h2>
                        <div style="font-size: 0.8rem; color: #94A3B8;">
                            Patient Context: {data.get('patient_context', 'De-identified')}
                        </div>
                    </div>
                </div>
                <div class="{rtl_class}" style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.7; margin-top: 0.5rem;">
                    {data.get('summary', 'No summary available.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        med1, med2, med3 = st.columns(3)
        with med1:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-label">Total Analytes</div>
                    <div class="stat-value">{metrics.get('total_analytes', 0)}</div>
                    <div style="font-size: 0.72rem; color: #94A3B8;">Tested parameters</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with med2:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-label">Attention Count</div>
                    <div class="stat-value" style="color: #F87171;">{metrics.get('attention_count', 0)}</div>
                    <div style="font-size: 0.72rem; color: #94A3B8;">Outside supplied range</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with med3:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-label">Unassessed Values</div>
                    <div class="stat-value" style="color: #60A5FA;">{metrics.get('unassessed_count', 0)}</div>
                    <div style="font-size: 0.72rem; color: #94A3B8;">Missing/qualitative range</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 0.75rem 1rem; margin: 1rem 0; font-size: 0.8rem; color: #94A3B8; line-height: 1.5;">
                ℹ️ <strong>Clinical Safety Standard:</strong> 'No abnormal values identified' means only that no validated numeric result was outside its supplied interval.
                It must never be presented as a declaration that the user is healthy. This application is an educational AI Report Assistant and does not provide clinical diagnoses.
            </div>
            """,
            unsafe_allow_html=True
        )

        med_tab_results, med_tab_questions, med_tab_chat = st.tabs([
            "📊 Analyte Results & Ranges",
            "🩺 Questions for Clinician",
            "💬 AI Report Assistant Chat"
        ])

        with med_tab_results:
            results = data.get("test_results", [])
            for res in results:
                t_name = res.get("test_name", "Analyte")
                val = res.get("raw_result", "N/A")
                unit = res.get("unit", "")
                interval = res.get("raw_interval", "Not stated")
                comp = res.get("computed_comparison", "Cannot assess from the supplied range")
                flag = res.get("reported_flag", "None")
                src = res.get("source_id", "N/A")
                expl = res.get("general_explanation", "")
                doctor_q = res.get("doctor_question", "")
                has_conflict = res.get("has_conflict", False)
                conflict_note = res.get("flag_conflict_note")

                glow = "dl-card-glow-rose" if "Above" in comp or "Below" in comp or has_conflict else ("dl-card-glow-emerald" if "Within" in comp else "dl-card-glow-indigo")

                st.markdown(
                    f"""
                    <div class="dl-card {glow}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">{t_name}</span>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                {get_medical_comparison_badge(comp, has_conflict)}
                                <span class="badge-pill badge-source">{src}</span>
                            </div>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; margin: 0.6rem 0; font-size: 0.88rem; color: #CBD5E1;">
                            <div><strong>Observed Value:</strong> <span style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">{val}</span> {unit}</div>
                            <div><strong>Supplied Range:</strong> {interval}</div>
                            <div><strong>Reported by Laboratory:</strong> <span class="badge-pill badge-source">{flag}</span></div>
                        </div>
                        {f'<div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 0.5rem 0.8rem; font-size: 0.82rem; color: #FCA5A5; margin-bottom: 0.5rem;">⚠️ {conflict_note}</div>' if conflict_note else ''}
                        <div class="{rtl_class}" style="margin: 0.6rem 0; font-size: 0.88rem; color: #94A3B8; line-height: 1.6;">
                            <span style="font-size: 0.76rem; text-transform: uppercase; font-weight: 700; color: #38BDF8;">[General explanation]</span> {expl}
                        </div>
                        <div style="background: rgba(20, 184, 166, 0.1); border-left: 3px solid #14B8A6; padding: 0.5rem 0.8rem; border-radius: 4px; font-size: 0.86rem; color: #5EEAD4; margin-top: 0.5rem;">
                            <strong>Question for your Doctor:</strong> {doctor_q}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with med_tab_questions:
            st.markdown("##### 🩺 Doctor Discussion Checklist")
            st.caption("Actionable questions tailored from your laboratory report to ask your clinician during your next visit.")
            checklist = data.get("doctor_discussion_checklist", [])
            for idx, q in enumerate(checklist, 1):
                st.markdown(
                    f"""
                    <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid #14B8A6; border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 0.6rem; color: #F1F5F9; font-size: 0.92rem;">
                        <strong>{idx}.</strong> {q}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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
        st.markdown(
            f"""
            <div class="dl-card dl-card-glow-amber">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
                    <div>
                        <div style="font-size: 0.78rem; text-transform: uppercase; color: #FBBF24; font-weight: 700; letter-spacing: 0.05em;">
                            {data.get('course_or_subject', 'Study Material')} • COVERAGE: {data.get('coverage_statement', 'Module Analyzed')}
                        </div>
                        <h2 style="margin: 0.2rem 0; font-size: 1.55rem; color: #FFFFFF; font-weight: 700;">
                            Learning Overview & Concept Synthesis
                        </h2>
                    </div>
                </div>
                <div class="{rtl_class}" style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.7;">
                    {data.get('summary', 'No summary available.')}
                </div>
                <div class="{rtl_class}" style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid rgba(255, 255, 255, 0.08); color: #E2E8F0; font-size: 0.92rem; line-height: 1.6;">
                    <strong>Topic Interplay:</strong> {data.get('topic_overview', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        study_tab_notes, study_tab_quiz, study_tab_chat = st.tabs([
            "📚 Revision Notes & Concepts",
            "📝 Practice Quiz (5 MCQs)",
            "💬 Ask the Notes"
        ])

        with study_tab_notes:
            notes = data.get("revision_notes", [])
            for n in notes:
                cat = n.get("category", "Key Concept")
                title = n.get("title", "Concept")
                content = n.get("content", "")
                src = n.get("source_id", "Source")
                quote = n.get("source_passage", "")
                ex = n.get("assistant_example")

                st.markdown(
                    f"""
                    <div class="dl-card dl-card-glow-indigo">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span class="badge-pill badge-source">{cat.upper()}</span>
                                <span style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">{title}</span>
                            </div>
                            <span class="badge-pill badge-source">{src}</span>
                        </div>
                        <div class="{rtl_class}" style="color: #E2E8F0; font-size: 0.94rem; line-height: 1.7; margin: 0.5rem 0;">
                            {content}
                        </div>
                        <div class="quote-callout">
                            "{quote}"
                        </div>
                        {f'<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #F59E0B; padding: 0.5rem 0.8rem; border-radius: 4px; font-size: 0.86rem; color: #FCD34D; margin-top: 0.4rem;"><strong>[Assistant Example]:</strong> {ex}</div>' if ex else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with study_tab_quiz:
            quiz_list = data.get("quiz", [])
            st.markdown("##### 📝 Grounded Practice Quiz (5 Questions)")
            st.caption("Multiple-choice questions generated strictly from your notes. Correct answers are hidden until submission.")

            with st.form("study_quiz_form"):
                current_choices = {}
                for idx, q in enumerate(quiz_list):
                    q_id = q.get("question_id", idx + 1)
                    q_stem = q.get("question", "")
                    options = q.get("options", [])
                    st.markdown(f"**Q{q_id}. {q_stem}**")

                    existing_val = st.session_state.quiz_user_answers.get(q_id, None)

                    selected = st.radio(
                        f"Choice for Q{q_id}",
                        options=list(range(len(options))),
                        format_func=lambda i: f"[{chr(65+i)}] {options[i]}",
                        key=f"quiz_radio_{q_id}",
                        index=existing_val if existing_val is not None else 0,
                        label_visibility="collapsed"
                    )
                    current_choices[q_id] = selected
                    st.markdown("---")

                col_sub, col_retake = st.columns([1, 1])
                with col_sub:
                    submitted = st.form_submit_button("✅ Submit Answers", use_container_width=True)

            if submitted:
                st.session_state.quiz_submitted = True
                st.session_state.quiz_user_answers = current_choices
                st.session_state.quiz_results = calculate_quiz_score(quiz_list, current_choices)
                st.rerun()

            if st.session_state.quiz_submitted and st.session_state.quiz_results:
                res = st.session_state.quiz_results
                score = res.get("score", 0)
                tot = res.get("total", 5)
                pct = res.get("percentage", 0.0)

                st.markdown(
                    f"""
                    <div class="dl-card dl-card-glow-emerald" style="margin-top: 1.5rem; text-align: center;">
                        <h3 style="margin: 0; color: #FFFFFF;">Quiz Results</h3>
                        <div style="font-size: 2.5rem; font-weight: 800; color: #34D399; margin: 0.5rem 0;">
                            {score} / {tot} ({pct}%)
                        </div>
                        <div style="font-size: 0.9rem; color: #CBD5E1;">
                            {'🎉 Excellent mastery of the study material!' if pct >= 80 else ('👍 Good effort! Review the detailed answer keys below to strengthen weak areas.' if pct >= 60 else '⚠️ Review the revision notes and cited passages to reinforce key concepts.')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("#### 🔍 Answer Breakdown & Citations")
                for item in res.get("details", []):
                    q_num = item["question_id"]
                    is_corr = item["is_correct"]
                    u_pick = item["user_choice"]
                    c_pick = item["correct_choice"]
                    opts = item["options"]
                    expl = item["explanation"]
                    src = item["source_id"]
                    passage = item["source_passage"]

                    badge_class = "badge-clear" if is_corr else "badge-high"
                    status_label = "✅ Correct" if is_corr else "❌ Incorrect"

                    st.markdown(
                        f"""
                        <div class="dl-card" style="border-left: 4px solid {'#10B981' if is_corr else '#EF4444'};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <span style="font-size: 1rem; font-weight: 700; color: #FFFFFF;">Q{q_num}: {item['question']}</span>
                                <div style="display: flex; gap: 0.4rem;">
                                    <span class="badge-pill {badge_class}">{status_label}</span>
                                    <span class="badge-pill badge-source">{src}</span>
                                </div>
                            </div>
                            <div style="font-size: 0.88rem; margin: 0.4rem 0;">
                                Your Answer: <strong style="color: {'#34D399' if is_corr else '#F87171'};">[{chr(65+u_pick)}] {opts[u_pick]}</strong>
                                {f'<br>Correct Answer: <strong style="color: #34D399;">[{chr(65+c_pick)}] {opts[c_pick]}</strong>' if not is_corr else ''}
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.7); border-radius: 6px; padding: 0.6rem 0.8rem; font-size: 0.86rem; color: #CBD5E1; margin-top: 0.4rem;">
                                <strong>Explanation:</strong> {expl}
                            </div>
                            <div class="quote-callout">
                                "{passage}"
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

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
    st.markdown(
        """
        <div class="dl-card" style="margin-top: 1rem; padding: 2.2rem; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 0.8rem;">📑</div>
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #FFFFFF;">
                Welcome to DocuLens AI
            </h2>
            <p style="color: #94A3B8; font-size: 1rem; max-width: 650px; margin: 0.8rem auto 1.5rem auto; line-height: 1.6;">
                Upload a contract, clinical report, or lecture module above — or choose a pre-loaded demo document in the sidebar to explore grounded document intelligence.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; text-align: left; margin-top: 1rem;">
                <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.2rem;">
                    <div style="font-size: 1.2rem; margin-bottom: 0.3rem;">📄 <strong>Document Lens</strong></div>
                    <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                        Examines contracts & general agreements against a 6-topic checklist. Flags vague clauses and missing terms with deterministic review priorities.
                    </div>
                </div>
                <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.2rem;">
                    <div style="font-size: 1.2rem; margin-bottom: 0.3rem;">🩺 <strong>Medical Lens</strong></div>
                    <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                        Explains laboratory reports with boundary-tested interval comparisons, detects lab flag conflicts, and prepares doctor discussion checklists.
                    </div>
                </div>
                <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.2rem;">
                    <div style="font-size: 1.2rem; margin-bottom: 0.3rem;">🎓 <strong>Study Lens</strong></div>
                    <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                        Structures definitions, key formulas, and study steps from notes. Generates an interactive 5-question practice quiz with hidden answers and scoring.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

