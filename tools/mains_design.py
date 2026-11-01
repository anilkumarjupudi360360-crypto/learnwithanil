"""Photo design for the descriptive Mains PYQ pages (APPSC Group-1 Mains: tools/g1mains.py; UPSC Mains GS and Anthropology:
tools/upscmains.py). Anil, 2 Nov 2026: "design bad for all UPSC & APPSC mains....pls make some good design...pls possible add
pics or photos".

Every paper has a photo and a colour of its own (the photo is the paper's identity on every page): a photo banner with the H1
on top of the pages, paper cards with year chips on the index, numbered question rows on the paper pages, a question card in
the paper's colour on the answer pages. The photos are freely licensed (Wikimedia Commons; ISRO and Indian Navy photos under the
Government Open Data Licence - India) and credited on every page that shows them. Files: src/static/mains-<key>.jpg (1200 px
wide) and mains-<key>-s.jpg (600 px), served from the site root.
"""
import html, re

esc = lambda s: html.escape(str(s), quote=True)

LIC = {'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
       'CC0': 'https://creativecommons.org/publicdomain/zero/1.0/',
       'FAL': 'https://artlibre.org/licence/lal/en/',
       'GODL-India': 'https://data.gov.in/sites/default/files/Gazette_Notification_OGDL.pdf'}
C = 'https://commons.wikimedia.org/wiki/File:'
# key: (width, height of the big file, alt text, short name for the credit, author, licence, Commons page, object-position)
PHOTOS = {
    'north-block': (1200, 750, 'North Block, the Central Secretariat on Raisina Hill, New Delhi', 'North Block, New Delhi', 'A.Savin', 'FAL',
                    C + 'New_Delhi_government_block_03-2016_img1.jpg', 'center 60%'),
    'konark': (1200, 777, 'A stone chariot wheel carved on the 13th-century Konark Sun Temple, Odisha', 'Konark Sun Temple wheel', 'Joydeep', 'CC BY-SA 4.0',
               C + 'Wheel_engraved_in_the_13th_century_built_Konark_Sun_Temple_in_Orissa,_India.jpg', 'center'),
    'parliament': (1200, 900, 'The new Parliament building in New Delhi, seen from above', 'New Parliament building', 'Ministry of Parliamentary Affairs', 'GODL-India',
                   C + 'Glimpses_of_the_new_Parliament_Building,_in_New_Delhi_(2).jpg', 'center 62%'),
    'vikrant': (1200, 800, 'INS Vikrant and INS Vikramaditya sailing with their carrier battle group', 'INS Vikrant and INS Vikramaditya', 'Indian Navy', 'GODL-India',
                C + 'INS_Vikrant_(R11)_and_INS_Vikramaditya_(R33)_with_the_carrier_battle_group.jpg', 'center 60%'),
    'charkha': (1200, 900, 'A wooden charkha, the spinning wheel of the freedom movement', 'Charkha', 'Janak Bhatta', 'CC BY-SA 4.0',
                C + 'Charkha_(spinning_wheel).jpg', 'center 45%'),
    'bhimbetka': (1200, 800, 'Prehistoric rock paintings at Bhimbetka, Madhya Pradesh', 'Bhimbetka rock paintings', 'Yann', 'CC BY-SA 4.0',
                  C + 'Rock_paintings,_Bhimbetka,_Raisen_district,_MP,_India.jpg', 'center'),
    'warli': (1200, 593, 'Warli tribal paintings on a city wall in Mysuru', 'Warli paintings, Mysuru', 'Prof tpms', 'CC BY-SA 4.0',
              C + 'Warli_Paintings,_Mysore.jpg', 'center 40%'),
    'prakasam': (1200, 800, 'Prakasam Barrage across the Krishna at Vijayawada, lit up at night', 'Prakasam Barrage, Vijayawada', 'Deensonu', 'CC BY-SA 4.0',
                 C + 'Prakasam_Barrage,_Vijayawada_2016_(7).jpg', 'center'),
    'lepakshi': (1200, 797, 'The monolithic Nandi at Lepakshi, Andhra Pradesh', 'Lepakshi Nandi', 'Rahmanuddin', 'CC BY-SA 4.0',
                 C + 'Lepakshi_nandi_15.JPG', 'center 42%'),
    'ap-assembly': (1000, 667, 'The Andhra Pradesh Legislative Assembly hall', 'Andhra Pradesh Legislative Assembly', 'Kdslk', 'CC0',
                    C + 'A.P_Legislative_Assembly.jpg', 'center'),
    'paddy': (1200, 800, 'Paddy fields near Eluru, Andhra Pradesh, at sunrise', 'Paddy fields near Eluru', 'iMahesh', 'CC BY-SA 4.0',
              C + 'Paddy_Fields_near_Eluru.jpg', 'center 45%'),
    'lvm3': (1200, 799, 'LVM3 lifting off with Chandrayaan-3 from Sriharikota, Andhra Pradesh', 'LVM3 launch, Sriharikota', 'ISRO', 'GODL-India',
             C + 'LVM3_M4,_Chandrayaan-3_-_Launch_vehicle_lifting_off_from_the_Second_Launch_Pad_(SLP)_of_SDSC-SHAR,_Sriharikota_01.webp', 'center 55%'),
}
# paper -> (photo, colour)
LOOK = {'GS1': ('konark', '#8A5A2B'), 'GS2': ('parliament', '#A23B2A'), 'GS3': ('vikrant', '#1D4E89'), 'GS4': ('charkha', '#75611C'),
        'AN1': ('bhimbetka', '#9A4E22'), 'AN2': ('warli', '#7E2F35'),
        'I': ('prakasam', '#0D6772'), 'II': ('lepakshi', '#80653A'), 'III': ('ap-assembly', '#6F3B1F'), 'IV': ('paddy', '#3A7428'), 'V': ('lvm3', '#2A5AA0')}

