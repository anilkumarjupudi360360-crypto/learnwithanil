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
       title='UPSC CAPF (AC) 2026 Paper I', notif='Series A · provisional key', held='19 July 2026', key="UPSC's provisional answer key",
       fmt='mcq', slug='upsc-capf-ac-2026-paper-1-general-ability-intelligence-question-paper-with-answers',
       blurb='General Ability & Intelligence: General Mental Ability, General Science, Current Events, Indian Polity & Economy, History and Geography (125 questions, 250 marks).'),
  dict(id='c2025a', file='capf-2025-paper-1.txt', year=2025, stage='Paper I', short='CAPF 2025 · P-I',
       title='UPSC CAPF (AC) 2025 Paper I', notif='Answers compiled (UPSC key not published)', held='3 August 2025', key='answers compiled by Learn with Anil from three published keys (UPSC has not published its key)',
       fmt='mcq', slug='upsc-capf-ac-2025-paper-1-general-ability-intelligence-question-paper-with-answers',
       blurb='General Ability & Intelligence: Current Events, General Science, Polity, Economy, History, Geography and Mental Ability (125 questions, 250 marks).'),
  dict(id='c2024a', file='capf-2024-paper-1.txt', year=2024, stage='Paper I', short='CAPF 2024 · P-I',
       title='UPSC CAPF (AC) 2024 Paper I', notif='Series A · official key', held='4 August 2024', key="UPSC's official answer key",
       fmt='mcq', slug='upsc-capf-ac-2024-paper-1-general-ability-intelligence-question-paper-with-answers',
       blurb='General Ability & Intelligence: General Science, Current Events, Polity, Economy, History, Geography and Mental Ability (125 questions, 250 marks).'),
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

