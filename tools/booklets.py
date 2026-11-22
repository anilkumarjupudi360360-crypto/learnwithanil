#!/usr/bin/env python3
"""Exam-booklet PDFs of the previous papers, for All-in-One Pass holders only (Anil, 27 Oct 2026).

Each paper is typeset like the board's own question booklet: a header box (board, exam, date, booklet series, time,
questions, marks), questions in two columns (English, then Telugu/Hindi as printed), the Learn with Anil logo,
a faint logo watermark on every page and "Learn with Anil · learnwithanil.in" with the page number in the footer.
The official answer key and the answers with explanations follow the questions.

The PDFs are paid content: they are written to the private folder BOOKS_PRIV/booklets (never committed), then
encrypted exactly like the study books (AES-256-GCM, additional data = key id "bk-<exam id>-<paper id>") into
src/books/. The keys go in the private sheet's keys tab; the payments script gives a key only to a valid All-in-One Pass.

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
BOARD_NAME = {'TSLPRB': 'TELANGANA STATE LEVEL POLICE RECRUITMENT BOARD', 'APPSC': 'ANDHRA PRADESH PUBLIC SERVICE COMMISSION',
              'SLPRB': 'STATE LEVEL POLICE RECRUITMENT BOARD, ANDHRA PRADESH', 'RRB': 'RAILWAY RECRUITMENT BOARDS · RAILWAY PROTECTION FORCE',
              'AP DSC': 'COMMISSIONERATE OF SCHOOL EDUCATION, GOVERNMENT OF ANDHRA PRADESH', 'TNPSC': 'TAMIL NADU PUBLIC SERVICE COMMISSION',
              'KEA': 'KARNATAKA EXAMINATIONS AUTHORITY', 'MPSC': 'MAHARASHTRA PUBLIC SERVICE COMMISSION', 'GSSSB': 'GUJARAT SUBORDINATE SERVICE SELECTION BOARD',
              'UPSSSC': 'UTTAR PRADESH SUBORDINATE SERVICES SELECTION COMMISSION', 'UPPSC': 'UTTAR PRADESH PUBLIC SERVICE COMMISSION',
              'UKPSC': 'UTTARAKHAND PUBLIC SERVICE COMMISSION', 'CG Vyapam': 'CHHATTISGARH VYAPAM (CHHATTISGARH KARMCHARI CHAYAN MANDAL)',
              'OPSC': 'ODISHA PUBLIC SERVICE COMMISSION', 'WBPSC': 'PUBLIC SERVICE COMMISSION, WEST BENGAL', 'DSSSB': 'DELHI SUBORDINATE SERVICES SELECTION BOARD', 'JKSSB': 'JAMMU & KASHMIR SERVICES SELECTION BOARD', 'Meghalaya PSC': 'MEGHALAYA PUBLIC SERVICE COMMISSION',
              'Karnataka School Education': 'DEPARTMENT OF SCHOOL EDUCATION, GOVERNMENT OF KARNATAKA'}
BOARD_NAME_EXAM = {'rrb-group-d': 'RAILWAY RECRUITMENT BOARDS'}   # an exam whose board line differs from its board's (RRB: RPF papers also use 'RRB')
# booklet series of the papers transcribed from a known booklet (others show the Learn with Anil box)
SERIES = {'ap-police-si': {'a2023s1': 'A', 'a2023s2': 'C'}, 'ap-police-constable': {'a2023pc': 'A'}, 'appsc-group-2': {'s2024': 'A', 'm2025p1': 'A', 'm2025p2': 'A'}, 'appsc-group-1': {'p2024a': 'A', 'p2024b': 'A'},
          'appsc-eo': {'e2025a': 'A', 'e2025b': 'A'}, 'tnpsc-group-4': {'t24': 'A', 't22': 'A'},
          'karnataka-fda-sda': {'f11g': 'A1', 'f11k': 'A1', 's25g': 'B1', 's25k': 'A1', 'k22g': 'A1', 'k22k': 'A1'}, 'karnataka-gpstr': {'g22g': '1A'}}
# Papers whose PDF is the board's ORIGINAL booklet, not a typeset one (Anil, 16 Nov 2026: "no need to upload like this... upload the original ones...
# just add our brand (at bottom of every page or something like that) on the original and upload... no need to use more energy for making new pdfs").
# exam -> paper -> (question booklet, official key) under BOOKS_PRIV/originals/<exam>/ (never committed); brand_original() adds a Learn with Anil
# footer strip under every page (the page itself is untouched) and appends the official answer key pages.
ORIGINALS = {'mpsc-group-c': {pid: (f'{pid}-qp.pdf', f'{pid}-key.pdf') for pid in ('g25', 'g24', 'g23')},
             'gsssb-cce': {pid: (f'{pid}-qp.pdf',) for pid in ('c01', 'c02', 'c71')},
             'uppsc-ro-aro': {'r25': ('r25-qp.pdf',)},   # UPPSC's own booklet with its key boxed; the 2021 papers are candidates' scans, so typeset (GSSSB's paper preview marks the final answers)
             'ukpsc-lower-pcs': {pid: (f'{pid}-qp.pdf', f'{pid}-key.pdf') for pid in ('l24', 'l21', 'r23')},   # UKPSC's own clean booklets + final keys
             'cg-vyapam-group-2': {pid: (f'{pid}-qp.pdf', f'{pid}-key.pdf') for pid in ('vd', 'ag', 'sg')},
             'opsc-aso': {pid: (f'{pid}-qp.pdf', f'{pid}-key.pdf') for pid in ('a1', 'a2', 'a3', 's1', 's2', 's3')},
             'wbpsc-ido': {pid: (f'{pid}-qp.pdf', f'{pid}-key.pdf') for pid in ('i19', 'm23')},
             'dsssb': {pid: (f'{pid}-qp.pdf',) for pid in ('j22', 'p22')},
             'jkssb-je-civil': {pid: (f'{pid}-qp.pdf', f'{pid}-key.pdf') for pid in ('c25', 'c23')},   # JKSSB's Series A booklets + provisional key and final key notice
             'meghalaya-psc': {pid: (f'{pid}-qp.pdf', f'{pid}-key.pdf') for pid in ('c1', 'c2', 'l25')}}   # MPSC's Series I booklets + its answer keys   # DSSSB's own question papers with answers (green ticks), from its Question Bank   # WBPSC's own booklets (m23 pages 18, 20 turned upright) + its keys   # OPSC's own scans + its keys (key pages of that paper)   # Vyapam's own booklets + final keys
# Every released mock of every test series gets a booklet (Anil, 22 Nov 2026: "mocks uploaded should have pdf to get downloaded").
# The list comes from build.MOCK_PACKS (live mocks only); the private keys of the sealed mocks are in BOOKS_PRIV/mock-keys.json.
MOCK_NOTE = {   # series not made of new questions only: what the booklet's note says instead
    'appsc-eo': 'Built from real APPSC questions (EO Grade-III, AMVI and other APPSC papers) with APPSC\'s official answers, mixed in the proportions APPSC asks',
    'appsc-group-2': 'History, Geography and Mental Ability are real questions from APPSC\'s other papers with the official answers; Indian Society and Current Affairs are new questions written by Learn with Anil',
}


def released_mocks(eid):
    """[(mock id, series name, mock name, minutes, questions)] for the live mocks of an exam's test series."""
    mk = B.MOCK_PACKS.get(eid)
    if not mk: return []
    if 'mocks' in mk:
        return [(m['id'], mk['name'], m['name'], m.get('mins'), m.get('qn')) for m in mk['mocks'] if m.get('live')]
    return [(f'{mk["id"]}-{i}', mk['name'], f'Mock {i}', 180, mk.get('qn')) for i in range(1, mk.get('live', 0) + 1)]   # Mission Khaki (SI): n / live counts


