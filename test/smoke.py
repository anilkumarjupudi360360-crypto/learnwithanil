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
            pg.on('console', lambda m: errors.append(f'console {m.type}: {m.text}') if m.type == 'error' else None)
            await pg.goto(URL); await pg.wait_for_timeout(600)
            if name == 'desk': await pg.screenshot(path=f'{SHOTS}/home-{name}.png', full_page=False)
            sw = await pg.evaluate('document.documentElement.scrollWidth'); 
            if sw > width: errors.append(f'{name}: horizontal overflow {sw}>{width}')
            for v in ['papers','practice','bank','mistakes','smart','bookmarks','heatmap','about']:
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
                await pg.screenshot(path=f'{SHOTS}/quiz-test.png')
                await pg.click('[data-act="asksubmit"]'); await pg.click('.confirm [data-act="finish"]'); await pg.wait_for_timeout(150)
                await pg.evaluate('location.hash="heatmap"'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/heatmap.png')
                await pg.evaluate('location.hash="bank"'); await pg.wait_for_timeout(150)
                await pg.fill('#bankSearch', 'Polavaram'); await pg.wait_for_timeout(400)
                print('bank search:', await pg.inner_text('#bankResults p.muted'))
                await pg.evaluate('location.hash="about"'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/about.png')
            else:
                await pg.evaluate('location.hash="home"'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SHOTS}/home-phone.png', full_page=False)
        # static page
        pg = await b.new_page(viewport={'width': 390, 'height': 900})
        pg.on('pageerror', lambda e: errors.append(f'static pageerror: {e}'))
        await pg.goto('file://' + os.path.join(ROOT, 'dist', 'site', 'papers', 'appsc-group-2-screening-test-2024-question-paper-with-answers.html'))
        sw = await pg.evaluate('document.documentElement.scrollWidth')
        if sw > 390: errors.append(f'static page overflow {sw}')
        await b.close()
        print('ERRORS:', errors if errors else 'none')
asyncio.run(main())
