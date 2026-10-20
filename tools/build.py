#!/usr/bin/env python3
"""Build the Learn with Anil PYQ site (exam hub + APPSC Group-II at the root, APPSC Group-I under /appsc-group-1/).

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
SHOW_TIMERS = False   # exam countdown cards on the start page (dates stay in src/exams.json); Anil asked to remove them, 20 Oct 2026

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

# ---------- APPSC Group-I (Prelims) ----------
G1_PAPERS = [
  dict(id='p2024a', file='prelims-2024-p1.txt', year=2024, stage='Prelims Paper I', short='Prelims 2024 · P-I',
       title='APPSC Group-I Prelims 2024 Paper I', notif='Notification 12/2023', held='17 March 2024',
       fmt='mcq', slug='appsc-group-1-prelims-2024-paper-1-general-studies-question-paper-with-answers',
       blurb='General Studies: History & Culture, Polity & International Relations, Indian & AP Economy, and Geography (30 questions each).'),
  dict(id='p2024b', file='prelims-2024-p2.txt', year=2024, stage='Prelims Paper II', short='Prelims 2024 · P-II',
       title='APPSC Group-I Prelims 2024 Paper II', notif='Notification 12/2023', held='17 March 2024',
       fmt='mcq', slug='appsc-group-1-prelims-2024-paper-2-general-aptitude-question-paper-with-answers',
       blurb='General Aptitude: Mental Ability, Administrative & Psychological Abilities, Science & Technology, and Current Events.'),
  dict(id='p2023a', file='prelims-2023-p1.txt', year=2023, stage='Prelims Paper I', short='Prelims 2023 · P-I',
       title='APPSC Group-I Prelims 2023 Paper I', notif='Notification 28/2022', held='8 January 2023',
       fmt='recall', slug='appsc-group-1-prelims-2023-paper-1-general-studies-questions-with-answers',
       blurb='General Studies: History & Culture, Polity & International Relations, Indian & AP Economy, and Geography.'),
  dict(id='p2023b', file='prelims-2023-p2.txt', year=2023, stage='Prelims Paper II', short='Prelims 2023 · P-II',
       title='APPSC Group-I Prelims 2023 Paper II', notif='Notification 28/2022', held='8 January 2023',
       fmt='recall', slug='appsc-group-1-prelims-2023-paper-2-general-aptitude-questions-with-answers',
       blurb='General Aptitude: Mental Ability, Administrative & Psychological Abilities, Science & Technology, and Current Events.'),
  dict(id='p2019a', file='prelims-2019-p1.txt', year=2019, stage='Prelims Paper I', short='Prelims 2019 · P-I',
       title='APPSC Group-I Prelims 2019 Paper I', notif='Notification 27/2018', held='26 May 2019',
       fmt='recall', slug='appsc-group-1-prelims-2019-paper-1-general-studies-questions-with-answers',
       blurb='General Studies: History & Culture, Polity & International Relations, Indian & AP Economy, and Geography.'),
  dict(id='p2019b', file='prelims-2019-p2.txt', year=2019, stage='Prelims Paper II', short='Prelims 2019 · P-II',
       title='APPSC Group-I Prelims 2019 Paper II', notif='Notification 27/2018', held='26 May 2019',
       fmt='recall', slug='appsc-group-1-prelims-2019-paper-2-general-aptitude-questions-with-answers',
       blurb='General Aptitude: Mental Ability, Administrative & Psychological Abilities, Science & Technology, and Current Events.'),
]

G1_SUBJECTS = [
  ('ih',  'History & Culture', 'history-culture', ['Ancient India', 'Medieval India', 'Modern India', 'Art & Culture', 'Andhra History']),
  ('pol', 'Polity, Social Justice & IR', 'polity-social-justice-international-relations', ['Constitution Basics & Preamble', 'Fundamental Rights & Duties', 'DPSP', 'Union Executive', 'Parliament', 'State Government', 'Judiciary', 'Federalism & Centre-State Relations', 'Local Government', 'Constitutional & Statutory Bodies', 'Amendments & Governance', 'Social Justice & Welfare', 'International Relations']),
  ('eco', 'Indian & AP Economy', 'indian-ap-economy', ['Planning & Development', 'National Income & Growth', 'Money, Banking & Inflation', 'Public Finance & Taxation', 'Agriculture', 'Industry & Infrastructure', 'Poverty, Employment & Population', 'External Sector', 'AP Economy']),
  ('geo', 'Geography', 'geography', ['Physical Geography', 'World Geography', 'Indian Geography', 'AP Geography', 'Environment & Ecology']),
  ('men', 'Mental Ability & Reasoning', 'mental-ability-reasoning', ['Numbers & Series', 'Reasoning', 'Arithmetic', 'Data Interpretation & Sufficiency']),
  ('apt', 'Administrative & Psychological Abilities', 'administrative-psychological-abilities', ['Administrative Abilities', 'Psychological Abilities']),
  ('sci', 'Science & Technology', 'science-technology', ['General Science', 'Space Technology', 'Defence Technology', 'Biotechnology & Health', 'IT & Communication', 'Energy', 'Environment & Ecology', 'Agriculture & Food']),
  ('cur', 'Current Affairs', 'current-affairs', ['National', 'International', 'AP Affairs', 'Sports', 'Awards & Personalities', 'Reports & Indices']),
]


# ---------- UPSC CAPF (AC) ----------
CAPF_PAPERS = [
  dict(id='c2026a', file='capf-2026-paper-1.txt', year=2026, stage='Paper I', short='CAPF 2026 · P-I',
       title='UPSC CAPF (AC) 2026 Paper I', notif='Series A · provisional key', held='19 July 2026',
       fmt='mcq', slug='upsc-capf-ac-2026-paper-1-general-ability-intelligence-question-paper-with-answers',
       blurb='General Ability & Intelligence: General Mental Ability, General Science, Current Events, Indian Polity & Economy, History and Geography (125 questions, 250 marks).'),
]

CAPF_SUBJECTS = [
  ('cur', 'Current Affairs', 'current-affairs', ['National', 'International', 'Sports', 'Awards & Personalities', 'Reports & Indices', 'Defence & Security']),
  ('ih',  'History', 'history', ['Ancient India', 'Medieval India', 'Modern India', 'Art & Culture', 'World History']),
  ('pol', 'Indian Polity', 'indian-polity', ['Constitution & Rights', 'Union & State Government', 'Judiciary', 'Federalism & Local Government', 'Constitutional & Statutory Bodies', 'Governance & Schemes']),
  ('eco', 'Indian Economy', 'indian-economy', ['Growth, Planning & National Income', 'Money, Banking & Inflation', 'Public Finance & Taxation', 'Agriculture & Industry', 'External Sector & Trade', 'Poverty, Employment & Welfare']),
  ('geo', 'Geography', 'geography', ['Physical Geography', 'Indian Geography', 'World Geography', 'Environment & Ecology']),
  ('sci', 'General Science', 'general-science', ['Physics', 'Chemistry', 'Biology', 'Science & Technology']),
  ('men', 'General Mental Ability', 'general-mental-ability', ['Numbers & Series', 'Reasoning', 'Arithmetic', 'Data Interpretation']),
]

# second language of each exam (the question booklet's other language)
L2_TE = dict(code='te', dir='te', label='తెలుగు', name='Telugu', font='Noto Sans Telugu', ans='సమాధానం', gf='')
L2_HI = dict(code='hi', dir='hi', label='हिंदी', name='Hindi', font='Noto Sans Devanagari', ans='उत्तर',
             gf='&family=Noto+Sans+Devanagari:wght@400;500;600;700')


def parse(paper, srcdir='', subj=SUBJ):
    path = os.path.join(SRC, srcdir, paper['file'])
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
        if s not in subj: errs.append(f'{paper["id"]} Q{n}: unknown subject {s}')
        elif t not in subj[s][3]: errs.append(f'{paper["id"]} Q{n}: unknown topic {s}/{t}')
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


def parse_te(paper, qs, srcdir='', l2dir='te'):
    """Merge the official second-language text (Telugu, or Hindi for UPSC) from src/[<exam>/]<l2dir>/<file>
    into the parsed questions (fields qt/ot/at). Format: 'Q <n>' line, then question lines, then optional
    '(1)'..'(4)' options, and for answer-only papers an optional '= <answer>' line."""
    path = os.path.join(SRC, srcdir, l2dir, paper['file'])
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


def load_exam(conf):
    """Parse one live exam's papers. Returns (papers, questions)."""
    subj = {s[0]: s for s in conf['subjects']}
    papers, questions = [], []
    for p in conf['papers']:
        qs = parse(p, conf['src'], subj)
        nte = parse_te(p, qs, conf['src'], conf['l2']['dir'])
        if nte: print(f'  {conf["short"]} {p["id"]}: {conf["l2"]["name"]} for {nte} questions')
        if not qs:
            print(f'  - skipping {conf["short"]} {p["id"]} (no source yet)'); continue
        for q in qs:
            if 'img' in q: q['img'] = img_data_uri(os.path.join(conf['src'], q['img']))
        pp = {k: p[k] for k in ('id', 'year', 'stage', 'short', 'title', 'notif', 'held', 'fmt', 'slug', 'blurb')}
        pp['count'] = len(qs)
        papers.append(pp); questions += qs
        print(f'  {conf["short"]} {p["id"]}: {len(qs)} questions')
    return papers, questions


