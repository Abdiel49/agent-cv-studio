#!/usr/bin/env python3
"""Export independent CV projects concurrently with isolated worker processes."""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def export_one(project: Path, output_format: str) -> tuple[Path, int, str]:
    command = [sys.executable, str(SCRIPT_DIR / "export_cv.py"), "--project", str(project), "--format", output_format]
    completed = subprocess.run(command, text=True, capture_output=True)
    transcript = (completed.stdout + completed.stderr).strip()
    return project, completed.returncode, transcript


def project_paths(args: argparse.Namespace) -> list[Path]:
    if args.projects_file:
        lines = args.projects_file.read_text(encoding="utf-8").splitlines()
        raw_paths = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    else:
        raw_paths = [str(item) for item in args.projects]
    paths = [Path(item).resolve() for item in raw_paths]
    missing = [str(item) for item in paths if not item.is_dir()]
    if missing:
        raise SystemExit("Project directories not found:\n" + "\n".join(missing))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--projects", type=Path, nargs="+", help="One or more independent CV project directories.")
    source.add_argument("--projects-file", type=Path, help="Text file with one CV project directory per line.")
    parser.add_argument("--format", choices=("docx", "pdf", "both"), default="both")
    parser.add_argument("--workers", type=int, help="Maximum concurrent exports; default is up to four.")
    args = parser.parse_args()
    projects = project_paths(args)
    if len(set(projects)) != len(projects):
        raise SystemExit("Each project directory must appear only once.")
    workers = args.workers or min(4, len(projects), os.cpu_count() or 1)
    if workers < 1:
        raise SystemExit("--workers must be at least 1.")

    print(f"Exporting {len(projects)} project(s) with {workers} worker(s).")
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(export_one, project, args.format) for project in projects]
        for future in concurrent.futures.as_completed(futures):
            project, code, transcript = future.result()
            label = "OK" if code == 0 else "FAIL"
            print(f"\n[{label}] {project}")
            if transcript:
                print(transcript)
            failures += int(code != 0)
    print(f"\nBatch finished: {len(projects) - failures} succeeded, {failures} failed.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
