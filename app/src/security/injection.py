"""Injection-canary helpers for KB sources and future skill ingestion.

SL1b covers MD/TXT/CSV.  HTML, Excel and PDF ingestion are intentionally blocked
until dedicated sandboxed parsers are implemented (SL2).  This module provides the
sanitization layer that lets us reject or neutralize known vectors early.
"""

from __future__ import annotations

import csv
import io
import re
from typing import Any


# CSV formula-injection prefixes.  A cell starting with any of these can be
# interpreted as a formula by spreadsheet applications.
CSV_FORMULA_PREFIXES = ('=', '+', '-', '@')

# HTML/tag/event-handler detection.  This is a guard rail, not a full sanitizer.
# It rejects obvious active content until a proper HTML parser is introduced.
HTML_UNSAFE_RE = re.compile(
    r"<\s*(script|iframe|object|embed|form|input|button|svg)[^>]*>|"
    r"<\s*/\s*script\s*>|"
    r"<\s*[^>]*\s(on[a-z]+)\s*=\s*['\"`]?|"
    r"(?:javascript|data|vbscript)\s*:",
    re.IGNORECASE,
)

# SKILL.md is plain Markdown.  We only reject obvious overrides / hidden
# instructions and require a top-level header.
HIDDEN_INSTRUCTION_RE = re.compile(
    r"(\n|\A)\s*(ignore previous instructions|ignore all prior|system override|"
    r"you are now .*override|disregard .*instructions)\s*(\n|\Z)",
    re.IGNORECASE,
)


def sanitize_csv_text(content_text: str) -> str:
    """Return a CSV text where formula-injection cells are neutralized.

    We prefix dangerous cells with a single quote, which spreadsheet
    applications interpret as forcing text mode.
    """

    reader = csv.reader(io.StringIO(content_text))
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    for row in reader:
        safe_row: list[str] = []
        for cell in row:
            stripped = cell.strip()
            if stripped.startswith(CSV_FORMULA_PREFIXES):
                safe_row.append("'" + cell)
            else:
                safe_row.append(cell)
        writer.writerow(safe_row)

    return output.getvalue()


def validate_csv_no_formulas(content_text: str) -> list[str]:
    """Return a list of errors if the CSV contains formula-injection cells."""

    errors: list[str] = []
    reader = csv.reader(io.StringIO(content_text))
    for row_index, row in enumerate(reader, start=1):
        for col_index, cell in enumerate(row, start=1):
            if cell.strip().startswith(CSV_FORMULA_PREFIXES):
                errors.append(
                    f"CSV formula-injection at row {row_index} col {col_index}: "
                    f"cell starts with '{cell.strip()[0]}'"
                )
    return errors


def validate_html_basic(content_text: str) -> list[str]:
    """Basic HTML safety check.  Rejects scripts, event handlers and risky URLs."""

    errors: list[str] = []
    for match in HTML_UNSAFE_RE.finditer(content_text):
        snippet = match.group(0)[:80]
        errors.append(f"Unsafe HTML detected: {snippet!r}")
    return errors


def validate_skill_md(content_text: str) -> list[str]:
    """Lightweight SKILL.md linter.

    Rejects hidden instruction overrides and requires a top-level heading.
    """

    errors: list[str] = []
    if not re.search(r"^#\s+", content_text, re.MULTILINE):
        errors.append("SKILL.md must start with a top-level (#) heading.")
    if HIDDEN_INSTRUCTION_RE.search(content_text):
        errors.append("SKILL.md contains possible hidden instruction override.")
    return errors


def assert_safe_kb_source(source_type: str, content_text: str) -> None:
    """Raise ValueError if a KB source contains known injection vectors.

    For SL1b we support md/txt/csv.  Excel/HTML/PDF are rejected until SL2
    sandboxed parsers exist.
    """

    if source_type in {"md", "txt"}:
        # Markdown/text can contain HTML.  Reject obvious script/event handlers.
        errors = validate_html_basic(content_text)
        if errors:
            raise ValueError("Unsafe KB source content: " + "; ".join(errors))
        return

    if source_type == "csv":
        errors = validate_csv_no_formulas(content_text)
        if errors:
            raise ValueError("Unsafe CSV content: " + "; ".join(errors))
        return

    if source_type in {"xlsx", "xls", "html", "pdf"}:
        raise ValueError(
            f"KB source type '{source_type}' is not supported in SL1b. "
            "Sandboxed parser required (SL2)."
        )

    # Unknown type: let the caller decide.
