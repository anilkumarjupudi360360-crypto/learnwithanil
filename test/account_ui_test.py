"""Student accounts on the website (Google login, phone step, My Account, link a payment, log out), against a fake payments
script and a fake Google button. Needs a PAY_TEST build:  PAY_TEST=1 python3 tools/build.py && python3 test/account_ui_test.py"""
import asyncio, json, os, sys, threading, http.server, functools
from playwright.async_api import async_playwright
SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist', 'site')
PORT = 8791
errors = []
def check(c, m): print(('ok   ' if c else 'FAIL ') + m); (None if c else errors.append(m))
GSTUB = """window.google = {accounts: {id: {initialize(o){ window.__gcb = o.callback; },
  renderButton(el){ const b = document.createElement('button'); b.className = 'gfake'; b.textContent = 'Continue with Google'; b.onclick = ()=>window.__gcb({credential:'cred-1'}); el.appendChild(b); }}}};"""
async def main():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    st = dict(phone='', claimed=False, calls=[], sessions=0)
    async def api(route):
        b = json.loads(route.request.post_data or '{}'); st['calls'].append((b['action'], bool(b.get('session'))))
        acc = dict(email='ravi@gmail.com', name='Ravi Kumar', phone=st['phone'], district='Guntur' if st['phone'] else '')
        paid = dict(pyq='2027-11-02', paid=True, mock='2027-11-02') if st['claimed'] else {}
        a = b['action']
        if a == 'glogin': st['sessions'] += 1; r = dict(ok=True, session='a' * 64, account=acc)
        elif a == 'setphone': st['phone'] = b['phone']; acc['phone'] = b['phone']; acc['district'] = b.get('district', ''); r = dict(ok=True, account=acc, passes=paid)
        elif a == 'passes': r = dict(ok=True, passes=paid)
        elif a == 'me': r = dict(ok=True, account=acc, passes=paid, devices=[dict(id='x1', name='Android phone · Chrome', since='2026-11-02', seen='2026-11-02', current=True), dict(id='x2', name='Windows computer · Chrome', since='2026-10-30', seen='', current=False)], payments=[])
        elif a == 'claim': st['claimed'] = True; r = dict(ok=True, passes=dict(pyq='2027-11-02', paid=True, mock='2027-11-02'), note='Payment linked. Your PYQ Pass is active.')
        elif a == 'logout': r = dict(ok=True)
        elif a == 'mock': r = dict(ok=False, need='pyq', error='needs pass')
        else: r = dict(ok=True)
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
    async with async_playwright() as pw:
        br = await pw.chromium.launch(); ctx = await br.new_context(viewport=dict(width=420, height=900))
        await ctx.add_init_script(GSTUB)
        pg = await ctx.new_page(); perr = []; pg.on('pageerror', lambda e: perr.append(str(e)))
        await pg.route('https://pay.test/**', api); await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        await pg.route('https://accounts.google.com/**', lambda r: r.fulfill(status=200, body=''))
        base = f'http://127.0.0.1:{PORT}'
        await pg.goto(base + '/ts-police-si/'); await pg.wait_for_timeout(800)
        check((await pg.text_content('#navAcct')).strip() == 'Login', 'top bar says Login before logging in')
        check(await pg.is_visible('#navSub'), 'Subscribe button shows without a pass')
        await pg.click('#navAcct'); await pg.wait_for_timeout(500)
        check(await pg.locator('.gfake').count() == 1, 'account page shows the Google button')
        await pg.click('.gfake'); await pg.wait_for_timeout(800)
        check(await pg.locator('#gPhoneForm').count() == 1, 'after Google: the one-time phone step')
        await pg.fill('#gPhoneForm input[name=phone]', '9959346357'); await pg.fill('#gPhoneForm input[name=district]', 'Guntur')
        await pg.click('#gPhoneForm button[type=submit]'); await pg.wait_for_timeout(1200)
        check('Ravi' in (await pg.text_content('#navAcct')), 'top bar shows the student after the phone step')
        stv = json.loads(await pg.evaluate("localStorage.getItem('lwa-appsc-g2-student-v1')"))
        check(stv.get('session') == 'a' * 64 and stv.get('phone') == '9959346357', 'session and phone saved on the device')
        await pg.goto(base + '/ts-police-si/account/'); await pg.wait_for_timeout(1200)
        check(await pg.locator('.devs li').count() == 2, 'My Account lists the devices')
        check(await pg.is_visible('text=No active pass'), 'My Account shows no active pass')
        await pg.fill('#claimForm input[name=payment]', 'MOJO6b01G05Q80872432'); await pg.click('#claimForm button[type=submit]'); await pg.wait_for_timeout(800)
        check(await pg.is_visible('text=PYQ Pass · active'), 'linking a payment ID opens the pass')
        check(not await pg.is_visible('#navSub'), 'Subscribe button hides with a pass')
        await pg.goto(base + '/appsc-group-1/'); await pg.wait_for_timeout(1000)
        check('Ravi' in (await pg.text_content('#navAcct')), 'still logged in on another exam (no second login)')
        check(any(a == 'passes' and s for a, s in st['calls']), 'pass checks send the session')
        await pg.goto(base + '/appsc-group-1/account/'); await pg.wait_for_timeout(1000)
        await pg.click('[data-act=logoutme]'); await pg.wait_for_timeout(800)
        check((await pg.text_content('#navAcct')).strip() == 'Login', 'log out of this device')
        check(not perr, 'no page errors: ' + '; '.join(perr[:3]))
        await br.close()
    srv.shutdown()
    print('ERRORS:', errors or 'none'); sys.exit(1 if errors else 0)
asyncio.run(main())
