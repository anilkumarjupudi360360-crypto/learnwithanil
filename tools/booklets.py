#!/usr/bin/env python3
"""Exam-booklet PDFs of the previous papers, for PYQ Pass holders only (Anil, 27 Oct 2026).

Each paper is typeset like the board's own question booklet: a header box (board, exam, date, booklet series, time,
questions, marks), questions in two columns (English, then Telugu/Hindi as printed), the Learn with Anil logo,
a faint logo watermark on every page and "Learn with Anil · learnwithanil.in" with the page number in the footer.
The official answer key and the answers with explanations follow the questions.

The PDFs are paid content: they are written to the private folder BOOKS_PRIV/booklets (never committed), then
encrypted exactly like the study books (AES-256-GCM, additional data = key id "bk-<exam id>-<paper id>") into
src/books/. The keys go in the private sheet's keys tab; the payments script gives a key only to a valid PYQ Pass.

    python3 tools/booklets.py [exam id ...]     # default: ts-police-si ts-police-constable
Writes src/books/booklets.json (exam -> paper -> file, download name, pages) and BOOKS_PRIV/booklet-keys-tab.tsv.
"""
import asyncio, base64, datetime, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('SITE_URL', 'https://learnwithanil.in')
import build as B  # noqa: E402
import pdfs as P  # noqa: E402

ROOT = B.ROOT
PRIV = os.environ.get('BOOKS_PRIV', '/home/claude/lwa-books/paid')
OUTDIR = os.path.join(PRIV, 'booklets')
SEALED = os.path.join(ROOT, 'src', 'books')
DEFAULT = ['ts-police-si', 'ts-police-constable']
esc = B.esc
LOGO = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(ROOT, 'src', 'static', 'icon-192.png'), 'rb').read()).decode()
BOARD_NAME = {'TSLPRB': 'TELANGANA STATE LEVEL POLICE RECRUITMENT BOARD', 'APPSC': 'ANDHRA PRADESH PUBLIC SERVICE COMMISSION'}
# booklet series of the papers transcribed from a known booklet (others show the Learn with Anil box)
SERIES = {'appsc-group-2': {'s2024': 'A', 'm2025p1': 'A', 'm2025p2': 'A'}, 'appsc-group-1': {'p2024a': 'A', 'p2024b': 'A'}}
# released mocks with a booklet: exam -> [(mock id, pack, mock name)]; their keys are in BOOKS_PRIV/mock-keys.json
MOCKS = {'ts-police-si': [('mk-si-1', 'Mission Khaki', 'Mock 1')], 'ts-police-constable': [('mk-pc-1', 'Mission Khaki – Constable', 'Mock 1')]}


def time_marks(conf, p):
    """(time allowed, maximum marks) as printed on the board's booklet."""
    if conf['board'] == 'TSLPRB': return '3 Hours', 200
    if conf['id'] == 'appsc-group-1': return '120 Minutes', 120   # each Prelims paper: 120 questions, 120 marks
    if conf['id'] == 'appsc-group-2': return '150 Minutes', 150   # Screening and each Mains paper: 150 questions, 150 marks
    return (f'{p["mins"]} Minutes' if p.get('mins') else ''), ''

