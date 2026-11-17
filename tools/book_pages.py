"""Crawlable pages for the study books (Anil, 16 Nov 2026: "chatgpt must know about the book i have in my website for respective exams").

The Study Material view inside each exam's app is drawn by JavaScript, so search engines and AI assistants (ChatGPT search,
Bing, Perplexity, Google) see little of it. These plain HTML pages carry the same facts as text, with schema.org Book and
FAQPage data:
  /study-material.html                 every book, grouped by the exam it is for
  /study-material/<slug>.html          one page per book: exam, medium, pages, chapters, PYQs inside, free sample, how to get it
Each book is listed under its own exams only (notes.json "exams"; a book without one is for NOTES_EXAMS, APPSC Group-I and II),
the same rule as the exam pages' Study Material (Anil, 16 Nov 2026: "only relevant books in relevant exam boxs").
"""
import json, os, re

HUB = 'study-material.html'
DIR = 'study-material'
# short, searchable addresses; a new book without an entry gets one from its title
SLUGS = {
    'aphist-en': 'ap-history-culture-appsc-group-1-group-2-book',
    'ma-en': 'mental-ability-appsc-group-1-group-2-book',
    'g1pa-en': 'public-administration-governance-appsc-group-1-mains-book',
    'g1eth-en': 'ethics-public-service-laws-appsc-group-1-mains-book',
    'apeco-en': 'andhra-pradesh-economy-crisp-notes-english',
    'apeco-te': 'andhra-pradesh-economy-crisp-notes-telugu',
    'stfull-en': 'science-technology-appsc-group-1-group-2-mains-book',
    'eohp-en': 'hindu-philosophy-temple-system-appsc-eo-grade-3-book',
    'eohp-te': 'hindu-philosophy-temple-system-appsc-eo-grade-3-book-telugu',
    'kaeco-en': 'karnataka-economy-panchayat-raj-kea-fda-sda-book',
    'kahis-en': 'karnataka-history-culture-geography-kea-fda-sda-book',
    'cst-en': 'computer-skill-test-practical-opsc-aso-odisha-book',
    'epfoca-en': 'epfo-current-affairs-2026-upsc-apfc-book',
    'hcse-en': 'computer-science-it-tgpsc-hmwssb-manager-paper-2-book',
    'aee2-en': 'environmental-science-engineering-appsc-aee-paper-2-book',
}
CSS = ('<style>.bk-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px;margin:14px 0 26px}'
       '.bk{border:1px solid #d8dee9;border-radius:12px;padding:12px;background:#fff;display:flex;flex-direction:column;gap:6px}'
       '.bk img{width:100%;height:auto;border-radius:6px;aspect-ratio:560/793;object-fit:cover;background:#0b2a6b}'
       '.bk h3{font-size:16px;margin:4px 0 0;line-height:1.3}.bk p{margin:0;font-size:14px}'
       '.bk-top{display:grid;grid-template-columns:minmax(150px,240px) 1fr;gap:20px;align-items:start;margin:10px 0 20px}'
       '.bk-top img{width:100%;height:auto;border-radius:8px;box-shadow:0 6px 20px rgba(11,42,107,.18)}'
       '.bk-samples{display:flex;gap:12px;flex-wrap:wrap;margin:10px 0 20px}.bk-samples img{width:220px;max-width:46%;height:auto;border:1px solid #d8dee9;border-radius:6px}'
       '.bk-btns{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}'
       '@media(max-width:620px){.bk-top{grid-template-columns:1fr}.bk-top img{max-width:240px}}</style>')


def slug(b):
    if b['id'] in SLUGS: return SLUGS[b['id']]
    t = re.sub(r'\b2026-27\b|\(.*?\)', '', b.get('product_en') or b.get('title_en') or b['id']).lower()
    s = re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:70].strip('-')
    return s + ('-telugu' if b.get('lang') == 'te' else '') + '-book'


def exams_of(B, b):
    return list(b['exams']) if b.get('exams') else sorted(B.NOTES_EXAMS)


def name(b):
    return b.get('product_en') or b.get('product') or b['title']