# ---------- Telangana Police (TSLPRB, now TGPRB): SI and Constable Preliminary Written Tests ----------
TS_SI_PAPERS = [
  dict(id='s2022', file='ts-si-2022-prelims.txt', year=2022, stage='Preliminary Written Test', short='SI Prelims 2022',
       title='TSLPRB SI Preliminary Written Test 2022', notif='SCT SI (Civil) & equivalent · booklet A', held='7 August 2022',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-si-prelims-2022-question-paper-with-answers',
       blurb='Arithmetic & Test of Reasoning / Mental Ability (Q1–100) and General Studies (Q101–200): 200 questions, 200 marks, 3 hours.'),
]
TS_PC_PAPERS = [
  dict(id='p2022', file='ts-pc-2022-prelims.txt', year=2022, stage='Preliminary Written Test', short='PC Prelims 2022',
       title='TSLPRB Police Constable Preliminary Written Test 2022', notif='SCT PC (Civil) & equivalent · booklet A', held='28 August 2022',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-constable-prelims-2022-question-paper-with-answers',
       blurb='English, Arithmetic, Reasoning / Mental Ability and General Studies: 200 questions, 200 marks, 3 hours.'),
]
TS_SUBJECTS = [
  ('ari', 'Arithmetic', 'arithmetic', ['Numbers & Simplification', 'Percentage, Profit & Loss', 'Ratio, Average & Ages', 'Interest', 'Time & Work', 'Time, Speed & Distance', 'Mensuration', 'Data Interpretation']),
  ('rea', 'Reasoning & Mental Ability', 'reasoning-mental-ability', ['Series & Analogies', 'Coding-Decoding', 'Blood Relations & Directions', 'Calendar & Clocks', 'Venn Diagrams & Syllogisms', 'Puzzles & Arrangements', 'Non-verbal Reasoning', 'Logical Reasoning']),
  ('eng', 'English', 'english', ['Grammar', 'Vocabulary', 'Comprehension']),
  ('sci', 'General Science', 'general-science', ['Physics', 'Chemistry', 'Biology & Health', 'Science & Technology']),
  ('ih',  'Indian History & Culture', 'indian-history', ['Ancient India', 'Medieval India', 'Modern India & Freedom Struggle', 'Art & Culture']),
  ('tg',  'Telangana', 'telangana-history-movement', ['Telangana History & Culture', 'Telangana Movement & State Formation', 'Telangana Geography & Economy', 'Telangana Schemes & Affairs']),
  ('geo', 'Geography', 'geography', ['Physical Geography', 'Indian Geography', 'World Geography', 'Environment & Ecology']),
  ('pol', 'Indian Polity', 'indian-polity', ['Constitution & Rights', 'Union & State Government', 'Judiciary', 'Local Government & Bodies', 'Governance & Schemes']),
  ('eco', 'Indian Economy', 'indian-economy', ['Growth & Planning', 'Money, Banking & Finance', 'Agriculture & Industry', 'Poverty, Employment & Welfare']),
  ('cur', 'Current Affairs', 'current-affairs', ['National', 'International', 'Sports', 'Awards & Personalities', 'Defence & Security', 'Reports & Indices']),
  ('soc', 'Society, Ethics & Sensitivity', 'ethics-gender-social-sensitivity', ['Ethics & Values', 'Gender & Social Sensitivity', 'Social Issues & Welfare', 'Disaster Management']),
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
        xp = os.path.join(SRC, conf['src'], conf['l2']['dir'], 'explanations.json')   # explanations in Telugu / Hindi
        if os.path.exists(xp):
            wt = json.load(open(xp, encoding='utf-8'))
            for q in qs:
                if q['id'] in wt and q.get('qt'): q['wt'] = wt[q['id']]
        if nte: print(f'  {conf["short"]} {p["id"]}: {conf["l2"]["name"]} for {nte} questions')
        if not qs:
            print(f'  - skipping {conf["short"]} {p["id"]} (no source yet)'); continue
        for q in qs:
            if 'img' in q: q['img'] = img_data_uri(os.path.join(conf['src'], q['img']))
        pp = {k: p[k] for k in ('id', 'year', 'stage', 'short', 'title', 'notif', 'held', 'fmt', 'slug', 'blurb')}
        pp['count'] = len(qs)
        if p.get('key'): pp['key'] = p['key']
        pp['pdf'] = pdf_href(conf, p)
        alt = paper_alt(conf, p)
        pp['kw'] = paper_kw(conf, p) + (f' ({alt})' if alt else '')
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
        pools.append([dict(id=q['id'], ex=conf['short'], exName=conf['name'], base=base, pb=conf['pb'], paper=pshort[q['p']], l2=conf['l2']['code'],
                           q=q['q'], qt=q.get('qt', ''), o=q['o'], ot=q.get('ot'), a=q['a'], w=q['w'], wt=q.get('wt', '')) for q in el])
    out, i = [], 0
    while len(out) < n and any(i < len(p) for p in pools):
        for p in pools:
            if i < len(p): out.append(p[i])
        i += 1
    return out[:n]


def exam_confs():
    return [
      dict(id='appsc-group-2', dir='', src='', key='appsc-g2', name='APPSC Group-II', short='Group-II', seo='APPSC Group 2',
           slugp='appsc-group-2', papers=PAPERS, subjects=SUBJECTS, faq=FAQ, board='APPSC', l2=L2_TE, pb='/appsc-group-2/',
           title='APPSC Group 2 Previous Year Question Papers with Answers – Prelims & Mains 2019–2025, PDF | Learn with Anil',
           h1='APPSC Group 2 previous year question papers <em>with answers.</em>',
           l2line='APPSC గ్రూప్ 2 మునుపటి సంవత్సరం ప్రశ్నపత్రాలు (ప్రిలిమ్స్, మెయిన్స్) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో, ఉచితంగా.',
           desc=lambda t: (f"APPSC Group 2 previous year question papers with answers from APPSC's final key: Prelims (Screening Test) 2024 and 2019, "
                           f"Mains 2025 Paper 1 and Paper 2, and Mains 2019. {t:,} questions in English and Telugu with explanations; "
                           f"free mock tests, practice bits and PDF downloads."),
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           eyebrow='APPSC Group-II · Prelims (Screening) &amp; Mains · 2019–2025',
           papers_note="Every paper uses APPSC's official final key. The 2024 and 2025 keys show all four options. The 2019 keys print only the correct answer, so those questions appear as quick-recall cards: think of the answer, reveal it, then mark yourself."),
      dict(id='appsc-group-1', dir='appsc-group-1', src='appsc-group-1', key='appsc-g1', name='APPSC Group-I', short='Group-I', seo='APPSC Group 1',
           slugp='appsc-group-1', papers=G1_PAPERS, subjects=G1_SUBJECTS, faq=FAQ_G1, board='APPSC', l2=L2_TE, pb='/appsc-group-1/',
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           title='APPSC Group 1 Previous Year Question Papers with Answers – Prelims 2019–2024, PDF | Learn with Anil',
           h1='APPSC Group 1 previous year question papers <em>with answers.</em>',
           l2line='APPSC గ్రూప్ 1 ప్రిలిమ్స్ మునుపటి సంవత్సరం ప్రశ్నపత్రాలు సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో, ఉచితంగా.',
           desc=lambda t: (f"APPSC Group 1 Prelims previous year question papers with answers from APPSC's final key: 2024, 2023 and 2019, "
                           f"Paper 1 General Studies and Paper 2 General Aptitude. {t:,} questions in English and Telugu with explanations; "
                           f"free mock tests and PDF downloads."),
           eyebrow='APPSC Group-I · Prelims · 2019–2024',
           papers_note="Every paper uses APPSC's official final key. The 2024 key shows all four options. The 2023 and 2019 keys print only the correct answer, so those questions appear as quick-recall cards: think of the answer, reveal it, then mark yourself."),
      dict(id='upsc-capf', dir='upsc-capf', src='upsc-capf', key='upsc-capf', name='UPSC CAPF (AC)', short='CAPF (AC)', seo='UPSC CAPF AC',
           slugp='upsc-capf-ac', papers=CAPF_PAPERS, subjects=CAPF_SUBJECTS, faq=FAQ_CAPF, board='UPSC', l2=L2_HI, pb='/upsc-capf/',
           keyname="UPSC's answer keys", keyshort="UPSC's answer keys (2025: compiled from published keys)",
           title='UPSC CAPF AC Previous Year Question Papers with Answers (2024–2026), English & Hindi PDF | Learn with Anil',
           h1='UPSC CAPF AC previous year question papers <em>with answers.</em>',
           l2line='यूपीएससी सीएपीएफ असिस्टेंट कमांडेंट के पिछले वर्षों के प्रश्न पत्र, उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में, निःशुल्क।',
           desc=lambda t: (f"UPSC CAPF AC (Assistant Commandant) previous year question papers: Paper 1 General Ability and Intelligence "
                           f"2026, 2025 and 2024 with answer keys and explanations. {t:,} questions in English and Hindi; "
                           f"free mock tests, subject-wise PYQs and PDF downloads."),
           eyebrow='UPSC CAPF (Assistant Commandants) · Paper I · 2024–2026',
           papers_note="2026: UPSC's provisional answer key, published three days after the exam; the final key may differ for a few questions. 2025: UPSC's key could not be found, so the answers were compiled by Learn with Anil from three published keys and checked one by one. 2024: UPSC's official answer key (Series A). Questions UPSC dropped are left out. Every question is in English and Hindi, as printed in the booklet."),
      dict(id='ts-police-si', dir='ts-police-si', src='ts-police-si', key='ts-si', name='TS Police SI', short='TS Police SI', seo='TS Police SI',
           slugp='ts-police-si', papers=TS_SI_PAPERS, subjects=TS_SUBJECTS, faq=FAQ_TS('SI'), board='TSLPRB', l2=L2_TE, pb='/ts-police-si/',
           keyname="TSLPRB's final key", keyshort="TSLPRB's final key", bits=True,
           te_name='తెలంగాణ పోలీస్ ఎస్ఐ', te_paper='ప్రిలిమినరీ పరీక్ష',
           title='TS Police SI Previous Year Question Papers with Answers – Prelims 2022, Telugu & English PDF | Learn with Anil',
           h1='TS Police SI previous year question papers <em>with answers.</em>',
           l2line='తెలంగాణ పోలీస్ ఎస్ఐ ప్రిలిమినరీ పరీక్ష మునుపటి ప్రశ్నపత్రం సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో, ఉచితంగా.',
           desc=lambda t: (f"TS Police SI (TSLPRB / TGPRB) previous year question paper: Preliminary Written Test 2022 with answers from TSLPRB's final key. "
                           f"{t} questions on arithmetic, reasoning and general studies in English and Telugu with explanations; free mock tests, practice bits and PDF download."),
           eyebrow='TSLPRB / TGPRB · SI (Civil) &amp; equivalent · Preliminary Written Test',
           papers_note="Answers come from TSLPRB's final key for booklet A, released on 21 October 2022. Questions the key deleted, or for which it accepted three or four options, are left out. Every question is in English and Telugu, as printed in the booklet."),
      dict(id='ts-police-constable', dir='ts-police-constable', src='ts-police-constable', key='ts-pc', name='TS Police Constable', short='TS Constable', seo='TS Police Constable',
           slugp='ts-police-constable', papers=TS_PC_PAPERS, subjects=TS_SUBJECTS, faq=FAQ_TS('PC'), board='TSLPRB', l2=L2_TE, pb='/ts-police-constable/',
           keyname="TSLPRB's final key", keyshort="TSLPRB's final key", bits=True,
           te_name='తెలంగాణ పోలీస్ కానిస్టేబుల్', te_paper='ప్రిలిమినరీ పరీక్ష',
           title='TS Police Constable Previous Year Question Papers with Answers – Prelims 2022, Telugu & English PDF | Learn with Anil',
           h1='TS Police Constable previous year question papers <em>with answers.</em>',
           l2line='తెలంగాణ పోలీస్ కానిస్టేబుల్ ప్రిలిమినరీ పరీక్ష మునుపటి ప్రశ్నపత్రం సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో, ఉచితంగా.',
           desc=lambda t: (f"TS Police Constable (TSLPRB / TGPRB) previous year question paper: Preliminary Written Test 2022 with answers from TSLPRB's final key. "
                           f"{t} questions on English, arithmetic, reasoning and general studies in English and Telugu with explanations; free mock tests, practice bits and PDF download."),
           eyebrow='TSLPRB / TGPRB · Police Constable (Civil) &amp; equivalent · Preliminary Written Test',
           papers_note="Answers come from TSLPRB's final key for booklet A, released on 21 October 2022. Questions the key deleted, or for which it accepted three or four options, are left out. The English-language questions are in English only; every other question is in English and Telugu, as printed in the booklet."),
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
                     .replace('{{FOOTSRC}}', 'Questions and answers are from the official final keys.' if conf['board'] in ('APPSC', 'TSLPRB')
                              else f'Questions are from {conf["board"]}\'s official question paper; answers from {conf["keyshort"]}.')
                     .replace('{{FROMPAPERS}}', f'{len(papers)} official papers' if len(papers) > 1 else f'the official {papers[0]["year"]} {esc(papers[0]["stage"])} question paper')
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
                     .replace('{{EYEBROW}}', conf['eyebrow']).replace('{{H1}}', conf['h1'])
                     .replace('{{L2LINE}}', f'<span lang="{l2["code"]}">{esc(conf["l2line"])}</span>'))
        root_title = 'Previous Year Question Papers (PYQs) for Government Exams – Free with Answers | Learn with Anil'
        root_desc = (f'Free previous year question papers with answers for government exams: APPSC Group 1, APPSC Group 2, UPSC CAPF AC and TS Police SI & Constable, '
                     f'{grand:,} questions with official keys and explanations in English, Telugu and Hindi. Free mock tests and PDFs. '
                     f'TGPSC, UPSC, SSC, banking and railway exams are being added.')
        home_title = conf['title']
        ptxt = f'{len(papers)} official papers' if len(papers) > 1 else f'the official {papers[0]["year"]} {papers[0]["stage"]} question paper'
        home_desc = conf['desc'](total)
        pb = conf['pb']; basedir = '/' + prefix
        person = {"@context":"https://schema.org","@type":"Person","name":"Jupudi Anil Kumar","jobTitle":"UPSC Faculty and Mentor","telephone":"+91-94947-92739","email":"mailto:anilkumarjupudi360360@gmail.com","url":SITE_URL+'/appsc-group-2/about/',"image":SITE_URL+'/anil.jpg',"sameAs":[f"https://www.instagram.com/{INSTAGRAM}/"]}
        website = {"@context":"https://schema.org","@type":"WebSite","name":"Learn with Anil","alternateName":"Learn with Anil – Previous year questions for every exam","url":SITE_URL+'/'}
        faqld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in faq]}
        seo_name = conf['seo']
        views = {   # view: (title, description, canonical path, indexable)
          'papers': (f'{seo_name} Previous Year Question Papers with Answers – All {len(papers)} Papers, PDF | Learn with Anil',
                     f'All {len(papers)} {seo_name} previous year question papers ({", ".join(paper_kw(conf, p).replace(seo_name + " ", "") for p in sorted(papers, key=lambda p: (-p["year"], p["id"])))}): '
                     f'practise each paper online as a mock test, read it with answers and explanations, or download the PDF, free.', pb + 'papers/', True),
          'practice': (f'{seo_name} Free Mock Test & Topic-wise Quiz from Previous Papers | Learn with Anil',
                       f'Free {seo_name} mock test and topic-wise quiz made from {total:,} real previous year questions{" (practice bits)" if conf["board"] == "APPSC" or conf.get("bits") else ""}: '
                       f'choose papers, subjects and topics, then practise with answers or take a timed test.', pb + 'practice/', True),
          'bank': (f'{seo_name} Question Bank – Search All {total:,} PYQs{" & Practice Bits" if conf["board"] == "APPSC" or conf.get("bits") else ""} | Learn with Anil',
                   f'Search every {seo_name} previous year question by keyword, paper or topic, with answers from {conf["keyshort"]} and explanations.', pb + 'bank/', True),
          'notes': ('Study Material 2026-27 – Crisp Notes by Jupudi Anil Kumar | Learn with Anil',
                    'Exam-focused study material by Jupudi Anil Kumar: Crisp Notes on AP Economy and Science & Technology for APPSC Mains, with the latest 2026 data.', '/appsc-group-2/notes/', True),
          'about': ('About Jupudi Anil Kumar – Learn with Anil',
                    'Jupudi Anil Kumar is a civil-services educator with 1,000+ hours of teaching for UPSC, APPSC and TGPSC aspirants. He built Learn with Anil to make previous-year questions free for everyone.', '/appsc-group-2/about/', True),
          'mistakes': (f'Mistakes Notebook – {seo_name} | Learn with Anil', 'Your mistakes notebook on Learn with Anil.', pb + 'mistakes/', False),
          'smart': (f'Smart Quiz – {seo_name} | Learn with Anil', 'Re-attempt the questions you got wrong.', pb + 'smart/', False),
          'bookmarks': (f'Bookmarks – {seo_name} | Learn with Anil', 'Your saved questions on Learn with Anil.', pb + 'bookmarks/', False),
          'heatmap': (f'Topic Heatmap – {seo_name} | Learn with Anil', 'Your topic-wise accuracy on Learn with Anil.', pb + 'heatmap/', False),
        }
        sdata = dict(data, pb=pb, qpages=True, examSeo=seo_name, homeTitle=home_title, hubTitle=root_title)
        sjson = json.dumps(sdata, ensure_ascii=False, separators=(',', ':'))
        import hashlib
        dfile = f'data/{conf["key"]}-{hashlib.sha1(sjson.encode()).hexdigest()[:10]}.js'
        outdir = os.path.join(DIST, 'site', conf['dir'])
        os.makedirs(os.path.join(outdir, 'data'), exist_ok=True)
        open(os.path.join(outdir, dfile), 'w', encoding='utf-8').write('window.LWA_DATA=' + sjson + ';\n')
        sbody = body.replace('<script type="application/json" id="lwa-data">{{DATA}}</script>', f'<script src="{dfile}"></script>')
        assert sbody != body

        def site_doc(title, desc, canon_path, ld, index=True):
            canon = SITE_URL + canon_path
            body_ = sbody if canon_path == '/' else re.sub(r'<div id="hub-static" class="view">.*?(?=<div id="home-static")', '', sbody, flags=re.S)
            assert canon_path == '/' or 'id="hub-static"' not in body_
            seo = (f'<link rel="canonical" href="{canon}">\n<meta name="robots" content="{"index,follow" if index else "noindex,follow"}">\n'
                   f'<meta property="og:type" content="website"><meta property="og:site_name" content="Learn with Anil">'
                   f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
                   f'<meta property="og:url" content="{canon}"><meta property="og:image" content="{SITE_URL}/anil.jpg">'
                   f'<meta name="twitter:card" content="summary">\n'
                   + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld))
            doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                   f'<base href="{basedir}">\n'
                   '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
                   + fill(head, up + 'anil.jpg', title, seo, desc).replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
                   + '\n</head>\n<body>\n' + fill(body_, up + 'anil.jpg', title, seo, desc) + '\n</body>\n</html>\n')
            return site_links(doc.replace('href="{{HUBHREF}}"', 'href="/"').replace(f'href="{hubhref}"', 'href="/"'), pb)

        site_pages = {}   # path under the site root -> html
        if is_root:
            os.makedirs(os.path.join(DIST, 'artifact', 'papers')); os.makedirs(os.path.join(DIST, 'artifact', 'subjects'))
            open(os.path.join(DIST, 'artifact', 'index.html'), 'w', encoding='utf-8').write(fill(head + body, photo_uri, 'Learn with Anil', '', root_desc))
            site_pages['index.html'] = site_doc(root_title, root_desc, '/', [website, person])
        site_pages[pb.strip('/') + '/index.html'] = site_doc(home_title, home_desc, pb, [person, faqld])
        for v, (t, d, cp, ix) in views.items():
            site_pages[pb.strip('/') + f'/{v}/index.html'] = site_doc(t, d, cp, [], ix and cp.startswith(pb))
        for rel, html_ in site_pages.items():
            fp = os.path.join(DIST, 'site', rel); os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, 'w', encoding='utf-8').write(html_)
        all_pages[pb.lstrip('/')] = None
        for v, (t, d, cp, ix) in views.items():
            if ix and cp.startswith(pb): all_pages[cp.lstrip('/')] = None
        os.makedirs(os.path.join(outdir, 'papers'), exist_ok=True); os.makedirs(os.path.join(outdir, 'subjects'), exist_ok=True)
        # crawlable pages per paper and per subject
        pages = build_static(conf, papers, subjects, questions, subj)
        for rel, content in pages.items():
            open(os.path.join(outdir, rel), 'w', encoding='utf-8').write(content)
            if is_root: open(os.path.join(DIST, 'artifact', rel), 'w', encoding='utf-8').write(content)
        for rel in pages: all_pages[prefix + rel] = None
        # one page per question
        qpages = question_pages(conf, papers, questions, subj)
        qdir = os.path.join(DIST, 'site', pb.strip('/'), 'q'); os.makedirs(qdir, exist_ok=True)
        for rel, content in qpages.items():
            open(os.path.join(DIST, 'site', pb.strip('/'), rel), 'w', encoding='utf-8').write(content)
            all_pages[pb.lstrip('/') + rel] = None
        for p in papers: all_pages[pdf_href(conf, p).lstrip('/')] = None   # the PDFs come from tools/pdfs.py
        print(f'  {conf["name"]}: {total} questions, {len(pages)} static pages, {len(qpages)} question pages, {len(site_pages)} app pages')

    # one crawlable page listing every APPSC paper (the page people land on from "APPSC PYQs" searches)
    hubrel = 'appsc-pyqs.html'
    open(os.path.join(DIST, 'site', hubrel), 'w', encoding='utf-8').write(appsc_pyqs_page(loaded, grand))
    all_pages = {hubrel: None, **all_pages}

    open(os.path.join(DIST, 'site', '404.html'), 'w', encoding='utf-8').write(not_found_page())

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


