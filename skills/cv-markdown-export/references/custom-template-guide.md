# Custom Theme Guide

Run `inspect_source.py` before creating a theme from a supplied file. Review the report and obtain permission to reuse the source design.

For a DOCX source, `create_theme.py` copies the file as `reference.docx`. Pandoc uses it to inherit compatible Word styles. The custom DOCX should use recognizable Title, Heading, Normal, and list styles for best results.

For a PDF source, `create_theme.py` stores the PDF as a visual reference and creates `theme.yml`. PDFs are not editable templates; manual refinement of the generated theme is expected.

The generated `theme.yml` includes the source type, photo support setting, and supported accents. Set `supports_photo: true` only when the design intentionally reserves an appropriate place for a profile photo.
