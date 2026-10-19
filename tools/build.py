#!/usr/bin/env python3
"""Build the Learn with Anil APPSC Group-II PYQ site.

src/*.txt  (question transcriptions)  ->  dist/  (artifact page + hostable website)
"""
import json, re, os, sys, html, base64, shutil, io
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
DIST = os.path.join(ROOT, 'dist')
SITE_URL = os.environ.get('SITE_URL', 'https://learnwithanil.in').rstrip('/')
INSTAGRAM = 'learn_with_anil06'
WHATSAPP = '919494792739'
PHONE = '+91 94947 92739'
EMAIL = 'anilkumarjupudi360360@gmail.com'

PAPERS = [
  dict(id='s2024', file='screening-2024.txt', year=2024, stage='Screening Test', short='Screening 2024',
       title='APPSC Group-II Screening Test 2024', notif='Notification 11/2023', held='25 February 2024',
       fmt='mcq', slug='appsc-group-2-screening-test-2024-question-paper-with-answers',
       blurb='General Studies & Mental Ability: Indian History, Geography, Indian Society, Current Affairs and Mental Ability (30 marks each).'),
  dict(id='m2025p1', file='mains-2025-p1.txt', year=2025, stage='Mains Paper I', short='Mains 2025 · P-I',
       title='APPSC Group-II Mains 2025 Paper I', notif='Notification 11/2023', held='23 February 2025',
       fmt='mcq', slug='appsc-group-2-mains-2025-paper-1-question-paper-with-answers',
       blurb='Social & Cultural History of Andhra Pradesh and the Indian Constitution (75 marks each).'),
  dict(id='m2025p2', file='mains-2025-p2.txt', year=2025, stage='Mains Paper II', short='Mains 2025 · P-II',
       title='APPSC Group-II Mains 2025 Paper II', notif='Notification 11/2023', held='23 February 2025',
       fmt='mcq', slug='appsc-group-2-mains-2025-paper-2-question-paper-with-answers',
       blurb='Indian & Andhra Pradesh Economy and Science & Technology (75 marks each).'),
  dict(id='s2019', file='screening-2019.txt', year=2019, stage='Screening Test', short='Screening 2019',
       title='APPSC Group-II Screening Test 2019', notif='Notification 25/2018', held='5 May 2019',
       fmt='recall', slug='appsc-group-2-screening-test-2019-question-paper-with-answers',
       blurb='General Studies & Mental Ability, AP History & Constitution, and Planning & Economy (old pattern).'),
  dict(id='m2019p1', file='mains-2019-p1.txt', year=2019, stage='Mains Paper I', short='Mains 2019 · P-I',
       title='APPSC Group-II Mains 2019 Paper I', notif='Notification 25/2018', held='29 August 2019',
       fmt='recall', slug='appsc-group-2-mains-2019-paper-1-general-studies-questions-with-answers',
       blurb='General Studies and Mental Ability (old pattern).'),
  dict(id='m2019p2', file='mains-2019-p2.txt', year=2019, stage='Mains Paper II', short='Mains 2019 · P-II',
       title='APPSC Group-II Mains 2019 Paper II', notif='Notification 25/2018', held='August 2019',
       fmt='recall', slug='appsc-group-2-mains-2019-paper-2-history-polity-questions-with-answers',
       blurb='Social & Cultural History of AP and General Overview of the Indian Constitution (old pattern).'),
  dict(id='m2019p3', file='mains-2019-p3.txt', year=2019, stage='Mains Paper III', short='Mains 2019 · P-III',
       title='APPSC Group-II Mains 2019 Paper III', notif='Notification 25/2018', held='30 August 2019',
       fmt='recall', slug='appsc-group-2-mains-2019-paper-3-economy-questions-with-answers',
       blurb='Planning in India and Indian Economy, and contemporary issues (old pattern).'),
]

SUBJECTS = [
  ('ih',  'Indian History', 'indian-history', ['Ancient India', 'Medieval India', 'Modern India', 'Art & Culture']),
  ('aph', 'AP History & Culture', 'ap-history-culture', ['Ancient Andhra', 'Medieval Andhra', 'Modern Andhra', 'AP Formation & Movements', 'Andhra Literature & Arts']),
  ('pol', 'Indian Polity', 'indian-polity-constitution', ['Constitution Basics & Preamble', 'Fundamental Rights & Duties', 'DPSP', 'Union Executive', 'Parliament', 'State Government', 'Judiciary', 'Federalism & Emergency', 'Local Government', 'Constitutional & Statutory Bodies', 'Amendments & Governance', 'AP Reorganisation Act, 2014']),
  ('geo', 'Geography', 'geography', ['Physical Geography', 'Indian Geography', 'World Geography', 'AP Geography']),
  ('soc', 'Indian Society', 'indian-society', ['Social Structure', 'Social Issues', 'Social Justice & Welfare', 'Education & Child Development']),
  ('eco', 'Economy (India & AP)', 'indian-ap-economy', ['Planning & Development', 'National Income & Growth', 'Money, Banking & Inflation', 'Public Finance & Taxation', 'Agriculture', 'Industry & Infrastructure', 'Poverty, Employment & Population', 'External Sector', 'Rural Development', 'AP Economy']),
  ('sci', 'Science & Technology', 'science-technology', ['General Science', 'Space Technology', 'Defence Technology', 'Biotechnology & Health', 'IT & Communication', 'Energy', 'Environment & Ecology', 'Disaster Management']),
  ('cur', 'Current Affairs', 'current-affairs', ['National', 'International', 'Sports', 'Awards & Personalities', 'AP Affairs']),
  ('men', 'Mental Ability', 'mental-ability-reasoning', ['Numbers & Series', 'Reasoning', 'Arithmetic', 'Data Interpretation & Statistics']),
  ('gk',  'General Knowledge', 'general-knowledge', ['Media & Communication', 'Days, Books & Organisations', 'Miscellaneous']),
]
SUBJ = {s[0]: s for s in SUBJECTS}


