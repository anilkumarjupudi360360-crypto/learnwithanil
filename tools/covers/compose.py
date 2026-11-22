"""Build a new cover page: background + picture panel + the old foreground re-flowed below the panel.
Returns a one-page PDF (bytes)."""
import pymupdf, subprocess, tempfile, os
from layout import plan, PANEL_TOP

CHROME = '/usr/bin/google-chrome'

def render_panel(svg_inner, h, out_pdf, border='#8fb0ff', W=494, VH=150):
    """svg_inner: SVG elements drawn in a 494 x 150 frame (ground near the bottom); the top is cropped to height h."""
    y0 = VH - h
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: {W}pt {h}pt; margin: 0 }} html,body {{ margin:0; padding:0; background: transparent }}
svg {{ display:block }}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{h}pt" viewBox="0 {y0} {W} {h}">
<defs><clipPath id="pc"><rect x="0" y="{y0}" width="{W}" height="{h}" rx="10"/></clipPath></defs>
<g clip-path="url(#pc)">{svg_inner}</g>
<rect x="0.75" y="{y0 + 0.75}" width="{W - 1.5}" height="{h - 1.5}" rx="9.5" fill="none" stroke="{border}" stroke-width="1.5"/>
</svg></body></html>'''
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, 'p.html'); open(f, 'w').write(html)
        subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={out_pdf}', f'file://{f}'], check=True, capture_output=True, timeout=120)
    d = pymupdf.open(out_pdf)
    if len(d) != 1: raise RuntimeError(f'panel has {len(d)} pages')

def compose(bg_pdf, fg_pdf, panel_pdf, out_pdf, lay=None):
    lay = lay or plan(fg_pdf)
    bg, fg, pn = pymupdf.open(bg_pdf), pymupdf.open(fg_pdf), pymupdf.open(panel_pdf)
    W, H = fg[0].rect.width, fg[0].rect.height
    doc = pymupdf.open(); page = doc.new_page(width=W, height=H)
    page.show_pdf_page(page.rect, bg, 0)
    page.show_pdf_page(pymupdf.Rect(51, PANEL_TOP, 545, PANEL_TOP + lay['h']), pn, 0, keep_proportion=False)
    page.show_pdf_page(pymupdf.Rect(0, 0, W, 100), fg, 0, clip=pymupdf.Rect(0, 0, W, 100))
    s = lay['s']
    for (a, b), y in lay['place']:
        clip = pymupdf.Rect(0, a - 1.5, W, b + 1.5)
        x0 = 51 - 51 * s
        tgt = pymupdf.Rect(x0, y - 1.5 * s, x0 + W * s, y + (b - a + 3) * s - 1.5 * s)
        page.show_pdf_page(tgt, fg, 0, clip=clip)
    a0, a1 = lay['author_clip']; sh = lay['author_shift']
    a1 = min(a1, H - sh)
    page.show_pdf_page(pymupdf.Rect(0, a0 + sh, W, a1 + sh), fg, 0, clip=pymupdf.Rect(0, a0, W, a1))
    doc.save(out_pdf, garbage=3, deflate=True)
    return lay
