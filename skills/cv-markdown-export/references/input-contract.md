# Input Contract

The project directory must contain `cv.md` and may contain this optional configuration file:

```text
my-cv/
├── cv.md
├── cv.config.yml
├── assets/
│   ├── photos/
│   └── others/
└── output/
```

`cv.config.yml` uses a simple `key: value` format. Supported keys:

```yaml
theme: ats-standard
accent: bold-black
format: both
output_name: John_Doe_CV
output_dir: output
include_photo: false
photo: assets/photos/profile.jpg
```

Valid themes are `harvard-chronological`, `ats-standard`, and `modern-professional`. Accents can be `bold-black`, `navy-blue`, `charcoal-gray`, `burgundy`, or `teal`, or a custom color such as `"#1A5A96"`, `"rgb(26, 90, 150)"`, or `"hsl(210, 70%, 35%)"`.

The `assets/photos/` folder is only for optional profile photos. Use JPG, PNG, or WEBP. The `assets/others/` folder is for optional certificates, logos, or supporting files; it is not embedded unless a future template explicitly supports it.

`output_dir` defaults to `output` and must remain inside the CV project directory. The exporter creates it when needed.

Place `<!-- CV_PHOTO -->` below the candidate name in `cv.md` to control photo placement. If a photo-enabled theme is selected and no marker exists, the renderer places the image after the first level-one heading.

Copy `assets/cv.config.example.yml` to `cv.config.yml` to start from an editable configuration. Replace the sample name and confirm the candidate data before export.