def parse(paper):
    path = os.path.join(SRC, paper['file'])
    if not os.path.exists(path):
        return []
    text = open(path, encoding='utf-8').read()
    out, errs = [], []
    blocks = re.split(r'\n(?=Q \d+ \|)', '\n' + text)
    for b in blocks:
        b = b.strip('\n')
        if not b.startswith('Q '):
            continue
        lines = b.split('\n')
        m = re.match(r'Q (\d+) \| (\w+) \| (.+)$', lines[0].strip())
        if not m:
            errs.append('bad header: ' + lines[0]); continue
        n, s, t = int(m.group(1)), m.group(2), m.group(3).strip()
        if s not in SUBJ: errs.append(f'{paper["id"]} Q{n}: unknown subject {s}')
        elif t not in SUBJ[s][3]: errs.append(f'{paper["id"]} Q{n}: unknown topic {s}/{t}')
        qlines, opts, ans, why, img = [], [], None, None, None
        for ln in lines[1:]:
            if re.match(r'^\(([1-4])\) ', ln):
                opts.append(ln[4:].strip())
            elif ln.startswith('= '):
                ans = ln[2:].strip()
            elif ln.startswith('~ '):
                why = ln[2:].strip()
            elif ln.startswith('! '):
                img = ln[2:].strip()
            elif ln.strip():
                if opts: errs.append(f'{paper["id"]} Q{n}: text after options: {ln[:40]}')
                qlines.append(ln.rstrip())
        q = dict(id=f'{paper["id"]}-{n}', p=paper['id'], n=n, s=s, t=t, q='\n'.join(qlines).strip(), w=why or '')
        if img: q['img'] = img
        if not why: errs.append(f'{paper["id"]} Q{n}: no explanation')
        if ans is None: errs.append(f'{paper["id"]} Q{n}: no answer'); continue
        if opts:
            if len(opts) != 4: errs.append(f'{paper["id"]} Q{n}: {len(opts)} options')
            try:
                a = [int(x) - 1 for x in ans.split(',')]
                assert all(0 <= x < len(opts) for x in a)
            except Exception:
                errs.append(f'{paper["id"]} Q{n}: bad answer {ans}'); continue
            q['o'], q['a'] = opts, a
        else:
            q['ans'] = ans
        out.append(q)
    ns = [q['n'] for q in out]
    if len(ns) != len(set(ns)): errs.append(f'{paper["id"]}: duplicate numbers')
    if ns != sorted(ns): errs.append(f'{paper["id"]}: numbers out of order')
    for e in errs: print('  !', e)
    return out


def parse_te(paper, qs):
    """Merge official Telugu text from src/te/<file> into the parsed questions.
    Format: 'Q <n>' line, then Telugu question lines, then optional '(1)'..'(4)' options,
    and for answer-only papers an optional '= <answer>' line."""
    path = os.path.join(SRC, 'te', paper['file'])
    if not os.path.exists(path):
        return 0
    by_n = {q['n']: q for q in qs}
    text = open(path, encoding='utf-8').read()
    done, errs = 0, []
    for b in re.split(r'\n(?=Q \d+\s*$)', '\n' + text, flags=re.M):
        b = b.strip('\n')
        m = re.match(r'Q (\d+)\s*$', b.split('\n')[0]) if b.startswith('Q ') else None
        if not m:
            continue
        n = int(m.group(1)); q = by_n.get(n)
        if not q:
            errs.append(f'{paper["id"]} te Q{n}: no such English question'); continue
        qlines, opts, ans = [], [], None
        for ln in b.split('\n')[1:]:
            if re.match(r'^\(([1-4])\) ', ln): opts.append(ln[4:].strip())
            elif ln.startswith('= '): ans = ln[2:].strip()
            elif ln.strip():
                if opts: errs.append(f'{paper["id"]} te Q{n}: text after options')
                qlines.append(ln.rstrip())
        if qlines: q['qt'] = '\n'.join(qlines).strip()
        if opts:
            if 'o' in q and len(opts) == len(q['o']): q['ot'] = opts
            else: errs.append(f'{paper["id"]} te Q{n}: {len(opts)} options')
        if ans and 'ans' in q: q['at'] = ans
        done += 1
    for e in errs: print('  !', e)
    return done


def img_data_uri(rel):
    p = os.path.join(SRC, rel)
    from PIL import Image
    im = Image.open(p).convert('L')
    im = im.quantize(16)
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def photo_data_uri(size=420):
    from PIL import Image
    im = Image.open(os.path.join(SRC, 'img', 'anil.jpg')).convert('RGB')
    im = im.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(), buf.getvalue()


def esc(s):
    return html.escape(s, quote=True)


