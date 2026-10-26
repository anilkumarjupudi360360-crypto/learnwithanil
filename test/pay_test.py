"""Payment and mock flows against a fake payments script (run after: PAY_TEST=1 python3 tools/build.py)."""
import asyncio, json, os, sys, threading, http.server, functools
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'dist', 'site')
REG = """try{localStorage.setItem('lwa-appsc-g2-student-v1', JSON.stringify({name:'Test Student', phone:'9876543210', email:'t@example.com', district:'Hyderabad', pending:[]}));}catch(e){}"""
MOCK = [dict(id=f'mk-si-1-{n}', p='mk-si-1', n=n, s=('ari' if n <= 2 else 'rea' if n <= 4 else 'geo'), t='Numbers & Simplification' if n <= 2 else 'Series & Analogies' if n <= 4 else 'Indian Geography',
             q=f'Test question {n}?', o=['a', 'b', 'c', 'd'], a=[0], w='Because.', qt=f'పరీక్ష ప్రశ్న {n}?', ot=['అ', 'ఆ', 'ఇ', 'ఈ'], wt='ఎందుకంటే.') for n in range(1, 7)]


http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None


def seal_test_mock():   # a sealed test mock exactly as tools/mk_seal.py makes them
    import base64
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key, nonce = os.urandom(32), os.urandom(12)
    blob = nonce + AESGCM(key).encrypt(nonce, json.dumps({'id': 'mk-si-1', 'questions': MOCK}).encode(), b'mk-si-1')
    d = os.path.join(SITE, 'ts-police-si', 'mk'); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'test-mock.bin'), 'wb').write(blob)
    return base64.b64encode(key).decode(), 'test-mock.bin'


TKEY, TFILE = seal_test_mock()
PCMOCK = [dict(q, id=q['id'].replace('mk-si-1', 'mk-pc-1'), p='mk-pc-1', s=('eng' if q['n'] == 1 else q['s'])) for q in MOCK]


def seal_pc_mock():   # a sealed test Constable mock (Mock 1 is free)
    import base64
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key, nonce = os.urandom(32), os.urandom(12)
    blob = nonce + AESGCM(key).encrypt(nonce, json.dumps({'id': 'mk-pc-1', 'questions': PCMOCK}).encode(), b'mk-pc-1')
    d = os.path.join(SITE, 'ts-police-constable', 'mk'); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'test-pc-mock.bin'), 'wb').write(blob)
    return base64.b64encode(key).decode(), 'test-pc-mock.bin'


PKEY, PFILE = seal_pc_mock()


