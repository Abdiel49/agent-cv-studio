#!/usr/bin/env python3
"""Render a Markdown CV project as a styled DOCX, PDF, or both."""

from __future__ import annotations

import argparse
import colorsys
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + NS + "}"
ACCENTS = {
    "bold-black": "000000",
    "navy-blue": "17365D",
    "charcoal-gray": "3F3F3F",
    "burgundy": "7A1F32",
    "teal": "006D77",
}
THEMES = {"harvard-chronological", "ats-standard", "modern-professional"}


def parse_simple_yaml(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("\"'")
    return result


def bool_value(value: str | None) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def accent_to_hex(value: str) -> str:
    """Convert a named, hexadecimal, RGB, or HSL accent into OOXML RRGGBB."""
    raw = value.strip()
    named = ACCENTS.get(raw.casefold())
    if named:
        return named
    hex_match = re.fullmatch(r"#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", raw)
    if hex_match:
        code = hex_match.group(1)
        if len(code) == 3:
            code = "".join(char * 2 for char in code)
        return code.upper()
    rgb_match = re.fullmatch(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", raw, re.IGNORECASE)
    if rgb_match:
        channels = [int(channel) for channel in rgb_match.groups()]
        if any(channel > 255 for channel in channels):
            raise ValueError("RGB channels must be between 0 and 255.")
        return "".join(f"{channel:02X}" for channel in channels)
    hsl_match = re.fullmatch(r"hsl\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%\s*\)", raw, re.IGNORECASE)
    if hsl_match:
        hue, saturation, lightness = (float(part) for part in hsl_match.groups())
        if not 0 <= saturation <= 100 or not 0 <= lightness <= 100:
            raise ValueError("HSL saturation and lightness must be between 0% and 100%.")
        red, green, blue = colorsys.hls_to_rgb((hue % 360) / 360, lightness / 100, saturation / 100)
        return "".join(f"{round(channel * 255):02X}" for channel in (red, green, blue))
    raise ValueError("Accent must be a named color, #RRGGBB, #RGB, rgb(r, g, b), or hsl(h, s%, l%).")


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "Unknown command error"
        raise RuntimeError(detail)


def resolve_theme(project: Path, built_in_templates: Path, theme: str) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", theme):
        raise RuntimeError("Theme names may contain lowercase letters, numbers, and hyphens only.")
    custom = project / "themes" / theme
    built_in = built_in_templates / theme
    if custom.is_dir():
        return custom
    if built_in.is_dir():
        return built_in
    raise RuntimeError(f"Theme was not found: {theme}")


def theme_supports_photo(theme_dir: Path) -> bool:
    config = parse_simple_yaml(theme_dir / "theme.yml")
    return bool_value(config.get("supports_photo"))


def choose_photo(project: Path, config: dict[str, str], enabled: bool) -> Path | None:
    if not enabled:
        return None
    configured = config.get("photo")
    if configured:
        candidate = (project / configured).resolve()
        if candidate.is_file():
            return candidate
        raise RuntimeError(f"Configured photo does not exist: {candidate}")
    photo_dir = project / "assets" / "photos"
    choices = [p for p in photo_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    if len(choices) == 1:
        return choices[0]
    if len(choices) > 1:
        raise RuntimeError("More than one profile photo found. Set the 'photo' value in cv.config.yml.")
    return None


def prepare_markdown(project: Path, source: Path, photo: Path | None) -> Path:
    text = source.read_text(encoding="utf-8")
    if photo:
        relative = photo.relative_to(project).as_posix()
        image = f"![Profile photo]({relative}){{ width=1.15in }}"
        if "<!-- CV_PHOTO -->" in text:
            text = text.replace("<!-- CV_PHOTO -->", image, 1)
        else:
            lines = text.splitlines()
            for index, line in enumerate(lines):
                if line.startswith("# "):
                    lines[index + 1:index + 1] = ["", image]
                    break
            text = "\n".join(lines)
    handle = tempfile.NamedTemporaryFile("w", suffix=".md", prefix=".cv-render-", dir=project, encoding="utf-8", delete=False)
    with handle:
        handle.write(text)
    return Path(handle.name)


def ensure(parent: ET.Element, tag: str) -> ET.Element:
    item = parent.find(W + tag)
    if item is None:
        item = ET.SubElement(parent, W + tag)
    return item


def replace_property(parent: ET.Element, tag: str, **attributes: str) -> None:
    for item in list(parent.findall(W + tag)):
        parent.remove(item)
    ET.SubElement(parent, W + tag, {W + key: value for key, value in attributes.items()})


def style_document(docx_path: Path, theme: str, color: str) -> None:
    layout = {
        "harvard-chronological": {"font": "Aptos", "margin": "1150", "title": "44", "heading": "28"},
        "ats-standard": {"font": "Aptos", "margin": "1000", "title": "42", "heading": "27"},
        "modern-professional": {"font": "Aptos", "margin": "900", "title": "46", "heading": "29"},
    }.get(theme, {"font": "Aptos", "margin": "1000", "title": "42", "heading": "27"})

    with zipfile.ZipFile(docx_path, "r") as source:
        contents = {name: source.read(name) for name in source.namelist()}

    styles_name = "word/styles.xml"
    if styles_name in contents:
        root = ET.fromstring(contents[styles_name])
        settings = {
            "Title": (layout["title"], True, color, "0", "180"),
            "Heading1": (layout["heading"], True, color, "260", "120"),
            "Heading2": ("24", True, color, "220", "90"),
            "Heading3": ("22", True, color, "160", "60"),
            "Normal": ("21", False, "000000", "0", "80"),
            "Strong": ("21", True, color, "0", "0"),
        }
        for style in root.findall(W + "style"):
            style_id = style.get(W + "styleId")
            if style_id not in settings:
                continue
            size, bold, font_color, before, after = settings[style_id]
            rpr = ensure(style, "rPr")
            replace_property(rpr, "rFonts", ascii=layout["font"], hAnsi=layout["font"], eastAsia=layout["font"])
            replace_property(rpr, "sz", val=size)
            replace_property(rpr, "szCs", val=size)
            replace_property(rpr, "color", val=font_color)
            for element in list(rpr.findall(W + "b")):
                rpr.remove(element)
            if bold:
                ET.SubElement(rpr, W + "b")
            ppr = ensure(style, "pPr")
            replace_property(ppr, "spacing", before=before, after=after, line="240", lineRule="auto")
            if style_id in {"Title", "Heading1", "Heading2", "Heading3"}:
                ensure(ppr, "keepNext")
        contents[styles_name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    document_name = "word/document.xml"
    if document_name in contents:
        root = ET.fromstring(contents[document_name])
        first_heading = True
        for paragraph in root.findall(".//" + W + "p"):
            ppr = paragraph.find(W + "pPr")
            style = ppr.find(W + "pStyle") if ppr is not None else None
            if first_heading and style is not None and style.get(W + "val") == "Heading1":
                style.set(W + "val", "Title")
                first_heading = False
        for section in root.findall(".//" + W + "sectPr"):
            margins = section.find(W + "pgMar")
            if margins is None:
                margins = ET.SubElement(section, W + "pgMar")
            margins.set(W + "top", layout["margin"])
            margins.set(W + "bottom", layout["margin"])
            margins.set(W + "left", layout["margin"])
            margins.set(W + "right", layout["margin"])
        contents[document_name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False, dir=docx_path.parent) as temporary:
        temp_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as target:
            for name, payload in contents.items():
                target.writestr(name, payload)
        temp_path.replace(docx_path)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--format", choices=("docx", "pdf", "both"), default=None)
    parser.add_argument("--theme", default=None)
    parser.add_argument("--accent", default=None, help="Named color, #RRGGBB, #RGB, rgb(r, g, b), or hsl(h, s%, l%).")
    parser.add_argument("--include-photo", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    source = project / "cv.md"
    if not source.is_file():
        raise SystemExit(f"cv.md was not found in {project}")
    config = parse_simple_yaml(project / "cv.config.yml")
    output_format = args.format or config.get("format", "both")
    theme = args.theme or config.get("theme", "ats-standard")
    accent = args.accent or config.get("accent", "bold-black")
    if output_format not in {"docx", "pdf", "both"}:
        raise SystemExit("Format must be docx, pdf, or both.")
    try:
        accent_hex = accent_to_hex(accent)
    except ValueError as error:
        raise SystemExit(f"Invalid accent: {error}") from error

    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("Pandoc is required. Run cv_doctor.py for environment diagnostics.")
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    try:
        theme_dir = resolve_theme(project, template_dir, theme)
    except RuntimeError as error:
        raise SystemExit(str(error)) from error
    wants_photo = args.include_photo or bool_value(config.get("include_photo"))
    if wants_photo and not theme_supports_photo(theme_dir):
        raise SystemExit(f"The {theme} theme does not support profile photos.")
    photo = choose_photo(project, config, wants_photo)

    output_setting = Path(config.get("output_dir", "output"))
    output_dir = (project / output_setting).resolve() if not output_setting.is_absolute() else output_setting.resolve()
    try:
        output_dir.relative_to(project)
    except ValueError as error:
        raise SystemExit("output_dir must be inside the CV project directory.") from error
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = re.sub(r"[^A-Za-z0-9._-]+", "_", config.get("output_name", "CV")).strip("._") or "CV"
    markdown = prepare_markdown(project, source, photo)
    temporary_dir = None
    try:
        if output_format == "pdf":
            temporary_dir = tempfile.TemporaryDirectory(prefix="cv-docx-")
            docx_path = Path(temporary_dir.name) / f"{output_name}.docx"
        else:
            docx_path = output_dir / f"{output_name}.docx"
        reference = theme_dir / "reference.docx"
        command = [pandoc, str(markdown), "--from=gfm+attributes", "--to=docx", "--output", str(docx_path)]
        if reference.is_file():
            command.append(f"--reference-doc={reference}")
        run(command)
        style_document(docx_path, theme, accent_hex)
        created = []
        if output_format in {"docx", "both"}:
            created.append(docx_path)
        if output_format in {"pdf", "both"}:
            office = shutil.which("libreoffice") or shutil.which("soffice")
            if not office:
                raise RuntimeError("LibreOffice is required for PDF output. Run cv_doctor.py for diagnostics.")
            with tempfile.TemporaryDirectory(prefix="cv-libreoffice-profile-") as office_profile:
                profile_url = Path(office_profile).resolve().as_uri()
                run([
                    office,
                    "--headless",
                    f"-env:UserInstallation={profile_url}",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(output_dir),
                    str(docx_path),
                ])
            pdf_path = output_dir / f"{output_name}.pdf"
            if not pdf_path.is_file():
                raise RuntimeError("LibreOffice did not create the requested PDF.")
            created.append(pdf_path)
        for artifact in created:
            print(f"Created: {artifact}")
    except RuntimeError as error:
        raise SystemExit(f"Rendering failed: {error}") from error
    finally:
        markdown.unlink(missing_ok=True)
        if temporary_dir:
            temporary_dir.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