def main():
    papers, questions = [], []
    for p in PAPERS:
        qs = parse(p)
        nte = parse_te(p, qs)
        if nte: print(f'  {p["id"]}: Telugu for {nte} questions')
        if not qs:
            print('  - skipping', p['id'], '(no source yet)'); continue
        for q in qs:
            if 'img' in q: q['img'] = img_data_uri(q['img'])
        pp = {k: p[k] for k in ('id', 'year', 'stage', 'short', 'title', 'notif', 'held', 'fmt', 'slug', 'blurb')}
        pp['count'] = len(qs)
        papers.append(pp); questions += qs
        print(f'  {p["id"]}: {len(qs)} questions')
    subjects = [dict(id=s[0], name=s[1], slug=s[2], topics=s[3]) for s in SUBJECTS]
    npath = os.path.join(SRC, 'notes.json')
    notes = json.load(open(npath, encoding='utf-8')) if os.path.exists(npath) else []
    data = dict(papers=papers, subjects=subjects, questions=questions, instagram=INSTAGRAM, site=SITE_URL, notes=notes, wa=WHATSAPP)
    photo_uri, photo_bytes = photo_data_uri()

    tpl = open(os.path.join(ROOT, 'tools', 'app.html'), encoding='utf-8').read()
    head, body = tpl.split('<!--BODY-->')
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    total = len(questions)
    home_papers = ''.join(home_paper_card(p) for p in sorted(papers, key=lambda p: (-p['year'], p['id'])))
    scount = {}
    for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
    home_subjects = ''.join(
        f'<button type="button" class="card subj-card" data-act="presubj" data-subj="{s["id"]}"><span>{esc(s["name"])}</span><span class="mono">{scount[s["id"]]} Q</span></button>'
        for s in subjects if scount.get(s['id']))
    faq = FAQ(total, len(papers))
    faq_html = ''.join(f'<details><summary>{esc(qq)}</summary><p>{esc(aa)}</p></details>' for qq, aa in faq)
    def fill(s, photo, title, seo):
        return (s.replace('{{SEO_HEAD}}', seo).replace('{{TITLE}}', title)
                 .replace('{{HOME_PAPERS}}', home_papers).replace('{{HOME_SUBJECTS}}', home_subjects).replace('{{FAQ}}', faq_html)
                 .replace('{{DATA}}', data_json).replace('{{PHOTO}}', photo)
                 .replace('{{TOTAL}}', str(total)).replace('{{SITE}}', SITE_URL).replace('{{NPAPERS}}', str(len(papers)))
                 .replace('{{HOME_NOTES}}', home_notes(notes)))
    site_title = 'APPSC Group 2 Previous Year Questions (PYQs) with Answers | Learn with Anil'
    site_desc = (f'Free APPSC Group 2 PYQs: {total} previous year questions from the Screening Test 2024, Mains 2025 Paper I & II '
                 f'and the 2019 papers, with official final-key answers and explanations. Topic-wise quizzes by Learn with Anil.')
    ld = [
      {"@context":"https://schema.org","@type":"WebSite","name":"Learn with Anil","alternateName":"Learn with Anil – APPSC Group-II PYQs","url":SITE_URL+'/'},
      {"@context":"https://schema.org","@type":"Person","name":"Jupudi Anil Kumar","jobTitle":"UPSC Faculty and Mentor","telephone":"+91-94947-92739","email":"mailto:anilkumarjupudi360360@gmail.com","url":SITE_URL+'/#about',"image":SITE_URL+'/anil.jpg',"sameAs":[f"https://www.instagram.com/{INSTAGRAM}/"]},
      {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in faq]},
    ]
    seo = (f'<link rel="canonical" href="{SITE_URL}/">\n<meta name="robots" content="index,follow">\n'
           f'<meta property="og:type" content="website"><meta property="og:site_name" content="Learn with Anil">'
           f'<meta property="og:title" content="{esc(site_title)}"><meta property="og:description" content="{esc(site_desc)}">'
           f'<meta property="og:url" content="{SITE_URL}/"><meta property="og:image" content="{SITE_URL}/anil.jpg">'
           f'<meta name="twitter:card" content="summary">\n'
           + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld))

    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'site', 'papers')); os.makedirs(os.path.join(DIST, 'site', 'subjects'))
    os.makedirs(os.path.join(DIST, 'artifact', 'papers')); os.makedirs(os.path.join(DIST, 'artifact', 'subjects'))

    # 1) artifact page: fragment (publisher adds the skeleton); photo inline
    open(os.path.join(DIST, 'artifact', 'index.html'), 'w', encoding='utf-8').write(fill(head + body, photo_uri, 'Learn with Anil', ''))
    # 2) hostable site: full document; photo as file
    open(os.path.join(DIST, 'site', 'anil.jpg'), 'wb').write(photo_bytes)
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
           + fill(head, 'anil.jpg', site_title, seo).replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '') + '\n</head>\n<body>\n' + fill(body, 'anil.jpg', site_title, seo) + '\n</body>\n</html>\n')
    open(os.path.join(DIST, 'site', 'index.html'), 'w', encoding='utf-8').write(doc)

    # 3) crawlable pages per paper and per subject (same files for both outputs)
    pages = build_static(papers, subjects, questions)
    pages['initiative.html'] = initiative_page(total, len(papers), notes)
    for rel, content in pages.items():
        for target in ('site', 'artifact'):
            open(os.path.join(DIST, target, rel), 'w', encoding='utf-8').write(content)

    # 4) sitemap + robots (site only)
    today = date.today().isoformat()
    urls = [SITE_URL + '/'] + [SITE_URL + '/' + rel for rel in pages]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls: sm.append(f'  <url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>')
    sm.append('</urlset>')
    open(os.path.join(DIST, 'site', 'sitemap.xml'), 'w').write('\n'.join(sm) + '\n')
    open(os.path.join(DIST, 'site', 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')
    # extra files served as-is at the site root (search-engine verification files etc.)
    static = os.path.join(SRC, 'static')
    if os.path.isdir(static):

        for f in os.listdir(static):
            shutil.copy(os.path.join(static, f), os.path.join(DIST, 'site', f))
    open(os.path.join(DIST, 'site', '.nojekyll'), 'w').write('')
    print(f'  total {total} questions, {len(pages)} static pages')


def home_notes(notes):
    if not notes: return ''
    covers = ''.join(f'<img src="{esc(b["cover"])}" alt="" width="140" height="198" loading="lazy">' for b in notes)
    return f'''<section class="wrap section">
    <a class="card notes-promo" href="#notes">
      <div class="np-copy"><p class="eyebrow">New · Study material</p><h2>Crisp Notes 2026-27</h2>
      <p>AP Economy and Science &amp; Technology for Group-II Mains Paper II, in English and Telugu medium, with APPSC's own previous questions inside. ₹{notes[0]["price"]} per book.</p>
      <span class="btn btn-primary">See the books</span></div>
      <div class="np-covers" aria-hidden="true">{covers}</div>
    </a>
  </section>'''


def nw(t):
    return esc(t).replace('Group-II', '<span class="nw">Group-II</span>')


def home_paper_card(p):
    fmt = 'All 4 options' if p['fmt'] == 'mcq' else 'Answer-only key'
    cls = 'good' if p['fmt'] == 'mcq' else 'warn'
    return (f'<article class="card paper"><span class="yr">{esc(p["held"])} · {esc(p["notif"])}</span><h3>{nw(p["title"])}</h3>'
            f'<p>{esc(p["blurb"])}</p><div class="meta"><span class="pill blue">{p["count"]} questions</span><span class="pill {cls}">{fmt}</span></div>'
            f'<div class="acts"><button class="btn btn-primary btn-sm" type="button" data-act="paperpractice" data-paper="{p["id"]}">Practise</button>'
            f'<a class="btn btn-ghost btn-sm" href="papers/{p["slug"]}.html">Read with answers</a></div></article>')


def FAQ(total, npapers):
    return [
      ('Where can I get APPSC Group 2 previous year question papers with answers?',
       f'This site has {total} questions from {npapers} APPSC Group-II papers: the Screening Test 2024, Mains 2025 Paper I and Paper II, and the 2019 Screening and Mains papers. Every answer is taken from APPSC\'s official final key, and each question has a short explanation. You can read each paper with answers or practise it as a quiz, free.'),
      ('What is the APPSC Group 2 exam pattern?',
       'Under Notification 11/2023, the Screening Test is one objective paper of 150 questions for 150 marks in 150 minutes, with 30 marks each for Indian History, Geography, Indian Society, Current Affairs and Mental Ability. The Mains has two objective papers of 150 marks each: Paper I covers the Social and Cultural History of Andhra Pradesh and the Indian Constitution, and Paper II covers the Indian and AP Economy and Science and Technology.'),
      ('Are the answers on this site official?',
       'Yes. The answers come from the final keys published by APPSC. Questions that APPSC deleted are left out, and where the final key accepted two options, both are shown as correct. The explanations are written by Learn with Anil.'),
      ('Why do the 2019 questions not show four options?',
       'APPSC\'s 2019 final keys print each question with only the correct answer. Those questions appear here as quick-recall cards: you think of the answer, reveal it and mark whether you knew it. The 2024 and 2025 papers show all four options.'),
      ('Do I need to sign up?',
       'No. The portal is free and practice needs no account. Before your first timed test you enter your name, phone, email and district once, so your test scores are saved with Learn with Anil and Anil can guide you. Your practice attempts, mistakes notebook and bookmarks stay in your own browser on your device.'),
    ]


STATIC_CSS = """
.nw{white-space:nowrap}
[lang="te"]{font-family:"Noto Sans Telugu",sans-serif;line-height:1.8}
.q .te{border-left:3px solid var(--line);padding-left:12px;margin:8px 0 4px}
:root{--bg:#F3F6FB;--surface:#fff;--ink:#0D1830;--muted:#55627C;--line:#D6DFEC;--accent:#1846C7;--accent-soft:#E2EAFC;--accent-text:#1440B8;--band:#0C2266;--band-ink:#EEF3FF;--good:#12804A;--good-soft:#DDF3E7}
@media (prefers-color-scheme:dark){:root{--bg:#0A1020;--surface:#111A2E;--ink:#E5ECF8;--muted:#9AA8C3;--line:#26334F;--accent:#6F95FF;--accent-soft:#1A2A52;--accent-text:#9DB7FF;--band:#0F1F4E;--band-ink:#EEF3FF;--good:#41C080;--good-soft:#123426;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 "Source Sans 3",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent-text)}.wrap{max-width:860px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header{background:var(--band);color:var(--band-ink)}header .wrap{padding-block:14px;display:flex;overflow-wrap:anywhere;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center}
header a{color:var(--band-ink);text-decoration:none;font-weight:700}h1,h2{font-family:Archivo,"Arial Narrow",system-ui,sans-serif;line-height:1.2;text-wrap:balance}
h1{font-size:clamp(26px,4vw,36px);margin:28px 0 8px}h2{font-size:22px;margin:32px 0 10px}.lede{color:var(--muted);max-width:65ch}
.cta{display:inline-block;background:var(--accent);color:#fff;padding:10px 16px;border-radius:10px;font-weight:700;text-decoration:none;margin:8px 8px 0 0}
.cta.alt{background:transparent;color:var(--accent-text);border:1.5px solid var(--line)}
ol.qs{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:14px}
.q{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.q .meta{font:13px/1.4 "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);margin-bottom:6px}
.q p{margin:0 0 8px;white-space:pre-line;font-weight:600;overflow-wrap:anywhere}.q ol{margin:0 0 8px;padding-left:28px}.q li{overflow-wrap:anywhere}
.q img{max-width:100%;background:#fff;border-radius:6px}
details summary{cursor:pointer;color:var(--accent-text);font-weight:700}
.ans{color:var(--good);font-weight:700;margin:8px 0 4px}.why{color:var(--muted);margin:0}
nav.toc{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}nav.toc a{background:var(--accent-soft);padding:4px 10px;border-radius:999px;text-decoration:none;font-size:15px}
footer{margin-top:40px;border-top:1px solid var(--line);color:var(--muted);font-size:15px}footer .wrap{padding-block:18px}
"""


INIT_CSS = """
:root{--bg:#F3F6FB;--surface:#FFFFFF;--surface-2:#EAF0F9;--ink:#0D1830;--muted:#55627C;--line:#D6DFEC;--accent:#1846C7;--accent-ink:#fff;--accent-soft:#E2EAFC;--accent-text:#1440B8;
--band:#0C2266;--band-ink:#EEF3FF;--band-muted:#AFC1EE;--gold:#F2B705;--good:#12804A;--good-soft:#DDF3E7;--warn:#9A620B;--warn-soft:#FBEFD6;
--shadow:0 1px 2px rgba(13,24,48,.06),0 8px 22px rgba(13,24,48,.06);
--f-display:"Archivo","Arial Narrow",system-ui,sans-serif;--f-body:"Source Sans 3",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0A1020;--surface:#111A2E;--surface-2:#17223A;--ink:#E5ECF8;--muted:#9AA8C3;--line:#26334F;--accent:#6F95FF;--accent-ink:#06102A;--accent-soft:#1A2A52;--accent-text:#9DB7FF;--band:#0F1F4E;--good:#41C080;--good-soft:#123426;--warn:#E6A846;--warn-soft:#3A2C12;--shadow:0 1px 2px rgba(0,0,0,.35),0 8px 22px rgba(0,0,0,.25);color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0A1020;--surface:#111A2E;--surface-2:#17223A;--ink:#E5ECF8;--muted:#9AA8C3;--line:#26334F;--accent:#6F95FF;--accent-ink:#06102A;--accent-soft:#1A2A52;--accent-text:#9DB7FF;--band:#0F1F4E;--good:#41C080;--good-soft:#123426;--warn:#E6A846;--warn-soft:#3A2C12;color-scheme:dark}
*{box-sizing:border-box}html,body{background:var(--bg)}
body{margin:0;color:var(--ink);font-family:var(--f-body);font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:var(--f-display);line-height:1.12;margin:0;letter-spacing:-.01em;text-wrap:balance}
p{margin:0}a{color:var(--accent-text)}img{max-width:100%}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:6px}
.wrap{width:100%;max-width:1080px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.eyebrow{font-family:var(--f-mono);font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:500}
.top{background:var(--surface);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:60px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink)}
.brand i{width:34px;height:34px;border-radius:50%;border:2.5px solid var(--accent);display:grid;place-items:center;font:normal 800 13px var(--f-display);color:var(--accent-text)}
.brand b{font-family:var(--f-display);font-size:18px;font-weight:800}
.top nav{display:flex;gap:4px;flex-wrap:wrap}.top nav a{text-decoration:none;font-weight:600;font-size:15px;padding:6px 10px;border-radius:8px}.top nav a:hover{background:var(--accent-soft)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border-radius:10px;padding:11px 18px;font-weight:700;font-size:15.5px;border:1.5px solid transparent;text-decoration:none;line-height:1.2}
.hero{background:var(--band);color:var(--band-ink);position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:40px 40px}
.hero::after{content:"";position:absolute;right:-180px;top:-220px;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,rgba(24,70,199,.9),rgba(24,70,199,0) 70%)}
.hero .wrap{position:relative;z-index:1;padding-top:56px;padding-bottom:56px;display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:40px;align-items:center}
.hero .eyebrow{color:var(--band-muted)}
.tag{display:inline-block;background:var(--gold);color:#0C2266;font:800 13px var(--f-display);letter-spacing:.06em;text-transform:uppercase;padding:5px 11px;border-radius:5px;margin-bottom:14px}
.hero h1{font-size:clamp(30px,5vw,48px);font-weight:800;color:#fff}
.hero p.lede{font-size:clamp(17px,2vw,19.5px);color:#D7E1FA;margin-top:16px;max-width:62ch}
.hero .ctas{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}
.hero .b1{background:#fff;color:#0C2266}.hero .b2{border-color:var(--band-muted);color:#fff}
.hero .ph{width:260px;height:260px;border-radius:50%;overflow:hidden;border:5px solid var(--band-muted);background:#1846C7;justify-self:center}
.hero .ph img{width:100%;height:100%;object-fit:cover;display:block}
.hero .who{text-align:center;margin-top:12px}.hero .who b{display:block;font:800 19px var(--f-display);color:#fff}.hero .who span{font-size:14.5px;color:var(--band-muted)}
@media (max-width:820px){.hero .wrap{grid-template-columns:1fr;gap:28px;padding-top:40px;padding-bottom:40px}.hero .side{order:-1;display:flex;align-items:center;gap:16px}.hero .ph{width:96px;height:96px;border-width:3px;justify-self:start}.hero .who{text-align:left;margin:0}}
section.blk{padding:52px 0 0}
section.blk>.wrap>h2{font-size:clamp(24px,3.4vw,32px);font-weight:800;margin-top:6px}
section.blk>.wrap>p.intro{color:var(--muted);max-width:68ch;margin-top:10px}
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:24px}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:24px}
@media (max-width:860px){.grid3{grid-template-columns:1fr}.grid2{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:20px 22px;box-shadow:var(--shadow)}
.card h3{font-size:19px;font-weight:700;margin-bottom:6px}.card p{color:var(--muted);font-size:16px}
.big{font:800 34px/1.05 var(--f-display);color:var(--accent-text);display:block;margin-bottom:6px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-top:24px}
@media (max-width:860px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.stats .card{padding:18px}.stats .card p{font-size:15px}
.list{margin:12px 0 0;padding-left:20px;color:var(--muted)}.list li{margin:5px 0}
.pill{display:inline-block;font-size:12.5px;font-weight:700;padding:2px 10px;border-radius:999px;margin-left:6px;vertical-align:2px}
.pill.live{background:var(--good-soft);color:var(--good)}.pill.plan{background:var(--warn-soft);color:var(--warn)}
.model{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:24px;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--surface)}
.model>div{padding:20px 22px;border-right:1px solid var(--line)}.model>div:last-child{border-right:0}
.model .price{font:800 28px var(--f-display);color:var(--ink);margin:4px 0}
.model p{color:var(--muted);font-size:15.5px}
@media (max-width:860px){.model{grid-template-columns:1fr}.model>div{border-right:0;border-bottom:1px solid var(--line)}.model>div:last-child{border-bottom:0}}
.road{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:24px}
@media (max-width:860px){.road{grid-template-columns:1fr}}
.road .card h3{display:flex;align-items:center;gap:8px}.road .dot{width:11px;height:11px;border-radius:50%;background:var(--good)}
.road .next .dot{background:var(--accent)}.road .later .dot{background:var(--muted)}
.books{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:24px}
@media (max-width:860px){.books{grid-template-columns:repeat(2,minmax(0,1fr))}}
.books a{text-decoration:none;color:var(--ink)}.books img{display:block;width:100%;height:auto;border-radius:6px;box-shadow:var(--shadow)}
.books span{display:block;font-size:14.5px;font-weight:600;margin-top:8px;line-height:1.35}.books small{color:var(--muted);font-weight:400}
.founder{display:grid;grid-template-columns:200px minmax(0,1fr);gap:28px;align-items:start;margin-top:24px}
@media (max-width:700px){.founder{grid-template-columns:1fr}.founder img{width:140px!important;height:140px!important}}
.founder img{width:200px;height:200px;border-radius:14px;object-fit:cover}
.founder .role{font-family:var(--f-mono);font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:4px 0 12px}
.founder p+p{margin-top:10px}
.fstats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:18px}
@media (max-width:700px){.fstats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.fstats div{background:var(--surface-2);border-radius:10px;padding:10px 12px}.fstats b{display:block;font:800 22px var(--f-display)}.fstats span{font-size:13.5px;color:var(--muted);line-height:1.3;display:block}
.ask{background:var(--band);color:var(--band-ink);border-radius:16px;padding:32px;margin-top:24px;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:28px}
@media (max-width:820px){.ask{grid-template-columns:1fr;padding:24px}}
.ask h3{font-size:22px;color:#fff;margin-bottom:10px}.ask ul{margin:0;padding-left:20px;color:#D7E1FA}.ask li{margin:6px 0}
.contact a{display:flex;flex-direction:column;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:10px 14px;margin-bottom:10px;color:#fff;text-decoration:none;font-weight:700;overflow-wrap:anywhere}
.contact a span{font:500 11.5px var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--band-muted)}
.contact a:hover{background:rgba(255,255,255,.14)}
.src{font-size:13.5px;color:var(--muted);margin-top:14px}
footer{margin-top:56px;border-top:1px solid var(--line);color:var(--muted);font-size:14.5px}footer .wrap{padding-top:20px;padding-bottom:28px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
"""


def initiative_page(total, npapers, notes):
    url = SITE_URL + '/initiative.html'
    title = 'Our Initiative: free, bilingual APPSC preparation | Learn with Anil'
    desc = (f'Learn with Anil is a free, bilingual (English and Telugu) practice portal for APPSC Group-II aspirants, '
            f'with {total} official previous questions and low-cost Crisp Notes. Founder: Jupudi Anil Kumar. Partner with us.')
    price = notes[0]['price'] if notes else 49
    mail = (f'mailto:{EMAIL}?subject=' + 'Partnership%20%E2%80%93%20Learn%20with%20Anil')
    wa = f'https://wa.me/{WHATSAPP}?text=' + 'Hi%20Anil%2C%20I%20saw%20the%20Learn%20with%20Anil%20initiative%20and%20would%20like%20to%20talk.'
    ld = [{"@context": "https://schema.org", "@type": "EducationalOrganization", "name": "Learn with Anil", "url": SITE_URL + '/',
           "logo": SITE_URL + '/anil.jpg', "email": EMAIL, "telephone": "+91-94947-92739", "sameAs": [f"https://www.instagram.com/{INSTAGRAM}/"],
           "founder": {"@type": "Person", "name": "Jupudi Anil Kumar", "jobTitle": "UPSC Faculty and Mentor", "image": SITE_URL + '/anil.jpg'},
           "description": desc},
          {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "description": desc}]
    books = ''.join(
        f'<a href="index.html#notes"><img src="{esc(b["cover"])}" alt="" width="560" height="792" loading="lazy">'
        f'<span>{esc(b["title_en"])}<br><small>{esc(b["medium_en"])} · {b["pages"]} pages · ₹{b["price"]}</small></span></a>'
        for b in notes)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow">
<meta property="og:type" content="website"><meta property="og:site_name" content="Learn with Anil">
<meta property="og:title" content="Learn with Anil: quality civil-services prep for every Andhra Pradesh aspirant">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/initiative-og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE_URL}/initiative-og.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@500&family=Source+Sans+3:wght@400;600;700&family=Noto+Sans+Telugu:wght@600&display=swap">
<style>{INIT_CSS}</style>
{''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)}
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="index.html"><i>LA</i><b>Learn with Anil</b></a>
  <nav aria-label="Page"><a href="index.html">Practice portal</a><a href="index.html#notes">Study material</a><a href="#contact">Contact</a></nav>
