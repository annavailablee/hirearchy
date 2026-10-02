"""Deterministic PDF text extraction. No LLM involved.

We keep this in a service module rather than in the endpoint because:
- It's a pure function — takes bytes, returns text or raises.
- It can be unit tested without HTTP or DB.
- If we later swap pypdf for a better extractor, one file changes.
"""
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PdfExtractionError(Exception):
    """Raised when a PDF cannot be parsed or yields no usable text."""


def extract_text_from_pdf(data: bytes) -> str:
    """
    Extract concatenated text from every page of a PDF.

    Raises PdfExtractionError for:
    - Corrupt / malformed PDFs
    - Encrypted PDFs we can't open
    - PDFs that yield no extractable text (e.g. pure-image scans)
    """
    try:
        reader = PdfReader(BytesIO(data))
    except PdfReadError as exc:
        raise PdfExtractionError("PDF is malformed or unreadable") from exc
    except Exception as exc:  # pypdf throws various low-level errors
        raise PdfExtractionError(f"Could not open PDF: {exc}") from exc

    if reader.is_encrypted:
        # Try empty password (common for "locked for editing" PDFs).
        try:
            if reader.decrypt("") == 0:
                raise PdfExtractionError("PDF is encrypted and requires a password")
        except PdfExtractionError:
            raise
        except Exception as exc:
            raise PdfExtractionError("PDF is encrypted") from exc

    pages_text: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            # A single bad page shouldn't nuke the whole document.
            text = ""
        pages_text.append(text)

    combined = "\n".join(pages_text).strip()

    if not combined:
        raise PdfExtractionError(
            "No extractable text found — the PDF may be a scanned image"
        )

    return combined


def looks_like_pdf(data: bytes) -> bool:
    """Magic-byte check. The Content-Type header from a client can lie."""
    return data[:5] == b"%PDF-"