"""NCERT Class 11 and Class 12: chapter-wise MCQs written by Learn with Anil (Anil, 16 Nov 2026: "create a ncert tile and....in
that 11th and 12th class", "subject wise & chapter wise", "i just these questions in my portal").

Two exams in the normal app (build.exam_confs): /ncert-class-11/ and /ncert-class-12/, on the start page under the board "NCERT".
Every NCERT chapter is one "paper" (id n<class><book><chapter>, e.g. n11icw01), every subject is a subject and its topics are the
book titles, so the app's practice, timed tests, quiz builder, mistakes notebook and the All-in-One Pass work unchanged.
The books and chapters are those of the current NCERT textbooks (rationalised 2023-24, Reprint 2026-27; NCERT keeps them for
2026-27, new Class 11 books are due from 2027-28). Questions are Learn with Anil's own, written from the chapter's content; NCERT's own
exercise questions are not copied.

Sources: src/ncert-class-<11|12>/<book code>-<chapter, 2 digits>.txt, the same format as the previous papers:
    Q <n> | <subject key> | <book title>
    question lines
    (1) .. (4) options
    = <answer number>
    ~ explanation
A chapter whose file does not exist yet shows "Coming soon" on the class page.
"""
import html
import re

SUBJ = [   # key, name, slug, short name, Hindi name
    ('pol', 'Political Science (Polity)', 'polity', 'Polity', 'राजनीति विज्ञान'),
    ('his', 'History', 'history', 'History', 'इतिहास'),
    ('geo', 'Geography', 'geography', 'Geography', 'भूगोल'),
    ('eco', 'Economics', 'economics', 'Economics', 'अर्थशास्त्र'),
    ('soc', 'Sociology', 'sociology', 'Sociology', 'समाजशास्त्र'),
    ('art', 'Fine Arts (Indian Art & Culture)', 'fine-arts', 'Indian Art', 'ललित कला'),
    ('phy', 'Physics', 'physics', 'Physics', 'भौतिकी'),
    ('chem', 'Chemistry', 'chemistry', 'Chemistry', 'रसायन विज्ञान'),
    ('bio', 'Biology', 'biology', 'Biology', 'जीव विज्ञान'),
]
SN = {s[0]: s for s in SUBJ}

