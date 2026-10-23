"""Functional + responsive audit of the built site. Serve dist/site on port 8766 first.

Usage: python3 scripts/audit.py <screenshot-dir>
"""
import hashlib, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

import os
URL = os.environ.get("SITE_URL", "http://127.0.0.1:8766/")
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SRC_PDF = Path(__file__).resolve().parent.parent / "dist/site/Jessie_Physiotherapist_Resume.pdf"
problems = []

MEASURE = """() => {
  const de = document.documentElement, vw = de.clientWidth;
  const shell = document.querySelector('.nav-shell').getBoundingClientRect();
  const brand = document.querySelector('.site-header .brand');
  const visible = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'; };
  const kids = [...document.querySelectorAll('.nav-shell > *')].filter(visible).map(el => el.getBoundingClientRect());
  let overlap = false;
  for (let i = 1; i < kids.length; i++) if (kids[i].left < kids[i-1].right - 1) overlap = true;
  const btns = [...document.querySelectorAll('main .btn-resume, .site-header .btn-resume')].filter(visible).map(b => {
    const r = b.getBoundingClientRect(), cs = getComputedStyle(b), ic = b.querySelector('svg').getBoundingClientRect();
    return { text: b.textContent.trim(), h: Math.round(r.height), font: cs.fontSize + ' ' + cs.fontWeight, radius: cs.borderRadius,
             pad: cs.paddingLeft, bg: cs.backgroundColor, icon: Math.round(ic.width) + 'x' + Math.round(ic.height),
             iconCentred: Math.abs((ic.top + ic.bottom) / 2 - (r.top + r.bottom) / 2) < 1.5 };
  });
  const clipped = [...document.querySelectorAll('h1,h2,h3,h4,p,a,button,span,li,dd,dt')].filter(el => {
    if (!visible(el) || el.closest('.tape-band') || el.closest('[aria-hidden="true"]')) return false;
    const cs = getComputedStyle(el); if (cs.overflow === 'visible' && cs.textOverflow !== 'ellipsis') return false;
    return el.scrollWidth > el.clientWidth + 1 && cs.overflowX !== 'auto';
  }).slice(0, 5).map(el => el.tagName + '.' + el.className);
  return { docW: de.scrollWidth, vw, brandText: brand.textContent.trim(), brandVisible: visible(brand),
           shellOverflow: Math.round(shell.right) > vw || document.querySelector('.nav-shell').scrollWidth > document.querySelector('.nav-shell').clientWidth + 1,
           overlap, btns, clipped, title: document.title };
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme in ("light", "dark"):
        for w in (320, 360, 390, 430, 600, 680, 768, 1024, 1180, 1220, 1280, 1440, 1920):
            ctx = b.new_context(viewport={"width": w, "height": 900}, color_scheme=scheme)
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda ex: errs.append(str(ex)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.goto(URL, wait_until="networkidle"); pg.wait_for_selector("#loader", state="detached", timeout=5000)
            m = pg.evaluate(MEASURE)
            tag = f"{scheme} {w}px"
            if m["docW"] > m["vw"]: problems.append(f"{tag}: horizontal overflow {m['docW']}")
            if m["brandText"] != "Jessie - Physiotherapist": problems.append(f"{tag}: brand text {m['brandText']!r}")
            if not m["brandVisible"]: problems.append(f"{tag}: brand hidden")
            if m["shellOverflow"] or m["overlap"]: problems.append(f"{tag}: header overflow/overlap")
            if m["title"] != "Jessie - Physiotherapist": problems.append(f"{tag}: title {m['title']!r}")
            if m["clipped"]: problems.append(f"{tag}: clipped {m['clipped']}")
            sig = {(x["text"], x["h"], x["font"], x["radius"], x["pad"], x["bg"], x["icon"]) for x in m["btns"]}
            if len(sig) > 1: problems.append(f"{tag}: résumé buttons differ {sig}")
            if any(not x["iconCentred"] for x in m["btns"]): problems.append(f"{tag}: icon not centred")
            if errs: problems.append(f"{tag}: console {errs}")
            if w in (320, 390, 768, 1280) :
                pg.screenshot(path=str(OUT / f"{scheme}-{w}-header.png"), clip={"x": 0, "y": 0, "width": w, "height": 110})
            print(tag, "buttons:", len(m["btns"]), sorted(sig)[0] if sig else "-", "| overflow" if m["shellOverflow"] else "")
            ctx.close()

    # ---- the real download, from every résumé button (desktop + mobile menu)
    expected = hashlib.sha256(SRC_PDF.read_bytes()).hexdigest()
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, accept_downloads=True); pg = ctx.new_page()
    pg.goto(URL); pg.wait_for_selector("#loader", state="detached", timeout=5000)
    n = pg.locator(".btn-resume").count()
    for i in range(n):
        loc = pg.locator(".btn-resume").nth(i)
        if not loc.is_visible(): continue
        loc.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
        with pg.expect_download() as dl:
            loc.click()
        d = dl.value; path = OUT / f"dl-{i}.pdf"; d.save_as(path)
        ok = hashlib.sha256(path.read_bytes()).hexdigest() == expected and path.read_bytes()[:5] == b"%PDF-"
        print(f"download #{i}: {d.suggested_filename} {path.stat().st_size} bytes, matches résumé: {ok}")
        if not ok or d.suggested_filename != "Jessie_Physiotherapist_Resume.pdf": problems.append(f"download #{i} wrong")
    ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, accept_downloads=True); pg = ctx.new_page()
    pg.goto(URL); pg.wait_for_selector("#loader", state="detached", timeout=5000); pg.click(".menu-btn"); pg.wait_for_timeout(800)
    pg.screenshot(path=str(OUT / "menu-390.png"))
    with pg.expect_download() as dl:
        pg.click(".mobile-menu .btn-resume")
    print("mobile menu download:", dl.value.suggested_filename)

    # ---- every link and control
    pg = b.new_page(viewport={"width": 1440, "height": 900}); pg.goto(URL); pg.wait_for_selector("#loader", state="detached", timeout=5000)
    links = pg.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
    missing = [h for h in links if h.startswith("#") and len(h) > 1 and not pg.query_selector(h)]
    external = sorted({h for h in links if not h.startswith("#")})
    print("in-page anchors broken:", missing, "| other links:", external)
    if missing: problems.append(f"broken anchors {missing}")
    for h in external:
        if h.endswith(".pdf"):
            r = pg.request.get(URL + h); print(h, r.status, r.headers.get("content-type"))
            if r.status != 200: problems.append(f"{h} -> {r.status}")
    pg.click("#tab-educate"); pg.wait_for_timeout(900)
    print("dial ->", pg.inner_text("#stage-panel h3"))
    pg.click('.care[data-area="ortho"] .title'); print("body map ortho markers:", pg.locator(".body-map .mk.on").count())
    pg.click(".job summary"); print("details open:", pg.eval_on_selector(".job details", "d => d.open"))
    pg.reload(); pg.wait_for_selector("#loader", state="detached", timeout=5000); pg.keyboard.press("Tab")
    print("first tab stop after load:", pg.evaluate("document.activeElement.textContent.trim()"))
    b.close()

print("\nPROBLEMS:" if problems else "\nNo problems found.")
for x in problems: print(" -", x)
