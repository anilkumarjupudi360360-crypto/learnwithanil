import asyncio, sys, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file://' + os.path.join(ROOT, 'dist', 'site', 'index.html')
SHOTS = os.path.join(ROOT, 'test')
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
            await pg.click('#hub-static a.exam.live[href="#home"]'); await pg.wait_for_timeout(150)
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
                assert await pg.evaluate('location.hash') == '#join', 'timed test should ask for student details first'
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
        for sub, tag, h1word, l2 in [('appsc-group-1', 'g1', 'Group-I', 'te'), ('upsc-capf', 'capf', 'CAPF', 'hi')]:
            fp = os.path.join(ROOT, 'dist', 'site', sub, 'index.html')
            if not os.path.exists(fp): continue
            for width, name in [(1280, 'desk'), (390, 'phone')]:
                pg = await b.new_page(viewport={'width': width, 'height': 900})
                pg.on('pageerror', lambda e, tag=tag: errors.append(f'{tag} pageerror: {e}'))
                pg.on('console', lambda m, tag=tag: errors.append(f'{tag} console {m.type}: {m.text}') if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_TUNNEL' not in m.text else None)
                await pg.goto('file://' + fp); await pg.wait_for_timeout(500)
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
        await pg.goto('file://' + os.path.join(ROOT, 'dist', 'site', 'papers', 'appsc-group-2-screening-test-2024-question-paper-with-answers.html'))
        sw = await pg.evaluate('document.documentElement.scrollWidth')
        if sw > 390: errors.append(f'static page overflow {sw}')
        await b.close()
        print('ERRORS:', errors if errors else 'none')
asyncio.run(main())
