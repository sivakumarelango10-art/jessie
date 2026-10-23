"""Renders the built site at several widths and themes, saves screenshots and reports problems.

Usage: python3 scripts/check.py <out_dir>
Expects the site to be served at http://127.0.0.1:8765/
"""
import sys, json
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
URL = "http://127.0.0.1:8765/"
VIEWS = [("desktop", 1440, 900, "light"), ("tablet", 768, 1024, "light"), ("phone", 390, 844, "light"),
         ("desktop-dark", 1440, 900, "dark"), ("phone-dark", 390, 844, "dark")]

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, scheme in VIEWS:
        ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, device_scale_factor=1)
        pg = ctx.new_page()
        errors = []
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda ex: errors.append(str(ex)))
        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_timeout(3600)
        pg.screenshot(path=f"{OUT}/{name}-top.png")
        # scroll through so reveal observers fire, then full page
        total = pg.evaluate("document.documentElement.scrollHeight")
        y = 0
        while y < total:
            pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(120); y += h // 2
        pg.wait_for_timeout(1500)
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(600)
        pg.screenshot(path=f"{OUT}/{name}-full.png", full_page=True)
        info = pg.evaluate("""() => {
          const de = document.documentElement;
          const wide = [...document.querySelectorAll('body *')].filter(el => {
            const r = el.getBoundingClientRect(); return r.right > de.clientWidth + 1 && getComputedStyle(el).position !== 'fixed' && !el.closest('.tape-band') && !el.closest('.hero-visual') && !el.closest('.tape') && !el.classList.contains('tape') && !el.closest('.hero-glow');
          }).slice(0, 8).map(el => el.tagName + '.' + el.className + ' ' + Math.round(el.getBoundingClientRect().right));
          const h2s = [...document.querySelectorAll('h1, h2')].map(h => {
            const lh = parseFloat(getComputedStyle(h).lineHeight); return [h.textContent.trim().slice(0, 30), Math.round(h.getBoundingClientRect().height / lh)];
          });
          return { scrollW: de.scrollWidth, clientW: de.clientWidth, wide, lines: h2s,
                   pending: document.querySelectorAll('.reveal-pending:not(.revealed)').length,
                   fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v,i,a)=>a.indexOf(v)===i) };
        }""")
        print(name, json.dumps(info), "errors:", errors)
        ctx.close()
    b.close()
