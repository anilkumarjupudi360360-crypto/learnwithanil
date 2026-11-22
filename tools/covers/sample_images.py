"""Watermarked sample-page images (site 'See sample pages') and the site cover image for a book."""
import pymupdf, io
from PIL import Image, ImageDraw, ImageFont

BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def page_png(pdf, pno, width):
    p = pymupdf.open(pdf)[pno]
    pix = p.get_pixmap(matrix=pymupdf.Matrix(width / p.rect.width, width / p.rect.width))
    return Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')


def cover_jpg(pdf, out, width=560):
    im = page_png(pdf, 0, width)
    im.save(out, 'JPEG', quality=86, optimize=True, progressive=True)


def sample_jpg(pdf, pno, out, wm=(118, 190, 148), bar=(11, 61, 42), width=880):
    im = page_png(pdf, pno, width).convert('RGBA')
    W, H = im.size
    layer = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(BOLD, 34)
    txt = 'SAMPLE PAGE · learnwithanil.in'
    for row in range(0, H * 2, 330):
        for col in range(-400, W * 2, 700):
            d.text((col + (row // 330 % 2) * 310, row), txt, font=f, fill=wm + (58,))
    layer = layer.rotate(30, resample=Image.BICUBIC)
    layer = layer.crop((W // 2, H // 2, W // 2 + W, H // 2 + H))
    im = Image.alpha_composite(im, layer)
    d = ImageDraw.Draw(im)
    d.rectangle((0, H - 44, W, H), fill=bar + (255,))
    fb = ImageFont.truetype(BOLD, 22)
    t = 'Preview only · full book on learnwithanil.in'
    tw = d.textlength(t, font=fb)
    d.text(((W - tw) / 2, H - 44 + 9), t, font=fb, fill=(255, 255, 255, 255))
    im.convert('RGB').save(out, 'JPEG', quality=86, optimize=True, progressive=True)
