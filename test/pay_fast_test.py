"""The payment link is made while the payment window is open (Anil, 4 Nov 2026: "there some latency ...while opening payments"),
so Pay goes straight to Instamojo. Needs a PAY_TEST build:  PAY_TEST=1 python3 tools/build.py && python3 test/pay_fast_test.py"""
import asyncio, json, os, sys, threading, http.server, functools, time
from playwright.async_api import async_playwright
SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist', 'site')
PORT = 8794
errors = []
def check(c, m): print(('ok   ' if c else 'FAIL ') + m); (None if c else errors.append(m))
REG = 'try{localStorage.setItem("lwa-appsc-g2-student-v1", JSON.stringify({name:"Test Student",phone:"9876543210",email:"t@example.com",district:"Guntur",pending:[],joined:1}))}catch(e){}'
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

async def main():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Q, directory=SITE)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{PORT}'
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        async def page(reg, paid=False):
            calls = []
            ctx = await br.new_context(viewport=dict(width=400, height=860)); pg = await ctx.new_page(); perr = []
            pg.on('pageerror', lambda e: perr.append(str(e)))
            async def api(route):
                b = json.loads(route.request.post_data or '{}'); calls.append(b.get('action'))
                if b.get('action') == 'buy': await asyncio.sleep(2.0); r = dict(ok=True, url=base + '/robots.txt')   # a slow payments script
                elif b.get('action') == 'passes': r = dict(ok=True, passes=dict(pyq='2099-01-01', paid=True) if paid else {})
                else: r = dict(ok=False, error='test')
                await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
            await pg.route('https://pay.test/**', api); await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
            await pg.route('https://accounts.google.com/**', lambda r: r.fulfill(status=200, body=''))
            if reg: await ctx.add_init_script(REG)
            return ctx, pg, calls, perr
        # registered student: the link is made while the window is open; Pay then opens the payment page at once
        ctx, pg, calls, perr = await page(True)
        await pg.goto(base + '/ts-police-si/'); await pg.wait_for_timeout(1000)
        await pg.click('#navSub'); await pg.wait_for_timeout(300)
        check(calls.count('buy') == 1, 'opening the payment window starts making the payment link')
        check(await pg.locator('link[rel=preconnect][href="https://www.instamojo.com"]').count() == 1, 'the browser connects to Instamojo early')
        await pg.wait_for_timeout(2500)   # the student reads the window
        t = time.time(); await pg.click('#payDlg [data-act="paybuy"]')
        await pg.wait_for_url('**/robots.txt', timeout=5000); took = time.time() - t
        check(took < 1.0, f'Pay opens the payment page at once ({took:.2f} s, the script takes 2 s)')
        check(calls.count('buy') == 1, 'no second payment link for the tap')
        check(not perr, 'no page errors: ' + '; '.join(perr[:2]))
        await ctx.close()
        # tapping Pay quickly (link still being made): waits for the same link, no duplicate
        ctx, pg, calls, perr = await page(True)
        await pg.goto(base + '/ts-police-si/'); await pg.wait_for_timeout(1000)
        await pg.click('#navSub'); await pg.wait_for_timeout(200); await pg.click('#payDlg [data-act="paybuy"]')
        await pg.wait_for_url('**/robots.txt', timeout=6000)
        check(calls.count('buy') == 1, 'a quick tap uses the link already being made (one link)')
        await ctx.close()
        # closing and opening the window again reuses the link
        ctx, pg, calls, perr = await page(True)
        await pg.goto(base + '/ts-police-si/'); await pg.wait_for_timeout(1000)
        await pg.click('#navSub'); await pg.wait_for_timeout(2300); await pg.click('#payDlg [data-act="payclose"]'); await pg.wait_for_timeout(300)
        await pg.click('#navSub'); await pg.wait_for_timeout(300)
        check(calls.count('buy') == 1, 'opening the window again does not make another link')
        await ctx.close()
        # a visitor who has not registered: no link in the background (Pay asks to register first)
        ctx, pg, calls, perr = await page(False)
        await pg.goto(base + '/ts-police-si/'); await pg.wait_for_timeout(1000)
        await pg.click('#navSub'); await pg.wait_for_timeout(2500)
        check(calls.count('buy') == 0, 'no payment link for a visitor who has not registered')
        await ctx.close()
        await br.close()
    srv.shutdown()
    print('ERRORS:', errors or 'none'); sys.exit(1 if errors else 0)
asyncio.run(main())