CSS = """
*{box-sizing:border-box}
html,body{margin:0}
body{font:9.6pt/1.38 'Source Sans 3',sans-serif;color:#111}
[lang=te]{font-family:'Noto Sans Telugu','Source Sans 3',sans-serif;line-height:1.5}
[lang=hi]{font-family:'Noto Sans Devanagari','Source Sans 3',sans-serif;line-height:1.5}
.wm{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:0}
.wm div{transform:rotate(-35deg);text-align:center;opacity:.07}
.wm img{width:62mm;height:62mm;border-radius:50%;display:block;margin:0 auto 4mm}
.wm b{font:800 30pt Archivo,sans-serif;color:#1846C7;white-space:nowrap}
.hd{position:relative;z-index:1;display:grid;grid-template-columns:auto 1fr auto;gap:4mm;align-items:center;border:1.2pt solid #111;padding:2.5mm 3mm}
.hd img{width:13mm;height:13mm;border-radius:50%}
.hd .t{text-align:center}
.hd .t b{display:block;font:800 11.5pt/1.15 Archivo,sans-serif}
.hd .t span{display:block;font-size:9.6pt;font-weight:700;margin-top:.6mm}
.hd .t i{display:block;font-style:normal;font-size:8.6pt}
.hd .s{border:1.2pt solid #111;text-align:center;padding:1mm 2.5mm;font:600 8pt 'Source Sans 3',sans-serif}
.hd .s b{display:block;font:800 18pt/1 Archivo,sans-serif}
.hd .s.lwa{font-size:7pt;line-height:1.2;padding:1.5mm 2mm}
.meta{position:relative;z-index:1;display:flex;justify-content:space-between;font-weight:700;font-size:9pt;border:1.2pt solid #111;border-top:0;padding:1.4mm 3mm}
.note{position:relative;z-index:1;font-size:8.4pt;margin:2mm 0 2.5mm;padding:1.6mm 3mm;border:.6pt dashed #777}
.cols{position:relative;z-index:1;column-count:2;column-gap:7mm;column-rule:.6pt solid #999}
.q{break-inside:avoid;margin:0 0 2.6mm}
.q .en{font-weight:600}
.q .n{font-weight:800;margin-right:1.2mm}
.q .ml{display:grid;grid-template-columns:1fr 1fr;gap:0 3mm}
.q ol{list-style:none;margin:.6mm 0 0;padding-left:5mm;display:grid;grid-template-columns:1fr 1fr;gap:0 3mm}
.q ol.long{grid-template-columns:1fr}
.q .l2{margin-top:.8mm;color:#222}
.q img{display:block;max-width:100%;max-height:70mm;margin:1mm 0;object-fit:contain}
h2{position:relative;z-index:1;font:800 13pt Archivo,sans-serif;margin:0 0 3mm;padding-bottom:1.5mm;border-bottom:1.2pt solid #111;break-after:avoid}
.pb{break-before:page}
.key{position:relative;z-index:1;display:grid;grid-template-columns:repeat(8,1fr);gap:1.2mm 2mm;font:500 8.6pt 'IBM Plex Mono',monospace;margin-bottom:6mm}
.key span{border:.5pt solid #bbb;border-radius:2pt;padding:.6mm 1mm;text-align:center}
.ans{break-inside:avoid;margin:0 0 2.4mm;font-size:8.8pt}
.ans .why{margin:.5mm 0 0;color:#222}
.end{position:relative;z-index:1;margin-top:4mm;font-size:8.4pt;border-top:.6pt solid #777;padding-top:2mm}
"""


def text(t):
    """One line per statement; 'a. X    I. Y' match-list lines as two aligned columns."""
    out = []
    for ln in str(t).split('\n'):
        m = re.match(r'^(.+?)\s{2,}(.+)$', ln)
        out.append(f'<div class="ml"><span>{esc(m.group(1))}</span><span>{esc(m.group(2))}</span></div>' if m else f'<div>{esc(ln)}</div>')
    return ''.join(out)


def opts(o):
    return (f'<ol class="{"long" if any(len(x) > 28 for x in o) else ""}">'
            + ''.join(f'<li>({i + 1}) {esc(x)}</li>' for i, x in enumerate(o)) + '</ol>')


def q_html(q, l2):
    first = text(q['q']).replace('<div>', '<span>', 1).replace('</div>', '</span>', 1)
    img = f'<img src="{q["img"]}" alt="">' if q.get('img') else ''
    two = (f'<div class="l2" lang="{l2}">{text(q["qt"])}{opts(q["ot"]) if q.get("ot") else ""}</div>') if q.get('qt') else ''
    return f'<div class="q"><div class="en"><span class="n">{q["n"]}.</span>{first}</div>{img}{opts(q["o"]) if q.get("o") else ""}{two}</div>'


def ans_html(q, l2):
    ans = ' / '.join(f'({i + 1}) {q["o"][i]}' for i in q['a'])
    ans2 = ' / '.join(f'({i + 1}) {q["ot"][i]}' for i in q['a']) if q.get('ot') else ''
    two = f' <span lang="{l2}">· {esc(ans2)}</span>' if ans2 else ''
    wt = f'<p class="why" lang="{l2}">{esc(q["wt"])}</p>' if q.get('wt') else ''
    return f'<div class="ans"><b>{q["n"]}. {esc(ans)}</b>{two}<p class="why">{esc(q.get("w", ""))}</p>{wt}</div>'