SANS = '"Source Sans 3",system-ui,sans-serif'
HEAD = 'Archivo,"Arial Narrow",system-ui,sans-serif'
CSS = ('a:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:6px}'
       # photo banner with the H1
       '.mh{position:relative;isolation:isolate;display:flex;align-items:flex-end;min-height:300px;margin:24px 0 18px;border-radius:18px;overflow:hidden;background:#0C2266}'
       '.mh .ph{position:absolute;inset:0;z-index:-2;display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);grid-template-rows:100%;gap:6px}'
       '.mh .ph img{width:100%;height:100%;min-width:0;min-height:0;object-fit:cover;display:block}'
       '.mh::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(90deg,rgba(4,10,30,.88) 0%,rgba(4,10,30,.62) 34%,rgba(4,10,30,.12) 62%,rgba(4,10,30,0) 80%)}'
       '.mh .in{padding:44px 26px 24px;color:#fff;max-width:58%}'
       '.mh .kick{margin:0 0 6px;font-weight:600;font-size:15.5px;color:rgba(255,255,255,.88)}'
       f'.mh h1{{color:#fff;margin:0;font-size:clamp(26px,4.4vw,40px);text-shadow:0 1px 12px rgba(0,0,0,.35)}}'
       '.mh .pc{position:absolute;top:10px;right:10px;margin:0;font-size:11.5px;line-height:1.3;color:rgba(255,255,255,.85);background:rgba(0,0,0,.42);padding:3px 8px;border-radius:6px;max-width:calc(100% - 20px);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
       '.mh .pc a{color:inherit}'
       '.mh.slim{min-height:210px}.mh.slim h1{font-size:clamp(22px,3.4vw,30px)}'
       '@media (max-width:640px){.mh{margin:14px -4px 12px;border-radius:14px}.mh .in{padding:54px 16px 14px;max-width:100%}.mh::after{background:linear-gradient(to top,rgba(4,10,30,.9) 0%,rgba(4,10,30,.6) 38%,rgba(4,10,30,.05) 70%)}.mh{min-height:320px}.mh.slim{min-height:230px}.mh .pc{font-size:10.5px;white-space:normal;left:10px;text-align:right}}'
       # paper cards (index: year-wise)
       '.pgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;margin:18px 0 12px}@media (max-width:700px){.pgrid{grid-template-columns:1fr}}'
       '.pgrid>.pcard:last-child:nth-child(odd){grid-column:1/-1}.pgrid>.pcard:last-child:nth-child(odd) .pimg{height:200px}'
       '.pcard{background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}'
       '.pcard .pimg{position:relative;display:block;height:156px;background:var(--pc)}.pcard .pimg img{width:100%;height:100%;object-fit:cover;display:block}'
       '.tag{display:inline-block;background:var(--pc);color:#fff;font-weight:700;font-size:14px;line-height:1.3;padding:4px 10px;border-radius:8px}'
       '.pcard .pimg .tag{position:absolute;left:12px;bottom:12px;box-shadow:0 2px 10px rgba(0,0,0,.25)}'
       '.pcard .pb{padding:18px 20px 20px;display:flex;flex-direction:column;gap:12px;flex:1}'
       f'.pcard h3{{font-family:{HEAD};font-size:19px;line-height:1.25;margin:0}}.pcard h3 a{{color:var(--ink);text-decoration:none}}.pcard h3 a:hover{{text-decoration:underline}}'
       '.pcard .pm{color:var(--muted);font-size:15px;margin:0}'
       '.pcard .sub{margin-top:auto;font-weight:700;font-size:15.5px}'
       # year and paper chips
       '.ychips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}'
       '.ychips a{display:inline-block;min-width:60px;text-align:center;padding:7px 12px;border-radius:999px;border:1.5px solid var(--line);background:var(--bg);color:var(--ink);'
       'text-decoration:none;font-weight:700;font-size:15.5px;font-variant-numeric:tabular-nums}'
       '.ychips a:hover{border-color:var(--pc,var(--accent))}.ychips a.on{background:var(--pc,var(--accent));border-color:var(--pc,var(--accent));color:#fff}'
       '.msw{display:grid;grid-template-columns:auto 1fr;gap:12px 16px;align-items:center;margin:8px 0 20px}'
       '.msw .lbl{font-weight:700;font-size:15px;color:var(--muted)}.msw .ychips a{min-width:0;padding:5px 11px;font-size:15px}'
       '@media (max-width:640px){.msw{grid-template-columns:1fr;gap:4px}.msw .lbl{margin-top:6px}}'
       # subject-wise blocks
       '.sblk{background:var(--surface);border:1px solid var(--line);border-radius:16px;margin:20px 0;overflow:hidden;scroll-margin-top:12px}'
       '.sblk .sh{display:flex;gap:16px;align-items:center;padding:16px 20px;border-bottom:1px solid var(--line);box-shadow:inset 6px 0 0 var(--pc)}'
       '.sblk .sh img{width:68px;height:68px;border-radius:12px;object-fit:cover;flex:none;margin-left:4px}'
       f'.sblk h3{{margin:4px 0 0;font-family:{HEAD};font-size:18px;line-height:1.25}}'
       '.plist{list-style:none;margin:0;padding:0}.plist li+li{border-top:1px solid var(--line)}'
       '.plist a{display:grid;grid-template-columns:1fr auto;gap:3px 14px;padding:13px 20px;text-decoration:none;color:var(--ink)}.plist a:hover{background:var(--bg)}'
       '.plist b{font-weight:700}.plist .n{color:var(--muted);font-size:14.5px;white-space:nowrap}'
       '.plist .t{grid-column:1/-1;color:var(--muted);font-size:14.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
       '@media (max-width:640px){.plist .t{white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}}'
       # question rows (paper pages and subject pages)
       '.qrows{list-style:none;margin:16px 0;padding:0;background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden}'
       '.qrows>li{display:grid;grid-template-columns:54px minmax(0,1fr);gap:4px 16px;padding:16px 22px;scroll-margin-top:12px;position:relative}.qrows>li:has(a.qt):hover{background:var(--bg)}a.qt::after{content:"";position:absolute;inset:0}.qm a,.qa a{position:relative;z-index:1}.qrows>li+li{border-top:1px solid var(--line)}'
       '.qrows>li:target{background:var(--accent-soft)}'
       f'.qn{{grid-row:span 3;align-self:start;width:54px;min-height:46px;border-radius:12px;background:var(--accent-soft);'
       f'background:color-mix(in srgb,var(--pc) 13%,var(--surface));color:var(--pc);font:800 16px/1.1 {HEAD};display:flex;flex-direction:column;align-items:center;justify-content:center;padding:6px 2px;text-align:center}}'
       f'.qn small{{display:block;font:600 12px/1.2 {SANS};color:var(--muted);margin-bottom:2px}}'
       '@media (prefers-color-scheme:dark){.qn{color:#fff;background:color-mix(in srgb,var(--pc) 75%,var(--surface))}.qn small{color:rgba(255,255,255,.8)}}'
       '.qt{display:block;font-weight:600;font-size:17px;line-height:1.5;color:var(--ink);text-decoration:none;white-space:pre-line;overflow-wrap:anywhere}'
       'a.qt:hover{text-decoration:underline;text-decoration-color:var(--pc)}'
       '.qm{color:var(--muted);font-size:14.5px;margin:0}.qm a{color:inherit}.qa{margin:6px 0 0;display:flex;flex-wrap:wrap;gap:8px}'
       '.mp{display:inline-flex;align-items:center;gap:4px;padding:3px 11px;border-radius:999px;font-weight:700;font-size:13.5px;line-height:1.5;text-decoration:none;border:1px solid var(--line);color:var(--accent-text);background:var(--surface)}'
       '.mp:hover{border-color:var(--accent)}.mp.free{background:var(--good-soft);border-color:var(--good-soft);color:var(--good)}'
       '@media (max-width:640px){.qrows>li{grid-template-columns:42px minmax(0,1fr);gap:4px 12px;padding:14px 12px}.qn{width:42px;min-height:40px;font-size:14px}.qt{font-size:16px}.qm{font-size:14px}}'
       f'.tsec{{font-family:{HEAD};font-size:18px;margin:22px 0 0}}.tsec span{{font:400 15px/1.4 {SANS};color:var(--muted)}}'
       # answer pages
       '.mq{background:var(--surface);border:1px solid var(--line);border-left:6px solid var(--pc);border-radius:14px;padding:20px 22px;margin:16px 0}'
       '.mq .tags{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 8px}'
       '.mq .tags span{background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:14px;font-weight:600}'
       '.mq .tags span:first-child{background:var(--pc);border-color:var(--pc);color:#fff}'
       '.mq .syl{margin:10px 0 0;font-size:15px;color:var(--muted)}'
       '.ma{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin:16px 0}''@media (max-width:640px){.mq{padding:16px 14px;border-left-width:5px}.ma{padding:16px 14px}.ma .ah{font-size:17.5px}}'
       f'.ma .ah{{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:0 0 10px;font:700 19px/1.25 {HEAD}}}'
       f'.ma .ah .free{{font:700 13.5px/1.3 {SANS};background:var(--good-soft);color:var(--good);border-radius:999px;padding:3px 10px}}'
       # paid answer in the page (for Google), shown as a faded preview until the PYQ Pass opens it (tools/g1mains.py)
       '.mans.pw{max-height:170px;overflow:hidden;position:relative;-webkit-mask-image:linear-gradient(#000 35%,transparent);mask-image:linear-gradient(#000 35%,transparent);user-select:none;-webkit-user-select:none;pointer-events:none}'
       '.pn{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:12px;margin:20px 0}'
       '.pn a{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 14px;text-decoration:none;color:var(--ink)}.pn a:hover{border-color:var(--pc)}'
       '.pn small{display:block;color:var(--muted);font-size:13.5px;font-weight:700}'
       '.pn span{display:block;font-weight:600;font-size:15px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
       '.pn .nx{text-align:right}.pn .all{align-self:stretch;display:flex;align-items:center;font-weight:700;color:var(--accent-text)}'
       '.pn a{min-width:0}@media (max-width:640px){.pn{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.pn .all{grid-column:1/-1;grid-row:2;justify-content:center}}'
       '.osec{margin:28px 0 0}.osec h2{font-size:19px;margin:0 0 4px}'
       # hub course cards
       '.ccard{background:var(--surface);border:1px solid var(--line);border-radius:18px;overflow:hidden;margin:24px 0}'
       '.ccard .ph{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);grid-template-rows:100%;gap:10px;height:180px;padding:12px 12px 0}'
       '.ccard .ph a{position:relative;display:block;border-radius:12px;overflow:hidden;background:var(--pc)}.ccard .ph img{width:100%;height:100%;object-fit:cover;display:block}'
       '.ccard .ph .tag{position:absolute;left:10px;bottom:10px;box-shadow:0 2px 10px rgba(0,0,0,.25)}'
       '.ccard .cb{padding:20px 24px 24px}.ccard .kick{margin:0 0 6px;font-weight:700;color:var(--muted);font-size:15px}'
       '.ccard h2{margin:0 0 10px}.ccard .lead{color:var(--muted);margin:0}.ccard .row{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0 0}.ccard .row .cta{margin:0}'
       '.cpair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin:24px 0}.cpair .ccard{margin:0}@media (max-width:700px){.cpair{grid-template-columns:1fr}.ccard .ph{height:140px;gap:6px;padding:8px 8px 0}.ccard .ph a{border-radius:9px}.ccard .cb{padding:18px 18px 20px}}'
       '.ccard.plain{border:2px solid var(--accent)}'
       # the price box on these pages
       '.buy.mbuy{background:var(--band);border-color:var(--band);color:#fff;border-radius:16px;padding:22px 24px;margin:28px 0 16px}'
       '.buy.mbuy .muted{color:rgba(255,255,255,.78)}.buy.mbuy .cta{background:#fff;color:var(--band)}'
       '.mcred{font-size:13px;color:var(--muted);margin:20px 0 0}.mcred a{color:inherit}'
       '.lede{margin-top:0}')


