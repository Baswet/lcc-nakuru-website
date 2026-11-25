"""QA: 13 pages x 8 widths — overflow, JS errors, axe (WCAG 2.1 AA), internal links, touch targets. Run with the site served on :8765."""
import asyncio, json, re, pathlib, sys
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent / 'website'
OUT = pathlib.Path(__file__).resolve().parent
PAGES = sorted(p.name for p in ROOT.glob('*.html'))
WIDTHS = [320, 360, 375, 390, 430, 768, 1024, 1440]
AXE = open('/tmp/fonts/node_modules/axe-core/axe.min.js').read()
async def main():
    res = {'overflow': [], 'jserrors': [], 'axe': {}, 'links': [], 'small_targets': []}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        STUB = open('/tmp/stub.jpg','rb').read()
        for name in PAGES:
            for w in WIDTHS:
                pg = await b.new_page(viewport={'width': w, 'height': 900 if w >= 768 else 780})
                await pg.route('https://i.ytimg.com/**', lambda r: r.fulfill(body=STUB, content_type='image/jpeg'))
                errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
                await pg.goto(f'http://localhost:8765/{name}', wait_until='domcontentloaded'); await pg.wait_for_timeout(350)
                await pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>{e.classList.add('in');e.style.transition='none'})")
                ov = await pg.evaluate("[document.documentElement.scrollWidth, innerWidth]")
                if ov[0] > ov[1]: res['overflow'].append(f'{name}@{w}: {ov}')
                if errs: res['jserrors'].append(f'{name}@{w}: {errs}')
                if w in (390, 1440):
                    await pg.add_script_tag(content=AXE)
                    r = await pg.evaluate("axe.run(document,{runOnly:['wcag2a','wcag2aa','wcag21aa','best-practice']}).then(r=>r.violations.map(v=>[v.id,v.impact,v.nodes.length,v.nodes.slice(0,2).map(n=>n.target.join(' '))]))")
                    if r: res['axe'][f'{name}@{w}'] = r
                if w == 390:
                    st = await pg.evaluate("[...document.querySelectorAll('main a.btn, main button, .menu-toggle, .chip')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [e.textContent.trim().slice(0,30),Math.round(r.width),Math.round(r.height)]}).filter(x=>x[1]<44||x[2]<44)")
                    if st: res['small_targets'].append(f'{name}: {st}')
                if (name == 'index.html' or name == 'about.html') or w in (390, 1440):
                    await pg.screenshot(path=str(OUT / 'screenshots' / f"{name[:-5]}-{w}.png"), full_page=(w in (390, 1440)))
                await pg.close()
        await b.close()
    for name in PAGES:
        src = (ROOT / name).read_text()
        for h in re.findall(r'href="([^"#:]+?)(?:#[^"]*)?"', src):
            if h.startswith(('http', 'mailto', 'tel', '//')) or h == './': continue
            if not (ROOT / h).exists(): res['links'].append(f'{name} -> {h}')
    json.dump(res, open(OUT / 'qa-results.json', 'w'), indent=1)
    print(json.dumps({k: (len(v) if not isinstance(v, dict) else len(v)) for k, v in res.items()}))
    print(json.dumps(res, indent=1)[:4000])
asyncio.run(main())