BOOKS = {   # class -> [(subject, book code, book title, [chapter titles])], in the order shown on the class page
    11: [
        ('pol', 'icw', 'Indian Constitution at Work', [
            'Constitution: Why and How?', 'Rights in the Indian Constitution', 'Election and Representation', 'Executive', 'Legislature',
            'Judiciary', 'Federalism', 'Local Governments', 'Constitution as a Living Document', 'The Philosophy of the Constitution']),
        ('pol', 'pt', 'Political Theory', [
            'Political Theory: An Introduction', 'Freedom', 'Equality', 'Social Justice', 'Rights', 'Citizenship', 'Nationalism', 'Secularism']),
        ('his', 'twh', 'Themes in World History', [
            'Writing and City Life', 'An Empire Across Three Continents', 'Nomadic Empires', 'The Three Orders', 'Changing Cultural Traditions',
            'Displacing Indigenous Peoples', 'Paths to Modernisation']),
        ('geo', 'fpg', 'Fundamentals of Physical Geography', [
            'Geography as a Discipline', 'The Origin and Evolution of the Earth', 'Interior of the Earth', 'Distribution of Oceans and Continents',
            'Geomorphic Processes', 'Landforms and their Evolution', 'Composition and Structure of Atmosphere',
            'Solar Radiation, Heat Balance and Temperature', 'Atmospheric Circulation and Weather Systems', 'Water in the Atmosphere',
            'World Climate and Climate Change', 'Water (Oceans)', 'Movements of Ocean Water', 'Biodiversity and Conservation']),
        ('geo', 'ipe', 'India: Physical Environment', [
            'India — Location', 'Structure and Physiography', 'Drainage System', 'Climate', 'Natural Vegetation', 'Natural Hazards and Disasters']),
        ('eco', 'ied', 'Indian Economic Development', [
            'Indian Economy on the Eve of Independence', 'Indian Economy 1950–1990', 'Liberalisation, Privatisation and Globalisation: An Appraisal',
            'Human Capital Formation in India', 'Rural Development', 'Employment: Growth, Informalisation and Other Issues',
            'Environment and Sustainable Development', 'Comparative Development Experiences of India and its Neighbours']),
        ('eco', 'sfe', 'Statistics for Economics', [
            'Introduction', 'Collection of Data', 'Organisation of Data', 'Presentation of Data', 'Measures of Central Tendency', 'Correlation',
            'Index Numbers', 'Use of Statistical Tools']),
        ('soc', 'isoc', 'Introducing Sociology', [
            'Sociology and Society', 'Terms, Concepts and their Use in Sociology', 'Understanding Social Institutions', 'Culture and Socialisation',
            'Doing Sociology: Research Methods']),
        ('soc', 'usoc', 'Understanding Society', [
            'Social Structure, Stratification and Social Processes in Society', 'Social Change and Social Order in Rural and Urban Society',
            'Environment and Society', 'Introducing Western Sociologists', 'Indian Sociologists']),
        ('art', 'iia1', 'An Introduction to Indian Art, Part I', [
            'Prehistoric Rock Paintings', 'Arts of the Indus Valley', 'Arts of the Mauryan Period', 'Post-Mauryan Trends in Indian Art and Architecture',
            'Later Mural Traditions', 'Temple Architecture and Sculpture', 'Indian Bronze Sculpture', 'Some Aspects of Indo-Islamic Architecture']),
        ('phy', 'phy', 'Physics, Parts I & II', [
            'Units and Measurements', 'Motion in a Straight Line', 'Motion in a Plane', 'Laws of Motion', 'Work, Energy and Power',
            'System of Particles and Rotational Motion', 'Gravitation', 'Mechanical Properties of Solids', 'Mechanical Properties of Fluids',
            'Thermal Properties of Matter', 'Thermodynamics', 'Kinetic Theory', 'Oscillations', 'Waves']),
        ('chem', 'chem', 'Chemistry, Parts I & II', [
            'Some Basic Concepts of Chemistry', 'Structure of Atom', 'Classification of Elements and Periodicity in Properties',
            'Chemical Bonding and Molecular Structure', 'Thermodynamics', 'Equilibrium', 'Redox Reactions',
            'Organic Chemistry: Some Basic Principles and Techniques', 'Hydrocarbons']),
        ('bio', 'bio', 'Biology', [
            'The Living World', 'Biological Classification', 'Plant Kingdom', 'Animal Kingdom', 'Morphology of Flowering Plants',
            'Anatomy of Flowering Plants', 'Structural Organisation in Animals', 'Cell: The Unit of Life', 'Biomolecules', 'Cell Cycle and Cell Division',
            'Photosynthesis in Higher Plants', 'Respiration in Plants', 'Plant Growth and Development', 'Breathing and Exchange of Gases',
            'Body Fluids and Circulation', 'Excretory Products and their Elimination', 'Locomotion and Movement', 'Neural Control and Coordination',
            'Chemical Coordination and Integration']),
    ],
    12: [
        ('pol', 'pisi', 'Politics in India since Independence', [
            'Challenges of Nation Building', 'Era of One-party Dominance', 'Politics of Planned Development', "India's External Relations",
            'Challenges to and Restoration of the Congress System', 'The Crisis of Democratic Order', 'Regional Aspirations',
            'Recent Developments in Indian Politics']),
        ('pol', 'cwp', 'Contemporary World Politics', [
            'The End of Bipolarity', 'Contemporary Centres of Power', 'Contemporary South Asia', 'International Organisations',
            'Security in the Contemporary World', 'Environment and Natural Resources', 'Globalisation']),
        ('his', 'tih1', 'Themes in Indian History, Part I', [
            'Bricks, Beads and Bones: The Harappan Civilisation', 'Kings, Farmers and Towns: Early States and Economies',
            'Kinship, Caste and Class: Early Societies', 'Thinkers, Beliefs and Buildings: Cultural Developments']),
        ('his', 'tih2', 'Themes in Indian History, Part II', [
            'Through the Eyes of Travellers: Perceptions of Society', 'Bhakti-Sufi Traditions: Changes in Religious Beliefs and Devotional Texts',
            'An Imperial Capital: Vijayanagara', 'Peasants, Zamindars and the State: Agrarian Society and the Mughal Empire']),
        ('his', 'tih3', 'Themes in Indian History, Part III', [
            'Colonialism and the Countryside: Exploring Official Archives', 'Rebels and the Raj: The Revolt of 1857 and its Representations',
            'Mahatma Gandhi and the Nationalist Movement: Civil Disobedience and Beyond', 'Framing the Constitution: The Beginning of a New Era']),
        ('geo', 'fhg', 'Fundamentals of Human Geography', [
            'Human Geography: Nature and Scope', 'The World Population: Distribution, Density and Growth', 'Human Development',
            'Primary Activities', 'Secondary Activities', 'Tertiary and Quaternary Activities', 'Transport and Communication', 'International Trade']),
        ('geo', 'ipeco', 'India: People and Economy', [
            'Population: Distribution, Density, Growth and Composition', 'Human Settlements', 'Land Resources and Agriculture', 'Water Resources',
            'Mineral and Energy Resources', 'Planning and Sustainable Development in Indian Context', 'Transport and Communication',
            'International Trade', 'Geographical Perspective on Selected Issues and Problems']),
        ('eco', 'mac', 'Introductory Macroeconomics', [
            'Introduction', 'National Income Accounting', 'Money and Banking', 'Determination of Income and Employment',
            'Government Budget and the Economy', 'Open Economy Macroeconomics']),
        ('eco', 'mic', 'Introductory Microeconomics', [
            'Introduction', 'Theory of Consumer Behaviour', 'Production and Costs', 'The Theory of the Firm under Perfect Competition',
            'Market Equilibrium']),
        ('soc', 'insoc', 'Indian Society', [
            'Introducing Indian Society', 'The Demographic Structure of the Indian Society', 'Social Institutions: Continuity and Change',
            'The Market as a Social Institution', 'Patterns of Social Inequality and Exclusion', 'The Challenges of Cultural Diversity']),
        ('soc', 'scdi', 'Social Change and Development in India', [
            'Structural Change', 'Cultural Change', 'The Story of Indian Democracy', 'Change and Development in Rural Society',
            'Change and Development in Industrial Society', 'Globalisation and Social Change', 'Mass Media and Communications', 'Social Movements']),
        ('art', 'iia2', 'An Introduction to Indian Art, Part II', [
            'The Manuscript Painting Tradition', 'The Rajasthani Schools of Painting', 'The Mughal School of Miniature Painting',
            'The Deccani Schools of Painting', 'The Pahari Schools of Painting', 'The Bengal School and Cultural Nationalism',
            'The Modern Indian Art', 'Living Art Traditions of India']),
        ('phy', 'phy', 'Physics, Parts I & II', [
            'Electric Charges and Fields', 'Electrostatic Potential and Capacitance', 'Current Electricity', 'Moving Charges and Magnetism',
            'Magnetism and Matter', 'Electromagnetic Induction', 'Alternating Current', 'Electromagnetic Waves', 'Ray Optics and Optical Instruments',
            'Wave Optics', 'Dual Nature of Radiation and Matter', 'Atoms', 'Nuclei', 'Semiconductor Electronics: Materials, Devices and Simple Circuits']),
        ('chem', 'chem', 'Chemistry, Parts I & II', [
            'Solutions', 'Electrochemistry', 'Chemical Kinetics', 'The d- and f-Block Elements', 'Coordination Compounds', 'Haloalkanes and Haloarenes',
            'Alcohols, Phenols and Ethers', 'Aldehydes, Ketones and Carboxylic Acids', 'Amines', 'Biomolecules']),
        ('bio', 'bio', 'Biology', [
            'Sexual Reproduction in Flowering Plants', 'Human Reproduction', 'Reproductive Health', 'Principles of Inheritance and Variation',
            'Molecular Basis of Inheritance', 'Evolution', 'Human Health and Disease', 'Microbes in Human Welfare',
            'Biotechnology: Principles and Processes', 'Biotechnology and its Applications', 'Organisms and Populations', 'Ecosystem',
            'Biodiversity and Conservation']),
    ],
}