def paper_doc(conf, p, qs, mock=None):
    l2 = conf['l2']
    board = BOARD_NAME.get(conf['board'], conf['board'])
    time_allowed, marks = time_marks(conf, p)
    m = re.search(r'booklet ([A-Z])\b', p.get('notif', '')) or (re.match(r'([A-Z])$', SERIES.get(conf['id'], {}).get(p['id'], '')))
    series = (f'<div class="s">BOOKLET<b>{m.group(1)}</b>SERIES</div>' if m else '<div class="s lwa">LEARN<br>WITH<br>ANIL</div>')
    sub = re.sub(r'\s*·\s*booklet [A-Z]\b.*$', '', p.get('notif', ''))
    key = p.get('key') or ("APPSC's final key" if conf['board'] == 'APPSC' else conf.get('keyname') or 'the official key')
    title = re.sub(r'^(TSLPRB|APPSC|UPSC|TGPSC|TSPSC|SSC)\s+', '', p['title'])
    l2name = l2['name'] if not p.get('en_only') and any(q.get('qt') for q in qs) else ''
    when = f' · Held on {esc(p["held"])}' if p.get('held') else ''
    if mock: board = 'LEARN WITH ANIL · ' + mock.upper() + ' TEST SERIES'
    head = (f'<div class="hd"><img src="{LOGO}" alt="Learn with Anil"><div class="t"><b>{esc(board)}</b><span>{esc(title)}</span>'
            f'<i>{esc(sub)}{when}</i></div>{series}</div>'
            f'<div class="meta"><span>{"Time Allowed: " + esc(time_allowed) if time_allowed else ""}</span><span>Questions in this booklet: {len(qs)}</span>'
            f'<span>{"Maximum Marks: " + str(marks) if marks else ""}</span></div>'
            + (f'<div class="note">New questions written by Learn with Anil for the {esc(mock)} test series in the {esc(conf["board"])} pattern (not previous-year questions), '
               'with an explanation for every answer. The answer key and answers with explanations are at the end of this booklet.</div>' if mock else
               f'<div class="note">Questions as printed in {esc(conf["board"])}\'s official booklet (English'
               + (f' &amp; <span lang="{l2["code"]}">{esc(l2["label"])}</span>' if l2name and l2.get('label') else (f' &amp; {esc(l2name)}' if l2name else ''))
               + f'); answers from {esc(key)}. Questions deleted by {esc(conf["board"])} are left out. '
               + (f'{esc(conf["board"])}\'s key for this paper printed only the correct answer and the original options were never published, '
                  'so in every question the other three options are written by Learn with Anil (the correct answer is always APPSC\'s). ' if p.get('own') else '')
               + 'The answer key and answers with explanations are at the end of this booklet.</div>'))
    mcq = [q for q in qs if q.get('o')]
    body = ''.join(q_html(q, l2['code']) for q in qs)
    keygrid = ''.join(f'<span>{q["n"]}-({",".join(str(i + 1) for i in q["a"])})</span>' for q in mcq)
    answers = ''.join(ans_html(q, l2['code']) for q in mcq)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(p["kw"] if p.get("kw") else p["title"])} | Learn with Anil</title>'
            f'<meta name="author" content="Jupudi Anil Kumar, Learn with Anil"><style>{P.font_css()}{CSS}</style></head><body>'
            f'<div class="wm"><div><img src="{LOGO}" alt=""><b>learnwithanil.in</b></div></div>'
            f'{head}<div class="cols">{body}</div>'
            f'<h2 class="pb">Answer key ({esc(key)})</h2><div class="key">{keygrid}</div>'
            f'<h2>Answers with explanations</h2><div class="cols">{answers}</div>'
            f'<div class="end">Explanations by Jupudi Anil Kumar, Learn with Anil (learnwithanil.in). Not affiliated with {esc(conf["board"])}. '
            'For your personal study.</div></body></html>')


FOOTER = ('<div style="width:100%;font:7.6px \'Source Sans 3\',sans-serif;color:#333;padding:0 12mm;display:flex;justify-content:space-between;align-items:center">'
          '<span><b>Learn with Anil</b> · learnwithanil.in</span><span style="font:800 10px sans-serif;color:#111" class="pageNumber"></span></div>')


async def render(jobs):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        for out, doc in jobs:
            f = out[:-4] + '.html'
            open(f, 'w', encoding='utf-8').write(doc)
            await pg.goto('file://' + f); await pg.evaluate('document.fonts.ready')
            await pg.pdf(path=out, format='A4', print_background=True, display_header_footer=True,
                         header_template='<span></span>', footer_template=FOOTER,
                         margin=dict(top='11mm', bottom='13mm', left='12mm', right='12mm'))
            os.remove(f)
        await b.close()


