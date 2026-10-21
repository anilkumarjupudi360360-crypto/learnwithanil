#!/usr/bin/env python3
"""Make "question of the day" images to post on WhatsApp, Telegram and Instagram (1080 x 1350).

Each card shows one real previous-year question in English and Telugu with its four options (no answer), and a link + QR code
to the question's own page on learnwithanil.in, where the answer and explanation are. Captions are written next to the images.

    python3 tools/qotd_cards.py --days 7 --start 2026-10-22 --out /path/to/folder

Questions already used are remembered in tools/qotd-used.json, so the next run picks new ones.
"""
import argparse, asyncio, base64, datetime as dt, html, io, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402

ROOT = B.ROOT
FONTS = os.path.join(ROOT, 'tools', 'fonts')
USED = os.path.join(ROOT, 'tools', 'qotd-used.json')
SITE = 'https://learnwithanil.in'

# one APPSC Group 2 card and one TS Police card per day; subjects that make good stand-alone questions
STREAMS = [
    dict(exams=['appsc-group-2'], subjects=['ih', 'aph', 'pol', 'geo', 'soc', 'eco', 'sci', 'men'], tag='#APPSC #APPSCGroup2 #Group2 #APGroup2'),
    dict(exams=['ts-police-si', 'ts-police-constable'], subjects=['ari', 'rea', 'sci', 'geo', 'tg', 'ih', 'pol', 'eco'], tag='#TSPolice #TSSI #TSConstable #TGPRB #TelanganaPolice'),
]


def font_css():
    faces = [('Archivo', 'archivo-latin-800-normal', 800), ('Plex', 'ibm-plex-mono-latin-500-normal', 500),
             ('Src', 'source-sans-3-latin-400-normal', 400), ('Src', 'source-sans-3-latin-600-normal', 600), ('Src', 'source-sans-3-latin-700-normal', 700),
             ('Te', 'noto-sans-telugu-telugu-400-normal', 400), ('Te', 'noto-sans-telugu-telugu-600-normal', 600)]
    return '\n'.join(f"@font-face{{font-family:'{f}';font-weight:{w};src:url('file://{FONTS}/{n}.woff2') format('woff2')}}" for f, n, w in faces)


