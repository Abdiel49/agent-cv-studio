---
name: cv-markdown-export
description: Render a Markdown CV into a formal DOCX, PDF, or both with selectable professional themes, real Word styles, and local validation. Use for CV formatting and export, not generic document conversion.
---

# CV Markdown Export

Render a CV project from `cv.md` to a polished DOCX, PDF, or both. Preserve the source facts and Markdown semantics; do not rewrite the candidate's history unless the user asks.

## Required workflow

1. Identify the CV project directory and requested output: `docx`, `pdf`, or `both`. If the user did not specify one, ask with the host agent's native selection control; otherwise use this numbered menu: `1. DOCX  2. PDF  3. DOCX + PDF`.
2. Read the first level-one heading as the candidate name. If it is missing or is a sample value such as `John Doe`, ask the user to enter and confirm the name before export. Also show available contact and target-role fields for confirmation. Use the host's native checklist when possible; otherwise accept `Field: value` corrections separated by semicolons. Read `cv-intake/references/confirmation-protocol.md` when `cv-intake` is installed.
3. Run `scripts/export_cv.py --project <project> --format <format>` for a normal export. It runs the required preflight, source validation, renderer, artifact validation, and diagnostics.
4. Confirm the selected theme and accent. Read the matching `templates/<theme>/theme.yml` when the user selects a theme.
5. The export wrapper writes the requested artifact to `<project>/output/` by default. A relative `output_dir` inside the project may be set in `cv.config.yml`.
6. If any validation or render step fails, `export_cv.py` runs `cv_doctor.py` again and prints the local environment status. Do not repeatedly retry an unchanged failure.

Never deliver a DOCX containing visible Markdown markers or a PDF generated from an unformatted plain-text fallback. If rendering prerequisites are unavailable, report the diagnostic result and stop.

## Multiple CV projects

When the user explicitly requests parallel work and the host agent supports subagents, assign one independent CV project to each worker. Each worker must receive one project directory, run `export_cv.py`, and write only to that project's own `output/` directory. The parent agent collects results and reports failures; workers must not edit another project's files.

Do not assume that every host exposes a subagent API. When subagents are unavailable, use `scripts/batch_export.py` for local parallel execution. It starts isolated worker processes and uses a separate LibreOffice profile for each PDF conversion.

Read [the batch export guide](references/batch-export.md) when exporting more than one CV.

## Design selection

If no theme is specified, use `ats-standard`. If no accent is specified, use `bold-black`.

- `harvard-chronological`: formal, single-column, chronology-first; no photo.
- `ats-standard`: minimal and machine-readable; no photo.
- `modern-professional`: refined, general professional layout; optional photo.

Use the host agent's native selection controls when available. Otherwise show a numbered menu with each name, description, and recommended use. Do not use a profile photo unless the selected theme supports it and the user explicitly enabled it.

## Input contract

Read [the input contract](references/input-contract.md) for the project layout and configuration keys. Read [the rendering guide](references/rendering-guide.md) for design behavior.

## Import and custom themes

For a supplied DOCX or PDF, first run `scripts/inspect_source.py`. The result is a confidence-based assessment, not a guarantee that the source is a CV.

Use `scripts/create_theme.py` only with a local source whose license or owner permits reuse. A DOCX can be used as a Word reference document. A PDF is a visual reference and cannot be treated as an editable Word template. Read [the custom theme guide](references/custom-template-guide.md) before creating a custom theme.
