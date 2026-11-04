"""Email code registration on the website (Anil, 4 Nov 2026: "OTP login for first timers"), against a fake payments script.
A first registration with phone + email asks for the 6-digit code emailed to the student; the right code logs in like Google.
When the script cannot send codes (older script, or no emails left today) the student is registered without a code, as before.
Needs a PAY_TEST build:  PAY_TEST=1 python3 tools/build.py && python3 test/otp_ui_test.py"""
import asyncio, json, os, sys, threading, http.server, functools
from playwright.async_api import async_playwright
SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist', 'site')
PORT = 8793
CODE = '246810'
errors = []
def check(c, m): print(('ok   ' if c else 'FAIL ') + m); (None if c else errors.append(m))

async def run(br, base, mode):
    st = dict(calls=[], phone='')
    async def api(route):
        b = json.loads(route.request.post_data or '{}'); a = b['action']; st['calls'].append((a, b))
        acc = dict(email=b.get('email', 'x@y.in').strip().lower(), name=b.get('name', ''), phone=st['phone'], district='')
        if a == 'otpsend':
            r = dict(ok=False, error='Unknown action.') if mode == 'old' else dict(ok=False, skip=True, error='no emails') if mode == 'skip' else dict(ok=True, mins=10, gap=45)
        elif a == 'otpverify':
            r = dict(ok=True, session='b' * 64, account=acc, loggedOut=0) if b.get('code') == CODE else dict(ok=False, error='That code is not right.')
        elif a == 'setphone': st['phone'] = b['phone']; r = dict(ok=True, account=dict(email='ravi@gmail.com', name=b['name'], phone=b['phone'], district=b['district']), passes={})
        elif a == 'passes': r = dict(ok=True, passes={})
        elif a == 'me': r = dict(ok=True, account=dict(email='ravi@gmail.com', name='Ravi Kumar', phone=st['phone'], district='Guntur'), passes={}, devices=[dict(id='x1', name='Android phone · Chrome', since='2026-11-04', seen='', current=True)], payments=[])
        else: r = dict(ok=True)
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
    ctx = await br.new_context(viewport=dict(width=420, height=900))
    pg = await ctx.new_page(); perr = []; pg.on('pageerror', lambda e: perr.append(str(e)))
    await pg.route('https://pay.test/**', api); await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
    await pg.route('https://accounts.google.com/**', lambda r: r.fulfill(status=200, body=''))
    await pg.goto(base + '/ts-police-si/account/'); await pg.wait_for_timeout(900)
    await pg.click('a[href="#join"]'); await pg.wait_for_timeout(500)
    async def fill(email):
        await pg.fill('#joinForm input[name=name]', 'Ravi Kumar'); await pg.fill('#joinForm input[name=phone]', '9959346357')
        await pg.fill('#joinForm input[name=email]', email); await pg.fill('#joinForm input[name=district]', 'Guntur')
        if not await pg.is_checked('#joinForm input[name=ok]'): await pg.check('#joinForm input[name=ok]')
        await pg.click('#joinForm button[type=submit]'); await pg.wait_for_timeout(900)
    stv = lambda: pg.evaluate("JSON.parse(localStorage.getItem('lwa-appsc-g2-student-v1')||'{}')")
    if mode == 'otp':
        check('6-digit code' in (await pg.text_content('#joinForm')), 'the form says a code will be emailed')
        await fill('ravi@gmial.com')
        check(await pg.locator('#otpForm').count() == 1, 'after the form: the "enter the code" step')
        check('ravi@gmial.com' in (await pg.text_content('#otpForm')), 'the step shows the email the code went to')
        check(any(a == 'otpsend' and b.get('email') == 'ravi@gmial.com' for a, b in st['calls']), 'the code was asked for that email')
        check(not (await stv()).get('name'), 'not registered before the code is entered')
        await pg.click('[data-act=otpback]'); await pg.wait_for_timeout(400)
        check(await pg.input_value('#joinForm input[name=name]') == 'Ravi Kumar' and await pg.input_value('#joinForm input[name=email]') == 'ravi@gmial.com', '"Change email" keeps the typed details')
        await fill('ravi@gmail.com')
        await pg.fill('#otpForm input[name=code]', '111111'); await pg.click('#otpForm button[type=submit]'); await pg.wait_for_timeout(700)
        check(await pg.is_visible('#otpErr') and 'not right' in (await pg.text_content('#otpErr')), 'a wrong code shows an error')
        await pg.click('[data-act=otpresend]'); await pg.wait_for_timeout(400)
        check('wait' in (await pg.text_content('#otpErr')), '"Send a new code" asks to wait 45 seconds first')
        await pg.fill('#otpForm input[name=code]', CODE[:3] + ' ' + CODE[3:]); await pg.click('#otpForm button[type=submit]'); await pg.wait_for_timeout(1500)
        s = await stv()
        check(s.get('session') == 'b' * 64 and s.get('lm') == 'email' and s.get('phone') == '9959346357' and s.get('email') == 'ravi@gmail.com', 'the right code logs in: session, phone and email saved')
        check(any(a == 'setphone' and b.get('session') == 'b' * 64 and b.get('phone') == '9959346357' for a, b in st['calls']), 'the phone number is linked to the new account')
        check('Ravi' in (await pg.text_content('#navAcct')), 'top bar shows the student')
        await pg.goto(base + '/ts-police-si/account/'); await pg.wait_for_timeout(1100)
        check(await pg.is_visible('text=Logged in with your email'), 'My Account says logged in with email')
        check(await pg.locator('.devs li').count() == 1, 'My Account lists the device')
    else:
        await fill('ravi@gmail.com')
        s = await stv()
        check(await pg.locator('#otpForm').count() == 0 and s.get('name') == 'Ravi Kumar' and not s.get('session'),
              ('older payments script' if mode == 'old' else 'no emails left today') + ': registered without a code, as before')
    check(not perr, mode + ': no page errors: ' + '; '.join(perr[:3]))
    await ctx.close()

async def main():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        for mode in ('otp', 'old', 'skip'): await run(br, f'http://127.0.0.1:{PORT}', mode)
        await br.close()
    srv.shutdown()
    print('ERRORS:', errors or 'none'); sys.exit(1 if errors else 0)
asyncio.run(main())
