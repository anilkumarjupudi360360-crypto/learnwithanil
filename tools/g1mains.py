"""APPSC Group-1 Mains previous questions with model answers (Anil, 31 Oct 2026).

Anil: "add group-1 PYQs mains questions and answers into website ... in group-1 tile add prelims and mains tiles ... in mains
tile add pyqs year wise and subject wise". Papers II, III and IV of the 2020, 2023 and 2025 Mains, 270 questions; Anil (1 Nov
2026): "ok do for paper 5...and only questions for essay": Paper V (90 questions, with answers) and Paper I (27 essay topics,
questions only, no model essays). The questions are public (crawlable pages); the model answers, written by Learn with Anil,
are in the ₹45 PYQ Pass, except the free sample (Q1(a) and Q1(b) of each paper).

Data (src/appsc-group-1/mains-pyqs/):
    questions.json   [{id, paper, year, qno, part_no, part, topic, text}]  (Papers I-IV from the Answer Writing Tool Kit;
                     Paper V from the official papers via the S&T book's PYQ chapter; essay qno is "II(b)" = Section II, topic (b))
    answers.json     {key: "bk-g1m-ans", files: {"<year>-p<n>": "<sealed bundle in src/books>"}, n, free: {id: answer}}
                     (tools/g1m_seal.py)
Each sealed bundle (one per paper and year; AES-256-GCM, one key, additional data "bk-g1m-ans") holds {id: answer HTML}; an
answer page asks the payments script for the key (action "mock", any bk- id needs a valid PYQ Pass) and fills the answer in.

Pages (all under /appsc-group-1/mains-pyqs/), in the box design of the course cards (Anil, 1 Nov 2026: "i want every mains
answer in seperate page ... mains tile > 2025 paper-1 > all questions in one page > click on question ... answer on another
page ... all questions & answer in each page must be in a box design"):
    index.html                    year-wise and subject-wise lists (boxes)
    <year>-paper-<n>.html         one paper of one year: every question as a card, linking to its answer page
    <year>-paper-<n>-q<1a>.html   one question and its model answer (Papers II-V; the essay paper has no answers)
    paper-<n>-<part slug>.html    one syllabus part of one paper, all three years, grouped by topic (cards)
Answer markup (key words, points and diagrams): see tools/g1m_render.py; answers are sealed and published as ready HTML.
"""
import html, json, os, re, shutil
import g1m_render

DIR = 'mains-pyqs'
PAPERS = {'I': (1, 'General Essay'),
          'II': (2, 'History, Culture & Geography of India and Andhra Pradesh'),
          'III': (3, 'Polity, Constitution, Governance, Law & Ethics'),
          'IV': (4, 'Economy & Development of India and Andhra Pradesh'),
          'V': (5, 'Science, Technology & Environmental Issues')}
ESSAY = 'I'   # questions only: no model essays
ROMAN = {'I': 1, 'II': 2, 'III': 3}
YEARS = (2025, 2023, 2020)
HELD = {2025: 'May 2025 (Notification 12/2023)', 2023: 'June 2023 (Notification 28/2022)', 2020: 'December 2020 (Notification 27/2018)'}
esc = lambda s: html.escape(str(s), quote=True)


def slug(s):
    x = re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and').replace("'", ''))).strip('-')
    return x if len(x) <= 60 else x[:60].rsplit('-', 1)[0]


def md(t):
    """Answer markup -> HTML (escaped)."""
    out = []
    for para in t.strip().split('\n\n'):
        lines = [l for l in para.split('\n') if l.strip()]
        bold = lambda s: re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', esc(s))
        if lines and all(l.startswith('- ') for l in lines):
            out.append('<ul>' + ''.join(f'<li>{bold(l[2:])}</li>' for l in lines) + '</ul>')
        elif lines:
            out.append(f'<p>{bold(" ".join(lines))}</p>')
    return ''.join(out)


def load(src):
    d = os.path.join(src, 'appsc-group-1', DIR)
    qp, ap = os.path.join(d, 'questions.json'), os.path.join(d, 'answers.json')
    if not os.path.exists(qp): return [], {}
    qs = json.load(open(qp, encoding='utf-8'))
    man = json.load(open(ap, encoding='utf-8')) if os.path.exists(ap) else {}
    return qs, man


