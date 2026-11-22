"""Put the new covers into the books (and free samples); CST also gets green inside pages."""
import sys, os, pymupdf; sys.path.insert(0, '/home/claude/covers/tools')
from split import split
from layout import plan
from compose import render_panel, compose
from scenes import SCENES
from recolor import recolor
P, PAID, REPO = '/home/claude/covers/parts', '/home/claude/lwa-books/paid', '/home/claude/learnwithanil'
GREEN = {'cst-en'}
SAMPLES = {
    'aphist-en': 'LearnWithAnil-AP-History-APPSC-Group-1-Group-2-Free-Sample.pdf',
    'cst-en': 'LearnWithAnil-Computer-Skill-Test-OPSC-ASO-Free-Sample.pdf',
    'eohp-en': 'LearnWithAnil-EO-Grade-3-Hindu-Philosophy-Temple-System-Free-Sample.pdf',
    'eohp-te': 'LearnWithAnil-EO-Grade-3-Hindu-Philosophy-Temple-System-Telugu-Free-Sample.pdf',
    'epfoca-en': 'LearnWithAnil-EPFO-Current-Affairs-2026-UPSC-APFC-Free-Sample.pdf',
    'kaeco-en': 'LearnWithAnil-Karnataka-Economy-KEA-FDA-SDA-Free-Sample.pdf',
    'kahis-en': 'LearnWithAnil-Karnataka-History-Culture-Geography-KEA-FDA-SDA-Free-Sample.pdf',
}


def new_cover(src_pdf, b, tag):
    split(src_pdf, f'{P}/{tag}-bg.pdf', f'{P}/{tag}-fg.pdf')
    lay = plan(f'{P}/{tag}-fg.pdf')
    render_panel(SCENES[b](), lay['h'], f'{P}/{tag}-panel.pdf', border='#7bd389' if b in GREEN else '#8fb0ff')
    bg = f'{P}/aee2-en-bg.pdf' if b in GREEN else f'{P}/{tag}-bg.pdf'
    compose(bg, f'{P}/{tag}-fg.pdf', f'{P}/{tag}-panel.pdf', f'{P}/{tag}-cover.pdf', lay)
    return f'{P}/{tag}-cover.pdf'


def swap(src_pdf, cover_pdf, out_pdf, green):
    d = pymupdf.open(src_pdf); meta = d.metadata
    d.insert_pdf(pymupdf.open(cover_pdf), from_page=0, to_page=0, start_at=0)
    d.delete_page(1)
    if green: recolor(d, first=1)
    d.set_metadata(meta)
    d.save(out_pdf, garbage=3, deflate=True)


if __name__ == '__main__':
    os.makedirs(f'{P}/samples', exist_ok=True)
    split(f'{PAID}/orig-aee2-en.pdf', f'{P}/aee2-en-bg.pdf', f'{P}/aee2-en-fg.pdf')
    for b in (sys.argv[1:] or list(SCENES)):
        cov = new_cover(f'{PAID}/orig-{b}.pdf', b, b)
        swap(f'{PAID}/orig-{b}.pdf', cov, f'{PAID}/{b}.pdf', b in GREEN)
        print(b, os.path.getsize(f'{PAID}/orig-{b}.pdf'), '->', os.path.getsize(f'{PAID}/{b}.pdf'))
        if b in SAMPLES:
            s = f'{REPO}/src/static/{SAMPLES[b]}'
            cov = new_cover(s, b, b + '-sample')
            swap(s, cov, f'{P}/samples/{SAMPLES[b]}', b in GREEN)
            print('   sample', os.path.getsize(s), '->', os.path.getsize(f'{P}/samples/{SAMPLES[b]}'))
