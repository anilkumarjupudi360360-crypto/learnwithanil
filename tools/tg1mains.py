"""TGPSC Group-I Mains previous questions, questions only (Anil, 8 Nov 2026: "add tg group-1prelims(multiple time cancelled papers
also) and mains", Mains: "Questions only for now"). The 2024 Mains (Notification 02/2024, written 21-27 October 2024): Paper I General
Essay and Papers II-VI, every question in English and Telugu as printed, no model answers.

Data (src/tgpsc-group-1/mains-pyqs/):
    questions.json  [{paper: 1-6, year, section: "I"/"II"/"III", qno: "1" / "3(A)", en, te, passage_en?, passage_te?}]
                    (text typed from the question paper; tables as pipe rows; a data-interpretation "Note" is repeated on each
                    question that uses it and shown once, before the first)
    charts.json     {"<year>-<paper>-<first qno>": chart} the bar, pie and line charts of Paper V, redrawn as SVG from the paper's figures
Pages (under /tgpsc-group-1/mains-pyqs/):
    index.html               year-wise (a card per paper and year) and subject-wise (every section of every paper)
    <year>-paper-<n>.html    one paper of one year: the questions section by section, internal choices joined by "OR"
"""
import html, json, math, os, re

DIR = 'mains-pyqs'
EXAM = 'tgpsc-group-1'
PAPERS = {1: 'General Essay', 2: 'History, Culture and Geography', 3: 'Indian Society, Constitution and Governance', 4: 'Economy and Development',
          5: 'Science & Technology and Data Interpretation', 6: 'Telangana Movement and State Formation'}
PAPERS_TE = {1: 'జనరల్ ఎస్సే', 2: 'చరిత్ర, సంస్కృతి, భూగోళశాస్త్రం', 3: 'భారతీయ సమాజం, రాజ్యాంగం, పరిపాలన', 4: 'ఆర్థిక వ్యవస్థ, అభివృద్ధి',
             5: 'సైన్స్ & టెక్నాలజీ, డేటా ఇంటర్‌ప్రిటేషన్', 6: 'తెలంగాణ ఉద్యమం, రాష్ట్ర ఆవిర్భావం'}
# what each section of a paper asks about (descriptions by Learn with Anil from the questions; the paper prints only "Section I/II/III")
SECTIONS = {1: {'I': 'Society, economy and development', 'II': 'Constitution, justice and culture', 'III': 'Science, environment and management'},
            2: {'I': 'Indian history and culture', 'II': 'Telangana history and culture', 'III': 'Geography of India and Telangana'},
            3: {'I': 'Indian society and social issues', 'II': 'Constitution of India', 'III': 'Governance'},
            4: {'I': 'Indian economy', 'II': 'Telangana economy', 'III': 'Development, environment and change'},
            5: {'I': 'Science and technology', 'II': 'Science and technology: applications and issues', 'III': 'Data interpretation and problem solving'},
            6: {'I': 'The idea of Telangana (1948–1970)', 'II': 'Mobilisation phase (1971–1990)', 'III': 'Towards the formation of Telangana (1991–2014)'}}
ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI'}
HELD = {2024: {1: '22 October 2024', 2: '23 October 2024', 3: '24 October 2024', 4: '25 October 2024', 5: '26 October 2024', 6: '27 October 2024'}}
NOTIF = {2024: 'Notification 02/2024'}
esc = lambda s: html.escape(str(s), quote=True)
COL = ['#2F6DB5', '#D9822B', '#3C9A5F', '#B8463F', '#7A5BB0', '#8C6D2C']