def write(B, loaded, notes, site_dir):
    """Write the hub and one page per book into site_dir; return {relative path: None} for the sitemap."""
    esc, SITE, price = B.esc, B.SITE_URL, B.PAY['pyq_price']
    confs = {c['id']: c for c, _, _ in loaded}
    books = [b for b in notes if any(e in confs for e in exams_of(B, b))]
    if not books: return {}
    os.makedirs(os.path.join(site_dir, DIR), exist_ok=True)
    by_exam = {}
    for b in books:
        for e in exams_of(B, b):
            if e in confs: by_exam.setdefault(e, []).append(b)
    order = [e for e in ('appsc-group-1', 'appsc-group-2', 'appsc-eo') if e in by_exam] + sorted(e for e in by_exam if e not in ('appsc-group-1', 'appsc-group-2', 'appsc-eo'))
    url = lambda b: f'/{DIR}/{slug(b)}.html'
    ex_names = lambda b: [confs[e]['name'] for e in exams_of(B, b) if e in confs]
    out = {}

    def card(b):
        sub = b.get('chapters_label') or f'{len(b.get("chapters", []))} chapters'
        return (f'<div class="bk"><a href="{url(b)}"><img src="/{esc(b["cover"])}" alt="Cover of {esc(name(b))}" width="560" height="793" loading="lazy"></a>'
                f'<h3><a href="{url(b)}">{esc(name(b))}</a></h3><p>{b["pages"]} pages · {esc(b.get("medium_en") or b.get("medium", ""))}</p>'
                f'<p class="why" style="font-weight:400">{esc(sub)}</p>'
                + (f'<p><a href="{esc(b["free"])}">Free sample chapter (PDF)</a></p>' if b.get('free') else '') + '</div>')

    # ---- one page per book
    for b in books:
        exs = [e for e in exams_of(B, b) if e in confs]
        main = confs[exs[0]]
        nm, can = name(b), SITE + url(b)
        ens = ex_names(b)
        en_txt = ' and '.join(ens)
        lang = 'Telugu' if b.get('lang') == 'te' else 'English'
        chapters = b.get('chapters', [])
        base = re.sub(r'\s+for\s+.*$', '', b.get('title_en') or b['title'])
        title = f'{base} Book for {en_txt}, 2026-27 ({lang} Medium)' + (' – Free Sample PDF' if b.get('free') else '') + ' | Learn with Anil'
        desc = (f'{nm}: {b["pages"]}-page PDF book by Jupudi Anil Kumar for {en_txt}, {lang} medium. '
                + (f'{b["chapters_label"]}. ' if b.get('chapters_label') else f'{len(chapters)} chapters. ')
                + f'Included in the ₹{price} All-in-One Pass' + ('; free sample chapter PDF.' if b.get('free') else '.'))
        rows = [('Book for', en_txt), ('Syllabus', b.get('syllabus') or b.get('series') or ''), ('Author', 'Jupudi Anil Kumar (Learn with Anil)'),
                ('Edition', '2026-27'), ('Medium', b.get('medium_en') or b.get('medium', '')), ('Pages', f'{b["pages"]} (PDF)'),
                ('Chapters', str(len(chapters)))]
        if b.get('pyqs'): rows.append(('Previous questions inside', f'{b["pyqs"]:,}'))
        rows.append(('How to get it', f'Included in the ₹{price} All-in-One Pass (12 months): every book, previous paper and mock test on Learn with Anil. Download the PDF from the Study Material page after paying.'))
        facts = '<table class="facts">' + ''.join(f'<tr><th scope="row">{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in rows if v) + '</table>'
        btns = ('<div class="bk-btns">'
                + (f'<a class="cta" href="{esc(b["free"])}">⬇ Free sample chapter (PDF)</a>' if b.get('free') else '')
                + f'<a class="cta" href="{main["pb"]}notes/">See the book on the {esc(main["name"])} study material page</a>'
                + f'<a class="cta" href="{main["pb"]}?buy=pyq">Get the All-in-One Pass · ₹{price}</a></div>')
        samples = ''.join(f'<img src="/{esc(s)}" alt="Sample page {i + 1} of {esc(nm)}" width="560" height="793" loading="lazy">' for i, s in enumerate(b.get('samples', [])))
        ch_lang = ' lang="te"' if b.get('lang') == 'te' else ''
        others = {e: [x for x in by_exam.get(e, []) if x['id'] != b['id']] for e in exs}
        more = ''.join(f'<h2>Other Learn with Anil books for {esc(confs[e]["name"])}</h2><ul>'
                       + ''.join(f'<li><a href="{url(x)}">{esc(name(x))}</a> · {x["pages"]} pages</li>' for x in xs) + '</ul>'
                       for e, xs in others.items() if xs)
        faq = [(f'Which exam is "{b.get("title_en") or b["title"]}" for?',
                f'It is written for {en_txt}' + (f' ({b["syllabus"]})' if b.get('syllabus') else '') + '. The edition is 2026-27.'),
               ('What is inside the book?',
                f'{b["pages"]} pages in {lang}: ' + (b.get('chapters_label') or f'{len(chapters)} chapters') + '. Chapters: ' + '; '.join(chapters) + '.'),
               ('Is it based on previous year questions?',
                (f'Yes. It includes {b["pyqs"]:,} previous questions of the exam with the official answers, and the chapters follow what the exam actually asks.' if b.get('pyqs')
                 else 'Yes. The chapters follow the exam\'s previous questions.')),
               ('How do I get the PDF?',
                f'The book is part of the ₹{price} All-in-One Pass on learnwithanil.in (one payment for 12 months that also opens every previous paper and mock test). '
                f'After paying, download it from the {main["name"]} Study Material page: {SITE}{main["pb"]}notes/'),
               ('Is there a free sample?',
                (f'Yes. A free sample chapter (PDF) can be downloaded and shared: {SITE}{b["free"]}' if b.get('free')
                 else f'Sample pages can be seen on the {main["name"]} Study Material page; tap the cover.')),
               ('Who wrote it?', 'Jupudi Anil Kumar, a civil-services educator and the founder of Learn with Anil (learnwithanil.in).')]
        faq_html = '<h2>Questions about this book</h2>' + ''.join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q, a in faq)
        book_ld = {"@context": "https://schema.org", "@type": "Book", "name": nm, "url": can,
                   "author": {"@type": "Person", "name": "Jupudi Anil Kumar", "url": SITE + '/'},
                   "publisher": {"@type": "Organization", "name": "Learn with Anil", "url": SITE + '/'},
                   "inLanguage": 'te' if b.get('lang') == 'te' else 'en', "bookFormat": "https://schema.org/EBook",
                   "numberOfPages": b['pages'], "bookEdition": "2026-27", "image": SITE + '/' + b['cover'],
                   "description": b.get('subtitle') or desc, "educationalUse": "Exam preparation",
                   "audience": {"@type": "EducationalAudience", "educationalRole": "student", "audienceType": f'{en_txt} aspirants'},
                   "about": [{"@type": "Thing", "name": n} for n in ens] + [{"@type": "Thing", "name": b.get('subject', '')}],
                   "hasPart": [{"@type": "Chapter", "position": i + 1, "name": c} for i, c in enumerate(chapters)],
                   "offers": {"@type": "Offer", "price": str(price), "priceCurrency": "INR", "availability": "https://schema.org/InStock",
                              "url": f'{SITE}{main["pb"]}notes/', "description": f'Included in the ₹{price} All-in-One Pass (12 months)'}}
        if b.get('free'): book_ld["workExample"] = {"@type": "Book", "name": f'{nm}: free sample chapter', "url": SITE + b['free'], "bookFormat": "https://schema.org/EBook", "isAccessibleForFree": True}
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
        body = (CSS + f'<div class="bk-top"><img src="/{esc(b["cover"])}" alt="Cover of {esc(nm)}" width="560" height="793">'
                f'<div>{facts}{btns}</div></div>'
                + (f'<h2>What\'s inside</h2><p>{esc(b["chapters_label"])}.</p>' if b.get('chapters_label') else '')
                + f'<h2>Contents</h2><ol{ch_lang}>' + ''.join(f'<li>{esc(c)}</li>' for c in chapters) + '</ol>'
                + (f'<h2>Sample pages</h2><div class="bk-samples">{samples}</div>' if samples else '')
                + faq_html + more
                + f'<p style="margin-top:22px"><a href="/{HUB}">All Learn with Anil books, exam by exam →</a></p>'
                + f'<script type="application/ld+json">{json.dumps(book_ld, ensure_ascii=False)}</script>'
                + f'<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>')
        html = B.static_page(1, title, desc, can, nm, esc(b.get('subtitle') or ''), body,
                             [('Home', SITE + '/'), ('Study material', f'{SITE}/{HUB}'), (b.get('title_en') or b['title'], can)],
                             main, at_root=True)
        rel = f'{DIR}/{slug(b)}.html'
        open(os.path.join(site_dir, rel), 'w', encoding='utf-8').write(html)
        out[rel] = None

    # ---- the hub: every book under the exams it is for
    can = f'{SITE}/{HUB}'
    toc = '<nav class="toc">' + ''.join(f'<a href="#{e}">{esc(confs[e]["name"])} ({len(by_exam[e])})</a>' for e in order) + '</nav>'
    secs = ''.join(f'<h2 id="{e}">Books for {esc(confs[e]["name"])}</h2>'
                   f'<p><a href="{confs[e]["pb"]}notes/">{esc(confs[e]["name"])} study material page</a> · <a href="{confs[e]["pb"]}">{esc(confs[e]["name"])} previous papers</a></p>'
                   f'<div class="bk-grid">{"".join(card(b) for b in by_exam[e])}</div>' for e in order)
    items = {"@context": "https://schema.org", "@type": "ItemList", "name": "Learn with Anil study books by exam",
             "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + url(b), "name": name(b)} for i, b in enumerate(books)]}
    exam_list = ', '.join(confs[e]['name'] for e in order)
    lede = (f'{len(books)} PDF books by Jupudi Anil Kumar, each written for a specific exam from that exam\'s own previous questions: {exam_list}. '
            f'Every book is included in the ₹{price} All-in-One Pass; most have a free sample chapter.')
    title = f'Study Material Books for {exam_list} – Learn with Anil (Free Sample PDFs)'
    desc = (f'Exam-wise study books by Jupudi Anil Kumar (Learn with Anil): ' + '; '.join(
        f'{confs[e]["name"]}: ' + ', '.join(x.get('subject_label') or x.get('subject') or x['title'] for x in by_exam[e]) for e in order) + '.')[:300]
    html = B.static_page(0, title, desc, can, 'Study material: books for each exam', esc(lede),
                         CSS + toc + secs + f'<script type="application/ld+json">{json.dumps(items, ensure_ascii=False)}</script>',
                         [('Home', SITE + '/'), ('Study material', can)], None, ename='every exam', at_root=True, head_all=True)
    open(os.path.join(site_dir, HUB), 'w', encoding='utf-8').write(html)
    out[HUB] = None
    return out


def llms_lines(B, loaded, notes):
    """The llms.txt section: every book once with its exams, then which books go with which exam."""
    SITE, price = B.SITE_URL, B.PAY['pyq_price']
    confs = {c['id']: c for c, _, _ in loaded}
    books = [b for b in notes if any(e in confs for e in exams_of(B, b))]
    if not books: return []
    L = [f'- [All study books, grouped by exam]({SITE}/{HUB}): each book is written for specific exams and built on that exam\'s previous questions.']
    for b in books:
        ens = ' and '.join(confs[e]['name'] for e in exams_of(B, b) if e in confs)
        line = (f'- [{name(b)}]({SITE}/{DIR}/{slug(b)}.html): for {ens}. {b["pages"]}-page PDF by Jupudi Anil Kumar'
                + (f', {b["chapters_label"]}' if b.get('chapters_label') else '') + f'. Chapters: {"; ".join(b.get("chapters", []))}. Included in the ₹{price} All-in-One Pass.')
        if b.get('free'): line += f' Free sample chapter (PDF, shareable): {SITE}{b["free"]}'
        L.append(line)
    by_exam = {}
    for b in books:
        for e in exams_of(B, b):
            if e in confs: by_exam.setdefault(e, []).append(b)
    L += ['', '### Which book for which exam']
    for e, xs in by_exam.items():
        L.append(f'- {confs[e]["name"]} ({SITE}{confs[e]["pb"]}notes/): ' + '; '.join(f'[{name(x)}]({SITE}/{DIR}/{slug(x)}.html)' for x in xs))
    L.append('- Other exams on the site: no Learn with Anil book yet; their previous papers, mock tests and explanations are in the same All-in-One Pass.')
    return L
