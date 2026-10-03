"""Document text extraction engine with source preservation and limit enforcement.
Complies with PRD C01 and C02 requirements.
"""
import io
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from src.config import MAX_FILE_SIZE_BYTES, MAX_PDF_PAGES, MAX_EXTRACTED_CHARS, SUPPORTED_EXTENSIONS

@dataclass
class SourceSection:
    source_id: str
    text: str
    page_num: Optional[int] = None
    section_index: int = 0

@dataclass
class ExtractedDocument:
    filename: str
    file_type: str
    file_hash: str
    total_pages: Optional[int]
    total_chars: int
    sections: List[SourceSection] = field(default_factory=list)
    full_text_with_sources: str = ""
    preview_snippet: str = ""
    formatting_warnings: List[str] = field(default_factory=list)

def compute_sha256(data: bytes) -> str:
    """Generate SHA-256 hash of raw uploaded file bytes."""
    return hashlib.sha256(data).hexdigest()

def extract_document(file_bytes: bytes, filename: str) -> Tuple[Optional[ExtractedDocument], Optional[str]]:
    """
    Validate and extract text from PDF, DOCX, or TXT file.
    Enforces 10 MB file size limit, 15 PDF pages limit, and 25,000 characters limit.
    Preserves valid source identifiers ([Page X] or [Para X]).
    Returns: (ExtractedDocument, None) if successful, or (None, error_message).
    """
    if not file_bytes or len(file_bytes) == 0:
        return None, "The uploaded file is empty (0 bytes). Please upload a valid document."

    # Size check (PRD C01: up to 10 MB)
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        return None, f"File size ({size_mb:.1f} MB) exceeds the maximum allowed limit of 10 MB."

    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if file_ext not in SUPPORTED_EXTENSIONS:
        return None, f"Unsupported file format '{file_ext}'. Supported formats are: PDF, DOCX, and TXT."

    file_hash = compute_sha256(file_bytes)
    sections: List[SourceSection] = []
    total_pages: Optional[int] = None
    formatting_warnings: List[str] = []

    try:
        if file_ext == "pdf":
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            try:
                pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            except Exception as e:
                return None, f"Unable to read PDF file. The file may be corrupted or malformed. ({str(e)})"

            if pdf_doc.is_encrypted:
                return None, "The uploaded PDF is encrypted or password-protected. Please upload an unencrypted PDF."

            total_pages = pdf_doc.page_count
            if total_pages > MAX_PDF_PAGES:
                return None, (
                    f"The PDF contains {total_pages} pages, which exceeds the MVP limit of {MAX_PDF_PAGES} pages. "
                    f"Please submit a document of {MAX_PDF_PAGES} pages or fewer."
                )

            extracted_chars = 0
            for page_idx in range(total_pages):
                page = pdf_doc.load_page(page_idx)
                page_text = page.get_text("text").strip()
                page_num = page_idx + 1

                # Check for tables or vector drawings that might be complex
                drawing_count = len(page.get_drawings())
                if drawing_count > 50 and not page_text:
                    formatting_warnings.append(f"Page {page_num}: Complex graphics detected without extractable text.")

                if page_text:
                    sections.append(SourceSection(
                        source_id=f"Page {page_num}",
                        text=page_text,
                        page_num=page_num,
                        section_index=page_num
                    ))
                    extracted_chars += len(page_text)

            if extracted_chars < 40:
                return None, (
                    "The uploaded PDF does not contain sufficient selectable text (less than 40 characters extracted). "
                    "It appears to be an image-only scan or unsupported format. DocuLens AI MVP requires readable text."
                )

        elif file_ext == "docx":
            import docx
            try:
                doc = docx.Document(io.BytesIO(file_bytes))
            except Exception as e:
                return None, f"Failed to open DOCX file. File may be corrupted or encrypted. ({str(e)})"

            para_count = 0
            for p in doc.paragraphs:
                p_text = p.text.strip()
                if p_text:
                    para_count += 1
                    sections.append(SourceSection(
                        source_id=f"Para {para_count}",
                        text=p_text,
                        page_num=None,
                        section_index=para_count
                    ))

            # Extract tables if present
            table_idx = 0
            for table in doc.tables:
                table_idx += 1
                table_rows = []
                for row in table.rows:
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    table_rows.append(" | ".join(row_cells))
                if table_rows:
                    para_count += 1
                    sections.append(SourceSection(
                        source_id=f"Table {table_idx}",
                        text="\n".join(table_rows),
                        page_num=None,
                        section_index=para_count
                    ))

            if not sections:
                return None, "The uploaded DOCX file does not contain any readable text paragraphs or tables."

        elif file_ext == "txt":
            # Attempt UTF-8 decoding
            raw_text = None
            for enc in ["utf-8", "utf-8-sig", "latin-1"]:
                try:
                    raw_text = file_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue

            if raw_text is None:
                return None, "The TXT file could not be decoded. Please ensure it is saved as UTF-8 encoded text."

            # Split into natural paragraphs or blocks
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [line.strip() for line in raw_text.splitlines() if line.strip()]

            para_count = 0
            for p in paragraphs:
                # Check if text already has custom source marks like [Para X] or [Page X]
                para_count += 1
                sections.append(SourceSection(
                    source_id=f"Para {para_count}",
                    text=p,
                    page_num=None,
                    section_index=para_count
                ))

            if not sections:
                return None, "The TXT file contains no readable text."

    except Exception as e:
        return None, f"An unexpected error occurred during extraction: {str(e)}"

    # Construct unified text with source anchors
    formatted_parts = []
    total_chars = 0
    for s in sections:
        part = f"[{s.source_id}]\n{s.text}\n"
        formatted_parts.append(part)
        total_chars += len(s.text)

    # Limit check (PRD C02: 25,000 characters maximum)
    if total_chars > MAX_EXTRACTED_CHARS:
        return None, (
            f"The document text ({total_chars:,} characters) exceeds the maximum limit of {MAX_EXTRACTED_CHARS:,} characters. "
            f"Please upload a shorter excerpt or document."
        )

    full_text_with_sources = "\n".join(formatted_parts)
    preview_snippet = full_text_with_sources[:1200] + ("..." if len(full_text_with_sources) > 1200 else "")

    return ExtractedDocument(
        filename=filename,
        file_type=file_ext,
        file_hash=file_hash,
        total_pages=total_pages,
        total_chars=total_chars,
        sections=sections,
        full_text_with_sources=full_text_with_sources,
        preview_snippet=preview_snippet,
        formatting_warnings=formatting_warnings
    ), None

