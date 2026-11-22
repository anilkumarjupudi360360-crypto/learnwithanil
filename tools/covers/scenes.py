"""Drawn cover pictures for the Learn with Anil books (flat illustration, 494 x 150 frame).
Key objects stay below y = 40 because short panels crop the top of the sky."""
import math

W, H = 494, 150


def lin(id_, stops, x2=0, y2=1):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rad(id_, c, op=0.55):
    return (f'<radialGradient id="{id_}"><stop offset="0" stop-color="{c}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')


def sky(stops, extra=''):
    return f'<defs>{lin("sky", stops)}{rad("glow", "#ffe9a0")}{extra}</defs><rect width="{W}" height="{H}" fill="url(#sky)"/>'


def sun(x, y, r=13, c='#ffd43b'):
    return f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="url(#glow)"/><circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>'


def cloud(x, y, s=1.0, c='#ffffff', op=0.75):
    return (f'<g fill="{c}" opacity="{op}" transform="translate({x} {y}) scale({s})">'
            '<ellipse cx="0" cy="0" rx="16" ry="6"/><ellipse cx="-6" cy="-4" rx="8" ry="6"/>'
            '<ellipse cx="5" cy="-6" rx="9" ry="7.5"/><ellipse cx="13" cy="-2" rx="7" ry="5"/></g>')


def birds(x, y, n=3, c='#ffffff', op=0.8):
    out = []
    for k in range(n):
        bx, by = x + k * 9, y + (k % 2) * 4
        out.append(f'<path d="M{bx - 3.5} {by} q1.8 -2.2 3.5 0 q1.7 -2.2 3.5 0" fill="none" stroke="{c}" stroke-width="1" opacity="{op}"/>')
    return ''.join(out)


def palm(x, y, s=1.0, trunk='#7a5230', leaf='#2f8f4e', lean=1):
    f = []
    for a in (-160, -130, -95, -60, -25, 5):
        ang = math.radians(a)
        ex, ey = 15 * math.cos(ang), 15 * math.sin(ang) + 4
        cx, cy = 8 * math.cos(ang), 8 * math.sin(ang) - 5
        f.append(f'<path d="M0 0 Q{cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f} Q{cx * .7:.1f} {cy * .5 + 2:.1f} 0 0" fill="{leaf}"/>')
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-1.6 0 Q{4 * lean} -14 {2 * lean} -30 L{3.6 * lean} -30 Q{6 * lean} -14 1.6 0 Z" fill="{trunk}"/>'
            f'<g transform="translate({2.8 * lean} -30)">{"".join(f)}<circle r="1.8" fill="#5b3b1f"/></g></g>')


def tree(x, y, s=1.0, c='#3f9a5c', c2='#2f7d49', trunk='#6b4a2b'):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-1.3" y="-8" width="2.6" height="8" fill="{trunk}"/>'
            f'<circle cx="0" cy="-13" r="7" fill="{c}"/><path d="M0 -20 a7 7 0 0 1 0 14 Z" fill="{c2}" opacity=".55"/></g>')


def pine(x, y, s=1.0, c='#2f7d49'):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-1" y="-4" width="2" height="4" fill="#5b3b1f"/>'
            f'<path d="M0 -22 L7 -4 L-7 -4 Z" fill="{c}"/></g>')


def person(x, y, s=1.0, body='#f2a93b', head='#8a5a3b', hair='#2b2b2b', extra=''):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-5 0 L-5 -10 Q-5 -15 0 -15 Q5 -15 5 -10 L5 0 Z" fill="{body}"/>'
            f'<circle cx="0" cy="-19" r="3.6" fill="{head}"/><path d="M-3.6 -19.5 A3.6 3.6 0 0 1 3.6 -19.5 Z" fill="{hair}"/>{extra}</g>')


def flag(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-0.5" y="-26" width="1" height="26" fill="#d8dde8"/>'
            '<rect x="0.5" y="-26" width="12" height="2.6" fill="#ff9933"/><rect x="0.5" y="-23.4" width="12" height="2.6" fill="#ffffff"/>'
            '<rect x="0.5" y="-20.8" width="12" height="2.6" fill="#138808"/><circle cx="6.5" cy="-22.1" r=".9" fill="#1f3b8f"/></g>')


def rupee(x, y, size=12, c='#7a4d06'):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans" font-weight="bold" font-size="{size}" fill="{c}" text-anchor="middle">₹</text>'


def waves(x0, x1, y, c='#bfe6ff', op=0.7, step=26):
    return ''.join(f'<path d="M{x} {y} q4 -2.5 8 0" fill="none" stroke="{c}" stroke-width="1.1" opacity="{op}"/>'
                   for x in range(int(x0), int(x1), step))


DAY = [(0, '#1c418f'), (0.5, '#3f78cf'), (1, '#a5cff2')]

# ---------------------------------------------------------------- AP economy

