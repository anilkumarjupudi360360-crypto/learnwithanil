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
import mains_design as D
from g1mains import CSS, slug, short, flip_js, unlock_js

EXAM = 'upsc-cse'
DIR = 'mains-pyqs'
PAPERS = {'GS1': (1, 'General Studies Paper I', 'Indian Heritage and Culture, History and Geography of the World and Society'),
          'GS2': (2, 'General Studies Paper II', 'Governance, Constitution, Polity, Social Justice and International Relations'),
          'GS3': (3, 'General Studies Paper III', 'Technology, Economic Development, Bio-diversity, Environment, Security and Disaster Management'),
          'GS4': (4, 'General Studies Paper IV', 'Ethics, Integrity and Aptitude')}
AN_PAPERS = {'AN1': (1, 'Anthropology Paper I', 'Foundations of Anthropology, Human Evolution, Culture, Society and Human Genetics'),
             'AN2': (2, 'Anthropology Paper II', 'Indian Anthropology: Indian Society, Caste, Village and Tribal India')}
YEARS = (2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019)
FREE = ('1', '2', '1(a)', '1(b)')   # free sample answers: the first two questions of every paper
esc = lambda s: html.escape(str(s), quote=True)
# The two Mains courses on the UPSC CSE pages (Anil, 1 Nov 2026: GS 1-4, then "complete anthropology" with model answers).
# pp: prefix of page names ("2026-gs1.html", "2026-paper-1.html"); kk: key of the sealed bundle per paper ("2026-gs1", "2026-an1").
COURSES = {
  'gs': dict(dir='mains-pyqs', pp='gs', kk='gs', papers=PAPERS, seo='UPSC Mains', crumb='Mains PYQs', pfx='GS', plabel='GS Paper',
             subj='General Studies', part_word='GS syllabus part', free_note='Q1 and Q2 of every paper are free',
             structure=('GS Papers I–III have 20 questions each (Q1–10: 10 marks, 150 words; Q11–20: 15 marks, 250 words). '
                        'GS Paper IV has Section A (questions with parts) and Section B (case studies of 20 marks).'),
             what='Every GS question', index_h='UPSC Mains PYQs with model answers'),
  'an': dict(dir='anthropology-pyqs', pp='paper-', kk='an', papers=AN_PAPERS, seo='UPSC Anthropology Optional', crumb='Anthropology PYQs',
             pfx='Paper', plabel='Anthropology Paper', subj='Anthropology', part_word='Anthropology syllabus part',
             free_note='the first two answers of every paper, Q1(a) and Q1(b), are free',
             structure=('Each paper has 8 questions in two sections (attempt 5): Q1 and Q5 are compulsory short notes of 10 marks, about 150 words each; '
                        'the other questions have parts of 20 and 15 marks. Every part is listed separately below.'),
             what='Every Anthropology question part', index_h='UPSC Anthropology optional PYQs with model answers'),
}


def conf_for(B):
    """The page settings static_page needs."""
    return dict(id=EXAM, dir=EXAM, name='UPSC Civil Services', seo='UPSC CSE', pb=f'/{EXAM}/', board='UPSC', l2=dict(gf=''), keyshort='',
                nav=('Mains PYQs →', f'/{EXAM}/{DIR}/'),
                foot=('Questions are from UPSC\'s official Civil Services (Main) question papers. Model answers are by Jupudi Anil Kumar, '
                      f'Learn with Anil (Instagram: @{B.INSTAGRAM}). Not affiliated with UPSC.'))


def load(src, code='gs'):
    d = os.path.join(src, EXAM, COURSES[code]['dir'])
    qp, ap = os.path.join(d, 'questions.json'), os.path.join(d, 'answers.json')
    if not os.path.exists(qp): return [], {}
    qs = json.load(open(qp, encoding='utf-8'))
    man = json.load(open(ap, encoding='utf-8')) if os.path.exists(ap) else {}
    return qs, man