def pv(paper):
    """style="--pc:..." for a paper."""
    return f' style="--pc:{LOOK[paper][1]}"'


def img(key, small=False, eager=False, sizes='(max-width: 880px) 100vw, 860px', alt=None):
    w, h, a, *_ , pos = PHOTOS[key]
    src = f'/mains-{key}-s.jpg' if small else f'/mains-{key}.jpg'
    ws, hs = (600, round(h * 600 / w)) if small else (w, h)
    srcset = '' if small else f' srcset="/mains-{key}-s.jpg 600w, /mains-{key}.jpg {w}w" sizes="{sizes}"'
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return (f'<img src="{src}"{srcset} width="{ws}" height="{hs}" alt="{esc(a if alt is None else alt)}"{load} decoding="async"'
            + (f' style="object-position:{pos}"' if pos != 'center' else '') + '>')


def credit(key, prefix='Photo: '):
    w, h, a, name, by, lic, page, pos = PHOTOS[key]
    return f'{prefix}<a href="{page}" rel="noopener">{esc(name)}</a>, {esc(by)}, <a href="{LIC[lic]}" rel="license noopener">{esc(lic)}</a>'


def credits(keys, cls='mcred'):
    """One line crediting every photo on the page."""
    keys = list(dict.fromkeys(keys))
    return f'<p class="{cls}">Photos from Wikimedia Commons: ' + '; '.join(credit(k, '') for k in keys) + '.</p>'


