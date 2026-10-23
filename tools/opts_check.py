"""Check a Learn-with-Anil options file for an answer-only APPSC paper.

Usage: python3 tools/opts_check.py <english source .txt> [<options .json>]
The options file defaults to <dir of source>/opts/<name>.json and looks like
  {"1": {"d": ["wrong 1", "wrong 2", "wrong 3"], "dt": ["తప్పు 1", "తప్పు 2", "తప్పు 3"]}, ...}
"d" = three wrong options in English, "dt" = the same three in Telugu (same order).
The correct option is never in the file: it is APPSC's official answer ('= ' line of the source and of te/<name>.txt).
"""
import json, os, re, sys

BANNED = re.compile(r'\b(all|none|both|neither) of (the )?(above|these)\b', re.I)


def norm(s):
    return re.sub(r'[\s\.‌‍]+', ' ', s).strip().lower()


def answers(path):
    out = {}
    if not os.path.exists(path): return out
    text = open(path, encoding='utf-8').read()
    for b in re.split(r'\n(?=Q \d+)', '\n' + text):
        b = b.strip('\n')
        m = re.match(r'Q (\d+)', b)
        if not m: continue
        for ln in b.split('\n'):
            if ln.startswith('= '): out[int(m.group(1))] = ln[2:].strip()
    return out


def check(src, optf=None):
    d, f = os.path.split(src)
    optf = optf or os.path.join(d, 'opts', f.replace('.txt', '.json'))
    en, te = answers(src), answers(os.path.join(d, 'te', f))
    errs = []
    try:
        opts = json.load(open(optf, encoding='utf-8'))
    except Exception as e:
        return [f'cannot read {optf}: {e}'], 0
    for n in en:
        o = opts.get(str(n))
        if not o: errs.append(f'Q{n}: missing'); continue
        dd, dt = o.get('d') or [], o.get('dt') or []
        if len(dd) != 3: errs.append(f'Q{n}: {len(dd)} English wrong options (need 3)')
        if len(dt) != 3: errs.append(f'Q{n}: {len(dt)} Telugu wrong options (need 3)')
        alle = [norm(en[n])] + [norm(x) for x in dd]
        if len(set(alle)) != len(alle): errs.append(f'Q{n}: English options repeat or a wrong option equals the answer')
        if n in te:
            allt = [norm(te[n])] + [norm(x) for x in dt]
            if len(set(allt)) != len(allt): errs.append(f'Q{n}: Telugu options repeat or a wrong option equals the answer')
        for x in dd + dt:
            if not str(x).strip(): errs.append(f'Q{n}: empty option')
            elif BANNED.search(x) and not BANNED.search(en[n]): errs.append(f'Q{n}: avoid "all/none of the above" style options: {x[:50]}')
        for x in dt:
            if re.search(r'[A-Za-z]{4,}', x) and not re.search(r'[ఀ-౿]', x) and re.search(r'[ఀ-౿]', te.get(n, 'అ')):
                errs.append(f'Q{n}: Telugu option looks untranslated: {x[:50]}')
        # code-style answers (a-III, b-I ...) and statement sets (I, II and IV only): wrong options in the same style
        if re.fullmatch(r'(?:[a-dA-D]\s*[-–]\s*[IVX]+[,\s]*)+', en[n].strip()):
            for x in dd:
                if not re.fullmatch(r'(?:[a-dA-D]\s*[-–]\s*[IVX]+[,\s]*)+', x.strip()): errs.append(f'Q{n}: answer is a code ("{en[n]}") but option "{x}" is not')
    for k in opts:
        if not k.isdigit() or int(k) not in en: errs.append(f'Q{k}: in the options file but not in the paper')
    return errs, len(en)


if __name__ == '__main__':
    errs, n = check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    for e in errs: print('!', e)
    print(f'{n} questions, {len(errs)} problems')
    sys.exit(1 if errs else 0)