EXAMS = ('ncert-class-11', 'ncert-class-12')
FOOT = ('Questions and explanations are written by Learn with Anil from the NCERT textbooks (current editions, Reprint 2026-27); '
        'NCERT\'s own exercises are not copied. Not affiliated with NCERT.')


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and').replace("'", '')).strip('-')


def chapters(cls):
    """Every chapter of the class as a paper dict (the build skips chapters whose source file is not there yet)."""
    out = []
    for s, code, book, chs in BOOKS[cls]:
        sname, sslug, sshort = SN[s][1], SN[s][2], SN[s][3]
        for i, ch in enumerate(chs, 1):
            out.append(dict(
                id=f'n{cls}{code}{i:02d}', file=f'{code}-{i:02d}.txt', year=cls, stage=book, nsub=s, nbook=code, nch=i,
                short=f'Ch {i}. {ch}', title=f'NCERT Class {cls} {sshort} · {book} · Chapter {i}: {ch}',
                notif=f'{book} · Class {cls}', held=f'Chapter {i}', fmt='mcq',
                slug=f'ncert-class-{cls}-{sslug}-{slugify(book)}-chapter-{i}-{slugify(ch)}-mcqs',
                blurb=f'MCQs on Chapter {i} of the NCERT Class {cls} {sname} textbook {book}, with answers and explanations.',
                kwname=f'NCERT Class {cls} {sshort} Chapter {i} {ch}', key="Learn with Anil's answers", en_only=True))
    return out


