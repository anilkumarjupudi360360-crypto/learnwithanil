"""Measure the foreground blocks of a cover: middle intervals (tag .. INSIDE list) and the author block."""
import pymupdf

def measure(fg_pdf):
    p = pymupdf.open(fg_pdf)[0]
    items = []
    for b in p.get_text('dict')['blocks']:
        if b['type'] == 0 and b['lines']:
            items.append(pymupdf.Rect(b['bbox']))
    for dr in p.get_drawings():
        r = dr['rect']
        if r.width > 590 and r.height > 800: continue
        items.append(pymupdf.Rect(r))
    imgs = [pymupdf.Rect(i['bbox']) for i in p.get_image_info(xrefs=True) if i['xref'] and i['bbox'][1] > 600]
    author_top = min(i.y0 for i in imgs)
    mid = [r for r in items if 98 < r.y0 < author_top - 8 and r.height < 300]
    mid.sort(key=lambda r: r.y0)
    iv = []
    for r in mid:
        if iv and r.y0 <= iv[-1][1] + 6: iv[-1][1] = max(iv[-1][1], r.y1)
        else: iv.append([r.y0, r.y1])
    return dict(intervals=iv, author_top=author_top)

if __name__ == '__main__':
    import sys
    print(measure(sys.argv[1]))
