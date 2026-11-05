#!/usr/bin/env python3
"""Tell Bing, Yandex and the other IndexNow engines (ChatGPT search reads Bing) which pages changed.
Run by .github/workflows/indexnow.yml (GitHub's servers can reach api.indexnow.org; the Claude cloud shell cannot).

    python3 tools/indexnow.py --diff <before-sha> <after-sha>   pages added or changed in docs/ by a push
    python3 tools/indexnow.py /page.html /exam/ ...              these addresses
    python3 tools/indexnow.py --main                             every page except the one-question pages (/q/)

Added pages are always sent; changed one-question pages (/q/) are skipped (a rebuild touches thousands of them);
noindex pages are skipped. Key file: docs/<KEY>.txt (src/static).
"""
import json, os, subprocess, sys, time, urllib.request

HOST = 'learnwithanil.in'
KEY = '34b90a20c060310aec19b8d5c5e5bc0e'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')


def url_of(rel):   # docs-relative file -> public address
    rel = rel.replace(os.sep, '/')
    if rel.endswith('index.html'): rel = rel[:-len('index.html')]
    return f'https://{HOST}/{rel}'


def wanted(rel, added):
    if not rel.endswith('.html') or rel in ('404.html',) or rel.startswith('google') or rel.startswith('books/'): return False
    if '/q/' in '/' + rel and not added: return False
    try: head = open(os.path.join(DOCS, rel), encoding='utf-8', errors='ignore').read(6000)
    except OSError: return False
    return 'noindex' not in head


def changed(a, b):
    out = subprocess.run(['git', 'diff', '--name-status', '--no-renames', a, b, '--', 'docs'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    urls = []
    for line in out.splitlines():
        st, path = line.split('\t', 1)
        if st == 'D': continue
        rel = path[len('docs/'):]
        if wanted(rel, st == 'A'): urls.append(url_of(rel))
    return urls


def every_main():
    urls = []
    for d, _, fs in os.walk(DOCS):
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), DOCS)
            if wanted(rel, False): urls.append(url_of(rel))
    return sorted(urls)


def submit(urls):
    urls = list(dict.fromkeys(urls))
    print(f'{len(urls)} URLs')
    for i in range(0, len(urls), 10000):
        part = urls[i:i + 10000]
        body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': part}).encode()
        req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as r: print('IndexNow', r.status, f'({len(part)} URLs)'); break
            except urllib.error.HTTPError as e:
                print('IndexNow HTTP', e.code, e.read()[:300]);
                if e.code in (400, 403, 422): sys.exit(1)
            except Exception as e: print('IndexNow error', e)
            time.sleep(20)
    for u in urls[:40]: print(' ', u)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--diff']: urls = changed(a[1], a[2])
    elif a[:1] == ['--main']: urls = every_main()
    else: urls = [u if u.startswith('http') else f'https://{HOST}/{u.lstrip("/")}' for u in ' '.join(a).split()]
    if urls: submit(urls)
    else: print('nothing to submit')