def qotd_pool(items, n):
    """Question-of-the-day list: four-option questions without figures, short enough for a phone screen and a
    share image, shuffled once (fixed seed) and interleaved across exams. The page picks one per day (India time)."""
    import random
    pools = []
    for conf, papers, questions in items:
        pshort = {p['id']: p['short'] for p in papers}
        el = [q for q in questions if q.get('o') and not q.get('img') and q.get('w') and len(q['q']) <= 520
              and all(len(o) <= 140 for o in q['o'])]
        random.Random('qotd-' + conf['id']).shuffle(el)
        base = conf['dir'] + '/' if conf['dir'] else ''
        pools.append([dict(id=q['id'], ex=conf['short'], exName=conf['name'], base=base, paper=pshort[q['p']], l2=conf['l2']['code'],
                           q=q['q'], qt=q.get('qt', ''), o=q['o'], ot=q.get('ot'), a=q['a'], w=q['w']) for q in el])
    out, i = [], 0
    while len(out) < n and any(i < len(p) for p in pools):
        for p in pools:
            if i < len(p): out.append(p[i])
        i += 1
    return out[:n]


def exam_confs():
    return [
      dict(id='appsc-group-2', dir='', src='', key='appsc-g2', name='APPSC Group-II', short='Group-II', seo='APPSC Group 2',
           slugp='appsc-group-2', papers=PAPERS, subjects=SUBJECTS, faq=FAQ, board='APPSC', l2=L2_TE,
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           eyebrow='APPSC Group-II · Screening &amp; Mains · 2019–2025',
           papers_note="Every paper uses APPSC's official final key. The 2024 and 2025 keys show all four options. The 2019 keys print only the correct answer, so those questions appear as quick-recall cards: think of the answer, reveal it, then mark yourself."),
      dict(id='appsc-group-1', dir='appsc-group-1', src='appsc-group-1', key='appsc-g1', name='APPSC Group-I', short='Group-I', seo='APPSC Group 1',
           slugp='appsc-group-1', papers=G1_PAPERS, subjects=G1_SUBJECTS, faq=FAQ_G1, board='APPSC', l2=L2_TE,
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           title='APPSC Group 1 PYQs – Prelims Previous Question Papers with Answers (2019–2024) | Learn with Anil',
           eyebrow='APPSC Group-I · Prelims · 2019–2024',
           papers_note="Every paper uses APPSC's official final key. The 2024 key shows all four options. The 2023 and 2019 keys print only the correct answer, so those questions appear as quick-recall cards: think of the answer, reveal it, then mark yourself."),
      dict(id='upsc-capf', dir='upsc-capf', src='upsc-capf', key='upsc-capf', name='UPSC CAPF (AC)', short='CAPF (AC)', seo='UPSC CAPF AC',
           slugp='upsc-capf-ac', papers=CAPF_PAPERS, subjects=CAPF_SUBJECTS, faq=FAQ_CAPF, board='UPSC', l2=L2_HI,
           keyname="UPSC's official provisional answer key", keyshort="UPSC's provisional answer key",
           title='UPSC CAPF AC PYQs – 2026 Paper I Question Paper with Answers in English & Hindi | Learn with Anil',
           eyebrow='UPSC CAPF (Assistant Commandants) · Paper I · 2026',
           papers_note="The 2026 Paper I uses UPSC's provisional answer key for Series A, published three days after the exam. UPSC dropped question 41, so it is left out. UPSC's final key may still differ for a few questions. Every question is in English and Hindi, as printed in the booklet."),
    ]