def part_pages(qs):
    """(paper, part_no) -> (part name, slug)"""
    out = {}
    for q in qs: out.setdefault((q['paper'], q['part_no']), (q['part'], f'paper-{PAPERS[q["paper"]][0]}-{slug(q["part"])}'))
    return out


def qkey(q):
    m = re.match(r'(\d+)|(I{1,3})\(', q['qno'])
    return (int(m.group(1)) if m.group(1) else ROMAN[m.group(2)], q['qno'])


def qlabel(q):
    if q['paper'] == ESSAY:
        sec, x = q['qno'].rstrip(')').split('(')
        return f'{q["year"]} · Paper I · Section {sec} ({x})'
    return f'{q["year"]} · Paper {q["paper"]} · Q{q["qno"]}'


CSS = ('<style>' + g1m_render.CSS + '.mans p{font-weight:400;margin:0 0 8px}.mans ul{margin:0 0 8px;padding-left:22px}.mans li{margin:2px 0}'
       '.mbox{border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:var(--bg);margin:12px 0 0}'
       '.mqt{font-weight:700;font-size:18px;line-height:1.45;margin:4px 0 0;white-space:pre-line;overflow-wrap:anywhere}'
       '.mlock{background:var(--accent-soft);border-radius:10px;padding:12px 14px;margin:6px 0 0;font-size:15.5px}.mlock .cta{margin:10px 0 0}'
       'ol.clist li b{overflow-wrap:anywhere}.qlink{color:var(--ink);text-decoration:none}.qlink:hover b{text-decoration:underline}'
       '.cta.green{background:#0E7A43;border-color:#0E7A43;color:#fff}.mdata{color:var(--muted);font-size:14.5px;margin:6px 0 0}'
       '.mnav{display:flex;flex-wrap:wrap;gap:0 4px;margin-top:6px}.course + .course{margin-top:18px}.course p.lead{margin:0 0 4px;color:var(--muted)}.course .ck.nt{text-transform:none}</style>')


def aslug(q): return q['qno'].replace('(', '').replace(')', '').lower()
def apage(q): return f'{q["year"]}-paper-{PAPERS[q["paper"]][0]}-q{aslug(q)}.html'
def ppage(q): return f'{q["year"]}-paper-{PAPERS[q["paper"]][0]}.html'
def pkey(q): return f'{q["year"]}-p{PAPERS[q["paper"]][0]}'
def marks(q): return 50 if q['paper'] == ESSAY else 10


def short(t, n):
    t = ' '.join(t.split())
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0].rstrip(',;:') + '…'


def flip_js():
    """Lock labels become ticks on a device with a valid PYQ Pass."""
    return ("<script>(function(){try{var a=(JSON.parse(localStorage.getItem('lwa-passes-v1')||'null')||{}).all||{};"
            "if(a.paid&&new Date(a.pyq+'T23:59:59+05:30')>=new Date())document.querySelectorAll('[data-lk]').forEach(function(e){e.textContent='✓ Model answer →'})}catch(e){}})();</script>")