def subjects(cls):
    """(key, name, slug, topics): the topics of a subject are its book titles in this class."""
    return [(k, n, sl, [b for s, _, b, _ in BOOKS[cls] if s == k]) for k, n, sl, _, _ in SUBJ if any(s == k for s, _, _, _ in BOOKS[cls])]


def faq(cls):
    def f(total, npapers):
        nch = sum(len(c) for _, _, _, c in BOOKS[cls])
        return [
            (f'What is on the NCERT Class {cls} page?',
             f'Chapter-wise multiple-choice questions (MCQs) on the NCERT Class {cls} textbooks of Polity, History, Geography, Economics, Sociology, '
             f'Fine Arts (Indian art and culture), Physics, Chemistry and Biology: {nch} chapters in all. {total:,} questions in {npapers} chapters are live now, '
             f'and new chapters are added every week. Every question has the correct answer and a short explanation.'),
            ('Are these NCERT\'s own exercise questions?',
             'No. The questions are written by Learn with Anil from the content of each NCERT chapter, in the style of UPSC, state PSC, SSC and other '
             'government exams. NCERT\'s own end-of-chapter exercises are not copied.'),
            ('Which NCERT books are used?',
             f'The current NCERT Class {cls} textbooks (the rationalised editions of 2023-24, Reprint 2026-27), with their chapter numbers and names. '
             'NCERT has said these books continue for the 2026-27 session; when new books come, the questions will be updated chapter by chapter.'),
            ('Why practise NCERT for government exams?',
             'UPSC Prelims, APPSC and TGPSC Group exams, SSC and police exams ask many questions straight from NCERT ideas: the Constitution, '
             'history, geography, economy and science. Practising each chapter as MCQs shows you what you have really understood and what to revise.'),
            ('What does it cost?',
             'The NCERT questions are part of the ₹45 All-in-One Pass, valid for 12 months, the same pass that opens every previous paper, mock test and '
             'study book on the site. Without the pass you can read every chapter\'s questions with their answers on the chapter pages, with the '
             'explanations of the first 10 questions of each chapter.'),
            ('Are the questions available in Hindi or Telugu?',
             'They are in English now. Hindi and Telugu versions will be added subject by subject.'),
        ]
    return f


