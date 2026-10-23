# Learn with Anil – APPSC Group-II PYQs

Free practice portal for APPSC Group-II previous year questions (Screening 2019 & 2024, Mains 2019 & 2025), with answers from APPSC's official final keys, topic-wise quizzes, a mistakes notebook, smart quiz, bookmarks and a memory heatmap.

- `docs/` – the published website (served by GitHub Pages)
- `src/` – one text file per question paper
- `tools/build.py` – rebuilds the site: `SITE_URL=https://<domain> python3 tools/build.py`, then copy `dist/site` to `docs/`
- `tools/app.html` – the app template
- `src/static/` – files copied unchanged to the site root (e.g. Google Search Console verification)

To publish a change: `SITE_URL=https://learnwithanil.in python3 tools/build.py && python3 tools/pdfs.py && python3 test/smoke.py && rm -rf docs && cp -r dist/site docs && rm -rf dist`, then commit and push.
- `tools/pdfs.py` – one PDF per paper (questions, answer key, explanations) into `dist/site/…/pdf/`; only changed papers are re-rendered (`tools/pdf-manifest.json`).

## Daily social posts (Telegram + Instagram)

`tools/social/bot.py`, run by `.github/workflows/social.yml` on GitHub Actions, posts every day (India time): a previous-year question card at 8 AM and 6 PM (rotating Group 2, TS SI, Group 1, TS Constable, CAPF), and the two memes made each morning by the Claude meme maker at 1 PM and 9 PM (a meme can be a short video: `"media": "video"` with `<n>.mp4` beside its `.json`, posted as a Reel and a Telegram video). Memes are sent to Anil on Telegram first with a Stop button. The bot's memory (cards, memes, logs) is on the `social` branch. Secrets: `TG_BOT_TOKEN`, `TG_CHANNEL`, `TG_ADMIN_CHAT`, `IG_TOKEN`, `IG_USER_ID` (optional), `STATE_KEY`. Test locally with `python3 tools/social/bot.py demo --out /tmp/cards`.
