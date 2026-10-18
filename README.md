# Learn with Anil – APPSC Group-II PYQs

Free practice portal for APPSC Group-II previous year questions (Screening 2019 & 2024, Mains 2019 & 2025), with answers from APPSC's official final keys, topic-wise quizzes, a mistakes notebook, smart quiz, bookmarks and a memory heatmap.

- `docs/` – the published website (served by GitHub Pages)
- `src/` – one text file per question paper
- `tools/build.py` – rebuilds the site: `SITE_URL=https://<domain> python3 tools/build.py`, then copy `dist/site` to `docs/`
- `tools/app.html` – the app template
- `src/static/` – files copied unchanged to the site root (e.g. Google Search Console verification)

To publish a change: `SITE_URL=https://anilkumarjupudi360360-crypto.github.io/learnwithanil python3 tools/build.py && rm -rf docs && cp -r dist/site docs`, then commit and push.