def confs(B):
    out = []
    for cls in (11, 12):
        nch = sum(len(c) for _, _, _, c in BOOKS[cls])
        out.append(dict(
            id=f'ncert-class-{cls}', dir=f'ncert-class-{cls}', src=f'ncert-class-{cls}', key=f'ncert-{cls}', name=f'NCERT Class {cls}',
            short=f'NCERT Class {cls}', seo=f'NCERT Class {cls}', slugp=f'ncert-class-{cls}', papers=chapters(cls), subjects=subjects(cls),
            faq=faq(cls), board='NCERT', l2=B.L2_HI, pb=f'/ncert-class-{cls}/', ncert=True, cls=cls, foot=FOOT,
            keyname="Learn with Anil's answers", keyshort="Learn with Anil's answers",
            title=(f'NCERT Class {cls} MCQs Chapter-wise with Answers – Polity, History, Geography, Economics, Sociology, Art & Science | Learn with Anil'),
            h1=f'NCERT Class {cls} chapter-wise MCQs <em>with answers.</em>',
            l2line=f'एनसीईआरटी कक्षा {cls} की हर पुस्तक के हर अध्याय पर बहुविकल्पीय प्रश्न (MCQ), उत्तर और व्याख्या सहित — अभी अंग्रेज़ी में, हिंदी संस्करण जल्द।',
            aka=(f'Written by Learn with Anil from the current NCERT Class {cls} textbooks (Reprint 2026-27) for UPSC, APPSC, TGPSC, SSC, police and '
                 f'other government exams: {len(BOOKS[cls])} books, {nch} chapters, subject-wise and chapter-wise.'),
            aka_short=f'NCERT Class {cls} textbooks',
            desc=lambda t, cls=cls: (f'NCERT Class {cls} chapter-wise MCQs with answers and explanations: Polity, History, Geography, Economics, Sociology, '
                                     f'Indian Art, Physics, Chemistry and Biology, book by book. {t:,} questions written by Learn with Anil for UPSC, state PSC and '
                                     f'SSC preparation; practise each chapter as a quiz or a timed test with the ₹45 All-in-One Pass.'),
            eyebrow=f'NCERT · Class {cls} · Subject-wise &amp; chapter-wise MCQs',
            papers_note=(f'One set of MCQs for every chapter of the NCERT Class {cls} textbooks, written by Learn with Anil, with answers and explanations. '
                         'Chapters are added every week.')))
    return out


def counts(papers):
    return {p['id']: p['count'] for p in papers}


CSS = """<style>
.ncb .ncb-head{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:6px 16px;margin:0 0 12px}
.ncb .ncb-head h2{margin:0}
.ncb-nav{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 16px}
.ncb-nav button{display:inline-flex;align-items:center;gap:7px;border:1.5px solid var(--line);background:var(--surface);border-radius:999px;padding:6px 13px;font:600 14px/1.2 var(--f-body,inherit);color:var(--ink);cursor:pointer}
.ncb-nav button b{font-family:var(--f-mono,monospace);font-size:12px;font-weight:600;color:var(--accent-text);background:var(--accent-soft);border-radius:999px;padding:1px 7px}
.ncb-nav button.ncb-off b{color:var(--muted);background:var(--surface-2)}
.ncb-nav button:hover{border-color:var(--accent)}
.ncb-s{background:var(--surface);border:1px solid var(--line);border-radius:14px;margin:0 0 14px;overflow:hidden;scroll-margin-top:80px}
.ncb-s>summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:14px 16px;font:800 19px/1.25 var(--f-display,inherit);color:var(--ink)}
.ncb-s>summary::-webkit-details-marker{display:none}
.ncb-s>summary::after{content:"▾";font-size:16px;color:var(--muted);transition:transform .2s}
.ncb-s:not([open])>summary::after{transform:rotate(-90deg)}
.ncb-s>summary small{font:600 13.5px/1.3 var(--f-body,inherit);color:var(--muted);margin-left:auto}
.ncb-book{padding:4px 16px 14px;border-top:1px solid var(--line)}
.ncb-book h3{font-size:16px;margin:12px 0 8px;display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline}
.ncb-book h3 span{font-size:13px;font-weight:600;color:var(--muted)}
.ncb-ch{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.ncb-ch li{display:grid;grid-template-columns:30px minmax(0,1fr) auto;gap:4px 10px;align-items:center;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
.ncb-ch li.ncb-off{background:var(--surface-2);color:var(--muted)}
.ncb-n{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;font:700 13px/1 var(--f-mono,monospace);background:var(--accent-soft);color:var(--accent-text)}
.ncb-ch li.ncb-off .ncb-n{background:var(--line);color:var(--muted)}
.ncb-t{min-width:0;display:flex;flex-direction:column;gap:1px}
.ncb-t a,.ncb-t b{font-weight:700;color:var(--ink);text-decoration:none;overflow-wrap:anywhere}
.ncb-t a:hover{text-decoration:underline}
.ncb-t small{font-size:12.5px;color:var(--muted)}
.ncb-a{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.ncb-btn{display:inline-flex;align-items:center;padding:6px 12px;border-radius:999px;border:1.5px solid var(--accent);color:var(--accent-text);background:var(--surface);font-weight:700;font-size:13.5px;text-decoration:none;white-space:nowrap}
.ncb-btn.go{background:var(--accent);color:var(--accent-ink,#fff)}
.ncb-btn:hover{filter:brightness(1.06)}
.ncb-soon{font-size:12.5px;font-weight:700;color:var(--muted);white-space:nowrap}
.ncb-note{font-size:14.5px;color:var(--muted);margin:6px 0 0}
@media (max-width:560px){.ncb-ch li{grid-template-columns:28px minmax(0,1fr)}.ncb-a{grid-column:2;justify-content:flex-start}}
</style>"""