# ---------- search wording ----------
# Students search with digits and the common names: "appsc group 2 prelims question paper 2024 with answers pdf",
# "appsc group 2 mains paper 1 2025 key", "capf ac previous year question paper in hindi", "గ్రూప్ 2 ప్రశ్నపత్రం".
# (Google autocomplete, India, 20 Oct 2026.) Titles, headings and descriptions use that wording.
def paper_no(p):
    m = re.search(r'Paper (I{1,3}|IV)$', p['stage'])
    return ROMAN[m.group(1)] if m else ''


def paper_kw(conf, p):
    """'APPSC Group 2 Prelims 2024', 'APPSC Group 2 Mains 2025 Paper 1', 'UPSC CAPF AC 2026 Paper 1'."""
    n = paper_no(p)
    if conf['board'] == 'UPSC':
        return f'{conf["seo"]} {p["year"]}' + (f' Paper {n}' if n else '')
    stage = 'Prelims' if p['stage'].startswith(('Screening', 'Prelims', 'Preliminary')) else 'Mains'
    return f'{conf["seo"]} {stage} {p["year"]}' + (f' Paper {n}' if n else '')


def paper_alt(conf, p):
    """The paper's other name, if students also search by it."""
    if p['stage'].startswith('Screening'): return 'Screening Test'
    if p['stage'].startswith('Preliminary'): return 'Preliminary Written Test'
    if conf['board'] == 'UPSC': return 'General Ability and Intelligence'
    if conf['short'] == 'Group-I': return 'General Studies' if paper_no(p) == '1' else 'General Aptitude'
    return ''


