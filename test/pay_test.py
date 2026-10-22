"""Payment and mock flows against a fake payments script (run after: PAY_TEST=1 python3 tools/build.py)."""
import asyncio, json, os, sys, threading, http.server, functools
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'dist', 'site')
REG = """try{localStorage.setItem('lwa-appsc-g2-student-v1', JSON.stringify({name:'Test Student', phone:'9876543210', email:'t@example.com', district:'Hyderabad', pending:[]}));}catch(e){}"""
MOCK = [dict(id=f'mk-si-1-{n}', p='mk-si-1', n=n, s=('ari' if n <= 2 else 'rea' if n <= 4 else 'geo'), t='Numbers & Simplification' if n <= 2 else 'Series & Analogies' if n <= 4 else 'Indian Geography',
             q=f'Test question {n}?', o=['a', 'b', 'c', 'd'], a=[0], w='Because.', qt=f'పరీక్ష ప్రశ్న {n}?', ot=['అ', 'ఆ', 'ఇ', 'ఈ'], wt='ఎందుకంటే.') for n in range(1, 7)]


http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None


async def main():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_port}/'
    state = {'paid': False, 'calls': []}
    async def api(route):
        b = json.loads(route.request.post_data or '{}'); state['calls'].append(b['action'])
        if b['action'] == 'passes': r = dict(ok=True, passes=({'mock': '2026-11-30'} if state['paid'] else {}))
        elif b['action'] == 'buy': r = dict(ok=True, url=url + 'ts-police-si/?payment_id=MOJO1&payment_status=Credit&payment_request_id=REQ1')
        elif b['action'] == 'verify': state['paid'] = True; r = dict(ok=True, passes={'mock': '2026-11-30'})
        elif b['action'] == 'mock': r = dict(ok=True, id=b['id'], questions=MOCK) if state['paid'] else dict(ok=False, need='mock', error='needs pass')
        else: r = dict(ok=False)
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
    errors = []
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page()
        pg.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        await pg.add_init_script(REG)
        await pg.route('https://pay.test/**', api)
        await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        # 1. a PYQ test without a pass opens the checkout instead
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(800)
        if not await pg.evaluate('!!document.querySelector("#payDlg[open]")'): errors.append('no checkout when attempting a PYQ test without a pass')
        # 2. a mock without a pass opens the mock checkout
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1'); await pg.wait_for_timeout(800)
        if 'Mission Khaki' not in (await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''): errors.append('no Mission Khaki checkout for a mock without a pass')
        # 3. pay: buy -> (fake Instamojo) -> back with payment_request_id -> verify -> unlocked
        await pg.click('[data-act="paybuy"]'); await pg.wait_for_timeout(1500)
        if not state['paid']: errors.append(f'payment not verified, calls {state["calls"]}')
        if 'mock' not in await pg.evaluate('JSON.stringify(JSON.parse(localStorage.getItem("lwa-passes-v1")||"{}"))'): errors.append('pass not saved after payment')
        # 4. the mock and a sectional now open
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1'); await pg.wait_for_timeout(1200)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/') or '6' not in await pg.inner_text('main'): errors.append('mock did not open after payment')
        if await pg.locator('[data-act="qchal"]').count(): errors.append('paid mock question offers "challenge a friend"')
        await pg.goto(url + 'ts-police-si/?mock=mk-si-1&part=rea'); await pg.wait_for_timeout(1200)
        if 'of 2' not in await pg.inner_text('main'): errors.append('reasoning sectional should have 2 questions')
        # 5. with the mock pass, PYQ tests open too
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(900)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append('PYQ test blocked although the mock pass includes the PYQ Pass')
        await b.close()
    srv.shutdown()
    print('PAY TEST ERRORS:', errors or 'none')
    sys.exit(1 if errors else 0)

asyncio.run(main())