def hero(kick, keys, slim=False, paper=None):
    """The photo banner; the H1 is put in by rehero(). One photo: credited inside the banner; several: see credits()."""
    ph = ''.join(img(k, eager=True, sizes=f'(max-width: 880px) {round(100 / len(keys))}vw, {round(860 / len(keys))}px') if len(keys) > 1 else img(k, eager=True)
                 for k in keys)
    pc = f'<p class="pc">{credit(keys[0])}</p>' if len(keys) == 1 else ''
    return (f'<div class="mh{" slim" if slim else ""}"{pv(paper) if paper else ""}><div class="ph">{ph}</div>{pc}'
            f'<div class="in">' + (f'<p class="kick">{esc(kick)}</p>' if kick else '') + '%%H1%%</div></div>')


def rehero(page, banner):
    """Moves the page's H1 (from build.static_page) into the photo banner, above the lede."""
    m = re.search(r'<main class="wrap">\n<h1>(.*?)</h1>\n', page, re.S)
    if not m: return page
    return page[:m.start()] + '<main class="wrap">\n' + banner.replace('%%H1%%', f'<h1>{m.group(1)}</h1>') + '\n' + page[m.end():]


def chips(items, cls='ychips'):
    """[(label, href, on)] -> a row of pill links."""
    return f'<ul class="{cls}">' + ''.join(f'<li><a href="{h}"' + (' class="on" aria-current="page"' if on else '') + f'>{esc(t)}</a></li>'
                                           for t, h, on in items) + '</ul>'


