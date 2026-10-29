#!/usr/bin/env python3
"""Seal the paid study books (src/notes.json) so they can be downloaded only with the ₹45 PYQ Pass.

Anil, 26 Oct 2026: "one ₹45 = everything" — the PYQ Pass now includes every mock series and the books. The book PDFs are
paid content, so they are never committed in readable form. This script encrypts each one with its own random
AES-256-GCM key (additional data = the key id "bk-<book id>", the same scheme as the sealed mocks) and writes only
the encrypted file to src/books/. build.py copies src/books/*.bin to /books/ on the site (robots.txt keeps search
engines out). The keys go in the 'keys' tab of the private "Learn with Anil – Passes" sheet; the payments script hands
a key only to a phone with a valid PYQ Pass ('mock' action with id "bk-<book id>"), and the app decrypts in the browser.

    python3 tools/books_seal.py            # seal every book that has a PDF in BOOKS_PRIV
Private folder BOOKS_PRIV (default /home/claude/lwa-books/paid; a copy of each PDF is on Anil's PC):
    <book id>.pdf      e.g. apeco-en.pdf, apeco-te.pdf, stfull-en.pdf (ids from src/notes.json)
    keys.json          {"bk-apeco-en": "<base64 key>", ...} — reused, so re-sealing keeps the keys already in the sheet
Prints the keys-tab rows (mock_id | key | file | opens) to BOOKS_PRIV/keys-tab.tsv; never to the terminal.
"""
import base64, datetime, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIV = os.environ.get('BOOKS_PRIV', '/home/claude/lwa-books/paid')
OUT = os.path.join(ROOT, 'src', 'books')


def main():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    books = json.load(open(os.path.join(ROOT, 'src', 'notes.json'), encoding='utf-8'))
    kpath = os.path.join(PRIV, 'keys.json')
    keys = json.load(open(kpath)) if os.path.exists(kpath) else {}
    os.makedirs(OUT, exist_ok=True)
    # keep the entries of books whose PDF is not in BOOKS_PRIV this time (e.g. sealing one new book on another machine)
    mpath = os.path.join(OUT, 'books.json')
    manifest, rows = (json.load(open(mpath)) if os.path.exists(mpath) else {}), []
    today = datetime.date.today().isoformat()
    for b in books:
        src = os.path.join(PRIV, b['id'] + '.pdf')
        if not os.path.exists(src): print('  no PDF for', b['id'], '(skipped)'); continue
        kid = 'bk-' + b['id']
        if kid not in keys: keys[kid] = base64.b64encode(os.urandom(32)).decode()
        key = base64.b64decode(keys[kid])
        pdf = open(src, 'rb').read()
        name = f'{b["id"]}-{hashlib.sha256(pdf).hexdigest()[:10]}.bin'
        out = os.path.join(OUT, name)
        if not os.path.exists(out):
            for f in os.listdir(OUT):   # drop the old sealed copy of this book
                if f.startswith(b['id'] + '-') and f.endswith('.bin'): os.remove(os.path.join(OUT, f))
            iv = os.urandom(12)
            open(out, 'wb').write(iv + AESGCM(key).encrypt(iv, pdf, kid.encode()))
        nice = re.sub(r'[^A-Za-z0-9]+', '-', f'LearnWithAnil {b["title_en"]} {b.get("medium_en", "")} 2026-27').strip('-')
        manifest[b['id']] = dict(file=name, bytes=len(pdf), pdf=nice + '.pdf')
        rows.append('\t'.join([kid, keys[kid], name, today]))
        print(f'  {kid}: {len(pdf):,} bytes -> src/books/{name}')
    json.dump(keys, open(kpath, 'w'), indent=1)
    json.dump(manifest, open(os.path.join(OUT, 'books.json'), 'w'), indent=1)
    open(os.path.join(PRIV, 'keys-tab.tsv'), 'w').write('\n'.join(rows) + '\n')
    print(f'{len(rows)} books sealed; keys-tab rows in {PRIV}/keys-tab.tsv')


if __name__ == '__main__':
    sys.exit(main())
