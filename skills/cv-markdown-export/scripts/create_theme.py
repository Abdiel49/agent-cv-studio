#!/usr/bin/env python3
"""Create a custom CV theme scaffold from a local DOCX or PDF reference."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


def valid_name(value: str) -> str:
    normalized = value.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        raise argparse.ArgumentTypeError("Theme name must use lowercase letters, numbers, and hyphens.")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-template", type=Path, required=True, dest="source")
    parser.add_argument("--name", type=valid_name, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--supports-photo", action="store_true")
    parser.add_argument("--license-ack", action="store_true", help="Confirm that you may use the supplied template.")
    args = parser.parse_args()

    source = args.source.resolve()
    if not args.license_ack:
        raise SystemExit("Refusing to create a theme without --license-ack confirming permission to use the source.")
    if not source.is_file() or source.suffix.lower() not in {".docx", ".pdf"}:
        raise SystemExit("The source must be an existing local .docx or .pdf file.")
    destination = args.destination.resolve() / args.name
    if destination.exists():
        raise SystemExit(f"Destination already exists: {destination}")
    destination.mkdir(parents=True)
    source_kind = "docx-reference" if source.suffix.lower() == ".docx" else "pdf-reference"
    target_name = "reference.docx" if source_kind == "docx-reference" else "reference.pdf"
    shutil.copy2(source, destination / target_name)
    theme = "\n".join([
        f"name: {args.name}",
        "description: Custom theme created from a user-supplied local reference.",
        "recommended_for: Review visually before use in a production application.",
        f"supports_photo: {'true' if args.supports_photo else 'false'}",
        "default_accent: bold-black",
        "layout: review-required",
        f"source_type: {source_kind}",
        "",
    ])
    (destination / "theme.yml").write_text(theme, encoding="utf-8")
    preview = "\n".join([
        "# Custom Theme Review",
        "",
        f"Source: `{source.name}`",
        "",
        "Review title, heading, body, and list styles before using this theme.",
        "A DOCX reference can be used by Pandoc. A PDF is visual reference material only.",
        "",
    ])
    (destination / "preview.md").write_text(preview, encoding="utf-8")
    print(f"Custom theme created: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