</div></header>

<section class="hero"><div class="wrap">
  <div>
    <span class="tag">Our initiative</span>
    <h1>Quality civil-services preparation for every Andhra Pradesh aspirant</h1>
    <p class="lede">Learn with Anil is a free, bilingual practice portal for APPSC Group-II. Aspirants practise APPSC's real previous questions with the official answers, in English or Telugu, see exactly where they lose marks, and buy low-cost exam notes when they need them.</p>
    <div class="ctas"><a class="btn b1" href="#contact">Partner with us</a><a class="btn b2" href="index.html">Try the portal</a></div>
  </div>
  <div class="side">
    <div class="ph"><img src="anil.jpg" alt="Jupudi Anil Kumar" width="260" height="260"></div>
    <div class="who"><b>Jupudi Anil Kumar</b><span>Founder · UPSC faculty &amp; mentor</span></div>
  </div>
</div></section>

<section class="blk"><div class="wrap">
  <p class="eyebrow">The problem</p>
  <h2>Lakhs of aspirants, very little free and structured practice</h2>
  <div class="grid3">
    <div class="card"><span class="big">4.83 lakh</span><h3>applicants for 897 posts</h3><p>That was the last APPSC Group-II recruitment. 92,250 candidates were then shortlisted for the Mains. Every mark decides a rank.</p></div>
    <div class="card"><span class="big">PDFs</span><h3>Previous papers are hard to practise</h3><p>APPSC releases question papers and final keys as separate PDF files. Practising them topic by topic, and keeping track of mistakes, is slow manual work.</p></div>
    <div class="card"><span class="big">EN + <span lang="te" style="font-family:'Noto Sans Telugu',sans-serif">తెలుగు</span></span><h3>Two languages, one exam</h3><p>APPSC sets its papers in English and Telugu, so practice material has to work in both. Coaching is costly and mostly in big cities, which leaves many aspirants with scattered free material.</p></div>
  </div>
  <p class="src">Sources: <a href="https://deccanchronicle.com/nation/appsc-releases-hall-tickets-for-group-2-preliminary-examinations-882208" rel="noopener">Deccan Chronicle</a> (4.83 lakh applicants, 897 posts); <a href="https://news.careers360.com/appsc-group-2-mains-admit-card-2025-out-pscapgovin-92250-candidates-appear" rel="noopener">Careers360</a> (92,250 shortlisted for the Mains, February 2025).</p>
