"""UPSC Civil Services Mains: General Studies Papers I-IV previous questions with model answers (Anil, 1 Nov 2026).

Anil: "can u do same for upsc mains ... (2019-26)" (same as the APPSC Group-1 Mains pages, tools/g1mains.py): GS 1-4 of the
2019-2026 Civil Services (Main) Examinations, long model answers in the Group-1 style, questions free, the first two answers
of every paper free, the rest in the ₹45 PYQ Pass. Box design: a paper page lists its questions as cards; every answer has
its own page.

Data (src/upsc-cse/mains-pyqs/):
    questions.json   [{id, paper (GS1-GS4), year, qno ("7", or "1(a)" in GS4 Section A), marks, words, part_no, part, topic, text}]
                     from UPSC's official question papers (upsc.gov.in), English version
    answers.json     {key: "bk-upm-ans", files: {"<year>-gs<n>": "<sealed bundle in src/books>"}, n, free: {id: answer HTML}}
                     (tools/g1m_seal.py with --exam upsc)
Pages (under /upsc-cse/): index.html (the UPSC CSE hub) and mains-pyqs/ (index, <year>-gs<n>.html, <year>-gs<n>-q<k>.html,
gs<n>-<part slug>.html).
"""
import html, json, os, re, shutil
import g1m_render
from g1mains import CSS, slug, short, flip_js, unlock_js

EXAM = 'upsc-cse'
DIR = 'mains-pyqs'
PAPERS = {'GS1': (1, 'General Studies Paper I', 'Indian Heritage and Culture, History and Geography of the World and Society'),
          'GS2': (2, 'General Studies Paper II', 'Governance, Constitution, Polity, Social Justice and International Relations'),
          'GS3': (3, 'General Studies Paper III', 'Technology, Economic Development, Bio-diversity, Environment, Security and Disaster Management'),
          'GS4': (4, 'General Studies Paper IV', 'Ethics, Integrity and Aptitude')}
YEARS = (2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019)
FREE = ('1', '2', '1(a)', '1(b)')   # free sample answers: the first two questions of every paper
esc = lambda s: html.escape(str(s), quote=True)


def conf_for(B):
    """The page settings static_page needs (UPSC CSE has no prelims app yet: Mains pages only)."""
    return dict(id=EXAM, dir=EXAM, name='UPSC Civil Services', seo='UPSC CSE', pb=f'/{EXAM}/', board='UPSC', l2=dict(gf=''), keyshort='',
                nav=('Mains PYQs →', f'/{EXAM}/{DIR}/'),
                foot=('Questions are from UPSC\'s official Civil Services (Main) question papers. Model answers are by Jupudi Anil Kumar, '
                      f'Learn with Anil (Instagram: @{B.INSTAGRAM}). Not affiliated with UPSC.'))


def load(src):
    d = os.path.join(src, EXAM, DIR)
    qp, ap = os.path.join(d, 'questions.json'), os.path.join(d, 'answers.json')
    if not os.path.exists(qp): return [], {}
    qs = json.load(open(qp, encoding='utf-8'))
    man = json.load(open(ap, encoding='utf-8')) if os.path.exists(ap) else {}
    return qs, man


def n_of(p): return PAPERS[p][0]
def qkey(q): return (int(re.match(r'\d+', q['qno']).group()), q['qno'])
def aslug(q): return q['qno'].replace('(', '').replace(')', '').lower()
def ppage(q): return f'{q["year"]}-gs{n_of(q["paper"])}.html'
def apage(q): return f'{q["year"]}-gs{n_of(q["paper"])}-q{aslug(q)}.html'
def pkey(q): return f'{q["year"]}-gs{n_of(q["paper"])}'
def pname(p): return f'{PAPERS[p][1]}: {PAPERS[p][2]}'


def part_pages(qs):
    out = {}
    for q in qs: out.setdefault((q['paper'], q['part_no']), (q['part'], f'gs{n_of(q["paper"])}-{slug(q["part"])}'))
    return out


def meta(q, show_year=False, show_part=True):
    bits = ([f'{q["year"]} · GS {n_of(q["paper"])}'] if show_year else []) + [f'Q{q["qno"]}', f'{q["marks"]} marks']
    if q.get('words'): bits.append(f'{q["words"]} words')
    if show_part: bits.append(f'{q["part"]} · {q["topic"]}')
    return ' · '.join(bits)


