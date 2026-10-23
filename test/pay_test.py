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


async def main():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_port}/'
    # fake payments script: the PYQ Pass covers every exam ('all'), the free trial too; Mission Khaki is separate
    state = {'mock': False, 'pyq': False, 'trial': 'expired', 'calls': [], 'kind': ''}
    def passes():
        p = {}
        if state['mock']: p['mock'] = '2026-11-30'
        if state['trial'] == 'start': state['trial'] = 'active'
        if state['trial'] == 'active': p['trial'] = p['pyq'] = '2099-01-03'
        if state['pyq']: p['pyq'] = '2099-12-31'; p['paid'] = True
        return p
    async def api(route):
        b = json.loads(route.request.post_data or '{}'); state['calls'].append(b['action'])
        if b['action'] == 'passes': r = dict(ok=True, passes=passes())
        elif b['action'] == 'buy': state['kind'] = b.get('kind'); r = dict(ok=True, url=url + 'ts-police-si/?payment_id=MOJO1&payment_status=Credit&payment_request_id=REQ1')
        elif b['action'] == 'verify':
            state['mock' if state['kind'] == 'mock' else 'pyq'] = True; r = dict(ok=True, passes=passes())
        elif b['action'] == 'mock': r = dict(ok=True, id=b['id'], key=TKEY, file=TFILE) if state['mock'] else dict(ok=False, need='mock', error='needs pass')
        else: r = dict(ok=False)
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
    errors = []
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        # A. a new visitor registers: the 3-day free trial starts and the PYQ test opens
        pg = await b.new_page()
        pg.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        await pg.route('https://pay.test/**', api)
        await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        state['trial'] = 'start'
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(900)
        if not await pg.locator('#joinForm').count(): errors.append('no registration form for a new visitor')
        else:
            for k, v in (('name', 'New Student'), ('phone', '9123456780'), ('email', 'n@example.com'), ('district', 'Warangal')): await pg.fill(f'#joinForm [name="{k}"]', v)
            await pg.check('#joinForm [name="ok"]'); await pg.click('#joinForm [type="submit"]'); await pg.wait_for_timeout(1500)
            if not (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append(f'PYQ test did not open in the free trial (calls {state["calls"]})')
        await pg.close()
        # B. a registered student whose trial is over
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
        if not await pg.locator('[data-act="unlockpyq"]').count() or await pg.locator('details.ans').count(): errors.append('question bank shows answers without a pass')
        # 2. a mock without a pass opens the mock checkout (mocks only)
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1'); await pg.wait_for_timeout(800)
        txt = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if 'Mission Khaki' not in txt or 'Mock tests only' not in txt: errors.append('no Mission Khaki (mocks only) checkout for a mock without a pass')
        # 3. pay: buy -> (fake Instamojo) -> back with payment_request_id -> verify -> unlocked
        await pg.click('[data-act="paybuy"]'); await pg.wait_for_timeout(1500)
        if not state['mock']: errors.append(f'payment not verified, calls {state["calls"]}')
        if 'mock' not in await pg.evaluate('JSON.stringify(JSON.parse(localStorage.getItem("lwa-passes-v1")||"{}"))'): errors.append('pass not saved after payment')
        # 4. the mock and a sectional now open
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1'); await pg.wait_for_timeout(1200)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/') or '6' not in await pg.inner_text('main'): errors.append('mock did not open after payment')
        if await pg.locator('[data-act="qchal"]').count(): errors.append('paid mock question offers "challenge a friend"')
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1&part=rea'); await pg.wait_for_timeout(1200)
        if 'of 2' not in await pg.inner_text('main'): errors.append('reasoning sectional should have 2 questions')
        # 5. Mission Khaki does not include the PYQ Pass
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(900)
        if (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append('PYQ test opened with only the Mission Khaki pass')
        # 6. buy the PYQ Pass on one exam: PYQs of another exam open too
        if await pg.locator('#payDlg[open]').count():
            await pg.click('[data-act="paybuy"]'); await pg.wait_for_timeout(1500)
        if not state['pyq']: errors.append(f'PYQ Pass payment not verified, calls {state["calls"]}')
        await pg.goto(url + 'appsc-group-1/?sec=pol'); await pg.wait_for_timeout(1200)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append('PYQ Pass bought on TS SI does not open APPSC Group 1 PYQs')
        await b.close()
    srv.shutdown()
    print('PAY TEST ERRORS:', errors or 'none')
    sys.exit(1 if errors else 0)

asyncio.run(main())
