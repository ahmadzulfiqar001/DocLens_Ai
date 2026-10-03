"""Structured Pydantic schemas for DocuLens AI analysis modes."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# -------------------------------------------------------------
# Base / Shared Models
# -------------------------------------------------------------
class SourceReference(BaseModel):
    source_id: str = Field(..., description="Source location identifier such as 'Page 1' or 'Para 3'")
    exact_text: str = Field(..., description="Verbatim text quotation from the source")

# -------------------------------------------------------------
# Document Lens Models
# -------------------------------------------------------------
class KeyDetails(BaseModel):
    parties: str = Field("Not found", description="Identified parties or entities")
    effective_date: str = Field("Not found", description="Explicit start date or execution date")
    amounts_and_currency: str = Field("Not found", description="Explicit financial figures preserving currency")
    payment_terms: str = Field("Not found", description="Payment frequency, milestones, or deadlines")
    deadlines: str = Field("Not found", description="Explicit delivery dates or milestones")
    responsibilities: str = Field("Not found", description="Core duties or deliverables assigned")

class ContractChecklistFinding(BaseModel):
    checklist_topic: str = Field(..., description="e.g. Termination, Payment Terms, Obligations, etc.")
    status: str = Field(..., description="'Found - Clear', 'Found - Unclear / Vague', or 'Not found in the analyzed text'")
    source_id: str = Field("Not found", description="Location identifier like 'Para 3' or 'Not found'")
    source_passage: str = Field("Not found in the analyzed text", description="Exact quotation or 'Not found in the analyzed text'")
    explanation: str = Field(..., description="Detailed explanation of the topic's status in this document")
    clarification_question: Optional[str] = Field(None, description="Actionable question to clarify if vague or missing")
    suggested_action: Optional[str] = Field(None, description="Recommended next step for the reader")
    review_priority: str = Field("Low", description="Review priority: 'High', 'Medium', or 'Low'")
    priority_reason: str = Field("", description="Justification for the assigned priority level")

class GeneralDocumentFinding(BaseModel):
    finding_id: str = Field(..., description="Identifier e.g. 'F-01'")
    topic: str = Field(..., description="Topic or section name")
    key_fact: str = Field(..., description="Important rule, requirement, or observation")
    source_id: str = Field(..., description="Location reference e.g. 'Para 2'")
    source_passage: str = Field(..., description="Exact quoted text supporting this fact")
    suggested_action: Optional[str] = Field(None, description="Recommended operational action or verification")

class DocumentLensAnalysis(BaseModel):
    document_title: str
    subtype: str  # "Contract" or "General Document"
    coverage_statement: str
    summary: str
    key_details: KeyDetails
    contract_findings: Optional[List[ContractChecklistFinding]] = []
    general_findings: Optional[List[GeneralDocumentFinding]] = []
    informational_observations: Optional[List[str]] = []

# -------------------------------------------------------------
# Medical Lens Models
# -------------------------------------------------------------
class MedicalTestResult(BaseModel):
    test_name: str = Field(..., description="Official test or analyte name")
    raw_result: str = Field(..., description="Unchanged numeric or qualitative result string")
    unit: str = Field("None", description="Unit of measurement e.g. mg/dL, mmol/L, %")
    raw_interval: str = Field("Not stated", description="Original reference interval stated in the report")
    reported_flag: str = Field("None", description="Explicit laboratory flag e.g. 'H', 'L', 'Normal', 'Abnormal', 'None'")
    source_id: str = Field(..., description="Source identifier e.g. 'Para 2'")
    source_passage: str = Field(..., description="Verbatim text containing this test result")
    extraction_status: str = Field("Valid", description="'Valid' or 'Needs verification'")
    general_explanation: str = Field(..., description="General educational explanation of what this test measures")
    doctor_question: str = Field(..., description="Specific question for the patient's clinician")

class MedicalLensAnalysis(BaseModel):
    report_title: str
    report_date: str = Field("Not stated", description="Date the report was issued or specimen taken")
    patient_context: str = Field("De-identified / Not stated", description="De-identified patient context")
    coverage_statement: str
    summary: str
    test_results: List[MedicalTestResult]
    doctor_discussion_checklist: List[str]

# -------------------------------------------------------------
# Study Lens Models
# -------------------------------------------------------------
class RevisionNoteItem(BaseModel):
    category: str = Field(..., description="'Definition', 'Key Concept', 'Formula / Equation', or 'Study Step'")
    title: str = Field(..., description="Short title of the revision item")
    content: str = Field(..., description="Clear explanation or formula")
    source_id: str = Field(..., description="Location reference e.g. 'Para 2'")
    source_passage: str = Field(..., description="Direct quote from the notes")
    assistant_example: Optional[str] = Field(None, description="Clarifying example created by the assistant, clearly labeled")

class QuizQuestion(BaseModel):
    question_id: int = Field(..., description="Question number 1 to 5")
    question: str = Field(..., description="Clear question stem grounded strictly in the material")
    options: List[str] = Field(..., min_length=4, max_length=4, description="Four distinct multiple-choice options")
    correct_index: int = Field(..., ge=0, le=3, description="0-based index of the single correct answer")
    explanation: str = Field(..., description="Detailed explanation of why the correct option is right")
    source_id: str = Field(..., description="Location reference e.g. 'Para 3'")
    source_passage: str = Field(..., description="Verbatim text from notes supporting the answer")

class StudyLensAnalysis(BaseModel):
    course_or_subject: str
    coverage_statement: str
    summary: str
    topic_overview: str
    revision_notes: List[RevisionNoteItem]
    quiz: List[QuizQuestion]

