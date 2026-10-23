#!/usr/bin/env python3
"""Bahubali Test Series: paid full-length tests for APPSC Group-II Mains (Paper I and Paper II, 12 tests each).

The questions are paid content, so their source is NOT in this public repository. It lives in BAHUBALI_SRC
(default /home/claude/bahubali; a copy is kept on Anil's PC). Only encrypted files are committed:

    src/bahubali/series.json   public settings: key-derivation salt, a check value, the list of sealed tests
    src/bahubali/data/*.bin    one AES-256-GCM file per test (questions, answers, explanations, Telugu)
    src/bahubali/pdf/*.pdf     question booklet and answers PDF per test, password = the access code

Buyers get the access code on the access card PDF delivered by Instamojo. The page derives the AES key from the
code in the browser (PBKDF2-SHA256), so tests added later open with the same code.

    python3 tools/bahubali.py seal           # encrypt every test in BAHUBALI_SRC/tests + render the PDFs
    python3 tools/bahubali.py card           # make the access card PDF (BAHUBALI_SRC/out) for Instamojo
build.py calls page() to publish /appsc-group-2/bahubali-test-series/.

Source layout in BAHUBALI_SRC:
    secret/code.txt            the access code, e.g. BAHU-XXXX-XXXX (or env BAHUBALI_CODE)
    tests/p1-t1.txt            150 questions, same format as src/*.txt; subjects aph+pol (P-I) or eco+sci (P-II)
    te/p1-t1.txt               Telugu text, same format as src/te/*.txt
    te/p1-t1.expl.json         Telugu explanations {"<question number>": "..."}
"""
import asyncio, base64, hashlib, html, json, os, re, shutil, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402

ROOT = B.ROOT
PUB = os.path.join(ROOT, 'src', 'bahubali')
PRIV = os.environ.get('BAHUBALI_SRC', '/home/claude/bahubali')
ITER = 210000
URLDIR = 'appsc-group-2/bahubali-test-series'
NAME = 'Bahubali Test Series'
PRICE = 250
TESTS_PER_PAPER = 12
esc = B.esc

PAPERS = [
  dict(id='p1', no=1, name='Paper I', sections=[
       ('A', 'Section A', 'Social & Cultural History of Andhra Pradesh', 'aph', 1, 75),
       ('B', 'Section B', 'General Overview of the Indian Constitution', 'pol', 76, 150)]),
  dict(id='p2', no=2, name='Paper II', sections=[
       ('A', 'Section A', 'Indian & Andhra Pradesh Economy', 'eco', 1, 75),
       ('B', 'Section B', 'Science & Technology', 'sci', 76, 150)]),
]
UNITS = {
  'aph': ['Ancient Andhra', 'Medieval Andhra', 'Europeans & British Rule', 'Social & National Movements', 'Andhra Movement', 'AP Formation & After (1956–2014)'],
  'pol': ['Constitutional Framework', 'Structure of Government', 'Centre-State Relations', 'Constitutional & Statutory Bodies', 'Federalism, Parties & Elections', 'Local Governance'],
  'eco': ['Indian Economy & Planning', 'Money, Banking & Public Finance', 'Agriculture, Industry & Services', 'AP Economy & Public Finance', 'AP Agriculture & Allied', 'AP Industry & Services'],
  'sci': ['S&T Policy & Emerging Tech', 'Space, Defence, ICT & Nuclear', 'Energy', 'Ecosystems & Biodiversity', 'Waste & Pollution', 'Environment & Climate Change', 'Health & Public Health'],
}
SUBJ = {k: (k, k, k, v) for k, v in UNITS.items()}
SAMPLES = [('p1t1', 'A'), ('p1t1', 'B'), ('p2t1', 'A'), ('p2t1', 'B')]   # one free sample question per section


def tid(p, n): return f'{p}t{n}'
def label(n): return f'Grand Test {n:02d}'
def pdf_names(p, n):
    base = f'bahubali-paper-{p["no"]}-grand-test-{n:02d}'
    return f'pdf/{base}-question-booklet.pdf', f'pdf/{base}-answers.pdf'


def norm(code): return re.sub(r'[^A-Z0-9]', '', code.upper())


