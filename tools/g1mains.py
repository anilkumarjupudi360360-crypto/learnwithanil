"""APPSC Group-1 Mains previous questions with model answers (Anil, 31 Oct 2026).

Anil: "add group-1 PYQs mains questions and answers into website ... in group-1 tile add prelims and mains tiles ... in mains
tile add pyqs year wise and subject wise". Papers II, III and IV of the 2020, 2023 and 2025 Mains (no essay paper; Paper V is
not on the site), 270 questions. The questions are public (crawlable pages); the model answers, written by Learn with Anil,
are in the ₹45 PYQ Pass, except the free sample (Q1(a) and Q1(b) of each paper).

Data (src/appsc-group-1/mains-pyqs/):
    questions.json   [{id, paper, year, qno, part_no, part, topic, text}]  (from the Answer Writing Tool Kit)
    answers.json     {key: "bk-g1m-ans", file: "<sealed bundle in src/books>", n, free: {id: answer}}  (tools/g1m_seal.py)
The sealed bundle (AES-256-GCM, additional data "bk-g1m-ans") holds {id: answer} for every question; a page asks the
payments script for the key (action "mock", any bk- id needs a valid PYQ Pass) and fills the answers in place.

Pages (all under /appsc-group-1/mains-pyqs/):
    index.html                    year-wise and subject-wise lists
    <year>-paper-<n>.html         one paper of one year, Q1(a) to Q15(b)
    paper-<n>-<part slug>.html    one syllabus part of one paper, all three years, grouped by topic
Answer markup: paragraphs split by a blank line, "- " bullet lines, **bold**.
"""
import html, json, os, re, shutil

DIR = 'mains-pyqs'
PAPERS = {'II': (2, 'History, Culture & Geography of India and Andhra Pradesh'),
          'III': (3, 'Polity, Constitution, Governance, Law & Ethics'),
          'IV': (4, 'Economy & Development of India and Andhra Pradesh')}
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


def qkey(q): return (int(re.match(r'\d+', q['qno']).group()), q['qno'])


CSS = ('<style>.mans{margin:10px 0 0;border-top:1px dashed var(--line);padding-top:10px}.mans h3{font:700 13px/1.4 "IBM Plex Mono",ui-monospace,monospace;'
       'text-transform:uppercase;letter-spacing:.05em;color:var(--good);margin:0 0 6px}.q .mans p{font-weight:400;white-space:normal;margin:0 0 8px}'
       '.mans ul{margin:0 0 8px;padding-left:22px}.mans li{margin:2px 0}.mlock{background:var(--accent-soft);border-radius:10px;padding:10px 12px;margin:10px 0 0;font-size:15.5px}'
       '.qtopic{display:inline-block;font-size:14px;margin:0 0 6px}.yp{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:10px 0 18px}'
       '.yp a{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;text-decoration:none;color:inherit}'
       '.yp a b{display:block;font-size:17px}.yp a span{color:var(--muted);font-size:14.5px}.ppart{margin:0 0 14px}.ppart a{font-weight:700}'
       '.ppart span{color:var(--muted);font-size:15px}@media (max-width:640px){.yp{grid-template-columns:1fr}}</style>')