def qr_data_uri(url):
    import qrcode
    q = qrcode.QRCode(border=1, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url); q.make(fit=True)
    buf = io.BytesIO(); q.make_image(fill_color='#0C2266', back_color='white').save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def card_html(item):
    e = html.escape
    opts = ''.join(f'<li><b>({i + 1})</b> {e(o)}</li>' for i, o in enumerate(item['o']))
    opts_te = ''.join(f'<li><b>({i + 1})</b> {e(o)}</li>' for i, o in enumerate(item['ot']))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{width:1080px;height:1350px;background:#F3F6FB;font-family:'Src',sans-serif;color:#0D1830;display:flex;flex-direction:column}}
.top{{background:#0C2266;color:#EEF3FF;padding:44px 64px 40px;display:flex;align-items:center;gap:24px}}
.logo{{width:92px;height:92px;border-radius:50%;background:#1846C7;display:grid;place-items:center;font:800 40px 'Archivo';letter-spacing:2px;color:#fff;box-shadow:inset 0 0 0 6px rgba(255,255,255,.28)}}
.brand b{{display:block;font:800 44px/1.05 'Archivo'}}.brand span{{font:500 22px 'Plex';letter-spacing:.08em;color:#AFC1EE;text-transform:uppercase}}
.day{{margin-left:auto;text-align:right;font:500 22px/1.4 'Plex';color:#AFC1EE;letter-spacing:.06em;text-transform:uppercase}}.day b{{display:block;color:#fff;font:800 40px 'Archivo';letter-spacing:0}}
main{{flex:1;min-height:0;padding:40px 64px 36px;display:flex;flex-direction:column;justify-content:center;gap:24px;overflow:hidden}}
.meta{{display:flex;gap:12px;flex-wrap:wrap}}.chip{{font:600 24px 'Src';background:#E2EAFC;color:#1440B8;border-radius:999px;padding:8px 20px}}
.q{{font:700 {item['fs']}px/1.32 'Src';margin:0;white-space:pre-line}}
ol{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:12px 18px}}
li{{background:#fff;border:2px solid #D6DFEC;border-radius:16px;padding:14px 20px;font:600 {item['fo']}px/1.3 'Src'}}li b{{color:#1440B8}}
.te{{border-left:6px solid #D6DFEC;padding-left:22px;color:#25324B}}.te .q{{font:600 {item['ft']}px/1.55 'Te','Src';}}
.te ol li{{font:400 {item['ft'] - 2}px/1.45 'Te','Src';padding:10px 16px}}
.foot{{margin-top:auto;background:#fff;border-top:2px solid #D6DFEC;padding:30px 64px;display:flex;align-items:center;gap:30px}}
.foot img{{width:170px;height:170px;border-radius:12px}}
.foot .t{{font:700 30px/1.25 'Src'}}.foot .u{{font:500 22px/1.3 'Plex';color:#1440B8;margin-top:8px;word-break:break-all}}.foot .s{{font:400 24px 'Src';color:#55627C;margin-top:8px}}
</style></head><body>
<div class="top"><div class="logo">LA</div><div class="brand"><b>Learn with Anil</b><span>Question of the day</span></div><div class="day">{e(item['daylabel'])}<b>{e(item['exam_short'])}</b></div></div>
<main>
<div class="meta"><span class="chip">{e(item['paper'])} · Q{item['n']}</span><span class="chip">{e(item['subject'])}</span></div>
<p class="q">{e(item['q'])}</p>
<ol>{opts}</ol>
<div class="te" lang="te"><p class="q">{e(item['qt'])}</p><ol style="margin-top:14px">{opts_te}</ol></div>
</main>
<div class="foot"><img src="{qr_data_uri(item['qr'])}" alt=""><div><div class="t">Answer + explanation in English &amp; Telugu</div>
<div class="u">{e(item['short'])}</div><div class="s">Free previous papers &amp; mock tests · comment your answer first</div></div></div>
</body></html>"""


def pick(days, start, seed):
    used = set(json.load(open(USED))) if os.path.exists(USED) else set()
    confs = {c['id']: c for c in B.exam_confs()}
    loaded = {}
    for cid in {x for s in STREAMS for x in s['exams']}:
        loaded[cid] = B.load_exam(confs[cid])
    rnd = random.Random(seed)
    items = []
    for d in range(days):
        day = start + dt.timedelta(days=d)
        for si, st in enumerate(STREAMS):
            cid = st['exams'][d % len(st['exams'])]
            conf = confs[cid]; papers, qs = loaded[cid]
            pm = {p['id']: p for p in papers}; subj = {s[0]: s[1] for s in conf['subjects']}
            want = st['subjects'][(d + si * 3) % len(st['subjects'])]
            def ok(q, s_=None):
                return (q['id'] not in used and q.get('o') and q.get('qt') and q.get('ot') and not q.get('img') and pm[q['p']]['fmt'] == 'mcq'
                        and len(q['a']) == 1 and len(q['q']) < 240 and len(q['qt']) < 280 and max(len(o) for o in q['o']) < 60
                        and max(len(o) for o in q['ot']) < 70 and q['s'] != 'cur' and '\n' not in q['q'].strip() and (s_ is None or q['s'] == s_))
            cand = [q for q in qs if ok(q, want)] or [q for q in qs if ok(q)]
            q = rnd.choice(cand); used.add(q['id'])
            p = pm[q['p']]
            url = f'{SITE}{conf["pb"]}q/{q["id"]}.html'
            long_ = len(q['q']) + len(q['qt']) + sum(len(o) for o in q['o'] + q['ot'])
            fs, fo, ft = 54, 38, 38   # start large; render() shrinks until it fits
            items.append(dict(day=day.isoformat(), daylabel=day.strftime('%a %d %b'), exam_short=conf['seo'].replace('TS Police Constable', 'TS Constable'),
                              paper=B.paper_kw(conf, p).replace(conf['seo'] + ' ', ''), n=q['n'], subject=subj[q['s']],
                              q=q['q'], o=q['o'], qt=q['qt'], ot=q['ot'], id=q['id'], url=url, short=url.replace('https://', ''),
                              qr=url + f'?utm_source=qotd&utm_medium=social&utm_campaign={day.isoformat()}', fs=fs, fo=fo, ft=ft,
                              tag=st['tag'], exam_id=cid, te_name=conf.get('te_name') or ('APPSC గ్రూప్ 2' if cid == 'appsc-group-2' else conf['seo'])))
    return items, used


def caption(it):
    return (f"{it['exam_short']} – Question of the day ({it['daylabel']})\n"
            f"From the real {it['paper']} paper, Q{it['n']} ({it['subject']}).\n"
            f"Comment your answer (1/2/3/4) before you check!\n\n"
            f"Answer with explanation in English & Telugu: {it['url']}\n"
            f"నేటి ప్రశ్న — సమాధానం, వివరణ తెలుగులో: పై లింక్‌లో.\n\n"
            f"Free previous papers & mock tests: https://learnwithanil.in\n{it['tag']} #PYQ #LearnWithAnil")


async def render(items, out):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for it in items:
            f = os.path.join(out, 'card.html'); open(f, 'w', encoding='utf-8').write(card_html(it))
            await pg.goto('file://' + f); await pg.evaluate('document.fonts.ready')
            # shrink the text until everything fits above the footer
            for _ in range(16):
                over = await pg.evaluate("(m => m.scrollHeight > m.clientHeight + 2)(document.querySelector('main'))")
                if not over: break
                it['fs'] -= 2; it['fo'] -= 1 if it['fo'] > 26 else 0; it['ft'] -= 1 if it['ft'] > 25 else 0
                open(f, 'w', encoding='utf-8').write(card_html(it)); await pg.goto('file://' + f); await pg.evaluate('document.fonts.ready')
            it['file'] = f"{it['day']}-{'appsc-group-2' if it['exam_id'] == 'appsc-group-2' else 'ts-police'}.png"
            await pg.screenshot(path=os.path.join(out, it['file']))
        os.remove(os.path.join(out, 'card.html'))
        await b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--start', default=(dt.date.today() + dt.timedelta(days=1)).isoformat())
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', default='lwa-qotd')
    ap.add_argument('--dry', action='store_true', help='do not remember the questions as used')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    items, used = pick(a.days, dt.date.fromisoformat(a.start), a.seed + a.start)
    asyncio.run(render(items, a.out))
    for it in items: it['caption'] = caption(it)
    json.dump([{k: it[k] for k in ('day', 'daylabel', 'exam_short', 'paper', 'n', 'subject', 'id', 'url', 'file', 'caption')} for it in items],
              open(os.path.join(a.out, 'cards.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if not a.dry: json.dump(sorted(used), open(USED, 'w'), indent=0)
    print(f'{len(items)} cards in {a.out}')


if __name__ == '__main__':
    main()
