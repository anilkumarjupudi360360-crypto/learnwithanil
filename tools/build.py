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
]


def epfo_text():
    """Wording for the EPFO page that depends on which EO/AO papers are on the site."""
    have = have_src('upsc-epfo', EPFO_PAPERS)
    eo23, eo21 = 'eoao23' in have, 'eoao21' in have
    eoy = ' & '.join(y for y, h in (('2023', eo23), ('2021', eo21)) if h)          # '2023 & 2021'
    return dict(eo=eo23 or eo21, eo21=eo21, eoy=eoy, n=len(have),
                papers=('APFC 2023, EO/AO ' + eoy) if (eo23 and eo21) else ('APFC 2023 & EO/AO ' + eoy) if eoy else 'APFC 2023',
                years='2021–2023' if eo21 else '2023',
                eodates=' and '.join(d for d, h in (('2 July 2023', eo23), ('5 September 2021', eo21)) if h))

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
]
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
]
HM_SUBJ_TE = {'cur': 'కరెంట్ అఫైర్స్', 'sci': 'జనరల్ సైన్స్', 'env': 'పర్యావరణం, విపత్తు నిర్వహణ', 'geo': 'భూగోళశాస్త్రం (జాగ్రఫీ)',
              'ih': 'భారతదేశ చరిత్ర', 'tg': 'తెలంగాణ చరిత్ర, ఉద్యమం', 'pol': 'భారత రాజ్యాంగం (పాలిటీ)', 'eco': 'భారత, తెలంగాణ ఆర్థిక వ్యవస్థ',
              'rea': 'రీజనింగ్, డేటా ఇంటర్‌ప్రిటేషన్', 'eng': 'ఇంగ్లీష్'}

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
        if p.get('fmt') != 'mcq': continue   # Anil, 23 Oct 2026: answer-only keys (no four options) are not shown on the site
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
        for k in ('key', 'alt', 'te_paper', 'hi_paper', 'en_only', 'kwname'):
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


def have_src(src, papers):
    """Ids of the papers whose source file exists (load_exam skips the others)."""
    return [p['id'] for p in papers if os.path.exists(os.path.join(SRC, src, p['file']))]


def ts_text():
    """Wording for the TS Police pages that depends on which 2023 Final Written Examination papers are on the site."""
    si = [i for i in have_src('ts-police-si', TS_SI_PAPERS) if i != 's2022']
    pc = [i for i in have_src('ts-police-constable', TS_PC_PAPERS) if i != 'p2022']
    si_fwe = 'Papers III and IV' if len(si) > 1 else {'s2023c': 'Paper III, Arithmetic & Reasoning', 's2023d': 'Paper IV, General Studies'}.get(si[0], '') if si else ''
    return dict(si=si, pc=pc, si_fwe=si_fwe)


