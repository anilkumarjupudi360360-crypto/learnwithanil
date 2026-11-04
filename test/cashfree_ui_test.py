"""Cashfree checkout on the website (4 Nov 2026), against a fake payments script and a fake Cashfree checkout script.
Pay -> the script answers with a Cashfree payment session -> Cashfree's script opens its page -> back with ?cf_order= -> verify -> unlocked.
Also: a failed Cashfree payment, Cashfree's script not loading, and the refund / delivery / contact pages.
Needs a PAY_TEST build:  PAY_TEST=1 python3 tools/build.py && python3 test/cashfree_ui_test.py"""
import asyncio, json, os, sys, threading, http.server, functools
from playwright.async_api import async_playwright
SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist', 'site')
http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
REG = """try{localStorage.setItem('lwa-appsc-g2-student-v1', JSON.stringify({name:'Test Student', phone:'9876543210', email:'t@example.com', district:'Hyderabad', pending:[]}));}catch(e){}"""
ORDER = 'LWA261104ABC123'
# Cashfree's checkout script, faked: remembers how it was called and "comes back" to the return address with ?cf_order=
FAKE_SDK = """window.Cashfree = function(o){ return {checkout: function(c){ window.__cf = {mode: o.mode, session: c.paymentSessionId, target: c.redirectTarget};
  sessionStorage.setItem('cf-called', JSON.stringify(window.__cf)); location.href = '/ts-police-si/?cf_order=%s'; return new Promise(function(){}); }}; };""" % ORDER


async def main():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_port}/'
    state = {'pyq': False, 'calls': [], 'verify': [], 'paid': True}

    async def api(route):
        b = json.loads(route.request.post_data or '{}'); state['calls'].append(b['action'])
        passes = {'pyq': '2099-12-31', 'paid': True, 'mock': '2099-12-31'} if state['pyq'] else {}
        if b['action'] == 'passes': r = dict(ok=True, passes=passes)
        elif b['action'] == 'buy': r = dict(ok=True, gateway='cashfree', mode='sandbox', session='session_' + ORDER, order=ORDER)
        elif b['action'] == 'verify':
            state['verify'].append(b.get('request'))
            if state['paid'] and b.get('request') == ORDER:
                state['pyq'] = True; r = dict(ok=True, passes={'pyq': '2099-12-31', 'paid': True, 'mock': '2099-12-31'})
            else: r = dict(ok=False, error='The payment is not complete yet.')
        else: r = dict(ok=False, error='Unknown action.')
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))

    errors = []
    async with async_playwright() as pw:
        br = await pw.chromium.launch()

        async def page(sdk=True):
            pg = await br.new_page(viewport={'width': 390, 'height': 800})
            pg.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
            await pg.add_init_script(REG)
            await pg.route('https://pay.test/**', api)
            await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
            if sdk: await pg.route('https://sdk.cashfree.com/**', lambda r: r.fulfill(status=200, content_type='application/javascript', body=FAKE_SDK))
            else: await pg.route('https://sdk.cashfree.com/**', lambda r: r.abort())
            return pg

        # 1. pay with Cashfree: one tap -> Cashfree's checkout with the session from the script -> back -> verified -> unlocked
        pg = await page()
        await pg.goto(url + 'appsc-group-2/?test=s2024'); await pg.wait_for_timeout(900)
        if not await pg.locator('#payDlg[open]').count(): errors.append('no checkout for a PYQ test without a pass')
        else:
            dlg = await pg.inner_text('#payDlg')
            if 'Instamojo' in dlg: errors.append(f'checkout still names Instamojo: {dlg[:160]!r}')
            await pg.click('[data-act="paybuy"]'); await pg.wait_for_timeout(2500)
            cf = json.loads(await pg.evaluate('sessionStorage.getItem("cf-called")') or 'null')
            if not cf: errors.append(f'Cashfree checkout was not opened (calls {state["calls"]})')
            elif cf != {'mode': 'sandbox', 'session': 'session_' + ORDER, 'target': '_self'}: errors.append(f'Cashfree checkout called with {cf}')
            if state['verify'] != [ORDER]: errors.append(f'verify after Cashfree: {state["verify"]}')
            if not state['pyq'] or 'pyq' not in await pg.evaluate('localStorage.getItem("lwa-passes-v1")||""'): errors.append('pass not saved after the Cashfree payment')
            if 'cf_order' in await pg.evaluate('location.search'): errors.append('cf_order left in the address bar')
            if state['calls'].count('buy') != 1: errors.append(f'{state["calls"].count("buy")} orders for one tap')
        await pg.close()

        # 2. back from Cashfree without a paid order: the checkout opens again with "didn't go through" and Try again
        state.update(pyq=False, calls=[], verify=[], paid=False)
        pg = await page()
        await pg.goto(url + f'ts-police-si/?cf_order={ORDER}'); await pg.wait_for_timeout(1800)
        txt = await pg.inner_text('#payDlg') if await pg.locator('#payDlg[open]').count() else ''
        if "didn't go through" not in txt or 'Try again' not in txt: errors.append(f'failed Cashfree payment: no failure note with Try again: {txt[:200]!r}')
        if state['verify'] != [ORDER]: errors.append(f'failed Cashfree payment not checked with the script: {state["verify"]}')
        await pg.close()

        # 3. Cashfree's script does not load (bad connection, blocker): a message, the Pay button works again, nothing else happens
        state.update(pyq=False, calls=[], verify=[], paid=True)
        pg = await page(sdk=False)
        await pg.goto(url + 'appsc-group-2/?test=s2024'); await pg.wait_for_timeout(900)
        await pg.click('[data-act="paybuy"]'); await pg.wait_for_timeout(1500)
        body = await pg.inner_text('body')
        if 'Could not open the payment page' not in body: errors.append('no message when Cashfree\'s script does not load')
        if not await pg.locator('[data-act="paybuy"]:not([disabled])').count(): errors.append('Pay button stays locked after Cashfree failed to load')
        if state['verify']: errors.append('verify called although the student never left')
        await pg.close()

        # 4. the pages payment gateways check: refund, delivery, contact, linked from the footer; no "Instamojo's page" left
        pg = await br.new_page()
        for fn, need in (('refund.html', ['Refund', 'Cancellation', '7 days', 'paid twice']), ('delivery.html', ['Nothing is shipped', 'within a minute']),
                         ('contact.html', ['Email', 'WhatsApp', 'Help'])):
            r = await pg.goto(url + fn)
            t = await pg.inner_text('body') if r and r.ok else ''
            miss = [w for w in need if w not in t]
            if not t or miss: errors.append(f'{fn}: missing {miss or "page"}')
        for where in ('help.html', 'ts-police-si/', 'appsc-group-2/papers/'):   # a static page and the exam app pages
            await pg.goto(url + where); await pg.wait_for_timeout(400)
            foot = await pg.inner_text('footer') if await pg.locator('footer').count() else ''
            if not all(w in foot for w in ('Refunds', 'Delivery', 'Contact')): errors.append(f'{where}: footer does not link the new pages: {foot[-200:]!r}')
        for fn in ('privacy.html', 'terms.html'):
            await pg.goto(url + fn); t = await pg.inner_text('main') if await pg.locator('main').count() else await pg.inner_text('body')
            if 'Cashfree' not in t: errors.append(f'{fn} does not name Cashfree as a payment gateway')
        await br.close()
    srv.shutdown()
    print('\n'.join(errors) if errors else 'cashfree ui: all passed')
    sys.exit(1 if errors else 0)

asyncio.run(main())
