---
name: cv-intake
description: Interview a candidate to create or improve an accurate, structured Markdown CV. Use when a user needs help gathering employment history, education, skills, or choosing a CV design before export.
---

# CV Intake

Create a factual, editable `cv.md` that can be rendered by `cv-markdown-export`.

## Interaction

Use the host agent's native choice, form, or question interface when it is available. If it is not available, use a short numbered text menu. Do not call or imitate an interface that the host agent does not provide.

Collect information in small groups. Confirm uncertain dates, employer names, locations, job titles, and claims before adding them. When an exact date is unavailable, use an honest approximate form such as `2019 — approximately 3 years`; never invent a month or achievement.

Before writing or changing a CV, confirm the candidate name and every available personal field. If a source has no name or contains a sample name such as `John Doe`, ask for a name instead of proceeding. If the source contains a name, show it for confirmation; do not assume it belongs to the current user.

Ask whether the candidate wants a photo before requesting one. Explain that the Harvard and ATS themes do not render photos.

Read [the interaction guide](references/interaction-guide.md) before beginning an intake. Read [the confirmation protocol](references/confirmation-protocol.md) before presenting collected data. Read [the output schema](references/output-schema.md) before writing `cv.md`.

## Design selection

Present these choices after enough information has been gathered:

1. **Harvard Chronological** — conservative, single-column, chronology-first; recommended for academic, corporate, and formal applications.
2. **ATS Standard** — minimal and machine-readable; recommended for online job portals and international applications.
3. **Modern Professional** — refined visual hierarchy with an optional photo; recommended for customer service, sales, hospitality, and general professional roles.

Then offer accent choices. Default to **Bold Black** when the user does not choose one:

1. Bold Black (default)
2. Navy Blue
3. Charcoal Gray
4. Burgundy
5. Teal
6. Custom Color — enter `#RRGGBB`, `#RGB`, `rgb(r, g, b)`, or `hsl(h, s%, l%)`

Ask for the delivery format with a native selection control when available, or with this menu:

1. **DOCX** — editable in Microsoft Word and compatible office software.
2. **PDF** — fixed layout for sending or printing.
3. **DOCX + PDF** — recommended when the user needs both an editable copy and a ready-to-send copy.

Record the selection as `format: docx`, `format: pdf`, or `format: both` in `cv.config.yml`. Use `both` only when the user selects it or asks for both formats.

## Output

Create or update only the agreed CV project files:

- `cv.md`
- `cv.config.yml` when a theme, accent, photo setting, or output format is selected
- `assets/photos/` only when the user supplies a photo

Use [assets/cv.md.example](assets/cv.md.example) as the starter when the project does not yet have `cv.md`. The sample name and all sample data must be replaced and explicitly confirmed.

Keep the source in Markdown. Do not produce a final DOCX or PDF unless the user asks to export it; then hand off to `cv-markdown-export`.