def unlock_js(api, man, file):
    """Fills the locked answer in place for a device with a valid PYQ Pass (registered student)."""
    if not api or not file: return ''
    return ("<script>(function(){var API=" + json.dumps(api) + ",KID=" + json.dumps(man['key']) + ",FILE=" + json.dumps(file) + """;
function J(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
var els=document.querySelectorAll('[data-ans]');if(!els.length||!window.crypto||!crypto.subtle||!window.TextEncoder)return;
var a=(J('lwa-passes-v1')||{}).all||{},s=J('lwa-appsc-g2-student-v1');if(!a.paid||!(new Date(a.pyq+'T23:59:59+05:30')>=new Date())||!s||!s.phone)return;
function dev(){try{var d=localStorage.getItem('lwa-device');if(!d){d=Math.random().toString(36).slice(2)+Date.now().toString(36);localStorage.setItem('lwa-device',d)}return d}catch(e){return ''}}
function msg(t){els.forEach(function(e){var l=e.querySelector('.mlock');if(l)l.textContent=t})}
msg('Opening your model answer…');
var ck='lwa-key-'+KID,c=J(ck);
(c&&c.key?Promise.resolve(c):fetch(API,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify({action:'mock',exam:'appsc-group-1',id:KID,phone:s.phone,email:s.email||'',device:dev()})}).then(function(r){return r.json()}).then(function(r){
if(!r||!r.ok)throw new Error((r&&r.error)||'');try{localStorage.setItem(ck,JSON.stringify({key:r.key}))}catch(_){}return r}))
.then(function(r){return fetch('/books/'+FILE).then(function(x){if(!x.ok)throw new Error('');return x.arrayBuffer()}).then(function(buf){var b=new Uint8Array(buf);
return crypto.subtle.importKey('raw',Uint8Array.from(atob(r.key),function(c){return c.charCodeAt(0)}),'AES-GCM',false,['decrypt']).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:b.slice(0,12),additionalData:new TextEncoder().encode(KID)},k,b.slice(12))})})})
.then(function(p){var A=JSON.parse(new TextDecoder().decode(p));els.forEach(function(e){var t=A[e.getAttribute('data-ans')];if(t){e.innerHTML=t;var h=document.getElementById('anshead');if(h)h.textContent='Model answer · PYQ Pass'}})})
.catch(function(err){try{localStorage.removeItem(ck)}catch(_){}msg((err&&err.message)||'Could not open the answer. Please check your connection and reload the page.')});})();</script>""")


def card(q, man, parts, show_year=False, show_part=True):
    """One question as a box card (like the course paper cards): meta line, the question (a link to its answer page), a button."""
    bits = ([f'{q["year"]} · Paper {q["paper"]}'] if show_year else []) + [qlabel(q).split(' · ', 2)[-1], f'{marks(q)} marks']
    if show_part: bits.append(f'{q["part"]} · {q["topic"]}')
    data = f'<p class="mdata">This question came with {esc(q["data"])}</p>' if q.get('data') else ''
    if q['paper'] == ESSAY:
        return f'<li id="{q["id"]}"><div class="cmeta">{esc(" · ".join(bits))}</div><b>{esc(q["text"])}</b>{data}</li>'
    href = apage(q)
    btn = (f'<a class="cta green" href="{href}">✓ Free model answer →</a>' if q['id'] in man.get('free', {})
           else f'<a class="cta" href="{href}" data-lk>🔒 Model answer →</a>')
    return (f'<li id="{q["id"]}"><div class="cmeta">{esc(" · ".join(bits))}</div><a class="qlink" href="{href}"><b>{esc(q["text"])}</b></a>{data}'
            f'<div class="cacts">{btn}</div></li>')


