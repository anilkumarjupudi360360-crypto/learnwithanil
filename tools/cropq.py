import sys, glob, re, os
from PIL import Image
import pytesseract
paper, out, nums = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
crops = []
for n in nums:
    files = sorted(glob.glob(f'{paper}/pg-*.txt'), key=lambda f: int(re.findall(r'\d+', os.path.basename(f))[0]))
    f = next((f for f in files if re.search(rf'Question Number\s*:\s*{n}\s+Question', open(f, errors='ignore').read())), None)
    if not f: print('not found', n); continue
    img = Image.open(f[:-4] + '.png')
    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    y = None
    for i, t in enumerate(d['text']):
        if t == str(n) and i >= 2 and d['text'][i-1] == ':' and d['text'][i-2].startswith('Number'):
            y = d['top'][i]; break
    if y is None: y = 0
    c = img.crop((0, max(0, y - 8), img.width, min(img.height, y + 470))).convert('L')
    c = c.resize((int(c.width * 0.5), int(c.height * 0.5)))
    crops.append(c)
W = max(c.width for c in crops); H = sum(c.height for c in crops) + 6 * len(crops)
m = Image.new('L', (W, H), 255); yy = 0
for c in crops: m.paste(c, (0, yy)); yy += c.height + 6
m.save(out); print(out, m.size)
