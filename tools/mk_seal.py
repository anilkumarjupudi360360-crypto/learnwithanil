#!/usr/bin/env python3
"""Mission Khaki (and other paid mock packs): seal each mock for the public site.

The questions are paid content, so their source is NOT in this repository. It lives in MK_SRC (default
/home/claude/mk: one folder per mock with en-*.txt / te-*.txt and mock-final.json). Each mock is encrypted with its
own random AES-256-GCM key; only the ciphertext is committed (src/mission-khaki/<file>.bin) and published at
/ts-police-si/mk/<file>.bin. The keys go in the private "Learn with Anil – Passes" Google Sheet (tab "keys"); the
payments script gives a mock's key only to a phone with a valid mock pass, and only from the mock's opening date.

    python3 tools/mk_seal.py mk-si-1 /home/claude/mk/m1/mock-final.json
        -> writes src/mission-khaki/<file>.bin and prints the sheet row: mock id, key (base64), file, opening date
"""
import base64, hashlib, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'src', 'mission-khaki')
KEYS = os.path.join(os.environ.get('MK_SRC', '/home/claude/mk'), 'secret', 'keys.json')   # never committed


def seal(mock_id, src_json):
    qs = json.load(open(src_json, encoding='utf-8'))
    assert qs and all(q['id'].startswith(mock_id + '-') for q in qs), 'question ids must start with the mock id'
    os.makedirs(os.path.dirname(KEYS), exist_ok=True)
    keys = json.load(open(KEYS)) if os.path.exists(KEYS) else {}
    if mock_id not in keys:
        keys[mock_id] = base64.b64encode(os.urandom(32)).decode()
        json.dump(keys, open(KEYS, 'w'), indent=1)
        os.chmod(KEYS, 0o600)
    key = base64.b64decode(keys[mock_id])
    data = json.dumps({'id': mock_id, 'questions': qs}, ensure_ascii=False, separators=(',', ':')).encode()
    nonce = os.urandom(12)
    blob = nonce + AESGCM(key).encrypt(nonce, data, mock_id.encode())   # mock id as associated data
    name = mock_id + '-' + hashlib.sha256(blob).hexdigest()[:10] + '.bin'
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith(mock_id + '-') and f.endswith('.bin') and f != name: os.remove(os.path.join(OUT, f))
    open(os.path.join(OUT, name), 'wb').write(blob)
    return name, keys[mock_id], len(qs)


if __name__ == '__main__':
    name, k, n = seal(sys.argv[1], sys.argv[2])
    print(f'{sys.argv[1]}: {n} questions sealed into src/mission-khaki/{name}')
    print('KEYROW', json.dumps([sys.argv[1], k, name]))