def main():
    confs = exam_confs()
    loaded = []
    for c in confs:
        papers, questions = load_exam(c)
        if questions: loaded.append((c, papers, questions))
    counts = {c['id']: len(qs) for c, _, qs in loaded}
    grand = sum(counts.values())

    vpath = os.path.join(SRC, 'videos.json')
    videos = json.load(open(vpath, encoding='utf-8')) if os.path.exists(vpath) else {}
    npath = os.path.join(SRC, 'notes.json')
    notes = json.load(open(npath, encoding='utf-8')) if os.path.exists(npath) else []
    epath = os.path.join(SRC, 'exams.json')
    catalog = json.load(open(epath, encoding='utf-8')) if os.path.exists(epath) else dict(cats=[], exams=[])
    # an exam tile is live only if its questions were built
    for e in catalog['exams']:
        if e.get('live') and e['id'] not in counts: e.pop('live')
    photo_uri, photo_bytes = photo_data_uri()
    tpl = open(os.path.join(ROOT, 'tools', 'app.html'), encoding='utf-8').read()
    head, body = tpl.split('<!--BODY-->')
    live_names = [c['name'] for c, _, _ in loaded]
    nav_extra = ''.join(f'      <a href="{c["dir"]}/" data-hubonly>{esc(c["short"])}</a>\n' for c, _, _ in loaded if c['dir'])
    hub_ctas = ''.join(f'<a class="btn btn-primary" href="{"#home" if c["dir"] == "" else c["dir"] + "/"}">{esc(c["name"])}</a>' for c, _, _ in loaded)
    live_list = [c['name'] for c, _, _ in loaded]
    live_summary = (f'Live now: {", ".join(live_list[:-1]) + " and " + live_list[-1] if len(live_list) > 1 else live_list[0]} '
                    f'previous question papers, {grand:,} questions in all; the other exams are being added one by one.')

    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'site')); os.makedirs(os.path.join(DIST, 'artifact'))
    open(os.path.join(DIST, 'site', 'anil.jpg'), 'wb').write(photo_bytes)
    all_pages = {}

    for conf, papers, questions in loaded:
        is_root = conf['dir'] == ''
        prefix = conf['dir'] + '/' if conf['dir'] else ''
        up = '' if is_root else '../'
        hubhref = '#exams' if is_root else '../#exams'
        subjects = [dict(id=s[0], name=s[1], slug=s[2], topics=s[3]) for s in conf['subjects']]
        subj = {s[0]: s for s in conf['subjects']}
        def upath(x): return x if (is_root or re.match(r'(https?:|data:|/)', x)) else up + x
        enotes = [dict(b, cover=upath(b['cover']), samples=[upath(x) for x in b.get('samples', [])]) for b in notes]
        for q in questions:
            if q['id'] in videos and is_root: q['v'] = videos[q['id']]
        data = dict(papers=papers, subjects=subjects, questions=questions, instagram=INSTAGRAM, site=SITE_URL, notes=enotes, wa=WHATSAPP,
                    key=conf['key'], exam=conf['name'], examShort=conf['short'], papersNote=conf['papers_note'], hub=is_root,
                    board=conf['board'], l2={k: conf['l2'][k] for k in ('code', 'label', 'name', 'font')},
                    base=prefix, qotd=qotd_pool(loaded if is_root else [(conf, papers, questions)], 120 if is_root else 90),
                    exams=catalog['exams'] if is_root else [], cats=catalog['cats'] if is_root else [],
                    timers=catalog.get('timers', []) if (is_root and SHOW_TIMERS) else [])
        data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        total = len(questions)
        home_papers = ''.join(home_paper_card(p) for p in sorted(papers, key=lambda p: (-p['year'], p['id'])))
        scount = {}
        for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
        home_subjects = ''.join(
            f'<button type="button" class="card subj-card" data-act="presubj" data-subj="{s["id"]}"><span>{esc(s["name"])}</span><span class="mono">{scount[s["id"]]} Q</span></button>'
            for s in subjects if scount.get(s['id']))
        faq = conf['faq'](total, len(papers))
        faq_html = ''.join(f'<details><summary>{esc(qq)}</summary><p>{esc(aa)}</p></details>' for qq, aa in faq)
        hub = hub_html(catalog, counts, grand) if is_root else ''
        timers = timers_html(catalog) if (is_root and SHOW_TIMERS) else ''

        l2 = conf['l2']
        if conf['board'] == 'APPSC':
            all_link = f'<a href="{up}appsc-pyqs.html" style="color:inherit">All APPSC previous question papers (Group 1 &amp; Group 2) →</a>'
        else:
            all_link = f'<a href="{up}#exams" style="color:inherit">All exams on Learn with Anil: APPSC Group 1, Group 2 and more →</a>'

        def fill(s, photo, title, seo, desc=''):
            return (s.replace('{{SEO_HEAD}}', seo).replace('{{TITLE}}', title).replace('{{DESC}}', esc(desc))
                     .replace('{{L2CODE}}', l2['code']).replace('{{L2LABEL}}', l2['label']).replace('{{FONTS2}}', l2['gf'])
                     .replace('{{LANGS}}', 'English and ' + l2['name']).replace('{{KEYSHORT}}', conf['keyshort'])
                     .replace('{{BOARD}}', conf['board']).replace('{{ALLLINK}}', all_link)
                     .replace('{{FOOTSRC}}', 'Questions and answers are from the official final keys.' if conf['board'] == 'APPSC'
                              else f'Questions are from {conf["board"]}\'s official question paper; answers from {conf["keyshort"]}.')
                     .replace('{{FROMPAPERS}}', f'{len(papers)} official papers' if len(papers) > 1 else f'the official {esc(papers[0]["title"])} paper')
                     .replace('{{PAPERSK}}', f'Official {conf["board"]} paper' + ('s' if len(papers) > 1 else ''))
                     .replace('{{HOME_PAPERS}}', home_papers).replace('{{HOME_SUBJECTS}}', home_subjects).replace('{{FAQ}}', faq_html)
                     .replace('{{DATA}}', data_json).replace('{{PHOTO}}', photo)
                     .replace('{{TOTAL}}', str(total)).replace('{{SITE}}', SITE_URL).replace('{{NPAPERS}}', str(len(papers)))
                     .replace('{{HOME_NOTES}}', home_notes(enotes)).replace('{{HUB}}', hub)
                     .replace('{{NEXAMS}}', str(len(catalog['exams']))).replace('{{TOTALC}}', f'{grand:,}')
                     .replace('{{LIVE_SUMMARY}}', esc(live_summary))
                     .replace('{{HUB_CTAS}}', hub_ctas)
                     .replace('{{NAV_EXTRA}}', nav_extra if is_root else '')
                     .replace('{{TIMERS}}', timers).replace('{{HUBHREF}}', hubhref).replace('{{ROOTUP}}', up)
                     .replace('{{EXAM}}', esc(conf['name'])).replace('{{EXAMSHORT}}', esc(conf['short']))
                     .replace('{{EYEBROW}}', conf['eyebrow']))
        if is_root:
            site_title = 'APPSC PYQs Free – Group 1 & Group 2 Previous Question Papers with Answers | Learn with Anil'
            site_desc = (f'Free APPSC PYQs: {grand:,} previous year questions from APPSC Group 1 and Group 2 question papers (2019–2025) '
                         f'and UPSC CAPF (AC) 2026, with official-key answers and explanations in English, Telugu and Hindi. Practise online topic-wise. '
                         f'TGPSC, UPSC, SSC, banking and railway exams are being added.')
            canon = SITE_URL + '/'
        else:
            site_title = conf['title']
            ptxt = f'{len(papers)} official papers' if len(papers) > 1 else f'the official {papers[0]["title"]} paper'
            site_desc = (f'{total} {conf["name"]} previous year questions from {ptxt}, with answers from {conf["keyshort"]} '
                         f'and explanations, in English and {l2["name"]}. Practise topic-wise quizzes and timed tests free.')
            canon = f'{SITE_URL}/{prefix}'
        ld = [
          {"@context":"https://schema.org","@type":"WebSite","name":"Learn with Anil","alternateName":"Learn with Anil – Previous year questions for every exam","url":SITE_URL+'/'},
          {"@context":"https://schema.org","@type":"Person","name":"Jupudi Anil Kumar","jobTitle":"UPSC Faculty and Mentor","telephone":"+91-94947-92739","email":"mailto:anilkumarjupudi360360@gmail.com","url":SITE_URL+'/#about',"image":SITE_URL+'/anil.jpg',"sameAs":[f"https://www.instagram.com/{INSTAGRAM}/"]},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in faq]},
        ]
        if not is_root: ld = ld[1:]
        seo = (f'<link rel="canonical" href="{canon}">\n<meta name="robots" content="index,follow">\n'
               f'<meta property="og:type" content="website"><meta property="og:site_name" content="Learn with Anil">'
               f'<meta property="og:title" content="{esc(site_title)}"><meta property="og:description" content="{esc(site_desc)}">'
               f'<meta property="og:url" content="{canon}"><meta property="og:image" content="{SITE_URL}/anil.jpg">'
               f'<meta name="twitter:card" content="summary">\n'
               + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld))
        outdir = os.path.join(DIST, 'site', conf['dir'])
        os.makedirs(os.path.join(outdir, 'papers'), exist_ok=True); os.makedirs(os.path.join(outdir, 'subjects'), exist_ok=True)
        if is_root:
            # artifact page: fragment (publisher adds the skeleton); photo inline
            os.makedirs(os.path.join(DIST, 'artifact', 'papers')); os.makedirs(os.path.join(DIST, 'artifact', 'subjects'))
            open(os.path.join(DIST, 'artifact', 'index.html'), 'w', encoding='utf-8').write(fill(head + body, photo_uri, 'Learn with Anil', '', site_desc))
        doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
               + fill(head, up + 'anil.jpg', site_title, seo, site_desc).replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
               + '\n</head>\n<body>\n' + fill(body, up + 'anil.jpg', site_title, seo, site_desc) + '\n</body>\n</html>\n')
        open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8').write(doc)
        # crawlable pages per paper and per subject
        pages = build_static(conf, papers, subjects, questions, subj)
        for rel, content in pages.items():
            open(os.path.join(outdir, rel), 'w', encoding='utf-8').write(content)
            if is_root: open(os.path.join(DIST, 'artifact', rel), 'w', encoding='utf-8').write(content)
        if not is_root: all_pages[prefix] = None
        for rel in pages: all_pages[prefix + rel] = None
        print(f'  {conf["name"]}: {total} questions, {len(pages)} static pages')

    # one crawlable page listing every APPSC paper (the page people land on from "APPSC PYQs" searches)
    hubrel = 'appsc-pyqs.html'
    open(os.path.join(DIST, 'site', hubrel), 'w', encoding='utf-8').write(appsc_pyqs_page(loaded, grand))
    all_pages = {hubrel: None, **all_pages}

    # sitemap + robots (site only)
    today = date.today().isoformat()
    urls = [SITE_URL + '/'] + [SITE_URL + '/' + rel for rel in all_pages]
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
    print(f'  grand total {grand} questions, {len(all_pages)} static pages')


