import re, sys
txt = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
parts = re.split(r'Question Number\s*:\s*(\d+)\s*Question Id', txt)
seen = {}
for i in range(1, len(parts), 2):
    n = int(parts[i]); body = parts[i+1]
    if n in seen: continue  # first occurrence = English
    # question text: after 'Wrong Marks : 0.33' line, before 'Options'
    m = re.search(r'Wrong Marks\s*:\s*[\d.]+\s*(.*?)Options\s*:?(.*)', body, re.S)
    if not m: seen[n] = ('??', body[:200]); continue
    q, rest = m.group(1), m.group(2)
    q = re.sub(r'Note: For this question.*?candidates\.', '[DELETED-NOTE]', q, flags=re.S)
    q = re.sub(r'\n\s*\n', '\n', q).strip()
    # answer: rest up to next 'Question Number' (already split) ; drop page footers
    a = re.sub(r'\s+', ' ', rest).strip()
    seen[n] = (q, a[:300])
for n in sorted(seen):
    q, a = seen[n]
    print(f'## {n}\n{q}\n=> {a}\n')
