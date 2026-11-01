#!/usr/bin/env python3
"""Seal the APPSC Group-1 Mains model answers for the website (see tools/g1mains.py).

    python3 tools/g1m_seal.py /home/claude/g1m/work [--partial]

Reads the private answer files <year>-p<n>.json ({question id: answer markup}), renders them to HTML (tools/g1m_render.py), encrypts them with AES-256-GCM
(one key; additional data "bk-g1m-ans", the scheme of the sealed books) into one file per paper and year,
src/books/g1m-ans-<year>-p<n>-<hash>.bin, and writes
src/appsc-group-1/mains-pyqs/answers.json with the key id, the file names and the free sample answers (Q1(a) and Q1(b) of
each paper). The key is kept in G1M_PRIV/key.json (default /home/claude/g1m/secret; never committed) and reused; the row
for the 'keys' tab of the private passes sheet (mock_id | key | file | opens) is printed as KEYROW.
"""
import base64, glob, hashlib, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g1m_render   # answers are sealed as ready HTML (text, key words and diagrams), Anil 1 Nov 2026

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KID = 'bk-g1m-ans'
work = sys.argv[1]
priv = os.environ.get('G1M_PRIV', '/home/claude/g1m/secret')
qs = json.load(open(os.path.join(ROOT, 'src', 'appsc-group-1', 'mains-pyqs', 'questions.json'), encoding='utf-8'))
ans = {}
for f in sorted(glob.glob(os.path.join(work, '20??-p?.json'))): ans.update(json.load(open(f, encoding='utf-8')))
ids = [q['id'] for q in qs if q['paper'] != 'I']   # Paper I (essay): questions only
missing = [i for i in ids if not ans.get(i)]
if missing and '--partial' not in sys.argv: sys.exit(f'{len(missing)} answers missing, e.g. {missing[:5]}')
ans = {i: g1m_render.render(ans[i]) for i in ids if ans.get(i)}
os.makedirs(priv, exist_ok=True)
kp = os.path.join(priv, 'key.json')
key = json.load(open(kp))['key'] if os.path.exists(kp) else base64.b64encode(os.urandom(32)).decode()
json.dump({'key': key}, open(kp, 'w')); os.chmod(kp, 0o600)
groups = {}   # one sealed bundle per paper and year (Anil, 1 Nov 2026: one answer per page, so a page loads only its paper)
for i, h in ans.items(): groups.setdefault(re.match(r'g1m-(\d{4}-p\d)-', i).group(1), {})[i] = h
bdir = os.path.join(ROOT, 'src', 'books')
files, total = {}, 0
for g, A in sorted(groups.items()):
    data = json.dumps(A, ensure_ascii=False, separators=(',', ':')).encode()
    nonce = os.urandom(12)
    blob = nonce + AESGCM(base64.b64decode(key)).encrypt(nonce, data, KID.encode())
    files[g] = f'g1m-ans-{g}-' + hashlib.sha256(blob).hexdigest()[:10] + '.bin'
    open(os.path.join(bdir, files[g]), 'wb').write(blob); total += len(blob)
for f in os.listdir(bdir):
    if f.startswith('g1m-ans-') and f.endswith('.bin') and f not in files.values(): os.remove(os.path.join(bdir, f))
free = {q['id']: ans[q['id']] for q in qs if q['qno'] in ('1(a)', '1(b)') and q['id'] in ans}
json.dump({'key': KID, 'files': files, 'n': len(ans), 'free': free},
          open(os.path.join(ROOT, 'src', 'appsc-group-1', 'mains-pyqs', 'answers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'sealed {len(ans)} answers ({len(free)} free samples) into {len(files)} files in src/books ({total:,} bytes)')
print('KEYROW', json.dumps([KID, key, 'g1m-ans-<year>-p<n>-*.bin (one per paper)']))