def home_notes(notes):
    if not notes: return ''
    covers = ''.join(f'<img src="{esc(b["cover"])}" alt="" width="140" height="198" loading="lazy">' for b in notes)
    return f'''<section class="wrap section">
    <a class="card notes-promo" href="#notes">
      <div class="np-copy"><p class="eyebrow">New · Study material</p><h2>Study material 2026-27</h2>
      <p>{esc(" and ".join(dict.fromkeys(b.get("subject_label", b["subject"]) for b in notes)))} for APPSC Mains, with the latest 2026 data and APPSC's own previous questions inside. From ₹{min(b["price"] for b in notes)}.</p>
      <span class="btn btn-primary">See the books</span></div>
      <div class="np-covers" aria-hidden="true">{covers}</div>
    </a>
  </section>'''


ROMAN = {'I': '1', 'II': '2', 'III': '3', 'IV': '4'}


def exam_terms(e, cat):
    """Lower-case words a student might type to find this exam (used by the search box)."""
    words = [e['b'], e['t'], e.get('n', ''), cat['name'], e['id'].replace('-', ' ')]
    m = re.search(r'Group-(I{1,3}|IV)\b', e['t'])
    if m:
        d = ROMAN[m.group(1)]
        words += [f'group {d}', f'group{d}', f'group-{d}', f'group {m.group(1)}']
    if e['cat'] == 'tg': words += ['tspsc', 'tgpsc', 'telangana']
    if e['cat'] == 'ap': words += ['appsc', 'andhra']
    return ' '.join(w.lower() for w in words if w)


