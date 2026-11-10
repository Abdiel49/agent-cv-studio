# Batch Export Guide

Each CV must be an independent project directory with its own `cv.md` and `output/` folder. Do not export multiple candidates into the same project directory.

Use one of these commands:

```bash
python scripts/batch_export.py --projects ./candidates/john-doe ./candidates/jane-doe --format both --workers 2
```

```bash
python scripts/batch_export.py --projects-file projects.txt --format pdf --workers 3
```

`projects.txt` contains one project directory per line. Blank lines and lines starting with `#` are ignored.

The batch runner invokes `export_cv.py` once per project. It limits concurrency to four workers by default and gives every LibreOffice conversion an isolated temporary profile, preventing profile-lock conflicts.

For an agent host with subagents, delegate one project per worker only after the user asks for parallel processing. Keep all projects isolated and have the parent agent summarize the final results.