def paper_kw_l2(conf, p):
    """The same name in Telugu (APPSC) or Hindi (UPSC CAPF), as students type it."""
    n = paper_no(p)
    if conf.get('te_name'):
        return f'{conf["te_name"]} {conf["te_paper"]} {p["year"]} ప్రశ్నపత్రం సమాధానాలతో'
    if conf['l2']['code'] == 'te':
        g = 'గ్రూప్ 2' if conf['short'] == 'Group-II' else 'గ్రూప్ 1'
        stage = 'ప్రిలిమ్స్' if p['stage'].startswith(('Screening', 'Prelims')) else 'మెయిన్స్'
        return f'APPSC {g} {stage} {p["year"]}' + (f' పేపర్-{n}' if n else '') + ' ప్రశ్నపత్రం సమాధానాలతో'
    return f'यूपीएससी सीएपीएफ (असिस्टेंट कमांडेंट) {p["year"]}' + (f' पेपर-{n}' if n else '') + ' प्रश्न पत्र, उत्तर कुंजी सहित'


def pdf_name(conf, p):
    """File name of the paper's PDF, e.g. appsc-group-2-prelims-2024-question-paper-with-answers.pdf."""
    return re.sub(r'[^a-z0-9]+', '-', paper_kw(conf, p).lower()).strip('-') + '-question-paper-with-answers.pdf'


def pdf_href(conf, p):
    """Site-root path of the paper's PDF (made by tools/pdfs.py after the build)."""
    return '/' + (conf['dir'] + '/' if conf['dir'] else '') + 'pdf/' + pdf_name(conf, p)