def live_href(e):
    """Where a live exam tile points: a hash in this page ('home') or another page ('appsc-group-1/')."""
    return e['live'] if '/' in e['live'] else '#' + e['live']


def hub_html(catalog, counts, grand):
    cats = catalog['cats']; byc = {c['id']: c for c in cats}
    chips = (f'<button type="button" class="chip" data-act="excat" data-cat="all" aria-pressed="true">All exams <span class="n">{len(catalog["exams"])}</span></button>'
             + ''.join(f'<button type="button" class="chip" data-act="excat" data-cat="{c["id"]}" aria-pressed="false">{esc(c["name"])} '
                       f'<span class="n">{sum(1 for e in catalog["exams"] if e["cat"] == c["id"])}</span></button>' for c in cats))
    secs = []
    for c in cats:
        tiles = []
        for e in [e for e in catalog['exams'] if e['cat'] == c['id']]:
            live = bool(e.get('live'))
            href = live_href(e) if live else '#exam/' + e['id']
            status = f'Live · {counts.get(e["id"], 0):,} questions' if live else 'Coming soon'
            sub = f'<span class="ex-n">{esc(e["n"])}</span>' if e.get('n') else ''
            tiles.append(f'<a class="card exam{" live" if live else ""}" href="{href}" data-cat="{c["id"]}" data-s="{esc(exam_terms(e, c))}">'
                         f'<span class="ex-b">{esc(e["b"])}</span><span class="ex-t">{nw(e["t"])}</span>{sub}<span class="ex-st">{status}</span></a>')
        te = f' <span class="te-sub" lang="te">{esc(c["te"])}</span>' if c.get('te') else ''
        secs.append(f'<section class="exam-cat" data-cat="{c["id"]}"><div class="section-title"><h2>{esc(c["name"])}{te}</h2>'
                    f'<span class="muted" style="font-size:14px">{esc(c["desc"])}</span></div><div class="exams">{"".join(tiles)}</div></section>')
    search = ('<label class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="color:var(--muted)">'
              '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4" stroke-linecap="round"/></svg>'
              '<input id="examSearch" type="search" placeholder="Search an exam, e.g. Group-II, CGL, NDA, Police SI" aria-label="Search exams" autocomplete="off"></label>')
    return (f'<div class="hub-tools">{search}<div class="chips" role="group" aria-label="Filter exams">{chips}</div></div>'
            f'<p class="muted" id="hubCount" style="font-size:14px"></p>'
            f'<div id="hubCats">{"".join(secs)}</div>'
            f'<div class="card empty" id="hubEmpty" hidden><h3>No exam matches your search</h3>'
            f'<p>Tell Anil which exam you are preparing for, and it will be added to the list.</p>'
            f'<div class="row" style="justify-content:center"><a class="btn btn-primary" id="hubAsk" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">Ask on WhatsApp</a></div></div>')