def card(q, man, show_year=False, show_part=True):
    href = apage(q)
    if q['id'] in man.get('free', {}): btn = f'<a class="cta green" href="{href}">✓ Free model answer →</a>'
    elif (man.get('files') or {}).get(pkey(q)): btn = f'<a class="cta" href="{href}" data-lk>🔒 Model answer →</a>'
    else: btn = f'<a class="cta alt" href="{href}">Model answer: coming soon</a>'
    text = q['text'] if len(q['text']) <= 420 else short(q['text'], 380)   # long case studies: the full text is on the answer page
    return (f'<li id="{q["id"]}"><div class="cmeta">{esc(meta(q, show_year, show_part))}</div><a class="qlink" href="{href}"><b style="white-space:pre-line">{esc(text)}</b></a>'
            f'<div class="cacts">{btn}</div></li>')


def pages(B):
    """{path under the site root: html} for the UPSC CSE hub and Mains pages; copies the sealed answers into /books/."""
    qs, man = load(B.SRC)
    if not qs: return {}
    conf = conf_for(B)
    files = man.get('files') or {}
    if files:
        os.makedirs(os.path.join(B.DIST, 'site', 'books'), exist_ok=True)
        for f in files.values(): shutil.copy(os.path.join(B.SRC, 'books', f), os.path.join(B.DIST, 'site', 'books', f))
    pb, price = conf['pb'], B.PAY['pyq_price']
    base = f'{B.SITE_URL}{pb}{DIR}/'
    crumbs0 = [('Home', B.SITE_URL + '/'), ('UPSC Civil Services', B.SITE_URL + pb), ('Mains PYQs', base)]
    parts = part_pages(qs)
    free = man.get('free', {})
    years = [y for y in YEARS if any(q['year'] == y for q in qs)]
    done = sorted({int(k[:4]) for k in files}, reverse=True)
    buyurl = '/upsc-epfo/?buy=pyq'   # the pass checkout lives in the exam apps (one ₹45 PYQ Pass for the whole site)
    buy = (f'<div class="buy"><div><b>UPSC Mains model answers</b><p>Every GS question of the Civil Services (Main) Examinations {years[-1]}–{years[0]} with a '
           f'model answer: key words and an introduction, every part of the question in numbered points, diagrams, flowcharts or tables, and a conclusion. '
           f'Included in the ₹{price} PYQ Pass, with every previous paper, mock test series and study book on the site.</p>'
           f'<p class="muted">₹{price} · {B.PYQ_VALID} · pay by UPI, card or net banking</p></div><a class="cta" href="{buyurl}">Get it for ₹{price}</a></div>')
    status = ('Model answers are ready for every paper.' if set(done) >= set(years)
              else f'Model answers are ready for {", ".join(map(str, done))}; the other years are being added, newest first.' if done
              else 'Model answers are being added year by year, newest first.')
    howto = (f'<p class="note">Tap a question to open its model answer on its own page. Q1 and Q2 of every paper are free; the rest open with the ₹{price} PYQ Pass '
             f'on the phone you registered in the app. The model answers are fuller than UPSC\'s 150/250-word limits so that you learn the content; '
             f'write within the limit in the exam. {status} Answers are by Learn with Anil (Jupudi Anil Kumar), not by UPSC.</p>')
    out = {}
    by_yp = {}
    for q in qs: by_yp.setdefault((q['year'], q['paper']), []).append(q)
    for L in by_yp.values(): L.sort(key=qkey)
    for (y, p), L in by_yp.items():
        n, long_ = n_of(p), pname(p)
        rel = f'{DIR}/{y}-gs{n}.html'
        can = f'{B.SITE_URL}{pb}{rel}'
        title = f'UPSC Mains {y} GS Paper {n} Questions with Model Answers ({PAPERS[p][2]}) | Learn with Anil'
        desc = (f'All {len(L)} questions of the UPSC Civil Services (Main) {y} General Studies Paper {n} ({PAPERS[p][2]}), each with a model answer on its own page '
                f'by Learn with Anil. Questions free; answers with the ₹{price} PYQ Pass.')
        lede = esc(f'UPSC Civil Services (Main) Examination {y}, {long_}. {len(L)} questions, 250 marks. Tap a question for its model answer.')
        other = ' · '.join(f'<a href="{yy}-gs{n}.html">{yy}</a>' for yy in years if yy != y and (yy, p) in by_yp)
        others = ' · '.join(f'<a href="{y}-gs{n_of(pp)}.html">GS {n_of(pp)}</a>' for pp in PAPERS if pp != p and (y, pp) in by_yp)
        box = (f'<section class="course"><div class="chead"><div><p class="ck">UPSC Civil Services (Main) {y} · GS Paper {n}</p>'
               f'<h2>{esc(PAPERS[p][2])}</h2></div><div class="cbuy"><a class="cta" href="{buyurl}" data-buy>Get the PYQ Pass · ₹{price}</a></div></div>'
               f'<h3>All {len(L)} questions</h3><ol class="clist">' + ''.join(card(q, man) for q in L) + '</ol></section>')
        body = (CSS + f'<p>Same paper, other years: {other}. Same year, other papers: {others}. <a href="./">All UPSC Mains PYQs (year-wise and subject-wise)</a>.</p>'
                + howto + box + buy + flip_js())
        out[rel] = B.static_page(1, title, desc, can, f'UPSC Mains {y} GS Paper {n} with model answers', lede, body, crumbs0 + [(f'{y} GS {n}', can)], conf)
        js = unlock_js(B.PAY.get('api'), man, files.get(pkey(L[0])), EXAM)
        for i, q in enumerate(L):
            arel = f'{DIR}/{apage(q)}'
            acan = f'{B.SITE_URL}{pb}{arel}'
            num = re.match(r'\d+', q['qno']).group()
            sib = [x for x in L if x is not q and re.match(r'\d+', x['qno']).group() == num]
            part, ps = parts[(p, q['part_no'])]
            qbox = (f'<div class="mbox"><div class="cmeta">Question · {esc(meta(q, show_part=False))}</div><p class="mqt">{esc(q["text"])}</p>'
                    f'<div class="cmeta" style="margin:10px 0 0">Syllabus: <a href="{ps}.html">{esc(part)}</a> · {esc(q["topic"])}</div></div>')
            if q['id'] in free:
                abox = f'<div class="mbox"><div class="cmeta" style="color:var(--good)">Model answer · free sample</div><div class="mans">{free[q["id"]]}</div></div>'
            elif files.get(pkey(q)):
                abox = (f'<div class="mbox"><div class="cmeta" id="anshead">Model answer</div><div class="mans" data-ans="{q["id"]}"><div class="mlock">'
                        f'🔒 This model answer (key words, numbered points and diagrams) opens with the ₹{price} PYQ Pass. '
                        f'If you have the pass, it opens here by itself on the phone you registered.<br><a class="cta" href="{buyurl}">Get the PYQ Pass · ₹{price}</a></div></div></div>')
            else:
                abox = ('<div class="mbox"><div class="cmeta">Model answer</div><div class="mlock">The model answers for this paper are being written and checked; '
                        'they are added year by year, newest first.</div></div>')
            nav = ('<div class="cacts mnav">'
                   + (f'<a class="cta alt" href="{apage(L[i - 1])}">← Q{L[i - 1]["qno"]}</a>' if i else '')
                   + f'<a class="cta alt" href="{ppage(q)}">All {len(L)} questions</a>'
                   + (f'<a class="cta" href="{apage(L[i + 1])}">Next: Q{L[i + 1]["qno"]} →</a>' if i + 1 < len(L) else '') + '</div>')
            sibbox = (f'<section class="course"><p class="ck nt">The other part{"s" if len(sib) > 1 else ""} of Q{num}</p><ol class="clist">'
                      + ''.join(card(x, man) for x in sib) + '</ol></section>' if sib else '')
            body = (CSS + f'<section class="course"><p class="ck nt">UPSC Civil Services (Main) {y} · GS Paper {n} · Q{q["qno"]}</p>' + qbox + abox + nav + '</section>'
                    + sibbox + ('' if q['id'] in free else buy) + js)
            title = f'{short(q["text"], 70)} – UPSC Mains {y} GS {n} Q{q["qno"]} Model Answer | Learn with Anil'
            desc = short(f'UPSC Mains {y} GS Paper {n} Q{q["qno"]}: {q["text"]} Model answer with key words, points and diagrams by Learn with Anil.', 300)
            out[arel] = B.static_page(1, title, desc, acan, f'UPSC Mains {y} GS {n} · Q{q["qno"]}: model answer', esc(f'{long_} · {part}.'), body,
                                      crumbs0 + [(f'{y} GS {n}', f'{B.SITE_URL}{pb}{DIR}/{ppage(q)}'), (f'Q{q["qno"]}', acan)], conf)
    # subject-wise: one page per syllabus part
    by_part = {}
    for q in qs: by_part.setdefault((q['paper'], q['part_no']), []).append(q)
    for (p, pno), L in by_part.items():
        n = n_of(p)
        part, ps = parts[(p, pno)]
        rel = f'{DIR}/{ps}.html'
        can = f'{B.SITE_URL}{pb}{rel}'
        topics = {}
        for q in sorted(L, key=lambda q: (-q['year'], qkey(q))): topics.setdefault(q['topic'], []).append(q)
        title = f'UPSC Mains {part} Questions with Answers (GS Paper {n}, {years[-1]}–{years[0]}) | Learn with Anil'
        desc = (f'{len(L)} UPSC Civil Services Mains GS Paper {n} previous questions on {part}, {years[-1]}–{years[0]}, grouped by topic, '
                f'each with a model answer by Learn with Anil. Questions free; answers with the ₹{price} PYQ Pass.')
        lede = esc(f'Every UPSC Mains question on {part} (GS Paper {n}) from {years[-1]} to {years[0]}: {len(L)} questions in {len(topics)} topics, newest first.')
        sibl = ' · '.join(f'<a href="{s}.html">{esc(nm)}</a>' for (pp, _), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]) if pp == p and s != ps)
        sec = [f'<h3>{esc(t)} <span style="font-weight:400;color:var(--muted);font-size:15px">· asked {len(TL)} time{"s" if len(TL) > 1 else ""}</span></h3>'
               f'<ol class="clist">' + ''.join(card(q, man, show_year=True, show_part=False) for q in TL) + '</ol>' for t, TL in topics.items()]
        box = (f'<section class="course"><div class="chead"><div><p class="ck">UPSC Mains · GS Paper {n} · subject-wise</p><h2>{esc(part)}</h2>'
               f'<p class="lead">{len(L)} questions, {years[-1]}–{years[0]}.</p></div>'
               f'<div class="cbuy"><a class="cta" href="{buyurl}" data-buy>Get the PYQ Pass · ₹{price}</a></div></div>' + ''.join(sec) + '</section>')
        body = (CSS + f'<p>{esc(pname(p))}. Other parts of this paper: {sibl}. <a href="./">All UPSC Mains PYQs</a>.</p>' + howto + box + buy + flip_js())
        out[rel] = B.static_page(1, title, desc, can, f'UPSC Mains {part}: previous questions with answers', lede, body, crumbs0 + [(f'GS {n} · {part}', can)], conf)
    # the Mains index: year-wise and subject-wise
    yw = []
    for y in years:
        items = [f'<li><div class="cmeta">GS {n_of(p)} · {len(by_yp[(y, p)])} questions · '
                 + ('model answers' if files.get(f'{y}-gs{n_of(p)}') else 'answers coming soon') + f'</div>'
                 f'<a class="qlink" href="{y}-gs{n_of(p)}.html"><b>{esc(pname(p))}</b></a>'
                 f'<div class="cacts"><a class="cta" href="{y}-gs{n_of(p)}.html">Open all {len(by_yp[(y, p)])} questions →</a></div></li>'
                 for p in PAPERS if (y, p) in by_yp]
        yw.append(f'<section class="course"><p class="ck">Civil Services (Main) {y}</p><h2>{y} papers</h2><ol class="clist">' + ''.join(items) + '</ol></section>')
    sw = []
    for p in PAPERS:
        items = []
        for (pp, pno), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]):
            if pp != p: continue
            L = by_part[(pp, pno)]
            tps = list(dict.fromkeys(q['topic'] for q in L))
            items.append(f'<li><div class="cmeta">{len(L)} questions · {esc("; ".join(tps))}</div><a class="qlink" href="{s}.html"><b>{esc(nm)}</b></a>'
                         f'<div class="cacts"><a class="cta alt" href="{s}.html">Open →</a></div></li>')
        if items:
            sw.append(f'<section class="course"><p class="ck">GS Paper {n_of(p)} · subject-wise</p><h2>{esc(PAPERS[p][2])}</h2><ol class="clist">' + ''.join(items) + '</ol></section>')
    body = (CSS + f'<a class="cta" href="#year">Year-wise</a><a class="cta alt" href="#subject">Subject-wise</a>' + howto
            + f'<h2 id="year">Year-wise: {years[0]} to {years[-1]}</h2><p>GS Papers I–III have 20 questions each (Q1–10: 10 marks, 150 words; Q11–20: 15 marks, 250 words). '
              f'GS Paper IV has Section A (questions with parts) and Section B (case studies of 20 marks).</p>' + ''.join(yw)
            + f'<h2 id="subject">Subject-wise: by syllabus part</h2><p>The same {len(qs)} questions sorted by the GS syllabus, so you can see which parts UPSC asks most.</p>'
            + ''.join(sw) + buy)
    title = f'UPSC Mains Previous Year Questions with Model Answers (GS 1–4, {years[-1]}–{years[0]}) – Year-wise & Subject-wise | Learn with Anil'
    desc = (f'All {len(qs)} UPSC Civil Services Mains General Studies questions of {years[-1]}–{years[0]} (GS Papers I, II, III and IV), year-wise and subject-wise, '
            f'each with a model answer by Learn with Anil. Questions free; answers with the ₹{price} PYQ Pass.')
    lede = esc(f'{len(qs)} real UPSC Mains GS questions from {years[-1]} to {years[0]}, each with a model answer on its own page: pick a year and paper, '
               f'or a syllabus part to see every question UPSC has asked on it.')
    out[f'{DIR}/index.html'] = B.static_page(1, title, desc, base, 'UPSC Mains PYQs with model answers', lede, body, crumbs0, conf)
    # the UPSC CSE hub
    def prelims_box(B):
        pl = getattr(B, 'PRE_LIVE', None)
        if not pl: return '<section class="course"><p class="ck">UPSC Civil Services · Prelims</p><h2>Prelims PYQs</h2><p class="lead">Upcoming.</p></section>'
        n, ys, np_ = pl
        yr = f'{ys[0]}–{ys[-1]}' if len(ys) > 1 else str(ys[0])
        return (f'<section class="course"><p class="ck">UPSC Civil Services · Prelims</p><h2>Prelims PYQs with answers</h2>'
                f'<p class="lead">General Studies Paper I and CSAT, {yr}: {n} questions from UPSC\'s official papers with UPSC\'s answer keys and explanations, in English and Hindi.</p>'
                f'<ol class="clist"><li><div class="cmeta">{np_} papers</div><a class="qlink" href="/upsc-prelims/pyqs.html"><b>Year-wise papers</b></a>'
                f'<div class="cacts"><a class="cta" href="/upsc-prelims/pyqs.html">Open the papers →</a></div></li>'
                f'<li><div class="cmeta">quizzes, timed tests, subject-wise</div><a class="qlink" href="/upsc-prelims/"><b>Practice app</b></a>'
                f'<div class="cacts"><a class="cta" href="/upsc-prelims/">Open UPSC Prelims →</a></div></li></ol></section>')
    hub = (CSS + f'<section class="course"><p class="ck">UPSC Civil Services · Mains</p><h2>Mains PYQs with model answers</h2>'
           f'<p class="lead">General Studies Papers I–IV, {years[-1]}–{years[0]}: {len(qs)} questions from UPSC\'s official papers, each with a model answer on its own page.</p>'
           f'<ol class="clist"><li><div class="cmeta">{len(years)} years × 4 papers</div><a class="qlink" href="{DIR}/#year"><b>Year-wise</b></a>'
           f'<div class="cacts"><a class="cta" href="{DIR}/#year">Open year-wise →</a></div></li>'
           f'<li><div class="cmeta">by GS syllabus part</div><a class="qlink" href="{DIR}/#subject"><b>Subject-wise</b></a>'
           f'<div class="cacts"><a class="cta" href="{DIR}/#subject">Open subject-wise →</a></div></li></ol></section>'
           + prelims_box(B) + buy + flip_js())
    out['index.html'] = B.static_page(0, 'UPSC Civil Services (CSE) Mains PYQs with Model Answers – GS 1 to 4 | Learn with Anil',
                                      f'UPSC Civil Services Mains previous year questions {years[-1]}–{years[0]}: GS Papers I–IV, year-wise and subject-wise, each with a model answer by Learn with Anil.',
                                      B.SITE_URL + pb, 'UPSC Civil Services (CSE)', esc('Mains previous questions with model answers, year-wise and subject-wise.'),
                                      hub, [('Home', B.SITE_URL + '/'), ('UPSC Civil Services', B.SITE_URL + pb)], conf)
    return out