def exam_confs():
    T = ts_text()
    E = epfo_text()
    si_m, pc_m = bool(T['si']), bool(T['pc'])
    return [
      dict(id='appsc-group-2', dir='', src='', key='appsc-g2', name='APPSC Group-II', short='Group-II', seo='APPSC Group 2',
           slugp='appsc-group-2', papers=PAPERS, subjects=SUBJECTS, faq=FAQ, board='APPSC', l2=L2_TE, pb='/appsc-group-2/',
           title='APPSC Group 2 Previous Year Question Papers (PYQs) with Answers – Prelims 2024 & Mains 2025, English & Telugu | Learn with Anil',
           h1='APPSC Group 2 previous year question papers <em>with answers.</em>',
           l2line='APPSC గ్రూప్ 2 మునుపటి సంవత్సరం ప్రశ్నపత్రాలు, పాత ప్రశ్నాపత్రాలు (ప్రిలిమ్స్, మెయిన్స్) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.',
           aka='Also known as AP Group 2 or APPSC Group-II Services. Old question papers, PYQs and practice bits, all with the final key.',
           desc=lambda t: (f"APPSC Group 2 (AP Group 2) previous year question papers and old papers with answers from APPSC's final key: Prelims (Screening Test) 2024 "
                           f"and Mains 2025 Paper 1 and Paper 2. {t:,} questions in English and Telugu with explanations; "
                           f"practice quizzes and timed mock tests, 3 days free."),
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           eyebrow='APPSC Group-II · Prelims (Screening) 2024 &amp; Mains 2025',
           papers_note="Every paper uses APPSC's official final key, with all four options for every question."),
      dict(id='appsc-group-1', dir='appsc-group-1', src='appsc-group-1', key='appsc-g1', name='APPSC Group-I', short='Group-I', seo='APPSC Group 1',
           slugp='appsc-group-1', papers=G1_PAPERS, subjects=G1_SUBJECTS, faq=FAQ_G1, board='APPSC', l2=L2_TE, pb='/appsc-group-1/',
           keyname="APPSC's official final key", keyshort="APPSC's final keys",
           title='APPSC Group 1 Previous Year Question Papers (PYQs) with Answers – Prelims 2024 Paper 1 & 2, English & Telugu | Learn with Anil',
           h1='APPSC Group 1 previous year question papers <em>with answers.</em>',
           l2line='APPSC గ్రూప్ 1 ప్రిలిమ్స్ మునుపటి సంవత్సరం ప్రశ్నపత్రాలు, పాత ప్రశ్నాపత్రాలు సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.',
           aka='Also known as AP Group 1 or APPSC Group-I Services. Old question papers and PYQs of the Prelims, with the final key.',
           desc=lambda t: (f"APPSC Group 1 (AP Group 1) Prelims previous year question papers and old papers with answers from APPSC's final key: the 2024 Prelims "
                           f"Paper 1 General Studies and Paper 2 General Aptitude. {t:,} questions in English and Telugu with explanations; "
                           f"practice quizzes and timed mock tests, 3 days free."),
           eyebrow='APPSC Group-I · Prelims 2024',
           papers_note="Every paper uses APPSC's official final key, with all four options for every question."),
      dict(id='upsc-capf', dir='upsc-capf', src='upsc-capf', key='upsc-capf', name='UPSC CAPF (AC)', short='CAPF (AC)', seo='UPSC CAPF AC',
           slugp='upsc-capf-ac', papers=CAPF_PAPERS, subjects=CAPF_SUBJECTS, faq=FAQ_CAPF, board='UPSC', l2=L2_HI, pb='/upsc-capf/',
           keyname="UPSC's answer keys", keyshort="UPSC's answer keys (2025: compiled from published keys)",
           title='UPSC CAPF AC Previous Year Question Papers with Answers (2024–2026), English & Hindi | Learn with Anil',
           h1='UPSC CAPF AC previous year question papers <em>with answers.</em>',
           aka='Also known as the CAPF Assistant Commandant (AC) exam. PYQs of Paper 1 (General Ability and Intelligence), subject-wise, with the answer key.',
           l2line='यूपीएससी सीएपीएफ असिस्टेंट कमांडेंट के पिछले वर्षों के प्रश्न पत्र, उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; पंजीकरण करने पर 3 दिन निःशुल्क।',
           desc=lambda t: (f"UPSC CAPF AC (Assistant Commandant) previous year question papers: Paper 1 General Ability and Intelligence "
                           f"2026, 2025 and 2024 with answer keys and explanations. {t:,} questions in English and Hindi; "
                           f"subject-wise practice and timed mock tests, 3 days free."),
           eyebrow='UPSC CAPF (Assistant Commandants) · Paper I · 2024–2026',
           papers_note="2026: UPSC's provisional answer key, published three days after the exam; the final key may differ for a few questions. 2025: UPSC's key could not be found, so the answers were compiled by Learn with Anil from three published keys and checked one by one. 2024: UPSC's official answer key (Series A). Questions UPSC dropped are left out. Every question is in English and Hindi, as printed in the booklet."),
      dict(id='upsc-epfo', dir='upsc-epfo', src='upsc-epfo', key='upsc-epfo', name='UPSC EPFO (APFC, EO/AO)', short='EPFO', seo=('UPSC EPFO' if E['eo'] else 'UPSC EPFO APFC'),
           slugp='upsc-epfo', papers=EPFO_PAPERS, subjects=EPFO_SUBJECTS, faq=FAQ_EPFO, board='UPSC', l2=L2_HI, pb='/upsc-epfo/',
           keyname="UPSC's official answer key", keyshort="UPSC's official answer keys",
           hi_name='यूपीएससी ईपीएफओ', hi_paper='भर्ती परीक्षा', subj_te=EPFO_SUBJ_HI,
           title=(f"UPSC EPFO Previous Year Question Papers with Answers – {E['papers']}, English & Hindi | Learn with Anil" if E['eo'] else
                  'UPSC EPFO APFC Previous Year Question Paper with Answers – APFC 2023, English & Hindi | Learn with Anil'),
           h1=('UPSC EPFO APFC &amp; EO/AO previous year question papers <em>with answers.</em>' if E['eo'] else
               'UPSC EPFO APFC previous year question paper <em>with answers.</em>'),
           aka=('Also known as the EPFO Assistant Provident Fund Commissioner (APFC) and Enforcement Officer / Accounts Officer (EO/AO) recruitment tests. ' if E['eo'] else
                'Also known as the EPFO Assistant Provident Fund Commissioner (APFC) recruitment test. ')
               + 'PYQs with UPSC\'s official answer key, subject-wise: labour laws, social security, accounting, polity, economy, history, science, aptitude and English.',
           aka_short=('UPSC EPFO APFC and EO/AO (Enforcement Officer / Accounts Officer)' if E['eo'] else 'UPSC EPFO Assistant Provident Fund Commissioner (APFC)'),
           l2line=('यूपीएससी ईपीएफओ सहायक भविष्य निधि आयुक्त (APFC) और प्रवर्तन अधिकारी/लेखा अधिकारी (EO/AO) भर्ती परीक्षाओं के पिछले वर्षों के प्रश्न पत्र, आधिकारिक उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; पंजीकरण करने पर 3 दिन निःशुल्क।' if E['eo'] else
                   'यूपीएससी ईपीएफओ सहायक भविष्य निधि आयुक्त (APFC) भर्ती परीक्षा का पिछले वर्ष का प्रश्न पत्र, आधिकारिक उत्तर कुंजी सहित — हिंदी और अंग्रेज़ी में; पंजीकरण करने पर 3 दिन निःशुल्क।'),
           desc=lambda t: ((f"UPSC EPFO previous year question papers with UPSC's official answer keys and explanations: the APFC 2023 recruitment test and the EO/AO (Enforcement Officer / Accounts Officer) {E['eoy'].replace(' & ', ' and ')} test{'s' if E['eo21'] else ''}. " if E['eo'] else
                            f"UPSC EPFO APFC (Assistant Provident Fund Commissioner) previous year question paper: the 2023 recruitment test with UPSC's official answer key and explanations. ")
                           + f"{t:,} questions in English and Hindi on labour laws, social security, accounting, polity, economy, history, science, aptitude and English; "
                           f"subject-wise practice and timed mock tests, 3 days free."),
           eyebrow=(f"UPSC · EPFO APFC &amp; EO/AO · Recruitment Tests {E['years']}" if E['eo'] else 'UPSC · EPFO Assistant Provident Fund Commissioner · Recruitment Test 2023'),
           papers_note=("Answers come from UPSC's official answer keys (Series A) on upsc.gov.in. UPSC dropped no question in the two 2023 papers"
                        + (" and one (Q71) in the 2021 EO/AO paper, which is left out" if E['eo21'] else "")
                        + ". Part A (General English) is in English only; every other question is in English and Hindi, as printed in the booklets." if E['eo'] else
                        "Answers come from UPSC's official answer key (Series A), published on upsc.gov.in in August 2024; no question was dropped. Part A (General English) is in English only; every other question is in English and Hindi, as printed in the booklet.")),
      dict(id='ts-police-si', dir='ts-police-si', src='ts-police-si', key='ts-si', name='TS Police SI', short='TS Police SI', seo='TS Police SI',
           slugp='ts-police-si', papers=TS_SI_PAPERS, subjects=TS_SUBJECTS, faq=FAQ_TS('SI', T['si']), board='TSLPRB', l2=L2_TE, pb='/ts-police-si/',
           keyname="TSLPRB's final key", keyshort="TSLPRB's final key", bits=True,
           te_name='తెలంగాణ పోలీస్ ఎస్ఐ', te_paper='ప్రిలిమినరీ పరీక్ష',
           title=('TS Police SI Previous Question Papers with Answers – Telangana SI Prelims 2022 & Mains 2023 (TSLPRB), English & Telugu | Learn with Anil' if si_m else
                  'TS Police SI Previous Question Papers with Answers – Telangana SI (TSLPRB) Prelims 2022, English & Telugu | Learn with Anil'),
           h1='TS Police SI previous year question papers <em>with answers.</em>',
           l2line=('తెలంగాణ పోలీస్ ఎస్ఐ ప్రిలిమినరీ, ఫైనల్ రాత పరీక్షల పాత ప్రశ్నాపత్రాలు (మునుపటి ప్రశ్నపత్రాలు) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.' if si_m else
                   'తెలంగాణ పోలీస్ ఎస్ఐ ప్రిలిమినరీ పరీక్ష పాత ప్రశ్నాపత్రం (మునుపటి ప్రశ్నపత్రం) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.'),
           aka='Also known as the Telangana (TG) Police SI exam: SCT SI (Civil) and equivalent posts, conducted by TSLPRB, now TGPRB.',
           aka_short='Telangana Police SI (TSLPRB / TGPRB)',
           desc=lambda t: ((f"TS Police SI (Telangana SI, TSLPRB / TGPRB) previous question papers: Prelims 2022 and Mains 2023 (Final Written Examination {T['si_fwe']}) with answers from TSLPRB's final keys. " if si_m else
                            f"TS Police SI (Telangana SI, TSLPRB / TGPRB) previous question paper: Preliminary Written Test 2022 with answers from TSLPRB's final key. ")
                           + f"{t:,} questions on arithmetic, reasoning and general studies in English and Telugu with explanations; practice quizzes and timed mock tests, 3 days free."),
           eyebrow=('TSLPRB / TGPRB · SI (Civil) &amp; equivalent · Prelims 2022 &amp; Final Written Exam 2023' if si_m else
                    'TSLPRB / TGPRB · SI (Civil) &amp; equivalent · Preliminary Written Test'),
           papers_note=("Answers come from TSLPRB's final keys: booklet A for the 2022 Preliminary Written Test (key released on 21 October 2022) and booklet D for the 2023 Final Written Examination. "
                        "Questions the key deleted, or for which it accepted three or four options, are left out, as are the few that cannot be read cleanly in the photographed booklet. Every question is in English and Telugu, as printed in the booklet." if si_m else
                        "Answers come from TSLPRB's final key for booklet A, released on 21 October 2022. Questions the key deleted, or for which it accepted three or four options, are left out. Every question is in English and Telugu, as printed in the booklet.")),
      dict(id='ts-police-constable', dir='ts-police-constable', src='ts-police-constable', key='ts-pc', name='TS Police Constable', short='TS Constable', seo='TS Police Constable',
           slugp='ts-police-constable', papers=TS_PC_PAPERS, subjects=TS_SUBJECTS, faq=FAQ_TS('PC', T['pc']), board='TSLPRB', l2=L2_TE, pb='/ts-police-constable/',
           keyname="TSLPRB's final key", keyshort="TSLPRB's final key", bits=True,
           te_name='తెలంగాణ పోలీస్ కానిస్టేబుల్', te_paper='ప్రిలిమినరీ పరీక్ష',
           title=('TS Police Constable Previous Question Papers with Answers – Telangana Constable Prelims 2022 & Mains 2023 (TSLPRB), English & Telugu | Learn with Anil' if pc_m else
                  'TS Police Constable Previous Question Papers with Answers – Telangana Constable (TSLPRB) Prelims 2022, English & Telugu | Learn with Anil'),
           h1='TS Police Constable previous year question papers <em>with answers.</em>',
           l2line=('తెలంగాణ పోలీస్ కానిస్టేబుల్ ప్రిలిమినరీ, ఫైనల్ రాత పరీక్షల పాత ప్రశ్నాపత్రాలు (మునుపటి ప్రశ్నపత్రాలు) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.' if pc_m else
                   'తెలంగాణ పోలీస్ కానిస్టేబుల్ ప్రిలిమినరీ పరీక్ష పాత ప్రశ్నాపత్రం (మునుపటి ప్రశ్నపత్రం) సమాధానాలతో — తెలుగు, ఇంగ్లీష్‌లో; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.'),
           aka='Also known as the Telangana (TG) Police Constable or TS PC exam: SCT PC (Civil) and equivalent posts, conducted by TSLPRB, now TGPRB.',
           aka_short='Telangana Police Constable (TSLPRB / TGPRB)',
           desc=lambda t: (("TS Police Constable (Telangana Constable, TSLPRB / TGPRB) previous question papers: Prelims 2022 and Mains 2023 (Final Written Examination, 30 April 2023) with answers from TSLPRB's final keys. " if pc_m else
                            "TS Police Constable (Telangana Constable, TSLPRB / TGPRB) previous question paper: Preliminary Written Test 2022 with answers from TSLPRB's final key. ")
                           + f"{t:,} questions on English, arithmetic, reasoning and general studies in English and Telugu with explanations; practice quizzes and timed mock tests, 3 days free."),
           eyebrow=('TSLPRB / TGPRB · Police Constable (Civil) &amp; equivalent · Prelims 2022 &amp; Final Written Exam 2023' if pc_m else
                    'TSLPRB / TGPRB · Police Constable (Civil) &amp; equivalent · Preliminary Written Test'),
           papers_note=("Answers come from TSLPRB's final keys for booklet A of the 2022 Preliminary Written Test (key released on 21 October 2022) and of the 2023 Final Written Examination. "
                        "Questions the key deleted, or for which it accepted three or four options, are left out, as are the few that cannot be read cleanly in the photographed booklet. The English-language questions are in English only; every other question is in English and Telugu, as printed in the booklet." if pc_m else
                        "Answers come from TSLPRB's final key for booklet A, released on 21 October 2022. Questions the key deleted, or for which it accepted three or four options, are left out. The English-language questions are in English only; every other question is in English and Telugu, as printed in the booklet.")),
      dict(id='tgpsc-hmwssb-manager', dir='tgpsc-hmwssb-manager', src='tgpsc-hmwssb-manager', key='tg-hmws', name='TGPSC HMWSSB Manager (Engineering)',
           short='HMWSSB Manager', seo='TGPSC HMWSSB Manager', slugp='tgpsc-hmwssb-manager', papers=HM_PAPERS, subjects=HM_SUBJECTS, faq=FAQ_HM,
           board='TGPSC', l2=L2_TE, pb='/tgpsc-hmwssb-manager/', keyname="TSPSC's final key", keyshort="TSPSC's final key", bits=True,
           te_name='టీజీపీఎస్సీ జలమండలి (HMWSSB) మేనేజర్ (ఇంజనీరింగ్)', te_paper='రాత పరీక్ష', subj_te=HM_SUBJ_TE,
           title='TGPSC HMWSSB Manager (Engineering) Previous Question Papers with Answers – GS & Civil Engineering, English & Telugu | Learn with Anil',
           h1='TGPSC HMWSSB Manager (Engineering) previous question papers <em>with answers.</em>',
           l2line='టీజీపీఎస్సీ జలమండలి (HMWSSB) మేనేజర్ (ఇంజనీరింగ్) పాత ప్రశ్నాపత్రాలు సమాధానాలతో — జనరల్ స్టడీస్ (తెలుగు, ఇంగ్లీష్), సివిల్ ఇంజనీరింగ్; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.',
           aka='Manager (Engineering) in the Hyderabad Metropolitan Water Supply and Sewerage Board (HMWSSB, Jalamandali), recruited by TGPSC, formerly TSPSC.',
           aka_short='TGPSC (TSPSC) Manager (Engineering), Hyderabad Metro Water Board',
           desc=lambda t: (f"TGPSC (TSPSC) HMWSSB Manager (Engineering) previous question papers: the 2015 Paper 1 General Studies (English and Telugu) "
                           f"and Paper 2 Civil Engineering with answers from TSPSC's final key. {t:,} questions with explanations; practice quizzes and timed mock tests, 3 days free."),
           eyebrow='TGPSC (TSPSC) · Manager (Engineering), HMWSSB · Notification 13/2015',
           papers_note="Answers come from TSPSC's final key for booklet Series A (Notification 13/2015, written test held on 1 November 2015). Questions for which TSPSC gave the mark to every candidate are left out. Paper 1 is in English and Telugu as printed (its English-language questions in English only); Paper 2 (Civil Engineering) is in English only."),
    ]


