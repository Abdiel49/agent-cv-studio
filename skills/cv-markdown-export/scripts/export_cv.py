#!/usr/bin/env python3
"""Export one CV with preflight checks and automatic diagnostics after a failure."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def simple_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip("\"'")
    return values


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result


def doctor(project: Path, output_format: str) -> int:
    print("\nRunning CV environment diagnostic...")
    return run([sys.executable, str(SCRIPT_DIR / "cv_doctor.py"), "--project", str(project), "--format", output_format]).returncode


def fail(project: Path, output_format: str, message: str) -> int:
    print(f"\nExport stopped: {message}", file=sys.stderr)
    doctor(project, output_format)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--format", choices=("docx", "pdf", "both"), default="both")
    parser.add_argument("--theme")
    parser.add_argument("--accent")
    parser.add_argument("--include-photo", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()

    if doctor(project, args.format):
        return 1
    source_check = run([sys.executable, str(SCRIPT_DIR / "validate_cv.py"), "--project", str(project)])
    if source_check.returncode:
        return fail(project, args.format, "The Markdown CV did not pass validation.")

    command = [sys.executable, str(SCRIPT_DIR / "render_cv.py"), "--project", str(project), "--format", args.format]
    if args.theme:
        command.extend(["--theme", args.theme])
    if args.accent:
        command.extend(["--accent", args.accent])
    if args.include_photo:
        command.append("--include-photo")
    render = run(command)
    if render.returncode:
        return fail(project, args.format, "The renderer returned an error.")

    config = simple_config(project / "cv.config.yml")
    output_name = re.sub(r"[^A-Za-z0-9._-]+", "_", config.get("output_name", "CV")).strip("._") or "CV"
    output_dir = project / config.get("output_dir", "output")
    suffixes = [".docx"] if args.format == "docx" else [".pdf"] if args.format == "pdf" else [".docx", ".pdf"]
    for suffix in suffixes:
        artifact = output_dir / f"{output_name}{suffix}"
        validation = run([sys.executable, str(SCRIPT_DIR / "validate_cv.py"), "--artifact", str(artifact)])
        if validation.returncode:
            return fail(project, args.format, f"Generated artifact did not pass validation: {artifact.name}")
    print("\nExport completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
