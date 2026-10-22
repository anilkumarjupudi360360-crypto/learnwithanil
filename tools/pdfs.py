#!/usr/bin/env python3
"""Make one PDF per paper: every question in English and the second language (Telugu or Hindi), then the
answer key and an explanation for each answer. Run after tools/build.py:

    SITE_URL=https://learnwithanil.in python3 tools/build.py && python3 tools/pdfs.py

Writes dist/site/<exam dir>/pdf/<name>.pdf (the names come from build.pdf_name). Rendering takes a while, so a
PDF is only re-made when its content changed: tools/pdf-manifest.json keeps a hash per file, and unchanged PDFs
are copied from the published copy in docs/. Fonts are in tools/fonts (SIL Open Font License).
"""
import asyncio, hashlib, html, json, os, re, shutil, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402

ROOT, DIST = B.ROOT, B.DIST
DOCS = os.path.join(ROOT, 'docs')
FONTS = os.path.join(ROOT, 'tools', 'fonts')
MANIFEST = os.path.join(ROOT, 'tools', 'pdf-manifest.json')
VERSION = 'pdf-v2'   # bump to re-render every PDF after a layout change
esc = B.esc

FACES = [('Source Sans 3', 'source-sans-3-latin', 400), ('Source Sans 3', 'source-sans-3-latin', 600), ('Source Sans 3', 'source-sans-3-latin', 700),
         ('Source Sans 3', 'source-sans-3-latin-ext', 400), ('Source Sans 3', 'source-sans-3-latin-ext', 700),
         ('Archivo', 'archivo-latin', 800), ('IBM Plex Mono', 'ibm-plex-mono-latin', 500),
         ('Noto Sans Telugu', 'noto-sans-telugu-telugu', 400), ('Noto Sans Telugu', 'noto-sans-telugu-telugu', 600),
         ('Noto Sans Devanagari', 'noto-sans-devanagari-devanagari', 400), ('Noto Sans Devanagari', 'noto-sans-devanagari-devanagari', 600)]
RANGES = {'latin': 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+20B9,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD',
          'latin-ext': 'U+0100-024F,U+20A0-20CF,U+2C60-2C7F,U+A720-A7FF', 'telugu': 'U+0C00-0C7F,U+200C-200D,U+25CC',
          'devanagari': 'U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FF'}


def font_css():
    out = []
    for fam, f, w in FACES:
        sub = re.search(r'-(latin-ext|latin|telugu|devanagari)$', f).group(1)
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('file://{FONTS}/{f}-{w}-normal.woff2') format('woff2');unicode-range:{RANGES[sub]}}}")
    return '\n'.join(out)


CSS = """
@page{size:A4;margin:14mm 13mm 16mm 13mm}
*{box-sizing:border-box}
body{margin:0;font:10.5pt/1.45 'Source Sans 3',sans-serif;color:#0D1830}
[lang=te]{font-family:'Noto Sans Telugu','Source Sans 3',sans-serif;line-height:1.6}
[lang=hi]{font-family:'Noto Sans Devanagari','Source Sans 3',sans-serif;line-height:1.6}
a{color:#1440B8}
.top{border-bottom:2.5pt solid #1846C7;padding-bottom:8pt;margin-bottom:10pt}
.brand{font:500 8.5pt 'IBM Plex Mono',monospace;letter-spacing:.06em;text-transform:uppercase;color:#55627C}
h1{font:800 19pt/1.15 Archivo,sans-serif;margin:4pt 0 3pt}
h1 + p{margin:0 0 4pt;font-size:12pt;font-weight:600}
.meta{color:#55627C;font-size:9.5pt;margin:0}
.box{border:1pt solid #D6DFEC;background:#F3F6FB;border-radius:6pt;padding:7pt 10pt;margin:8pt 0 4pt;font-size:9.5pt}
h2{font:800 13pt Archivo,sans-serif;margin:14pt 0 6pt;color:#0C2266}
.q{break-inside:avoid;margin:0 0 9pt;padding-bottom:7pt;border-bottom:.5pt solid #E3E9F3}
.q .n{font-weight:700;color:#1440B8}
.q p{margin:0;white-space:pre-line;font-weight:600}
.q ol{margin:3pt 0 0;padding-left:12pt;list-style:none}
.q ol li{margin:1pt 0}
.q .l2{margin-top:4pt;padding-left:8pt;border-left:2pt solid #D6DFEC;color:#25324B}
.q .l2 p{font-weight:400}
.q img{max-width:100%;max-height:70mm;margin:4pt 0}
.keygrid{display:grid;grid-template-columns:repeat(7,1fr);gap:2pt 6pt;font:500 9pt 'IBM Plex Mono',monospace;margin-bottom:6pt}
.ans{break-inside:avoid;margin:0 0 7pt}
.ans b{color:#12804A}
.ans .why{margin:1pt 0 0;color:#25324B}
.pb{break-before:page}
"""


def opt_list(opts):
    return '<ol>' + ''.join(f'<li>({i + 1}) {esc(o)}</li>' for i, o in enumerate(opts)) + '</ol>'