def qkey(q): return (int(re.match(r'\d+', q['qno']).group()), q['qno'])
def aslug(q): return q['qno'].replace('(', '').replace(')', '').lower()
def n_of(p): return {**PAPERS, **AN_PAPERS}[p][0]   # module-level for build.py's llms.txt


def helpers(C):
    """Page-name and wording helpers for one course."""
    P = C['papers']
    def n_of(p): return P[p][0]
    def ppage(q): return f'{q["year"]}-{C["pp"]}{n_of(q["paper"])}.html'
    def apage(q): return f'{q["year"]}-{C["pp"]}{n_of(q["paper"])}-q{aslug(q)}.html'
    def pkey(q): return f'{q["year"]}-{C["kk"]}{n_of(q["paper"])}'
    def pname(p): return f'{P[p][1]}: {P[p][2]}'
    def part_pages(qs):
        out = {}
        for q in qs: out.setdefault((q['paper'], q['part_no']), (q['part'], f'{C["pp"]}{n_of(q["paper"])}-{slug(q["part"])}'))
        return out
    def meta(q, show_year=False, show_part=True):
        bits = ([f'{q["year"]} · {C["pfx"]} {n_of(q["paper"])}'] if show_year else []) + [f'Q{q["qno"]}', f'{q["marks"]} marks']
        if q.get('words'): bits.append(f'{q["words"]} words')
        if show_part: bits.append(f'{q["part"]} · {q["topic"]}')
        return ' · '.join(bits)
    def card(q, man, show_year=False, show_part=True, parts=None):
        """One question as a numbered row (tools/mains_design.py)."""
        href = apage(q)
        if q['id'] in man.get('free', {}): btn = f'<a class="mp free" href="{href}">✓ Free model answer</a>'
        elif (man.get('files') or {}).get(pkey(q)): btn = f'<a class="mp" href="{href}" data-lk>🔒 Model answer</a>'
        else: btn = f'<a class="mp" href="{href}">Model answer: coming soon</a>'
        text = q['text'] if len(q['text']) <= 420 else short(q['text'], 380)   # long case studies: the full text is on the answer page
        bits = ([f'{q["year"]} {C["pfx"]} {n_of(q["paper"])}'] if show_year else []) + [f'{q["marks"]} marks'] + ([f'{q["words"]} words'] if q.get('words') else [])
        m = esc(' · '.join(bits))
        if show_part:
            part, ps = (parts or {}).get((q['paper'], q['part_no']), (q['part'], None))
            m += ' · ' + (f'<a href="{ps}.html">{esc(part)}</a>' if ps else esc(part)) + f' · {esc(q["topic"])}'
        return D.qrow(q['id'], q['qno'], 'Q', text, href, m, btn)
    return n_of, ppage, apage, pkey, pname, part_pages, meta, card


def tag_of(C, p):
    return C['papers'][p][1].replace('General Studies', 'GS').replace('Anthropology ', '')