def unlock_js(api, man):
    """Fills the locked answers in place for a device with a valid PYQ Pass (registered student)."""
    if not api or not man.get('file'): return ''
    return ("<script>(function(){var API=" + json.dumps(api) + ",KID=" + json.dumps(man['key']) + ",FILE=" + json.dumps(man['file']) + """;
function J(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
var els=document.querySelectorAll('[data-ans]');if(!els.length||!window.crypto||!crypto.subtle||!window.TextEncoder)return;
var a=(J('lwa-passes-v1')||{}).all||{},s=J('lwa-appsc-g2-student-v1');if(!a.paid||!(new Date(a.pyq+'T23:59:59+05:30')>=new Date())||!s||!s.phone)return;
function dev(){try{var d=localStorage.getItem('lwa-device');if(!d){d=Math.random().toString(36).slice(2)+Date.now().toString(36);localStorage.setItem('lwa-device',d)}return d}catch(e){return ''}}
function E(t){return t.replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function B(t){return E(t).replace(/\\*\\*(.+?)\\*\\*/g,'<b>$1</b>')}
function MD(t){return t.trim().split('\\n\\n').map(function(p){var L=p.split('\\n').filter(function(l){return l.trim()});if(!L.length)return'';
if(L.every(function(l){return l.indexOf('- ')===0}))return'<ul>'+L.map(function(l){return'<li>'+B(l.slice(2))+'</li>'}).join('')+'</ul>';return'<p>'+B(L.join(' '))+'</p>'}).join('')}
function msg(t){els.forEach(function(e){var l=e.querySelector('.mlock');if(l)l.textContent=t})}
var ck='lwa-key-'+KID,c=J(ck);
(c&&c.key?Promise.resolve(c):fetch(API,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify({action:'mock',exam:'appsc-group-1',id:KID,phone:s.phone,email:s.email||'',device:dev()})}).then(function(r){return r.json()}).then(function(r){
if(!r||!r.ok)throw new Error((r&&r.error)||'');try{localStorage.setItem(ck,JSON.stringify({key:r.key}))}catch(_){}return r}))
.then(function(r){return fetch('/books/'+FILE).then(function(x){if(!x.ok)throw new Error('');return x.arrayBuffer()}).then(function(buf){var b=new Uint8Array(buf);
return crypto.subtle.importKey('raw',Uint8Array.from(atob(r.key),function(c){return c.charCodeAt(0)}),'AES-GCM',false,['decrypt']).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:b.slice(0,12),additionalData:new TextEncoder().encode(KID)},k,b.slice(12))})})})
.then(function(p){var A=JSON.parse(new TextDecoder().decode(p));els.forEach(function(e){var t=A[e.getAttribute('data-ans')];if(t)e.innerHTML='<h3>Model answer</h3>'+MD(t)})})
.catch(function(err){try{localStorage.removeItem(ck)}catch(_){}msg((err&&err.message)||'Could not open the answers. Please check your connection and reload the page.')});})();</script>""")


def ans_html(q, man, pb, price):
    free = man.get('free', {})
    if q['id'] in free:
        return f'<div class="mans"><h3>Model answer · free sample</h3>{md(free[q["id"]])}</div>'
    if not man.get('file'):
        return '<div class="mans"><p class="mlock">Model answer: coming soon.</p></div>'
    return (f'<div class="mans" data-ans="{q["id"]}"><p class="mlock">🔒 Model answer (about 250 words) with the ₹{price} PYQ Pass. '
            f'<a href="{pb}?buy=pyq">Get the PYQ Pass</a></p></div>')


def q_html(q, man, pb, price, parts, label, show_topic=True):
    pslug = parts[(q['paper'], q['part_no'])][1]
    top = (f'<a class="qtopic" href="{pslug}.html">{esc(q["part"])} · {esc(q["topic"])}</a>' if show_topic else '')
    return (f'<li class="q" id="{q["id"]}"><div class="meta">{esc(label)} · 10 marks</div>{top}<p>{esc(q["text"])}</p>'
            + ans_html(q, man, pb, price) + '</li>')


