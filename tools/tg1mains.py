"""TGPSC Group-I Mains previous questions, questions only (Anil, 8 Nov 2026: "add tg group-1prelims(multiple time cancelled papers
also) and mains", Mains: "Questions only for now"). The 2024 Mains (Notification 02/2024, written 21-27 October 2024): Paper I General
Essay and Papers II-VI, every question in English and Telugu as printed, no model answers.

Data: src/tgpsc-group-1/mains-pyqs/questions.json  [{paper: 1-6, year, section: "I"/"II"/"III", section_title, qno: "1" / "3(A)", en, te}]
Pages (under /tgpsc-group-1/mains-pyqs/):
    index.html               year-wise (a card per paper and year) and subject-wise (every section of every paper)
    <year>-paper-<n>.html    one paper of one year: the questions section by section, internal choices joined by "OR"
"""
import html, json, os, re

DIR = 'mains-pyqs'
EXAM = 'tgpsc-group-1'
PAPERS = {1: 'General Essay', 2: 'History, Culture and Geography', 3: 'Indian Society, Constitution and Governance', 4: 'Economy and Development',
          5: 'Science & Technology and Data Interpretation', 6: 'Telangana Movement and State Formation'}
PAPERS_TE = {1: 'జనరల్ ఎస్సే', 2: 'చరిత్ర, సంస్కృతి, భూగోళశాస్త్రం', 3: 'భారతీయ సమాజం, రాజ్యాంగం, పరిపాలన', 4: 'ఆర్థిక వ్యవస్థ, అభివృద్ధి',
             5: 'సైన్స్ & టెక్నాలజీ, డేటా ఇంటర్‌ప్రిటేషన్', 6: 'తెలంగాణ ఉద్యమం, రాష్ట్ర ఆవిర్భావం'}
ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI'}
HELD = {2024: {1: '22 October 2024', 2: '23 October 2024', 3: '24 October 2024', 4: '25 October 2024', 5: '26 October 2024', 6: '27 October 2024'}}
NOTIF = {2024: 'Notification 02/2024'}
esc = lambda s: html.escape(str(s), quote=True)

CSS = ('<style>.tgm-sec{margin:26px 0 0}.tgm-sec h2{margin:0 0 4px}.tgm-sec .sm{color:var(--muted);margin:0 0 10px;font-size:14.5px}'
       'ol.tgm{list-style:none;margin:0;padding:0}ol.tgm>li{border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:10px 0;background:var(--card,#fff)}'
       '.tgm .qn{display:inline-block;min-width:44px;font-weight:700;color:var(--accent);margin:0 0 4px}'
       '.tgm .alt{margin:8px 0 0;padding:8px 0 0;border-top:1px dashed var(--line)}.tgm .or{display:block;font-size:12.5px;font-weight:700;letter-spacing:.06em;color:var(--muted);margin:0 0 4px}'
       '.tgm p{margin:0 0 6px;line-height:1.55;overflow-wrap:anywhere}.tgm p[lang=te]{color:var(--ink-2,#333)}'
       '.tgm-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:12px 0 0}'
       '.tgm-cards a{display:block;border:1px solid var(--line);border-radius:12px;padding:14px;text-decoration:none;color:var(--ink);background:var(--card,#fff)}'
       '.tgm-cards a:hover{border-color:var(--accent)}.tgm-cards b{display:block;font-size:16.5px}.tgm-cards span{display:block;color:var(--muted);font-size:14px;margin-top:4px}'
       '.tgm-sw{list-style:none;padding:0;margin:8px 0 0}.tgm-sw li{margin:6px 0}.tgm-sw small{color:var(--muted)}</style>')