def mock_pid(mid):
    """Paper id of a mock's booklet: 'mk-si-1' -> 'mksi1' (as before), 'bk-dscmk-sgt-2' -> 'dscmksgt2'."""
    return (mid[3:] if mid.startswith('bk-') else mid).replace('-', '')


def sealed_mock(mid):
    """Path of a mock's sealed file in src/ (any series folder), or None."""
    import glob
    hits = [f for f in glob.glob(os.path.join(ROOT, 'src', '*', f'{mid}-*.bin'))
            if re.fullmatch(re.escape(mid) + r'-[0-9a-f]{8,12}\.bin', os.path.basename(f)) and os.sep + 'books' + os.sep not in f]
    return sorted(hits)[-1] if hits else None


def inline_img(q):
    """A figure question's site path (/exam/mk/x.png) as a data: URI, so the booklet prints the figure."""
    import glob, mimetypes
    src = q.get('img')
    if not src or src.startswith('data:'): return q
    hits = glob.glob(os.path.join(ROOT, 'src', '*', os.path.basename(src))) or glob.glob(os.path.join(ROOT, 'src', '**', os.path.basename(src)), recursive=True)
    if not hits: return q
    mime = mimetypes.guess_type(hits[0])[0] or 'image/png'
    return dict(q, img=f'data:{mime};base64,' + base64.b64encode(open(hits[0], 'rb').read()).decode())


