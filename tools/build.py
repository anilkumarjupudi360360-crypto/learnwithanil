#!/usr/bin/env python3
"""Build the Learn with Anil PYQ site (exam hub + APPSC Group-II at the root, APPSC Group-I under /appsc-group-1/).

src/*.txt  (question transcriptions)  ->  dist/  (artifact page + hostable website)
"""
import json, re, os, sys, html, base64, shutil, io, hashlib
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
DIST = os.path.join(ROOT, 'dist')
SITE_URL = os.environ.get('SITE_URL', 'https://learnwithanil.in').rstrip('/')
INSTAGRAM = 'learn_with_anil06'
WHATSAPP = '919494792739'
PHONE = '+91 94947 92739'
EMAIL = 'anilkumarjupudi360360@gmail.com'
# Google Analytics 4 measurement id (G-XXXXXXXXXX) from Anil's Analytics property; empty = no tracking tag on the site.
GA_ID = os.environ.get('GA_ID', '') or (open(os.path.join(ROOT, 'src', 'ga-id.txt')).read().strip() if os.path.exists(os.path.join(ROOT, 'src', 'ga-id.txt')) else '')


# site icon (src/static): Google shows it next to the site in search results; it wants a multiple of 48 px square
ICONS = ('<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">\n'
         '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n')


def ga_tag():
    """Google Analytics tag (page views, visitor counts, sources, cities). No tag in the artifact copy or without an id."""
    if not re.fullmatch(r'G-[A-Z0-9]{4,}', GA_ID or ''): return ''
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
            f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{GA_ID}");</script>\n')


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

# ---------- UPSC EPFO: Assistant Provident Fund Commissioner (APFC) and Enforcement Officer / Accounts Officer (EO/AO) ----------
EPFO_PAPERS = [
  dict(id='epfo25', file='apfc-eoao-2025.txt', year=2025, stage='APFC & EO/AO Recruitment Test', short='APFC & EO/AO 2025',
       title='UPSC EPFO APFC & EO/AO Recruitment Test 2025 (General Ability Test, common paper)', notif='Advt. 52/2025 · Series A · provisional answers by Learn with Anil', held='30 November 2025',
       key="answers worked out and checked by Learn with Anil (provisional: UPSC has not yet published its key)", fmt='mcq', slug='upsc-epfo-apfc-eo-ao-2025-question-paper-with-answers', alt='Assistant Provident Fund Commissioner & Enforcement Officer / Accounts Officer', kwname='UPSC EPFO APFC EO/AO 2025',
       hi_paper='एपीएफसी और प्रवर्तन अधिकारी/लेखा अधिकारी भर्ती परीक्षा', nokey=1, alabel='Provisional answer (Learn with Anil; UPSC key not yet out)',
       blurb='The first common General Ability Test for Assistant Provident Fund Commissioner and Enforcement Officer / Accounts Officer: General English, history and freedom struggle, current events, polity and economy, accounting, labour laws, social security, general science and computers, and quantitative aptitude (120 questions, 300 marks, 2 hours). UPSC has not yet published the answer key, so the answers are by Learn with Anil and will be replaced by the official key when it comes out.'),
  dict(id='pa24', file='pa-2024.txt', year=2024, stage='PA Recruitment Test', short='PA 2024',
       title='UPSC EPFO Personal Assistant Recruitment Test 2024 (General Ability Test)', notif='Advt. 51/2024 · Series A · official key', held='7 July 2024',
       key="UPSC's official answer key", fmt='mcq', slug='upsc-epfo-personal-assistant-2024-question-paper-with-answers', alt='Personal Assistant', kwname='UPSC EPFO PA 2024',
       hi_paper='वैयक्तिक सहायक (PA) भर्ती परीक्षा',
       blurb='General Ability Test for Personal Assistant in EPFO: 50 General English questions, then Indian polity and economy, current events, freedom struggle, general science and computers, and reasoning and quantitative aptitude (120 questions, 300 marks, 2 hours).'),
  dict(id='apfc23', file='apfc-2023.txt', year=2023, stage='APFC Recruitment Test', short='APFC 2023',
       title='UPSC EPFO APFC Recruitment Test 2023 (General Studies)', notif='Advt. 51/2023 · Series A · official key', held='2 July 2023',
       key="UPSC's official answer key", fmt='mcq', slug='upsc-epfo-apfc-2023-question-paper-with-answers', alt='Assistant Provident Fund Commissioner', kwname='UPSC EPFO APFC 2023',
       hi_paper='सहायक भविष्य निधि आयुक्त (APFC) भर्ती परीक्षा',
       blurb='General Studies for Assistant Provident Fund Commissioner: General English, Indian history and culture, current events, polity and economy, accounting, labour laws, social security, general science and computers, and quantitative aptitude (120 questions, 300 marks, 2 hours).'),
  dict(id='eoao23', file='eoao-2023.txt', year=2023, stage='EO/AO Recruitment Test', short='EO/AO 2023',
       title='UPSC EPFO EO/AO Recruitment Test 2023 (General Ability Test)', notif='Advt. 51/2023 · Series A · official key', held='2 July 2023',
       key="UPSC's official answer key", fmt='mcq', slug='upsc-epfo-eo-ao-2023-question-paper-with-answers', alt='Enforcement Officer / Accounts Officer', kwname='UPSC EPFO EO/AO 2023',
       hi_paper='प्रवर्तन अधिकारी/लेखा अधिकारी (EO/AO) भर्ती परीक्षा',
       blurb='General Ability Test for Enforcement Officer / Accounts Officer: General English, Indian freedom struggle, current events, polity and economy, accounting, labour laws, social security, general science and computers, and quantitative aptitude (120 questions, 300 marks, 2 hours).'),
  dict(id='eoao21', file='eoao-2021.txt', year=2021, stage='EO/AO Recruitment Test', short='EO/AO 2021',
       title='UPSC EPFO EO/AO Recruitment Test 2021 (General Ability Test, Advt. 51/2020)', notif='Advt. 51/2020 · Series A · official key', held='5 September 2021',
       key="UPSC's official answer key", fmt='mcq', slug='upsc-epfo-eo-ao-2021-question-paper-with-answers', alt='Enforcement Officer / Accounts Officer', kwname='UPSC EPFO EO/AO 2021',
       hi_paper='प्रवर्तन अधिकारी/लेखा अधिकारी (EO/AO) भर्ती परीक्षा',
       blurb='General Ability Test for Enforcement Officer / Accounts Officer (advertisement of 2020, test held in 2021): General English, Indian freedom struggle, current events, polity and economy, accounting, labour laws, social security, general science and computers, and quantitative aptitude (119 questions; UPSC dropped Q71).'),
  dict(id='eoao17', file='eoao-2017.txt', year=2017, stage='EO/AO Recruitment Test', short='EO/AO 2017',
       title='UPSC EPFO EO/AO Recruitment Test 2017 (General Ability Test, 2016 recruitment)', notif='2016 recruitment · Series A · answers by Learn with Anil', held='26 February 2017',
       key="answers worked out and checked by Learn with Anil (UPSC has published no key for this paper)", fmt='mcq', slug='upsc-epfo-eo-ao-2017-question-paper-with-answers', alt='Enforcement Officer / Accounts Officer', kwname='UPSC EPFO EO/AO 2017',
       hi_paper='प्रवर्तन अधिकारी/लेखा अधिकारी (EO/AO) भर्ती परीक्षा', nokey=1, alabel='Answer by Learn with Anil (no official key)',
       blurb='General Ability Test for Enforcement Officer / Accounts Officer of the 2016 recruitment, held on 26 February 2017 (120 questions, 100 marks, 2 hours). UPSC\'s website carries neither this paper nor its key; the questions are from a candidate\'s copy of the printed booklet and the answers are worked out and checked by Learn with Anil.'),
]



def epfo_text():
    """Wording for the EPFO page that depends on which papers are on the site."""
    have = have_src('upsc-epfo', EPFO_PAPERS)
    ps = [p for p in EPFO_PAPERS if p['id'] in have]
    eo23, eo21 = 'eoao23' in have, 'eoao21' in have
    eoy = ' & '.join(y for y, h in (('2023', eo23), ('2021', eo21)) if h)          # '2023 & 2021'
    official = [p['short'] for p in ps if not p.get('nokey')]
    nokey = [p for p in ps if p.get('nokey')]
    def ands(xs): return ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else (xs[0] if xs else '')
    ys = sorted({p['year'] for p in ps}) or [2023]
    return dict(eo=eo23 or eo21 or len(ps) > 1, eo21=eo21, eoy=eoy, n=len(ps), many=len(ps) > 3,
                papers=', '.join(p['short'] for p in ps) if len(ps) > 3 else (('APFC 2023, EO/AO ' + eoy) if (eo23 and eo21) else ('APFC 2023 & EO/AO ' + eoy) if eoy else 'APFC 2023'),
                years=f'{ys[0]}–{ys[-1]}' if len(ys) > 1 else str(ys[0]),
                pa='pa24' in have,
                official=ands(official), nokey=[(p['short'], p['held'], p['id']) for p in nokey],
                nokeyy=' and '.join(str(p['year']) for p in nokey),
                tests=ands([f"{p['short']} (held {p['held']})" for p in ps]),
                eodates=' and '.join(d for d, h in (('2 July 2023', eo23), ('5 September 2021', eo21)) if h))


def epfo_keynote(E):
    """Where the EPFO answers come from (papers page note and FAQ)."""
    t = f"Answers come from UPSC's official answer keys (Series A) on upsc.gov.in for {E['official']}." if E['official'] else ''
    if E['eo21']: t += ' UPSC dropped Q71 of the 2021 EO/AO paper, which is left out.'
    for short, held, pid in E['nokey']:
        if pid == 'epfo25': t += f" For {short} (held {held}) UPSC has not yet published its key, so the answers are worked out and double-checked by Learn with Anil and marked provisional; they will be replaced by the official key when it is out."
        else: t += f" For {short} (held {held}) UPSC's website carries neither the paper nor a key: the questions are from a candidate's copy of the printed booklet and the answers are worked out and double-checked by Learn with Anil."
    return t.strip()


EPFO_SUBJECTS = [
  ('eng', 'General English', 'general-english', ['Sentence Arrangement', 'Vocabulary & Idioms', 'Reading Comprehension', 'Grammar & Usage']),
  ('ih',  'History, Culture & Freedom Struggle', 'history-culture-freedom-struggle', ['Ancient India', 'Medieval India', 'Art & Culture', 'Modern India & Freedom Struggle']),
  ('cur', 'Current Events & Developmental Issues', 'current-events-developmental-issues', ['National', 'International', 'Schemes & Development', 'Reports & Indices', 'Awards, Sports & Persons']),
  ('pol', 'Indian Polity', 'indian-polity', ['Constitution & Rights', 'Union & State Government', 'Judiciary', 'Federalism & Local Government', 'Constitutional & Statutory Bodies']),
  ('eco', 'Indian Economy', 'indian-economy', ['Growth & National Income', 'Money, Banking & Inflation', 'Public Finance & Taxation', 'Agriculture & Industry', 'External Sector', 'Poverty, Employment & Welfare']),
  ('acc', 'General Accounting Principles', 'general-accounting-principles', ['Accounting Basics', 'Financial Statements', 'Depreciation & Valuation', 'Cost & Management Accounting', 'Auditing & Company Accounts']),
  ('lab', 'Industrial Relations & Labour Laws', 'industrial-relations-labour-laws', ['Labour Codes & Wages', 'Industrial Disputes & Trade Unions', 'Factories & Working Conditions', 'Labour Welfare & ILO']),
  ('ss',  'Social Security in India', 'social-security-in-india', ['EPF & Pension', 'ESI & Health Insurance', 'Compensation & Maternity Benefit', 'Social Security Schemes & Codes']),
  ('sci', 'General Science & Computers', 'general-science-computers', ['Physics', 'Chemistry', 'Biology', 'Computer Applications', 'Science & Technology']),
  ('qa',  'Quantitative Aptitude', 'quantitative-aptitude', ['Arithmetic', 'Algebra & Numbers', 'Data Interpretation', 'Geometry & Mensuration', 'Reasoning']),
]
EPFO_SUBJ_HI = {'eng': 'सामान्य अंग्रेज़ी', 'ih': 'इतिहास, संस्कृति और स्वतंत्रता संग्राम', 'cur': 'समसामयिक घटनाएँ और विकास के मुद्दे',
                'pol': 'भारतीय राजव्यवस्था', 'eco': 'भारतीय अर्थव्यवस्था', 'acc': 'सामान्य लेखा सिद्धांत', 'lab': 'औद्योगिक संबंध और श्रम कानून',
                'ss': 'भारत में सामाजिक सुरक्षा', 'sci': 'सामान्य विज्ञान और कंप्यूटर', 'qa': 'मात्रात्मक अभिरुचि (क्वांटिटेटिव एप्टीट्यूड)'}

# ---------- UPSC Civil Services (Preliminary): GS Paper I and CSAT (GS Paper II), 2025 and 2026 (Anil, 1 Nov 2026) ----------
PRE_HELD = {2026: '24 May 2026', 2025: '25 May 2025', 2024: '16 June 2024', 2023: '28 May 2023', 2022: '5 June 2022',
            2021: '10 October 2021', 2020: '4 October 2020', 2019: '2 June 2019'}
PRE_PROVISIONAL = {2026}       # UPSC's provisional key (27 May 2026); the final key comes after the final result
PRE_NOKEY = set()              # years whose official key could not be found: answers by Learn with Anil (sets nokey/alabel)


def _pre_paper(y, gs):
    prov, nokey = y in PRE_PROVISIONAL, y in PRE_NOKEY
    key = ("answers worked out and checked by Learn with Anil (UPSC's key could not be found)" if nokey else
           "UPSC's provisional answer key" if prov else "UPSC's official answer key")
    d = dict(id=f'gs{y}' if gs else f'csat{y}', file=f'gs-{y}.txt' if gs else f'csat-{y}.txt', year=y,
             stage='GS Paper I' if gs else 'CSAT (Paper II)', short=f'Prelims {y} · GS I' if gs else f'Prelims {y} · CSAT',
             title=(f'UPSC Prelims {y} General Studies Paper I' if gs else f'UPSC Prelims {y} CSAT (General Studies Paper II)'),
             notif='Series A · ' + ('answers by Learn with Anil' if nokey else 'provisional key' if prov else 'official key'), held=PRE_HELD[y],
             key=key, fmt='mcq',
             slug=(f'upsc-prelims-{y}-gs-paper-1-question-paper-with-answers' if gs else f'upsc-prelims-{y}-csat-paper-2-question-paper-with-answers'),
             alt=('IAS Prelims General Studies Paper 1' if gs else 'IAS Prelims CSAT Paper 2'),
             kwname=(f'UPSC Prelims {y} GS Paper 1' if gs else f'UPSC CSAT {y}'),
             hi_paper=('सामान्य अध्ययन प्रश्न-पत्र I' if gs else 'सामान्य अध्ययन प्रश्न-पत्र II (सीसैट)'),
             blurb=('General Studies Paper I: history and culture, geography, polity and governance, economy, environment, science and technology, '
                    'and current affairs (100 questions, 200 marks, 2 hours). Its marks decide who qualifies for the Mains.' if gs else
                    'General Studies Paper II (CSAT): reading comprehension, logical and analytical reasoning, basic numeracy and data interpretation '
                    '(80 questions, 200 marks, 2 hours). It is qualifying: 33% (66 marks) is needed.'))
    if nokey: d.update(nokey=1, alabel="Answer by Learn with Anil (UPSC's key not found)")
    return d


PRE_PAPERS = [_pre_paper(y, gs) for y in range(2026, 2024, -1) for gs in (True, False)]   # Anil, 1 Nov 2026 21:02: Prelims 2026 and 2025 only
PRE_SUBJECTS = [
  ('ih',  'History & Culture', 'history-culture', ['Ancient India', 'Medieval India', 'Modern India & Freedom Struggle', 'Art & Culture']),
  ('geo', 'Geography', 'geography', ['Physical Geography', 'Indian Geography', 'World Geography']),
  ('pol', 'Indian Polity & Governance', 'indian-polity-governance', ['Constitution & Rights', 'Union & State Government', 'Judiciary', 'Federalism & Local Government', 'Constitutional & Statutory Bodies', 'Governance & Policies']),
  ('eco', 'Indian Economy', 'indian-economy', ['Growth & National Income', 'Money, Banking & Inflation', 'Public Finance & Taxation', 'Agriculture & Industry', 'External Sector & Trade', 'Poverty, Employment & Welfare']),
  ('env', 'Environment & Ecology', 'environment-ecology', ['Ecology & Ecosystems', 'Biodiversity & Conservation', 'Climate Change & Pollution', 'Environmental Laws, Bodies & Conventions']),
  ('sci', 'Science & Technology', 'science-technology', ['Biology & Health', 'Physics & Chemistry', 'Space & Defence', 'IT, Computers & Emerging Technology', 'Biotechnology']),
  ('cur', 'Current Affairs & International Relations', 'current-affairs-international-relations', ['International Organisations & Groupings', 'India & the World', 'National Affairs & Schemes', 'Reports, Indices & Places in News']),
  ('rc',  'CSAT: Reading Comprehension', 'csat-reading-comprehension', ['Passages']),
  ('qa',  'CSAT: Quantitative Aptitude', 'csat-quantitative-aptitude', ['Number System', 'Arithmetic', 'Algebra', 'Geometry & Mensuration', 'Permutations, Combinations & Probability', 'Data Interpretation & Sufficiency']),
  ('lr',  'CSAT: Logical & Analytical Reasoning', 'csat-logical-reasoning', ['Logical Reasoning', 'Analytical Reasoning', 'Puzzles & Arrangements', 'Series & Patterns', 'Directions, Clocks & Calendars']),
]
PRE_SUBJ_HI = {'ih': 'इतिहास और संस्कृति', 'geo': 'भूगोल', 'pol': 'भारतीय राजव्यवस्था और शासन', 'eco': 'भारतीय अर्थव्यवस्था',
               'env': 'पर्यावरण और पारिस्थितिकी', 'sci': 'विज्ञान और प्रौद्योगिकी', 'cur': 'समसामयिकी और अंतरराष्ट्रीय संबंध',
               'rc': 'सीसैट: बोधगम्यता', 'qa': 'सीसैट: मात्रात्मक अभिरुचि', 'lr': 'सीसैट: तार्किक और विश्लेषणात्मक तर्कशक्ति'}


def pre_text():
    """Wording for the UPSC Prelims page that depends on which papers are on the site."""
    have = have_src('upsc-prelims', PRE_PAPERS)
    ys = sorted({p['year'] for p in PRE_PAPERS if p['id'] in have}) or [2026]
    yrs = f'{ys[0]}–{ys[-1]}' if len(ys) > 1 else str(ys[0])
    def ands(xs): xs = [str(x) for x in xs]; return ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else (xs[0] if xs else '')
    prov = [y for y in ys if y in PRE_PROVISIONAL]; nokey = [y for y in ys if y in PRE_NOKEY]
    official = [y for y in ys if y not in PRE_PROVISIONAL and y not in PRE_NOKEY]
    keyshort = "UPSC's official answer keys" + (f" ({ands(prov)}: provisional key)" if prov else '') + (f"; {ands(nokey)}: answers by Learn with Anil" if nokey else '')
    note = ((f"{ands(official)}: UPSC's official (final) answer key, Series A, published after the final result. " if official else '')
            + (f"{ands(prov)}: UPSC's provisional answer key, published three days after the exam (the first time UPSC has done this); "
               f"the final key, due after the final result, can differ for a few questions. " if prov else '')
            + (f"{ands(nokey)}: UPSC's key could not be found, so the answers are worked out and checked by Learn with Anil. " if nokey else '')
            + "Questions UPSC dropped are left out. Every question is in English and Hindi, as printed in the Series A booklet.")
    return dict(years=yrs, n=len(have), ylist=ands(sorted(ys, reverse=True)), keyshort=keyshort, note=note)


def FAQ_PRE(total, npapers):
    P = pre_text()
    return [
      ('Where can I get UPSC Prelims previous year question papers with answers?',
       f'This page has {total} questions from {npapers} UPSC Civil Services (Preliminary) papers, General Studies Paper I and CSAT (Paper II) of {P["ylist"]}, '
       'in English and Hindi as printed in the official question booklets, with UPSC\'s answer keys. Every question has a short explanation. You can practise '
       'each paper as a quiz or a timed test, or subject-wise (polity, history, geography, economy, environment, science, current affairs, CSAT), '
       'with one ₹45 All-in-One Pass for every exam.'),
      ('What does it cost, and what does the ₹45 All-in-One Pass cover?',
       'One plan: the ₹45 All-in-One Pass, for 12 months. It opens everything on the website: every previous paper of every exam, including exams added later, '
       'with answers, explanations, quizzes, timed tests and all study tools, every mock test series and the study books (the UPSC and APPSC Mains model answers are free to read). '
       'Without a plan you can see the question of the day, the correct answer to every question on the paper pages, and the explanations of the first 10 '
       'questions of each paper.'),
      ('Are the answers official?',
       P['note'] + ' The explanations are written by Learn with Anil.'),
      ('What is the UPSC Prelims exam pattern?',
       'The Preliminary Examination has two objective papers on the same day, each of 200 marks and two hours, in English and Hindi. General Studies '
       'Paper I has 100 questions and its marks alone decide who qualifies for the Mains. General Studies Paper II (CSAT) has 80 questions on comprehension, '
       'reasoning and basic numeracy and is qualifying: you need 33% (66 marks). A wrong answer costs one-third of the marks for that question.'),
      ('Is there a UPSC Prelims mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects such as Polity, Environment or CSAT Quantitative Aptitude, and pick Timed test: you get a mock '
       'test made of real UPSC Prelims questions, in English or Hindi, with your score and a topic-wise analysis.'),
      ('Is the UPSC Prelims question paper available in Hindi?',
       'Yes. Tap हिंदी at the top of the page to see every question and option in Hindi, exactly as printed in UPSC\'s booklet, with the explanation in '
       'Hindi. Tap EN to switch back.'),
      ('Where are the UPSC Mains papers?',
       'UPSC Mains General Studies Papers I–IV (2019–2026), with a model answer for every question, are on the UPSC Civil Services page: '
       'learnwithanil.in/upsc-cse/.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass '
       'opens the previous papers of every exam for 12 months. There is no password.'),
    ]

# ---------- SSC CGL (Combined Graduate Level): Tier-I and Tier-II, from SSC's own response sheets (SSC's key marked on them) ----------
CGL_T1_BLURB = ('Tier-I: General Intelligence & Reasoning, General Awareness, Quantitative Aptitude and English Comprehension, '
                '25 questions each: 100 questions, 200 marks, 60 minutes, −0.50 for a wrong answer.')
CGL_T2_BLURB = ('Tier-II Paper I: Mathematical Abilities (30) and Reasoning & General Intelligence (30); English Language & Comprehension (45) '
                'and General Awareness (25); Computer Knowledge (20, qualifying). 3 marks a question, −1 for a wrong answer.')
def _cgl_t1(pid, year, day, shift, time_, file_):
    return dict(id=pid, file=file_, year=year, stage='Tier-I', short=f'Tier-I {year} · {day} S{shift}',
                title=f'SSC CGL {year} Tier-I, {day} {year}, Shift {shift}', notif=f'Shift {shift} ({time_}) · SSC key', held=f'{day} {year}',
                key="SSC's answer key as marked on the candidate's response sheet", fmt='mcq',
                slug=f'ssc-cgl-{year}-tier-1-{day.lower().replace(" ", "-")}-shift-{shift}-question-paper-with-answers',
                alt='Prelims', kwname=f'SSC CGL {year} Tier 1 ({day} Shift {shift})', hi_paper=f'टियर-1 ({day}, पाली {shift})', blurb=CGL_T1_BLURB, mins=60)
CGL_PAPERS = [
  _cgl_t1('c25s1', 2025, '18 September', 1, '9:00 AM', 'cgl-2025-tier1-18sep-shift1.txt'),
  _cgl_t1('c25s2', 2025, '18 September', 2, '12:30 PM', 'cgl-2025-tier1-18sep-shift2.txt'),
  _cgl_t1('c25s3', 2025, '18 September', 3, '4:00 PM', 'cgl-2025-tier1-18sep-shift3.txt'),
  dict(id='c25t2', file='cgl-2025-tier2-paper1.txt', year=2025, stage='Tier-II Paper I', short='Tier-II 2025 · Paper I',
       title='SSC CGL 2025 Tier-II, Paper I', notif='Held 19 January 2026 · SSC key', held='19 January 2026',
       key="SSC's answer key as marked on the candidate's response sheet", fmt='mcq', slug='ssc-cgl-2025-tier-2-paper-1-question-paper-with-answers',
       alt='Mains', kwname='SSC CGL 2025 Tier 2 Paper 1', hi_paper='टियर-2 पेपर-1', blurb=CGL_T2_BLURB, mins=135),
  _cgl_t1('c24s1', 2024, '9 September', 1, '9:00 AM', 'cgl-2024-tier1-09sep-shift1.txt'),
  _cgl_t1('c23s1', 2023, '14 July', 1, '9:00 AM', 'cgl-2023-tier1-14jul-shift1.txt'),
  _cgl_t1('c24s2', 2024, '9 September', 2, '12:30 PM', 'cgl-2024-tier1-09sep-shift2.txt'),
  _cgl_t1('c24s3', 2024, '9 September', 3, '4:00 PM', 'cgl-2024-tier1-09sep-shift3.txt'),
  dict(id='c24t2', file='cgl-2024-tier2-paper1.txt', year=2024, stage='Tier-II Paper I', short='Tier-II 2024 · Paper I',
       title='SSC CGL 2024 Tier-II, Paper I', notif='Held 18 January 2025 · SSC key', held='18 January 2025',
       key="SSC's answer key as marked on the candidate's response sheet", fmt='mcq', slug='ssc-cgl-2024-tier-2-paper-1-question-paper-with-answers',
       alt='Mains', kwname='SSC CGL 2024 Tier 2 Paper 1', hi_paper='टियर-2 पेपर-1', blurb=CGL_T2_BLURB, mins=135),
]
CGL_SUBJECTS = [
  ('rea', 'General Intelligence & Reasoning', 'reasoning', ['Analogy & Classification', 'Series', 'Coding-Decoding', 'Blood Relations & Directions', 'Arrangement & Puzzles', 'Syllogism & Statements', 'Mathematical Operations', 'Non-verbal Reasoning', 'Miscellaneous Reasoning']),
  ('qa',  'Quantitative Aptitude', 'quantitative-aptitude', ['Number System & Simplification', 'Percentage, Profit & Interest', 'Ratio, Average & Mixtures', 'Time, Work, Speed & Distance', 'Algebra', 'Geometry', 'Mensuration', 'Trigonometry & Heights', 'Data Interpretation & Statistics']),
  ('eng', 'English Comprehension', 'english', ['Vocabulary', 'Idioms & One-word Substitution', 'Spelling', 'Error Spotting & Sentence Improvement', 'Fill in the Blanks & Cloze Test', 'Voice & Narration', 'Sentence Arrangement', 'Reading Comprehension']),
  ('ih',  'History & Culture', 'history', ['Ancient India', 'Medieval India', 'Modern India', 'Art & Culture']),
  ('pol', 'Indian Polity', 'polity', ['Constitution & Rights', 'Government & Parliament', 'Judiciary & Constitutional Bodies', 'Local Government & Governance']),
  ('geo', 'Geography', 'geography', ['Indian Geography', 'World & Physical Geography', 'Environment & Ecology']),
  ('eco', 'Indian Economy', 'economy', ['Planning, Growth & Budget', 'Money, Banking & Finance', 'Agriculture, Industry & Trade', 'Schemes & Welfare']),
  ('sci', 'General Science', 'general-science', ['Physics', 'Chemistry', 'Biology', 'Science & Technology']),
  ('cur', 'Current Affairs & Static GK', 'current-affairs-static-gk', ['National', 'International', 'Sports', 'Awards, Books & Persons', 'Static GK & Culture']),
  ('comp', 'Computer Knowledge', 'computer-knowledge', ['Computer Basics & Hardware', 'Software & Operating Systems', 'Internet, Networking & Security', 'MS Office & Applications']),
]
CGL_SUBJ_HI = {'rea': 'सामान्य बुद्धि और तर्कशक्ति (रीजनिंग)', 'qa': 'मात्रात्मक योग्यता (गणित)', 'eng': 'अंग्रेज़ी', 'ih': 'इतिहास और संस्कृति',
               'pol': 'भारतीय राजव्यवस्था', 'geo': 'भूगोल', 'eco': 'भारतीय अर्थव्यवस्था', 'sci': 'सामान्य विज्ञान',
               'cur': 'करेंट अफेयर्स और स्टैटिक जीके', 'comp': 'कंप्यूटर ज्ञान'}


def cgl_text():
    """Wording for the SSC CGL page that depends on which papers are on the site."""
    have = [p for p in CGL_PAPERS if p['id'] in have_src('ssc-cgl', CGL_PAPERS)]
    t1 = [p for p in have if p['stage'] == 'Tier-I']; t2 = [p for p in have if p['stage'].startswith('Tier-II')]
    years = sorted({p['year'] for p in have}) or [2025]
    yr = f'{years[0]}–{years[-1]}' if len(years) > 1 else str(years[0])
    return dict(n=len(have), t1=len(t1), t2=len(t2), years=yr,
                what=' and '.join(x for x in (f'{len(t1)} Tier-I shift paper{"s" if len(t1) != 1 else ""}' if t1 else '',
                                               f'{len(t2)} Tier-II Paper I' if t2 else '') if x))

# ---------- Telangana Police (TSLPRB, now TGPRB): SI and Constable Preliminary Written Tests ----------
TS_SI_PAPERS = [
  dict(id='s2022', file='ts-si-2022-prelims.txt', year=2022, stage='Preliminary Written Test', short='SI Prelims 2022',
       title='TSLPRB SI Preliminary Written Test 2022', notif='SCT SI (Civil) & equivalent · booklet A', held='7 August 2022',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-si-prelims-2022-question-paper-with-answers',
       blurb='Arithmetic & Test of Reasoning / Mental Ability (Q1–100) and General Studies (Q101–200): 200 questions, 200 marks, 3 hours.'),
  dict(id='s2023c', file='ts-si-2023-fwe-paper3.txt', year=2023, stage='Final Written Examination Paper III', short='SI Mains 2023 Paper III',
       title='TSLPRB SI Final Written Examination 2023, Paper III (Arithmetic & Reasoning)', notif='SCT SI (Civil) & others · booklet D', held='8 April 2023',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-si-mains-2023-paper-3-arithmetic-reasoning-question-paper-with-answers',
       alt='Final Written Exam, Arithmetic & Reasoning', te_paper='ఫైనల్ రాత పరీక్ష పేపర్-3 (అర్థమెటిక్, రీజనింగ్)',
       blurb='Final Written Examination, Paper III: Arithmetic and Test of Reasoning / Mental Ability, 200 questions, 200 marks, 3 hours.'),
  dict(id='s2023d', file='ts-si-2023-fwe-paper4.txt', year=2023, stage='Final Written Examination Paper IV', short='SI Mains 2023 Paper IV',
       title='TSLPRB SI Final Written Examination 2023, Paper IV (General Studies)', notif='SCT SI (Civil) & others · booklet D', held='9 April 2023',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-si-mains-2023-paper-4-general-studies-question-paper-with-answers',
       alt='Final Written Exam, General Studies', te_paper='ఫైనల్ రాత పరీక్ష పేపర్-4 (జనరల్ స్టడీస్)',
       blurb='Final Written Examination, Paper IV: General Studies (science, history, geography, polity, economy, current events, personality test and the Telangana movement), 200 questions, 200 marks, 3 hours.'),
]
TS_PC_PAPERS = [
  dict(id='p2022', file='ts-pc-2022-prelims.txt', year=2022, stage='Preliminary Written Test', short='PC Prelims 2022',
       title='TSLPRB Police Constable Preliminary Written Test 2022', notif='SCT PC (Civil) & equivalent · booklet A', held='28 August 2022',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-constable-prelims-2022-question-paper-with-answers',
       blurb='English, Arithmetic, Reasoning / Mental Ability and General Studies: 200 questions, 200 marks, 3 hours.'),
  dict(id='p2023', file='ts-pc-2023-fwe.txt', year=2023, stage='Final Written Examination', short='PC Mains 2023',
       title='TSLPRB Police Constable Final Written Examination 2023 (General Studies)', notif='SCT PC (Civil) & equivalent · booklet A', held='30 April 2023',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-constable-mains-2023-question-paper-with-answers',
       alt='Final Written Exam', te_paper='ఫైనల్ రాత పరీక్ష',
       blurb='Final Written Examination (General Studies): English, arithmetic, reasoning, science, history, geography, polity and economy, current events, personality test and Telangana, 200 questions, 200 marks, 3 hours.'),
  # older papers (Anil, 25 Oct 2026: "add other pyqs of constable paper also"); question booklets from tsstudies / universityupdates copies
  dict(id='p2019f', file='ts-pc-2019-fwe.txt', year=2019, stage='Final Written Examination', short='PC Mains 2019',
       title='TSLPRB Police Constable Final Written Examination 2019 (General Studies)', notif='SCT PC (Civil) & equivalent · booklet A · preliminary key', held='28 April 2019',
       key="TSLPRB's preliminary key (the final key could not be found)", fmt='mcq', slug='ts-police-constable-mains-2019-question-paper-with-answers',
       alt='Final Written Exam', te_paper='ఫైనల్ రాత పరీక్ష', alabel="Answer (TSLPRB's preliminary key)",
       blurb='Final Written Examination of the 2018 recruitment (General Studies): English, arithmetic, reasoning, science, history, geography, polity and economy, current events and Telangana, 200 questions, 200 marks, 3 hours. Answers are from TSLPRB\'s preliminary key; the final key may differ for a few questions.'),
  dict(id='p2018', file='ts-pc-2018-prelims.txt', year=2018, stage='Preliminary Written Test', short='PC Prelims 2018',
       title='TSLPRB Police Constable Preliminary Written Test 2018', notif='SCT PC (Civil) & equivalent · booklet B', held='30 September 2018',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-constable-prelims-2018-question-paper-with-answers',
       blurb='English, Arithmetic, Reasoning / Mental Ability and General Studies: 200 questions, 200 marks, 3 hours.'),
  dict(id='p2016f', file='ts-pc-2016-fwe.txt', year=2016, stage='Final Written Examination', short='PC Mains 2016',
       title='TSLPRB Police Constable Final Written Examination 2016', notif='SCT PC (Civil) & equivalent · booklet A', held='23 October 2016',
       key="TSLPRB's final key", fmt='mcq', slug='ts-police-constable-mains-2016-question-paper-with-answers',
       alt='Final Written Exam', te_paper='ఫైనల్ రాత పరీక్ష',
       blurb='Final Written Examination of the 2015–16 recruitment: English, arithmetic, reasoning, science, history, Telangana, geography, polity and economy, and current events, 200 questions, 200 marks, 3 hours.'),
  dict(id='p2016', file='ts-pc-2016-prelims.txt', year=2016, stage='Preliminary Written Test', short='PC Prelims 2016',
       title='TSLPRB Police Constable Preliminary Written Test 2016', notif='SCT PCs, SPF constables & firemen · booklet A · preliminary key', held='24 April 2016',
       key="TSLPRB's preliminary key (the final key could not be found)", fmt='mcq', slug='ts-police-constable-prelims-2016-question-paper-with-answers',
       alabel="Answer (TSLPRB's preliminary key)",
       blurb='Preliminary Written Test of the 2015–16 recruitment (SCT PCs Civil/AR/SAR CPL/TSSP, constables in SPF and firemen): English, Arithmetic, Reasoning and General Studies, 200 questions, 200 marks, 3 hours. Answers are from TSLPRB\'s preliminary key; the final key may differ for a few questions.'),
]
NOKEY_LABEL = {p['id']: p['alabel'] for p in EPFO_PAPERS + TS_PC_PAPERS if p.get('alabel')}   # answer label on papers without an official final key
# ---------- TGPSC (formerly TSPSC): Manager (Engineering) in HMWSSB, Hyderabad's water board ----------
HM_PAPERS = [
  dict(id='m15a', file='tgpsc-hmwssb-manager-2015-paper1-gs.txt', year=2015, stage='Written Examination Paper I', short='Manager 2015 Paper 1 (GS)',
       title='TSPSC Manager (Engineering), HMWSSB, 2015: Paper 1 (General Studies)', notif='Notification 13/2015 · Series A', held='1 November 2015',
       key="TSPSC's final key", fmt='mcq', slug='tgpsc-hmwssb-manager-2015-paper-1-general-studies-question-paper-with-answers',
       alt='General Studies', te_paper='పేపర్-1 జనరల్ స్టడీస్',
       blurb='Paper 1: General Studies (current affairs, science, environment, geography, history, Telangana, polity, economy, reasoning and data interpretation), 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  dict(id='m15b', file='tgpsc-hmwssb-manager-2015-paper2-civil.txt', year=2015, stage='Written Examination Paper II', short='Manager 2015 Paper 2 (Civil)',
       title='TSPSC Manager (Engineering), HMWSSB, 2015: Paper 2 (Civil Engineering)', notif='Notification 13/2015 · Series A', held='1 November 2015',
       key="TSPSC's final key", fmt='mcq', slug='tgpsc-hmwssb-manager-2015-paper-2-civil-engineering-question-paper-with-answers',
       alt='Civil Engineering', te_paper='పేపర్-2 సివిల్ ఇంజనీరింగ్', en_only=True,
       blurb='Paper 2: Civil Engineering (surveying, transportation, structures and design, geotechnical, fluid mechanics, water resources, environmental engineering, building materials and construction), 150 questions, 300 marks, 150 minutes, in English only.'),
  # Anil, 8 Nov 2026: sent the scanned ECE booklet (ME1315, code 504, Series A), "add this exam in Telangana engineering exam";
  # answers from TSPSC's final key (Series A), copy on freejobalert.com like the GS and Civil keys.
  dict(id='m15e', file='tgpsc-hmwssb-manager-2015-paper2-ece.txt', year=2015, stage='Written Examination Paper II', short='Manager 2015 Paper 2 (ECE)',
       title='TSPSC Manager (Engineering), HMWSSB, 2015: Paper 2 (Electronics & Communication Engineering)', notif='Notification 13/2015 · Series A', held='1 November 2015',
       key="TSPSC's final key", fmt='mcq', slug='tgpsc-hmwssb-manager-2015-paper-2-electronics-communication-engineering-ece-question-paper-with-answers',
       alt='Electronics & Communication Engineering (ECE)', te_paper='పేపర్-2 ఎలక్ట్రానిక్స్ & కమ్యూనికేషన్ ఇంజనీరింగ్', en_only=True,
       blurb='Paper 2: Electronics & Communication Engineering (networks, electronic devices and circuits, digital electronics, signals and systems, control systems, analog and digital communication, '
             'electromagnetics, transmission lines, microwaves and antennas), 150 questions, 300 marks, 150 minutes, in English only.'),
]
HM_SUBJECTS = [
  ('cur', 'Current Affairs', 'current-affairs', ['National', 'International', 'Telangana', 'Sports & Awards']),
  ('sci', 'General Science & Technology', 'general-science', ['Physics', 'Chemistry', 'Biology & Health', 'Science & Technology']),
  ('env', 'Environment & Disaster Management', 'environment-disaster-management', ['Environment & Ecology', 'Disaster Management']),
  ('geo', 'Geography', 'geography', ['World Geography', 'Indian Geography', 'Telangana Geography']),
  ('ih',  'Indian History & Culture', 'indian-history', ['Ancient India', 'Medieval India', 'Modern India & Freedom Struggle', 'Art & Culture']),
  ('tg',  'Telangana History & Movement', 'telangana-history-movement', ['Telangana History & Culture', 'Telangana Movement & State Formation', 'Telangana Schemes & Policies']),
  ('pol', 'Indian Polity', 'indian-polity', ['Constitution & Rights', 'Union & State Government', 'Local Government', 'Governance, Schemes & Social Issues']),
  ('eco', 'Economy', 'economy', ['Indian Economy', 'Telangana Economy']),
  ('rea', 'Reasoning & Data Interpretation', 'reasoning-data-interpretation', ['Logical Reasoning', 'Arithmetic & Mental Ability', 'Data Interpretation']),
  ('eng', 'English', 'english', ['Grammar', 'Vocabulary']),
  ('sur', 'Surveying & GIS', 'surveying', ['Surveying', 'Remote Sensing & GIS']),
  ('trn', 'Transportation Engineering', 'transportation-engineering', ['Highway Engineering', 'Traffic Engineering', 'Railways & Airports']),
  ('som', 'Strength of Materials & Structural Analysis', 'strength-of-materials-structural-analysis', ['Strength of Materials', 'Structural Analysis']),
  ('rcd', 'RCC, Steel & Prestressed Design', 'rcc-steel-design', ['RCC Design', 'Steel Design', 'Prestressed Concrete']),
  ('geot', 'Geotechnical Engineering', 'geotechnical-engineering', ['Soil Mechanics', 'Foundation Engineering']),
  ('fm',  'Fluid Mechanics & Hydraulics', 'fluid-mechanics-hydraulics', ['Fluid Mechanics', 'Hydraulics & Hydraulic Machines']),
  ('wre', 'Water Resources & Irrigation', 'water-resources-irrigation', ['Hydrology', 'Irrigation Engineering']),
  ('evn', 'Environmental Engineering', 'environmental-engineering', ['Water Supply', 'Sewerage & Wastewater Treatment', 'Solid Waste & Pollution']),
  ('bmc', 'Building Materials & Construction', 'building-materials-construction', ['Building Materials', 'Construction & Estimation', 'Construction Management']),
  # Paper 2 ECE (m15e), 8 Nov 2026
  ('nwk', 'Network Theory', 'network-theory', ['Network Laws & Theorems', 'AC Circuits & Resonance', 'Transients & Laplace Analysis', 'Two-Port Networks & Network Synthesis']),
  ('edv', 'Electronic Devices & IC Technology', 'electronic-devices', ['Semiconductor Physics', 'Diodes & Transistors', 'IC Fabrication']),
  ('anc', 'Analog Circuits', 'analog-circuits', ['Transistor Amplifiers & Biasing', 'Op-Amps & Linear ICs', 'Feedback, Oscillators & Power Supplies']),
  ('dge', 'Digital Electronics & Microprocessors', 'digital-electronics-microprocessors', ['Number Systems & Logic Gates', 'Combinational & Sequential Circuits', 'Logic Families, Memories & Converters', 'Microprocessors & Microcontrollers']),
  ('sgs', 'Signals & Systems', 'signals-systems', ['Signals & LTI Systems', 'Fourier, Laplace & Z-Transforms', 'Sampling & Digital Signal Processing']),
  ('cts', 'Control Systems', 'control-systems', ['Transfer Functions & Block Diagrams', 'Time Response & Stability', 'Frequency Response & Compensation']),
  ('acm', 'Analog Communication', 'analog-communication', ['Amplitude Modulation & Receivers', 'Frequency & Phase Modulation', 'Noise & Random Processes']),
  ('dcm', 'Digital Communication', 'digital-communication', ['Sampling, PCM & Delta Modulation', 'Digital Modulation & Detection', 'Information Theory & Coding']),
  ('emw', 'Electromagnetics & Transmission Lines', 'electromagnetics-transmission-lines', ['Vector Calculus & Electrostatics', "Magnetostatics & Maxwell's Equations", 'Wave Propagation', 'Transmission Lines']),
  ('mwa', 'Microwaves & Antennas', 'microwaves-antennas', ['Waveguides & Cavity Resonators', 'Microwave Devices', 'Antennas & Arrays']),
  ('msr', 'Measurements & Instrumentation', 'measurements-instrumentation', ['Electrical & Electronic Instruments', 'Transducers']),
  ('ocn', 'Optical, Satellite & Computer Communication', 'optical-satellite-communication', ['Optical Fibre Communication', 'Satellite & Mobile Communication', 'Computer Networks']),
]
HM_SUBJ_TE = {'cur': 'కరెంట్ అఫైర్స్', 'sci': 'జనరల్ సైన్స్', 'env': 'పర్యావరణం, విపత్తు నిర్వహణ', 'geo': 'భూగోళశాస్త్రం (జాగ్రఫీ)',
              'ih': 'భారతదేశ చరిత్ర', 'tg': 'తెలంగాణ చరిత్ర, ఉద్యమం', 'pol': 'భారత రాజ్యాంగం (పాలిటీ)', 'eco': 'భారత, తెలంగాణ ఆర్థిక వ్యవస్థ',
              'rea': 'రీజనింగ్, డేటా ఇంటర్‌ప్రిటేషన్', 'eng': 'ఇంగ్లీష్'}

# ---------- AMVI (Assistant Motor Vehicle Inspector): APPSC and TGPSC (formerly TSPSC); Anil, 26 Oct 2026 ----------
AMVI_AUTO = [
  ('thm', 'Thermodynamics & Heat Transfer', 'thermodynamics-heat-transfer', ['Thermodynamics', 'Heat Transfer', 'Refrigeration & Air Conditioning']),
  ('ice', 'IC Engines, Fuels & Emissions', 'ic-engines', ['Engine Fundamentals & Cycles', 'Fuel Supply & Combustion', 'Cooling & Lubrication', 'Fuels, Lubricants & Emissions']),
  ('chs', 'Automobile Chassis & Transmission', 'automobile-chassis-transmission', ['Chassis & Body', 'Clutch & Gearbox', 'Drive Line, Axles & Differential', 'Brakes', 'Steering & Suspension', 'Wheels & Tyres']),
  ('ael', 'Automotive Electrical & Electronics', 'automotive-electrical-electronics', ['Batteries & Charging', 'Starting & Ignition', 'Lighting, Instruments & Wiring', 'Electronics, Sensors & ECU']),
  ('mec', 'Engineering Mechanics & Machine Design', 'mechanics-machine-design', ['Engineering Mechanics', 'Strength of Materials', 'Theory of Machines', 'Machine Design']),
  ('mfg', 'Materials, Manufacturing & Metrology', 'materials-manufacturing', ['Engineering Materials', 'Manufacturing & Workshop', 'Metrology & Measurement']),
  ('flu', 'Fluid Mechanics & Hydraulics', 'fluid-mechanics', ['Fluid Mechanics', 'Hydraulic Machines & Pneumatics']),
  ('mva', 'Motor Vehicles Act, Transport & Maintenance', 'motor-vehicles-act-transport', ['Motor Vehicles Act & Rules', 'Transport Management', 'Vehicle Maintenance & Testing', 'Road Safety']),
  ('emv', 'Electric, Hybrid & Alternative-Fuel Vehicles', 'electric-alternative-vehicles', ['Electric & Hybrid Vehicles', 'Alternative Fuels']),
]
AMVI_AP_SUBJECTS = [
  ('cur', 'Current Affairs', 'current-affairs', ['National', 'International', 'AP Affairs', 'Sports & Awards', 'Reports & Indices']),
  ('sci', 'General Science & Technology', 'general-science', ['Physics', 'Chemistry', 'Biology & Health', 'Science & Technology']),
  ('ih',  'History & Culture', 'history-culture', ['Ancient India', 'Medieval India', 'Modern India & Freedom Struggle', 'Art & Culture', 'Andhra History']),
  ('geo', 'Geography & Environment', 'geography-environment', ['Indian Geography', 'AP Geography', 'World Geography', 'Environment & Ecology', 'Disaster Management']),
  ('pol', 'Indian Polity & Governance', 'indian-polity', ['Constitution & Rights', 'Union & State Government', 'Local Government', 'Governance & Schemes']),
  ('eco', 'Indian & AP Economy', 'indian-ap-economy', ['Indian Economy', 'AP Economy']),
  ('apr', 'AP Reorganisation & Issues', 'ap-reorganisation', ['AP Reorganisation Act & Issues']),
  ('men', 'Mental Ability & Data Interpretation', 'mental-ability-reasoning', ['Reasoning', 'Arithmetic', 'Data Interpretation']),
] + AMVI_AUTO
AMVI_TG_SUBJECTS = [s for s in HM_SUBJECTS if s[0] in ('cur', 'sci', 'env', 'geo', 'ih', 'tg', 'pol', 'eco', 'rea', 'eng')] + AMVI_AUTO
AMVI_AP_SUBJ_TE = {'cur': 'కరెంట్ అఫైర్స్', 'sci': 'జనరల్ సైన్స్', 'ih': 'చరిత్ర, సంస్కృతి', 'geo': 'భూగోళశాస్త్రం, పర్యావరణం', 'pol': 'భారత రాజ్యాంగం (పాలిటీ)',
                   'eco': 'భారత, ఏపీ ఆర్థిక వ్యవస్థ', 'apr': 'ఏపీ పునర్వ్యవస్థీకరణ', 'men': 'మెంటల్ ఎబిలిటీ'}
AMVI_TG_SUBJ_TE = dict(HM_SUBJ_TE)
AMVI_AP_PAPERS = [
  dict(id='a2026a', file='appsc-amvi-2026-paper1-gsma.txt', year=2026, stage='Written Examination Paper I', short='AMVI 2026 Paper 1 (GS & MA)',
       kwname='APPSC AMVI 2026 Paper 1 General Studies & Mental Ability',
       title='APPSC Assistant Motor Vehicle Inspector 2026: Paper I (General Studies & Mental Ability)', notif='Notification 21/2025 · Series A', held='27 January 2026',
       key="APPSC's final key", fmt='mcq', slug='appsc-amvi-2026-paper-1-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper='పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ',
       blurb='Paper I: General Studies & Mental Ability (current affairs, science, history, geography, polity, economy, AP affairs and mental ability), the common paper for AMVI and other APPSC posts, 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  dict(id='a2026b', file='appsc-amvi-2026-paper2-automobile.txt', year=2026, stage='Written Examination Paper II', short='AMVI 2026 Paper 2 (Automobile)',
       kwname='APPSC AMVI 2026 Paper 2 Automobile Engineering',
       title='APPSC Assistant Motor Vehicle Inspector 2026: Paper II (Automobile Engineering)', notif='Notification 21/2025 · Series A', held='28 January 2026',
       key="APPSC's final key", fmt='mcq', slug='appsc-amvi-2026-paper-2-automobile-engineering-question-paper-with-answers',
       alt='Automobile Engineering', te_paper='పేపర్-2 ఆటోమొబైల్ ఇంజనీరింగ్', en_only=True,
       blurb='Paper II: Automobile Engineering (diploma standard: thermodynamics, IC engines, chassis and transmission, auto electricals, mechanics and machine design, manufacturing, Motor Vehicles Act and transport), 150 questions, 300 marks, 150 minutes, in English.'),
  dict(id='a2023a', file='appsc-amvi-2023-paper1-gsma.txt', year=2023, stage='Written Examination Paper I', short='AMVI 2023 Paper 1 (GS & MA)',
       kwname='APPSC AMVI 2023 Paper 1 General Studies & Mental Ability',
       title='APPSC Assistant Motor Vehicle Inspector 2023: Paper I (General Studies & Mental Ability)', notif='Notification 12/2022 (Suppl. 08/2023) · CBT', held='6 October 2023',
       key="APPSC's final key", fmt='mcq', slug='appsc-amvi-2023-paper-1-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper='పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ',
       blurb='Paper I: General Studies & Mental Ability, computer-based test, 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  dict(id='a2023b', file='appsc-amvi-2023-paper2-automobile.txt', year=2023, stage='Written Examination Paper II', short='AMVI 2023 Paper 2 (Automobile)',
       kwname='APPSC AMVI 2023 Paper 2 Automobile Engineering',
       title='APPSC Assistant Motor Vehicle Inspector 2023: Paper II (Automobile Engineering)', notif='Notification 12/2022 (Suppl. 08/2023) · CBT', held='6 October 2023',
       key="APPSC's final key", fmt='mcq', slug='appsc-amvi-2023-paper-2-automobile-engineering-question-paper-with-answers',
       alt='Automobile Engineering', te_paper='పేపర్-2 ఆటోమొబైల్ ఇంజనీరింగ్', en_only=True,
       blurb='Paper II: Automobile Engineering (diploma standard), computer-based test, 150 questions, 300 marks, 150 minutes, in English.'),
  dict(id='a2019a', file='appsc-amvi-2019-paper1-gsma.txt', year=2019, stage='Written Examination Paper I', short='AMVI 2019 Paper 1 (GS & MA)',
       kwname='APPSC AMVI 2019 Paper 1 General Studies & Mental Ability',
       title='APPSC Assistant Motor Vehicle Inspector 2019: Paper I (General Studies & Mental Ability)', notif='Notification 11/2018 · answer-only key', held='April 2019',
       key="APPSC's final key", fmt='recall', slug='appsc-amvi-2019-paper-1-general-studies-mental-ability-questions-with-answers',
       alt='General Studies & Mental Ability', te_paper='పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ', en_only=True,
       blurb="Paper I: General Studies & Mental Ability, the common paper for AMVI, Agriculture Officer and Assistant Electrical Inspector. APPSC's final key prints each question with only its correct answer, so these are quick-recall questions, in English."),
  dict(id='a2019b', file='appsc-amvi-2019-paper2-automobile.txt', year=2019, stage='Written Examination Paper II', short='AMVI 2019 Paper 2 (Automobile)',
       kwname='APPSC AMVI 2019 Paper 2 Automobile Engineering',
       title='APPSC Assistant Motor Vehicle Inspector 2019: Paper II (Automobile Engineering)', notif='Notification 11/2018 · answer-only key', held='17 April 2019',
       key="APPSC's final key", fmt='recall', slug='appsc-amvi-2019-paper-2-automobile-engineering-questions-with-answers',
       alt='Automobile Engineering', te_paper='పేపర్-2 ఆటోమొబైల్ ఇంజనీరింగ్', en_only=True,
       blurb="Paper II: Automobile Engineering. APPSC's final key prints each question with only its correct answer, so these are quick-recall questions, in English."),
]
AMVI_TG_PAPERS = [
  dict(id='t2023a', file='tgpsc-amvi-2023-paper1-gs.txt', year=2023, stage='Written Examination Paper I', short='AMVI 2023 Paper 1 (GS & GA)',
       kwname='TGPSC AMVI 2023 Paper 1 General Studies & General Abilities',
       title='TSPSC Assistant Motor Vehicles Inspector 2023: Paper I (General Studies & General Abilities)', notif='Notification 31/2022 · CBRT · preliminary key', held='28 June 2023',
       key="TSPSC's preliminary key (the final key was released only on candidates' response sheets)", fmt='mcq', alabel="Answer (TSPSC's preliminary key)",
       slug='tgpsc-amvi-2023-paper-1-general-studies-question-paper-with-answers',
       alt='General Studies & General Abilities', te_paper='పేపర్-1 జనరల్ స్టడీస్ & జనరల్ ఎబిలిటీస్',
       blurb="Paper I: General Studies & General Abilities, computer-based test, 150 questions, 150 marks, 150 minutes, in English and Telugu. Answers are from TSPSC's preliminary key; the final key may differ for a few questions."),
  dict(id='t2023b', file='tgpsc-amvi-2023-paper2-automobile.txt', year=2023, stage='Written Examination Paper II', short='AMVI 2023 Paper 2 (Automobile)',
       kwname='TGPSC AMVI 2023 Paper 2 Automobile Engineering',
       title='TSPSC Assistant Motor Vehicles Inspector 2023: Paper II (Automobile Engineering)', notif='Notification 31/2022 · CBRT · preliminary key', held='28 June 2023',
       key="TSPSC's preliminary key (the final key was released only on candidates' response sheets)", fmt='mcq', alabel="Answer (TSPSC's preliminary key)",
       slug='tgpsc-amvi-2023-paper-2-automobile-engineering-question-paper-with-answers',
       alt='Automobile Engineering', te_paper='పేపర్-2 ఆటోమొబైల్ ఇంజనీరింగ్', en_only=True,
       blurb="Paper II: Automobile Engineering, computer-based test, 150 questions, 300 marks, 150 minutes, in English. Answers are from TSPSC's preliminary key; the final key may differ for a few questions."),
]
NOKEY_LABEL.update({p['id']: p['alabel'] for p in AMVI_TG_PAPERS if p.get('alabel')})

# APPSC Executive Officer Grade-III, A.P. Endowments Subordinate Service (Anil, 28 Oct 2026: Notification 23/2026, 104 posts,
# apply 16 Oct to 5 Nov 2026). Paper I General Studies & Mental Ability + Paper II Hindu Philosophy & Temple System, 150 Q each.
EO_HP_SUBJECTS = [
  ('ram', 'Ramayanam', 'ramayanam', ['Characters', 'Kandas & Places', 'Dynasties & Events']),
  ('mbh', 'Mahabharatham', 'mahabharatham', ['Characters', 'Parvas & Places', 'Bhagavad Gita & Events']),
  ('bhg', 'Bhagavatham', 'bhagavatham', ['Characters', 'Skandhas & Avatars', 'Places & Events']),
  ('pur', 'Puranas & Itihasa', 'puranas', ['Puranas', 'Tirthas & Kshetras', 'Deities & Legends']),
  ('aga', 'Temple Agamas & Worship', 'temple-agamas', ['Vaikhanasa & Pancharatra', 'Saiva & Sakta Agamas', 'Temple Rituals & Architecture']),
  ('fes', 'Festivals & Fine Arts', 'hindu-festivals-fine-arts', ['Hindu Festivals', 'Classical Arts']),
  ('ved', 'Vedic Culture', 'vedic-culture', ['Vedas & Upavedas', 'Upanishads', 'Yajnas & Ashramas']),
  ('phi', 'Philosophies, Cults & Gurus', 'hindu-philosophies-gurus', ['Advaita, Visishtadvaita & Dvaita', 'Alwars & Nayanars', 'Veerasaiva & Other Cults']),
  ('fam', 'Hindu Family Law', 'hindu-family-adoption-succession', ['Family Structure', 'Adoption', 'Succession & Marriage']),
  ('inc', 'Temple Income & Funds', 'temple-income-funds', ['Sources of Income', 'Allocation of Funds (Sec. 57)']),
  ('eod', 'Executive Officer & Endowments Act', 'executive-officer-endowments-act', ['Duties & Powers of EO (Sec. 29)', 'Endowments Administration']),
  ('lan', 'Endowment Lands & Records', 'endowment-lands-land-records', ['Land Records & ROR Act', 'Endowment Lands (Secs. 75–86)']),
]
EO_SUBJECTS = EO_HP_SUBJECTS + [s for s in AMVI_AP_SUBJECTS if s not in AMVI_AUTO]
EO_SUBJ_TE = dict(AMVI_AP_SUBJ_TE, ram='రామాయణం', mbh='మహాభారతం', bhg='భాగవతం', pur='పురాణాలు', aga='ఆగమాలు, ఆలయ పూజా విధానం',
                  fes='పండుగలు, లలిత కళలు', ved='వైదిక సంస్కృతి', phi='తత్వాలు, సంప్రదాయాలు, గురువులు', fam='హిందూ కుటుంబం, దత్తత, వారసత్వం',
                  inc='ఆలయ ఆదాయం, నిధులు', eod='కార్యనిర్వహణాధికారి, దేవాదాయ చట్టం', lan='దేవాదాయ భూములు, భూ రికార్డులు')
EO_TE_P2 = 'పేపర్-2 హిందూ తత్వశాస్త్రం & దేవాలయ వ్యవస్థ'
EO_TE_P1 = 'పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ'
EO_PAPERS = [
  dict(id='e2025b', file='appsc-eo-2026-paper2-hindu-philosophy.txt', year=2026, stage='Written Examination Paper II', short='EO 2026 Paper 2 (Hindu Philosophy)',
       kwname='APPSC EO Grade 3 2026 Paper 2 Hindu Philosophy & Temple System',
       title='APPSC Executive Officer Grade-III 2026: Paper II (Hindu Philosophy & Temple System)', notif='Notification 10/2025 · Series A', held='11 February 2026',
       key="APPSC's final key", fmt='mcq', slug='appsc-eo-grade-3-2026-paper-2-hindu-philosophy-temple-system-question-paper-with-answers',
       alt='Hindu Philosophy & Temple System', te_paper=EO_TE_P2,
       blurb='Paper II: Hindu Philosophy & Temple System (Ramayanam, Mahabharatham, Bhagavatham, Puranas, Agamas, festivals, Vedic culture, philosophies and gurus, Hindu family law, temple income, duties of the Executive Officer and endowment lands), 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  dict(id='e2025a', file='appsc-eo-2026-paper1-gsma.txt', year=2026, stage='Written Examination Paper I', short='EO 2026 Paper 1 (GS & MA)',
       kwname='APPSC EO Grade 3 2026 Paper 1 General Studies & Mental Ability',
       title='APPSC Executive Officer Grade-III 2026: Paper I (General Studies & Mental Ability)', notif='Notification 10/2025 · Series A', held='11 February 2026',
       key="APPSC's final key", fmt='mcq', slug='appsc-eo-grade-3-2026-paper-1-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper=EO_TE_P1,
       blurb='Paper I: General Studies & Mental Ability (current affairs, science, history, geography, polity, economy, AP affairs and mental ability), 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  dict(id='e2023b', file='appsc-eo-2023-mains-paper2-hindu-philosophy.txt', year=2023, stage='Main Examination Paper II', short='EO Mains 2023 Paper 2 (Hindu Philosophy)',
       kwname='APPSC EO Grade 3 Mains 2023 Paper 2 Hindu Philosophy & Temple System',
       title='APPSC Executive Officer Grade-III Mains 2023: Paper II (Hindu Philosophy & Temple System)', notif='Notification 24/2021 · CBT', held='17 February 2023',
       key="APPSC's final key", fmt='mcq', slug='appsc-eo-grade-3-mains-2023-paper-2-hindu-philosophy-temple-system-question-paper-with-answers',
       alt='Hindu Philosophy & Temple System', te_paper=EO_TE_P2,
       blurb='Mains Paper II: Hindu Philosophy & Temple System, computer-based test, 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  dict(id='e2023a', file='appsc-eo-2023-mains-paper1-gsma.txt', year=2023, stage='Main Examination Paper I', short='EO Mains 2023 Paper 1 (GS & MA)',
       kwname='APPSC EO Grade 3 Mains 2023 Paper 1 General Studies & Mental Ability',
       title='APPSC Executive Officer Grade-III Mains 2023: Paper I (General Studies & Mental Ability)', notif='Notification 24/2021 · CBT', held='February 2023',
       key="APPSC's final key", fmt='mcq', slug='appsc-eo-grade-3-mains-2023-paper-1-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper=EO_TE_P1,
       blurb='Mains Paper I: General Studies & Mental Ability, computer-based test, 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  dict(id='e2022s', file='appsc-eo-2022-screening-test.txt', year=2022, stage='Screening Test', short='EO Screening 2022',
       kwname='APPSC EO Grade 3 Screening Test 2022',
       title='APPSC Executive Officer Grade-III Screening Test 2022 (GS & Mental Ability + Hindu Philosophy & Temple System)', notif='Notification 24/2021 · answer-only key', held='2022',
       key="APPSC's final key", fmt='recall', slug='appsc-eo-grade-3-screening-test-2022-questions-with-answers',
       alt='GS & Mental Ability, Hindu Philosophy & Temple System', te_paper='స్క్రీనింగ్ టెస్ట్',
       blurb="Screening Test: Section A General Studies & Mental Ability (Q1–50) and Section B Hindu Philosophy & Temple System (Q51–150). APPSC's final key prints each question with only its correct answer, so these are quick-recall questions, in English and Telugu."),
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


def add_own_options(paper, qs, srcdir=''):
    """Answer-only papers: APPSC's final key prints each question with only the correct answer. At Anil's request
    (23 Oct 2026) Learn with Anil writes three wrong options per question: src/[<exam>/]opts/<file>.json
    {"<n>": {"d": [3 English], "dt": [3 Telugu]}}. The official answer goes in at a fixed pseudo-random place.
    Such questions are marked lwo=1 so the app and pages say the options are ours and the answer is APPSC's."""
    path = os.path.join(SRC, srcdir, 'opts', paper['file'].replace('.txt', '.json'))
    if not os.path.exists(path): return 0
    od = json.load(open(path, encoding='utf-8')); n = 0
    for q in qs:
        o = od.get(str(q['n']))
        if 'ans' not in q or not o or len(o.get('d') or []) != 3: continue
        pos = int(hashlib.md5(q['id'].encode()).hexdigest(), 16) % 4
        q['o'] = o['d'][:pos] + [q['ans']] + o['d'][pos:]; q['a'] = [pos]
        if q.get('at') and len(o.get('dt') or []) == 3: q['ot'] = o['dt'][:pos] + [q['at']] + o['dt'][pos:]
        q.pop('ans'); q.pop('at', None); q['lwo'] = 1; n += 1
    return n


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
        nown = add_own_options(p, qs, conf['src'])
        if not qs:
            print(f'  - skipping {conf["short"]} {p["id"]} (no source yet)'); continue
        for q in qs:
            if 'img' in q: q['img'] = img_data_uri(os.path.join(conf['src'], q['img']))
        pp = {k: p[k] for k in ('id', 'year', 'stage', 'short', 'title', 'notif', 'held', 'fmt', 'slug', 'blurb')}
        pp['count'] = len(qs)
        if nown:
            if nown == len(qs): pp['fmt'], pp['own'] = 'mcq', 1   # four options now (ours + APPSC's answer); still All-in-One Pass only
            else: print(f'  ! {conf["short"]} {p["id"]}: options for {nown} of {len(qs)} questions only; paper stays quick-recall')
        for k in ('key', 'alt', 'te_paper', 'hi_paper', 'en_only', 'kwname', 'mins', 'nokey', 'alabel'):
            if p.get(k): pp[k] = p[k]
        pp['pdf'] = pdf_href(conf, p) if PUBLIC_PDFS else ''
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
        el = [q for q in questions if q.get('o') and not q.get('lwo') and not q.get('img') and q.get('w') and len(q['q']) <= 520
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


def have_src(src, papers):
    """Ids of the papers whose source file exists (load_exam skips the others)."""
    return [p['id'] for p in papers if os.path.exists(os.path.join(SRC, src, p['file']))]


def ts_text():
    """Wording for the TS Police pages that depends on which 2023 Final Written Examination papers are on the site."""
    si = [i for i in have_src('ts-police-si', TS_SI_PAPERS) if i != 's2022']
    pc = [i for i in have_src('ts-police-constable', TS_PC_PAPERS) if i != 'p2022']
    si_fwe = 'Papers III and IV' if len(si) > 1 else {'s2023c': 'Paper III, Arithmetic & Reasoning', 's2023d': 'Paper IV, General Studies'}.get(si[0], '') if si else ''
    have = have_src('ts-police-constable', TS_PC_PAPERS)
    pcs = sorted([p for p in TS_PC_PAPERS if p['id'] in have], key=lambda p: (-p['year'], p['id']))
    def yrs(stage): return sorted({p['year'] for p in pcs if p['stage'] == stage})
    def ands(xs): xs = [str(x) for x in xs]; return ', '.join(xs[:-1]) + ' & ' + xs[-1] if len(xs) > 1 else (xs[0] if xs else '')
    prelim = [p for p in pcs if 'preliminary key' in p.get('key', '')]
    return dict(si=si, pc=pc, si_fwe=si_fwe, pcs=pcs, pcmany=len(pcs) > 2,
                pc_pre=ands(yrs('Preliminary Written Test')), pc_fwe=ands(yrs('Final Written Examination')),
                pc_years=f"{pcs[-1]['year']}–{pcs[0]['year']}" if pcs else '',
                pc_prelim=[p['short'] for p in prelim],
                pc_list=ands([f"{p['short']} (held {p['held']}, booklet {p['notif'].split('booklet ')[1].split(' ')[0]})" for p in pcs]).replace(' & ', ' and '))



# ---------- Andhra Pradesh Police (SLPRB AP): SI and Constable ----------
# Anil, 2 Nov 2026: "pls also add APPSC SI Police & Constable PYQs...the notification is on" (SLPRB AP notifications of 16 Sep 2026:
# Rc.No.81/SLPRB/Rect.1/2026 for SIs, Rc.No.91/SLPRB/Rect.2/2026 for PCs; 2,050 posts in all; application dates to be announced).
# Papers: SLPRB's own booklet PDF (Constable PWT 2023) and scanned booklets (SI PWT 2023), answers from SLPRB's keys (column A).
AP_SI_PAPERS = [
  dict(id='a2023s1', file='ap-si-2023-prelims-paper1.txt', year=2023, stage='Preliminary Written Test Paper I', short='SI Prelims 2023 Paper I',
       title='SLPRB AP SI Preliminary Written Test 2023, Paper I (Arithmetic & Reasoning)', notif='SCT SI (Civil) & RSI (APSP) · booklet A', held='19 February 2023',
       key="SLPRB's final key", fmt='mcq', slug='ap-police-si-prelims-2023-paper-1-arithmetic-reasoning-question-paper-with-answers',
       alt='Prelims Paper I, Arithmetic & Reasoning', te_paper='ప్రిలిమినరీ పేపర్-1 (అర్థమెటిక్, రీజనింగ్)',
       blurb='Preliminary Written Test, Paper I: Arithmetic (SSC standard) and Test of Reasoning / Mental Ability, 100 questions, 100 marks, 3 hours.'),
  dict(id='a2023s2', file='ap-si-2023-prelims-paper2.txt', year=2023, stage='Preliminary Written Test Paper II', short='SI Prelims 2023 Paper II',
       title='SLPRB AP SI Preliminary Written Test 2023, Paper II (General Studies)', notif='SCT SI (Civil) & RSI (APSP) · booklet C · preliminary key', held='19 February 2023',
       key="SLPRB's preliminary key (the final key could not be found)", fmt='mcq', alabel="Answer (SLPRB's preliminary key)",
       slug='ap-police-si-prelims-2023-paper-2-general-studies-question-paper-with-answers',
       alt='Prelims Paper II, General Studies', te_paper='ప్రిలిమినరీ పేపర్-2 (జనరల్ స్టడీస్)',
       blurb="Preliminary Written Test, Paper II: General Studies (degree standard), 100 questions, 100 marks, 3 hours. Answers are from SLPRB's preliminary key; "
             "SLPRB's final key changed only one question of this paper, to accept more than one answer."),
]
AP_PC_PAPERS = [
  dict(id='a2023pc', file='ap-pc-2023-prelims.txt', year=2023, stage='Preliminary Written Test', short='PC Prelims 2023',
       title='SLPRB AP Police Constable Preliminary Written Test 2023', notif='SCT PC (Civil) & PC (APSP) · booklet A', held='22 January 2023',
       key="SLPRB's final key", fmt='mcq', slug='ap-police-constable-prelims-2023-question-paper-with-answers',
       blurb='Preliminary Written Test (Intermediate standard): English, Arithmetic, Reasoning / Mental Ability and General Studies, 200 questions, 200 marks, 3 hours.'),
]
AP_SUBJECTS = [s if s[0] != 'tg' else
               ('ap', 'Andhra Pradesh', 'andhra-pradesh', ['AP History & Culture', 'AP Geography & Economy', 'AP Schemes & Affairs']) for s in TS_SUBJECTS]
AP_POLICE_SUBJ_TE = {'ari': 'అర్థమెటిక్ (అంకగణితం)', 'rea': 'రీజనింగ్, మెంటల్ ఎబిలిటీ', 'eng': 'ఇంగ్లీష్', 'sci': 'జనరల్ సైన్స్', 'ih': 'భారతదేశ చరిత్ర, సంస్కృతి',
                     'ap': 'ఆంధ్రప్రదేశ్', 'geo': 'భూగోళశాస్త్రం (జాగ్రఫీ)', 'pol': 'భారత రాజ్యాంగం (పాలిటీ)', 'eco': 'భారత ఆర్థిక వ్యవస్థ',
                     'cur': 'కరెంట్ అఫైర్స్', 'soc': 'నైతికత, సామాజిక స్పృహ'}


# APPSC Analyst Grade-II, A.P. Pollution Control Board (Anil, 1 Nov 2026: Notification 21/2026, 18 posts, apply 13 Oct to 2 Nov 2026).
# Previous papers: Notification 02/2024, computer-based test, March 2025; APPSC's final keys (APOnline master question papers,
# correct option ticked). Paper II was one paper per degree subject in 2025 (Chemistry, Biochemistry, Biology, Environmental
# Science); from 2026 it is one Common Paper covering all four, so all four 2025 papers are practice for it. English only.
ANALYST_P2_SUBJECTS = [
  ('chm', 'Chemistry', 'chemistry', ['Inorganic Chemistry', 'Photochemistry & Spectroscopy', 'Chromatography & Analytical Methods', 'Organic & Natural Products', 'Amino Acids & Proteins', 'Green Chemistry', 'Physical & General Chemistry']),
  ('bch', 'Biochemistry', 'biochemistry', ['Enzymes & Coenzymes', 'Immunology', 'Blood & Body Systems', 'Endocrinology', 'Nutrition & Vitamins', 'Clinical Biochemistry', 'Biomolecules & Metabolism']),
  ('bio', 'Biology', 'biology', ['Bacteria & Viruses', 'Cell Biology', 'Genetics & Evolution', 'Molecular Biology', 'Plant & Animal Biology']),
  ('evs', 'Environmental Science', 'environmental-science', ['Ecology & Ecosystems', 'Natural Resources', 'Pollution & Waste Management', 'Climate Change & Global Issues', 'Environmental Assessment & Planning', 'Environmental Laws & Policy']),
]
ANALYST_SUBJECTS = ANALYST_P2_SUBJECTS + [s for s in AMVI_AP_SUBJECTS if s not in AMVI_AUTO]   # Paper I GS & MA added 8 Nov 2026
ANALYST_SUBJ_TE = dict(AMVI_AP_SUBJ_TE, chm='రసాయన శాస్త్రం', bch='జీవ రసాయన శాస్త్రం', bio='జీవ శాస్త్రం', evs='పర్యావరణ శాస్త్రం')
ANALYST_TE_P2 = 'పేపర్-2 కామన్ పేపర్'
def _an_paper(pid, subj, slugsub, blurbsub):
    return dict(id=pid, file=f'appsc-analyst-2025-paper2-{slugsub}.txt', year=2025, stage=f'Written Examination Paper II ({subj})', short=f'Analyst 2025 Paper 2 ({subj})',
                kwname=f'APPSC Analyst Grade 2 2025 Paper 2 {subj}',
                title=f'APPSC Analyst Grade-II 2025: Paper II {subj} (A.P. Pollution Control Board)', notif='Notification 02/2024 · CBT', held='March 2025',
                key="APPSC's final key", fmt='mcq', slug=f'appsc-analyst-grade-2-2025-paper-2-{slugsub}-question-paper-with-answers',
                alt=subj, te_paper=ANALYST_TE_P2, en_only=True,
                blurb=f'Paper II {subj}: {blurbsub} Computer-based test, 150 questions, 300 marks, 150 minutes, in English. In 2025 each candidate wrote the Paper II of their degree subject; from 2026 Paper II is one Common Paper covering Chemistry, Biochemistry, Biology and Environmental Science.')
ANALYST_PAPERS = [
  _an_paper('n2025c', 'Chemistry', 'chemistry', 'non-transition elements, boranes, photochemistry, spectroscopy and Beer–Lambert law, chromatography, terpenoids, amino acids, green chemistry and heterocyclic compounds.'),
  _an_paper('n2025b', 'Biochemistry', 'biochemistry', 'enzymes and coenzymes, immunology, blood and lymph, nervous and excretory systems, hormones, nutrition and vitamins, and clinical biochemistry.'),
  _an_paper('n2025g', 'Biology', 'biology', 'bacteria and viruses, cell biology, mitosis and meiosis, Mendelian genetics, mutations, evolution and molecular biology.'),
  _an_paper('n2025e', 'Environmental Science', 'environmental-science', 'ecology and ecosystems, natural resources, air, water and soil pollution, waste management, global warming, environmental assessment and eco-planning.'),
  # Anil, 8 Nov 2026 ("add the rest also" -> Analyst + FRO GS papers): Paper I is the same APOnline paper (byte-identical final key PDF)
  # that was set on 25 March 2025 for Assistant Environmental Engineer; the checked AEE text is reused (src/appsc-analyst/*paper1*).
  dict(id='n2025a', file='appsc-analyst-2025-paper1-gsma.txt', year=2025, stage='Written Examination Paper I', short='Analyst 2025 Paper 1 (GS & MA)',
       kwname='APPSC Analyst Grade 2 2025 Paper 1 General Studies & Mental Ability',
       title='APPSC Analyst Grade-II 2025: Paper I (General Studies & Mental Ability)', notif='Notification 02/2024 · CBT', held='25 March 2025',
       key="APPSC's final key", fmt='mcq', slug='appsc-analyst-grade-2-2025-paper-1-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper=EO_TE_P1,
       blurb='Paper I: General Studies & Mental Ability (current affairs, science, history, geography, polity, economy, AP affairs and mental ability), computer-based test, '
             '150 questions, 150 marks, 150 minutes, in English and Telugu. The same paper was set that day for Assistant Environmental Engineer of the A.P. Pollution Control Board.'),
]

# APPSC Forest Range Officer, A.P. Forest Service (Anil, 1 Nov 2026: Notification 16/2026, 5 posts, apply 16 Oct to 5 Nov 2026).
# Main examination: qualifying English & Telugu, Paper I GS & MA, Paper II Mathematics, Paper III General Forestry I,
# Paper IV General Forestry II. First the General Forestry papers of the 2023 (Notification 21/2022) and 2020 (Notification
# 10/2018) Mains, from APPSC's final keys on the APOnline master question papers. English only.
FRO_FORESTRY_SUBJECTS = [
  ('nrs', 'Natural Resources', 'natural-resources', ['Forest & Water Resources', 'Mineral, Food & Energy Resources', 'Land Resources & Soil Erosion']),
  ('pls', 'Plant Sciences', 'plant-sciences', ['Classification & Morphology', 'Plant Anatomy & Wood', 'Reproduction & Propagation', 'Plant Physiology', 'Genetics & Plant Diseases']),
  ('bdc', 'Biodiversity & Conservation', 'biodiversity-conservation', ['Biodiversity & Hotspots', 'Biomes & Population Ecology']),
  ('ssg', 'Soil Science & Geology', 'soil-science-geology', ['Rocks & Minerals', 'Soil Properties & Formation', 'Soil Conservation & Reclamation', 'Soil Organic Matter & Nutrient Cycles']),
  ('wsm', 'Water & Watershed Management', 'watershed-management', ['Water Resources', 'Watershed & Water Harvesting']),
  ('slv', 'Silviculture & Agroforestry', 'silviculture-agroforestry', ['Silvicultural Principles & Regeneration', 'Nursery & Planting', 'Silviculture of Species', 'Agroforestry', 'Social & Community Forestry']),
  ('ecw', 'Ecosystems & Wildlife', 'ecosystems-wildlife', ['Ecosystem Concepts', 'Types of Ecosystems', 'Wildlife & Protected Areas']),
  ('fpt', 'Forest Protection', 'forest-protection', ['Pests & Diseases', 'Forest Fire', 'Grazing & Human Impacts']),
  ('fut', 'Forest Utilization & NTFP', 'forest-utilization-ntfp', ['Logging & Wood Technology', 'Wood Properties', 'NTFPs & Medicinal Plants']),
  ('anm', 'Animal Management & Economic Zoology', 'animal-management-zoology', ['Animal Health & Nutrition', 'Snakes & Venomous Animals', 'Birds', 'Economic Zoology']),
  ('fel', 'Forest Economics, Policy & Law', 'forest-economics-policy-law', ['Forest Economics', 'Forest Policy', 'Forest & Environment Laws', 'Forest Administration']),
  ('fim', 'Forest Inventory, Mensuration & Remote Sensing', 'forest-mensuration-remote-sensing', ['Sampling & Inventory', 'Tree & Stand Measurement', 'Remote Sensing & GIS']),
  ('ens', 'Environmental Science', 'environmental-science', ['Pollution', 'Waste Management', 'Climate & Global Issues', 'Environmental Laws & Ethics']),
  ('fse', 'Forest Survey, Engineering & First Aid', 'forest-survey-first-aid', ['Survey & Engineering', 'First Aid']),
]
# Anil, 8 Nov 2026 ("add the rest also"): FRO General Studies papers added (2025 and 2019 Screening, 2023 and 2020 Mains GS & MA).
FRO_SUBJECTS = FRO_FORESTRY_SUBJECTS + [s for s in AMVI_AP_SUBJECTS if s not in AMVI_AUTO] + [
  ('mth', 'Mathematics', 'mathematics', ['Algebra', 'Geometry & Mensuration', 'Trigonometry', 'Statistics & Probability'])]
FRO_SUBJ_TE = dict(AMVI_AP_SUBJ_TE, nrs='సహజ వనరులు', pls='వృక్ష శాస్త్రం', bdc='జీవవైవిధ్యం, సంరక్షణ', ssg='మృత్తిక శాస్త్రం, భూగర్భ శాస్త్రం', wsm='నీటి వనరులు, వాటర్‌షెడ్ నిర్వహణ',
                   slv='సిల్వికల్చర్, వ్యవసాయ అటవీకరణ', ecw='పర్యావరణ వ్యవస్థలు, వన్యప్రాణులు', fpt='అటవీ సంరక్షణ', fut='అటవీ ఉత్పత్తుల వినియోగం', anm='జంతు నిర్వహణ, ఆర్థిక జంతుశాస్త్రం',
                   fel='అటవీ ఆర్థిక శాస్త్రం, విధానం, చట్టాలు', fim='అటవీ ఇన్వెంటరీ, కొలతలు, రిమోట్ సెన్సింగ్', ens='పర్యావరణ శాస్త్రం', fse='సర్వే, ఇంజనీరింగ్, ప్రథమ చికిత్స', mth='గణితం')
def _fro_paper(pid, year, notif, held, n, roman):
    nm = f'General Forestry {"I" * n}'
    return dict(id=pid, file=f'appsc-fro-{year}-mains-general-forestry-{n}.txt', year=year, stage=f'Main Examination {roman} ({nm})', short=f'FRO Mains {year} {nm}',
                kwname=f'APPSC FRO Mains {year} General Forestry {n}',
                title=f'APPSC Forest Range Officer Mains {year}: {roman} {nm}', notif=f'{notif} · CBT', held=held,
                key="APPSC's final key", fmt='mcq', slug=f'appsc-fro-mains-{year}-general-forestry-{n}-question-paper-with-answers',
                alt=nm, te_paper=f'జనరల్ ఫారెస్ట్రీ-{n}', en_only=True,
                blurb=(f'{roman}: {nm} ' + ('(natural resources, plant sciences, biodiversity, soil science and geology, watershed management, silviculture of AP species and agroforestry)'
                                           if n == 1 else '(ecosystems and wildlife, forest protection and fire, forest utilization and NTFPs, animal management, forest economics, policy and laws, inventory, mensuration and remote sensing, environmental science, survey and first aid)')
                       + ', computer-based test, 150 questions, 150 marks, 150 minutes, in English.'))
FRO_PAPERS = [
  dict(id='f2025s', file='appsc-fro-2025-screening-test.txt', year=2025, stage='Screening Test', short='FRO Screening 2025',
       kwname='APPSC FRO Screening Test 2025', title='APPSC Forest Range Officer Screening Test 2025 (General Studies, Mental Ability & Mathematics and General Forestry)',
       notif='Notification 11/2024 · CBT', held='16 March 2025', key="APPSC's final key", fmt='mcq', slug='appsc-fro-screening-test-2025-question-paper-with-answers',
       alt='Screening Test', te_paper='స్క్రీనింగ్ టెస్ట్',
       blurb='Screening Test (online): Section 1 General Studies, Mental Ability & Mathematics (75 questions, in English and Telugu) and Section 2 General Forestry I & II (75 questions, in English), 150 marks, 150 minutes.'),
  dict(id='f2023a', file='appsc-fro-2023-mains-paper1-gsma.txt', year=2023, stage='Main Examination Paper I (General Studies & Mental Ability)', short='FRO Mains 2023 Paper I (GS & MA)',
       kwname='APPSC FRO Mains 2023 Paper 1 General Studies & Mental Ability', title='APPSC Forest Range Officer Mains 2023: Paper I General Studies & Mental Ability',
       notif='Notification 21/2022 · CBT', held='25 September 2023', key="APPSC's final key", fmt='mcq', slug='appsc-fro-mains-2023-paper-1-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper=EO_TE_P1,
       blurb='Paper I: General Studies & Mental Ability, computer-based test, 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
  _fro_paper('f2023c', 2023, 'Notification 21/2022', '26 September 2023', 1, 'Paper III'),
  _fro_paper('f2023d', 2023, 'Notification 21/2022', '27 September 2023', 2, 'Paper IV'),
  _fro_paper('f2020c', 2020, 'Notification 10/2018', '18 March 2020', 1, 'Paper III'),
  _fro_paper('f2020d', 2020, 'Notification 10/2018', '19 March 2020', 2, 'Paper IV'),
  dict(id='f2020a', file='appsc-fro-2020-mains-gsma.txt', year=2020, stage='Main Examination Paper I (General Studies & Mental Ability)', short='FRO Mains 2020 Paper I (GS & MA)',
       kwname='APPSC FRO Mains 2020 General Studies & Mental Ability', title='APPSC Forest Range Officer Mains 2020: General Studies & Mental Ability',
       notif='Notification 10/2018 · CBT', held='17 March 2020', key="APPSC's final key", fmt='mcq', slug='appsc-fro-mains-2020-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper=EO_TE_P1, en_only=True,
       blurb='Paper I: General Studies & Mental Ability, computer-based test, 150 questions, 150 marks, 150 minutes, in English (the master paper prints English only).'),
  dict(id='f2019s', file='appsc-fro-2019-screening-test.txt', year=2019, stage='Screening Test', short='FRO Screening 2019',
       kwname='APPSC FRO Screening Test 2019', title='APPSC Forest Range Officer Screening Test 2019 (General Studies & Mental Ability, Mathematics and General Forestry)',
       notif='Notification 10/2018 · answer-only key', held='2019', key="APPSC's final key", fmt='recall', slug='appsc-fro-screening-test-2019-questions-with-answers',
       alt='Screening Test', te_paper='స్క్రీనింగ్ టెస్ట్', en_only=True,
       blurb="Screening Test: General Studies & Mental Ability, Mathematics and General Forestry. APPSC's final key prints each question with only its correct answer, so these are quick-recall questions, in English."),
]

# APPSC Assistant Environmental Engineer, A.P. Pollution Control Board (Anil, 8 Nov 2026: "pls add pyqs for it in ap section",
# Notification 08/2026 of 6 Oct 2026, 41 posts incl. 1 carried forward, applications 6 to 27 Oct 2026). Previous papers:
# Notification 15/2023, computer-based test of 25 March 2025, APPSC's final keys of 6 Aug 2025 (APOnline master question
# papers, correct option ticked). Paper I GS & MA in English and Telugu (the same paper was set that day for Analyst
# Grade-II); Paper II Common Subject in English only. Exam id appsc-env-engineer, because the start page already has an
# "appsc-aee" tile (Assistant Executive Engineer).
AEE_P2_SUBJECTS = [
  ('ecs', 'Ecosystems', 'ecosystems', ['Ecosystem Structure & Function', 'Food Chains, Webs & Pyramids', 'Biogeochemical Cycles & Bioaccumulation']),
  ('nrr', 'Natural Resources', 'natural-resources', ['Water Resources & Dams', 'Mineral & Land Resources', 'Forest Resources', 'Energy Resources']),
  ('bdv', 'Biodiversity & Biotic Resources', 'biodiversity', ['Biodiversity & Its Value', 'Hotspots & Threats', 'Conservation & Biodiversity Act']),
  ('emt', 'Engineering Materials', 'engineering-materials', ['Structure & Properties', 'Phase Diagrams & Heat Treatment', 'Stress-Strain Behaviour']),
  ('flu', 'Fluid Mechanics & Hydraulics', 'fluid-mechanics-hydraulics', ['Fluid Properties & Pressure', 'Fluid Kinematics & Dynamics', 'Pipe Flow & Losses', 'Dimensional Analysis & Boundary Layer']),
  ('ptd', 'Process Calculations & Thermodynamics', 'process-calculations-thermodynamics', ['Material & Energy Balances', 'Laws of Thermodynamics', 'Equations of State & Properties']),
  ('apc', 'Air, Water, Soil & Noise Pollution', 'pollution-control-technologies', ['Air Pollution & Control', 'Water Quality & Wastewater Treatment', 'Soil Pollution', 'Noise Pollution']),
  ('swm', 'Solid & Industrial Waste Management', 'solid-industrial-waste-management', ['Municipal Solid Waste', 'E-Waste & Hazardous Waste', 'Bioremediation']),
  ('gel', 'Global Environment, Policies & Laws', 'environmental-policies-laws', ['Climate Change & Ozone', 'International Conventions', 'Indian Environmental Laws & Rules']),
  ('eia', 'EIA & Sustainable Development', 'eia-sustainable-development', ['EIA & EMP', 'Sustainable Development & Green Concepts']),
]
AEE_SUBJECTS = AEE_P2_SUBJECTS + [s for s in AMVI_AP_SUBJECTS if s not in AMVI_AUTO]
AEE_SUBJ_TE = dict(AMVI_AP_SUBJ_TE, ecs='పర్యావరణ వ్యవస్థలు', nrr='సహజ వనరులు', bdv='జీవవైవిధ్యం, జీవ వనరులు', emt='ఇంజనీరింగ్ మెటీరియల్స్',
                   flu='ఫ్లూయిడ్ మెకానిక్స్, హైడ్రాలిక్స్', ptd='ప్రాసెస్ కాలిక్యులేషన్స్, థర్మోడైనమిక్స్', apc='వాయు, నీటి, నేల, శబ్ద కాలుష్యం',
                   swm='ఘన, పారిశ్రామిక వ్యర్థాల నిర్వహణ', gel='ప్రపంచ పర్యావరణ సమస్యలు, విధానాలు, చట్టాలు', eia='పర్యావరణ ప్రభావ అంచనా, సుస్థిర అభివృద్ధి')
def aee_p1():
    """True once the 2025 Paper I (GS & MA) source is on the site (Anil, 8 Nov 2026: "focus on paper-2 first")."""
    return 'v25g' in have_src('appsc-env-engineer', AEE_PAPERS)
AEE_PAPERS = [
  dict(id='v25c', file='appsc-aee-2025-paper2-common-subject.txt', year=2025, stage='Written Examination Paper II', short='AEE 2025 Paper 2 (Common Subject)',
       kwname='APPSC Assistant Environmental Engineer 2025 Paper 2 Common Subject',
       title='APPSC Assistant Environmental Engineer 2025: Paper II (Common Subject, A.P. Pollution Control Board)', notif='Notification 15/2023 · CBT', held='25 March 2025',
       key="APPSC's final key", fmt='mcq', slug='appsc-assistant-environmental-engineer-2025-paper-2-common-subject-question-paper-with-answers',
       alt='Common Subject (Environmental Engineering)', te_paper='పేపర్-2 కామన్ సబ్జెక్ట్', en_only=True,
       blurb='Paper II: Common Subject (ecosystems, natural resources, biodiversity, engineering materials, fluid mechanics and hydraulics, process calculations and thermodynamics, '
             'air, water, soil and noise pollution and their control, solid and e-waste, environmental laws and conventions, EIA and sustainable development), computer-based test, '
             '150 questions, 300 marks, 150 minutes, in English. In the 2026 exam (Notification 08/2026) Paper II carries 150 marks.'),
  dict(id='v25g', file='appsc-aee-2025-paper1-gsma.txt', year=2025, stage='Written Examination Paper I', short='AEE 2025 Paper 1 (GS & MA)',
       kwname='APPSC Assistant Environmental Engineer 2025 Paper 1 General Studies & Mental Ability',
       title='APPSC Assistant Environmental Engineer 2025: Paper I (General Studies & Mental Ability)', notif='Notification 15/2023 · CBT', held='25 March 2025',
       key="APPSC's final key", fmt='mcq', slug='appsc-assistant-environmental-engineer-2025-paper-1-general-studies-mental-ability-question-paper-with-answers',
       alt='General Studies & Mental Ability', te_paper=EO_TE_P1,
       blurb='Paper I: General Studies & Mental Ability (current affairs, science, history, geography, polity, economy, AP affairs and mental ability), computer-based test, '
             '150 questions, 150 marks, 150 minutes, in English and Telugu. The same paper was set that day for Analyst Grade-II of the A.P. Pollution Control Board.'),
]

# APPSC Assistant Statistical Officer, A.P. Economics & Statistical Subordinate Service (Anil, 8 Nov 2026, after the TGPSC
# MPSO/ASO notification page: "do we dont have anyother pyqs ?" -> "ok" to adding the APPSC Statistics papers). Paper II
# (Subject: economics, financial accounting, statistics, basics of computers) of two exams, APOnline master question papers
# with APPSC's final key (correct option ticked): Notification 12/2024 (5 posts), CBT 29 April 2025, bilingual text
# (computer questions English only); Notification 20/2021 (29 posts), CBT 4 November 2022 ("ECOSTATS 0411S2"), every
# question printed as a picture with English and Telugu. Paper I (GS & MA) is the common APPSC paper of those days.
ASO_SUBJECTS = [
  ('ect', 'Economic Theory', 'economic-theory', ['Demand, Supply & Elasticity', 'Market Structures & Pricing', 'Production, Costs & Factor Pricing', 'National Income', 'Money, Banking & Inflation', 'Public Finance & Budget']),
  ('ine', 'International Economics', 'international-economics', ['Trade & Protection', 'Balance of Payments & Exchange Rates', 'IMF, World Bank & Monetary System']),
  ('ind', 'Indian Economy', 'indian-economy', ['Population & Human Development', 'Poverty, Unemployment & Inequality', 'Agriculture, Industry & Regional Imbalances', 'Planning & Economic Policies', 'Inflation, Fiscal Deficit & External Debt']),
  ('acc', 'Financial Accounting', 'financial-accounting', ['Accounting Concepts & Principles', 'Journal, Ledger & Subsidiary Books', 'Bank Reconciliation, Trial Balance & Final Accounts', 'Depreciation, Errors & Company Law']),
  ('cmp', 'Basics of Computers', 'computers', ['Digital Logic & Number Systems', 'Memory & Hardware', 'MS Excel & Office']),
  ('sdc', 'Statistics: Data, Sampling & Diagrams', 'statistics-data-collection-sampling', ['Primary & Secondary Data', 'Census, Sampling & Probability', 'Schedules & Questionnaires', 'Classification, Tables & Diagrams']),
  ('mct', 'Measures of Central Tendency', 'measures-of-central-tendency', ['Mean, Median & Mode', 'Quartiles & Partition Values']),
  ('dsp', 'Dispersion, Skewness & Normal Distribution', 'dispersion-skewness', ['Measures of Dispersion', 'Skewness & Kurtosis', 'Normal Distribution']),
  ('cor', 'Correlation', 'correlation', ["Karl Pearson's Correlation", 'Rank Correlation & Probable Error']),
  ('tsi', 'Time Series & Index Numbers', 'time-series-index-numbers', ['Time Series', 'Index Numbers']),
]
ASO_SUBJ_TE = dict(ect='ఆర్థిక సిద్ధాంతం', ine='అంతర్జాతీయ అర్థశాస్త్రం', ind='భారత ఆర్థిక వ్యవస్థ', acc='ఫైనాన్షియల్ అకౌంటింగ్', cmp='కంప్యూటర్ ప్రాథమికాంశాలు',
                   sdc='గణాంకాలు: దత్తాంశ సేకరణ, నమూనా, చిత్రాలు', mct='కేంద్రీయ స్థాన కొలతలు', dsp='విస్తరణ, వైషమ్యం, సాధారణ విభాజనం', cor='సహసంబంధం',
                   tsi='కాలశ్రేణులు, సూచీ సంఖ్యలు')
ASO_BLURB = ('economics (economic theory, international economics and the Indian economy), financial accounting, statistics (collection and presentation of data, '
             'central tendency, dispersion and skewness, correlation, time series and index numbers) and basics of computers')
ASO_PAPERS = [
  dict(id='aso25', file='appsc-aso-2025-paper2.txt', year=2025, stage='Written Examination Paper II (Subject)', short='ASO 2025 Paper 2',
       kwname='APPSC ASO 2025 Paper 2',
       title='APPSC Assistant Statistical Officer 2025: Paper II (Statistics, Economics, Accountancy & Computers)', notif='Notification 12/2024 · CBT', held='29 April 2025',
       key="APPSC's final key", fmt='mcq', slug='appsc-aso-2025-paper-2-statistics-economics-question-paper-with-answers',
       alt='Statistics, Economics, Accountancy & Computers', te_paper='పేపర్-2 సబ్జెక్ట్ (స్టాటిస్టిక్స్, ఎకనామిక్స్)',
       blurb='Paper II (Subject): ' + ASO_BLURB + ', computer-based test, 150 questions, 150 marks, 150 minutes, in English and Telugu (the computer questions in English only).'),
  dict(id='aso22', file='appsc-aso-2022-paper2.txt', year=2022, stage='Written Examination Paper II (Subject)', short='ASO 2022 Paper 2',
       kwname='APPSC ASO 2022 Paper 2',
       title='APPSC Assistant Statistical Officer 2022: Paper II (Economics & Statistics)', notif='Notification 20/2021 · CBT', held='4 November 2022',
       key="APPSC's final key", fmt='mcq', slug='appsc-aso-2022-paper-2-statistics-economics-question-paper-with-answers',
       alt='Economics & Statistics', te_paper='పేపర్-2 సబ్జెక్ట్ (ఎకనామిక్స్, స్టాటిస్టిక్స్)',
       blurb='Paper II (Subject): ' + ASO_BLURB + ', computer-based test, 150 questions, 150 marks, 150 minutes, in English and Telugu.'),
]
def aso_have():
    """Ids of the ASO papers on the site (2025 went up first, 8 Nov 2026)."""
    return have_src('appsc-aso', ASO_PAPERS)
def aso_years():
    return ' and '.join(str(p['year']) for p in ASO_PAPERS if p['id'] in aso_have()) or '2025'

def exam_confs():
    T = ts_text()
    E = epfo_text()
    G = cgl_text()
    P = pre_text()
    si_m, pc_m = bool(T['si']), bool(T['pc'])
    return [
      dict(id='appsc-group-2', dir='', src='', key='appsc-g2', name='APPSC Group-II', short='Group-II', seo='APPSC Group 2',
           slugp='appsc-group-2', papers=PAPERS, subjects=SUBJECTS, faq=FAQ, board='APPSC', l2=L2_TE, pb='/appsc-group-2/',
           title='APPSC Group 2 Previous Year Question Papers (PYQs) with Answers – Prelims & Mains 2019–2025, English & Telugu | Learn with Anil',
           h1='APPSC Group 2 previous year question papers <em>with answers.</em>',
           l2line='APPSC గ్రూప్ 2 మునుపటి సంవత్సరం ప్రశ్నపత్రాలు, పాత ప్రశ్నాపత్రాలు (ప్రిలిమ్స్, మెయిన్స్) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Also known as AP Group 2 or APPSC Group-II Services. Old question papers, PYQs and practice bits, all with the final key.',
           desc=lambda t: (f"APPSC Group 2 (AP Group 2) previous year question papers and old papers with answers from APPSC's final key: Prelims (Screening Test) 2024 and 2019, "
                           f"Mains 2025 Paper 1 and Paper 2, and Mains 2019. {t:,} questions in English and Telugu with explanations; "
                           f"practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           eyebrow='APPSC Group-II · Prelims (Screening) &amp; Mains · 2019–2025',
           # Group-II Micro-Syllabus book added 29 Oct 2026 (Anil); the AP Economy and S&T books stay on this page too
           notes_title='Study material for APPSC Group-II',
           notes_seo=('APPSC Group 2 Micro Syllabus 2026 (Notification 37/2026) – Topic-wise Syllabus with PYQs, Free PDF Sample | Learn with Anil',
                      'APPSC Group-II micro-syllabus by Jupudi Anil Kumar for Notification 37/2026: all 9 Screening and Mains subjects in 267 sub-topics, '
                      'each tagged with the papers that asked it, 1,004 previous questions mapped and 112 current affairs of 2025–26. Free sample PDF; '
                      'plus History and Culture of Andhra Pradesh (all 207 APPSC AP history questions), the Mental Ability book (all 212 APPSC mental-ability questions solved, 500 practice questions), AP Economy Crisp Notes and the Science & Technology book.'),
           notes_lede='Exam-focused books by Jupudi Anil Kumar for APPSC Group-II: the new History and Culture of Andhra Pradesh book for Mains Paper I (17 chapters, all 207 AP history questions APPSC has asked with the official answers), the Mental Ability book for the Screening Test (all 212 APPSC mental-ability questions solved the fast way, 269 shortcuts and 500 practice questions), the Micro-Syllabus, which breaks every Screening and Mains subject into sub-topics and shows which papers asked each one, Crisp Notes on AP Economy, and a full Science & Technology book. Every book has APPSC\'s own previous questions inside.',
           notes_line='The new AP History book for Mains Paper I (all 207 APPSC AP history questions with official answers), the Mental Ability book for the Screening Test (212 APPSC questions solved, 500 practice questions), the Group-II Micro-Syllabus (Notification 37/2026), Public Administration and Governance, Ethics and Laws, Crisp Notes on AP Economy and a full Science & Technology book, built on APPSC\'s own previous questions.',
           papers_note="Every paper uses APPSC's official final key. The 2024 and 2025 keys show all four options. The 2019 keys print only the correct answer: there the answer is APPSC's and the other three options are written by Learn with Anil (inside the All-in-One Pass)."),
      dict(id='appsc-group-1', dir='appsc-group-1', src='appsc-group-1', key='appsc-g1', name='APPSC Group-I', short='Group-I', seo='APPSC Group 1',
           # Mental Ability book added 8 Nov 2026 (Anil): it is for Prelims Paper II, so the card text no longer says 'for APPSC Mains' only
           # History and Culture of AP book (aphist-en) added 8 Nov 2026 (Anil: "pls go ahead"); on both Group-I and Group-II pages
           notes_title='Study material for APPSC Group-I',
           notes_seo=('APPSC Group 1 Mental Ability Book – Shortcuts, All Previous Questions Solved, 500 Practice Questions (Free Sample PDF) | Learn with Anil',
                      'Mental Ability for APPSC Group-I Prelims Paper II and the Group-II Screening Test by Jupudi Anil Kumar: 25 chapters, 269 shortcuts, all 212 APPSC '
                      'mental-ability questions (2019–2024) solved the fast way and 500 practice questions with answers. Free sample chapter (Percentage); '
                      'plus Group-I Mains books on History and Culture of Andhra Pradesh (with answer frames), Public Administration, Ethics and Laws, AP Economy and Science & Technology.'),
           notes_lede='Exam-focused books by Jupudi Anil Kumar for APPSC Group-I: the new Mental Ability book for Prelims Paper II (all 212 APPSC mental-ability questions solved the fast way, 269 shortcuts and 500 practice questions), and for the Mains: the new History and Culture of Andhra Pradesh book for Paper II Section B (17 chapters, all 30 Group-I Mains AP history questions with answer frames), Public Administration and Governance, Ethics and Laws, Crisp Notes on AP Economy and a full Science & Technology book. Every book has APPSC\'s own previous questions with the official answers.',
           notes_line='The new Mental Ability book for Prelims Paper II (all 212 APPSC mental-ability questions solved the fast way, 500 practice questions), plus History and Culture of Andhra Pradesh (Paper II, with answer frames), Public Administration and Governance, Ethics and Laws, Crisp Notes on AP Economy and a full Science & Technology book for the Mains, built on APPSC\'s own previous questions.',
           slugp='appsc-group-1', papers=G1_PAPERS, subjects=G1_SUBJECTS, faq=FAQ_G1, board='APPSC', l2=L2_TE, pb='/appsc-group-1/',
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           title='APPSC Group 1 Previous Year Question Papers (PYQs) with Answers – Prelims 2019–2024, English & Telugu | Learn with Anil',
           h1='APPSC Group 1 previous year question papers <em>with answers.</em>',
           l2line='APPSC గ్రూప్ 1 ప్రిలిమ్స్ మునుపటి సంవత్సరం ప్రశ్నపత్రాలు, పాత ప్రశ్నాపత్రాలు సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Also known as AP Group 1 or APPSC Group-I Services. Old question papers and PYQs of the Prelims, with the final key.',
           desc=lambda t: (f"APPSC Group 1 (AP Group 1) Prelims previous year question papers and old papers with answers from APPSC's final key: 2024, 2023 and 2019, "
                           f"Paper 1 General Studies and Paper 2 General Aptitude. {t:,} questions in English and Telugu with explanations; "
                           f"practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='APPSC Group-I · Prelims · 2019–2024',
           papers_note="Every paper uses APPSC's official final key. The 2024 key shows all four options. The 2023 and 2019 keys print only the correct answer: there the answer is APPSC's and the other three options are written by Learn with Anil (inside the All-in-One Pass)."),
      dict(id='upsc-capf', dir='upsc-capf', src='upsc-capf', key='upsc-capf', name='UPSC CAPF (AC)', short='CAPF (AC)', seo='UPSC CAPF AC',
           slugp='upsc-capf-ac', papers=CAPF_PAPERS, subjects=CAPF_SUBJECTS, faq=FAQ_CAPF, board='UPSC', l2=L2_HI, pb='/upsc-capf/',
           keyname="UPSC's answer keys", keyshort="UPSC's answer keys (2025: compiled from published keys)",
           title='UPSC CAPF AC Previous Year Question Papers with Answers (2024–2026), English & Hindi | Learn with Anil',
           h1='UPSC CAPF AC previous year question papers <em>with answers.</em>',
           aka='Also known as the CAPF Assistant Commandant (AC) exam. PYQs of Paper 1 (General Ability and Intelligence), subject-wise, with the answer key.',
           l2line='यूपीएससी सीएपीएफ असिस्टेंट कमांडेंट के पिछले वर्षों के प्रश्न पत्र, उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; सभी परीक्षाओं के लिए एक ₹45 ऑल-इन-वन पास।',
           desc=lambda t: (f"UPSC CAPF AC (Assistant Commandant) previous year question papers: Paper 1 General Ability and Intelligence "
                           f"2026, 2025 and 2024 with answer keys and explanations. {t:,} questions in English and Hindi; "
                           f"subject-wise practice and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='UPSC CAPF (Assistant Commandants) · Paper I · 2024–2026',
           papers_note="2026: UPSC's provisional answer key, published three days after the exam; the final key may differ for a few questions. 2025: UPSC's key could not be found, so the answers were compiled by Learn with Anil from three published keys and checked one by one. 2024: UPSC's official answer key (Series A). Questions UPSC dropped are left out. Every question is in English and Hindi, as printed in the booklet."),
      dict(id='upsc-epfo', dir='upsc-epfo', src='upsc-epfo', key='upsc-epfo', name=('UPSC EPFO (APFC, EO/AO, PA)' if E.get('pa') else 'UPSC EPFO (APFC, EO/AO)'), short='EPFO', seo=('UPSC EPFO' if E['eo'] else 'UPSC EPFO APFC'),
           slugp='upsc-epfo', papers=EPFO_PAPERS, subjects=EPFO_SUBJECTS, faq=FAQ_EPFO, board='UPSC', l2=L2_HI, pb='/upsc-epfo/',
           keyname="UPSC's official answer key", keyshort=("UPSC's official answer keys (" + E['nokeyy'] + ": answers by Learn with Anil, as UPSC has published no key)" if E['nokey'] else "UPSC's official answer keys"),
           hi_name='यूपीएससी ईपीएफओ', hi_paper='भर्ती परीक्षा', subj_te=EPFO_SUBJ_HI,
           title=(f"UPSC EPFO Previous Year Question Papers with Answers – {E['papers']}, English & Hindi | Learn with Anil" if E['eo'] else
                  'UPSC EPFO APFC Previous Year Question Paper with Answers – APFC 2023, English & Hindi | Learn with Anil'),
           h1=('UPSC EPFO APFC, EO/AO &amp; PA previous year question papers <em>with answers.</em>' if E['pa'] else
               'UPSC EPFO APFC &amp; EO/AO previous year question papers <em>with answers.</em>' if E['eo'] else
               'UPSC EPFO APFC previous year question paper <em>with answers.</em>'),
           aka=('Also known as the EPFO Assistant Provident Fund Commissioner (APFC), Enforcement Officer / Accounts Officer (EO/AO) and Personal Assistant (PA) recruitment tests. ' if E['pa'] else
                'Also known as the EPFO Assistant Provident Fund Commissioner (APFC) and Enforcement Officer / Accounts Officer (EO/AO) recruitment tests. ' if E['eo'] else
                'Also known as the EPFO Assistant Provident Fund Commissioner (APFC) recruitment test. ')
               + ('PYQs with answers (UPSC\'s official key wherever UPSC has published one), subject-wise: labour laws, social security, accounting, polity, economy, history, science, aptitude and English.' if E['many'] else
                  'PYQs with UPSC\'s official answer key, subject-wise: labour laws, social security, accounting, polity, economy, history, science, aptitude and English.'),
           aka_short=('UPSC EPFO APFC, EO/AO (Enforcement Officer / Accounts Officer) and PA (Personal Assistant)' if E['pa'] else
                      'UPSC EPFO APFC and EO/AO (Enforcement Officer / Accounts Officer)' if E['eo'] else 'UPSC EPFO Assistant Provident Fund Commissioner (APFC)'),
           l2line=('यूपीएससी ईपीएफओ सहायक भविष्य निधि आयुक्त (APFC), प्रवर्तन अधिकारी/लेखा अधिकारी (EO/AO) और वैयक्तिक सहायक (PA) भर्ती परीक्षाओं के पिछले वर्षों के प्रश्न पत्र, उत्तर सहित (जहाँ यूपीएससी ने कुंजी जारी की है, वहाँ आधिकारिक उत्तर कुंजी से) — हिंदी और अंग्रेज़ी में; सभी परीक्षाओं के लिए एक ₹45 ऑल-इन-वन पास।' if E['pa'] and E['nokey'] else
                   'यूपीएससी ईपीएफओ सहायक भविष्य निधि आयुक्त (APFC) और प्रवर्तन अधिकारी/लेखा अधिकारी (EO/AO) भर्ती परीक्षाओं के पिछले वर्षों के प्रश्न पत्र, आधिकारिक उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; सभी परीक्षाओं के लिए एक ₹45 ऑल-इन-वन पास।' if E['eo'] else
                   'यूपीएससी ईपीएफओ सहायक भविष्य निधि आयुक्त (APFC) भर्ती परीक्षा का पिछले वर्ष का प्रश्न पत्र, आधिकारिक उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; सभी परीक्षाओं के लिए एक ₹45 ऑल-इन-वन पास।'),
           desc=lambda t: ((f"UPSC EPFO previous year question papers with answers and explanations: {E['papers']} (APFC, Enforcement Officer / Accounts Officer and Personal Assistant recruitment tests). " if E['many'] else
                            f"UPSC EPFO previous year question papers with UPSC's official answer keys and explanations: the APFC 2023 recruitment test and the EO/AO (Enforcement Officer / Accounts Officer) {E['eoy'].replace(' & ', ' and ')} test{'s' if E['eo21'] else ''}. " if E['eo'] else
                            f"UPSC EPFO APFC (Assistant Provident Fund Commissioner) previous year question paper: the 2023 recruitment test with UPSC's official answer key and explanations. ")
                           + f"{t:,} questions in English and Hindi on labour laws, social security, accounting, polity, economy, history, science, aptitude and English; "
                           f"subject-wise practice and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow=(f"UPSC · EPFO APFC, EO/AO &amp; PA · Recruitment Tests {E['years']}" if E['pa'] else
                    f"UPSC · EPFO APFC &amp; EO/AO · Recruitment Tests {E['years']}" if E['eo'] else 'UPSC · EPFO Assistant Provident Fund Commissioner · Recruitment Test 2023'),
           papers_note=(epfo_keynote(E) + " Part A (General English) is in English only; every other question is in English and Hindi, as printed in the booklets." if E['many'] else
                        "Answers come from UPSC's official answer keys (Series A) on upsc.gov.in. UPSC dropped no question in the two 2023 papers"
                        + (" and one (Q71) in the 2021 EO/AO paper, which is left out" if E['eo21'] else "")
                        + ". Part A (General English) is in English only; every other question is in English and Hindi, as printed in the booklets." if E['eo'] else
                        "Answers come from UPSC's official answer key (Series A), published on upsc.gov.in in August 2024; no question was dropped. Part A (General English) is in English only; every other question is in English and Hindi, as printed in the booklet.")),
      dict(id='upsc-prelims', dir='upsc-prelims', src='upsc-prelims', key='upsc-prelims', name='UPSC CSE Prelims', short='UPSC Prelims', seo='UPSC Prelims',
           slugp='upsc-prelims', papers=PRE_PAPERS, subjects=PRE_SUBJECTS, faq=FAQ_PRE, board='UPSC', l2=L2_HI, pb='/upsc-prelims/',
           keyname="UPSC's official answer keys", keyshort=P['keyshort'],
           hi_name='यूपीएससी सिविल सेवा प्रारंभिक परीक्षा', hi_paper='प्रश्न पत्र', subj_te=PRE_SUBJ_HI,
           title=f"UPSC Prelims Previous Year Question Papers with Answers ({P['years']}) – GS Paper 1 & CSAT, English & Hindi | Learn with Anil",
           h1='UPSC Prelims previous year question papers <em>with answers.</em>',
           aka=('Also known as the UPSC Civil Services (Preliminary) Examination, CSE Prelims or IAS Prelims. PYQs of General Studies Paper I and '
                'CSAT (Paper II), year-wise and subject-wise, with UPSC\'s answer keys.'),
           aka_short='UPSC Civil Services (Preliminary) Examination: General Studies Paper I and CSAT',
           l2line=('यूपीएससी सिविल सेवा प्रारंभिक परीक्षा (IAS Prelims) के पिछले वर्षों के प्रश्न पत्र — सामान्य अध्ययन प्रश्न-पत्र I और सीसैट, '
                   'यूपीएससी की उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; सभी परीक्षाओं के लिए एक ₹45 ऑल-इन-वन पास।'),
           desc=lambda t: (f"UPSC Prelims (IAS / CSE Prelims) previous year question papers with answers: General Studies Paper 1 and CSAT Paper 2, "
                           f"{P['years']}, with UPSC's answer keys and explanations. {t:,} questions in English and Hindi; year-wise and subject-wise "
                           f"practice and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow=f"UPSC Civil Services · Prelims · GS Paper I &amp; CSAT · {P['years']}",
           papers_note=P['note']),
      dict(id='ssc-cgl', dir='ssc-cgl', src='ssc-cgl', key='ssc-cgl', name='SSC CGL', short='SSC CGL', seo='SSC CGL',
           slugp='ssc-cgl', papers=CGL_PAPERS, subjects=CGL_SUBJECTS, faq=FAQ_CGL, board='SSC', l2=L2_HI, pb='/ssc-cgl/',
           keyname="SSC's answer key", keyshort="SSC's answer key (as marked on the response sheets)",
           hi_name='एसएससी सीजीएल', hi_paper='प्रश्न पत्र', subj_te=CGL_SUBJ_HI,
           title=f"SSC CGL Previous Year Question Papers with Answers – Tier 1 & Tier 2 {G['years']}, English & Hindi | Learn with Anil",
           h1='SSC CGL previous year question papers <em>with answers.</em>',
           aka='SSC Combined Graduate Level Examination (CGLE): Tier-I (Prelims) shift-wise papers and Tier-II (Mains) Paper I, with SSC\'s answer key, subject-wise: reasoning, maths, English and general awareness.',
           aka_short='SSC Combined Graduate Level (CGL) Tier 1 and Tier 2',
           l2line='एसएससी सीजीएल टियर-1 और टियर-2 के पिछले वर्षों के प्रश्न पत्र, एसएससी की उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; रीजनिंग, गणित, अंग्रेज़ी और सामान्य जागरूकता।',
           desc=lambda t: (f"SSC CGL previous year question papers with SSC's answer key and explanations: {G['what']} ({G['years']}), from SSC's own response sheets. "
                           f"{t:,} questions in English and Hindi on reasoning, quantitative aptitude, English and general awareness; subject-wise practice and timed mock tests."),
           eyebrow=f"SSC · Combined Graduate Level · Tier-I &amp; Tier-II · {G['years']}",
           papers_note=("Every paper is SSC's own question paper as candidates print it from SSC's portal (the response sheet), with the answer SSC marked as correct. "
                        "The Tier-I sheets are from the answer-key stage, so SSC's final key may differ for a few questions. "
                        "Each shift had a different paper. English Comprehension is in English only; every other question is in English and Hindi, as printed.")),
      dict(id='ts-police-si', dir='ts-police-si', src='ts-police-si', key='ts-si', name='TS Police SI', short='TS Police SI', seo='TS Police SI',
           slugp='ts-police-si', papers=TS_SI_PAPERS, subjects=TS_SUBJECTS, faq=FAQ_TS('SI', T['si']), board='TSLPRB', l2=L2_TE, pb='/ts-police-si/',
           keyname="TSLPRB's final key", keyshort="TSLPRB's final key", bits=True,
           te_name='తెలంగాణ పోలీస్ ఎస్ఐ', te_paper='ప్రిలిమినరీ పరీక్ష',
           title=('TS Police SI Previous Question Papers with Answers – Telangana SI Prelims 2022 & Mains 2023 (TSLPRB), English & Telugu | Learn with Anil' if si_m else
                  'TS Police SI Previous Question Papers with Answers – Telangana SI (TSLPRB) Prelims 2022, English & Telugu | Learn with Anil'),
           h1='TS Police SI previous year question papers <em>with answers.</em>',
           l2line=('తెలంగాణ పోలీస్ ఎస్ఐ ప్రిలిమినరీ, ఫైనల్ రాత పరీక్షల పాత ప్రశ్నాపత్రాలు (మునుపటి ప్రశ్నపత్రాలు) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.' if si_m else
                   'తెలంగాణ పోలీస్ ఎస్ఐ ప్రిలిమినరీ పరీక్ష పాత ప్రశ్నాపత్రం (మునుపటి ప్రశ్నపత్రం) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.'),
           aka='Also known as the Telangana (TG) Police SI exam: SCT SI (Civil) and equivalent posts, conducted by TSLPRB, now TGPRB.',
           aka_short='Telangana Police SI (TSLPRB / TGPRB)',
           desc=lambda t: ((f"TS Police SI (Telangana SI, TSLPRB / TGPRB) previous question papers: Prelims 2022 and Mains 2023 (Final Written Examination {T['si_fwe']}) with answers from TSLPRB's final keys. " if si_m else
                            f"TS Police SI (Telangana SI, TSLPRB / TGPRB) previous question paper: Preliminary Written Test 2022 with answers from TSLPRB's final key. ")
                           + f"{t:,} questions on arithmetic, reasoning and general studies in English and Telugu with explanations; practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow=('TSLPRB / TGPRB · SI (Civil) &amp; equivalent · Prelims 2022 &amp; Final Written Exam 2023' if si_m else
                    'TSLPRB / TGPRB · SI (Civil) &amp; equivalent · Preliminary Written Test'),
           papers_note=("Answers come from TSLPRB's final keys: booklet A for the 2022 Preliminary Written Test (key released on 21 October 2022) and booklet D for the 2023 Final Written Examination. "
                        "Questions the key deleted, or for which it accepted three or four options, are left out, as are the few that cannot be read cleanly in the photographed booklet. Every question is in English and Telugu, as printed in the booklet." if si_m else
                        "Answers come from TSLPRB's final key for booklet A, released on 21 October 2022. Questions the key deleted, or for which it accepted three or four options, are left out. Every question is in English and Telugu, as printed in the booklet.")),
      dict(id='ts-police-constable', dir='ts-police-constable', src='ts-police-constable', key='ts-pc', name='TS Police Constable', short='TS Constable', seo='TS Police Constable',
           slugp='ts-police-constable', papers=TS_PC_PAPERS, subjects=TS_SUBJECTS, faq=FAQ_TS('PC', T['pc']), board='TSLPRB', l2=L2_TE, pb='/ts-police-constable/',
           keyname="TSLPRB's final key", keyshort=("TSLPRB's keys" if T['pc_prelim'] else "TSLPRB's final key"), bits=True,
           te_name='తెలంగాణ పోలీస్ కానిస్టేబుల్', te_paper='ప్రిలిమినరీ పరీక్ష',
           title=(f"TS Police Constable Previous Question Papers with Answers – Telangana Constable Prelims & Mains {T['pc_years']} (TSLPRB), English & Telugu | Learn with Anil" if T['pcmany'] else
                  'TS Police Constable Previous Question Papers with Answers – Telangana Constable Prelims 2022 & Mains 2023 (TSLPRB), English & Telugu | Learn with Anil' if pc_m else
                  'TS Police Constable Previous Question Papers with Answers – Telangana Constable (TSLPRB) Prelims 2022, English & Telugu | Learn with Anil'),
           h1='TS Police Constable previous year question papers <em>with answers.</em>',
           l2line=('తెలంగాణ పోలీస్ కానిస్టేబుల్ ప్రిలిమినరీ, ఫైనల్ రాత పరీక్షల పాత ప్రశ్నాపత్రాలు (మునుపటి ప్రశ్నపత్రాలు) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.' if pc_m else
                   'తెలంగాణ పోలీస్ కానిస్టేబుల్ ప్రిలిమినరీ పరీక్ష పాత ప్రశ్నాపత్రం (మునుపటి ప్రశ్నపత్రం) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.'),
           aka='Also known as the Telangana (TG) Police Constable or TS PC exam: SCT PC (Civil) and equivalent posts, conducted by TSLPRB, now TGPRB.',
           aka_short='Telangana Police Constable (TSLPRB / TGPRB)',
           desc=lambda t: ((f"TS Police Constable (Telangana Constable, TSLPRB / TGPRB) previous question papers: Prelims ({T['pc_pre'].replace(' & ', ' and ')}) and Mains / Final Written Examination ({T['pc_fwe'].replace(' & ', ' and ')}) with answers from TSLPRB's keys. " if T['pcmany'] else
                            "TS Police Constable (Telangana Constable, TSLPRB / TGPRB) previous question papers: Prelims 2022 and Mains 2023 (Final Written Examination, 30 April 2023) with answers from TSLPRB's final keys. " if pc_m else
                            "TS Police Constable (Telangana Constable, TSLPRB / TGPRB) previous question paper: Preliminary Written Test 2022 with answers from TSLPRB's final key. ")
                           + f"{t:,} questions on English, arithmetic, reasoning and general studies in English and Telugu with explanations; practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow=(f"TSLPRB / TGPRB · Police Constable (Civil) &amp; equivalent · Prelims &amp; Final Written Exams {T['pc_years']}" if T['pcmany'] else
                    'TSLPRB / TGPRB · Police Constable (Civil) &amp; equivalent · Prelims 2022 &amp; Final Written Exam 2023' if pc_m else
                    'TSLPRB / TGPRB · Police Constable (Civil) &amp; equivalent · Preliminary Written Test'),
           papers_note=(("Answers come from TSLPRB's final keys for the booklet shown with each paper"
                         + (f"; for {' and '.join(T['pc_prelim'])} TSLPRB's final key could not be found, so the answers are from its preliminary key and a few may differ from the final key" if T['pc_prelim'] else '')
                         + ". Questions the key deleted, or for which it accepted three or four options, are left out, as are the few that cannot be read cleanly in the booklet copies or have no correct option as printed; where a key also gave the mark for a blank answer, the explanation says so. "
                         "The English-language questions are in English only; every other question is in English and Telugu, as printed in the booklet.") if T['pcmany'] else
                        "Answers come from TSLPRB's final keys for booklet A of the 2022 Preliminary Written Test (key released on 21 October 2022) and of the 2023 Final Written Examination. "
                        "Questions the key deleted, or for which it accepted three or four options, are left out, as are the few that cannot be read cleanly in the photographed booklet. The English-language questions are in English only; every other question is in English and Telugu, as printed in the booklet." if pc_m else
                        "Answers come from TSLPRB's final key for booklet A, released on 21 October 2022. Questions the key deleted, or for which it accepted three or four options, are left out. The English-language questions are in English only; every other question is in English and Telugu, as printed in the booklet.")),
      dict(id='tgpsc-hmwssb-manager', dir='tgpsc-hmwssb-manager', src='tgpsc-hmwssb-manager', key='tg-hmws', name='TGPSC HMWSSB Manager (Engineering)',
           short='HMWSSB Manager', seo='TGPSC HMWSSB Manager', slugp='tgpsc-hmwssb-manager', papers=HM_PAPERS, subjects=HM_SUBJECTS, faq=FAQ_HM,
           board='TGPSC', l2=L2_TE, pb='/tgpsc-hmwssb-manager/', keyname="TSPSC's final key", keyshort="TSPSC's final key", bits=True,
           te_name='టీజీపీఎస్సీ జలమండలి (HMWSSB) మేనేజర్ (ఇంజనీరింగ్)', te_paper='రాత పరీక్ష', subj_te=HM_SUBJ_TE,
           title='TGPSC HMWSSB Manager (Engineering) Previous Question Papers with Answers – GS, Civil & ECE, English & Telugu | Learn with Anil',
           h1='TGPSC HMWSSB Manager (Engineering) previous question papers <em>with answers.</em>',
           l2line='టీజీపీఎస్సీ జలమండలి (HMWSSB) మేనేజర్ (ఇంజనీరింగ్) పాత ప్రశ్నాపత్రాలు సమాధానాలతో — జనరల్ స్టడీస్ (తెలుగు, ఇంగ్లీష్), సివిల్ ఇంజనీరింగ్, ఎలక్ట్రానిక్స్ & కమ్యూనికేషన్ ఇంజనీరింగ్ (ECE); అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Manager (Engineering) in the Hyderabad Metropolitan Water Supply and Sewerage Board (HMWSSB, Jalamandali), recruited by TGPSC, formerly TSPSC.',
           aka_short='TGPSC (TSPSC) Manager (Engineering), Hyderabad Metro Water Board',
           desc=lambda t: (f"TGPSC (TSPSC) HMWSSB Manager (Engineering) previous question papers: the 2015 Paper 1 General Studies (English and Telugu) "
                           f"and Paper 2 Civil Engineering and Electronics & Communication Engineering (ECE) with answers from TSPSC's final key. {t:,} questions with explanations; practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='TGPSC (TSPSC) · Manager (Engineering), HMWSSB · Notification 13/2015',
           papers_note="Answers come from TSPSC's final key for booklet Series A (Notification 13/2015, written test held on 1 November 2015). Questions for which TSPSC gave the mark to every candidate are left out. Paper 1 is in English and Telugu as printed (its English-language questions in English only); the Paper 2 subject papers (Civil Engineering, Electronics & Communication Engineering) are in English only."),
      dict(id='appsc-amvi', dir='appsc-amvi', src='appsc-amvi', key='ap-amvi', name='APPSC AMVI (Assistant Motor Vehicle Inspector)',
           short='APPSC AMVI', seo='APPSC AMVI', slugp='appsc-amvi', papers=AMVI_AP_PAPERS, subjects=AMVI_AP_SUBJECTS, faq=FAQ_AMVI('AP'),
           board='APPSC', l2=L2_TE, pb='/appsc-amvi/', keyname="APPSC's final key", keyshort="APPSC's final keys", bits=True,
           te_name='ఏపీపీఎస్సీ అసిస్టెంట్ మోటార్ వెహికల్ ఇన్‌స్పెక్టర్ (AMVI)', te_paper='రాత పరీక్ష', subj_te=AMVI_AP_SUBJ_TE,
           title='APPSC AMVI Previous Question Papers with Answers – Assistant Motor Vehicle Inspector 2019, 2023 & 2026, GS & Automobile Engineering | Learn with Anil',
           h1='APPSC AMVI previous question papers <em>with answers.</em>',
           l2line='ఏపీపీఎస్సీ అసిస్టెంట్ మోటార్ వెహికల్ ఇన్‌స్పెక్టర్ (AMVI) పాత ప్రశ్నాపత్రాలు సమాధానాలతో — జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ (తెలుగు, ఇంగ్లీష్), ఆటోమొబైల్ ఇంజనీరింగ్; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Assistant Motor Vehicle Inspector (AMVI) in the A.P. Transport Subordinate Service, recruited by the Andhra Pradesh Public Service Commission.',
           aka_short='APPSC Assistant Motor Vehicle Inspector (AP Transport Department)',
           desc=lambda t: (f"APPSC AMVI (Assistant Motor Vehicle Inspector) previous question papers: Paper I General Studies & Mental Ability (English and Telugu) and Paper II Automobile Engineering "
                           f"of 2026, 2023 and 2019 with answers from APPSC's final keys. {t:,} questions with explanations; practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='APPSC · Assistant Motor Vehicle Inspector · Transport Department · 2019, 2023 &amp; 2026',
           papers_note="Answers come from APPSC's final keys: the boxed answers of the 2026 Series A booklets (Notification 21/2025), the APOnline final key of the 6 October 2023 computer-based test (Notification 12/2022) and the 2019 final and revised keys (Notification 11/2018). Questions APPSC deleted or ignored for all candidates are left out. APPSC's 2019 keys print only the correct answer, so the 2019 papers are quick-recall questions. Paper I is in English and Telugu as printed (2019: English only); Paper II (Automobile Engineering) is in English only."),
      dict(id='tgpsc-amvi', dir='tgpsc-amvi', src='tgpsc-amvi', key='tg-amvi', name='TGPSC AMVI (Assistant Motor Vehicles Inspector)',
           short='TGPSC AMVI', seo='TGPSC AMVI', slugp='tgpsc-amvi', papers=AMVI_TG_PAPERS, subjects=AMVI_TG_SUBJECTS, faq=FAQ_AMVI('TG'),
           board='TGPSC', l2=L2_TE, pb='/tgpsc-amvi/', keyname="TSPSC's preliminary key", keyshort="TSPSC's preliminary key", bits=True,
           te_name='టీజీపీఎస్సీ అసిస్టెంట్ మోటార్ వెహికల్స్ ఇన్‌స్పెక్టర్ (AMVI)', te_paper='రాత పరీక్ష', subj_te=AMVI_TG_SUBJ_TE,
           title='TGPSC (TSPSC) AMVI Previous Question Papers with Answers – Assistant Motor Vehicles Inspector 2023, GS & Automobile Engineering | Learn with Anil',
           h1='TGPSC AMVI previous question papers <em>with answers.</em>',
           l2line='టీజీపీఎస్సీ (టీఎస్‌పీఎస్సీ) అసిస్టెంట్ మోటార్ వెహికల్స్ ఇన్‌స్పెక్టర్ (AMVI) 2023 ప్రశ్నాపత్రాలు సమాధానాలతో — జనరల్ స్టడీస్ (తెలుగు, ఇంగ్లీష్), ఆటోమొబైల్ ఇంజనీరింగ్; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Assistant Motor Vehicles Inspector (AMVI) in the Telangana Transport Department, recruited by TGPSC, formerly TSPSC.',
           aka_short='TGPSC (TSPSC) Assistant Motor Vehicles Inspector (Telangana Transport Department)',
           desc=lambda t: (f"TGPSC (TSPSC) AMVI (Assistant Motor Vehicles Inspector) previous question papers: the 2023 Paper I General Studies & General Abilities (English and Telugu) and Paper II Automobile Engineering "
                           f"with answers from TSPSC's preliminary key. {t:,} questions with explanations; practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='TGPSC (TSPSC) · Assistant Motor Vehicles Inspector · Notification 31/2022',
           papers_note="Answers come from TSPSC's preliminary key on the master question papers of the computer-based test held on 28 June 2023 (Notification 31/2022). TSPSC released its final key on 7 February 2024 only on candidates' individual response sheets, so a few answers may differ from the final key; doubtful ones are marked in the explanations. Paper I is in English and Telugu as printed; Paper II (Automobile Engineering) is in English only."),
      dict(id='appsc-eo', dir='appsc-endowment-officer', src='appsc-eo', key='ap-eo', name='APPSC Executive Officer Grade-III (Endowments)',
           short='APPSC EO Grade-III', seo='APPSC EO Grade 3', slugp='appsc-eo-grade-3', papers=EO_PAPERS, subjects=EO_SUBJECTS, faq=FAQ_EO,
           board='APPSC', l2=L2_TE, pb='/appsc-endowment-officer/', keyname="APPSC's final key", keyshort="APPSC's final keys", bits=True,
           te_name='ఏపీపీఎస్సీ ఎగ్జిక్యూటివ్ ఆఫీసర్ గ్రేడ్-III (దేవాదాయ శాఖ)', te_paper='రాత పరీక్ష', subj_te=EO_SUBJ_TE,
           title='APPSC Endowment Officer (EO Grade 3) Previous Question Papers with Answers – Hindu Philosophy & Temple System, GS, 2022–2026 | Learn with Anil',
           h1='APPSC Endowment Officer (EO Grade-III) previous question papers <em>with answers.</em>',
           l2line='ఏపీపీఎస్సీ దేవాదాయ శాఖ ఎగ్జిక్యూటివ్ ఆఫీసర్ గ్రేడ్-III పాత ప్రశ్నాపత్రాలు సమాధానాలతో — హిందూ తత్వశాస్త్రం & దేవాలయ వ్యవస్థ, జనరల్ స్టడీస్ (తెలుగు, ఇంగ్లీష్); స్టడీ నోట్స్‌తో పాటు అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Executive Officer Grade-III in the A.P. Endowments Subordinate Service (temple Executive Officer, Endowments Department), recruited by the Andhra Pradesh Public Service Commission.',
           aka_short='APPSC Executive Officer Grade-III (AP Endowments Department)',
           desc=lambda t: (f"APPSC Endowment Officer (Executive Officer Grade-III, AP Endowments) previous question papers: Paper II Hindu Philosophy & Temple System and Paper I General Studies & Mental Ability "
                           f"of 2026 and the 2023 Mains, and the 2022 Screening Test, with answers from APPSC's final keys. {t:,} questions in English and Telugu with explanations; practice quizzes, timed mock tests and study notes with the ₹45 All-in-One Pass."),
           eyebrow='APPSC · Executive Officer Grade-III · Endowments Department · 2022–2026',
           notes_title='Study material: Hindu Philosophy & Temple System',
           notes_seo=('Hindu Philosophy & Temple System Notes – APPSC EO Grade 3 (Endowment Officer) Paper II Study Material | Learn with Anil',
                      'APPSC Endowment Officer (EO Grade-III) Paper II study material by Jupudi Anil Kumar: Hindu Philosophy & Temple System notes from Ramayanam to the Endowments Act, with meme breaks and 291 previous questions with official answers. Free sample chapter.'),
           notes_lede='Exam notes by Jupudi Anil Kumar for Paper II of the APPSC Executive Officer Grade-III exam: every syllabus topic from Ramayanam to the Endowments Act, written from what APPSC actually asks, with key-fact tables, quick-revision boxes and APPSC\'s own previous questions with the official answers.',
           notes_line='Hindu Philosophy & Temple System notes for EO Grade-III Paper II, built on APPSC\'s own previous questions.',
           papers_note="Answers come from APPSC's final keys: the boxed answers of the 2026 Series A booklets (Notification 10/2025, held 11 February 2026), the final key on the master question papers of the 2023 Mains computer-based test (Notification 24/2021) and the 2022 Screening Test final key. Questions APPSC deleted or ignored for all candidates are left out. The 2022 key prints only the correct answer, so that paper is quick-recall questions. Every paper is in English and Telugu as printed."),
      dict(id='appsc-analyst', dir='appsc-analyst-grade-2', src='appsc-analyst', key='ap-analyst', name='APPSC Analyst Grade-II (A.P. Pollution Control Board)',
           short='APPSC Analyst Grade-II', seo='APPSC Analyst Grade 2', slugp='appsc-analyst-grade-2', papers=ANALYST_PAPERS, subjects=ANALYST_SUBJECTS, faq=FAQ_ANALYST,
           board='APPSC', l2=L2_TE, pb='/appsc-analyst-grade-2/', keyname="APPSC's final key", keyshort="APPSC's final keys", bits=True,
           te_name='ఏపీపీఎస్సీ అనలిస్ట్ గ్రేడ్-II (ఏపీ కాలుష్య నియంత్రణ మండలి)', te_paper='రాత పరీక్ష', subj_te=ANALYST_SUBJ_TE,
           title='APPSC Analyst Grade 2 Previous Question Papers with Answers – AP Pollution Control Board, GS & Mental Ability, Chemistry, Biochemistry, Biology & Environmental Science | Learn with Anil',
           h1='APPSC Analyst Grade-II previous question papers <em>with answers.</em>',
           l2line='ఏపీపీఎస్సీ అనలిస్ట్ గ్రేడ్-II (ఏపీ కాలుష్య నియంత్రణ మండలి) పాత ప్రశ్నాపత్రాలు సమాధానాలతో — పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ (తెలుగు, ఇంగ్లీష్), పేపర్-2 కెమిస్ట్రీ, బయోకెమిస్ట్రీ, బయాలజీ, ఎన్విరాన్‌మెంటల్ సైన్స్ (ఇంగ్లీష్); అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Analyst Grade-II in the A.P. Pollution Control Board (APPCB), recruited by the Andhra Pradesh Public Service Commission.',
           aka_short='APPSC Analyst Grade-II (AP Pollution Control Board)',
           desc=lambda t: (f"APPSC Analyst Grade-II (A.P. Pollution Control Board) previous question papers: the 2025 Paper I General Studies & Mental Ability (English and Telugu) and Paper II Chemistry, Biochemistry, Biology and Environmental Science papers "
                           f"with answers from APPSC's final keys, {t:,} questions with explanations. Practice quizzes and timed mock tests for the 2026 exam with the ₹45 All-in-One Pass."),
           eyebrow='APPSC · Analyst Grade-II · A.P. Pollution Control Board · 2025',
           papers_note="Answers come from APPSC's final keys on the master question papers of the March 2025 computer-based test (Notification 02/2024): the option marked correct there is the answer. Questions APPSC ignored for all candidates are left out; where APPSC accepted two options, both are shown as correct. In 2025 Paper II was set separately for each degree subject; from 2026 it is one Common Paper with all four subjects, so practise all four. Paper I (General Studies & Mental Ability, held 25 March 2025, the same paper as for Assistant Environmental Engineer) is in English and Telugu as printed; the Paper II papers are in English only."),
      dict(id='appsc-env-engineer', dir='appsc-assistant-environmental-engineer', src='appsc-env-engineer', key='ap-enveng', name='APPSC Assistant Environmental Engineer (A.P. Pollution Control Board)',
           short='APPSC Asst. Environmental Engineer', seo='APPSC Assistant Environmental Engineer', slugp='appsc-assistant-environmental-engineer', papers=AEE_PAPERS, subjects=AEE_SUBJECTS, faq=FAQ_AEE,
           board='APPSC', l2=L2_TE, pb='/appsc-assistant-environmental-engineer/', keyname="APPSC's final key", keyshort="APPSC's final keys", bits=True,
           te_name='ఏపీపీఎస్సీ అసిస్టెంట్ ఎన్విరాన్‌మెంటల్ ఇంజనీర్ (ఏపీ కాలుష్య నియంత్రణ మండలి)', te_paper='రాత పరీక్ష', subj_te=AEE_SUBJ_TE,
           title=('APPSC Assistant Environmental Engineer Previous Question Papers with Answers – AP Pollution Control Board AEE 2025, ' + ('GS & Common Subject' if aee_p1() else 'Paper 2 Common Subject') + ' | Learn with Anil'),
           h1='APPSC Assistant Environmental Engineer previous question papers <em>with answers.</em>',
           l2line=('ఏపీపీఎస్సీ అసిస్టెంట్ ఎన్విరాన్‌మెంటల్ ఇంజనీర్ (ఏపీ కాలుష్య నియంత్రణ మండలి) 2025 ప్రశ్నాపత్రాలు సమాధానాలతో — '
                   + ('పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ (తెలుగు, ఇంగ్లీష్), ' if aee_p1() else '') + 'పేపర్-2 కామన్ సబ్జెక్ట్ (ఇంగ్లీష్); అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.'),
           aka='Assistant Environmental Engineer (AEE) in the A.P. Pollution Control Board (APPCB), recruited by the Andhra Pradesh Public Service Commission.',
           aka_short='APPSC Assistant Environmental Engineer (AP Pollution Control Board)',
           desc=lambda t: (f"APPSC Assistant Environmental Engineer (A.P. Pollution Control Board) previous question papers: the 2025 "
                           + ("Paper I General Studies & Mental Ability (English and Telugu) and Paper II Common Subject" if aee_p1() else "Paper II Common Subject (environmental engineering)")
                           + f" with answers from APPSC's final keys, {t:,} questions with explanations. Practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='APPSC · Assistant Environmental Engineer · A.P. Pollution Control Board · 2025',
           papers_note="Answers come from APPSC's final keys (6 August 2025) on the master question papers of the computer-based test held on 25 March 2025 (Notification 15/2023): the option marked correct there is the answer. "
                       "Questions APPSC ignored for all candidates are left out; where APPSC accepted more than one option, each accepted option is shown as correct. "
                       + ("Paper I is in English and Telugu as printed; Paper II (Common Subject) is in English only." if aee_p1() else
                          "Paper II (Common Subject) is set in English only. Paper I (General Studies & Mental Ability, English and Telugu) is being added next.")),
      dict(id='appsc-aso', dir='appsc-assistant-statistical-officer', src='appsc-aso', key='ap-aso', name='APPSC Assistant Statistical Officer (ASO)',
           short='APPSC ASO', seo='APPSC ASO', slugp='appsc-aso', papers=ASO_PAPERS, subjects=ASO_SUBJECTS, faq=FAQ_ASO,
           board='APPSC', l2=L2_TE, pb='/appsc-assistant-statistical-officer/', keyname="APPSC's final key", keyshort="APPSC's final keys", bits=True,
           te_name='ఏపీపీఎస్సీ అసిస్టెంట్ స్టాటిస్టికల్ ఆఫీసర్ (ASO)', te_paper='రాత పరీక్ష', subj_te=ASO_SUBJ_TE,
           title=f'APPSC ASO Previous Question Papers with Answers – Assistant Statistical Officer {aso_years()} Paper 2 Statistics & Economics | Learn with Anil',
           h1='APPSC Assistant Statistical Officer (ASO) previous question papers <em>with answers.</em>',
           l2line=f'ఏపీపీఎస్సీ అసిస్టెంట్ స్టాటిస్టికల్ ఆఫీసర్ (ASO) {aso_years()} పేపర్-2 (స్టాటిస్టిక్స్, ఎకనామిక్స్, అకౌంటెన్సీ, కంప్యూటర్స్) ప్రశ్నాపత్రాలు సమాధానాలతో — తెలుగు, ఇంగ్లీష్; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Assistant Statistical Officer (ASO) in the A.P. Economics & Statistical Subordinate Service, recruited by the Andhra Pradesh Public Service Commission. The same Paper II subjects are asked in the TGPSC MPSO / ASO exam.',
           aka_short='APPSC Assistant Statistical Officer (AP Economics & Statistics Department)',
           desc=lambda t: (f"APPSC Assistant Statistical Officer (ASO) previous question papers: Paper II (Subject) of {aso_years()} with answers from APPSC's final keys, "
                           f"{t:,} questions on statistics, economics, accountancy and computers in English and Telugu with explanations. Useful for TGPSC MPSO / ASO too. "
                           f"Practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow=f'APPSC · Assistant Statistical Officer · A.P. Economics &amp; Statistical Sub-Service · {aso_years().replace(" and ", " &amp; ")}',
           papers_note=("Answers come from APPSC's final keys on the master question papers of the computer-based tests (Notification 12/2024, 29 April 2025"
                        + ("; Notification 20/2021, 4 November 2022" if 'aso22' in aso_have() else '') + "): the option marked correct there is the answer. "
                        "Questions APPSC ignored for all candidates are left out. The papers are in English and Telugu as printed (the 2025 computer questions in English only).")),
      dict(id='appsc-fro', dir='appsc-forest-range-officer', src='appsc-fro', key='ap-fro', name='APPSC Forest Range Officer (FRO)',
           short='APPSC FRO', seo='APPSC FRO', slugp='appsc-fro', papers=FRO_PAPERS, subjects=FRO_SUBJECTS, faq=FAQ_FRO,
           board='APPSC', l2=L2_TE, pb='/appsc-forest-range-officer/', keyname="APPSC's final key", keyshort="APPSC's final keys", bits=True,
           te_name='ఏపీపీఎస్సీ ఫారెస్ట్ రేంజ్ ఆఫీసర్ (FRO)', te_paper='రాత పరీక్ష', subj_te=FRO_SUBJ_TE,
           title='APPSC FRO Previous Question Papers with Answers – Forest Range Officer Screening 2019 & 2025, Mains 2020 & 2023 GS and General Forestry | Learn with Anil',
           h1='APPSC Forest Range Officer (FRO) previous question papers <em>with answers.</em>',
           l2line='ఏపీపీఎస్సీ ఫారెస్ట్ రేంజ్ ఆఫీసర్ (FRO) పాత ప్రశ్నాపత్రాలు సమాధానాలతో — స్క్రీనింగ్ టెస్ట్ 2019, 2025; మెయిన్స్ 2020, 2023 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ (తెలుగు, ఇంగ్లీష్), జనరల్ ఫారెస్ట్రీ-1, 2 (ఇంగ్లీష్); అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Forest Range Officer (FRO) in the A.P. Forest Service, Andhra Pradesh Forest Department, recruited by the Andhra Pradesh Public Service Commission.',
           aka_short='APPSC Forest Range Officer (AP Forest Department)',
           desc=lambda t: (f"APPSC Forest Range Officer (FRO) previous question papers: the 2025 and 2019 Screening Tests, Paper I General Studies & Mental Ability and General Forestry I and II of the 2023 and 2020 Mains, with answers from APPSC's final keys, "
                           f"{t:,} questions with explanations. Practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='APPSC · Forest Range Officer · A.P. Forest Service · Screening &amp; Mains, 2019–2025',
           papers_note="Answers come from APPSC's final keys on the master question papers of the computer-based Screening Test of 16 March 2025 (Notification 11/2024) and Main Examinations of September 2023 (Notification 21/2022) and March 2020 (Notification 10/2018): the option marked correct there is the answer. The 2019 Screening Test key prints only the correct answer, so that paper is quick-recall questions. Questions APPSC ignored or deleted for all candidates are left out; where APPSC accepted two options, both are shown as correct. The 2023 Mains Paper I and the first section of the 2025 Screening Test are in English and Telugu as printed; the other papers are in English only. APPSC has published only the initial keys of the 2025 Mains (Notification 11/2024), so those papers are not here yet."),
      dict(id='ap-police-si', dir='ap-police-si', src='ap-police-si', key='ap-si', name='AP Police SI', short='AP Police SI', seo='AP Police SI',
           slugp='ap-police-si', papers=AP_SI_PAPERS, subjects=AP_SUBJECTS, faq=FAQ_AP('SI'), board='SLPRB', l2=L2_TE, pb='/ap-police-si/',
           keyname="SLPRB's key", keyshort="SLPRB's keys", bits=True,
           te_name='ఏపీ పోలీస్ ఎస్ఐ', te_paper='ప్రిలిమినరీ పరీక్ష', subj_te=AP_POLICE_SUBJ_TE,
           title='AP Police SI Previous Question Papers with Answers – SLPRB AP SI Prelims 2023 Paper 1 & 2, English & Telugu | Learn with Anil',
           h1='AP Police SI previous year question papers <em>with answers.</em>',
           l2line='ఏపీ పోలీస్ ఎస్ఐ ప్రిలిమినరీ పరీక్ష పాత ప్రశ్నాపత్రాలు (పేపర్-1 అర్థమెటిక్, రీజనింగ్; పేపర్-2 జనరల్ స్టడీస్) SLPRB కీ సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Also known as the Andhra Pradesh Police Sub-Inspector exam: SCT SI (Civil), RSI (AR) and SI (SPF) posts, conducted by the State Level Police Recruitment Board, Andhra Pradesh (SLPRB AP / APSLPRB).',
           aka_short='Andhra Pradesh Police SI (SLPRB AP)',
           desc=lambda t: (f"AP Police SI (SLPRB AP / APSLPRB) previous question papers: the Preliminary Written Test of 19 February 2023, Paper I Arithmetic & Reasoning and Paper II General Studies, "
                           f"with answers from SLPRB's keys. {t:,} questions in English and Telugu with explanations; practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='SLPRB AP · SCT SI (Civil) &amp; RSI · Preliminary Written Test 2023',
           papers_note=("Answers come from SLPRB AP's keys for the booklet code of each paper (Paper I booklet A, Paper II booklet C) of the Preliminary Written Test held on 19 February 2023. For Paper I the final key made no change to the preliminary key. "
                        "For Paper II the final key accepted more than one answer for one question, but that file is no longer on SLPRB's website, so Paper II shows the preliminary key's answers. "
                        "Every question is in English and Telugu, as printed in the booklet.")),
      dict(id='ap-police-constable', dir='ap-police-constable', src='ap-police-constable', key='ap-pc', name='AP Police Constable', short='AP Constable', seo='AP Police Constable',
           slugp='ap-police-constable', papers=AP_PC_PAPERS, subjects=AP_SUBJECTS, faq=FAQ_AP('PC'), board='SLPRB', l2=L2_TE, pb='/ap-police-constable/',
           keyname="SLPRB's final key", keyshort="SLPRB's final key", bits=True,
           te_name='ఏపీ పోలీస్ కానిస్టేబుల్', te_paper='ప్రిలిమినరీ పరీక్ష', subj_te=AP_POLICE_SUBJ_TE,
           title='AP Police Constable Previous Question Papers with Answers – SLPRB AP Constable Prelims 2023, English & Telugu | Learn with Anil',
           h1='AP Police Constable previous year question papers <em>with answers.</em>',
           l2line='ఏపీ పోలీస్ కానిస్టేబుల్ ప్రిలిమినరీ పరీక్ష పాత ప్రశ్నాపత్రం (మునుపటి ప్రశ్నపత్రం) SLPRB ఫైనల్ కీ సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.',
           aka='Also known as the Andhra Pradesh Police Constable (AP PC) exam: SCT PC (Civil), PC (AR), Firemen and Warders, conducted by the State Level Police Recruitment Board, Andhra Pradesh (SLPRB AP / APSLPRB).',
           aka_short='Andhra Pradesh Police Constable (SLPRB AP)',
           desc=lambda t: (f"AP Police Constable (SLPRB AP / APSLPRB) previous question paper: the Preliminary Written Test of 22 January 2023 with answers from SLPRB's final key. "
                           f"{t:,} questions on English, arithmetic, reasoning and general studies in English and Telugu with explanations; practice quizzes and timed mock tests with the ₹45 All-in-One Pass."),
           eyebrow='SLPRB AP · SCT PC (Civil) &amp; APSP · Preliminary Written Test 2023',
           papers_note=("Answers come from SLPRB AP's final key for booklet A of the Preliminary Written Test held on 22 January 2023; the question booklet is SLPRB's own copy. "
                        "The English-language questions are in English only; every other question is in English and Telugu, as printed in the booklet.")),
    ]


def main():
    confs = exam_confs()
    loaded = []
    for c in confs:
        papers, questions = load_exam(c)
        if questions: loaded.append((c, papers, questions))
    # only exams whose papers are built (an exam configured before its paper sources are added, e.g. AMVI, stays out of the lists and links)
    PAY['exams'] = ', '.join(c['seo'] for c, _, _ in loaded)   # the All-in-One Pass covers every one of these
    PAY['exam_links'] = [(c['seo'], c['pb']) for c, _, _ in loaded]
    counts = {c['id']: len(qs) for c, _, qs in loaded}
    grand = sum(counts.values())
    import upscmains   # UPSC CSE Mains GS 1-4 previous questions with model answers (tools/upscmains.py): its own pages; Prelims is the 'upsc-prelims' app
    upm_qs, _ = upscmains.load(SRC)
    upa_qs, _ = upscmains.load(SRC, 'an')   # Anthropology optional Papers I-II (same pages module, course 'an')
    if upm_qs: counts[upscmains.EXAM] = len(upm_qs) + len(upa_qs)
    global PRE_LIVE   # the UPSC CSE hub's Prelims box: (questions, years, papers) of the built Prelims app
    pre = [(ps, qs) for c, ps, qs in loaded if c['id'] == 'upsc-prelims']
    PRE_LIVE = ((len(pre[0][1]), sorted({p['year'] for p in pre[0][0]}), len(pre[0][0]),
                 # the newest GS Paper I and CSAT pages, for the photo links on the hub card: {'gs': (year, slug), 'csat': (year, slug)}
                 {k: max((p['year'], p['slug']) for p in pre[0][0] if p['id'].startswith(k)) for k in ('gs', 'csat') if any(p['id'].startswith(k) for p in pre[0][0])})
                if pre else None)

    vpath = os.path.join(SRC, 'videos.json')
    videos = json.load(open(vpath, encoding='utf-8')) if os.path.exists(vpath) else {}
    npath = os.path.join(SRC, 'notes.json')
    notes = json.load(open(npath, encoding='utf-8')) if os.path.exists(npath) else []
    # sealed books (tools/books_seal.py): the app downloads /books/<file> and gets its key with the All-in-One Pass
    bpath = os.path.join(SRC, 'books', 'books.json')
    sealed = json.load(open(bpath)) if os.path.exists(bpath) else {}
    # exam-booklet PDFs of the previous papers (tools/booklets.py), All-in-One Pass only: exam -> paper -> key, file, name, pages
    kpath_ = os.path.join(SRC, 'books', 'booklets.json')
    booklets = json.load(open(kpath_)) if os.path.exists(kpath_) else {}
    BOOKLETS.clear(); BOOKLETS.update(booklets)
    # sealed paid explanations (tools/ex_seal.py): exam id -> key, file, n, h; the app gets them with the All-in-One Pass
    xpath_ = os.path.join(SRC, 'books', 'explanations.json')
    exsealed = json.load(open(xpath_, encoding='utf-8')) if os.path.exists(xpath_) else {}
    notes = [dict(b, dl=sealed[b['id']]['pdf'], buy='') if b['id'] in sealed else b for b in notes]
    epath = os.path.join(SRC, 'exams.json')
    catalog = json.load(open(epath, encoding='utf-8')) if os.path.exists(epath) else dict(cats=[], exams=[])
    # an exam tile is live only if its questions were built
    for e in catalog['exams']:
        if e.get('live') and e['id'] not in counts: e.pop('live')
    import bahubali   # paid Group-II Mains test series (encrypted; see tools/bahubali.py)
    bb_live = bool(bahubali.load_series().get('tests'))
    bb_url = '/' + bahubali.URLDIR + '/' if bb_live else ''
    global BB_URL
    BB_URL = bb_url
    photo_uri, photo_bytes = photo_data_uri()
    tpl = open(os.path.join(ROOT, 'tools', 'app.html'), encoding='utf-8').read()
    head, body = tpl.split('<!--BODY-->')
    live_names = [c['name'] for c, _, _ in loaded]
    NAVB = {'upsc': 'UPSC', 'ap': 'APPSC', 'tg': 'TGPSC & TS Police', 'ssc': 'SSC', 'rail': 'Railways', 'bank': 'Banking'}   # Anil, 2 Nov 2026: the top bar lists boards, not every exam
    nav_extra = ''.join(f'      <a href="/#exams-list" data-act="excat" data-cat="{cid}" data-hubonly>{lbl}</a>\n' for cid, lbl in NAVB.items()
                        if any(c['id'] == cid for c in catalog['cats']))
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
        # a book with an 'exams' list shows only on those exams' pages; the others (APPSC Mains books) on NOTES_EXAMS
        # the start page's Study Material shows every book (Anil, 2 Nov 2026: "in study material only this 3 books are showing")
        enotes = [dict(b, cover=upath(b['cover']), samples=[upath(x) for x in b.get('samples', [])]) for b in notes
                  if is_root or (conf['id'] in b['exams'] if b.get('exams') else conf['id'] in NOTES_EXAMS)]
        emains = mains_kit(conf)
        for q in questions:
            if q['id'] in videos and is_root: q['v'] = videos[q['id']]
        bks = booklets.get(conf['id'], {})
        papers = [dict(p, bk=dict(key=bks[p['id']]['key'], name=bks[p['id']]['name'], pages=bks[p['id']]['pages'])) if p['id'] in bks else p for p in papers]
        exb = exsealed.get(conf['id'])
        pub_qs, stale = public_questions(questions, exb)
        if stale: print(f'  NOTE {conf["id"]}: {stale} paid explanations are not sealed yet and stay in the public app data; run tools/ex_seal.py {conf["id"]}')
        data = dict(mockHtml=inapp_mocks(conf, papers), secHtml=inapp_sectionals(conf, papers, questions),
                    pdfs={k: dict(key=v['key'], name=v['name'], pages=v['pages']) for k, v in bks.items()}, papers=papers, subjects=subjects, questions=pub_qs, instagram=INSTAGRAM,
                    exb=dict(key=exb['key'], file=exb['file']) if exb else None, site=SITE_URL, notes=enotes, wa=WHATSAPP,
                    mains=emains, mainsP5=MAINS_P5 if emains else None,
                    notesTitle=ROOT_NOTES[0] if is_root else conf.get('notes_title', ''), notesLede=ROOT_NOTES[1] if is_root else conf.get('notes_lede', ''),
                    key=conf['key'], exam=conf['name'], bahubali=bb_url if conf['board'] == 'APPSC' else '', examShort=conf['short'], papersNote=conf['papers_note'], hub=is_root,
                    board=conf['board'], l2={k: conf['l2'][k] for k in ('code', 'label', 'name', 'font')},
                    base=prefix, qotd=qotd_pool(loaded, 120) if is_root else [],
                    pay=dict(pay_data(conf), sample=len(free_sample(conf, papers, questions)) if any(p['fmt'] == 'mcq' for p in papers) else 0),
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

        links = [(N['h1'], '/' + rel) for rel, N in NOTIFS.items() if N['exam'] == conf['id']]
        if bb_url and conf['id'] == 'appsc-group-2': links.insert(0, ('New: Bahubali Test Series – Group 2 Mains full-length tests', bb_url))
        tiles = tiles_html(conf, papers, questions, links, emains)

        def fill(s, photo, title, seo, desc=''):
            return (s.replace('{{SEO_HEAD}}', seo).replace('{{TITLE}}', title).replace('{{DESC}}', esc(desc))
                     .replace('{{L2CODE}}', l2['code']).replace('{{L2LABEL}}', l2['label']).replace('{{FONTS2}}', l2['gf'])
                     .replace('{{LANGS}}', 'English' if papers and all(p.get('en_only') for p in papers) else 'English and ' + l2['name']).replace('{{KEYSHORT}}', conf['keyshort'])
                     .replace('{{BOARD}}', conf['board'])
                     .replace('{{FOOTSRC}}', ('Questions and answers are from the official final keys, or the preliminary key where the final key could not be found.'
                                              if any('preliminary key' in x.get('key', '') for x in papers) else 'Questions and answers are from the official final keys.') if conf['board'] in ('APPSC', 'TSLPRB', 'SLPRB')
                              else f'Questions are from {conf["board"]}\'s official question paper; answers from {conf["keyshort"]}.')
                     .replace('{{FROMPAPERS}}', f'{len(papers)} official papers' if len(papers) > 1 else f'the official {papers[0]["year"]} {esc(papers[0]["stage"])} question paper')
                     .replace('{{PAPERSK}}', f'Official {conf["board"]} paper' + ('s' if len(papers) > 1 else ''))
                     .replace('{{HOME_PAPERS}}', home_papers).replace('{{PYQPAGE}}', conf['pb'] + 'pyqs.html').replace('{{HOME_SUBJECTS}}', home_subjects).replace('{{FAQ}}', faq_html)
                     .replace('{{DATA}}', data_json).replace('{{PHOTO}}', photo)
                     .replace('{{TOTAL}}', str(total)).replace('{{SITE}}', SITE_URL).replace('{{NPAPERS}}', str(len(papers)))
                     .replace('{{HUB_NOTES}}', '').replace('{{HOME_NOTES}}', home_notes([b for b in enotes if not b.get('exams') or conf['id'] in b['exams']], bb_url if conf['board'] == 'APPSC' else '', conf.get('notes_line', ''))).replace('{{HUB}}', hub)
                     .replace('{{NEXAMS}}', str(len(catalog['exams']))).replace('{{TOTALC}}', f'{grand:,}').replace('{{NLIVE}}', str(len(loaded)))
                     .replace('{{NLIVEX}}', str(sum(1 for e in catalog['exams'] if e.get('live')))).replace('{{HERO_NEW}}', HERO_NEW)
                     .replace('{{MOCKQ}}', f'{mock_questions():,}')
                     .replace('{{GOALPCT}}', f'{grand * 100 / 100000:.0f}').replace('{{GOALW}}', f'{max(1.5, min(100, grand * 100 / 100000)):.1f}')
                     .replace('{{LIVE_SUMMARY}}', esc(live_summary))
                     .replace('{{HUB_CTAS}}', hub_ctas)
                     .replace('{{NAV_EXTRA}}', nav_extra if is_root else '')
                     .replace('{{NAV_FUND}}', NAV_FUND if is_root else '')
                     .replace('{{TIMERS}}', timers).replace('{{HUBHREF}}', hubhref).replace('{{ROOTUP}}', up)
                     .replace('{{EXAM}}', esc(conf['name'])).replace('{{EXAMSHORT}}', esc(conf['short']))
                     .replace('{{HERO_PHC}}', ' hero-ph' if exam_photo(conf['id'], 'h') else '').replace('{{HERO_PHS}}', f' style="--hero-ph:url({exam_photo(conf["id"], "h")})"' if exam_photo(conf['id'], 'h') else '')
                     .replace('{{HERO_PHCR}}', f'<p class="hero-cr">{photo_credit(conf["id"])}</p>' if exam_photo(conf['id'], 'h') else '')
                     .replace('{{EYEBROW}}', conf['eyebrow']).replace('{{H1}}', conf['h1'])
                     .replace('{{L2LINE}}', f'<span lang="{l2["code"]}">{esc(conf["l2line"])}</span>')
                     .replace('{{AKA}}', esc(conf.get('aka', '')))
                     .replace('{{TILES}}', tiles)
                     .replace('{{NOTES_NAV}}', ('<a href="#mains" data-v="mains">Mains Tool Kit <span class="new">NEW</span></a>' if emains else '')
                              + ('<a href="#notes" data-v="notes">Study Material <span class="new">NEW</span></a>' if enotes else ''))
                     .replace('{{NOTES_FOOT}}', '<a href="#notes">Study material</a> · ' if enotes else ''))
        _fill0, LF = fill, lang_fills()
        def fill(s, photo, title, seo, desc=''):   # then the site's languages (SITE_LANGS)
            s = _fill0(s, photo, title, seo, desc)
            for k, v in LF.items(): s = s.replace(k, v)
            return s
        root_title = 'Learn with Anil (LearnWithAnil.in) – PYQs with Answers: UPSC Prelims, Mains & Anthropology, APPSC Group 1 & 2, TS Police, SSC CGL'
        pre_y = (lambda ys: f' ({ys[0]}–{ys[-1]})' if len(ys) > 1 else f' ({ys[0]})')(PRE_LIVE[1]) if PRE_LIVE else ''   # Anil, 2 Nov 2026: home title/description name UPSC Prelims and Anthropology
        root_desc = (f'Learn with Anil (learnwithanil.in): previous year question papers (PYQs) with answers for UPSC Civil Services Prelims GS Paper I & CSAT{pre_y} in English & Hindi, '
                     f'APPSC Group 1 & Group 2 (AP Group 1, AP Group 2), TS Police SI & Constable '
                     f'(Telangana police, TSLPRB / TGPRB), UPSC CAPF AC, UPSC EPFO (APFC, EO/AO), SSC CGL, TGPSC HMWSSB Manager, APPSC & TGPSC AMVI (Assistant Motor Vehicle Inspector), APPSC Endowment Officer (EO Grade-III), APPSC Analyst Grade-II and APPSC Forest Range Officer (FRO). {grand:,} questions from the official keys, with explanations in English, Telugu and Hindi. '
                     f'UPSC Civil Services Mains GS 1–4 (2019–2026), UPSC Anthropology optional Papers I & II and APPSC Group 1 Mains questions with model answers. One ₹45 All-in-One Pass for every exam.')
        home_title = conf['title']
        ptxt = f'{len(papers)} official papers' if len(papers) > 1 else f'the official {papers[0]["year"]} {papers[0]["stage"]} question paper'
        home_desc = conf['desc'](total)
        pb = conf['pb']; basedir = '/' + prefix
        person = {"@context":"https://schema.org","@type":"Person","name":"Jupudi Anil Kumar","jobTitle":"UPSC Faculty and Mentor","telephone":"+91-94947-92739","email":"mailto:anilkumarjupudi360360@gmail.com","url":SITE_URL+'/appsc-group-2/about/',"image":SITE_URL+'/anil.jpg',"sameAs":[f"https://www.instagram.com/{INSTAGRAM}/","https://www.youtube.com/@learn_with_anil06"]}
        website = {"@context":"https://schema.org","@type":"WebSite","name":"Learn with Anil","alternateName":["LearnWithAnil","learnwithanil.in","Learn with Anil PYQs"],"url":SITE_URL+'/'}
        org = {"@context":"https://schema.org","@type":"Organization","name":"Learn with Anil","url":SITE_URL+'/',"logo":SITE_URL+'/icon-512.png',"alternateName":["LearnWithAnil","learnwithanil.in","Learn with Anil PYQs"],"founder":{"@type":"Person","name":"Jupudi Anil Kumar"},"sameAs":[f"https://www.instagram.com/{INSTAGRAM}/","https://t.me/learn_with_anil06","https://www.youtube.com/@learn_with_anil06"]}
        faqld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in faq]}
        seo_name = conf['seo']
        views = {   # view: (title, description, canonical path, indexable)
          'papers': ((f'{seo_name} Previous Year Question Papers with Answers – All {len(papers)} Papers | Learn with Anil' if len(papers) > 1 else
                      f'{seo_name} Previous Question Paper with Answers – {paper_kw(conf, papers[0]).replace(seo_name + " ", "")}, English & {conf["l2"]["name"]} | Learn with Anil'),
                     (f'All {len(papers)} {seo_name} previous year question papers' if len(papers) > 1 else f'{seo_name} previous question paper') + f' ({", ".join(paper_kw(conf, p).replace(seo_name + " ", "") for p in sorted(papers, key=lambda p: (-p["year"], p["id"])))}): '
                     f'practise {"each paper" if len(papers) > 1 else "it"} online as a quiz or a timed mock test, with answers and explanations, with the ₹45 All-in-One Pass.', pb + 'papers/', True),
          'practice': (f'{seo_name} Mock Test & Topic-wise Quiz from Previous Papers | Learn with Anil',
                       f'{seo_name} mock test and topic-wise quiz made from {total:,} real previous year questions{" (practice bits)" if conf["board"] == "APPSC" or conf.get("bits") else ""}: '
                       f'choose papers, subjects and topics, then practise with answers or take a timed test.', pb + 'practice/', True),
          'bank': (f'{seo_name} Question Bank – Search All {total:,} PYQs{" & Practice Bits" if conf["board"] == "APPSC" or conf.get("bits") else ""} | Learn with Anil',
                   f'Search every {seo_name} previous year question by keyword, paper or topic, with answers from {conf["keyshort"]} and explanations.', pb + 'bank/', True),
          'notes': ((conf['notes_seo'][0], conf['notes_seo'][1], pb + 'notes/', True) if conf.get('notes_seo') else
                    ('Study Material 2026-27 – Crisp Notes by Jupudi Anil Kumar | Learn with Anil',
                     'Exam-focused study material by Jupudi Anil Kumar: Crisp Notes on AP Economy and Science & Technology for APPSC Mains, with the latest 2026 data.', '/appsc-group-2/notes/', True)),
          'about': ('About Jupudi Anil Kumar – Learn with Anil',
                    'Jupudi Anil Kumar is a civil-services educator with 2.5 years of teaching and mentorship for UPSC, APPSC and TGPSC aspirants. He built Learn with Anil to make previous-year questions easy and affordable to practise for every aspirant.', '/appsc-group-2/about/', True),
          'mistakes': (f'Mistakes Notebook – {seo_name} | Learn with Anil', 'Your mistakes notebook on Learn with Anil.', pb + 'mistakes/', False),
          'smart': (f'Smart Quiz – {seo_name} | Learn with Anil', 'Re-attempt the questions you got wrong.', pb + 'smart/', False),
          'bookmarks': (f'Bookmarks – {seo_name} | Learn with Anil', 'Your saved questions on Learn with Anil.', pb + 'bookmarks/', False),
          'heatmap': (f'Topic Heatmap – {seo_name} | Learn with Anil', 'Your topic-wise accuracy on Learn with Anil.', pb + 'heatmap/', False),
          'mocks': (f'{seo_name} Mock Tests | Learn with Anil', f'{seo_name} mock tests with a timer, answers and explanations.', pb + 'mocks/', False),
          'sectionals': (f'{seo_name} Sectional Tests | Learn with Anil', f'{seo_name} subject-wise sectional tests with a timer.', pb + 'sectionals/', False),
          'account': ('My account – Learn with Anil', 'Your Learn with Anil account: your All-in-One Pass, devices and payments.', pb + 'account/', False),
        }
        sdata = dict(data, pb=pb, qpages=True, examSeo=seo_name, homeTitle=home_title, hubTitle=root_title)
        sjson = json.dumps(sdata, ensure_ascii=False, separators=(',', ':'))
        import hashlib
        outdir = os.path.join(DIST, 'site', conf['dir'])
        os.makedirs(os.path.join(outdir, 'data'), exist_ok=True)
        # figures go to their own files (loaded only when a question with a figure is on screen), so the
        # data file the app waits for stays small: SSC CGL 2.1 MB -> ~0.7 MB, TS SI 1.2 MB -> ~0.4 MB
        os.makedirs(os.path.join(outdir, 'qimg'), exist_ok=True)

        def _fig(m):
            raw = base64.b64decode(m.group(2))
            name = f'qimg/{hashlib.sha1(raw).hexdigest()[:12]}.{m.group(1)}'
            fp = os.path.join(outdir, name)
            if not os.path.exists(fp): open(fp, 'wb').write(raw)
            return '/' + (conf['dir'] + '/' if conf['dir'] else '') + name
        sjson = re.sub(r'data:image/(png|jpeg);base64,([A-Za-z0-9+/=]+)', _fig, sjson)
        dfile = f'data/{conf["key"]}-{hashlib.sha1(sjson.encode()).hexdigest()[:10]}.js'
        open(os.path.join(outdir, dfile), 'w', encoding='utf-8').write('window.LWA_DATA=' + sjson + ';\n')
        DATA_FILES[conf['id']] = (conf['dir'], dfile)
        sbody = body.replace('<script type="application/json" id="lwa-data">{{DATA}}</script>', f'<script src="{dfile}"></script>')
        assert sbody != body

        def site_doc(title, desc, canon_path, ld, index=True):
            canon = SITE_URL + canon_path
            body_ = sbody if canon_path == '/' else re.sub(r'<div id="hub-static" class="view">.*?(?=<div id="home-static")', '', sbody, flags=re.S)
            assert canon_path == '/' or 'id="hub-static"' not in body_
            seo = (ICONS + ga_tag() + f'<link rel="canonical" href="{canon}">\n<meta name="robots" content="{"index,follow" if index else "noindex,follow"}">\n'
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

        if not enotes: views.pop('notes', None)   # no study-material page outside APPSC Group 1 / Group 2
        if emains:
            views['mains'] = ('APPSC Group 1 Mains Answer Writing Tool Kit – Previous Questions of Papers I to IV by Syllabus | Learn with Anil',
                              'APPSC Group 1 Mains previous questions of 2020, 2023 and 2025 for Paper I (Essay), II (History & Geography), III (Polity & Ethics) '
                              'and IV (Economy), sorted by syllabus, with practice questions: four PDF books by Jupudi Anil Kumar, part of the ₹45 All-in-One Pass.',
                              pb + 'mains/', True)
        site_pages = {}   # path under the site root -> html
        if is_root:
            os.makedirs(os.path.join(DIST, 'artifact', 'papers')); os.makedirs(os.path.join(DIST, 'artifact', 'subjects'))
            open(os.path.join(DIST, 'artifact', 'index.html'), 'w', encoding='utf-8').write(fill(head + body, photo_uri, 'Learn with Anil', '', root_desc))
            site_pages['index.html'] = site_doc(root_title, root_desc, '/', [website, org, person])
        exam_crumbs = [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb)]
        site_pages[pb.strip('/') + '/index.html'] = site_doc(home_title, home_desc, pb, [person, faqld, crumb_ld(exam_crumbs)])
        for v, (t, d, cp, ix) in views.items():
            vld = [crumb_ld(exam_crumbs + [(VIEW_CRUMB.get(v, v.title()), SITE_URL + cp)])] if ix and cp.startswith(pb) else []
            site_pages[pb.strip('/') + f'/{v}/index.html'] = site_doc(t, d, cp, vld, ix and cp.startswith(pb))
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
        if conf['id'] in MAINS_EXAMS:   # APPSC Group-1 Mains previous questions with model answers (tools/g1mains.py)
            import g1mains
            for rel, content in g1mains.pages(sys.modules[__name__], conf).items():
                fp = os.path.join(outdir, rel); os.makedirs(os.path.dirname(fp), exist_ok=True)
                open(fp, 'w', encoding='utf-8').write(content)
                all_pages[prefix + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)] = None
        # one page per question
        qpages = question_pages(conf, papers, questions, subj)
        qdir = os.path.join(DIST, 'site', pb.strip('/'), 'q'); os.makedirs(qdir, exist_ok=True)
        for rel, content in qpages.items():
            open(os.path.join(DIST, 'site', pb.strip('/'), rel), 'w', encoding='utf-8').write(content)
            if not GOOGLE_SKIP_QPAGES: all_pages[pb.lstrip('/') + rel] = None
        if PUBLIC_PDFS:
            for p in papers: all_pages[pdf_href(conf, p).lstrip('/')] = None   # the PDFs come from tools/pdfs.py
        print(f'  {conf["name"]}: {total} questions, {len(pages)} static pages, {len(qpages)} question pages, {len(site_pages)} app pages')

    # one crawlable page per recruiting board listing all its papers (where "APPSC PYQs" / "TS police previous papers" searches land)
    lands = {rel: None for rel in LANDINGS if any(c['board'] == LANDINGS[rel]['board'] for c, _, _ in loaded)}
    for rel in lands:
        open(os.path.join(DIST, 'site', rel), 'w', encoding='utf-8').write(landing_page(loaded, rel))
    all_pages = {**lands, **all_pages}
    notifs = {rel: None for rel in NOTIFS if not NOTIFS[rel].get('exam') or any(c['id'] == NOTIFS[rel]['exam'] for c, _, _ in loaded)}
    for rel in notifs:
        open(os.path.join(DIST, 'site', rel), 'w', encoding='utf-8').write(notif_page(loaded, rel))
    open(os.path.join(DIST, 'site', NEWS_HUB), 'w', encoding='utf-8').write(news_hub_page(loaded, list(notifs)))   # every news page in one list (SEO, 4 Nov 2026)
    notifs[NEWS_HUB] = None
    mocks = {}
    for c, ps, qs in loaded:
        if not any(p['fmt'] == 'mcq' for p in ps): continue
        for fn in (pyq_page, mock_page, sectional_page):
            rel, html_ = fn(c, ps, qs)
            open(os.path.join(DIST, 'site', rel), 'w', encoding='utf-8').write(html_)
            mocks[rel] = None
    if bb_live: mocks[bahubali.page(os.path.join(DIST, 'site'))] = None
    all_pages = {**notifs, **mocks, **all_pages}

    open(os.path.join(DIST, 'site', 'help.html'), 'w', encoding='utf-8').write(help_page(loaded))
    open(os.path.join(DIST, 'site', 'privacy.html'), 'w', encoding='utf-8').write(privacy_page())
    open(os.path.join(DIST, 'site', 'terms.html'), 'w', encoding='utf-8').write(terms_page())
    for fn, page in (('refund.html', refund_page), ('delivery.html', delivery_page), ('contact.html', contact_page)):
        open(os.path.join(DIST, 'site', fn), 'w', encoding='utf-8').write(page())
    all_pages = {**all_pages, 'help.html': None, 'privacy.html': None, 'terms.html': None, 'refund.html': None, 'delivery.html': None, 'contact.html': None}
    open(os.path.join(DIST, 'site', 'funders.html'), 'w', encoding='utf-8').write(funders_page(loaded))
    # Anil, 28 Oct 2026: tapping Practise / Start on the PYQs, mock-test and sectional pages felt slow on phones, because the app
    # page then downloads the exam's question data (0.2-2.3 MB). These pages are where students go next into the app, so they
    # ask the browser to fetch that file quietly in the background (low priority, used from the cache on the next page).
    for eid, (edir, dfile) in DATA_FILES.items():
        href = '/' + (edir + '/' if edir else '') + dfile
        for name in ('pyqs.html', 'mock-test.html', 'sectional-tests.html'):
            fp = os.path.join(DIST, 'site', edir, name) if edir else os.path.join(DIST, 'site', 'appsc-group-2', name)
            if not os.path.exists(fp): continue
            h = open(fp, encoding='utf-8').read()
            if 'rel="prefetch"' not in h:
                open(fp, 'w', encoding='utf-8').write(h.replace('</head>', f'<link rel="prefetch" href="{href}" as="script">\n</head>', 1))
    all_pages = {**all_pages, 'funders.html': None}
    # UPSC CSE: the hub and the Mains GS pages (tools/upscmains.py)
    for rel, content in upscmains.pages(sys.modules[__name__]).items():
        fp = os.path.join(DIST, 'site', upscmains.EXAM, rel); os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w', encoding='utf-8').write(content)
        all_pages[upscmains.EXAM + '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)] = None
    # free sample chapters of the study books (public PDFs; Anil, 28 Oct 2026) go in the sitemap so search engines and AI assistants find them
    for b in notes:
        if b.get('free'): all_pages[b['free'].lstrip('/')] = None
    # the free paper PDFs were removed on 23 Oct 2026, but Google still shows their addresses: send those visitors to the paper page
    old_pdfs = {f'/{c["dir"] + "/" if c["dir"] else ""}pdf/{pdf_name(c, p)}': f'/{c["dir"] + "/" if c["dir"] else ""}papers/{p["slug"]}.html'
                for c, papers, _ in loaded for p in papers}
    open(os.path.join(DIST, 'site', '404.html'), 'w', encoding='utf-8').write(not_found_page(old_pdfs))

    # sitemap + robots (site only)
    today = date.today().isoformat()
    urls = [SITE_URL + '/'] + [SITE_URL + '/' + rel for rel in all_pages]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls: sm.append(f'  <url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>')
    sm.append('</urlset>')
    open(os.path.join(DIST, 'site', 'sitemap.xml'), 'w').write('\n'.join(sm) + '\n')
    kit_dirs = ''.join(f'Disallow: /{c["dir"]}/{MAINS_DIR}/\n' for c, _, _ in loaded if c['id'] in MAINS_EXAMS)   # the paid tool-kit PDFs
    open(os.path.join(DIST, 'site', 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n{kit_dirs}Disallow: /books/\n\nSitemap: {SITE_URL}/sitemap.xml\n')
    open(os.path.join(DIST, 'site', 'llms.txt'), 'w', encoding='utf-8').write(llms_txt(loaded, sum(len(q) for _, _, q in loaded)))
    # extra files served as-is at the site root (search-engine verification files etc.)
    static = os.path.join(SRC, 'static')
    if os.path.isdir(static):
        for f in os.listdir(static):
            shutil.copy(os.path.join(static, f), os.path.join(DIST, 'site', f))
    # sealed (encrypted) study books, part of the All-in-One Pass (tools/books_seal.py); keys only in Anil's private sheet
    os.makedirs(os.path.join(DIST, 'site', 'books'), exist_ok=True)
    for bid, bk in sealed.items(): shutil.copy(os.path.join(SRC, 'books', bk['file']), os.path.join(DIST, 'site', 'books', bk['file']))
    for ex in booklets.values():
        for bk in ex.values(): shutil.copy(os.path.join(SRC, 'books', bk['file']), os.path.join(DIST, 'site', 'books', bk['file']))
    for ex in exsealed.values(): shutil.copy(os.path.join(SRC, 'books', ex['file']), os.path.join(DIST, 'site', 'books', ex['file']))
    # sealed (encrypted) paid mocks: published as-is; the keys are only in Anil's private sheet (tools/mk_seal.py)
    for exam_dir, src_dir in [('ts-police-si', 'mission-khaki')] + [(v.get('dir', k), v['src']) for k, v in MOCK_PACKS.items() if v.get('src')]:
        mkdir_ = os.path.join(SRC, src_dir)
        if os.path.isdir(mkdir_):
            os.makedirs(os.path.join(DIST, 'site', exam_dir, 'mk'), exist_ok=True)
            for f in os.listdir(mkdir_):
                if f.endswith('.bin'): shutil.copy(os.path.join(mkdir_, f), os.path.join(DIST, 'site', exam_dir, 'mk', f))
    open(os.path.join(DIST, 'site', '.nojekyll'), 'w').write('')
    print(f'  grand total {grand} questions, {len(all_pages)} static pages')


def bahubali_promo(url):
    return f'''<a class="card notes-promo bb-promo" href="{url}">
      <div class="np-copy"><p class="eyebrow">New · APPSC Group-II Mains 2026</p><h2>Bahubali Test Series</h2>
      <p>24 full-length mock tests for Paper I and Paper II (12 each): 150 questions per test, English and Telugu, ⅓ negative marking, explanations from official sources and PDFs. {INCL}.</p>
      <span class="btn btn-primary">See the tests</span></div>
      <div class="bb-mark" aria-hidden="true"><b>150</b><span>Qs · 150 min</span></div>
    </a>'''


def home_notes(notes, bb_url='', line=''):
    if not notes and not bb_url: return ''
    if not notes: return f'<section class="wrap section">{bahubali_promo(bb_url)}</section>'
    covers = ''.join(f'<img src="{esc(b["cover"])}" alt="" width="140" height="198" loading="lazy">' for b in notes[:5])   # at most 5 covers, so the card fits a 390 px phone
    # Anil, 4 Nov 2026: "first books for that relevant exams followed by test series": the exam's own books, then the test series.
    return f'''<section class="wrap section">
    <a class="card notes-promo" href="#notes">
      <div class="np-copy"><p class="eyebrow">New · Study material</p><h2>Study material 2026-27</h2>
      <p>{esc(line) if line else esc(" and ".join(dict.fromkeys(b.get("subject_label", b["subject"]) for b in notes))) + " for APPSC Mains, with the latest 2026 data and APPSC's own previous questions inside."} {INCL}.</p>
      <span class="btn btn-primary">See the books</span></div>
      <div class="np-covers" aria-hidden="true">{covers}</div>
    </a>{bahubali_promo(bb_url) if bb_url else ''}
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
    """'APPSC Group 2 Prelims 2024', 'APPSC Group 2 Mains 2025 Paper 1', 'UPSC CAPF AC 2026 Paper 1'; a paper's own 'kwname' wins (EPFO: APFC vs EO/AO)."""
    if p.get('kwname'): return p['kwname']
    n = paper_no(p)
    if conf['board'] in ('UPSC', 'TGPSC'):
        return f'{conf["seo"]} {p["year"]}' + (f' Paper {n}' if n else '')
    stage = 'Prelims' if p['stage'].startswith(('Screening', 'Prelims', 'Preliminary')) else 'Mains'
    return f'{conf["seo"]} {stage} {p["year"]}' + (f' Paper {n}' if n else '')


def paper_alt(conf, p):
    """The paper's other name, if students also search by it."""
    if p.get('alt'): return '' if p['alt'] in p.get('kwname', '') else p['alt']   # AMVI: the name already says it
    if p['stage'].startswith('Screening'): return 'Screening Test'
    if p['stage'].startswith('Preliminary'): return 'Preliminary Written Test'
    if conf['board'] == 'UPSC': return 'General Ability and Intelligence'
    if conf['short'] == 'Group-I': return 'General Studies' if paper_no(p) == '1' else 'General Aptitude'
    return ''


def alt_shown(alt, title):
    """The alternative name, unless the paper's full title already says it (e.g. 'Final Written Exam, General Studies')."""
    if not alt: return ''
    return '' if all(x.strip().replace(' Exam', ' Examination') in title for x in alt.split(',')) else alt


def paper_kw_l2(conf, p):
    """The same name in Telugu (APPSC) or Hindi (UPSC CAPF), as students type it."""
    n = paper_no(p)
    if conf.get('te_name'):
        return f'{conf["te_name"]} {p.get("te_paper") or conf["te_paper"]} {p["year"]} ప్రశ్నపత్రం సమాధానాలతో'
    if conf.get('hi_name'):
        return f'{conf["hi_name"]} {p.get("hi_paper") or conf["hi_paper"]} {p["year"]} प्रश्न पत्र, ' + ('उत्तर सहित' if p.get('nokey') else 'उत्तर कुंजी सहित')
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
    name = conf.get('subj_te', {}).get(s['id']) if 'subj_te' in conf else SUBJ_L2[conf['l2']['code']].get(s['id'])
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
    if 'police' in e['id'] and e['cat'] == 'tg': words += ['ts police', 'tg police', 'tslprb', 'tgprb', 'si', 'constable']
    if 'police' in e['id'] and e['cat'] == 'ap': words += ['ap police', 'andhra police', 'slprb', 'apslprb', 'si', 'sub inspector', 'constable', 'pc', 'rsi', 'fireman', 'warder']
    if 'amvi' in e['id']: words += ['amvi', 'motor vehicle inspector', 'mvi', 'rto', 'transport department', 'automobile engineering', 'automobile']
    if e['id'] == 'appsc-aso': words += ['aso', 'assistant statistical officer', 'statistical officer', 'statistics', 'economics', 'ecostats', 'economics and statistics', 'des', 'mpso', 'accountancy']
    if e['id'] == 'appsc-env-engineer': words += ['aee', 'assistant environmental engineer', 'environmental engineer', 'environmental engineering', 'pollution control board', 'appcb', 'common subject', 'fluid mechanics', 'eia']
    if e['id'] == 'appsc-analyst': words += ['analyst', 'analyst grade 2', 'analyst grade ii', 'pollution control board', 'appcb', 'chemistry', 'biochemistry', 'biology', 'environmental science']
    if e['id'] == 'appsc-fro': words += ['fro', 'forest range officer', 'forest', 'forestry', 'general forestry', 'range officer', 'forest department']
    if e['id'] == 'appsc-eo': words += ['endowments', 'endowment officer', 'eo grade 3', 'eo grade iii', 'executive officer', 'temple', 'devadaya', 'dharmadaya', 'hindu philosophy']
    if 'hmwssb' in e['id']: words += ['hmwssb', 'water board', 'jalamandali', 'metro water', 'manager engineering', 'civil engineering', 'hmws', 'ece', 'electronics', 'electronics and communication', 'communication engineering']
    if 'civil-judge' in e['id']: words += ['civil judge', 'junior civil judge', 'jcj', 'judiciary', 'high court', 'llb', 'law']
    if e['cat'] == 'ap': words += ['appsc', 'andhra'] + ([f'ap group {ROMAN[m.group(1)]}'] if m else [])
    if e['id'] in MAINS_EXAMS and MAINS_KIT: words += ['mains', 'answer writing', 'tool kit', 'toolkit', 'essay']
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


HERO_NEW = ('<a class="hero-new" href="/upsc-cse/"><span>New</span> UPSC Prelims 2026 &amp; 2025 · Anthropology model answers <b aria-hidden="true">→</b></a>')   # start-page announcement pill; change with each big release


BOARD_ART = {   # line drawings for the board tiles (own artwork; no photos, no maps, no emblems)
    'upsc': '<path d="M40 34 80 15l40 19Z"/><path d="M38 34h84M42 39h76"/><path d="M50 43v26M63 43v26M76 43v26M89 43v26M102 43v26M114 43v26"/><path d="M40 71h80M35 77h90"/>',
    'ap': '<path d="M54 78h52l-4-13H58Z"/><path d="M59 65h42l-4-12H63Z"/><path d="M64 53h32l-4-11H68Z"/><path d="M69 42h22l-4-10H73Z"/><path d="M73 32h14l-3-8H76Z"/><path d="M74 24c0-5 12-5 12 0"/><path d="M80 19v-7M77 15h6"/><path d="M75 78v-7a5 5 0 0 1 10 0v7"/>',
    'tg': '<path d="M58 78V36h44v42"/><path d="M68 78V60a12 12 0 0 1 24 0v18"/><path d="M56 36h48M58 30h44"/><path d="M73 30c0-7 14-7 14 0"/><path d="M47 78V27h9v51M104 78V27h9v51"/><path d="M47 27c0-8 9-8 9 0M104 27c0-8 9-8 9 0"/><path d="M51.5 19v-5M108.5 19v-5"/><path d="M44 44h15M44 61h15M101 44h15M101 61h15"/>',
    'ssc': '<rect x="56" y="14" width="44" height="62" rx="4"/><path d="M64 28h28M64 38h28M64 48h18"/><path d="m64 61 4 4 9-9"/><path d="m104 50 16-16 5 5-16 16-7 2Z"/>',
    'rail': '<rect x="56" y="12" width="48" height="54" rx="11"/><rect x="63" y="20" width="34" height="19" rx="3"/><circle cx="68" cy="53" r="3.5"/><circle cx="92" cy="53" r="3.5"/><path d="M74 53h12"/><path d="m63 66-9 13M97 66l9 13M48 79h64M52 73h56"/>',
    'bank': '<path d="M42 34 80 15l38 19Z"/><path d="M42 34h76"/><path d="M50 39v28M64 39v28M96 39v28M110 39v28"/><path d="M40 70h80M35 77h90"/><circle cx="80" cy="52" r="10"/><path d="M76 47h9M76 51h9M79 47c5 0 5 8 0 8h-3l7 7"/>',
}
EXAM_ART = [   # header drawings on the exam tiles (own line art, 160x90; Anil 2 Nov 2026: a picture instead of a strip). No photos, maps or emblems.
    (r'police|constable|\bsi\b', '<path d="M44 52c-4-34 76-34 72 0"/><path d="M42 52h76v11H42Z"/><path d="M46 63c12 13 56 13 68 0"/><path d="M80 20l9 4v8c0 7-4 11-9 14-5-3-9-7-9-14v-8Z"/><path d="m76 31 3 3 6-6"/><path d="M50 57.5h60" opacity=".55"/>'),
    (r'capf|\bcds\b|\bnda\b|defence|afcat|army|navy', '<path d="M80 12 58 20v16c0 15 9 27 22 34 13-7 22-19 22-34V20Z"/><path d="m80 28 4 8.5 9.3 1.3-6.7 6.5 1.6 9.2L80 49.2l-8.2 4.3 1.6-9.2-6.7-6.5 9.3-1.3Z"/><path d="M50 40c-6 6-6 16 2 22M110 40c6 6 6 16-2 22"/>'),
    (r'amvi|motor vehicle', '<path d="M38 60V50l10-14h52l12 14h10v10Z"/><path d="M54 40h18v10H50ZM78 40h18l8 10H78Z"/><circle cx="56" cy="62" r="7"/><circle cx="106" cy="62" r="7"/><path d="M28 72h108"/>'),
    (r'endowment', '<path d="M54 74h52"/><path d="M60 74V48h40v26"/><path d="M56 48h48L80 28Z"/><path d="M80 28V14l12 4-12 4"/><path d="M73 74V61a7 7 0 0 1 14 0v13"/><path d="M65 55h4M91 55h4"/>'),
    (r'forest|\bfro\b|\bifos\b|\bfbo\b', '<path d="M44 72 58 48h-6l12-22 12 22h-6l14 24Z"/><path d="M84 72 96 52h-5l11-20 11 20h-5l12 20Z"/><path d="M64 72v7M102 72v7M34 79h98"/>'),
    (r'environmental engineer|env engineer', '<path d="M40 74V46l16 8V46l16 8V46l16 8v20Z"/><path d="M96 74V24h10v50"/><path d="M98 18c-4-6 2-10 8-8 4-6 14-4 14 3 6 1 6 9 0 10"/><path d="M114 52c10-12 22-12 26-10-2 12-12 20-24 16Z"/><path d="M116 58l14-10"/><path d="M30 74h104"/>'),
    (r'statistic|\baso\b|mpso', '<path d="M34 76h96"/><path d="M42 76V58h12v18M60 76V44h12v32M78 76V30h12v46M96 76V48h12v28M114 76V62h12v14"/><path d="M36 56c14 0 20-40 44-40s30 40 44 40"/>'),
    (r'analyst|chemist|drug|pharma|\blab\b', '<path d="M70 14h20M73 14v20L56 66a5 5 0 0 0 4.5 7h39a5 5 0 0 0 4.5-7L87 34V14"/><path d="M62 54h36"/><circle cx="74" cy="62" r="3"/><circle cx="86" cy="58" r="2"/><circle cx="114" cy="26" r="5"/><circle cx="126" cy="42" r="4"/><path d="m117 30 6 8"/>'),
    (r'hmwssb|water', '<path d="M80 10s18 20 18 34a18 18 0 0 1-36 0c0-14 18-34 18-34Z"/><path d="M72 46a8 8 0 0 0 8 8"/><path d="M32 74c8-5 16-5 24 0s16 5 24 0 16-5 24 0 16 5 24 0"/>'),
    (r'teacher|\btet\b|\bdsc\b|lecturer|gurukul|\btgt\b|\bpgt\b', '<path d="M80 26c-8-6-20-8-34-6v44c14-2 26 0 34 6 8-6 20-8 34-6V20c-14-2-26 0-34 6Z"/><path d="M80 26v44"/><path d="M54 32h16M54 40h16M90 32h16M90 40h16"/>'),
    (r'rail|\brrb\b|ntpc|\balp\b', None),
    (r'bank|ibps|\bsbi\b|\brbi\b|nabard|\blic\b|epfo|insurance|apfc|account|audit', '<path d="M42 34 80 15l38 19Z"/><path d="M42 34h76"/><path d="M50 39v28M64 39v28M96 39v28M110 39v28"/><path d="M40 70h80M35 77h90"/><circle cx="80" cy="52" r="10"/><path d="M76 47h9M76 51h9M79 47c5 0 5 8 0 8h-3l7 7"/>'),
    (r'health|nurs|medical|mphw|doctor', '<path d="M80 72S54 56 54 38a13 13 0 0 1 26-6 13 13 0 0 1 26 6c0 18-26 34-26 34Z"/><path d="M34 48h24l5-10 7 20 6-14 4 4h46"/>'),
    (r'prelims|csat', '<rect x="56" y="10" width="48" height="68" rx="4"/><circle cx="66" cy="24" r="3.2"/><circle cx="76" cy="24" r="3.2" fill="currentColor"/><circle cx="86" cy="24" r="3.2"/><circle cx="96" cy="24" r="3.2"/><circle cx="66" cy="37" r="3.2"/><circle cx="76" cy="37" r="3.2"/><circle cx="86" cy="37" r="3.2"/><circle cx="96" cy="37" r="3.2" fill="currentColor"/><circle cx="66" cy="50" r="3.2" fill="currentColor"/><circle cx="76" cy="50" r="3.2"/><circle cx="86" cy="50" r="3.2"/><circle cx="96" cy="50" r="3.2"/><circle cx="66" cy="63" r="3.2"/><circle cx="76" cy="63" r="3.2"/><circle cx="86" cy="63" r="3.2" fill="currentColor"/><circle cx="96" cy="63" r="3.2"/>'),
    (r'mains|civil services', '<rect x="48" y="12" width="44" height="64" rx="4"/><path d="M56 26h28M56 36h28M56 46h20"/><path d="m90 68 4-14 26-26 10 10-26 26Z"/><path d="m116 32 10 10"/>'),
    (r'ssc|cgl|chsl|\bmts\b|steno|clerk|secretariat', None),
]


def exam_art(e, cat):
    t = f'{e["id"]} {e["t"]} {e.get("n", "")}'.lower().replace('-', ' ')
    for rx, svg in EXAM_ART:
        if re.search(rx, t): return svg or BOARD_ART['rail' if 'rail' in rx else 'ssc']
    return BOARD_ART.get(cat, BOARD_ART['upsc'])   # PSC groups and posts: the board's own drawing (gopuram, Charminar, building)


BOARD_PHOTO = {   # free-licence photos from Wikimedia Commons, cropped to 640x250 WebP in src/static (Anil approved the download, 2 Nov 2026)
    'upsc': ('North Block, Delhi', 'Atulburnwal', 'CC BY-SA 3.0', 'https://commons.wikimedia.org/wiki/File:North_Block,_Delhi.jpg', 'https://creativecommons.org/licenses/by-sa/3.0/'),
    'ap': ('Tirumala gopurams', 'Vimalkalyan', 'public domain', 'https://commons.wikimedia.org/wiki/File:Tirumala_gopurams.JPG', ''),
    'tg': ('Charminar, Hyderabad', 'Craftofolio.media', 'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Charminar,_Hyderabad,_Telangana,_India.jpg', 'https://creativecommons.org/licenses/by-sa/4.0/'),
    'ssc': ('Writing an exam', 'Alison wood', 'CC BY 3.0', 'https://commons.wikimedia.org/wiki/File:Hand-writing-exam-classroom.jpg', 'https://creativecommons.org/licenses/by/3.0/'),
    'rail': ('Vijayawada–Chennai Vande Bharat Express', 'Ravi Dwivedi', 'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Vijayawada_-_Chennai_Central_Vande_Bharat_Express.jpg', 'https://creativecommons.org/licenses/by-sa/4.0/'),
    'bank': ('Rupee coins', 'Ravi Kumar', 'CC BY 3.0', 'https://commons.wikimedia.org/wiki/File:Coin_(127690727).jpeg', 'https://creativecommons.org/licenses/by/3.0/'),
    # other states' PSCs, "Coming soon" boards for later (Anil, 2 Nov 2026: "add one or more state photos, where state PSC exams are going on ... in future we will built them")
    'tn': ('Brihadeeswarar Temple, Thanjavur', 'Bernard Gagnon', 'CC BY-SA 3.0', 'https://commons.wikimedia.org/wiki/File:Brihadeeswarar_Temple_02.jpg', 'https://creativecommons.org/licenses/by-sa/3.0/'),
    'ka': ('Vidhana Soudha, Bengaluru', 'DeepanjanGhosh', 'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Vidhana_Soudha_LE.jpg', 'https://creativecommons.org/licenses/by-sa/4.0/'),
    'kl': ('Kerala backwaters', 'Vyacheslav Argenberg', 'CC BY 4.0', 'https://commons.wikimedia.org/wiki/File:Kerala_backwaters,_Houseboats,_India.jpg', 'https://creativecommons.org/licenses/by/4.0/'),
    'mh': ('Gateway of India, Mumbai', 'Joe Ravi', 'CC BY-SA 3.0', 'https://commons.wikimedia.org/wiki/File:Gateway_Of_India.jpg', 'https://creativecommons.org/licenses/by-sa/3.0/'),
    'up': ('Taj Mahal, Agra', 'Yann, edited by King of Hearts', 'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Taj_Mahal,_Agra,_India_edit2.jpg', 'https://creativecommons.org/licenses/by-sa/4.0/'),
    'br': ('Bihar Legislature, Patna', 'Innocentbunny', 'CC BY-SA 3.0', 'https://commons.wikimedia.org/wiki/File:Bihar_Legislature_Building.jpg', 'https://creativecommons.org/licenses/by-sa/3.0/'),
}


def photo_credits(ids):
    bits = []
    for k in ids:
        if k not in BOARD_PHOTO: continue
        t, a, lic, url, lurl = BOARD_PHOTO[k]
        bits.append(f'<a href="{url}" target="_blank" rel="noopener">{esc(t)}</a> by {esc(a)} ('
                    + (f'<a href="{lurl}" target="_blank" rel="noopener">{lic}</a>' if lurl else lic) + ')')
    return f'<p class="ph-credit">Photos (cropped) via Wikimedia Commons: {" · ".join(bits)}.</p>' if bits else ''


CCL = {'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0/', 'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
       'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0/', 'CC0': 'https://creativecommons.org/publicdomain/zero/1.0/',
       'GODL-India': 'https://data.gov.in/sites/default/files/Gazette_Notification_OGDL.pdf', 'FAL': 'https://artlibre.org/licence/lal/en/'}
_CW = 'https://commons.wikimedia.org/wiki/File:'
EXAM_PHOTO = {   # one free-licence photo per live exam (Wikimedia Commons; Anil approved, 2 Nov 2026): src/static/ex-<id>-t.webp (tile) and -h.webp (exam page banner)
    'upsc-cse': ('New Parliament building', 'Ministry of Parliamentary Affairs', 'GODL-India', _CW + 'Glimpses_of_the_new_Parliament_Building,_in_New_Delhi_(2).jpg'),
    'upsc-prelims': ('India Gate, New Delhi', 'Yann', 'CC BY-SA 3.0', _CW + 'India_Gate,_New_Delhi.jpg'),
    'upsc-epfo': ('Shastri Bhawan, New Delhi', 'Pinakpani', 'CC BY-SA 4.0', _CW + 'Shastri_Bhawan,_a_Government_buildings_in_New_Delhi_10.jpg'),
    'upsc-capf': ('Nathu La, Sikkim', 'Nitin Ticku', 'CC BY-SA 3.0', _CW + 'Nathu_La_by_Nitin_Ticku.JPG'),
    'appsc-group-1': ('Andhra Pradesh Legislative Assembly', 'Kdslk', 'CC0', _CW + 'A.P_Legislative_Assembly.jpg'),
    'appsc-group-2': ('Prakasam Barrage, Vijayawada', 'Deensonu', 'CC BY-SA 4.0', _CW + 'Prakasam_Barrage,_Vijayawada_2016_(7).jpg'),
    'appsc-fro': ('Nallamala forest', 'Dubbala Divya', 'CC BY-SA 4.0', _CW + 'Nallamala_forest_view_01.jpg'),
    'appsc-amvi': ('NH 16 near Eluru', 'iMahesh', 'CC BY-SA 4.0', _CW + 'National_Highway_16_near_Bhimadole,_Eluru_(02).jpg'),
    'appsc-eo': ('Lepakshi Nandi', 'Rahmanuddin', 'CC BY-SA 4.0', _CW + 'Lepakshi_nandi_15.JPG'),
    'appsc-analyst': ('Chemical test tubes', 'Vis M', 'CC BY-SA 4.0', _CW + 'Chemical_test_tubes_2013.jpg'),
    'ap-police-si': ('Police station, AP Secretariat', 'IM3847', 'CC BY-SA 4.0', _CW + 'Police_station_at_Andhra_Pradesh_Secretariat.jpg'),
    'ap-police-constable': ('Thullur police station, Mandadam', 'IM3847', 'CC BY-SA 4.0', _CW + 'Mandadam_Police_station.jpg'),
    'tgpsc-amvi': ('Outer Ring Road, Hyderabad', 'iMahesh', 'CC BY-SA 4.0', _CW + 'Long_Exposure_shot_of_Nehru_Outer_ring_road_towards_Gachibowli.jpg'),
    'tgpsc-hmwssb-manager': ('Osman Sagar, Hyderabad', 'Swaroop', 'CC BY-SA 4.0', _CW + 'Osman_Sagar_lake_near_Hyderabad.jpg'),
    'ts-police-si': ('James Street police station, Hyderabad', 'adbh266', 'CC BY-SA 4.0', _CW + 'James_Street_police_station,_Hyderabad.jpg'),
    'ts-police-constable': ('Chikkadpally police station, Hyderabad', 'Adbh266', 'CC BY-SA 4.0', _CW + 'Chikkadpally_police_station.jpg'),
    'ssc-cgl': ('Shastri Bhawan, New Delhi', 'Pinakpani', 'CC BY-SA 4.0', _CW + 'Shastri_Bhawan,_a_Government_buildings_in_New_Delhi_02.jpg'),
}


def exam_photo(eid, kind='t'):
    return f'/ex-{eid}-{kind}.webp' if eid in EXAM_PHOTO and os.path.exists(os.path.join(SRC, 'static', f'ex-{eid}-{kind}.webp')) else ''


def photo_credit(eid, prefix='Photo: '):
    t, a, lic, url = EXAM_PHOTO[eid]
    return f'{prefix}<a href="{url}" target="_blank" rel="noopener">{esc(t)}</a>, {esc(a)}, <a href="{CCL[lic]}" target="_blank" rel="noopener license">{lic}</a>' if lic != 'public domain' else f'{prefix}<a href="{url}" target="_blank" rel="noopener">{esc(t)}</a>, {esc(a)}, public domain'


# The site's languages in one list (Anil, 2 Nov 2026: "update them...as new languages are added"): (code, own name, in Hindi, in Telugu, live).
# Live ones are named in the hero line, the badge, the counts and the score card; the others show as "coming soon" (the "+N" chip in the
# language switcher, the badge, the figures). A language goes live only when questions exist in it; the switcher then needs its own button.
SITE_LANGS = [('en', 'English', 'अंग्रेज़ी', 'ఇంగ్లీష్', True), ('te', 'తెలుగు', 'तेलुगु', 'తెలుగు', True), ('hi', 'हिंदी', 'हिंदी', 'హిందీ', True),
              ('ta', 'தமிழ்', 'तमिल', 'తమిళం', False), ('kn', 'ಕನ್ನಡ', 'कन्नड़', 'కన్నడ', False), ('ml', 'മലയാളം', 'मलयालम', 'మలయాళం', False),
              ('mr', 'मराठी', 'मराठी', 'మరాఠీ', False)]


def lang_fills():
    live = [x[1] for x in SITE_LANGS if x[4]]; soon = [x[1] for x in SITE_LANGS if not x[4]]
    and_ = ', '.join(live[:-1]) + ' and ' + live[-1] if len(live) > 1 else live[0]
    js = json.dumps([dict(c=c, self=n, hi=h, te=te_, live=lv) for c, n, h, te_, lv in SITE_LANGS], ensure_ascii=False)
    chip = (f'      <button type="button" class="lang-soon" data-act="langsoon" title="Coming soon: {esc(", ".join(soon))}" '
            f'aria-label="More languages coming soon: {esc(", ".join(soon))}">+{len(soon)}</button>\n') if soon else ''
    return {'{{SITE_LANGS}}': js, '{{LANGS_EN}}': and_, '{{LANGS_DOT}}': ' · '.join(live), '{{NLANGS}}': str(len(live)),
            '{{LANGS_LIST}}': ', '.join(live), '{{LANGS_SOON_DOT}}': ' · '.join(soon), '{{LANGS_SOON_LIST}}': ', '.join(soon), '{{LANG_SOON_BTN}}': chip}


NAV_FUND = ('      <a class="nav-fund" href="/funders.html" title="Fund this project" data-hubonly><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
            '<path d="M12 21s-7.5-4.6-9.6-9.2C.9 8.5 3 5 6.4 5c2 0 3.4 1.1 4.1 2.3h3C14.2 6.1 15.6 5 17.6 5 21 5 23.1 8.5 21.6 11.8 19.5 16.4 12 21 12 21Z"/></svg>'
            '<span>Fund<span class="nf-x"> this project</span></span></a>\n')   # Anil, 2 Nov 2026: "add fund the project...here" (start page top bar)
BOARD_ORDER = ['upsc', 'ap', 'tg', 'ssc', 'rail', 'bank', 'tn', 'ka', 'kl', 'mh', 'up', 'br']   # Anil, 1 Nov 2026: boards first (UPSC, APPSC, TGPSC, SSC, Railways, Banking …)


def hub_html(catalog, counts, grand):
    """Start page exam list (Anil, 1 Nov 2026: "too clumsy ... one page prior with UPSC, APPSC, TGPSC, Railway, Banking, SSC tiles").
    Board tiles first (live exams and questions on each), a row of popular exams and the student's recent exams; tapping a board
    shows only its exams (live first, upcoming folded). Search still finds any exam on the list. All exam tiles stay in the HTML."""
    cats = sorted(catalog['cats'], key=lambda c: (not any(e.get('live') for e in catalog['exams'] if e['cat'] == c['id']),
                                                   BOARD_ORDER.index(c['id']) if c['id'] in BOARD_ORDER else 99))
    boards, secs = [], []
    for c in cats:
        ex = [e for e in catalog['exams'] if e['cat'] == c['id']]
        lv = sorted([e for e in ex if e.get('live')], key=lambda e: -counts.get(e['id'], 0))
        nq = sum(counts.get(e['id'], 0) for e in lv)
        te = f'<span class="bd-te" lang="te">{esc(c["te"])}</span>' if c.get('te') else ''
        pills = ''.join(f'<span>{esc(e["t"])}</span>' for e in lv[:4]) + (f'<span class="more">+{len(lv) - 4} more</span>' if len(lv) > 4 else '')
        art = BOARD_ART.get(c['id'], BOARD_ART['ssc'])
        badge = f'<span class="bd-badge"><i></i>{len(lv)} exam{"s" if len(lv) != 1 else ""} live</span>' if lv else '<span class="bd-badge bd-soon">Coming soon</span>'
        foot = f'{nq:,} questions' if lv else f'{len(ex)} exams listed'
        boards.append(f'<button type="button" class="card board b-{c["id"]}{"" if lv else " soon"}" data-act="excat" data-cat="{c["id"]}" title="{esc(c["desc"])}">'
                      f'<span class="bd-art{" has-ph" if c["id"] in BOARD_PHOTO and os.path.exists(os.path.join(SRC, "static", "board-" + c["id"] + ".webp")) else ""}">'
                      + (f'<img class="bd-ph" src="/board-{c["id"]}.webp" alt="" width="640" height="250" loading="lazy" decoding="async">' if c['id'] in BOARD_PHOTO and os.path.exists(os.path.join(SRC, 'static', f'board-{c["id"]}.webp')) else '')
                      + f'<svg viewBox="0 0 160 90" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{art}</svg>{badge}</span>'
                      f'<span class="bd-body"><span class="bd-n">{esc(c["name"])}</span>{te}'
                      + (f'<span class="bd-pills">{pills}</span>' if pills else f'<span class="bd-d">{esc(c["desc"])}</span>')
                      + f'<span class="bd-ft"><span>{foot}</span><span class="bd-go">{"Open" if lv else "See list"} →</span></span></span></button>')
        tiles = {True: [], False: []}
        for e in lv + [e for e in ex if not e.get('live')]:
            live = bool(e.get('live'))
            href = live_href(e) if live else '#exam/' + e['id']
            status = f'Live · {counts.get(e["id"], 0):,} questions' if live else 'Upcoming'
            sub = f'<span class="ex-n">{esc(e["n"])}</span>' if e.get('n') else ''
            if live and e['id'] in MAINS_EXAMS and MAINS_KIT: sub += '<span class="ex-x">Prelims + Mains PYQs with model answers</span>'
            tiles[live].append(f'<a class="card exam x-{c["id"]}{" live" if live else ""}" href="{href}" data-cat="{c["id"]}" data-id="{e["id"]}" data-s="{esc(exam_terms(e, c))}">'
                               f'<span class="ex-art{" has-ph" if live and exam_photo(e["id"]) else ""}" aria-hidden="true">'
                               + (f'<img class="ex-ph" src="{exam_photo(e["id"])}" alt="" width="480" height="180" loading="lazy" decoding="async">' if live and exam_photo(e['id']) else '')
                               + f'<svg viewBox="0 0 160 90" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{exam_art(e, c["id"])}</svg></span>'
                               f'<span class="ex-body"><span class="ex-b">{esc(e["b"])}</span><span class="ex-t">{nw(e["t"])}</span>{sub}<span class="ex-st" data-n="{counts.get(e["id"], 0) if live else ""}">{status}</span></span></a>')
        upc = (f'<details class="upc"{"" if lv else " open"}><summary>Upcoming exams in {esc(c["name"])} ({len(tiles[False])}) · being added one by one</summary>'
               f'<div class="exams">{"".join(tiles[False])}</div></details>' if tiles[False] else '')
        secs.append(f'<section class="exam-cat" data-cat="{c["id"]}"><div class="section-title"><h2>{esc(c["name"])}{" <span class=te-sub lang=te>" + esc(c["te"]) + "</span>" if c.get("te") else ""}</h2>'
                    f'<span class="muted" style="font-size:14px">{esc(c["desc"])}</span></div>'
                    + (f'<div class="exams">{"".join(tiles[True])}</div>' if tiles[True] else '') + upc + '</section>')
    live_all = sorted([e for e in catalog['exams'] if e.get('live')], key=lambda e: -counts.get(e['id'], 0))
    pop = ''.join(f'<a class="chip pop" href="{live_href(e)}" data-id="{e["id"]}">{esc(e["b"])} {esc(e["t"])}</a>' for e in live_all[:8])
    search = ('<label class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="color:var(--muted)">'
              '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4" stroke-linecap="round"/></svg>'
              '<input id="examSearch" type="search" placeholder="Search an exam, e.g. Group-II, CGL, NDA, Police SI" aria-label="Search exams" autocomplete="off"></label>')
    return (f'<div class="hub-tools">{search}</div>'
            f'<div id="hubRecent" class="hub-row" hidden><span class="hub-k" data-i18n="contT">Continue where you left off</span><div class="chips" id="hubRecentL"></div></div>'
            f'<div id="hubHome"><div class="boards" role="list">{"".join(boards)}</div>'
            f'<div class="hub-row"><span class="hub-k" data-i18n="popT">Popular exams</span><div class="chips">{pop}</div></div>'
            + photo_credits([c['id'] for c in cats]) + '</div>'
            f'<div id="hubBack" hidden><button type="button" class="btn btn-secondary btn-sm" data-act="excat" data-cat="all" data-i18n="allB">← All exam boards</button></div>'
            f'<p class="muted" id="hubCount" style="font-size:14px"></p>'
            f'<div id="hubCats">{"".join(secs)}</div>'
            + (f'<p class="ph-credit" id="exCredits" hidden>Exam photos (cropped) via Wikimedia Commons: '
               + ' · '.join(photo_credit(e['id'], '') for e in catalog['exams'] if e.get('live') and exam_photo(e['id'])) + '.</p>')
            + f'<div class="card empty" id="hubEmpty" hidden><h3 data-i18n="emptyT">No exam matches your search</h3>'
            f'<p data-i18n="emptyP">Tell Anil which exam you are preparing for, and it will be added to the list.</p>'
            f'<div class="row" style="justify-content:center"><a class="btn btn-primary" id="hubAsk" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener" data-i18n="ask">Ask on WhatsApp</a></div></div>'
            + p5_card('hubP5'))


def p5_card(el_id):
    """Shown when a student searches for Paper V: the Group-1 Mains Paper V book is not on the site, so they message Anil."""
    if not MAINS_KIT: return ''
    from urllib.parse import quote
    text = f'Hi Anil sir, I need the APPSC Group-1 Mains Paper V ({MAINS_P5["name"]}) Answer Writing Tool Kit.'
    return (f'<div class="card p5-card" id="{el_id}" hidden><p class="eyebrow">APPSC Group-1 Mains · Paper V</p>'
            f'<h3>Looking for Paper V ({esc(MAINS_P5["name"])})?</h3>'
            f'<p>All 90 Paper V previous questions of 2020, 2023 and 2025 are on the site, each with a free model answer. '
            f'The Paper V tool kit (PDF) is not on the website: message Anil on WhatsApp and he will help you get it.</p>'
            f'<div class="row"><a class="btn btn-primary" href="/appsc-group-1/mains-pyqs/2025-paper-5.html">Paper V questions with answers</a>'
            f'<a class="btn btn-secondary" href="https://wa.me/{WHATSAPP}?text={quote(text)}" target="_blank" rel="noopener">Message Anil on WhatsApp</a>'
            f'<a class="btn btn-secondary" href="/appsc-group-1/mains/">Papers I–IV tool kit</a></div></div>')


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
    fmt = 'Options by Learn with Anil' if p.get('own') else 'All 4 options' if p['fmt'] == 'mcq' else 'Answer-only key'
    cls = 'good' if p['fmt'] == 'mcq' else 'warn'
    return (f'<article class="card paper"><span class="yr">{esc(p["held"])} · {esc(p["notif"])}</span><h3>{esc(p.get("kw") or p["title"])}</h3>'
            f'<p>{esc(p["blurb"])}</p><div class="meta"><span class="pill blue">{p["count"]} questions</span><span class="pill {cls}">{fmt}</span></div>'
            f'<div class="acts"><button class="btn btn-primary btn-sm" type="button" data-act="paperpractice" data-paper="{p["id"]}">Practise</button>'
            f'<a class="btn btn-ghost btn-sm" href="papers/{p["slug"]}.html">Read with answers</a>'
            + (f'<a class="btn btn-ghost btn-sm" href="{p["pdf"]}" download>PDF</a>' if p.get('pdf') else '') + '</div></article>')


def FAQ(total, npapers):
    return [
      ('Where can I get APPSC Group 2 previous year question papers with answers?',
       f'This site has {total} questions from {npapers} APPSC Group-II papers: the Screening Test 2024, Mains 2025 Paper I and Paper II, and the 2019 Screening and Mains papers. Every answer is taken from APPSC\'s official final key, and each question has a short explanation. You can practise each paper as a quiz or a timed test, with answers and explanations with one ₹45 All-in-One Pass for every exam.'),
      ('What does it cost, and what does the ₹45 All-in-One Pass cover?',
       'One plan: the ₹45 All-in-One Pass, for 12 months. It opens everything on the website: every previous paper of every exam, including exams added later, with answers, explanations, quizzes, timed tests and all study tools, plus every mock test series (Mission Khaki, Mission CGL, Bahubali and the ones still to come) and the study books. Without a plan you can see the question of the day, the correct answer to every question on the paper pages, and the explanations of the first 10 questions of each paper.'),
      ('Are the APPSC Group 2 previous papers available in Telugu?',
       'Yes. Almost every question has APPSC\'s own Telugu text, as printed in the question booklet. Tap తెలుగు at the top of the page to practise in Telugu.'),
      ('Is there a APPSC Group 2 mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects, and pick Timed test: you get a mock test made of real APPSC Group 2 Prelims and Mains questions, with your score and a topic-wise analysis at the end. Practice mode works like practice bits, one question at a time with the answer and explanation.'),
      ('What is the APPSC Group 2 exam pattern?',
       'Under Notification 11/2023, the Screening Test is one objective paper of 150 questions for 150 marks in 150 minutes, with 30 marks each for Indian History, Geography, Indian Society, Current Affairs and Mental Ability. The Mains has two objective papers of 150 marks each: Paper I covers the Social and Cultural History of Andhra Pradesh and the Indian Constitution, and Paper II covers the Indian and AP Economy and Science and Technology.'),
      ('Are the answers on this site official?',
       'Yes. The answers come from the final keys published by APPSC. Questions that APPSC deleted are left out, and where the final key accepted two options, both are shown as correct. The explanations are written by Learn with Anil.'),
      ('Where do the options of the 2019 papers come from?',
       'APPSC\'s 2019 final keys print each question with only the correct answer, and APPSC has not published the original options. In the All-in-One Pass, the correct option of each 2019 question is APPSC\'s official answer and the other three options are written by Learn with Anil; every such question is labelled. The 2024 and 2025 papers show APPSC\'s own four options.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass opens the previous papers of every exam for 12 months. There is no password. Your scores are saved with Learn with Anil so Anil can guide you, and your practice attempts, mistakes notebook and bookmarks stay on your own device.'),
    ]


def FAQ_G1(total, npapers):
    return [
      ('Where can I get APPSC Group 1 previous year question papers with answers?',
       f'This page has {total} questions from {npapers} APPSC Group-I Prelims papers: Paper I (General Studies) and Paper II (General Aptitude) of the 2024 exam, and the 2023 and 2019 Prelims papers. Every answer is taken from APPSC\'s official final key, and each question has a short explanation. You can practise each paper as a quiz or a timed test, with answers and explanations with one ₹45 All-in-One Pass for every exam.'),
      ('What does it cost, and what does the ₹45 All-in-One Pass cover?',
       'One plan: the ₹45 All-in-One Pass, for 12 months. It opens everything on the website: every previous paper of every exam, including exams added later, with answers, explanations, quizzes, timed tests and all study tools, plus every mock test series (Mission Khaki, Mission CGL, Bahubali and the ones still to come) and the study books. Without a plan you can see the question of the day, the correct answer to every question on the paper pages, and the explanations of the first 10 questions of each paper.'),
      ('Where is the APPSC Group 1 Prelims 2024 answer key?',
       'Each question on this site shows the answer from APPSC\'s final key, for Paper 1 (General Studies) and Paper 2 (General Aptitude) of the 2024 Prelims, and for the 2023 and 2019 Prelims. Open a paper to see every question with its answer.'),
      ('Is there a APPSC Group 1 mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects, and pick Timed test: you get a mock test made of real APPSC Group 1 Prelims questions, in English or Telugu, with your score and a topic-wise analysis at the end.'),
      ('What is the APPSC Group 1 Prelims exam pattern?',
       'The Preliminary Examination has two objective papers on the same day: Paper I General Studies (History and Culture; Constitution, Polity, Social Justice and International Relations; Indian and AP Economy and Planning; Geography) and Paper II General Aptitude (General Mental Ability, Administrative and Psychological Abilities; Science and Technology; Current Events). Each paper has 120 questions for 120 marks in 120 minutes, and one-third of the marks of a question is deducted for a wrong answer. Prelims marks are used only to shortlist candidates for the Mains.'),
      ('Are the answers on this site official?',
       'Yes. The answers come from the final keys published by APPSC. Questions that APPSC deleted are left out, and where the final key accepted two options, both are shown as correct. The explanations are written by Learn with Anil.'),
      ('Where do the options of the 2023 and 2019 papers come from?',
       'APPSC\'s 2023 and 2019 final keys print each question with only the correct answer, and APPSC has not published the original options. In the All-in-One Pass, the correct option of each 2023 and 2019 question is APPSC\'s official answer and the other three options are written by Learn with Anil; every such question is labelled. The 2024 papers show APPSC\'s own four options.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass opens the previous papers of every exam for 12 months. There is no password. Your scores are saved with Learn with Anil so Anil can guide you, and your practice attempts, mistakes notebook and bookmarks stay on your own device.'),
    ]


def FAQ_CAPF(total, npapers):
    return [
      ('Where can I get UPSC CAPF AC previous year question papers with answers?',
       f'This page has {total} questions from {npapers} UPSC CAPF (Assistant Commandants) Paper I papers, General Ability and Intelligence (2024, 2025 and 2026), in English and Hindi as printed in the official question booklets. Every question has a short explanation. You can practise each paper as a quiz or a timed test, with answers and explanations with one ₹45 All-in-One Pass for every exam.'),
      ('What does it cost, and what does the ₹45 All-in-One Pass cover?',
       'One plan: the ₹45 All-in-One Pass, for 12 months. It opens everything on the website: every previous paper of every exam, including exams added later, with answers, explanations, quizzes, timed tests and all study tools, plus every mock test series (Mission Khaki, Mission CGL, Bahubali and the ones still to come) and the study books. Without a plan you can see the question of the day, the correct answer to every question on the paper pages, and the explanations of the first 10 questions of each paper.'),
      ('Where is the CAPF AC 2026 answer key?',
       'Every 2026 question on this site shows the answer from UPSC\'s provisional answer key (Series A booklet), published three days after the exam on 19 July 2026. UPSC\'s final key can differ for a few questions.'),
      ('Is there a CAPF AC mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects such as General Science, Current Affairs or Polity, and pick Timed test: you get a mock test made of real CAPF AC Paper 1 questions, in English or Hindi, with your score and a topic-wise analysis.'),
      ('What is the UPSC CAPF AC exam pattern?',
       'The written exam has two papers on the same day. Paper I, General Ability and Intelligence, is objective, carries 250 marks and lasts two hours; recent papers have had 125 questions, in English and Hindi. It covers General Mental Ability, General Science, Current Events of national and international importance, Indian Polity and Economy, History of India, and Indian and World Geography. A wrong answer costs one-third of the marks for that question. Paper II, General Studies, Essay and Comprehension, is descriptive and carries 200 marks. Candidates who qualify take physical and medical standards tests and then an interview.'),
      ('Are the answers on this site official?',
       'For 2024 they come from UPSC\'s official answer key. For 2026 they come from the provisional key UPSC published after the exam; the final key can differ for a few questions. UPSC has not published a key for 2025 that we could find, so those answers were compiled from three published coaching keys and checked one by one; where a source reports a different answer, the explanation says so. Questions UPSC dropped are left out. The explanations are written by Learn with Anil.'),
      ('Is the CAPF AC previous year question paper available in Hindi?',
       'Yes. Tap हिंदी at the top of the page to see every question and option in Hindi, exactly as printed in UPSC\'s booklet. Tap EN to switch back.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass opens the previous papers of every exam for 12 months. There is no password. Your scores are saved with Learn with Anil so Anil can guide you, and your practice attempts, mistakes notebook and bookmarks stay on your own device.'),
    ]


def FAQ_EPFO(total, npapers):
    E = epfo_text(); eo = E['eo']   # are the EO/AO papers on the site?
    return [
      (('Where can I get UPSC EPFO previous year question papers with answers?' if eo else
        'Where can I get the UPSC EPFO APFC previous year question paper with answers?'),
       (f'This page has {total} questions from {npapers} UPSC recruitment tests for EPFO: {E["tests"]}. ' if E['many'] else
        f'This page has {total} questions from {npapers} UPSC recruitment tests for EPFO: Assistant Provident Fund Commissioner (APFC), held on 2 July 2023, and Enforcement Officer / Accounts Officer (EO/AO), held on {E["eodates"]}. ' if eo else
        f'This page has {total} questions from the UPSC recruitment test for Assistant Provident Fund Commissioner (APFC) in EPFO, held on 2 July 2023. ')
       + ('Every question is in English and Hindi as printed in the booklet (Series A), apart from the General English part. Answers are from UPSC\'s official answer keys where UPSC has published one (see the next answer), and every question has a short explanation. ' if E['many'] else
          'Every question is in English and Hindi as printed in the official booklet (Series A), apart from the General English part. Every answer is taken from UPSC\'s official answer key and every question has a short explanation. ')
       + 'You can practise each paper question by question, subject-wise or as a timed test with one ₹45 All-in-One Pass for every exam.'),
      ('Are the answers official?',
       ('For most papers, yes. ' if E['nokey'] else '') + (epfo_keynote(E) + ' ' if E['many'] else '') + ('' if E['many'] else
       ('Yes. They come from UPSC\'s official answer keys for Series A, published on upsc.gov.in after each recruitment was completed. UPSC dropped no question in the 2023 papers'
        + ('; in the 2021 EO/AO paper it dropped Q71, which is left out. ' if E['eo21'] else '. ') if eo else
        'Yes. They come from UPSC\'s official answer key for Series A, published on upsc.gov.in in August 2024 after the recruitment was completed. UPSC dropped no question in this paper. '))
       + 'Where a keyed answer is debatable, the explanation says "(Official key; some sources differ.)"'
       + ('; where one of our own answers is, it says "(No official key; some sources differ.)"' if E['nokey'] else '')
       + '. The explanations are written by Learn with Anil.'),
      ('What is the UPSC EPFO exam pattern?' if eo else 'What is the UPSC EPFO APFC exam pattern?',
       'The recruitment test is one objective paper of 120 questions for 300 marks in two hours, in English and Hindi (the General English part in English only). '
       + ('(The 2017 EO/AO paper had the same 120 questions for 100 marks.) ' if any(n[2] == 'eoao17' for n in E['nokey']) else '')
       + 'A wrong answer costs one-third of the marks for that question. '
       + ('Candidates who qualify for APFC or EO/AO are called for an interview; the test and the interview are weighted 75:25. ' if E['pa'] else
          'Candidates who qualify are called for an interview; the test and the interview are weighted 75:25. ')
       + 
       'The syllabus covers General English, Indian freedom struggle, history and culture, current events and developmental issues, Indian polity and economy, general accounting principles, '
       'industrial relations and labour laws, social security in India, general science and computer applications, and general mental ability and quantitative aptitude. '
       + ('APFC and EO/AO have had separate papers on the same syllabus; in 2025 UPSC set one common paper for both posts.' if eo else '')),
      ('Which labour law questions come in the EPFO exams?' if eo else 'Which labour law questions come in the APFC exam?',
       ('The papers ask about the EPF & MP Act, the Employees\' Compensation Act, the ESI Act, the Industrial Disputes Act, the Trade Unions Act, the Factories Act, the Mines Act, the Payment of Wages, Payment of Bonus and Minimum Wages Acts, '
        'the Contract Labour and Standing Orders Acts, the Building and Other Construction Workers Act, and ILO conventions. ' if eo else
        'The 2023 paper had 18 questions on labour laws and social security: the EPF & MP Act, the Employees\' Compensation Act, the ESI Act, the Industrial Disputes Act, the Trade Unions Act, '
        'the Factories Act, the Mines Act, the Payment of Wages and Payment of Bonus Acts, the Building and Other Construction Workers Act, and ILO core conventions. ')
       + 'The four Labour Codes, in force since 21 November 2025, have since replaced most of these Acts; the explanations say where the law has changed after the exam.'),
      ('Is the EPFO question paper available in Hindi?' if eo else 'Is the APFC question paper available in Hindi?',
       'Yes. Tap हिंदी at the top of the page to see every question and option of Part B in Hindi, exactly as printed in UPSC\'s booklet, with the explanation in Hindi. Part A (General English) is in English only.'),
      ('Is there an EPFO mock test?' if eo else 'Is there an EPFO APFC mock test?',
       ('Yes. Open the mock test page and take a real APFC, EO/AO or PA paper with a timer, ' if E['pa'] else
        'Yes. Open the mock test page and take a real APFC or EO/AO paper with a timer, ' if eo else 'Yes. Open the mock test page and take the real 2023 paper with a timer, ')
       + 'or tap Create a quiz to choose subjects such as Labour Laws, Social Security or Accounting. You get your score, the ' + ('' if E['nokey'] else 'official ') + 'answer and an explanation for every question.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass opens the previous papers of every exam for 12 months. There is no password.'),
    ]


def FAQ_CGL(total, npapers):
    G = cgl_text()
    return [
      ('Where can I get SSC CGL previous year question papers with answers?',
       f'This page has {total} questions from {G["what"]} of the SSC Combined Graduate Level Examination ({G["years"]}). Each is SSC\'s own question paper as candidates print it from SSC\'s portal, '
       'with the answer SSC marked as correct, and every question has a short explanation. Practise a whole shift as a timed mock test, or by subject and topic.'),
      ('Are the answers official?',
       'Yes. Every answer is the one SSC marked as correct on the candidate\'s response sheet. The Tier-I sheets come from the answer-key stage, so SSC\'s final key can differ for a few questions; where a marked answer looks debatable, the explanation says "(SSC key; some sources differ.)". The explanations are written by Learn with Anil.'),
      ('What is the SSC CGL exam pattern?',
       'Tier-I has 100 questions (General Intelligence & Reasoning, General Awareness, Quantitative Aptitude and English Comprehension, 25 each) for 200 marks in 60 minutes, with 0.50 marks cut for a wrong answer. '
       'Tier-II Paper I has Mathematical Abilities (30) and Reasoning & General Intelligence (30), English Language & Comprehension (45) and General Awareness (25), and Computer Knowledge (20, qualifying), '
       'each question worth 3 marks with 1 mark cut for a wrong answer, plus a data-entry speed test. Tier-I is a qualifying screening; the merit list is made from Tier-II.'),
      ('Why are there so many SSC CGL papers for one year?',
       'SSC holds Tier-I over many days and several shifts a day, and every shift gets a different question paper. This page gives whole shifts, so you can take each one as a real 60-minute test.'),
      ('Is the SSC CGL question paper available in Hindi?',
       'Yes. Tap हिंदी at the top of the page to see every question and option in Hindi, as printed in SSC\'s paper, with the explanation in Hindi. English Comprehension questions are in English only.'),
      ('Is there an SSC CGL mock test?',
       'Yes. Every shift paper here can be taken as a timed mock test with the real time limit. Mission CGL, Learn with Anil\'s series of new full-length Tier-I and Tier-II mock tests in English and Hindi, is included in the same ₹45 All-in-One Pass.'),
    ]


def FAQ_HM(total, npapers):
    return [
      ('Where can I get TGPSC HMWSSB Manager (Engineering) previous question papers with answers?',
       f'This page has {total} questions from the TSPSC Manager (Engineering) written test for HMWSSB, Notification 13/2015, held on 1 November 2015: '
       'Paper 1 General Studies in English and Telugu, and Paper 2 in Civil Engineering and in Electronics & Communication Engineering (ECE). Every answer is taken from TSPSC\'s final key (Series A), and each question has a short explanation. '
       'You can practise each paper as a quiz or a timed mock test, with answers and explanations with one ₹45 All-in-One Pass for every exam.'),
      ('What is the TGPSC HMWSSB Manager (Engineering) 2026 exam pattern?',
       'Two objective papers: Paper 1 General Studies and General Abilities (150 questions, 150 marks, in English and Telugu) and Paper 2 in the candidate\'s engineering '
       'subject (150 questions, 300 marks, in English), 450 marks in all. Notification 04/2026 has 130 posts, mostly Civil, and the exam is tentatively in December 2026; confirm dates on tgpsc.gov.in.'),
      ('Are the HMWSSB Manager General Studies questions available in Telugu?',
       'Yes. Paper 1 (General Studies) is printed in English and Telugu, apart from its English-language questions, and every question is here exactly as printed. Tap తెలుగు at the top of the page to practise in Telugu. The Paper 2 subject papers (Civil Engineering and ECE) are printed in English only.'),
      ('Is there a HMWSSB Manager mock test?',
       'Yes. Open the mock test page and take a real 2015 paper with a timer, or tap Create a quiz to choose subjects such as Environmental Engineering, Fluid Mechanics or Telangana History. You get your score, the official answer and an explanation for every question.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass opens the previous papers of every exam for 12 months. There is no password.'),
      ('Which questions are left out?',
       'TSPSC\'s final key gave the mark to every candidate for five questions of Paper 2 Civil (Q3, 37, 64, 95 and 128 in Series A) and five of Paper 2 ECE (Q38, 47, 53, 123 and 134); they are left out. The Mechanical, Electrical and CSE papers are not on the site yet.'),
    ]



def FAQ_AMVI(state):
    ap = state == 'AP'
    name = 'APPSC AMVI' if ap else 'TGPSC AMVI'
    def faq(total, npapers):
        if ap:
            where = (f'This page has {total:,} questions from {npapers} APPSC Assistant Motor Vehicle Inspector papers: Paper I General Studies & Mental Ability and Paper II Automobile Engineering '
                     'of the 2026 (Notification 21/2025, held 27 and 28 January 2026), 2023 (Notification 12/2022, computer-based test of 6 October 2023) and 2019 (Notification 11/2018) exams. '
                     'Every answer is taken from APPSC\'s final key, and each question has a short explanation. You can practise each paper as a quiz or a timed mock test, with answers and explanations, with one ₹45 All-in-One Pass for every exam.')
        else:
            where = (f'This page has {total:,} questions from the TSPSC (now TGPSC) Assistant Motor Vehicles Inspector computer-based test of 28 June 2023 (Notification 31/2022): Paper I General Studies & General Abilities in English and Telugu, and Paper II Automobile Engineering. '
                     'The answers are from TSPSC\'s preliminary key, because the final key was released only on candidates\' individual response sheets; a few answers may differ from the final key. Each question has a short explanation. '
                     'You can practise each paper as a quiz or a timed mock test, with answers and explanations, with one ₹45 All-in-One Pass for every exam.')
        return [
          (f'Where can I get {name} previous year question papers with answers?', where),
          (f'What is the {name} exam pattern?',
           ('Two objective papers: Paper I General Studies & Mental Ability (degree standard, 150 questions, 150 marks, 150 minutes, in English and Telugu) and Paper II Automobile Engineering (diploma standard, 150 questions, 300 marks, 150 minutes, in English), 450 marks in all, with a one-third negative mark for a wrong answer. '
            if ap else
            'Two objective papers: Paper I General Studies & General Abilities (150 questions, 150 marks, 150 minutes, in English and Telugu) and Paper II Automobile Engineering (150 questions, 300 marks, 150 minutes, in English), 450 marks in all. ')
           + 'Check the latest notification for the posts, eligibility and dates.'),
          (f'Are the {name} questions available in Telugu?',
           'Yes. Paper I is printed in English and Telugu, and every question is here as printed; tap తెలుగు at the top of the page to practise in Telugu. Paper II (Automobile Engineering) is printed in English only.'),
          (f'Is there a {name} mock test?',
           'Yes. Open the mock test page and take a real AMVI paper with a timer, or tap Create a quiz to choose subjects such as IC Engines, Brakes, the Motor Vehicles Act or Current Affairs. You get your score, the answer and an explanation for every question.'),
          ('Do I need to register?',
           'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass opens the previous papers of every exam for 12 months. There is no password.'),
          ('Which questions are left out?',
           ('Questions that APPSC deleted or ignored for all candidates are left out. APPSC\'s 2019 keys print only the correct answer, so the 2019 papers are quick-recall questions (question and answer), and a few 2019 questions whose answer makes no sense without the options are left out.'
            if ap else
            'Questions that cannot be answered as printed are left out; the explanations point out where TSPSC\'s final key may have changed the preliminary answer.')),
        ]
    return faq


def FAQ_AP(post):
    """FAQs of the AP Police (SLPRB AP) SI and Constable pages; facts from the 16 September 2026 notifications."""
    si = post == 'SI'
    name = 'AP Police SI' if si else 'AP Police Constable'
    def faq(total, npapers):
        return [
          (f'Where can I get {name} previous year question papers with answers?',
           (f'This page has {total:,} questions from the SLPRB AP SI Preliminary Written Test held on 19 February 2023: Paper I, Arithmetic and Test of Reasoning / Mental Ability, '
            "and Paper II, General Studies, in English and Telugu as printed. Paper I's answers are from SLPRB's final key and Paper II's from its preliminary key, and every question has a short explanation. "
            if si else
            f'This page has {total:,} questions from the SLPRB AP Police Constable Preliminary Written Test held on 22 January 2023 (booklet A), in English and Telugu as printed, '
            "with answers from SLPRB's final key and a short explanation for every question. ")
           + 'Practise each paper as a quiz or a timed mock test with one ₹45 All-in-One Pass for every exam.'),
          (f'How many posts are in the AP Police {"SI" if si else "Constable"} 2026 notification?',
           ('SLPRB AP notification Rc.No.81/SLPRB/Rect.1/2026 of 16 September 2026 has 378 posts: 253 SCT SI (Civil), 116 SCT RSI (AR) and 9 SI in the Special Protection Force; '
            'a separate notification has 50 SI (Communications) and 10 SI (PTO) posts. SLPRB will announce the application and exam dates in a press note.'
            if si else
            'SLPRB AP notification Rc.No.91/SLPRB/Rect.2/2026 of 16 September 2026 has 1,156 posts: 542 SCT PC (Civil), 285 SCT PC (AR), 158 Firemen, 150 Warders (Men) and 21 Warders (Women); '
            'separate notifications have 200 PC (Communications) and 213 PC (Mechanics and Drivers) posts. SLPRB will announce the application and exam dates in a press note.')),
          (f'What is the {name} Preliminary Written Test pattern?',
           ('Two objective papers of 100 questions each, 3 hours each: Paper I Arithmetic (SSC standard) and Test of Reasoning / Mental Ability, and Paper II General Studies (degree standard). '
            'You must qualify in each paper: 40% for OC (and EWS), 35% for BC, 30% for SC and ST. Qualified candidates take the PMT/PET and then the Final Written Examination of four papers.'
            if si else
            'One objective paper of 200 questions for 200 marks in 3 hours (Intermediate standard): English, Arithmetic, Reasoning / Mental Ability, General Science, history and culture, '
            'geography, polity and economy, and current events. The qualifying marks are 40% for OC (and EWS), 35% for BC and 30% for SC and ST. Qualified candidates take the PMT/PET and then the Final Written Examination.')),
          ('Who can apply?',
           ('A degree from a recognised university (SC and ST candidates who passed Intermediate and studied a degree are also eligible), age 21 to 27 years as on 1 July 2026 with the usual relaxations. '
            'Height at least 167.6 cm for men and 152.5 cm for women (lower for Aboriginal ST candidates of the agency areas). Fee ₹600 (₹300 for SC and ST of AP).'
            if si else
            'Intermediate passed (SC and ST candidates who passed SSC and appeared for Intermediate are also eligible), age 18 to 24 years as on 1 July 2026 for SCT PC (Civil) and (AR) with the usual relaxations. '
            'Height at least 167.6 cm for men and 152.5 cm for women (lower for Aboriginal ST candidates of the agency areas). Fee ₹300 (half that for SC and ST candidates of AP).')),
          (f'Are the {name} questions available in Telugu?',
           'Yes. Every question that the booklet printed in Telugu is here exactly as printed. Tap తెలుగు at the top of the page to practise in Telugu.'
           + ('' if si else ' The English-language questions are printed in English only, as in the real paper.')),
        ]
    return faq


def FAQ_ANALYST(total, npapers):
    return [
      ('Where can I get APPSC Analyst Grade-II previous question papers with answers?',
       f'This page has {total:,} questions from {npapers} APPSC Analyst Grade-II (A.P. Pollution Control Board) papers: the 2025 Paper I General Studies & Mental Ability and the Paper II Chemistry, Biochemistry, Biology and Environmental Science papers '
       "(Notification 02/2024, computer-based test, March 2025). Every answer is from APPSC's final key, and each question has a short explanation. Practise each paper as a quiz or a timed mock test with one ₹45 All-in-One Pass for every exam."),
      ('What is the APPSC Analyst Grade-II exam pattern in 2026?',
       'Notification 21/2026 (18 posts) has two objective papers of degree standard: Paper I General Studies & Mental Ability (150 questions, 150 marks, 150 minutes) and Paper II, a Common Paper of Chemistry, '
       'Biochemistry, Biology and Environmental Science (150 questions, 150 marks, 150 minutes), 300 marks in all, computer-based, with one-third of a mark deducted for each wrong answer, followed by a qualifying '
       'Computer Proficiency Test. Online applications run from 13 October to 2 November 2026.'),
      ('Why are there four Paper II papers from 2025?',
       'In 2025 (Notification 02/2024) Paper II was set separately for each degree subject. From 2026 Paper II is one Common Paper covering all four subjects, so all four 2025 papers are useful practice: '
       'they show the level and the topics APPSC asks in each subject.'),
      ('Who can apply for APPSC Analyst Grade-II?',
       "A bachelor's degree in Chemistry, Biochemistry, Biology or Environmental Sciences from a recognised university in India (first class preferred), age 18 to 44 years as on 1 July 2026 with the usual relaxations. "
       'Pay scale ₹48,440 – ₹1,37,220.'),
      ('Are the questions in Telugu?',
       'Paper I (General Studies & Mental Ability) is here in English and Telugu, as APPSC printed it. The Paper II papers are printed in English only, so they are here in English.'),
      ('Which questions are left out?',
       'Questions that APPSC ignored for all candidates are left out. Where APPSC accepted two options, both are shown as correct.'),
    ]


def FAQ_FRO(total, npapers):
    return [
      ('Where can I get APPSC Forest Range Officer previous question papers with answers?',
       f'This page has {total:,} questions from {npapers} APPSC Forest Range Officer (FRO) papers: the 2025 Screening Test (Notification 11/2024), Paper I General Studies & Mental Ability, General Forestry I and General Forestry II '
       "of the 2023 Mains (Notification 21/2022) and the 2020 Mains (Notification 10/2018), and the 2019 Screening Test. Every answer is from APPSC's final key, and each question has a short explanation. Practise each paper as a quiz or a timed mock test with one ₹45 All-in-One Pass for every exam."),
      ('What is the APPSC FRO exam pattern?',
       'Notification 16/2026 (5 posts) has a qualifying test in General English and General Telugu (100 marks) and four objective papers of 150 marks each: Paper I General Studies & Mental Ability, '
       'Paper II Mathematics (SSC standard), Paper III General Forestry I and Paper IV General Forestry II, 600 marks in all, computer-based, with one-third of a mark deducted for each wrong answer. '
       'Shortlisted candidates take a walking test (men 25 km, women 16 km in 4 hours), a medical examination and a Computer Proficiency Test. Online applications run from 16 October to 5 November 2026.'),
      ('What is in the General Forestry syllabus?',
       'General Forestry I: renewable and non-renewable natural resources, plant sciences, biodiversity and its conservation, soil science and geology, water and watershed management, silviculture of AP species, '
       'agroforestry, social and community forestry. General Forestry II: ecosystems and wildlife, forest protection and fire, forest utilization and NTFPs, animal management and economic zoology, forest economics, '
       'policy, laws and administration, forest inventory, mensuration and remote sensing, environmental science, survey and engineering, and first aid.'),
      ('Who can apply for APPSC FRO?',
       "A bachelor's degree in agriculture, botany, chemistry, computer applications or science, engineering (agriculture, chemical, civil, computer, electrical, electronics or mechanical), environmental science, forestry, "
       'geology, horticulture, mathematics, physics, statistics, veterinary science or zoology; age 18 to 30 years as on 1 July 2026 with the usual relaxations; height at least 163 cm for men and 150 cm for women. '
       'Pay scale ₹48,440 – ₹1,37,220.'),
      ('Are the questions in Telugu?',
       'The 2023 Mains Paper I (General Studies & Mental Ability) and Section 1 of the 2025 Screening Test are here in English and Telugu, as APPSC printed them. The General Forestry papers, the 2020 Mains GS paper and the 2019 Screening Test are printed in English only, so they are here in English.'),
      ('Which questions are left out?',
       "Questions that APPSC ignored or deleted for all candidates are left out. Where APPSC accepted two options, both are shown as correct. The 2025 Mains (Notification 11/2024) is not here yet, because APPSC has published only its initial keys."),
    ]


def FAQ_AEE(total, npapers):
    return [
      ('Where can I get APPSC Assistant Environmental Engineer previous question papers with answers?',
       f'This page has {total:,} questions from the APPSC Assistant Environmental Engineer (A.P. Pollution Control Board) exam held on 25 March 2025 (Notification 15/2023): '
       + ('Paper I General Studies & Mental Ability and Paper II Common Subject. ' if aee_p1() else 'Paper II Common Subject; Paper I General Studies & Mental Ability is being added next. ')
       + "Every answer is from APPSC's final key, and each question has a short explanation. Practise each paper as a quiz or a timed mock test with one ₹45 All-in-One Pass for every exam."),
      ('What is the APPSC Assistant Environmental Engineer exam pattern in 2026?',
       'Notification 08/2026 (41 posts) has two objective papers of degree standard: Paper I General Studies & Mental Ability (150 questions, 150 marks, 150 minutes) and Paper II Common Subject '
       '(150 questions, 150 marks, 150 minutes), 300 marks in all, computer-based, with one-third of a mark deducted for each wrong answer, followed by a qualifying Computer Proficiency Test. '
       'In 2025 Paper II carried 300 marks (2 marks a question).'),
      ('What is in the Paper II Common Subject syllabus?',
       'Ecosystems; natural resources; biodiversity and its conservation; engineering materials; fluid mechanics and hydraulics; process calculations and thermodynamics; air, water, soil and noise pollution '
       'and control technologies; solid, industrial and e-waste management and bioremediation; climate change, ozone depletion, international conventions and Indian environmental laws and rules; '
       'and environmental impact assessment and sustainable development.'),
      ('Who can apply for APPSC Assistant Environmental Engineer?',
       'A B.E./B.Tech. degree in Civil, Mechanical, Chemical or Environmental Engineering, or a pass in Sections A and B of the AMIE (India) Civil examination; age 18 to 44 years as on 1 July 2026 with the usual relaxations. '
       'Pay scale ₹57,100 – ₹1,47,760. Online applications ran from 6 to 27 October 2026.'),
      ('Are the questions in Telugu?',
       ('Paper I (General Studies & Mental Ability) is here in English and Telugu, as APPSC printed it. Paper II (Common Subject) is set in English only, so it is here in English.' if aee_p1() else
        'Paper II (Common Subject) is set in English only, so it is here in English. Paper I (General Studies & Mental Ability), coming next, will be in English and Telugu as APPSC printed it.')),
      ('Which questions are left out?',
       'Questions that APPSC ignored for all candidates are left out (' + ('two in Paper II and three in Paper I' if aee_p1() else 'Q30 and Q97 of Paper II') + '). Where APPSC accepted more than one option, each accepted option is shown as correct.'),
    ]

def FAQ_ASO(total, npapers):
    left = ['Q134 of 2025'] + (['Q51 and Q81 of 2022'] if 'aso22' in aso_have() else [])
    return [
      ('Where can I get APPSC ASO previous question papers with answers?',
       f'This page has {total:,} questions from the APPSC Assistant Statistical Officer Paper II (Subject) of {aso_years()}: statistics, economics, financial accounting and computers, '
       "in English and Telugu as APPSC printed them. Every answer is from APPSC's final key, and each question has a short explanation. "
       'Practise each paper as a quiz or a timed mock test with one ₹45 All-in-One Pass for every exam.'),
      ('What is the APPSC ASO exam pattern?',
       'Two objective papers of degree standard, computer-based: Paper I General Studies & Mental Ability (150 questions, 150 marks, 150 minutes) and Paper II Subject '
       '(150 questions, 150 marks, 150 minutes), 300 marks in all, with one-third of a mark deducted for each wrong answer, followed by a qualifying Computer Proficiency Test (60 minutes, 100 marks).'),
      ('What is in the ASO Paper II syllabus?',
       'Economic concepts (demand, markets, national income, money and banking, inflation, public finance); international economics (trade, balance of payments, exchange rates, IMF and World Bank); '
       'the Indian economy (population, poverty, unemployment, inequality, planning and NITI Aayog, fiscal deficit, external debt); financial accounting (concepts, journal and ledger, cash book, bank reconciliation, '
       'trial balance, final accounts, depreciation); basics of computers; and statistics: collection and presentation of data, sampling, central tendency, dispersion and skewness, correlation, '
       'time series and index numbers.'),
      ('Are these papers useful for TGPSC MPSO / ASO?',
       'Yes. The TGPSC Mandal Planning & Statistical Officer / Assistant Statistical Officer exam (Notification 07/G/ES/2026) has a degree-level Statistics paper, and these APPSC Paper II questions cover the same '
       'statistics topics, besides economics and accountancy. See the <a href="/tgpsc-mpso-aso-notification-2026.html">TGPSC MPSO / ASO notification page</a>.'),
      ('Who can apply for APPSC ASO?',
       'A bachelor\'s degree with Statistics as a main subject, or with Mathematics, Economics, Commerce or Computer Science as a main subject and Statistics as one of the papers. '
       'In Notification 12/2024 the age limit was 18 to 42 years (with the usual relaxations) and the pay scale ₹37,640 – ₹1,15,500.'),
      ('Which questions are left out?',
       'Questions that APPSC ignored for all candidates are left out (' + ' and '.join(left) + ').'),
    ]

def FAQ_EO(total, npapers):
    return [
      ('Where can I get APPSC Executive Officer Grade-III previous question papers with answers?',
       f'This page has {total:,} questions from {npapers} APPSC Executive Officer Grade-III (Endowments) papers: Paper I General Studies & Mental Ability and Paper II Hindu Philosophy & Temple System '
       'of the 2026 exam (Notification 10/2025, held 11 February 2026) and the 2023 Mains (Notification 24/2021, computer-based test), plus the 2022 Screening Test. '
       "Every answer is taken from APPSC's final key, and each question has a short explanation in English and Telugu. Practise each paper as a quiz or a timed mock test with one ₹45 All-in-One Pass for every exam."),
      ('What is the APPSC EO Grade-III exam pattern?',
       'Two objective papers of degree standard: Paper I General Studies & Mental Ability (150 questions, 150 marks, 150 minutes) and Paper II Hindu Philosophy & Temple System '
       '(150 questions, 150 marks, 150 minutes), 300 marks in all, computer-based, with one-third of a mark deducted for each wrong answer, followed by a qualifying Computer Proficiency Test. '
       'Notification 23/2026 has 104 posts; online applications run from 16 October to 5 November 2026.'),
      ('What is in the Hindu Philosophy & Temple System syllabus?',
       'Ramayanam, Mahabharatham, Bhagavatham and the Puranas (characters, parts, dynasties and places); temple Agamas (Vaikhanasa, Pancharatra, Saiva and Sakta); Hindu festivals and classical arts; '
       'Vedic culture; philosophies and gurus (Alwars, Nayanars, Sankara, Ramanuja, Madhva, Basava); family structure, adoption and succession; temple income and Section 57, duties of the Executive Officer '
       '(Section 29) and endowment lands (Sections 75–86) of the A.P. Endowments Act, 1987, and the ROR Act. Learn with Anil\'s study notes on this paper are part of the All-in-One Pass.'),
      ('Are the questions available in Telugu?',
       'Yes. Both papers are printed in English and Telugu, and every question is here as printed; tap తెలుగు at the top of the page to practise in Telugu. The explanations are in Telugu too.'),
      ('Is there an APPSC EO mock test?',
       'Yes. Open the mock test page and take a real paper with a timer, or tap Create a quiz to choose subjects such as Ramayanam, Temple Agamas or the Endowments Act. You get your score, the answer and an explanation for every question.'),
      ('Which questions are left out?',
       'Questions that APPSC deleted or ignored for all candidates are left out. APPSC\'s 2022 Screening Test key prints only the correct answer, so that paper is given as quick-recall questions (question and answer).'),
    ]


def FAQ_TS(post, mains=()):
    si = post == 'SI'
    name = 'TS Police SI' if si else 'TS Police Constable'
    mkp = MOCK_PACKS.get('ts-police-si' if si else 'ts-police-constable')
    mkt = mkp and (mkp['name'] + (' (SI)' if si else ''))
    def faq(total, npapers):
        T = ts_text()
        if not si and T['pcmany']:
            where = (f'This page has {total:,} questions from {npapers} TSLPRB Police Constable papers: {T["pc_list"]}, in English and Telugu as printed. '
                     'Every answer is taken from TSLPRB\'s final key for that paper'
                     + (f' (for {" and ".join(T["pc_prelim"])} only the preliminary key could be found, so a few answers may differ from the final key)' if T['pc_prelim'] else '')
                     + ', and each question has a short explanation. You can practise each paper as a quiz or a mock test, with answers and explanations, with one ₹45 All-in-One Pass for every exam.')
        elif mains:
            fwe = (' and '.join(x for i, x in (('s2023c', 'Paper III, Arithmetic & Reasoning, on 8 April'), ('s2023d', 'Paper IV, General Studies, on 9 April')) if i in mains)
                   + ' 2023, booklet D') if si else '30 April 2023, booklet A'
            where = (f'This page has {total:,} questions from {npapers} TSLPRB papers: the {"SI" if si else "Police Constable"} Preliminary Written Test of {"7 August" if si else "28 August"} 2022 (booklet A) '
                     f'and the Final Written Examination ({fwe}), in English and Telugu as printed. '
                     f'Every answer is taken from TSLPRB\'s final key for that paper, and each question has a short explanation. You can practise each paper as a quiz or a mock test, with answers and explanations with one ₹45 All-in-One Pass for every exam.')
        else:
            where = (f'This page has {total} questions from the {"SI" if si else "Police Constable"} Preliminary Written Test held by TSLPRB on {"7 August" if si else "28 August"} 2022 (booklet A), in English and Telugu as printed. '
                     f'Every answer is taken from TSLPRB\'s final key, released on 21 October 2022, and each question has a short explanation. You can practise the paper as a quiz, with answers and explanations with one ₹45 All-in-One Pass for every exam.')
        return [
          (f'Where can I get {name} previous year question papers with answers?', where),
          (f'What is the {name} Preliminary Written Test pattern?',
           ('The SI Preliminary Written Test is one objective paper of 200 questions for 200 marks in 3 hours: Arithmetic and Test of Reasoning / Mental Ability, and General Studies. '
            if si else
            'The Police Constable Preliminary Written Test is one objective paper of 200 questions for 200 marks in 3 hours, covering English, Arithmetic, Reasoning / Mental Ability and General Studies. ')
           + 'The qualifying marks are 30% for OC, 25% for BC and 20% for SC, ST and ex-servicemen. Qualified candidates take the physical tests (PMT/PET) and then the Final Written Examination.'),
          ('When is the 2026 Preliminary Written Test?',
           ('TGPRB has tentatively scheduled the SI Preliminary Written Test for 29 November 2026 (forenoon). ' if si else
            'TGPRB has tentatively scheduled the Police Constable Preliminary Written Test for 20 December 2026 (forenoon). ')
           + 'Dates can change, so confirm on tgprb.in. The 2022 prelims paper on this page follows the same pattern.'),
          (f'Are the {name} questions available in Telugu?',
           'Yes. Every question that the booklet printed in Telugu is here exactly as printed. Tap తెలుగు at the top of the page to practise in Telugu.'),
          (f'Is there a {name} mock test?',
           (f'Yes. {mkt}: {mkp["n"]} full-length mocks of 200 questions in the real pattern, in English and Telugu, with explanations and sectional tests, included in the ₹{PAY["pyq_price"]} All-in-One Pass with every previous paper'
            + (' (Mock 1 is free for registered students)' if mkp.get('free1') or any(m.get('free') for m in mkp.get('mocks', [])) else '')
            + f'; the same pass opens Mission Khaki for both SI and Constable. You can also take the real TSLPRB previous papers as timed tests, or tap Create a quiz for a timed test from chosen subjects, with the All-in-One Pass.')
           if mkp else
           f'Yes. Tap Create a quiz, choose subjects or topics, and pick Timed test: you get a mock test made of real TSLPRB questions, with your score and a topic-wise analysis at the end. Practice mode works like practice bits, one question at a time with the answer and explanation.'),
          ('Do I need to register?',
           'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; after that one ₹45 All-in-One Pass opens the previous papers of every exam for 12 months. There is no password.'),
          ('Which questions are left out?',
           ('Questions that TSLPRB deleted in its key, questions for which the key accepted three or four options, and the few that have no correct option as printed in the booklet are left out. '
            if not si and T['pcmany'] else
            'Questions that TSLPRB deleted in the final key, and questions for which the final key accepted three or four options, are left out. ')
           + 'Where the key accepted two options, both are shown as correct, and where it also gave the mark for leaving a question blank, the explanation says so.'),
        ]
    return faq


STATIC_CSS = """.mbtns{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.mbtn{display:inline-flex;align-items:center;gap:5px;padding:6px 13px;border-radius:999px;border:1.5px solid var(--accent);color:var(--accent-text);background:var(--surface);font-weight:700;font-size:14px;text-decoration:none;line-height:1.2}
.mbtn:hover{background:var(--accent-soft)}
.mbtn.go{background:var(--accent);color:#fff}.mbtn.go:hover{filter:brightness(1.08);background:var(--accent)}
.mbtn.mpdf{border-color:#0E7A43;color:#0E7A43}
.mchips{display:flex;flex-wrap:wrap;gap:6px}
.mchip{display:inline-block;padding:4px 11px;border-radius:999px;background:var(--accent-soft);color:var(--accent-text);font-weight:600;font-size:13.5px;text-decoration:none}
.mchip:hover{text-decoration:underline}
table.mtab tr.msoon td{color:var(--muted);background:var(--surface-2,#f1f5f9)}

.nw{white-space:nowrap}
[lang="te"]{font-family:"Noto Sans Telugu",sans-serif;line-height:1.8}
[lang="hi"]{font-family:"Noto Sans Devanagari",sans-serif;line-height:1.75}
.q .te{border-left:3px solid var(--line);padding-left:12px;margin:8px 0 4px}
:root{--bg:#F3F6FB;--surface:#fff;--ink:#0D1830;--muted:#55627C;--line:#D6DFEC;--accent:#1846C7;--accent-soft:#E2EAFC;--accent-text:#1440B8;--band:#0C2266;--band-ink:#EEF3FF;--good:#12804A;--good-soft:#DDF3E7}
@media (prefers-color-scheme:dark){:root{--bg:#0A1020;--surface:#111A2E;--ink:#E5ECF8;--muted:#9AA8C3;--line:#26334F;--accent:#6F95FF;--accent-soft:#1A2A52;--accent-text:#9DB7FF;--band:#0F1F4E;--band-ink:#EEF3FF;--good:#41C080;--good-soft:#123426;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 "Source Sans 3",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent-text)}.wrap{max-width:860px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header{background:var(--band);color:var(--band-ink)}header .wrap{padding-block:14px;display:flex;overflow-wrap:anywhere;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center}
header a{color:var(--band-ink);text-decoration:none;font-weight:700}header .hr{display:inline-flex;align-items:center;gap:12px;flex-wrap:wrap}header a.hsub{background:linear-gradient(135deg,#f59e0b,#f97316);color:#1f1300;padding:6px 12px;border-radius:999px;font-weight:800;font-size:14px;white-space:nowrap}header a.hsub[hidden]{display:none}h1,h2{font-family:Archivo,"Arial Narrow",system-ui,sans-serif;line-height:1.2;text-wrap:balance}
h1{font-size:clamp(26px,4vw,36px);margin:28px 0 8px}h2{font-size:22px;margin:32px 0 10px}.lede{color:var(--muted);max-width:65ch}
.cta{display:inline-block;background:var(--accent);color:#fff;padding:10px 16px;border-radius:10px;font-weight:700;text-decoration:none;margin:8px 8px 0 0}
.cta.alt{background:transparent;color:var(--accent-text);border:1.5px solid var(--line)}
ol.qs{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:14px}
.q{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.q .meta{font:13px/1.4 "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);margin-bottom:6px}
.q p{margin:0 0 8px;white-space:pre-line;font-weight:600;overflow-wrap:anywhere}.qtbl-wrap{overflow-x:auto;margin:0 0 10px}.qtbl{border-collapse:collapse;font-size:15px}.qtbl th,.qtbl td{border:1px solid var(--line);padding:4px 10px;text-align:left;vertical-align:top}.qtbl th{background:var(--accent-soft);font-weight:700}.qtbl .num{text-align:right;white-space:nowrap}.q ol{margin:0 0 8px;padding-left:28px}.q li{overflow-wrap:anywhere}
.q img{max-width:100%;background:#fff;border-radius:6px}
details summary{cursor:pointer;color:var(--accent-text);font-weight:700}
.buy{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--surface);border:1.5px solid var(--accent);border-radius:14px;padding:16px 18px;margin:12px 0}
.buy b{font-size:18px}.buy p{margin:6px 0 0}.buy .muted{color:var(--muted);font-size:14.5px}.buy .cta{margin:0;white-space:nowrap}
table.facts{border-collapse:collapse;width:100%;margin:8px 0 16px;background:var(--surface);font-size:16px}
table.facts th,table.facts td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}
table.facts th{background:var(--accent-soft);font-weight:700;overflow-wrap:normal}table.facts td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.note{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:12px 14px;margin:16px 0}
.ans{color:var(--good);font-weight:700;margin:8px 0 4px}.why{color:var(--muted);margin:0}
.lock{background:var(--accent-soft);border-radius:10px;padding:10px 12px;margin:8px 0 0;font-size:15.5px}
.passon{background:#E6F4EC;color:#0B5E36;border:1px solid #9FD3B5;border-radius:10px;padding:10px 12px;margin:10px 0;font-weight:600}
nav.toc{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}nav.toc a{background:var(--accent-soft);padding:4px 10px;border-radius:999px;text-decoration:none;font-size:15px}
footer{margin-top:40px;border-top:1px solid var(--line);color:var(--muted);font-size:15px}footer .wrap{padding-block:18px}
.course{background:var(--surface);border:2px solid var(--accent);border-radius:16px;padding:18px 20px;margin:16px 0 8px}
.course .chead{display:flex;gap:16px;justify-content:space-between;align-items:flex-start;flex-wrap:wrap}.course .chead>div{flex:1 1 380px}
.course .ck{font:13px/1.4 "IBM Plex Mono",ui-monospace,monospace;color:var(--accent-text);text-transform:uppercase;letter-spacing:.04em;margin:0 0 4px}
.course h2{margin:0 0 6px}.course h3{font-family:Archivo,"Arial Narrow",system-ui,sans-serif;font-size:18px;margin:18px 0 8px}
.course .chead .cta{margin:4px 0 0;white-space:nowrap}
.cbuy{display:flex;flex-direction:column;align-items:flex-start;gap:8px}.cbuy .try{font-weight:700;font-size:15.5px;white-space:nowrap}
:root{--bad:#B42318;--bad-soft:#FDECEA}@media (prefers-color-scheme:dark){:root{--bad:#FF8A80;--bad-soft:#3B1C1C}}
.q ol.sopts{list-style:none;padding:0;margin:4px 0 10px;display:flex;flex-direction:column;gap:8px}
.sopts button{width:100%;display:flex;gap:10px;align-items:flex-start;text-align:left;font:inherit;font-weight:600;color:var(--ink);background:var(--bg);border:1.5px solid var(--line);border-radius:10px;padding:10px 12px;cursor:pointer;overflow-wrap:anywhere}
.sopts button:hover:not(:disabled){border-color:var(--accent)}.sopts button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.sopts button:disabled{cursor:default;color:var(--ink)}.sopts .on{font:14px/1.6 "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);flex:none}
.sopts button.right{border-color:var(--good);background:var(--good-soft)}.sopts button.right .on{color:var(--good)}
.sopts button.wrong{border-color:var(--bad);background:var(--bad-soft)}.sopts button.wrong .on{color:var(--bad)}
.sscore{background:var(--good-soft);color:var(--good);border-radius:10px;padding:10px 14px;margin:14px 0 0;font-weight:700}
ol.clist{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px}
ol.clist li{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--bg)}
.cmeta{font:13px/1.4 "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);margin-bottom:4px}.cacts .cta{margin:8px 8px 0 0}
.sgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:8px 0}
.sgrid a{display:flex;justify-content:space-between;gap:10px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:700}
.sgrid a:hover,.fgrid a:hover{border-color:var(--accent)}.sgrid .n{font:13px/1.4 "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);font-weight:400;white-space:nowrap}
.fgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:8px 0}@media (max-width:640px){.fgrid{grid-template-columns:1fr}}
.fgrid:has(> a:only-child){grid-template-columns:1fr}
.fgrid a{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.fgrid b{display:block;font-size:17px;margin-bottom:2px}.fgrid span{color:var(--muted);font-size:15px}
"""


def static_page(rel_depth, title, desc, canonical, h1, lede, body_html, crumbs, conf=None, ename=None, at_root=False, foot_text=None, head_all=False):
    ename = ename or (conf['name'] if conf else 'APPSC Group-II')
    rootup = '' if at_root else '../' * (rel_depth + (1 if conf and conf.get('dir') else 0))
    up = '../' * rel_depth
    pb = conf['pb'] if conf else '/appsc-group-2/'
    board = conf['board'] if conf else 'APPSC'
    gf = conf['l2']['gf'] if conf else ''
    if foot_text:
        foot = foot_text
    elif conf and conf.get('foot'):
        foot = conf['foot']
    elif board == 'APPSC':
        foot = (f'Questions and answers are taken from APPSC\'s official final keys. Explanations are by Jupudi Anil Kumar, '
                f'Learn with Anil (Instagram: @{INSTAGRAM}). Not affiliated with APPSC.')
    else:
        foot = (f'Questions are from {board}\'s official question paper and answers from {conf["keyshort"]}. Explanations are by '
                f'Jupudi Anil Kumar, Learn with Anil (Instagram: @{INSTAGRAM}). Not affiliated with {board}.')
    if PAY.get('on'):   # PYQ buttons carry a lock; the small script at the end removes it once this device has a paid All-in-One Pass
        body_html = re.sub(r'(<a class="cta[^"]*" href="[^"]*\?(?:' + ('pdf' if conf and conf['id'] in FREE_PYQ else 'sec|practice|test|pdf') + r')=[^"]*">)',
                           r'\1<span class="lk" aria-hidden="true">🔒 </span>', body_html)
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
{ICONS}{ga_tag()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header><div class="wrap"><a href="{pb if conf else '/'}">Learn with Anil · {nw(ename) + ' PYQs' if not head_all else 'PYQs for every exam'}</a><span class="hr"><a href="{'/' if head_all else (conf or {}).get('nav', ('', pb + 'practice/'))[1]}">{'All exams →' if head_all else (conf or {}).get('nav', ('Practise online →', ''))[0]}</a><a class="hsub" id="hsub" href="{pb}?buy=pyq" title="One ₹{PAY["pyq_price"]} payment opens every PYQ, mock test and book on the site for 12 months">Subscribe ₹{PAY["pyq_price"]}</a></span></div></header>
<script>try{{var P=JSON.parse(localStorage.getItem("lwa-passes-v1")||"{{}}").all||{{}};if(P.paid&&P.pyq&&new Date(P.pyq+"T23:59:59+05:30")>=new Date())document.getElementById("hsub").hidden=true;}}catch(e){{}}</script>
<main class="wrap">
<h1>{nw(h1)}</h1>
<p class="lede">{lede}</p>
{'<p class="passon" hidden></p>' if PAY.get('on') else ''}{body_html}
</main>
<footer><div class="wrap"><p style="margin:0 0 8px"><b>Learn with Anil</b> · <a href="/">LearnWithAnil.in</a>: previous year questions with answers for every exam.</p><p style="margin:0 0 8px"><a href="{rootup}appsc-pyqs.html">All APPSC previous question papers (PYQs)</a> · <a href="{rootup}ts-police-pyqs.html">All TS Police previous question papers</a> · <a href="{rootup}ap-police-pyqs.html">All AP Police previous question papers</a> · <a href="/exam-notifications.html">All exam notifications 2026</a> · <a href="/appsc-group-2-notification-2026.html">APPSC Group 2 Notification 2026</a> · <a href="/appsc-group-1-notification-2026.html">Group 1 Notification 2026</a> · <a href="{rootup}appsc-group-1/">APPSC Group-I</a> · <a href="/appsc-group-2/">APPSC Group-II</a> · <a href="/upsc-prelims/">UPSC Prelims</a> · <a href="/upsc-cse/">UPSC Mains</a> · <a href="/upsc-capf/">UPSC CAPF (AC)</a> · <a href="/upsc-epfo/">UPSC EPFO (APFC)</a> · <a href="/ssc-cgl/">SSC CGL</a> · <a href="/ts-police-si/">TS Police SI</a> · <a href="/ts-police-constable/">TS Police Constable</a> · <a href="/ap-police-si/">AP Police SI</a> · <a href="/ap-police-constable/">AP Police Constable</a> · <a href="/ap-police-si-notification-2026.html">AP Police SI Notification 2026</a> · <a href="/ap-police-constable-notification-2026.html">AP Police Constable Notification 2026</a> · <a href="/appsc-amvi/">APPSC AMVI</a> · <a href="/tgpsc-amvi/">TGPSC AMVI</a> · <a href="/appsc-endowment-officer/">APPSC Endowment Officer (EO Grade-III)</a> · <a href="/appsc-eo-grade-3-notification-2026.html">EO Grade-III Notification 2026</a> · <a href="/appsc-analyst-grade-2/">APPSC Analyst Grade-II</a> · <a href="/appsc-assistant-environmental-engineer/">APPSC Assistant Environmental Engineer</a> · <a href="/appsc-assistant-statistical-officer/">APPSC Assistant Statistical Officer (ASO)</a> · <a href="/appsc-forest-range-officer/">APPSC Forest Range Officer (FRO)</a> · <a href="/">All exams</a> · <a href="/help.html">Help &amp; grievances</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a> · <a href="/refund.html">Refunds</a> · <a href="/delivery.html">Delivery</a> · <a href="/contact.html">Contact</a> · <a href="/funders.html">Fund this project</a></p>{foot} Visits are counted with Google Analytics.</div></footer>
<script>try{{var c=(new URLSearchParams(location.search).get("ref")||"").toUpperCase(),st=JSON.parse(localStorage.getItem("lwa-appsc-g2-student-v1")||"{{}}")||{{}},rf=JSON.parse(localStorage.getItem("lwa-ref-from")||"null");
if(/^[A-Z]{{6}}$/.test(c)&&!st.name&&!(rf&&rf.c&&Date.now()-rf.t<2592e6))localStorage.setItem("lwa-ref-from",JSON.stringify({{c:c,t:Date.now()}}))}}catch(e){{}}
try{{var a=(JSON.parse(localStorage.getItem("lwa-passes-v1")||"{{}}").all)||{{}},L=function(d){{return!!d&&new Date(d+"T23:59:59+05:30")>=new Date()}};
if(!(a.paid&&L(a.pyq))&&L(a.bonus)){{document.querySelectorAll(".lk").forEach(function(e){{e.textContent="✓ ";e.className="lk ok"}});
var f=document.querySelector(".passon");if(f){{f.textContent="🎁 Your free days from inviting friends are active until "+new Date(a.bonus+"T12:00:00+05:30").toLocaleDateString("en-IN",{{day:"numeric",month:"long",year:"numeric"}})+": every previous paper, sectional and quiz is unlocked on this device.";f.hidden=false}}}}
if(a.paid&&L(a.pyq)){{
document.querySelectorAll(".lk").forEach(function(e){{e.textContent="✓ ";e.className="lk ok"}});
document.querySelectorAll("[data-paidtxt]").forEach(function(e){{e.textContent=e.getAttribute("data-paidtxt")}});
document.querySelectorAll('a[href*="?buy=pyq"]').forEach(function(e){{e.textContent="✓ All-in-One Pass active"}});
var b=document.querySelector(".passon");if(b){{b.textContent="✓ Your All-in-One Pass is active until "+new Date(a.pyq+"T12:00:00+05:30").toLocaleDateString("en-IN",{{day:"numeric",month:"long",year:"numeric"}})+": every previous paper, sectional and quiz of every exam is unlocked on this device. Students without the pass see a lock (🔒) on these buttons.";b.hidden=false}}}}}}catch(e){{}}</script>
</body>
</html>
"""


def lock_html(unlock):
    return (f'<p class="lock">Explanation: <a href="{unlock}">open it in the practice app</a>. '
            f'It needs the ₹{PAY["pyq_price"]} All-in-One Pass: one payment for every exam on the site.</p>')


def ex_hash(w, wt=''):
    """Short hash of one explanation (English + Telugu/Hindi), to know whether the sealed bundle still has its current text (tools/ex_seal.py)."""
    return hashlib.sha256((w + '\x00' + (wt or '')).encode()).hexdigest()[:8]


def public_questions(questions, sealed):
    """The questions for the public app data: an explanation that is in the exam's sealed bundle (tools/ex_seal.py; paid,
    outside the free sample) is left out and the question is marked "wx": 1, so the app fetches it with the All-in-One Pass.
    Returns (questions, number of paid explanations still public because they were added or changed after sealing)."""
    if not sealed: return questions, 0
    h, free, out, stale = sealed['h'], sample_ids(questions), [], 0
    for q in questions:
        if q.get('w') and q['id'] in h and h[q['id']] == ex_hash(q['w'], q.get('wt', '')):
            q = {k: v for k, v in q.items() if k not in ('w', 'wt')}; q['wx'] = 1
        elif q.get('w') and q['id'] not in free: stale += 1
        out.append(q)
    return out, stale


def sample_ids(questions):
    """The questions whose explanations stay public: the first SAMPLE_N of each paper (every answer is public since 25 Oct 2026)."""
    seen, out = {}, set()
    for q in questions:
        seen[q['p']] = seen.get(q['p'], 0) + 1
        if seen[q['p']] <= SAMPLE_N: out.add(q['id'])
    return out


def _tbl_row(line):
    """A line of a pipe-typed table ('Trade receivables | 25,00,000 |'); '|x - y|' (absolute value) is not one."""
    s = line.strip()
    return '|' in s and (' | ' in s or s.startswith('| ') or s.endswith(' |') or s == '|')


def qtext_html(text):
    """Question text as <p> blocks; runs of two or more pipe-typed rows become a real table (first row = header unless it holds figures)."""
    lines, out, buf, i = text.split('\n'), [], [], 0
    def flush():
        if buf: out.append(f'<p>{esc(chr(10).join(buf))}</p>'); buf.clear()
    while i < len(lines):
        j = i
        while j < len(lines) and _tbl_row(lines[j]): j += 1
        if j - i >= 2:
            flush()
            rows = [[c.strip() for c in ln.strip().split('|')] for ln in lines[i:j]]
            w = max(len(r) for r in rows)
            rows = [r + [''] * (w - len(r)) for r in rows]
            num = lambda c: bool(re.fullmatch(r'[₹$%()+\-–—−.,:/\d\s]*\d[₹$%()+\-–—−.,:/\d\s]*', c))
            cell = lambda tag, c: f'<{tag}{" class=num" if num(c) else ""}>{esc(c)}</{tag}>'
            head = not any(num(c) for c in rows[0])   # a first row with figures in it is data, not a header ('Hockey | 15%')
            out.append('<div class="qtbl-wrap"><table class="qtbl">' + ('<thead><tr>' + ''.join(cell('th', c) for c in rows[0]) + '</tr></thead>' if head else '') + '<tbody>'
                       + ''.join('<tr>' + ''.join(cell('td', c) for c in r) + '</tr>' for r in rows[1 if head else 0:]) + '</tbody></table></div>')
            i = j
        else:
            buf.append(lines[i]); i += 1
    flush()
    return ''.join(out)


def q_html(q, paper_short, num_label, subj=SUBJ, l2=L2_TE, qhref=None, unlock=None):
    label = f'<a href="{qhref}">{esc(num_label)}</a>' if qhref else esc(num_label)
    parts = [f'<li class="q" id="q{q["n"]}"><div class="meta">{label} · {esc(subj[q["s"]][1])} · {esc(q["t"])}</div>',
             qtext_html(q['q'])]
    if q.get('img'):
        parts.append(f'<img src="{q["img"]}" alt="Figure for question {q["n"]}" loading="lazy">')
    if q.get('o'):
        parts.append('<ol>' + ''.join(f'<li>{esc(o)}</li>' for o in q['o']) + '</ol>')
        if q.get('lwo'): parts.append('<p class="muted" style="font-size:13px;margin:4px 0 0">APPSC\'s key printed only the answer: the correct option is APPSC\'s, the other three are written by Learn with Anil.</p>')
        ans = ' / '.join(f'({i + 1}) {q["o"][i]}' for i in q['a'])
    else:
        ans = q['ans']
    if q.get('qt'):
        te = qtext_html(q['qt'])
        if q.get('ot'):
            te += '<ol>' + ''.join(f'<li>{esc(o)}</li>' for o in q['ot']) + '</ol>'
        parts.append(f'<div class="te" lang="{l2["code"]}">{te}</div>')
    ans_te = ''
    if q.get('ot'): ans_te = ' / '.join(f'({i + 1}) {q["ot"][i]}' for i in q['a'])
    elif q.get('at'): ans_te = q['at']
    te_ans = f'<p class="ans" lang="{l2["code"]}">{l2["ans"]}: {esc(ans_te)}</p>' if ans_te else ''
    wt = f'<p class="why" lang="{l2["code"]}" style="margin-top:6px">{esc(q["wt"])}</p>' if q.get('wt') else ''
    shown = f'<details><summary>Show answer</summary><p class="ans">{esc(NOKEY_LABEL.get(q.get("p"), "Answer"))}: {esc(ans)}</p>{te_ans}'
    if unlock:   # outside the free sample: the answer is public (Anil, 25 Oct 2026, so ChatGPT and Google can read it); the explanation needs the All-in-One Pass
        parts.append(f'{shown}</details>' + lock_html(unlock) + '</li>')
        return ''.join(parts)
    parts.append(f'{shown}<p class="why">{esc(q["w"])}</p>{wt}</details></li>')
    return ''.join(parts)


def llms_txt(loaded, grand):
    """/llms.txt: a plain summary of the site for AI assistants (ChatGPT, Claude, Perplexity …) that cite pages when people
    ask where to find previous papers. ChatGPT was the biggest source of visitors on 24 Oct 2026."""
    exams = [c for c, _, _ in loaded]
    L = [f'# Learn with Anil PYQs (learnwithanil.in)', '',
         f'> Previous year question papers (PYQs) of Indian government recruitment exams with answers from the official final keys, '
         f'a short explanation for every question, and online practice: question-by-question practice with a timer, timed tests, '
         f'subject-wise (sectional) tests and topic-wise quizzes. Made by Jupudi Anil Kumar, a civil-services educator in Hyderabad.', '',
         'Key facts:',
         f'- {grand:,} questions from the official papers of {len(exams)} exams: ' + ', '.join(c['name'] for c in exams) + '.',
         '- Answers come only from the official keys published by the recruiting body (APPSC, TSLPRB/TGPRB, UPSC, TSPSC/TGPSC). '
         'For a few old APPSC papers (Group 1 2019 and 2023, Group 2 2019) APPSC printed only the correct answer; there the other three options are written by Learn with Anil and labelled.',
         '- Languages: English with Telugu for APPSC, TS Police and TGPSC exams; English with Hindi for UPSC exams.',
         f'- Free: every question and its correct answer from the official key are public on the paper, subject and question pages, with the explanations of the first {SAMPLE_N} questions of each paper, and a daily question of the day.',
         f'- All-in-One Pass: ₹{PAY["pyq_price"]} once for 12 months, covering everything on the site: every previous paper of every exam (and exams added later) with every explanation, practice in the app, timed tests, sectionals and study tools, every mock test series and the study books. Nothing else is sold.']
    for c in exams:
        mk = MOCK_PACKS.get(c['id']); up = UPCOMING_PACKS.get(c['id'])
        if mk: L.append(f'- {mk["title"]}: {mk["n"]} full-length mock tests ({live_text(mk).replace(" (included in the price)", "").rstrip(".")}), included in the ₹{PAY["pyq_price"]} All-in-One Pass. {SITE_URL}{c["pb"]}mock-test.html')
        elif up: L.append(f'- {up["name"]}: {up["n"]} mock tests, coming soon, included in the ₹{PAY["pyq_price"]} All-in-One Pass. {SITE_URL}{c["pb"]}mock-test.html')
    if BB_URL: L.append(f'- Bahubali Test Series (APPSC Group 2 Mains): 24 full-length tests, included in the ₹{PAY["pyq_price"]} All-in-One Pass. {SITE_URL}{BB_URL}')
    L += ['- Not affiliated with APPSC, TSLPRB, UPSC, TGPSC or any recruiting body.', '', '## Exams and their previous papers']
    for c, papers, questions in loaded:
        base = c['dir'] + '/' if c['dir'] else ''
        L.append(f'- [{c["name"]} previous year question papers with answers]({SITE_URL}{c["pb"]}): {len(questions):,} questions, '
                 f'English and {c["l2"]["name"]}. PYQs: {SITE_URL}{c["pb"]}pyqs.html · Sectional tests: {SITE_URL}{c["pb"]}sectional-tests.html')
        for p in sorted(papers, key=lambda p: (-p['year'], p['id'])):
            L.append(f'  - [{paper_kw(c, p)} question paper with answers]({SITE_URL}/{base}papers/{p["slug"]}.html) — held {p["held"]}, {p["count"]} questions')
        if c['id'] in MAINS_EXAMS and os.path.exists(os.path.join(SRC, c['src'], 'mains-pyqs', 'questions.json')):   # descriptive Mains PYQs (tools/g1mains.py)
            L.append(f'  - [APPSC Group 1 Mains previous year questions with model answers, year-wise and subject-wise]({SITE_URL}{c["pb"]}mains-pyqs/) — '
                     f'Papers II to V of the 2020, 2023 and 2025 Mains, 360 questions, plus the 27 Paper I essay topics; questions and all model answers free')
            mdir = os.path.join(DIST, 'site', c['dir'], 'mains-pyqs')   # each year-paper page (SEO, 1 Nov 2026)
            for y in (2025, 2023, 2020):
                for n, nm in ((1, 'Paper I (Essay) topics'), (2, 'Paper II (History & Geography)'), (3, 'Paper III (Polity & Ethics)'), (4, 'Paper IV (Economy)'), (5, 'Paper V (Science, Technology & Environment)')):
                    if os.path.exists(os.path.join(mdir, f'{y}-paper-{n}.html')):
                        L.append(f'    - [APPSC Group 1 Mains {y} {nm}' + ('' if n == 1 else ' questions with model answers') + f']({SITE_URL}{c["pb"]}mains-pyqs/{y}-paper-{n}.html)')
    try:   # UPSC CSE Mains GS 1-4 (tools/upscmains.py): its own pages, not an app exam
        import upscmains
        uq, _ = upscmains.load(SRC)
    except Exception: uq = []
    if uq:
        ub = f'{SITE_URL}/{upscmains.EXAM}/mains-pyqs/'
        L.append(f'- [UPSC Civil Services (CSE) Mains previous year questions with model answers, GS Papers 1–4]({ub}): {len(uq):,} questions of '
                 f'{min(q["year"] for q in uq)}–{max(q["year"] for q in uq)}, year-wise and subject-wise, each with a model answer on its own page '
                 f'(key words, points, diagrams); questions and all model answers free. Hub: {SITE_URL}/{upscmains.EXAM}/')
        for y in sorted({q['year'] for q in uq}, reverse=True):
            for p in upscmains.PAPERS:
                if any(q['year'] == y and q['paper'] == p for q in uq):
                    L.append(f'  - [UPSC Mains {y} GS Paper {upscmains.n_of(p)} ({upscmains.PAPERS[p][2]}) questions with model answers]({ub}{y}-gs{upscmains.n_of(p)}.html)')
    try: aq, _ = upscmains.load(SRC, 'an')   # UPSC Anthropology optional Papers I-II (same module, course 'an')
    except Exception: aq = []
    if aq:
        ab = f'{SITE_URL}/{upscmains.EXAM}/anthropology-pyqs/'
        L.append(f'- [UPSC Anthropology optional previous year questions with model answers, Papers I and II]({ab}): {len(aq):,} question parts of '
                 f'{min(q["year"] for q in aq)}–{max(q["year"] for q in aq)}, year-wise and syllabus-wise, each with a model answer on its own page '
                 f'(key words, anthropologists and ethnographic examples, diagrams); questions and all written model answers free (answers for 2019–2022 are being added).')
        for y in sorted({q['year'] for q in aq}, reverse=True):
            for p in upscmains.AN_PAPERS:
                if any(q['year'] == y and q['paper'] == p for q in aq):
                    L.append(f'  - [UPSC Anthropology {y} Paper {upscmains.n_of(p)} ({upscmains.AN_PAPERS[p][2]}) questions with model answers]({ab}{y}-paper-{upscmains.n_of(p)}.html)')
    npath_ = os.path.join(SRC, 'notes.json')
    books = json.load(open(npath_, encoding='utf-8')) if os.path.exists(npath_) else []
    ids = {c['id']: c for c in exams}
    bl = []
    for b in books:
        page = (ids[b['exams'][0]]['pb'] + 'notes/') if b.get('exams') and b['exams'][0] in ids else '/appsc-group-2/notes/'
        if b.get('exams') and b['exams'][0] not in ids: continue
        line = (f'- [{b.get("product_en") or b["product"]}]({SITE_URL}{page}): {b["pages"]}-page PDF by Jupudi Anil Kumar'
                + (f', {b["chapters_label"]}' if b.get('chapters_label') else '') + f'. Chapters: {"; ".join(b["chapters"])}. Included in the ₹{PAY["pyq_price"]} All-in-One Pass.')
        if b.get('free'): line += f' Free sample chapter (PDF, shareable): {SITE_URL}{b["free"]}'
        bl.append(line)
    if bl: L += ['', '## Study material (PDF books)'] + bl
    L += ['', '## Pages for each recruiting board']
    for rel, X in LANDINGS.items():
        if any(c['board'] == X['board'] for c in exams): L.append(f'- [{X["title"].split(" | ")[0]}]({SITE_URL}/{rel})')
    for rel, N in NOTIFS.items():
        if not N.get('exam') or any(c['id'] == N['exam'] for c in exams): L.append(f'- [{re.sub("<[^>]+>", "", N["h1"])}]({SITE_URL}/{rel})')
    L += ['', '## About', f'- [About Jupudi Anil Kumar]({SITE_URL}/appsc-group-2/about/): civil-services educator, 2.5 years of UPSC, APPSC and TGPSC teaching and mentorship.',
          f'- [Fund Learn with Anil]({SITE_URL}/funders.html): a one-person project built to be student-friendly and to democratise learning, with the goal of 1 lakh PYQs of various government exams under one roof for ₹45; Anil needs help from funders, which in turn helps him help the students.',
          f'- Instagram: https://www.instagram.com/{INSTAGRAM}/ · Telegram: https://t.me/learn_with_anil06 · YouTube: https://www.youtube.com/@learn_with_anil06', f'- Sitemap: {SITE_URL}/sitemap.xml', '']
    return '\n'.join(L)


GRIEVANCE_OFFICER = 'Jupudi Anil Kumar'
CONTACT_PHONE, CONTACT_EMAIL = '+91 94947 92739', 'anilkumarjupudi360360@gmail.com'


def help_page(loaded):
    """/help.html: Help & Grievance Redressal Cell (Anil, 25 Oct 2026). Common doubts answered first, then a complaint form that
    records a ticket in the private payments sheet ('grievances' tab), the grievance officer's contact details and the time limits
    of the Consumer Protection (E-Commerce) Rules, 2020 (acknowledge within 48 hours, redress within one month)."""
    can = SITE_URL + '/help.html'
    exams = ''.join(f'<option value="{c["id"]}">{esc(c["name"])}</option>' for c, _, _ in loaded)
    cats = ['Payment or All-in-One Pass', 'Mock test pack', 'A question or answer', 'Website not working', 'Refund', 'Other']
    faq = [
        ('I paid, but the All-in-One Pass or mock pack has not opened.',
         'Open any previous paper and tap "I have paid · check". The pass is linked to the mobile number and email you registered with, so use the same ones you paid with. One pass works on up to 3 phones or computers. If it still does not open, send the form below with the payment ID or order ID from your payment SMS or email (it starts with MOJO or LWA).'),
        ('Money was taken from my account, but the payment failed.',
         'A failed payment is returned automatically by the payment gateway and your bank, usually within 5–7 working days. If it is not back by then, send the form with the payment ID or the UPI reference number.'),
        ('I think an answer is wrong.',
         'Answers come from the official final key of the recruiting body. Where sources disagree, the explanation says so. Send the form with the paper and question number, and we will check it and reply.'),
        ('My test closed, or the page went back to the start.',
         'Practice papers ("Attempt this paper") never close by themselves: when the time is up, the extra time is shown in red and you can carry on. Timed tests and mock tests submit when the time is up, as in the real exam. A test in progress is kept on your device for 24 hours, so reopening the page brings you back to it.'),
        ('Refunds.',
         'If you paid and the pass or test pack does not work, and we cannot fix it within 7 days of your complaint, you get the full amount back to the account you paid from.'),
    ]
    faq_html = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq)
    body = f"""<p><b>We acknowledge every complaint within 48 hours and resolve it within 30 days</b> (most are sorted out within 3 working days).
Every complaint gets a ticket number, so you can refer to it later.</p>
<h2>Quick answers</h2>{faq_html}
<h2>Send a complaint or a doubt</h2>
<form id="gForm" class="buy" style="display:block" novalidate>
<p><label>Your name<br><input name="name" required maxlength="80" autocomplete="name" style="width:100%;padding:9px;font-size:16px"></label></p>
<p><label>Mobile number (the one you registered or paid with)<br><input name="phone" required inputmode="numeric" maxlength="14" autocomplete="tel" style="width:100%;padding:9px;font-size:16px"></label></p>
<p><label>Email (optional)<br><input name="email" type="email" maxlength="100" autocomplete="email" style="width:100%;padding:9px;font-size:16px"></label></p>
<p><label>Exam<br><select name="exam" style="width:100%;padding:9px;font-size:16px"><option value="site">Not about one exam</option>{exams}</select></label></p>
<p><label>What is it about?<br><select name="category" style="width:100%;padding:9px;font-size:16px">{''.join(f'<option>{esc(c)}</option>' for c in cats)}</select></label></p>
<p><label>Payment ID, if it is about a payment (optional)<br><input name="payment_id" maxlength="60" placeholder="MOJO…, LWA… or UPI reference" style="width:100%;padding:9px;font-size:16px"></label></p>
<p><label>Your complaint or doubt<br><textarea name="message" required maxlength="2000" rows="5" style="width:100%;padding:9px;font-size:16px"></textarea></label></p>
<p class="muted" style="font-size:14px">Your details are used only to answer this complaint.</p>
<button class="cta" type="submit" style="border:0;cursor:pointer;font-size:16px">Send</button>
<p id="gMsg" role="status" style="font-weight:600;margin:12px 0 0"></p>
</form>
<h2>Grievance officer</h2>
<p><b>{esc(GRIEVANCE_OFFICER)}</b>, Learn with Anil (learnwithanil.in)<br>
Email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br>
Phone / WhatsApp: <a href="tel:{CONTACT_PHONE.replace(' ', '')}">{CONTACT_PHONE}</a> (10 am – 7 pm, Monday to Saturday)</p>
<p>If you are not satisfied with our reply, you can also contact the National Consumer Helpline: call 1915 or visit <a href="https://consumerhelpline.gov.in/" rel="nofollow">consumerhelpline.gov.in</a>.</p>
<script>(function(){{var f=document.getElementById('gForm'),m=document.getElementById('gMsg');if(!f)return;
try{{var st=JSON.parse(localStorage.getItem('lwa-appsc-g2-student-v1')||'{{}}');['name','phone','email'].forEach(function(k){{if(st[k])f.elements[k].value=st[k];}});}}catch(e){{}}
f.addEventListener('submit',function(e){{e.preventDefault();var v={{}};['name','phone','email','exam','category','payment_id','message'].forEach(function(k){{v[k]=f.elements[k].value.trim();}});
if(!v.name||!/^[6-9]\\d{{9}}$/.test(v.phone.replace(/\\D/g,'').slice(-10))){{m.textContent='Please give your name and a valid 10-digit mobile number.';return;}}
if(v.message.length<10){{m.textContent='Please describe the problem in a sentence or two.';return;}}
var b=f.querySelector('button');b.disabled=true;m.textContent='Sending…';v.action='grievance';
fetch({json.dumps(PAY['api'])},{{method:'POST',headers:{{'Content-Type':'text/plain;charset=utf-8'}},body:JSON.stringify(v)}}).then(function(r){{return r.json();}}).then(function(r){{
if(r&&r.ok){{f.reset();m.textContent='Received. Your ticket number is '+r.ticket+'. We will reply within 48 hours on your phone or email.';}}else{{m.textContent=(r&&r.error)||'Could not send. Please WhatsApp {CONTACT_PHONE}.';b.disabled=false;}}
}}).catch(function(){{m.textContent='No connection. Please try again, or WhatsApp {CONTACT_PHONE}.';b.disabled=false;}});}});}})();</script>"""
    return static_page(0, 'Help & Grievance Redressal Cell | Learn with Anil', 'Help with payments, the All-in-One Pass, mock tests and answers on learnwithanil.in: quick answers, a complaint form with a ticket number, and the grievance officer\'s contact details.',
                       can, 'Help & Grievance Redressal Cell', esc('Questions about a payment, your All-in-One Pass, a mock test or an answer? Find a quick answer below, or send us a complaint.'),
                       body, [('Home', SITE_URL + '/'), ('Help & grievances', can)], None, ename='every exam', at_root=True)


def privacy_page():
    """/privacy.html: privacy policy (2 Nov 2026), written for the student accounts with "Sign in with Google": Google's consent
    screen links here. States what the site really collects (registration form, Google name and email, phone, sessions, payments
    through Instamojo or Cashfree Payments, test progress kept on the device, Google Analytics) and how a student can get it corrected or deleted."""
    can = SITE_URL + '/privacy.html'
    sec = [
        ('What we collect',
         '<ul><li><b>When you register:</b> your name, mobile number, email, district or city, and anything you choose to write in the help box.</li>'
         '<li><b>When you sign in with Google:</b> your name and email address from your Google account, and Google\'s account ID. We do not see '
         'your Google password and we do not get access to your Gmail, Drive, contacts or anything else in your Google account.</li>'
         '<li><b>When you are logged in:</b> a login record for each phone or computer (the type of device and browser, when you last used it), '
         'so that you can see your devices on the My Account page and log out of any of them. At most 3 devices stay logged in at a time.</li>'
         '<li><b>When you pay:</b> the payment is made on the secure page of our payment gateway (Instamojo or Cashfree Payments). We receive the payment ID, amount, date, and the name, phone and '
         'email given there. We never see or store your card, UPI or bank details.</li>'
         '<li><b>Complaints:</b> what you send through the help form.</li>'
         '<li><b>Visits:</b> pages visited are counted with Google Analytics, which uses cookies.</li></ul>'),
        ('What stays on your own device',
         '<p>Your attempts, scores, mistakes notebook and bookmarks are kept in your browser on your phone or computer. They are not sent to us, '
         'and clearing the browser\'s site data removes them.</p>'),
        ('Why we use it',
         '<p>Only to run the site for you: to open the All-in-One Pass and mock tests you paid for on your devices, keep you logged in, link a payment '
         'to your account, answer your questions and complaints, and help with your preparation if you asked for it. '
         'We do not sell or rent your details, and we do not use them for advertising.</p>'),
        ('Where it is kept and who can see it',
         '<p>Your details are kept in a private Google Sheet in Learn with Anil\'s Google account, which only Learn with Anil can open. '
         'They are shared only with the services that make the site work: Google (sign-in, storage and visit counts), Instamojo and Cashfree Payments (payments) and '
         'GitHub Pages (which hosts the site), or with the authorities when the law requires it.</p>'),
        ('How long we keep it',
         '<p>For as long as you have an account or a pass, and after that only as long as needed for payment records and the law. '
         'A login ends after 12 months, or earlier when you log out.</p>'),
        ('Your choices',
         '<p>You can see your profile, devices and payments on the <a href="/#account">My Account</a> page, and log out of any device there. '
         'To correct or delete your details or your account, write to the grievance officer below or use the <a href="/help.html">help form</a>; '
         'we do it within 30 days. You can also remove Learn with Anil\'s access to your Google account at any time at '
         '<a href="https://myaccount.google.com/connections" rel="nofollow">myaccount.google.com/connections</a>.</p>'),
        ('Contact',
         f'<p>Grievance officer: <b>{esc(GRIEVANCE_OFFICER)}</b>, Learn with Anil (learnwithanil.in)<br>Email: <a href="mailto:{CONTACT_EMAIL}">'
         f'{CONTACT_EMAIL}</a><br>Phone / WhatsApp: <a href="tel:{CONTACT_PHONE.replace(" ", "")}">{CONTACT_PHONE}</a></p>'
         '<p class="muted">If we change this policy, the new version will be posted on this page with its date.</p>'),
    ]
    body = '<p class="muted">Last updated: 4 November 2026</p>' + ''.join(f'<h2>{esc(h)}</h2>{t}' for h, t in sec)
    return static_page(0, 'Privacy Policy | Learn with Anil', 'What Learn with Anil (learnwithanil.in) collects when you register, sign in with Google or pay, why, where it is kept, and how to get it corrected or deleted.',
                       can, 'Privacy Policy', esc('What we collect when you register, sign in or pay, and what we do with it.'),
                       body, [('Home', SITE_URL + '/'), ('Privacy policy', can)], None, ename='every exam', at_root=True)


def terms_page():
    """/terms.html: terms of use (2 Nov 2026), linked from Google's sign-in consent screen. Plain terms that match how the site
    and the payments script work: the All-in-One Pass (price and 12 months from the payments config), 3 devices, refunds as on /help.html."""
    can = SITE_URL + '/terms.html'
    sec = [
        ('About the site',
         '<p>learnwithanil.in (Learn with Anil, run by Jupudi Anil Kumar) publishes previous year questions with answers and explanations, '
         'practice tests and mock tests for government recruitment exams. It is not affiliated with UPSC, APPSC, TGPSC, SSC, the police '
         'recruitment boards or any other recruiting body.</p>'),
        ('Your account',
         '<p>You can register with your phone number and email, or sign in with Google and add your phone number once. Please give correct '
         'details: your passes are linked to your phone number and email. Your account is for you alone; one account can stay logged in on '
         'up to 3 phones or computers at a time, and logging in on a fourth logs out the oldest one.</p>'),
        ('Passes and payments',
         f'<p>The All-in-One Pass costs ₹{PAY["pyq_price"]} and opens everything on the site (every previous paper with explanations, the mock '
         'test series and the study booklets, including exams added later) for 12 months from the date of payment. Some papers and '
         'mocks are free for registered students, as marked on the site. Payments are made through our payment gateways, Instamojo and Cashfree Payments. If you have paid but '
         'your pass has not opened, use "Link my payment" on the My Account page or the <a href="/help.html">help page</a>.</p>'),
        ('Refunds',
         '<p>If you paid and the pass or test pack does not work, and we cannot fix it within 7 days of your complaint, you get the full '
         'amount back to the account you paid from. A failed payment is returned by the payment gateway and your bank, usually within 5–7 working days. '
         'The full <a href="/refund.html">refund and cancellation policy</a> has the details.</p>'),
        ('Fair use',
         '<p>The explanations, model answers, mock tests and notes are Learn with Anil\'s work. Use them for your own preparation; do not copy, '
         'resell, or share your account or paid content with others.</p>'),
        ('Accuracy',
         '<p>Answers follow the official final keys of the recruiting bodies, and we take care to keep explanations correct. If you find a '
         'mistake, tell us through the <a href="/help.html">help page</a> and we will check it. Always confirm exam dates, rules and '
         'notifications on the recruiting body\'s official website.</p>'),
        ('Privacy',
         '<p>How we handle your details is explained in the <a href="/privacy.html">privacy policy</a>.</p>'),
        ('Contact',
         f'<p>{esc(GRIEVANCE_OFFICER)}, Learn with Anil · <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> · '
         f'<a href="tel:{CONTACT_PHONE.replace(" ", "")}">{CONTACT_PHONE}</a></p>'),
    ]
    body = '<p class="muted">Last updated: 4 November 2026</p>' + ''.join(f'<h2>{esc(h)}</h2>{t}' for h, t in sec)
    return static_page(0, 'Terms of Use | Learn with Anil', 'Terms of use of learnwithanil.in: accounts and sign-in, the All-in-One Pass and mock test packs, payments, refunds and fair use.',
                       can, 'Terms of Use', esc('The rules for accounts, passes and payments on learnwithanil.in.'),
                       body, [('Home', SITE_URL + '/'), ('Terms of use', can)], None, ename='every exam', at_root=True)



def _policy_page(fn, title, desc, h1, lede, crumb, sec):
    can = SITE_URL + '/' + fn
    body = '<p class="muted">Last updated: 4 November 2026</p>' + ''.join(f'<h2>{esc(h)}</h2>{t}' for h, t in sec)
    return static_page(0, title + ' | Learn with Anil', desc, can, h1, esc(lede), body, [('Home', SITE_URL + '/'), (crumb, can)], None,
                       ename='every exam', at_root=True)


def _contact_html():
    return (f'<p>{esc(GRIEVANCE_OFFICER)}, Learn with Anil (learnwithanil.in)<br>Email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br>'
            f'Phone / WhatsApp: <a href="tel:{CONTACT_PHONE.replace(" ", "")}">{CONTACT_PHONE}</a> (10 am – 7 pm, Monday to Saturday)<br>'
            'Complaint form: <a href="/help.html">Help &amp; grievances</a> (reply within 48 hours)</p>')


def refund_page():
    """/refund.html: refund and cancellation policy (4 Nov 2026), a page of its own because payment gateways (Cashfree) check for it
    during KYC. Same promise as the Refunds part of /terms.html and /help.html: full refund if a paid pass does not work and is not fixed
    within 7 days of the complaint; failed payments come back through the gateway and the bank."""
    price = PAY['pyq_price']
    return _policy_page('refund.html', 'Refund & Cancellation Policy',
        f'Refund and cancellation policy of learnwithanil.in: the ₹{price} All-in-One Pass, failed and double payments, and how to ask for a refund.',
        'Refund & Cancellation Policy', 'When you get your money back, and how to ask for it.', 'Refund policy', [
        ('What you buy',
         f'<p>The All-in-One Pass costs ₹{price}. It is a digital pass: it opens everything on learnwithanil.in (every previous paper with '
         'explanations, the mock test series and the study books) for 12 months, as soon as the payment is confirmed. Nothing is posted to you; '
         'see the <a href="/delivery.html">delivery policy</a>.</p>'),
        ('Cancellation',
         '<p>You can cancel at any time before paying by closing the payment page; nothing is charged. Because the pass opens the moment '
         'the payment is confirmed, a paid pass cannot be cancelled afterwards, except as below.</p>'),
        ('When you get a full refund',
         '<ul><li><b>The pass does not work.</b> If you paid and your pass does not open, and we cannot fix it within 7 days of your '
         'complaint, you get the full amount back.</li>'
         '<li><b>You paid twice for the same pass.</b> The extra payment is refunded in full.</li>'
         '<li><b>The payment failed but money was taken.</b> The payment gateway and your bank return it automatically, usually within '
         '5–7 working days. If it is not back by then, send us the payment ID or the UPI reference number.</li></ul>'),
        ('How a refund is paid',
         '<p>To the same UPI ID, card or bank account you paid from, within 7 working days of our decision. Your bank may take a few more '
         'working days to show it.</p>'),
        ('How to ask',
         '<p>Use the <a href="/help.html">help form</a> (choose "Refund"), email or WhatsApp us with your registered phone number and the '
         'payment ID or order ID from your payment SMS or email. Every request gets a ticket number and a reply within 48 hours.</p>'
         + _contact_html()),
    ])


def delivery_page():
    """/delivery.html: delivery (shipping) policy (4 Nov 2026). Everything sold is digital and opens on the site; payment gateways
    (Cashfree) ask for a shipping/delivery policy during KYC."""
    return _policy_page('delivery.html', 'Delivery Policy',
        'Delivery policy of learnwithanil.in: the All-in-One Pass is digital and opens online right after payment; nothing is shipped.',
        'Delivery Policy', 'How and when you get what you paid for.', 'Delivery policy', [
        ('Nothing is shipped',
         '<p>Everything on Learn with Anil is digital. We do not send any physical books or parcels, so there are no shipping charges.</p>'),
        ('When your pass opens',
         '<p>The All-in-One Pass is linked to the mobile number and email you registered with. It opens on the website as soon as the payment '
         'is confirmed, normally within a minute, on up to 3 phones or computers. The study books are PDF downloads on the site, opened by '
         'the same pass.</p>'),
        ('If it does not open',
         '<p>Open any previous paper and tap "I have paid · check", or enter the payment ID or order ID from your payment SMS or email under '
         '"Link my payment" on the <a href="/#account">My Account</a> page. If it still does not open, contact us and we will open it; '
         'see the <a href="/refund.html">refund policy</a> if we cannot.</p>' + _contact_html()),
    ])


def contact_page():
    """/contact.html: contact us (4 Nov 2026), a page of its own for payment gateway KYC (Cashfree); the same details as /help.html."""
    return _policy_page('contact.html', 'Contact Us',
        'Contact Learn with Anil (learnwithanil.in): email, phone and WhatsApp, and the complaint form.',
        'Contact Us', 'Questions about the site, a payment or your pass? Write or call us.', 'Contact', [
        ('Learn with Anil',
         f'<p>learnwithanil.in is run by {esc(GRIEVANCE_OFFICER)}.</p>' + _contact_html()),
        ('Payments and refunds',
         '<p>Please give your registered phone number and the payment ID or order ID from your payment SMS or email. See also the '
         '<a href="/refund.html">refund and cancellation policy</a>, the <a href="/delivery.html">delivery policy</a>, the '
         '<a href="/terms.html">terms of use</a> and the <a href="/privacy.html">privacy policy</a>.</p>'),
    ])

def funders_page(loaded):
    """/funders.html: Fund Learn with Anil (Anil, 26 Oct 2026). Goal: 1 lakh PYQs of various government exams under one roof for ₹45;
    Anil is the only person developing the site and needs help from funders, which in turn helps him help the students.
    Built in the start page's own style (app.html CSS, top bar, blue hero, figures, feature cards) with the EN / हिंदी / తెలుగు switch
    (remembered in localStorage 'lwa-lang', shared with the rest of the site). No money is taken through this page."""
    from urllib.parse import quote
    can = SITE_URL + '/funders.html'
    nq = sum(len(qs) for _, _, qs in loaded)
    nex = len(loaded)
    goal = 100000
    pct = min(100, nq * 100 / goal)
    NQ, PCT = f'{nq:,}', f'{pct:.0f}'
    # Applicants per exam on the site's exam list (src/exams.json, live and coming soon): src/reach.json, one entry per exam id with the
    # number who applied (or appeared, where that is the only published figure) in its latest recruitment, the cycle and the source.
    # Researched 26 Oct 2026 at Anil's request ("add all other exams' numbers that I mentioned on the website").
    catalog = json.load(open(os.path.join(ROOT, 'src', 'exams.json'), encoding='utf-8'))
    reach = json.load(open(os.path.join(ROOT, 'src', 'reach.json'), encoding='utf-8'))
    live_ids = {c['id'] for c, _, _ in loaded}
    UNITS = {'lakh': ('lakh', 'लाख', 'లక్షలు'), 'crore': ('crore', 'करोड़', 'కోట్లు')}
    def amount(n, floor=False):   # Indian units: 28,15,445 -> ('28.15', 'lakh'); 1,26,30,885 -> ('1.26', 'crore')
        import math
        for base, unit in ((10**7, 'crore'), (10**5, 'lakh')):
            if n >= base:
                v = n / base
                if floor: v = math.floor(v * 10) / 10
                return (f'{v:.1f}' if floor else f'{v:.2f}').rstrip('0').rstrip('.'), unit
        return f'{n:,}', ''
    def amount_lang(n, li, floor=False):
        v, u = amount(n, floor)
        return f'{v} {UNITS[u][li]}' if u else v
    nums = {k: r['applied'] for k, r in reach.items() if r.get('applied') and r.get('in_total', True)}   # IFoS shares the CSE prelims: shown, not added
    total = sum(nums.values())
    live_total = sum(v for k, v in nums.items() if k in live_ids)
    n_with = sum(1 for e in catalog['exams'] if reach.get(e['id'], {}).get('applied'))
    n_all = len(catalog['exams'])
    TOT = [amount_lang(total, li, True) for li in range(3)]
    LIVE_TOT = [amount_lang(live_total, li, True) for li in range(3)]
    wa = f'https://wa.me/{WHATSAPP}?text=' + quote('Hi Learn_with_anil Team, I am interested in funding Learn with Anil.')
    mail = f'mailto:{CONTACT_EMAIL}?subject=' + quote('Funding Learn with Anil')
    share = 'https://wa.me/?text=' + quote('Learn with Anil: 1 lakh PYQs of government exams under one roof, for ₹45. Anil is building it alone and needs funders: https://learnwithanil.in/funders')
    T = {
      'eyebrow': ('Fund Learn with Anil', 'Learn with Anil को सहयोग दें', 'Learn with Anil‌కు నిధులు ఇవ్వండి'),
      'h1': ('1 lakh PYQs under one roof, <em>for just ₹45.</em>', '1 लाख PYQs एक ही जगह, <em>सिर्फ़ ₹45 में।</em>', '1 లక్ష PYQs ఒకే చోట, <em>కేవలం ₹45కే.</em>'),
      'lede': ('That is the goal of Learn with Anil, along with a mock test series for every exam, all in the same ₹45 pass. I am building this website to be student-friendly and to democratise learning. '
               'I am the only person developing it, and I need help from funders: your support, in turn, helps me help the students.',
               'यही Learn with Anil का लक्ष्य है, साथ ही हर परीक्षा के लिए एक मॉक टेस्ट सीरीज़, सब उसी ₹45 पास में। मैं यह वेबसाइट विद्यार्थियों के अनुकूल बनाने और शिक्षा को सबके लिए सुलभ बनाने के लिए बना रहा हूँ। '
               'इसे बनाने वाला मैं अकेला व्यक्ति हूँ, और मुझे फंड देने वालों की मदद चाहिए: आपका सहयोग मुझे विद्यार्थियों की मदद करने में सहायता करता है।',
               'ఇదే Learn with Anil లక్ష్యం, దానితో పాటు ప్రతి పరీక్షకు ఒక మాక్ టెస్ట్ సిరీస్, అన్నీ అదే ₹45 పాస్‌లో. విద్యార్థులకు అనుకూలంగా, అందరికీ అందుబాటులో ఉండే చదువు కోసం నేను ఈ వెబ్‌సైట్‌ను నిర్మిస్తున్నాను. '
               'దీన్ని అభివృద్ధి చేస్తున్నది నేను ఒక్కడినే, అందుకే నాకు నిధులు ఇచ్చేవారి సహాయం కావాలి: మీ సహాయం, నేను విద్యార్థులకు సహాయం చేయడానికి తోడ్పడుతుంది.'),
      'wa': ('WhatsApp me', 'WhatsApp पर संपर्क करें', 'WhatsAppలో సంప్రదించండి'),
      'mail': ('Email me', 'ईमेल करें', 'ఈమెయిల్ చేయండి'),
      'mentor': ('Founder, Learn with Anil · UPSC faculty &amp; mentor', 'संस्थापक, Learn with Anil · UPSC शिक्षक और मार्गदर्शक', 'వ్యవస్థాపకులు, Learn with Anil · UPSC అధ్యాపకులు, మెంటార్'),
      'f1': ('Previous-year questions so far', 'अब तक के पिछले वर्षों के प्रश्न', 'ఇప్పటివరకు ఉన్న గత సంవత్సరాల ప్రశ్నలు'),
      'f2': ('The goal: 1 lakh PYQs + a mock test series for every exam', 'लक्ष्य: 1 लाख PYQs + हर परीक्षा के लिए मॉक टेस्ट सीरीज़', 'లక్ష్యం: 1 లక్ష PYQs + ప్రతి పరీక్షకు మాక్ టెస్ట్ సిరీస్'),
      'f3': ('Aspirants apply for these exams in one cycle', 'अभ्यर्थी एक भर्ती चक्र में इन परीक्षाओं के लिए आवेदन करते हैं', 'అభ్యర్థులు ఒక్క నియామక చక్రంలో ఈ పరీక్షలకు దరఖాస్తు చేస్తారు'),
      'reachT': ('How many students it can help', 'यह कितने विद्यार्थियों की मदद कर सकता है', 'ఇది ఎంతమంది విద్యార్థులకు ఉపయోగపడుతుంది'),
      'reachV': (TOT[0] + '+', TOT[1] + '+', TOT[2] + '+'),
      # letter to funders (Anil approved the English text, 26 Oct 2026 14:53 IST)
      'msgHi': ('Respected Sir/Madam,', 'आदरणीय महोदय/महोदया,', 'గౌరవనీయులైన అయ్యా/అమ్మా,'),
      'msgP1': ('Lakhs of aspirants in our towns and villages prepare for government jobs without the money for coaching. All they need is the real questions, the right answers and simple explanations, in their own language.',
                'हमारे कस्बों और गाँवों के लाखों अभ्यर्थी कोचिंग के पैसे के बिना सरकारी नौकरियों की तैयारी करते हैं। उन्हें बस असली प्रश्न, सही उत्तर और अपनी भाषा में सरल व्याख्याएँ चाहिए।',
                'మన పట్టణాలు, గ్రామాల్లో లక్షలాది అభ్యర్థులు కోచింగ్‌కు డబ్బు లేకుండానే ప్రభుత్వ ఉద్యోగాలకు సిద్ధమవుతున్నారు. వారికి కావలసింది అసలు ప్రశ్నలు, సరైన సమాధానాలు, తమ భాషలో సులభమైన వివరణలు మాత్రమే.'),
      'msgP2': (f'My dream: <b>1 lakh PYQs of every government exam, with a mock test series for each, under one roof for just ₹45 a year</b>, for the <b>{TOT[0]}+</b> aspirants who apply.',
                f'मेरा सपना: <b>हर सरकारी परीक्षा के 1 लाख PYQs, हर परीक्षा के लिए एक मॉक टेस्ट सीरीज़ के साथ, एक ही जगह, सिर्फ़ ₹45 प्रति वर्ष में</b>, आवेदन करने वाले <b>{TOT[1]}+</b> अभ्यर्थियों के लिए।',
                f'నా కల: <b>ప్రతి ప్రభుత్వ పరీక్షకు 1 లక్ష PYQs, ప్రతి పరీక్షకు ఒక మాక్ టెస్ట్ సిరీస్‌తో, ఒకే చోట, సంవత్సరానికి కేవలం ₹45కే</b>, దరఖాస్తు చేసే <b>{TOT[2]}+</b> అభ్యర్థుల కోసం.'),
      'msgP3': ('I am building this alone. <b>Your support, in turn, helps me help the students.</b> Please stand with me.',
                'मैं यह अकेले बना रहा हूँ। <b>आपका सहयोग मुझे विद्यार्थियों की मदद करने में सहायता करता है।</b> कृपया मेरा साथ दें।',
                'దీన్ని నేను ఒక్కడినే నిర్మిస్తున్నాను. <b>మీ సహాయం, నేను విద్యార్థులకు సహాయం చేయడానికి తోడ్పడుతుంది.</b> దయచేసి నాకు తోడుగా నిలవండి.'),
      'msgSig': ('Jupudi Anil Kumar, Founder, Learn with Anil', 'जुपुडी अनिल कुमार, संस्थापक, Learn with Anil', 'జూపూడి అనిల్ కుమార్, వ్యవస్థాపకులు, Learn with Anil'),
      'bigL': (f'applications from aspirants for the {n_all} government exams on my list, in a single recruitment cycle. That is how many students this work can reach.',
               f'मेरी सूची की {n_all} सरकारी परीक्षाओं के लिए एक ही भर्ती चक्र में अभ्यर्थियों के आवेदन। इतने विद्यार्थियों तक यह काम पहुँच सकता है।',
               f'నా జాబితాలోని {n_all} ప్రభుత్వ పరీక్షలకు ఒక్క నియామక చక్రంలో వచ్చే దరఖాస్తులు. ఇంతమంది విద్యార్థులకు ఈ పని చేరగలదు.'),
      'reachP': (f'Here is every exam on the Learn with Anil list, with the number of students who applied in its latest recruitment. The exams marked "Coming soon" will get their previous-year questions in future. '
                 f'Together, these exams draw <b>more than {TOT[0]} applications</b> in a single recruitment cycle, {LIVE_TOT[0]}+ of them for the {len(live_ids)} exams that are already live.',
                 f'यहाँ Learn with Anil की सूची की हर परीक्षा है, उसकी पिछली भर्ती में आवेदन करने वाले विद्यार्थियों की संख्या के साथ। "जल्द आ रहा है" वाली परीक्षाओं के पिछले वर्षों के प्रश्न आगे जोड़े जाएँगे। '
                 f'कुल मिलाकर, इन परीक्षाओं में एक ही भर्ती चक्र में <b>{TOT[1]} से अधिक आवेदन</b> आते हैं, जिनमें से {LIVE_TOT[1]}+ उन {len(live_ids)} परीक्षाओं के हैं जो पहले से उपलब्ध हैं।',
                 f'Learn with Anil జాబితాలోని ప్రతి పరీక్ష, దాని తాజా నియామకంలో దరఖాస్తు చేసిన విద్యార్థుల సంఖ్యతో ఇక్కడ ఉంది. "త్వరలో" అని ఉన్న పరీక్షల గత ప్రశ్నలు భవిష్యత్తులో చేరుస్తాం. '
                 f'మొత్తం కలిపి, ఈ పరీక్షలకు ఒక్క నియామక చక్రంలోనే <b>{TOT[2]}కు పైగా దరఖాస్తులు</b> వస్తాయి; వాటిలో {LIVE_TOT[2]}+ ఇప్పటికే అందుబాటులో ఉన్న {len(live_ids)} పరీక్షలవి.'),
      'applied': ('applied', 'आवेदन', 'దరఖాస్తులు'),
      'appeared': ('appeared', 'परीक्षा में बैठे', 'హాజరు'),
      'lakh': UNITS['lakh'], 'crore': UNITS['crore'],
      'live': ('Live', 'उपलब्ध', 'అందుబాటులో'),
      'soon': ('Coming soon', 'जल्द आ रहा है', 'త్వరలో'),
      'np': ('Number not published', 'संख्या प्रकाशित नहीं', 'సంఖ్య ప్రచురించలేదు'),
      'reachNote': (f'Numbers are for the latest recruitment with a published figure ({n_with} of {n_all} exams); "appeared" is shown, and counted, where only the number who sat the exam was published. '
                    'UPSC IFoS shares the Civil Services prelims, so it is not added again to the total. '
                    'Sources: official press notes, annual reports and RTI replies where available, otherwise news and education websites (listed below). An aspirant who applies for two exams is counted twice.',
                    f'संख्याएँ उस पिछली भर्ती की हैं जिसका आँकड़ा प्रकाशित हुआ है ({n_all} में से {n_with} परीक्षाएँ); जहाँ केवल परीक्षा में बैठने वालों की संख्या प्रकाशित हुई, वहाँ वही दी और गिनी गई है। '
                    'UPSC IFoS की प्रारंभिक परीक्षा सिविल सेवा के साथ होती है, इसलिए इसे कुल में दोबारा नहीं जोड़ा गया। '
                    'स्रोत: जहाँ उपलब्ध हों, आधिकारिक प्रेस नोट, वार्षिक रिपोर्ट और RTI उत्तर, अन्यथा समाचार और शिक्षा वेबसाइटें (नीचे सूची)। दो परीक्षाओं के लिए आवेदन करने वाले अभ्यर्थी को दो बार गिना गया है।',
                    f'సంఖ్యలు ప్రచురించిన తాజా నియామకానివి ({n_all}లో {n_with} పరీక్షలు); హాజరైన వారి సంఖ్య మాత్రమే ప్రచురించిన చోట అదే ఇచ్చి, లెక్కించాం. '
                    'UPSC IFoS ప్రిలిమ్స్ సివిల్ సర్వీసెస్‌తో కలిసే జరుగుతుంది, అందుకే మొత్తంలో మళ్లీ కలపలేదు. '
                    'ఆధారాలు: అందుబాటులో ఉన్నచోట అధికారిక ప్రెస్ నోట్లు, వార్షిక నివేదికలు, RTI సమాధానాలు; లేకపోతే వార్తా, విద్యా వెబ్‌సైట్లు (కింద జాబితా). రెండు పరీక్షలకు దరఖాస్తు చేసిన అభ్యర్థిని రెండుసార్లు లెక్కించాం.'),
      'srcT': ('Sources for every number', 'हर संख्या के स्रोत', 'ప్రతి సంఖ్యకు ఆధారం'),
      'expandT': ('Next: exams of other states too', 'आगे: दूसरे राज्यों की परीक्षाएँ भी', 'తరువాత: ఇతర రాష్ట్రాల పరీక్షలు కూడా'),
      'expandP': ('Learn with Anil will not stop at Andhra Pradesh, Telangana and the central exams. It will expand to the public service commission, police and other recruitment exams of other states too, '
                  'so that aspirants across India can find their exam here, all under the same ₹45 All-in-One Pass.',
                  'Learn with Anil आंध्र प्रदेश, तेलंगाना और केंद्रीय परीक्षाओं तक ही सीमित नहीं रहेगा। यह दूसरे राज्यों के लोक सेवा आयोग, पुलिस और अन्य भर्ती परीक्षाओं तक भी विस्तार करेगा, '
                  'ताकि पूरे भारत के अभ्यर्थियों को अपनी परीक्षा यहीं मिले, सब कुछ उसी ₹45 ऑल-इन-वन पास में।',
                  'Learn with Anil ఆంధ్రప్రదేశ్, తెలంగాణ, కేంద్ర పరీక్షల వద్దే ఆగిపోదు. ఇతర రాష్ట్రాల పబ్లిక్ సర్వీస్ కమిషన్, పోలీస్, ఇతర నియామక పరీక్షలకు కూడా విస్తరిస్తుంది, '
                  'తద్వారా దేశవ్యాప్తంగా అభ్యర్థులు తమ పరీక్షను ఇక్కడే, అదే ₹45 ఆల్-ఇన్-వన్ పాస్‌లో పొందగలరు.'),
      'f4': ('One pass for every exam, PYQs and mock tests · 12 months', 'हर परीक्षा, PYQs और मॉक टेस्ट के लिए एक पास · 12 महीने', 'అన్ని పరీక్షలు, PYQs, మాక్ టెస్ట్‌లకు ఒకే పాస్ · 12 నెలలు'),
      'progT': ('Progress to 1 lakh', '1 लाख की ओर प्रगति', '1 లక్ష వైపు ప్రగతి'),
      'progP': (f'So far: <b>{NQ}</b> of 1,00,000 questions ({PCT}%). Your support helps me reach the goal sooner.',
                f'अब तक: 1,00,000 में से <b>{NQ}</b> प्रश्न ({PCT}%)। आपका सहयोग मुझे लक्ष्य तक जल्दी पहुँचने में मदद करता है।',
                f'ఇప్పటివరకు: 1,00,000లో <b>{NQ}</b> ప్రశ్నలు ({PCT}%). మీ సహాయంతో లక్ష్యాన్ని త్వరగా చేరుకోగలను.'),
      'builtT': ('What is already built', 'अब तक क्या बना है', 'ఇప్పటికే ఏమి సిద్ధమైంది'),
      'b1t': ('Real papers, official answers', 'असली प्रश्न पत्र, आधिकारिक उत्तर', 'అసలు ప్రశ్నపత్రాలు, అధికారిక సమాధానాలు'),
      'b1p': (f'{NQ} previous-year questions from {nex} government exams, each with its answer (from the official key wherever one has been published) and a short explanation.',
              f'{nex} सरकारी परीक्षाओं के {NQ} पिछले वर्षों के प्रश्न, हर प्रश्न का उत्तर (जहाँ आधिकारिक कुंजी प्रकाशित हुई है, वहाँ उसी से) और एक संक्षिप्त व्याख्या के साथ।',
              f'{nex} ప్రభుత్వ పరీక్షల {NQ} గత సంవత్సరాల ప్రశ్నలు, ప్రతి ప్రశ్నకు సమాధానం (అధికారిక కీ ప్రచురించిన చోట దాని నుంచే) మరియు చిన్న వివరణతో.'),
      'b2t': ('In your language', 'आपकी भाषा में', 'మీ భాషలో'),
      'b2p': ('Questions and explanations in English, Telugu and Hindi (each exam in the languages of its own paper), on any phone.',
              'प्रश्न और व्याख्याएँ अंग्रेज़ी, तेलुगु और हिंदी में (हर परीक्षा उसके अपने प्रश्न पत्र की भाषाओं में), किसी भी फ़ोन पर।',
              'ప్రశ్నలు, వివరణలు ఇంగ్లీష్, తెలుగు, హిందీలో (ప్రతి పరీక్ష దాని ప్రశ్నపత్రం భాషల్లో), ఏ ఫోన్‌లోనైనా.'),
      'b3t': ('Prepare without a coaching fee', 'बिना कोचिंग फ़ीस के तैयारी', 'కోచింగ్ ఫీజు లేకుండా సన్నద్ధత'),
      'b3p': ('Topic-wise practice, timed mock tests and a mistakes notebook.', 'विषयवार अभ्यास, समयबद्ध मॉक टेस्ट और गलतियों की नोटबुक।', 'అంశాలవారీ ప్రాక్టీస్, సమయబద్ధ మాక్ టెస్ట్‌లు, తప్పుల నోట్‌బుక్.'),
      'b4t': ('Free to read, ₹45 to practise', 'पढ़ना मुफ़्त, अभ्यास ₹45 में', 'చదవడం ఉచితం, ప్రాక్టీస్ ₹45కే'),
      'b4p': ('Every question and its correct answer can be read for free, along with the explanations for the first 10 questions of every paper. One ₹45 All-in-One Pass, for 12 months, opens everything: every explanation, all the online practice and tests, every mock test series and the study books.',
              'हर प्रश्न और उसका सही उत्तर मुफ़्त में पढ़ा जा सकता है, साथ ही हर प्रश्न पत्र के पहले 10 प्रश्नों की व्याख्याएँ भी। एक ₹45 ऑल-इन-वन पास 12 महीनों के लिए सब कुछ खोल देता है: सभी व्याख्याएँ, सारा ऑनलाइन अभ्यास व टेस्ट, हर मॉक टेस्ट सीरीज़ और अध्ययन पुस्तकें।',
              'ప్రతి ప్రశ్న, దాని సరైన సమాధానం ఉచితంగా చదవొచ్చు; ప్రతి ప్రశ్నపత్రంలోని మొదటి 10 ప్రశ్నల వివరణలు కూడా ఉచితం. ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్‌తో 12 నెలల పాటు అన్నీ తెరుచుకుంటాయి: అన్ని వివరణలు, ఆన్‌లైన్ ప్రాక్టీస్, టెస్ట్‌లు, ప్రతి మాక్ టెస్ట్ సిరీస్, స్టడీ పుస్తకాలు.'),
      'whyT': ('Why the project needs funding', 'इस परियोजना को धन की ज़रूरत क्यों है', 'ఈ ప్రాజెక్ట్‌కు నిధులు ఎందుకు అవసరం'),
      'whyP': ('I am the only person developing Learn with Anil. Every paper has to be found, typed from the official question booklet, checked against the official answer key, explained and translated, and then kept up to date whenever the keys change. '
               'The website itself also has to be built and kept running. I keep the price at ₹45 so that every aspirant can afford it, which means that fees alone cannot pay for this work.',
               'Learn with Anil को बनाने वाला मैं अकेला व्यक्ति हूँ। हर प्रश्न पत्र को खोजना, आधिकारिक प्रश्न पुस्तिका से टाइप करना, आधिकारिक उत्तर कुंजी से मिलाना, समझाना और अनुवाद करना पड़ता है, और जब भी कुंजी बदले, उसे अपडेट रखना पड़ता है। '
               'वेबसाइट को भी बनाना और चलाते रहना पड़ता है। मैं कीमत ₹45 रखता हूँ ताकि हर अभ्यर्थी इसे ले सके, इसलिए सिर्फ़ फ़ीस से यह काम नहीं चल सकता।',
               'Learn with Anil‌ను అభివృద్ధి చేస్తున్నది నేను ఒక్కడినే. ప్రతి ప్రశ్నపత్రాన్ని వెతకాలి, అధికారిక ప్రశ్నాపత్రం నుంచి టైప్ చేయాలి, అధికారిక సమాధాన కీతో సరిచూడాలి, వివరణ రాయాలి, అనువదించాలి, కీ మారినప్పుడల్లా అప్‌డేట్ చేయాలి. '
               'వెబ్‌సైట్‌ను కూడా నిర్మించి, నడుపుతూ ఉండాలి. ప్రతి అభ్యర్థి కొనగలిగేలా ధరను ₹45గా ఉంచుతున్నాను, అందుకే కేవలం ఫీజులతో ఈ పని నడవదు.'),
      'helpT': ('What your support will help me do', 'आपका सहयोग मुझे क्या करने में मदद करेगा', 'మీ సహాయం దేనికి ఉపయోగపడుతుంది'),
      'h1t': ('Reach 1 lakh PYQs sooner', '1 लाख PYQs तक जल्दी पहुँचना', '1 లక్ష PYQsను త్వరగా చేరుకోవడం'),
      'h1p': ('Add the remaining government exams, including other states’ exams (state PSCs, police, SSC, banks, railways and defence), so that every aspirant finds their exam here.',
              'दूसरे राज्यों की परीक्षाओं समेत बाकी सरकारी परीक्षाएँ (राज्य PSC, पुलिस, SSC, बैंक, रेलवे और रक्षा) जोड़ना, ताकि हर अभ्यर्थी को यहाँ अपनी परीक्षा मिले।',
              'ఇతర రాష్ట్రాల పరీక్షలతో సహా మిగిలిన ప్రభుత్వ పరీక్షలను (రాష్ట్ర PSCలు, పోలీస్, SSC, బ్యాంకులు, రైల్వేలు, రక్షణ రంగం) చేర్చడం, తద్వారా ప్రతి అభ్యర్థికి తన పరీక్ష ఇక్కడ దొరుకుతుంది.'),
      'h2t': ('More explanations and translations', 'और व्याख्याएँ और अनुवाद', 'మరిన్ని వివరణలు, అనువాదాలు'),
      'h2p': ('Explain and translate more papers in English, Telugu and Hindi.', 'अंग्रेज़ी, तेलुगु और हिंदी में और प्रश्न पत्रों की व्याख्या और अनुवाद करना।', 'ఇంగ్లీష్, తెలుగు, హిందీలో మరిన్ని ప్రశ్నపత్రాలకు వివరణలు, అనువాదాలు.'),
      'h4t': ('A mock test series for every exam', 'हर परीक्षा के लिए मॉक टेस्ट सीरीज़', 'ప్రతి పరీక్షకు మాక్ టెస్ట్ సిరీస్'),
      'h4p': ('Write full-length mock tests in each exam’s own pattern, like Mission Khaki for TS Police SI and Mission CGL for SSC CGL, so that every aspirant can practise for their exam, not just read old papers.',
              'हर परीक्षा के अपने पैटर्न में पूरी लंबाई के मॉक टेस्ट तैयार करना, जैसे TS पुलिस SI के लिए Mission Khaki और SSC CGL के लिए Mission CGL, ताकि हर अभ्यर्थी केवल पुराने प्रश्न पत्र पढ़े नहीं, अपनी परीक्षा का अभ्यास भी करे।',
              'ప్రతి పరీక్ష సొంత నమూనాలో పూర్తి నిడివి మాక్ టెస్ట్‌లు రాయడం, TS పోలీస్ SIకి Mission Khaki, SSC CGLకి Mission CGL లాగా, తద్వారా ప్రతి అభ్యర్థి పాత ప్రశ్నపత్రాలు చదవడమే కాకుండా తన పరీక్షకు ప్రాక్టీస్ కూడా చేయగలరు.'),
      'h3t': ('Keep it at ₹45', 'कीमत ₹45 ही रखना', 'ధర ₹45గానే ఉంచడం'),
      'h3p': ('Keep everything (every PYQ, every mock test series and the study books) in one ₹45 pass, within reach of every student.', 'सब कुछ (हर PYQ, हर मॉक टेस्ट सीरीज़ और अध्ययन पुस्तकें) एक ही ₹45 पास में रखना, हर विद्यार्थी की पहुँच में।', 'అన్నింటినీ (ప్రతి PYQ, ప్రతి మాక్ టెస్ట్ సిరీస్, స్టడీ పుస్తకాలు) ఒకే ₹45 పాస్‌లో ఉంచడం, ప్రతి విద్యార్థికి అందుబాటులో.'),
      'whoT': ('Who can fund', 'कौन सहयोग कर सकता है', 'ఎవరు నిధులు ఇవ్వవచ్చు'),
      'whoP': ('I welcome support from individuals, alumni, teachers, institutions, companies and foundations who believe that good exam preparation should not depend on how much a student can pay. '
               'Support can take the form of a grant, a sponsorship or a partnership, and I will work out the details with you.',
               'मैं उन व्यक्तियों, पूर्व छात्रों, शिक्षकों, संस्थानों, कंपनियों और फ़ाउंडेशनों के सहयोग का स्वागत करता हूँ जो मानते हैं कि अच्छी परीक्षा तैयारी इस पर निर्भर नहीं होनी चाहिए कि विद्यार्थी कितना खर्च कर सकता है। '
               'सहयोग अनुदान, प्रायोजन या साझेदारी के रूप में हो सकता है, और विवरण मैं आपके साथ मिलकर तय करूँगा।',
               'మంచి పరీక్షా సన్నద్ధత విద్యార్థి ఎంత ఖర్చు చేయగలడనే దానిపై ఆధారపడకూడదని నమ్మే వ్యక్తులు, పూర్వ విద్యార్థులు, ఉపాధ్యాయులు, సంస్థలు, కంపెనీలు, ఫౌండేషన్ల సహాయాన్ని స్వాగతిస్తున్నాను. '
               'సహాయం గ్రాంట్, స్పాన్సర్‌షిప్ లేదా భాగస్వామ్య రూపంలో ఉండవచ్చు; వివరాలను మీతో కలిసి నిర్ణయిస్తాను.'),
      'contactT': ('Get in touch', 'संपर्क करें', 'సంప్రదించండి'),
      'founder': ('Founder, Learn with Anil', 'संस्थापक, Learn with Anil', 'వ్యవస్థాపకులు, Learn with Anil'),
      'hours': ('10 am – 7 pm, Monday to Saturday', 'सुबह 10 बजे – शाम 7 बजे, सोमवार से शनिवार', 'ఉదయం 10 – సాయంత్రం 7, సోమవారం నుంచి శనివారం'),
      'note': ('Please do not send money to anyone who claims to be collecting it for me. I agree on every contribution directly with you, in writing.',
               'कृपया किसी ऐसे व्यक्ति को पैसे न भेजें जो मेरे नाम पर पैसे इकट्ठा करने का दावा करे। हर सहयोग मैं सीधे आपके साथ, लिखित रूप में तय करता हूँ।',
               'నా తరఫున డబ్బు వసూలు చేస్తున్నామని చెప్పే ఎవరికీ డబ్బు పంపవద్దు. ప్రతి సహాయాన్ని నేరుగా మీతో, లిఖితపూర్వకంగా ఒప్పందం చేసుకుంటాను.'),
      'shareT': ('Help spread the word', 'यह बात आगे बढ़ाएँ', 'ఈ విషయాన్ని అందరికీ తెలియజేయండి'),
      'shareP': ('Share this page or the poster with someone who might want to help.', 'यह पेज या पोस्टर किसी ऐसे व्यक्ति के साथ साझा करें जो मदद करना चाहे।', 'సహాయం చేయాలనుకునే వారితో ఈ పేజీని లేదా పోస్టర్‌ను పంచుకోండి.'),
      'shareWa': ('Share on WhatsApp', 'WhatsApp पर साझा करें', 'WhatsAppలో పంచుకోండి'),
      'poster': ('Download the poster', 'पोस्टर डाउनलोड करें', 'పోస్టర్ డౌన్‌లోడ్ చేయండి'),
      'aboutT': ('About me', 'मेरे बारे में', 'నా గురించి'),
      'aboutP': ('I am Jupudi Anil Kumar, a civil-services educator with 2.5 years of teaching and mentorship for UPSC, APPSC and TGPSC aspirants. Learn with Anil is my independent initiative.',
                 'मैं जुपुडी अनिल कुमार हूँ, एक सिविल सेवा शिक्षक। मैंने 2.5 वर्षों तक UPSC, APPSC और TGPSC अभ्यर्थियों को पढ़ाया और उनका मार्गदर्शन किया है। Learn with Anil मेरी स्वतंत्र पहल है।',
                 'నేను జూపూడి అనిల్ కుమార్, సివిల్ సర్వీసెస్ అధ్యాపకుడిని. UPSC, APPSC, TGPSC అభ్యర్థులకు 2.5 సంవత్సరాలుగా బోధన, మెంటార్‌షిప్ అందిస్తున్నాను. Learn with Anil నా స్వతంత్ర కార్యక్రమం.'),
      'aboutL': ('Read more about me', 'मेरे बारे में और पढ़ें', 'నా గురించి మరింత చదవండి'),
    }
    def t(k, tag='span', attrs=''):
        return f'<{tag} data-t="{k}"{(" " + attrs) if attrs else ""}>{T[k][0]}</{tag}>'
    ic = {   # the start page's feature-card icons
      'doc': '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5"/><path d="M9 14l2 2 4-4"/>',
      'lang': '<path d="M4 5h9M8.5 3v2M6 5c1 4 4 7 7 8M11 5c-1 4-4 7-7 8"/><path d="M13 21l4-9 4 9M14.5 18h5"/>',
      'loop': '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v5h-5"/><path d="M9 12l2 2 4-4"/>',
      'rupee': '<path d="M7 4h11M7 9h11M7 4c5 0 7 2 7 5s-3 5-7 5l8 6"/>',
      'up': '<path d="M4 18l6-6 4 4 6-8"/><path d="M15 8h5v5"/>',
      'heart': '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    }
    def svg(k): return f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ic[k]}</svg>'
    def card(k, a, b): return f'<div class="card feature"><span class="ic">{svg(k)}</span><span>{t(a, "h3")}{t(b, "p")}</span></div>'
    def ename(e): return e['t'] if e['t'].startswith(e['b']) else f"{e['b']} {e['t']}"
    def cell(e):
        r = reach.get(e['id'], {})
        chip = f'<span class="chip live">{t("live")}</span>' if e['id'] in live_ids else f'<span class="chip">{t("soon")}</span>'
        if r.get('applied'):
            v, u = amount(r['applied'])
            yr = (re.search(r'(19|20)\d\d', r.get('cycle', '')) or [''])[0]
            return (f'<div><span class="v">{v}{(" " + t(u)) if u else ""}</span><span class="n">{esc(ename(e))}</span>'
                    f'<span class="y">{yr}{" · " if yr else ""}{t(r.get("kind", "applied"))}</span>{chip}</div>')
        return f'<div><span class="v np">{t("np")}</span><span class="n">{esc(ename(e))}</span>{chip}</div>'
    reach_cells = ''
    for cid, cname in catalog['cats'].items() if isinstance(catalog['cats'], dict) else [(c['id'], c['name']) for c in catalog['cats']]:
        ex = [e for e in catalog['exams'] if e['cat'] == cid]
        ex.sort(key=lambda e: (e['id'] not in live_ids, -(reach.get(e['id'], {}).get('applied') or 0)))
        sub = sum(nums.get(e['id'], 0) for e in ex)
        reach_cells += (f'<h3 class="reach-cat">{esc(cname)} <span>{(amount(sub)[0] + " " + (t(amount(sub)[1]) if amount(sub)[1] else "")) if sub else ""}</span></h3>'
                        f'<div class="reach-grid">{"".join(cell(e) for e in ex)}</div>')
    srcs = ''.join(f'<li>{esc(ename(e))}: <a href="{esc(reach[e["id"]]["source"])}" rel="nofollow noopener" target="_blank">{esc(reach[e["id"]].get("source_name") or "source")}</a> ({esc(reach[e["id"]].get("cycle", ""))})</li>'
                   for e in catalog['exams'] if reach.get(e['id'], {}).get('applied') and reach[e['id']].get('source'))
    nav = ''.join(f'<a href="{c["pb"]}">{esc(c["short"])}</a>' for c, _, _ in loaded)
    app = open(os.path.join(ROOT, 'tools', 'app.html'), encoding='utf-8').read()
    css = app[app.index('<style>') + 7: app.index('</style>')]
    title = 'Fund Learn with Anil – 1 Lakh PYQs Under One Roof for ₹45 + Mock Tests for Every Exam'
    desc = ('Fund Learn with Anil, a one-person project with one goal: 1 lakh previous-year questions (PYQs) of various government exams under one roof '
            f'with answers and explanations, plus a mock test series for every exam, all for ₹45, for the {TOT[0]}+ aspirants who apply for these exams, expanding to other states. Individuals and organisations can sponsor or partner.')
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": can, "image": SITE_URL + '/og-funders.jpg', "inLanguage": ["en", "hi", "te"],
          "keywords": "fund education India, sponsor students, support free exam preparation, government exam PYQs, Learn with Anil, democratise learning",
          "about": {"@type": "EducationalOrganization", "name": "Learn with Anil", "url": SITE_URL + '/', "founder": {"@type": "Person", "name": "Jupudi Anil Kumar"}},
          "isPartOf": {"@type": "WebSite", "name": "Learn with Anil", "url": SITE_URL + '/'},
          "author": {"@type": "Person", "name": "Jupudi Anil Kumar", "url": SITE_URL + '/appsc-group-2/about/'},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + '/'},
              {"@type": "ListItem", "position": 2, "name": "Fund Learn with Anil", "item": can}]}}
    tj = json.dumps({k: {'en': v[0], 'hi': v[1], 'te': v[2]} for k, v in T.items()}, ensure_ascii=False).replace('</', '<\\/')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{can}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Learn with Anil"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{can}"><meta property="og:image" content="{SITE_URL}/og-funders.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Learn with Anil: 1 lakh PYQs under one roof, for ₹45"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Source+Sans+3:wght@400;500;600;700&family=Noto+Sans+Telugu:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap">
<style>{css}
.fund-bar{{background:var(--surface-2);border-radius:999px;height:14px;overflow:hidden;border:1px solid var(--line)}}
.fund-bar i{{display:block;height:100%;background:var(--accent);border-radius:999px}}
.fund-box{{padding:20px 22px;display:flex;flex-direction:column;gap:12px}}
.fund-box p{{max-width:75ch}}
.fund-note{{border-left:4px solid var(--accent);background:var(--accent-soft);border-radius:10px;padding:12px 14px;font-size:15px}}
.fund-poster{{display:block;width:100%;max-width:720px;height:auto;border-radius:var(--r);border:1px solid var(--line)}}
.hero .mentor b{{display:block}}
.fund-letter{{border-left:5px solid #FFD54A;font-size:17.5px;line-height:1.65;background:linear-gradient(180deg,var(--accent-soft),var(--surface) 60%)}}.fund-letter .hi{{font-weight:700;font-size:19px}}.fund-letter .sig{{font-family:var(--f-display);font-weight:700;color:var(--accent-text)}}
.bigstat{{display:flex;flex-direction:column;gap:2px;border-left:4px solid #FFD54A;padding:4px 0 4px 14px}}
.hero .bigstat b{{font-family:var(--f-display);font-weight:800;font-size:clamp(40px,7vw,64px);line-height:1;color:#FFD54A;letter-spacing:-.02em}}
.hero .bigstat span{{color:var(--band-ink);font-size:16px;max-width:52ch}}
.reach-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--surface)}}
.reach-grid>div{{background:var(--surface);padding:14px 16px;display:flex;flex-direction:column;gap:2px;box-shadow:inset -1px -1px 0 var(--line)}}
.reach-grid .v{{font-family:var(--f-display);font-weight:800;font-size:24px;line-height:1.15}}
.reach-grid .v.np{{font-size:15px;font-weight:600;color:var(--muted);font-family:var(--f-body)}}
.reach-grid .n{{font-weight:700}}.reach-grid .y{{font-size:13.5px;color:var(--muted)}}
.reach-grid .chip{{align-self:flex-start;margin-top:6px;font-size:12px;font-weight:700;border-radius:999px;padding:2px 9px;background:var(--none-soft);color:var(--muted)}}
.reach-grid .chip.live{{background:var(--good-soft);color:var(--good)}}
.reach-cat{{font-size:17px;font-weight:800;margin-top:6px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}}.reach-cat span{{color:var(--accent-text);font-family:var(--f-display)}}
.reach-src summary{{cursor:pointer;font-weight:700;color:var(--accent-text)}}.reach-src ul{{margin:10px 0 0;padding-left:20px;font-size:14px;color:var(--muted)}}.reach-src li{{margin:3px 0}}
</style>
{ICONS}{ga_tag()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Learn with Anil, all exams">
      <span class="brand-mark" aria-hidden="true">LA</span>
      <span class="brand-text"><b>Learn with Anil</b> <span>PYQs for every exam</span></span>
    </a>
    <nav class="nav hub" aria-label="Main"><a href="/">All Exams</a>{nav}<a href="/funders.html" aria-current="page">Fund</a></nav>
    <div class="lang" role="group" aria-label="Page language">
      <button type="button" data-l="en" aria-pressed="true">EN</button>
      <button type="button" data-l="hi" lang="hi" aria-pressed="false">हिंदी</button>
      <button type="button" data-l="te" lang="te" aria-pressed="false">తెలుగు</button>
    </div>
  </div>
</header>
<main>
  <section class="hero"><div class="wrap">
    <div class="hero-copy">
      {t('eyebrow', 'p', 'class="eyebrow"')}
      {t('h1', 'h1')}
      {t('lede', 'p')}
      <p class="bigstat">{t('reachV', 'b')}{t('bigL', 'span')}</p>
      <div class="row"><a class="btn btn-primary" href="{wa}" target="_blank" rel="noopener">{t('wa')}</a><a class="btn btn-secondary" href="{mail}">{t('mail')}</a></div>
    </div>
    <a class="mentor" href="/appsc-group-2/about/" style="color:inherit;text-decoration:none">
      <span class="ph"><img src="/anil.jpg" alt="Jupudi Anil Kumar" width="210" height="210"></span>
      <span><b>Jupudi Anil Kumar</b>{t('mentor')}</span>
    </a>
  </div></section>

  <section class="wrap section hub-figs" id="letter">
    <div class="card fund-box fund-letter">
      {t('msgHi', 'p', 'class="hi"')}
      {t('msgP1', 'p')}
      {t('msgP2', 'p')}
      {t('msgP3', 'p')}
      <p class="sig">— {t('msgSig')}</p>
      <div class="row"><a class="btn btn-primary" href="{wa}" target="_blank" rel="noopener">{t('wa')}</a><a class="btn btn-secondary" href="{mail}">{t('mail')}</a></div>
    </div>
  </section>

  <section class="wrap section" id="why">
    <div class="section-title">{t('whyT', 'h2')}</div>
    <div class="card fund-box">{t('whyP', 'p')}</div>
  </section>

  <section class="wrap section">
    <div class="figures">
      <div class="figure"><div class="v">{NQ}</div>{t('f1', 'div', 'class="k"')}</div>
      <div class="figure"><div class="v">1,00,000</div>{t('f2', 'div', 'class="k"')}</div>
      <div class="figure">{t('reachV', 'div', 'class="v"')}{t('f3', 'div', 'class="k"')}</div>
      <div class="figure"><div class="v">₹45</div>{t('f4', 'div', 'class="k"')}</div>
    </div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('reachT', 'h2')}</div>
    <div class="card fund-box">{t('reachP', 'p')}
      {reach_cells}
      {t('reachNote', 'p', 'class="muted" style="font-size:14px"')}
      <details class="reach-src"><summary>{t('srcT')}</summary><ul>{srcs}</ul></details>
    </div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('expandT', 'h2')}</div>
    <div class="card fund-box">{t('expandP', 'p')}</div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('progT', 'h2')}</div>
    <div class="card fund-box">
      <div class="fund-bar" role="img" aria-label="{NQ} of 1,00,000 questions so far"><i style="width:{max(pct, 1.5):.1f}%"></i></div>
      {t('progP', 'p', 'class="muted"')}
    </div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('builtT', 'h2')}</div>
    <div class="features">{card('doc', 'b1t', 'b1p')}{card('lang', 'b2t', 'b2p')}{card('loop', 'b3t', 'b3p')}{card('rupee', 'b4t', 'b4p')}</div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('helpT', 'h2')}</div>
    <div class="features">{card('up', 'h1t', 'h1p')}{card('loop', 'h4t', 'h4p')}{card('lang', 'h2t', 'h2p')}{card('heart', 'h3t', 'h3p')}</div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('whoT', 'h2')}</div>
    <div class="card fund-box">{t('whoP', 'p')}</div>
  </section>

  <section class="wrap section" id="contact">
    <div class="section-title">{t('contactT', 'h2')}</div>
    <div class="card fund-box">
      <p><b>{esc(GRIEVANCE_OFFICER)}</b>, {t('founder')}<br>
      Email: <a href="{mail}">{CONTACT_EMAIL}</a><br>
      Phone / WhatsApp: <a href="tel:{CONTACT_PHONE.replace(' ', '')}">{CONTACT_PHONE}</a> ({t('hours')})</p>
      <div class="row"><a class="btn btn-primary" href="{wa}" target="_blank" rel="noopener">{t('wa')}</a><a class="btn btn-secondary" href="{mail}">{t('mail')}</a></div>
      {t('note', 'p', 'class="fund-note"')}
    </div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('shareT', 'h2')}</div>
    <div class="card fund-box">
      {t('shareP', 'p', 'class="muted"')}
      <img class="fund-poster" src="/og-funders.jpg" data-lsrc-en="/og-funders.jpg" data-lsrc-hi="/og-funders-hi.jpg" data-lsrc-te="/og-funders-te.jpg" alt="Learn with Anil: 1 lakh PYQs under one roof, for ₹45, plus a mock test series for every exam. Fund this project." width="1200" height="630" loading="lazy">
      <div class="row"><a class="btn btn-primary" href="{share}" target="_blank" rel="noopener">{t('shareWa')}</a><a class="btn btn-secondary" href="/og-funders.jpg" data-lhref-en="/og-funders.jpg" data-lhref-hi="/og-funders-hi.jpg" data-lhref-te="/og-funders-te.jpg" download="LearnWithAnil-Fund-poster.jpg">{t('poster')}</a></div>
    </div>
  </section>

  <section class="wrap section">
    <div class="section-title">{t('aboutT', 'h2')}</div>
    <div class="card fund-box"><p>{t('aboutP')} <a href="/appsc-group-2/about/">{t('aboutL')}</a></p></div>
  </section>
</main>
<footer class="foot">
  <div class="wrap">
    <span><b>Learn with Anil</b> · <a href="/">LearnWithAnil.in</a>: previous year questions with answers for every exam. Not affiliated with APPSC, TGPSC, UPSC, SSC or any recruiting body. Visits are counted with Google Analytics. <a href="/exam-notifications.html">Exam notifications</a> · <a href="/appsc-pyqs.html">APPSC PYQs</a> · <a href="/ts-police-pyqs.html">TS Police PYQs</a> · <a href="/ap-police-pyqs.html">AP Police PYQs</a> · <a href="/help.html">Help &amp; grievances</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a> · <a href="/refund.html">Refunds</a> · <a href="/delivery.html">Delivery</a> · <a href="/contact.html">Contact</a> · <a href="/funders.html">Fund this project</a></span>
  </div>
</footer>
<script>(function(){{var T={tj};
function apply(l){{document.documentElement.lang=l;document.querySelectorAll('[data-t]').forEach(function(el){{var x=T[el.getAttribute('data-t')];if(!x)return;el.innerHTML=x[l]||x.en;if(l==='en')el.removeAttribute('lang');else el.setAttribute('lang',l);}});
document.querySelectorAll('.lang button').forEach(function(b){{b.setAttribute('aria-pressed',String(b.getAttribute('data-l')===l));}});
document.querySelectorAll('[data-lsrc-'+l+']').forEach(function(e){{e.src=e.getAttribute('data-lsrc-'+l);}});document.querySelectorAll('[data-lhref-'+l+']').forEach(function(e){{e.href=e.getAttribute('data-lhref-'+l);}});}}
document.querySelectorAll('.lang button').forEach(function(b){{b.addEventListener('click',function(){{var l=b.getAttribute('data-l');apply(l);try{{localStorage.setItem('lwa-lang',l);}}catch(e){{}}}});}});
try{{var g=localStorage.getItem('lwa-lang');if(g==='hi'||g==='te')apply(g);}}catch(e){{}}}})();</script>
</body>
</html>
"""


LANDINGS = {
  # file: what the page covers. People search "APPSC PYQs", "TS police previous papers", "TSLPRB previous question papers" ...
  'appsc-pyqs.html': dict(
      board='APPSC', ename='APPSC', crumb='APPSC PYQs',
      title='APPSC Previous Year Question Papers with Answers – Group 1, Group 2, AMVI, Endowment Officer, Analyst, Environmental Engineer, ASO & FRO PYQs | Learn with Anil',
      desc='All APPSC previous year question papers in one place: Group 1 Prelims 2019–2024, Group 2 Prelims & Mains 2019–2025 AMVI (Assistant Motor Vehicle Inspector) 2019, 2023 & 2026, Endowment Officer (EO Grade-III) 2022–2026, Analyst Grade-II 2025, Assistant Environmental Engineer 2025, Assistant Statistical Officer (ASO) ' + aso_years().replace(' and ', ' & ') + ' and Forest Range Officer (FRO) 2020 & 2023, '
           '{n} questions with final-key answers and explanations in English and Telugu. Practise them online with answers and explanations with one ₹45 All-in-One Pass for every exam.',
      h1='APPSC previous year question papers with answers',
      lede="Every APPSC Group 1, Group 2, AMVI, Endowment Officer (EO Grade-III), Analyst Grade-II, Assistant Environmental Engineer, Assistant Statistical Officer (ASO) and Forest Range Officer previous question paper on Learn with Anil, {n} questions in all. "
           "Answers come from APPSC's official final keys, and every question has a short explanation, in English and Telugu (AMVI Automobile Engineering, Analyst Paper II, Environmental Engineer Paper II and FRO General Forestry papers in English).",
      intro='<p>Looking for AP Group 2 or AP Group 1 previous papers, APPSC AMVI (Assistant Motor Vehicle Inspector) or Endowment Officer (EO Grade-III) previous papers, APPSC old question papers with the key, or an APPSC mock test? '
            'They are all here: open a paper to see its questions, or practise it online with answers and explanations.</p>'
            '<p lang="te">APPSC గ్రూప్ 1, గ్రూప్ 2 మునుపటి సంవత్సరం ప్రశ్నపత్రాలు (పాత ప్రశ్నాపత్రాలు) అధికారిక ఫైనల్ కీ సమాధానాలు, వివరణలతో — ప్రాక్టీస్ క్విజ్‌లు, మాక్ టెస్ట్‌లు; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.</p>'
            '<p class="note">New: <a href="/appsc-group-2-notification-2026.html">APPSC Group 2 Notification 2026</a> (686 posts, apply 10–30 November) and '
            '<a href="/appsc-group-1-notification-2026.html">APPSC Group 1 Notification 2026</a> (166 posts, last date extended to 9 November 2026) and '
            '<a href="/appsc-eo-grade-3-notification-2026.html">APPSC EO Grade-III Notification 2026</a> (104 Endowments Executive Officer posts, apply by 5 November), '
            '<a href="/appsc-analyst-grade-2-notification-2026.html">Analyst Grade-II Notification 2026</a> (18 Pollution Control Board posts, apply by 2 November) and '
            '<a href="/appsc-fro-notification-2026.html">FRO Notification 2026</a> (5 Forest Range Officer posts, apply by 5 November) and '
            '<a href="/appsc-assistant-environmental-engineer-notification-2026.html">Assistant Environmental Engineer Notification 2026</a> (41 Pollution Control Board posts). Timed mock tests: '
            '<a href="/appsc-group-2/mock-test.html">Group 2</a> · <a href="/appsc-group-1/mock-test.html">Group 1</a>.</p>',
      te={'Group-I': 'APPSC గ్రూప్-1 ప్రశ్నాపత్రాలు', 'Group-II': 'APPSC గ్రూప్-2 ప్రశ్నాపత్రాలు', 'APPSC AMVI': 'APPSC AMVI ప్రశ్నాపత్రాలు', 'APPSC EO Grade-III': 'APPSC దేవాదాయ శాఖ EO గ్రేడ్-III ప్రశ్నాపత్రాలు', 'APPSC Analyst Grade-II': 'APPSC అనలిస్ట్ గ్రేడ్-II ప్రశ్నాపత్రాలు', 'APPSC Asst. Environmental Engineer': 'APPSC అసిస్టెంట్ ఎన్విరాన్‌మెంటల్ ఇంజనీర్ ప్రశ్నాపత్రాలు', 'APPSC ASO': 'APPSC అసిస్టెంట్ స్టాటిస్టికల్ ఆఫీసర్ (ASO) ప్రశ్నాపత్రాలు', 'APPSC FRO': 'APPSC ఫారెస్ట్ రేంజ్ ఆఫీసర్ ప్రశ్నాపత్రాలు'},
      order=lambda c: {'Group-I': 0, 'Group-II': 1, 'APPSC EO Grade-III': 3, 'APPSC Analyst Grade-II': 4, 'APPSC Asst. Environmental Engineer': 5, 'APPSC ASO': 6, 'APPSC FRO': 7}.get(c['short'], 2)),   # Group-I, Group-II, AMVI, then EO Grade-III
  'ts-police-pyqs.html': dict(
      board='TSLPRB', ename='TS Police', crumb='TS Police PYQs',
      title='TS Police Previous Question Papers with Answers – SI & Constable PYQs (TSLPRB / TGPRB), English & Telugu | Learn with Anil',
      desc='Telangana Police SI and Constable previous question papers in one place: TSLPRB Preliminary Written Test and Final Written Examination papers from 2016 to 2023, '
           '{n} questions with answers from TSLPRB\'s keys and explanations in English and Telugu. Practise them online with answers and explanations with one ₹45 All-in-One Pass for every exam.',
      h1='TS Police SI & Constable previous question papers with answers',
      lede="Every Telangana Police SI and Constable question paper on Learn with Anil, {n} questions in all. "
           "Answers come from TSLPRB's keys (the final key wherever it could be found), and every question has a short explanation, in English and Telugu.",
      intro='<p>Looking for TS Police SI previous papers, the TS SI or Constable mains 2023 question paper, the TS Constable question paper 2022, the older Constable papers of 2016, 2018 and 2019, TSLPRB / TGPRB previous question papers with answers, '
            'or a Telangana police mock test? They are all here: open a paper to see its questions, or practise it online with answers and explanations.</p>'
            '<p lang="te">తెలంగాణ పోలీస్ ఎస్ఐ, కానిస్టేబుల్ పాత ప్రశ్నాపత్రాలు (మునుపటి ప్రశ్నపత్రాలు) TSLPRB ఫైనల్ కీ సమాధానాలు, తెలుగులో వివరణలతో — ప్రాక్టీస్ క్విజ్‌లు, మాక్ టెస్ట్‌లు; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.</p>'
            '<p class="note">2026 prelims are tentatively on 29 November (SI) and 20 December (Constable). Full mock tests with a timer: '
            '<a href="/ts-police-si/mock-test.html">TS Police SI mock test</a> · <a href="/ts-police-constable/mock-test.html">TS Police Constable mock test</a>.</p>',
      te={'TS Police SI': 'తెలంగాణ పోలీస్ ఎస్ఐ ప్రశ్నాపత్రాలు', 'TS Constable': 'తెలంగాణ పోలీస్ కానిస్టేబుల్ ప్రశ్నాపత్రాలు'},
      order=lambda c: 0 if c['id'] == 'ts-police-si' else 1),
  'ap-police-pyqs.html': dict(
      board='SLPRB', ename='AP Police', crumb='AP Police PYQs',
      title='AP Police Previous Question Papers with Answers – SI & Constable PYQs (SLPRB AP), English & Telugu | Learn with Anil',
      desc='Andhra Pradesh Police SI and Constable previous question papers in one place: SLPRB AP Preliminary Written Test papers of 2023, '
           '{n} questions with answers from SLPRB\'s keys and explanations, in English and Telugu. Practise them online with one ₹45 All-in-One Pass for every exam.',
      h1='AP Police SI & Constable previous question papers with answers',
      lede="Every Andhra Pradesh Police SI and Constable question paper on Learn with Anil, {n} questions in all. "
           "Answers come from SLPRB AP's keys, and every question has a short explanation, in English and Telugu.",
      intro='<p>Looking for AP Police SI previous papers, the AP SI prelims 2023 Paper 1 or Paper 2, the AP Police Constable question paper 2023, SLPRB AP / APSLPRB previous question papers with answers, '
            'or an AP police mock test? They are all here: open a paper to see its questions, or practise it online with answers and explanations.</p>'
            '<p lang="te">ఏపీ పోలీస్ ఎస్ఐ, కానిస్టేబుల్ పాత ప్రశ్నాపత్రాలు (మునుపటి ప్రశ్నపత్రాలు) SLPRB కీ సమాధానాలు, వివరణలతో — తెలుగు, ఇంగ్లీష్‌లో; అన్ని పరీక్షలకు ఒకే ₹45 ఆల్-ఇన్-వన్ పాస్.</p>'
            '<p class="note">New: <a href="/ap-police-si-notification-2026.html">AP Police SI Notification 2026</a> (378 posts) and '
            '<a href="/ap-police-constable-notification-2026.html">AP Police Constable Notification 2026</a> (1,156 posts); SLPRB will announce the application dates in a press note.</p>',
      te={'AP Police SI': 'ఏపీ పోలీస్ ఎస్ఐ ప్రశ్నాపత్రాలు', 'AP Constable': 'ఏపీ పోలీస్ కానిస్టేబుల్ ప్రశ్నాపత్రాలు'},
      order=lambda c: 0 if c['id'] == 'ap-police-si' else 1),
}


def landing_page(loaded, rel):
    """One crawlable page listing every paper and subject page of one recruiting board (APPSC, TSLPRB)."""
    L = LANDINGS[rel]
    loaded = sorted([x for x in loaded if x[0]['board'] == L['board']], key=lambda x: L['order'](x[0]))
    n = f'{sum(len(x[2]) for x in loaded):,}'
    can = f'{SITE_URL}/{rel}'
    secs = []
    for conf, papers, questions in loaded:
        papers, questions = public_only(papers, questions)   # public pages only for four-option papers
        base = conf['dir'] + '/' if conf['dir'] else ''
        subj = {s[0]: s for s in conf['subjects']}
        scount = {}
        for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
        rows = ''.join(
            f'<li class="q"><div class="meta">{esc(p["held"])} · {esc(p["notif"])} · {p["count"]} questions · '
            f'{"answer from APPSC\'s key, options by Learn with Anil" if p.get("own") else "all four options" if p["fmt"] == "mcq" else "answer-only key"}</div>'
            f'<p><a href="{base}papers/{p["slug"]}.html">{esc(paper_kw(conf, p))} question paper with answers</a></p>'
            f'<p class="why" style="font-weight:400">{esc(p["blurb"])}</p></li>'
            for p in sorted(papers, key=lambda p: (-p['year'], p['id'])))
        subs = ''.join(f'<a href="{base}subjects/{conf["slugp"]}-{subj[s][2]}-pyqs.html">{esc(subj[s][1])} ({scount[s]})</a>'
                       for s in subj if scount.get(s))
        secs.append(f'<h2 id="{conf["id"]}">{nw(conf["name"])} PYQs <span lang="te" style="font-size:.8em;font-weight:600">· {esc(L["te"][conf["short"]])}</span></h2>'
                    + (f'<p class="why" style="font-weight:400">{esc(conf["aka"])}</p>' if conf.get('aka') and L['board'] != 'APPSC' else '')
                    + f'<p><a class="cta" href="{conf["pb"]}">Practise {esc(conf["name"])} online</a></p>'
                    f'<ol class="qs">{rows}</ol><h3>{esc(conf["name"])} PYQs by subject</h3><nav class="toc">{subs}</nav>')
    toc = '<nav class="toc">' + ''.join(f'<a href="#{c["id"]}">{esc(c["name"])}</a>' for c, _, _ in loaded) + '</nav>'
    return static_page(0, L['title'], L['desc'].format(n=n), can, L['h1'], esc(L['lede'].format(n=n)), toc + L['intro'] + ''.join(secs),
                       [('Home', SITE_URL + '/'), (L['crumb'], can)], loaded[0][0] if L['board'] != 'APPSC' else None,
                       ename=L['ename'], at_root=True)


# ---------- 2026 notification pages and free mock-test pages ----------
# Facts from APPSC's notifications (as reported by several exam sites on 13-20 Oct 2026; each page links the official PDF
# and tells readers to check psc.ap.gov.in). Update these when the detailed notifications or exam dates come out.
def facts_table(rows, head=None):
    h = ('<tr>' + ''.join(f'<th>{esc(x)}</th>' for x in head) + '</tr>') if head else ''
    return ('<table class="facts">' + h + ''.join(
        '<tr>' + ''.join(f'<td class="n">{c:,}</td>' if (i and isinstance(c, int)) else (f'<th scope="row">{esc(str(c))}</th>' if (not i and not head) else f'<td>{esc(str(c))}</td>')
                         for i, c in enumerate(r)) + '</tr>' for r in rows) + '</table>')


def practice_links(conf, papers, questions):
    """Links to this exam's papers, mock tests and subject pages (for the notification pages)."""
    papers, questions = public_only(papers, questions)
    base = conf['dir'] + '/' if conf['dir'] else ''
    subj = {x[0]: x for x in conf['subjects']}
    scount = {}
    for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
    rows = ''.join(
        f'<li class="q"><div class="meta">{esc(p["held"])} · {p["count"]} questions · {p.get("mins") or p["count"]} min timer{" · answer from APPSC's key, options by Learn with Anil" if p.get("own") else "" if p["fmt"] == "mcq" else " · answer-only key (quick-recall cards)"}</div>'
        f'<p><a href="/{base}papers/{p["slug"]}.html">{esc(paper_kw(conf, p))} question paper with answers</a>'
        + f' · <a href="{conf["pb"]}?practice={p["id"]}">Attempt it with a timer</a></p></li>'
        for p in sorted(papers, key=lambda p: (-p['year'], p['id'])))
    subs = ''.join(f'<a href="/{base}subjects/{conf["slugp"]}-{subj[x][2]}-pyqs.html">{esc(subj[x][1])} ({scount[x]})</a>' for x in subj if scount.get(x))
    return (f'<ol class="qs">{rows}</ol><h3>{esc(conf["seo"])} previous questions by subject</h3><nav class="toc">{subs}</nav>'
            f'<p><a class="cta" href="{conf["pb"]}mock-test.html">{esc(conf["seo"])} mock tests</a><a class="cta alt" href="{conf["pb"]}">Practise topic-wise</a></p>')


NOTIFS = {
  'appsc-group-2-notification-2026.html': dict(
    exam='appsc-group-2', crumb='Group 2 Notification 2026',
    title='APPSC Group 2 Notification 2026 – 686 Posts, Apply Online 10–30 November, Salary, Eligibility, Exam Pattern & Previous Papers | Learn with Anil',
    desc='APPSC Group 2 Notification 2026 (No. 37/2026): 686 posts including 200 Deputy Tahsildar and 176 Deputy MPDO posts, the pay scale of every post, '
         'how to apply online (OTPR, 10 to 30 November 2026), eligibility, the screening test and mains pattern, the 2023 cut-off facts and Group 2 previous year question papers with answers.',
    h1='APPSC Group 2 Notification 2026: 686 posts',
    lede='APPSC issued a brief notification (No. 37/2026) on 13 October 2026 for 686 Group-II posts, Executive and Non-Executive. '
         'Online applications run from 10 to 30 November 2026. Here are the posts, the dates, the exam pattern, and the Group 2 previous papers to start practising now.',
    te='APPSC గ్రూప్ 2 నోటిఫికేషన్ 2026 (నం. 37/2026): 686 పోస్టులు — ఆన్‌లైన్ దరఖాస్తులు నవంబర్ 10 నుంచి 30 వరకు. పరీక్ష విధానం, పాత ప్రశ్నాపత్రాలు సమాధానాలతో.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Group_II_372026.pdf', pdfname='APPSC brief notification No. 37/2026, dated 13 October 2026',
    more_src=[('https://psc.ap.gov.in/Documents/NotificationDocuments/SelectionNotification_112023_28012026.pdf', 'APPSC final selection notification for Group-II (No. 11/2023), 28 January 2026')],
    related=['appsc-group-2-syllabus-2026.html', 'appsc-group-1-notification-2026.html', 'appsc-group-1-syllabus-2026.html'],
    sections=[
      ('Important dates', 'table', [
        ('Brief notification (No. 37/2026)', '13 October 2026'),
        ('Detailed notification', 'Expected by 10 November 2026: age limits, fee and reservations'),
        ('Online applications', '10 November to 30 November 2026 (till 11:59 pm)'),
        ('Screening test (prelims)', 'Date not announced yet'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts, vacancies and salary', 'table+', (['Post', 'Vacancies', 'Pay scale (₹ per month)'], [
        ('Municipal Commissioner Grade-III', 6, '45,830 – 1,30,580'), ('Sub-Registrar Grade-II', 7, '44,570 – 1,27,480'), ('Deputy Tahsildar', 200, '44,570 – 1,27,480'),
        ('Goods and Services Tax Officer (erstwhile ACTO)', 40, '45,830 – 1,30,580'), ('Assistant Registrar of Co-operative Societies', 10, '45,830 – 1,30,580'),
        ('Deputy Mandal Parishad Development Officer', 176, '45,830 – 1,30,580'), ('Prohibition and Excise Sub-Inspector', 29, '40,970 – 1,24,380'),
        ('Assistant Section Officer (GAD)', 71, '40,970 – 1,24,380'), ('Assistant Section Officer (Finance)', 5, '40,970 – 1,24,380'), ('Assistant Section Officer (Law)', 4, '40,970 – 1,24,380'),
        ('Senior Accountant (HODs)', 90, '34,580 – 1,07,210'), ('Junior Accountant (HODs)', 48, '25,220 – 80,910'), ('Total', 686, '')])),
      ('', 'note', 'Executive posts (Municipal Commissioner, Sub-Registrar, Deputy Tahsildar, GST Officer, Assistant Registrar, Deputy MPDO and Excise SI) and the Assistant Section Officer posts '
                   'start between ₹40,970 and ₹45,830 a month in the pay scale, before allowances.'),
      ('Who can apply', 'p', 'A bachelor\'s degree from a recognised university. Some posts need a particular degree: Assistant Section Officer (Finance) a degree in '
                          'mathematics, economics or commerce; Assistant Section Officer (Law) a law degree; Senior and Junior Accountant a degree in commerce, '
                          'economics or mathematics plus a computer qualification. Age limits, relaxations and the fee are given in the detailed notification.'),
      ('How to apply online (10 to 30 November 2026)', 'steps', [
        'Register once for the One Time Profile Registration (OTPR) on psc.ap.gov.in, or update your old OTPR: your details, education, community and photo. Note your OTPR ID (AP followed by 10 digits).',
        'If you have never set a password, create one on the APPSC candidate login page with your OTPR ID and mobile number.',
        'Log in during the application window, choose Notification No. 37/2026 (Group-II Services) and fill in the form; pick your exam centre.',
        'Pay the fee online (net banking, debit or credit card, UPI), submit, and save the PDF of your application.',
        'Do not wait for 30 November: near the Group 1 last date in October the website slowed down and many candidates could not pay. Apply in the first week.']),
      ('Fee and age limit: what the last Group 2 notification said', 'list', [
        'Fee in 2023 (Notification 11/2023): ₹250 application processing fee + ₹80 examination fee. SC, ST, BC, PwBD and ex-service candidates, white-card families and unemployed youth of AP paid only the ₹250.',
        'Age in 2023: 18 to 42 years for most posts (Excise Sub-Inspector 18 to 30), with 5 years\' relaxation for SC, ST and BC and 10 for persons with disabilities.',
        'AP has since raised the upper age limit for non-uniformed posts from 42 to 44 (until 30 September 2027); Group 1 2026 uses 44. Whether Group 2 does is confirmed only in the detailed notification due by 10 November 2026.']),
      ('Exam pattern', 'table+', (['Stage', 'What it covers', 'Questions · marks · time'], [
        ('Screening test (objective, OMR)', 'Indian History, Geography, Indian Society, Current Affairs and Mental Ability, 30 marks each', '150 · 150 · 150 min'),
        ('Mains Paper I (objective)', 'Social and cultural history of Andhra Pradesh; general overview of the Indian Constitution', '150 · 150 · 150 min'),
        ('Mains Paper II (objective)', 'Indian and Andhra Pradesh economy; science and technology', '150 · 150 · 150 min'),
        ('Computer Proficiency Test', 'Qualifying test for the posts that need it, then document verification', '—')])),
      ('', 'note', 'The screening test only shortlists candidates for the Mains; selection is on the Mains marks. The pattern is the same as in the previous '
                   'Group-II recruitment (Notification 11/2023), so the 2024 Screening Test and the 2025 Mains papers below are the closest practice you can get.'),
      ('Cut-off marks', 'p', 'APPSC has not published category-wise cut-off marks for the last Group 2 recruitment (Notification 11/2023). The screening test is only a filter: '
                             'about 92,250 candidates qualified for the Mains from the screening test of 25 February 2024, for 905 posts, and the final selection was made on the Mains marks '
                             '(final selection list on 28 January 2026). Figures you see online as "Group 2 cut-off" are estimates by coaching sites, not APPSC\'s.'),
      ('How long the last Group 2 took', 'table', [
        ('Notification 11/2023', 'December 2023, 897 posts (later 905)'), ('Screening test', '25 February 2024'), ('Screening result', '10 April 2024'),
        ('Mains', '23 February 2025 (after two postponements)'), ('Final selection list', '28 January 2026')]),
    ]),
  'appsc-group-1-notification-2026.html': dict(
    exam='appsc-group-1', crumb='Group 1 Notification 2026',
    # Anil, 27 Oct 2026: APPSC web note of 27 Oct 2026 extended the last date for Notifications 07, 08, 19, 25 and 26/2026 to
    # 9 Nov 2026, 11:59 pm ("no further extension"; Group-I screening test date unchanged). Source: Extension_Webnote_27102026.pdf
    title='APPSC Group 1 Last Date Extended to 9 November 2026 – Apply Online, 166 Posts, Fee & Help | Learn with Anil',
    desc='APPSC has extended the last date for Group 1 (Notification 07/2026) online applications to 9 November 2026, 11:59 pm, with no further extension; '
         'the screening test date is unchanged. Also extended: AEE (Pollution Control Board), Horticulture Officer, Hostel Welfare Officer and ATWO/ASWO. Step-by-step help, posts, pattern and previous papers.',
    h1='APPSC Group 1 last date extended to 9 November 2026',
    lede='APPSC has extended the last date for Group-I Services (Notification No. 07/2026, 166 posts) to 9 November 2026, 11:59 pm, after requests from aspirants. '
         'APPSC says there will be no further extension and no change in the screening test date (tentatively 24 January 2027). Below: what to do if the website or payment gets stuck, '
         'the posts, the exam pattern and the Group 1 previous papers to practise.',
    te='APPSC గ్రూప్ 1 (నోటిఫికేషన్ నం. 07/2026, 166 పోస్టులు) దరఖాస్తు గడువు 2026 నవంబర్ 9 రాత్రి 11:59 వరకు పొడిగించారు. ఇక పొడిగింపు ఉండదు; స్క్రీనింగ్ టెస్ట్ తేదీలో మార్పు లేదు. చివరి రోజు వరకు ఆగకుండా ముందే దరఖాస్తు చేయండి.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Group_I_07_2026.pdf', pdfname='APPSC Notification No. 07/2026 (Group-I Services)',
    more_src=[('https://psc.ap.gov.in/Documents/NotificationDocuments/Extension_Webnote_27102026.pdf', 'APPSC web note on the extension of the last date, 27 October 2026'),
              ('https://images.assettype.com/edexlive/2026-09-15/0j3savzw/Group_I_072026.pdf', 'APPSC brief notification No. 07/2026 of 15 September 2026 (posts and pay scales)')],
    related=['appsc-group-1-syllabus-2026.html', 'appsc-group-2-notification-2026.html'],
    sections=[
      ('Last date extended to 9 November 2026', 'p',
       'On 27 October 2026, the last day, the APPSC website was very slow, the OTPR password page kept hanging and many fee payments failed. The same day APPSC issued a web note: '
       '"In view of requests received from the aspirants", the last date for online applications is extended to 9 November 2026, up to 11:59 pm. APPSC says there shall be no further '
       'extension, and the Group-I screening test date does not change. If you could not finish on 27 October, apply now; do not leave it for the last day again.'),
      ('All APPSC notifications extended to 9 November 2026', 'table+', (['Notification', 'Posts'], [
        ('07/2026 (6 October 2026)', 'Group-I Services'),
        ('08/2026 (6 October 2026)', 'Assistant Environmental Engineer, A.P. Pollution Control Board'),
        ('19/2026 (6 October 2026)', 'Horticulture Officer, A.P. Horticulture Service'),
        ('25/2026 (9 October 2026)', 'Hostel Welfare Officer Grade-II, BC Welfare, Social Welfare and Tribal Welfare Departments'),
        ('26/2026 (9 October 2026)', 'Assistant Tribal Welfare Officer and Assistant Social Welfare Officer')])),
      ('What to do if you are stuck', 'list', [
        'No password after the OTPR? APPSC does not send one. Create it once at portal-psc.ap.gov.in/CandidateLoginPages/UserRegistration.aspx with your OTPR ID '
        '(AP followed by 10 digits) and mobile number. The password needs 8 to 12 characters with a capital letter, a number and a special character ($ @ ! % * #).',
        'Page hanging: click Submit only once and wait a minute or two. If it stays stuck, refresh, type the new captcha and submit once more. Another browser, or your phone on mobile data, often works better.',
        'Payment failed: first check whether money left your account. If it did, do not pay again; the payment usually shows up on the APPSC site within a few hours, '
        'and the bank refunds a failed payment on its own in about 5 to 7 days. If no money left your account, try again.',
        'No SBI in the net-banking list? Look for "State Bank of India" under S, or pay with your SBI debit card (switch on online use in the YONO app) or by UPI.',
        'Fee: ₹370 (₹250 application fee + ₹120 examination fee); candidates exempt from the examination fee pay only the ₹250 application fee. '
        'Candidates from other states, including Telangana, apply in the open category and pay ₹370.',
        'BC certificate: the form accepts a BC non-creamy-layer certificate issued on or after 1 April 2026.',
        'Photo: JPG under 50 KB, 3.5 cm × 4.5 cm, with your name and the date of the photograph printed at the bottom. Signature: JPG under 30 KB, 3.5 cm × 1.5 cm.',
        'Exam centre: Vijayawada appears as "Ntr" (NTR district) in the list; "Krishna" now means Machilipatnam.']),
      ('Important dates', 'table', [
        ('Notification (No. 07/2026)', '6 October 2026'),
        ('Online applications', '6 October to 9 November 2026, 11:59 pm (extended from 27 October; no further extension)'),
        ('Extension web note', '27 October 2026'),
        ('Screening test (prelims)', 'Tentatively 24 January 2027 (unchanged by the extension)'),
        ('Mains and interview', 'To be announced'),
        ('Official website', 'psc.ap.gov.in')]),
      # Corrected 3 Nov 2026: the post list is from the brief notification of 15 Sep 2026 (163 posts, with pay scales); the detailed notification of
      # 6 Oct 2026 added one post each to Deputy Collector, Deputy Registrar and Assistant Audit Officer (166). The old list wrongly had Jails and Fire posts.
      ('Posts, vacancies and salary', 'table+', (['Post', 'Vacancies', 'Pay scale (₹ per month)'], [
        ('Deputy Collector (A.P. Civil Service, Executive Branch)', 12, '61,960 – 1,51,370'),
        ('Assistant Commissioner of State Tax', 14, '61,960 – 1,51,370'),
        ('Deputy Superintendent of Police (Civil), Category-II', 36, '61,960 – 1,51,370'),
        ('Deputy Superintendent of Police (Communications)', 3, '61,960 – 1,51,370'),
        ('District Educational Officer', 14, '61,960 – 1,51,370'),
        ('Regional Transport Officer', 3, '57,100 – 1,47,760'),
        ('District Tribal Welfare Officer', 1, '57,100 – 1,47,760'),
        ('Deputy Registrar (Co-operative Service)', 16, '57,100 – 1,47,760'),
        ('Municipal Commissioner Grade-II', 12, '54,060 – 1,40,540'),
        ('Assistant Treasury Officer / Assistant Accounts Officer', 2, '54,060 – 1,40,540'),
        ('District Employment Officer', 3, '54,060 – 1,40,540'),
        ('Assistant Audit Officer (State Audit Service)', 15, '54,060 – 1,40,540'),
        ('Divisional Development Officer (Panchayat Raj)', 35, '65,360 – 1,54,980'),
        ('Total', 166, '')])),
      ('', 'note', 'The brief notification (15 September 2026) listed 163 posts; the detailed notification (6 October 2026) raised Deputy Collector, Deputy Registrar and Assistant Audit Officer by one each, to 166. '
                   'DSP (Communications) needs a B.E./B.Tech in Electronics & Communication, Electronics & Telecommunication or Radio Engineering; the DSP posts have physical standards and an age limit of 30.'),
      ('Who can apply', 'p', 'A bachelor\'s degree from a recognised university (a few posts ask for a particular degree). Most posts take candidates aged 18 to 44, '
                          'reckoned on 1 July 2026, with the usual relaxations for reserved categories; the police posts have their own age limits. '
                          'Fee: ₹250 application fee plus ₹120 examination fee; the examination fee is waived for SC, ST, BC, PwBD and ex-service candidates and some others.'),
      ('Exam pattern', 'table+', (['Stage', 'What it covers', 'Questions · marks · time'], [
        ('Screening test Paper I', 'General Studies: history and culture; polity, constitution, social justice and international relations; Indian and AP economy and planning; geography', '120 · 120 · 120 min'),
        ('Screening test Paper II', 'General Aptitude: mental ability, administrative and psychological abilities; science and technology; current events', '120 · 120 · 120 min'),
        ('Mains (written, descriptive)', 'Telugu and English (qualifying); General Essay; History, Culture and Geography of India and AP; Polity, Constitution, Governance, Law and Ethics; '
                                         'Economy and Development of India and AP; Science, Technology and Environmental Issues', '7 papers · 150 marks each · 3 hours each'),
        ('Interview', 'Personality test', '75 marks')])),
      ('', 'note', 'In the screening test, one-third of a mark is deducted for each wrong answer, and about 50 candidates per post go through to the Mains. '
                   'Screening marks are not counted in the final merit (Mains merit papers 750 + interview 75 = 825). The 2024 Prelims papers below follow this same pattern.'),
    ]),
  'appsc-analyst-grade-2-notification-2026.html': dict(
    exam='appsc-analyst', crumb='Analyst Grade-II Notification 2026',
    # Anil, 28 Oct / 1 Nov 2026: APPSC Notification 21/2026 dated 13 Oct 2026 (Analyst_Grade_II_21_2026.pdf)
    title='APPSC Analyst Grade 2 Notification 2026 – AP Pollution Control Board, 18 Posts, Apply by 2 November, Syllabus & Previous Papers | Learn with Anil',
    desc='APPSC Analyst Grade-II (A.P. Pollution Control Board) Notification 2026 (No. 21/2026): 18 posts, online applications 13 October to 2 November 2026, eligibility, fee, '
         'the Paper I and Paper II (Chemistry, Biochemistry, Biology, Environmental Science) pattern and syllabus, and Analyst Grade-II previous question papers with answers.',
    h1='APPSC Analyst Grade-II Notification 2026: 18 posts in the AP Pollution Control Board',
    lede='APPSC Notification No. 21/2026 (13 October 2026) invites online applications for 18 posts of Analyst Grade-II in the A.P. Pollution Control Board, the laboratory analysts who test '
         'air, water and waste samples. Apply by 2 November 2026. Below: dates, eligibility, the exam pattern and syllabus, and the previous papers to start practising.',
    te='ఏపీపీఎస్సీ అనలిస్ట్ గ్రేడ్-II (ఏపీ కాలుష్య నియంత్రణ మండలి) నోటిఫికేషన్ (నం. 21/2026): 18 పోస్టులు — ఆన్‌లైన్ దరఖాస్తులు అక్టోబర్ 13 నుంచి నవంబర్ 2, 2026 వరకు. పేపర్-1 జనరల్ స్టడీస్, పేపర్-2 కామన్ పేపర్ (కెమిస్ట్రీ, బయోకెమిస్ట్రీ, బయాలజీ, ఎన్విరాన్‌మెంటల్ సైన్స్); పాత ప్రశ్నాపత్రాలు సమాధానాలతో కింద.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Analyst_Grade_II_21_2026.pdf', pdfname='APPSC Notification No. 21/2026, dated 13 October 2026',
    sections=[
      ('Important dates', 'table', [
        ('Notification (No. 21/2026)', '13 October 2026'),
        ('Online applications', '13 October to 2 November 2026 (till 11:59 pm)'),
        ('Written examination', 'Computer-based (CBRT); date to be announced by APPSC'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts, pay and age', 'table', [
        ('Post', 'Analyst Grade-II, A.P. Pollution Control Board (state-wide post)'),
        ('Vacancies', '18 (break-up in Annexure-I of the notification)'),
        ('Pay scale', '₹48,440 – ₹1,37,220'),
        ('Age', '18 to 44 years as on 1 July 2026, with the usual relaxations for reserved categories')]),
      ('Who can apply', 'p', "A bachelor's degree in Chemistry, Biochemistry, Biology or Environmental Sciences from a recognised university in India; first-class graduates are preferred. "
                          'Fee: ₹250 application processing fee plus ₹80 examination fee; SC, ST, BC, PwBD and ex-service candidates, white-card families and unemployed youth of AP are exempt from the ₹80 examination fee.'),
      ('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I (objective, degree standard)', 'General Studies & Mental Ability', '150 · 150 · 150 min'),
        ('Paper II (objective, degree standard)', 'Common Paper: Chemistry, Biochemistry, Biology, Environmental Science', '150 · 150 · 150 min'),
        ('Computer Proficiency Test', 'Office automation with computers; qualifying', '—')])),
      ('', 'note', 'One-third of a mark is deducted for each wrong answer. Selection is on the 300 marks of the written examination, after the qualifying Computer Proficiency Test.'),
      ('Paper II syllabus: Common Paper', 'list', [
        'Chemistry: non-transition elements and their halides and oxides, polymorphism of carbon and sulphur, boranes and carboranes; photochemistry (laws, HCl and HBr reactions, fluorescence, phosphorescence, Jablonski diagram); '
        'spectroscopy and the Beer–Lambert law (Cr and Mn estimation); chromatography (TLC, gas-liquid, paper, column, HPLC); terpenoids; amino acids and proteins; solvent-free, ultrasound- and microwave-assisted green synthesis; furan and pyrrole.',
        'Biochemistry: enzyme inhibition and mechanisms (chymotrypsin, trypsin, lysozyme); coenzymes; zymogen activation and multi-enzyme complexes; immunology, immunoglobulins, ELISA, vaccines and hypersensitivity; '
        'blood and lymph; autoimmunity; nervous and excretory systems; endocrinology; nutritional biochemistry and vitamins; clinical biochemistry (liver, renal, GTT, gastric and pancreatic function tests).',
        'Biology: bacteria (structure of E. coli, nutrition, reproduction, economic importance); viruses (TMV, polio, HIV); plant and animal cells and organelles; mitosis and meiosis; Mendelian genetics, linkage, '
        'cytoplasmic inheritance, mutations; origin of life, Darwinism, Hardy–Weinberg law; nucleosome, DNA types and replication, DNA repair, RNA and protein synthesis.',
        'Environmental Science: environment and ecology, ecosystems, energy flow, food chains, ecological pyramids and succession; forest, water, mineral and energy resources; air, water and soil pollution and waste management; '
        'greenhouse gases, global warming, the ozone hole, biogas; environmental assessment (plant, flora, animal and aquatic surveys); eco-planning, land use, urban and rural planning.']),
      ('Paper I syllabus: General Studies & Mental Ability', 'p',
       'Current events (international, national, Andhra Pradesh); general science and technology; history of India with a focus on AP and the national movement; geography of India and AP; '
       'Indian polity and governance; Indian economy and planning; sustainable development and environment; disaster management; logical reasoning; data analysis.'),
    ]),
  'appsc-assistant-environmental-engineer-notification-2026.html': dict(
    exam='appsc-env-engineer', crumb='Assistant Environmental Engineer Notification 2026',
    # Anil, 8 Nov 2026: APPSC Notification 08/2026 dated 6 Oct 2026 (Assistant_Environmental_Engineer_08_2026.pdf, attached by Anil)
    title='APPSC Assistant Environmental Engineer Notification 2026 – AP Pollution Control Board, 41 Posts, Syllabus & Previous Papers | Learn with Anil',
    desc='APPSC Assistant Environmental Engineer (A.P. Pollution Control Board) Notification 2026 (No. 08/2026): 41 posts, online applications 6 to 27 October 2026, eligibility, fee, '
         'the Paper I General Studies and Paper II Common Subject pattern and syllabus, and AEE previous question papers with answers.',
    h1='APPSC Assistant Environmental Engineer Notification 2026: 41 posts in the AP Pollution Control Board',
    lede='APPSC Notification No. 08/2026 (6 October 2026) invited online applications for 41 posts (one of them carried forward) of Assistant Environmental Engineer in the A.P. Pollution Control Board, '
         'for engineering graduates. Applications ran from 6 to 27 October 2026; the computer-based exam date is still to be announced. Below: dates, eligibility, the exam pattern and syllabus, '
         'and the 2025 papers to start practising.',
    te='ఏపీపీఎస్సీ అసిస్టెంట్ ఎన్విరాన్‌మెంటల్ ఇంజనీర్ (ఏపీ కాలుష్య నియంత్రణ మండలి) నోటిఫికేషన్ (నం. 08/2026): 41 పోస్టులు — ఆన్‌లైన్ దరఖాస్తులు అక్టోబర్ 6 నుంచి 27, 2026 వరకు. పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ, పేపర్-2 కామన్ సబ్జెక్ట్; 2025 ప్రశ్నాపత్రాలు సమాధానాలతో కింద.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Assistant_Environmental_Engineer_08_2026.pdf', pdfname='APPSC Notification No. 08/2026, dated 6 October 2026',
    sections=[
      ('Important dates', 'table', [
        ('Notification (No. 08/2026)', '6 October 2026'),
        ('Online applications', '6 to 27 October 2026 (till 11:59 pm)'),
        ('Written examination', 'Computer-based (CBRT); date to be announced by APPSC'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts, pay and age', 'table', [
        ('Post', 'Assistant Environmental Engineer, A.P. Pollution Control Board (state-wide post)'),
        ('Vacancies', '41, including 1 carried forward (break-up in Annexure-I of the notification)'),
        ('Pay scale', '₹57,100 – ₹1,47,760'),
        ('Age', '18 to 44 years as on 1 July 2026; 5 years more for SC, ST, BC and EWS, 10 years for persons with benchmark disabilities')]),
      ('Who can apply', 'p', 'A B.E./B.Tech. degree in Civil, Mechanical, Chemical or Environmental Engineering from a recognised university in India, or a pass in Sections A and B of the AMIE (India) Civil examination. '
                          'Fee: ₹250 application processing fee plus ₹80 examination fee; SC, ST, BC, PwBD and ex-service candidates, white-card families and unemployed youth of AP are exempt from the ₹80 examination fee.'),
      ('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I (objective, degree standard)', 'General Studies & Mental Ability (English and Telugu)', '150 · 150 · 150 min'),
        ('Paper II (objective, degree standard)', 'Common Subject (English only)', '150 · 150 · 150 min'),
        ('Computer Proficiency Test', 'Office automation with computers; qualifying', '60 min · 100 marks')])),
      ('', 'note', 'One-third of a mark is deducted for each wrong answer. Selection is on the 300 marks of the written examination, after the qualifying Computer Proficiency Test. '
                   'Minimum qualifying marks: 40% for OC, sportspersons, ex-servicemen and EWS, 35% for BCs, 30% for SC, ST and PwBD. In the 2025 exam Paper II carried 300 marks; it is now 150.'),
      ('Paper II syllabus: Common Subject', 'list', [
        'Ecosystems: structure and function, food chains, food webs and ecological pyramids, energy flow, biogeochemical cycles, bioaccumulation and biomagnification, ecosystem services and carrying capacity.',
        'Natural resources: water (surface and ground water, floods, droughts, dams), mineral, land, forest and energy resources, renewable and non-renewable energy.',
        'Biodiversity and biotic resources: genetic, species and ecosystem diversity, values of biodiversity, India as a mega-diversity nation, hotspots, threats, in-situ and ex-situ conservation, the Biological Diversity Act.',
        'Engineering materials: structure and properties, phase diagrams, heat treatment, stress–strain diagrams.',
        "Fluid mechanics and hydraulics: Newtonian and non-Newtonian fluids, fluid properties, manometers, stream function and velocity potential, continuity, Bernoulli's and impulse-momentum equations, "
        "laminar and turbulent pipe flow, Reynolds number, Hagen–Poiseuille and Darcy–Weisbach equations, losses in pipes, dimensional analysis and similarity, boundary layer.",
        'Process calculations and thermodynamics: conservation of mass and energy, tie components, recycle, bypass and purge, degrees of freedom, first and second laws, equations of state and properties of real systems.',
        'Air, water, soil and noise pollution and control technologies: primary and secondary air pollutants, particulate, SOx and NOx control, ambient air quality standards; drinking-water standards, '
        'primary, secondary and tertiary wastewater treatment (grit chambers, sedimentation, trickling filters, oxidation ponds, activated sludge, septic tanks, sludge disposal); soil pollution; noise standards.',
        'Solid and industrial waste management: municipal solid waste collection, segregation, transport and processing, e-waste, bioremediation.',
        'Global environmental problems, policies and laws: climate change, ozone depletion, deforestation and desertification, the Earth Summit and the Kyoto, Montreal and Paris agreements, '
        'the Environment (Protection), Air, Water, Forest and Wild Life Acts, and the solid waste, bio-medical waste and hazardous waste rules.',
        'Environmental impact assessment and sustainable development: EIA structure and baseline data, risk assessment, environmental management plans, sustainable development, green buildings, '
        'ecological footprint, life cycle assessment, low-carbon lifestyle.']),
      ('Paper I syllabus: General Studies & Mental Ability', 'p',
       'Current events (international, national, Andhra Pradesh); general science and technology; history of India with a focus on AP and the national movement; geography of India and AP; '
       'Indian polity and governance; Indian economy and planning; sustainable development and environment; disaster management; logical reasoning; data analysis.'),
    ]),
  'appsc-fro-notification-2026.html': dict(
    exam='appsc-fro', crumb='FRO Notification 2026',
    # Anil, 28 Oct / 1 Nov 2026: APPSC Notification 16/2026 dated 16 Oct 2026 (FRODetailedNotification_162026.pdf)
    title='APPSC FRO Notification 2026 – Forest Range Officer, 5 Posts, Apply by 5 November, Syllabus & Previous Papers | Learn with Anil',
    desc='APPSC Forest Range Officer (FRO) Notification 2026 (No. 16/2026): 5 posts in the A.P. Forest Service, online applications 16 October to 5 November 2026, eligibility, physical standards, fee, '
         'the exam pattern and General Forestry syllabus, and FRO previous question papers with answers.',
    h1='APPSC Forest Range Officer (FRO) Notification 2026: 5 posts',
    lede='APPSC Notification No. 16/2026 (16 October 2026) invites online applications for 5 posts of Forest Range Officer in the A.P. Forest Service. Apply by 5 November 2026. '
         'Below: dates, eligibility and physical standards, the exam pattern and syllabus, and the previous papers to start practising.',
    te='ఏపీపీఎస్సీ ఫారెస్ట్ రేంజ్ ఆఫీసర్ (FRO) నోటిఫికేషన్ (నం. 16/2026): 5 పోస్టులు — ఆన్‌లైన్ దరఖాస్తులు అక్టోబర్ 16 నుంచి నవంబర్ 5, 2026 వరకు. జనరల్ స్టడీస్, గణితం, జనరల్ ఫారెస్ట్రీ-1, 2 పేపర్లు; పాత ప్రశ్నాపత్రాలు సమాధానాలతో కింద.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/FRODetailedNotification_162026.pdf', pdfname='APPSC Notification No. 16/2026, dated 16 October 2026',
    sections=[
      ('Important dates', 'table', [
        ('Notification (No. 16/2026)', '16 October 2026'),
        ('Online applications', '16 October to 5 November 2026 (till 11:59 pm)'),
        ('Written examination', 'Computer-based (CBRT); date to be announced by APPSC'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts, pay and age', 'table', [
        ('Post', 'Forest Range Officer, A.P. Forest Service (zonal post)'),
        ('Vacancies', '5, including 1 carried forward (break-up in Annexure-I of the notification)'),
        ('Pay scale', '₹48,440 – ₹1,37,220'),
        ('Age', '18 to 30 years as on 1 July 2026, with the usual relaxations for reserved categories')]),
      ('Who can apply', 'p', "A bachelor's degree in agriculture, botany, chemistry, computer applications or computer science, engineering (agriculture, chemical, civil, computer, electrical, electronics or mechanical), "
                          'environmental science, forestry, geology, horticulture, mathematics, physics, statistics, veterinary science or zoology. Physical standards: men at least 163 cm tall, chest 79 cm with 5 cm expansion, '
                          'able to walk 25 km in 4 hours; women at least 150 cm, chest 74 cm with 5 cm expansion, able to walk 16 km in 4 hours (lower heights for Scheduled Tribes and some other groups). '
                          'Fee: ₹250 application processing fee plus ₹120 examination fee.'),
      ('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Qualifying test (SSC standard)', 'General English (50) and General Telugu (50), to be qualified separately', '100 · 100 · 100 min'),
        ('Paper I (objective)', 'General Studies & Mental Ability', '150 · 150 · 150 min'),
        ('Paper II (objective)', 'Mathematics (SSC standard)', '150 · 150 · 150 min'),
        ('Paper III (objective)', 'General Forestry I', '150 · 150 · 150 min'),
        ('Paper IV (objective)', 'General Forestry II', '150 · 150 · 150 min')])),
      ('', 'note', 'One-third of a mark is deducted for each wrong answer. Papers I–IV count for 600 marks. Candidates picked in the ratio 1:3 take a walking test and a medical examination arranged by the Forest Department, and a qualifying Computer Proficiency Test.'),
      ('General Forestry I syllabus', 'list', [
        'Renewable and non-renewable natural resources: forest, water, mineral, food, energy and land resources.',
        'Plant sciences: classification, morphology, tissues, wood anatomy, seeds, reproduction, propagation, plant physiology, inheritance and plant diseases.',
        'Biodiversity and its conservation: levels and value of biodiversity, hotspots, biomes of India, population ecology.',
        'Soil science and geology: rocks and minerals of India, soil formation and properties, soil conservation, reclamation of problem soils, organic matter, N and C cycles.',
        'Water resource and watershed management: water harvesting, groundwater recharge, forest hydrology.',
        'Silviculture, agroforestry, social forestry and community forest management: regeneration, nursery and planting, silviculture of 14 species grown in AP (teak, red sanders, sandalwood, neem, bamboo, eucalyptus, casuarina and others).']),
      ('General Forestry II syllabus', 'list', [
        'Ecosystems and wildlife: ecosystem structure and function, GPP and NPP, types of ecosystems, wildlife and protected areas of India.',
        'Forest protection: injuries, pests and diseases, fire, grazing, encroachment and other human impacts.',
        'Forest utilization: logging and transport, seasoning and preservation, wood properties, MFP/NTFP species of AP, antidote plants.',
        'Animal management and economic zoology: animal ailments, dentition, snakes and snake bite, nutrition, birds and migration, beneficial and harmful insects, fish and prawns.',
        'Forest economics, legislation and administration: cost-benefit and investment methods, forest policies of 1894, 1952 and 1988, AP Forest Act 1967, Forest Conservation Act 1980, Wildlife Protection Act 1972, forest services.',
        'Forest inventory, mensuration and remote sensing: sampling methods, tree and stand measurement, instruments, GIS, GPS and forest cover monitoring.',
        'Environmental science: pollution, solid waste, sustainable development, climate change, environmental laws (EPA 1986, Air Act 1981, Water Act 1974, APWALTA 2004).',
        'Forest survey and engineering, and first aid.']),
      ('Paper I and Paper II', 'p',
       'Paper I General Studies & Mental Ability follows the common APPSC syllabus (current events, science, history, geography, polity, economy, environment, disaster management, reasoning, data analysis). '
       'Paper II Mathematics is SSC standard: arithmetic, algebra, trigonometry, geometry, mensuration and statistics.'),
    ]),
  'ap-police-si-notification-2026.html': dict(
    exam='ap-police-si', board='SLPRB AP', site='slprb.ap.gov.in', crumb='AP Police SI Notification 2026',
    # Anil, 2 Nov 2026. SLPRB AP Rc.No.81/SLPRB/Rect.1/2026 and press note of 16 Sep 2026 (slprb.ap.gov.in/2026_PDFS/SLPRB_AP_SI_Notification_2026.pdf)
    title='AP Police SI Notification 2026 – SLPRB AP, 378 SI Posts (Civil, AR, SPF), Eligibility, Exam Pattern & Previous Papers | Learn with Anil',
    desc='AP Police SI Notification 2026 (SLPRB AP Rc.No.81/2026, 16 September 2026): 378 posts of SCT SI (Civil), RSI (AR) and SI (SPF), eligibility, age, height, fee, the Preliminary and Final '
         'Written Test pattern and syllabus, PMT/PET standards, and AP Police SI previous question papers with answers.',
    h1='AP Police SI Notification 2026: 378 Sub-Inspector posts',
    lede='The State Level Police Recruitment Board, Andhra Pradesh notified 378 Sub-Inspector posts on 16 September 2026: 253 SCT SI (Civil), 116 SCT Reserve SI (AR) and 9 SI in the Special Protection Force. '
         'SLPRB will announce the online application dates and the Preliminary Written Test date in a press note. Below: posts, eligibility, the exam pattern and syllabus, and the previous papers to start practising.',
    te='ఏపీ పోలీస్ ఎస్ఐ నోటిఫికేషన్ 2026 (SLPRB AP, 16 సెప్టెంబర్ 2026): 378 పోస్టులు — SCT ఎస్ఐ (సివిల్) 253, ఆర్ఎస్ఐ (AR) 116, ఎస్ఐ (SPF) 9. దరఖాస్తు, ప్రిలిమినరీ పరీక్ష తేదీలు త్వరలో ప్రెస్ నోట్ ద్వారా. అర్హత, పరీక్ష విధానం, సిలబస్, పాత ప్రశ్నాపత్రాలు సమాధానాలతో కింద.',
    pdf='https://slprb.ap.gov.in/2026_PDFS/SLPRB_AP_SI_Notification_2026.pdf', pdfname='SLPRB AP Notification Rc.No.81/SLPRB/Rect.1/2026, dated 16 September 2026',
    sections=[
      ('Important dates', 'table', [
        ('Notification', '16 September 2026 (Rc.No.81/SLPRB/Rect.1/2026)'),
        ('Online applications (Stage I)', 'Dates to be announced by SLPRB in a press note'),
        ('Preliminary Written Test', 'Date to be announced'),
        ('Official website', 'slprb.ap.gov.in')]),
      ('Posts', 'table', [
        ('SCT Sub-Inspectors of Police (Civil) (Men & Women), post code 11', '253 (zone-wise)'),
        ('SCT Reserve Sub-Inspectors of Police (AR) (Men & Women), post code 12', '116 (zone-wise)'),
        ('Sub-Inspectors (Men), Special Protection Force, post code 31', '9'),
        ('Total', '378'),
        ('Separate notification', '50 SI (Communications) and 10 SI (PTO)')]),
      ('Who can apply', 'p', 'A degree from a university recognised in India, as on 1 July 2026; SC and ST candidates who passed Intermediate and studied a degree are also eligible. '
                          'Age 21 to 27 years as on 1 July 2026 (born between 2 July 1999 and 1 July 2005), relaxed by up to 5 years for SC, ST, BC and EWS candidates and for AP government employees. '
                          'Fee ₹600 (₹300 for SC and ST candidates of AP; non-local candidates pay ₹600 as open category).'),
      ('Physical standards (PMT) and physical test (PET)', 'p',
       'Height at least 167.6 cm and chest 86.3 cm with 5 cm expansion for men; height 152.5 cm and weight 40 kg for women (lower heights for Aboriginal ST candidates of the agency areas). '
       'PET: 1,600 m run in 8 minutes (women 10 min 30 s), 100 m in 15 seconds (women 18 s), long jump 3.80 m (women 2.75 m). SI (Civil) candidates must pass the 1,600 m run and one of the other two; '
       'RSI (AR) and SPF candidates must pass all three, and their PET carries 100 marks.'),
      ('Exam pattern', 'table+', (['Stage', 'Paper', 'Questions · marks · time'], [
        ('Preliminary Written Test', 'Paper I: Arithmetic (SSC standard) & Test of Reasoning / Mental Ability', '100 · 100 · 3 hours'),
        ('Preliminary Written Test', 'Paper II: General Studies (degree standard)', '100 · 100 · 3 hours'),
        ('Final Written Examination', 'Paper I English and Paper II Telugu or Urdu (descriptive, qualifying)', '100 + 100 marks'),
        ('Final Written Examination', 'Paper III Arithmetic & Reasoning, Paper IV General Studies (objective, 200 questions each)', '200 + 200 marks for SI (Civil)')])),
      ('', 'note', 'Each paper must be qualified: 40% for OC (and EWS), 35% for BC, 30% for SC and ST. SI (Civil) selection is on Papers III and IV of the Final Written Examination; '
                   'for RSI (AR) and SPF the PET marks are added. No marks are deducted for wrong answers.'),
      ('Syllabus', 'list', [
        'Arithmetic: number system, simple and compound interest, ratio and proportion, average, percentage, profit and loss, time and work, work and wages, time and distance, clocks and calendars, partnership, mensuration.',
        'Test of Reasoning / Mental Ability: verbal and non-verbal reasoning, analogies, similarities and differences, spatial visualisation and orientation, problem solving, analysis, judgement, decision making, visual memory.',
        'General Studies: general science and contemporary developments in science, technology and the environment; current events of national and international importance; history of India and the Indian National Movement; '
        'geography of India; Indian polity and economy, including rural development, planning and economic reforms.']),
    ]),
  'ap-police-constable-notification-2026.html': dict(
    exam='ap-police-constable', board='SLPRB AP', site='slprb.ap.gov.in', crumb='AP Police Constable Notification 2026',
    # Anil, 2 Nov 2026. SLPRB AP Rc.No.91/SLPRB/Rect.2/2026 and press note of 16 Sep 2026 (slprb.ap.gov.in/2026_PDFS/SLPRB_AP_PC_Notification_2026.pdf)
    title='AP Police Constable Notification 2026 – SLPRB AP, 1,156 PC, Firemen & Warder Posts, Eligibility, Exam Pattern & Previous Papers | Learn with Anil',
    desc='AP Police Constable Notification 2026 (SLPRB AP Rc.No.91/2026, 16 September 2026): 1,156 posts of SCT PC (Civil), PC (AR), Firemen and Warders, eligibility, age, height, fee, '
         'the Preliminary and Final Written Examination pattern and syllabus, PMT/PET standards, and AP Police Constable previous question papers with answers.',
    h1='AP Police Constable Notification 2026: 1,156 posts',
    lede='The State Level Police Recruitment Board, Andhra Pradesh notified 1,156 posts on 16 September 2026: 542 SCT Police Constables (Civil), 285 SCT Police Constables (AR), 158 Firemen, '
         '150 Warders (Men) and 21 Warders (Women). SLPRB will announce the online application dates and the Preliminary Written Test date in a press note. Below: posts, eligibility, the exam pattern and syllabus, and the previous paper to start practising.',
    te='ఏపీ పోలీస్ కానిస్టేబుల్ నోటిఫికేషన్ 2026 (SLPRB AP, 16 సెప్టెంబర్ 2026): 1,156 పోస్టులు — SCT పీసీ (సివిల్) 542, పీసీ (AR) 285, ఫైర్‌మెన్ 158, వార్డర్లు 171. దరఖాస్తు, ప్రిలిమినరీ పరీక్ష తేదీలు త్వరలో ప్రెస్ నోట్ ద్వారా. అర్హత, పరీక్ష విధానం, సిలబస్, పాత ప్రశ్నాపత్రం సమాధానాలతో కింద.',
    pdf='https://slprb.ap.gov.in/2026_PDFS/SLPRB_AP_PC_Notification_2026.pdf', pdfname='SLPRB AP Notification Rc.No.91/SLPRB/Rect.2/2026, dated 16 September 2026',
    sections=[
      ('Important dates', 'table', [
        ('Notification', '16 September 2026 (Rc.No.91/SLPRB/Rect.2/2026)'),
        ('Online applications (Stage I)', 'Dates to be announced by SLPRB in a press note'),
        ('Preliminary Written Test', 'Date to be announced'),
        ('Official website', 'slprb.ap.gov.in')]),
      ('Posts', 'table', [
        ('SCT Police Constables (Civil) (Men & Women), post code 21', '542 (district-wise)'),
        ('SCT Police Constables (AR) (Men & Women), post code 22', '285'),
        ('Firemen, State Disaster Response and Fire Services, post code 42', '158'),
        ('Warders (Men), Prisons and Correctional Services, post code 53', '150'),
        ('Warders (Women), Prisons and Correctional Services, post code 54', '21'),
        ('Total', '1,156'),
        ('Separate notifications', '200 PC (Communications) and 213 PC (Mechanics 15, Drivers 198)')]),
      ('Who can apply', 'p', 'Intermediate or an equivalent examination passed as on 1 July 2026; SC and ST candidates who passed SSC and studied and appeared for both years of Intermediate are also eligible. '
                          'Age for SCT PC (Civil) and (AR): 18 to 24 years as on 1 July 2026 (born between 2 July 2002 and 1 July 2008), with the usual relaxations (Home Guards up to 32). '
                          'Fee ₹300 (half that for SC and ST candidates of AP; non-local candidates pay ₹300 as open category).'),
      ('Physical standards (PMT) and physical test (PET)', 'p',
       'Height at least 167.6 cm and chest 86.3 cm with 5 cm expansion for men; height 152.5 cm and weight 40 kg for women (lower heights for Aboriginal ST candidates of the agency areas). '
       'PET: 1,600 m run in 8 minutes (women 10 min 30 s), 100 m in 15 seconds (women 18 s), long jump 3.80 m (women 2.75 m). PC (Civil), Firemen and Warders must pass the 1,600 m run and one of the other two; '
       'PC (AR) candidates must pass all three, and their PET carries 100 marks.'),
      ('Exam pattern', 'table+', (['Stage', 'Paper', 'Questions · marks · time'], [
        ('Preliminary Written Test (qualifying)', 'One paper, Intermediate standard, objective', '200 · 200 · 3 hours'),
        ('Physical tests', 'PMT and PET', 'qualifying (PC (AR): PET 100 marks)'),
        ('Final Written Examination', 'One paper, same syllabus, objective', '200 · 200 (PC (AR): 100) · 3 hours')])),
      ('', 'note', 'Qualifying marks in each written test: 40% for OC (and EWS), 35% for BC, 30% for SC and ST. Preliminary marks do not count for selection. No marks are deducted for wrong answers.'),
      ('Syllabus (Preliminary and Final Written Examination)', 'list', [
        'English (printed in English only, also in the Telugu and Urdu versions of the paper).',
        'Arithmetic (SSC standard).',
        'Test of Reasoning / Mental Ability.',
        'General Science.',
        'History of India, Indian culture and the Indian National Movement.',
        'Indian geography, polity and economy.',
        'Current events of national and international importance.']),
    ]),
  'appsc-eo-grade-3-notification-2026.html': dict(
    exam='appsc-eo', crumb='EO Grade-III Notification 2026',
    # Anil, 28 Oct 2026: APPSC Notification 23/2026 dated 16 Oct 2026 (EO_Grade_III_DetailedNotification_232026.pdf)
    title='APPSC Endowment Officer (EO Grade 3) Notification 2026 – 104 Posts, Apply by 5 November, Syllabus & Previous Papers | Learn with Anil',
    desc='APPSC Executive Officer Grade-III (Endowments) Notification 2026 (No. 23/2026): 104 district posts, online applications 16 October to 5 November 2026, '
         'eligibility, fee, the Paper I and Paper II (Hindu Philosophy & Temple System) pattern and syllabus, and EO Grade-III previous question papers with answers.',
    h1='APPSC Endowment Officer (EO Grade-III) Notification 2026: 104 posts',
    lede='APPSC Notification No. 23/2026 (16 October 2026) invites online applications for 104 posts of Executive Officer Grade-III in the A.P. Endowments Subordinate Service, '
         'the officers who run temples and charitable institutions under the Endowments Department. Apply by 5 November 2026. Below: dates, eligibility, the exam pattern and syllabus, '
         'and the previous papers to start practising.',
    te='ఏపీపీఎస్సీ దేవాదాయ శాఖ ఎగ్జిక్యూటివ్ ఆఫీసర్ గ్రేడ్-III నోటిఫికేషన్ (నం. 23/2026): 104 పోస్టులు — ఆన్‌లైన్ దరఖాస్తులు అక్టోబర్ 16 నుంచి నవంబర్ 5, 2026 వరకు. పేపర్-1 జనరల్ స్టడీస్, పేపర్-2 హిందూ తత్వశాస్త్రం & దేవాలయ వ్యవస్థ; పాత ప్రశ్నాపత్రాలు సమాధానాలతో కింద.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/EO_Grade_III_DetailedNotification_232026.pdf', pdfname='APPSC Notification No. 23/2026, dated 16 October 2026',
    sections=[
      ('Important dates', 'table', [
        ('Notification (No. 23/2026)', '16 October 2026'),
        ('Online applications', '16 October to 5 November 2026 (till 11:59 pm)'),
        ('Written examination', 'Computer-based (CBRT); date to be announced by APPSC'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts, pay and age', 'table', [
        ('Post', 'Executive Officer Grade-III, A.P. Endowments Subordinate Service (district-wise post)'),
        ('Vacancies', '104 (district-wise break-up in Annexure-I of the notification)'),
        ('Pay scale', '₹25,220 – ₹80,910'),
        ('Age', '18 to 44 years as on 1 July 2026, with the usual relaxations for reserved categories')]),
      ('Who can apply', 'p', 'A bachelor\'s degree from a recognised university (any discipline) or an equivalent qualification. Under Section 29(3) of the A.P. Charitable and Hindu Religious '
                          'Institutions and Endowments Act, 1987 (as amended by Act 33 of 2007), the Executive Officer must be a person professing the Hindu religion. '
                          'Fee: ₹250 application processing fee plus ₹80 examination fee; SC, ST, BC, PwBD and ex-service candidates, white-card families and unemployed youth of AP are exempt from the ₹80 examination fee.'),
      ('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I (objective, degree standard)', 'General Studies & Mental Ability', '150 · 150 · 150 min'),
        ('Paper II (objective, degree standard)', 'Hindu Philosophy & Temple System', '150 · 150 · 150 min'),
        ('Computer Proficiency Test', 'Office automation with computers; qualifying (OC 40, BC 35, SC/ST/PwBD 30 out of 100), 60 minutes', '—')])),
      ('', 'note', 'One-third of a mark is deducted for each wrong answer. Selection is on the 300 marks of the written examination, after the qualifying Computer Proficiency Test.'),
      ('Paper II syllabus: Hindu Philosophy & Temple System', 'list', [
        'Ramayanam: characters, Kandas, dynasties and places.',
        'Mahabharatham: characters, Parvas, dynasties and places.',
        'Bhagavatham: characters, Skandhas and places.',
        'Hindu Puranams and the places in them.',
        'Temple Agamas: Vaishnavam (Vaikhanasam, Pancharathram, Chattada Srivaishnavam), Saivam (Smardham, Adi Saiva, Veera Saiva, Jangama, Kapalika) and Sakteyam.',
        'Hindu festivals in different parts of India; classical fine arts of Indian origin.',
        'Vedic culture: Yagnas and Yagams, Vedas, Upavedas, Upanishads, dharmas of the stages of life.',
        'Philosophies, cults and gurus: Alwars, Nayanars, Sankaracharya (Advaita), Ramanujacharya (Visishtadvaita), Madhwacharya (Dvaita), Basava (Veera Saiva).',
        'Family structure in Hindu society: adoption and succession.',
        'Sources of income of temples and charitable institutions; allocation of funds (Section 57 of Act 30 of 1987).',
        'Duties of Executive Officers (Section 29 of Act 30 of 1987).',
        'Land records; law on endowment lands: ROR Act and Sections 75 to 86 of Act 30 of 1987.']),
      ('Study material for Paper II', 'html',
       '<p>Learn with Anil\'s <b>Hindu Philosophy &amp; Temple System</b> notes cover every Paper II topic, from Ramayanam to the Endowments Act, '
       'written from the questions APPSC has actually asked, with APPSC\'s 2023 and 2026 Paper II questions and official answers at the end. '
       '<a href="/LearnWithAnil-EO-Grade-3-Hindu-Philosophy-Temple-System-Free-Sample.pdf">Download the free sample chapter (PDF)</a>; '
       'the full book is part of the ₹45 All-in-One Pass, under <a href="/appsc-endowment-officer/#notes">Study Material</a>.</p>'),
      ('Paper I syllabus: General Studies & Mental Ability', 'p',
       'Current events (international, national, Andhra Pradesh); general science and technology; history of India with a focus on AP and the national movement; geography of India and AP; '
       'Indian polity and governance; Indian economy and planning; sustainable development and environment; disaster management; logical reasoning; data analysis.'),
    ]),
}


# ---------- exam-date, hall-ticket and answer-key pages (Anil, 3 Nov 2026: "like the Group 1 last-date page, what else can bring traffic") ----------
# Facts from TGPRB's notifications of 29 July 2026 (SI Rc.No.225, PC Rc.No.189), its press notes of 8 and 17 September 2026, and its
# 2022 press notes (hall tickets 29 Jul / 17 Aug 2022, keys 14 Aug 2022, results 21 Oct 2022). Research notes: claude/ts-police-exam-pages.md.
TGPRB = 'https://www.tgprb.in/SI_PC_2026/'
TS_SRC_1709 = (TGPRB + 'Press%20Note%20dated%2017-09-2026.pdf', 'TGPRB press note of 17 September 2026 (tentative exam dates)')
TS_SRC_0809 = (TGPRB + 'Press%20Note%20dated%2008-09-2026.pdf', 'TGPRB press note of 8 September 2026')
TS_SRC_RES22 = ('https://tgprb.in/Pdfs/PressNoteDatedon2110022.pdf', 'TSLPRB press note of 21 October 2022 (2022 prelims results)')


def score_calc(pid, total, marks):
    """A small score calculator for a 1-mark objective paper with a 0.2 negative mark; marks = [(label, qualifying mark)]."""
    opts = ''.join(f'<option value="{m}">{esc(l)}</option>' for l, m in marks)
    return (f'<div class="calc" id="{pid}" style="border:1px solid #d0d7e2;border-radius:12px;padding:14px 16px;margin:10px 0 14px">'
            f'<p style="margin:0 0 10px">Count the questions you got right and wrong with the key (out of {total}). Each right answer gets 1 mark, each wrong answer loses 0.2 marks, and an unanswered question gets 0.</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:10px 16px;align-items:flex-end">'
            f'<label style="display:flex;flex-direction:column;font-weight:600">Right<input type="number" min="0" max="{total}" inputmode="numeric" style="width:110px;padding:8px;font-size:16px"></label>'
            f'<label style="display:flex;flex-direction:column;font-weight:600">Wrong<input type="number" min="0" max="{total}" inputmode="numeric" style="width:110px;padding:8px;font-size:16px"></label>'
            f'<label style="display:flex;flex-direction:column;font-weight:600">Category<select style="padding:8px;font-size:16px">{opts}</select></label></div>'
            f'<p class="out" aria-live="polite" style="margin:12px 0 0;font-weight:700"></p></div>'
            f'<script>(function(){{var b=document.getElementById("{pid}"),i=b.querySelectorAll("input"),c=b.querySelector("select"),o=b.querySelector(".out");'
            f'function f(){{var R=+i[0].value||0,W=+i[1].value||0;if(!i[0].value&&!i[1].value){{o.textContent="";return}}'
            f'if(R+W>{total}||R<0||W<0){{o.textContent="Right + wrong cannot be more than {total}.";return}}'
            f'var s=Math.round((R-0.2*W)*100)/100,q=+c.value;o.textContent="Your score: "+s+" / {total}. Qualifying mark for your category: "+q+". "+(s>=q?"✓ You clear it (if the final key does not change).":"✗ Below the qualifying mark.")}}'
            f'i[0].addEventListener("input",f);i[1].addEventListener("input",f);c.addEventListener("change",f)}})();</script>')


TS_RULES = [
    'Print the hall ticket on A4 paper (both sides if you can) and paste the same passport photo you uploaded with the application in the box on page 1, with gum, not pins or staples. A hall ticket without the photo is not accepted.',
    'Reach early: candidates are let in one hour before the start, and no one is admitted even one minute after the exam begins.',
    'Carry only the hall ticket and black or blue ballpoint pens.',
    'Not allowed: mobile phones, smart watches and any wrist watch, calculators, Bluetooth devices, pen drives, wallets, purses, notes or loose papers. There is no cloakroom, so leave bags at home; women are advised not to wear jewellery.',
    'A photo and fingerprints are taken in the hall: avoid mehendi or tattoos on the hands.',
    'Write nothing on the OMR sheet except the answers and the details asked for: symbols, prayers or marks count as malpractice.',
    'The question booklet is in English–Telugu or English–Urdu; where the two differ, the English version is final.',
    'Keep the hall ticket safely until the whole recruitment is over.',
]
TS_QUAL = [('OC (including EWS): 30%', 60), ('BC: 25%', 50), ('SC, ST, Ex-Servicemen: 20%', 40)]

NOTIFS.update({
  'ts-police-si-exam-date-hall-ticket-2026.html': dict(
    exam='ts-police-si', board='TGPRB', site='tgprb.in', crumb='SI Exam Date & Hall Ticket 2026',
    title='TS Police SI Exam Date 2026 (29 November) & Hall Ticket – Download, Exam Pattern, Qualifying Marks, Salary | Learn with Anil',
    desc='TS Police SI Preliminary Written Test 2026: Sunday 29 November 2026, forenoon (TGPRB, tentative). When and how to download the SI hall ticket, '
         'exam-day rules, the 200-mark pattern with 0.2 negative marking, qualifying marks (30/25/20%), 275 posts, salary ₹42,300–1,15,270, PMT/PET and previous papers.',
    h1='TS Police SI exam date 2026: Sunday, 29 November',
    lede='The Telangana State Level Police Recruitment Board (TGPRB) will hold the Preliminary Written Test for SCT SI (Civil) and equivalent posts '
         '(Notification Rc.No.225/2026, 275 posts) on Sunday, 29 November 2026, in the forenoon, at the 10 erstwhile district headquarters. The date is marked tentative '
         '(press note of 17 September 2026); about 1.6 lakh applications were filed. Below: the hall ticket, exam-day rules, the pattern and qualifying marks, the posts, the salary and the physical tests.',
    te='టీఎస్ పోలీస్ ఎస్ఐ ప్రిలిమినరీ రాత పరీక్ష 2026: ఆదివారం, 29 నవంబర్ 2026 ఉదయం (తాత్కాలిక తేదీ). హాల్ టికెట్ డౌన్‌లోడ్, పరీక్ష రోజు నియమాలు, పరీక్ష విధానం, అర్హత మార్కులు, జీతం, పాత ప్రశ్నాపత్రాలు.',
    pdf=TGPRB + 'SI%20(Civil%20et%20al)%202026%20Notification%20dated%2029-07-2026.pdf',
    pdfname='TGPRB Notification Rc.No.225/Rect./Rect-1/2026 (SCT SI Civil and equivalent posts), dated 29 July 2026',
    more_src=[TS_SRC_1709, TS_SRC_0809, ('https://tgprb.in/Pdfs/PressNote29072022.pdf', 'TSLPRB hall-ticket press note of 29 July 2022 (exam-day instructions)'), TS_SRC_RES22],
    related=['ts-police-si-answer-key-2026.html', 'ts-police-constable-exam-date-hall-ticket-2026.html', 'ts-police-constable-answer-key-2026.html'],
    sections=[
      ('Important dates', 'table', [
        ('Notification (Rc.No.225/2026)', '29 July 2026'),
        ('Online applications', '19 August to 16 September 2026 (closed)'),
        ('Preliminary Written Test', 'Sunday, 29 November 2026, forenoon (tentative)'),
        ('Hall ticket', 'Date not announced yet. In 2022 the window opened 8 days before the exam, so expect it around 21 November 2026'),
        ('Exam centres', 'The 10 erstwhile district headquarters of Telangana'),
        ('Official website', 'www.tgprb.in')]),
      ('How to download the hall ticket', 'steps', [
        'Go to www.tgprb.in and open the hall-ticket link (it appears only when TGPRB opens the download window).',
        'Log in to your candidate account with the details you used to apply (in 2022: your registered mobile number and password).',
        'Download the hall ticket and print it on A4 paper, preferably on both sides, so the ticket and the instructions fit on one sheet.',
        'Paste the passport photo you uploaded with the application in the box on page 1, using gum.',
        'Check your name, photo, exam centre and timing; visit the centre a day before the exam.']),
      ('', 'note', 'In 2022 the SI hall tickets could be downloaded from 8 am on 30 July to midnight on 5 August for the exam on 7 August: the window closed two days before the exam. '
                   'Download yours as soon as it opens. The 2022 exam ran from 10 am to 1 pm; TGPRB has not announced the 2026 timing yet.'),
      ("Exam-day rules (TGPRB's hall-ticket instructions)", 'list', TS_RULES),
      ('Exam pattern', 'table+', (['Part', 'Subjects', 'Questions · marks'], [
        ('Part A', 'Arithmetic and Test of Reasoning / Mental Ability', '100 · 100'),
        ('Part B', 'General Studies', '100 · 100'),
        ('Total', 'One objective paper (OMR) of 3 hours, in English–Telugu or English–Urdu', '200 · 200')])),
      ('', 'note', 'Negative marking: 20% of a question\'s mark (0.2 of a mark) is deducted for each wrong answer; an unanswered question gets zero. '
                   'The prelims only qualifies you for the physical tests: its marks do not count in the final merit.'),
      ('Qualifying marks', 'table+', (['Category', 'Minimum', 'Out of 200'], [
        ('OC (including EWS)', '30%', 60), ('BC', '25%', 50), ('SC, ST and Ex-Servicemen', '20%', 40)])),
      ('', 'note', 'In 2022, 1,05,603 of the 2,25,668 candidates evaluated (46.8%) cleared the SI prelims. The average score was 47.25 and the highest 133 out of 200 (TSLPRB, 21 October 2022).'),
      ('Posts and vacancies', 'table+', (['Post', 'Vacancies'], [
        ('SCT Sub-Inspector of Police (Civil)', 148), ('SCT Reserve SI (AR)', 14), ('SCT Reserve SI (SAR CPL), men', 3), ('SCT Reserve SI (TGSP), men', 12),
        ('Sub-Inspector, Telangana Special Protection Force', 44), ('Station Fire Officer', 39), ('Deputy Jailor (men)', 14), ('Deputy Jailor (women)', 1), ('Total', 275)])),
      ('Salary', 'table+', (['Post', 'Pay scale (per month)'], [
        ('SCT SI (Civil); SI, Special Protection Force', '₹42,300 – ₹1,15,270'),
        ('Station Fire Officer; Deputy Jailor', '₹38,890 – ₹1,12,510')])),
      ('', 'note', 'TGPRB puts the starting annual pay of an SI (Police / SPF) at about ₹7.34 lakh to ₹8.0 lakh including HRA (press note of 8 September 2026). '
                   'SCT means Stipendiary Cadet Trainee: a stipend is paid during training.'),
      ('After the prelims: physical tests and the final exam', 'list', [
        'Physical Measurement Test: height at least 167.6 cm for men and 152.5 cm for women (160 cm and 150 cm for ST candidates of the notified agency areas). There is no chest measurement.',
        'Physical Efficiency Test: a 1,600 m run in 7 min 15 s for men (9 min 30 s for ex-servicemen) or 800 m in 5 min 20 s for women; the long jump (4 m men, 2.5 m women) and the shot put (6 m men, 4 m women) are qualifying.',
        'Final Written Examination: four papers of 3 hours. Paper I English and Paper II Telugu or Urdu are qualifying; Paper III Arithmetic & Reasoning and Paper IV General Studies (200 marks each for SI Civil) decide the merit. '
        'You need 40% (OC, EWS), 35% (BC) or 30% (SC, ST, Ex-Servicemen) in every paper.']),
    ]),
  'ts-police-si-answer-key-2026.html': dict(
    exam='ts-police-si', board='TGPRB', site='tgprb.in', crumb='SI Answer Key 2026',
    title='TS Police SI Answer Key 2026 (Prelims, 29 November) – Preliminary Key, Objections, Score Calculator, Qualifying Marks | Learn with Anil',
    desc='TS Police SI Prelims answer key 2026: when TGPRB releases the preliminary key and how to raise objections, a score calculator with the 0.2 negative mark, '
         'the qualifying marks (60/50/40 out of 200), the 2022 results in numbers, and the previous SI papers with answers.',
    h1='TS Police SI answer key 2026',
    lede='The TS Police SI Preliminary Written Test is on Sunday, 29 November 2026 (tentative). TGPRB publishes a preliminary key on www.tgprb.in a few days after the exam, '
         'takes objections question by question in the candidate login, and releases the final key with the results. Work out your score below with the 0.2 negative mark '
         'and see whether you clear the qualifying mark. We will add the 2026 question paper with answers here once the paper is available.',
    te='టీఎస్ పోలీస్ ఎస్ఐ ప్రిలిమ్స్ ఆన్సర్ కీ 2026 (పరీక్ష 29 నవంబర్): ప్రాథమిక కీ, అభ్యంతరాలు, మీ స్కోర్ లెక్కించండి (తప్పు సమాధానానికి 0.2 మార్కు కోత), అర్హత మార్కులు.',
    pdf=TGPRB + 'SI%20(Civil%20et%20al)%202026%20Notification%20dated%2029-07-2026.pdf',
    pdfname='TGPRB Notification Rc.No.225/Rect./Rect-1/2026, dated 29 July 2026',
    more_src=[TS_SRC_1709, ('https://tgprb.in/Pdfs/PressNoteDatedon1408022.pdf', 'TSLPRB press note of 14 August 2022 (preliminary key and objections)'), TS_SRC_RES22],
    related=['ts-police-si-exam-date-hall-ticket-2026.html', 'ts-police-constable-answer-key-2026.html'],
    sections=[
      ('Calculate your score', 'html', score_calc('scsi', 200, TS_QUAL)),
      ('When the key comes: what happened in 2022', 'table', [
        ('Preliminary key', '12 August 2022, five days after the 7 August exam'),
        ('Objections', '13 to 15 August 2022, question by question, in the candidate login on the board\'s website'),
        ('Final key and results', '21 October 2022, with the qualified list; candidates could see their OMR sheet in the login'),
        ('2026', 'TGPRB will announce the dates; this page will be updated')]),
      ('', 'note', 'TGPRB usually deletes a few questions (their marks are given to everyone) and accepts more than one answer for some, so your final score can differ slightly from the preliminary key.'),
      ('Qualifying marks', 'table+', (['Category', 'Minimum', 'Out of 200'], [
        ('OC (including EWS)', '30%', 60), ('BC', '25%', 50), ('SC, ST and Ex-Servicemen', '20%', 40)])),
      ('Is there a cut-off?', 'p', 'Not in the prelims. Everyone who reaches the qualifying mark of their category goes on to the physical tests; the competition is decided in the '
                                  'Final Written Examination (Papers III and IV for SI Civil), where TGPRB later publishes the marks of the last selected candidate in each category.'),
      ('The 2022 SI prelims in numbers', 'table', [
        ('Attended', '2,25,759 of 2,47,217 (91.3%)'), ('Qualified', '1,05,603 (46.8%)'),
        ('Qualified by category', 'BC 49,825 · SC 26,168 · ST 22,571 · OC 6,817 · Ex-Servicemen 222'),
        ('Average score', '47.25 out of 200'), ('Highest score', '133 out of 200'), ('Most common score', '36.80 (2,176 candidates)')]),
      ('', 'note', 'Scores in the 40s to 60s cleared the prelims in 2022 (the qualifying marks were cut to 30/25/20% in October 2022). Use the 2022 paper below to see the level.'),
    ]),
  'ts-police-constable-exam-date-hall-ticket-2026.html': dict(
    exam='ts-police-constable', board='TGPRB', site='tgprb.in', crumb='Constable Exam Date & Hall Ticket 2026',
    title='TS Police Constable Exam Date 2026 (20 December) & Hall Ticket – Download, Exam Pattern, Qualifying Marks, Salary | Learn with Anil',
    desc='TS Police Constable Preliminary Written Test 2026: Sunday 20 December 2026, forenoon (TGPRB, tentative). When and how to download the constable hall ticket, '
         'exam-day rules, the 200-mark pattern with 0.2 negative marking, qualifying marks (30/25/20%), 7,112 posts, salary ₹24,280–72,850, PMT/PET and previous papers.',
    h1='TS Police Constable exam date 2026: Sunday, 20 December',
    lede='TGPRB will hold the Preliminary Written Test for SCT Police Constable (Civil) and equivalent posts (Notification Rc.No.189/2026, 7,112 posts) on Sunday, '
         '20 December 2026, in the forenoon, at 15 to 18 centres including the 10 erstwhile district headquarters. The date is marked tentative (press note of 17 September 2026); '
         'about 3.9 lakh applications were filed. Below: the hall ticket, exam-day rules, the pattern and qualifying marks, the posts, the salary and the physical tests.',
    te='టీఎస్ పోలీస్ కానిస్టేబుల్ ప్రిలిమినరీ రాత పరీక్ష 2026: ఆదివారం, 20 డిసెంబర్ 2026 ఉదయం (తాత్కాలిక తేదీ). హాల్ టికెట్, పరీక్ష రోజు నియమాలు, పరీక్ష విధానం, అర్హత మార్కులు, జీతం, పాత ప్రశ్నాపత్రాలు.',
    pdf=TGPRB + 'PC%20(Civil%20et%20al)%202026%20Notification%20dated%2029-07-2026.pdf',
    pdfname='TGPRB Notification Rc.No.189/Rect./Rect-2/2026 (SCT PC Civil and equivalent posts), dated 29 July 2026',
    more_src=[TS_SRC_1709, TS_SRC_0809, ('https://tgprb.in/Pdfs/PressNoteDatedon1708022.pdf', 'TSLPRB hall-ticket press note of 17 August 2022'), TS_SRC_RES22],
    related=['ts-police-constable-answer-key-2026.html', 'ts-police-si-exam-date-hall-ticket-2026.html', 'ts-police-si-answer-key-2026.html'],
    sections=[
      ('Important dates', 'table', [
        ('Notification (Rc.No.189/2026)', '29 July 2026'),
        ('Online applications', '19 August to 16 September 2026 (closed)'),
        ('Preliminary Written Test', 'Sunday, 20 December 2026, forenoon (tentative)'),
        ('Hall ticket', 'Date not announced yet. In 2022 the window opened 10 days before the exam, so expect it around 10 December 2026'),
        ('Exam centres', '15 to 18 locations, including the 10 erstwhile district headquarters'),
        ('Official website', 'www.tgprb.in')]),
      ('How to download the hall ticket', 'steps', [
        'Go to www.tgprb.in and open the hall-ticket link (it appears only when TGPRB opens the download window).',
        'Log in to your candidate account with the details you used to apply (in 2022: your registered mobile number and password).',
        'Download the hall ticket and print it on A4 paper, preferably on both sides, so the ticket and the instructions fit on one sheet.',
        'Paste the passport photo you uploaded with the application in the box on page 1, using gum.',
        'Check your name, photo, exam centre and timing; visit the centre a day before the exam.']),
      ('', 'note', 'In 2022 the constable hall tickets could be downloaded from 8 am on 18 August to midnight on 26 August for the exam on 28 August: the window closed two days before the exam. '
                   'The 2022 exam ran from 10 am to 1 pm; TGPRB has not announced the 2026 timing yet.'),
      ("Exam-day rules (TGPRB's hall-ticket instructions)", 'list', TS_RULES),
      ('Exam pattern', 'table+', (['Paper', 'Subjects', 'Questions · marks · time'], [
        ('Preliminary Written Test (objective, OMR)', 'English, Arithmetic, General Science, History of India and the National Movement, Geography, Polity and Economy, '
                                                      'Current Events, Reasoning / Mental Ability, and Telangana-specific topics', '200 · 200 · 3 hours')])),
      ('', 'note', 'Negative marking: 0.2 of a mark is deducted for each wrong answer; an unanswered question gets zero. The question booklet is in English–Telugu or English–Urdu. '
                   'The prelims only qualifies you for the physical tests.'),
      ('Qualifying marks', 'table+', (['Category', 'Minimum', 'Out of 200'], [
        ('OC (including EWS)', '30%', 60), ('BC', '25%', 50), ('SC, ST, Ex-Servicemen and Home Guards', '20%', 40)])),
      ('', 'note', 'In 2022, 1,84,861 of the 5,88,891 candidates for constable (civil and equivalent) posts (31.4%) cleared the prelims. The average score was 41.16 and the highest 141 out of 200 (TSLPRB, 21 October 2022).'),
      ('Posts and vacancies', 'table+', (['Post', 'Vacancies'], [
        ('SCT Police Constable (Civil)', 3697), ('SCT Police Constable (AR)', 1052), ('SCT Police Constable (SAR CPL), men', 24),
        ('SCT Constable, Telangana Special Protection Force', 1380), ('Fire Fighter', 751), ('Warder (male)', 196), ('Warder (female)', 12), ('Total', 7112)])),
      ('Salary', 'p', 'Pay scale ₹24,280 – ₹72,850 a month for every post in this notification. TGPRB puts the starting annual pay of a constable at about ₹4.21 lakh to ₹4.59 lakh '
                      'including HRA (press note of 8 September 2026). SCT means Stipendiary Cadet Trainee: a stipend is paid during training.'),
      ('After the prelims: physical tests and the final exam', 'list', [
        'Physical Measurement Test: height at least 167.6 cm for men and 152.5 cm for women (160 cm and 150 cm for ST candidates of the notified agency areas). There is no chest measurement.',
        'Physical Efficiency Test: a 1,600 m run in 7 min 15 s for men (9 min 30 s for ex-servicemen) or 800 m in 5 min 20 s for women; the long jump (4 m men, 2.5 m women) and the shot put (6 m men, 4 m women) are qualifying. For AR, SAR CPL and SPF posts the run is scored.',
        'Final Written Examination: one objective paper of 3 hours, 200 marks for Civil constable, Fire Fighter and Warder (100 marks for AR, SAR CPL and SPF, where run marks are added). '
        'You need 40% (OC, EWS), 35% (BC) or 30% (SC, ST, Ex-Servicemen).']),
    ]),
  'ts-police-constable-answer-key-2026.html': dict(
    exam='ts-police-constable', board='TGPRB', site='tgprb.in', crumb='Constable Answer Key 2026',
    title='TS Police Constable Answer Key 2026 (Prelims, 20 December) – Preliminary Key, Objections, Score Calculator, Qualifying Marks | Learn with Anil',
    desc='TS Police Constable Prelims answer key 2026: when TGPRB releases the preliminary key and how to raise objections, a score calculator with the 0.2 negative mark, '
         'the qualifying marks (60/50/40 out of 200), the 2022 results in numbers, and the previous constable papers with answers.',
    h1='TS Police Constable answer key 2026',
    lede='The TS Police Constable Preliminary Written Test is on Sunday, 20 December 2026 (tentative). In 2022 TSLPRB released the preliminary key two days after the exam and took '
         'objections in the candidate login; the final key came with the results. Work out your score below with the 0.2 negative mark and see whether you clear the qualifying mark. '
         'We will add the 2026 question paper with answers here once the paper is available.',
    te='టీఎస్ పోలీస్ కానిస్టేబుల్ ప్రిలిమ్స్ ఆన్సర్ కీ 2026 (పరీక్ష 20 డిసెంబర్): ప్రాథమిక కీ, అభ్యంతరాలు, మీ స్కోర్ లెక్కించండి (తప్పు సమాధానానికి 0.2 మార్కు కోత), అర్హత మార్కులు.',
    pdf=TGPRB + 'PC%20(Civil%20et%20al)%202026%20Notification%20dated%2029-07-2026.pdf',
    pdfname='TGPRB Notification Rc.No.189/Rect./Rect-2/2026, dated 29 July 2026',
    more_src=[TS_SRC_1709, ('https://tgprb.in/Pdfs/PressNoteDatedon2808022.pdf', 'TSLPRB press note of 28 August 2022'), TS_SRC_RES22],
    related=['ts-police-constable-exam-date-hall-ticket-2026.html', 'ts-police-si-answer-key-2026.html'],
    sections=[
      ('Calculate your score', 'html', score_calc('scpc', 200, [('OC (including EWS): 30%', 60), ('BC: 25%', 50), ('SC, ST, Ex-Servicemen, Home Guards: 20%', 40)])),
      ('When the key comes: what happened in 2022', 'table', [
        ('Preliminary key', '30 August 2022, two days after the 28 August exam'),
        ('Objections', 'About three days, question by question, in the candidate login'),
        ('Final key and results', '21 October 2022, with the qualified list'),
        ('2026', 'TGPRB will announce the dates; this page will be updated')]),
      ('Qualifying marks', 'table+', (['Category', 'Minimum', 'Out of 200'], [
        ('OC (including EWS)', '30%', 60), ('BC', '25%', 50), ('SC, ST, Ex-Servicemen and Home Guards', '20%', 40)])),
      ('Is there a cut-off?', 'p', 'Not in the prelims. Everyone who reaches the qualifying mark of their category goes on to the physical tests; the competition is decided in the Final Written Examination.'),
      ('The 2022 constable prelims in numbers', 'table', [
        ('Attended (constable-level posts)', '6,03,955 of 6,61,198 (91.3%)'),
        ('Qualified, PC Civil and equivalent', '1,84,861 of 5,88,891 (31.4%)'),
        ('Average score', '41.16 out of 200'), ('Highest score', '141 out of 200')]),
    ]),
})


# AP DSC 2026 (APTRT-2026): brief notifications of 13 Oct 2026 (G.O.Ms.No.28) and the School Education press note with Annexures I-II
# (district and society tables checked twice against the PDF, 3 Nov 2026). Fee, age and TET rules below are the Mega DSC 2025 rules
# (G.O.Ms.No.15 and 16 of 19.04.2025) until the detailed 2026 notification is out. Research notes: claude/ap-dsc-2026.md.
APDSC = 'https://tet2dsc.apcfss.in/DSC2026/'
NOTIFS['ap-dsc-2026-notification.html'] = dict(
    exam=None, ename='AP DSC 2026', board='the School Education Department, Andhra Pradesh', site='tet2dsc.apcfss.in', crumb='AP DSC 2026 Notification',
    title='AP DSC 2026 Notification – 2,721 Teacher Posts (SA, SGT, Special Education, PGT, TGT), District-wise Vacancies, Dates, Eligibility & Exam Pattern | Learn with Anil',
    desc='AP DSC 2026 (APTRT-2026): 2,721 teacher posts, with 906 School Assistant, 1,205 SGT, 350 special-education and 260 residential-school posts; '
         'district-wise and society-wise vacancies; detailed notification out 4 November, online applications from 11 November 2026; fee, age limit, TET weightage and the CBT exam pattern.',
    h1='AP DSC 2026: 2,721 teacher posts',
    lede='The Andhra Pradesh School Education Department issued brief notifications on 13 October 2026 for 2,721 teacher posts (DSC-2026): 2,111 School Assistant and SGT posts '
         'in government, ZP, MPP and municipal schools, 350 special-education posts, and 260 posts in residential societies and model schools. The detailed notification, '
         'with the application dates, fee, age limit and exam schedule, was issued on Wednesday 4 November 2026 on tet2dsc.apcfss.in, and online applications open on 11 November 2026 '
         '(Deccan Chronicle and Sakshi Education, 5 November 2026). The exam is a computer-based test (CBT).',
    te='ఏపీ డీఎస్సీ 2026: 2,721 టీచర్ పోస్టులు — స్కూల్ అసిస్టెంట్ 906, ఎస్జీటీ 1,205, స్పెషల్ ఎడ్యుకేషన్ 350, గురుకులాలు/మోడల్ స్కూళ్లు 260. జిల్లాల వారీ ఖాళీలు, తేదీలు, అర్హత, పరీక్ష విధానం.',
    pdf=APDSC + 'DSC-2026%20Press%20Note%20English.pdf', pdfname='School Education Department press note on DSC-2026 with district-wise and society-wise vacancies (13 October 2026)',
    more_src=[(APDSC + 'notifications/DSC-2026%20General%20notification%20(1).pdf', 'Brief Notification No.1/DSC-2026 (General)'),
              (APDSC + 'notifications/DSC-2026%20Special%20Education%20Notifcation.pdf', 'Brief Notification No.2/DSC-2026 (Special Education)'),
              (APDSC + 'notifications/DSC-2026%20Socities%20Notification.pdf', 'Brief Notification No.3/DSC-2026 (Societies)'),
              (APDSC + 'Gos/2026SE_MS28_E.pdf', 'G.O.Ms.No.28, School Education, 13 October 2026'),
              ('https://tet2dsc.apcfss.in/DSC-PDF/Syllabus-2026/Special%20Education%20DSC%20-%202026.pdf', 'Special Education DSC syllabus 2026'),
              ('https://www.deccanchronicle.com/southern-states/andhra-pradesh/ap-releases-detailed-dsc-notification-applications-open-on-nov-11-2001889', 'Deccan Chronicle, 5 November 2026: detailed notification issued, applications from 11 November'),
              ('https://education.sakshi.com/en/ap-dsc/education-news/ap-dsc-2026-notification-released-2721-teacher-vacanciescheck-category-wise-and-society-wise-vacancies-202150', 'Sakshi Education, 5 November 2026: applications from 11 November')],
    sections=[
      ('Important dates', 'table', [
        ('Brief notifications (Nos. 1, 2 and 3/DSC-2026)', '13 October 2026'),
        ('Detailed notification', 'Issued Wednesday 4 November 2026 on tet2dsc.apcfss.in (as reported by Deccan Chronicle, 5 November 2026)'),
        ('Online applications open', '11 November 2026 (Deccan Chronicle and Sakshi Education, 5 November 2026)'),
        ('Last date, fee payment dates', 'In the detailed notification on tet2dsc.apcfss.in; not yet confirmed here'),
        ('Exam', 'Computer-based test; the dates are in the detailed notification (not yet confirmed here)'),
        ('Official website', 'tet2dsc.apcfss.in')]),
      ('Posts', 'table+', (['Post', 'Where', 'Posts'], [
        ('School Assistant (SA)', 'Government, ZP, MPP and municipal schools', 906),
        ('Secondary Grade Teacher (SGT)', 'Government, ZP, MPP and municipal schools', 1205),
        ('School Assistant (Special Education)', 'Government, ZP, MPP and municipal schools', 150),
        ('SGT (Special Education)', 'Government, ZP, MPP and municipal schools', 200),
        ('Principal', 'Residential societies and model schools', 30),
        ('Post Graduate Teacher (PGT)', 'Residential societies and model schools', 81),
        ('Trained Graduate Teacher (TGT)', 'Residential societies and model schools', 113),
        ('Physical Director', 'Residential societies', 2),
        ('Physical Education Teacher (PET)', 'Residential societies', 34),
        ('Total', 'All tentative; final numbers and rosters in the detailed notification', 2721)])),
      ('District-wise vacancies (government, ZP, MPP and municipal schools)', 'table+', (['District', 'SA', 'SGT', 'SA (SE)', 'SGT (SE)', 'Total'], [
        ('Srikakulam', 16, 4, 7, 9, 36),
        ('Vizianagaram', 0, 4, 6, 8, 18),
        ('Parvathipuram Manyam', 6, 2, 3, 4, 15),
        ('Alluri Sitharamaraju', 6, 153, 5, 7, 171),
        ('Visakhapatnam', 20, 9, 2, 3, 34),
        ('Anakapalli', 19, 1, 5, 7, 32),
        ('Kakinada', 51, 1, 5, 6, 63),
        ('Konaseema', 42, 1, 4, 6, 53),
        ('East Godavari', 9, 2, 5, 6, 22),
        ('West Godavari', 10, 0, 4, 6, 20),
        ('Eluru', 7, 1, 6, 8, 22),
        ('NTR', 19, 3, 4, 6, 32),
        ('Krishna', 15, 1, 6, 8, 30),
        ('Guntur', 24, 1, 4, 5, 34),
        ('Palnadu', 14, 0, 6, 8, 28),
        ('Bapatla', 17, 0, 4, 6, 27),
        ('Prakasam', 96, 170, 11, 14, 291),
        ('SPSR Nellore', 65, 100, 8, 11, 184),
        ('Tirupati', 22, 77, 8, 11, 118),
        ('Chittoor', 30, 100, 6, 8, 144),
        ('Annamayya', 46, 61, 5, 7, 119),
        ('YSR Kadapa', 48, 158, 9, 12, 227),
        ('Kurnool', 176, 213, 7, 8, 404),
        ('Nandyal', 40, 117, 6, 8, 171),
        ('Anantapuramu', 66, 26, 7, 9, 108),
        ('Sri Satya Sai', 42, 0, 7, 9, 58),
        ('Total', 906, 1205, 150, 200, 2461)])),
      ('', 'note', 'SE = special education. Kurnool (404), Prakasam (291), YSR Kadapa (227) and SPSR Nellore (184) have the most posts; Vizianagaram, West Godavari and Bapatla have no or almost no SGT posts. '
                   'The subject-wise split of School Assistant posts will be in the detailed notification.'),
      ('Society-wise vacancies (residential and model schools)', 'table+', (['Society / management', 'Principal', 'PGT', 'TGT', 'PD', 'PET', 'Total'], [
        ('APSWREIS (social welfare)', 21, 45, 0, 0, 19, 85), ('APTWREIS (tribal welfare, Gurukulam)', 0, 6, 27, 1, 2, 36),
        ('MJPAPBCWREIS (BC welfare)', 3, 10, 24, 0, 0, 37), ('APREIS', 4, 20, 32, 1, 11, 68), ('AP Model Schools', 2, 0, 17, 0, 0, 19),
        ('Welfare of Differently Abled, Transgender & Senior Citizens', 0, 0, 13, 0, 2, 15), ('Total', 30, 81, 113, 2, 34, 260)])),
      ('Exam pattern', 'table+', (['Post', 'Computer-based test', 'Plus'], [
        ('School Assistant (2025 pattern)', '160 questions, 80 marks, 2 h 30 min: GK & current affairs 10, perspectives in education 5, educational psychology 5, subject content 40, methodology 20', '20 marks of TET weightage'),
        ('SGT (2025 pattern)', '160 questions, 80 marks, 2 h 30 min', '20 marks of TET weightage'),
        ('SA and SGT, Special Education (2026 syllabus)', '160 questions, 80 marks, 2 h 30 min', '20 marks of TET weightage (2025 rule)'),
        ('SA (Physical Education), PET, PD (2025 pattern)', '200 questions, 100 marks, 3 hours', 'No TET'),
        ('PGT, Principal (2025 pattern)', 'English proficiency test (qualifying) + Paper II of 200 questions, 100 marks, 3 hours', 'No TET'),
        ('TGT (2025 pattern)', 'English proficiency test (qualifying, non-language TGT) + Paper II of 160 questions, 80 marks', '20 marks of TET weightage')])),
      ('', 'note', 'Each question carries half a mark in the 160-question papers. The 2026 special-education syllabus confirms the 160-question, 80-mark paper; the patterns for the other posts are from Mega DSC 2025 and will be confirmed by the detailed notification.'),
      ('Eligibility, fee and TET: the 2025 rules', 'list', [
        'Age (2025): 18 to 44 years, up to 49 for SC, ST, BC and EWS candidates and 54 for persons with disabilities. The reference date for 2026 will be in the detailed notification.',
        'Fee (2025): ₹750 for each post applied for.',
        'TET: SA (except Physical Education) and SGT candidates must have passed APTET or CTET; the TET score carries 20% of the final marks. PET, SA (Physical Education), PGT, PD and Principal posts need no TET.',
        'SGT: Intermediate with 50% (45% for SC, ST, BC and PwBD) and a two-year D.Ed / D.El.Ed (or B.El.Ed). SA: a degree in the subject with 50% (45%) and B.Ed with that methodology. PGT: a post-graduate degree with 50% and B.Ed.',
        'The Special TET of August 2026 (for in-service teachers) cannot be used to apply for DSC; the regular AP TET of June 2026 (results in September 2026) can.']),
      ('', 'note', 'These are the Mega DSC 2025 rules (G.O.Ms.No.15 and 16, 19 April 2025). The 2026 detailed notification may change them: check it before applying.'),
      ('How Mega DSC 2025 went', 'table', [
        ('Notification', '20 April 2025, 16,347 posts'), ('Applications', '20 April to 15 May 2025'), ('Exams (CBT)', '6 June to 2 July 2025'),
        ('Question papers with preliminary keys', 'From 18 June 2025, as each exam finished'), ('Final key', 'Early August 2025'), ('Results', '12 August 2025; 15,941 teachers selected')]),
    ],
    tail_html='<h2>Prepare with previous questions</h2><p>The GK and current-affairs part of DSC overlaps with APPSC and police exams. <a href="/">Learn with Anil</a> has previous year questions with answers '
              'for APPSC Group 1 and 2, AP and TS Police, SSC and UPSC: <a href="/appsc-pyqs.html">all APPSC previous papers</a> · <a href="/appsc-group-2/">APPSC Group 2</a> · <a href="/ap-police-pyqs.html">AP Police</a>.</p>')


MSY_STYLE = ('<style>.msy h3{font-size:16.5px;margin:16px 0 6px}.msy ol{margin:0 0 6px;padding-left:0;list-style:none;columns:2 300px;column-gap:28px}'
             '.msy li{margin:0 0 4px;break-inside:avoid}.msy .no{font:12.5px "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);margin-right:4px}'
             '.msy .hy{color:#B7791F;font-weight:700}.msy .nw,.msy .sub{font-size:13px;color:var(--muted)}.msy .sm{color:var(--muted);font-size:14.5px;margin:-4px 0 6px}</style>')


# APPSC Group 2 syllabus page (Anil, 30 Oct 2026: "add micro listing of group-2 syllabus"): the topic-wise outline of his
# Group-II Micro-Syllabus book (src/appsc-group-2-micro-syllabus.json: 9 subjects, units, 267 sub-topic names; star = asked
# 4+ times in the 2019-2025 Group-II papers, new = not asked yet). Which papers asked each sub-topic, the notes and the
# 2025-26 current affairs stay in the book (book g2micro-en, All-in-One Pass); this page links to its free sample.
def g2_syllabus_notif():
    path = os.path.join(SRC, 'appsc-group-2-micro-syllabus.json')
    if not os.path.exists(path): return None
    subs = json.load(open(path, encoding='utf-8'))
    ntop = sum(len(u['topics']) for s in subs for u in s['units'])
    nstar = sum(t['star'] for s in subs for u in s['units'] for t in u['topics'])
    sample = '/LearnWithAnil-APPSC-Group-2-Micro-Syllabus-Free-Sample.pdf'
    style = MSY_STYLE
    book = (f'<div class="note"><b>Get the full Micro-Syllabus (47-page PDF).</b> For every sub-topic below it shows which Group-II papers (2019–2025) asked it '
            f'and how many times, with short exam notes, 1,004 previous questions mapped and 112 current-affairs points of 2025–26 attached to their subjects. '
            f'<a href="{sample}">Download the free sample (PDF)</a>: cover, exam pattern, contents and the whole Indian History unit. '
            f'The full book is included in the ₹{PAY["pyq_price"]} All-in-One Pass: <a href="/appsc-group-2/notes/">Group-II study material</a>.</div>')
    secs = [('Exam pattern', 'table+', (['Stage', 'Subjects', 'Marks'], [
                ('Screening Test (objective)', 'Indian History · Geography · Indian Society · Current Affairs · Mental Ability, 30 marks each', '150'),
                ('Mains Paper I (objective)', 'Social and Cultural History of Andhra Pradesh (75) · General Overview of the Indian Constitution (75)', '150'),
                ('Mains Paper II (objective)', 'Indian and Andhra Pradesh Economy (75) · Science and Technology (75)', '150')])),
            ('', 'note', 'Negative marking: one-third of a mark for each wrong answer. The Screening Test only shortlists candidates for the Mains; selection is on the Mains marks. '
                         'Notification 37/2026 follows the same pattern and syllabus as Notification 11/2023.'),
            ('', 'html', style + book)]
    for s in subs:
        hy = sum(t['star'] for u in s['units'] for t in u['topics'])
        n = sum(len(u['topics']) for u in s['units'])
        h = [f'<div class="msy"><h2>{s["no"]:02d}. {esc(s["name"])}</h2>',
             f'<p class="sm">{esc(s["stage"])} · {s["marks"]} marks · {n} sub-topics, {hy} high-yield ★</p>']
        for u in s['units']:
            items = ''.join(f'<li><span class="no">{esc(t["no"])}</span>{esc(t["title"])}'
                            + (' <span class="hy" title="Asked 4 or more times">★</span>' if t['star'] else '')
                            + (' <span class="nw">(not asked yet)</span>' if t['new'] else '') + '</li>' for t in u['topics'])
            h.append(f'<h3>{u["no"]}. {esc(u["title"])}</h3><ol>{items}</ol>')
        secs.append(('', 'html', ''.join(h) + '</div>'))
    secs.append(('How to use this syllabus', 'list', [
        'Start with the ★ sub-topics: APPSC has asked each of them four or more times in the Group-II papers of 2019–2025.',
        'Then cover the rest of each unit; sub-topics marked "not asked yet" are still in the official syllabus.',
        'After each unit, practise the previous questions of that subject and attach the 2025–26 current affairs to it.']))
    return dict(
        exam='appsc-group-2', crumb='Group 2 Syllabus 2026',
        title='APPSC Group 2 Syllabus 2026 – Topic-wise Micro Syllabus for Screening Test & Mains (Notification 37/2026) | Learn with Anil',
        desc=(f'APPSC Group 2 syllabus 2026, topic by topic: all 9 subjects of the Screening Test and Mains Paper I and II broken into {ntop} sub-topics, '
              f'with the {nstar} high-yield topics APPSC has asked 4 or more times marked. Exam pattern and a free micro-syllabus PDF sample.'),
        h1='APPSC Group 2 syllabus 2026: topic-wise micro syllabus',
        lede=(f'The APPSC Group-II syllabus (Notification 37/2026, same as 11/2023), broken into {ntop} sub-topics across all 9 subjects of the Screening Test and the Mains. '
              f'★ marks the {nstar} sub-topics APPSC has asked four or more times in the 2019–2025 Group-II papers: start there. '
              f'Built from APPSC\'s own papers by Jupudi Anil Kumar.'),
        te=f'APPSC గ్రూప్ 2 సిలబస్ 2026 — స్క్రీనింగ్ టెస్ట్, మెయిన్స్ పేపర్ I, II లోని 9 సబ్జెక్టులు {ntop} ఉప-అంశాలుగా; నాలుగు లేదా అంతకంటే ఎక్కువసార్లు అడిగిన అంశాలకు ★ గుర్తు.',
        pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Group_II_372026.pdf',
        pdfname='APPSC brief notification No. 37/2026 (pattern and syllabus as in Notification 11/2023); topic breakdown: Learn with Anil, APPSC Group-II Micro-Syllabus',
        sections=secs)



# APPSC EO Grade-III syllabus page (Anil, 30 Oct 2026: "also add Endowment officer too", after the Group 2 micro syllabus page):
# Paper II in the chapters and sections of his Hindu Philosophy & Temple System book (src/appsc-eo-micro-syllabus.json: 10
# chapters, 81 sections and their sub-headings), Paper I by the site's subject topics; every part shows how many questions
# APPSC asked from it, counted from the EO papers on the site at build time (2022 Screening, 2023 Mains, 2026).
# APPSC Group-I syllabus page (Anil, 3 Nov 2026). Section structure and marks: Notification 07/2026 as reported (FJA/Adda247, Oct 2026), the
# same scheme as APPSC's revised Group-I syllabus of October 2018; units summarised in our words. PYQ counts come from the site's 2019, 2023
# and 2024 screening papers at build time; the Mains part links to the Mains PYQ pages.
G1_SYL = [
  ('Paper I: General Studies', '120 questions · 120 marks · 120 minutes', [
    ('A. History and Culture', 30, ['ih'], [
      'Ancient India: Indus Valley, Vedic age and Mahajanapadas, Jainism and Buddhism, the Mauryas, foreign invasions, the Kushans, Satavahanas, Sangam age, Sungas and Guptas',
      'Early medieval and South India: Kanauj, the Badami and Eastern Chalukyas, Rashtrakutas, Kalyani Chalukyas, Cholas, Hoysalas, Yadavas, Kakatiyas and Reddis',
      'Delhi Sultanate, Vijayanagara and the Mughals; Bhakti and Sufi movements; administration, society, literature, art and architecture',
      'European trading companies and their struggle for supremacy (Bengal, Bombay, Madras, Mysore, Andhra, the Nizam); Governors-General and Viceroys',
      'The revolt of 1857; 19th-century religious and social reform movements; the freedom movement and revolutionaries in India and abroad',
      'Gandhi, Patel, Subhas Bose and Ambedkar; post-independence consolidation and the reorganisation of states']),
    ('B. Constitution, Polity, Social Justice and International Relations', 30, ['pol'], [
      'The Constitution: evolution, features, Preamble, Fundamental Rights and Duties, Directive Principles, amendments and the basic structure',
      'Union and states; Parliament and state legislatures; issues of the federal structure; devolution of powers and finances to local bodies',
      'Constitutional authorities; Panchayati Raj; public policy and governance',
      'Liberalisation, privatisation and globalisation and governance; statutory, regulatory and quasi-judicial bodies',
      'Rights issues: human rights, women, SC and ST, children',
      'India\'s foreign policy and international relations; important institutions and agencies; major central and state government schemes']),
    ('C. Indian and Andhra Pradesh Economy and Planning', 30, ['eco'], [
      'Features of the Indian economy, NITI Aayog, human development, environment and sustainable development',
      'National income, demography, poverty and inequality, unemployment, employment and poverty schemes, rural and urban development',
      'Agriculture, irrigation, land reforms, agricultural credit and MSP, food security; industry and industrial policy, Make in India, SEZs and corridors; energy; trade, balance of payments and the WTO',
      'RBI and monetary policy, banking reforms and NPAs, markets and SEBI; taxes and GST; Centre-state finances and Finance Commissions; public debt, fiscal policy and the budget',
      'The Andhra Pradesh economy after 2014: urbanisation, skills and welfare; the AP Reorganisation Act, 2014 and the special-status question']),
    ('D. Geography', 30, ['geo'], [
      'General geography: the solar system, the earth\'s motions and interior, the atmosphere, climate change and oceans',
      'Physical geography of the world, India and AP: earthquakes and landslides, drainage, monsoon, vegetation, parks and sanctuaries, soils, rocks and minerals',
      'Social geography: population, density, sex ratio, literacy, SC and ST population, urbanisation and migration',
      'Economic geography: sectors of the economy, basic industries, transport and trade']),
  ]),
  ('Paper II: General Aptitude', '120 questions · 120 marks · 120 minutes', [
    ('A. General Mental Ability, Administrative and Psychological Abilities', 60, ['men', 'apt'], [
      'Reasoning: logical and analytical reasoning, number series, coding-decoding, relations, Venn diagrams, clocks, calendars and ages',
      'Arithmetic: number system, ratio and proportion, averages (mean, median, mode), powers and roots, HCF and LCM, percentages, interest, profit and loss, time and work, time and distance',
      'Mensuration and geometry; basic algebra and simplification; data interpretation, data sufficiency and probability',
      'Emotional and social intelligence, interpersonal skills, decision making, critical thinking, problem solving and personality']),
    ('B. Science and Technology', 30, ['sci'], [
      'Science and technology policy, institutions and Indian scientists',
      'Information and communication technology, e-governance and cyber security',
      'Space and defence: ISRO and satellite programmes (communication, IRNSS, remote sensing), DRDO',
      'Energy: India\'s needs and resources, energy policy, solar, wind and nuclear power',
      'Environment: biodiversity, climate change, forest and wildlife law, pollution, disaster management; biotechnology, nanotechnology and genetic engineering; health and environment']),
    ('C. Current Affairs', 30, ['cur'], ['Current events of regional, national and international importance']),
  ]),
]
G1_MAINS = [
  ('Telugu', 'qualifying', None), ('English', 'qualifying', None),
  ('Paper I: General Essay', 'three essays, one from each section', '2025-paper-1'),
  ('Paper II: History, Culture and Geography of India and Andhra Pradesh', '', '2025-paper-2'),
  ('Paper III: Polity, Constitution, Governance, Law and Ethics', '', '2025-paper-3'),
  ('Paper IV: Economy and Development of India and Andhra Pradesh', '', '2025-paper-4'),
  ('Paper V: Science, Technology and Environmental Issues', '', '2025-paper-5'),
]


def g1_syllabus_notif():
    def sections(conf, papers, questions):
        subj = {x[0]: x for x in conf['subjects']}
        cnt, tcnt = {}, {}
        for q in questions:
            cnt[q['s']] = cnt.get(q['s'], 0) + 1
            tcnt[(q['s'], q.get('t'))] = tcnt.get((q['s'], q.get('t')), 0) + 1
        years = sorted({p['year'] for p in papers if p.get('fmt') == 'mcq'})
        surl = lambda sid: f'{conf["pb"]}subjects/{conf["slugp"]}-{subj[sid][2]}-pyqs.html'
        ny = ', '.join(map(str, years[:-1])) + ' and ' + str(years[-1]) if len(years) > 1 else str(years[0])
        secs = [('Exam pattern', 'table+', (['Stage', 'Papers', 'Marks · time'], [
                    ('Screening test (objective, OMR)', 'Paper I General Studies; Paper II General Aptitude', '120 + 120 marks · 120 min each'),
                    ('Mains (descriptive)', 'Telugu and English (qualifying); Papers I–V', '150 marks each, 3 hours each (Papers I–V: 750)'),
                    ('Interview', 'Personality test', '75 marks')])),
                ('', 'note', f'In the screening test one-third of a mark is cut for each wrong answer, and its marks only decide who goes to the Mains (about 50 candidates per post). '
                             f'Final merit is out of 825 (Mains 750 + interview 75). The numbers below are the questions APPSC asked from each part in the {ny} screening tests on this site.'),
                ('', 'html', MSY_STYLE)]
        for title, meta, parts in G1_SYL:
            n = sum(cnt.get(sid, 0) for _, _, sids, _ in parts for sid in sids)
            h = [f'<div class="msy"><h2>{esc(title)}</h2><p class="sm">{esc(meta)} · {n} previous questions on this site</p>']
            for name, marks, sids, units in parts:
                k = sum(cnt.get(sid, 0) for sid in sids)
                tops = ' · '.join(f'{esc(t)} {tcnt[(sid, t)]}' for sid in sids for t in subj[sid][3] if tcnt.get((sid, t)))
                links = ', '.join(f'<a href="{surl(sid)}">{esc(subj[sid][1])} questions</a>' for sid in sids if cnt.get(sid))
                items = ''.join(f'<li>{esc(u)}</li>' for u in units)
                h.append(f'<h3>{esc(name)} <span class="sub">({marks} marks)</span></h3><p class="sm">{k} PYQs{": " + tops if tops else ""}'
                         f'{" · Practise: " + links if links else ""}</p><ol>{items}</ol>')
            secs.append(('', 'html', ''.join(h) + '</div>'))
        mp = f'{conf["pb"]}mains-pyqs/'
        rows = ''.join(f'<li><b>{esc(t)}</b>{" (" + esc(x) + ")" if x else ""}'
                       + (f' · <a href="{mp}{slug}.html">2025 questions with model answers</a>' if slug else '') + '</li>' for t, x, slug in G1_MAINS)
        secs.append(('Mains syllabus at a glance', 'html',
                     f'<p>Seven descriptive papers of 150 marks and 3 hours each. Telugu and English (Class X standard) only have to be passed; Papers I to V count for the merit.</p>'
                     f'<ul>{rows}</ul><p><a href="{mp}">Every Group 1 Mains question of 2020, 2023 and 2025, paper by paper and topic by topic, with model answers</a></p>'))
        secs.append(('How to use this syllabus', 'list', [
            'Paper I sections carry 30 marks each, so no section can be skipped; start with the topics that have the most previous questions above.',
            'Half of Paper II (60 marks) is mental ability and administrative and psychological abilities: practise it daily with a timer, it is the easiest place to gain marks.',
            'Science and technology and current affairs move with the news: read the last 12 months of AP and national developments with the static topics.',
            'Take the 2024, 2023 and 2019 papers as full timed tests (120 questions in 120 minutes) with the one-third negative mark in mind.']))
        return secs

    return dict(
        exam='appsc-group-1', crumb='Group 1 Syllabus 2026',
        title='APPSC Group 1 Syllabus 2026 – Prelims (Screening) Paper I & II Topic-wise with PYQ Counts, Mains Papers I–V | Learn with Anil',
        desc='APPSC Group 1 syllabus 2026 (Notification 07/2026), topic by topic: Screening Test Paper I General Studies (history, polity, economy, geography, 30 marks each) and '
             'Paper II General Aptitude (mental ability 60, science and technology 30, current affairs 30), how many previous questions APPSC asked from each topic, and the Mains papers.',
        h1='APPSC Group 1 syllabus 2026: topic-wise, with previous-question counts',
        lede='The APPSC Group-I syllabus for Notification 07/2026, part by part: the two screening-test papers of 120 marks each and the seven Mains papers. Each part of the screening test '
             'shows how many questions APPSC actually asked from it in the 2019, 2023 and 2024 papers, so you know where the marks are. The screening test is tentatively on 24 January 2027.',
        te='ఏపీపీఎస్సీ గ్రూప్ 1 సిలబస్ 2026: ప్రిలిమ్స్ పేపర్ 1, 2 టాపిక్‌ల వారీగా — ప్రతి భాగం నుంచి గత పరీక్షల్లో ఎన్ని ప్రశ్నలు వచ్చాయో, మెయిన్స్ పేపర్లు.',
        pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Group_I_07_2026.pdf', pdfname='APPSC Notification No. 07/2026 (Group-I Services), scheme and syllabus',
        related=['appsc-group-1-notification-2026.html', 'appsc-group-2-syllabus-2026.html'],
        sections=[], sections_fn=sections)


def eo_syllabus_notif():
    path = os.path.join(SRC, 'appsc-eo-micro-syllabus.json')
    if not os.path.exists(path): return None
    chs = json.load(open(path, encoding='utf-8'))
    nsec = sum(len(c['sections']) for c in chs)
    sample = '/LearnWithAnil-EO-Grade-3-Hindu-Philosophy-Temple-System-Free-Sample.pdf'

    def sections(conf, papers, questions):
        subj = {x[0]: x for x in conf['subjects']}
        cnt, tcnt = {}, {}
        for q in questions:
            cnt[q['s']] = cnt.get(q['s'], 0) + 1
            tcnt[(q['s'], q.get('t'))] = tcnt.get((q['s'], q.get('t')), 0) + 1
        surl = lambda sid: f'{conf["pb"]}subjects/{conf["slugp"]}-{subj[sid][2]}-pyqs.html'
        p2 = {sid for c in chs for sid in c['subjects']}
        n2 = sum(cnt.get(sid, 0) for sid in p2)
        n1 = sum(v for k, v in cnt.items() if k not in p2)
        book = (f'<div class="note"><b>Study material for Paper II.</b> Each chapter below is a chapter of Learn with Anil\'s <b>Hindu Philosophy &amp; Temple System</b> notes '
                f'(167 pages), written from the questions APPSC has actually asked, with APPSC\'s 2023 and 2026 Paper II questions and official answers at the end. '
                f'<a href="{sample}">Download the free sample chapter (PDF)</a>; the full book is included in the ₹{PAY["pyq_price"]} All-in-One Pass: '
                f'<a href="{conf["pb"]}notes/">EO study material</a>.</div>')
        secs = [('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
                    ('Paper I (objective, degree standard)', 'General Studies & Mental Ability', '150 · 150 · 150 min'),
                    ('Paper II (objective, degree standard)', 'Hindu Philosophy & Temple System', '150 · 150 · 150 min'),
                    ('Computer Proficiency Test', 'Office automation with computers; qualifying', '—')])),
                ('', 'note', 'One-third of a mark is deducted for each wrong answer. Selection is on the 300 marks of the written examination, after the qualifying '
                             'Computer Proficiency Test. The counts below are the questions APPSC asked from each part in the 2022 Screening Test, the 2023 Mains and the 2026 exam.'),
                ('', 'html', MSY_STYLE + book)]
        h = [f'<div class="msy"><h2>Paper II: Hindu Philosophy &amp; Temple System</h2>'
             f'<p class="sm">150 marks · {len(chs)} chapters · {nsec} sub-topics · {n2} previous questions on this site</p>']
        for c in chs:
            k = sum(cnt.get(sid, 0) for sid in c['subjects'])
            tops = ' · '.join(f'{esc(t)} {tcnt[(sid, t)]}' for sid in c['subjects'] for t in subj[sid][3] if tcnt.get((sid, t)))
            links = ', '.join(f'<a href="{surl(sid)}">{esc(subj[sid][1])} questions</a>' for sid in c['subjects'] if cnt.get(sid))
            items = ''.join(f'<li><span class="no">{esc(x["no"])}</span>{esc(x["title"])}'
                            + (f' <span class="sub">({esc("; ".join(x["subs"]))})</span>' if x['subs'] else '') + '</li>' for x in c['sections'])
            h.append(f'<h3>{c["no"]:02d}. {esc(c["title"])}</h3><p class="sm">{k} PYQs{": " + tops if tops else ""}'
                     f'{" · Practise: " + links if links else ""}</p><ol>{items}</ol>')
        secs.append(('', 'html', ''.join(h) + '</div>'))
        h = [f'<div class="msy"><h2>Paper I: General Studies &amp; Mental Ability</h2>'
             f'<p class="sm">150 marks · {n1} previous questions on this site, by topic</p>']
        for sid, name, slug, topics in conf['subjects']:
            if sid in p2 or not cnt.get(sid): continue
            items = ''.join(f'<li>{esc(t)} <span class="sub">({tcnt[(sid, t)]} PYQs)</span></li>' for t in topics if tcnt.get((sid, t)))
            h.append(f'<h3>{esc(name)}</h3><p class="sm">{cnt[sid]} PYQs · <a href="{surl(sid)}">Practise {esc(name)} questions</a></p><ol>{items}</ol>')
        secs.append(('', 'html', ''.join(h) + '</div>'))
        secs.append(('How to use this syllabus', 'list', [
            'Paper II is the paper special to this post and half of the 300 marks: read it chapter by chapter, starting with the chapters APPSC asks most from.',
            'APPSC\'s Paper II questions are short and factual (which Kanda, Parva, Purana, Agama or section of the Act), so revise from tables and one-line facts.',
            'For Paper I, practise the previous questions topic by topic, then take full timed tests of the 2026 and 2023 papers.']))
        return secs

    return dict(
        exam='appsc-eo', crumb='EO Grade-III Syllabus 2026',
        title='APPSC EO Grade 3 Syllabus 2026 – Topic-wise Micro Syllabus, Paper I & Paper II (Hindu Philosophy & Temple System) | Learn with Anil',
        desc=(f'APPSC Endowment Officer (EO Grade-III) syllabus 2026, topic by topic: Paper II Hindu Philosophy & Temple System in {len(chs)} chapters and {nsec} sub-topics, '
              'Paper I General Studies & Mental Ability by topic, with how many previous questions APPSC asked from each part (2022–2026). Free sample notes PDF.'),
        h1='APPSC EO Grade 3 syllabus 2026: topic-wise micro syllabus',
        lede=(f'The APPSC Executive Officer Grade-III syllabus (Notification 23/2026), broken into topics: Paper II, Hindu Philosophy & Temple System, in {len(chs)} chapters '
              f'and {nsec} sub-topics, and Paper I, General Studies & Mental Ability, by topic. Each part shows how many questions APPSC asked from it in the 2022 Screening Test, '
              'the 2023 Mains and the 2026 exam, so you know where to start. Built by Jupudi Anil Kumar.'),
        te=(f'ఏపీపీఎస్సీ ఎండోమెంట్ ఆఫీసర్ (EO గ్రేడ్-III) సిలబస్ 2026 — పేపర్-2 హిందూ తత్వశాస్త్రం & దేవాలయ వ్యవస్థ {len(chs)} అధ్యాయాలు, {nsec} ఉప-అంశాలుగా; '
            'పేపర్-1 జనరల్ స్టడీస్ అంశాల వారీగా, ప్రతి అంశం నుంచి అడిగిన పాత ప్రశ్నల సంఖ్యతో.'),
        pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/EO_Grade_III_DetailedNotification_232026.pdf',
        pdfname='APPSC Notification No. 23/2026 (syllabus in Annexure-II); topic breakdown: Learn with Anil',
        sections=[], sections_fn=sections)

def notif_page(loaded, rel):
    N = NOTIFS[rel]
    hit = next((x for x in loaded if x[0]['id'] == N['exam']), None) if N.get('exam') else None
    conf, papers, questions = hit if hit else (None, [], [])
    board, site = N.get('board', 'APPSC'), N.get('site', 'psc.ap.gov.in')   # who issued it, and their website (for the source note)
    can = f'{SITE_URL}/{rel}'
    body = ['<style>main{overflow-wrap:break-word}main li,main td{overflow-wrap:anywhere}.qa{border:1px solid var(--line);border-radius:12px;padding:10px 14px;margin:8px 0;background:var(--surface)}.qa summary{font-weight:700;cursor:pointer}.qa p{margin:8px 0 2px}</style>']
    if N.get('te'): body.append(f'<p lang="te" style="margin:0 0 6px">{esc(N["te"])}</p>')
    elif N.get('hi'): body.append(f'<p lang="hi" style="margin:0 0 6px">{esc(N["hi"])}</p>')
    if conf: body.append(f'<a class="cta" href="{conf["pb"]}mock-test.html">{esc(conf["seo"])} mock tests</a><a class="cta alt" href="{conf["pb"]}papers/">All {esc(conf["seo"])} previous papers</a>')
    for head, kind, data in (N['sections_fn'](conf, papers, questions) if N.get('sections_fn') else N['sections']):
        if head: body.append(f'<h2>{esc(head)}</h2>')
        if kind == 'table': body.append(facts_table(data))
        elif kind == 'table+': body.append('<div style="overflow-x:auto">' + facts_table(data[1], data[0]) + '</div>')
        elif kind == 'list': body.append('<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in data) + '</ul>')
        elif kind == 'steps': body.append('<ol>' + ''.join(f'<li>{esc(x)}</li>' for x in data) + '</ol>')
        elif kind == 'note': body.append(f'<p class="note">{esc(data)}</p>')
        elif kind == 'html': body.append(data)   # trusted markup written here (links)
        else: body.append(f'<p>{esc(data)}</p>')
    if N.get('faqs'):   # "Quick answers": the questions students type into Google and ChatGPT (Anil, 4 Nov 2026: "masala questions")
        body.append(f'<h2 id="quick-answers">Quick answers{esc(" (as of " + N["faq_asof"] + ")") if N.get("faq_asof") else ""}</h2>'
                    + ''.join(f'<details class="qa"{" open" if i < 3 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(N['faqs']))
                    + '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
                        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in N['faqs']]}, ensure_ascii=False) + '</script>')
    if N.get('related'):   # other pages for the same exam (hall ticket, answer key, syllabus, salary…)
        body.append('<h2>More on this exam</h2><ul>' + ''.join(f'<li><a href="/{r}">{esc(re.sub("<[^>]+>", "", NOTIFS[r]["h1"]))}</a></li>'
                                                            for r in N['related'] if r in NOTIFS and r != rel) + '</ul>')
    if conf and not N.get('no_practice'):
        key = 'the official answer keys (where the board has published them)' if board != 'APPSC' else "APPSC's final key"
        body.append(f'<h2>Start with the previous papers</h2><p>Every {esc(conf["name"])} paper on this site comes with the answers from {key} and a short '
                    f'explanation in English and {esc(conf["l2"]["name"])}. Practise a paper online or take it as a timed mock test.</p>' + practice_links(conf, papers, questions))
    elif not conf:
        body.append(N.get('tail_html', '<h2>Practise previous papers</h2><p><a href="/">Learn with Anil</a> has previous year questions with answers for APPSC, TGPSC, '
                                       'TS and AP Police, SSC and UPSC exams. <a href="/appsc-pyqs.html">All APPSC previous papers</a> · <a href="/ts-police-pyqs.html">TS Police previous papers</a></p>'))
    more = ''.join(f'; <a href="{u}" rel="nofollow">{esc(nm)}</a>' for u, nm in N.get('more_src', []))
    body.append(f'<p class="note">Source: <a href="{N["pdf"]}" rel="nofollow">{esc(N["pdfname"])}</a>{more}. Dates and vacancies can change with corrigenda; '
                f'always check the official website {esc(site)} before applying. Learn with Anil is not connected with {esc(board)}.</p>')
    crumbs = [('Home', SITE_URL + '/')] + ([(conf['name'], SITE_URL + conf['pb'])] if conf else []) + [(N['crumb'], can)]
    return static_page(0, N['title'], N['desc'], can, N['h1'], esc(N['lede']), ''.join(body), crumbs, conf, ename=N.get('ename'), at_root=True, head_all=not conf,
                       foot_text=None if conf else f'Exam information compiled from {board}\'s official notifications by Jupudi Anil Kumar, Learn with Anil. Not affiliated with {board}.')


NEWS_HUB = 'exam-notifications.html'
NEWS_BOARDS = [('UPSC', 'UPSC'), ('SSC', 'SSC'), ('APPSC', 'APPSC (Andhra Pradesh)'), ('SLPRB AP', 'AP Police (SLPRB)'), ('AP DSC', 'AP DSC (teachers)'),
               ('TGPSC', 'TGPSC (Telangana)'), ('TGPRB', 'TS Police (TGPRB)')]


def news_hub_page(loaded, rels):
    """/exam-notifications.html: every notification / exam-date / answer-key / syllabus page, grouped by board, with its first
    Quick answer, so students (and Google) find the latest news for each exam in one place (Anil, 4 Nov 2026: "update SEO")."""
    names = {c['id']: c['name'] for c, _, _ in loaded}
    groups = {}
    for rel in rels:
        N = NOTIFS[rel]
        b = 'AP DSC' if rel.startswith('ap-dsc') else N.get('board', 'APPSC')
        groups.setdefault(b, []).append(rel)
    body = ['<style>.nh{list-style:none;padding:0;margin:0}.nh li{border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:8px 0;background:var(--surface)}'
            '.nh a{font-weight:700}.nh p{margin:6px 0 0;font-size:15px;color:var(--muted)}</style>',
            '<p>The latest official news for every exam on Learn with Anil: notifications, last dates and extensions, exam dates, hall tickets, answer keys and syllabus, '
            'each with quick answers to the questions students ask and links to the previous papers. Pages show the date their facts were checked.</p>']
    order = [b for b, _ in NEWS_BOARDS] + sorted(set(groups) - {b for b, _ in NEWS_BOARDS})
    for b in order:
        if b not in groups: continue
        label = dict(NEWS_BOARDS).get(b, b)
        items = []
        for rel in groups[b]:
            N = NOTIFS[rel]
            h1 = re.sub('<[^>]+>', '', N['h1'])
            ex = f' · {esc(names[N["exam"]])}' if N.get('exam') in names and names[N['exam']].lower() not in h1.lower() else ''
            qa = N.get('faqs') or []
            sub = f'{esc(qa[0][0])} {esc(qa[0][1])}' if qa else esc(N['lede'].split('. ')[0].rstrip('.') + '.')
            items.append(f'<li><a href="/{rel}">{esc(h1)}</a>{ex}<p>{sub}</p></li>')
        body.append(f'<h2 id="{re.sub("[^a-z]+", "-", b.lower()).strip("-")}">{esc(label)}</h2><ul class="nh">' + ''.join(items) + '</ul>')
    body.append('<p class="note">Compiled from the boards\' official notifications and web notes by Jupudi Anil Kumar, Learn with Anil. Dates can change; always check the '
                'board\'s website before applying. Learn with Anil is not connected with any recruiting board.</p>')
    can = f'{SITE_URL}/{NEWS_HUB}'
    return static_page(0, 'Govt Exam Notifications 2026 – APPSC, TGPSC, UPSC, SSC, TS & AP Police: Last Dates, Exam Dates, Hall Tickets, Answer Keys | Learn with Anil',
                       'Latest government exam notifications and news in one place: APPSC Group 1 & 2 (last date extended?), AMVI, EO, FRO; TS Police SI & Constable exam '
                       'date and hall ticket; AP Police; TGPSC HMWSSB; UPSC CSE, CAPF, EPFO; SSC CGL; AP DSC. Quick answers and previous papers for each.',
                       can, 'Exam notifications 2026: latest dates for every exam',
                       esc('Notifications, last dates, extensions, exam dates, hall tickets and answer keys for APPSC, TGPSC, UPSC, SSC, TS Police, AP Police and AP DSC.'),
                       ''.join(body), [('Home', SITE_URL + '/'), ('Exam notifications', can)], None, ename='All exams', at_root=True, head_all=True,
                       foot_text='Exam information compiled from the official notifications by Jupudi Anil Kumar, Learn with Anil. Not affiliated with any recruiting board.')


ROOT_NOTES = ('Study material: every book on the site',   # the start page's Study Material lists every book, for every exam
              'Exam-focused books by Jupudi Anil Kumar for APPSC Group-I, Group-II and the EO Grade-III exam: History and Culture of Andhra Pradesh, '
              'Mental Ability, Public Administration and Governance, Ethics and Laws, the Group-II Micro-Syllabus, Crisp Notes on AP Economy, '
              'Science and Technology, and Hindu Philosophy & Temple System. '
              'Every book has the exam\'s own previous questions inside.')
NOTES_EXAMS = {'appsc-group-2', 'appsc-group-1'}   # Anil, 24 Oct 2026: the APPSC Mains books are shown only on the APPSC Group 1 and Group 2 pages

# APPSC Group-I Mains · Answer Writing Tool Kit (Anil, 26 Oct 2026): one PDF book per Mains paper (Papers I-IV) with every
# previous question of 2020, 2023 and 2025 sorted by syllabus part, and practice questions on each part. Part of the ₹45
# All-in-One Pass: the app shows the download buttons only on a device with the paid pass. Paper V is not on the site: students
# message Anil on WhatsApp. Source files: src/appsc-group-1/mains/<file>.pdf and <file>-cover.jpg; published under
# /appsc-group-1/mains/kit/ with a content hash in the name (robots.txt keeps search engines out of that folder).
MAINS_EXAMS = {'appsc-group-1'}
MAINS_KIT = [
    dict(paper='I', name='General Essay', file='g1-mains-paper-1-essay', n=27, unit='essay topics', parts=7, practice=42, pages=12),
    dict(paper='II', name='History, Culture & Geography of India and AP', file='g1-mains-paper-2-history-geography', n=90, unit='questions', parts=9, practice=54, pages=20),
    dict(paper='III', name='Polity, Constitution, Governance, Law & Ethics', file='g1-mains-paper-3-polity-ethics', n=90, unit='questions', parts=9, practice=54, pages=20),
    dict(paper='IV', name='Economy & Development of India and AP', file='g1-mains-paper-4-economy', n=90, unit='questions', parts=8, practice=48, pages=20),
]
MAINS_P5 = dict(paper='V', name='Science, Technology & Environmental Issues')
MAINS_DIR = 'mains/kit'   # under the exam's folder


def mains_kit(conf):
    """The tool-kit books for an exam's data (paths on the site), copying the files into dist/site."""
    if conf['id'] not in MAINS_EXAMS: return []
    import hashlib
    src = os.path.join(SRC, conf['src'], 'mains')
    out = os.path.join(DIST, 'site', conf['dir'], MAINS_DIR)
    os.makedirs(out, exist_ok=True)
    books = []
    for b in MAINS_KIT:
        pdf = open(os.path.join(src, b['file'] + '.pdf'), 'rb').read()
        h = hashlib.sha256(pdf).hexdigest()[:8]
        names = (f'{b["file"]}-{h}.pdf', f'{b["file"]}-{h}-cover.jpg')
        open(os.path.join(out, names[0]), 'wb').write(pdf)
        shutil.copy(os.path.join(src, b['file'] + '-cover.jpg'), os.path.join(out, names[1]))
        base = conf['pb'] + MAINS_DIR + '/'
        books.append(dict(b, pdf=base + names[0], cover=base + names[1]))
    return books


def mains_section(conf, books):
    """'Group-1 Mains' on the exam's home page: the Answer Writing Tool Kit, part of the All-in-One Pass."""
    if not books: return ''
    covers = ''.join(f'<img src="{esc(b["cover"])}" alt="" width="120" height="170" loading="lazy">' for b in books)
    return (f'<div class="section-title" style="margin-top:28px"><h2>Group-1 Mains</h2><span class="muted" style="font-size:14px">Answer Writing Tool Kit · Papers I–IV</span></div>'
            f'<a class="card notes-promo" href="#mains"><div class="np-copy"><p class="eyebrow">New · Group-1 Mains</p><h2>Answer Writing Tool Kit</h2>'
            f'<p>Every Mains question of 2020, 2023 and 2025 for Papers I to IV, sorted by syllabus: how many came from each part, the exact questions, '
            f'and {sum(b["practice"] for b in books)} practice questions including recent news. Four PDF books by Jupudi Anil Kumar.</p>'
            f'<span class="etile-price" data-paidtxt="✓ Included in your All-in-One Pass · tap to download">🔒 Included in the All-in-One Pass (₹{PAY["pyq_price"]} once, for everything)</span></div>'
            f'<div class="np-covers" aria-hidden="true">{covers}</div></a>')


# ---------- paid passes: Instamojo or Cashfree checkout through the Learn with Anil payments script (Google Apps Script) ----------
PAY = dict(
    on=True,    # Anil, 23 Oct 2026: attempting any PYQ needs the paid All-in-One Pass (no free trial) (False = everything free, never again)
    api='https://script.google.com/macros/s/AKfycbxgNi2CfnbaEsVpA1Ghgy0AdYdUG7eYBkol5zqcbMgA2Q4D0Pvy0rndLxeyE7MlPy_3Rg/exec',   # the payments script (Apps Script web app, deployed 23 Oct 2026)
    pyq_price=45,
    gid=(open(os.path.join(SRC, 'google-client-id.txt')).read().strip() if os.path.exists(os.path.join(SRC, 'google-client-id.txt')) else ''),   # "Continue with Google" (public OAuth client id; Anil, 2 Nov 2026)
    exams='',   # names of every live exam, for the pay dialog ("one payment for the whole website"); set in main()
    otp=False,  # off (Anil, 4 Nov 2026, 06:10: "let the students login previously as done yesterday"); was True: Anil, 4 Nov 2026: a first registration with phone + email is confirmed with a 6-digit code emailed by the payments script
                # (actions otpsend/otpverify); until that script version is deployed the site registers students without a code
    ref=True,  # "invite friends, earn free days" (3 Nov 2026): on since 4 Nov 2026 06:17, when payments script version 12 ('ref'/'refjoin') was deployed
)
PYQ_VALID = 'valid for 12 months from the day you pay, on every exam'
_g2s = g2_syllabus_notif()   # the APPSC Group 2 syllabus page (needs PAY, so it is added here)
if _g2s: NOTIFS['appsc-group-2-syllabus-2026.html'] = _g2s
NOTIFS['appsc-group-1-syllabus-2026.html'] = g1_syllabus_notif()   # the APPSC Group 1 syllabus page (3 Nov 2026)
import notif_news   # Quick answers on every notification page + notification pages for the other live exams (Anil, 4 Nov 2026)
notif_news.apply(NOTIFS)
_eos = eo_syllabus_notif()   # the APPSC EO Grade-III syllabus page
if _eos: NOTIFS['appsc-eo-grade-3-syllabus-2026.html'] = _eos
# Anil, 26 Oct 2026: "one ₹45 = everything". The ₹45 All-in-One Pass opens every previous paper, every mock test series
# (Mission Khaki SI & Constable, Mission CGL, Bahubali, and the series still to come) and the study books. Mock packs,
# the combo, the Bahubali series and the books are no longer sold on their own (nobody had bought one).
INCL = 'Included in the ₹45 All-in-One Pass'   # price line on every mock pack, test series and book (₹45 = PAY["pyq_price"])
EVERYTHING = ('every previous paper of every exam on the site (and exams added later), every mock test series '
              '(Mission Khaki for TS SI and Constable, Mission CGL, the Bahubali Group-II Mains tests, and new series as they come) '
              'and the study books (AP Economy notes, Science &amp; Technology for Mains, the Group-1 Mains tool kit)')
TRIAL_DAYS = 0   # Anil, 23 Oct 2026: no free trial; every PYQ needs the paid All-in-One Pass (was 3)
# Anil, 28 Oct 2026: TS Police papers free to attempt (registration needed): questions, answers and score. The explanations
# (Q11 onwards of each paper), the Mission Khaki mocks from Mock 2, the PDF booklets, the study tools and every other exam stay in the ₹45 All-in-One Pass.
PRE_LIVE = None
FREE_PYQ = {'ts-police-si', 'ts-police-constable'}
FREE_PYQ_NOTE = ('Free: attempt every {seo} paper online, as a practice quiz or a timed test, with the correct answers and your score. '
                 'Register once (free); Mission Khaki Mock 1 is free too. The ₹{price} All-in-One Pass adds the explanations, the other Mission Khaki mocks, the PDF booklets and every other exam.')
SAMPLE_N = 10        # public paper / question pages show every correct answer (since 25 Oct 2026) and the explanations of the first SAMPLE_N questions of each paper; the other explanations need the All-in-One Pass
PUBLIC_PDFS = False  # Anil, 23 Oct 2026: no free PDF downloads (tools/pdfs.py makes nothing while this is False)
if os.environ.get('PAY_TEST'):   # test builds only (test/pay_test.py): payments on, against a fake script address
    PAY.update(on=True, api='https://pay.test/exec', gid=PAY.get('gid') or 'test-gid.apps.googleusercontent.com', ref=PAY.get('ref') or bool(os.environ.get('REF_TEST')))
DATA_FILES = {}   # exam id -> (folder, data file), filled while building (for the prefetch links)
BB_URL = ''   # the Bahubali Test Series page (APPSC Group 2 Mains), set by main() once its tests are sealed
# when an exam's passes run out (the day after the exam); None = 12 months from purchase
PASS_UNTIL = {'ts-police-si': ('2026-11-30', 'TS Police SI Prelims on 29 November 2026'),
              'ts-police-constable': ('2026-12-21', 'TS Police Constable Prelims on 20 December 2026'),
              'appsc-group-1': ('2027-01-25', 'APPSC Group 1 screening test on 24 January 2027')}
# mock-test packs on sale (Anil sets the price per exam)
MOCK_PACKS = {
  'ts-police-si': dict(id='mk-si', name='Mission Khaki', price=150, n=10, live=4, qn=200, free1=True,   # live = mocks released so far (Mock 2 added 1 Nov 2026, Mock 3 on 3 Nov 2026, Mock 4 on 8 Nov 2026; rest: coming soon); free1: Mock 1 free for registered students (Anil, 28 Oct 2026; FREE_MOCKS in the payments script)
                       title='Mission Khaki – TS Police SI Prelims 2026 Test Series',
                       summary='10 full-length TS SI Prelims mock tests, 200 questions each (Arithmetic & Reasoning 100, General Studies 100), '
                               'in English and Telugu, with an explanation for every answer. Each mock\'s sections can also be taken on their own as sectional tests.',
                       sections=['Arithmetic', 'Reasoning & Mental Ability', 'General Studies']),
  # packs with a 'mocks' list (several kinds of mock, each with its own parts and time limit): generic pages and app code
  'ssc-cgl': dict(id='mk-cgl', name='Mission CGL', price=149, src='mission-cgl', langs='English &amp; Hindi',   # Anil, 24 Oct 2026: ₹149, 10 Tier-I + 3 Tier-II
                  title='Mission CGL – SSC CGL Mock Test Series (Tier-I & Tier-II)',
                  summary='10 full-length Tier-I and 3 full-length Tier-II (Paper I) SSC CGL mock tests in the latest pattern, in English and Hindi, '
                          'with an explanation for every answer. Each mock\'s sections can also be taken on their own as sectional tests.',
                  about=['New questions written for this series in the SSC CGL pattern, not copied from coaching material or previous papers.',
                         'Tier-I mocks: Reasoning, General Awareness, Quantitative Aptitude and English, 25 questions each, 60 minutes. '
                         'Tier-II mocks (Paper I): Mathematical Abilities 30, Reasoning 30, English 45, General Awareness 25 and Computer Knowledge 20, 135 minutes.',
                         'Every question is in English and Hindi (English Comprehension in English only), with an explanation in both. '
                         'Your score, accuracy and topic-wise analysis come after each mock.'],
                  mocks=[dict(id=f'mk-cgl-t1-{i}', name=f'Tier-I Mock {i}', qn=100, mins=60, live=(i == 1),
                              parts=[('rea', 'Reasoning', ['rea']), ('ga', 'General Awareness', ['ih', 'pol', 'geo', 'eco', 'sci', 'cur']),
                                     ('qa', 'Quantitative Aptitude', ['qa']), ('eng', 'English', ['eng'])]) for i in range(1, 11)]
                        + [dict(id=f'mk-cgl-t2-{i}', name=f'Tier-II Mock {i}', qn=150, mins=135, live=(i == 1),
                                parts=[('qa', 'Mathematical Abilities', ['qa']), ('rea', 'Reasoning', ['rea']), ('eng', 'English', ['eng']),
                                       ('ga', 'General Awareness', ['ih', 'pol', 'geo', 'eco', 'sci', 'cur']), ('comp', 'Computer Knowledge', ['comp'])]) for i in range(1, 4)]),
  'ts-police-constable': dict(id='mk-pc', name='Mission Khaki – Constable', price=99, src='mission-khaki-pc', langs='English &amp; Telugu',   # Anil, 25 Oct 2026
                  title='Mission Khaki – Constable: TS Police Constable Prelims Test Series',
                  summary='10 full-length TS Police Constable Prelims mock tests, 200 questions each (English 25, Arithmetic 25, Reasoning 25, General Studies 125), '
                          'in English and Telugu, with an explanation for every answer. Each mock\'s sections can also be taken on their own as sectional tests.',
                  about=['New questions written for this series in the Constable Prelims pattern, at Intermediate level, not copied from coaching material or previous papers.',
                         'Each mock: English 25 (in English only, as in the real exam), Arithmetic 25, Reasoning & Mental Ability 25 and General Studies 125 '
                         '(history, Telangana, science, geography, polity, economy, society and current affairs), 3 hours.',
                         'Every other question is in English and Telugu, with an explanation in both. Your score, accuracy and topic-wise analysis come after each mock.',
                         'Mock 1 is free: register once and take it. Writing the SI exam too? Mission Khaki (SI) is included in the same ₹45 All-in-One Pass.'],
                  mocks=[dict(id=f'mk-pc-{i}', name=f'Mock {i}', qn=200, mins=180, live=(i <= 4), free=(i == 1),   # Mock 2 added 1 Nov 2026, Mock 3 on 3 Nov 2026, Mock 4 on 8 Nov 2026 (Anil)
                              parts=[('eng', 'English', ['eng']), ('ari', 'Arithmetic', ['ari']), ('rea', 'Reasoning', ['rea']),
                                     ('gs', 'General Studies', ['ih', 'tg', 'soc', 'sci', 'eco', 'geo', 'pol', 'cur'])]) for i in range(1, 11)]),
  # Anil, 8 Nov 2026: EO Grade-III test series from the site's own previous questions (tools/eo_mocks.py), full-length and sectional.
  # Ids start with "bk-" so the payments script gives the keys to any paid All-in-One Pass holder (no script change); 'dir' = the exam folder.
  'appsc-eo': dict(id='bk-eomk', name='EO Grade-III', live_note='All 3 mocks (6 papers) are available now', price=45, src='appsc-eo-mocks', dir='appsc-endowment-officer', langs='English &amp; Telugu',
                   title='APPSC EO Grade-III Test Series – Paper I & Paper II Full-Length Mocks',
                   summary='3 full-length APPSC EO Grade-III mock tests, each with Paper I (General Studies & Mental Ability, 150 questions) and Paper II '
                           '(Hindu Philosophy & Temple System, 150 questions), in English and Telugu, with an explanation for every answer. Every section can also be taken on its own as a sectional test.',
                   about=['Built from real APPSC questions: Paper I from the common APPSC General Studies & Mental Ability papers (EO 2026 and 2023, AMVI 2026 and 2023), '
                          'Paper II from the EO Hindu Philosophy & Temple System papers of 2026 and 2023, mixed subject by subject in the proportions APPSC asks.',
                          'Official APPSC answers; each explanation says which paper and question it came from. Paper I questions never repeat across the 3 mocks. '
                          'APPSC has asked only 291 Paper II questions with four options, so about half of them appear in two of the three Paper II mocks.',
                          'Each paper: 150 questions, 150 minutes, as in the real exam. Your score, accuracy and topic-wise analysis come after each test.'],
                   mocks=[m for i in range(1, 4) for m in (dict(id=f'bk-eomk-{i}a', name=f'Mock {i} · Paper I (GS & Mental Ability)', qn=150, mins=150, live=True,
                               parts=[('cur', 'Current Affairs', ['cur']), ('sci', 'General Science', ['sci']), ('ih', 'History & Culture', ['ih']),
                                      ('geo', 'Geography & Environment', ['geo']), ('pol', 'Polity & Governance', ['pol']),
                                      ('eco', 'Economy & AP Issues', ['eco', 'apr']), ('men', 'Mental Ability', ['men'])]),
                                                           dict(id=f'bk-eomk-{i}b', name=f'Mock {i} · Paper II (Hindu Philosophy)', qn=150, mins=150, live=True,
                                 parts=[('epi', 'Ramayanam, Mahabharatham & Bhagavatham', ['ram', 'mbh', 'bhg']), ('pur', 'Puranas & Itihasa', ['pur']),
                                        ('aga', 'Agamas, Festivals & Arts', ['aga', 'fes']), ('ved', 'Vedic Culture & Philosophies', ['ved', 'phi']),
                                        ('law', 'Family Law, Endowments Act & Lands', ['fam', 'inc', 'eod', 'lan'])]))]),
  # Anil, 8 Nov 2026: "start group-2 prelims test series ... suggest a name, no of exams ... add few exams"; "add info from our existing
  # questions"; chose the name "Bahubali Prelims" (same family as the Bahubali Group-II Mains tests) and Mock 1 free for registered students.
  # Each mock: History, Geography and Mental Ability = real questions from the site's other APPSC (and police) papers with official keys;
  # Indian Society and Current Affairs = new questions. Ids start with "bk-" (any paid All-in-One Pass holder); bk-g2mk-1 is in the
  # payments script's FREE_MOCKS. Sealed source: private (/home/claude/g2mk), sealed files in src/appsc-group-2-mocks/.
  'appsc-group-2': dict(id='bk-g2mk', name='Bahubali Prelims', price=45, src='appsc-group-2-mocks', dir='appsc-group-2', langs='English &amp; Telugu',
                   title='Bahubali Prelims – APPSC Group-II Screening Test Series (Mock Tests)',
                   summary='10 full-length APPSC Group-II Screening Test mocks in the real pattern, 150 questions in 150 minutes '
                           '(Indian History, Geography, Indian Society, Current Affairs and Mental Ability, 30 each), in English and Telugu, '
                           'with an explanation for every answer. Each section can also be taken on its own as a sectional test.',
                   about=['History, Geography and Mental Ability: real questions from APPSC\'s other papers (Group-I Prelims 2024, EO, AMVI and '
                          'AEE General Studies papers) and a few from the police exams, with the official answers; each explanation says which paper '
                          'and question it came from. The Group-II 2024 paper itself is not used: practise it free on the previous-papers page.',
                          'Indian Society and Current Affairs: new questions written for this series (current affairs from November 2025 to '
                          'November 2026), each checked against official and newspaper sources.',
                          'Every question is in English and Telugu, with an explanation in both. Your score, accuracy and topic-wise analysis '
                          'come after each mock. Mock 1 is free: register once and take it.'],
                   mocks=[dict(id=f'bk-g2mk-{i}', name=f'Mock {i}', qn=150, mins=150, live=(i <= 3), free=(i == 1),   # Mocks 1-3 on 8 Nov 2026
                               parts=[('ih', 'Indian History', ['ih']), ('geo', 'Geography', ['geo']), ('soc', 'Indian Society', ['soc']),
                                      ('cur', 'Current Affairs', ['cur']), ('men', 'Mental Ability', ['men'])]) for i in range(1, 11)]),
}
# SI + Constable together (the payments script records one mock pass for each exam)
COMBO = dict(price=199, exams=('ts-police-si', 'ts-police-constable'), name='Mission Khaki SI + Constable combo',
             title='Mission Khaki combo: TS Police SI + Constable mock tests',
             what='Both test series in one payment: Mission Khaki for the SI Prelims (10 mocks, 200 questions each) and Mission Khaki – Constable '
                  '(10 mocks, 200 questions each), in English and Telugu, with explanations and sectional tests. Each pack is valid till its exam.')
for _mk in MOCK_PACKS.values():   # n / live / qn / sections for packs described by a 'mocks' list
    if 'mocks' in _mk:
        _mk.update(n=len(_mk['mocks']), live=sum(m['live'] for m in _mk['mocks']), qn=_mk['mocks'][0]['qn'],
                   sections=list(dict.fromkeys(x[1] for m in _mk['mocks'] for x in m['parts'])))

def mock_questions():
    """Questions in the mock tests students can take now (released mocks of every series + the live Bahubali tests),
    for the start page's numbers strip (Anil, 1 Nov 2026: "add no of mock test questions"). Unreleased mocks are not counted."""
    n = 0
    for mk in MOCK_PACKS.values():
        n += sum(m['qn'] for m in mk['mocks'] if m['live']) if 'mocks' in mk else mk['live'] * mk['qn']
    try:
        import bahubali
        n += sum(t.get('q', 0) for t in bahubali.load_series().get('tests', {}).values())
    except Exception:
        pass
    return n


# mock-test packs with a price but no mocks yet: shown as "coming soon", no Pay button and no checkout until Mock 1 is ready
UPCOMING_PACKS = {
  'upsc-epfo': dict(name='UPSC EPFO Mock Test Series', price=199, n=10, qn=120, langs='English &amp; Hindi',   # Anil, 24 Oct 2026: ₹199
                    summary='10 full-length UPSC EPFO (APFC / EO-AO) mock tests in the real exam pattern, 120 questions each, in English and Hindi, '
                            'with an explanation for every answer.'),
}


EXAM_CLOCK = {   # exam id: (exam name, date or None, where the date comes from) — the countdown under the exam tiles
  'appsc-group-2': ('APPSC Group 2 Screening Test', None, 'Applications 10–30 November 2026 (Notification 37/2026); APPSC has not announced the exam date yet.'),
  'appsc-group-1': ('APPSC Group 1 Screening Test', '2027-01-24', 'APPSC Notification 07/2026.'),
  'ts-police-si': ('TS Police SI Preliminary Written Test', '2026-11-29', 'Tentative, TGPRB press note of 17 September 2026.'),
  'ts-police-constable': ('TS Police Constable Preliminary Written Test', '2026-12-20', 'Tentative, TGPRB press note of 17 September 2026.'),
  'upsc-capf': ('UPSC CAPF (Assistant Commandants) 2027', '2027-07-04', 'UPSC Calendar 2027.'),
  'upsc-prelims': ('UPSC Civil Services (Preliminary) Examination 2027', '2027-05-23', 'UPSC Calendar 2027.'),
  'ssc-cgl': ('SSC CGL 2026 Tier-II', None, 'CGL 2026 Tier-I is being held from 30 September to 30 October 2026; SSC has not announced the Tier-II date yet.'),
  'upsc-epfo': ('UPSC EPFO APFC Recruitment Test 2026', '2026-12-20', 'UPSC Special Advertisement 52/2026 (80 APFC posts): pen-and-paper Recruitment Test on 20 December 2026.'),
  'appsc-analyst': ('APPSC Analyst Grade-II written examination', None, 'Applications 13 October to 2 November 2026 (Notification 21/2026); APPSC has not announced the exam date yet.'),
  'appsc-env-engineer': ('APPSC Assistant Environmental Engineer written examination', None, 'Applications 6 to 27 October 2026 (Notification 08/2026); APPSC has not announced the exam date yet.'),
  'appsc-fro': ('APPSC Forest Range Officer written examination', None, 'Applications 16 October to 5 November 2026 (Notification 16/2026); APPSC has not announced the exam date yet.'),
  'ap-police-si': ('AP Police SI Preliminary Written Test', None, 'SLPRB AP notified 378 SI posts on 16 September 2026; the application and exam dates will be announced in a press note.'),
  'ap-police-constable': ('AP Police Constable Preliminary Written Test', None, 'SLPRB AP notified 1,156 posts on 16 September 2026; the application and exam dates will be announced in a press note.'),
  'tgpsc-hmwssb-manager': ('TGPSC HMWSSB Manager (Engineering)', None, 'Tentatively December 2026; TGPSC has not announced the exact date yet.'),
}


def exam_clock_html(conf):
    c = EXAM_CLOCK.get(conf['id'])
    if not c: return ''
    name, d, src = c
    if not d or d < date.today().isoformat():
        return (f'<div class="card eclock eclock-tba"><div class="ec-l"><span class="ec-k">Exam clock</span><b>{esc(name)}</b>'
                f'<span class="ec-src">{esc(src)}</span></div><div class="ec-r"><span class="ec-tba">Date not announced yet</span></div></div>')
    dd = date.fromisoformat(d)
    return (f'<div class="card cdown eclock" data-date="{d}T00:00:00+05:30"><div class="ec-l"><span class="ec-k">Exam clock</span><b>{esc(name)}</b>'
            f'<span class="ec-date">{dd.strftime("%A, %d %B %Y")}</span><span class="ec-src">{esc(src)} Confirm on the official website.</span></div>'
            f'<div class="ec-r tm-count"><b class="tm-d">–</b> <span class="ec-days">days to go</span> <span class="tm-hms">--:--:--</span></div></div>')


def live_text(mk):
    """'Mock 1 is available now; Mocks 2–10 are coming soon.' (all mocks are included in the pack price)"""
    if 'mocks' in mk:
        on = [m['name'] + (' (free)' if m.get('free') else '') for m in mk['mocks'] if m['live']]
        if len(on) == len(mk['mocks']): return mk.get('live_note') or f'All {len(on)} mocks are available now'
        names = on[0] if len(on) == 1 else ', '.join(on[:-1]) + ' and ' + on[-1]
        return f'{names} {"is" if len(on) == 1 else "are"} available now; the other {len(mk["mocks"]) - len(on)} mocks are coming soon (included in the price)'
    a, n = mk['live'], mk['n']
    if a >= n: return f'All {n} mocks are available now'
    now = 'Mock 1 is' if a == 1 else f'Mocks 1–{a} are'
    later = f'Mock {n} is' if a == n - 1 else f'Mocks {a + 1}–{n} are'
    return f'{now} available now; {later} coming soon (included in the price)'


def pass_until_text(conf):
    u = PASS_UNTIL.get(conf['id'])
    if not u: return 'valid for 12 months'
    return f'valid till the {u[1].split(" on ")[0]}'   # no dates on the site (Anil, 23 Oct 2026)


def pass_until_short(conf):
    u = PASS_UNTIL.get(conf['id'])
    if not u: return 'valid 12 months'
    return 'valid till the exam'


def pay_data(conf):
    """What the app needs to show prices and sell passes for this exam."""
    pb = conf['pb']
    mk = MOCK_PACKS.get(conf['id'])
    return dict(on=PAY['on'], api=PAY['api'], exam=conf['id'], freePyq=conf['id'] in FREE_PYQ, gid=PAY.get('gid', ''), ref=bool(PAY.get('ref')), otp=bool(PAY.get('otp')),
                pyq=dict(price=PAY['pyq_price'], valid=PYQ_VALID, exams=PAY['exams'], trial=TRIAL_DAYS),
                mock=(dict(id=mk['id'], name=mk['name'], title=mk['title'], price=PAY['pyq_price'], n=mk['n'], live=mk['live'],
                           valid=pass_until_text(conf)[0].upper() + pass_until_text(conf)[1:],
                           mocks=[dict(id=m['id'], name=m['name'], mins=m['mins'], live=m['live'], free=bool(m.get('free')), parts=m['parts']) for m in mk.get('mocks', [])]) if mk else None),
                combo=None,   # no longer sold (26 Oct 2026): the ₹45 All-in-One Pass opens both Mission Khaki packs
                pages=dict(pyq=pb + 'pyqs.html', mock=pb + 'mock-test.html', sec=pb + 'sectional-tests.html'))


def tiles_html(conf, papers, questions, extra_links, mains=()):
    """The three tiles on an exam's home page (PYQs, mock tests, sectional tests), tiles 2 and 3 open the app's own Mock tests and Sectional tests views in place (Anil, 29 Oct 2026), plus link tiles."""
    pb, mk = conf['pb'], MOCK_PACKS.get(conf['id'])
    n = len(questions)
    nsub = len({q['s'] for q in questions})
    t1 = (f'<a class="etile" href="{pb}pyqs.html"><span class="etile-k">01 · Previous papers</span><b>PYQs with answers</b>'
          f'<span class="etile-p">{n:,} questions from {len(papers)} official paper{"s" if len(papers) > 1 else ""}, with answers and explanations, as quizzes and timed tests'
          f'{", and as PDFs to download" if BOOKLETS.get(conf["id"]) else ""}. '
          f'One pass for every exam.</span>'
          + (f'<span class="etile-price">✓ Free to attempt · explanations with the ₹{PAY["pyq_price"]} All-in-One Pass</span></a>' if conf['id'] in FREE_PYQ else
             f'<span class="etile-price" data-paidtxt="✓ Unlocked · your All-in-One Pass is active">🔒 ₹{PAY["pyq_price"]} once · every exam, mock &amp; book · 12 months</span></a>'))
    if mk:
        t2 = (f'<a class="etile" href="{pb}mocks/"><span class="etile-k">02 · Mock tests</span><b>{esc(mk["name"])} test series</b>'
              + (f'<span class="etile-p">{esc(mk["summary"].split(". ")[0])}. {live_text(mk)}.</span>' if 'mocks' in mk else
                 f'<span class="etile-p">{mk["n"]} full-length mocks, {mk["qn"]} questions each, English &amp; Telugu, with explanations. {live_text(mk)}.</span>')
              + f'<span class="etile-price" data-paidtxt="✓ Included in your All-in-One Pass">🔒 {INCL}{" · Mock 1 free" if mk.get("free1") or any(m.get("free") for m in mk.get("mocks", [])) else ""}</span></a>')
    elif BB_URL and conf['id'] == 'appsc-group-2':
        t2 = (f'<a class="etile" href="{BB_URL}"><span class="etile-k">02 · Mock tests</span><b>Bahubali Test Series</b>'
              f'<span class="etile-p">24 full-length Group-II Mains mocks, 12 for Paper I and 12 for Paper II: 150 questions each, English and Telugu, with explanations.</span>'
              f'<span class="etile-price" data-paidtxt="✓ Included in your All-in-One Pass">🔒 {INCL}</span></a>')
    elif conf['id'] in UPCOMING_PACKS:
        up = UPCOMING_PACKS[conf['id']]
        t2 = (f'<a class="etile" href="{pb}mocks/"><span class="etile-k">02 · Mock tests</span><b>{esc(up["name"])}</b>'
              f'<span class="etile-p">{up["n"]} full-length mocks, {up["qn"]} questions each, {up["langs"]}, with explanations. Coming soon.</span>'
              f'<span class="etile-price">Coming soon · {INCL.lower()}</span></a>')
    else:
        t2 = (f'<a class="etile" href="{pb}mocks/"><span class="etile-k">02 · Mock tests</span><b>Mock test pack</b>'
              f'<span class="etile-p">Full-length mock tests in the exam pattern. Until the pack opens, take the real previous papers as timed mocks.</span>'
              f'<span class="etile-price">Upcoming</span></a>')
    t3 = (f'<a class="etile" href="{pb}sectionals/"><span class="etile-k">03 · Sectional tests</span><b>Subject-wise tests</b>'
          f'<span class="etile-p">PYQ sectionals in {nsub} subjects{", plus sectional mocks from " + esc(mk["name"]) if mk else ""}. '
          f'Practise one section at a time with a timer.</span><span class="etile-price" data-paidtxt="✓ Unlocked · your All-in-One Pass is active">🔒 With the All-in-One Pass</span></a>')
    ETI = {'1': ('<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6"/><path d="m9 16 2 2 4-4"/>', 'Open the PYQs →'),
           '2': ('<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M10 2h4M12 2v3"/>', 'See the mock tests →'),
           '3': ('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>', 'Practise a subject →')}
    def fx(t):   # Anil, 2 Nov 2026: the three cards get a coloured header with a drawn icon, and a real button
        m = re.search(r'<span class="etile-k">0(\d) · ([^<]+)</span>', t)
        if not m: return t
        n = m.group(1); ic, btn = ETI[n]
        hd = (f'<span class="etile-hd eh{n}"><span class="etile-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ic}</svg></span>'
              f'<span class="etile-k">0{n} · {m.group(2)}</span></span>')
        t = t.replace('<a class="etile"', '<a class="etile fx"', 1).replace(m.group(0), hd, 1)
        return t[:-4] + f'<span class="etile-btn">{btn}</span></a>' if t.endswith('</a>') else t
    t1, t2, t3 = fx(t1), fx(t2), fx(t3)
    links = ''.join(f'<a class="etile etile-sm" href="{h}"><b>{esc(x)}</b><span class="etile-go">→</span></a>' for x, h in extra_links)
    note = ''
    if conf['id'] in MAINS_EXAMS:   # Anil, 31 Oct 2026: APPSC Group-1 page has Prelims tiles and Mains tiles (Mains PYQs year-wise and subject-wise)
        import g1mains
        mq, _ = g1mains.load(SRC)
        if mq:
            hd = lambda h, s: f'<div class="section-title" style="margin:{"0" if h == "Prelims" else "26px"} 0 12px"><h2>{h}</h2><span class="muted" style="font-size:14px">{s}</span></div>'
            return (f'<section class="wrap section">' + hd('Prelims', 'Screening test: previous papers, mock tests, sectional tests')
                    + f'<div class="etiles">{t1}{t2}{t3}</div>' + hd('Mains', 'Descriptive papers: previous questions with model answers')
                    + f'<div class="etiles">{g1mains.tiles(conf, sum(q["paper"] != g1mains.ESSAY for q in mq))}</div>' + g1mains.tiles_credit() + exam_clock_html(conf)
                    + (f'<div class="etiles etiles-links">{links}</div>' if links else '') + note + '</section>')
    return (f'<section class="wrap section"><div class="etiles">{t1}{t2}{t3}</div>' + exam_clock_html(conf)
            + (f'<div class="etiles etiles-links">{links}</div>' if links else '') + note + mains_section(conf, mains) + '</section>')


def buy_box(conf, kind):
    """A price box with a buy button that opens the checkout inside the app."""
    pb = conf['pb']
    if kind == 'pyq':
        price, name = PAY['pyq_price'], 'All-in-One Pass · all exams'
        what = (f'<b>One payment of ₹{PAY["pyq_price"]} for the whole website:</b> {EVERYTHING}, not just {esc(conf["seo"])}. '
                f'Every answer and explanation, practice quizzes and timed tests, PYQ sectionals, topic-wise quizzes, Smart Quiz and your Mistakes notebook.')
        valid = PYQ_VALID
    elif kind == 'combo':
        return ''   # no longer sold (26 Oct 2026): the All-in-One Pass opens both Mission Khaki packs
    else:
        mk = MOCK_PACKS[conf['id']]
        price, name = PAY['pyq_price'], mk['title']
        what = (esc(mk['summary']) + f' <b>{INCL}</b>, together with every previous paper of every exam, the other mock test series and the study books. '
                'Nothing else to buy.')
        valid = PYQ_VALID
    return (f'<div class="buy"><div><b>{esc(name)}</b><p>{what}</p><p class="muted">₹{price} · {valid} · pay by UPI, card or net banking</p></div>'
            f'<a class="cta" href="{pb}?buy=pyq">Get it for ₹{price}</a></div>')


def plans_html(conf):
    """Every plan in one table, so there is no doubt about what is free and what is paid."""
    mk = MOCK_PACKS.get(conf['id'])
    rows = [('All-in-One Pass', f'₹{PAY["pyq_price"]}', f'Everything on the site: every previous paper of every exam ({esc(PAY["exams"])}) and every exam added later, with answers and explanations, practice quizzes, timed tests, PYQ sectionals and all study tools; '
             'every mock test series (Mission Khaki for TS SI and Constable, Mission CGL, Bahubali Prelims and the Bahubali Mains tests for Group-II, and new series as they come); and the study books', '12 months from payment')]
    up = UPCOMING_PACKS.get(conf['id'])
    if up:
        rows.append((esc(up['name']), 'Included (coming soon)', f'{up["n"]} full-length {esc(conf["seo"])} mock tests, {up["qn"]} questions each, with explanations. They open for All-in-One Pass holders as each mock is released.', 'With the All-in-One Pass'))
    if mk:
        free = [m['name'] for m in mk.get('mocks', []) if m.get('free')]
        rows.append((esc(mk['name']), 'Included', f'{mk["n"]} full-length {esc(conf["seo"])} mock tests and their sectional tests, with explanations.'
                     + (f' {" and ".join(free)} {"is" if len(free) == 1 else "are"} free for every registered student.' if free else ''),
                     'With the All-in-One Pass'))
    return ('<table class="facts plans"><tr><th style="width:17%">Plan</th><th style="width:17%">Price</th><th>What you get</th><th style="width:19%">Valid</th></tr>'
            + ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows) + '</table>'
            f'<p>Open to everyone without a plan: the question of the day, the correct answer to every question on the paper pages, and the explanations of the first {SAMPLE_N} questions of each paper. '
            'Plans are linked to the phone number and email you register with, on up to 3 devices; pay with the same details.</p>')


TOOLS_NOTE = 'Included in the ₹45 All-in-One Pass, with every previous paper and every mock test series.'


FEATURES = {   # how the practice tools work (shown on the PYQs and mock-test pages; the app pages are /<exam>/<view>/)
  'practice': ('Topic-wise quiz', 'Choose papers, subjects and topics, the number of questions, and practice or timed-test mode.'),
  'mistakes': ('Mistakes notebook', 'Every question you get wrong or skip is filed automatically, sorted by subject.'),
  'smart': ('Smart quiz', 'Re-attempt your mistakes from memory. Two correct answers in a row clears a question.'),
  'heatmap': ('Memory heatmap', 'Topic-wise accuracy in one grid, so your weak areas show up at a glance.'),
  'bookmarks': ('Bookmarks', 'Save any question with one tap and come back to it before the exam.'),
}


def features_html(pb, keys):
    return '<div class="fgrid">' + ''.join(f'<a href="{pb}{k}/"><b>{esc(FEATURES[k][0])}</b><span>{esc(FEATURES[k][1])}</span></a>' for k in keys) + '</div>'


def subjects_html(conf, questions):
    """Practise by subject: one card per subject, opening the quiz builder with that subject picked."""
    pb, cnt = conf['pb'], {}
    for q in questions: cnt[q['s']] = cnt.get(q['s'], 0) + 1
    return '<div class="sgrid">' + ''.join(f'<a href="{pb}?subj={s[0]}"><span>{esc(s[1])}</span><span class="n">{cnt[s[0]]} Q</span></a>'
                                           for s in conf['subjects'] if cnt.get(s[0])) + '</div>'


FREE_SAMPLE_N = 10   # Anil, 24 Oct 2026: 10 free questions to try on each exam's PYQs page, where the ₹45 All-in-One Pass is sold


def free_sample(conf, papers, questions, n=FREE_SAMPLE_N):
    """The questions to try for free on the PYQs page: only from the free sample (answers already public on the paper pages),
    four-option questions with an explanation, papers with the board's own options first. The papers take turns (newest
    first), and each paper gives its first question in the subject picked least so far, so the sample mixes papers and subjects."""
    free = sample_ids(questions)
    order = {p['id']: i for i, p in enumerate(sorted(papers, key=lambda p: (-p['year'], p['id'])))}
    num = lambda q: int(re.sub(r'\D', '', str(q['n'])) or 0)
    ok = sorted((q for q in questions if q['id'] in free and q.get('o') and q.get('a') and q.get('w')), key=lambda q: (order.get(q['p'], 99), num(q)))
    picked, used = [], {}
    for own in (False, True):
        groups = {}
        for q in ok:
            if bool(q.get('lwo')) == own: groups.setdefault(q['p'], []).append(q)
        while len(picked) < n and any(groups.values()):
            for lst in groups.values():
                if len(picked) >= n: break
                if not lst: continue
                q = min(lst, key=lambda x: (used.get(x['s'], 0), lst.index(x)))
                picked.append(q); lst.remove(q); used[q['s']] = used.get(q['s'], 0) + 1
    return picked


def free_sample_html(conf, papers, questions, qs):
    """'Try 10 free questions': tap an option to check it, then see the answer and explanation (works without JavaScript too)."""
    if not qs: return ''
    pb, l2, seo = conf['pb'], conf['l2'], conf['seo']
    pmap = {p['id']: p for p in papers}
    subj = {s[0]: s for s in conf['subjects']}
    items = []
    for i, q in enumerate(qs, 1):
        p = pmap[q['p']]
        parts = [f'<li class="q sq" data-a="{",".join(str(a) for a in q["a"])}"><div class="meta">{i} of {len(qs)} · {esc(paper_kw(conf, p))} · Q{esc(str(q["n"]))}'
                 f'{" · " + esc(subj[q["s"]][1]) if q["s"] in subj else ""}</div>', qtext_html(q['q'])]
        if q.get('img'):
            parts.append(f'<img src="{q["img"]}" alt="Figure for this question" loading="lazy">')
        parts.append('<ol class="sopts">' + ''.join(f'<li><button type="button" data-i="{k}"><span class="on">({k + 1})</span><span>{esc(o)}</span></button></li>'
                                                    for k, o in enumerate(q['o'])) + '</ol>')
        if q.get('lwo'):
            parts.append('<p class="muted" style="font-size:13px;margin:4px 0 0;font-weight:400">APPSC\'s key printed only the answer: the correct option is APPSC\'s, the other three are written by Learn with Anil.</p>')
        if q.get('qt'):
            te = qtext_html(q['qt']) + ('<ol>' + ''.join(f'<li>{esc(o)}</li>' for o in q['ot']) + '</ol>' if q.get('ot') else '')
            parts.append(f'<div class="te" lang="{l2["code"]}">{te}</div>')
        ans = ' / '.join(f'({a + 1}) {q["o"][a]}' for a in q['a'])
        ans_te = ' / '.join(f'({a + 1}) {q["ot"][a]}' for a in q['a']) if q.get('ot') else q.get('at', '')
        parts.append('<details><summary>Show answer</summary>'
                     f'<p class="ans">{esc(NOKEY_LABEL.get(q.get("p"), "Answer"))}: {esc(ans)}</p>'
                     + (f'<p class="ans" lang="{l2["code"]}">{l2["ans"]}: {esc(ans_te)}</p>' if ans_te else '')
                     + f'<p class="why">{esc(q["w"])}</p>'
                     + (f'<p class="why" lang="{l2["code"]}" style="margin-top:6px">{esc(q["wt"])}</p>' if q.get('wt') else '')
                     + '</details></li>')
        items.append(''.join(parts))
    return (f'<section id="free-sample" class="sample"><h2>Try {len(qs)} free questions</h2>'
            f'<p>Real {esc(seo)} questions from the official papers, with the official answer and an explanation. '
            f'Tap an option to check your answer. No registration needed.</p>'
            '<ol class="qs">' + ''.join(items) + '</ol>'
            '<p class="sscore" aria-live="polite" hidden></p>'
            f'<div class="buy"><div><b>Liked these? Practise all {len(questions):,} {esc(seo)} questions</b>'
            f'<p>One ₹{PAY["pyq_price"]} All-in-One Pass opens every previous paper of every exam on Learn with Anil for 12 months, with answers, explanations, quizzes and timed tests.</p></div>'
            f'<a class="cta" href="{pb}?buy=pyq">Get everything for ₹{PAY["pyq_price"]}</a></div></section>' + SAMPLE_JS)


SAMPLE_JS = """<script>(function(){var s=document.getElementById("free-sample");if(!s)return;var sc=s.querySelector(".sscore"),tot=s.querySelectorAll(".sq").length,got=0,done=0;
s.addEventListener("click",function(e){var b=e.target.closest(".sopts button");if(!b)return;var q=b.closest(".sq");if(!q||q.classList.contains("done"))return;
q.classList.add("done");var a=q.getAttribute("data-a").split(","),ok=a.indexOf(b.getAttribute("data-i"))>=0;
q.querySelectorAll(".sopts button").forEach(function(x){x.disabled=true;if(a.indexOf(x.getAttribute("data-i"))>=0)x.classList.add("right")});
if(!ok)b.classList.add("wrong");var d=q.querySelector("details");if(d)d.open=true;done++;if(ok)got++;
sc.textContent=(done<tot?"Your score so far: ":"Your score: ")+got+" / "+done+(done<tot?" · "+(tot-done)+" more to go":(got>=Math.ceil(tot*0.7)?" · well done!":" · the All-in-One Pass has every paper for more practice"));sc.hidden=false;
try{if(done===tot&&window.gtag)gtag("event","sample_done",{score:got})}catch(_){}});})();</script>"""


def pyq_page(conf, papers, questions):
    """Tile 1: PYQs — a sample of answers on the public pages; everything with the All-in-One Pass (all exams)."""
    pb, seo, l2 = conf['pb'], conf['seo'], conf['l2']
    rel = pb.strip('/') + '/pyqs.html'
    can = SITE_URL + '/' + rel
    base = '/' + (conf['dir'] + '/' if conf['dir'] else '')
    extra = pass_only_papers(papers)
    ps = sorted(public_only(papers, questions)[0], key=lambda p: (-p['year'], p['id']))
    free = conf['id'] in FREE_PYQ
    title = (f'{seo} Previous Papers – Free Online Tests with Answers (PYQs) | Learn with Anil' if free else
             f'{seo} PYQs with Answers – Previous Papers as Quizzes & Timed Tests | Learn with Anil')
    desc = (f'{seo} previous year question papers free: attempt all {len(papers)} official papers ({len(questions):,} questions) online as practice quizzes and timed tests, '
            f'with the correct answers in English and {l2["name"]}. Explanations and Mission Khaki mock tests with the ₹{PAY["pyq_price"]} All-in-One Pass.' if free else
            f'{seo} previous year questions (PYQs): {len(questions):,} questions from {len(papers)} official papers with answers and explanations in English and {l2["name"]}, '
            f'as practice quizzes and timed tests, with one ₹{PAY["pyq_price"]} All-in-One Pass for every exam on the site.')
    def row(p):
        recall = p['fmt'] != 'mcq'
        note = (" · answers from APPSC's key; APPSC printed no options, so the other three options are by Learn with Anil" if p.get('own')
                else " · official key gives the answer only: quick-recall cards" if recall else "")
        return (f'<li><div class="cmeta">{esc(p["held"])} · {p["count"]} questions{note}</div>'
                f'<b>{esc(paper_kw(conf, p))}{f" ({esc(paper_alt(conf, p))})" if paper_alt(conf, p) else ""}</b>'
                f'<div class="cacts"><a class="cta" href="{pb}?practice={p["id"]}">Attempt this paper · {p.get("mins") or p["count"]} min timer</a>'
                + (f'<a class="cta" style="background:#0E7A43;border-color:#0E7A43;color:#fff" href="{pb}?pdf={p["id"]}"{pdf_attrs(conf, p["id"])}>⬇ Download PDF · {BOOKLETS[conf["id"]][p["id"]]["pages"]} pages</a>' if p['id'] in BOOKLETS.get(conf['id'], {}) else '')
                + '</div></li>')
    allp = ps + sorted(extra, key=lambda p: (-p['year'], p['id']))
    others = [(x, h) for x, h in PAY.get('exam_links', []) if x != seo]
    sample = free_sample(conf, papers, questions)
    course = (f'<section class="course"><div class="chead"><div><p class="ck">All-in-One Pass · ₹{PAY["pyq_price"]} once · every exam, mock test &amp; book</p>'
              f'<h2>Every previous paper, one pass</h2>'
              f'<p>One payment of ₹{PAY["pyq_price"]} for the whole website, valid for 12 months. Every answer and explanation in English and {esc(l2["name"])}, '
              f'practice question by question, timed tests, PYQ sectionals, subject and topic quizzes, and all study tools. '
              + ('Every paper runs with its real time limit (' + ', '.join(f'{m} minutes for {esc(st)}' for st, m in dict.fromkeys((p['stage'], p['mins']) for p in allp if p.get('mins'))) + ') on a timer that you can switch off and on at the top of the screen.</p></div>'
                 if allp and allp[0].get('mins') else 'Every paper runs with a timer (1 minute per question) that you can switch off and on at the top of the screen.</p></div>') +
              f'<div class="cbuy"><a class="cta" href="{pb}?buy=pyq">Get everything for ₹{PAY["pyq_price"]}</a>'
              + (f'<a class="try" href="#free-sample">Try {len(sample)} free questions first ↓</a>' if sample else '') + '</div></div>'
              + (f'<p style="margin:10px 0;padding:10px 12px;border-radius:10px;background:#E8F6EE;border:1px solid #9FD8B8"><b>📄 New: download every paper as a PDF</b> — '
                 f'exam-booklet style, English &amp; {esc(l2["name"])}, with the official answer key and explanations. Tap <b>⬇ Download PDF</b> under any paper below (with the All-in-One Pass).</p>'
                 if BOOKLETS.get(conf['id']) else '') +
              f'<h3>{esc(seo)} papers in this course ({len(allp)} papers, {len(questions):,} questions)</h3><ol class="clist">' + ''.join(row(p) for p in allp) + '</ol>'
              + (f'<h3>Also in the same ₹{PAY["pyq_price"]} pass</h3><p>Every paper of these exams, and of every exam added to the site later:</p>'
                 '<nav class="toc">' + ''.join(f'<a href="{h}pyqs.html">{esc(x)}</a>' for x, h in others) + '</nav>' if others else '')
              + '</section>')
    banner = (f'<p class="card" style="padding:14px 16px;margin:0 0 16px;background:#E8F6EE;border:1px solid #9FD8B8;font-size:16px"><b>🎉 {esc(FREE_PYQ_NOTE.format(seo=seo, price=PAY["pyq_price"]))}</b></p>'
              if free else '')
    body = (banner + course + free_sample_html(conf, papers, questions, sample)
            + '<h2>Practise by subject and topic</h2><p>' + ('Free' if free else 'With the All-in-One Pass') + ': pick a subject to build a quiz from every paper, or build your own topic-wise quiz.</p>'
            + subjects_html(conf, questions) + features_html(pb, ('practice',))
            + f'<h2>Study tools</h2><p>{TOOLS_NOTE}</p>' + features_html(pb, ('mistakes', 'smart', 'heatmap', 'bookmarks'))
            + '<h2>Plans</h2>' + plans_html(conf)
            + f'<p><a class="cta alt" href="{pb}mock-test.html">Mock tests</a><a class="cta alt" href="{pb}sectional-tests.html">Sectional tests</a></p>'
            + (pdf_inline_js(conf) if BOOKLETS.get(conf['id']) else ''))
    lede = esc(f'Every {seo} previous paper on Learn with Anil, free to attempt online as practice quizzes and timed tests, with the official answers. '
               f'The ₹{PAY["pyq_price"]} All-in-One Pass adds the explanations, the mock tests and every other exam for 12 months.' if free else
               f'Every {seo} previous paper on Learn with Anil, with official answers and explanations, as practice quizzes and timed tests. '
               f'One ₹{PAY["pyq_price"]} All-in-One Pass opens every exam on the site for 12 months.')
    return rel, static_page(0 if conf['dir'] else 1, title, desc, can, f'{seo} PYQs with answers', lede, body,
                            [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), ('PYQs', can)], conf)


def sectional_page(conf, papers, questions):
    """Tile 3: sectional tests — PYQ sectionals by subject, and sectional mocks from the mock pack."""
    pb, seo = conf['pb'], conf['seo']
    rel = pb.strip('/') + '/sectional-tests.html'
    can = SITE_URL + '/' + rel
    mk = MOCK_PACKS.get(conf['id'])
    cnt = {}
    for q in questions:
        if q.get('o'): cnt[q['s']] = cnt.get(q['s'], 0) + 1
    subs = [s for s in conf['subjects'] if cnt.get(s[0])]
    title = f'{seo} Sectional Tests – Subject-wise PYQ Tests{" & " + mk["name"] + " Sectional Mocks" if mk else ""} with Timer | Learn with Anil'
    desc = (f'{seo} sectional tests: subject-wise timed tests made of real previous year questions'
            + (f', and sectional mocks from the {mk["name"]} test series' if mk else '') + ', with answers and explanations.')
    rows = ''.join(f'<li class="q"><div class="meta">{cnt[s[0]]} previous questions · all in one test · one minute per question</div><p>{esc(s[1])}</p>'
                   f'<a class="cta" href="{pb}?sec={s[0]}">Start {esc(s[1])} sectional</a></li>' for s in subs)
    secrows = (''.join((f'<li class="q"><div class="meta">{"Free now" if m.get("free") else "Available now"} · {m["name"]}</div><p>{esc(m["name"])} sections</p>'
                        + ''.join(f'<a class="cta alt" href="{pb}?mock={m["id"]}&amp;part={k}">{esc(v)}</a>' for k, v, _ in m['parts']) + '</li>')
                       if m['live'] else f'<li class="q"><div class="meta">Coming soon</div><p>{esc(m["name"])} sections</p></li>'
                       for m in mk['mocks']) if mk and 'mocks' in mk else
               ''.join((f'<li class="q"><div class="meta">{"Free now" if mk.get("free1") and i == 0 else "Available now"}</div><p>Mock {i + 1} sections</p>'
                        + ''.join(f'<a class="cta alt" href="{pb}?mock={mk["id"]}-{i + 1}&amp;part={k}">{v}</a>' for k, v in (('ari', 'Arithmetic'), ('rea', 'Reasoning'), ('gs', 'General Studies')))
                        + '</li>') if i < mk['live'] else f'<li class="q"><div class="meta">Coming soon</div><p>Mock {i + 1} sections</p></li>'
                       for i in range(mk['n'])) if mk else '')
    mock_part = (f'<h2>{esc(mk["name"])} sectional mocks</h2><ol class="qs">{secrows}</ol><p>Each {esc(mk["name"])} mock\'s sections — '
                 + ', '.join(esc(x) for x in mk['sections']) + ' — open as separate timed tests as the mocks are released '
                 f'({live_text(mk)}). {INCL}.</p>'
                 if mk else (f'<h2>Sectional mocks</h2><p>Sectional mocks will come with the {esc(UPCOMING_PACKS[conf["id"]]["name"])} '
                             f'(coming soon, {INCL.lower()}).</p>' if conf['id'] in UPCOMING_PACKS else
                             f'<h2>Sectional mocks</h2><p>Sectional mocks open with this exam\'s mock test pack, coming soon and {INCL.lower()}.</p>'))
    body = (f'<h2>PYQ sectionals</h2><p>Each test has every real previous question from one subject, in one go, with a timer. 🔒 Opens with the ₹{PAY["pyq_price"]} All-in-One Pass, which also opens every mock test series and the study books.</p>'
            '<ol class="qs">' + rows + '</ol>' + buy_box(conf, 'pyq') + mock_part + '<h2>Plans</h2>' + plans_html(conf))
    lede = esc(f'Practise {seo} one section at a time: timed tests from real previous questions in every subject'
               + (f', and sectional mocks from {mk["name"]}.' if mk else '.'))
    return rel, static_page(0 if conf['dir'] else 1, title, desc, can, f'{seo} sectional tests', lede, body,
                            [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), ('Sectional tests', can)], conf)


def inapp_mocks(conf, papers):
    """HTML of the app's Mock tests view (/<exam>/mocks/): the same content as the static mock-test page, without the page frame."""
    pack, rows, info = mock_parts(conf, papers, app=True)
    l2, mk = conf['l2'], MOCK_PACKS.get(conf['id'])
    return (pack + (f'<p class="note">{esc(info)}</p>' if info else '')
            + '<h2>Real previous papers as mock tests</h2><ol class="qs">' + rows + '</ol>'
            + '<h2>How the mock test works</h2><ul>'
            f'<li>Questions appear in English and {esc(l2["name"])} as printed. Switch language with the buttons at the top.</li>'
            '<li><b>Start</b> is the exam-style test: answer, mark for review, and see your score with every answer and explanation when you submit. '
            '<b>Practice mode</b> checks each answer as you go, with its explanation, like the previous papers.</li>'
            '<li>The green <b>TIMER</b> switch at the top turns the timer off and on again. The timer also pauses while you are away from the test.</li>'
            '<li>When you finish you get your score, accuracy and a topic-wise analysis, with the correct answer and an explanation for every question. Wrong answers go to your Mistakes notebook.</li>'
            f'<li>Everything here opens with the All-in-One Pass (₹{PAY["pyq_price"]} for every exam on the site, 12 months){"; the same pass opens " + esc(mk["name"]) if mk else ""}.</li></ul>')


def inapp_sectionals(conf, papers, questions):
    """HTML of the app's Sectional tests view (/<exam>/sectionals/): PYQ sectionals by subject and the mock pack's sectional mocks."""
    _rel, html_ = sectional_page(conf, papers, questions)
    m = re.search(r'<h2>PYQ sectionals</h2>.*?(?=<h2>Plans</h2>)', html_, flags=re.S)
    return m.group(0) if m else ''


def dur_text(p):
    """'60 minutes' for a paper with a real time limit, else 'about 2 hours' (one minute per question)."""
    return f'{p["mins"]} minutes' if p.get('mins') else f'about {round(p["count"] / 60 * 4) / 4:g} hours'


def mock_btns(start_href, start_label, practice_href, pdf):
    """Start / Practice / PDF as buttons in the mock tables (Anil, 2 Nov 2026: text links were hard to tap)."""
    b = f'<a class="mbtn go" href="{start_href}">▶ {start_label}</a>'
    if practice_href: b += f'<a class="mbtn" href="{practice_href}">Practice mode</a>'
    if pdf: b += pdf.replace(' · <a ', '<a class="mbtn mpdf" ', 1)
    return f'<span class="mbtns">{b}</span>'


def chips(html):
    return '<span class="mchips">' + html.replace(' · ', '').replace('<a ', '<a class="mchip" ') + '</span>'


def soon_rows(names, total_cols=4):
    """Consecutive coming-soon mocks folded into one row: 'Mocks 3–10 · coming soon'."""
    if not names: return ''
    label = names[0] if len(names) == 1 else f'{names[0].replace("Mock ", "Mocks ")}–{names[-1].replace("Mock ", "")}'
    return f'<tr class="msoon"><td colspan="{total_cols}"><b>{esc(label)}</b> · coming soon, one by one</td></tr>'


def part_links(pb, m):
    """'Reasoning · General Awareness · …' links that open one part of a released mock as a sectional test."""
    return ' · '.join(f'<a href="{pb}?mock={m["id"]}&amp;part={k}">{esc(v)}</a>' for k, v, _ in m['parts'])


MOCK_INFO = {}   # exam dates removed at Anil's request (23 Oct 2026): no exam dates on the site
BOOKLETS = {}   # exam id -> paper id -> booklet PDF (key, file, name, pages); filled by main() from src/books/booklets.json


def mock_pdf_link(conf, mock_id):
    """' · 🔒 PDF' link for a released mock that has a booklet PDF (All-in-One Pass), else ''."""
    hit = [k for k, v in BOOKLETS.get(conf['id'], {}).items() if v.get('mock') == mock_id]
    return f' · <a href="{conf["pb"]}?pdf={hit[0]}"{pdf_attrs(conf, hit[0])}><span class="lk" aria-hidden="true">🔒 </span>Download PDF</a>' if hit else ''


def pdf_attrs(conf, pid):
    """data-* for a booklet PDF link, so PDF_INLINE_JS can save it right on this page (the link opens the app only as a fallback)."""
    b = BOOKLETS.get(conf['id'], {}).get(pid)
    return f' data-pdf="{esc(b["key"])}" data-name="{esc(b["name"])}" data-paper="{esc(pid)}"' if b else ''


def pdf_inline_js(conf):
    """Anil, 27 Oct 2026: tapping Download PDF on a static page must not take the student to another page. A registered
    student on this browser gets the PDF right here: the payments script gives the key only to a valid All-in-One Pass, the
    encrypted booklet (/books/<file>) is decrypted in the browser and saved. Not registered, no pass, or an old browser:
    the link opens the app, which handles registration and the checkout."""
    if not PAY.get('api'): return ''
    return ("""<script>(function(){var API=""" + json.dumps(PAY['api']) + ',EXAM=' + json.dumps(conf['id']) + """;
function J(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
function dev(){try{var d=localStorage.getItem('lwa-device');if(!d){d=Math.random().toString(36).slice(2)+Date.now().toString(36);localStorage.setItem('lwa-device',d)}return d}catch(e){return ''}}
function say(a,t,bad){var n=a.parentNode.querySelector('.pdfmsg');if(!n){n=document.createElement('p');n.className='pdfmsg';n.style.cssText='margin:6px 0 0;font-size:14px;width:100%';a.parentNode.appendChild(n)}n.style.color=bad?'#B42318':'#0E7A43';n.textContent=t}
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[data-pdf]');if(!a||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey)return;
var s=J('lwa-appsc-g2-student-v1');if(!s||!s.name||!s.phone||!window.crypto||!crypto.subtle||!window.TextEncoder)return;
e.preventDefault();if(a.getAttribute('aria-busy')==='true')return;var html=a.innerHTML,kid=a.getAttribute('data-pdf');a.setAttribute('aria-busy','true');a.textContent='Preparing your PDF…';
fetch(API,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify({action:'mock',exam:EXAM,id:kid,phone:s.phone,email:s.email||'',device:dev()})}).then(function(r){return r.json()}).then(function(r){
if(!r||!r.ok){if(r&&r.need){location.href=a.href;return}throw new Error((r&&r.error)||'')}
return fetch('/books/'+r.file).then(function(x){if(!x.ok)throw new Error('');return x.arrayBuffer()}).then(function(buf){var b=new Uint8Array(buf);
return crypto.subtle.importKey('raw',Uint8Array.from(atob(r.key),function(c){return c.charCodeAt(0)}),'AES-GCM',false,['decrypt']).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:b.slice(0,12),additionalData:new TextEncoder().encode(kid)},k,b.slice(12))})}).then(function(pdf){
var u=URL.createObjectURL(new Blob([pdf],{type:'application/pdf'})),d=document.createElement('a');d.href=u;d.download=a.getAttribute('data-name')||'LearnWithAnil.pdf';document.body.appendChild(d);d.click();d.remove();setTimeout(function(){URL.revokeObjectURL(u)},60000);
try{if(window.gtag)gtag('event','paper_pdf_download',{paper:a.getAttribute('data-paper'),from:'pyqs_page'})}catch(_){}
say(a,'✓ Your PDF is downloading (saved in Downloads). For your personal study only.')})}).catch(function(err){say(a,(err&&err.message)||'Could not get the PDF. Please check your connection and try again.',true)}).then(function(){a.innerHTML=html;a.removeAttribute('aria-busy')})});})();</script>""")


def mock_parts(conf, papers, app=False):
    """The mock-pack box and the previous papers as timed tests: shared by the static mock-test page and, with app=True,
    the app's own Mock tests view (Anil, 29 Oct 2026: the exam tile must open the test series in place, not another page)."""
    pb, seo = conf['pb'], conf['seo']
    mcq = [p for p in sorted(papers, key=lambda p: (-p['year'], p['id'])) if p['fmt'] == 'mcq' and not p.get('own')]
    mk = MOCK_PACKS.get(conf['id'])
    rows = ''.join(
        f'<li class="q"><div class="meta">{esc(p["held"])} · {p["count"]} questions · {dur_text(p)}</div>'
        f'<p>{esc(paper_kw(conf, p))}{f" ({esc(paper_alt(conf, p))})" if paper_alt(conf, p) else ""}</p>'
        f'<p style="font-weight:400">{esc(p["blurb"])}</p>'
        f'<a class="cta" href="{pb}?test={p["id"]}">Start the mock test</a>' + (f'<a class="cta alt" href="{pb}?practice={p["id"]}">Practise with answers</a></li>' if app else f'<a class="cta alt" href="/{conf["dir"] + "/" if conf["dir"] else ""}papers/{p["slug"]}.html">See the questions</a></li>')
        for p in mcq)
    info = MOCK_INFO.get(conf['id'], '')
    if mk and 'mocks' in mk:
        sched = ''.join(f'<tr><td><b>{esc(m["name"])}</b></td><td>{"<b>Free</b> · register and start" if m.get("free") else "Available now"}</td><td>{m["qn"]} questions · {m["mins"]} min'
                        f'{mock_btns(f"{pb}?mock={m[chr(105) + chr(100)]}", "Start free" if m.get("free") else "Start", f"{pb}?mock={m[chr(105) + chr(100)]}&amp;mode=practice" if app else "", mock_pdf_link(conf, m["id"]))}</td>'
                        f'<td>{chips(part_links(pb, m))}</td></tr>' for m in mk['mocks'] if m['live'])
        sched += soon_rows([m['name'] for m in mk['mocks'] if not m['live']])
        pack = (f'<h2>{esc(mk["title"])}</h2>' + buy_box(conf, 'mock')
                + f'<table class="facts mtab"><tr><th>Mock</th><th>Status</th><th>Full mock</th><th>Sectional tests</th></tr>{sched}</table>'
                + '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in mk['about']) + '</ul>'
)
    elif mk:
        mid = lambda i: f'{mk["id"]}-{i + 1}'
        sched = ''.join(f'<tr><td><b>Mock {i + 1}</b></td><td>{"<b>Free</b> · register and start" if mk.get("free1") and i == 0 else "Available now"}</td><td>{mk["qn"]} questions'
                        f'{mock_btns(f"{pb}?mock={mid(i)}", "Start free" if mk.get("free1") and i == 0 else "Start", f"{pb}?mock={mid(i)}&amp;mode=practice" if app else "", mock_pdf_link(conf, mid(i)))}</td>'
                        f'<td>{chips(f"<a href={chr(34)}{pb}?mock={mid(i)}&amp;part=ari{chr(34)}>Arithmetic</a> · <a href={chr(34)}{pb}?mock={mid(i)}&amp;part=rea{chr(34)}>Reasoning</a> · <a href={chr(34)}{pb}?mock={mid(i)}&amp;part=gs{chr(34)}>General Studies</a>")}</td></tr>'
                        for i in range(mk['live']))
        sched += soon_rows([f'Mock {i + 1}' for i in range(mk['live'], mk['n'])])
        pack = (f'<h2>{esc(mk["title"])}</h2>' + buy_box(conf, 'mock')
                + f'<table class="facts mtab"><tr><th>Mock</th><th>Status</th><th>Full mock</th><th>Sectional tests</th></tr>{sched}</table>'
                '<ul><li>Fresh questions written for this series in the TS SI Prelims pattern, not copied from coaching material: Arithmetic &amp; Reasoning (100) and General Studies (100), in English and Telugu.</li>'
                '<li>Every question has an explanation in English and Telugu. Your score, accuracy and topic-wise analysis come after each mock.</li>'
                '<li>Each mock\'s sections can also be taken on their own as sectional tests.</li></ul>'
)
    elif BB_URL and conf['id'] == 'appsc-group-2':
        pack = (f'<h2>Bahubali Test Series</h2><p>24 full-length APPSC Group-II Mains mock tests, 12 for Paper I and 12 for Paper II: 150 questions each, '
                f'English and Telugu, with explanations and PDFs. {INCL}, with every previous paper and the study books.</p><p><a class="cta" href="{BB_URL}">See the Bahubali tests</a></p>')
    elif conf['id'] in UPCOMING_PACKS:
        up = UPCOMING_PACKS[conf['id']]
        pack = (f'<h2>{esc(up["name"])} · coming soon</h2>'
                f'<div class="buy"><div><b>{esc(up["name"])}</b><p>{esc(up["summary"])} <b>{INCL}</b>: nothing extra to pay. '
                f'Each mock opens for All-in-One Pass holders as soon as it is ready.</p><p class="muted">Coming soon · {INCL.lower()}</p></div>'
                f'<span class="cta alt" aria-disabled="true">Coming soon</span></div>'
                '<p>Until then, take the real previous papers below as timed mocks (with the All-in-One Pass).</p>')
    else:
        pack = f'<h2>Mock test pack</h2><p>Full-length mock tests for this exam are being prepared; they will be {INCL.lower()}. Until then, take the real previous papers below as timed mocks.</p>'
    return pack, rows, info


def mock_page(conf, papers, questions):
    """Tile 2: mock tests — the exam's mock-test pack (if on sale) and the real previous papers as full timed tests."""
    pb, seo = conf['pb'], conf['seo']
    rel = pb.strip('/') + '/mock-test.html'
    can = SITE_URL + '/' + rel
    mcq = [p for p in sorted(papers, key=lambda p: (-p['year'], p['id'])) if p['fmt'] == 'mcq' and not p.get('own')]
    l2 = conf['l2']
    mk = MOCK_PACKS.get(conf['id'])
    tseo = seo.replace('TS Police', 'TS (Telangana) Police') if conf['id'].startswith('ts-police') else seo
    title = (f'{tseo} Mock Test 2026 – {mk["name"]} Test Series & Previous Papers with Timer | Learn with Anil' if mk else
             f'{seo} Mock Test – Full Previous Papers with Timer, English & {l2["name"]} | Learn with Anil')
    desc = ((f'{mk["title"]}: {mk["summary"]} {INCL}. ' if mk else f'{seo} mock tests online: ')
            + f'take the real {", ".join(paper_kw(conf, p).replace(seo + " ", "") for p in mcq)} question paper{"s" if len(mcq) > 1 else ""} as timed tests, '
            f'in English and {l2["name"]}, with your score, official answers and an explanation for every question.')
    pack, rows, info = mock_parts(conf, papers)
    body = (pack + (f'<p class="note">{esc(info)}</p>' if info else '')
            + '<h2>Real previous papers as mock tests</h2><ol class="qs">' + rows + '</ol>'
            + '<h2>How the mock test works</h2><ul>'
            f'<li>Questions appear in English and {esc(l2["name"])} as printed. Switch language with the buttons at the top.</li>'
            '<li>The timer gives you one minute per question. You can move between questions and change answers until you submit.</li>'
            '<li>When you finish you get your score, accuracy and a topic-wise analysis, with the correct answer and an explanation for every question. Wrong answers go to your Mistakes notebook.</li>'
            f'<li>Previous papers as tests need the All-in-One Pass (₹{PAY["pyq_price"]} for every exam on the site, 12 months){"; the same pass opens " + esc(mk["name"]) if mk else ""}. Register once with your phone number and use the same number when you pay.</li></ul>'
            + f'<h2>Study tools after every test</h2><p>{TOOLS_NOTE}</p>' + features_html(pb, ('mistakes', 'smart', 'heatmap', 'bookmarks'))
            + '<h2>Plans</h2>' + plans_html(conf)
            + f'<p><a class="cta alt" href="{pb}sectional-tests.html">Sectional tests</a><a class="cta alt" href="{pb}pyqs.html">All {esc(seo)} PYQs</a></p>'
            + (pdf_inline_js(conf) if BOOKLETS.get(conf['id']) else ''))
    lede = esc((f'{mk["title"]}, plus every real {seo} previous paper as a timed mock test.') if mk else
               f'Take a real {seo} previous paper as a full mock test with a timer, then see your score and an explanation for every answer.')
    return rel, static_page(0 if conf['dir'] else 1, title, desc, can, f'{seo} mock tests', lede, body,
                            [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), ('Mock test', can)], conf)


VIEW_CRUMB = {'papers': 'Previous papers', 'practice': 'Topic-wise quiz', 'bank': 'Question bank', 'notes': 'Study material', 'about': 'About', 'mains': 'Group-1 Mains Tool Kit'}


def crumb_ld(items):
    """BreadcrumbList structured data, so Google shows the page's place on the site (Home › Exam › Page) in results."""
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def public_only(papers, questions):
    """Papers and questions that get public pages: all of them. Answer-only papers (no four options) were kept off the public pages
    on 23 Oct 2026; on 24 Oct Anil chose to give them the same free-sample pages as the other papers (questions public, first
    SAMPLE_N answers free, the rest with the All-in-One Pass), because Google had already indexed their pages. Since 24 Oct those papers
    also have four options (APPSC's answer + three by Learn with Anil), labelled on every page. Since 25 Oct every answer is public on
    these pages and only the explanations keep the SAMPLE_N split."""
    return list(papers), list(questions)


def pass_only_papers(papers):
    return []   # no paper is hidden from the public pages any more (see public_only)


def build_static(conf, papers, subjects, questions, subj):
    papers, questions = public_only(papers, questions)
    pages = {}
    by_p = {}
    for q in questions: by_p.setdefault(q['p'], []).append(q)
    pmap = {p['id']: p for p in papers}
    base = f'{SITE_URL}/{conf["dir"] + "/" if conf["dir"] else ""}'
    home_crumbs = [('Home', SITE_URL + '/')] + ([(conf['name'], base)] if conf['dir'] else [])
    name, seo, slugp = conf['name'], conf['seo'], conf['slugp']
    free = sample_ids(questions)
    unl = lambda q: None if q['id'] in free else f'{conf["pb"]}?q={q["id"]}'
    for p in papers:
        qs = by_p[p['id']]
        rel = f'papers/{p["slug"]}.html'
        can = base + rel
        pkey = p.get('key', conf['keyname'])
        fmt = (f'Each question with its official answer from {conf["keyname"]}; the key printed only the answer, so the other three options are written by Learn with Anil' if p.get('own')
               else f'All four options, with {pkey}' if p.get('nokey')
               else f'All four options with the answer from {pkey}' if p['fmt'] == 'mcq'
               else f'Each question with its official answer from {conf["keyname"]} (the key lists the correct answer only)')
        kw, alt = paper_kw(conf, p), paper_alt(conf, p)
        if p.get('nokey'):
            title = f'{kw} Question Paper with Answers, English & Hindi | Learn with Anil'
        elif conf['board'] in ('UPSC', 'SSC'):
            title = f'{kw} Question Paper with Answer Key{f" ({alt})" if alt and conf["board"] == "SSC" else ""}, English & Hindi | Learn with Anil'
        else:
            title = f'{kw} Question Paper with Answers{f" ({alt})" if alt else ""} – {"Preliminary Key" if "preliminary key" in pkey else "Final Key"}, {"English" if p.get("en_only") else "Telugu & English"} | Learn with Anil'
        kdesc = ("answers from APPSC's final key" if conf['board'] == 'APPSC' else 'compiled answers' if p.get('key', '').startswith('answers compiled')
                 else pkey if p.get('nokey')
                 else f'answers from {pkey}')
        desc = (f'{kw} question paper{f" ({alt})" if alt else ""}, held {p["held"]}: all {len(qs)} questions in {"English" if p.get("en_only") else "English and " + conf["l2"]["name"]} '
                f'with {kdesc} and explanations. Practise it online as a quiz or a timed mock test with the ₹45 All-in-One Pass.'
                + (f' {conf["aka_short"]}.' if conf.get('aka_short') else ''))
        subs = {}
        for q in qs: subs.setdefault(q['s'], 0); subs[q['s']] += 1
        toc = '<nav class="toc">' + ''.join(
            f'<a href="../subjects/{slugp}-{subj[s][2]}-pyqs.html">{esc(subj[s][1])} ({c})</a>' for s, c in subs.items()) + '</nav>'
        body = (f'<p lang="{conf["l2"]["code"]}" style="margin:0 0 6px">{esc(paper_kw_l2(conf, p))}</p>'
                f'<a class="cta" href="{conf["pb"]}?practice={p["id"]}">Attempt this paper · {p.get("mins") or len(qs)} min timer</a>' +
                f'<a class="cta alt" href="{conf["pb"]}practice/">Make a topic-wise quiz</a>'
                f'<p class="note">The correct answer to every question is free on this page, and so are the explanations of the first {min(SAMPLE_N, len(qs))}. For all {len(qs)} explanations, practise the paper in the app '
                f'with the ₹{PAY["pyq_price"]} All-in-One Pass, one payment for every exam on the site.</p>'
                f'<h2>Subjects in this paper</h2>{toc}<h2>All {len(qs)} questions</h2><ol class="qs">'
                + ''.join(q_html(q, p['short'], f'Q{q["n"]}', subj, conf['l2'], f'{conf["pb"]}q/{q["id"]}.html', unl(q)) for q in qs) + '</ol>')
        held = f'{p["notif"]}, held on {p["held"]}' if conf['board'] == 'APPSC' else f'Held on {p["held"]} ({p["notif"].replace(" · ", ", ")})'
        lede = esc(f'{p["title"]}{f" ({alt_shown(alt, p['title'])})" if alt_shown(alt, p['title']) else ""}. {p["blurb"]} {held}. {fmt}, plus a short explanation for every question (the first {SAMPLE_N} here, all of them in the app). '
                   + ('' if p.get('en_only') else f'Each question is shown in English and {conf["l2"]["name"]}, as printed in the ' + ('question paper.' if 'CBT' in p['notif'] or 'CBRT' in p['notif'] else 'booklet.')))
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
                f'topic-wise, with answers, explanations and {conf["l2"]["name"]} text. Practise them as a quiz or a timed test with the ₹45 All-in-One Pass.')
        l2l = subject_l2_line(conf, s)
        body = ([f'<p lang="{conf["l2"]["code"]}" style="margin:0 0 6px">{esc(l2l)}</p>'] if l2l else []) + [f'<a class="cta" href="{conf["pb"]}practice/">Practise {esc(s["name"])} online</a>']
        tops = {}
        for q in qs: tops.setdefault(q['t'], []).append(q)
        body.append('<nav class="toc">' + ''.join(f'<a href="#t{i}">{esc(t)} ({len(tops[t])})</a>' for i, t in enumerate(s['topics']) if t in tops) + '</nav>')
        for i, t in enumerate(s['topics']):
            if t not in tops: continue
            body.append(f'<h2 id="t{i}">{esc(t)}</h2><ol class="qs">' + ''.join(
                q_html(q, pmap[q['p']]['short'], f'{pmap[q["p"]]["short"]} · Q{q["n"]}', subj, conf['l2'], f'{conf["pb"]}q/{q["id"]}.html', unl(q)) for q in tops[t]) + '</ol>')
        lede = esc(f'Every {s["name"]} question asked in the {name} papers on this site, grouped by topic. '
                   f'Answers come from {conf["keyshort"]}; each has a short explanation (free here for a sample, all of them in the practice app).')
        pages[rel] = static_page(1, title, desc, can, f'{seo} {s["name"]} previous year questions with answers', lede, ''.join(body),
                                 home_crumbs + [(s['name'], can)], conf)
    return pages


# Anil, 2 Nov 2026 (SEO check): Google had dropped most of the site, even exam and paper pages that were getting clicks, as "Crawled -
# currently not indexed", after ~10,000 near-identical one-question pages went up in two weeks. The one-question pages now tell Google only
# (meta googlebot noindex; they stay open to Bing, which ChatGPT uses, and to visitors) not to index them, and leave the sitemap, so Google
# judges the site on its exam, paper, subject, notification and Mains model-answer pages.
GOOGLE_SKIP_QPAGES = True


def question_pages(conf, papers, questions, subj):
    """One crawlable page per question (q/<id>.html in the exam's folder): question, options, answer, explanation, both languages."""
    papers, questions = public_only(papers, questions)
    pages = {}
    pmap = {p['id']: p for p in papers}
    by_p = {}
    for q in questions: by_p.setdefault(q['p'], []).append(q)
    pb, l2 = conf['pb'], conf['l2']
    sdir = '/' + (conf['dir'] + '/' if conf['dir'] else '')
    depth = 1 if conf['dir'] else 2
    free = sample_ids(questions)
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
                    + (f'Answer worked out by Learn with Anil (no official key), with explanation, in English and {l2["name"]}.' if p.get('nokey') else
                       f'Answer from {p.get("key") or conf["keyname"]}, with explanation, in English and {l2["name"]}.'))
            prev_q, next_q = (qs[i - 1] if i else None), (qs[i + 1] if i + 1 < len(qs) else None)
            nav = ('<nav class="toc">'
                   + (f'<a href="{prev_q["id"]}.html">← Q{prev_q["n"]}</a>' if prev_q else '')
                   + (f'<a href="{next_q["id"]}.html">Q{next_q["n"]} →</a>' if next_q else '')
                   + f'<a href="{paper_url}">All questions of this paper</a></nav>')
            locked = q['id'] not in free
            body = (f'<ol class="qs">{q_html(q, p["short"], f"{p["short"]} · Q{q["n"]}", subj, l2, None, f"{pb}?q={q["id"]}" if locked else None)}</ol>'
                    f'<p><a class="cta" href="{pb}?q={q["id"]}">Answer it in the practice app</a>'
                    f'<a class="cta alt" href="{pb}practice/">Make a topic-wise quiz</a></p>' + nav)
            lede = esc(f'Question {q["n"]} of the {p["title"]} ({p["held"]}). '
                       + ('Try it first, then open the answer. The explanation is in the practice app with the All-in-One Pass.' if locked else 'Try it first, then open the answer and explanation.'))
            crumbs = [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), (p['title'], SITE_URL + paper_url), (f'Q{q["n"]}', can)]
            page = static_page(depth, title, desc, can, f'{kw} · Question {q["n"]}', lede, body, crumbs, conf)
            if GOOGLE_SKIP_QPAGES: page = page.replace('<link rel="canonical"', '<meta name="googlebot" content="noindex,follow">\n<link rel="canonical"', 1)
            pages[rel] = page
    return pages


def not_found_page(old_pdfs=None):
    """GitHub Pages serves this for any unknown address. Practice-app links such as /upsc-capf/q/c2026a-3/ are sent to the app,
    and the old free-PDF addresses (/…/pdf/<paper>.pdf, removed 23 Oct 2026) to that paper's page."""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found | Learn with Anil</title><meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<script>
(function(){
  var pdfs = """ + json.dumps(old_pdfs or {}, separators=(',', ':')) + """;
  if (pdfs[location.pathname]) { location.replace(pdfs[location.pathname]); return; }
  var p = location.pathname, bases = ["/appsc-group-2/", "/appsc-group-1/", "/upsc-capf/", "/upsc-epfo/", "/upsc-prelims/", "/ssc-cgl/", "/ts-police-si/", "/ts-police-constable/", "/tgpsc-hmwssb-manager/", "/appsc-amvi/", "/tgpsc-amvi/", "/appsc-endowment-officer/", "/appsc-analyst-grade-2/", "/appsc-assistant-environmental-engineer/", "/appsc-assistant-statistical-officer/", "/appsc-forest-range-officer/", "/ap-police-si/", "/ap-police-constable/"], base = "/";
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
<li><a href="/appsc-group-1/">APPSC Group-I PYQs</a></li><li><a href="/upsc-prelims/">UPSC Prelims PYQs</a></li><li><a href="/upsc-cse/">UPSC Mains PYQs</a></li><li><a href="/upsc-capf/">UPSC CAPF (AC) PYQs</a></li><li><a href="/upsc-epfo/">UPSC EPFO APFC PYQs</a></li><li><a href="/ssc-cgl/">SSC CGL PYQs</a></li>
<li><a href="/ts-police-si/">TS Police SI PYQs</a></li><li><a href="/ts-police-constable/">TS Police Constable PYQs</a></li><li><a href="/appsc-pyqs.html">All APPSC previous question papers</a></li>
<li><a href="/ts-police-pyqs.html">All TS Police previous question papers</a></li><li><a href="/ap-police-si/">AP Police SI PYQs</a></li><li><a href="/ap-police-constable/">AP Police Constable PYQs</a></li></ul>
</main></body></html>
"""


if __name__ == '__main__':
    main()