def ap_economy():
    o = [sky(DAY)]
    o.append(sun(440, 52, 12))
    o += [cloud(330, 55, 1.0), cloud(120, 44, .8, op=.55), cloud(470, 78, .7, op=.6)]
    # rising chart with rupee coin
    pts = [(262, 96), (282, 88), (300, 92), (318, 78), (336, 72), (356, 60)]
    o.append('<polyline points="' + ' '.join(f'{a},{b}' for a, b in pts) + '" fill="none" stroke="#ffd43b" stroke-width="2.2" stroke-linejoin="round"/>')
    o += [f'<circle cx="{a}" cy="{b}" r="2.4" fill="#ffffff"/>' for a, b in pts[:-1]]
    o.append('<path d="M356 60 l-8 1 l5 5.6 Z" fill="#ffd43b"/>')
    o.append('<circle cx="376" cy="56" r="11" fill="#f2b705" stroke="#ffe27a" stroke-width="1.6"/>' + rupee(376, 61, 13))
    # far hills
    o.append('<path d="M150 112 Q210 86 260 100 Q310 80 370 98 Q420 84 494 96 L494 150 L150 150 Z" fill="#5c9fd6" opacity=".55"/>')
    # sea and port (left)
    o.append('<rect x="0" y="108" width="190" height="42" fill="#2f7fd0"/>')
    o.append(waves(4, 180, 125) + waves(16, 180, 138))
    o.append('<path d="M8 112 L104 112 L96 124 L16 124 Z" fill="#1c2f5e"/><rect x="18" y="108" width="74" height="4" fill="#c2352c"/>')
    cols = ['#c2352c', '#f2b705', '#0e7c86', '#e07b00', '#1846c7', '#12804a']
    for r in range(2):
        for k in range(6):
            o.append(f'<rect x="{22 + k * 11}" y="{98 - r * 8}" width="10" height="7.4" fill="{cols[(k + r * 2) % 6]}"/>')
    o.append('<rect x="88" y="90" width="9" height="18" fill="#f4f7fc"/><rect x="90" y="93" width="5" height="3" fill="#7aa9e6"/>')
    # quay and cranes
    o.append('<rect x="112" y="110" width="80" height="6" fill="#8a96ad"/>')
    for cx in (130, 165):
        o.append(f'<g stroke="#f2b705" stroke-width="2.2" fill="none"><path d="M{cx - 7} 110 L{cx - 4} 62 M{cx + 7} 110 L{cx + 4} 62 M{cx - 6} 90 L{cx + 6} 90 M{cx - 5} 74 L{cx + 5} 74"/>'
                 f'<path d="M{cx - 30} 64 L{cx + 14} 64" stroke-width="2.6"/><path d="M{cx - 2} 62 L{cx - 22} 64 M{cx + 2} 56 L{cx - 4} 62" stroke-width="1.2"/></g>'
                 f'<rect x="{cx - 5}" y="56" width="10" height="6" fill="#f2b705"/><line x1="{cx - 22}" y1="64" x2="{cx - 22}" y2="82" stroke="#d6dfec" stroke-width="1"/>'
                 f'<rect x="{cx - 26}" y="82" width="8" height="5" fill="#0e7c86"/>')
    # land: fields
    o.append('<path d="M190 106 Q300 98 494 104 L494 150 L184 150 Z" fill="#4c9c4f"/>')
    o.append('<path d="M188 120 Q320 112 494 118 L494 150 L184 150 Z" fill="#62b15b"/>')
    for k in range(7):
        y = 126 + k * 3.6
        o.append(f'<path d="M{200 + k * 4} {y} Q330 {y - 6} 494 {y - 2}" fill="none" stroke="#8fd07a" stroke-width=".9" opacity=".8"/>')
    o.append('<path d="M250 150 Q300 128 360 120 Q420 112 494 110" fill="none" stroke="#5fb4ef" stroke-width="4"/>')
    # factory and small skyline
    o.append('<g><rect x="214" y="92" width="34" height="16" fill="#e8eefb"/><path d="M214 92 l8 -6 l0 6 l8 -6 l0 6 l8 -6 l0 6 l10 -6 l0 6 Z" fill="#c3d1f1"/>'
             '<rect x="238" y="72" width="5" height="22" fill="#d6dfec"/><rect x="238" y="76" width="5" height="2" fill="#c2352c"/>'
             '<circle cx="246" cy="66" r="4" fill="#ffffff" opacity=".6"/><circle cx="252" cy="61" r="5" fill="#ffffff" opacity=".45"/>'
             '<rect x="218" y="97" width="5" height="4" fill="#7aa9e6"/><rect x="227" y="97" width="5" height="4" fill="#7aa9e6"/></g>')
    for x, hgt, w in ((392, 30, 10), (404, 40, 12), (418, 26, 9), (429, 34, 11)):
        o.append(f'<rect x="{x}" y="{104 - hgt}" width="{w}" height="{hgt}" fill="#d6e4f7"/>')
        o += [f'<rect x="{x + 2}" y="{104 - hgt + 3 + j * 6}" width="{w - 4}" height="2" fill="#7aa9e6"/>' for j in range(hgt // 6 - 1)]
    o += [palm(196, 112, .9), palm(270, 108, .85, lean=-1), palm(466, 112, 1.0), palm(482, 116, .8, lean=-1), palm(372, 110, .75)]
    o.append(birds(60, 58) + birds(270, 46, 2))
    return ''.join(o)

# ---------------------------------------------------------------- science & technology

def science_tech():
    o = [sky([(0, '#0b1d57'), (0.55, '#24489e'), (1, '#6f9fe0')],
             extra=lin('flame', [(0, '#fff3b0'), (0.5, '#ffb02e'), (1, '#e0521b')]))]
    import random
    rnd = random.Random(7)
    o += [f'<circle cx="{rnd.randint(5, 489)}" cy="{rnd.randint(40, 95)}" r="{rnd.choice([.6, .8, 1.0])}" fill="#ffffff" opacity="{rnd.choice([.5, .7, .9])}"/>' for _ in range(40)]
    o.append('<circle cx="40" cy="58" r="9" fill="#e8eefb"/><circle cx="44" cy="55" r="9" fill="#24489e" opacity=".9"/>')  # crescent moon
    # atom (left)
    o.append('<g transform="translate(92 74)" fill="none" stroke="#9fd0ff" stroke-width="1.4">'
             '<ellipse rx="22" ry="8"/><ellipse rx="22" ry="8" transform="rotate(60)"/><ellipse rx="22" ry="8" transform="rotate(-60)"/>'
             '<circle r="3.6" fill="#ffd43b" stroke="none"/><circle cx="22" cy="0" r="1.8" fill="#ffffff" stroke="none"/></g>')
    # DNA helix
    dna = []
    for k in range(13):
        x = 140 + k * 6
        y1 = 76 + 9 * math.sin(k * .7); y2 = 76 - 9 * math.sin(k * .7)
        dna.append(f'<line x1="{x}" y1="{y1:.1f}" x2="{x}" y2="{y2:.1f}" stroke="#c3d1f1" stroke-width="1" opacity=".8"/>')
        dna.append(f'<circle cx="{x}" cy="{y1:.1f}" r="1.9" fill="#5fd3c4"/><circle cx="{x}" cy="{y2:.1f}" r="1.9" fill="#ffb36b"/>')
    o.append(''.join(dna))
    # satellite
    o.append('<g transform="translate(262 58) rotate(-12)">'
             '<rect x="-26" y="-5" width="18" height="10" fill="#2f6fd6" stroke="#c3d1f1" stroke-width=".8"/>'
             '<rect x="8" y="-5" width="18" height="10" fill="#2f6fd6" stroke="#c3d1f1" stroke-width=".8"/>'
             '<path d="M-20 -5 v10 M-14 -5 v10 M14 -5 v10 M20 -5 v10" stroke="#c3d1f1" stroke-width=".6"/>'
             '<rect x="-8" y="-1" width="16" height="2" fill="#d6dfec"/><rect x="-6" y="-7" width="12" height="14" rx="1.5" fill="#f2b705"/>'
             '<path d="M0 7 l0 4 M-4 14 a5 3 0 0 0 8 0 Z" stroke="#e8eefb" stroke-width="1" fill="#e8eefb"/></g>')
    o.append('<path d="M232 72 q-8 6 -10 14 M240 76 q-6 4 -7 10" stroke="#9fd0ff" stroke-width=".8" fill="none" opacity=".7"/>')
    # sea and island
    o.append('<rect x="0" y="116" width="494" height="34" fill="#173e86"/>' + waves(6, 300, 132, '#5f8fd6', .6) + waves(20, 300, 143, '#5f8fd6', .5))
    o.append('<path d="M300 150 L318 120 Q380 108 494 112 L494 150 Z" fill="#1f5a3a"/>')
    o += [palm(316, 124, .8, leaf='#2c7a46'), palm(330, 122, .7, lean=-1, leaf='#2c7a46'), palm(484, 116, .8, leaf='#2c7a46')]
    # launch tower
    o.append('<g stroke="#c3d1f1" stroke-width="1.2" fill="none"><path d="M432 116 L432 46 M444 116 L444 46 M432 46 L444 46"/>'
             + ''.join(f'<path d="M432 {y} L444 {y + 8} M444 {y} L432 {y + 8}"/>' for y in range(48, 112, 8)) +
             '<path d="M432 62 L416 62 M432 84 L416 84" stroke-width="1.6"/></g>')
    o.append('<rect x="370" y="114" width="88" height="5" fill="#8a96ad"/>')
    # exhaust plume
    for (cx, cy, r, op) in ((384, 112, 12, .9), (402, 113, 14, .9), (420, 114, 10, .8), (370, 115, 9, .75), (394, 104, 9, .8)):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#e8eefb" opacity="{op}"/>')
    # rocket (lifting off)
    o.append('<g transform="translate(400 44)">'
             '<path d="M-6 58 Q0 92 6 58 Z" fill="url(#flame)"/><path d="M-15 56 Q-12 74 -9 56 Z M9 56 Q12 74 15 56 Z" fill="url(#flame)"/>'
             '<rect x="-6" y="6" width="12" height="52" rx="2" fill="#f4f7fc"/><path d="M-6 6 Q0 -10 6 6 Z" fill="#f4f7fc"/>'
             '<rect x="-6" y="22" width="12" height="3" fill="#ff9933"/><rect x="-6" y="27" width="12" height="2" fill="#138808"/>'
             '<rect x="-15" y="26" width="6" height="30" rx="2" fill="#e3e8f0"/><path d="M-15 26 Q-12 16 -9 26 Z" fill="#c2352c"/>'
             '<rect x="9" y="26" width="6" height="30" rx="2" fill="#e3e8f0"/><path d="M9 26 Q12 16 15 26 Z" fill="#c2352c"/>'
             '<circle cx="0" cy="14" r="2.2" fill="#2f6fd6"/></g>')
    return ''.join(o)

# ---------------------------------------------------------------- temple (Hindu philosophy & temple system)

def gopuram(x, base, w, tiers=6, th=11, c='#e9b96e', c2='#c98f45', c3='#a86b2e', bh=18):
    o = [f'<rect x="{x - w / 2}" y="{base - bh}" width="{w}" height="{bh}" fill="{c2}"/>',
         f'<rect x="{x - 7}" y="{base - 16}" width="14" height="16" fill="#5a3418"/>',
         f'<path d="M{x - 7} {base - 16} a7 7 0 0 1 14 0" fill="#5a3418"/>']
    y = base - bh
    ww = w
    for k in range(tiers):
        top = ww - 8
        o.append(f'<path d="M{x - ww / 2} {y} L{x - top / 2} {y - th} L{x + top / 2} {y - th} L{x + ww / 2} {y} Z" fill="{c if k % 2 == 0 else c2}"/>')
        o.append(f'<rect x="{x - ww / 2}" y="{y - 1.4}" width="{ww}" height="1.6" fill="{c3}"/>')
        for j in range(-2, 3):
            if abs(j) * 9 < top / 2 - 2:
                o.append(f'<rect x="{x + j * 9 - 1.6}" y="{y - th + 3}" width="3.2" height="{th - 5}" fill="{c3}" opacity=".75"/>')
        y -= th; ww = top
    o.append(f'<path d="M{x - ww / 2 - 2} {y} Q{x} {y - 14} {x + ww / 2 + 2} {y} Z" fill="{c}"/>')
    o.append(f'<rect x="{x - ww / 2 - 2}" y="{y - 1}" width="{ww + 4}" height="2" fill="{c3}"/>')
    for j in (-1, 0, 1):
        o.append(f'<g transform="translate({x + j * ww / 3.2} {y - 9 + abs(j) * 2})"><circle r="2" fill="#ffd43b"/><rect x="-.5" y="-5" width="1" height="3.4" fill="#ffd43b"/></g>')
    return ''.join(o)


def temple():
    o = [sky([(0, '#1c3c90'), (0.55, '#5f7cc8'), (0.85, '#f0b27a'), (1, '#f8d39a')])]
    o.append(sun(118, 82, 15, '#ffd43b'))
    o += [cloud(90, 60, .9, '#fff1d6', .7), cloud(400, 52, 1.1, '#fff1d6', .65)]
    o.append(birds(330, 56, 3, '#5a3418', .7))
    # side vimana
    o.append('<g>' + gopuram(352, 108, 34, tiers=3, th=9) + '</g>')
    # prakara wall with kavi stripes
    o.append('<rect x="20" y="92" width="454" height="18" fill="#f3efe6"/>')
    o += [f'<rect x="{x}" y="92" width="7" height="18" fill="#c0392b"/>' for x in range(24, 470, 14)]
    o.append('<rect x="20" y="89" width="454" height="4" fill="#d8c3a0"/>')
    # main gopuram
    o.append(gopuram(246, 110, 70, tiers=5, th=8.4))
    # dhvaja stambha
    o.append('<rect x="168" y="50" width="3" height="60" fill="#e6b422"/>' + ''.join(f'<rect x="165.5" y="{y}" width="8" height="2" fill="#f2c94c"/>' for y in (56, 64, 72)) +
             '<path d="M169.5 46 l3 4 l-6 0 Z" fill="#f2c94c"/><rect x="163" y="104" width="13" height="6" fill="#c98f45"/>')
    # ground and tank
    o.append('<rect x="0" y="110" width="494" height="40" fill="#d8b98a"/>')
    for k in range(4):
        o.append(f'<rect x="{30 + k * 8}" y="{114 + k * 4}" width="{434 - k * 16}" height="4" fill="{["#c9a774", "#bd9a68", "#b08d5c", "#a48152"][k]}"/>')
    o.append('<rect x="62" y="130" width="370" height="20" fill="#3f8fd2"/>' + waves(70, 420, 138, '#bfe6ff', .7, 24) + waves(82, 420, 145, '#bfe6ff', .6, 30))
    for x in (44, 60, 420, 436, 452):   # lamps on the steps
        o.append(f'<path d="M{x - 3} 114 q3 3 6 0 Z" fill="#a86b2e"/><path d="M{x} 113 q-1.6 -2.6 0 -5 q1.6 2.4 0 5 Z" fill="#ffb02e"/>')
    o += [palm(12, 110, 1.0), palm(482, 110, 1.05, lean=-1), palm(470, 110, .8)]
    return ''.join(o)

# ---------------------------------------------------------------- governance

def icon_bubble(x, y, kind):
    g = [f'<circle cx="{x}" cy="{y}" r="11" fill="#ffffff" opacity=".22"/><circle cx="{x}" cy="{y}" r="11" fill="none" stroke="#e8eefb" stroke-width="1"/>']
    if kind == 'doc':
        g.append(f'<rect x="{x - 4.5}" y="{y - 6}" width="9" height="12" rx="1" fill="#ffffff"/><path d="M{x - 2.5} {y - 2.5} h5 M{x - 2.5} {y} h5" stroke="#7aa9e6" stroke-width=".9"/>'
                 f'<path d="M{x - 2} {y + 3} l1.4 1.4 l2.8 -3" stroke="#12804a" stroke-width="1.2" fill="none"/>')
    elif kind == 'people':
        g.append(f'<circle cx="{x - 3.5}" cy="{y - 3}" r="2.2" fill="#ffffff"/><circle cx="{x + 3.5}" cy="{y - 3}" r="2.2" fill="#ffffff"/>'
                 f'<path d="M{x - 7.5} {y + 5} q4 -7 8 0 Z M{x - .5} {y + 5} q4 -7 8 0 Z" fill="#ffffff"/>')
    elif kind == 'phone':
        g.append(f'<rect x="{x - 4}" y="{y - 7}" width="8" height="14" rx="1.5" fill="#ffffff"/><rect x="{x - 2.6}" y="{y - 5}" width="5.2" height="8.5" fill="#7aa9e6"/>'
                 f'<path d="M{x + 5} {y - 8} a4 4 0 0 1 3 3 M{x + 5} {y - 11} a7 7 0 0 1 6 6" stroke="#ffffff" stroke-width=".9" fill="none"/>')
    elif kind == 'gear':
        teeth = ''.join(f'<rect x="{x - 1.4}" y="{y - 7.5}" width="2.8" height="3" fill="#ffffff" transform="rotate({a} {x} {y})"/>' for a in range(0, 360, 45))
        g.append(teeth + f'<circle cx="{x}" cy="{y}" r="5" fill="#ffffff"/><circle cx="{x}" cy="{y}" r="2" fill="#5b8fd6"/>')
    return ''.join(g)


def governance():
    o = [sky(DAY)]
    o.append(sun(60, 52, 11))
    o += [cloud(150, 50, .8, op=.6), cloud(460, 60, .9, op=.6)]
    # network of e-governance icons
    nodes = [(112, 70, 'doc'), (176, 52, 'people'), (336, 56, 'phone'), (396, 76, 'gear')]
    o.append('<path d="M112 70 L176 52 M336 56 L396 76 M176 52 Q200 40 222 54 M336 56 Q300 40 272 54" stroke="#e8eefb" stroke-width="1" stroke-dasharray="2 3" fill="none" opacity=".8"/>')
    o += [icon_bubble(*n) for n in nodes]
    # far trees line
    o.append('<path d="M0 104 Q40 96 80 102 Q120 94 160 102 L160 112 L0 112 Z M334 102 Q380 94 420 102 Q460 95 494 101 L494 112 L334 112 Z" fill="#3f8a5a"/>')
    # secretariat building
    o.append('<rect x="150" y="80" width="194" height="32" fill="#f4f0e6"/><rect x="150" y="78" width="194" height="4" fill="#d8cfbd"/>')
    o += [f'<rect x="{x}" y="86" width="7" height="9" fill="#7aa9e6"/><rect x="{x}" y="99" width="7" height="9" fill="#7aa9e6"/>' for x in list(range(157, 210, 13)) + list(range(287, 340, 13))]
    o.append('<rect x="212" y="66" width="70" height="46" fill="#fbf8f1"/><path d="M206 68 L247 50 L288 68 Z" fill="#e8e0cf"/>')
    o += [f'<rect x="{x}" y="72" width="4" height="36" fill="#e2d9c6"/>' for x in range(218, 280, 10)]
    o.append('<rect x="210" y="106" width="74" height="3" fill="#d8cfbd"/><rect x="204" y="109" width="86" height="3" fill="#cbbfa8"/>')
    o.append('<rect x="233" y="44" width="28" height="9" fill="#f4f0e6"/><path d="M229 46 A18 16 0 0 1 265 46 Z" fill="#f8f5ee"/>'
             '<path d="M247 30 A18 16 0 0 1 265 46 L247 46 Z" fill="#e2d9c6" opacity=".6"/><rect x="246" y="24" width="2" height="7" fill="#d8cfbd"/><circle cx="247" cy="24" r="1.8" fill="#f2c94c"/>')
    o.append(flag(104, 116, .95))
    # lawn, path and people
    o.append('<rect x="0" y="112" width="494" height="38" fill="#57a85c"/><path d="M220 112 L274 112 L330 150 L164 150 Z" fill="#d9cdb3"/>')
    o += [tree(130, 114, 1.2), tree(362, 114, 1.25), tree(20, 116, 1.0), tree(470, 116, 1.1), tree(400, 118, .9)]
    o += [person(204, 138, .9, '#f2a93b'), person(225, 132, .8, '#5fb4ef', hair='#3a2a1a'), person(282, 136, .9, '#e07b9a'), person(300, 128, .75, '#8fd07a')]
    o.append(birds(400, 48, 3))
    return ''.join(o)

# ---------------------------------------------------------------- ethics & laws

def ethics_laws():
    o = [sky([(0, '#1c3f8f'), (0.6, '#5a8fd8'), (1, '#c9def5')])]
    o += [cloud(300, 50, 1.0, op=.6), cloud(60, 60, .8, op=.55)]
    # court building
    o.append('<rect x="120" y="70" width="170" height="42" fill="#f4f0e6"/><path d="M112 72 L205 44 L298 72 Z" fill="#ebe3d2"/>'
             '<path d="M128 70 L205 49 L282 70 Z" fill="#f8f5ee"/><circle cx="205" cy="62" r="5" fill="#d8cfbd"/>')
    o += [f'<rect x="{x}" y="76" width="7" height="32" fill="#e5dccb"/><rect x="{x - 1.5}" y="74" width="10" height="3" fill="#d8cfbd"/>' for x in range(130, 285, 21)]
    o.append('<rect x="116" y="106" width="178" height="3" fill="#d8cfbd"/><rect x="108" y="109" width="194" height="3" fill="#cbbfa8"/>')
    # ground
    o.append('<rect x="0" y="112" width="494" height="38" fill="#4f9a5a"/><path d="M180 112 L230 112 L262 150 L148 150 Z" fill="#d9cdb3"/>')
    o += [tree(30, 114, 1.3), tree(64, 116, 1.0), tree(318, 114, 1.0)]
    # scales of justice
    o.append('<g transform="translate(412 0)" fill="#f2c94c" stroke="#f2c94c">'
             '<rect x="-2" y="52" width="4" height="66" stroke="none"/><path d="M-14 118 h28 l-4 -6 h-20 Z" stroke="none"/>'
             '<circle cx="0" cy="50" r="4" stroke="none"/><path d="M-40 58 L40 50" stroke-width="3" fill="none"/>'
             '<path d="M-40 58 L-52 84 M-40 58 L-28 84 M40 50 L28 76 M40 50 L52 76" stroke-width="1" fill="none"/>'
             '<path d="M-56 84 h32 a16 6 0 0 1 -32 0 Z" stroke="none"/><path d="M24 76 h32 a16 6 0 0 1 -32 0 Z" stroke="none"/></g>')
    # books stack
    o.append('<g><rect x="322" y="128" width="60" height="10" rx="1.5" fill="#7a2420"/><rect x="326" y="131" width="52" height="1.5" fill="#f2c94c"/>'
             '<rect x="318" y="118" width="64" height="10" rx="1.5" fill="#1f3b8f"/><rect x="322" y="121" width="56" height="1.5" fill="#f2c94c"/>'
             '<rect x="326" y="108" width="52" height="10" rx="1.5" fill="#0e6b3d"/><rect x="330" y="111" width="44" height="1.5" fill="#f2c94c"/>'
             '<rect x="320" y="138" width="66" height="3" fill="#3a2a1a" opacity=".35"/></g>')
    # diya
    o.append('<g transform="translate(82 132)"><circle cy="-14" r="16" fill="url(#glow)"/><path d="M-12 0 Q0 9 12 0 Q6 -4 0 -4 Q-6 -4 -12 0 Z" fill="#c98f45"/>'
             '<path d="M0 -4 q-3.6 -6 0 -12 q3.6 6 0 12 Z" fill="#ffb02e"/><path d="M0 -6 q-1.6 -3 0 -6 q1.6 3 0 6 Z" fill="#fff3b0"/></g>')
    o.append(birds(220, 40, 3))
    return ''.join(o)

# ---------------------------------------------------------------- AP history & culture

def stupa(x, base):
    o = [f'<rect x="{x - 50}" y="{base - 12}" width="100" height="12" fill="#e6d8bb"/>',
         f'<path d="M{x - 44} {base - 12} A44 34 0 0 1 {x + 44} {base - 12} Z" fill="#f4ecd9"/>',
         f'<path d="M{x} {base - 46} A44 34 0 0 1 {x + 44} {base - 12} L{x} {base - 12} Z" fill="#e6d8bb" opacity=".55"/>',
         f'<rect x="{x - 7}" y="{base - 54}" width="14" height="8" fill="#d8c3a0"/>',
         f'<rect x="{x - 1}" y="{base - 66}" width="2" height="12" fill="#a86b2e"/>',
         f'<path d="M{x - 9} {base - 62} h18 l-3 -3 h-12 Z M{x - 7} {base - 67} h14 l-3 -3 h-8 Z" fill="#c98f45"/>']
    o += [f'<rect x="{xx}" y="{base - 9}" width="2.4" height="9" fill="#cbb58e"/>' for xx in range(x - 48, x + 50, 6)]
    o.append(f'<rect x="{x - 50}" y="{base - 10}" width="100" height="1.6" fill="#cbb58e"/>')
    for gx in (x - 22, x + 18):   # torana gateway
        o.append(f'<g fill="#c98f45"><rect x="{gx - 6}" y="{base - 26}" width="2.6" height="26"/><rect x="{gx + 4}" y="{base - 26}" width="2.6" height="26"/>'
                 f'<rect x="{gx - 9}" y="{base - 28}" width="18" height="2.4"/><rect x="{gx - 8}" y="{base - 22}" width="16" height="2"/></g>')
    return ''.join(o)


def ap_history():
    o = [sky([(0, '#1c418f'), (0.55, '#4f84d2'), (1, '#f3d9a8')])]
    o.append(sun(420, 56, 12))
    o += [cloud(250, 46, .9, op=.6), cloud(140, 56, .7, op=.5)]
    o.append(birds(300, 52, 3))
    # hills with fort wall
    o.append('<path d="M150 112 Q210 66 270 80 Q320 62 370 84 Q400 96 430 112 Z" fill="#7a8f6a"/>')
    o.append('<path d="M196 84 Q232 70 270 78 Q316 64 352 80" fill="none" stroke="#b9925e" stroke-width="5"/>')
    o += [f'<rect x="{x}" y="{y}" width="3" height="3" fill="#b9925e"/>' for x, y in ((200, 79), (210, 75), (220, 72), (236, 71), (250, 73), (262, 75), (284, 70), (300, 66), (316, 66), (332, 70), (344, 74))]
    o += [f'<rect x="{x - 5}" y="{y - 8}" width="10" height="12" fill="#a98352"/><rect x="{x - 6}" y="{y - 10}" width="12" height="3" fill="#b9925e"/>' for x, y in ((226, 72), (296, 68), (340, 76))]
    # gopuram on the right
    o.append(gopuram(452, 112, 40, tiers=3, th=9))
    # stupa on the left
    o.append(stupa(86, 112))
    # river and banks
    o.append('<rect x="0" y="112" width="494" height="38" fill="#6aa864"/><path d="M0 128 Q120 120 250 128 Q370 136 494 126 L494 150 L0 150 Z" fill="#3f8fd2"/>')
    o.append(waves(10, 480, 138, '#bfe6ff', .7, 30))
    o.append('<g transform="translate(300 134)"><path d="M-14 0 h28 l-5 5 h-18 Z" fill="#6b4a2b"/><path d="M0 0 V-18 L12 -2 Z" fill="#fff1d6"/><rect x="-.6" y="-18" width="1.2" height="18" fill="#5b3b1f"/></g>')
    o += [palm(160, 114, .9), palm(176, 114, .75, lean=-1), palm(410, 114, .85, lean=-1), tree(384, 116, .9)]
    return ''.join(o)

# ---------------------------------------------------------------- Karnataka economy

def tractor(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-12" y="-12" width="16" height="7" rx="1" fill="#2f9e44"/>'
            '<rect x="0" y="-20" width="9" height="12" fill="#2f9e44"/><rect x="2" y="-18" width="5" height="5" fill="#bfe6ff"/>'
            '<rect x="-9" y="-16" width="1.6" height="5" fill="#3a3a3a"/><circle cx="5" cy="-4" r="6" fill="#2b2b2b"/><circle cx="5" cy="-4" r="2.4" fill="#f2c94c"/>'
            '<circle cx="-8" cy="-2.5" r="3.6" fill="#2b2b2b"/><circle cx="-8" cy="-2.5" r="1.4" fill="#f2c94c"/></g>')


def ka_economy():
    o = [sky(DAY)]
    o.append(sun(300, 50, 11))
    o += [cloud(210, 54, .8, op=.6), cloud(400, 46, .9, op=.55)]
    # Bengaluru towers (right distance)
    for x, hgt, w in ((404, 46, 13), (419, 60, 14), (435, 40, 12), (449, 52, 13), (464, 34, 11)):
        o.append(f'<rect x="{x}" y="{106 - hgt}" width="{w}" height="{hgt}" fill="#a9c8ee"/><rect x="{x + w - 4}" y="{106 - hgt}" width="4" height="{hgt}" fill="#8fb4e6"/>')
        o += [f'<rect x="{x + 2}" y="{106 - hgt + 4 + j * 5}" width="{w - 7}" height="1.6" fill="#e8f2ff"/>' for j in range(hgt // 5 - 1)]
    # Western Ghats with coffee rows
    o.append('<path d="M0 64 Q40 50 80 62 Q120 48 170 70 Q200 82 230 112 L0 112 Z" fill="#2f7d49"/>')
    o.append('<path d="M0 84 Q60 66 120 80 Q170 90 210 112 L0 112 Z" fill="#3e9457"/>')
    for k in range(6):
        y = 74 + k * 6.5
        o.append(f'<path d="M{4 + k * 3} {y + 8} Q{70 + k * 6} {y - 6} {150 + k * 10} {y + 14}" fill="none" stroke="#1f6a3a" stroke-width="2.2" stroke-dasharray="2.4 2.2" stroke-linecap="round"/>')
    o += [pine(40, 66, .8, '#1f6a3a'), pine(98, 60, .9, '#1f6a3a'), pine(150, 72, .8, '#1f6a3a')]
    # plains
    o.append('<path d="M150 108 Q320 100 494 106 L494 150 L0 150 L0 112 Z" fill="#7cc06a"/>')
    # sugarcane patch
    o += [f'<path d="M{x} 128 q1 -12 {(-1) ** x * 2} -20" stroke="#4d9a3a" stroke-width="1.6" fill="none"/><path d="M{x} 116 l5 -4" stroke="#6bbf4f" stroke-width="1.2"/>' for x in range(14, 120, 6)]
    # panchayat office
    o.append('<g><rect x="214" y="92" width="58" height="22" fill="#fbefd6"/><path d="M208 93 L243 78 L278 93 Z" fill="#c2552c"/>'
             '<rect x="236" y="100" width="12" height="14" fill="#7a4d06"/><rect x="220" y="98" width="9" height="7" fill="#7aa9e6"/><rect x="256" y="98" width="9" height="7" fill="#7aa9e6"/>'
             '<rect x="228" y="84" width="30" height="7" fill="#ffffff" stroke="#c2552c" stroke-width=".6"/><rect x="232" y="86.5" width="22" height="1.4" fill="#c2552c" opacity=".6"/></g>')
    o.append(flag(290, 114, .85))
    o.append(tree(200, 114, 1.3, '#3f9a5c'))
    # dairy co-op: milk cans
    for x in (306, 316, 326):
        o.append(f'<g transform="translate({x} 114)"><rect x="-4" y="-12" width="8" height="12" rx="1.2" fill="#d6dfec"/><rect x="-2.5" y="-15" width="5" height="3" fill="#c5ccd8"/><rect x="-4" y="-8" width="8" height="1.4" fill="#9aa8c2"/></g>')
    # paddy field rows and road
    o.append('<path d="M120 150 Q260 122 494 128 L494 150 Z" fill="#8fd07a"/>')
    o += [f'<path d="M{140 + k * 18} 150 Q{300 + k * 6} 130 494 {130 + k * 2.8}" fill="none" stroke="#5fae4f" stroke-width=".9"/>' for k in range(7)]
    o.append('<path d="M150 150 Q250 128 340 118 Q400 112 494 112" fill="none" stroke="#d9cdb3" stroke-width="5"/>')
    o.append(tractor(356, 120, 1.1))
    o.append(birds(130, 44, 3))
    return ''.join(o)

# ---------------------------------------------------------------- Karnataka history

def ka_history():
    o = [sky([(0, '#1c418f'), (0.55, '#4f84d2'), (1, '#f5dcae')])]
    o.append(sun(300, 54, 11))
    o += [cloud(180, 50, .8, op=.55), cloud(440, 48, .9, op=.55)]
    # Jog falls cliff (left)
    o.append('<path d="M0 58 L64 58 Q76 60 80 70 L86 112 L0 112 Z" fill="#355e3b"/><path d="M0 58 L64 58 Q72 59 76 64 L0 66 Z" fill="#2c7a46"/>')
    o += [pine(10, 60, .8, '#1f6a3a'), pine(30, 59, .7, '#1f6a3a'), pine(50, 60, .75, '#1f6a3a')]
    o.append('<path d="M60 62 C64 80 62 96 66 112 L80 112 C76 96 78 80 74 64 Z" fill="#e8f4ff"/>')
    o += [f'<path d="M{x} 66 C{x + 2} 82 {x} 98 {x + 2} 112" stroke="#bfe0ff" stroke-width="1" fill="none"/>' for x in (64, 68, 72)]
    o.append('<ellipse cx="72" cy="114" rx="22" ry="5" fill="#ffffff" opacity=".7"/>')
    # boulders
    for cx, cy, rx, ry, c in ((150, 104, 22, 14, '#c58a52'), (178, 96, 16, 12, '#d39a5e'), (130, 110, 14, 9, '#b47a44'), (196, 106, 12, 8, '#b47a44'), (164, 84, 10, 8, '#c58a52')):
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{c}"/><ellipse cx="{cx - rx * .3}" cy="{cy - ry * .35}" rx="{rx * .45}" ry="{ry * .3}" fill="#e2b380" opacity=".55"/>')
    # stone chariot (Hampi)
    o.append('<g transform="translate(250 112)">'
             '<rect x="-24" y="-8" width="48" height="8" fill="#b8a89a"/><rect x="-20" y="-30" width="40" height="22" fill="#cdbfb2"/>'
             '<path d="M-20 -30 L-14 -40 L14 -40 L20 -30 Z" fill="#b8a89a"/><path d="M-12 -40 L-8 -48 L8 -48 L12 -40 Z" fill="#cdbfb2"/>'
             '<path d="M-6 -48 L0 -56 L6 -48 Z" fill="#b8a89a"/><rect x="-6" y="-24" width="12" height="16" fill="#8f8073"/>'
             '<g fill="none" stroke="#6f6156" stroke-width="1.6"><circle cx="-14" cy="-6" r="8"/><circle cx="14" cy="-6" r="8"/></g>'
             '<path d="M-14 -14 V2 M-22 -6 H-6 M14 -14 V2 M6 -6 H22" stroke="#6f6156" stroke-width=".9"/></g>')
    # Gol Gumbaz (right)
    o.append('<g transform="translate(410 112)">'
             '<rect x="-38" y="-34" width="76" height="34" fill="#a39486"/><rect x="-38" y="-36" width="76" height="3" fill="#8f8073"/>'
             '<path d="M-30 -36 A30 30 0 0 1 30 -36 Z" fill="#b8a89a"/><path d="M0 -66 A30 30 0 0 1 30 -36 L0 -36 Z" fill="#a39486" opacity=".6"/>'
             '<rect x="-1" y="-72" width="2" height="7" fill="#8f8073"/>'
             + ''.join(f'<rect x="{x - 5}" y="-50" width="10" height="50" fill="#9a8b7d"/><path d="M{x - 6} -50 A6 6 0 0 1 {x + 6} -50 Z" fill="#b8a89a"/>'
                       + ''.join(f'<rect x="{x - 3}" y="{y}" width="6" height="3" fill="#7d6f63"/>' for y in (-44, -36, -28, -20)) for x in (-38, 38)) +
             '<path d="M-10 0 V-18 A10 10 0 0 1 10 -18 V0 Z" fill="#6f6156"/>'
             + ''.join(f'<path d="M{x} -6 V-20 A4 4 0 0 1 {x + 8} -20 V-6 Z" fill="#7d6f63"/>' for x in (-30, 22)) + '</g>')
    # ground, river
    o.append('<rect x="0" y="112" width="494" height="38" fill="#8a9f5a"/><path d="M0 132 Q140 124 260 134 Q380 142 494 132 L494 150 L0 150 Z" fill="#3f8fd2"/>')
    o.append(waves(10, 480, 141, '#bfe6ff', .7, 30))
    o += [palm(320, 114, .85), palm(336, 114, .7, lean=-1), tree(470, 116, 1.0), tree(104, 116, .9)]
    o.append(birds(330, 44, 3))
    return ''.join(o)

# ---------------------------------------------------------------- computer skill test (green theme)

def computer_skill():
    o = [f'<defs>{lin("wall", [(0, "#0d3d28"), (1, "#17694a")])}{rad("glow", "#ffe9a0")}{lin("scr", [(0, "#ffffff"), (1, "#eef8f2")])}</defs>',
         '<rect width="494" height="150" fill="url(#wall)"/>']
    # window with sky
    o.append('<rect x="20" y="42" width="72" height="58" rx="3" fill="#9fd4b4"/><rect x="24" y="46" width="64" height="50" fill="#bfe6ff"/>'
             '<path d="M56 46 V96 M24 71 H88" stroke="#9fd4b4" stroke-width="3"/>' + cloud(44, 62, .5, '#ffffff', .9) + sun(76, 58, 5))
    # wall clock (one hour)
    o.append('<g transform="translate(440 62)"><circle r="16" fill="#f3f9f5" stroke="#8fd6a8" stroke-width="2"/><path d="M0 0 V-10 M0 0 L8 3" stroke="#0b3d2a" stroke-width="1.8" stroke-linecap="round"/>'
             + ''.join(f'<rect x="-.6" y="-14" width="1.2" height="3" fill="#0b3d2a" transform="rotate({a})"/>' for a in range(0, 360, 30)) +
             '<path d="M0 -16 A16 16 0 0 1 16 0 L0 0 Z" fill="#12804a" opacity=".25"/></g>')
    # desk
    o.append('<rect x="0" y="118" width="494" height="32" fill="#a0703f"/><rect x="0" y="116" width="494" height="4" fill="#c08a52"/>')
    # monitor with spreadsheet
    o.append('<rect x="132" y="38" width="170" height="76" rx="4" fill="#1d2a24"/><rect x="137" y="43" width="160" height="64" fill="url(#scr)"/>'
             '<rect x="137" y="43" width="160" height="6" fill="#12804a"/><rect x="137" y="49" width="160" height="5" fill="#e7f6ee"/>'
             + ''.join(f'<rect x="{140 + k * 12}" y="50.5" width="8" height="2" fill="#12804a" opacity=".5"/>' for k in range(6)) +
             '<rect x="207" y="114" width="20" height="6" fill="#1d2a24"/><rect x="194" y="118" width="46" height="3" rx="1" fill="#2a3a33"/>')
    gx, gy = 140, 58
    for r in range(7):
        for c in range(5):
            fill = '#cfe3d6' if r == 0 else '#ffffff'
            o.append(f'<rect x="{gx + c * 18}" y="{gy + r * 6.6}" width="18" height="6.6" fill="{fill}" stroke="#bfd8c8" stroke-width=".4"/>')
            if r > 0 and c > 0:
                o.append(f'<rect x="{gx + c * 18 + 4}" y="{gy + r * 6.6 + 2.6}" width="{6 + (r * c) % 7}" height="1.4" fill="#55627c" opacity=".6"/>')
    for k, hgt in enumerate((14, 22, 18, 30, 26)):   # chart
        o.append(f'<rect x="{240 + k * 10}" y="{102 - hgt}" width="7" height="{hgt}" fill="{["#12804a", "#2f9e66", "#f2b705", "#0e7c86", "#7bd389"][k]}"/>')
    o.append('<path d="M236 102 H292" stroke="#9aa8c2" stroke-width=".8"/>')
    # document (Word) on the right
    o.append('<g transform="translate(330 46) rotate(4)"><rect width="62" height="76" rx="2" fill="#ffffff"/><rect x="6" y="7" width="34" height="4" fill="#0b3d2a"/>'
             + ''.join(f'<rect x="6" y="{16 + k * 5}" width="{50 - (k % 3) * 6}" height="1.8" fill="#9aa8c2"/>' for k in range(8)) +
             '<rect x="6" y="58" width="22" height="12" fill="#cfe3d6"/><path d="M8 68 l5 -5 l4 3 l6 -6" stroke="#12804a" stroke-width="1" fill="none"/></g>')
    # keyboard and mouse
    o.append('<rect x="160" y="124" width="104" height="14" rx="2" fill="#e7efe9"/>' +
             ''.join(f'<rect x="{164 + k * 8}" y="{127 + r * 4}" width="6" height="2.6" rx=".6" fill="#b9c9bf"/>' for r in range(2) for k in range(12)) +
             '<rect x="186" y="135" width="52" height="2" rx=".6" fill="#b9c9bf"/>'
             '<ellipse cx="282" cy="132" rx="6" ry="8" fill="#e7efe9"/><path d="M282 124 V130" stroke="#b9c9bf" stroke-width="1"/>')
    # mug and plant
    o.append('<g transform="translate(100 124)"><rect x="-7" y="-14" width="14" height="16" rx="2" fill="#f2b705"/><path d="M7 -10 q6 0 6 5 q0 5 -6 5" fill="none" stroke="#f2b705" stroke-width="2"/>'
             '<path d="M-3 -18 q2 -3 0 -6 M2 -18 q2 -3 0 -6" stroke="#ffffff" stroke-width="1" fill="none" opacity=".7"/></g>')
    o.append('<g transform="translate(430 124)"><path d="M-9 -12 h18 l-3 14 h-12 Z" fill="#c2552c"/>'
             '<path d="M0 -12 q-14 -10 -12 -24 q8 8 12 24 M0 -12 q4 -16 14 -20 q-2 12 -14 20 M0 -12 q-2 -20 4 -28 q4 14 -4 28" fill="#2f9e44"/></g>')
    return ''.join(o)

# ---------------------------------------------------------------- EPFO current affairs

def epfo_ca():
    o = [sky(DAY)]
    o.append(sun(470, 50, 10))
    o += [cloud(300, 48, .8, op=.55), cloud(160, 44, .7, op=.5)]
    # city and factories skyline
    sk = [(200, 36, 14), (216, 50, 12), (230, 28, 16), (330, 44, 12), (344, 30, 14), (360, 54, 12), (374, 34, 16), (392, 26, 14)]
    for x, hgt, w in sk:
        o.append(f'<rect x="{x}" y="{106 - hgt}" width="{w}" height="{hgt}" fill="#9fc0ea"/>')
        o += [f'<rect x="{x + 3}" y="{106 - hgt + 4 + j * 6}" width="{w - 6}" height="2" fill="#d6e4f7"/>' for j in range(hgt // 6 - 1)]
    o.append('<path d="M410 106 V86 L424 94 V86 L438 94 V86 L452 94 V106 Z" fill="#8fb4e6"/><rect x="456" y="70" width="6" height="36" fill="#8fb4e6"/>'
             '<circle cx="462" cy="64" r="4" fill="#ffffff" opacity=".55"/><circle cx="468" cy="58" r="5" fill="#ffffff" opacity=".4"/>')
    # ground
    o.append('<rect x="0" y="112" width="494" height="38" fill="#57a85c"/><path d="M0 106 H494 V114 H0 Z" fill="#4c9c4f"/>')
    # globe
    o.append('<g transform="translate(70 84)"><circle r="24" fill="#2f7fd0"/>'
             '<path d="M-14 -14 q8 -4 12 2 q-2 8 -10 8 q-6 4 -4 10 q-8 -4 -8 -10 Z M4 -20 q10 2 14 10 q-6 2 -8 8 q-6 -4 -6 -10 Z M2 6 q8 -2 12 4 q-2 8 -8 10 q-6 -6 -4 -14 Z" fill="#5fbf6a"/>'
             '<g fill="none" stroke="#bfe6ff" stroke-width=".7" opacity=".8"><ellipse rx="24" ry="8"/><ellipse rx="10" ry="24"/><path d="M-24 0 H24 M0 -24 V24"/></g>'
             '<path d="M-28 22 q28 14 56 0" stroke="#d6dfec" stroke-width="3" fill="none"/><rect x="-3" y="26" width="6" height="8" fill="#d6dfec"/><rect x="-12" y="33" width="24" height="3" rx="1" fill="#c5ccd8"/></g>')
    # newspaper
    o.append('<g transform="translate(108 96) rotate(-8)"><rect width="46" height="34" fill="#ffffff"/><rect x="4" y="4" width="38" height="5" fill="#0c2266"/>'
             '<rect x="4" y="12" width="17" height="12" fill="#c3d1f1"/>' + ''.join(f'<rect x="24" y="{12 + k * 3.4}" width="18" height="1.6" fill="#9aa8c2"/>' for k in range(4)) +
             ''.join(f'<rect x="4" y="{27 + k * 3}" width="38" height="1.4" fill="#9aa8c2"/>' for k in range(2)) + '</g>')
    # ground
    # shield with rupee
    o.append('<g transform="translate(278 50)"><path d="M0 0 L30 10 V36 Q30 62 0 76 Q-30 62 -30 36 V10 Z" fill="#0c2266" stroke="#ffd43b" stroke-width="2.4"/>'
             '<path d="M0 8 L22 15 V36 Q22 56 0 67 Z" fill="#1846c7" opacity=".7"/>' + rupee(0, 46, 26, '#ffd43b') + '</g>')
    # workers
    hat = '<path d="M-4.6 -20 a4.6 4.6 0 0 1 9.2 0 h1.6 v1.4 h-12.4 v-1.4 Z" fill="#f2b705"/>'
    tie = '<path d="M0 -14 l1.4 3 l-1.4 7 l-1.4 -7 Z" fill="#c2352c"/>'
    o += [person(212, 140, 1.25, '#e07b00', extra=hat), person(236, 142, 1.3, '#ffffff', hair='#1a1a1a', extra=tie),
          person(326, 142, 1.25, '#c2357a', hair='#1a1a1a', extra='<path d="M-5 -12 Q0 -6 5 -12 L5 -8 Q0 -2 -5 -8 Z" fill="#ffd43b"/>'),
          person(350, 140, 1.2, '#0e7c86', extra=hat)]
    # coins
    o += [f'<ellipse cx="420" cy="{136 - k * 4}" rx="11" ry="3.6" fill="#f2b705" stroke="#c98f05" stroke-width=".8"/>' for k in range(5)]
    o += [f'<ellipse cx="446" cy="{138 - k * 4}" rx="10" ry="3.4" fill="#f2b705" stroke="#c98f05" stroke-width=".8"/>' for k in range(3)]
    o += [tree(20, 116, 1.0), tree(482, 116, 1.1)]
    o.append(birds(250, 26, 3))
    return ''.join(o)


SCENES = {
    'apeco-en': ap_economy, 'apeco-te': ap_economy, 'stfull-en': science_tech, 'eohp-en': temple, 'eohp-te': temple,
    'g1pa-en': governance, 'g1eth-en': ethics_laws, 'aphist-en': ap_history, 'kaeco-en': ka_economy,
    'kahis-en': ka_history, 'cst-en': computer_skill, 'epfoca-en': epfo_ca,
}
