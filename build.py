"""Builds Jessie's portfolio from src/ into two outputs:

  dist/site/      the static website (index.html + hashed, long-cached assets), deployed by Vercel
  dist/artifact/  a single self-contained page for the claude.ai preview

Run:  python3 build.py
Optional minification uses esbuild if it is installed (npm i -D esbuild, or set ESBUILD=/path/to/esbuild).
"""
import base64, hashlib, html, io, json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
import content as C  # noqa: E402
import markup as M  # noqa: E402

e = html.escape
TITLE = M.BRAND_NAME
DESCRIPTION = ("Jessie J. is a physiotherapist in Chennai specialising in sports and orthopaedic "
               "rehabilitation, post-operative recovery, neuro rehab and home-based care.")
RESUME = M.RESUME
FONT_FILES = {"FONT_DISPLAY": "bricolage-grotesque.woff2", "FONT_BODY": "plus-jakarta-sans.woff2", "FONT_LABELS": "ibm-plex-mono-500.woff2"}
PORTRAIT_WIDTHS = (480, 760, 1040)


# ---------------------------------------------------------------- helpers
def esbuild_bin():
    for cand in (os.environ.get("ESBUILD"), ROOT / "node_modules/.bin/esbuild", Path.home() / "tools/node_modules/.bin/esbuild"):
        if cand and Path(cand).exists():
            return str(cand)
    return None


def minify(code, loader):
    """Minify CSS/JS with esbuild when available; otherwise ship the readable source unchanged."""
    exe = esbuild_bin()
    if not exe:
        return code
    r = subprocess.run([exe, f"--loader={loader}", "--minify", "--target=es2019,chrome90,safari14,firefox90"],
                       input=code.encode(), capture_output=True)
    if r.returncode != 0:
        print("esbuild failed, using unminified", loader, r.stderr.decode()[:300])
        return code
    return r.stdout.decode().strip()


def hashed(out_dir, name, data):
    """Write data under a content-hashed filename so it can be cached for a year."""
    stem, ext = name.rsplit(".", 1)
    fname = f"{stem}.{hashlib.sha256(data).hexdigest()[:10]}.{ext}"
    (out_dir / fname).write_bytes(data)
    return f"assets/{fname}"


def portrait_variants():
    """Responsive AVIF + WebP renditions of the cut-out portrait."""
    from PIL import Image
    master = Image.open(SRC / "assets" / "jessie-portrait-master.webp").convert("RGB")
    out = {}
    for w in PORTRAIT_WIDTHS:
        im = master.resize((w, round(master.height * w / master.width)), Image.LANCZOS)
        for fmt, kw in (("avif", {"quality": 58}), ("webp", {"quality": 80, "method": 6})):
            buf = io.BytesIO(); im.save(buf, fmt.upper(), **kw)
            out[(w, fmt)] = buf.getvalue()
    return out


def make_og():
    """Link-preview image: porcelain card with the portrait in a rounded frame."""
    from PIL import Image, ImageDraw
    og = Image.new("RGB", (1200, 630), (244, 243, 239))
    d = ImageDraw.Draw(og)
    for x in range(0, 1200, 32): d.line([(x, 0), (x, 630)], fill=(232, 231, 226))
    for y in range(0, 630, 32): d.line([(0, y), (1200, y)], fill=(232, 231, 226))
    ph = Image.open(SRC / "assets" / "jessie-portrait-master.webp").convert("RGB")
    fw, fh = 440, 550                                   # frame, 4:5
    ph = ph.resize((fw, round(ph.height * fw / ph.width)), Image.LANCZOS).crop((0, 0, fw, fh))
    mask = Image.new("L", (fw, fh), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, fw - 1, fh - 1), radius=32, fill=255)
    og.paste(ph, (700, 40), mask)
    d.rounded_rectangle((60, 520, 520, 560), radius=20, fill=(36, 71, 223))
    d.rounded_rectangle((60, 70, 140, 150), radius=22, fill=(36, 71, 223))
    buf = io.BytesIO(); og.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
    return buf.getvalue()


