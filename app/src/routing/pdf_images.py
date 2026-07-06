"""PDF extraction helpers for E2-4 auto dispatcher.

Provides text extraction and optional page-to-image conversion. The image
conversion is best-effort: if ``pdf2image`` is unavailable, the page_images
list will be empty and the dispatcher will fall back to text-only summarization.
"""

from __future__ import annotations

from typing import Any


# Optional dependency; not required for tests or text-only flows.
try:
    from pdf2image import convert_from_bytes
except Exception:  # pragma: no cover
    convert_from_bytes = None  # type: ignore[assignment,misc]


def extract_pdf_text_and_images(pdf_bytes: bytes) -> dict[str, Any]:
    """Return {'text': str, 'page_images': list[bytes]} from a PDF.

    text is always extracted via pdfplumber. page_images requires pdf2image
    and poppler; otherwise it returns an empty list.
    """

    from ..kb_extractors import extract_from_pdf

    text = ""
    try:
        extracted = extract_from_pdf(pdf_bytes)
        text_parts: list[str] = []
        if isinstance(extracted, dict):
            if extracted.get("text"):
                text_parts.append(str(extracted["text"]))
            tables = extracted.get("tables") or []
            for table in tables:
                if isinstance(table, list):
                    text_parts.append("\n".join(" | ".join(str(cell) for cell in row) for row in table))
        else:
            text_parts.append(str(extracted))
        text = "\n\n".join(p for p in text_parts if p.strip())
    except Exception:
        text = ""

    page_images: list[bytes] = []
    if convert_from_bytes is not None:
        try:
            pil_images = convert_from_bytes(pdf_bytes, dpi=150)
            for img in pil_images:
                import io

                buf = io.BytesIO()
                img.save(buf, format="PNG")
                page_images.append(buf.getvalue())
        except Exception:
            page_images = []

    return {"text": text, "page_images": page_images}