def pages(B, conf):
    """{path under the exam folder: html} for the Mains PYQ pages; copies the sealed answers into /books/."""
    qs, man = load(B.SRC)
    if not qs: return {}
    if man.get('file'):
        os.makedirs(os.path.join(B.DIST, 'site', 'books'), exist_ok=True)
        shutil.copy(os.path.join(B.SRC, 'books', man['file']), os.path.join(B.DIST, 'site', 'books', man['file']))
    pb, price = conf['pb'], B.PAY['pyq_price']
    base = f'{B.SITE_URL}{pb}{DIR}/'
    crumbs0 = [('Home', B.SITE_URL + '/'), (conf['name'], B.SITE_URL + pb), ('Mains PYQs', base)]
    parts = part_pages(qs)
    nfree = len(man.get('free', {}))
    js = unlock_js(B.PAY.get('api'), man)
    buy = (f'<div class="buy"><div><b>Model answers for all {len(qs)} questions</b><p>Every Group-1 Mains question of 2020, 2023 and 2025 (Papers II, III and IV) '
           f'with a model answer written the way a top APPSC candidate would: introduction, every part of the question, the Andhra Pradesh angle and a conclusion. '
           f'Included in the ₹{price} PYQ Pass, with every previous paper, mock test series and study book on the site.</p>'
           f'<p class="muted">₹{price} · {B.PYQ_VALID} · pay by UPI, card or net banking</p></div><a class="cta" href="{pb}?buy=pyq">Get it for ₹{price}</a></div>')
    howto = (f'<p class="note">The questions are free to read. The model answers open on this page for students with the ₹{price} PYQ Pass '
             f'(register once in the app on this phone, with the same phone number you paid with). The answers to Q1(a) and Q1(b) of every paper are free samples. '
             f'Answers are by Learn with Anil (Jupudi Anil Kumar), not by APPSC; facts and data are as of October 2026.</p>')
    out = {}
    by_yp = {}
    for q in qs: by_yp.setdefault((q['year'], q['paper']), []).append(q)
    # one page per paper per year
    for (y, p), L in by_yp.items():
        n, pname = PAPERS[p]
        rel = f'{DIR}/{y}-paper-{n}.html'
        can = f'{B.SITE_URL}{pb}{rel}'
        L.sort(key=qkey)
        title = f'APPSC Group 1 Mains {y} Paper {p} Questions with Model Answers ({pname}) | Learn with Anil'
        desc = (f'All 30 questions of the APPSC Group 1 Mains {y} Paper {p} ({pname}), held {HELD[y]}, with model answers by Learn with Anil: '
                f'year-wise, with each question\'s syllabus topic. Questions free; answers with the ₹{price} PYQ Pass.')
        other = ' · '.join(f'<a href="{yy}-paper-{n}.html">{yy}</a>' for yy in YEARS if yy != y)
        others = ' · '.join(f'<a href="{y}-paper-{PAPERS[pp][0]}.html">Paper {pp}</a>' for pp in PAPERS if pp != p)
        body = (CSS + f'<p>Same paper, other years: {other}. Same year, other papers: {others}. <a href="./">All Mains PYQs (year-wise and subject-wise)</a>.</p>'
                + howto + f'<h2>All 30 questions with model answers</h2><ol class="qs">'
                + ''.join(q_html(q, man, pb, price, parts, f'{y} · Paper {p} · Q{q["qno"]}') for q in L) + '</ol>' + buy + js)
        lede = esc(f'APPSC Group-I Mains {y}, Paper {p}: {pname}. Held in {HELD[y]}. 15 questions with an internal choice (a) or (b), 10 marks each, '
                   f'so 30 questions in all; every one is below with its syllabus topic and a model answer.')
        out[rel] = B.static_page(1, title, desc, can, f'APPSC Group 1 Mains {y} Paper {p} with model answers', lede, body,
                                 crumbs0 + [(f'{y} Paper {p}', can)], conf)
    # one page per syllabus part (subject-wise)
    by_part = {}
    for q in qs: by_part.setdefault((q['paper'], q['part_no']), []).append(q)
    for (p, pno), L in by_part.items():
        n, pname = PAPERS[p]
        part, ps = parts[(p, pno)]
        rel = f'{DIR}/{ps}.html'
        can = f'{B.SITE_URL}{pb}{rel}'
        topics = {}
        for q in L: topics.setdefault(q['topic'], []).append(q)
        title = f'APPSC Group 1 Mains {part} Questions with Answers (Paper {p}, 2020–2025) | Learn with Anil'
        desc = (f'{len(L)} APPSC Group 1 Mains Paper {p} previous questions on {part}, from the 2020, 2023 and 2025 papers, grouped by topic, '
                f'with model answers by Learn with Anil. Questions free; answers with the ₹{price} PYQ Pass.')
        sib = ' · '.join(f'<a href="{s}.html">{esc(nm)}</a>' for (pp, _), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]) if pp == p and s != ps)
        sec = []
        for t, TL in topics.items():
            TL.sort(key=lambda q: (-q['year'], qkey(q)))
            sec.append(f'<h2>{esc(t)} <span style="font-weight:400;color:var(--muted);font-size:16px">· asked {len(TL)} time{"s" if len(TL) > 1 else ""}</span></h2><ol class="qs">'
                       + ''.join(q_html(q, man, pb, price, parts, f'{q["year"]} · Paper {p} · Q{q["qno"]}', False) for q in TL) + '</ol>')
        yc = {y: sum(q['year'] == y for q in L) for y in YEARS}
        body = (CSS + f'<p>Paper {p}: {esc(pname)}. Other parts of this paper: {sib}. <a href="./">All Mains PYQs</a>.</p>'
                + f'<table class="facts"><tr><th>Year</th>' + ''.join(f'<th>{y}</th>' for y in YEARS) + '<th>Total</th></tr><tr><td>Questions</td>'
                + ''.join(f'<td class="n">{yc[y]}</td>' for y in YEARS) + f'<td class="n"><b>{len(L)}</b></td></tr></table>'
                + howto + ''.join(sec) + buy + js)
        lede = esc(f'Every APPSC Group-I Mains question on {part} (Paper {p}) from the 2020, 2023 and 2025 papers: {len(L)} questions in {len(topics)} topics, '
                   f'newest first, each with a model answer.')
        out[rel] = B.static_page(1, title, desc, can, f'APPSC Group 1 Mains {part}: previous questions with answers', lede, body,
                                 crumbs0 + [(f'Paper {p} · {part}', can)], conf)
    # the index: year-wise and subject-wise
    yw = ''.join(f'<h3 style="margin:18px 0 4px">{y} Mains <span style="font-weight:400;color:var(--muted);font-size:15px">· held {HELD[y]}</span></h3><div class="yp">'
                 + ''.join(f'<a href="{y}-paper-{PAPERS[p][0]}.html"><b>Paper {p}</b><span>{esc(PAPERS[p][1])} · 30 questions</span></a>' for p in PAPERS) + '</div>'
                 for y in YEARS)
    sw = []
    for p, (n, pname) in PAPERS.items():
        items = []
        for (pp, pno), (nm, s) in sorted(parts.items(), key=lambda x: x[0][1]):
            if pp != p: continue
            L = by_part[(pp, pno)]
            tps = list(dict.fromkeys(q['topic'] for q in L))
            items.append(f'<div class="ppart"><a href="{s}.html">{esc(nm)}</a> · {len(L)} questions<br><span>{esc("; ".join(tps))}</span></div>')
        sw.append(f'<h3 style="margin:22px 0 8px">Paper {p}: {esc(pname)}</h3>' + ''.join(items))
    body = (CSS + f'<a class="cta" href="#year">Year-wise</a><a class="cta alt" href="#subject">Subject-wise</a>'
            f'<a class="cta alt" href="{pb}#mains">Answer Writing Tool Kit (PDF)</a>' + howto
            + f'<h2 id="year">Year-wise: 2025, 2023 and 2020 papers</h2><p>Each paper has 15 questions with an internal choice, (a) or (b), 10 marks each.</p>' + yw
            + f'<h2 id="subject">Subject-wise: by syllabus part</h2><p>The same {len(qs)} questions sorted by the Notification 07/2026 syllabus, so you can see which parts APPSC asks most.</p>'
            + ''.join(sw)
            + '<p class="note">Paper I (General Essay) topics are in the Answer Writing Tool Kit. Paper V (Science, Technology &amp; Environmental Issues) is not on the site yet.</p>'
            + buy)
    title = 'APPSC Group 1 Mains Previous Year Questions with Model Answers (2020, 2023, 2025) – Year-wise & Subject-wise | Learn with Anil'
    desc = (f'All {len(qs)} APPSC Group 1 Mains questions of 2020, 2023 and 2025 for Paper II (History & Geography), Paper III (Polity & Ethics) and Paper IV (Economy), '
            f'year-wise and subject-wise, with model answers by Learn with Anil. Questions free; answers with the ₹{price} PYQ Pass.')
    lede = esc(f'{len(qs)} real APPSC Group-I Mains questions from the 2020, 2023 and 2025 papers (Papers II, III and IV), each with a model answer: '
               f'pick a year and paper, or a syllabus part to see every question APPSC has asked on it.')
    out[f'{DIR}/index.html'] = B.static_page(1, title, desc, base, 'APPSC Group 1 Mains PYQs with model answers', lede, body, crumbs0, conf)
    return out


