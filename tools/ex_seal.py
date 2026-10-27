#!/usr/bin/env python3
"""Seal the paid explanations, so the public app data no longer carries them (Anil, 27 Oct 2026).

Every question, its options and its correct answer stay public (question, paper and subject pages, and the app data),
and so do the explanations of the free sample (build.sample_ids: the first SAMPLE_N questions of each paper). The other
explanations are what the ₹45 PYQ Pass sells, but until now they were in the public app data file
(/<exam>/data/<key>-<hash>.js), readable by anyone who opened it. This script puts them, one bundle per exam, in a file
encrypted with AES-256-GCM (additional data = the key id "bk-ex-<exam id>", the same scheme as the sealed books and
booklets) and writes:
    src/books/ex-<exam id>-<hash>.bin    the encrypted bundle {question id: [explanation, explanation in Telugu/Hindi]}
    src/books/explanations.json          exam id -> {key, file, n, h: {question id: 8-hex hash of that explanation}}
build.py copies the bundles to /books/ (robots.txt keeps search engines out), takes out of the app data every
explanation whose hash is in the manifest (marking the question "wx": 1), and tells the app where the bundle is.
The app asks the payments script for the key with the 'mock' action (id "bk-ex-<exam id>"; any bk- id needs a valid
PYQ Pass) and decrypts the bundle in the browser. An explanation added or edited after the last sealing stays public
(build.py prints how many) until this script is run again, so nothing ever disappears for a paying student.

    python3 tools/ex_seal.py [exam id ...]       # default: every exam with explanations

Keys: BOOKS_PRIV/ex-keys.json ({"bk-ex-<exam id>": "<base64 key>"}, never committed; reused, so re-sealing keeps the key
already in the sheet). The same keys are in the 'keys' tab of the private "Learn with Anil – Passes" sheet
(mock_id | key | file | opens); a session without ex-keys.json can rebuild it from those bk-ex-* rows before
re-sealing. New keys are written to BOOKS_PRIV/ex-keys-tab.tsv for the sheet; never printed.
"""
import base64, datetime, hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('SITE_URL', 'https://learnwithanil.in')
import build as B  # noqa: E402

PRIV = os.environ.get('BOOKS_PRIV', '/home/claude/lwa-books/paid')
SEALED = os.path.join(B.ROOT, 'src', 'books')
MANIFEST = os.path.join(SEALED, 'explanations.json')


def paid_explanations(questions):
    """{question id: [w, wt]} for every explanation outside the free sample."""
    free = B.sample_ids(questions)
    return {q['id']: [q['w'], q.get('wt', '')] for q in questions if q.get('w') and q['id'] not in free}


def main(only):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    os.makedirs(PRIV, exist_ok=True)
    kpath = os.path.join(PRIV, 'ex-keys.json')
    keys = json.load(open(kpath)) if os.path.exists(kpath) else {}
    manifest = json.load(open(MANIFEST, encoding='utf-8')) if os.path.exists(MANIFEST) else {}
    today = datetime.date.today().isoformat()
    rows, new = [], []
    for conf in B.exam_confs():
        if only and conf['id'] not in only: continue
        papers, qs = B.load_exam(conf)[:2]
        ex = paid_explanations(qs) if qs else {}
        if not ex: continue
        kid = 'bk-ex-' + conf['id']
        if kid not in keys:
            keys[kid] = base64.b64encode(os.urandom(32)).decode(); new.append(kid)
        plain = json.dumps(ex, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
        name = f'ex-{conf["id"]}-{hashlib.sha256(plain).hexdigest()[:10]}.bin'
        out = os.path.join(SEALED, name)
        if not os.path.exists(out):
            for f in os.listdir(SEALED):   # drop this exam's older bundle
                if f.startswith(f'ex-{conf["id"]}-') and f.endswith('.bin'): os.remove(os.path.join(SEALED, f))
            iv = os.urandom(12)
            open(out, 'wb').write(iv + AESGCM(base64.b64decode(keys[kid])).encrypt(iv, plain, kid.encode()))
        manifest[conf['id']] = dict(key=kid, file=name, n=len(ex), h={qid: B.ex_hash(w, wt) for qid, (w, wt) in sorted(ex.items())})
        rows.append('\t'.join([kid, keys[kid], name, today]))
        print(f'  {conf["id"]}: {len(ex)} paid explanations sealed -> src/books/{name}')
    json.dump(keys, open(kpath, 'w'), indent=1); os.chmod(kpath, 0o600)
    json.dump(manifest, open(MANIFEST, 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    tsv = os.path.join(PRIV, 'ex-keys-tab.tsv')
    open(tsv, 'w').write('\n'.join(rows) + '\n'); os.chmod(tsv, 0o600)
    print(f'{len(rows)} exams sealed; new keys: {", ".join(new) or "none"}. Rows for the sheet\'s keys tab: {tsv}')


if __name__ == '__main__':
    main(set(sys.argv[1:]))
