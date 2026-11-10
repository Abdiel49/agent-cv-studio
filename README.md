# Agent CV Studio

Portable Agent Skills for gathering CV information and exporting a Markdown CV as a polished DOCX, PDF, or both.

**Project repository:** [https://github.com/Abdiel49/agent-cv-studio](https://github.com/Abdiel49/agent-cv-studio)

## Install

Install the repository with the open Skills CLI:

```bash
npx skills add https://github.com/Abdiel49/agent-cv-studio.git
```

Install a single skill when needed:

```bash
npx skills add https://github.com/Abdiel49/agent-cv-studio.git --skill cv-intake
npx skills add https://github.com/Abdiel49/agent-cv-studio.git --skill cv-markdown-export
```

The CLI prompts for supported target agents. It can install the same skills for Codex, Claude Code, OpenCode, and other compatible agents.

## Skills

- **cv-intake** — Interview a candidate and create or improve an accurate `cv.md` file.
- **cv-markdown-export** — Check the local toolchain, validate the project, and render `cv.md` to formal DOCX, PDF, or both.

## Quick start

Create a project folder:

```text
my-cv/
├── cv.md
├── cv.config.yml
├── assets/
│   ├── photos/
│   └── others/
└── output/
```

Copy the included examples before editing:

```bash
cp skills/cv-intake/assets/cv.md.example my-cv/cv.md
cp skills/cv-markdown-export/assets/cv.config.example.yml my-cv/cv.config.yml
```

Replace the sample values before exporting. An agent using `cv-intake` confirms the candidate's name and available personal data interactively before it writes or updates the CV.

### `cv.config.yml` example

This optional file controls the presentation and output without changing the CV content:

```yaml
# Replace John Doe and every selected value before exporting.
theme: modern-professional      # harvard-chronological | ats-standard | modern-professional
accent: "#1A5A96"               # Named color, #RRGGBB, #RGB, rgb(...), or hsl(...)
format: both                    # docx | pdf | both
output_name: John_Doe_CV        # File name without an extension
output_dir: output              # Must stay inside this CV project
include_photo: false            # true only for modern-professional
# photo: assets/photos/john-doe.jpg
```

The agent can ask for these choices interactively. `bold-black`, `ats-standard`, and `output` are the defaults when a value is not supplied. The accent color is used for the candidate name, section headings, role headings, and Markdown bold text; regular body text stays black for readability.

Use the export wrapper for one CV. It runs diagnostics before export and again whenever validation or rendering fails:

```bash
python skills/cv-markdown-export/scripts/export_cv.py --project my-cv --format both
```

## Requirements

- Python 3.10 or later for the bundled scripts.
- Pandoc for Markdown-to-DOCX rendering.
- LibreOffice for DOCX-to-PDF conversion when PDF output is requested.

The scripts do not install software, upload CV data, or access the network. Run `cv_doctor.py` to see the local status and suggested next steps.

## Built-in designs

| Theme | Best for | Photo support |
| --- | --- | --- |
| `harvard-chronological` | Formal, academic, corporate, and chronology-first applications | No |
| `ats-standard` | Job boards and applicant-tracking systems | No |
| `modern-professional` | Customer service, sales, hospitality, and general professional roles | Optional |

The default accent is `bold-black`, which uses strong type hierarchy rather than color.

## Output selection and batch export

An agent using the skill asks the user to choose **DOCX**, **PDF**, or **DOCX + PDF** when no output format was supplied. Generated files are placed in each project's `output/` folder by default.

For several independent CV projects, use local parallel workers:

```bash
python skills/cv-markdown-export/scripts/batch_export.py \
  --projects ./candidates/john-doe ./candidates/jane-doe \
  --format both \
  --workers 2
```

Agents that support subagents may instead delegate one isolated project to each worker after the user explicitly requests parallel processing. Every worker must write only to its own project `output/` folder.

## Custom themes and document import

Inspect a supplied DOCX or text-based PDF before using it as a reference:

```bash
python skills/cv-markdown-export/scripts/inspect_source.py path/to/source.docx
```

Create a custom theme from a local source only when you have permission to use it:

```bash
python skills/cv-markdown-export/scripts/create_theme.py \
  --from-template path/to/template.docx \
  --name my-custom-theme \
  --destination my-cv/themes \
  --license-ack
```

DOCX sources can become Word reference documents. PDF sources are visual references: the tool records their metadata and creates a theme scaffold, but it does not claim to reproduce an editable PDF layout exactly.

## Privacy and responsible use

CVs can contain personal data. Keep source files, photos, and generated output in a private workspace. Do not import or redistribute a third-party template unless its license or the owner permits it.

## License

MIT. See [LICENSE](LICENSE).
