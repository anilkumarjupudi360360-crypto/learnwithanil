import asyncio, sys, os, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'dist', 'site')
SHOTS = os.path.join(ROOT, 'test')


class Pages(SimpleHTTPRequestHandler):
    """Serves dist/site like GitHub Pages: folder/ -> folder/index.html, unknown address -> 404.html with status 404."""
    def log_message(self, *a): pass
    def send_error(self, code, message=None, explain=None):
        if code == 404:
            body = open(os.path.join(SITE, '404.html'), 'rb').read()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers()
            self.wfile.write(body); return
        super().send_error(code, message, explain)


srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Pages, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        errors = []
        for width, name in [(1280, 'desk'), (390, 'phone')]:
            pg = await b.new_page(viewport={'width': width, 'height': 900})
            pg.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
            pg.on('console', lambda m: errors.append(f'console {m.type}: {m.text}') if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_TUNNEL' not in m.text else None)
            await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
            await pg.goto(URL); await pg.wait_for_timeout(600)
            assert await pg.evaluate('!document.getElementById("hub-static").hidden'), 'start page should be the exam hub'
            tiles = await pg.locator('#hub-static .exam').count()
            assert tiles >= 90, f'expected the full exam list, got {tiles}'
            await pg.fill('#examSearch', 'group 2'); await pg.wait_for_timeout(100)
            assert await pg.locator('#hub-static .exam:not([hidden])').count() == 2, 'search "group 2" should find APPSC and TGPSC Group-II'
            await pg.fill('#examSearch', '')
            await pg.screenshot(path=f'{SHOTS}/hub-{name}.png', full_page=False)
            sw = await pg.evaluate('document.documentElement.scrollWidth');
            if sw > width: errors.append(f'{name}: horizontal overflow {sw}>{width}')
            await pg.evaluate('window.__same = 1')
            await pg.click('#hub-static a.exam.live[href="/appsc-group-2/"]'); await pg.wait_for_timeout(150)
            assert await pg.evaluate('location.pathname') == '/appsc-group-2/', 'Group-II tile should open /appsc-group-2/'
            assert await pg.evaluate('window.__same === 1'), 'moving between views should not reload the page'
            assert await pg.evaluate('!document.getElementById("home-static").hidden'), 'the live Group-II tile should open the Group-II page'
            if name == 'desk': await pg.screenshot(path=f'{SHOTS}/home-{name}.png', full_page=False)
            for v in ['exams','exam/ssc-cgl','home','papers','practice','bank','mistakes','smart','bookmarks','heatmap','about','join','notes']:
                await pg.evaluate(f'location.hash="{v}"'); await pg.wait_for_timeout(150)
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                if sw > width: errors.append(f'{name}/{v}: horizontal overflow {sw}>{width}')
            if name == 'desk':
                # MCQ practice flow
                await pg.evaluate('location.hash="papers"'); await pg.wait_for_timeout(150)
                await pg.click('#view [data-act="paperpractice"][data-paper="s2024"]'); await pg.wait_for_timeout(150)
                for i in range(3):
                    await pg.click('[data-act="pick"][data-i="0"]'); await pg.click('[data-act="check"]')
                    await pg.click('[data-act="next"]')
                await pg.screenshot(path=f'{SHOTS}/quiz-mcq.png')
                await pg.click('[data-act="finish"]'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/result.png', full_page=False)
                # recall flow
                await pg.evaluate('location.hash="papers"'); await pg.wait_for_timeout(150)
                await pg.click('#view [data-act="paperpractice"][data-paper="s2019"]'); await pg.wait_for_timeout(150)
                await pg.click('[data-act="reveal"]'); await pg.click('[data-act="self"][data-v="W"]')
                await pg.screenshot(path=f'{SHOTS}/quiz-recall.png')
                await pg.click('[data-act="finish"]'); await pg.wait_for_timeout(150)
                mis = await pg.evaluate('document.getElementById("mcount").textContent')
                print('mistakes after two quizzes:', mis)
                # builder + timed test
                await pg.evaluate('location.hash="practice"'); await pg.wait_for_timeout(150)
                await pg.click('[data-act="mode"][data-mode="test"]'); await pg.click('[data-act="start"]'); await pg.wait_for_timeout(150)
                assert (await pg.evaluate('location.pathname')).endswith('/join/'), 'timed test should ask for student details first'
                await pg.fill('[name=name]', 'Test Student'); await pg.fill('[name=phone]', '9876543210'); await pg.fill('[name=email]', 'test@example.com')
                await pg.fill('[name=district]', 'Guntur'); await pg.check('[name=ok]'); await pg.click('#joinForm button[type=submit]'); await pg.wait_for_timeout(200)
                await pg.screenshot(path=f'{SHOTS}/quiz-test.png')
                await pg.click('[data-act="asksubmit"]'); await pg.click('.confirm [data-act="finish"]'); await pg.wait_for_timeout(150)
                await pg.evaluate('location.hash="heatmap"'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/heatmap.png')
                await pg.evaluate('location.hash="bank"'); await pg.wait_for_timeout(150)
                await pg.fill('#bankSearch', 'Polavaram'); await pg.wait_for_timeout(400)
                print('bank search:', await pg.inner_text('#bankResults p.muted'))
                await pg.evaluate('location.hash="about"'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/about.png')
                await pg.evaluate('location.hash="q/m2025p2-117"'); await pg.wait_for_timeout(300)
                assert 'GSLV' in await pg.inner_text('#view'), 'question link should open the GSLV question'
                await pg.click('[data-act="pick"][data-i="0"]'); await pg.click('[data-act="check"]'); await pg.wait_for_timeout(200)
                await pg.click('[data-act="video"]'); await pg.wait_for_timeout(500)
                assert await pg.evaluate('document.getElementById("videoDlg").open'), 'video dialog should open'
                await pg.screenshot(path=f'{SHOTS}/video-dialog.png')
                await pg.click('[data-act="closevideo"]')
                await pg.evaluate('location.hash="notes"'); await pg.wait_for_timeout(300)
                await pg.screenshot(path=f'{SHOTS}/notes-desk.png', full_page=True)
                print('notes cards:', await pg.locator('.note').count())
                await pg.click('.note-cover >> nth=1'); await pg.wait_for_timeout(400)
                await pg.screenshot(path=f'{SHOTS}/notes-sample.png')
                assert await pg.evaluate('document.getElementById("sampleDlg").open'), 'sample dialog should open'
                await pg.click('[data-act="closesample"]')
            else:
                await pg.evaluate('location.hash="notes"'); await pg.wait_for_timeout(300)
                await pg.screenshot(path=f'{SHOTS}/notes-phone.png', full_page=True)
                await pg.evaluate('location.hash="home"'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/home-phone.png', full_page=False)
        # exams in their own folders: APPSC Group-I (Telugu) and UPSC CAPF (Hindi)
        for sub, tag, h1word, l2 in [('appsc-group-1', 'g1', 'Group 1', 'te'), ('upsc-capf', 'capf', 'CAPF', 'hi'), ('ts-police-si', 'tssi', 'TS Police SI', 'te'), ('ts-police-constable', 'tspc', 'TS Police Constable', 'te')]:
            if not os.path.exists(os.path.join(SITE, sub, 'index.html')): continue
            fp = URL + sub + '/'
            for width, name in [(1280, 'desk'), (390, 'phone')]:
                pg = await b.new_page(viewport={'width': width, 'height': 900})
                pg.on('pageerror', lambda e, tag=tag: errors.append(f'{tag} pageerror: {e}'))
                pg.on('console', lambda m, tag=tag: errors.append(f'{tag} console {m.type}: {m.text}') if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_TUNNEL' not in m.text else None)
                await pg.goto(fp); await pg.wait_for_timeout(500)
                assert await pg.evaluate('!document.getElementById("home-static").hidden'), f'{tag} page should open on its home'
                assert h1word in await pg.inner_text('#home-static h1')
                assert await pg.locator(f'[data-act="lang"][data-l="{l2}"]').count() == 1, f'{tag}: {l2} language button missing'
                await pg.screenshot(path=f'{SHOTS}/{tag}-home-{name}.png', full_page=False)
                for v in ['papers','practice','bank','mistakes','smart','bookmarks','heatmap','about','notes']:
                    await pg.evaluate(f'location.hash="{v}"'); await pg.wait_for_timeout(150)
                    sw = await pg.evaluate('document.documentElement.scrollWidth')
                    if sw > width: errors.append(f'{tag} {name}/{v}: horizontal overflow {sw}>{width}')
                await pg.evaluate('location.hash="papers"'); await pg.wait_for_timeout(150)
                await pg.click('#view [data-act="paperpractice"] >> nth=0'); await pg.wait_for_timeout(150)
                await pg.click('[data-act="pick"][data-i="0"]'); await pg.click('[data-act="check"]')
                await pg.screenshot(path=f'{SHOTS}/{tag}-quiz-{name}.png')
                await pg.click(f'[data-act="lang"][data-l="{l2}"]'); await pg.wait_for_timeout(150)
                if l2 == 'hi':
                    assert await pg.locator('#view .qtext[lang="hi"]').count() >= 1, 'CAPF question should show in Hindi'
                await pg.screenshot(path=f'{SHOTS}/{tag}-quiz-{l2}-{name}.png')
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                if sw > width: errors.append(f'{tag} {name}/quiz-{l2}: horizontal overflow {sw}>{width}')
                await pg.click('[data-act="lang"][data-l="en"]')
                await pg.close()
        # static page
        pg = await b.new_page(viewport={'width': 390, 'height': 900})
        pg.on('pageerror', lambda e: errors.append(f'static pageerror: {e}'))
        await pg.goto(URL + 'papers/appsc-group-2-screening-test-2024-question-paper-with-answers.html')
        sw = await pg.evaluate('document.documentElement.scrollWidth')
        if sw > 390: errors.append(f'static page overflow {sw}')
        # real addresses: direct loads, old #links, deep links through 404.html, question pages, back button
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        pg.on('pageerror', lambda e: errors.append(f'paths pageerror: {e}'))
        async def view():
            return await pg.evaluate("""(()=>{ const hub = document.getElementById('hub-static'), home = document.getElementById('home-static');
                if(hub && !hub.hidden) return 'exams'; if(home && !home.hidden) return 'home';
                const h = document.querySelector('#view h1, #view h2'); return h ? h.innerText : '?'; })()""")
        checks = [('appsc-group-1/bank/', '/appsc-group-1/bank/', 'Search'), ('upsc-capf/practice/', '/upsc-capf/practice/', 'quiz'),
                  ('#home', '/appsc-group-2/', 'home'), ('appsc-group-1/#papers', '/appsc-group-1/papers/', 'question papers'),
                  ('upsc-capf/q/c2026a-3/', '/upsc-capf/quiz/', 'Raghu'), ('upsc-capf/?q=c2026a-4', '/upsc-capf/quiz/', 'Ol Chiki'),
                  ('exam/ssc-cgl/', '/exam/ssc-cgl/', 'CGL'), ('appsc-group-2/papers/', '/appsc-group-2/papers/', 'question papers')]
        for path, want, word in checks:
            await pg.goto(URL + path); await pg.wait_for_timeout(700)
            got = await pg.evaluate('location.pathname')
            txt = await pg.evaluate('document.body.innerText')
            if got != want: errors.append(f'paths: {path} ended at {got}, wanted {want}')
            elif word not in (await view()) and word not in txt: errors.append(f'paths: {path} did not show "{word}"')
        await pg.goto(URL + 'appsc-group-1/'); await pg.wait_for_timeout(500)
        await pg.click('#nav a[data-v="bank"]'); await pg.wait_for_timeout(200)
        if await pg.evaluate('location.pathname') != '/appsc-group-1/bank/': errors.append('paths: nav click did not change the address')
        await pg.go_back(); await pg.wait_for_timeout(300)
        if await pg.evaluate('location.pathname') != '/appsc-group-1/' or await view() != 'home': errors.append('paths: back button did not return home')
        await pg.goto(URL + 'upsc-capf/q/c2026a-3.html'); await pg.wait_for_timeout(300)
        if 'Raghu Rai' not in await pg.inner_text('main'): errors.append('question page: text missing')
        await pg.click('text=Answer it in the practice app'); await pg.wait_for_timeout(800)
        if await pg.evaluate('location.pathname') != '/upsc-capf/quiz/': errors.append('question page: practice link did not open the quiz')
        # an exam page carries only its own heading; "All exams" goes back to the start page
        await pg.goto(URL + 'appsc-group-1/'); await pg.wait_for_timeout(400)
        raw = open(os.path.join(SITE, 'appsc-group-1', 'index.html'), encoding='utf-8').read()
        markup = raw.split('<body>')[1].split('<script')[0]
        if 'id="hub-static"' in raw or markup.count('<h1') != 1: errors.append('appsc-group-1/: should have one h1 and no exam list')
        await pg.click('#nav a[href="/"]'); await pg.wait_for_timeout(800)
        if await pg.evaluate('location.pathname') != '/' or await view() != 'exams': errors.append('All exams link from an exam page did not open the start page')
        # every PDF in the sitemap exists
        import re as _re
        for u in _re.findall(r'<loc>https?://[^/]+/([^<]*\.pdf)</loc>', open(os.path.join(SITE, 'sitemap.xml')).read()):
            f = os.path.join(SITE, u)
            if not os.path.exists(f) or open(f, 'rb').read(4) != b'%PDF': errors.append(f'missing PDF {u} (run tools/pdfs.py)')
        r = await pg.goto(URL + 'no-such-page/'); await pg.wait_for_timeout(200)
        if r.status != 404 or 'does not exist' not in await pg.inner_text('body'): errors.append('404 page missing')
        await pg.close()
        await b.close()
        srv.shutdown()
        print('ERRORS:', errors if errors else 'none')
asyncio.run(main())