def tiles(conf, qs_n):
    """The Mains tiles on the APPSC Group-1 home page."""
    pb = conf['pb']
    return (f'<a class="etile" href="{pb}{DIR}/#year"><span class="etile-k">01 · Mains PYQs</span><b>Year-wise</b>'
            f'<span class="etile-p">The 2025, 2023 and 2020 Mains papers II, III and IV: all {qs_n} questions, each with a model answer.</span>'
            f'<span class="etile-price">✓ Questions free · answers in the pass</span></a>'
            f'<a class="etile" href="{pb}{DIR}/#subject"><span class="etile-k">02 · Mains PYQs</span><b>Subject-wise</b>'
            f'<span class="etile-p">The same questions by syllabus part: history, AP history, geography, polity, ethics, economy and AP economy.</span>'
            f'<span class="etile-price">✓ Questions free · answers in the pass</span></a>'
            f'<a class="etile" href="#mains"><span class="etile-k">03 · Answer writing</span><b>Answer Writing Tool Kit</b>'
            f'<span class="etile-p">Four PDF books (Papers I–IV): every previous question sorted by syllabus, with practice questions.</span>'
            f'<span class="etile-price" data-paidtxt="✓ Included in your PYQ Pass">🔒 Included in the PYQ Pass</span></a>')