SUBJ_L2 = {
  'te': {'ih': 'చరిత్ర', 'aph': 'ఆంధ్రప్రదేశ్ చరిత్ర, సంస్కృతి', 'pol': 'భారత రాజ్యాంగం (పాలిటీ)', 'geo': 'భూగోళశాస్త్రం (జాగ్రఫీ)',
         'soc': 'భారతీయ సమాజం', 'eco': 'భారత, ఏపీ ఆర్థిక వ్యవస్థ (ఎకానమీ)', 'sci': 'సైన్స్ అండ్ టెక్నాలజీ', 'cur': 'కరెంట్ అఫైర్స్',
         'men': 'మెంటల్ ఎబిలిటీ (రీజనింగ్)', 'gk': 'జనరల్ నాలెడ్జ్', 'apt': 'పరిపాలనా, మానసిక సామర్థ్యాలు',
         'ari': 'అర్థమెటిక్ (అంకగణితం)', 'rea': 'రీజనింగ్, మెంటల్ ఎబిలిటీ', 'eng': 'ఇంగ్లీష్', 'tg': 'తెలంగాణ చరిత్ర, ఉద్యమం'},
  'hi': {'cur': 'समसामयिकी (करेंट अफेयर्स)', 'ih': 'इतिहास', 'pol': 'भारतीय राजव्यवस्था', 'eco': 'भारतीय अर्थव्यवस्था',
         'geo': 'भूगोल', 'sci': 'सामान्य विज्ञान', 'men': 'सामान्य मानसिक योग्यता (रीजनिंग)'},
}


def subject_l2_line(conf, s):
    name = SUBJ_L2[conf['l2']['code']].get(s['id'])
    if not name: return ''
    if conf.get('te_name'):
        if s['id'] == 'soc': name = 'నైతిక విలువలు, జెండర్ సెన్సిటివిటీ'
        return f'{conf["te_name"]} {name} ప్రాక్టీస్ బిట్స్ — మునుపటి సంవత్సరం ప్రశ్నలు, సమాధానాలు, వివరణలతో.'
    if conf['l2']['code'] == 'te':
        g = 'గ్రూప్ 2' if conf['short'] == 'Group-II' else 'గ్రూప్ 1'
        return f'APPSC {g} {name} ప్రాక్టీస్ బిట్స్ — మునుపటి సంవత్సరం ప్రశ్నలు, సమాధానాలు, వివరణలతో.'
    return f'सीएपीएफ (एसी) {name} — पिछले वर्षों के प्रश्न, उत्तर और व्याख्या सहित।'


def exam_terms(e, cat):
    """Lower-case words a student might type to find this exam (used by the search box)."""
    words = [e['b'], e['t'], e.get('n', ''), cat['name'], e['id'].replace('-', ' ')]
    m = re.search(r'Group-(I{1,3}|IV)\b', e['t'])
    if m:
        d = ROMAN[m.group(1)]
        words += [f'group {d}', f'group{d}', f'group-{d}', f'group {m.group(1)}']
    if e['cat'] == 'tg': words += ['tspsc', 'tgpsc', 'telangana']
    if 'police' in e['id']: words += ['ts police', 'tg police', 'tslprb', 'tgprb', 'si', 'constable']
    if e['cat'] == 'ap': words += ['appsc', 'andhra']
    return ' '.join(w.lower() for w in words if w)


ROUTE_RE = r'(exams|exam/[\w-]+|home|appsc-group-2|papers|practice|quiz|result|bank|mistakes|smart|bookmarks|heatmap|about|join|notes)'


def site_links(html_, pb):
    """On the website every view has its own address: turn in-app links such as #bank into /appsc-group-1/bank/."""
    def to(v):
        if v == 'exams': return '/'
        if v.startswith('exam/'): return f'/{v}/'
        if v == 'home': return pb
        if v == 'appsc-group-2': return '/appsc-group-2/'
        return f'{pb}{v}/'
    html_ = re.sub(r'href="\.\./#(exams|exam/[\w-]+)"', lambda m: f'href="{to(m.group(1))}"', html_)
    return re.sub(r'href="#' + ROUTE_RE + '"', lambda m: f'href="{to(m.group(1))}"', html_)


def live_href(e):
    """Where a live exam tile points: a hash in this page ('home') or another page ('appsc-group-1/')."""
    return e['live'] if '/' in e['live'] else '#' + e['live']


def hub_html(catalog, counts, grand):
    cats = catalog['cats']; byc = {c['id']: c for c in cats}
    chips = (f'<button type="button" class="chip" data-act="excat" data-cat="all" aria-pressed="true"><span data-i18n="all">All exams</span> <span class="n">{len(catalog["exams"])}</span></button>'
             + ''.join(f'<button type="button" class="chip" data-act="excat" data-cat="{c["id"]}" aria-pressed="false">{esc(c["name"])} '
                       f'<span class="n">{sum(1 for e in catalog["exams"] if e["cat"] == c["id"])}</span></button>' for c in cats))
    secs = []
    for c in cats:
        tiles = []
        for e in sorted([e for e in catalog['exams'] if e['cat'] == c['id']], key=lambda e: not e.get('live')):   # live exams first
            live = bool(e.get('live'))
            href = live_href(e) if live else '#exam/' + e['id']
            status = f'Live · {counts.get(e["id"], 0):,} questions' if live else 'Coming soon'
            sub = f'<span class="ex-n">{esc(e["n"])}</span>' if e.get('n') else ''
            tiles.append(f'<a class="card exam{" live" if live else ""}" href="{href}" data-cat="{c["id"]}" data-s="{esc(exam_terms(e, c))}">'
                         f'<span class="ex-b">{esc(e["b"])}</span><span class="ex-t">{nw(e["t"])}</span>{sub}<span class="ex-st" data-n="{counts.get(e["id"], 0) if live else ""}">{status}</span></a>')
        te = f' <span class="te-sub" lang="te">{esc(c["te"])}</span>' if c.get('te') else ''
        secs.append(f'<section class="exam-cat" data-cat="{c["id"]}"><div class="section-title"><h2>{esc(c["name"])}{te}</h2>'
                    f'<span class="muted" style="font-size:14px">{esc(c["desc"])}</span></div><div class="exams">{"".join(tiles)}</div></section>')
    search = ('<label class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="color:var(--muted)">'
              '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4" stroke-linecap="round"/></svg>'
              '<input id="examSearch" type="search" placeholder="Search an exam, e.g. Group-II, CGL, NDA, Police SI" aria-label="Search exams" autocomplete="off"></label>')
    return (f'<div class="hub-tools">{search}<div class="chips" role="group" aria-label="Filter exams">{chips}</div></div>'
            f'<p class="muted" id="hubCount" style="font-size:14px"></p>'
            f'<div id="hubCats">{"".join(secs)}</div>'
            f'<div class="card empty" id="hubEmpty" hidden><h3 data-i18n="emptyT">No exam matches your search</h3>'
            f'<p data-i18n="emptyP">Tell Anil which exam you are preparing for, and it will be added to the list.</p>'
            f'<div class="row" style="justify-content:center"><a class="btn btn-primary" id="hubAsk" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener" data-i18n="ask">Ask on WhatsApp</a></div></div>')


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
    return (f'<article class="card paper"><span class="yr">{esc(p["held"])} · {esc(p["notif"])}</span><h3>{esc(p.get("kw") or p["title"])}</h3>'
            f'<p>{esc(p["blurb"])}</p><div class="meta"><span class="pill blue">{p["count"]} questions</span><span class="pill {cls}">{fmt}</span></div>'
            f'<div class="acts"><button class="btn btn-primary btn-sm" type="button" data-act="paperpractice" data-paper="{p["id"]}">Practise</button>'
            f'<a class="btn btn-ghost btn-sm" href="papers/{p["slug"]}.html">Read with answers</a>'
            f'<a class="btn btn-ghost btn-sm" href="{p["pdf"]}" download>PDF</a></div></article>')


