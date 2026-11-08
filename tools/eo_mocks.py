#!/usr/bin/env python3
"""APPSC EO Grade-III Test Series: full-length mocks built from the site's own previous questions (Anil, 8 Nov 2026:
"pls upload a test series for EO exam....if possible any other questions from our data base"; chose 3 mocks from the database;
"same questions should be written as full length and sectional wise").

Each mock has the two papers of the real exam, as two tests:
    Paper I  General Studies & Mental Ability: 150 Q / 150 min, from APPSC's common GS & MA papers (EO 2026 & 2023, AMVI 2026 & 2023)
    Paper II Hindu Philosophy & Temple System: 150 Q / 150 min, from the EO Paper II PYQs (2026 & 2023)
Every question keeps its official answer, English + Telugu text and explanations; the explanation ends with where the question
was asked. Paper I questions never repeat across the 3 mocks. Paper II has only 291 four-option PYQs, so a few repeat (spread evenly).
The same questions open as sectional tests (the parts in MOCK_PACKS['appsc-eo'] in build.py).

Sealed like the other mock packs (AES-256-GCM per mock, mock id as associated data) into src/appsc-eo-mocks/<id>-<hash>.bin; the
ids start with "bk-" so the payments script serves the key to any paid All-in-One Pass holder without a script change. Keys:
MK_SRC/secret/keys.json (private) and the private sheet's keys tab (rows printed as KEYROW).

    python3 tools/eo_mocks.py          (deterministic: same seed, same mocks; re-sealing keeps the existing keys)
"""
import base64, collections, copy, hashlib, json, os, random, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('SITE_URL', 'https://learnwithanil.in')
import build as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'src', 'appsc-eo-mocks')
KEYS = os.path.join(os.environ.get('MK_SRC', '/home/claude/mk'), 'secret', 'keys.json')
N_MOCKS, QN = 3, 150
P1_PAPERS = {'e2025a': 'APPSC EO Grade-III 2026 Paper I', 'e2023a': 'APPSC EO Grade-III Mains 2023 Paper I',
             'a2026a': 'APPSC AMVI 2026 Paper I', 'a2023a': 'APPSC AMVI 2023 Paper I'}
P2_PAPERS = {'e2025b': 'APPSC EO Grade-III 2026 Paper II', 'e2023b': 'APPSC EO Grade-III Mains 2023 Paper II'}
P1_ORDER = ['cur', 'sci', 'ih', 'geo', 'pol', 'eco', 'apr', 'men']
P2_ORDER = ['ram', 'mbh', 'bhg', 'pur', 'aga', 'fes', 'ved', 'phi', 'fam', 'inc', 'eod', 'lan']
TE_FROM = {'e2025a': 'APPSC EO గ్రేడ్-III 2026 పేపర్-1', 'e2023a': 'APPSC EO గ్రేడ్-III మెయిన్స్ 2023 పేపర్-1', 'a2026a': 'APPSC AMVI 2026 పేపర్-1',
           'a2023a': 'APPSC AMVI 2023 పేపర్-1', 'e2025b': 'APPSC EO గ్రేడ్-III 2026 పేపర్-2', 'e2023b': 'APPSC EO గ్రేడ్-III మెయిన్స్ 2023 పేపర్-2'}


def pool(papers):
    cs = {c['id']: c for c in B.exam_confs()}
    out, seen = [], set()
    for cid in ('appsc-eo', 'appsc-amvi'):
        _, qs = B.load_exam(cs[cid])
        for q in qs:
            if q['p'] not in papers or not q.get('o') or q.get('lwo'): continue
            key = re.sub(r'\W+', '', q['q'].lower())[:160]
            if key in seen: continue   # the same question in two papers
            seen.add(key); out.append(q)
    return out


def quota(pool_, order, n):
    """Questions per subject in one mock: the subject's share of the pool (largest remainder)."""
    c = collections.Counter(q['s'] for q in pool_)
    raw = {s: n * c[s] / len(pool_) for s in order if c[s]}
    q = {s: int(v) for s, v in raw.items()}
    for s in sorted(raw, key=lambda s: raw[s] - q[s], reverse=True)[:n - sum(q.values())]: q[s] += 1
    return q


