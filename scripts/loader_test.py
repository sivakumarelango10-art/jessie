"""Loading-screen tests for the real-progress loader.

Records, every animation frame, the displayed number, the bar width and the measured target, then checks:
starts at 0, never goes backwards, number == bar, display never ahead of measured progress, 100% only after
every task closed, page unlocked and clickable afterwards. Runs normal, slow network, failed portrait,
blocked fonts, broken main script, reduced motion, no JavaScript, and several screen sizes.

Usage: SITE_URL=http://127.0.0.1:8767/dist/site/ python3 scripts/loader_test.py <screenshot-dir>
"""
import os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = os.environ.get("SITE_URL", "http://127.0.0.1:8766/")
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
problems = []

RECORDER = """
window.__rec = [];
(function poll() {
  const l = document.getElementById('loader');
  if (l) {
    const b = l.querySelector('.ld-pct b'), bar = l.querySelector('.ld-bar i');
    const m = bar && /scaleX\\(([\\d.]+)\\)/.exec(bar.style.transform || '');
    const st = window.PortfolioLoader ? window.PortfolioLoader.state() : null;
    window.__rec.push({ t: Math.round(performance.now()), text: b ? +b.textContent : null, bar: m ? +m[1] * 100 : 0,
                  target: st ? st.target : null, pending: st ? st.pending.length : null, leaving: l.classList.contains('leaving'),
                  status: (l.querySelector('.ld-status') || {}).textContent });
  }
  if (!window.__done) requestAnimationFrame(poll);
})();
"""

