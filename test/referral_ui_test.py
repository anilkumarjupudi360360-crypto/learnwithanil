"""Invite friends, earn free days, on the website (against a fake payments script). Needs a PAY_TEST build:
   PAY_TEST=1 python3 tools/build.py && python3 test/referral_ui_test.py"""
import asyncio, json, os, sys, threading, http.server, functools
from playwright.async_api import async_playwright
SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist', 'site')
http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
errors = []
def check(c, m): print(('ok   ' if c else 'FAIL ') + m); (None if c else errors.append(m))
OPEN = "window.__opened=[];window.open=function(u){window.__opened.push(String(u));return null;};"


async def main():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_port}'
    st = dict(calls=[], bonus='', joins=[])

    async def api(route):
        b = json.loads(route.request.post_data or '{}'); a = b['action']; st['calls'].append(a)
        if a == 'passes': r = dict(ok=True, passes=dict(bonus=st['bonus'], mock=st['bonus']) if st['bonus'] else {})
        elif a == 'refjoin': st['joins'].append(b); r = dict(ok=True, status='ok')
        elif a == 'ref': r = dict(ok=True, code='QWERTY', joined=2, bought=1, days=36, left=8)
        elif a == 'mock' and b['id'].startswith('bk-ex-'): r = dict(ok=False, need='pyq', error='needs pass')
        elif a == 'mock': r = dict(ok=False, need='pyq', error='needs pass')
        else: r = dict(ok=False)
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))

    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        # 1. a friend arrives through an invite link on a static question page, then opens the exam and registers
        ctx = await br.new_context(viewport=dict(width=400, height=860)); await ctx.add_init_script(OPEN)
        pg = await ctx.new_page(); perr = []; pg.on('pageerror', lambda e: perr.append(str(e)))
        await pg.route('https://pay.test/**', api); await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        qdir = os.path.join(SITE, 'appsc-group-2', 'q'); qf = sorted(os.listdir(qdir))[0]
        await pg.goto(f'{base}/appsc-group-2/q/{qf}?ref=abcdef'); await pg.wait_for_timeout(400)
        rf = json.loads(await pg.evaluate("localStorage.getItem('lwa-ref-from')") or 'null')
        check(rf and rf.get('c') == 'ABCDEF', 'a static question page keeps the friend\'s invite code')
        await pg.goto(f'{base}/ts-police-si/?ref=ZZZZZZ'); await pg.wait_for_timeout(700)
        rf = json.loads(await pg.evaluate("localStorage.getItem('lwa-ref-from')") or 'null')
        check(rf.get('c') == 'ABCDEF', 'the first friend\'s link counts (a second link does not replace it)')
        await pg.goto(f'{base}/ts-police-si/#join'); await pg.wait_for_timeout(900)
        for k, v in (('name', 'New Friend'), ('phone', '9123456780'), ('email', 'nf@example.com'), ('district', 'Warangal')):
            await pg.fill(f'#joinForm [name="{k}"]', v)
        await pg.check('#joinForm [name="ok"]'); await pg.click('#joinForm [type="submit"]'); await pg.wait_for_timeout(2500)
        check(len(st['joins']) == 1 and st['joins'][0]['code'] == 'ABCDEF' and st['joins'][0]['phone'] == '9123456780', 'registering sends the invite once: ' + json.dumps(st['joins']))
        check('ref' in st['calls'] and st['calls'].index('ref') > st['calls'].index('refjoin'), 'own code is asked for only after the invite was sent')
        await pg.goto(f'{base}/ts-police-si/'); await pg.wait_for_timeout(3500)
        check(len(st['joins']) == 1, 'no second refjoin on the next page')
        # 2. My Account: the invite card with the student's own link and numbers
        await pg.goto(f'{base}/ts-police-si/account/'); await pg.wait_for_timeout(1500)
        link = await pg.input_value('.reflink') if await pg.locator('.reflink').count() else ''
        check('ref=QWERTY' in link and 'utm_source=friend' in link, 'invite card shows the personal link: ' + link)
        txt = await pg.text_content('.share-card')
        check('Friends joined: 2' in txt and 'Free days earned: 36' in txt, 'invite card shows the numbers')
        await pg.click('.share-card [data-act="sitewa"]'); await pg.wait_for_timeout(300)
        op = await pg.evaluate('window.__opened')
        check(op and 'ref%3DQWERTY' in op[-1], 'WhatsApp share carries the invite code')
        # 3. free days from invites: PYQs open, PDF downloads still need the pass, Subscribe stays
        st['bonus'] = '2099-01-05'
        await pg.evaluate("localStorage.removeItem('lwa-pass-checked')")
        await pg.goto(f'{base}/ts-police-si/account/'); await pg.wait_for_timeout(1500)
        check(await pg.is_visible('text=Free days from inviting friends'), 'My Account shows the free days')
        check(await pg.is_visible('#navSub'), 'Subscribe stays visible with free days only')
        await pg.goto(f'{base}/appsc-group-2/bank/'); await pg.wait_for_timeout(1500)
        check(await pg.locator('#bankSearch').count() == 1, 'free days open the question bank (a PYQ Pass feature)')
        await pg.goto(f'{base}/appsc-group-2/papers/'); await pg.wait_for_timeout(1200)
        pdf = pg.locator('[data-act="paperpdf"]')
        if await pdf.count():
            await pdf.first.click(); await pg.wait_for_timeout(600)
            check(await pg.locator('#payDlg[open], dialog[open]').count() >= 1, 'a PDF download asks for the paid pass')
        check(not perr, 'no page errors: ' + '; '.join(perr))
        # 4. someone already registered who opens a friend's link is not counted
        ctx2 = await br.new_context(); await ctx2.add_init_script("localStorage.setItem('lwa-appsc-g2-student-v1', JSON.stringify({name:'Old', phone:'9000000009', email:'o@x.com', pending:[]}))")
        p2 = await ctx2.new_page(); await p2.route('https://pay.test/**', api)
        await p2.goto(f'{base}/appsc-group-2/?ref=BBBBBB'); await p2.wait_for_timeout(800)
        check(await p2.evaluate("localStorage.getItem('lwa-ref-from')") is None, 'an already registered device keeps no invite')
        await br.close()
    srv.shutdown()
    print('\nREFERRAL UI TEST ERRORS: ' + ('; '.join(errors) if errors else 'none'))
    sys.exit(1 if errors else 0)

asyncio.run(main())