def FAQ(total, npapers):
    return [
      ('Where can I get APPSC Group 2 previous year question papers with answers?',
       f'This site has {total} questions from {npapers} APPSC Group-II papers: the Screening Test 2024, Mains 2025 Paper I and Paper II, and the 2019 Screening and Mains papers. Every answer is taken from APPSC\'s official final key, and each question has a short explanation. You can read each paper with answers or practise it as a quiz, free.'),
      ('Can I download the APPSC Group 2 previous papers as PDF?',
       'Yes, free. Every paper has its own PDF: all the questions in English and Telugu, then the answer key and an explanation for each answer. Open a paper and tap Download PDF.'),
      ('Are the APPSC Group 2 previous papers available in Telugu?',
       'Yes. Almost every question has APPSC\'s own Telugu text, as printed in the question booklet. Tap తెలుగు at the top of the page to practise in Telugu.'),
      ('Is there a free APPSC Group 2 mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects, and pick Timed test: you get a free mock test made of real APPSC Group 2 Prelims and Mains questions, with your score and a topic-wise analysis at the end. Practice mode works like practice bits, one question at a time with the answer and explanation.'),
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
      ('Can I download the APPSC Group 1 previous papers as PDF?',
       'Yes, free. Every paper has its own PDF: all the questions in English and Telugu, then the answer key and an explanation for each answer. Open a paper and tap Download PDF.'),
      ('Where is the APPSC Group 1 Prelims 2024 answer key?',
       'Each question on this site shows the answer from APPSC\'s final key, for Paper 1 (General Studies) and Paper 2 (General Aptitude) of the 2024 Prelims, and for the 2023 and 2019 Prelims. Open a paper to see every question with its answer.'),
      ('Is there a free APPSC Group 1 mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects, and pick Timed test: you get a free mock test made of real APPSC Group 1 Prelims questions, in English or Telugu, with your score and a topic-wise analysis at the end.'),
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
       f'This page has {total} questions from {npapers} UPSC CAPF (Assistant Commandants) Paper I papers, General Ability and Intelligence (2024, 2025 and 2026), in English and Hindi as printed in the official question booklets. Every question has a short explanation. You can read each paper with answers or practise it as a quiz, free.'),
      ('Can I download the CAPF AC previous year question papers as PDF?',
       'Yes, free. Each paper (2026, 2025 and 2024 Paper 1) has its own PDF with every question in English and Hindi, then the answer key and an explanation for each answer. Open a paper and tap Download PDF.'),
      ('Where is the CAPF AC 2026 answer key?',
       'Every 2026 question on this site shows the answer from UPSC\'s provisional answer key (Series A booklet), published three days after the exam on 19 July 2026. UPSC\'s final key can differ for a few questions.'),
      ('Is there a free CAPF AC mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects such as General Science, Current Affairs or Polity, and pick Timed test: you get a free mock test made of real CAPF AC Paper 1 questions, in English or Hindi, with your score and a topic-wise analysis.'),
      ('What is the UPSC CAPF AC exam pattern?',
       'The written exam has two papers on the same day. Paper I, General Ability and Intelligence, is objective, carries 250 marks and lasts two hours; recent papers have had 125 questions, in English and Hindi. It covers General Mental Ability, General Science, Current Events of national and international importance, Indian Polity and Economy, History of India, and Indian and World Geography. A wrong answer costs one-third of the marks for that question. Paper II, General Studies, Essay and Comprehension, is descriptive and carries 200 marks. Candidates who qualify take physical and medical standards tests and then an interview.'),
      ('Are the answers on this site official?',
       'For 2024 they come from UPSC\'s official answer key. For 2026 they come from the provisional key UPSC published after the exam; the final key can differ for a few questions. UPSC has not published a key for 2025 that we could find, so those answers were compiled from three published coaching keys and checked one by one; where a source reports a different answer, the explanation says so. Questions UPSC dropped are left out. The explanations are written by Learn with Anil.'),
      ('Is the CAPF AC previous year question paper available in Hindi?',
       'Yes. Tap हिंदी at the top of the page to see every question and option in Hindi, exactly as printed in UPSC\'s booklet. Tap EN to switch back.'),
      ('Do I need to sign up?',
       'No. The portal is free and practice needs no account. Before your first timed test you enter your name, phone, email and district once, so your test scores are saved with Learn with Anil and Anil can guide you. Your practice attempts, mistakes notebook and bookmarks stay in your own browser on your device.'),
    ]