</div></section>

<section class="blk"><div class="wrap">
  <p class="eyebrow">What is live today</p>
  <h2>Built and running at learnwithanil.in</h2>
  <div class="stats">
    <div class="card"><span class="big">{total}</span><p>APPSC Group-II previous questions, each with the official final-key answer</p></div>
    <div class="card"><span class="big">{npapers}</span><p>official papers: Screening 2019 &amp; 2024, Mains 2019 &amp; 2025</p></div>
    <div class="card"><span class="big">100%</span><p>of questions available in both English and Telugu</p></div>
    <div class="card"><span class="big">₹0</span><p>for aspirants to practise, with no sign-up needed for quizzes</p></div>
  </div>
  <div class="grid2">
    <div class="card"><h3>Practice portal <span class="pill live">Live</span></h3><p>Topic-wise quiz builder, timed tests, a mistakes notebook, a smart quiz that brings back weak topics, bookmarks and a progress heatmap. Every question has an explanation.</p></div>
    <div class="card"><h3>Crisp Notes 2026-27 <span class="pill live">Ready</span></h3><p>Four study books for Group-II Mains Paper II: AP Economy and Science &amp; Technology, each in English and Telugu medium, with APPSC's previous questions and practice MCQs inside. ₹{price} per book; online sales open soon.</p></div>
  </div>
  <div class="books">{books}</div>
