"""Print a paper's questions with APPSC's answer and our three wrong options (English + Telugu), for review.
Usage: python3 tools/opts_review.py <english source .txt> [<options .json>] > review.txt"""
import json, os, re, sys
src = sys.argv[1]; d, f = os.path.split(src)
optf = sys.argv[2] if len(sys.argv) > 2 else os.path.join(d, 'opts', f.replace('.txt', '.json'))
opts = json.load(open(optf, encoding='utf-8'))
def blocks(path, head):
    out = {}
    if not os.path.exists(path): return out
    for b in re.split(r'\n(?=Q \d+)', '\n' + open(path, encoding='utf-8').read()):
        b = b.strip('\n'); m = re.match(r'Q (\d+)', b)
        if not m: continue
        lines = b.split('\n')[1:]
        out[int(m.group(1))] = (head(b.split('\n')[0]), '\n'.join(l for l in lines if l.strip() and not l.startswith(('= ', '~ ', '! '))),
                                next((l[2:] for l in lines if l.startswith('= ')), ''))
    return out
en = blocks(src, lambda h: h); te = blocks(os.path.join(d, 'te', f), lambda h: h)
for n in sorted(en):
    h, q, a = en[n]; o = opts.get(str(n), {})
    print(f'=== {h}\n{q}\n  ANSWER (APPSC): {a}')
    for i, x in enumerate(o.get('d', []), 1): print(f'  wrong {i}: {x}')
    if n in te:
        print(f'  TE ANSWER: {te[n][2]}')
        for i, x in enumerate(o.get('dt', []), 1): print(f'  TE wrong {i}: {x}')
    print()
