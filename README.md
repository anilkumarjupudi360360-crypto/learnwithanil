# Learn with Anil – social posting state

This branch is the memory of the daily social bot (`tools/social/bot.py` on `main`, run by `.github/workflows/social.yml`).
Nothing here is part of the website.

- `cards/` – question cards (made a day ahead) with their captions
- `memes/<date>/1.jpg, 2.jpg` + `.json` – memes queued by the Claude meme maker (1 = current affairs, posts 1 PM; 2 = aspirant life, posts 9 PM)
- `memes/history.jsonl` – every meme posted, so the meme maker doesn't repeat a topic
- `log/<date>.json` – what was posted where, with the Instagram and Telegram links
- `used-questions.json` – questions already posted
- `control.json` – Telegram previews and stopped memes

## Meme JSON (written by the meme maker)

```json
{"kind": "current-affairs", "title": "Short title", "topic": "the news item",
 "caption_ig": "Instagram caption with hashtags", "caption_tg": "Telegram caption (links allowed)",
 "sources": ["https://..."], "canva": "https://www.canva.com/design/..."}
```
The image is `<n>.jpg` (or `.png`), 1080 × 1350. If only Canva's download link is available, put it in `"export_url"` and the bot fetches it.