def share_passages(qs):
    """Mock booklets: when consecutive questions repeat the same passage (the app shows it with every question), print it with the
    first one only and point the others to it. Long questions may break across a column (no near-empty first page)."""
    out, prev, first = [], None, None
    for q in qs:
        q = dict(q)
        lines = str(q['q']).split('\n')
        if prev is not None:
            i = 0
            while i < min(len(lines), len(prev)) - 1 and lines[i] == prev[i]: i += 1
            if sum(len(x) for x in lines[:i]) > 300:
                same_t = q.get('qt') == q['q']
                q['q'] = f'(Read the passage given with Q.{first}.)\n' + '\n'.join(lines[i:])
                if same_t: q['qt'] = q['q']
                elif q.get('qt'):
                    lt, pt = str(q['qt']).split('\n'), prevt
                    j = 0
                    while pt and j < min(len(lt), len(pt)) - 1 and lt[j] == pt[j]: j += 1
                    if j: q['qt'] = '\n'.join(lt[j:])
                out.append(q); continue
        prev, prevt, first = lines, (str(q.get('qt')).split('\n') if q.get('qt') else None), q['n']
        if len(q['q']) > 900: q['long'] = 1
        out.append(q)
    return out


def time_marks(conf, p):
    """(time allowed, maximum marks) as printed on the board's booklet."""
    if p.get('mock') and conf['board'] != 'TSLPRB':
        mins = p.get('mins') or 0
        return (f'{mins} Minutes' if mins else ''), ''
    if conf['board'] == 'TSLPRB': return '3 Hours', 200
    if conf['board'] == 'RRB': return '90 Minutes', 120   # RPF SI / Constable CBT: 120 questions, 1 mark each
    if conf['board'] == 'SLPRB': return '3 Hours', (100 if conf['id'] == 'ap-police-si' else 200)   # AP SI prelims: two papers of 100; AP PC prelims: 200
    if conf['id'] == 'appsc-group-1': return '120 Minutes', 120   # each Prelims paper: 120 questions, 120 marks
    if conf['id'] == 'appsc-group-2': return '150 Minutes', 150   # Screening and each Mains paper: 150 questions, 150 marks
    if conf['id'] == 'appsc-eo': return '150 Minutes', 150   # EO Grade-III: each paper 150 questions, 150 marks
    if conf['id'] == 'appsc-analyst': return '150 Minutes', (150 if p['id'] == 'n2025a' else 300)   # Analyst 2025: Paper I 1 mark, Paper II 2 marks a question
    if conf['id'] == 'appsc-env-engineer': return '150 Minutes', (300 if p['id'] == 'v25c' else 150)   # AEE 2025: Paper II 2 marks a question, Paper I 1 mark
    if conf['id'] == 'appsc-aso': return '150 Minutes', 150   # ASO Paper II: 150 questions, 150 marks
    if conf['id'] == 'ap-dsc': return (('180 Minutes', 100) if p.get('mins') == 180 else ('150 Minutes', 80))   # DSC: 160 Q / 80 marks; SA PE and PET 200 Q / 100 marks
    if conf['id'] in ('tgpsc-group-1', 'tgpsc-group-2'): return '150 Minutes', 150   # TG Group-I Prelims and each Group-II paper: 150 questions, 150 marks
    if conf['id'] == 'appsc-fro': return '150 Minutes', 150   # FRO Screening and each Mains paper: 150 questions, 150 marks
    if conf['id'] == 'rrb-group-d': return '90 Minutes', 100   # RRB Group D CBT: 100 questions, 1 mark each
    if conf['id'] == 'tnpsc-group-4': return '3 Hours', 300   # TNPSC Group 4: 200 questions (Part A 150 marks, Parts B-C 150 marks)
    if conf['id'] == 'karnataka-gpstr': return '2 Hours 30 Minutes', 150   # GPSTR 2022 Paper-1: 150 questions, 150 marks
    if conf['id'] == 'karnataka-fda-sda': return '2 Hours', 100   # KEA FDA/SDA: each paper 100 questions, 100 marks, 2 hours
    if conf['id'] == 'mpsc-group-c': return '1 Hour', 100   # MPSC Group-C prelims: 100 questions, 100 marks, 1 hour
    if conf['id'] == 'upsssc-inter-level': return '2 Hours', 100   # UPSSSC Mains: 100 questions, 100 marks, 2 hours
    if conf['id'] == 'opsc-aso': return (('2 Hours', 200) if p['id'] in ('a3', 's3') else ('1 Hour 30 Minutes', 100))   # OPSC ASO papers
    if conf['id'] == 'jkssb-je-civil': return '120 Minutes', 120   # JKSSB JE (Civil): 120 questions, 1 mark each
    if conf['id'] == 'meghalaya-psc': return (('2 Hours 30 Minutes', 300) if p['id'] == 'l25' else ('2 Hours', 200))   # MPSC: MCS Prelims papers 100 x 2 marks; LDA 150 x 2 marks
    if conf['id'] == 'dsssb': return '120 Minutes', 200   # DSSSB one-tier tests: 200 questions, 1 mark each
    if conf['id'] == 'wbpsc-ido': return ('1 Hour 30 Minutes', 200 if p['id'] == 'm23' else 100)   # WBPSC: IDO 100 marks; Miscellaneous 100 questions x 2 marks
    if conf['id'] == 'ukpsc-lower-pcs': return '2 Hours', 150   # UKPSC prelims: 150 questions, 150 marks
    if conf['id'] == 'cg-vyapam-group-2': return {'vd': ('3 Hours', 200), 'ag': ('3 Hours', 200), 'sg': ('2 Hours 30 Minutes', 150)}[p['id']]   # Vyapam 2021 papers
    if conf['id'] == 'uppsc-ro-aro': return {'r25': ('3 Hours', 200), 'g21': ('2 Hours', 140), 'h21': ('1 Hour', 60)}[p['id']]   # RO/ARO prelims
    if conf['id'] == 'ssc-mts': return '90 Minutes (two sessions of 45)', 270   # MTS: 90 questions, 3 marks each
    return (f'{p["mins"]} Minutes' if p.get('mins') else ''), ''

