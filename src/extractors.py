"""Document text extraction engine with source preservation and limit enforcement.
Supports PDF (up to 500 pages, including scanned pages), DOCX, TXT, MD,
and image formats (JPEG, JPG, PNG, WEBP) with multimodal transcription.
"""
import io
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from src.config import MAX_FILE_SIZE_BYTES, MAX_PDF_PAGES, MAX_EXTRACTED_CHARS, SUPPORTED_EXTENSIONS, IMAGE_EXTENSIONS

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
    Validate and extract text from PDF, DOCX, TXT, or Image files.
    Preserves valid source identifiers ([Page X] or [Para X] or [Section X]).
    Returns: (ExtractedDocument, None) if successful, or (None, error_message).
    """
    if not file_bytes or len(file_bytes) == 0:
        return None, "The uploaded file is empty (0 bytes). Please upload a valid document."

    # Size check (up to 50 MB)
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        return None, f"File size ({size_mb:.1f} MB) exceeds the maximum allowed limit of 50 MB."

    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if file_ext not in SUPPORTED_EXTENSIONS:
        return None, f"Unsupported file format '{file_ext}'. Supported formats: PDF, DOCX, TXT, MD, and Images (JPEG, PNG, WEBP)."

    file_hash = compute_sha256(file_bytes)
    sections: List[SourceSection] = []
    total_pages: Optional[int] = None
    formatting_warnings: List[str] = []

    try:
        # =====================================================================
        # 1. PDF Documents (Selectable + Scanned OCR)
        # =====================================================================
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
                return None, f"The PDF contains {total_pages} pages, which exceeds the limit of {MAX_PDF_PAGES} pages."

            extracted_chars = 0
            scanned_pages = []

            for page_idx in range(total_pages):
                page = pdf_doc.load_page(page_idx)
                page_text = page.get_text("text").strip()
                page_num = page_idx + 1

                if page_text:
                    sections.append(SourceSection(
                        source_id=f"Page {page_num}",
                        text=page_text,
                        page_num=page_num,
                        section_index=page_num
                    ))
                    extracted_chars += len(page_text)
                else:
                    scanned_pages.append((page_num, page))

            # If PDF has minimal selectable text, attempt image transcription on scanned pages
            if extracted_chars < 40 and scanned_pages:
                from src.gemini_client import get_gemini_api_key
                from google import genai
                api_key = get_gemini_api_key()
                if api_key:
                    client = genai.Client(api_key=api_key)
                    for page_num, p in scanned_pages[:10]:
                        try:
                            pix = p.get_pixmap(dpi=150)
                            img_data = pix.tobytes("jpeg")
                            part = genai.types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
                            resp = client.models.generate_content(
                                model="gemini-flash-lite-latest",
                                contents=[part, "Transcribe all text from this scanned page verbatim. Preserve numbers, headers, and tables."]
                            )
                            p_transcribed = resp.text.strip() if resp.text else ""
                            if p_transcribed:
                                sections.append(SourceSection(
                                    source_id=f"Page {page_num} (OCR)",
                                    text=p_transcribed,
                                    page_num=page_num,
                                    section_index=page_num
                                ))
                                extracted_chars += len(p_transcribed)
                        except Exception:
                            continue

            if extracted_chars < 20 and not sections:
                return None, (
                    "The uploaded PDF does not contain sufficient readable text or OCR content. "
                    "Please ensure the document contains clear text or upload a higher resolution document."
                )

        # =====================================================================
        # 2. Word Documents (.docx, .doc)
        # =====================================================================
        elif file_ext in ["docx", "doc"]:
            import docx
            try:
                doc = docx.Document(io.BytesIO(file_bytes))
            except Exception as e:
                return None, f"Failed to open Word file. File may be corrupted or encrypted. ({str(e)})"

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
                return None, "The uploaded Word document does not contain any readable text paragraphs or tables."

        # =====================================================================
        # 3. Plain Text & Markdown (.txt, .md)
        # =====================================================================
        elif file_ext in ["txt", "md"]:
            raw_text = None
            for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                try:
                    raw_text = file_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue

            if raw_text is None:
                return None, "The text file could not be decoded. Please ensure it is saved as UTF-8 encoded text."

            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [line.strip() for line in raw_text.splitlines() if line.strip()]

            para_count = 0
            for p in paragraphs:
                para_count += 1
                sections.append(SourceSection(
                    source_id=f"Para {para_count}",
                    text=p,
                    page_num=None,
                    section_index=para_count
                ))

            if not sections:
                return None, "The text file contains no readable text."

        # =====================================================================
        # 4. Images (JPEG, JPG, PNG, WEBP) via Multimodal Gemini
        # =====================================================================
        elif file_ext in IMAGE_EXTENSIONS:
            from src.gemini_client import get_gemini_api_key
            from google import genai
            api_key = get_gemini_api_key()
            if not api_key:
                return None, "Gemini API Key is required to process image files (JPEG/PNG/WEBP). Please configure GEMINI_API_KEY in Secrets."

            mime_type = "image/jpeg" if file_ext in ["jpeg", "jpg"] else f"image/{file_ext}"
            client = genai.Client(api_key=api_key)
            part = genai.types.Part.from_bytes(data=file_bytes, mime_type=mime_type)

            resp = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=[
                    part,
                    "Transcribe all readable text, labels, test names, numbers, values, and tables from this document image verbatim. "
                    "Preserve original wording and structure. Do not summarize or explain."
                ]
            )
            img_text = resp.text.strip() if resp.text else ""
            if not img_text or len(img_text) < 10:
                return None, "Unable to extract readable text from the uploaded image. Please ensure the image is clear and well-lit."

            paras = [p.strip() for p in img_text.split("\n\n") if p.strip()]
            if not paras:
                paras = [p.strip() for p in img_text.splitlines() if p.strip()]

            for p_idx, p_text in enumerate(paras, 1):
                sections.append(SourceSection(
                    source_id=f"Section {p_idx}",
                    text=p_text,
                    page_num=1,
                    section_index=p_idx
                ))
            total_pages = 1

    except Exception as e:
        return None, f"An unexpected error occurred during extraction: {str(e)}"

    # Construct unified text with source anchors
    formatted_parts = []
    total_chars = 0
    for s in sections:
        part = f"[{s.source_id}]\n{s.text}\n"
        formatted_parts.append(part)
        total_chars += len(s.text)

    # Limit check (expanded to 250,000 characters)
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
