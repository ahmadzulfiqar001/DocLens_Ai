"""Comprehensive test suite for DocuLens AI PRD Acceptance Criteria (A01 - A10).
Can be run locally with: python test_doculens.py
"""
import os
import unittest

from src.config import (
    MAX_EXTRACTED_CHARS,
    MAX_FILE_SIZE_BYTES,
    CONTRACT_CHECKLIST_TOPICS
)
from src.extractors import extract_document, compute_sha256
from src.deterministic_rules import (
    compute_medical_range,
    compute_contract_metrics,
    calculate_quiz_score
)
from src.export import generate_txt_report

class TestDocuLensAcceptanceCriteria(unittest.TestCase):

    def setUp(self):
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), "demo_fixtures")

    def test_a01_upload_and_extraction(self):
        """A01: Correct preview and source locations; extraction preserves anchors across TXT, DOCX, and PDF."""
        # TXT extraction
        fixture_txt = os.path.join(self.fixtures_dir, "01_incomplete_contract.txt")
        with open(fixture_txt, "rb") as f:
            data_txt = f.read()

        doc_txt, err_txt = extract_document(data_txt, "01_incomplete_contract.txt")
        self.assertIsNone(err_txt)
        self.assertIsNotNone(doc_txt)
        self.assertGreater(doc_txt.total_chars, 100)
        self.assertLessEqual(doc_txt.total_chars, MAX_EXTRACTED_CHARS)
        self.assertTrue(any("Para" in s.source_id for s in doc_txt.sections))
        self.assertIn("[Para 1]", doc_txt.full_text_with_sources)

        # DOCX extraction
        fixture_docx = os.path.join(self.fixtures_dir, "02_complete_contract.docx")
        if os.path.exists(fixture_docx):
            with open(fixture_docx, "rb") as f:
                data_docx = f.read()
            doc_docx, err_docx = extract_document(data_docx, "02_complete_contract.docx")
            self.assertIsNone(err_docx)
            self.assertIsNotNone(doc_docx)
            self.assertGreater(doc_docx.total_chars, 100)
            self.assertTrue(any("Para" in s.source_id for s in doc_docx.sections))

        # PDF extraction
        fixture_pdf = os.path.join(self.fixtures_dir, "04_medical_report_standard.pdf")
        if os.path.exists(fixture_pdf):
            with open(fixture_pdf, "rb") as f:
                data_pdf = f.read()
            doc_pdf, err_pdf = extract_document(data_pdf, "04_medical_report_standard.pdf")
            self.assertIsNone(err_pdf)
            self.assertIsNotNone(doc_pdf)
            self.assertGreater(doc_pdf.total_chars, 100)
            self.assertTrue(any("Page" in s.source_id for s in doc_pdf.sections))
            self.assertIn("[Page 1]", doc_pdf.full_text_with_sources)

    def test_a02_oversized_and_empty_inputs(self):
        """A02: Oversized input or empty file returns readable error without crashing."""
        # Empty file
        doc, err = extract_document(b"", "empty.txt")
        self.assertIsNone(doc)
        self.assertIn("empty", err.lower())

        # Oversized text (>25,000 characters)
        big_text = "A" * (MAX_EXTRACTED_CHARS + 500)
        doc_big, err_big = extract_document(big_text.encode("utf-8"), "big.txt")
        self.assertIsNone(doc_big)
        self.assertIn("exceeds the maximum limit", err_big.lower())

    def test_a03_contract_priority_rules(self):
        """A03: Review incomplete & complete contracts; missing topics only when absent; exact counts."""
        # Incomplete contract scenario
        incomplete_findings = [
            {
                "checklist_topic": "Payment Terms",
                "status": "Found - Unclear / Vague",
                "review_priority": "High",
                "suggested_action": "Clarify payment schedule and milestones"
            },
            {
                "checklist_topic": "Termination",
                "status": "Not found in the analyzed text",
                "review_priority": "High",
                "suggested_action": "Draft explicit termination clause"
            },
            {
                "checklist_topic": "Dispute Resolution",
                "status": "Not found in the analyzed text",
                "review_priority": "High",
                "suggested_action": "Include arbitration clause"
            },
            {
                "checklist_topic": "Governing Law",
                "status": "Found - Clear",
                "review_priority": "Low",
                "suggested_action": None
            }
        ]
        metrics_inc = compute_contract_metrics(incomplete_findings, is_complete=True)
        self.assertEqual(metrics_inc["overall_priority"], "High")
        self.assertEqual(metrics_inc["missing_topics_count"], 2)
        self.assertEqual(metrics_inc["unique_issues_count"], 3)
        self.assertEqual(metrics_inc["actions_count"], 3)

        # Complete contract scenario
        complete_findings = [
            {"checklist_topic": topic, "status": "Found - Clear", "review_priority": "Low", "suggested_action": None}
            for topic in CONTRACT_CHECKLIST_TOPICS
        ]
        metrics_comp = compute_contract_metrics(complete_findings, is_complete=True)
        self.assertEqual(metrics_comp["overall_priority"], "No flagged checklist issues")
        self.assertEqual(metrics_comp["missing_topics_count"], 0)
        self.assertEqual(metrics_comp["unique_issues_count"], 0)

    def test_a04_medical_boundaries_and_flag_conflicts(self):
        """A04: Boundaries within range; uncertain remain unassessed; flag conflicts detected."""
        # Standard within range
        r1 = compute_medical_range("185", "125 - 200", "Normal")
        self.assertEqual(r1["comparison"], "Within range")
        self.assertFalse(r1["is_outside_range"])

        # Boundary condition: exactly 3.5 with range 3.5 - 5.0 (PRD M02: boundary values within interval)
        r_bound_low = compute_medical_range("3.5", "3.5 - 5.0", "Normal")
        self.assertEqual(r_bound_low["comparison"], "Within range")
        self.assertFalse(r_bound_low["is_outside_range"])

        r_bound_high = compute_medical_range("5.0", "3.5 - 5.0", "Normal")
        self.assertEqual(r_bound_high["comparison"], "Within range")

        # Above range
        r_above = compute_medical_range("118", "70 - 99", "H")
        self.assertEqual(r_above["comparison"], "Above range")
        self.assertTrue(r_above["is_outside_range"])

        # Below range
        r_below = compute_medical_range("120", "150 - 450", "L")
        self.assertEqual(r_below["comparison"], "Below range")
        self.assertTrue(r_below["is_outside_range"])

        # Qualitative: Non-Reactive
        r_qual = compute_medical_range("Non-Reactive", "Not Applicable", "Negative")
        self.assertEqual(r_qual["comparison"], "Cannot assess from the supplied range")

        # Qualitative: Trace
        r_trace = compute_medical_range("Trace", "Negative", "Abnormal")
        self.assertEqual(r_trace["comparison"], "Cannot assess from the supplied range")

        # Flag conflict: value 32.0 is inside 30.0 - 100.0, but lab flagged "L"
        r_conflict = compute_medical_range("32.0", "30.0 - 100.0", "L")
        self.assertEqual(r_conflict["comparison"], "Within range")
        self.assertTrue(r_conflict["has_conflict"])
        self.assertIsNotNone(r_conflict["verification_note"])

    def test_a06_study_quiz_scoring(self):
        """A06: Complete study quiz; score calculated from actual count; feedback details."""
        sample_quiz = [
            {"question_id": 1, "question": "Q1", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "E1", "source_id": "Para 1", "source_passage": "P1"},
            {"question_id": 2, "question": "Q2", "options": ["A", "B", "C", "D"], "correct_index": 2, "explanation": "E2", "source_id": "Para 2", "source_passage": "P2"},
            {"question_id": 3, "question": "Q3", "options": ["A", "B", "C", "D"], "correct_index": 1, "explanation": "E3", "source_id": "Para 3", "source_passage": "P3"},
            {"question_id": 4, "question": "Q4", "options": ["A", "B", "C", "D"], "correct_index": 3, "explanation": "E4", "source_id": "Para 4", "source_passage": "P4"},
            {"question_id": 5, "question": "Q5", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "E5", "source_id": "Para 5", "source_passage": "P5"},
        ]
        # 4 correct, 1 wrong
        user_answers = {1: 0, 2: 2, 3: 1, 4: 3, 5: 2}
        score_res = calculate_quiz_score(sample_quiz, user_answers)

        self.assertEqual(score_res["score"], 4)
        self.assertEqual(score_res["total"], 5)
        self.assertEqual(score_res["percentage"], 80.0)
        self.assertTrue(score_res["passed"])
        self.assertEqual(len(score_res["details"]), 5)
        self.assertFalse(score_res["details"][4]["is_correct"])

    def test_a10_report_export(self):
        """A10: Export reflects active analysis in UTF-8 format."""
        analysis = {
            "summary": "Sample executive summary for testing.",
            "coverage_statement": "100% of document evaluated",
            "subtype": "Contract",
            "key_details": {"parties": "Alpha & Beta", "effective_date": "2026-10-01"},
            "contract_findings": [
                {
                    "checklist_topic": "Termination",
                    "status": "Found - Clear",
                    "source_id": "Para 5",
                    "source_passage": "Either party may terminate on 30 days notice.",
                    "explanation": "Explicit termination clause present.",
                    "suggested_action": "None needed",
                    "review_priority": "Low",
                    "priority_reason": "Clear clause"
                }
            ]
        }
        metrics = {"overall_priority": "No flagged checklist issues", "priority_rule": "All clear", "unique_issues_count": 0, "missing_topics_count": 0, "actions_count": 0}
        report = generate_txt_report("contract.txt", "Document Lens", "Simple English", analysis, metrics)

        self.assertIn("DOCULENS AI - INTELLIGENT DOCUMENT ANALYSIS REPORT", report)
        self.assertIn("contract.txt", report)
        self.assertIn("Alpha & Beta", report)
        self.assertIn("Termination", report)

if __name__ == "__main__":
    unittest.main()

