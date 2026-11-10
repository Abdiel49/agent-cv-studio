#!/usr/bin/env python3
"""Inspect a DOCX or text-based PDF and report whether it likely resembles a CV."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SIGNALS = {
    "contact": ("email", "phone", "tel", "linkedin", "@", "+"),
    "experience": ("experience", "employment", "work history", "experiencia", "experiência"),
    "education": ("education", "academic", "degree", "educacion", "educación", "formacion", "formación", "formação"),
    "skills": ("skills", "competencies", "habilidades", "competências"),
}


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return "\n".join(node.text or "" for node in root.iter(W + "t"))


def pdf_text(path: Path) -> tuple[str, str]:
    utility = shutil.which("pdftotext")
    if not utility:
        return "", "pdftotext is not installed; only file metadata was inspected."
    completed = subprocess.run([utility, str(path), "-"], text=True, capture_output=True)
    if completed.returncode:
        return "", completed.stderr.strip() or "Text extraction failed."
    return completed.stdout, "Text extracted with pdftotext."


def assess(text: str) -> dict[str, object]:
    lower = text.lower()
    found = [name for name, terms in SIGNALS.items() if any(term in lower for term in terms)]
    date_count = len(re.findall(r"\b(?:19|20)\d{2}\b", text))
    score = len(found) + (1 if date_count >= 2 else 0) + (1 if len(text.split()) >= 100 else 0)
    confidence = "high" if score >= 4 else "medium" if score >= 2 else "low"
    return {"likely_cv": score >= 2, "confidence": confidence, "signals": found, "year_count": date_count, "word_count": len(text.split())}


def write_report(path: Path, source: Path, result: dict[str, object], note: str) -> None:
    lines = [
        "# Source Inspection Report",
        "",
        f"- Source: `{source}`",
        f"- Likely CV: `{result['likely_cv']}`",
        f"- Confidence: `{result['confidence']}`",
        f"- Signals: {', '.join(result['signals']) or 'none'}",
        f"- Detected years: {result['year_count']}",
        f"- Note: {note}",
        "",
        "Review the source manually before exporting or deriving a custom theme.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--to-markdown", type=Path, help="Convert a DOCX source to Markdown with Pandoc.")
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.is_file() or source.suffix.lower() not in {".docx", ".pdf"}:
        raise SystemExit("Source must be an existing .docx or .pdf file.")
    try:
        if source.suffix.lower() == ".docx":
            text, note = docx_text(source), "Text extracted from DOCX."
        else:
            text, note = pdf_text(source)
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as error:
        raise SystemExit(f"Unable to inspect source: {error}") from error
    result = assess(text)
    result["source"] = str(source)
    result["note"] = note
    print(json.dumps(result, indent=2))
    if args.report:
        write_report(args.report.resolve(), source, result, note)
        print(f"Report written: {args.report.resolve()}")
    if args.to_markdown:
        if source.suffix.lower() != ".docx":
            raise SystemExit("Only DOCX sources can be converted to Markdown automatically.")
        pandoc = shutil.which("pandoc")
        if not pandoc:
            raise SystemExit("Pandoc is required for DOCX-to-Markdown conversion.")
        converted = subprocess.run([pandoc, str(source), "--to=gfm", "--output", str(args.to_markdown.resolve())], text=True, capture_output=True)
        if converted.returncode:
            raise SystemExit(converted.stderr.strip() or "Pandoc conversion failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