def FAQ_TS(post):
    si = post == 'SI'
    name = 'TS Police SI' if si else 'TS Police Constable'
    def faq(total, npapers):
        return [
          (f'Where can I get {name} previous year question papers with answers?',
           f'This page has {total} questions from the {"SI" if si else "Police Constable"} Preliminary Written Test held by TSLPRB on {"7 August" if si else "28 August"} 2022 (booklet A), in English and Telugu as printed. '
           f'Every answer is taken from TSLPRB\'s final key, released on 21 October 2022, and each question has a short explanation. You can read the paper with answers, practise it as a quiz or download the PDF, free.'),
          (f'What is the {name} Preliminary Written Test pattern?',
           ('The SI Preliminary Written Test is one objective paper of 200 questions for 200 marks in 3 hours: Arithmetic and Test of Reasoning / Mental Ability, and General Studies. '
            if si else
            'The Police Constable Preliminary Written Test is one objective paper of 200 questions for 200 marks in 3 hours, covering English, Arithmetic, Reasoning / Mental Ability and General Studies. ')
           + 'The qualifying marks are 30% for OC, 25% for BC and 20% for SC, ST and ex-servicemen. Qualified candidates take the physical tests (PMT/PET) and then the Final Written Examination.'),
          ('When is the 2026 Preliminary Written Test?',
           ('TGPRB has tentatively scheduled the SI Preliminary Written Test for 29 November 2026 (forenoon). ' if si else
            'TGPRB has tentatively scheduled the Police Constable Preliminary Written Test for 20 December 2026 (forenoon). ')
           + 'Dates can change, so confirm on tgprb.in. The 2022 paper on this page follows the same pattern.'),
          (f'Are the {name} questions available in Telugu?',
           'Yes. Every question that the booklet printed in Telugu is here exactly as printed. Tap తెలుగు at the top of the page to practise in Telugu.'),
          (f'Is there a free {name} mock test?',
           f'Yes. Tap Create a quiz, choose subjects or topics, and pick Timed test: you get a free mock test made of real TSLPRB questions, with your score and a topic-wise analysis at the end. Practice mode works like practice bits, one question at a time with the answer and explanation.'),
          ('Which questions are left out?',
           'Questions that TSLPRB deleted in the final key, and questions for which the final key accepted three or four options, are left out. Where the key accepted two options, both are shown as correct, and where it also gave the mark for leaving a question blank, the explanation says so.'),
        ]
    return faq


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
    pb = conf['pb'] if conf else '/appsc-group-2/'
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
<header><div class="wrap"><a href="{pb if conf else '/'}">Learn with Anil · {nw(ename)} PYQs</a><a href="{pb}practice/">Practise online →</a></div></header>
<main class="wrap">
<h1>{nw(h1)}</h1>
<p class="lede">{lede}</p>
{body_html}
</main>
<footer><div class="wrap"><p style="margin:0 0 8px"><a href="{rootup}appsc-pyqs.html">All APPSC previous question papers (PYQs)</a> · <a href="{rootup}appsc-group-1/">APPSC Group-I</a> · <a href="/appsc-group-2/">APPSC Group-II</a> · <a href="/upsc-capf/">UPSC CAPF (AC)</a> · <a href="/ts-police-si/">TS Police SI</a> · <a href="/ts-police-constable/">TS Police Constable</a> · <a href="/">All exams</a></p>{foot}</div></footer>
</body>
</html>
"""


def q_html(q, paper_short, num_label, subj=SUBJ, l2=L2_TE, qhref=None):
    label = f'<a href="{qhref}">{esc(num_label)}</a>' if qhref else esc(num_label)
    parts = [f'<li class="q" id="q{q["n"]}"><div class="meta">{label} · {esc(subj[q["s"]][1])} · {esc(q["t"])}</div>',
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
    wt = f'<p class="why" lang="{l2["code"]}" style="margin-top:6px">{esc(q["wt"])}</p>' if q.get('wt') else ''
    parts.append(f'<details><summary>Show answer</summary><p class="ans">Answer: {esc(ans)}</p>{te_ans}<p class="why">{esc(q["w"])}</p>{wt}</details></li>')
    return ''.join(parts)


def appsc_pyqs_page(loaded, grand):
    """Landing page for 'APPSC PYQs' searches: every APPSC paper and subject page, Group-I and Group-II."""
    loaded = [x for x in loaded if x[0]['board'] == 'APPSC']
    grand = sum(len(x[2]) for x in loaded)
    can = f'{SITE_URL}/appsc-pyqs.html'
    title = 'APPSC Previous Year Question Papers with Answers – Group 1 & Group 2 PYQs, Free PDF | Learn with Anil'
    desc = (f'All APPSC previous year question papers in one place: Group 1 Prelims 2019–2024 and Group 2 Prelims & Mains 2019–2025, '
            f'{grand:,} questions with final-key answers and explanations in English and Telugu. Read online, take a free mock test or download the PDF.')
    secs = []
    for conf, papers, questions in sorted(loaded, key=lambda x: x[0]['short']):   # Group-I first, then Group-II
        base = conf['dir'] + '/' if conf['dir'] else ''
        home = conf['pb']
        subj = {s[0]: s for s in conf['subjects']}
        scount = {}
        for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
        rows = ''.join(
            f'<li class="q"><div class="meta">{esc(p["held"])} · {esc(p["notif"])} · {p["count"]} questions · '
            f'{"all four options" if p["fmt"] == "mcq" else "answer-only key"}</div>'
            f'<p><a href="{base}papers/{p["slug"]}.html">{esc(paper_kw(conf, p))} question paper with answers</a> · <a href="{pdf_href(conf, p)}" download>PDF</a></p>'
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
    body = (toc + '<p>Looking for AP Group 2 or AP Group 1 previous papers, APPSC old question papers with the key, or a free APPSC mock test? '
            'They are all here: open a paper to read it with answers, download its PDF, or practise it online.</p>'
            '<p lang="te">APPSC గ్రూప్ 1, గ్రూప్ 2 మునుపటి సంవత్సరం ప్రశ్నపత్రాలు (పాత ప్రశ్నాపత్రాలు) అధికారిక ఫైనల్ కీ సమాధానాలు, వివరణలతో — PDF డౌన్‌లోడ్, ఉచిత మాక్ టెస్ట్.</p>'
            + ''.join(secs))
    return static_page(0, title, desc, can, 'APPSC previous year question papers with answers', lede, body,
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
        pkey = p.get('key', conf['keyname'])
        fmt = (f'All four options with the answer from {pkey}' if p['fmt'] == 'mcq'
               else f'Each question with its official answer from {conf["keyname"]} (the key lists the correct answer only)')
        kw, alt = paper_kw(conf, p), paper_alt(conf, p)
        if conf['board'] == 'UPSC':
            title = f'{kw} Question Paper with Answer Key, English & Hindi PDF | Learn with Anil'
        else:
            title = f'{kw} Question Paper with Answers{f" ({alt})" if alt else ""} – Final Key, PDF | Learn with Anil'
        kdesc = ("answers from APPSC's final key" if conf['board'] == 'APPSC' else 'compiled answers' if p.get('key', '').startswith('answers compiled')
                 else f'answers from {pkey}')
        desc = (f'{kw} question paper{f" ({alt})" if alt else ""}, held {p["held"]}: all {len(qs)} questions in English and {conf["l2"]["name"]} '
                f'with {kdesc} and explanations. Download the PDF or practise it online as a free mock test.')
        subs = {}
        for q in qs: subs.setdefault(q['s'], 0); subs[q['s']] += 1
        toc = '<nav class="toc">' + ''.join(
            f'<a href="../subjects/{slugp}-{subj[s][2]}-pyqs.html">{esc(subj[s][1])} ({c})</a>' for s, c in subs.items()) + '</nav>'
        body = (f'<p lang="{conf["l2"]["code"]}" style="margin:0 0 6px">{esc(paper_kw_l2(conf, p))}</p>'
                f'<a class="cta" href="{pdf_href(conf, p)}" download>Download PDF (free)</a>'
                f'<a class="cta alt" href="{conf["pb"]}papers/">Practise this paper online</a>'
                f'<a class="cta alt" href="{conf["pb"]}practice/">Make a topic-wise quiz</a>'
                f'<h2>Subjects in this paper</h2>{toc}<h2>All {len(qs)} questions</h2><ol class="qs">'
                + ''.join(q_html(q, p['short'], f'Q{q["n"]}', subj, conf['l2'], f'{conf["pb"]}q/{q["id"]}.html') for q in qs) + '</ol>')
        held = f'{p["notif"]}, held on {p["held"]}' if conf['board'] == 'APPSC' else f'Held on {p["held"]} ({p["notif"].replace(" · ", ", ")})'
        lede = esc(f'{p["title"]}{f" ({alt})" if alt and alt not in p["title"] else ""}. {p["blurb"]} {held}. {fmt}, plus a short explanation for every question. '
                   f'Each question is shown in English and {conf["l2"]["name"]}, as printed in the booklet.')
        pages[rel] = static_page(1, title, desc, can, f'{kw} question paper with answers', lede, body,
                                 home_crumbs + [(p['title'], can)], conf)
    by_s = {}
    for q in questions: by_s.setdefault(q['s'], []).append(q)
    for s in subjects:
        qs = by_s.get(s['id'], [])
        if not qs: continue
        rel = f'subjects/{slugp}-{s["slug"]}-pyqs.html'
        can = base + rel
        bits = ' & Practice Bits' if conf['board'] == 'APPSC' or conf.get('bits') else ' (Subject-wise)'
        title = f'{seo} {s["name"]} Previous Year Questions (PYQs) with Answers{bits} | Learn with Anil'
        desc = (f'{len(qs)} {seo} {s["name"]} previous year questions from {", ".join(paper_kw(conf, pmap[pid]).replace(seo + " ", "") for pid in dict.fromkeys(q["p"] for q in qs))}, '
                f'topic-wise, with answers, explanations and {conf["l2"]["name"]} text. Practise them free as a mock test.')
        l2l = subject_l2_line(conf, s)
        body = ([f'<p lang="{conf["l2"]["code"]}" style="margin:0 0 6px">{esc(l2l)}</p>'] if l2l else []) + [f'<a class="cta" href="{conf["pb"]}practice/">Practise {esc(s["name"])} online</a>']
        tops = {}
        for q in qs: tops.setdefault(q['t'], []).append(q)
        body.append('<nav class="toc">' + ''.join(f'<a href="#t{i}">{esc(t)} ({len(tops[t])})</a>' for i, t in enumerate(s['topics']) if t in tops) + '</nav>')
        for i, t in enumerate(s['topics']):
            if t not in tops: continue
            body.append(f'<h2 id="t{i}">{esc(t)}</h2><ol class="qs">' + ''.join(
                q_html(q, pmap[q['p']]['short'], f'{pmap[q["p"]]["short"]} · Q{q["n"]}', subj, conf['l2'], f'{conf["pb"]}q/{q["id"]}.html') for q in tops[t]) + '</ol>')
        lede = esc(f'Every {s["name"]} question asked in the {name} papers on this site, grouped by topic. '
                   f'Answers come from {conf["keyshort"]}; each has a short explanation.')
        pages[rel] = static_page(1, title, desc, can, f'{seo} {s["name"]} previous year questions with answers', lede, ''.join(body),
                                 home_crumbs + [(s['name'], can)], conf)
    return pages


def question_pages(conf, papers, questions, subj):
    """One crawlable page per question (q/<id>.html in the exam's folder): question, options, answer, explanation, both languages."""
    pages = {}
    pmap = {p['id']: p for p in papers}
    by_p = {}
    for q in questions: by_p.setdefault(q['p'], []).append(q)
    pb, l2 = conf['pb'], conf['l2']
    sdir = '/' + (conf['dir'] + '/' if conf['dir'] else '')
    depth = 1 if conf['dir'] else 2
    for pid, qs in by_p.items():
        p = pmap[pid]
        paper_url = f'{sdir}papers/{p["slug"]}.html'
        for i, q in enumerate(qs):
            rel = f'q/{q["id"]}.html'
            can = SITE_URL + pb + rel
            text = re.sub(r'\s+', ' ', q['q']).strip()
            short = text if len(text) <= 80 else text[:78].rsplit(' ', 1)[0] + '…'
            kw = paper_kw(conf, p)
            title = f'{short} – {kw} Q{q["n"]} | Learn with Anil'
            desc = (f'{kw} question paper, Q{q["n"]}: {text[:140].rsplit(" ", 1)[0]}… '
                    f'Answer from {p.get("key") or conf["keyname"]}, with explanation, in English and {l2["name"]}.')
            prev_q, next_q = (qs[i - 1] if i else None), (qs[i + 1] if i + 1 < len(qs) else None)
            nav = ('<nav class="toc">'
                   + (f'<a href="{prev_q["id"]}.html">← Q{prev_q["n"]}</a>' if prev_q else '')
                   + (f'<a href="{next_q["id"]}.html">Q{next_q["n"]} →</a>' if next_q else '')
                   + f'<a href="{paper_url}">All questions of this paper</a></nav>')
            body = (f'<ol class="qs">{q_html(q, p["short"], f"{p["short"]} · Q{q["n"]}", subj, l2)}</ol>'
                    f'<p><a class="cta" href="{pb}?q={q["id"]}">Answer it in the practice app</a>'
                    f'<a class="cta alt" href="{pb}practice/">Make a topic-wise quiz</a></p>' + nav)
            lede = esc(f'Question {q["n"]} of the {p["title"]} ({p["held"]}). Try it first, then open the answer and explanation.')
            crumbs = [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), (p['title'], SITE_URL + paper_url), (f'Q{q["n"]}', can)]
            pages[rel] = static_page(depth, title, desc, can, f'{kw} · Question {q["n"]}', lede, body, crumbs, conf)
    return pages


