"""Configuration constants and limits for DocuLens AI."""
import os
from typing import List, Dict

# Application Metadata
APP_NAME = "DocuLens AI"
APP_TAGLINE = "Grounded Document Intelligence & Multi-Lens Knowledge Engine"
APP_VERSION = "2.0.0"

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

# System Limits - Expanded per user request (Removed 15 page limit, added images, Word, PDF)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_PDF_PAGES = 500  # Virtually unlimited
MAX_EXTRACTED_CHARS = 250000  # 250k characters
SUPPORTED_EXTENSIONS = ["pdf", "docx", "doc", "txt", "md", "jpeg", "jpg", "png", "webp"]
IMAGE_EXTENSIONS = ["jpeg", "jpg", "png", "webp"]

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
DEFAULT_GEMINI_MODEL = "gemini-flash-lite-latest"
AVAILABLE_GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest"
]

# Static Avatar URL / SVG configuration (Medical Lens static AI avatar)
ASSISTANT_AVATAR_ICON = "🤖"
DOCTOR_AVATAR_ICON = "🩺"