def course_pages(B, code):
    """{path under /upsc-cse/: html} for one Mains course (GS or Anthropology); copies its sealed answers into /books/."""
    C = COURSES[code]; DIR = C['dir']; PAPERS = C['papers']
    n_of, ppage, apage, pkey, pname, part_pages, meta, card = helpers(C)
    qs, man = load(B.SRC, code)
    if not qs: return {}, None
    conf = conf_for(B)
    files = man.get('files') or {}
    if files:
        os.makedirs(os.path.join(B.DIST, 'site', 'books'), exist_ok=True)
        for f in files.values(): shutil.copy(os.path.join(B.SRC, 'books', f), os.path.join(B.DIST, 'site', 'books', f))
    pb, price = conf['pb'], B.PAY['pyq_price']
    base = f'{B.SITE_URL}{pb}{DIR}/'
    crumbs0 = [('Home', B.SITE_URL + '/'), ('UPSC Civil Services', B.SITE_URL + pb), (C['crumb'], base)]
    parts = part_pages(qs)
    free = man.get('free', {})
    allfree = len(free) >= man.get('n', 10 ** 9)   # Anil, 2 Nov 2026: "make both mains free" (GS), then "ok" to Anthropology too: every written answer free
    payline = 'Questions and model answers free.' if allfree else f'Questions free; answers with the ₹{price} PYQ Pass.'
    years = [y for y in YEARS if any(q['year'] == y for q in qs)]
    done = sorted({int(k[:4]) for k in files}, reverse=True)
    buyurl = '/upsc-epfo/?buy=pyq'   # the pass checkout lives in the exam apps (one ₹45 PYQ Pass for the whole site)
    buy = (f'<div class="buy mbuy"><div><b>{C["seo"]} model answers</b><p>{C["what"]} of the Civil Services (Main) Examinations {years[-1]}–{years[0]} with a '
           f'model answer: key words and an introduction, every part of the question in numbered points, diagrams, flowcharts or tables, and a conclusion. '
           f'Included in the ₹{price} PYQ Pass, with every previous paper, mock test series and study book on the site.</p>'
           f'<p class="muted">₹{price} · {B.PYQ_VALID} · pay by UPI, card or net banking</p></div><a class="cta" href="{buyurl}">Get it for ₹{price}</a></div>')
    if allfree:   # a small box under every free answer: what the pass still adds (Anil, 2 Nov 2026)
        buy = (f'<div class="buy mbuy"><div><b>Every model answer here is free</b><p>The ₹{price} PYQ Pass opens the rest of the site for 12 months: '
               f'UPSC Prelims GS Paper I and CSAT with explanations, practice quizzes and timed tests, UPSC CAPF and EPFO, the previous papers of every APPSC, '
               f'TSPSC, police and SSC exam, every mock test series and the study books.</p>'
               f'<p class="muted">₹{price} · {B.PYQ_VALID} · pay by UPI, card or net banking</p></div><a class="cta" href="{buyurl}">Get it for ₹{price}</a></div>')
    status = ('Model answers are ready for every paper.' if set(done) >= set(years)
              else f'Model answers are ready for {", ".join(map(str, done))}; the other years are being added, newest first.' if done
              else 'Model answers are being added year by year, newest first.')
    howto = (f'<p class="note">Tap a question to open its model answer on its own page. '
             + ('Every model answer is free. ' if allfree else f'{C["free_note"][0].upper() + C["free_note"][1:]}; the rest open with the ₹{price} PYQ Pass on the phone you registered in the app. ')
             + f'The model answers are fuller than UPSC\'s 150/250-word limits so that you learn the content; '
             f'write within the limit in the exam. {status} Answers are by Learn with Anil (Jupudi Anil Kumar), not by UPSC.</p>')
    passbtn = '' if allfree else f'<a class="cta" href="{buyurl}" data-buy style="margin:0">Get the PYQ Pass · ₹{price}</a>'
    wrap = lambda p, h: f'<div{D.pv(p)}>{h}</div>'
    def head(h2, sub):
        return (f'<div style="display:flex;flex-wrap:wrap;gap:8px 16px;align-items:end;justify-content:space-between;margin:22px 0 0">'
                f'<div><h2 style="margin:0">{h2}</h2><p class="qm" style="margin:2px 0 0">{sub}</p></div>{passbtn}</div>')
    out = {}
    by_yp = {}
    for q in qs: by_yp.setdefault((q['year'], q['paper']), []).append(q)
    for L in by_yp.values(): L.sort(key=qkey)
    for (y, p), L in by_yp.items():
        n, long_ = n_of(p), pname(p)
        rel = f'{DIR}/{y}-{C["pp"]}{n}.html'
        can = f'{B.SITE_URL}{pb}{rel}'
        title = f'{C["seo"]} {y} {"GS " if code == "gs" else ""}Paper {n} Questions with Model Answers ({PAPERS[p][2]}) | Learn with Anil'
        desc = (f'All {len(L)} questions of the UPSC Civil Services (Main) {y} {C["subj"]} Paper {n} ({PAPERS[p][2]}), each with a model answer on its own page '
                f'by Learn with Anil. {payline}')
        lede = esc(f'UPSC Civil Services (Main) Examination {y}, {long_}. {len(L)} {"questions" if code == "gs" else "question parts"}, 250 marks. Tap a question for its model answer.')
        sw = ('<div class="msw"><span class="lbl">Year</span>'
              + D.chips([(str(yy), f'{yy}-{C["pp"]}{n}.html', yy == y) for yy in years if (yy, p) in by_yp])
              + '<span class="lbl">Paper</span>'
              + D.chips([(tag_of(C, pp), f'{y}-{C["pp"]}{n_of(pp)}.html', pp == p) for pp in PAPERS if (y, pp) in by_yp]) + '</div>')
        body = (CSS + wrap(p, sw + howto + head(esc(PAPERS[p][2]), f'{len(L)} {"questions" if code == "gs" else "question parts"} · 250 marks')
                           + '<ol class="qrows">' + ''.join(card(q, man, parts=parts) for q in L) + '</ol>'
                           + f'<p><a href="./">All {C["seo"]} PYQs, year-wise and subject-wise</a></p>' + buy) + flip_js())
        page = B.static_page(1, title, desc, can, f'{C["seo"]} {y} {C["plabel"]} {n} with model answers', lede, body, crumbs0 + [(f'{y} {C["pfx"]} {n}', can)], conf)
        out[rel] = D.rehero(page, D.hero(f'UPSC Civil Services (Main) {y} · {tag_of(C, p)}', [D.LOOK[p][0]], paper=p))
        js = unlock_js(B.PAY.get('api'), man, files.get(pkey(L[0])), EXAM)
        for i, q in enumerate(L):
            arel = f'{DIR}/{apage(q)}'
            acan = f'{B.SITE_URL}{pb}{arel}'
            num = re.match(r'\d+', q['qno']).group()
            sib = [x for x in L if x is not q and re.match(r'\d+', x['qno']).group() == num]
            part, ps = parts[(p, q['part_no'])]
            tags = [f'Q{q["qno"]}', f'{q["marks"]} marks'] + ([f'{q["words"]} words'] if q.get('words') else []) + [f'{y} · {tag_of(C, p)}']
            qbox = (f'<div class="mq"><div class="tags">' + ''.join(f'<span>{esc(t)}</span>' for t in tags) + f'</div><p class="mqt">{esc(q["text"])}</p>'
                    f'<p class="syl">Syllabus: <a href="{ps}.html">{esc(part)}</a> · {esc(q["topic"])}</p></div>')
            if q['id'] in free:
                abox = f'<div class="ma"><div class="ah"><span>Model answer · free{"" if allfree else " sample"}</span></div><div class="mans">{free[q["id"]]}</div></div>'
            elif files.get(pkey(q)):
                abox = (f'<div class="ma"><div class="ah"><span id="anshead">Model answer</span></div><div class="mans" data-ans="{q["id"]}"><div class="mlock">'
                        f'🔒 This model answer (key words, numbered points and diagrams) opens with the ₹{price} PYQ Pass. '
                        f'If you have the pass, it opens here by itself on the phone you registered.<br><a class="cta" href="{buyurl}">Get the PYQ Pass · ₹{price}</a></div></div></div>')
            else:
                abox = ('<div class="ma"><div class="ah"><span>Model answer</span></div><div class="mlock">The model answers for this paper are being written and checked; '
                        'they are added year by year, newest first.</div></div>')
            nav = D.answer_nav((f'Q{L[i - 1]["qno"]}', apage(L[i - 1]), short(L[i - 1]['text'], 70)) if i else None,
                               (f'All {len(L)} questions', ppage(q)),
                               (f'Q{L[i + 1]["qno"]}', apage(L[i + 1]), short(L[i + 1]['text'], 70)) if i + 1 < len(L) else None)
            sibbox = (f'<section class="osec"><h2>The other part{"s" if len(sib) > 1 else ""} of Q{num}</h2><ol class="qrows">'
                      + ''.join(card(x, man, parts=parts) for x in sib) + '</ol></section>' if sib else '')
            body = CSS + wrap(p, qbox + abox + nav + sibbox + ('' if q['id'] in free and not allfree else buy)) + js
            title = f'{short(q["text"], 70)} – {C["seo"]} {y} {C["pfx"]} {n} Q{q["qno"]} Model Answer | Learn with Anil'
            desc = short(f'{C["seo"]} {y} {C["plabel"]} {n} Q{q["qno"]}: {q["text"]} Model answer with key words, points and diagrams by Learn with Anil.', 300)
            page = B.static_page(1, title, desc, acan, f'{C["seo"]} {y} {C["pfx"]} {n} · Q{q["qno"]}: model answer', esc(f'{long_} · {part}.'), body,
                                 crumbs0 + [(f'{y} {C["pfx"]} {n}', f'{B.SITE_URL}{pb}{DIR}/{ppage(q)}'), (f'Q{q["qno"]}', acan)], conf)
            out[arel] = D.rehero(page, D.hero(f'UPSC Civil Services (Main) {y} · {tag_of(C, p)}', [D.LOOK[p][0]], slim=True, paper=p))
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
        title = f'{C["seo"]} {part} Questions with Answers ({C["plabel"]} {n}, {years[-1]}–{years[0]}) | Learn with Anil'
        desc = (f'{len(L)} UPSC Civil Services Mains {C["plabel"]} {n} previous questions on {part}, {years[-1]}–{years[0]}, grouped by topic, '
                f'each with a model answer by Learn with Anil. {payline}')
        lede = esc(f'Every {C["seo"]} question on {part} ({C["plabel"]} {n}) from {years[-1]} to {years[0]}: {len(L)} questions in {len(topics)} topics, newest first.')
        sw = (f'<div class="msw"><span class="lbl">{tag_of(C, p)} parts</span>'
              + D.chips([(nm, f'{s}.html', s == ps) for (pp, _), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]) if pp == p]) + '</div>')
        sec = [f'<h3 class="tsec">{esc(t)} <span>· asked {len(TL)} time{"s" if len(TL) > 1 else ""}</span></h3>'
               f'<ol class="qrows">' + ''.join(card(q, man, show_year=True, show_part=False) for q in TL) + '</ol>' for t, TL in topics.items()]
        body = (CSS + wrap(p, sw + howto + head(esc(part), f'{len(L)} questions, {years[-1]}–{years[0]}') + ''.join(sec)
                           + f'<p><a href="./">All {C["seo"]} PYQs, year-wise and subject-wise</a></p>' + buy) + flip_js())
        page = B.static_page(1, title, desc, can, f'{C["seo"]} {part}: previous questions with answers', lede, body, crumbs0 + [(f'{C["pfx"]} {n} · {part}', can)], conf)
        out[rel] = D.rehero(page, D.hero(f'{C["seo"]} · {pname(p)}', [D.LOOK[p][0]], paper=p))
    # the Mains index: paper cards with a chip per year, then the syllabus parts of every paper
    cards, sw = [], []
    for p in PAPERS:
        ys = [y for y in years if (y, p) in by_yp]
        if not ys: continue
        n = n_of(p)
        np_ = sum(1 for (pp, _) in parts if pp == p)
        anchor = f's-{C["pp"]}{n}'
        cards.append(D.paper_card(p, tag_of(C, p), PAPERS[p][2], f'{ys[0]}-{C["pp"]}{n}.html',
                                  f'{len(by_yp[(ys[0], p)])} {"questions" if code == "gs" else "question parts"} in {ys[0]} · model answers',
                                  [(y, f'{y}-{C["pp"]}{n}.html') for y in ys], (f'Subject-wise: {np_} syllabus parts', f'#{anchor}')))
        rows = [(nm, f'{s}.html', f'{len(by_part[(pp, pno)])} questions', '; '.join(dict.fromkeys(q['topic'] for q in by_part[(pp, pno)])))
                for (pp, pno), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]) if pp == p]
        sw.append(D.subject_block(p, anchor, tag_of(C, p), PAPERS[p][2], rows))
    body = (CSS + f'<a class="cta" href="#year">Year-wise</a><a class="cta alt" href="#subject">Subject-wise</a>' + howto
            + f'<h2 id="year">Year-wise: pick a paper and a year</h2><p>{C["structure"]}</p><div class="pgrid">' + ''.join(cards) + '</div>'
            + f'<h2 id="subject">Subject-wise: by syllabus part</h2><p>The same {len(qs)} questions sorted by the {C["part_word"].replace(" part", "")}, so you can see which parts UPSC asks most.</p>'
            + ''.join(sw) + buy + D.credits([D.LOOK[p][0] for p in PAPERS]))
    if code == 'gs':
        title = f'UPSC Mains Previous Year Questions with Model Answers (GS 1–4, {years[-1]}–{years[0]}) – Year-wise & Subject-wise | Learn with Anil'
        desc = (f'All {len(qs)} UPSC Civil Services Mains General Studies questions of {years[-1]}–{years[0]} (GS Papers I, II, III and IV), year-wise and subject-wise, '
                f'each with a model answer by Learn with Anil. {payline}')
        lede = esc(f'{len(qs)} real UPSC Mains GS questions from {years[-1]} to {years[0]}, each with a model answer on its own page: pick a year and paper, '
                   f'or a syllabus part to see every question UPSC has asked on it.')
    else:
        title = f'UPSC Anthropology Optional PYQs with Model Answers (Paper 1 & 2, {years[-1]}–{years[0]}) – Year-wise & Topic-wise | Learn with Anil'
        desc = (f'All {len(qs)} UPSC Civil Services Mains Anthropology optional question parts of {years[-1]}–{years[0]} (Papers I and II), year-wise and '
                f'topic-wise, each with a model answer by Learn with Anil. {payline}')
        lede = esc(f'{len(qs)} real UPSC Anthropology optional question parts from {years[-1]} to {years[0]}, each with a model answer on its own page: '
                   f'pick a year and paper, or a syllabus part to see every question UPSC has asked on it.')
    page = B.static_page(1, title, desc, base, C['index_h'], lede, body, crumbs0, conf)
    out[f'{DIR}/index.html'] = D.rehero(page, D.hero(f'UPSC Civil Services (Main) · {C["subj"]} · {years[-1]} to {years[0]}', [D.LOOK[p][0] for p in PAPERS]))
    info = dict(n=len(qs), years=years, npapers=len(by_yp), done=done, files=files, dir=DIR, buy=buy,
                latest={p: max(y for (y, pp) in by_yp if pp == p) for p in PAPERS if any(pp == p for (_, pp) in by_yp)})
    return out, info