# ---------------------------------------------------------------- build
def build():
    critical_src = (SRC / "critical.css").read_text()
    css = minify((SRC / "styles.css").read_text(), "css")
    js = minify((SRC / "main.js").read_text(), "js")
    loader_js = minify((SRC / "loader.js").read_text(), "js")
    stages = json.dumps([{k: s[k] for k in ("angle", "title", "text")} for s in C.STAGES], separators=(",", ":"))
    scripts = f"<script>window.STAGES={stages};</script>\n<script>{js}</script>"
    fonts = {k: (SRC / "assets" / "fonts" / v).read_bytes() for k, v in FONT_FILES.items()}
    variants = portrait_variants()

    def critical_with(urls):
        out = critical_src
        for k, u in urls.items():
            out = out.replace("{{" + k + "}}", u)
        return minify(out, "css")

    # Paint order: critical CSS (tokens, fonts, loader) -> loader + its progress script -> main CSS -> content.
    loader_block = M.loader(loader_js) + f"<style>{css}</style>\n"

    # ---------- deployable static site
    site = ROOT / "dist" / "site"
    if site.exists(): shutil.rmtree(site)
    assets = site / "assets"; assets.mkdir(parents=True)
    font_urls = {k: hashed(assets, FONT_FILES[k], data) for k, data in fonts.items()}
    pics = {(w, f): hashed(assets, f"jessie-{w}.{f}", data) for (w, f), data in variants.items()}
    photo = {
        "avif": ", ".join(f"{pics[(w, 'avif')]} {w}w" for w in PORTRAIT_WIDTHS),
        "webp": ", ".join(f"{pics[(w, 'webp')]} {w}w" for w in PORTRAIT_WIDTHS),
        "fallback": pics[(760, "webp")],
    }
    og_url = hashed(assets, "og.jpg", make_og())
    shutil.copy(SRC / "assets" / "Jessie-J-Resume-public.pdf", site / RESUME)
    person = {"@context": "https://schema.org", "@type": "Person", "name": "Jessie J.", "jobTitle": "Physiotherapist",
              "address": {"@type": "PostalAddress", "addressLocality": "Chennai", "addressCountry": "IN"},
              "alumniOf": "Saveetha College of Physiotherapy, SIMATS", "email": "mailto:" + C.PERSON["email"]}
    sizes = "(max-width: 960px) min(82vw, 420px), 500px"
    preloads = "".join(f'<link rel="preload" href="{u}" as="font" type="font/woff2" crossorigin>' for u in font_urls.values())
    preloads += (f'<link rel="preload" as="image" type="image/avif" imagesrcset="{photo["avif"]}" imagesizes="{sizes}" fetchpriority="high">')
    head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{e(DESCRIPTION)}">
<meta name="author" content="Jessie">
<meta name="theme-color" content="#2447df">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="profile">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{e(DESCRIPTION)}">
<meta property="og:image" content="{og_url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{M.FAVICON}">
{preloads}
<script type="application/ld+json">{json.dumps(person)}</script>
<style>{critical_with(font_urls)}</style>
</head>
<body>'''
    page = M.page("site", photo)
    (site / "index.html").write_text(head + loader_block + page + scripts + "\n</body>\n</html>\n")

    # ---------- single-file artifact (wrapped in a skeleton at publish time; everything inlined)
    art = ROOT / "dist" / "artifact"
    if art.exists(): shutil.rmtree(art)
    art.mkdir(parents=True)
    font_data = {k: "data:font/woff2;base64," + base64.b64encode(v).decode() for k, v in fonts.items()}
    photo_inline = "data:image/webp;base64," + base64.b64encode(variants[(760, "webp")]).decode()
    shutil.copy(SRC / "assets" / "Jessie-J-Resume-public.pdf", art / RESUME)
    art_head = (f'<title>{TITLE}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
                f'<meta name="description" content="{e(DESCRIPTION)}">\n<style>{critical_with(font_data)}</style>\n')
    (art / "index.html").write_text(art_head + loader_block + M.page("artifact", photo_inline) + scripts + "\n")

    kb = lambda p: round(p.stat().st_size / 1024, 1)
    print("built", site / "index.html", f"({kb(site / 'index.html')} KB)", "| minified:", bool(esbuild_bin()))
    for f in sorted(assets.iterdir()): print("  ", f.name, kb(f), "KB")
    print("artifact", kb(art / "index.html"), "KB")


if __name__ == "__main__":
    build()