def main(exams):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import pikepdf
    os.makedirs(OUTDIR, exist_ok=True); os.makedirs(SEALED, exist_ok=True)
    kpath = os.path.join(PRIV, 'keys.json')
    keys = json.load(open(kpath)) if os.path.exists(kpath) else {}
    mpath = os.path.join(SEALED, 'booklets.json')
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    confs = {c['id']: c for c in B.exam_confs()}
    jobs, todo = [], []
    mkeys = json.load(open(os.path.join(PRIV, 'mock-keys.json'))) if os.path.exists(os.path.join(PRIV, 'mock-keys.json')) else {}
    for eid in exams:
        conf = confs[eid]
        papers, qs = B.load_exam(conf)[:2]
        for p in papers:
            pq = [q for q in qs if q['p'] == p['id']]
            if not pq: continue
            out = os.path.join(OUTDIR, f'{eid}-{p["id"]}.pdf')
            doc = paper_doc(conf, p, pq)
            jobs.append((out, doc))
            todo.append((eid, conf, p, out, hashlib.sha256(doc.encode()).hexdigest()[:10]))
        for mid, pack, mname in MOCKS.get(eid, []):   # released Mission Khaki mocks: decrypt the sealed file with its private key
            import glob
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _A
            f = sorted(glob.glob(os.path.join(ROOT, 'docs', conf['dir'], 'mk', f'{mid}-*.bin')))
            if not f or mid not in mkeys: print('  no sealed file or key for', mid); continue
            raw = open(f[-1], 'rb').read()
            mq = json.loads(_A(base64.b64decode(mkeys[mid])).decrypt(raw[:12], raw[12:], mid.encode()))['questions']
            mk = B.MOCK_PACKS[eid]
            p = dict(id=mid.replace('-', ''), mock=mid, title=f'{mk["title"].split(":")[-1].split("–")[-1].strip()} · {mname}', notif=f'{pack} · {mname}', held='',
                     kw=f'{pack} {mname}', key='Learn with Anil')
            p['title'] = f'{conf["seo"]} Prelims 2026 · {mname}'
            out = os.path.join(OUTDIR, f'{eid}-{p["id"]}.pdf')
            doc = paper_doc(conf, p, mq, mock=pack)
            jobs.append((out, doc))
            todo.append((eid, conf, p, out, hashlib.sha256(doc.encode()).hexdigest()[:10]))
    asyncio.run(render(jobs))
    rows, today = [], datetime.date.today().isoformat()
    for eid, conf, p, out, dhash in todo:   # file name from the booklet's content, so an unchanged booklet keeps its name (and its keys-tab row)
        pdf = open(out, 'rb').read()
        pages = len(pikepdf.open(out).pages)
        kid = f'bk-{eid}-{p["id"]}'
        if kid not in keys: keys[kid] = base64.b64encode(os.urandom(32)).decode()
        name = f'{eid}-{p["id"]}-{dhash}.bin'
        if not os.path.exists(os.path.join(SEALED, name)):
            for f in os.listdir(SEALED):
                if f.startswith(f'{eid}-{p["id"]}-') and f.endswith('.bin'): os.remove(os.path.join(SEALED, f))
            iv = os.urandom(12)
            open(os.path.join(SEALED, name), 'wb').write(iv + AESGCM(base64.b64decode(keys[kid])).encrypt(iv, pdf, kid.encode()))
        dl = re.sub(r'[^A-Za-z0-9]+', '-', f'LearnWithAnil {p.get("kw") or p["title"]} {"Mock Test" if p.get("key") == "Learn with Anil" else "Question Paper"}').strip('-') + '.pdf'
        manifest.setdefault(eid, {})[p['id']] = dict(key=kid, file=name, name=dl, pages=pages, bytes=len(pdf), **({'mock': p['mock']} if p.get('mock') else {}))
        rows.append('\t'.join([kid, keys[kid], name, today]))
        print(f'  {kid}: {pages} pages, {len(pdf) // 1024} KB -> src/books/{name}')
    json.dump(keys, open(kpath, 'w'), indent=1)
    json.dump(manifest, open(mpath, 'w'), indent=1, sort_keys=True)
    open(os.path.join(PRIV, 'booklet-keys-tab.tsv'), 'w').write('\n'.join(rows) + '\n')
    print(f'{len(rows)} booklets; keys-tab rows in {PRIV}/booklet-keys-tab.tsv')


if __name__ == '__main__':
    main(sys.argv[1:] or DEFAULT)
