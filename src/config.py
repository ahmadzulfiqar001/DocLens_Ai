"""Configuration constants and limits for DocuLens AI."""
import os
from typing import List, Dict

# Application Metadata
APP_NAME = "DocuLens AI"
APP_TAGLINE = "Intelligent Multi-Lens Document Analysis & Grounded Evidence Engine"
APP_VERSION = "1.0.0"

# Supported Modes
MODE_DOC_LENS = "Document Lens"
MODE_MEDICAL_LENS = "Medical Lens"
MODE_STUDY_LENS = "Study Lens"
ALL_MODES = [MODE_DOC_LENS, MODE_MEDICAL_LENS, MODE_STUDY_LENS]

# Document Lens Sub-Types (PRD: Must not silently infer legal category)
DOC_SUBTYPE_CONTRACT = "Contract / Agreement"
DOC_SUBTYPE_GENERAL = "General Document"
DOC_SUBTYPES = [DOC_SUBTYPE_CONTRACT, DOC_SUBTYPE_GENERAL]

# Supported Languages (PRD C03)
LANG_ENGLISH = "Simple English"
LANG_ROMAN_URDU = "Roman Urdu"
LANG_URDU = "Urdu (اردو)"
ALL_LANGUAGES = [LANG_ENGLISH, LANG_ROMAN_URDU, LANG_URDU]

# System Limits (PRD C01, C02)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_PDF_PAGES = 15
MAX_EXTRACTED_CHARS = 25000
SUPPORTED_EXTENSIONS = ["pdf", "docx", "txt"]

# Contract Review Topics (PRD D02, D04)
CONTRACT_CHECKLIST_TOPICS = [
    "Termination",
    "Payment Terms",
    "Obligations",
    "Duration or Renewal",
    "Dispute Resolution",
    "Governing Law"
]

# PRD D04: High covers missing or unclear payment, termination, or dispute resolution
HIGH_PRIORITY_TOPICS = ["Payment Terms", "Termination", "Dispute Resolution"]
# PRD D04: Medium covers other missing or unclear checklist topics
MEDIUM_PRIORITY_TOPICS = ["Obligations", "Duration or Renewal", "Governing Law"]

# Google Gemini Model Defaults (Verified active production models)
DEFAULT_GEMINI_MODEL = "gemini-flash-latest"
AVAILABLE_GEMINI_MODELS = [
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite"
]

# Static Avatar URL / SVG configuration (Medical Lens static AI avatar)
ASSISTANT_AVATAR_ICON = "🤖"
DOCTOR_AVATAR_ICON = "🩺"

