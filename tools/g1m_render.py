"""Model-answer markup -> HTML with diagrams (APPSC Group-1 Mains answers, tools/g1mains.py).

Anil, 1 Nov 2026: the intro must carry 2-3 key words, the body must be more elaborate with points, and answers should have
relevant diagrams, flowcharts and maps. Answers are written in a small markup; blocks are separated by a blank line:

    plain paragraph            **bold** for key words and sub-headings
    - bullet                   a block of lines starting with "- "
    ::keys A | B | C           key-word chips (shown above the answer)
    ::flow Title               one step per line (a flowchart: step -> step -> step)
    ::cycle Title              one step per line (a cycle: the last step leads back to the first)
    ::hub Centre               one spoke per line (a mind map around the centre)
    ::table Title              rows "a | b | c", the first row is the header
    ::timeline Title           rows "year | event"
    ::bars Title (unit)        rows "label | number"
    ::map ap Title             Andhra Pradesh outline with districts (schematic). Rows (legend: Text  explains the shading):
                                 point: Name | lat | lon [| left]     a place (dot + label; "left" puts the label on the left)
                                 line: Name | lat,lon; lat,lon; ...  a track or river (arrow at the end)
                                 zone: Label | lat | lon             a large italic label for a region
                                 shade: District, District           districts to shade (2011 census districts)
India-level maps are not drawn (India's external boundary must follow the Survey of India); use a table or flowchart.
"""
import html, json, math, os, re

esc = lambda s: html.escape(str(s), quote=True)
_GEO = None
GEO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'appsc-group-1', 'mains-pyqs', 'geo.json')


def geo():
    global _GEO
    if _GEO is None: _GEO = json.load(open(GEO_PATH)) if os.path.exists(GEO_PATH) else {}
    return _GEO


def inline(s):
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', esc(s))


def wrap(s, n):
    out, cur = [], ''
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > n: out.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    if cur: out.append(cur)
    return out


def svg_text(x, y, s, n, size=13, anchor='middle', weight=400, fill='var(--ink)'):
    lines = wrap(s, n)
    y0 = y - (len(lines) - 1) * size * 0.6
    return ''.join(f'<text x="{x:.1f}" y="{y0 + i * size * 1.2:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" dominant-baseline="middle">{esc(l)}</text>'
                   for i, l in enumerate(lines))


def fig(title, inner, cls=''):
    cap = f'<figcaption>{inline(title)}</figcaption>' if title else ''
    return f'<figure class="dg {cls}">{inner}{cap}</figure>'


def d_flow(title, rows):
    steps = ''.join((f'<span class="dg-arr" aria-hidden="true"></span>' if i else '') + f'<div class="dg-step">{inline(r)}</div>' for i, r in enumerate(rows))
    return fig(title, f'<div class="dg-flow">{steps}</div>')


def d_timeline(title, rows):
    items = ''.join(f'<li><b>{inline(a)}</b><span>{inline(b)}</span></li>' for a, b in (r.split('|', 1) if '|' in r else (r, '') for r in rows))
    return fig(title, f'<ol class="dg-tl">{items}</ol>')