JS = """<script>
document.addEventListener("click", function(e){
  var b = e.target.closest && e.target.closest("[data-ncs]"); if(!b) return;
  var d = document.getElementById("ncs-" + b.getAttribute("data-ncs")); if(!d) return;
  d.open = true; d.scrollIntoView({behavior:"smooth", block:"start"});
});
</script>"""


def browser(conf, papers, abs_links=False):
    """The class page's subject -> book -> chapter list. Live chapters link to their page and open in the app as a practice quiz
    (?practice=) or a timed test (?test=); the others say 'Coming soon'."""
    cls, pb = conf['cls'], conf['pb']
    live = {p['id']: p for p in papers}
    by_s = {}
    for s, code, book, chs in BOOKS[cls]: by_s.setdefault(s, []).append((code, book, chs))
    nav, secs = [], []
    first_open = True
    for k, name, sslug, short, _hi in SUBJ:
        if k not in by_s: continue
        books = by_s[k]
        nch = sum(len(c) for _, _, c in books)
        ids = [f'n{cls}{code}{i:02d}' for code, _, chs in books for i in range(1, len(chs) + 1)]
        nlive = sum(1 for i in ids if i in live)
        nq = sum(live[i]['count'] for i in ids if i in live)
        nav.append(f'<button type="button" data-ncs="{k}"{" class=ncb-off" if not nq else ""}>{esc(short)} <b>{f"{nq:,} Q" if nq else "soon"}</b></button>')
        blocks = []
        for code, book, chs in books:
            items = []
            bl = 0
            for i, ch in enumerate(chs, 1):
                pid = f'n{cls}{code}{i:02d}'
                p = live.get(pid)
                if p:
                    bl += 1
                    items.append(f'<li><span class="ncb-n">{i}</span><span class="ncb-t"><a href="{pb}papers/{p["slug"]}.html">{esc(ch)}</a>'
                                 f'<small>{p["count"]} MCQs · answers &amp; explanations</small></span>'
                                 f'<span class="ncb-a"><a class="ncb-btn go" href="{pb}?practice={pid}">Practise</a>'
                                 f'<a class="ncb-btn" href="{pb}?test={pid}">Timed test</a></span></li>')
                else:
                    items.append(f'<li class="ncb-off"><span class="ncb-n">{i}</span><span class="ncb-t"><b>{esc(ch)}</b></span><span class="ncb-soon">Coming soon</span></li>')
            blocks.append(f'<div class="ncb-book"><h3>{esc(book)} <span>{len(chs)} chapters' + (f' · {bl} live' if bl else '') + '</span></h3>'
                          f'<ol class="ncb-ch">{"".join(items)}</ol></div>')
        op = ' open' if (nq and first_open) else ''
        if nq: first_open = False
        secs.append(f'<details class="ncb-s" id="ncs-{k}"{op}><summary>{esc(name)}<small>{len(books)} book{"s" if len(books) > 1 else ""} · {nch} chapters'
                    + (f' · {nlive} live · {nq:,} questions' if nq else ' · coming soon') + f'</small></summary>{"".join(blocks)}</details>')
    total = sum(p['count'] for p in papers)
    allch = sum(len(c) for _, _, _, c in BOOKS[cls])
    return (CSS + f'<section class="wrap section ncb" id="chapters"><div class="ncb-head"><h2>Subject-wise &amp; chapter-wise MCQs</h2>'
            f'<span class="muted" style="font-size:14px">{total:,} questions in {len(papers)} of {allch} chapters · new chapters every week</span></div>'
            f'<nav class="ncb-nav" aria-label="Subjects">{"".join(nav)}</nav>{"".join(secs)}'
            f'<p class="ncb-note">Tap a chapter name to read its questions with answers (free). <b>Practise</b> checks each answer as you go; '
            f'<b>Timed test</b> gives one minute a question. Both open with the ₹45 All-in-One Pass, the same pass for every exam, mock test and book on the site.</p>'
            '</section>' + JS)