def pages(B, conf):
    """{path under the exam folder: html} for the Mains PYQ pages; copies the sealed answers into /books/."""
    qs, man = load(B.SRC)
    if not qs: return {}
    files = man.get('files') or {}
    if files:
        os.makedirs(os.path.join(B.DIST, 'site', 'books'), exist_ok=True)
        for f in files.values(): shutil.copy(os.path.join(B.SRC, 'books', f), os.path.join(B.DIST, 'site', 'books', f))
    pb, price = conf['pb'], B.PAY['pyq_price']
    base = f'{B.SITE_URL}{pb}{DIR}/'
    crumbs0 = [('Home', B.SITE_URL + '/'), (conf['name'], B.SITE_URL + pb), ('Mains PYQs', base)]
    parts = part_pages(qs)
    free = man.get('free', {})
    nans = sum(q['paper'] != ESSAY for q in qs)
    ap = [p for p in PAPERS if p != ESSAY and any(q['paper'] == p for q in qs)]
    aps = ', '.join(ap[:-1]) + ' and ' + ap[-1]
    buy = (f'<div class="buy"><div><b>Model answers for all {nans} questions</b><p>Every Group-1 Mains question of 2020, 2023 and 2025 (Papers {aps}) '
           f'with a model answer written the way a top APPSC candidate would: key words and an introduction, every part of the question in numbered points, diagrams, flowcharts, tables or maps, the Andhra Pradesh angle and a conclusion. '
           f'Included in the ₹{price} PYQ Pass, with every previous paper, mock test series and study book on the site.</p>'
           f'<p class="muted">₹{price} · {B.PYQ_VALID} · pay by UPI, card or net banking</p></div><a class="cta" href="{pb}?buy=pyq">Get it for ₹{price}</a></div>')
    howto = (f'<p class="note">Tap a question to open its model answer on its own page. Q1(a) and Q1(b) of every paper are free; the rest open with the '
             f'₹{price} PYQ Pass on the phone you registered in the app. Answers are by Learn with Anil (Jupudi Anil Kumar), not by APPSC; facts as of October 2026.</p>')
    howto_e = (f'<p class="note">Paper I is the essay paper: 9 topics in 3 sections of 3, and candidates write one essay from each section '
               f'(50 marks each, 150 in all). These are the real topics only, with no model essays. Practice essay topics on every syllabus part are in the '
               f'<a href="{pb}#mains">Answer Writing Tool Kit</a> (PDF, in the ₹{price} PYQ Pass).</p>')
    out = {}
    by_yp = {}
    for q in qs: by_yp.setdefault((q['year'], q['paper']), []).append(q)
    for L in by_yp.values(): L.sort(key=qkey)
    # one page per paper per year: every question as a card
    for (y, p), L in by_yp.items():
        n, pname = PAPERS[p]
        E = p == ESSAY
        rel = f'{DIR}/{y}-paper-{n}.html'
        can = f'{B.SITE_URL}{pb}{rel}'
        if E:
            title = f'APPSC Group 1 Mains {y} Paper I Essay Topics (General Essay Question Paper) | Learn with Anil'
            desc = (f'All 9 essay topics of the APPSC Group 1 Mains {y} Paper I (General Essay), held {HELD[y]}, section-wise, '
                    f'with each topic\'s syllabus theme. Free to read.')
            lede = esc(f'APPSC Group-I Mains {y}, Paper I: General Essay. Held in {HELD[y]}. Three sections of three topics each; candidates write one essay from each section.')
        else:
            title = f'APPSC Group 1 Mains {y} Paper {p} Questions with Model Answers ({pname}) | Learn with Anil'
            desc = (f'All {len(L)} questions of the APPSC Group 1 Mains {y} Paper {p} ({pname}), held {HELD[y]}, each with a model answer on its own page by Learn with Anil. '
                    f'Questions free; answers with the ₹{price} PYQ Pass.')
            lede = esc(f'APPSC Group-I Mains {y}, Paper {p}: {pname}. Held in {HELD[y]}. 15 questions with an internal choice (a) or (b), 10 marks each, '
                       f'so 30 questions in all. Tap a question for its model answer.')
        other = ' · '.join(f'<a href="{yy}-paper-{n}.html">{yy}</a>' for yy in YEARS if yy != y and (yy, p) in by_yp)
        others = ' · '.join(f'<a href="{y}-paper-{PAPERS[pp][0]}.html">Paper {pp}</a>' for pp in PAPERS if pp != p and (y, pp) in by_yp)
        box = (f'<section class="course"><div class="chead"><div><p class="ck">APPSC Group-1 Mains {y} · Paper {p} · held {HELD[y]}</p>'
               f'<h2>{esc(pname)}</h2></div>'
               + ('' if E else f'<div class="cbuy"><a class="cta" href="{pb}?buy=pyq" data-buy>Get the PYQ Pass · ₹{price}</a></div>') + '</div>'
               f'<h3>All {len(L)} {"essay topics" if E else "questions"}</h3><ol class="clist">' + ''.join(card(q, man, parts) for q in L) + '</ol></section>')
        body = (CSS + f'<p>Same paper, other years: {other}. Same year, other papers: {others}. <a href="./">All Mains PYQs (year-wise and subject-wise)</a>.</p>'
                + (howto_e if E else howto) + box + ('' if E else buy + flip_js()))
        out[rel] = B.static_page(1, title, desc, can, f'APPSC Group 1 Mains {y} Paper I essay topics' if E else f'APPSC Group 1 Mains {y} Paper {p} with model answers',
                                 lede, body, crumbs0 + [(f'{y} Paper {p}', can)], conf)
        if E: continue
        # one page per question: the question and its model answer
        js = unlock_js(B.PAY.get('api'), man, files.get(pkey(L[0])))
        for i, q in enumerate(L):
            arel = f'{DIR}/{apage(q)}'
            acan = f'{B.SITE_URL}{pb}{arel}'
            num = re.match(r'\d+', q['qno']).group()
            alt = next((x for x in L if x is not q and re.match(r'\d+', x['qno']).group() == num), None)
            part, ps = parts[(p, q['part_no'])]
            data = f'<p class="mdata">This question came with {esc(q["data"])}</p>' if q.get('data') else ''
            qbox = (f'<div class="mbox"><div class="cmeta">Question · Q{q["qno"]} · 10 marks</div><p class="mqt">{esc(q["text"])}</p>{data}'
                    f'<div class="cmeta" style="margin:10px 0 0">Syllabus: <a href="{ps}.html">{esc(part)}</a> · {esc(q["topic"])}</div></div>')
            if q['id'] in free:
                abox = f'<div class="mbox"><div class="cmeta" style="color:var(--good)">Model answer · free sample</div><div class="mans">{free[q["id"]]}</div></div>'
            elif files.get(pkey(q)):
                abox = (f'<div class="mbox"><div class="cmeta" id="anshead">Model answer</div><div class="mans" data-ans="{q["id"]}"><div class="mlock">'
                        f'🔒 This model answer (key words, numbered points, diagrams and the AP angle) opens with the ₹{price} PYQ Pass. '
                        f'If you have the pass, it opens here by itself on the phone you registered.<br><a class="cta" href="{pb}?buy=pyq">Get the PYQ Pass · ₹{price}</a></div></div></div>')
            else:
                abox = '<div class="mbox"><div class="cmeta">Model answer</div><div class="mlock">Coming soon.</div></div>'
            nav = ('<div class="cacts mnav">'
                   + (f'<a class="cta alt" href="{apage(L[i - 1])}">← Q{L[i - 1]["qno"]}</a>' if i else '')
                   + f'<a class="cta alt" href="{ppage(q)}">All {len(L)} questions</a>'
                   + (f'<a class="cta" href="{apage(L[i + 1])}">Next: Q{L[i + 1]["qno"]} →</a>' if i + 1 < len(L) else '') + '</div>')
            altbox = (f'<section class="course"><p class="ck nt">The other choice in Q{num} (answer either one in the exam)</p><ol class="clist">{card(alt, man, parts)}</ol></section>' if alt else '')
            body = (CSS + f'<section class="course"><p class="ck nt">APPSC Group-1 Mains {y} · Paper {p} · Q{q["qno"]}</p>' + qbox + abox + nav + '</section>'
                    + altbox + ('' if q['id'] in free else buy) + js)
            sq = short(q['text'], 70)
            title = f'{sq} – APPSC Group 1 Mains {y} Paper {p} Q{q["qno"]} Model Answer | Learn with Anil'
            desc = short(f'APPSC Group 1 Mains {y} Paper {p} Q{q["qno"]}: {q["text"]} Model answer with key words, points and diagrams by Learn with Anil.', 300)
            lede = esc(f'{pname} · {part}. Held in {HELD[y]}.')
            out[arel] = B.static_page(1, title, desc, acan, f'{y} Paper {p} · Q{q["qno"]}: model answer', lede, body,
                                      crumbs0 + [(f'{y} Paper {p}', f'{B.SITE_URL}{pb}{DIR}/{ppage(q)}'), (f'Q{q["qno"]}', acan)], conf)
    # one page per syllabus part (subject-wise)
    by_part = {}
    for q in qs: by_part.setdefault((q['paper'], q['part_no']), []).append(q)
    for (p, pno), L in by_part.items():
        n, pname = PAPERS[p]
        part, ps = parts[(p, pno)]
        E = p == ESSAY
        rel = f'{DIR}/{ps}.html'
        can = f'{B.SITE_URL}{pb}{rel}'
        topics = {}
        for q in L: topics.setdefault(q['topic'], []).append(q)
        if E:
            title = f'APPSC Group 1 Mains Essay Topics on {part} (Paper I, 2020–2025) | Learn with Anil'
            desc = (f'{len(L)} APPSC Group 1 Mains Paper I essay topic{"s" if len(L) > 1 else ""} on {part}, from the 2020, 2023 and 2025 papers, grouped by theme. Free to read.')
            lede = esc(f'Every APPSC Group-I Mains essay topic on {part} (Paper I) from the 2020, 2023 and 2025 papers: {len(L)} topic{"s" if len(L) > 1 else ""}, newest first.')
        else:
            title = f'APPSC Group 1 Mains {part} Questions with Answers (Paper {p}, 2020–2025) | Learn with Anil'
            desc = (f'{len(L)} APPSC Group 1 Mains Paper {p} previous questions on {part}, from the 2020, 2023 and 2025 papers, grouped by topic, '
                    f'each with a model answer by Learn with Anil. Questions free; answers with the ₹{price} PYQ Pass.')
            lede = esc(f'Every APPSC Group-I Mains question on {part} (Paper {p}) from the 2020, 2023 and 2025 papers: {len(L)} questions in {len(topics)} topics, '
                       f'newest first. Tap a question for its model answer.')
        sib = ' · '.join(f'<a href="{s}.html">{esc(nm)}</a>' for (pp, _), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]) if pp == p and s != ps)
        yc = {y: sum(q['year'] == y for q in L) for y in YEARS}
        sec = []
        for t, TL in topics.items():
            TL.sort(key=lambda q: (-q['year'], qkey(q)))
            sec.append(f'<h3>{esc(t)} <span style="font-weight:400;color:var(--muted);font-size:15px">· asked {len(TL)} time{"s" if len(TL) > 1 else ""}</span></h3>'
                       f'<ol class="clist">' + ''.join(card(q, man, parts, show_year=True, show_part=False) for q in TL) + '</ol>')
        box = (f'<section class="course"><div class="chead"><div><p class="ck">APPSC Group-1 Mains · Paper {p} · subject-wise</p><h2>{esc(part)}</h2>'
               f'<p class="lead">{len(L)} {"essay topics" if E else "questions"}: ' + ', '.join(f'{yc[y]} in {y}' for y in YEARS) + '.</p></div>'
               + ('' if E else f'<div class="cbuy"><a class="cta" href="{pb}?buy=pyq" data-buy>Get the PYQ Pass · ₹{price}</a></div>') + '</div>'
               + ''.join(sec) + '</section>')
        body = (CSS + f'<p>Paper {p}: {esc(pname)}. Other parts of this paper: {sib}. <a href="./">All Mains PYQs</a>.</p>'
                + (howto_e if E else howto) + box + ('' if E else buy + flip_js()))
        out[rel] = B.static_page(1, title, desc, can, f'APPSC Group 1 Mains essay topics: {part}' if E else f'APPSC Group 1 Mains {part}: previous questions with answers', lede, body,
                                 crumbs0 + [(f'Paper {p} · {part}', can)], conf)
    # the index: year-wise and subject-wise, in boxes
    yw = []
    for y in YEARS:
        items = []
        for p in PAPERS:
            if (y, p) not in by_yp: continue
            L = by_yp[(y, p)]
            meta = f'Paper {p} · ' + ('9 essay topics · questions only' if p == ESSAY else f'{len(L)} questions · model answers')
            items.append(f'<li><div class="cmeta">{meta}</div><a class="qlink" href="{y}-paper-{PAPERS[p][0]}.html"><b>{esc(PAPERS[p][1])}</b></a>'
                         f'<div class="cacts"><a class="cta" href="{y}-paper-{PAPERS[p][0]}.html">Open all {len(L)} {"topics" if p == ESSAY else "questions"} →</a></div></li>')
        yw.append(f'<section class="course"><p class="ck">{y} Mains · held {HELD[y]}</p><h2>{y} papers</h2><ol class="clist">' + ''.join(items) + '</ol></section>')
    sw = []
    for p, (n, pname) in PAPERS.items():
        items = []
        for (pp, pno), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]):
            if pp != p: continue
            L = by_part[(pp, pno)]
            tps = list(dict.fromkeys(q['topic'] for q in L))
            unit = ('topic' if len(L) == 1 else 'topics') if p == ESSAY else 'questions'
            items.append(f'<li><div class="cmeta">{len(L)} {unit} · {esc("; ".join(tps))}</div><a class="qlink" href="{s}.html"><b>{esc(nm)}</b></a>'
                         f'<div class="cacts"><a class="cta alt" href="{s}.html">Open →</a></div></li>')
        if items:
            sw.append(f'<section class="course"><p class="ck">Paper {p} · subject-wise</p><h2>{esc(pname)}</h2><ol class="clist">' + ''.join(items) + '</ol></section>')
    body = (CSS + f'<a class="cta" href="#year">Year-wise</a><a class="cta alt" href="#subject">Subject-wise</a>'
            f'<a class="cta alt" href="{pb}#mains">Answer Writing Tool Kit (PDF)</a>' + howto
            + f'<h2 id="year">Year-wise: 2025, 2023 and 2020 papers</h2><p>Papers II to V have 15 questions each with an internal choice, (a) or (b), 10 marks each. '
              f'Paper I (Essay) has 9 topics in 3 sections; candidates write one essay from each.</p>' + ''.join(yw)
            + f'<h2 id="subject">Subject-wise: by syllabus part</h2><p>The same {nans} questions and {len(qs) - nans} essay topics sorted by syllabus part, so you can see which parts APPSC asks most.</p>'
            + ''.join(sw)
            + '<p class="note">Paper I (General Essay): the real topics only, with no model essays. Practice essay topics are in the Answer Writing Tool Kit.</p>'
            + buy)
    title = 'APPSC Group 1 Mains Previous Year Questions with Model Answers (2020, 2023, 2025) – Year-wise & Subject-wise | Learn with Anil'
    desc = (f'All {nans} APPSC Group 1 Mains questions of 2020, 2023 and 2025 for Paper II (History & Geography), Paper III (Polity & Ethics), Paper IV (Economy) '
            f'and Paper V (Science, Technology & Environment), each with a model answer by Learn with Anil, plus the {len(qs) - nans} Paper I essay topics; '
            f'year-wise and subject-wise. Questions free; answers with the ₹{price} PYQ Pass.')
    lede = esc(f'{nans} real APPSC Group-I Mains questions from the 2020, 2023 and 2025 papers (Papers {aps}), each with a model answer on its own page, '
               f'and the {len(qs) - nans} Paper I essay topics: pick a year and paper, or a syllabus part to see every question APPSC has asked on it.')
    out[f'{DIR}/index.html'] = B.static_page(1, title, desc, base, 'APPSC Group 1 Mains PYQs with model answers', lede, body, crumbs0, conf)
    return out