def deal(pool_, order, rng):
    """N_MOCKS mocks of QN questions: subject-balanced; each question used as few times as possible, evenly."""
    by = collections.defaultdict(list)
    for q in pool_: by[q['s']].append(q)
    for L in by.values(): rng.shuffle(L)
    qt = quota(pool_, order, QN)
    mocks = [[] for _ in range(N_MOCKS)]
    for s, k in qt.items():
        L, need = by[s], k * N_MOCKS
        seq = (L * (need // len(L) + 1))[:need]   # cycle through the subject's questions: repeats only when the pool is too small
        for i in range(N_MOCKS): mocks[i] += seq[i * k:(i + 1) * k]
    for m in mocks: m.sort(key=lambda q: (order.index(q['s']), q['t']))
    return mocks


def make(mid, qs, names):
    out = []
    for i, q in enumerate(qs, 1):
        x = {k: copy.deepcopy(q[k]) for k in ('s', 't', 'q', 'o', 'a', 'w', 'qt', 'ot', 'wt', 'img') if q.get(k)}
        x.update(id=f'{mid}-{i}', p=mid, n=i)
        src = f'{names[q["p"]]}, Q{q["n"]}'
        x['w'] = (x.get('w') or '').rstrip() + f' (Asked in {src}.)'
        if x.get('wt'): x['wt'] = x['wt'].rstrip() + f' ({TE_FROM[q["p"]]}, ప్రశ్న {q["n"]}.)'
        out.append(x)
    return out


def seal(mid, qs):
    keys = json.load(open(KEYS)) if os.path.exists(KEYS) else {}
    if mid not in keys:
        keys[mid] = base64.b64encode(os.urandom(32)).decode()
        os.makedirs(os.path.dirname(KEYS), exist_ok=True); json.dump(keys, open(KEYS, 'w'), indent=1); os.chmod(KEYS, 0o600)
    data = json.dumps({'id': mid, 'questions': qs}, ensure_ascii=False, separators=(',', ':')).encode()
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):   # unchanged mock: keep its file
        if f.startswith(mid + '-') and f.endswith('.bin'):
            b = open(os.path.join(OUT, f), 'rb').read()
            try:
                if AESGCM(base64.b64decode(keys[mid])).decrypt(b[:12], b[12:], mid.encode()) == data: return f, keys[mid]
            except Exception: pass
            os.remove(os.path.join(OUT, f))
    nonce = os.urandom(12)
    blob = nonce + AESGCM(base64.b64decode(keys[mid])).encrypt(nonce, data, mid.encode())
    name = f'{mid}-{hashlib.sha256(blob).hexdigest()[:10]}.bin'
    open(os.path.join(OUT, name), 'wb').write(blob)
    return name, keys[mid]


def main():
    rng = random.Random('eo-test-series-2026')
    p1, p2 = pool(P1_PAPERS), pool(P2_PAPERS)
    print(f'pool: Paper I {len(p1)} questions, Paper II {len(p2)}')
    m1, m2 = deal(p1, P1_ORDER, rng), deal(p2, P2_ORDER, rng)
    uses = collections.Counter(q['id'] for m in m2 for q in m)
    print('Paper II repeats:', sum(1 for v in uses.values() if v > 1), 'questions used twice')
    for i in range(N_MOCKS):
        for part, qs, names in (('a', m1[i], P1_PAPERS), ('b', m2[i], P2_PAPERS)):
            mid = f'bk-eomk-{i + 1}{part}'
            x = make(mid, qs, names)
            f, key = seal(mid, x)
            print(mid, len(x), dict(collections.Counter(q['s'] for q in x)), f)
            print('KEYROW', json.dumps([mid, key, f, __import__('datetime').date.today().isoformat()]))


if __name__ == '__main__':
    main()