def run(b, name, *, w=1440, h=900, scheme="light", throttle=None, route=None, reduced=False, check_click=False, shot=None):
    ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, reduced_motion="reduce" if reduced else "no-preference")
    ctx.add_init_script(RECORDER)
    ctx.add_init_script("window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda ex: errs.append(str(ex)))
    if throttle:
        cdp = ctx.new_cdp_session(pg); cdp.send("Network.enable"); cdp.send("Network.emulateNetworkConditions", throttle)
    for pattern, handler in (route or []): pg.route(pattern, handler)
    pg.goto(URL, wait_until="commit", timeout=90000)
    if shot:
        import base64
        cdp2 = ctx.new_cdp_session(pg)
        for ms in shot:  # raw CDP capture: Playwright's screenshot() would wait for web fonts and arrive late
            pg.wait_for_function(f"document.getElementById('loader') && performance.now() > {ms}", timeout=60000, polling=50)
            label = pg.evaluate("(document.querySelector('.ld-pct b')||{}).textContent")
            data = cdp2.send("Page.captureScreenshot", {"format": "png"})["data"]
            (OUT / f"{name}-{ms}.png").write_bytes(base64.b64decode(data)); print(f"   frame {ms} ms: {label}%")
    pg.wait_for_function("!document.getElementById('loader')", timeout=60000, polling=100)
    pg.wait_for_timeout(300)
    rec = pg.evaluate("window.__done = true, window.__rec")
    st_log = pg.evaluate("window.PortfolioLoader ? window.PortfolioLoader.state().log : []")
    after = pg.evaluate("""() => ({ locked: document.documentElement.classList.contains('is-loading') || getComputedStyle(document.documentElement).overflow === 'hidden',
        busy: document.getElementById('main').getAttribute('aria-busy'),
        cls: Math.round(window.__cls * 10000) / 10000, photoFailed: !!document.querySelector('.photo-card.photo-failed') })""")
    tag = name
    texts = [r["text"] for r in rec if r["text"] is not None]
    if not texts: problems.append(f"{tag}: loader never seen"); ctx.close(); return
    if texts[0] != 0: problems.append(f"{tag}: first value {texts[0]} not 0")
    if any(y < x for x, y in zip(texts, texts[1:])): problems.append(f"{tag}: number went backwards")
    for r in rec:
        if r["text"] is not None and abs(r["bar"] - r["text"]) >= 1.01:
            problems.append(f"{tag}: bar {r['bar']:.1f} vs number {r['text']} at {r['t']}ms"); break
    for r in rec:
        if r["target"] is not None and r["text"] is not None and r["text"] > r["target"]:
            problems.append(f"{tag}: display {r['text']} ahead of measured {r['target']}"); break
    hundred = [r for r in rec if r["text"] == 100]
    if hundred and hundred[0]["pending"]: problems.append(f"{tag}: showed 100% with {hundred[0]['pending']} tasks pending")
    if after["locked"] or after["busy"]: problems.append(f"{tag}: page still locked/busy after loader")
    if errs and "simulated" not in " ".join(errs): problems.append(f"{tag}: page errors {errs}")
    leave = next((r["t"] for r in rec if r["leaving"]), None)
    hit100 = hundred[0]["t"] if hundred else None
    print(f"\n{tag}: loader visible from {rec[0]['t']} ms | 100% at {hit100} ms | lifts {leave} ms | "
          f"{len(set(texts))} distinct values | CLS {after['cls']}" + (" | portrait fallback used" if after["photoFailed"] else ""))
    msgs = []
    for r in rec:
        if r["status"] and (not msgs or msgs[-1] != r["status"]): msgs.append(r["status"])
    print("   status:", " → ".join(msgs))
    print("   measured:", ", ".join(f"{e['target']}%@{e['t']}({e['key'].split(':')[-1]}{' FAILED' if e['failed'] else ''})" for e in st_log))
    if check_click:
        pg.click(".nav-links a[href='#contact']"); pg.wait_for_timeout(2600)
        y = pg.evaluate("Math.round(document.getElementById('contact').getBoundingClientRect().top)")
        if abs(y) > 140: problems.append(f"{tag}: nav link after load did not reach contact ({y})")
        else: print("   nav click after load: reached Contact")
    ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    run(b, "normal-1440-light", check_click=True, shot=(150,))
    run(b, "slow-network", throttle={"offline": False, "latency": 400, "downloadThroughput": 50 * 1024, "uploadThroughput": 20 * 1024},
        shot=(1500, 3500, 6000))
    def abort(route): route.abort()
    run(b, "portrait-fails", route=[("**/assets/jessie-*", abort)])
    run(b, "fonts-blocked", route=[("https://fonts.googleapis.com/**", abort), ("https://fonts.gstatic.com/**", abort)])
    def broken(route):
        resp = route.fetch()
        head, tail = resp.text().rsplit("<script>", 1)   # the last script is main.js
        route.fulfill(response=resp, body=head + '<script>throw new Error("simulated");' + tail)
    run(b, "main-script-broken", route=[(URL, broken)])
    run(b, "reduced-motion", reduced=True)
    for (w, h, sc) in ((390, 844, "dark"), (320, 640, "light"), (768, 1024, "dark")):
        run(b, f"size-{w}-{sc}", w=w, h=h, scheme=sc, shot=(250,))

    pg = b.new_page(viewport={"width": 320, "height": 640})
    pg.goto(URL, wait_until="domcontentloaded")
    fit = pg.evaluate("""() => { const l = document.getElementById('loader'); if (!l) return null;
        const r = s => l.querySelector(s).getBoundingClientRect();
        return { brand: [Math.round(r('.ld-brand').left), Math.round(r('.ld-brand').right)], bar: [Math.round(r('.ld-bar').left), Math.round(r('.ld-bar').right)],
                 pct: Math.round(r('.ld-pct').right), vw: innerWidth }; }""")
    print("\n320px layout:", fit)
    if fit and (fit["brand"][0] < 0 or fit["brand"][1] > fit["vw"] or fit["bar"][1] > fit["vw"] or fit["pct"] > fit["vw"]): problems.append("320px: loader overflows")
    pg.close()

    ctx = b.new_context(java_script_enabled=False); pg = ctx.new_page(); pg.goto(URL)
    vis = pg.locator("#loader").is_visible(); print("no JavaScript: loader visible =", vis)
    if vis: problems.append("loader shown without JavaScript")
    ctx.close(); b.close()

print("\nPROBLEMS:" if problems else "\nNo problems found.")
for x in problems: print(" -", x)
