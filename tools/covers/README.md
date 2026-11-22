# Book covers with pictures (22 Nov 2026)

Anil (18 Nov 2026): every Learn with Anil book cover carries pictures that match its exam and subject, and the inside
pages follow the cover's colour (green cover -> green-themed book). These scripts re-cover an already-built book PDF
without its sources:

- `split.py` splits the old cover (page 1) into background (navy fill, grid, glow) and foreground (text, pills, photo).
- `layout.py` plans the new page: a picture panel (112-150 pt high) under the logo, the old foreground re-flowed below
  it (gaps tightened, scaled down to 95% at most), author block moved to y=765 like the AEE book.
- `scenes.py` holds the drawn pictures (SVG, 494 x 150 frame); `compose.py` renders a panel with headless Chrome and
  builds the page. `recolor.py` maps the navy palette to the AEE green palette (Computer Skill Test).
- `build_books.py` puts the cover into each book and its free sample; `seal_publish_prep.py` re-seals the books with
  their existing keys (new file names), refreshes notes-<id>-cover.jpg and the CST sample images.

Paths assume the decrypted books in /home/claude/lwa-books/paid/orig-<id>.pdf (keys from the Passes sheet keys tab)
and the scripts in /home/claude/covers/tools. The Mental Ability book (ma-en) was held back by Anil on 22 Nov 2026.
