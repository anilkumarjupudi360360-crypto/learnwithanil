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
PAY_API = 'https://script.google.com/macros/**'
def fake_pay(passes):   # the payments script: a student with the given passes
    import json
    async def h(route):
        try: act = json.loads(route.request.post_data or '{}').get('action')
        except Exception: act = ''
        r = {'ok': True, 'passes': passes} if act in ('passes', 'verify') else {'ok': False, 'error': 'test'}
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
    return h
PAID = {'pyq': '2099-12-31', 'paid': True}
REGISTERED = 'try{localStorage.setItem("lwa-appsc-g2-student-v1", JSON.stringify({name:"Test Student",phone:"9876543210",email:"t@example.com",district:"Guntur",pending:[]}))}catch(e){}'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        _new = b.new_page
        async def new_page(passes=PAID, **kw):   # every page talks to a fake payments script: by default a student with the PYQ Pass
            pg = await _new(**kw); await pg.route(PAY_API, fake_pay(passes)); return pg
        b.new_page = new_page
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
            live = await pg.locator('#hub-static .exam.live').count()
            built = sum(1 for d in ('appsc-group-1', 'upsc-capf', 'upsc-epfo', 'ssc-cgl', 'ts-police-si', 'ts-police-constable', 'tgpsc-hmwssb-manager', 'appsc-amvi', 'tgpsc-amvi') if os.path.exists(os.path.join(SITE, d, 'index.html'))) + 1
            assert live == built, f'{built} exams are built but {live} tiles are live'
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
            for v in ['exams','exam/ssc-chsl','home','papers','practice','bank','mistakes','smart','bookmarks','heatmap','about','join','notes']:
                await pg.evaluate(f'location.hash="{v}"'); await pg.wait_for_timeout(150)
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                if sw > width: errors.append(f'{name}/{v}: horizontal overflow {sw}>{width}')
            if name == 'desk':
                # MCQ practice flow
                await pg.evaluate('location.hash="papers"'); await pg.wait_for_timeout(150)
                await pg.click('#view [data-act="paperpractice"][data-paper="s2024"]'); await pg.wait_for_timeout(150)
                # the first quiz of a new visitor asks for the one-time registration
                assert (await pg.evaluate('location.pathname')).endswith('/join/'), 'the first quiz should ask for registration'
                await pg.screenshot(path=f'{SHOTS}/join.png')
                await pg.fill('[name=name]', 'Test Student'); await pg.fill('[name=phone]', '9876543210'); await pg.fill('[name=email]', 'test@example.com')
                await pg.fill('[name=district]', 'Guntur'); await pg.check('[name=ok]'); await pg.click('#joinForm button[type=submit]'); await pg.wait_for_timeout(200)
                assert (await pg.evaluate('location.pathname')).endswith('/quiz/'), 'after registering, the quiz should start'
                for i in range(3):
                    await pg.click('[data-act="pick"][data-i="0"]'); await pg.click('[data-act="check"]')
                    await pg.click('[data-act="next"]')
                await pg.screenshot(path=f'{SHOTS}/quiz-mcq.png')
                await pg.click('[data-act="finish"]'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/result.png', full_page=False)
                # an answer-only paper (2019): APPSC's answer plus three options by Learn with Anil, labelled
                await pg.evaluate('location.hash="papers"'); await pg.wait_for_timeout(150)
                await pg.click('#view [data-act="paperpractice"][data-paper="s2019"]'); await pg.wait_for_timeout(150)
                if await pg.locator('[data-act="reveal"]').count():
                    await pg.click('[data-act="reveal"]'); await pg.click('[data-act="self"][data-v="W"]')
                else:
                    if await pg.locator('[data-act="pick"]').count() != 4: errors.append('s2019: question does not show four options')
                    if 'options: Learn with Anil' not in await pg.inner_text('#view'): errors.append('s2019: options are not labelled as written by Learn with Anil')
                    await pg.click('[data-act="pick"][data-i="0"]'); await pg.click('[data-act="check"]')
                await pg.screenshot(path=f'{SHOTS}/quiz-recall.png')
                await pg.click('[data-act="finish"]'); await pg.wait_for_timeout(150)
                mis = await pg.evaluate('document.getElementById("mcount").textContent')
                print('mistakes after two quizzes:', mis)
                # builder + timed test
                await pg.evaluate('location.hash="practice"'); await pg.wait_for_timeout(150)
                await pg.click('[data-act="mode"][data-mode="test"]'); await pg.click('[data-act="start"]'); await pg.wait_for_timeout(150)
                assert (await pg.evaluate('location.pathname')).endswith('/quiz/'), 'a registered student should go straight to the test'
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
        for sub, tag, h1word, l2 in [('appsc-group-1', 'g1', 'Group 1', 'te'), ('upsc-capf', 'capf', 'CAPF', 'hi'), ('upsc-epfo', 'epfo', 'EPFO', 'hi'), ('ssc-cgl', 'cgl', 'SSC CGL', 'hi'), ('ts-police-si', 'tssi', 'TS Police SI', 'te'), ('ts-police-constable', 'tspc', 'TS Police Constable', 'te'), ('tgpsc-hmwssb-manager', 'hmws', 'HMWSSB Manager', 'te'), ('appsc-amvi', 'apamvi', 'APPSC AMVI', 'te'), ('tgpsc-amvi', 'tgamvi', 'TGPSC AMVI', 'te')]:
            if not os.path.exists(os.path.join(SITE, sub, 'index.html')): continue
            fp = URL + sub + '/'
            for width, name in [(1280, 'desk'), (390, 'phone')]:
                pg = await b.new_page(viewport={'width': width, 'height': 900})
                await pg.add_init_script(REGISTERED); await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
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
                if l2 == 'hi' and tag != 'epfo':   # EPFO Q1-20 (General English) are English only
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
        await pg.add_init_script(REGISTERED); await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        pg.on('pageerror', lambda e: errors.append(f'paths pageerror: {e}'))
        async def view():
            return await pg.evaluate("""(()=>{ const hub = document.getElementById('hub-static'), home = document.getElementById('home-static');
                if(hub && !hub.hidden) return 'exams'; if(home && !home.hidden) return 'home';
                const h = document.querySelector('#view h1, #view h2'); return h ? h.innerText : '?'; })()""")
        checks = [('appsc-group-1/bank/', '/appsc-group-1/bank/', 'Search'), ('upsc-capf/practice/', '/upsc-capf/practice/', 'quiz'),
                  ('#home', '/appsc-group-2/', 'home'), ('appsc-group-1/#papers', '/appsc-group-1/papers/', 'question papers'),
                  ('upsc-capf/q/c2026a-3/', '/upsc-capf/quiz/', 'Raghu'), ('upsc-capf/?q=c2026a-4', '/upsc-capf/quiz/', 'Ol Chiki'),
                  ('exam/ssc-chsl/', '/exam/ssc-chsl/', 'CHSL'), ('appsc-group-2/papers/', '/appsc-group-2/papers/', 'question papers')]
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
        # ?test=<paper>: a full timed mock test of that paper, from the mock-test pages
        for path, n in (('ts-police-si/?test=s2022', 191), ('appsc-group-2/?test=s2024', 143)):
            await pg.goto(URL + path); await pg.wait_for_timeout(700)
            if not (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append(f'{path}: did not open the mock test')
            elif str(n) not in await pg.inner_text('main'): errors.append(f'{path}: mock test does not show {n} questions')
        for rel in ('ts-police-si/mock-test.html', 'appsc-group-2/mock-test.html', 'appsc-group-2-notification-2026.html', 'appsc-group-1-notification-2026.html'):
            raw = open(os.path.join(SITE, rel), encoding='utf-8').read()
            for h in _re.findall(r'href="(/[^"#:?]*)', raw):
                f = os.path.join(SITE, h.lstrip('/'))
                if not (os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html'))): errors.append(f'{rel}: broken link {h}')
        # every exam home: three tiles (PYQs, mock tests, sectional tests), each a page of its own; no question of the day there
        smx = open(os.path.join(SITE, 'sitemap.xml')).read()
        for sub in ('ts-police-si', 'ts-police-constable', 'appsc-group-2', 'appsc-group-1', 'upsc-capf', 'upsc-epfo', 'ssc-cgl', 'tgpsc-hmwssb-manager', 'appsc-amvi', 'tgpsc-amvi'):
            for rel in (f'{sub}/pyqs.html', f'{sub}/mock-test.html', f'{sub}/sectional-tests.html'):
                if not os.path.isfile(os.path.join(SITE, rel)): errors.append(f'missing {rel}'); continue
                if f'/{rel}</loc>' not in smx: errors.append(f'{rel} not in sitemap')
                body = open(os.path.join(SITE, rel), encoding='utf-8').read()
                if 'Payments open soon' in body or 'stays free' in body or 'Read with answers (free)' in body or 'download>PDF' in body:
                    errors.append(f'{rel}: says something is free or offers a free PDF')
                if '<h2>Plans</h2>' not in body or 'PYQ Pass' not in body: errors.append(f'{rel}: no plans table')
                if 'Free trial' in body or 'days free' in body.lower(): errors.append(f'{rel}: still offers a free trial')
                if ('?sec=' in body or '?practice=' in body) and 'class="lk"' not in body: errors.append(f'{rel}: PYQ buttons show no lock')
                if rel.endswith('pyqs.html') and ('Attempt as a timed test' in body or 'Practise question by question' in body or 'min timer</a>' not in body): errors.append(f'{rel}: papers should have one "Attempt this paper" button')
                for h in _re.findall(r'href="(/[^"#:?]*)', open(os.path.join(SITE, rel), encoding='utf-8').read()):
                    f = os.path.join(SITE, h.lstrip('/'))
                    if not (os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html'))): errors.append(f'{rel}: broken link {h}')
            await pg.goto(URL + sub + '/'); await pg.wait_for_timeout(400)
            nt = await pg.locator('#home-static .etiles .etile:not(.etile-sm)').count()
            if nt != 3: errors.append(f'{sub}: {nt} main tiles on the exam home, expected 3')
            if await pg.locator('#qotd-home').count(): errors.append(f'{sub}: question of the day should only be on the start page')
            for h in await pg.eval_on_selector_all('#home-static .etiles a', 'els => els.map(e => e.getAttribute("href"))'):
                f = os.path.join(SITE, h.lstrip('/'))
                if not (os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html'))): errors.append(f'{sub}: tile links to missing {h}')
        # every previous paper runs with a countdown timer (1 minute per question), also question by question
        for path in ('appsc-group-2/?practice=s2024', 'appsc-group-1/?practice=p2023a'):
            await pg.goto(URL + path); await pg.wait_for_timeout(1500)
            if (await pg.evaluate('location.pathname')).endswith('/quiz/'):
                t = await pg.inner_text('#timer')
                if t.count(':') != 2: errors.append(f'{path}: no countdown timer (shows {t})')
                # the student can switch the timer off (the clock pauses) and on again
                if not await pg.locator('[data-act="timertoggle"][aria-checked="true"].on').count(): errors.append(f'{path}: no timer on/off button')
                else:
                    await pg.click('[data-act="timertoggle"]'); t1 = await pg.inner_text('#timer'); await pg.wait_for_timeout(2200)
                    if await pg.inner_text('#timer') != t1 or not await pg.locator('#timer.off').count(): errors.append(f'{path}: timer kept running after switching it off')
                    await pg.click('[data-act="timertoggle"]'); await pg.wait_for_timeout(2200)
                    if await pg.inner_text('#timer') == t1: errors.append(f'{path}: timer did not restart after switching it on')
        # study material (APPSC Mains books) only on the APPSC Group 1 / Group 2 pages
        for sub, want in (('appsc-group-2', True), ('appsc-group-1', True), ('upsc-epfo', False), ('ts-police-si', False), ('upsc-capf', False)):
            raw = open(os.path.join(SITE, sub, 'index.html'), encoding='utf-8').read()
            has = 'class="card notes-promo"' in raw or 'data-v="notes"' in raw
            if has != want: errors.append(f'{sub}: study material {"missing" if want else "shown"}')
        # help & grievance page: exists, in the sitemap, linked from footers, form posts a grievance and shows the ticket
        if '/help.html</loc>' not in open(os.path.join(SITE, 'sitemap.xml')).read(): errors.append('help.html not in sitemap')
        if 'href="/help.html"' not in open(os.path.join(SITE, 'appsc-group-1', 'index.html'), encoding='utf-8').read(): errors.append('app footer has no Help & grievances link')
        if '/funders.html</loc>' not in open(os.path.join(SITE, 'sitemap.xml')).read(): errors.append('funders.html not in sitemap')
        if 'href="/funders.html"' not in open(os.path.join(SITE, 'index.html'), encoding='utf-8').read(): errors.append('home page has no Fund this project link')
        _fp = open(os.path.join(SITE, 'funders.html'), encoding='utf-8').read()
        if 'wa.me/' not in _fp or 'mailto:' not in _fp: errors.append('funders.html: no WhatsApp/email contact')
        if '/og-funders.jpg"' not in _fp or not os.path.exists(os.path.join(SITE, 'og-funders.jpg')): errors.append('funders.html: no og:image')
        hp = await b.new_page(viewport={'width': 390, 'height': 900})
        async def griev(route):
            import json as _j
            body = _j.loads(route.request.post_data or '{}')
            ok = body.get('action') == 'grievance' and body.get('category') and len(body.get('message', '')) >= 10
            await route.fulfill(status=200, content_type='application/json', body=_j.dumps({'ok': True, 'ticket': 'LWA-261025-001'} if ok else {'ok': False, 'error': 'bad'}))
        await hp.route(PAY_API, griev)
        await hp.goto(URL + 'help.html'); await hp.wait_for_timeout(300)
        await hp.fill('#gForm [name=name]', 'Test Student'); await hp.fill('#gForm [name=phone]', '9876543210')
        await hp.fill('#gForm [name=message]', 'My pass did not open after paying.'); await hp.click('#gForm button[type=submit]'); await hp.wait_for_timeout(800)
        if 'LWA-261025-001' not in await hp.inner_text('#gMsg'): errors.append('help.html: grievance form did not show a ticket number')
        sw = await hp.evaluate('document.documentElement.scrollWidth')
        if sw > 390: errors.append(f'help.html overflow {sw}')
        await hp.close()
        # practice papers do not close at time-up; a test in progress survives a reload
        tp = await b.new_page(viewport={'width': 1280, 'height': 900}); await tp.add_init_script(REGISTERED)
        await tp.goto(URL + 'appsc-group-2/?practice=s2024'); await tp.wait_for_timeout(1200)
        await tp.click('[data-act="pick"][data-i="0"]'); await tp.click('[data-act="check"]'); await tp.wait_for_timeout(200)
        await tp.reload(); await tp.wait_for_timeout(1500)
        if not (await tp.evaluate('location.pathname')).endswith('/quiz/') or 'Question' not in await tp.inner_text('main'): errors.append('reload during a practice paper lost the paper')
        # pretend the paper's time ran out long ago: a practice paper stays open, the extra time shows as +m:ss
        await tp.goto(URL + 'help.html'); await tp.wait_for_timeout(300)
        await tp.evaluate('(()=>{const k=Object.keys(localStorage).find(k=>k.endsWith("-quiz-v1")); const v=JSON.parse(localStorage.getItem(k)); v.QZ.t0-=1e7; localStorage.setItem(k, JSON.stringify(v));})()')
        await tp.goto(URL + 'appsc-group-2/quiz/'); await tp.wait_for_timeout(2500)
        if not (await tp.evaluate('location.pathname')).endswith('/quiz/') or not (await tp.inner_text('#timer')).startswith('+'): errors.append('practice paper closed at time-up (should stay open with +extra time)')
        # pick one answer without pressing "Check answer", then End quiz: the result page, not some other page
        await tp.goto(URL + 'appsc-group-2/?practice=s2024'); await tp.wait_for_timeout(1500)
        if await tp.locator('[data-act="pick"]').count():
            await tp.click('[data-act="pick"][data-i="1"]'); await tp.click('[data-act="finish"]'); await tp.wait_for_timeout(800)
            if not (await tp.evaluate('location.pathname')).endswith('/result/'): errors.append('End quiz after picking one answer did not show the result')
        await tp.evaluate('localStorage.removeItem("lwa-appsc-g2-quiz-v1")')
        # the last question always has a Submit button below it
        await tp.goto(URL + 'appsc-group-2/?practice=s2024'); await tp.wait_for_timeout(1500)
        n = await tp.locator('[data-act="jump"]').count()
        if n:
            await tp.click(f'[data-act="jump"][data-i="{n-1}"]'); await tp.wait_for_timeout(300)
            if not await tp.locator('.qnav [data-act="finish"]').count(): errors.append('last question has no Submit button below it')
            await tp.click('.qnav [data-act="finish"]'); await tp.wait_for_timeout(600)
        await tp.evaluate('localStorage.removeItem("lwa-appsc-g2-quiz-v1")')
        # leaving the test (other app/tab) pauses the clock; coming back starts it again from the same time
        await tp.goto(URL + 'ts-police-si/?sec=ari'); await tp.wait_for_timeout(1500)
        t1 = await tp.inner_text('#timer')
        await tp.evaluate('Object.defineProperty(document, "hidden", {value: true, configurable: true}); document.dispatchEvent(new Event("visibilitychange"))')
        await tp.wait_for_timeout(4000)
        await tp.evaluate('Object.defineProperty(document, "hidden", {value: false, configurable: true}); document.dispatchEvent(new Event("visibilitychange"))')
        await tp.wait_for_timeout(600); t2 = await tp.inner_text('#timer')
        secs = lambda t: sum(int(x) * 60 ** i for i, x in enumerate(reversed(t.split(':'))))
        if secs(t1) - secs(t2) > 3: errors.append(f'timer kept running while the student was away ({t1} -> {t2})')
        await tp.evaluate('localStorage.clear()'); await tp.goto(URL + 'upsc-epfo/quiz/'); await tp.wait_for_timeout(1200)
        if not (await tp.evaluate('location.pathname')).endswith('/papers/'): errors.append('quiz page with no open test should show the papers list')
        await tp.close()
        # llms.txt (summary for AI assistants) lists every exam, and every link in it is a real page
        lt = open(os.path.join(SITE, 'llms.txt'), encoding='utf-8').read()
        for h in _re.findall(r'https://learnwithanil\.in/([^\s)]*)', lt):
            f = os.path.join(SITE, h)
            if h and not (os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html'))): errors.append(f'llms.txt: broken link /{h}')
        epm = open(os.path.join(SITE, 'upsc-epfo', 'mock-test.html'), encoding='utf-8').read()
        if '₹199' not in epm or 'coming soon' not in epm or '?buy=mock' in epm: errors.append('upsc-epfo/mock-test.html: no "₹199 · coming soon" pack, or it can be bought already')
        await pg.goto(URL + 'ts-police-si/?sec=ari'); await pg.wait_for_timeout(600)
        if not (await pg.evaluate('location.pathname')).endswith('/quiz/'): errors.append('?sec=ari did not open a sectional test')
        await pg.goto(URL + 'ts-police-si/?buy=mock'); await pg.wait_for_timeout(500)
        if not await pg.evaluate('!!document.querySelector("#payDlg[open]")') or 'Mission Khaki' not in await pg.inner_text('#payDlg'): errors.append('?buy=mock did not open the Mission Khaki checkout')
        # site icon: the files exist and the pages point to them
        for f in ('favicon.ico', 'icon-192.png', 'apple-touch-icon.png', 'icon-512.png'):
            if not os.path.isfile(os.path.join(SITE, f)): errors.append(f'missing {f}')
        for page in ('index.html', 'appsc-group-1/index.html', 'ts-police-pyqs.html', 'ts-police-si/papers/ts-police-si-prelims-2022-question-paper-with-answers.html', 'upsc-capf/q/c2026a-3.html'):
            if 'rel="icon" href="/favicon.ico"' not in open(os.path.join(SITE, page), encoding='utf-8').read(): errors.append(f'{page}: no site icon link')
        # board landing pages: in the sitemap, and every link on them leads to a real file
        sm = open(os.path.join(SITE, 'sitemap.xml')).read()
        for land in ('appsc-pyqs.html', 'ts-police-pyqs.html'):
            if f'/{land}</loc>' not in sm: errors.append(f'{land} not in sitemap')
            for h in _re.findall(r'href="([^"#:]+)"', open(os.path.join(SITE, land), encoding='utf-8').read()):
                f = os.path.join(SITE, h.lstrip('/'))
                if not (os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html'))): errors.append(f'{land}: broken link {h}')
        # Bahubali Test Series (paid): the page is built once tests are sealed, and nothing is published unencrypted
        bbdir = os.path.join(SITE, 'appsc-group-2', 'bahubali-test-series')
        if os.path.isfile(os.path.join(ROOT, 'src', 'bahubali', 'series.json')):
            if not os.path.isfile(os.path.join(bbdir, 'index.html')): errors.append('Bahubali page missing')
            else:
                await pg.goto(URL + 'appsc-group-2/bahubali-test-series/'); await pg.wait_for_timeout(300)
                if await pg.locator('[data-test]').count() < 1: errors.append('Bahubali: no live test cards')
                if await pg.locator('#unlockForm').count() != 1: errors.append('Bahubali: no unlock form')
                if '/appsc-group-2/bahubali-test-series/</loc>' not in sm: errors.append('Bahubali page not in sitemap')
                for d, bad in (('data', b'"q":'), ('pdf', None)):
                    for f in os.listdir(os.path.join(bbdir, d)):
                        raw = open(os.path.join(bbdir, d, f), 'rb').read()
                        if (bad and bad in raw) or (d == 'pdf' and b'/Encrypt' not in raw): errors.append(f'Bahubali {d}/{f} is not encrypted')
        # no free trial anywhere on the site (Anil, 23 Oct 2026)
        for dp, _, fs in os.walk(SITE):
            for f in fs:
                if f.endswith(('.html', '.js')):
                    t = open(os.path.join(dp, f), encoding='utf-8', errors='ignore').read()
                    if 'days free' in t or 'రోజులు ఉచితం' in t or 'दिन निःशुल्क' in t: errors.append(f'{os.path.relpath(os.path.join(dp, f), SITE)}: mentions a free trial')
        # payments on: without a pass nothing PYQ opens (registered student, old free-trial date, no PYQ Pass)
        np = await b.new_page(passes={'pyq': '2099-01-03', 'trial': '2099-01-03'}, viewport={'width': 1280, 'height': 900})
        await np.add_init_script(REGISTERED); await np.route('**/formResponse', lambda r: r.fulfill(status=200, body='ok'))
        np.on('pageerror', lambda e: errors.append(f'nopass pageerror: {e}'))
        for path in ('ts-police-si/?test=s2022', 'ts-police-si/?sec=ari', 'upsc-capf/q/c2026a-3/', 'appsc-group-2/?practice=s2024'):
            await np.goto(URL + path); await np.wait_for_timeout(900)
            if (await np.evaluate('location.pathname')).endswith('/quiz/'): errors.append(f'nopass: {path} opened a quiz without a pass')
        await np.goto(URL + 'ts-police-si/?test=s2022'); await np.wait_for_timeout(900)
        if not await np.evaluate('!!document.querySelector("#payDlg[open]")') or 'PYQ Pass' not in await np.inner_text('#payDlg'): errors.append('nopass: ?test= did not open the PYQ Pass checkout')
        for v in ('bank', 'practice', 'mistakes'):
            await np.goto(URL + f'appsc-group-2/{v}/'); await np.wait_for_timeout(600)
            if 'Unlock' not in await np.inner_text('#view'): errors.append(f'nopass: {v} is open without a plan')
        await np.goto(URL + 'upsc-epfo/sectional-tests.html'); await np.wait_for_timeout(400)
        if await np.locator('.lk.ok').count() or not await np.locator('.lk').count(): errors.append('nopass: sectional buttons show no lock')
        await np.goto(URL + 'upsc-epfo/'); await np.wait_for_timeout(600)
        if '🔒' not in await np.inner_text('#home-static .etiles'): errors.append('nopass: exam tiles show no lock')
        await np.close()
        # with a paid pass: "✓ Unlocked", no locks, and a line saying the pass is active
        pp = await b.new_page(viewport={'width': 1280, 'height': 900}); await pp.add_init_script(REGISTERED)
        await pp.add_init_script('try{localStorage.setItem("lwa-passes-v1", JSON.stringify({all:{pyq:"2099-12-31",paid:true}}))}catch(e){}')
        await pp.goto(URL + 'upsc-epfo/sectional-tests.html'); await pp.wait_for_timeout(400)
        if await pp.locator('.lk:not(.ok)').count() or not await pp.locator('.passon:not([hidden])').count(): errors.append('paid: sectional page still locked or no "pass active" line')
        await pp.goto(URL + 'upsc-epfo/'); await pp.wait_for_timeout(800)
        if 'Unlocked' not in await pp.inner_text('#home-static .etiles') or '🔒' in await pp.inner_text('#home-static .etiles'): errors.append('paid: exam tiles not marked unlocked')
        await pp.close()
        r = await pg.goto(URL + 'no-such-page/'); await pg.wait_for_timeout(200)
        if r.status != 404 or 'does not exist' not in await pg.inner_text('body'): errors.append('404 page missing')
        await pg.close()
        await b.close()
        srv.shutdown()
        print('ERRORS:', errors if errors else 'none')
asyncio.run(main())