def main():
    confs = exam_confs()
    PAY['exams'] = ', '.join(c['seo'] for c in confs)   # the PYQ Pass covers every one of these
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
    import bahubali   # paid Group-II Mains test series (encrypted; see tools/bahubali.py)
    bb_live = bool(bahubali.load_series().get('tests'))
    bb_url = '/' + bahubali.URLDIR + '/' if bb_live else ''
    global BB_URL
    BB_URL = bb_url
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
                    key=conf['key'], exam=conf['name'], bahubali=bb_url if conf['board'] == 'APPSC' else '', examShort=conf['short'], papersNote=conf['papers_note'], hub=is_root,
                    board=conf['board'], l2={k: conf['l2'][k] for k in ('code', 'label', 'name', 'font')},
                    base=prefix, qotd=qotd_pool(loaded, 120) if is_root else [], pay=pay_data(conf),
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
        tiles = tiles_html(conf, papers, questions, links)

        def fill(s, photo, title, seo, desc=''):
            return (s.replace('{{SEO_HEAD}}', seo).replace('{{TITLE}}', title).replace('{{DESC}}', esc(desc))
                     .replace('{{L2CODE}}', l2['code']).replace('{{L2LABEL}}', l2['label']).replace('{{FONTS2}}', l2['gf'])
                     .replace('{{LANGS}}', 'English and ' + l2['name']).replace('{{KEYSHORT}}', conf['keyshort'])
                     .replace('{{BOARD}}', conf['board'])
                     .replace('{{FOOTSRC}}', 'Questions and answers are from the official final keys.' if conf['board'] in ('APPSC', 'TSLPRB')
                              else f'Questions are from {conf["board"]}\'s official question paper; answers from {conf["keyshort"]}.')
                     .replace('{{FROMPAPERS}}', f'{len(papers)} official papers' if len(papers) > 1 else f'the official {papers[0]["year"]} {esc(papers[0]["stage"])} question paper')
                     .replace('{{PAPERSK}}', f'Official {conf["board"]} paper' + ('s' if len(papers) > 1 else ''))
                     .replace('{{HOME_PAPERS}}', home_papers).replace('{{PYQPAGE}}', conf['pb'] + 'pyqs.html').replace('{{HOME_SUBJECTS}}', home_subjects).replace('{{FAQ}}', faq_html)
                     .replace('{{DATA}}', data_json).replace('{{PHOTO}}', photo)
                     .replace('{{TOTAL}}', str(total)).replace('{{SITE}}', SITE_URL).replace('{{NPAPERS}}', str(len(papers)))
                     .replace('{{HOME_NOTES}}', home_notes(enotes, bb_url if conf['board'] == 'APPSC' else '')).replace('{{HUB}}', hub)
                     .replace('{{NEXAMS}}', str(len(catalog['exams']))).replace('{{TOTALC}}', f'{grand:,}')
                     .replace('{{LIVE_SUMMARY}}', esc(live_summary))
                     .replace('{{HUB_CTAS}}', hub_ctas)
                     .replace('{{NAV_EXTRA}}', nav_extra if is_root else '')
                     .replace('{{TIMERS}}', timers).replace('{{HUBHREF}}', hubhref).replace('{{ROOTUP}}', up)
                     .replace('{{EXAM}}', esc(conf['name'])).replace('{{EXAMSHORT}}', esc(conf['short']))
                     .replace('{{EYEBROW}}', conf['eyebrow']).replace('{{H1}}', conf['h1'])
                     .replace('{{L2LINE}}', f'<span lang="{l2["code"]}">{esc(conf["l2line"])}</span>')
                     .replace('{{AKA}}', esc(conf.get('aka', '')))
                     .replace('{{TILES}}', tiles))
        root_title = 'PYQs with Answers – APPSC Group 1 & Group 2, TS Police SI & Constable, UPSC CAPF Previous Papers | Learn with Anil'
        root_desc = (f'Free previous year question papers (PYQs) with answers: APPSC Group 1 & Group 2 (AP Group 1, AP Group 2), TS Police SI & Constable '
                     f'(Telangana police, TSLPRB / TGPRB) and UPSC CAPF AC. {grand:,} questions from the official keys, with explanations in English, Telugu and Hindi. '
                     f'3 days free when you register, then one ₹45 PYQ Pass for every exam; TGPSC, UPSC, SSC, banking and railway exams are being added.')
        home_title = conf['title']
        ptxt = f'{len(papers)} official papers' if len(papers) > 1 else f'the official {papers[0]["year"]} {papers[0]["stage"]} question paper'
        home_desc = conf['desc'](total)
        pb = conf['pb']; basedir = '/' + prefix
        person = {"@context":"https://schema.org","@type":"Person","name":"Jupudi Anil Kumar","jobTitle":"UPSC Faculty and Mentor","telephone":"+91-94947-92739","email":"mailto:anilkumarjupudi360360@gmail.com","url":SITE_URL+'/appsc-group-2/about/',"image":SITE_URL+'/anil.jpg',"sameAs":[f"https://www.instagram.com/{INSTAGRAM}/"]}
        website = {"@context":"https://schema.org","@type":"WebSite","name":"Learn with Anil","alternateName":"Learn with Anil – Previous year questions for every exam","url":SITE_URL+'/'}
        org = {"@context":"https://schema.org","@type":"Organization","name":"Learn with Anil","url":SITE_URL+'/',"logo":SITE_URL+'/icon-512.png',"founder":{"@type":"Person","name":"Jupudi Anil Kumar"},"sameAs":[f"https://www.instagram.com/{INSTAGRAM}/"]}
        faqld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in faq]}
        seo_name = conf['seo']
        views = {   # view: (title, description, canonical path, indexable)
          'papers': ((f'{seo_name} Previous Year Question Papers with Answers – All {len(papers)} Papers | Learn with Anil' if len(papers) > 1 else
                      f'{seo_name} Previous Question Paper with Answers – {paper_kw(conf, papers[0]).replace(seo_name + " ", "")}, English & {conf["l2"]["name"]} | Learn with Anil'),
                     (f'All {len(papers)} {seo_name} previous year question papers' if len(papers) > 1 else f'{seo_name} previous question paper') + f' ({", ".join(paper_kw(conf, p).replace(seo_name + " ", "") for p in sorted(papers, key=lambda p: (-p["year"], p["id"])))}): '
                     f'practise {"each paper" if len(papers) > 1 else "it"} online as a quiz or a timed mock test, with answers and explanations: 3 days free when you register.', pb + 'papers/', True),
          'practice': (f'{seo_name} Mock Test & Topic-wise Quiz from Previous Papers | Learn with Anil',
                       f'{seo_name} mock test and topic-wise quiz made from {total:,} real previous year questions{" (practice bits)" if conf["board"] == "APPSC" or conf.get("bits") else ""}: '
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

        site_pages = {}   # path under the site root -> html
        if is_root:
            os.makedirs(os.path.join(DIST, 'artifact', 'papers')); os.makedirs(os.path.join(DIST, 'artifact', 'subjects'))
            open(os.path.join(DIST, 'artifact', 'index.html'), 'w', encoding='utf-8').write(fill(head + body, photo_uri, 'Learn with Anil', '', root_desc))
            site_pages['index.html'] = site_doc(root_title, root_desc, '/', [website, org, person])
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
        if PUBLIC_PDFS:
            for p in papers: all_pages[pdf_href(conf, p).lstrip('/')] = None   # the PDFs come from tools/pdfs.py
        print(f'  {conf["name"]}: {total} questions, {len(pages)} static pages, {len(qpages)} question pages, {len(site_pages)} app pages')

    # one crawlable page per recruiting board listing all its papers (where "APPSC PYQs" / "TS police previous papers" searches land)
    lands = {rel: None for rel in LANDINGS if any(c['board'] == LANDINGS[rel]['board'] for c, _, _ in loaded)}
    for rel in lands:
        open(os.path.join(DIST, 'site', rel), 'w', encoding='utf-8').write(landing_page(loaded, rel))
    all_pages = {**lands, **all_pages}
    notifs = {rel: None for rel in NOTIFS if any(c['id'] == NOTIFS[rel]['exam'] for c, _, _ in loaded)}
    for rel in notifs:
        open(os.path.join(DIST, 'site', rel), 'w', encoding='utf-8').write(notif_page(loaded, rel))
    mocks = {}
    for c, ps, qs in loaded:
        if not any(p['fmt'] == 'mcq' for p in ps): continue
        for fn in (pyq_page, mock_page, sectional_page):
            rel, html_ = fn(c, ps, qs)
            open(os.path.join(DIST, 'site', rel), 'w', encoding='utf-8').write(html_)
            mocks[rel] = None
    if bb_live: mocks[bahubali.page(os.path.join(DIST, 'site'))] = None
    all_pages = {**notifs, **mocks, **all_pages}

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
    # sealed (encrypted) paid mocks: published as-is; the keys are only in Anil's private sheet (tools/mk_seal.py)
    mkdir_ = os.path.join(SRC, 'mission-khaki')
    if os.path.isdir(mkdir_):
        os.makedirs(os.path.join(DIST, 'site', 'ts-police-si', 'mk'), exist_ok=True)
        for f in os.listdir(mkdir_):
            if f.endswith('.bin'): shutil.copy(os.path.join(mkdir_, f), os.path.join(DIST, 'site', 'ts-police-si', 'mk', f))
    open(os.path.join(DIST, 'site', '.nojekyll'), 'w').write('')
    print(f'  grand total {grand} questions, {len(all_pages)} static pages')


def bahubali_promo(url):
    return f'''<a class="card notes-promo bb-promo" href="{url}">
      <div class="np-copy"><p class="eyebrow">New · APPSC Group-II Mains 2026</p><h2>Bahubali Test Series</h2>
      <p>24 full-length mock tests for Paper I and Paper II (12 each): 150 questions per test, English and Telugu, ⅓ negative marking, explanations from official sources and PDFs. ₹250 for the whole series.</p>
      <span class="btn btn-primary">See the tests</span></div>
      <div class="bb-mark" aria-hidden="true"><b>150</b><span>Qs · 150 min</span></div>
    </a>'''


def home_notes(notes, bb_url=''):
    if not notes and not bb_url: return ''
    if not notes: return f'<section class="wrap section">{bahubali_promo(bb_url)}</section>'
    covers = ''.join(f'<img src="{esc(b["cover"])}" alt="" width="140" height="198" loading="lazy">' for b in notes)
    return f'''<section class="wrap section">{bahubali_promo(bb_url) if bb_url else ''}
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
    """'APPSC Group 2 Prelims 2024', 'APPSC Group 2 Mains 2025 Paper 1', 'UPSC CAPF AC 2026 Paper 1'; a paper's own 'kwname' wins (EPFO: APFC vs EO/AO)."""
    if p.get('kwname'): return p['kwname']
    n = paper_no(p)
    if conf['board'] in ('UPSC', 'TGPSC'):
        return f'{conf["seo"]} {p["year"]}' + (f' Paper {n}' if n else '')
    stage = 'Prelims' if p['stage'].startswith(('Screening', 'Prelims', 'Preliminary')) else 'Mains'
    return f'{conf["seo"]} {stage} {p["year"]}' + (f' Paper {n}' if n else '')


def paper_alt(conf, p):
    """The paper's other name, if students also search by it."""
    if p.get('alt'): return p['alt']
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
        return f'{conf["hi_name"]} {p.get("hi_paper") or conf["hi_paper"]} {p["year"]} प्रश्न पत्र, उत्तर कुंजी सहित'
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
    if 'police' in e['id']: words += ['ts police', 'tg police', 'tslprb', 'tgprb', 'si', 'constable']
    if 'hmwssb' in e['id']: words += ['hmwssb', 'water board', 'jalamandali', 'metro water', 'manager engineering', 'civil engineering', 'hmws']
    if 'civil-judge' in e['id']: words += ['civil judge', 'junior civil judge', 'jcj', 'judiciary', 'high court', 'llb', 'law']
    if e['cat'] == 'ap': words += ['appsc', 'andhra'] + ([f'ap group {ROMAN[m.group(1)]}'] if m else [])
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
            status = f'Live · {counts.get(e["id"], 0):,} questions' if live else 'Upcoming'
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
            + (f'<a class="btn btn-ghost btn-sm" href="{p["pdf"]}" download>PDF</a>' if p.get('pdf') else '') + '</div></article>')


def FAQ(total, npapers):
    return [
      ('Where can I get APPSC Group 2 previous year question papers with answers?',
       f'This site has {total} questions from {npapers} APPSC Group-II papers: the Screening Test 2024 and Mains 2025 Paper I and Paper II. Every answer is taken from APPSC\'s official final key, and each question has a short explanation. You can practise each paper as a quiz or a timed test, with answers and explanations: 3 days free when you register, then one ₹45 PYQ Pass for every exam.'),
      ('What does it cost, and what does the ₹45 PYQ Pass cover?',
       'There are three plans. Free trial: register once and every previous paper of every exam, with all study tools, opens for 3 days. PYQ Pass, ₹45: every previous paper of every exam on the website, including exams added later, with answers, explanations, quizzes, timed tests and all study tools, for 12 months. Mock-test packs such as Mission Khaki are sold separately. Without a plan you can see the question of the day and the answers to the first 10 questions of each paper.'),
      ('Are the APPSC Group 2 previous papers available in Telugu?',
       'Yes. Almost every question has APPSC\'s own Telugu text, as printed in the question booklet. Tap తెలుగు at the top of the page to practise in Telugu.'),
      ('Is there a APPSC Group 2 mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects, and pick Timed test: you get a mock test made of real APPSC Group 2 Prelims and Mains questions, with your score and a topic-wise analysis at the end. Practice mode works like practice bits, one question at a time with the answer and explanation.'),
      ('What is the APPSC Group 2 exam pattern?',
       'Under Notification 11/2023, the Screening Test is one objective paper of 150 questions for 150 marks in 150 minutes, with 30 marks each for Indian History, Geography, Indian Society, Current Affairs and Mental Ability. The Mains has two objective papers of 150 marks each: Paper I covers the Social and Cultural History of Andhra Pradesh and the Indian Constitution, and Paper II covers the Indian and AP Economy and Science and Technology.'),
      ('Are the answers on this site official?',
       'Yes. The answers come from the final keys published by APPSC. Questions that APPSC deleted are left out, and where the final key accepted two options, both are shown as correct. The explanations are written by Learn with Anil.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; registering also starts your 3-day free trial of the previous papers of every exam, and after that one ₹45 PYQ Pass covers them all for 12 months. There is no password. Your scores are saved with Learn with Anil so Anil can guide you, and your practice attempts, mistakes notebook and bookmarks stay on your own device.'),
    ]


def FAQ_G1(total, npapers):
    return [
      ('Where can I get APPSC Group 1 previous year question papers with answers?',
       f'This page has {total} questions from {npapers} APPSC Group-I Prelims papers: Paper I (General Studies) and Paper II (General Aptitude) of the 2024 exam. Every answer is taken from APPSC\'s official final key, and each question has a short explanation. You can practise each paper as a quiz or a timed test, with answers and explanations: 3 days free when you register, then one ₹45 PYQ Pass for every exam.'),
      ('What does it cost, and what does the ₹45 PYQ Pass cover?',
       'There are three plans. Free trial: register once and every previous paper of every exam, with all study tools, opens for 3 days. PYQ Pass, ₹45: every previous paper of every exam on the website, including exams added later, with answers, explanations, quizzes, timed tests and all study tools, for 12 months. Mock-test packs such as Mission Khaki are sold separately. Without a plan you can see the question of the day and the answers to the first 10 questions of each paper.'),
      ('Where is the APPSC Group 1 Prelims 2024 answer key?',
       'Each question on this site shows the answer from APPSC\'s final key, for Paper 1 (General Studies) and Paper 2 (General Aptitude) of the 2024 Prelims. Open a paper to see every question with its answer.'),
      ('Is there a APPSC Group 1 mock test?',
       'Yes. Tap Create a quiz, choose papers or subjects, and pick Timed test: you get a mock test made of real APPSC Group 1 Prelims questions, in English or Telugu, with your score and a topic-wise analysis at the end.'),
      ('What is the APPSC Group 1 Prelims exam pattern?',
       'The Preliminary Examination has two objective papers on the same day: Paper I General Studies (History and Culture; Constitution, Polity, Social Justice and International Relations; Indian and AP Economy and Planning; Geography) and Paper II General Aptitude (General Mental Ability, Administrative and Psychological Abilities; Science and Technology; Current Events). Each paper has 120 questions for 120 marks in 120 minutes, and one-third of the marks of a question is deducted for a wrong answer. Prelims marks are used only to shortlist candidates for the Mains.'),
      ('Are the answers on this site official?',
       'Yes. The answers come from the final keys published by APPSC. Questions that APPSC deleted are left out, and where the final key accepted two options, both are shown as correct. The explanations are written by Learn with Anil.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; registering also starts your 3-day free trial of the previous papers of every exam, and after that one ₹45 PYQ Pass covers them all for 12 months. There is no password. Your scores are saved with Learn with Anil so Anil can guide you, and your practice attempts, mistakes notebook and bookmarks stay on your own device.'),
    ]


def FAQ_CAPF(total, npapers):
    return [
      ('Where can I get UPSC CAPF AC previous year question papers with answers?',
       f'This page has {total} questions from {npapers} UPSC CAPF (Assistant Commandants) Paper I papers, General Ability and Intelligence (2024, 2025 and 2026), in English and Hindi as printed in the official question booklets. Every question has a short explanation. You can practise each paper as a quiz or a timed test, with answers and explanations: 3 days free when you register, then one ₹45 PYQ Pass for every exam.'),
      ('What does it cost, and what does the ₹45 PYQ Pass cover?',
       'There are three plans. Free trial: register once and every previous paper of every exam, with all study tools, opens for 3 days. PYQ Pass, ₹45: every previous paper of every exam on the website, including exams added later, with answers, explanations, quizzes, timed tests and all study tools, for 12 months. Mock-test packs such as Mission Khaki are sold separately. Without a plan you can see the question of the day and the answers to the first 10 questions of each paper.'),
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
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; registering also starts your 3-day free trial of the previous papers of every exam, and after that one ₹45 PYQ Pass covers them all for 12 months. There is no password. Your scores are saved with Learn with Anil so Anil can guide you, and your practice attempts, mistakes notebook and bookmarks stay on your own device.'),
    ]


def FAQ_EPFO(total, npapers):
    E = epfo_text(); eo = E['eo']   # are the EO/AO papers on the site?
    return [
      (('Where can I get UPSC EPFO previous year question papers with answers?' if eo else
        'Where can I get the UPSC EPFO APFC previous year question paper with answers?'),
       (f'This page has {total} questions from {npapers} UPSC recruitment tests for EPFO: Assistant Provident Fund Commissioner (APFC), held on 2 July 2023, and Enforcement Officer / Accounts Officer (EO/AO), held on {E["eodates"]}. ' if eo else
        f'This page has {total} questions from the UPSC recruitment test for Assistant Provident Fund Commissioner (APFC) in EPFO, held on 2 July 2023. ')
       + 'Every question is in English and Hindi as printed in the official booklet (Series A), apart from the General English part. Every answer is taken from UPSC\'s official answer key and every question has a short explanation. '
       'You can practise each paper question by question, subject-wise or as a timed test: 3 days free when you register, then one ₹45 PYQ Pass for every exam.'),
      ('Are the answers official?',
       ('Yes. They come from UPSC\'s official answer keys for Series A, published on upsc.gov.in after each recruitment was completed. UPSC dropped no question in the 2023 papers'
        + ('; in the 2021 EO/AO paper it dropped Q71, which is left out. ' if E['eo21'] else '. ') if eo else
        'Yes. They come from UPSC\'s official answer key for Series A, published on upsc.gov.in in August 2024 after the recruitment was completed. UPSC dropped no question in this paper. ')
       + 'Where a keyed answer is debatable, the explanation says "(Official key; some sources differ.)". The explanations are written by Learn with Anil.'),
      ('What is the UPSC EPFO exam pattern?' if eo else 'What is the UPSC EPFO APFC exam pattern?',
       'The recruitment test is one objective paper of 120 questions for 300 marks in two hours, in English and Hindi (the General English part in English only). '
       'A wrong answer costs one-third of the marks for that question. Candidates who qualify are called for an interview; the test and the interview are weighted 75:25. '
       'The syllabus covers General English, Indian freedom struggle, history and culture, current events and developmental issues, Indian polity and economy, general accounting principles, '
       'industrial relations and labour laws, social security in India, general science and computer applications, and general mental ability and quantitative aptitude. '
       + ('APFC and EO/AO have had separate papers on the same syllabus; in 2025 UPSC set one common paper for both posts.' if eo else '')),
      ('Which labour law questions come in the EPFO exams?' if eo else 'Which labour law questions come in the APFC exam?',
       ('The papers ask about the EPF &amp; MP Act, the Employees\' Compensation Act, the ESI Act, the Industrial Disputes Act, the Trade Unions Act, the Factories Act, the Mines Act, the Payment of Wages, Payment of Bonus and Minimum Wages Acts, '
        'the Contract Labour and Standing Orders Acts, the Building and Other Construction Workers Act, and ILO conventions. ' if eo else
        'The 2023 paper had 18 questions on labour laws and social security: the EPF &amp; MP Act, the Employees\' Compensation Act, the ESI Act, the Industrial Disputes Act, the Trade Unions Act, '
        'the Factories Act, the Mines Act, the Payment of Wages and Payment of Bonus Acts, the Building and Other Construction Workers Act, and ILO core conventions. ')
       + 'The four Labour Codes, in force since 21 November 2025, have since replaced most of these Acts; the explanations say where the law has changed after the exam.'),
      ('Is the EPFO question paper available in Hindi?' if eo else 'Is the APFC question paper available in Hindi?',
       'Yes. Tap हिंदी at the top of the page to see every question and option of Part B in Hindi, exactly as printed in UPSC\'s booklet, with the explanation in Hindi. Part A (General English) is in English only.'),
      ('Is there an EPFO mock test?' if eo else 'Is there an EPFO APFC mock test?',
       ('Yes. Open the mock test page and take a real APFC or EO/AO paper with a timer, ' if eo else 'Yes. Open the mock test page and take the real 2023 paper with a timer, ')
       + 'or tap Create a quiz to choose subjects such as Labour Laws, Social Security or Accounting. You get your score, the official answer and an explanation for every question.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; registering also starts your 3-day free trial of the previous papers of every exam, and after that one ₹45 PYQ Pass covers them all for 12 months. There is no password.'),
    ]


def FAQ_HM(total, npapers):
    return [
      ('Where can I get TGPSC HMWSSB Manager (Engineering) previous question papers with answers?',
       f'This page has {total} questions from the TSPSC Manager (Engineering) written test for HMWSSB, Notification 13/2015, held on 1 November 2015: '
       'Paper 1 General Studies in English and Telugu, and Paper 2 Civil Engineering. Every answer is taken from TSPSC\'s final key (Series A), and each question has a short explanation. '
       'You can practise each paper as a quiz or a timed mock test, with answers and explanations: 3 days free when you register, then one ₹45 PYQ Pass for every exam.'),
      ('What is the TGPSC HMWSSB Manager (Engineering) 2026 exam pattern?',
       'Two objective papers: Paper 1 General Studies and General Abilities (150 questions, 150 marks, in English and Telugu) and Paper 2 in the candidate\'s engineering '
       'subject (150 questions, 300 marks, in English), 450 marks in all. Notification 04/2026 has 130 posts, mostly Civil, and the exam is tentatively in December 2026; confirm dates on tgpsc.gov.in.'),
      ('Are the HMWSSB Manager General Studies questions available in Telugu?',
       'Yes. Paper 1 (General Studies) is printed in English and Telugu, apart from its English-language questions, and every question is here exactly as printed. Tap తెలుగు at the top of the page to practise in Telugu. Paper 2 (Civil Engineering) is printed in English only.'),
      ('Is there a HMWSSB Manager mock test?',
       'Yes. Open the mock test page and take a real 2015 paper with a timer, or tap Create a quiz to choose subjects such as Environmental Engineering, Fluid Mechanics or Telangana History. You get your score, the official answer and an explanation for every question.'),
      ('Do I need to register?',
       'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; registering also starts your 3-day free trial of the previous papers of every exam, and after that one ₹45 PYQ Pass covers them all for 12 months. There is no password.'),
      ('Which questions are left out?',
       'In Paper 2 (Civil Engineering), TSPSC\'s final key gave the mark to every candidate for five questions (Q3, 37, 64, 95 and 128 in Series A); they are left out. The Mechanical, Electrical, ECE and CSE papers are not on the site yet.'),
    ]


def FAQ_TS(post, mains=()):
    si = post == 'SI'
    name = 'TS Police SI' if si else 'TS Police Constable'
    def faq(total, npapers):
        if mains:
            fwe = (' and '.join(x for i, x in (('s2023c', 'Paper III, Arithmetic & Reasoning, on 8 April'), ('s2023d', 'Paper IV, General Studies, on 9 April')) if i in mains)
                   + ' 2023, booklet D') if si else '30 April 2023, booklet A'
            where = (f'This page has {total:,} questions from {npapers} TSLPRB papers: the {"SI" if si else "Police Constable"} Preliminary Written Test of {"7 August" if si else "28 August"} 2022 (booklet A) '
                     f'and the Final Written Examination ({fwe}), in English and Telugu as printed. '
                     f'Every answer is taken from TSLPRB\'s final key for that paper, and each question has a short explanation. You can practise each paper as a quiz or a mock test, with answers and explanations: 3 days free when you register, then one ₹45 PYQ Pass for every exam.')
        else:
            where = (f'This page has {total} questions from the {"SI" if si else "Police Constable"} Preliminary Written Test held by TSLPRB on {"7 August" if si else "28 August"} 2022 (booklet A), in English and Telugu as printed. '
                     f'Every answer is taken from TSLPRB\'s final key, released on 21 October 2022, and each question has a short explanation. You can practise the paper as a quiz, with answers and explanations: 3 days free when you register, then one ₹45 PYQ Pass for every exam.')
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
           f'Yes. Tap Create a quiz, choose subjects or topics, and pick Timed test: you get a mock test made of real TSLPRB questions, with your score and a topic-wise analysis at the end. Practice mode works like practice bits, one question at a time with the answer and explanation.'),
          ('Do I need to register?',
           'Only once, and it is free. Before your first quiz or test you enter your name, phone, email and district one time; registering also starts your 3-day free trial of the previous papers of every exam, and after that one ₹45 PYQ Pass covers them all for 12 months. There is no password.'),
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
nav.toc{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}nav.toc a{background:var(--accent-soft);padding:4px 10px;border-radius:999px;text-decoration:none;font-size:15px}
footer{margin-top:40px;border-top:1px solid var(--line);color:var(--muted);font-size:15px}footer .wrap{padding-block:18px}
.sgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:8px 0}
.sgrid a{display:flex;justify-content:space-between;gap:10px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:700}
.sgrid a:hover,.fgrid a:hover{border-color:var(--accent)}.sgrid .n{font:13px/1.4 "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);font-weight:400;white-space:nowrap}
.fgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:8px 0}@media (max-width:640px){.fgrid{grid-template-columns:1fr}}
.fgrid:has(> a:only-child){grid-template-columns:1fr}
.fgrid a{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.fgrid b{display:block;font-size:17px;margin-bottom:2px}.fgrid span{color:var(--muted);font-size:15px}
"""


def static_page(rel_depth, title, desc, canonical, h1, lede, body_html, crumbs, conf=None, ename=None, at_root=False):
    ename = ename or (conf['name'] if conf else 'APPSC Group-II')
    rootup = '' if at_root else '../' * (rel_depth + (1 if conf and conf.get('dir') else 0))
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
{ICONS}{ga_tag()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header><div class="wrap"><a href="{pb if conf else '/'}">Learn with Anil · {nw(ename)} PYQs</a><a href="{pb}practice/">Practise online →</a></div></header>
<main class="wrap">
<h1>{nw(h1)}</h1>
<p class="lede">{lede}</p>
{body_html}
</main>
<footer><div class="wrap"><p style="margin:0 0 8px"><a href="{rootup}appsc-pyqs.html">All APPSC previous question papers (PYQs)</a> · <a href="{rootup}ts-police-pyqs.html">All TS Police previous question papers</a> · <a href="/appsc-group-2-notification-2026.html">APPSC Group 2 Notification 2026</a> · <a href="/appsc-group-1-notification-2026.html">Group 1 Notification 2026</a> · <a href="{rootup}appsc-group-1/">APPSC Group-I</a> · <a href="/appsc-group-2/">APPSC Group-II</a> · <a href="/upsc-capf/">UPSC CAPF (AC)</a> · <a href="/upsc-epfo/">UPSC EPFO (APFC)</a> · <a href="/ts-police-si/">TS Police SI</a> · <a href="/ts-police-constable/">TS Police Constable</a> · <a href="/">All exams</a></p>{foot} Visits are counted with Google Analytics.</div></footer>
</body>
</html>
"""


def lock_html(unlock):
    return (f'<p class="lock">Answer and explanation: <a href="{unlock}">open it in the practice app</a>. '
            f'{TRIAL_DAYS} days free when you register, then one ₹{PAY["pyq_price"]} PYQ Pass for every exam on the site.</p>')


def sample_ids(questions):
    """The questions whose answers stay public: the first SAMPLE_N of each paper."""
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
    if unlock:   # outside the free sample: no answer on the public page
        parts.append(lock_html(unlock) + '</li>')
        return ''.join(parts)
    parts.append(f'<details><summary>Show answer</summary><p class="ans">Answer: {esc(ans)}</p>{te_ans}<p class="why">{esc(q["w"])}</p>{wt}</details></li>')
    return ''.join(parts)


LANDINGS = {
  # file: what the page covers. People search "APPSC PYQs", "TS police previous papers", "TSLPRB previous question papers" ...
  'appsc-pyqs.html': dict(
      board='APPSC', ename='APPSC', crumb='APPSC PYQs',
      title='APPSC Previous Year Question Papers with Answers – Group 1 & Group 2 PYQs | Learn with Anil',
      desc='All APPSC previous year question papers in one place: Group 1 Prelims 2024 and Group 2 Prelims 2024 & Mains 2025, '
           '{n} questions with final-key answers and explanations in English and Telugu. Practise them online with answers and explanations: 3 days free, then one ₹45 PYQ Pass for every exam.',
      h1='APPSC previous year question papers with answers',
      lede="Every APPSC Group 1 and Group 2 previous question paper on Learn with Anil, {n} questions in all. "
           "Answers come from APPSC's official final keys, and every question has a short explanation, in English and Telugu.",
      intro='<p>Looking for AP Group 2 or AP Group 1 previous papers, APPSC old question papers with the key, or an APPSC mock test? '
            'They are all here: open a paper to see its questions, or practise it online with answers and explanations.</p>'
            '<p lang="te">APPSC గ్రూప్ 1, గ్రూప్ 2 మునుపటి సంవత్సరం ప్రశ్నపత్రాలు (పాత ప్రశ్నాపత్రాలు) అధికారిక ఫైనల్ కీ సమాధానాలు, వివరణలతో — ప్రాక్టీస్ క్విజ్‌లు, మాక్ టెస్ట్‌లు; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.</p>'
            '<p class="note">New: <a href="/appsc-group-2-notification-2026.html">APPSC Group 2 Notification 2026</a> (686 posts, apply 10–30 November) and '
            '<a href="/appsc-group-1-notification-2026.html">APPSC Group 1 Notification 2026</a> (166 posts). Timed mock tests: '
            '<a href="/appsc-group-2/mock-test.html">Group 2</a> · <a href="/appsc-group-1/mock-test.html">Group 1</a>.</p>',
      te={'Group-I': 'APPSC గ్రూప్-1 ప్రశ్నాపత్రాలు', 'Group-II': 'APPSC గ్రూప్-2 ప్రశ్నాపత్రాలు'},
      order=lambda c: c['short']),   # Group-I first, then Group-II
  'ts-police-pyqs.html': dict(
      board='TSLPRB', ename='TS Police', crumb='TS Police PYQs',
      title='TS Police Previous Question Papers with Answers – SI & Constable PYQs (TSLPRB / TGPRB), English & Telugu | Learn with Anil',
      desc='Telangana Police SI and Constable previous question papers in one place: the TSLPRB Preliminary Written Test 2022 and Final Written Examination 2023 papers, '
           '{n} questions with final-key answers and explanations in English and Telugu. Practise them online with answers and explanations: 3 days free, then one ₹45 PYQ Pass for every exam.',
      h1='TS Police SI & Constable previous question papers with answers',
      lede="Every Telangana Police SI and Constable question paper on Learn with Anil, {n} questions in all. "
           "Answers come from TSLPRB's final key, and every question has a short explanation, in English and Telugu.",
      intro='<p>Looking for TS Police SI previous papers, the TS SI or Constable mains 2023 question paper, the TS Constable question paper 2022, TSLPRB / TGPRB previous question papers with answers, '
            'or a Telangana police mock test? They are all here: open a paper to see its questions, or practise it online with answers and explanations.</p>'
            '<p lang="te">తెలంగాణ పోలీస్ ఎస్ఐ, కానిస్టేబుల్ పాత ప్రశ్నాపత్రాలు (మునుపటి ప్రశ్నపత్రాలు) TSLPRB ఫైనల్ కీ సమాధానాలు, తెలుగులో వివరణలతో — ప్రాక్టీస్ క్విజ్‌లు, మాక్ టెస్ట్‌లు; రిజిస్టర్ చేసుకుంటే 3 రోజులు ఉచితం.</p>'
            '<p class="note">2026 prelims are tentatively on 29 November (SI) and 20 December (Constable). Full mock tests with a timer: '
            '<a href="/ts-police-si/mock-test.html">TS Police SI mock test</a> · <a href="/ts-police-constable/mock-test.html">TS Police Constable mock test</a>.</p>',
      te={'TS Police SI': 'తెలంగాణ పోలీస్ ఎస్ఐ ప్రశ్నాపత్రాలు', 'TS Constable': 'తెలంగాణ పోలీస్ కానిస్టేబుల్ ప్రశ్నాపత్రాలు'},
      order=lambda c: 0 if c['id'] == 'ts-police-si' else 1),
}


def landing_page(loaded, rel):
    """One crawlable page listing every paper and subject page of one recruiting board (APPSC, TSLPRB)."""
    L = LANDINGS[rel]
    loaded = sorted([x for x in loaded if x[0]['board'] == L['board']], key=lambda x: L['order'](x[0]))
    n = f'{sum(len(x[2]) for x in loaded):,}'
    can = f'{SITE_URL}/{rel}'
    secs = []
    for conf, papers, questions in loaded:
        base = conf['dir'] + '/' if conf['dir'] else ''
        subj = {s[0]: s for s in conf['subjects']}
        scount = {}
        for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
        rows = ''.join(
            f'<li class="q"><div class="meta">{esc(p["held"])} · {esc(p["notif"])} · {p["count"]} questions · '
            f'{"all four options" if p["fmt"] == "mcq" else "answer-only key"}</div>'
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
    base = conf['dir'] + '/' if conf['dir'] else ''
    subj = {x[0]: x for x in conf['subjects']}
    scount = {}
    for q in questions: scount[q['s']] = scount.get(q['s'], 0) + 1
    rows = ''.join(
        f'<li class="q"><div class="meta">{esc(p["held"])} · {p["count"]} questions · {"timed mock test available" if p["fmt"] == "mcq" else "answer-only key (quick-recall cards)"}</div>'
        f'<p><a href="/{base}papers/{p["slug"]}.html">{esc(paper_kw(conf, p))} question paper with answers</a>'
        + (f' · <a href="{conf["pb"]}?test={p["id"]}">Take it as a timed mock test</a>' if p['fmt'] == 'mcq' else '') + '</p></li>'
        for p in sorted(papers, key=lambda p: (-p['year'], p['id'])))
    subs = ''.join(f'<a href="/{base}subjects/{conf["slugp"]}-{subj[x][2]}-pyqs.html">{esc(subj[x][1])} ({scount[x]})</a>' for x in subj if scount.get(x))
    return (f'<ol class="qs">{rows}</ol><h3>{esc(conf["seo"])} previous questions by subject</h3><nav class="toc">{subs}</nav>'
            f'<p><a class="cta" href="{conf["pb"]}mock-test.html">Free {esc(conf["seo"])} mock tests</a><a class="cta alt" href="{conf["pb"]}">Practise topic-wise</a></p>')


NOTIFS = {
  'appsc-group-2-notification-2026.html': dict(
    exam='appsc-group-2', crumb='Group 2 Notification 2026',
    title='APPSC Group 2 Notification 2026 – 686 Posts, Apply 10–30 November, Exam Pattern & Previous Papers | Learn with Anil',
    desc='APPSC Group 2 Notification 2026 (No. 37/2026): 686 posts including 200 Deputy Tahsildar and 176 Deputy MPDO posts, online applications '
         'from 10 to 30 November 2026, the screening test and mains pattern, and APPSC Group 2 previous year question papers with answers.',
    h1='APPSC Group 2 Notification 2026: 686 posts',
    lede='APPSC issued a brief notification (No. 37/2026) on 13 October 2026 for 686 Group-II posts, Executive and Non-Executive. '
         'Online applications run from 10 to 30 November 2026. Here are the posts, the dates, the exam pattern, and the Group 2 previous papers to start practising now.',
    te='APPSC గ్రూప్ 2 నోటిఫికేషన్ 2026 (నం. 37/2026): 686 పోస్టులు — ఆన్‌లైన్ దరఖాస్తులు నవంబర్ 10 నుంచి 30 వరకు. పరీక్ష విధానం, పాత ప్రశ్నాపత్రాలు సమాధానాలతో.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Group_II_372026.pdf', pdfname='APPSC brief notification No. 37/2026, dated 13 October 2026',
    sections=[
      ('Important dates', 'table', [
        ('Brief notification (No. 37/2026)', '13 October 2026'),
        ('Detailed notification', 'Expected by 10 November 2026: age limits, fee and reservations'),
        ('Online applications', '10 November to 30 November 2026 (till 11:59 pm)'),
        ('Screening test (prelims)', 'Date not announced yet'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts and vacancies', 'table+', (['Post', 'Vacancies'], [
        ('Municipal Commissioner Grade-III', 6), ('Sub-Registrar Grade-II', 7), ('Deputy Tahsildar', 200),
        ('Goods and Services Tax Officer (erstwhile ACTO)', 40), ('Assistant Registrar of Co-operative Societies', 10),
        ('Deputy Mandal Parishad Development Officer', 176), ('Prohibition and Excise Sub-Inspector', 29),
        ('Assistant Section Officer (GAD)', 71), ('Assistant Section Officer (Finance)', 5), ('Assistant Section Officer (Law)', 4),
        ('Senior Accountant (HODs)', 90), ('Junior Accountant (HODs)', 48), ('Total', 686)])),
      ('Who can apply', 'p', 'A bachelor\'s degree from a recognised university. Some posts need a particular degree: Assistant Section Officer (Finance) a degree in '
                          'mathematics, economics or commerce; Assistant Section Officer (Law) a law degree; Senior and Junior Accountant a degree in commerce, '
                          'economics or mathematics plus a computer qualification. Age limits, relaxations and the fee are given in the detailed notification.'),
      ('Exam pattern', 'table+', (['Stage', 'What it covers', 'Questions · marks · time'], [
        ('Screening test (objective, OMR)', 'Indian History, Geography, Indian Society, Current Affairs and Mental Ability, 30 marks each', '150 · 150 · 150 min'),
        ('Mains Paper I (objective)', 'Social and cultural history of Andhra Pradesh; general overview of the Indian Constitution', '150 · 150 · 150 min'),
        ('Mains Paper II (objective)', 'Indian and Andhra Pradesh economy; science and technology', '150 · 150 · 150 min'),
        ('Computer Proficiency Test', 'Qualifying test for the posts that need it, then document verification', '—')])),
      ('', 'note', 'The screening test only shortlists candidates for the Mains; selection is on the Mains marks. The pattern is the same as in the previous '
                   'Group-II recruitment (Notification 11/2023), so the 2024 Screening Test and the 2025 Mains papers below are the closest practice you can get.'),
    ]),
  'appsc-group-1-notification-2026.html': dict(
    exam='appsc-group-1', crumb='Group 1 Notification 2026',
    title='APPSC Group 1 Notification 2026 – 166 Posts, Last Date 27 October, Prelims Pattern & Previous Papers | Learn with Anil',
    desc='APPSC Group 1 Notification 2026 (No. 07/2026): 166 posts including Deputy Collector, DSP and Divisional Development Officer, applications till 27 October 2026, '
         'screening test tentatively on 24 January 2027, prelims and mains pattern, and APPSC Group 1 previous year question papers with answers.',
    h1='APPSC Group 1 Notification 2026: 166 posts',
    lede='APPSC Notification No. 07/2026 is for 166 Group-I Services posts, from Deputy Collector and DSP to Divisional Development Officer. '
         'Online applications close on 27 October 2026, and the screening test is tentatively on 24 January 2027. Here are the dates, the posts, the exam pattern, and the Group 1 previous papers to practise.',
    te='APPSC గ్రూప్ 1 నోటిఫికేషన్ 2026 (నం. 07/2026): 166 పోస్టులు — దరఖాస్తుకు చివరి తేదీ అక్టోబర్ 27, ప్రిలిమ్స్ (స్క్రీనింగ్ టెస్ట్) తాత్కాలికంగా 2027 జనవరి 24. పరీక్ష విధానం, పాత ప్రశ్నాపత్రాలు సమాధానాలతో.',
    pdf='https://psc.ap.gov.in/Documents/NotificationDocuments/Group_I_07_2026.pdf', pdfname='APPSC Notification No. 07/2026 (Group-I Services)',
    sections=[
      ('Important dates', 'table', [
        ('Notification (No. 07/2026)', '6 October 2026'),
        ('Online applications', '6 October to 27 October 2026 (till 11:59 pm)'),
        ('Screening test (prelims)', 'Tentatively 24 January 2027'),
        ('Mains and interview', 'To be announced'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts', 'list', ['Deputy Collector (A.P. Civil Service, Executive Branch)', 'Assistant Commissioner of State Tax', 'Deputy Superintendent of Police (Civil)',
                         'Deputy Superintendent of Jails (Men)', 'Divisional / District Fire Officer', 'Regional Transport Officer', 'District Tribal Welfare Officer',
                         'Deputy Registrar of Co-operative Societies', 'Municipal Commissioner Grade-II', 'Assistant Treasury Officer / Assistant Accounts Officer',
                         'District Employment Officer', 'Divisional Development Officer', 'Assistant Audit Officer']),
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
}


def notif_page(loaded, rel):
    N = NOTIFS[rel]
    conf, papers, questions = next(x for x in loaded if x[0]['id'] == N['exam'])
    can = f'{SITE_URL}/{rel}'
    body = [f'<p lang="te" style="margin:0 0 6px">{esc(N["te"])}</p>',
            f'<a class="cta" href="{conf["pb"]}mock-test.html">Free {esc(conf["seo"])} mock test</a><a class="cta alt" href="{conf["pb"]}papers/">All {esc(conf["seo"])} previous papers</a>']
    for head, kind, data in N['sections']:
        if head: body.append(f'<h2>{esc(head)}</h2>')
        if kind == 'table': body.append(facts_table(data))
        elif kind == 'table+': body.append(facts_table(data[1], data[0]))
        elif kind == 'list': body.append('<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in data) + '</ul>')
        elif kind == 'note': body.append(f'<p class="note">{esc(data)}</p>')
        else: body.append(f'<p>{esc(data)}</p>')
    body.append(f'<h2>Start with the previous papers</h2><p>Every {esc(conf["name"])} paper on this site comes with the answers from APPSC\'s final key and a short '
                f'explanation in English and Telugu. Practise a paper online or take it as a timed mock test.</p>' + practice_links(conf, papers, questions))
    body.append(f'<p class="note">Source: <a href="{N["pdf"]}" rel="nofollow">{esc(N["pdfname"])}</a>. Dates and vacancies can change with corrigenda; '
                f'always check the official website psc.ap.gov.in before applying. Learn with Anil is not connected with APPSC.</p>')
    return static_page(0, N['title'], N['desc'], can, N['h1'], esc(N['lede']), ''.join(body),
                       [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + conf['pb']), (N['crumb'], can)], conf, at_root=True)


# ---------- paid passes: Instamojo checkout through the Learn with Anil payments script (Google Apps Script) ----------
PAY = dict(
    on=False,   # True once Instamojo payments work end to end: attempting tests then needs a pass. Until then everything stays free.
    api='https://script.google.com/macros/s/AKfycbxgNi2CfnbaEsVpA1Ghgy0AdYdUG7eYBkol5zqcbMgA2Q4D0Pvy0rndLxeyE7MlPy_3Rg/exec',   # the payments script (Apps Script web app, deployed 23 Oct 2026)
    pyq_price=45,
    exams='',   # names of every live exam, for the pay dialog ("one payment for the whole website"); set in main()
)
PYQ_VALID = 'valid for 12 months from the day you pay, on every exam'
TRIAL_DAYS = 3
SAMPLE_N = 10        # public paper / question pages show the answers of the first SAMPLE_N questions of each paper; the rest need the pass or trial
PUBLIC_PDFS = False  # Anil, 23 Oct 2026: no free PDF downloads (tools/pdfs.py makes nothing while this is False)
if os.environ.get('PAY_TEST'):   # test builds only (test/pay_test.py): payments on, against a fake script address
    PAY.update(on=True, api='https://pay.test/exec')
BB_URL = ''   # the Bahubali Test Series page (APPSC Group 2 Mains), set by main() once its tests are sealed
# when an exam's passes run out (the day after the exam); None = 12 months from purchase
PASS_UNTIL = {'ts-police-si': ('2026-11-30', 'TS Police SI Prelims on 29 November 2026'),
              'ts-police-constable': ('2026-12-21', 'TS Police Constable Prelims on 20 December 2026'),
              'appsc-group-1': ('2027-01-25', 'APPSC Group 1 screening test on 24 January 2027')}
# mock-test packs on sale (Anil sets the price per exam)
MOCK_PACKS = {
  'ts-police-si': dict(id='mk-si', name='Mission Khaki', price=150, n=10, live=1, qn=200,   # live = mocks released so far (rest: coming soon)
                       title='Mission Khaki – TS Police SI Prelims 2026 Test Series',
                       summary='10 full-length TS SI Prelims mock tests, 200 questions each (Arithmetic & Reasoning 100, General Studies 100), '
                               'in English and Telugu, with an explanation for every answer. Each mock\'s sections can also be taken on their own as sectional tests.',
                       sections=['Arithmetic', 'Reasoning & Mental Ability', 'General Studies']),
}


EXAM_CLOCK = {   # exam id: (exam name, date or None, where the date comes from) — the countdown under the exam tiles
  'appsc-group-2': ('APPSC Group 2 Screening Test', None, 'Applications 10–30 November 2026 (Notification 37/2026); APPSC has not announced the exam date yet.'),
  'appsc-group-1': ('APPSC Group 1 Screening Test', '2027-01-24', 'APPSC Notification 07/2026.'),
  'ts-police-si': ('TS Police SI Preliminary Written Test', '2026-11-29', 'Tentative, TGPRB press note of 17 September 2026.'),
  'ts-police-constable': ('TS Police Constable Preliminary Written Test', '2026-12-20', 'Tentative, TGPRB press note of 17 September 2026.'),
  'upsc-capf': ('UPSC CAPF (Assistant Commandants) 2027', '2027-07-04', 'UPSC Calendar 2027.'),
  'upsc-epfo': ('UPSC EPFO APFC / EO-AO Recruitment Test', None, 'UPSC holds this test only when EPFO posts are advertised; no new advertisement yet.'),
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
    a, n = mk['live'], mk['n']
    if a >= n: return f'All {n} mocks are available now.'
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
    return dict(on=PAY['on'], api=PAY['api'], exam=conf['id'],
                pyq=dict(price=PAY['pyq_price'], valid=PYQ_VALID, exams=PAY['exams'], trial=TRIAL_DAYS),
                mock=(dict(id=mk['id'], name=mk['name'], title=mk['title'], price=mk['price'], n=mk['n'], live=mk['live'],
                           valid=pass_until_text(conf)[0].upper() + pass_until_text(conf)[1:]) if mk else None),
                pages=dict(pyq=pb + 'pyqs.html', mock=pb + 'mock-test.html', sec=pb + 'sectional-tests.html'))


def tiles_html(conf, papers, questions, extra_links):
    """The three tiles on an exam's home page (PYQs, mock tests, sectional tests), each opening its own page, plus link tiles."""
    pb, mk = conf['pb'], MOCK_PACKS.get(conf['id'])
    n = len(questions)
    nsub = len({q['s'] for q in questions})
    t1 = (f'<a class="etile" href="{pb}pyqs.html"><span class="etile-k">01 · Previous papers</span><b>PYQs with answers</b>'
          f'<span class="etile-p">{n:,} questions from {len(papers)} official paper{"s" if len(papers) > 1 else ""}, with answers and explanations, as quizzes and timed tests. '
          f'3 days free when you register.</span><span class="etile-price">₹{PAY["pyq_price"]} · all exams · 12 months</span></a>')
    if mk:
        t2 = (f'<a class="etile" href="{pb}mock-test.html"><span class="etile-k">02 · Mock tests</span><b>{esc(mk["name"])} test series</b>'
              f'<span class="etile-p">{mk["n"]} full-length mocks, {mk["qn"]} questions each, English &amp; Telugu, with explanations. {live_text(mk)}.</span>'
              f'<span class="etile-price">₹{mk["price"]} · mock tests only</span></a>')
    elif BB_URL and conf['id'] == 'appsc-group-2':
        t2 = (f'<a class="etile" href="{BB_URL}"><span class="etile-k">02 · Mock tests</span><b>Bahubali Test Series</b>'
              f'<span class="etile-p">24 full-length Group-II Mains mocks, 12 for Paper I and 12 for Paper II: 150 questions each, English and Telugu, with explanations.</span>'
              f'<span class="etile-price">₹250 for all 24 tests</span></a>')
    else:
        t2 = (f'<a class="etile" href="{pb}mock-test.html"><span class="etile-k">02 · Mock tests</span><b>Mock test pack</b>'
              f'<span class="etile-p">Full-length mock tests in the exam pattern. Until the pack opens, take the real previous papers as timed mocks.</span>'
              f'<span class="etile-price">Upcoming</span></a>')
    t3 = (f'<a class="etile" href="{pb}sectional-tests.html"><span class="etile-k">03 · Sectional tests</span><b>Subject-wise tests</b>'
          f'<span class="etile-p">PYQ sectionals in {nsub} subjects{", plus sectional mocks from " + esc(mk["name"]) if mk else ""}. '
          f'Practise one section at a time with a timer.</span><span class="etile-price">{"With the PYQ Pass or " + esc(mk["name"]) if mk else "With the PYQ Pass"}</span></a>')
    links = ''.join(f'<a class="etile etile-sm" href="{h}"><b>{esc(x)}</b><span class="etile-go">→</span></a>' for x, h in extra_links)
    note = ''
    return (f'<section class="wrap section"><div class="etiles">{t1}{t2}{t3}</div>' + exam_clock_html(conf)
            + (f'<div class="etiles etiles-links">{links}</div>' if links else '') + note + '</section>')


def buy_box(conf, kind):
    """A price box with a buy button that opens the checkout inside the app."""
    pb = conf['pb']
    if kind == 'pyq':
        price, name = PAY['pyq_price'], 'PYQ Pass · all exams'
        what = (f'<b>One payment of ₹{PAY["pyq_price"]} for the whole website:</b> the previous papers of every exam on Learn with Anil '
                f'({esc(PAY["exams"])}) and every exam added later, not just {esc(conf["seo"])}. Every answer and explanation, practice quizzes and timed tests, '
                f'PYQ sectionals, topic-wise quizzes, Smart Quiz and your Mistakes notebook. New here? Register once and get {TRIAL_DAYS} days free.')
        valid = PYQ_VALID
    else:
        mk = MOCK_PACKS[conf['id']]
        price, name = mk['price'], mk['title']
        what = esc(mk['summary']) + f' Mock tests only: previous papers need the PYQ Pass (₹{PAY["pyq_price"]}, all exams), bought separately.'
        valid = pass_until_text(conf)
    status = ''
    return (f'<div class="buy"><div><b>{esc(name)}</b><p>{what}</p><p class="muted">₹{price} · {valid} · pay by UPI, card or net banking (Instamojo)</p></div>'
            f'<a class="cta" href="{pb}?buy={kind}">Get it for ₹{price}</a></div>{status}')


def plans_html(conf):
    """Every plan in one table, so there is no doubt about what is free and what is paid."""
    mk = MOCK_PACKS.get(conf['id'])
    rows = [('Free trial', '₹0, once per phone number', f'Every previous paper of every exam on the site, with answers and explanations, practice quizzes, timed tests and all study tools', f'{TRIAL_DAYS} days from registration'),
            ('PYQ Pass', f'₹{PAY["pyq_price"]}', f'Every previous paper of every exam on the site ({esc(PAY["exams"])}) and every exam added later: answers and explanations, practice quizzes, timed tests, PYQ sectionals and all study tools', '12 months from payment')]
    if mk:
        rows.append((esc(mk['name']), f'₹{mk["price"]}', f'{mk["n"]} full-length {esc(conf["seo"])} mock tests and their sectional tests, with explanations, and the study tools for your mock results. Previous papers are not included (that is the PYQ Pass).',
                     esc(pass_until_text(conf)[0].upper() + pass_until_text(conf)[1:])))
    return ('<table class="facts plans"><tr><th style="width:17%">Plan</th><th style="width:17%">Price</th><th>What you get</th><th style="width:19%">Valid</th></tr>'
            + ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows) + '</table>'
            f'<p>Open to everyone without a plan: the question of the day, and the answers to the first {SAMPLE_N} questions of each paper on the paper pages. '
            'Plans are linked to the phone number and email you register with, on up to 3 devices; pay with the same details.</p>')


TOOLS_NOTE = 'Included with every plan: the free trial, the PYQ Pass and mock-test packs such as Mission Khaki.'


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


def pyq_page(conf, papers, questions):
    """Tile 1: PYQs — a free sample on the public pages; everything with the free trial or the PYQ Pass (all exams)."""
    pb, seo, l2 = conf['pb'], conf['seo'], conf['l2']
    rel = pb.strip('/') + '/pyqs.html'
    can = SITE_URL + '/' + rel
    base = '/' + (conf['dir'] + '/' if conf['dir'] else '')
    ps = sorted(papers, key=lambda p: (-p['year'], p['id']))
    title = f'{seo} PYQs with Answers – Previous Papers as Quizzes & Timed Tests, 3 Days Free | Learn with Anil'
    desc = (f'{seo} previous year questions (PYQs): {len(questions):,} questions from {len(papers)} official papers with answers and explanations in English and {l2["name"]}, '
            f'as practice quizzes and timed tests. 3 days free when you register, then one ₹{PAY["pyq_price"]} PYQ Pass for every exam on the site.')
    rows = ''.join(
        f'<li class="q"><div class="meta">{esc(p["held"])} · {p["count"]} questions</div><p>{esc(paper_kw(conf, p))}{f" ({esc(paper_alt(conf, p))})" if paper_alt(conf, p) else ""}</p>'
        f'<a class="cta alt" href="{pb}?practice={p["id"]}">Practise question by question</a>'
        + (f'<a class="cta" href="{pb}?test={p["id"]}">Attempt as a timed test</a>' if p['fmt'] == 'mcq' else '') + '</li>' for p in ps)
    body = (buy_box(conf, 'pyq') + '<h2>Previous papers</h2><ol class="qs">' + rows + '</ol>'
            + '<h2>Practise by subject and topic</h2><p>With the PYQ Pass or the free trial: pick a subject to build a quiz from every paper, or build your own topic-wise quiz.</p>'
            + subjects_html(conf, questions) + features_html(pb, ('practice',))
            + f'<h2>Study tools</h2><p>{TOOLS_NOTE}</p>' + features_html(pb, ('mistakes', 'smart', 'heatmap', 'bookmarks'))
            + '<h2>Plans</h2>' + plans_html(conf)
            + f'<p><a class="cta alt" href="{pb}mock-test.html">Mock tests</a><a class="cta alt" href="{pb}sectional-tests.html">Sectional tests</a></p>')
    lede = esc(f'Every {seo} previous paper on Learn with Anil, with official answers and explanations, as practice quizzes and timed tests. '
               f'{TRIAL_DAYS} days free when you register; then one ₹{PAY["pyq_price"]} PYQ Pass opens every exam on the site for 12 months.')
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
    secrows = (''.join((f'<li class="q"><div class="meta">Available now</div><p>Mock {i + 1} sections</p>'
                        + ''.join(f'<a class="cta alt" href="{pb}?mock={mk["id"]}-{i + 1}&amp;part={k}">{v}</a>' for k, v in (('ari', 'Arithmetic'), ('rea', 'Reasoning'), ('gs', 'General Studies')))
                        + '</li>') if i < mk['live'] else f'<li class="q"><div class="meta">Coming soon</div><p>Mock {i + 1} sections</p></li>'
                       for i in range(mk['n'])) if mk else '')
    mock_part = (f'<h2>{esc(mk["name"])} sectional mocks</h2><ol class="qs">{secrows}</ol><p>Each {esc(mk["name"])} mock\'s sections — '
                 + ', '.join(esc(x) for x in mk['sections']) + ' — open as separate timed tests as the mocks are released '
                 f'({live_text(mk)}). They come with the {esc(mk["name"])} pack.</p>' + buy_box(conf, 'mock')
                 if mk else '<h2>Sectional mocks</h2><p>Sectional mocks open with this exam\'s mock test pack. Its price will be announced soon.</p>')
    body = ('<h2>PYQ sectionals</h2><p>Each test has every real previous question from one subject, in one go, with a timer. With the PYQ Pass or the free trial.</p>'
            '<ol class="qs">' + rows + '</ol>' + buy_box(conf, 'pyq') + mock_part + '<h2>Plans</h2>' + plans_html(conf))
    lede = esc(f'Practise {seo} one section at a time: timed tests from real previous questions in every subject'
               + (f', and sectional mocks from {mk["name"]}.' if mk else '.'))
    return rel, static_page(0 if conf['dir'] else 1, title, desc, can, f'{seo} sectional tests', lede, body,
                            [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), ('Sectional tests', can)], conf)


MOCK_INFO = {}   # exam dates removed at Anil's request (23 Oct 2026): no exam dates on the site


def mock_page(conf, papers, questions):
    """Tile 2: mock tests — the exam's mock-test pack (if on sale) and the real previous papers as full timed tests."""
    pb, seo = conf['pb'], conf['seo']
    rel = pb.strip('/') + '/mock-test.html'
    can = SITE_URL + '/' + rel
    mcq = [p for p in sorted(papers, key=lambda p: (-p['year'], p['id'])) if p['fmt'] == 'mcq']
    l2 = conf['l2']
    mk = MOCK_PACKS.get(conf['id'])
    title = (f'{seo} Mock Test – {mk["name"]} Test Series (₹{mk["price"]}) & Previous Papers with Timer | Learn with Anil' if mk else
             f'{seo} Mock Test – Full Previous Papers with Timer, English & {l2["name"]} | Learn with Anil')
    desc = ((f'{mk["title"]}: {mk["summary"]} ₹{mk["price"]}. ' if mk else f'{seo} mock tests online: ')
            + f'take the real {", ".join(paper_kw(conf, p).replace(seo + " ", "") for p in mcq)} question paper{"s" if len(mcq) > 1 else ""} as timed tests, '
            f'in English and {l2["name"]}, with your score, official answers and an explanation for every question.')
    rows = ''.join(
        f'<li class="q"><div class="meta">{esc(p["held"])} · {p["count"]} questions · about {round(p["count"] / 60 * 4) / 4:g} hours</div>'
        f'<p>{esc(paper_kw(conf, p))}{f" ({esc(paper_alt(conf, p))})" if paper_alt(conf, p) else ""}</p>'
        f'<p style="font-weight:400">{esc(p["blurb"])}</p>'
        f'<a class="cta" href="{pb}?test={p["id"]}">Start the mock test</a><a class="cta alt" href="/{conf["dir"] + "/" if conf["dir"] else ""}papers/{p["slug"]}.html">Read it with answers</a></li>'
        for p in mcq)
    info = MOCK_INFO.get(conf['id'], '')
    if mk:
        mid = lambda i: f'{mk["id"]}-{i + 1}'
        sched = ''.join((f'<tr><td>Mock {i + 1}</td><td>Available now</td><td>{mk["qn"]} questions · <a href="{pb}?mock={mid(i)}">Start</a></td>'
                         f'<td><a href="{pb}?mock={mid(i)}&amp;part=ari">Arithmetic</a> · <a href="{pb}?mock={mid(i)}&amp;part=rea">Reasoning</a> · '
                         f'<a href="{pb}?mock={mid(i)}&amp;part=gs">General Studies</a></td></tr>') if i < mk['live'] else
                        f'<tr><td>Mock {i + 1}</td><td>Coming soon</td><td>{mk["qn"]} questions</td><td>Arithmetic · Reasoning · General Studies</td></tr>'
                        for i in range(mk['n']))
        pack = (f'<h2>{esc(mk["title"])}</h2>' + buy_box(conf, 'mock')
                + f'<table class="facts"><tr><th>Mock</th><th>Status</th><th>Full mock</th><th>Sectional tests</th></tr>{sched}</table>'
                '<ul><li>Fresh questions written for this series in the TS SI Prelims pattern, not copied from coaching material: Arithmetic &amp; Reasoning (100) and General Studies (100), in English and Telugu.</li>'
                '<li>Every question has an explanation in English and Telugu. Your score, accuracy and topic-wise analysis come after each mock.</li>'
                '<li>Each mock\'s sections can also be taken on their own as sectional tests.</li></ul>')
    elif BB_URL and conf['id'] == 'appsc-group-2':
        pack = (f'<h2>Bahubali Test Series</h2><p>24 full-length APPSC Group-II Mains mock tests, 12 for Paper I and 12 for Paper II: 150 questions each, '
                f'English and Telugu, with explanations and PDFs. ₹250 for the whole series.</p><p><a class="cta" href="{BB_URL}">See the Bahubali tests</a></p>')
    else:
        pack = '<h2>Mock test pack</h2><p>Full-length mock tests for this exam are being prepared; the price will be announced soon. Until then, take the real previous papers below as timed mocks.</p>'
    body = (pack + (f'<p class="note">{esc(info)}</p>' if info else '')
            + '<h2>Real previous papers as mock tests</h2><ol class="qs">' + rows + '</ol>'
            + '<h2>How the mock test works</h2><ul>'
            f'<li>Questions appear in English and {esc(l2["name"])} as printed. Switch language with the buttons at the top.</li>'
            '<li>The timer gives you one minute per question. You can move between questions and change answers until you submit.</li>'
            '<li>When you finish you get your score, accuracy and a topic-wise analysis, with the correct answer and an explanation for every question. Wrong answers go to your Mistakes notebook.</li>'
            f'<li>Previous papers as tests need the PYQ Pass (₹{PAY["pyq_price"]} for every exam on the site, 12 months) or your {TRIAL_DAYS}-day free trial{"; " + esc(mk["name"]) + " is separate" if mk else ""}. Register once with your phone number and use the same number when you pay.</li></ul>'
            + f'<h2>Study tools after every test</h2><p>{TOOLS_NOTE}</p>' + features_html(pb, ('mistakes', 'smart', 'heatmap', 'bookmarks'))
            + '<h2>Plans</h2>' + plans_html(conf)
            + f'<p><a class="cta alt" href="{pb}sectional-tests.html">Sectional tests</a><a class="cta alt" href="{pb}pyqs.html">All {esc(seo)} PYQs</a></p>')
    lede = esc((f'{mk["title"]}, plus every real {seo} previous paper as a timed mock test.') if mk else
               f'Take a real {seo} previous paper as a full mock test with a timer, then see your score and an explanation for every answer.')
    return rel, static_page(0 if conf['dir'] else 1, title, desc, can, f'{seo} mock tests', lede, body,
                            [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), ('Mock test', can)], conf)


def build_static(conf, papers, subjects, questions, subj):
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
        fmt = (f'All four options with the answer from {pkey}' if p['fmt'] == 'mcq'
               else f'Each question with its official answer from {conf["keyname"]} (the key lists the correct answer only)')
        kw, alt = paper_kw(conf, p), paper_alt(conf, p)
        if conf['board'] == 'UPSC':
            title = f'{kw} Question Paper with Answer Key, English & Hindi | Learn with Anil'
        else:
            title = f'{kw} Question Paper with Answers{f" ({alt})" if alt else ""} – Final Key, {"English" if p.get("en_only") else "Telugu & English"} | Learn with Anil'
        kdesc = ("answers from APPSC's final key" if conf['board'] == 'APPSC' else 'compiled answers' if p.get('key', '').startswith('answers compiled')
                 else f'answers from {pkey}')
        desc = (f'{kw} question paper{f" ({alt})" if alt else ""}, held {p["held"]}: all {len(qs)} questions in {"English" if p.get("en_only") else "English and " + conf["l2"]["name"]} '
                f'with {kdesc} and explanations. Practise it online as a quiz or a timed mock test: {TRIAL_DAYS} days free when you register.'
                + (f' {conf["aka_short"]}.' if conf.get('aka_short') else ''))
        subs = {}
        for q in qs: subs.setdefault(q['s'], 0); subs[q['s']] += 1
        toc = '<nav class="toc">' + ''.join(
            f'<a href="../subjects/{slugp}-{subj[s][2]}-pyqs.html">{esc(subj[s][1])} ({c})</a>' for s, c in subs.items()) + '</nav>'
        body = (f'<p lang="{conf["l2"]["code"]}" style="margin:0 0 6px">{esc(paper_kw_l2(conf, p))}</p>'
                f'<a class="cta" href="{conf["pb"]}?practice={p["id"]}">Practise this paper online</a>'
                + (f'<a class="cta alt" href="{conf["pb"]}?test={p["id"]}">Take it as a timed test</a>' if p['fmt'] == 'mcq' else '') +
                f'<a class="cta alt" href="{conf["pb"]}practice/">Make a topic-wise quiz</a>'
                f'<p class="note">The answers and explanations of the first {min(SAMPLE_N, len(qs))} questions are free on this page. For all {len(qs)}, practise the paper in the app: '
                f'{TRIAL_DAYS} days free when you register, then one ₹{PAY["pyq_price"]} PYQ Pass for every exam on the site.</p>'
                f'<h2>Subjects in this paper</h2>{toc}<h2>All {len(qs)} questions</h2><ol class="qs">'
                + ''.join(q_html(q, p['short'], f'Q{q["n"]}', subj, conf['l2'], f'{conf["pb"]}q/{q["id"]}.html', unl(q)) for q in qs) + '</ol>')
        held = f'{p["notif"]}, held on {p["held"]}' if conf['board'] == 'APPSC' else f'Held on {p["held"]} ({p["notif"].replace(" · ", ", ")})'
        lede = esc(f'{p["title"]}{f" ({alt_shown(alt, p['title'])})" if alt_shown(alt, p['title']) else ""}. {p["blurb"]} {held}. {fmt}, plus a short explanation for every question (the first {SAMPLE_N} here, all of them in the app). '
                   + ('' if p.get('en_only') else f'Each question is shown in English and {conf["l2"]["name"]}, as printed in the booklet.'))
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
                f'topic-wise, with answers, explanations and {conf["l2"]["name"]} text. Practise them as a quiz or a timed test: {TRIAL_DAYS} days free when you register.')
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


def question_pages(conf, papers, questions, subj):
    """One crawlable page per question (q/<id>.html in the exam's folder): question, options, answer, explanation, both languages."""
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
                    f'Answer from {p.get("key") or conf["keyname"]}, with explanation, in English and {l2["name"]}.')
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
                       + ('Try it first, then check your answer and the explanation in the practice app.' if locked else 'Try it first, then open the answer and explanation.'))
            crumbs = [('Home', SITE_URL + '/'), (conf['name'], SITE_URL + pb), (p['title'], SITE_URL + paper_url), (f'Q{q["n"]}', can)]
            pages[rel] = static_page(depth, title, desc, can, f'{kw} · Question {q["n"]}', lede, body, crumbs, conf)
    return pages


def not_found_page():
    """GitHub Pages serves this for any unknown address. Practice-app links such as /upsc-capf/q/c2026a-3/ are sent to the app."""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found | Learn with Anil</title><meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<script>
(function(){
  var p = location.pathname, bases = ["/appsc-group-2/", "/appsc-group-1/", "/upsc-capf/", "/upsc-epfo/", "/ts-police-si/", "/ts-police-constable/", "/tgpsc-hmwssb-manager/"], base = "/";
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
<li><a href="/appsc-group-1/">APPSC Group-I PYQs</a></li><li><a href="/upsc-capf/">UPSC CAPF (AC) PYQs</a></li><li><a href="/upsc-epfo/">UPSC EPFO APFC PYQs</a></li>
<li><a href="/ts-police-si/">TS Police SI PYQs</a></li><li><a href="/ts-police-constable/">TS Police Constable PYQs</a></li><li><a href="/appsc-pyqs.html">All APPSC previous question papers</a></li>
<li><a href="/ts-police-pyqs.html">All TS Police previous question papers</a></li></ul>
</main></body></html>
"""


if __name__ == '__main__':
    main()