def timers_html(catalog):
    """Countdown cards for important upcoming exams (the page script fills in the time left and hides past ones)."""
    timers = [t for t in catalog.get('timers', []) if t['date'] >= date.today().isoformat()]
    if not timers: return ''
    ex = {e['id']: e for e in catalog['exams']}
    cards = []
    for t in timers:
        d = date.fromisoformat(t['date'])
        e = ex.get(t['exam'], {})
        href = live_href(e) if e.get('live') else '#exam/' + t['exam']
        cards.append(f'<a class="card cdown" href="{href}" data-date="{t["date"]}T00:00:00+05:30">'
                     f'<span class="tm-label">{esc(t["label"])}</span>'
                     f'<span class="tm-date">{d.strftime("%a, %d %b %Y")}</span>'
                     f'<span class="tm-count"><b class="tm-d">–</b> days <span class="tm-hms">--:--:--</span></span></a>')
    return (f'<section class="wrap timers-wrap" id="timers" aria-label="Exam countdown">'
            f'<div class="timers-head"><span class="eyebrow">Exam countdown</span>'
            f'<span class="muted tm-note">Dates from the official calendars and notifications. They can change, so confirm on the official website.</span></div>'
            f'<div class="timers">{"".join(cards)}</div></section>')


def nw(t):
    return re.sub(r'Group-(I{1,3}|IV)\b', r'<span class="nw">Group-\1</span>', esc(t))


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


def FAQ_G1(total, npapers):
    return [
      ('Where can I get APPSC Group 1 previous year question papers with answers?',
       f'This page has {total} questions from {npapers} APPSC Group-I Prelims papers: Paper I (General Studies) and Paper II (General Aptitude) of the 2024 exam, and the 2023 and 2019 Prelims papers. Every answer is taken from APPSC\'s official final key, and each question has a short explanation. You can read each paper with answers or practise it as a quiz, free.'),
      ('What is the APPSC Group 1 Prelims exam pattern?',
       'The Preliminary Examination has two objective papers on the same day: Paper I General Studies (History and Culture; Constitution, Polity, Social Justice and International Relations; Indian and AP Economy and Planning; Geography) and Paper II General Aptitude (General Mental Ability, Administrative and Psychological Abilities; Science and Technology; Current Events). Each paper has 120 questions for 120 marks in 120 minutes, and one-third of the marks of a question is deducted for a wrong answer. Prelims marks are used only to shortlist candidates for the Mains.'),
      ('Are the answers on this site official?',
       'Yes. The answers come from the final keys published by APPSC. Questions that APPSC deleted are left out, and where the final key accepted two options, both are shown as correct. The explanations are written by Learn with Anil.'),
      ('Why do the 2023 and 2019 questions not show four options?',
       'APPSC\'s 2023 and 2019 final keys print each question with only the correct answer. Those questions appear here as quick-recall cards: you think of the answer, reveal it and mark whether you knew it. The 2024 papers show all four options.'),
      ('Do I need to sign up?',
       'No. The portal is free and practice needs no account. Before your first timed test you enter your name, phone, email and district once, so your test scores are saved with Learn with Anil and Anil can guide you. Your practice attempts, mistakes notebook and bookmarks stay in your own browser on your device.'),
    ]


def FAQ_CAPF(total, npapers):
    return [
      ('Where can I get UPSC CAPF AC previous year question papers with answers?',
       f'This page has {total} questions from the UPSC CAPF (Assistant Commandants) 2026 Paper I, General Ability and Intelligence, in English and Hindi as printed in the official question booklet. The answers come from UPSC\'s provisional answer key (Series A), and every question has a short explanation. You can read the paper with answers or practise it as a quiz, free.'),
      ('What is the UPSC CAPF AC exam pattern?',
       'The written exam has two papers on the same day. Paper I, General Ability and Intelligence, is objective, carries 250 marks and lasts two hours; the 2026 paper had 125 questions, in English and Hindi. It covers General Mental Ability, General Science, Current Events of national and international importance, Indian Polity and Economy, History of India, and Indian and World Geography. A wrong answer costs one-third of the marks for that question. Paper II, General Studies, Essay and Comprehension, is descriptive and carries 200 marks. Candidates who qualify take physical and medical standards tests and then an interview.'),
      ('Are the answers on this site official?',
       'They come from the provisional answer key that UPSC published on its website after the 2026 exam. Question 41, which UPSC dropped, is left out. UPSC\'s final key can differ for a few questions. The explanations are written by Learn with Anil.'),
      ('Can I practise the CAPF questions in Hindi?',
       'Yes. Tap हिंदी at the top of the page to see every question and option in Hindi, exactly as printed in UPSC\'s booklet. Tap EN to switch back.'),
      ('Do I need to sign up?',
       'No. The portal is free and practice needs no account. Before your first timed test you enter your name, phone, email and district once, so your test scores are saved with Learn with Anil and Anil can guide you. Your practice attempts, mistakes notebook and bookmarks stay in your own browser on your device.'),
    ]