</div></section>

<section class="blk"><div class="wrap">
  <p class="eyebrow">How it sustains itself</p>
  <h2>Free practice, low-cost material, premium guidance</h2>
  <p class="intro">The site is a fast static website with near-zero hosting cost, so the free practice portal can stay free. Revenue comes from what aspirants choose to buy.</p>
  <div class="model">
    <div><p class="eyebrow">Free</p><div class="price">₹0</div><p>Previous-question practice portal in English and Telugu. This brings aspirants in and builds trust.</p></div>
    <div><p class="eyebrow">Study material</p><div class="price">₹{price}</div><p>Crisp Notes books, priced so that any aspirant can afford them. More subjects to follow.</p></div>
    <div><p class="eyebrow">Guidance <span class="pill plan">Planned</span></p><div class="price">Premium</div><p>Test series, Mains answer evaluation and interview guidance, drawing on 1,200+ answer copies evaluated and 95+ mock interviews conducted.</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap">
  <p class="eyebrow">Roadmap</p>
  <h2>Where we are going</h2>
  <div class="road">
    <div class="card now"><h3><span class="dot"></span>Now</h3><ul class="list"><li>Group-II previous-question portal, fully bilingual</li><li>Crisp Notes: AP Economy and Science &amp; Technology</li><li>Daily current affairs on Instagram</li></ul></div>
    <div class="card next"><h3><span class="dot"></span>Next</h3><ul class="list"><li>Online payments and instant download for the notes</li><li>Crisp Notes for the other Group-II Mains sections</li><li>APPSC Group-I previous questions on the portal</li></ul></div>
    <div class="card later"><h3><span class="dot"></span>Later</h3><ul class="list"><li>Online test series with all-AP ranking</li><li>Mains answer-writing evaluation</li><li>Interview guidance programme</li></ul></div>
  </div>
