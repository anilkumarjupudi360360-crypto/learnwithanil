#!/usr/bin/env python3
"""Seal the APPSC Group-1 Mains model answers for the website (see tools/g1mains.py).

    python3 tools/g1m_seal.py /home/claude/g1m/work [--partial]

Reads the private answer files <year>-p<n>.json ({question id: answer}), encrypts all answers with AES-256-GCM
(additional data "bk-g1m-ans", the scheme of the sealed books) into src/books/g1m-ans-<hash>.bin, and writes
src/appsc-group-1/mains-pyqs/answers.json with the key id, the file name and the free sample answers (Q1(a) and Q1(b) of
each paper). The key is kept in G1M_PRIV/key.json (default /home/claude/g1m/secret; never committed) and reused; the row
for the 'keys' tab of the private passes sheet (mock_id | key | file | opens) is printed as KEYROW.
"""
import base64, glob, hashlib, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KID = 'bk-g1m-ans'
work = sys.argv[1]
priv = os.environ.get('G1M_PRIV', '/home/claude/g1m/secret')
qs = json.load(open(os.path.join(ROOT, 'src', 'appsc-group-1', 'mains-pyqs', 'questions.json'), encoding='utf-8'))
ans = {}
for f in sorted(glob.glob(os.path.join(work, '20??-p?.json'))): ans.update(json.load(open(f, encoding='utf-8')))
ids = [q['id'] for q in qs]
missing = [i for i in ids if not ans.get(i)]
if missing and '--partial' not in sys.argv: sys.exit(f'{len(missing)} answers missing, e.g. {missing[:5]}')
ans = {i: ans[i] for i in ids if ans.get(i)}
os.makedirs(priv, exist_ok=True)
kp = os.path.join(priv, 'key.json')
key = json.load(open(kp))['key'] if os.path.exists(kp) else base64.b64encode(os.urandom(32)).decode()
json.dump({'key': key}, open(kp, 'w')); os.chmod(kp, 0o600)
data = json.dumps(ans, ensure_ascii=False, separators=(',', ':')).encode()
nonce = os.urandom(12)
blob = nonce + AESGCM(base64.b64decode(key)).encrypt(nonce, data, KID.encode())
name = 'g1m-ans-' + hashlib.sha256(blob).hexdigest()[:10] + '.bin'
bdir = os.path.join(ROOT, 'src', 'books')
for f in os.listdir(bdir):
    if f.startswith('g1m-ans-') and f.endswith('.bin') and f != name: os.remove(os.path.join(bdir, f))
open(os.path.join(bdir, name), 'wb').write(blob)
free = {q['id']: ans[q['id']] for q in qs if q['qno'] in ('1(a)', '1(b)') and q['id'] in ans}
json.dump({'key': KID, 'file': name, 'n': len(ans), 'free': free},
          open(os.path.join(ROOT, 'src', 'appsc-group-1', 'mains-pyqs', 'answers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'sealed {len(ans)} answers ({len(free)} free samples) into src/books/{name} ({len(blob):,} bytes)')
print('KEYROW', json.dumps([KID, key, name]))