async def main():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_port}/'
    # fake payments script: the ₹45 PYQ Pass covers every exam ('all') and, since 26 Oct 2026, every mock series too
    # (the script reports mock = the PYQ Pass date); a 'buy' of any kind is the PYQ Pass
    state = {'mock': False, 'pyq': False, 'trial': 'expired', 'calls': [], 'kind': ''}
    def passes():
        p = {}
        if state['mock']: p['mock'] = '2026-11-30'
        if state['trial'] == 'start': state['trial'] = 'active'
        if state['trial'] == 'active': p['trial'] = p['pyq'] = '2099-01-03'
        if state['pyq']: p['pyq'] = '2099-12-31'; p['paid'] = True; p['mock'] = max(p.get('mock', ''), '2099-12-31')
        return p
    async def api(route):
        b = json.loads(route.request.post_data or '{}'); state['calls'].append(b['action'])
        if b['action'] == 'passes': r = dict(ok=True, passes=passes())
        elif b['action'] == 'buy':
            state['kind'] = b.get('kind')
            if state.get('slowbuy'): await asyncio.sleep(0.8); r = dict(ok=True, url=url + 'robots.txt')   # stays away, like a slow Instamojo
            else: r = dict(ok=True, url=url + 'ts-police-si/?payment_id=MOJO1&payment_status=Credit&payment_request_id=REQ1')
        elif b['action'] == 'verify':
            if state.get('verifyfail'): r = dict(ok=False, error='The payment is not complete yet.')
            else: state['pyq'] = True; r = dict(ok=True, passes=passes())
        elif b['action'] == 'mock' and b['id'] == 'mk-pc-1': r = dict(ok=True, id=b['id'], key=PKEY, file=PFILE, free=True)   # free for registered students
        elif b['action'] == 'mock': r = dict(ok=True, id=b['id'], key=TKEY, file=TFILE) if (state['mock'] or state['pyq']) else dict(ok=False, need='pyq', error='needs pass')
        else: r = dict(ok=False)
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
    errors = []
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        # A. no free trial (Anil, 23 Oct 2026): a new visitor registers and gets the checkout, not the test,
        #    even if the server still answered with an old free-trial date, and even with one cached on the phone
        pg = await b.new_page()
        pg.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        await pg.add_init_script('try{localStorage.setItem("lwa-passes-v1", JSON.stringify({all:{pyq:"2099-01-03", trial:"2099-01-03", paid:false}}))}catch(e){}')
        await pg.route('https://pay.test/**', api)
        await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        state['trial'] = 'start'
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(900)
        if not await pg.locator('#joinForm').count(): errors.append('no registration form for a new visitor')
        else:
            for k, v in (('name', 'New Student'), ('phone', '9123456780'), ('email', 'n@example.com'), ('district', 'Warangal')): await pg.fill(f'#joinForm [name="{k}"]', v)
            await pg.check('#joinForm [name="ok"]'); await pg.click('#joinForm [type="submit"]'); await pg.wait_for_timeout(1500)
            if (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append(f'PYQ test opened without payment (calls {state["calls"]})')
            elif not await pg.locator('#payDlg[open]').count(): errors.append('no PYQ Pass checkout after registering')
            elif 'days free' in (await pg.inner_text('body')) or 'free trial' in (await pg.inner_text('body')).lower(): errors.append('the page still mentions a free trial')
        await pg.close()
        # B. a registered student without a pass
        state.update(trial='expired', calls=[])
        pg = await b.new_page()
        pg.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        await pg.add_init_script(REG)
        await pg.route('https://pay.test/**', api)
        await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        # 1. a PYQ test without a pass opens the PYQ Pass checkout, which says it covers every exam
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(800)
        txt = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if not txt: errors.append('no checkout when attempting a PYQ test without a pass')
        elif 'whole website' not in txt or '12 months' not in txt or 'all exams' not in txt: errors.append(f'PYQ Pass checkout does not say it covers every exam: {txt[:200]!r}')
        # 1b. the question bank hides answers
        await pg.goto(url + 'ts-police-si/bank/'); await pg.wait_for_timeout(800)
        if await pg.locator('details.ans').count() or not await pg.locator('[data-act="openpay"],[data-act="unlockpyq"]').count(): errors.append('question bank shows answers without a pass')
        # 1c. no plan: the study tools and the quiz builder are locked, with a way to buy
        for view in ('mistakes', 'smart', 'heatmap', 'bookmarks', 'practice'):
            await pg.goto(url + f'ts-police-si/{view}/'); await pg.wait_for_timeout(700)
            if not await pg.locator('[data-act="openpay"]').count(): errors.append(f'{view} is open without any plan')
        # 2. a mock without a pass opens the ₹45 PYQ Pass checkout, which includes Mission Khaki (no mock-only pack any more)
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1'); await pg.wait_for_timeout(800)
        txt = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if 'Mission Khaki' not in txt or 'PYQ Pass' not in txt or '₹45' not in txt or 'Mock tests only' in txt or '₹150' in txt: errors.append(f'a mock without a pass should open the ₹45 PYQ Pass checkout listing Mission Khaki: {txt[:200]!r}')
        # 3. pay: buy -> (fake Instamojo) -> back with payment_request_id -> verify -> unlocked
        await pg.click('[data-act="paybuy"]'); await pg.wait_for_timeout(1500)
        if not state['pyq']: errors.append(f'payment not verified, calls {state["calls"]}')
        if state['kind'] != 'pyq': errors.append(f'the app asked to buy "{state["kind"]}", not the PYQ Pass')
        if 'pyq' not in await pg.evaluate('JSON.stringify(JSON.parse(localStorage.getItem("lwa-passes-v1")||"{}"))'): errors.append('pass not saved after payment')
        # 4. the mock and a sectional now open with the PYQ Pass
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1'); await pg.wait_for_timeout(1200)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/') or '6' not in await pg.inner_text('main'): errors.append('mock did not open after payment')
        if await pg.locator('[data-act="qchal"]').count(): errors.append('paid mock question offers "challenge a friend"')
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1&part=rea'); await pg.wait_for_timeout(1200)
        if 'of 2' not in await pg.inner_text('main'): errors.append('reasoning sectional should have 2 questions')
        # 4b. the same pass opens the study tools and the PYQ quiz builder
        for view in ('mistakes', 'practice'):
            await pg.goto(url + f'ts-police-si/{view}/'); await pg.wait_for_timeout(700)
            if await pg.locator('[data-act="openpay"]').count(): errors.append(f'{view} locked although the PYQ Pass was bought')
        # 5. PYQ tests open, here and on another exam
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(900)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append('PYQ test did not open with the PYQ Pass')
        await pg.goto(url + 'appsc-group-1/?sec=pol'); await pg.wait_for_timeout(1200)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append('PYQ Pass bought on TS SI does not open APPSC Group 1 PYQs')
        await pg.close()
        # C. a registered student without a pass, on a phone: what happens around Instamojo (24 Oct 2026)
        state.update(mock=False, pyq=False, trial='expired', calls=[], kind='')
        pg = await b.new_page(viewport={'width': 390, 'height': 800})
        pg.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        await pg.add_init_script(REG)
        await pg.route('https://pay.test/**', api)
        await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        # 1. three quick taps on Pay make ONE payment link, and the button says it is opening
        state['slowbuy'] = True
        await pg.goto(url + 'ts-police-si/?buy=pyq'); await pg.wait_for_timeout(800)
        await pg.evaluate('for(let i=0;i<3;i++) document.querySelector(\'[data-act="paybuy"]\').click()')
        await pg.wait_for_timeout(150)
        btn = await pg.evaluate('(b=>b&&[b.disabled,b.textContent])(document.querySelector(\'[data-act="paybuy"]\'))')
        if not btn or not btn[0] or 'Opening' not in btn[1]: errors.append(f'Pay button not locked while the payment page opens: {btn}')
        await pg.wait_for_timeout(1500)
        if state['calls'].count('buy') != 1: errors.append(f'3 quick taps made {state["calls"].count("buy")} payment links, not 1')
        state['slowbuy'] = False
        # 2. back from Instamojo with a FAILED payment: the checkout stays open with a lasting note, Try again and WhatsApp help
        state['verifyfail'] = True
        await pg.goto(url + 'ts-police-si/?payment_id=MOJO9&payment_status=Failed&payment_request_id=REQ9'); await pg.wait_for_timeout(1500)
        if not await pg.locator('#payDlg[open]').count(): errors.append('no checkout after a failed payment')
        else:
            t = await pg.inner_text('#payDlg')
            if "didn't go through" not in t: errors.append(f'failed payment note missing: {t[:160]!r}')
            if 'Try again' not in await pg.inner_text('#payDlg [data-act="paybuy"]'): errors.append('no Try again button after a failed payment')
            if not await pg.locator('#payDlg a[href^="https://wa.me/"]').count(): errors.append('no WhatsApp help link after a failed payment')
            if 'payment_request_id' in await pg.evaluate('location.search'): errors.append('payment details left in the address bar')
            await pg.wait_for_timeout(9000)   # a toast would be gone by now; the note must still be there
            if "didn't go through" not in await pg.inner_text('#payDlg'): errors.append('failed payment note disappeared')
            # Try again makes a new payment link
            n = state['calls'].count('buy'); state['slowbuy'] = True
            await pg.click('#payDlg [data-act="paybuy"]'); await pg.wait_for_timeout(1300)
            if state['calls'].count('buy') != n + 1: errors.append('Try again did not open the payment page')
            state['slowbuy'] = False
        # 3. back from Instamojo saying Credit, but not confirmed yet: "still confirming", not "failed"
        await pg.goto(url + 'ts-police-si/?payment_id=MOJO8&payment_status=Credit&payment_request_id=REQ8'); await pg.wait_for_timeout(1500)
        t = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if 'still confirming' not in t or "didn't go through" in t: errors.append(f'unconfirmed payment shows the wrong note: {t[:160]!r}')
        state['verifyfail'] = False
        # 4. back from Instamojo with the back button (no payment details): offered once to try again
        await pg.goto(url + 'ts-police-si/'); await pg.wait_for_timeout(700)
        await pg.evaluate('sessionStorage.setItem("lwa-pay", JSON.stringify({kind:"pyq", t: Date.now()}))')
        await pg.reload(); await pg.wait_for_timeout(1500)
        t = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if "isn't finished" not in t: errors.append(f'no "payment isn\'t finished" note after coming back without paying: {t[:160]!r}')
        await pg.reload(); await pg.wait_for_timeout(1500)
        if await pg.locator('#payDlg[open]').count(): errors.append('the "try again" checkout opens again on every page load')
        # 5. a student who did pay and comes back with the back button is not asked to pay again
        state['pyq'] = True
        await pg.evaluate('sessionStorage.setItem("lwa-pay", JSON.stringify({kind:"pyq", t: Date.now()}))')
        await pg.reload(); await pg.wait_for_timeout(1500)
        if await pg.locator('#payDlg[open]').count(): errors.append('a student who already paid was asked to pay again')
        # D. Mission Khaki – Constable (25 Oct 2026): Mock 1 is free for a registered student; Mock 2 and an old ?buy=combo link
        #    open the ₹45 PYQ Pass checkout (26 Oct 2026: no separate packs or combo)
        state.update(mock=False, pyq=False, trial='expired', calls=[], kind='')
        await pg.goto(url + 'ts-police-constable/?mock=mk-pc-1'); await pg.wait_for_timeout(1500)
        if await pg.locator('#payDlg[open]').count(): errors.append('free Constable Mock 1 asked for payment')
        body = await pg.inner_text('body')
        if 'Mock 1' not in body or 'Test question' not in body: errors.append(f'free Constable Mock 1 did not open: {body[:200]!r}')
        await pg.goto(url + 'ts-police-constable/?mock=mk-pc-1&part=eng'); await pg.wait_for_timeout(1500)
        body = await pg.inner_text('body')
        if 'English sectional' not in body: errors.append(f'Constable English sectional did not open: {body[:200]!r}')
        await pg.goto(url + 'ts-police-constable/?mock=mk-pc-2'); await pg.wait_for_timeout(1500)
        t = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if '₹45' not in t or '₹99' in t: errors.append(f'Constable Mock 2 did not ask for the ₹45 PYQ Pass: {t[:160]!r}')
        await pg.goto(url + 'ts-police-constable/?buy=combo'); await pg.wait_for_timeout(1000)
        t = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if '₹45' not in t or '₹199' in t or 'Mission Khaki' not in t: errors.append(f'old combo link should open the ₹45 PYQ Pass checkout: {t[:200]!r}')
        state['slowbuy'] = True
        await pg.click('#payDlg [data-act="paybuy"]'); await pg.wait_for_timeout(1300)
        if state['kind'] != 'pyq': errors.append(f'old combo link checkout sent kind {state["kind"]!r} (want pyq)')
        state['slowbuy'] = False
        await b.close()
    srv.shutdown()
    print('PAY TEST ERRORS:', errors or 'none')
    sys.exit(1 if errors else 0)

asyncio.run(main())
