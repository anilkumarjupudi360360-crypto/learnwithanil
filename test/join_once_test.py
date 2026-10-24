"""Registration sends one row per real change (run after: PAY_TEST=1 python3 tools/build.py).

Students on slow connections tap "Register and start" / "Save details" again and again while the
site checks their pass. Each tap used to send another row ("Updated details") to the sheet.
"""
import asyncio, json, os, sys, threading, http.server, functools
from urllib.parse import parse_qs
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'dist', 'site')
TEST_FIELD = 'entry.1498681403'
http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None


async def main():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_port}/'
    rows, errors = [], []

    async def slow_api(route):   # the payments script answers slowly, like on a weak mobile signal
        await asyncio.sleep(2.5)
        await route.fulfill(status=200, content_type='application/json', body=json.dumps({'ok': True, 'passes': {}}))

    async def form(route):
        rows.append(parse_qs(route.request.post_data or '').get(TEST_FIELD, [''])[0])
        await route.fulfill(status=200, body='ok')

    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context(viewport={'width': 390, 'height': 844})).new_page()
        pg.on('pageerror', lambda e: errors.append(f'page error: {e}'))
        await pg.route('https://pay.test/**', slow_api)
        await pg.route('**/formResponse', form)

        # 1. New student taps "Register and start" six times while the site is saving
        await pg.goto(url + 'ts-police-si/?test=s2022'); await pg.wait_for_timeout(900)
        for k, v in (('name', 'New Student'), ('phone', '9123456780'), ('email', 'n@example.com'), ('district', 'Warangal')):
            await pg.fill(f'#joinForm [name="{k}"]', v)
        await pg.check('#joinForm [name="ok"]')
        btn = pg.locator('#joinForm [type="submit"]')
        await btn.click()
        await pg.wait_for_timeout(100)
        label = await btn.text_content() if await btn.count() else ''
        disabled = await btn.is_disabled() if await btn.count() else None
        for _ in range(5):   # extra taps (dispatching submit directly also covers the Enter key)
            await pg.evaluate("()=>{ const f=document.getElementById('joinForm'); if(f) f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true})); }")
            await pg.wait_for_timeout(80)
        await pg.wait_for_timeout(3500)
        print('after six taps:', rows, '| button while saving:', repr(label), 'disabled' if disabled else 'enabled')
        if rows != ['Registered · before TSLPRB SI Preliminary Written Test 2022'] and not (len(rows) == 1 and rows[0].startswith('Registered')):
            errors.append(f'registration should send exactly one "Registered" row, sent {rows}')
        if disabled is not True: errors.append('the button should be disabled while saving')

        # 2. Same student opens "Your details" and saves without changing anything
        n = len(rows)
        await pg.goto(url + 'ts-police-si/#join'); await pg.wait_for_timeout(900)
        if await pg.locator('#joinForm').count():
            await pg.click('#joinForm [type="submit"]'); await pg.wait_for_timeout(3500)
            if len(rows) != n: errors.append(f'saving unchanged details sent rows: {rows[n:]}')
        else:
            errors.append('no details form at #join')

        # 3. Changes the district: one "Updated details" row
        n = len(rows)
        await pg.goto(url + 'ts-police-si/#join'); await pg.wait_for_timeout(900)
        await pg.fill('#joinForm [name="district"]', 'Hanamkonda')
        await pg.click('#joinForm [type="submit"]'); await pg.wait_for_timeout(200)
        await pg.evaluate("()=>{ const f=document.getElementById('joinForm'); if(f) f.requestSubmit(); }")
        await pg.wait_for_timeout(3500)
        if rows[n:] != ['Updated details']: errors.append(f'changing the district should send one "Updated details" row, sent {rows[n:]}')

        # 4. Writes a help message: one row; saving the same message again: none
        n = len(rows)
        await pg.goto(url + 'ts-police-si/#join'); await pg.wait_for_timeout(900)
        await pg.fill('#joinForm [name="help"]', 'Need help with reasoning')
        await pg.click('#joinForm [type="submit"]'); await pg.wait_for_timeout(3500)
        await pg.goto(url + 'ts-police-si/#join'); await pg.wait_for_timeout(900)
        await pg.fill('#joinForm [name="help"]', 'Need help with reasoning')
        await pg.click('#joinForm [type="submit"]'); await pg.wait_for_timeout(3500)
        if rows[n:] != ['Updated details']: errors.append(f'a help message should send one row, sent {rows[n:]}')
        await b.close()
    srv.shutdown()
    print('rows sent in total:', rows)
    print('ERRORS:', 'none' if not errors else '')
    for e in errors: print(' -', e)
    sys.exit(1 if errors else 0)


asyncio.run(main())