CSS = ('<style>.tgm-sec{margin:26px 0 0}.tgm-sec h2{margin:0 0 4px}.tgm-sec .sm{color:var(--muted);margin:0 0 10px;font-size:14.5px}'
       'ol.tgm{list-style:none;margin:0;padding:0}ol.tgm>li{border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:10px 0}'
       '.tgm .qn{display:inline-block;min-width:44px;font-weight:700;color:var(--accent);margin:0 0 4px}'
       '.tgm .alt{margin:8px 0 0;padding:8px 0 0;border-top:1px dashed var(--line)}.tgm .or{display:block;font-size:12.5px;font-weight:700;letter-spacing:.06em;color:var(--muted);margin:0 0 4px}'
       '.tgm p{margin:0 0 6px;line-height:1.55;overflow-wrap:anywhere}'
       '.tgm .note{border-left:3px solid var(--accent);padding:8px 12px;margin:14px 0 4px;background:var(--accent-soft,rgba(47,109,181,.06));border-radius:0 10px 10px 0}'
       '.tgm .note p{margin:0 0 6px}.tgm figure{margin:10px 0}.tgm figure svg{width:100%;height:auto;max-width:640px;display:block}'
       '.tgm figcaption{color:var(--muted);font-size:12.5px}.tgm .qtbl-wrap{overflow-x:auto}'
       '.tgm-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:12px 0 0}'
       '.tgm-cards a{display:block;border:1px solid var(--line);border-radius:12px;padding:14px;text-decoration:none;color:var(--ink)}'
       '.tgm-cards a:hover{border-color:var(--accent)}.tgm-cards b{display:block;font-size:16.5px}.tgm-cards span{display:block;color:var(--muted);font-size:14px;margin-top:4px}'
       '.tgm-sw{list-style:none;padding:0;margin:8px 0 0}.tgm-sw li{margin:6px 0}.tgm-sw small{color:var(--muted)}</style>')


