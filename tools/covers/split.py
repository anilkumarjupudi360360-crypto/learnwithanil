"""Split a cover page (page 0 of a book PDF) into background-only and foreground-only one-page PDFs.
Background = page fill + grid patterns + the top-right glow (the first pattern fill after the grid)."""
import pymupdf, re, sys

def bg_end(s):
    i = s.find('/P9 scn'); j = s.find('Q\nQ\n', i) + 4
    m = re.compile(r'/P\d+ scn').search(s, j)
    bt = s.find('BT', j)
    if m and m.start() < bt:
        j = s.find('Q\nQ\n', m.end()) + 4
    return j

def split(src, out_bg, out_fg):
    for out, keep_bg in ((out_bg, True), (out_fg, False)):
        d = pymupdf.open(src)
        d.select([0])
        p = d[0]
        s = p.read_contents().decode('latin1')
        j = bg_end(s)
        head = s[:s.find('q\n')]          # the initial cm (Chrome's y flip)
        new = s[:j] if keep_bg else head + s[j:]
        d.update_stream(p.get_contents()[0], new.encode('latin1'))
        d.save(out, garbage=3, deflate=True)

if __name__ == '__main__':
    split(*sys.argv[1:4])