def hero(conf, papers, questions):
    """HERO_P and FIG12 for the class home page."""
    cls = conf['cls']
    allch = sum(len(c) for _, _, _, c in BOOKS[cls])
    hp = (f'<p>{len(questions):,} questions on {len(papers)} chapter{"s" if len(papers) != 1 else ""} of the NCERT Class {cls} textbooks so far, each with the answer and a short explanation. '
          f'Pick a subject, then a chapter: practise it question by question or take it as a timed test, and revise your mistakes, '
          f'with one ₹45 All-in-One Pass for every exam on the site.</p>')
    fig = (f'      <div class="figure"><div class="v">{len(questions):,}</div><div class="k">NCERT MCQs written so far</div></div>\n'
           f'      <div class="figure"><div class="v">{len(papers)}/{allch}</div><div class="k">Chapters live</div></div>\n')
    return hp, fig


def static_pages(B, conf, papers, subjects_, questions, subj):
    """One crawlable page per chapter (all its questions; every answer free, explanations of the first SAMPLE_N free) and one per subject."""
    pages = {}
    by_p = {}
    for q in questions: by_p.setdefault(q['p'], []).append(q)
    pmap = {p['id']: p for p in papers}
    cls, pb = conf['cls'], conf['pb']
    base = f'{B.SITE_URL}{pb}'
    home = [('Home', B.SITE_URL + '/'), (conf['name'], base)]
    free = B.sample_ids(questions)
    unl = lambda q: None if q['id'] in free else f'{pb}?q={q["id"]}'
    order = [p['id'] for p in chapters(cls)]
    papers = sorted(papers, key=lambda p: order.index(p['id']))
    for idx, p in enumerate(papers):
        qs = by_p[p['id']]
        sname, sshort = SN[p['nsub']][1], SN[p['nsub']][3]
        ch = p['short'].split('. ', 1)[1]
        rel = f'papers/{p["slug"]}.html'
        can = base + rel
        title = f'NCERT Class {cls} {sshort} Chapter {p["nch"]} {ch} MCQs with Answers ({p["stage"]}) | Learn with Anil'
        desc = (f'{len(qs)} MCQs on NCERT Class {cls} {sname}, {p["stage"]}, Chapter {p["nch"]}: {ch}, with answers and explanations, '
                f'for UPSC, state PSC and SSC preparation. Practise them online as a quiz or a timed test.')
        prev_p = papers[idx - 1] if idx and papers[idx - 1]['stage'] == p['stage'] else None
        next_p = papers[idx + 1] if idx + 1 < len(papers) and papers[idx + 1]['stage'] == p['stage'] else None
        nav = ('<nav class="toc">' + (f'<a href="{prev_p["slug"]}.html">← Chapter {prev_p["nch"]}</a>' if prev_p else '')
               + (f'<a href="{next_p["slug"]}.html">Chapter {next_p["nch"]} →</a>' if next_p else '')
               + f'<a href="{pb}#chapters">All NCERT Class {cls} chapters</a>'
               + f'<a href="../subjects/ncert-class-{cls}-{SN[p["nsub"]][2]}-mcqs.html">All Class {cls} {esc(sshort)} MCQs</a></nav>')
        body = (f'<a class="cta" href="{pb}?practice={p["id"]}">Practise this chapter · {len(qs)} questions</a>'
                f'<a class="cta alt" href="{pb}?test={p["id"]}">Take it as a timed test</a>'
                f'<p class="note">The correct answer to every question is free on this page, and so are the explanations of the first {min(B.SAMPLE_N, len(qs))}. '
                f'For all {len(qs)} explanations, practise the chapter in the app with the ₹{B.PAY["pyq_price"]} All-in-One Pass, one payment for every exam on the site.</p>'
                f'<h2>All {len(qs)} questions</h2><ol class="qs">'
                + ''.join(B.q_html(q, p['short'], f'Q{q["n"]}', subj, conf['l2'], f'{pb}q/{q["id"]}.html', unl(q)) for q in qs) + '</ol>' + nav)
        lede = esc(f'Multiple-choice questions on Chapter {p["nch"]}, "{ch}", of the NCERT Class {cls} {sname} textbook {p["stage"]} (current edition). '
                   f'Written by Learn with Anil to test the chapter\'s ideas the way UPSC, state PSC and SSC exams ask them; each has the answer and a short explanation.')
        pages[rel] = B.static_page(1, title, desc, can, f'NCERT Class {cls} {sshort} · Chapter {p["nch"]}: {ch} · MCQs', lede, body,
                                   home + [(f'Chapter {p["nch"]}: {ch}', can)], conf)
    for s in subjects_:
        sp = [p for p in papers if p['nsub'] == s['id']]
        if not sp: continue
        rel = f'subjects/ncert-class-{cls}-{s["slug"]}-mcqs.html'
        can = base + rel
        sshort = SN[s['id']][3]
        n = sum(len(by_p[p['id']]) for p in sp)
        title = f'NCERT Class {cls} {sshort} MCQs Chapter-wise with Answers | Learn with Anil'
        desc = (f'{n} chapter-wise MCQs on the NCERT Class {cls} {s["name"]} textbooks ({", ".join(dict.fromkeys(p["stage"] for p in sp))}), '
                f'with answers and explanations, for UPSC, state PSC and SSC preparation.')
        body = []
        for book in dict.fromkeys(p['stage'] for p in sp):
            body.append(f'<h2>{esc(book)}</h2><ol class="clist">' + ''.join(
                f'<li><div class="cmeta">Chapter {p["nch"]} · {len(by_p[p["id"]])} questions</div><b><a href="../papers/{p["slug"]}.html">{esc(p["short"].split(". ", 1)[1])}</a></b>'
                f'<div class="cacts"><a class="cta" href="{pb}?practice={p["id"]}">Practise</a><a class="cta alt" href="{pb}?test={p["id"]}">Timed test</a></div></li>'
                for p in sp if p['stage'] == book) + '</ol>')
        body.append(f'<p><a class="cta alt" href="{pb}#chapters">Every NCERT Class {cls} subject and chapter</a></p>')
        lede = esc(f'Every chapter of the NCERT Class {cls} {s["name"]} textbooks that has questions on Learn with Anil so far, book by book, '
                   f'with links to read each chapter\'s questions and answers or practise them.')
        pages[rel] = B.static_page(1, title, desc, can, f'NCERT Class {cls} {sshort} chapter-wise MCQs', lede, ''.join(body),
                                   home + [(s['name'], can)], conf)
    return pages


def qpage_desc(conf, p, q, text):
    return (f'NCERT Class {conf["cls"]} {SN[p["nsub"]][3]}, {p["stage"]}, Chapter {p["nch"]}, Q{q["n"]}: {text[:140].rsplit(" ", 1)[0]}… '
            'MCQ with answer and explanation by Learn with Anil.')


def llms_lines(B, loaded):
    L = []
    for c, papers, questions in loaded:
        if not c.get('ncert'): continue
        L.append(f'- [{c["name"]} chapter-wise MCQs with answers]({B.SITE_URL}{c["pb"]}): {len(questions):,} questions written by Learn with Anil '
                 f'on {len(papers)} chapters of the NCERT Class {c["cls"]} textbooks (Polity, History, Geography, Economics, Sociology, Indian Art, Physics, '
                 'Chemistry, Biology), with answers and explanations; more chapters every week.')
        for p in papers:
            L.append(f'  - [NCERT Class {c["cls"]} {SN[p["nsub"]][3]} Chapter {p["nch"]} {p["short"].split(". ", 1)[1]} MCQs]({B.SITE_URL}{c["pb"]}papers/{p["slug"]}.html) — {p["count"]} questions')
    return L
