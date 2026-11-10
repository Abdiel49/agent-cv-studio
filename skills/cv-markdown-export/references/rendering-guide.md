# Rendering Guide

The renderer treats Markdown semantically:

| Markdown | Rendered result |
| --- | --- |
| `# Candidate Name` | 22 pt bold title |
| `## Section` | 14 pt bold section heading |
| `### Role — Employer` | 11 pt bold role heading |
| `**text**` | Real bold text in DOCX and PDF |
| `- item` | Indented bullet list |

All themes use A4 pages, restrained spacing, and readable professional typography. The renderer applies page margins, heading spacing, font size, bold text, and accent color after Pandoc creates the DOCX. PDF output is exported from that styled DOCX, keeping both formats aligned.

`bold-black` is the default accent and uses black text hierarchy rather than decorative color. A selected accent is applied consistently to the candidate name, section headings, role/employer headings, and Markdown bold text. Body paragraphs remain black for readability.

Use a named accent or a custom color in any of these forms:

```yaml
accent: navy-blue
accent: "#1A5A96"
accent: "#159957"
accent: "rgb(26, 90, 150)"
accent: "hsl(210, 70%, 35%)"
```

The renderer converts every accepted color to Word's `RRGGBB` format. Do not use transparency, gradients, or color values with alpha channels.
