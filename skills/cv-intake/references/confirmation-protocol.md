# Confirmation Protocol

Before creating, changing, or exporting a CV, inspect the source for the candidate name and available personal details.

If the name is absent, blank, or a sample value such as `John Doe`, ask for the candidate's name. If a name is present, show it and ask the candidate to confirm or correct it. Do not assume that the account owner and the candidate are the same person.

Use the host agent's native checklist, form, or selector when available. Present all collected fields with their current values and allow the user to confirm all or select individual fields to edit.

When no native checklist is available, use this fallback:

```text
Please review the candidate details:
[ ] Name: John Doe
[ ] Profession: Customer Service Representative
[ ] Location: City, Country
[ ] Phone: +00 000 000 000
[ ] Email: john.doe@example.com

Reply "Confirm all", identify the fields to change, or send corrections in this format:
Name: Jane Doe; Profession: Sales Associate; Location: City, Country
```

Accept corrections as `Field: value` pairs separated by semicolons. Commas may also separate pairs only when each following field has a colon. Preserve commas that belong inside a value. Normalize common aliases before writing: `Name` or `Nombre` becomes `Name`; `Profession`, `Role`, or `Profesión` becomes `Target Profession`.

Require explicit confirmation of `Name` before export. For other available fields, preserve a missing value rather than inventing one. Ask a focused follow-up only when a missing field prevents the requested CV content.

`Location` is optional and independent. Ask for it directly when needed; never infer it from prior CVs, employment locations, the current workspace, account data, or another candidate's information.