def load(src):
    p = os.path.join(src, EXAM, DIR, 'questions.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def charts(src):
    p = os.path.join(src, EXAM, DIR, 'charts.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def qnum(q):
    return int(re.match(r'\d+', q['qno']).group())


def groups(L):
    """Questions of one paper and year -> [(section, [[alternatives of one question number], ...])]"""
    out = {}
    for q in sorted(L, key=lambda q: (qnum(q), q['qno'])):
        out.setdefault(q['section'], {}).setdefault(qnum(q), []).append(q)
    return [(s, list(d.values())) for s, d in sorted(out.items(), key=lambda kv: ['I', 'II', 'III', 'IV'].index(kv[0]))]


def sec_name(p, s):
    d = SECTIONS.get(p, {}).get(s)
    return f'Section {s}' + (f': {d}' if d else '')


# ---------- the Paper V figures, redrawn as SVG (text in the page font, so Telugu shapes correctly) ----------
def _t(x, y, s, size=13, anchor='middle', weight=400, fill='currentColor'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{esc(s)}</text>'


def svg_stack(c):
    W, H, L, T, B = 640, 400, 46, 92, 56
    ch = H - T - B; n = len(c['bars']); bw = (W - L - 20) / n
    o = [_t(W / 2, 20, c['title'], 15, weight=700), _t(W / 2, 40, c['title_te'], 13)]
    lx = 12
    for i, (en, te) in enumerate(c['cats']):
        x = lx + i * 125
        o.append(f'<rect x="{x}" y="54" width="12" height="12" fill="{COL[i]}"/>' + _t(x + 17, 64, en, 12, 'start') + _t(x + 17, 80, te, 11.5, 'start'))
    for v in range(0, 101, 5):
        y = T + ch - ch * v / 100
        o.append(f'<line x1="{L}" x2="{W - 10}" y1="{y:.1f}" y2="{y:.1f}" stroke="currentColor" stroke-opacity=".15"/>' + _t(L - 6, y + 4, v, 11, 'end'))
    for j, (en, te, vals) in enumerate(c['bars']):
        x = L + j * bw + bw * .2; acc = 0
        for i, v in enumerate(vals):
            y1 = T + ch - ch * (acc + v) / 100
            o.append(f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw * .6:.1f}" height="{ch * v / 100:.1f}" fill="{COL[i]}" stroke="#fff" stroke-width=".8"/>')
            acc += v
        o.append(_t(x + bw * .3, H - B + 18, en, 12.5) + _t(x + bw * .3, H - B + 35, te, 11.5))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(c["title"])}: stacked bar diagram">' + ''.join(o) + '</svg>'


def svg_pies(c):
    W, H = 640, 330
    o = []
    for k, p in enumerate(c['pies']):
        cx, cy, r = 160 + k * 320, 150, 112
        a = -90.0
        for i, (lab, v) in enumerate(p['parts']):
            a2 = a + 360 * v / 100
            x1, y1 = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
            x2, y2 = cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2))
            o.append(f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {1 if v > 50 else 0},1 {x2:.1f},{y2:.1f} Z" fill="{COL[i]}" stroke="#fff" stroke-width="1.5"/>')
            m = math.radians((a + a2) / 2)
            tx, ty = cx + r * .62 * math.cos(m), cy + r * .62 * math.sin(m)
            o.append(_t(tx, ty - 2, lab, 13, weight=700, fill='#fff') + _t(tx, ty + 13, f'{v}%', 12, fill='#fff'))
            a = a2
        o.append(_t(cx, cy + r + 28, p['title'], 13.5, weight=700) + _t(cx, cy + r + 46, p['title_te'], 12.5))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Two pie charts: {esc(c["pies"][0]["title"])} and {esc(c["pies"][1]["title"])}">' + ''.join(o) + '</svg>'


def svg_lines(c, g):
    W, H, L, T, B, R = 640, 360, 62, 62, 52, 80
    ymax = g.get('ymax', c['ymax']); cw, ch = W - L - R, H - T - B; xs = c['x']
    X = lambda i: L + cw * i / (len(xs) - 1)
    Y = lambda v: T + ch - ch * v / ymax
    o = [_t(W / 2, 22, g['title'], 15, weight=700), _t(W / 2, 42, g['title_te'], 13)]
    for v in range(0, ymax + 1, c['step']):
        o.append(f'<line x1="{L}" x2="{W - R + 10}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="currentColor" stroke-opacity=".15"/>' + _t(L - 6, Y(v) + 4, v, 11, 'end'))
    for i, x in enumerate(xs): o.append(_t(X(i), H - B + 18, x, 12))
    o.append(_t(W / 2 - R / 2, H - 8, c['xlabel'], 12.5) + f'<text x="14" y="{T + ch / 2}" font-size="12.5" text-anchor="middle" fill="currentColor" transform="rotate(-90 14 {T + ch / 2})">{esc(c["ylabel"])}</text>')
    for k, (name, vals) in enumerate(g['series']):
        pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{COL[k]}" stroke-width="2.4"/>'
                 + ''.join(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" fill="{COL[k]}"/>' for i, v in enumerate(vals))
                 + _t(W - R + 16, Y(vals[-1]) + 4 + (k - 1) * 3, name, 12.5, 'start', 700, COL[k]))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(g["title"])}: line graph of {", ".join(s[0] for s in g["series"])}">' + ''.join(o) + '</svg>'


def figure(c):
    if c['type'] == 'stack100': svgs = [svg_stack(c)]
    elif c['type'] == 'pies': svgs = [svg_pies(c)]
    else: svgs = [svg_lines(c, g) for g in c['charts']]
    return ''.join(f'<figure>{s}</figure>' for s in svgs[:-1]) + (f'<figure>{svgs[-1]}<figcaption>Figure redrawn by Learn with Anil from the one in the question paper.</figcaption></figure>')


def qitem(B, alts, note=''):
    parts = []
    for i, q in enumerate(alts):
        lab = q['qno'] if len(alts) > 1 else str(qnum(q))
        parts.append((f'<div class="alt"><span class="or">OR / లేదా</span>' if i else '<div>')
                     + f'<span class="qn">{esc(lab)}</span>{B.qtext_html(q["en"])}' + (f'<div lang="te">{B.qtext_html(q["te"])}</div>' if q.get('te') else '') + '</div>')
    return note + f'<li id="q{qnum(alts[0])}">' + ''.join(parts) + '</li>'


