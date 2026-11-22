"""Plan the new cover layout: picture panel at the top, the old foreground re-flowed below it."""
from measure import measure

PANEL_TOP, PANEL_GAP, GAP_CAP, H_MIN, H_MAX, AUTHOR_MIN = 105, 22, 22, 112, 150, 765

def plan(fg_pdf):
    m = measure(fg_pdf)
    iv = [list(x) for x in m['intervals']]
    rule = None
    if iv and iv[-1][1] - iv[-1][0] < 2:          # separator rule above the author block
        rule = iv.pop()
    a_old = m['author_top']
    a_new = max(a_old, AUTHOR_MIN)
    if a_new + 59 > 836: a_new = 836 - 59          # keep the round photo inside the page
    bottom_pad = min(a_old - iv[-1][1], 29)
    mid_end = a_new - bottom_pad
    gaps = [iv[k + 1][0] - iv[k][1] for k in range(len(iv) - 1)]
    capped = [min(g, GAP_CAP) for g in gaps]
    content = sum(b - a for a, b in iv)
    L = content + sum(capped)
    h = max(H_MIN, min(H_MAX, mid_end - PANEL_TOP - PANEL_GAP - L))
    T = PANEL_TOP + h + PANEL_GAP
    avail = mid_end - T
    s = min(1.0, avail / L)
    if s == 1.0:   # give back spare room to the gaps that were capped
        spare = avail - L
        extra = [g - c for g, c in zip(gaps, capped)]
        tot = sum(extra)
        if tot > 0:
            capped = [c + e * min(1, spare / tot) for c, e in zip(capped, extra)]
    place, y = [], T
    for k, (a, b) in enumerate(iv):
        place.append(((a, b), y))
        y += (b - a) * s + (capped[k] * s if k < len(capped) else 0)
    author_clip = ((rule[0] - 3) if rule else a_old - 16, 842)
    return dict(h=h, s=s, T=T, place=place, author_clip=author_clip, author_shift=a_new - a_old, end=y)