STATIC_CSS = """
.nw{white-space:nowrap}
[lang="te"]{font-family:"Noto Sans Telugu",sans-serif;line-height:1.8}
[lang="hi"]{font-family:"Noto Sans Devanagari",sans-serif;line-height:1.75}
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


def static_page(rel_depth, title, desc, canonical, h1, lede, body_html, crumbs, conf=None, ename=None):
    ename = ename or (conf['name'] if conf else 'APPSC Group-II')
    rootup = '../' * (rel_depth + (1 if conf and conf.get('dir') else 0))
    up = '../' * rel_depth
    board = conf['board'] if conf else 'APPSC'
    gf = conf['l2']['gf'] if conf else ''
    if board == 'APPSC':
        foot = (f'Questions and answers are taken from APPSC\'s official final keys. Explanations are by Jupudi Anil Kumar, '
                f'Learn with Anil (Instagram: @{INSTAGRAM}). Not affiliated with APPSC.')
    else:
        foot = (f'Questions are from {board}\'s official question paper and answers from {conf["keyshort"]}. Explanations are by '
                f'Jupudi Anil Kumar, Learn with Anil (Instagram: @{INSTAGRAM}). Not affiliated with {board}.')
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600{gf}&display=swap">
<style>{STATIC_CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header><div class="wrap"><a href="{up}index.html#home">Learn with Anil · {nw(ename)} PYQs</a><a href="{up}index.html#practice">Practise online →</a></div></header>
<main class="wrap">
<h1>{nw(h1)}</h1>
<p class="lede">{lede}</p>
{body_html}
</main>
<footer><div class="wrap"><p style="margin:0 0 8px"><a href="{rootup}appsc-pyqs.html">All APPSC previous question papers (PYQs)</a> · <a href="{rootup}appsc-group-1/">APPSC Group-I</a> · <a href="{rootup}index.html#home">APPSC Group-II</a> · <a href="{rootup}upsc-capf/">UPSC CAPF (AC)</a> · <a href="{rootup}index.html#exams">All exams</a></p>{foot}</div></footer>
</body>
</html>
"""


