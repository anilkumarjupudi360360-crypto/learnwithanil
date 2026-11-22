"""Seal the re-covered books into the repo (same keys, new file names) and refresh the site images and samples."""
import sys, os, json, base64, hashlib, shutil; sys.path.insert(0, '/home/claude/covers/tools')
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sample_images import cover_jpg, sample_jpg
from build_books import SAMPLES
from scenes import SCENES
PAID, REPO, P = '/home/claude/lwa-books/paid', '/home/claude/learnwithanil', '/home/claude/covers/parts'
keys = json.load(open(f'{PAID}/keys.json'))
man_p = f'{REPO}/src/books/books.json'
man = json.load(open(man_p))
rows = []
for b in SCENES:
    pdf = open(f'{PAID}/{b}.pdf', 'rb').read()
    kid = 'bk-' + b
    name = f'{b}-{hashlib.sha256(pdf).hexdigest()[:10]}.bin'
    key = base64.b64decode(keys[kid])
    iv = os.urandom(12)
    open(f'{REPO}/src/books/{name}', 'wb').write(iv + AESGCM(key).encrypt(iv, pdf, kid.encode()))
    old = man[b]['file']
    man[b]['file'] = name; man[b]['bytes'] = len(pdf)
    rows.append((kid, old, name))
    cover_jpg(f'{PAID}/{b}.pdf', f'{REPO}/src/static/notes-{b}-cover.jpg')
    if b in SAMPLES:
        shutil.copy(f'{P}/samples/{SAMPLES[b]}', f'{REPO}/src/static/{SAMPLES[b]}')
json.dump(man, open(man_p, 'w'), indent=1)
sample_jpg(f'{PAID}/cst-en.pdf', 38, f'{REPO}/src/static/notes-cst-en-p1.jpg')
sample_jpg(f'{PAID}/cst-en.pdf', 53, f'{REPO}/src/static/notes-cst-en-p2.jpg')
json.dump(rows, open(f'{PAID}/covers-keyrows.json', 'w'), indent=1)
for r in rows: print(*r)