def pages(B, conf):
    qs = load(B.SRC)
    if not qs: return {}
    CH = charts(B.SRC)
    pb = conf['pb']; base = f'{B.SITE_URL}{pb}{DIR}/'
    crumbs0 = [('Home', B.SITE_URL + '/'), (conf['name'], B.SITE_URL + pb), ('Mains PYQs', base)]
    by_yp = {}
    for q in qs: by_yp.setdefault((q['year'], q['paper']), []).append(q)
    years = sorted({y for y, _ in by_yp}, reverse=True)
    note = ('<p class="note">The real questions only, in English and Telugu as typed from the question paper; Learn with Anil has not written model answers for '
            'these papers yet. The section names are our short descriptions (the paper prints only Section I, II and III). '
            'The Prelims papers (2024, and the cancelled 2023 and 2022 papers) are on this site with answers and explanations.</p>')
    out = {}
    for (y, p), L in sorted(by_yp.items()):
        G = groups(L); nq = sum(len(gs) for _, gs in G); nalt = len(L)
        rel = f'{DIR}/{y}-paper-{p}.html'; can = base + f'{y}-paper-{p}.html'
        E = p == 1
        chips = ' · '.join((f'<b>Paper {ROMAN[pp]}</b>' if pp == p else f'<a href="{y}-paper-{pp}.html">Paper {ROMAN[pp]}</a>') for pp in PAPERS if (y, pp) in by_yp)
        secs = []
        for s, gs in G:
            items, last = [], None
            for g in gs:
                q0 = g[0]; pn = q0.get('passage_en')
                box = ''
                if pn and pn != last:
                    c = CH.get(f'{y}-{p}-{qnum(q0)}')
                    box = (f'<li class="note"><div>{B.qtext_html(pn)}</div>' + (f'<div lang="te">{B.qtext_html(q0["passage_te"])}</div>' if q0.get('passage_te') else '')
                           + (figure(c) if c else '') + '</li>')
                last = pn
                items.append(qitem(B, g, box))
            ch_ = sum(len(g) > 1 for g in gs)
            secs.append(f'<section class="tgm-sec" id="section-{s.lower()}"><h2>{esc(sec_name(p, s))}</h2>'
                        f'<p class="sm">{len(gs)} {"essay questions" if E else "questions"}'
                        + (f', {ch_} with a choice of {"topics" if E else "(A) or (B)"}' if ch_ else '') + '</p>'
                        f'<ol class="tgm">' + ''.join(items) + '</ol></section>')
        body = (CSS + f'<p>{chips}</p>' + note + ''.join(secs)
                + f'<p style="margin-top:22px"><a href="./">All TGPSC Group-I Mains questions, year-wise and subject-wise</a> · '
                  f'<a href="{pb}pyqs.html">Group-I Prelims papers with answers</a></p>')
        what = 'essay topics' if E else 'questions'
        title = f'TGPSC Group 1 Mains {y} Paper {ROMAN[p]} {PAPERS[p]} Question Paper ({"Essay Topics" if E else "Questions"}, English & Telugu) | Learn with Anil'
        desc = (f'The TGPSC (TSPSC) Group-I Mains {y} Paper {ROMAN[p]} ({PAPERS[p]}) question paper, held on {HELD[y][p]} ({NOTIF[y]}): all {nalt} {what} '
                f'in English and Telugu, section by section with the internal choices. Free to read.')
        lede = esc(f'Held on {HELD[y][p]} ({NOTIF[y]}), 3 hours, 150 marks. {nq} {"essay questions" if E else "questions"} in {len(G)} sections'
                   + (f' ({nalt} counting the internal choices)' if nalt != nq else '') + ', in English and Telugu.')
        out[rel] = B.static_page(1, title, desc, can, f'TGPSC Group 1 Mains {y} Paper {ROMAN[p]}: {PAPERS[p]}', lede, body,
                                 crumbs0 + [(f'{y} Paper {ROMAN[p]}', can)], conf)
    # index: year-wise cards, then subject-wise (each section of each paper)
    cards = ''.join(f'<a href="{y}-paper-{p}.html"><b>{y} · Paper {ROMAN[p]}</b><span>{esc(PAPERS[p])} · {PAPERS_TE[p]}</span>'
                    f'<span>{len(by_yp[(y, p)])} {"essay topics" if p == 1 else "questions"}, counting the choices</span></a>'
                    for y in years for p in PAPERS if (y, p) in by_yp)
    sw = []
    for p in PAPERS:
        rows = []
        for y in years:
            if (y, p) not in by_yp: continue
            for s, gs in groups(by_yp[(y, p)]):
                ex = re.sub(r'\s+', ' ', gs[0][0]['en'])
                ex = ex if len(ex) <= 80 else ex[:80].rsplit(' ', 1)[0] + '…'
                rows.append(f'<li><a href="{y}-paper-{p}.html#section-{s.lower()}"><b>{esc(sec_name(p, s))}</b></a> <small>· {y} · {len(gs)} questions · e.g. {esc(ex)}</small></li>')
        if rows: sw.append(f'<h3>Paper {ROMAN[p]}: {esc(PAPERS[p])}</h3><ul class="tgm-sw">' + ''.join(rows) + '</ul>')
    nall = len(qs)
    body = (CSS + note + f'<h2 id="year">Year-wise</h2><p>Each paper has three sections. In Papers II–VI the first two questions of a section are compulsory and the '
            f'others offer a choice of (A) or (B) (Paper V Section III is thirty short data-interpretation problems); in Paper I (General Essay) candidates choose one topic in each section.</p>'
            f'<div class="tgm-cards">{cards}</div>'
            f'<h2 id="subject" style="margin-top:26px">Subject-wise: section by section</h2>' + ''.join(sw)
            + f'<p style="margin-top:22px"><a href="{pb}pyqs.html">TGPSC Group-I Prelims papers with answers and explanations</a></p>')
    ys = ', '.join(map(str, years))
    title = f'TGPSC Group 1 Mains Previous Question Papers {ys} – All Papers, Year-wise & Subject-wise, English & Telugu | Learn with Anil'
    desc = (f'TGPSC (TSPSC) Group-I Mains {ys} question papers: Paper I General Essay and Papers II–VI (History, Culture & Geography; Society, Constitution & Governance; '
            f'Economy & Development; Science & Technology and Data Interpretation; Telangana Movement & State Formation), {nall} questions in English and Telugu, year-wise and subject-wise. Free.')
    lede = esc(f'Every question of the TGPSC Group-I Mains {ys} (Paper I General Essay and Papers II–VI), {nall} in all counting the internal choices, '
               f'in English and Telugu. Pick a paper, or a section of the syllabus.')
    out[f'{DIR}/index.html'] = B.static_page(1, title, desc, base, 'TGPSC Group 1 Mains previous question papers', lede, body, crumbs0, conf)
    return out


def tiles(conf, n):
    pb = conf['pb']
    return (f'<a class="etile" href="{pb}{DIR}/#year"><span class="etile-k">01 · Mains PYQs</span><b>Year-wise</b>'
            f'<span class="etile-p">The 2024 Mains: Paper I General Essay and Papers II–VI, all {n} questions in English and Telugu.</span>'
            f'<span class="etile-price">✓ Free to read · questions only</span></a>'
            f'<a class="etile" href="{pb}{DIR}/#subject"><span class="etile-k">02 · Mains PYQs</span><b>Subject-wise</b>'
            f'<span class="etile-p">The same questions section by section: history, culture, geography, society, Constitution, governance, economy, science and the Telangana movement.</span>'
            f'<span class="etile-price">✓ Free to read · questions only</span></a>')