def paper_card(paper, tag, title, href, meta, years, sub=None):
    """Index card for one paper: photo, tag, title, one line, a chip per year. years: [(year, href)], newest first."""
    key = LOOK[paper][0]
    return (f'<article class="pcard"{pv(paper)}><a class="pimg" href="{href}" tabindex="-1" aria-hidden="true">{img(key, small=True)}<span class="tag">{esc(tag)}</span></a>'
            f'<div class="pb"><h3><a href="{href}">{esc(title)}</a></h3><p class="pm">{esc(meta)}</p>'
            + chips([(str(y), h, i == 0) for i, (y, h) in enumerate(years)])
            + (f'<a class="sub" href="{sub[1]}">{esc(sub[0])}</a>' if sub else '') + '</div></article>')


def subject_block(paper, anchor, tag, title, rows):
    """Subject-wise list for one paper. rows: [(part, href, count text, topics)]"""
    key = LOOK[paper][0]
    return (f'<section class="sblk" id="{anchor}"{pv(paper)}><div class="sh">{img(key, small=True, alt="")}<div><span class="tag">{esc(tag)}</span><h3>{esc(title)}</h3></div></div>'
            '<ul class="plist">' + ''.join(f'<li><a href="{h}"><b>{esc(nm)}</b><span class="n">{esc(n)}</span><span class="t">{esc(t)}</span></a></li>'
                                           for nm, h, n, t in rows) + '</ul></section>')


def qrow(qid, badge, small, text, href, meta, btn):
    """One question row. badge: the question number; small: a line above it (the year on subject pages); btn: html or ''."""
    t = f'<a class="qt" href="{href}">{esc(text)}</a>' if href else f'<p class="qt" style="margin:0">{esc(text)}</p>'
    return (f'<li id="{qid}"><span class="qn">' + (f'<small>{esc(small)}</small>' if small else '') + f'{esc(badge)}</span>{t}'
            f'<p class="qm">{meta}</p>' + (f'<div class="qa">{btn}</div>' if btn else '') + '</li>')


def answer_nav(prev, all_, nxt):
    """prev/nxt: (label, href, question text) or None; all_: (label, href)."""
    p = f'<a href="{prev[1]}"><small>← {esc(prev[0])}</small><span>{esc(prev[2])}</span></a>' if prev else '<div></div>'
    n = f'<a class="nx" href="{nxt[1]}"><small>Next: {esc(nxt[0])} →</small><span>{esc(nxt[2])}</span></a>' if nxt else '<div></div>'
    return f'<nav class="pn" aria-label="Questions">{p}<a class="all" href="{all_[1]}">{esc(all_[0])}</a>{n}</nav>'