def tiles(conf, qs_n):
    """The Mains tiles on the APPSC Group-1 home page."""
    pb = conf['pb']
    return (f'<a class="etile" href="{pb}{DIR}/#year"><span class="etile-k">01 · Mains PYQs</span><b>Year-wise</b>'
            f'<span class="etile-p">The 2025, 2023 and 2020 Mains: all {qs_n} questions of Papers II–V, each with a model answer, and the Paper I essay topics.</span>'
            f'<span class="etile-price">✓ Questions free · answers in the pass</span></a>'
            f'<a class="etile" href="{pb}{DIR}/#subject"><span class="etile-k">02 · Mains PYQs</span><b>Subject-wise</b>'
            f'<span class="etile-p">The same questions by syllabus part: essay themes, history, geography, polity, ethics, economy, science, technology and environment.</span>'
            f'<span class="etile-price">✓ Questions free · answers in the pass</span></a>'
            f'<a class="etile" href="#mains"><span class="etile-k">03 · Answer writing</span><b>Answer Writing Tool Kit</b>'
            f'<span class="etile-p">Four PDF books (Papers I–IV): every previous question sorted by syllabus, with practice questions.</span>'
            f'<span class="etile-price" data-paidtxt="✓ Included in your PYQ Pass">🔒 Included in the PYQ Pass</span></a>')
