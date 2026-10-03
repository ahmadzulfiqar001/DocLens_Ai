"""UTF-8 text analysis report exporter for DocuLens AI.
Complies with PRD C05 and A10 requirements.
"""
from datetime import datetime
from typing import Dict, Any, List

def generate_txt_report(
    filename: str,
    mode: str,
    language: str,
    analysis_data: Dict[str, Any],
    deterministic_metrics: Dict[str, Any]
) -> str:
    """Generates a complete, structured, human-readable UTF-8 text report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []

    # Header
    lines.append("=" * 78)
    lines.append(" DOCULENS AI - INTELLIGENT DOCUMENT ANALYSIS REPORT")
    lines.append("=" * 78)
    lines.append(f"Source File       : {filename}")
    lines.append(f"Analysis Mode     : {mode}")
    lines.append(f"Output Language   : {language}")
    lines.append(f"Report Generated  : {timestamp}")
    lines.append(f"Coverage Status   : {analysis_data.get('coverage_statement', 'N/A')}")
    lines.append("=" * 78)
    lines.append("")

    # Executive Summary
    lines.append("--- EXECUTIVE SUMMARY ---")
    lines.append(analysis_data.get("summary", "No summary available."))
    lines.append("")

    # Mode-Specific Sections
    if mode == "Document Lens":
        subtype = analysis_data.get("subtype", "Document")
        lines.append(f"--- DOCUMENT SUBTYPE: {subtype.upper()} ---")
        
        # Contract-specific metrics
        if subtype.lower() == "contract" or "contract_findings" in analysis_data:
            p_val = deterministic_metrics.get("overall_priority", "N/A")
            lines.append(f"Overall Review Priority : {p_val}")
            lines.append(f"Priority Rule           : {deterministic_metrics.get('priority_rule', 'N/A')}")
            lines.append(f"Flagged Issues Count    : {deterministic_metrics.get('unique_issues_count', 0)}")
            lines.append(f"Missing Topics Count    : {deterministic_metrics.get('missing_topics_count', 0)}")
            lines.append(f"Recommended Actions     : {deterministic_metrics.get('actions_count', 0)}")
            lines.append("")

            lines.append("--- CONTRACT CHECKLIST EVALUATION ---")
            findings = analysis_data.get("contract_findings", [])
            for idx, f in enumerate(findings, 1):
                topic = f.get("checklist_topic", "N/A")
                status = f.get("status", "N/A")
                src = f.get("source_id", "N/A")
                prio = f.get("review_priority", "Low")
                quote = f.get("source_passage", "N/A")
                explanation = f.get("explanation", "")
                action = f.get("suggested_action", "")
                clarify = f.get("clarification_question", "")

                lines.append(f"[{idx}] Topic: {topic}")
                lines.append(f"    Status       : {status}")
                lines.append(f"    Priority     : {prio} (Reason: {f.get('priority_reason', 'N/A')})")
                lines.append(f"    Source       : {src}")
                lines.append(f"    Quotation    : \"{quote}\"")
                lines.append(f"    Explanation  : {explanation}")
                if clarify:
                    lines.append(f"    Clarification: {clarify}")
                if action:
                    lines.append(f"    Action Item  : {action}")
                lines.append("-" * 50)
        else:
            # General document findings
            lines.append("--- KEY FINDINGS & RULES ---")
            for idx, f in enumerate(analysis_data.get("general_findings", []), 1):
                lines.append(f"[{idx}] Topic: {f.get('topic', 'N/A')}")
                lines.append(f"    Key Fact     : {f.get('key_fact', '')}")
                lines.append(f"    Source       : {f.get('source_id', 'N/A')}")
                lines.append(f"    Quotation    : \"{f.get('source_passage', 'N/A')}\"")
                if f.get("suggested_action"):
                    lines.append(f"    Action       : {f.get('suggested_action')}")
                lines.append("-" * 50)

        # Key Details
        kd = analysis_data.get("key_details", {})
        if kd:
            lines.append("")
            lines.append("--- KEY EXTRACTED DETAILS ---")
            lines.append(f"Parties Identified   : {kd.get('parties', 'Not found')}")
            lines.append(f"Effective Date       : {kd.get('effective_date', 'Not found')}")
            lines.append(f"Amounts & Currency   : {kd.get('amounts_and_currency', 'Not found')}")
            lines.append(f"Payment Terms        : {kd.get('payment_terms', 'Not found')}")
            lines.append(f"Deadlines/Milestones : {kd.get('deadlines', 'Not found')}")
            lines.append(f"Responsibilities     : {kd.get('responsibilities', 'Not found')}")

    elif mode == "Medical Lens":
        lines.append("--- MEDICAL LABORATORY ANALYSIS ---")
        lines.append("DISCLAIMER: AI Report Assistant observations are educational only.")
        lines.append("No medical diagnosis, severity assessment, or prescription is provided.")
        lines.append("No abnormal values identified means only that no validated result was outside")
        lines.append("its supplied interval. It must never be presented as a declaration of health.")
        lines.append("")
        lines.append(f"Report Date          : {analysis_data.get('report_date', 'Not stated')}")
        lines.append(f"Patient Context      : {analysis_data.get('patient_context', 'De-identified')}")
        lines.append(f"Attention Needed     : {deterministic_metrics.get('attention_count', 0)} values outside interval")
        lines.append(f"Unassessed Values    : {deterministic_metrics.get('unassessed_count', 0)} missing/qualitative ranges")
        lines.append("")

        lines.append("--- TEST RESULTS EVALUATION ---")
        for idx, res in enumerate(analysis_data.get("test_results", []), 1):
            name = res.get("test_name", "N/A")
            raw_val = res.get("raw_result", "N/A")
            unit = res.get("unit", "")
            interval = res.get("raw_interval", "Not stated")
            flag = res.get("reported_flag", "None")
            src = res.get("source_id", "N/A")
            comp = res.get("computed_comparison", "Cannot assess from the supplied range")
            expl = res.get("general_explanation", "")
            q = res.get("doctor_question", "")

            lines.append(f"[{idx}] {name}")
            lines.append(f"    Value & Unit       : {raw_val} {unit}".strip())
            lines.append(f"    Stated Interval    : {interval}")
            lines.append(f"    App Comparison     : {comp}")
            lines.append(f"    Reported Lab Flag  : {flag}")
            lines.append(f"    Source Location    : {src}")
            lines.append(f"    General Explanation: {expl}")
            lines.append(f"    Doctor Question    : {q}")
            if res.get("flag_conflict_note"):
                lines.append(f"    * NOTE: {res.get('flag_conflict_note')}")
            lines.append("-" * 50)

        lines.append("")
        lines.append("--- DOCTOR DISCUSSION CHECKLIST ---")
        for idx, q in enumerate(analysis_data.get("doctor_discussion_checklist", []), 1):
            lines.append(f"[{idx}] {q}")

    elif mode == "Study Lens":
        lines.append("--- STUDY MATERIAL OVERVIEW ---")
        lines.append(f"Course / Subject  : {analysis_data.get('course_or_subject', 'General Study Material')}")
        lines.append(f"Topic Overview    : {analysis_data.get('topic_overview', '')}")
        lines.append("")

        lines.append("--- REVISION NOTES ---")
        for idx, note in enumerate(analysis_data.get("revision_notes", []), 1):
            cat = note.get("category", "Concept")
            title = note.get("title", "")
            content = note.get("content", "")
            src = note.get("source_id", "")
            quote = note.get("source_passage", "")
            ex = note.get("assistant_example")

            lines.append(f"[{idx}] [{cat.upper()}] {title}")
            lines.append(f"    Content        : {content}")
            lines.append(f"    Source Cited   : {src}")
            lines.append(f"    Source Quote   : \"{quote}\"")
            if ex:
                lines.append(f"    [Assistant Example]: {ex}")
            lines.append("-" * 50)

        lines.append("")
        lines.append("--- PRACTICE QUIZ QUESTIONS (5 MCQs) ---")
        for idx, q in enumerate(analysis_data.get("quiz", []), 1):
            lines.append(f"Question {idx}: {q.get('question', '')}")
            for opt_idx, opt in enumerate(q.get("options", [])):
                letter = chr(65 + opt_idx)
                lines.append(f"   [{letter}] {opt}")
            correct_letter = chr(65 + q.get("correct_index", 0))
            lines.append(f"   Correct Answer : Option [{correct_letter}]")
            lines.append(f"   Explanation    : {q.get('explanation', '')}")
            lines.append(f"   Source Cited   : {q.get('source_id', '')}")
            lines.append("-" * 50)

    lines.append("")
    lines.append("=" * 78)
    lines.append(" END OF DOCULENS AI REPORT")
    lines.append("=" * 78)
    return "\n".join(lines)

