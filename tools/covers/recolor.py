"""Recolour a navy-themed Learn with Anil book PDF to the green theme (the AEE book's palette)."""
import pymupdf, re

NAVY2GREEN = {
    '#0c2266': '#0b3d2a', '#0d1830': '#0a2a1d', '#c3d1f1': '#cfe3d6', '#e8eefb': '#e7f6ee', '#9aa8c2': '#93ad9f',
    '#1846c7': '#12804a', '#f4f7fc': '#f3f9f5', '#eef3ff': '#ecf7f0', '#1440b8': '#166534', '#e2eafc': '#ddf3e7',
    '#fcfdff': '#fbfefc', '#d6dfec': '#d2e2d8', '#dce3ee': '#d8e6dd',
}
RX = re.compile(rb'(-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (rg|RG)\b')


def hx(t): return '#%02x%02x%02x' % tuple(max(0, min(255, round(float(x) * 255))) for x in t)


def fmt(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return s.replace('0.', '.', 1) if s.startswith('0.') else (s or '0')


def sub(m):
    h = hx(m.group(1, 2, 3))
    if h not in NAVY2GREEN: return m.group(0)
    n = NAVY2GREEN[h]
    vals = [int(n[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return (' '.join(fmt(v) for v in vals) + ' ').encode() + m.group(4)


def recolor(doc, first=1):
    done, hits = set(), 0
    for pno in range(first, len(doc)):
        page = doc[pno]
        xrefs = list(page.get_contents())
        for item in page.get_xobjects():
            xrefs.append(item[0])
        for x in xrefs:
            if x in done: continue
            done.add(x)
            if doc.xref_get_key(x, 'Subtype')[1] not in ('/Form', 'null') and x not in page.get_contents(): continue
            s = doc.xref_stream(x)
            if s is None: continue
            new, n = RX.subn(sub, s)
            new2 = new
            if new2 != s:
                doc.update_stream(x, new2); hits += n
    return hits