def d_table(title, rows):
    cells = [[c.strip() for c in r.split('|')] for r in rows]
    head = ''.join(f'<th>{inline(c)}</th>' for c in cells[0])
    body = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in cells[1:])
    return fig(title, f'<div class="dg-tw"><table class="dg-tab"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def d_hub(title, rows):
    n = len(rows); W, H = 640, 360; cx, cy = W / 2, H / 2
    rx, ry = 230, 128
    parts = []
    for i, r in enumerate(rows):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="2"/>')
    for i, r in enumerate(rows):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        lines = wrap(r, 18); h = 14 + 16 * len(lines)
        parts.append(f'<rect x="{x - 78:.1f}" y="{y - h / 2:.1f}" width="156" height="{h}" rx="9" fill="var(--surface)" stroke="var(--accent)" stroke-width="1.5"/>'
                     + svg_text(x, y, r, 18, 13))
    parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="92" ry="40" fill="var(--accent)"/>' + svg_text(cx, cy, title, 16, 14, weight=700, fill='#fff'))
    return fig('', f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">{"".join(parts)}</svg>', 'dg-svg')


def d_cycle(title, rows):
    n = len(rows); W, H = 640, 380; cx, cy, R = W / 2, H / 2 + 6, 140
    pts = [(cx + R * 1.45 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), cy + R * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
    parts = ['<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="var(--accent)"/></marker></defs>']
    hh = [(14 + 16 * len(wrap(r, 18))) / 2 + 7 for r in rows]
    def edge(i, ux, uy):   # distance from box i's centre to its edge along (ux, uy), plus a gap
        return min(85 / abs(ux) if ux else 1e9, hh[i] / abs(uy) if uy else 1e9)
    for i in range(n):
        j = (i + 1) % n
        (x1, y1), (x2, y2) = pts[i], pts[j]
        L = math.hypot(x2 - x1, y2 - y1) or 1; ux, uy = (x2 - x1) / L, (y2 - y1) / L
        e1, e2 = edge(i, ux, uy), edge(j, ux, uy)
        if e1 + e2 > L - 16: e1 = e2 = max((L - 16) / 2, 0)
        sx, sy = x1 + ux * e1, y1 + uy * e1
        ex, ey = x2 - ux * e2, y2 - uy * e2
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        dx, dy = mx - cx, my - cy; d = math.hypot(dx, dy) or 1
        qx, qy = mx + dx / d * 18, my + dy / d * 18
        parts.append(f'<path d="M{sx:.1f} {sy:.1f} Q{qx:.1f} {qy:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="var(--accent)" stroke-width="2" marker-end="url(#ah)"/>')
    for (x, y), r in zip(pts, rows):
        lines = wrap(r, 18); h = 14 + 16 * len(lines)
        parts.append(f'<rect x="{x - 78:.1f}" y="{y - h / 2:.1f}" width="156" height="{h}" rx="9" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>' + svg_text(x, y, r, 18, 13))
    parts.append(svg_text(cx, cy, title, 18, 14, weight=700, fill='var(--accent-text)'))
    return fig('', f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">{"".join(parts)}</svg>', 'dg-svg')


def d_bars(title, rows):
    data = []
    for r in rows:
        a, b = r.rsplit('|', 1); data.append((a.strip(), float(b.replace(',', '').strip())))
    W, row = 640, 34; H = row * len(data) + 16; mx = max(v for _, v in data) or 1
    parts = []
    for i, (lab, v) in enumerate(data):
        y = 8 + i * row; w = (W - 330) * v / mx
        parts.append(f'<text x="210" y="{y + row / 2:.1f}" font-size="13.5" text-anchor="end" dominant-baseline="middle" fill="var(--ink)">{esc(lab)}</text>'
                     f'<rect x="220" y="{y + 6}" width="{max(w, 2):.1f}" height="{row - 12}" rx="4" fill="var(--accent)"/>'
                     f'<text x="{226 + w:.1f}" y="{y + row / 2:.1f}" font-size="13.5" dominant-baseline="middle" font-weight="700" fill="var(--ink)">{v:g}</text>')
    return fig(title, f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">{"".join(parts)}</svg>', 'dg-svg')


def d_map(kind, title, rows):
    g = geo().get('ap') if kind == 'ap' else None
    if not g: return fig(title, '<p class="muted">[map]</p>')
    allpts = [p for rings in g.values() for ring in rings for p in ring]
    for r in rows:   # include tracks and places that lie out at sea
        if r.startswith('line:'):
            allpts += [[float(q.split(',')[1]), float(q.split(',')[0])] for q in r.split('|', 1)[1].split(';') if q.strip()]
        elif r.startswith(('point:', 'zone:')):
            bits = [x.strip() for x in r.split(':', 1)[1].split('|')]
            allpts.append([float(bits[2]), float(bits[1])])
    lon0, lon1 = min(p[0] for p in allpts) - .25, max(p[0] for p in allpts) + .35
    lat0, lat1 = min(p[1] for p in allpts) - .2, max(p[1] for p in allpts) + .2
    k = math.cos(math.radians((lat0 + lat1) / 2))
    W = 640; pad = 14; sx = (W - 2 * pad) / ((lon1 - lon0) * k); H = (lat1 - lat0) * sx + 2 * pad
    P = lambda lon, lat: (pad + (lon - lon0) * k * sx, pad + (lat1 - lat) * sx)
    shade = set()
    for r in rows:
        if r.startswith('shade:'): shade |= {x.strip().lower() for x in r[6:].split(',')}
    parts = ['<defs><marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--bad,#B42318)"/></marker></defs>']
    for name, rings in g.items():
        fill = 'var(--accent)' if name.lower() in shade else 'var(--accent-soft)'
        op = ' fill-opacity=".55"' if name.lower() in shade else ''
        d = ''.join('M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in (P(*p) for p in ring)) + 'Z' for ring in rings)
        parts.append(f'<path d="{d}" fill="{fill}"{op} stroke="var(--muted)" stroke-width=".7"/>')
    # Bay of Bengal label (lower right, out at sea)
    bx, by = P(lon1 - (lon1 - lon0) * 0.16, lat0 + (lat1 - lat0) * 0.12)
    parts.append(f'<text x="{bx:.1f}" y="{by:.1f}" font-size="14" font-style="italic" fill="var(--accent-text)" text-anchor="middle">Bay of Bengal</text>')
    for r in rows:
        if r.startswith('line:'):
            nm, pts = r[5:].split('|', 1)
            xy = [P(float(b), float(a)) for a, b in (q.strip().split(',') for q in pts.split(';') if q.strip())]
            parts.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in xy)}" fill="none" stroke="var(--bad,#B42318)" stroke-width="2.2" stroke-dasharray="6 4" marker-end="url(#am)"/>')
            x, y = xy[0]
            right = x > W - 130   # near the right edge: put the label to the left of the track's start
            parts.append(f'<text x="{x + (-6 if right else 6):.1f}" y="{y - 6:.1f}" font-size="12.5" font-weight="700" text-anchor="{"end" if right else "start"}" fill="var(--bad,#B42318)">{esc(nm.strip())}</text>')
        elif r.startswith('zone:'):
            nm, a, b = [x.strip() for x in r[5:].split('|')]
            x, y = P(float(b), float(a))
            parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="15" font-weight="700" font-style="italic" fill="var(--accent-text)" text-anchor="middle" opacity=".9">{esc(nm)}</text>')
        elif r.startswith('point:'):
            bits = [x.strip() for x in r[6:].split('|')]
            nm, a, b = bits[:3]; left = len(bits) > 3 and bits[3] == 'left'
            x, y = P(float(b), float(a))
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="var(--ink)" stroke="var(--surface)" stroke-width="1.5"/>'
                         f'<text x="{x + (-8 if left else 8):.1f}" y="{y:.1f}" font-size="13" text-anchor="{"end" if left else "start"}" dominant-baseline="middle" fill="var(--ink)" font-weight="600" paint-order="stroke" stroke="var(--surface)" stroke-width="3">{esc(nm)}</text>')
    legend = ''.join(f'<span>{inline(r[7:].strip())}</span>' for r in rows if r.startswith('legend:'))
    note = (f'<p class="dg-legend">{legend}</p>' if legend else '') + '<p class="dg-note">Schematic map of Andhra Pradesh (2011 census district outlines), not to scale; for study only.</p>'
    return fig(title, f'<svg viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{esc(title)}">{"".join(parts)}</svg>' + note, 'dg-svg dg-map')


def render(t):
    out, keys = [], ''
    for para in t.strip().split('\n\n'):
        lines = [l.rstrip() for l in para.split('\n') if l.strip()]
        if not lines: continue
        head = lines[0]
        if head.startswith('::'):
            kind, _, rest = head[2:].partition(' ')
            rows = [l.strip() for l in lines[1:]]
            if kind == 'keys':
                keys = '<p class="dg-keys">' + ''.join(f'<span>{inline(k.strip())}</span>' for k in rest.split('|') if k.strip()) + '</p>'
            elif kind == 'flow': out.append(d_flow(rest, rows))
            elif kind == 'cycle': out.append(d_cycle(rest, rows))
            elif kind == 'hub': out.append(d_hub(rest, rows))
            elif kind == 'table': out.append(d_table(rest, rows))
            elif kind == 'timeline': out.append(d_timeline(rest, rows))
            elif kind == 'bars': out.append(d_bars(rest, rows))
            elif kind == 'map':
                mk, _, title = rest.partition(' ')
                out.append(d_map(mk, title, rows))
            continue
        if all(l.startswith('- ') for l in lines):
            out.append('<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in lines) + '</ul>')
        else:
            out.append(f'<p>{inline(" ".join(lines))}</p>')
    return keys + ''.join(out)


CSS = ('.dg{margin:12px 0 14px;padding:0}.dg figcaption{font-size:13.5px;color:var(--muted);margin-top:6px;text-align:center}'
       '.dg svg{width:100%;height:auto;display:block;background:var(--surface);border:1px solid var(--line);border-radius:10px}'
       '.dg-flow{display:flex;flex-wrap:wrap;align-items:center;gap:6px}.dg-step{flex:1 1 120px;background:var(--accent-soft);border:1.5px solid var(--accent);'
       'border-radius:9px;padding:7px 9px;font-size:14.5px;line-height:1.35;font-weight:600;text-align:center}'
       '.dg-arr{flex:0 0 18px;height:18px;position:relative}.dg-arr::before{content:"\\2192";position:absolute;inset:0;text-align:center;color:var(--accent);font-weight:800;font-size:18px;line-height:18px}'
       '@media (max-width:640px){.dg-flow{flex-direction:column;align-items:stretch}.dg-step{flex:none}.dg-arr::before{content:"\\2193"}.dg-arr{flex:none;width:100%}}'
       '.dg-tl,.mans .dg-tl{list-style:none;padding:0 0 0 14px;margin:0;border-left:3px solid var(--accent)}.dg-tl li{position:relative;margin:0 0 8px;padding-left:10px}'
       '.dg-tl li::before{content:"";position:absolute;left:-22px;top:7px;width:11px;height:11px;border-radius:50%;background:var(--accent)}'
       '.dg-tl b{display:inline-block;min-width:58px;margin-right:6px;color:var(--accent-text)}'
       '.dg-tw{overflow-x:auto}.dg-tab{border-collapse:collapse;width:100%;font-size:14.5px;background:var(--surface)}.dg-tab th,.dg-tab td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}'
       '.dg-tab th{background:var(--accent-soft)}.dg-keys{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 8px}.dg-keys span{background:var(--accent);color:#fff;border-radius:999px;padding:2px 10px;font-size:13.5px;font-weight:700}'
       '.dg-note{font-size:12.5px;color:var(--muted);margin:4px 0 0;text-align:center}.dg-map svg{max-width:560px;margin:0 auto}'
       '.dg-legend{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 14px;font-size:13px;margin:6px 0 0}.dg-legend span::before{content:"";display:inline-block;width:12px;height:12px;border-radius:3px;background:var(--accent);opacity:.55;margin-right:5px;vertical-align:-1px}')
