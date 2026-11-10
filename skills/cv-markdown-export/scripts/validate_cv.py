#!/usr/bin/env python3
"""Validate a Markdown CV project or a generated DOCX/PDF artifact."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SECTION_TERMS = {
    "experience": ("experience", "employment", "work history", "experiencia"),
    "education": ("education", "academic", "educacion", "educación", "formacion", "formación"),
    "skills": ("skills", "competencies", "habilidades", "competencias"),
}


def print_result(state: str, message: str) -> bool:
    print(f"[{state}] {message}")
    return state != "FAIL"


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
    return "\n".join(node.text or "" for node in document.iter(W + "t"))


def extract_pdf_text(path: Path) -> str:
    converter = shutil.which("pdftotext")
    if not converter:
        return ""
    completed = subprocess.run([converter, str(path), "-"], text=True, capture_output=True)
    return completed.stdout if completed.returncode == 0 else ""


def validate_markdown(project: Path) -> bool:
    source = project / "cv.md"
    if not source.is_file():
        return print_result("FAIL", f"Missing required file: {source}")
    text = source.read_text(encoding="utf-8")
    ok = True
    name_match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if not name_match:
        ok &= print_result("FAIL", "Candidate name heading (# ...) found")
    else:
        candidate_name = name_match.group(1).strip()
        placeholders = {"john doe", "jane doe", "candidate name", "full name", "your name", "nombre completo"}
        if candidate_name.casefold() in placeholders or candidate_name.startswith("["):
            ok &= print_result("FAIL", "Candidate name is a sample or placeholder; ask the user to confirm a real name before export")
        else:
            ok &= print_result("OK", "Candidate name heading (# ...) found")
    headings = [line[2:].strip().lower() for line in text.splitlines() if line.startswith("## ")]
    for label, terms in SECTION_TERMS.items():
        found = any(any(term in heading for term in terms) for heading in headings)
        print_result("OK" if found else "WARN", f"{label.title()} section {'found' if found else 'not found'}")
    if "<!-- CV_PHOTO -->" in text:
        print_result("OK", "Optional CV photo marker found")
    return ok


def validate_artifact(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return print_result("FAIL", f"Artifact is missing or empty: {path}")
    suffix = path.suffix.lower()
    if suffix == ".docx":
        try:
            with zipfile.ZipFile(path) as archive:
                valid = "word/document.xml" in archive.namelist()
            text = extract_docx_text(path)
        except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as error:
            return print_result("FAIL", f"Invalid DOCX: {error}")
        ok = print_result("OK" if valid else "FAIL", "DOCX package contains word/document.xml")
        ok &= print_result("OK" if len(text.strip()) > 20 else "FAIL", "DOCX contains readable document text")
        raw_markdown = bool(re.search(r"(?m)^#\s+|\*\*[^*]+\*\*", text))
        ok &= print_result("FAIL" if raw_markdown else "OK", "No visible Markdown heading or bold markers detected")
        return ok
    if suffix == ".pdf":
        header = path.read_bytes()[:5]
        ok = print_result("OK" if header == b"%PDF-" else "FAIL", "PDF signature is valid")
        text = extract_pdf_text(path)
        if text:
            ok &= print_result("OK" if len(text.strip()) > 20 else "WARN", "PDF text extraction returned content")
        else:
            print_result("WARN", "PDF text was not inspected; install pdftotext for an additional check")
        return ok
    return print_result("FAIL", "Artifact must be a .docx or .pdf file")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    ok = validate_artifact(args.artifact.resolve()) if args.artifact else validate_markdown(args.project.resolve())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