def paper_html(conf, p, qs, subj):
    kw, alt, l2 = B.paper_kw(conf, p), B.paper_alt(conf, p), conf['l2']
    site = B.SITE_URL
    paper_url = f'{site}/{conf["dir"] + "/" if conf["dir"] else ""}papers/{p["slug"]}.html'
    if conf['board'] == 'APPSC':
        src = "Answers from APPSC's official final key."
    else:
        src = f'Answers from {p.get("key") or conf["keyname"]}.'
    title = f'{kw} Question Paper with Answers'
    parts = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)} | Learn with Anil</title>'
             f'<meta name="author" content="Jupudi Anil Kumar, Learn with Anil"><style>{font_css()}{CSS}</style></head><body>',
             f'<div class="top"><div class="brand">Learn with Anil · learnwithanil.in · free previous year question papers</div>'
             f'<h1>{esc(title)}</h1><p lang="{l2["code"]}">{esc(B.paper_kw_l2(conf, p))}</p>'
             f'<p class="meta">{esc(p["title"])}{f" ({esc(B.alt_shown(alt, p['title']))})" if B.alt_shown(alt, p['title']) else ""} · held {esc(p["held"])} · {esc(p["notif"])} · {len(qs)} questions. {esc(src)}</p>'
             f'<div class="box">Practise this paper free online, as a mock test or topic by topic, with your mistakes saved for revision: '
             f'<a href="{esc(paper_url)}">{esc(paper_url.replace("https://", ""))}</a>. '
             f'Questions are as printed in the official booklet, in English and {l2["name"]}; the answer key and explanations follow the questions.</div></div>']
    parts.append('<h2>Questions</h2>')
    for q in qs:
        h = [f'<div class="q"><p><span class="n">Q{q["n"]}.</span> {esc(q["q"])}</p>']
        if q.get('img'): h.append(f'<img src="{q["img"]}" alt="">')
        if q.get('o'): h.append(opt_list(q['o']))
        if q.get('qt'):
            h.append(f'<div class="l2" lang="{l2["code"]}"><p>{esc(q["qt"])}</p>{opt_list(q["ot"]) if q.get("ot") else ""}</div>')
        h.append('</div>')
        parts.append(''.join(h))
    mcq = [q for q in qs if q.get('o')]
    parts.append('<h2 class="pb">Answer key</h2>')
    if mcq:
        parts.append('<div class="keygrid">' + ''.join(f'<span>{q["n"]} → {",".join(f"({i + 1})" for i in q["a"])}</span>' for q in mcq) + '</div>')
    parts.append('<h2>Answers with explanations</h2>')
    for q in qs:
        if q.get('o'):
            ans = ' / '.join(f'({i + 1}) {q["o"][i]}' for i in q['a'])
            ans2 = ' / '.join(f'({i + 1}) {q["ot"][i]}' for i in q['a']) if q.get('ot') else ''
        else:
            ans, ans2 = q['ans'], q.get('at', '')
        l2a = f' <span lang="{l2["code"]}">· {esc(ans2)}</span>' if ans2 else ''
        wt = f'<p class="why" lang="{l2["code"]}">{esc(q["wt"])}</p>' if q.get('wt') else ''
        parts.append(f'<div class="ans"><span class="n">Q{q["n"]}.</span> <b>{esc(ans)}</b>{l2a}'
                     f'<p class="why">{esc(q["w"])}</p>{wt}</div>')
    parts.append(f'<div class="box">More free papers, mock tests and Telugu/Hindi practice at <a href="{site}/">learnwithanil.in</a>. '
                 f'Explanations by Jupudi Anil Kumar. Not affiliated with {conf["board"]}.</div></body></html>')
    return ''.join(parts)


def footer(kw):
    return ('<div style="width:100%;font:8px sans-serif;color:#55627C;padding:0 13mm;display:flex;justify-content:space-between">'
            f'<span>learnwithanil.in · {esc(kw)} question paper with answers</span>'
            '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')


async def render(jobs):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        tmp = tempfile.mkdtemp(prefix='lwa-pdf-')
        for out, doc, kw in jobs:
            f = os.path.join(tmp, 'p.html'); open(f, 'w', encoding='utf-8').write(doc)
            await pg.goto('file://' + f); await pg.evaluate('document.fonts.ready')
            await pg.pdf(path=out, format='A4', print_background=True, display_header_footer=True,
                         header_template='<span></span>', footer_template=footer(kw),
                         margin=dict(top='14mm', bottom='16mm', left='13mm', right='13mm'))
            print(f'  rendered {os.path.relpath(out, DIST)} ({os.path.getsize(out) // 1024} KB)')
        await b.close()
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not os.path.isdir(os.path.join(DIST, 'site')): sys.exit('run tools/build.py first')
    manifest = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    new, jobs, kept = {}, [], 0
    for conf in B.exam_confs():
        papers, questions = B.load_exam(conf)
        if not questions: continue
        subj = {s[0]: s for s in conf['subjects']}
        by_p = {}
        for q in questions: by_p.setdefault(q['p'], []).append(q)
        for p in papers:
            rel = B.pdf_href(conf, p).lstrip('/')
            out = os.path.join(DIST, 'site', rel); os.makedirs(os.path.dirname(out), exist_ok=True)
            doc = paper_html(conf, p, by_p[p['id']], subj)
            h = hashlib.sha1((VERSION + doc).encode()).hexdigest()
            new[rel] = h
            pub = os.path.join(DOCS, rel)
            if manifest.get(rel) == h and os.path.exists(pub):
                shutil.copy(pub, out); kept += 1
            else:
                jobs.append((out, doc, B.paper_kw(conf, p)))
    if jobs: asyncio.run(render(jobs))
    json.dump(new, open(MANIFEST, 'w'), indent=1, sort_keys=True)
    print(f'  PDFs: {len(jobs)} rendered, {kept} unchanged')


if __name__ == '__main__':
    main()