</div></section>

<section class="blk"><div class="wrap">
  <p class="eyebrow">The founder</p>
  <h2>Jupudi Anil Kumar</h2>
  <div class="founder">
    <img src="anil.jpg" alt="Jupudi Anil Kumar" width="200" height="200" loading="lazy">
    <div>
      <p class="role">Academic Manager · UPSC Faculty · Mentor</p>
      <p>A civil-services educator with more than 1,000 hours of classroom teaching for UPSC, APPSC and TGPSC aspirants. He teaches Indian Polity, Governance and Ethics, builds test series and study material, and evaluates Mains answer scripts.</p>
      <p>As Academic Manager, he plans Group-1 and Group-2 programmes and their test series, coordinates a UPSC mock interview programme in Delhi, and mentors aspirants. He started Learn with Anil so that every APPSC aspirant can practise the real previous questions for free and see clearly where they are losing marks.</p>
      <div class="fstats">
        <div><b>1000+</b><span>hours of classroom teaching</span></div>
        <div><b>1200+</b><span>Mains answer copies evaluated</span></div>
        <div><b>70+</b><span>APPSC Group-1 mock interviews</span></div>
        <div><b>25</b><span>UPSC CSE mock interviews, Delhi</span></div>
        <div><b>150+</b><span>educational reels &amp; videos</span></div>
      </div>
    </div>
  </div>
</div></section>

<section class="blk" id="contact"><div class="wrap">
  <p class="eyebrow">Partner with us</p>
  <h2>Help us reach every aspirant in Andhra Pradesh</h2>
  <div class="ask">
    <div>
      <h3>We are open to</h3>
      <ul>
        <li>Early-stage investment to build the test series and expand the notes</li>
        <li>Partnerships with institutes, colleges and libraries across Andhra Pradesh</li>
        <li>Ed-tech, publishing and media partners who want to reach Telugu-medium aspirants</li>
        <li>Sponsors who want to keep the practice portal free</li>
      </ul>
    </div>
    <div class="contact">
      <a href="tel:+919494792739"><span>Phone</span>{PHONE}</a>
      <a href="{wa}" target="_blank" rel="noopener"><span>WhatsApp</span>Message Anil</a>
      <a href="{mail}"><span>Email</span>{EMAIL.replace('@', '@<wbr>')}</a>
      <a href="https://www.instagram.com/{INSTAGRAM}/" target="_blank" rel="noopener"><span>Instagram</span>@{INSTAGRAM}</a>
    </div>
  </div>
</div></section>