CSS = """
*{box-sizing:border-box}
html,body{margin:0}
body{font:9.6pt/1.38 'Source Sans 3',sans-serif;color:#111}
[lang=te]{font-family:'Noto Sans Telugu','Source Sans 3',sans-serif;line-height:1.5}
[lang=ta]{font-family:'Noto Sans Tamil','Source Sans 3',sans-serif;line-height:1.5}
[lang=kn]{font-family:'Noto Sans Kannada','Source Sans 3',sans-serif;line-height:1.55}
[lang=mr]{font-family:'Noto Sans Devanagari','Source Sans 3',sans-serif;line-height:1.5}
[lang=gu]{font-family:'Noto Sans Gujarati','Source Sans 3',sans-serif;line-height:1.5}
[lang=or]{font-family:'Noto Sans Oriya','Source Sans 3',sans-serif;line-height:1.5}
[lang=bn]{font-family:'Noto Sans Bengali','Source Sans 3',sans-serif;line-height:1.5}
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
.q.long{break-inside:auto}
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


def script_lang(t):
    """'te' / 'hi' when a question has no English and is printed in Telugu / Hindi only (AP DSC language papers), else ''."""
    if re.search(r'[A-Za-z]{3,}', t or ''): return ''
    return ('te' if re.search(r'[\u0C00-\u0C7F]', t or '') else 'hi' if re.search(r'[\u0900-\u097F]', t or '')
            else 'ta' if re.search(r'[\u0B80-\u0BFF]', t or '') else 'kn' if re.search(r'[\u0C80-\u0CFF]', t or '') else 'gu' if re.search(r'[\u0A80-\u0AFF]', t or '') else 'or' if re.search(r'[\u0B00-\u0B7F]', t or '') else 'bn' if re.search(r'[\u0980-\u09FF]', t or '') else '')   # TNPSC Group 4 Part A is in Tamil only; KEA Paper-2 General Kannada in Kannada only


def q_html(q, l2):
    first = text(q['q']).replace('<div>', '<span>', 1).replace('</div>', '</span>', 1)
    img = f'<img src="{q["img"]}" alt="">' if q.get('img') else ''
    same = q.get('qt') == q['q']   # a Telugu-only question carries the same text in both fields: print it once
    two = (f'<div class="l2" lang="{l2}">{text(q["qt"])}{opts(q["ot"]) if q.get("ot") else ""}</div>') if q.get('qt') and not same else ''
    sl = script_lang(q['q'])
    return (f'<div class="q{" long" if q.get("long") else ""}"><div class="en"{f' lang="{sl}"' if sl else ""}><span class="n">{q["n"]}.</span>{first}</div>{img}'
            f'{f'<div lang="{sl}">' if sl else ""}{opts(q["o"]) if q.get("o") else ""}{"</div>" if sl else ""}{two}</div>')


def ans_html(q, l2):
    ans = ' / '.join(f'({i + 1}) {q["o"][i]}' for i in q['a'])
    ans2 = ' / '.join(f'({i + 1}) {q["ot"][i]}' for i in q['a']) if q.get('ot') and q.get('ot') != q.get('o') else ''
    two = f' <span lang="{l2}">· {esc(ans2)}</span>' if ans2 else ''
    sl = script_lang(q['q'])
    if sl: ans = f'<span lang="{sl}">{esc(ans)}</span>'
    else: ans = esc(ans)
    wt = f'<p class="why" lang="{l2}">{esc(q["wt"])}</p>' if q.get('wt') else ''
    return f'<div class="ans"><b>{q["n"]}. {ans}</b>{two}<p class="why">{esc(q.get("w", ""))}</p>{wt}</div>'


def paper_doc(conf, p, qs, mock=None):
    l2 = conf['l2']
    board = BOARD_NAME_EXAM.get(conf['id']) or BOARD_NAME.get(conf['board'], conf['board'])
    time_allowed, marks = time_marks(conf, p)
    m = re.search(r'booklet ([A-Z])\b', p.get('notif', '')) or (re.match(r'([A-Z]\d?)$', SERIES.get(conf['id'], {}).get(p['id'], '')))
    series = ((f'<div class="s">VERSION<b>{m.group(1)}</b>CODE</div>' if len(m.group(1)) > 1 else f'<div class="s">BOOKLET<b>{m.group(1)}</b>SERIES</div>')   # KEA booklets carry a version code (A1, B1 ...)
              if m else '<div class="s lwa">LEARN<br>WITH<br>ANIL</div>')
    sub = re.sub(r'\s*·\s*booklet [A-Z]\b.*$', '', p.get('notif', ''))
    key = p.get('key') or ("APPSC's final key" if conf['board'] == 'APPSC' else conf.get('keyname') or 'the official key')
    title = re.sub(r'^(TSLPRB|APPSC|UPSC|TGPSC|TSPSC|SSC|SLPRB AP|RRB|TNPSC|KEA|MPSC|GSSSB|UPSSSC|UPPSC|UKPSC|CG Vyapam|OPSC|WBPSC|DSSSB|JKSSB|Meghalaya PSC)\s+', '', p['title'])
    l2name = l2['name'] if not p.get('en_only') and any(q.get('qt') for q in qs) else ''
    when = f' · Held on {esc(p["held"])}' if p.get('held') else ''
    if mock: board = 'LEARN WITH ANIL · ' + mock.upper() + ' TEST SERIES'
    head = (f'<div class="hd"><img src="{LOGO}" alt="Learn with Anil"><div class="t"><b>{esc(board)}</b><span>{esc(title)}</span>'
            f'<i>{esc(sub)}{when}</i></div>{series}</div>'
            f'<div class="meta"><span>{"Time Allowed: " + esc(time_allowed) if time_allowed else ""}</span><span>Questions in this booklet: {len(qs)}</span>'
            f'<span>{"Maximum Marks: " + str(marks) if marks else ""}</span></div>'
            + (f'<div class="note">{esc(MOCK_NOTE[conf["id"]])}, for the {esc(mock)} test series, with an explanation for every answer. '
               'The answer key and answers with explanations are at the end of this booklet.</div>' if mock and conf['id'] in MOCK_NOTE else
               f'<div class="note">New questions written by Learn with Anil for the {esc(mock)} test series in the {esc(conf["board"])} pattern (not previous-year questions), '
               'with an explanation for every answer. The answer key and answers with explanations are at the end of this booklet.</div>' if mock else
               f'<div class="note">Questions as printed in {esc(conf["board"])}\'s official {"question paper of this shift" if conf["board"] == "RRB" else "booklet"} (English'
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


def brand_original(conf, p, srcs, out):
    """The board's own booklet (+ its answer key), each page kept as it is, with a footer strip added below it:
    the Learn with Anil logo, 'Learn with Anil · learnwithanil.in', the paper and the page number."""
    import io, pikepdf
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    S = 24   # footer strip height (pt)
    pages = []
    for f in srcs:
        src = pikepdf.open(os.path.join(PRIV, 'originals', conf['id'], f))
        pages += [(src, pg) for pg in src.pages]
    sizes = []
    for src, pg in pages:
        mb = [float(x) for x in pg.mediabox]; w, h = mb[2] - mb[0], mb[3] - mb[1]
        if int(pg.obj.get('/Rotate', 0)) % 180: w, h = h, w
        sizes.append((w, h))
    buf = io.BytesIO(); c = canvas.Canvas(buf, invariant=1)
    logo = ImageReader(os.path.join(ROOT, 'src', 'static', 'icon-192.png'))
    label = (f'{p.get("kwname") or p["title"]} · {conf["board"]}\'s original question booklet and final answer key' if len(srcs) > 1 else
             f'{p.get("kwname") or p["title"]} · {conf["board"]}\'s original question paper, ' + ('answer key marked' if conf['id'] == 'uppsc-ro-aro' else 'final answers marked'))   # GSSSB: the paper preview ticks the answers
    for i, (w, h) in enumerate(sizes):
        c.setPageSize((w, S))
        c.setStrokeColorRGB(0.09, 0.27, 0.78); c.setLineWidth(0.8); c.line(18, S - 1, w - 18, S - 1)
        c.drawImage(logo, 18, 5, 14, 14, mask='auto')
        c.setFillColorRGB(0.05, 0.09, 0.19); c.setFont('Helvetica-Bold', 8.5); c.drawString(37, 9, 'Learn with Anil · learnwithanil.in')
        c.setFont('Helvetica', 7); c.setFillColorRGB(0.33, 0.38, 0.49)
        c.drawString(37 + c.stringWidth('Learn with Anil · learnwithanil.in', 'Helvetica-Bold', 8.5) + 8, 9.4, label)
        c.drawRightString(w - 18, 9.4, f'Page {i + 1} of {len(sizes)}')
        c.showPage()
    c.save()
    foot = pikepdf.open(io.BytesIO(buf.getvalue()))
    dst = pikepdf.new()
    for i, ((src, pg), (w, h)) in enumerate(zip(pages, sizes)):
        page = dst.add_blank_page(page_size=(w, h + S))
        page.add_overlay(pg, pikepdf.Rectangle(0, S, w, h + S))
        page.add_overlay(foot.pages[i], pikepdf.Rectangle(0, 0, w, S))
    dst.docinfo['/Title'] = f'{p["title"]} – original question booklet with the official answer key' if len(srcs) > 1 else f'{p["title"]} – original question paper with the official answers marked'
    dst.docinfo['/Author'] = 'Learn with Anil (learnwithanil.in)'
    dst.save(out, deterministic_id=True, compress_streams=True)


def main(exams, mocks_only=False):
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
        papers, qs = B.load_exam(conf)[:2] if not mocks_only else ([], [])
        for p in papers:
            pq = [q for q in qs if q['p'] == p['id']]
            if not pq or p.get('fmt') == 'recall': continue   # answer-only papers without options: no booklet
            out = os.path.join(OUTDIR, f'{eid}-{p["id"]}.pdf')
            if p['id'] in ORIGINALS.get(eid, {}):   # the board's own booklet with our footer (no typesetting)
                brand_original(conf, p, ORIGINALS[eid][p['id']], out)
                todo.append((eid, conf, p, out, hashlib.sha256(open(out, 'rb').read()).hexdigest()[:10])); continue
            doc = paper_doc(conf, p, pq)
            jobs.append((out, doc))
            todo.append((eid, conf, p, out, hashlib.sha256(doc.encode()).hexdigest()[:10]))
        for mid, pack, mname, mins, qn in released_mocks(eid):   # every released mock: decrypt the sealed file with its private key
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _A
            f = sealed_mock(mid)
            if not f or mid not in mkeys: print('  no sealed file or key for', mid); continue
            raw = open(f, 'rb').read()
            mq = [inline_img(q) for q in json.loads(_A(base64.b64decode(mkeys[mid])).decrypt(raw[:12], raw[12:], mid.encode()))['questions']]
            for i, q in enumerate(mq, 1): q.setdefault('n', i)
            mq = share_passages(mq)
            p = dict(id=mock_pid(mid), mock=mid, notif=f'{pack} · {mname}', held='', kw=f'{pack} {mname}', key='Learn with Anil', mins=mins)
            p['title'] = f'{conf["seo"]} Prelims 2026 · {mname}' if mid.startswith('mk-si-') or mid.startswith('mk-pc-') else f'{conf["seo"]} Mock Test · {mname}'
            out = os.path.join(OUTDIR, f'{eid}-{p["id"]}.pdf')
            doc = paper_doc(conf, p, mq, mock=pack)
            jobs.append((out, doc))
            todo.append((eid, conf, p, out, hashlib.sha256(doc.encode()).hexdigest()[:10]))
    if jobs: asyncio.run(render(jobs))
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
        manifest.setdefault(eid, {})[p['id']] = dict(key=kid, file=name, name=dl, pages=pages, bytes=len(pdf), **({'mock': p['mock']} if p.get('mock') else {}),
                                                     **({'orig': 1 if len(ORIGINALS[eid][p['id']]) > 1 else 2} if p['id'] in ORIGINALS.get(eid, {}) else {}))
        rows.append('\t'.join([kid, keys[kid], name, today]))
        print(f'  {kid}: {pages} pages, {len(pdf) // 1024} KB -> src/books/{name}')
    json.dump(keys, open(kpath, 'w'), indent=1)
    json.dump(manifest, open(mpath, 'w'), indent=1, sort_keys=True)
    open(os.path.join(PRIV, 'booklet-keys-tab.tsv'), 'w').write('\n'.join(rows) + '\n')
    print(f'{len(rows)} booklets; keys-tab rows in {PRIV}/booklet-keys-tab.tsv')


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--mocks' in a:   # python3 tools/booklets.py --mocks [exam ids]: booklets of every released mock (default: every test series)
        a.remove('--mocks')
        main(a or list(B.MOCK_PACKS), mocks_only=True)
    else:
        main(a or DEFAULT)