def read_code():
    c = os.environ.get('BAHUBALI_CODE') or open(os.path.join(PRIV, 'secret', 'code.txt')).read()
    return c.strip()


def derive(code, salt):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(norm(code).encode())


def seal_bytes(key, data):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    iv = os.urandom(12)
    return iv + AESGCM(key).encrypt(iv, data, None)


def unseal_bytes(key, blob):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(key).decrypt(blob[:12], blob[12:], None)


def load_series():
    p = os.path.join(PUB, 'series.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def load_test(p, n):
    """Parse one private test (English + Telugu + Telugu explanations) into the payload the page decrypts."""
    f = f'p{p["no"]}-t{n}.txt'
    paper = dict(id=tid(p['id'], n), file=f)
    qs = B.parse(paper, os.path.join(PRIV, 'tests'), SUBJ) if os.path.exists(os.path.join(PRIV, 'tests', f)) else []
    if not qs: return None
    # Telugu (same format as the official-booklet files)
    B.parse_te(paper, qs, PRIV, 'te')
    xp = os.path.join(PRIV, 'te', f.replace('.txt', '.expl.json'))
    wt = json.load(open(xp, encoding='utf-8')) if os.path.exists(xp) else {}
    secs = p['sections']
    out = []
    for q in qs:
        sec = next(s for s in secs if s[4] <= q['n'] <= s[5])
        if q['s'] != sec[3]: print(f'  ! {paper["id"]} Q{q["n"]}: subject {q["s"]} in {sec[1]}')
        if len(q.get('a', [])) != 1: print(f'  ! {paper["id"]} Q{q["n"]}: needs exactly one answer')
        x = dict(n=q['n'], s=sec[0], t=q['t'], q=q['q'], o=q['o'], a=q['a'][0], w=q['w'])
        if q.get('qt'): x['qt'] = q['qt']
        if q.get('ot'): x['ot'] = q['ot']
        if wt.get(str(q['n'])): x['wt'] = wt[str(q['n'])]
        out.append(x)
    if len(out) != 150: print(f'  ! {paper["id"]}: {len(out)} questions (a full test has 150)')
    nte = sum(1 for x in out if x.get('qt')); nwt = sum(1 for x in out if x.get('wt'))
    print(f'  {paper["id"]}: {len(out)} questions, Telugu {nte}, Telugu explanations {nwt}')
    return dict(id=paper['id'], paper=p['id'], paper_name=p['name'], n=n, label=label(n), min=150,
                sections=[dict(k=s[0], name=s[1], sub=s[2], **{'from': s[4], 'to': s[5]}) for s in secs], q=out)


# ---------------------------------------------------------------- PDFs
PDF_CSS = """
@page{size:A4;margin:13mm 12mm 15mm 12mm}
*{box-sizing:border-box}
body{margin:0;font:10.2pt/1.42 'Source Sans 3',sans-serif;color:#0D1830}
[lang=te]{font-family:'Noto Sans Telugu','Source Sans 3',sans-serif;line-height:1.6}
.cover{height:258mm;display:flex;flex-direction:column;border:2.5pt solid #0C2266;border-radius:8pt;padding:16mm 14mm}
.cover .brand{font:500 9pt 'IBM Plex Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:#55627C}
.cover h1{font:800 34pt/1.05 Archivo,sans-serif;margin:10mm 0 2mm;color:#0C2266}
.cover h1 span{color:#C98A00}
.cover h2{font:800 20pt Archivo,sans-serif;margin:0 0 2mm}
.cover .te{font-size:12pt;color:#25324B}
.cover table{border-collapse:collapse;margin:8mm 0 6mm;width:100%}
.cover td{border:1pt solid #D6DFEC;padding:5pt 8pt;font-size:10.5pt}
.cover ol{margin:2mm 0 0;padding-left:14pt}
.cover li{margin:2pt 0}
.cover .foot{margin-top:auto;font-size:9pt;color:#55627C;border-top:1pt solid #D6DFEC;padding-top:4mm}
.sec{font:800 13pt Archivo,sans-serif;color:#0C2266;margin:4mm 0 3mm;padding:3pt 0;border-bottom:1.5pt solid #1846C7;break-after:avoid}
.cols{column-count:2;column-gap:7mm;column-rule:.5pt solid #D6DFEC}
.q{break-inside:avoid;margin:0 0 7pt;padding-bottom:5pt;border-bottom:.4pt solid #E3E9F3}
.q p{margin:0;white-space:pre-line;font-weight:600}
.q .n{font-weight:700;color:#1440B8}
.q ol{margin:2pt 0 0;padding-left:0;list-style:none}
.q li{margin:.5pt 0}
.q .te{margin-top:3pt;padding-left:6pt;border-left:1.6pt solid #D6DFEC;color:#25324B}
.q .te p{font-weight:500}
.key{display:grid;grid-template-columns:repeat(10,1fr);gap:2pt 4pt;font:500 9pt 'IBM Plex Mono',monospace;margin:2mm 0 4mm}
.key span{border:.5pt solid #D6DFEC;border-radius:3pt;padding:1.5pt 3pt;text-align:center}
.ans{break-inside:avoid;margin:0 0 7pt;padding-bottom:5pt;border-bottom:.4pt solid #E3E9F3}
.ans .h{font-weight:700}
.ans .h b{color:#12804A}
.ans .u{font:500 8pt 'IBM Plex Mono',monospace;color:#55627C}
.ans p{margin:1.5pt 0 0}
.ans p.te{color:#25324B}
.omr{display:grid;grid-template-columns:repeat(5,1fr);gap:1.6mm 4mm;font:500 8.5pt 'IBM Plex Mono',monospace}
.omr div{display:flex;align-items:center;gap:1.4mm}
.omr b{width:7mm;text-align:right}
.omr i{width:4.2mm;height:4.2mm;border:.8pt solid #0D1830;border-radius:50%;display:inline-grid;place-items:center;font-style:normal;font-size:6.5pt}
.pb{break-before:page}
h3{font:800 15pt Archivo,sans-serif;margin:0 0 3mm;color:#0C2266}
"""


def _opts(o):
    return '<ol>' + ''.join(f'<li>({i + 1}) {esc(x)}</li>' for i, x in enumerate(o)) + '</ol>'


def cover_html(T, kind):
    secs = ''.join(f'<tr><td>{esc(s["name"])}</td><td>{esc(s["sub"])}</td><td>Q{s["from"]}–{s["to"]}</td><td>75 marks</td></tr>' for s in T['sections'])
    what = 'Question Booklet' if kind == 'q' else 'Answer Key and Explanations'
    inst = ('<p><b>Instructions</b></p><ol>'
            '<li>This booklet has 150 questions. Each question has four options; choose the one correct answer.</li>'
            '<li>Each correct answer carries 1 mark. One-third (1/3) of a mark is deducted for each wrong answer. Unanswered questions get no mark.</li>'
            '<li>Time allowed: 150 minutes. Use the OMR sheet at the end of this booklet, or write the test online at learnwithanil.in.</li>'
            '<li>Questions are in English and Telugu. If there is any difference, the English version prevails.</li></ol>'
            '<p class="te" lang="te" style="margin-top:3mm">ఈ బుక్‌లెట్‌లో 150 ప్రశ్నలు ఉన్నాయి. ప్రతి సరైన సమాధానానికి 1 మార్కు; ప్రతి తప్పు సమాధానానికి 1/3 మార్కు తగ్గించబడుతుంది. సమయం: 150 నిమిషాలు. ఇంగ్లీష్, తెలుగు పాఠాల మధ్య తేడా ఉంటే ఇంగ్లీష్ పాఠమే ప్రామాణికం.</p>') if kind == 'q' else (
            '<p>The answer key is followed by an explanation for every question, in English and Telugu, with the official source for each answer.</p>')
    return (f'<div class="cover"><div class="brand">Learn with Anil · learnwithanil.in · APPSC Group-II Mains 2026</div>'
            f'<h1><span>Bahubali</span><br>Test Series</h1><h2>{esc(T["paper_name"])} · {esc(T["label"])}</h2>'
            f'<p class="te" lang="te">బాహుబలి టెస్ట్ సిరీస్ · పేపర్-{"I" if T["paper"] == "p1" else "II"} · గ్రాండ్ టెస్ట్ {T["n"]:02d}</p>'
            f'<p style="margin-top:4mm;font-weight:700;font-size:12pt">{what}</p>'
            f'<table><tr><td><b>Time</b></td><td>150 minutes</td><td><b>Max. marks</b></td><td>150</td></tr>{secs}</table>'
            f'{inst}<div class="foot">Original questions by Jupudi Anil Kumar, Learn with Anil, for the purchaser\'s personal use only. '
            f'Copying or sharing this booklet is not allowed. Not affiliated with APPSC.</div></div>')


def booklet_html(T):
    parts = [cover_html(T, 'q')]
    for s in T['sections']:
        parts.append(f'<div class="pb"></div><div class="sec">{esc(s["name"])} · {esc(s["sub"])} (Q{s["from"]}–{s["to"]})</div><div class="cols">')
        for q in T['q']:
            if not s['from'] <= q['n'] <= s['to']: continue
            te = f'<div class="te" lang="te"><p>{esc(q["qt"])}</p>{_opts(q.get("ot") or q["o"])}</div>' if q.get('qt') else ''
            parts.append(f'<div class="q"><p><span class="n">{q["n"]}.</span> {esc(q["q"])}</p>{_opts(q["o"])}{te}</div>')
        parts.append('</div>')
    omr = ''.join(f'<div><b>{n}</b>' + ''.join(f'<i>{k}</i>' for k in '1234') + '</div>' for n in range(1, 151))
    parts.append(f'<div class="pb"></div><h3>OMR answer sheet · {esc(T["paper_name"])} · {esc(T["label"])}</h3>'
                 f'<p style="margin:0 0 4mm">Name: ______________________________ &nbsp; Date: ____________ &nbsp; Score: ______ / 150</p><div class="omr">{omr}</div>')
    return parts


def answers_html(T):
    parts = [cover_html(T, 'a'), '<div class="pb"></div><h3>Answer key</h3>',
             '<div class="key">' + ''.join(f'<span>{q["n"]}-({q["a"] + 1})</span>' for q in T['q']) + '</div>']
    for s in T['sections']:
        parts.append(f'<div class="sec">{esc(s["name"])} · {esc(s["sub"])}</div><div class="cols">')
        for q in T['q']:
            if not s['from'] <= q['n'] <= s['to']: continue
            a = q['a']; ans = f'({a + 1}) {q["o"][a]}'
            te = f'<p class="te" lang="te">{esc(q["wt"])}</p>' if q.get('wt') else ''
            parts.append(f'<div class="ans"><div class="h">{q["n"]}. Answer <b>{esc(ans)}</b></div><div class="u">{esc(q["t"])}</div>'
                         f'<p>{esc(q["w"])}</p>{te}</div>')
        parts.append('</div>')
    return parts


def doc(T, parts):
    import pdfs as P
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{NAME} · {esc(T["paper_name"])} · {esc(T["label"])}</title>'
            f'<meta name="author" content="Jupudi Anil Kumar, Learn with Anil"><style>{P.font_css()}{PDF_CSS}</style></head><body>{"".join(parts)}</body></html>')