<footer><div class="wrap"><span>© {date.today().year} Learn with Anil · Jupudi Anil Kumar</span><span>Not affiliated with APPSC. Questions and answers are from APPSC's official final keys.</span></div></footer>
</body>
</html>
'''


def static_page(rel_depth, title, desc, canonical, h1, lede, body_html, crumbs):
    up = '../' * rel_depth
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": canonical,
          "isPartOf": {"@type": "WebSite", "name": "Learn with Anil", "url": SITE_URL + '/'},
          "author": {"@type": "Person", "name": "Jupudi Anil Kumar"},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": c[0], "item": c[1]} for i, c in enumerate(crumbs)]}}
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canonical)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600&display=swap">
<style>{STATIC_CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header><div class="wrap"><a href="{up}index.html">Learn with Anil · APPSC Group-II PYQs</a><a href="{up}index.html#practice">Practise online →</a></div></header>
<main class="wrap">
<h1>{nw(h1)}</h1>
<p class="lede">{lede}</p>
{body_html}
</main>
<footer><div class="wrap">Questions and answers are taken from APPSC's official final keys. Explanations are by Jupudi Anil Kumar, Learn with Anil (Instagram: @{INSTAGRAM}). Not affiliated with APPSC.</div></footer>
</body>
</html>
"""


def q_html(q, paper_short, num_label):
    parts = [f'<li class="q" id="q{q["n"]}"><div class="meta">{esc(num_label)} · {esc(SUBJ[q["s"]][1])} · {esc(q["t"])}</div>',
             f'<p>{esc(q["q"])}</p>']
    if q.get('img'):
        parts.append(f'<img src="{q["img"]}" alt="Figure for question {q["n"]}" loading="lazy">')
    if q.get('o'):
        parts.append('<ol>' + ''.join(f'<li>{esc(o)}</li>' for o in q['o']) + '</ol>')
        ans = ' / '.join(f'({i + 1}) {q["o"][i]}' for i in q['a'])
    else:
        ans = q['ans']
    if q.get('qt'):
        te = f'<p>{esc(q["qt"])}</p>'
        if q.get('ot'):
            te += '<ol>' + ''.join(f'<li>{esc(o)}</li>' for o in q['ot']) + '</ol>'
        parts.append(f'<div class="te" lang="te">{te}</div>')
    ans_te = ''
    if q.get('ot'): ans_te = ' / '.join(f'({i + 1}) {q["ot"][i]}' for i in q['a'])
    elif q.get('at'): ans_te = q['at']
    te_ans = f'<p class="ans" lang="te">సమాధానం: {esc(ans_te)}</p>' if ans_te else ''
    parts.append(f'<details><summary>Show answer</summary><p class="ans">Answer: {esc(ans)}</p>{te_ans}<p class="why">{esc(q["w"])}</p></details></li>')
    return ''.join(parts)


def build_static(papers, subjects, questions):
    pages = {}
    by_p = {}
    for q in questions: by_p.setdefault(q['p'], []).append(q)
    pmap = {p['id']: p for p in papers}
    for p in papers:
        qs = by_p[p['id']]
        rel = f'papers/{p["slug"]}.html'
        can = f'{SITE_URL}/{rel}'
        fmt = ('All four options with the official answer from the APPSC final key' if p['fmt'] == 'mcq'
               else 'Each question with its official answer from the APPSC final key (the key lists the correct answer only)')
        title = f'{p["title"]} Question Paper with Answers & Explanations | Learn with Anil'
        desc = (f'{p["title"]} ({p["notif"]}, held {p["held"]}): {len(qs)} previous year questions with official '
                f'final-key answers and short explanations, topic-wise. Practise APPSC Group 2 PYQs online free.')
        subs = {}
        for q in qs: subs.setdefault(q['s'], 0); subs[q['s']] += 1
        toc = '<nav class="toc">' + ''.join(
            f'<a href="../subjects/appsc-group-2-{SUBJ[s][2]}-pyqs.html">{esc(SUBJ[s][1])} ({c})</a>' for s, c in subs.items()) + '</nav>'
        body = (f'<a class="cta" href="../index.html#papers">Practise this paper online</a>'
                f'<a class="cta alt" href="../index.html#practice">Make a topic-wise quiz</a>'
                f'<h2>Subjects in this paper</h2>{toc}<h2>All {len(qs)} questions</h2><ol class="qs">'
                + ''.join(q_html(q, p['short'], f'Q{q["n"]}') for q in qs) + '</ol>')
        lede = esc(f'{p["blurb"]} {p["notif"]}, held on {p["held"]}. {fmt}, plus a short explanation for every question.')
        pages[rel] = static_page(1, title, desc, can, f'{p["title"]}: questions with answers', lede, body,
                                 [('Home', SITE_URL + '/'), (p['title'], can)])
    by_s = {}
    for q in questions: by_s.setdefault(q['s'], []).append(q)
    for s in subjects:
        qs = by_s.get(s['id'], [])
        if not qs: continue
        rel = f'subjects/appsc-group-2-{s["slug"]}-pyqs.html'
        can = f'{SITE_URL}/{rel}'
        title = f'APPSC Group 2 {s["name"]} PYQs – Previous Year Questions with Answers | Learn with Anil'
        desc = (f'{len(qs)} APPSC Group-II {s["name"]} previous year questions from {", ".join(sorted({pmap[q["p"]]["short"] for q in qs}))}, '
                f'arranged topic-wise with official answers and explanations.')
        body = [f'<a class="cta" href="../index.html#practice">Practise {esc(s["name"])} online</a>']
        tops = {}
        for q in qs: tops.setdefault(q['t'], []).append(q)
        body.append('<nav class="toc">' + ''.join(f'<a href="#t{i}">{esc(t)} ({len(tops[t])})</a>' for i, t in enumerate(s['topics']) if t in tops) + '</nav>')
        for i, t in enumerate(s['topics']):
            if t not in tops: continue
            body.append(f'<h2 id="t{i}">{esc(t)}</h2><ol class="qs">' + ''.join(
                q_html(q, pmap[q['p']]['short'], f'{pmap[q["p"]]["short"]} · Q{q["n"]}') for q in tops[t]) + '</ol>')
        lede = esc(f'Every {s["name"]} question asked in the APPSC Group-II papers on this site, grouped by topic. '
                   f'Answers come from APPSC\'s final keys; each has a short explanation.')
        pages[rel] = static_page(1, title, desc, can, f'APPSC Group-II {s["name"]} PYQs', lede, ''.join(body),
                                 [('Home', SITE_URL + '/'), (s['name'], can)])
    return pages


if __name__ == '__main__':
    main()