def q_html(q, paper_short, num_label, subj=SUBJ, l2=L2_TE):
    parts = [f'<li class="q" id="q{q["n"]}"><div class="meta">{esc(num_label)} · {esc(subj[q["s"]][1])} · {esc(q["t"])}</div>',
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
        parts.append(f'<div class="te" lang="{l2["code"]}">{te}</div>')
    ans_te = ''
    if q.get('ot'): ans_te = ' / '.join(f'({i + 1}) {q["ot"][i]}' for i in q['a'])
    elif q.get('at'): ans_te = q['at']
    te_ans = f'<p class="ans" lang="{l2["code"]}">{l2["ans"]}: {esc(ans_te)}</p>' if ans_te else ''
    parts.append(f'<details><summary>Show answer</summary><p class="ans">Answer: {esc(ans)}</p>{te_ans}<p class="why">{esc(q["w"])}</p></details></li>')
    return ''.join(parts)


def appsc_pyqs_page(loaded, grand):
    """Landing page for 'APPSC PYQs' searches: every APPSC paper and subject page, Group-I and Group-II."""
    loaded = [x for x in loaded if x[0]['board'] == 'APPSC']
    grand = sum(len(x[2]) for x in loaded)
    can = f'{SITE_URL}/appsc-pyqs.html'
    title = 'APPSC PYQs – Group 1 & Group 2 Previous Question Papers with Answers (Free) | Learn with Anil'
    desc = (f'All APPSC previous year question papers in one place: Group 1 Prelims 2019–2024 and Group 2 Screening & Mains 2019–2025, '
            f'{grand:,} questions with official final-key answers and explanations in English and Telugu. Read or practise online free.')
    secs = []
    for conf, papers, questions in sorted(loaded, key=lambda x: x[0]['short']):   # Group-I first, then Group-II
        base = conf['dir'] + '/' if conf['dir'] else ''
        home = base if base else 'index.html#home'
        subj = {s[0]: s for s in conf['subjects']}
        scount = {}
        for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
        rows = ''.join(
            f'<li class="q"><div class="meta">{esc(p["held"])} · {esc(p["notif"])} · {p["count"]} questions · '
            f'{"all four options" if p["fmt"] == "mcq" else "answer-only key"}</div>'
            f'<p><a href="{base}papers/{p["slug"]}.html">{esc(p["title"])} question paper with answers</a></p>'
            f'<p class="why" style="font-weight:400">{esc(p["blurb"])}</p></li>'
            for p in sorted(papers, key=lambda p: (-p['year'], p['id'])))
        subs = ''.join(f'<a href="{base}subjects/{conf["slugp"]}-{subj[s][2]}-pyqs.html">{esc(subj[s][1])} ({scount[s]})</a>'
                       for s in subj if scount.get(s))
        te = 'గ్రూప్-1' if conf['short'] == 'Group-I' else 'గ్రూప్-2'
        secs.append(f'<h2 id="{conf["id"]}">{nw(conf["name"])} PYQs <span lang="te" style="font-size:.8em;font-weight:600">· APPSC {te} ప్రశ్నాపత్రాలు</span></h2>'
                    f'<p><a class="cta" href="{home}">Practise {esc(conf["name"])} online</a></p>'
                    f'<ol class="qs">{rows}</ol><h3>{esc(conf["name"])} PYQs by subject</h3><nav class="toc">{subs}</nav>')
    lede = esc(f'Every APPSC Group 1 and Group 2 previous question paper on Learn with Anil, {grand:,} questions in all. '
               f'Answers come from APPSC\'s official final keys, and every question has a short explanation, in English and Telugu.')
    toc = '<nav class="toc">' + ''.join(f'<a href="#{c["id"]}">{esc(c["name"])}</a>' for c, _, _ in sorted(loaded, key=lambda x: x[0]['short'])) + '</nav>'
    body = (toc + '<p lang="te">APPSC గ్రూప్ 1, గ్రూప్ 2 పాత ప్రశ్నాపత్రాలు అధికారిక ఫైనల్ కీ సమాధానాలు మరియు వివరణలతో — ఉచితంగా.</p>'
            + ''.join(secs))
    return static_page(0, title, desc, can, 'APPSC PYQs: previous question papers with answers', lede, body,
                       [('Home', SITE_URL + '/'), ('APPSC PYQs', can)], ename='APPSC')


def build_static(conf, papers, subjects, questions, subj):
    pages = {}
    by_p = {}
    for q in questions: by_p.setdefault(q['p'], []).append(q)
    pmap = {p['id']: p for p in papers}
    base = f'{SITE_URL}/{conf["dir"] + "/" if conf["dir"] else ""}'
    home_crumbs = [('Home', SITE_URL + '/')] + ([(conf['name'], base)] if conf['dir'] else [])
    name, seo, slugp = conf['name'], conf['seo'], conf['slugp']
    for p in papers:
        qs = by_p[p['id']]
        rel = f'papers/{p["slug"]}.html'
        can = base + rel
        fmt = (f'All four options with the answer from {conf["keyname"]}' if p['fmt'] == 'mcq'
               else f'Each question with its official answer from {conf["keyname"]} (the key lists the correct answer only)')
        title = f'{p["title"]} Question Paper with Answers – {seo} PYQs | Learn with Anil'
        kdesc = 'official final-key answers' if conf['board'] == 'APPSC' else f'answers from {conf["keyshort"]}'
        langs = f' in English and {conf["l2"]["name"]}' if conf['board'] != 'APPSC' else ''
        desc = (f'{p["title"]} ({p["notif"]}, held {p["held"]}): {len(qs)} previous year questions{langs} with {kdesc} '
                f'and short explanations, topic-wise. Practise {seo} PYQs online free.')
        subs = {}
        for q in qs: subs.setdefault(q['s'], 0); subs[q['s']] += 1
        toc = '<nav class="toc">' + ''.join(
            f'<a href="../subjects/{slugp}-{subj[s][2]}-pyqs.html">{esc(subj[s][1])} ({c})</a>' for s, c in subs.items()) + '</nav>'
        body = (f'<a class="cta" href="../index.html#papers">Practise this paper online</a>'
                f'<a class="cta alt" href="../index.html#practice">Make a topic-wise quiz</a>'
                f'<h2>Subjects in this paper</h2>{toc}<h2>All {len(qs)} questions</h2><ol class="qs">'
                + ''.join(q_html(q, p['short'], f'Q{q["n"]}', subj, conf['l2']) for q in qs) + '</ol>')
        held = f'{p["notif"]}, held on {p["held"]}' if conf['board'] == 'APPSC' else f'Held on {p["held"]} ({p["notif"].replace(" · ", ", ")})'
        lede = esc(f'{p["blurb"]} {held}. {fmt}, plus a short explanation for every question.'
                   + (f' Each question is shown in English and {conf["l2"]["name"]}, as printed.' if conf['board'] != 'APPSC' else ''))
        pages[rel] = static_page(1, title, desc, can, f'{p["title"]}: questions with answers', lede, body,
                                 home_crumbs + [(p['title'], can)], conf)
    by_s = {}
    for q in questions: by_s.setdefault(q['s'], []).append(q)
    for s in subjects:
        qs = by_s.get(s['id'], [])
        if not qs: continue
        rel = f'subjects/{slugp}-{s["slug"]}-pyqs.html'
        can = base + rel
        title = f'{seo} {s["name"]} PYQs – Previous Year Questions with Answers | Learn with Anil'
        desc = (f'{len(qs)} {name} {s["name"]} previous year questions from {", ".join(sorted({pmap[q["p"]]["short"] for q in qs}))}, '
                f'arranged topic-wise with official answers and explanations.')
        body = [f'<a class="cta" href="../index.html#practice">Practise {esc(s["name"])} online</a>']
        tops = {}
        for q in qs: tops.setdefault(q['t'], []).append(q)
        body.append('<nav class="toc">' + ''.join(f'<a href="#t{i}">{esc(t)} ({len(tops[t])})</a>' for i, t in enumerate(s['topics']) if t in tops) + '</nav>')
        for i, t in enumerate(s['topics']):
            if t not in tops: continue
            body.append(f'<h2 id="t{i}">{esc(t)}</h2><ol class="qs">' + ''.join(
                q_html(q, pmap[q['p']]['short'], f'{pmap[q["p"]]["short"]} · Q{q["n"]}', subj, conf['l2']) for q in tops[t]) + '</ol>')
        lede = esc(f'Every {s["name"]} question asked in the {name} papers on this site, grouped by topic. '
                   f'Answers come from {conf["keyshort"]}; each has a short explanation.')
        pages[rel] = static_page(1, title, desc, can, f'{name} {s["name"]} PYQs', lede, ''.join(body),
                                 home_crumbs + [(s['name'], can)], conf)
    return pages


if __name__ == '__main__':
    main()
