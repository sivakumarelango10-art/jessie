"""Loading-screen checks: first frame, duration, layout shift, reveal, clickability, reduced motion, no JS.

Usage: SITE_URL=http://127.0.0.1:8767/dist/site/ python3 scripts/loader_test.py <screenshot-dir>
"""
import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = os.environ.get("SITE_URL", "http://127.0.0.1:8766/")
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
problems = []
CLS = """window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"""

def leaving_at(pg):
    return pg.evaluate("""() => new Promise(res => { const l = document.getElementById('loader');
      const check = () => (!l || l.classList.contains('leaving')) ? res(Math.round(performance.now())) : requestAnimationFrame(check); check(); })""")

def gone_at(pg):
    """ms after navigation start at which the loader left the DOM."""
    return pg.evaluate("""() => new Promise(res => {
      const check = () => document.getElementById('loader') ? requestAnimationFrame(check) : res(Math.round(performance.now()));
      check(); })""")

with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme in ("light", "dark"):
        for (w, h) in ((1440, 900), (390, 844), (320, 640), (768, 1024)):
            ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
            ctx.add_init_script(CLS)
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda ex: errs.append(str(ex)))
            pg.goto(URL, wait_until="domcontentloaded")
            first = pg.evaluate("""() => { const l = document.getElementById('loader');
                const r = l && l.getBoundingClientRect(); const cs = l && getComputedStyle(l);
                const brand = l && l.querySelector('.ld-brand'); const br = brand && brand.getBoundingClientRect();
                return { present: !!l, covers: !!r && r.width >= innerWidth - 0.5 && r.height >= innerHeight - 0.5, bg: cs && cs.backgroundColor,
                         page: getComputedStyle(document.body).backgroundColor, text: brand && brand.textContent.replace(/\\u00a0/g,' '),
                         brandFits: !!br && br.left >= 0 && br.right <= innerWidth, loading: document.documentElement.classList.contains('is-loading') }; }""")
            tag = f"{scheme} {w}x{h}"
            if not first["present"] or not first["covers"]: problems.append(f"{tag}: loader not covering at first frame")
            if first["bg"] != first["page"]: problems.append(f"{tag}: loader bg {first['bg']} != page {first['page']}")
            if first["text"] != "Jessie - Physiotherapist": problems.append(f"{tag}: brand {first['text']!r}")
            if not first["brandFits"]: problems.append(f"{tag}: brand overflows")
            if w in (1440, 390) and scheme == "light":
                pg.wait_for_timeout(450); pg.screenshot(path=str(OUT / f"loader-{w}.png"))
            t0 = leaving_at(pg); t = gone_at(pg)
            pg.wait_for_timeout(1600)
            after = pg.evaluate("""() => { const x = innerWidth / 2, y = innerHeight / 2; const el = document.elementFromPoint(x, y);
                return { cls: Math.round(window.__cls * 10000) / 10000, loading: document.documentElement.classList.contains('is-loading'),
                         overflow: getComputedStyle(document.documentElement).overflow, busy: document.getElementById('main').getAttribute('aria-busy'),
                         topEl: el ? el.tagName + '.' + el.className : '', heroVisible: getComputedStyle(document.querySelector('.hero h1 .line > span')).transform };}""")
            if after["loading"] or after["overflow"] == "hidden": problems.append(f"{tag}: page still locked")
            if after["busy"]: problems.append(f"{tag}: aria-busy left on")
            if after["cls"] > 0.05: problems.append(f"{tag}: layout shift {after['cls']}")
            if errs: problems.append(f"{tag}: errors {errs}")
            print(f"{tag}: first frame ok={first['covers']} bg={first['bg']} | lifts at {t0} ms, gone at {t} ms | CLS {after['cls']} | centre element {after['topEl'][:40]}")
            if w == 1440 and scheme == "light":
                pg.screenshot(path=str(OUT / "revealed-1440.png"))
                # repeat visit in the same session: no minimum hold
                pg.reload(wait_until="domcontentloaded"); t1 = leaving_at(pg); t2 = gone_at(pg); print(f"  repeat visit: lifts at {t1} ms, gone at {t2} ms")
                # buttons clickable right after reveal
                pg.wait_for_timeout(100)
                pg.click(".nav-links a[href='#contact']"); pg.wait_for_timeout(2600)
                y = pg.evaluate("Math.round(document.getElementById('contact').getBoundingClientRect().top)")
                print("  nav click after reveal -> contact top at", y)
                if abs(y) > 140: problems.append("nav link did not scroll to contact")
            ctx.close()

    # mid-animation frames for the review
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded")
    for i, ms in enumerate((120, 300, 550)):
        pg.wait_for_timeout(ms - (0 if i == 0 else (120, 300)[i - 1])); pg.screenshot(path=str(OUT / f"seq-{ms}.png"))
    ctx.close()

    # reduced motion
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce"); pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded")
    anim = pg.evaluate("getComputedStyle(document.querySelector('.ld-shank')).animationName")
    t = gone_at(pg); print(f"reduced motion: shank animation={anim!r}, gone at {t} ms")
    if anim not in ("none", ""): problems.append("reduced motion still animates the figure")
    ctx.close()

    # JavaScript disabled: loader must not block the page
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, java_script_enabled=False); pg = ctx.new_page()
    pg.goto(URL)
    vis = pg.locator("#loader").is_visible(); print("no-JS: loader visible =", vis)
    if vis: problems.append("loader blocks page without JavaScript")
    pg.screenshot(path=str(OUT / "nojs.png")); ctx.close()

    # main script fails: inline failsafe must still lift it
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    def broken(route):
        resp = route.fetch(); body = resp.text().replace('"use strict";', 'throw new Error("simulated failure");', 1)
        route.fulfill(response=resp, body=body)
    pg.route(URL, broken)
    pg.goto(URL, wait_until="domcontentloaded"); pg.wait_for_timeout(4400)
    st = pg.evaluate("(()=>{const l=document.getElementById('loader');return l?getComputedStyle(l).visibility:'removed'})()")
    print("main script broken: loader after 4.4 s =", st)
    if st == "visible": problems.append("failsafe did not lift loader")
    ctx.close()
    b.close()

print("\nPROBLEMS:" if problems else "\nNo problems found.")
for x in problems: print(" -", x)