def pages(B):
    """{path under /upsc-cse/: html}: the UPSC CSE hub, the Mains GS pages and the Anthropology optional pages."""
    out, info = {}, {}
    for code in COURSES:
        o, inf = course_pages(B, code)
        out.update(o)
        if inf: info[code] = inf
    if 'gs' not in info: return out
    conf = conf_for(B); pb = conf['pb']
    gs, an = info['gs'], info.get('an')
    def yr(ys): return f'{ys[-1]}–{ys[0]}' if len(ys) > 1 else str(ys[0])
    def course_card(code, kick, h2, lead, d):
        C = COURSES[code]
        ph = ''.join(f'<a href="{d["dir"]}/{y}-{C["pp"]}{C["papers"][p][0]}.html" aria-label="{esc(C["papers"][p][1])}, {y}"{D.pv(p)}>'
                     f'{D.img(D.LOOK[p][0], small=True, alt="")}<span class="tag">{esc(tag_of(C, p).replace("GS Paper", "GS"))}</span>{D.go(f"Open {y} paper")}</a>'
                     for p, y in d['latest'].items())
        return (f'<section class="ccard"><div class="ph">{ph}</div><div class="cb"><p class="kick">{kick}</p><h2>{h2}</h2><p class="lead">{lead}</p>'
                f'<div class="row"><a class="cta" href="{d["dir"]}/#year">Year-wise</a><a class="cta alt" href="{d["dir"]}/#subject">Subject-wise</a></div></div></section>')
    def prelims_card():
        pl = getattr(B, 'PRE_LIVE', None)
        if not pl: return '<section class="ccard plain"><div class="cb"><p class="kick">Prelims</p><h2>Prelims PYQs</h2><p class="lead">Upcoming.</p></div></section>'
        n, ys, np_, latest = pl
        y_ = f'{ys[0]}–{ys[-1]}' if len(ys) > 1 else str(ys[0])
        # Anil, 2 Nov 2026: "where is photo here ?" - a photo per paper, like the Mains cards: Sanchi for GS Paper I, Jantar Mantar for CSAT
        ph = ''.join(f'<a href="/upsc-prelims/papers/{slug}.html" aria-label="{"General Studies Paper I" if k == "gs" else "CSAT (Paper II)"}, {y}"{D.pv(pk)}>'
                     f'{D.img(D.LOOK[pk][0], small=True, alt="")}<span class="tag">{"GS Paper I" if k == "gs" else "CSAT"}</span>{D.go(f"Open {y} paper")}</a>'
                     for k, pk in (('gs', 'PGS'), ('csat', 'PCSAT')) if k in latest for y, slug in [latest[k]])
        return (f'<section class="ccard"><div class="ph">{ph}</div><div class="cb"><p class="kick">Prelims · objective</p><h2>Prelims PYQs with answers</h2>'
                f'<p class="lead">General Studies Paper I and CSAT, {y_}: {n} questions in {np_} papers from UPSC\'s official papers with UPSC\'s answer keys and explanations, in English and Hindi. '
                f'Practise them as quizzes, timed tests or subject-wise. Tap a photo for the latest paper.</p>'
                f'<div class="row"><a class="cta" href="/upsc-prelims/pyqs.html">Papers</a><a class="cta alt" href="/upsc-prelims/">Practice app</a></div></div></section>')
    gsc = course_card('gs', 'Mains · General Studies', 'Mains GS PYQs with model answers',
                      f'General Studies Papers I–IV, {yr(gs["years"])}: {gs["n"]} questions from UPSC\'s official papers, each with a model answer on its own page. '
                      f'Tap a photo for the latest paper.', gs)
    anc = (course_card('an', 'Mains · Optional', 'Anthropology optional PYQs with model answers',
                       f'Anthropology Papers I and II, {yr(an["years"])}: {an["n"]} question parts, each with a model answer on its own page.', an) if an else '')
    keys = ([D.LOOK[p][0] for p in PAPERS] + ([D.LOOK[p][0] for p in AN_PAPERS] if an else [])
            + ([D.LOOK['PGS'][0], D.LOOK['PCSAT'][0]] if getattr(B, 'PRE_LIVE', None) else []))
    hub = (CSS + gsc + f'<div class="cpair">{anc}{prelims_card()}</div>'
           + ((gs['buy'].replace('Every GS question', 'Every GS and Anthropology optional question') if an else gs['buy']) if gs['buy'] else (an['buy'] if an else '')) + flip_js() + D.credits(keys))
    page = B.static_page(0, 'UPSC Civil Services (CSE) PYQs – Mains GS 1–4' + (' & Anthropology' if an else '') + ' Model Answers, Prelims GS & CSAT | Learn with Anil',
                         f'UPSC Civil Services previous year questions: Mains GS Papers I–IV ({yr(gs["years"])})'
                         + (f', Anthropology optional Papers I–II ({yr(an["years"])})' if an else '')
                         + ', each with a model answer, and Prelims GS Paper I and CSAT with answer keys, by Learn with Anil.',
                         B.SITE_URL + pb, 'UPSC Civil Services (CSE)', esc('Mains and Prelims previous questions with model answers and answer keys.'),
                         hub, [('Home', B.SITE_URL + '/'), ('UPSC Civil Services', B.SITE_URL + pb)], conf)
    out['index.html'] = D.rehero(page, D.hero('Civil Services Examination · Mains and Prelims', ['north-block']))
    return out