def not_found_page():
    """GitHub Pages serves this for any unknown address. Practice-app links such as /upsc-capf/q/c2026a-3/ are sent to the app."""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found | Learn with Anil</title><meta name="robots" content="noindex">
<script>
(function(){
  var p = location.pathname, bases = ["/appsc-group-2/", "/appsc-group-1/", "/upsc-capf/", "/ts-police-si/", "/ts-police-constable/"], base = "/";
  for (var i = 0; i < bases.length; i++) if (p.indexOf(bases[i]) === 0) base = bases[i];
  var rest = p.slice(base.length);
  var ok = base === "/" ? /^exam\\/[\\w-]+\\/?$/.test(rest) : /^(q\\/[\\w-]+|quiz|result|join)\\/?$/.test(rest);
  if (ok) { try { sessionStorage.setItem("lwa-path", p); } catch (e) {} location.replace(base); }
})();
</script>
<style>body{margin:0;font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#0D1830;background:#F3F6FB}
@media (prefers-color-scheme:dark){body{color:#E5ECF8;background:#0A1020}a{color:#9DB7FF}}
main{max-width:640px;margin:0 auto;padding:48px 16px}h1{font-size:28px;margin:0 0 8px}a{color:#1440B8;font-weight:700}li{margin:6px 0}</style>
</head><body><main>
<h1>This page does not exist</h1>
<p>The address may be mistyped, or the page has moved. Try one of these:</p>
<ul><li><a href="/">All exams on Learn with Anil</a></li><li><a href="/appsc-group-2/">APPSC Group-II PYQs</a></li>
<li><a href="/appsc-group-1/">APPSC Group-I PYQs</a></li><li><a href="/upsc-capf/">UPSC CAPF (AC) PYQs</a></li>
<li><a href="/ts-police-si/">TS Police SI PYQs</a></li><li><a href="/ts-police-constable/">TS Police Constable PYQs</a></li><li><a href="/appsc-pyqs.html">All APPSC previous question papers</a></li></ul>
</main></body></html>
"""


if __name__ == '__main__':
    main()