def foot(text):
    return ('<div style="width:100%;font:7.5px sans-serif;color:#55627C;padding:0 12mm;display:flex;justify-content:space-between">'
            f'<span>{esc(text)}</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')


async def render(jobs):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page()
        tmp = tempfile.mkdtemp(prefix='bb-pdf-')
        for out, html_, ftxt in jobs:
            f = os.path.join(tmp, 'p.html'); open(f, 'w', encoding='utf-8').write(html_)
            await pg.goto('file://' + f); await pg.evaluate('document.fonts.ready')
            await pg.pdf(path=out, format='A4', print_background=True, display_header_footer=True, header_template='<span></span>',
                         footer_template=foot(ftxt), margin=dict(top='13mm', bottom='15mm', left='12mm', right='12mm'))
        await b.close(); shutil.rmtree(tmp, ignore_errors=True)


def protect(src, dst, password):
    import pikepdf
    owner = base64.b32encode(os.urandom(15)).decode()
    with pikepdf.open(src) as pdf:
        pdf.save(dst, encryption=pikepdf.Encryption(user=password, owner=owner, R=6,
                 allow=pikepdf.Permissions(extract=False, modify_annotation=False, modify_assembly=False, modify_form=False, modify_other=False)))


# ---------------------------------------------------------------- seal
def seal():
    code = read_code()
    if not re.fullmatch(r'BAHU-[A-Z0-9]{4}-[A-Z0-9]{4}', code): sys.exit('code must look like BAHU-XXXX-XXXX')
    old = load_series()
    salt = base64.b64decode(old['kdf']['salt']) if old.get('kdf') else os.urandom(16)
    key = derive(code, salt)
    if old.get('check'):
        try: unseal_bytes(key, base64.b64decode(old['check']))
        except Exception: sys.exit('this code does not match the one the published tests use (src/bahubali/series.json); '
                                   'delete series.json only if you really mean to change the code for every buyer')
    for d in ('data', 'pdf'):
        if os.path.isdir(os.path.join(PUB, d)): shutil.rmtree(os.path.join(PUB, d))
        os.makedirs(os.path.join(PUB, d))
    tests, samples, jobs, payloads = {}, [], [], {}
    tmp = tempfile.mkdtemp(prefix='bb-')
    for p in PAPERS:
        for n in range(1, TESTS_PER_PAPER + 1):
            T = load_test(p, n)
            if not T: continue
            body = json.dumps(T, ensure_ascii=False, separators=(',', ':')).encode()
            blob = seal_bytes(key, body)
            fn = f'data/{T["id"]}-{hashlib.sha1(body).hexdigest()[:10]}.bin'
            open(os.path.join(PUB, fn), 'wb').write(blob)
            pq, pa = pdf_names(p, n)
            tests[T['id']] = dict(data=fn, pdf_q=pq, pdf_a=pa, q=len(T['q']))
            payloads[T['id']] = T
            for kind, rel, parts in (('q', pq, booklet_html(T)), ('a', pa, answers_html(T))):
                raw = os.path.join(tmp, os.path.basename(rel))
                jobs.append((raw, doc(T, parts), f'{NAME} · {T["paper_name"]} · {T["label"]} · {"Question booklet" if kind == "q" else "Answers"} · learnwithanil.in · purchaser\'s personal use only'))
    for sid, sk in SAMPLES:
        T = payloads.get(sid)
        if not T: continue
        q = next((x for x in T['q'] if x['s'] == sk and re.search(r'^I\. ', x['q'], re.M)), None) or next(x for x in T['q'] if x['s'] == sk)
        samples.append(dict(paper=T['paper_name'], sec=next(s['sub'] for s in T['sections'] if s['k'] == sk), **{k: q[k] for k in ('n', 't', 'q', 'o', 'a', 'w')},
                            **({'qt': q['qt'], 'ot': q.get('ot')} if q.get('qt') else {})))
    if jobs:
        print(f'  rendering {len(jobs)} PDFs …')
        asyncio.run(render(jobs))
        for raw, _, _ in jobs:
            rel = next(v for t in tests.values() for v in (t['pdf_q'], t['pdf_a']) if os.path.basename(v) == os.path.basename(raw))
            protect(raw, os.path.join(PUB, rel), code)
    shutil.rmtree(tmp, ignore_errors=True)
    check = base64.b64encode(seal_bytes(key, b'bahubali-ok')).decode()
    series = dict(kdf=dict(salt=base64.b64encode(salt).decode(), iter=ITER), check=check, tests=tests, samples=samples,
                  buy=old.get('buy', ''), note='Encrypted. The question source is private (see tools/bahubali.py).')
    json.dump(series, open(os.path.join(PUB, 'series.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # keep a plain copy of every payload in the private folder for checking
    os.makedirs(os.path.join(PRIV, 'out'), exist_ok=True)
    for k, T in payloads.items():
        json.dump(T, open(os.path.join(PRIV, 'out', f'{k}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  sealed {len(tests)} tests: {", ".join(tests)}')


# ---------------------------------------------------------------- page
FAQ = [
  ('What is the Bahubali Test Series?',
   f'A paid series of full-length mock tests for the APPSC Group-II Services Main Examination by Jupudi Anil Kumar (Learn with Anil): {TESTS_PER_PAPER} tests for Paper I and {TESTS_PER_PAPER} for Paper II. '
   'Every test has 150 questions, 150 marks and 150 minutes, with one-third negative marking, exactly like the real paper.'),
  ('How much does it cost?', f'₹{PRICE} once, for all {2 * TESTS_PER_PAPER} tests of both papers. Tests added later open with the same code at no extra cost.'),
  ('Which tests are available now?', '{LIVE}'),
  ('Are these previous APPSC questions?', 'No. They are original questions written to the Group-II Mains syllabus at UPSC Prelims standard, in the styles APPSC uses. '
   'For APPSC\'s own previous papers, use the free APPSC Group 2 PYQs on this site.'),
  ('Can I write the test in Telugu?', 'Yes. Every question, option and explanation is in English and Telugu. Switch language at any time during the test or while reviewing answers.'),
  ('How is the score calculated?', 'Each correct answer gives 1 mark and each wrong answer takes away one-third of a mark; unanswered questions give 0. You also get section-wise and unit-wise scores.'),
  ('Can I use it on my phone and my computer?', 'Yes. Enter the same access code on each device. Your attempts and scores are saved in each browser.'),
  ('Are PDFs included?', 'Yes. For every live test you can download the question booklet (with an OMR sheet) and the answers-with-explanations PDF. The PDF password is your access code.'),
  ('I paid but did not get my access code.', f'The access card downloads right after payment and Instamojo also emails it. If you still cannot find it, WhatsApp {B.PHONE} with your payment ID.'),
]


def page(dist_site):
    """Write the Bahubali page into dist/site (called by build.py)."""
    S = load_series()
    outdir = os.path.join(dist_site, URLDIR)
    os.makedirs(outdir, exist_ok=True)
    for d in ('data', 'pdf'):
        src = os.path.join(PUB, d)
        if os.path.isdir(src): shutil.copytree(src, os.path.join(outdir, d), dirs_exist_ok=True)
    tests = S.get('tests', {})
    url = f'{B.SITE_URL}/{URLDIR}/'
    conf_tests = []
    papers_html = []
    for p in PAPERS:
        live = [n for n in range(1, TESTS_PER_PAPER + 1) if tid(p['id'], n) in tests]
        cards = []
        for n in range(1, TESTS_PER_PAPER + 1):
            k = tid(p['id'], n)
            if k in tests:
                t = tests[k]
                conf_tests.append(dict(id=k, paper=p['id'], paper_name=p['name'], n=n, label=label(n), q=t['q'], min=150, data=t['data'], pdf_q=t['pdf_q'], pdf_a=t['pdf_a'],
                                       sections_desc=' and '.join(f'{s[1]}: {s[2]} (Q{s[4]}–{s[5]})' for s in p['sections'])))
                cards.append(f'<article class="card test" data-test="{k}"><div class="top"><span class="no">{label(n)}</span><span class="badge live">Live</span></div>'
                             f'<p class="meta">{p["name"]} · {t["q"]} questions · 150 minutes · 150 marks</p>'
                             f'<div class="secs">' + ''.join(f'<span><b>{s[0]}</b> · {esc(s[2])} · 75</span>' for s in p['sections']) + '</div>'
                             f'<p class="score-line" hidden></p><div class="acts"><button class="btn btn-secondary" type="button" data-act="needcode">🔒 Unlock to start</button></div>'
                             f'<div class="pdfs" hidden></div></article>')
            else:
                cards.append(f'<article class="card test soon"><div class="top"><span class="no">{label(n)}</span><span class="badge soon">Upcoming</span></div>'
                             f'<p class="meta">{p["name"]} · 150 questions · 150 minutes</p></article>')
        papers_html.append(f'<div class="paper-head"><div><h3>{p["name"]}</h3><p>' + ' + '.join(f'{s[1]}: {esc(s[2])} (75)' for s in p['sections']) +
                           f'</p></div><p class="mono">{len(live)} of {TESTS_PER_PAPER} live</p></div><div class="tests">{"".join(cards)}</div>')
    nlive = len(conf_tests)
    live_desc = ' and '.join(f'{p["name"]} Grand Test' + ('s ' if sum(t['paper'] == p['id'] for t in conf_tests) > 1 else ' ') + _ranges([t['n'] for t in conf_tests if t['paper'] == p['id']]) for p in PAPERS if any(t['paper'] == p['id'] for t in conf_tests)) or 'first tests coming soon'
    buy = S.get('buy', '')
    buy_btn = (f'<a class="btn btn-gold" href="{esc(buy)}" target="_blank" rel="noopener" data-buy>Buy now · ₹{PRICE}</a>' if buy else
               f'<a class="btn btn-gold" href="https://wa.me/{B.WHATSAPP}?text={html.escape("Hi Anil, I want to buy the Bahubali Test Series (APPSC Group-II Mains).")}" target="_blank" rel="noopener">Buy on WhatsApp · ₹{PRICE}</a>')
    samples = S.get('samples', [])
    sample_html = ''
    if samples:
        items = []
        for i, q in enumerate(samples):
            te = (f'<p class="q" lang="te">{esc(q["qt"])}</p><ol lang="te">' + ''.join(f'<li>({j + 1}) {esc(o)}</li>' for j, o in enumerate(q.get("ot") or q["o"])) + '</ol>') if q.get('qt') else ''
            items.append(f'<article class="card sample"><p class="qn">Sample {i + 1} · {esc(q["paper"])} · {esc(q["sec"])} · {esc(q["t"])}</p>'
                         f'<p class="q">{esc(q["q"])}</p><ol>' + ''.join(f'<li>({j + 1}) {esc(o)}</li>' for j, o in enumerate(q["o"])) + '</ol>'
                         f'<details><summary>తెలుగులో చదవండి · Read in Telugu</summary>{te}</details>' * bool(te) +
                         f'<details><summary>Show answer and explanation</summary><p class="why"><b>Answer: ({q["a"] + 1}) {esc(q["o"][q["a"]])}</b><br>{esc(q["w"])}</p></details></article>')
        sample_html = (f'<section class="blk"><div class="wrap"><h2>Try sample questions</h2>'
                       f'<p class="lead">One question from each section of Grand Test 01, so you can see the standard before you buy.</p>{"".join(items)}</div></section>')
    live_ans = (f'{live_desc} {"is" if nlive == 1 else "are"} live now. The other tests are upcoming and are added one by one; each opens for buyers, with the same code, as soon as it is published here.'
                if nlive else 'The first tests are upcoming.')
    faq = [(q, a.replace('{LIVE}', live_ans)) for q, a in FAQ]
    faq_html = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq)
    title = 'Bahubali Test Series – APPSC Group 2 Mains Mock Tests (Paper 1 & Paper 2), Full-Length, English & Telugu | Learn with Anil'
    desc = (f'Bahubali Test Series for APPSC Group 2 Mains 2026: {2 * TESTS_PER_PAPER} full-length mock tests ({TESTS_PER_PAPER} for Paper 1, {TESTS_PER_PAPER} for Paper 2), '
            f'150 questions each, in English and Telugu, with negative marking, explanations and PDFs. ₹{PRICE} for the whole series.')
    ld = [{"@context": "https://schema.org", "@type": "Course", "name": f"{NAME} – APPSC Group-II Mains", "description": desc, "url": url,
           "inLanguage": ["en", "te"], "provider": {"@type": "Organization", "name": "Learn with Anil", "url": B.SITE_URL + '/'},
           "offers": {"@type": "Offer", "price": str(PRICE), "priceCurrency": "INR", "category": "Paid", "url": url},
           "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online", "courseWorkload": "PT150M"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    head_extra = B.ICONS + B.ga_tag() + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    conf = dict(kdf=S.get('kdf', {}), check=S.get('check', ''), tests=conf_tests, url=url)
    tpl = open(os.path.join(ROOT, 'tools', 'bahubali.html'), encoding='utf-8').read()
    rep = {'{{TITLE}}': esc(title), '{{DESC}}': esc(desc), '{{CANON}}': url, '{{SITE}}': B.SITE_URL, '{{HEAD_EXTRA}}': head_extra,
           '{{HERO_SUB}}': f'{2 * TESTS_PER_PAPER} full-length mock tests for APPSC Group-II Mains — {TESTS_PER_PAPER} for Paper I and {TESTS_PER_PAPER} for Paper II — with 150 questions in every test.',
           '{{PRICE}}': str(PRICE), '{{TOTAL_TESTS}}': str(2 * TESTS_PER_PAPER), '{{NLIVE}}': f'{nlive} test{"" if nlive == 1 else "s"}', '{{LIVE_DESC}}': esc(live_desc),
           '{{BUY_BUTTON}}': buy_btn, '{{PAPERS_HTML}}': ''.join(papers_html), '{{SAMPLE_HTML}}': sample_html, '{{FAQ_HTML}}': faq_html,
           '{{WA}}': B.WHATSAPP, '{{PHONE}}': B.PHONE, '{{EMAIL}}': B.EMAIL,
           '{{CONF}}': json.dumps(conf, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')}
    for k, v in rep.items(): tpl = tpl.replace(k, v)
    assert '{{' not in tpl, re.findall(r'\{\{\w+\}\}', tpl)
    open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8').write(tpl)
    return URLDIR + '/'


def _ranges(ns):
    ns = sorted(ns)
    if not ns: return ''
    if ns == list(range(ns[0], ns[-1] + 1)): return f'{ns[0]:02d}–{ns[-1]:02d}' if len(ns) > 1 else f'{ns[0]:02d}'
    return ', '.join(f'{n:02d}' for n in ns)


# ---------------------------------------------------------------- access card (the file Instamojo delivers)
def card():
    import pdfs as P
    code = read_code()
    url = f'{B.SITE_URL}/{URLDIR}/'
    body = f"""<div class="cover" style="height:262mm;padding:11mm 12mm">
<div class="brand">Learn with Anil · learnwithanil.in</div>
<h1><span>Bahubali</span><br>Test Series</h1><h2>APPSC Group-II Mains · Paper I &amp; Paper II</h2>
<p class="te" lang="te">బాహుబలి టెస్ట్ సిరీస్ · మీ యాక్సెస్ కార్డ్</p>
<p style="margin-top:5mm;font-size:12pt">Thank you for buying the Bahubali Test Series. This card has your access code.</p>
<div style="margin:4mm 0;border:2pt dashed #C98A00;border-radius:8pt;padding:6mm;text-align:center;background:#FFF8E6">
<div style="font:500 9pt 'IBM Plex Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:#6B4500">Your access code</div>
<div style="font:600 30pt 'IBM Plex Mono',monospace;letter-spacing:.08em;margin-top:2mm">{esc(code)}</div></div>
<p><b>How to start</b></p><ol>
<li>Open <a href="{url}">{url.replace('https://', '')}</a> on your phone or computer.</li>
<li>Type the code above in “Already bought? Enter your access code” and tap <b>Unlock</b>.</li>
<li>Choose a Grand Test and write it: 150 questions, 150 minutes, ⅓ negative marking, English and Telugu.</li>
<li>After you submit, see your score, section-wise and unit-wise analysis, and every explanation.</li>
<li>PDFs (question booklet with OMR sheet, and answers): download them from the same page. <b>PDF password: {esc(code)}</b> (type it exactly, with the hyphens).</li></ol>
<p style="margin-top:4mm"><b>What is included:</b> {TESTS_PER_PAPER} tests for Paper I and {TESTS_PER_PAPER} for Paper II. New tests open with this same code as they are added, at no extra cost.</p>
<p class="te" lang="te" style="margin-top:4mm">learnwithanil.in/{URLDIR}/ పేజీ తెరిచి, పై కోడ్ నమోదు చేసి “Unlock” నొక్కండి. అన్ని టెస్టులు ఇదే కోడ్‌తో తెరుచుకుంటాయి. PDF పాస్‌వర్డ్ కూడా ఇదే కోడ్.</p>
<p style="margin-top:4mm">This code is for your personal use. Please do not share it. Help: WhatsApp {esc(B.PHONE)} · {esc(B.EMAIL)}</p>
<div class="foot">Bahubali Test Series by Jupudi Anil Kumar, Learn with Anil. Original questions for practice; not affiliated with APPSC.</div></div>"""
    T = dict(paper_name='', label='')
    html_ = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{NAME} – Access Card</title>'
             f'<style>{P.font_css()}{PDF_CSS}</style></head><body>{body}</body></html>')
    os.makedirs(os.path.join(PRIV, 'out'), exist_ok=True)
    out = os.path.join(PRIV, 'out', 'Bahubali-Test-Series-Access-Card.pdf')
    asyncio.run(render([(out, html_, f'{NAME} · access card · learnwithanil.in')]))
    print('  wrote', out)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'seal': seal()
    elif cmd == 'card': card()
    else: sys.exit(__doc__)
