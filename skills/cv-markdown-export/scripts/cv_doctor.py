#!/usr/bin/env python3
"""Check local prerequisites for rendering a Markdown CV without installing anything."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


def status(label: str, state: str, detail: str) -> bool:
    print(f"[{state}] {label}: {detail}")
    return state != "FAIL"


def executable(name: str) -> str | None:
    return shutil.which(name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--format", choices=("docx", "pdf", "both"), default="both")
    args = parser.parse_args()

    project = args.project.resolve()
    ok = True
    print("Agent CV Studio diagnostic")
    ok &= status("Python", "OK" if sys.version_info >= (3, 10) else "FAIL", sys.version.split()[0])
    ok &= status("Project directory", "OK" if project.is_dir() else "FAIL", str(project))
    cv_file = project / "cv.md"
    ok &= status("Markdown source", "OK" if cv_file.is_file() else "FAIL", str(cv_file))
    pandoc = executable("pandoc")
    ok &= status("Pandoc", "OK" if pandoc else "FAIL", pandoc or "Install Pandoc to create styled DOCX output.")

    if args.format in {"pdf", "both"}:
        office = executable("libreoffice") or executable("soffice")
        ok &= status("LibreOffice", "OK" if office else "FAIL", office or "Install LibreOffice to convert styled DOCX to PDF.")

    photos = project / "assets" / "photos"
    others = project / "assets" / "others"
    status("Photo assets folder", "OK" if photos.is_dir() else "WARN", str(photos))
    status("Other assets folder", "OK" if others.is_dir() else "WARN", str(others))

    if project.is_dir():
        try:
            with tempfile.NamedTemporaryFile(dir=project, prefix=".cv-write-check-", delete=True):
                pass
            status("Project write access", "OK", "Writable")
        except OSError as error:
            ok &= status("Project write access", "FAIL", str(error))
    else:
        ok &= status("Project write access", "FAIL", "Project directory does not exist.")

    font_tool = executable("fc-match")
    if font_tool:
        status("Font inspection", "OK", "fc-match is available; the renderer requests Aptos with system fallback.")
    else:
        status("Font inspection", "WARN", "No fc-match utility found; Word or LibreOffice will choose a compatible fallback.")

    print("\nResult: " + ("ready to render" if ok else "fix the FAIL items before rendering"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