def load(src):
    p = os.path.join(src, EXAM, DIR, 'questions.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def qnum(q):
    return int(re.match(r'\d+', q['qno']).group())


def groups(L):
    """Questions of one paper and year -> [(section, section_title, [[alternatives of Q1], [alternatives of Q2], ...])]"""
    out = {}
    for q in sorted(L, key=lambda q: (qnum(q), q['qno'])):
        sec = out.setdefault(q['section'], [q.get('section_title', ''), {}])
        sec[1].setdefault(qnum(q), []).append(q)
    return [(s, t, list(d.values())) for s, (t, d) in sorted(out.items(), key=lambda kv: ['I', 'II', 'III', 'IV'].index(kv[0]))]


def sec_name(s, t):
    return f'Section {s}' + (f': {t}' if t else '')


def qitem(alts):
    parts = []
    for i, q in enumerate(alts):
        lab = q['qno'] if len(alts) > 1 else str(qnum(q))
        parts.append((f'<div class="alt"><span class="or">OR / లేదా</span>' if i else '<div>')
                     + f'<span class="qn">{esc(lab)}</span><p>{esc(q["en"])}</p>' + (f'<p lang="te">{esc(q["te"])}</p>' if q.get('te') else '') + '</div>')
    return f'<li id="q{qnum(alts[0])}">' + ''.join(parts) + '</li>'


def pages(B, conf):
    qs = load(B.SRC)
    if not qs: return {}
    pb = conf['pb']; base = f'{B.SITE_URL}{pb}{DIR}/'
    crumbs0 = [('Home', B.SITE_URL + '/'), (conf['name'], B.SITE_URL + pb), ('Mains PYQs', base)]
    by_yp = {}
    for q in qs: by_yp.setdefault((q['year'], q['paper']), []).append(q)
    years = sorted({y for y, _ in by_yp}, reverse=True)
    note = ('<p class="note">The real questions only, in English and Telugu as printed in the question paper; Learn with Anil has not written model answers for '
            'these papers yet. The Prelims papers (2024, and the cancelled 2023 and 2022 papers) are on this site with answers and explanations.</p>')
    out = {}
    for (y, p), L in sorted(by_yp.items()):
        G = groups(L); nq = sum(len(g) for _, _, gs in G for g in gs); nalt = len(L)
        rel = f'{DIR}/{y}-paper-{p}.html'; can = base + f'{y}-paper-{p}.html'
        E = p == 1
        chips = ' · '.join((f'<b>Paper {ROMAN[pp]}</b>' if pp == p else f'<a href="{y}-paper-{pp}.html">Paper {ROMAN[pp]}</a>') for pp in PAPERS if (y, pp) in by_yp)
        secs = ''.join(f'<section class="tgm-sec" id="section-{s.lower()}"><h2>{esc(sec_name(s, t))}</h2>'
                       f'<p class="sm">{len(gs)} {"essay question" if E and len(gs) == 1 else "essay questions" if E else "questions"}'
                       + (f', {sum(len(g) > 1 for g in gs)} with a choice of {"topics" if E else "(A) or (B)"}' if any(len(g) > 1 for g in gs) else '') + '</p>'
                       f'<ol class="tgm">' + ''.join(qitem(g) for g in gs) + '</ol></section>' for s, t, gs in G)
        body = (CSS + f'<p>{chips}</p>' + note + secs
                + f'<p style="margin-top:22px"><a href="./">All TGPSC Group-I Mains questions, year-wise and subject-wise</a> · '
                  f'<a href="{pb}pyqs.html">Group-I Prelims papers with answers</a></p>')
        what = 'essay topics' if E else 'questions'
        title = f'TGPSC Group 1 Mains {y} Paper {ROMAN[p]} {PAPERS[p]} Question Paper ({"Essay Topics" if E else "Questions"}, English & Telugu) | Learn with Anil'
        desc = (f'The TGPSC (TSPSC) Group-I Mains {y} Paper {ROMAN[p]} ({PAPERS[p]}) question paper, held on {HELD[y][p]} ({NOTIF[y]}): all {nalt} {what} '
                f'in English and Telugu, section by section with the internal choices. Free to read.')
        lede = esc(f'Held on {HELD[y][p]} ({NOTIF[y]}), 3 hours, 150 marks. {nq} {"essay questions" if E else "questions"} in {len(G)} sections'
                   + (f' ({nalt} with the internal choices)' if nalt != nq else '') + ', in English and Telugu as printed.')
        out[rel] = B.static_page(1, title, desc, can, f'TGPSC Group 1 Mains {y} Paper {ROMAN[p]}: {PAPERS[p]}', lede, body,
                                 crumbs0 + [(f'{y} Paper {ROMAN[p]}', can)], conf)
    # index: year-wise cards, then subject-wise (each section of each paper)
    cards = ''.join(f'<a href="{y}-paper-{p}.html"><b>{y} · Paper {ROMAN[p]}</b><span>{esc(PAPERS[p])} · {PAPERS_TE[p]}</span>'
                    f'<span>{len(by_yp[(y, p)])} {"essay topics" if p == 1 else "questions"} (with choices)</span></a>'
                    for y in years for p in PAPERS if (y, p) in by_yp)
    sw = []
    for p in PAPERS:
        rows = []
        for y in years:
            if (y, p) not in by_yp: continue
            for s, t, gs in groups(by_yp[(y, p)]):
                topics = '; '.join(re.sub(r'\s+', ' ', g[0]['en'])[:70].rsplit(' ', 1)[0] + '…' for g in gs[:2])
                rows.append(f'<li><a href="{y}-paper-{p}.html#section-{s.lower()}"><b>{esc(sec_name(s, t))}</b></a> <small>· {y} · {len(gs)} questions · e.g. {esc(topics)}</small></li>')
        if rows: sw.append(f'<h3>Paper {ROMAN[p]}: {esc(PAPERS[p])}</h3><ul class="tgm-sw">' + ''.join(rows) + '</ul>')
    nall = len(qs)
    body = (CSS + note + f'<h2 id="year">Year-wise</h2><p>Each paper has three sections. In Papers II–VI the first two questions of each section are compulsory and the '
            f'other three offer a choice of (A) or (B); in Paper I (General Essay) candidates choose one topic in each section.</p>'
            f'<div class="tgm-cards">{cards}</div>'
            f'<h2 id="subject" style="margin-top:26px">Subject-wise: by section of the syllabus</h2>' + ''.join(sw)
            + f'<p style="margin-top:22px"><a href="{pb}pyqs.html">TGPSC Group-I Prelims papers with answers and explanations</a></p>')
    ys = ', '.join(map(str, years))
    title = f'TGPSC Group 1 Mains Previous Question Papers {ys} – All Papers, Year-wise & Subject-wise, English & Telugu | Learn with Anil'
    desc = (f'TGPSC (TSPSC) Group-I Mains {ys} question papers: Paper I General Essay and Papers II–VI (History, Culture & Geography; Society, Constitution & Governance; '
            f'Economy & Development; Science & Technology and Data Interpretation; Telangana Movement & State Formation), {nall} questions in English and Telugu, year-wise and subject-wise. Free.')
    lede = esc(f'Every question of the TGPSC Group-I Mains {ys} (Paper I General Essay and Papers II–VI), {nall} in all counting the internal choices, '
               f'in English and Telugu as printed. Pick a paper, or a section of the syllabus.')
    out[f'{DIR}/index.html'] = B.static_page(1, title, desc, base, 'TGPSC Group 1 Mains previous question papers', lede, body, crumbs0, conf)
    return out


def tiles(conf, n):
    pb = conf['pb']
    return (f'<a class="etile" href="{pb}{DIR}/#year"><span class="etile-k">01 · Mains PYQs</span><b>Year-wise</b>'
            f'<span class="etile-p">The 2024 Mains: Paper I General Essay and Papers II–VI, all {n} questions in English and Telugu.</span>'
            f'<span class="etile-price">✓ Free to read · questions only</span></a>'
            f'<a class="etile" href="{pb}{DIR}/#subject"><span class="etile-k">02 · Mains PYQs</span><b>Subject-wise</b>'
            f'<span class="etile-p">The same questions by section: history, culture, geography, society, Constitution, governance, economy, science and the Telangana movement.</span>'
            f'<span class="etile-price">✓ Free to read · questions only</span></a>')
