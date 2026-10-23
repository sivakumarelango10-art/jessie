"""Builds Jessie J.'s portfolio from src/ into two outputs:

  dist/site/      a standard static website (index.html + assets) ready to deploy anywhere
  dist/artifact/  a single self-contained page for publishing as a claude.ai artifact

Run:  python3 build.py
"""
import base64, html, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
import content as C  # noqa: E402
import markup as M  # noqa: E402

e = html.escape
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800"
         "&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap")
TITLE = M.BRAND_NAME
DESCRIPTION = ("Jessie J. is a physiotherapist in Chennai specialising in sports and orthopaedic "
               "rehabilitation, post-operative recovery, neuro rehab and home-based care.")
RESUME = M.RESUME


def build():
    css = (SRC / "styles.css").read_text()
    js = (SRC / "main.js").read_text()
    stages = json.dumps([{k: s[k] for k in ("angle", "title", "text")} for s in C.STAGES])
    scripts = f"<script>window.STAGES={stages};</script>\n<script>\n{js}\n</script>"
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             f'<link rel="stylesheet" href="{FONTS}">')

    # --- deployable static site
    site = ROOT / "dist" / "site"
    if site.exists(): shutil.rmtree(site)
    (site / "assets").mkdir(parents=True)
    shutil.copy(SRC / "assets" / "jessie-cutout.webp", site / "assets" / "jessie.webp")
    shutil.copy(SRC / "assets" / "Jessie-J-Resume-public.pdf", site / RESUME)
    make_og(site / "assets" / "og.jpg")
    person = {"@context": "https://schema.org", "@type": "Person", "name": "Jessie J.", "jobTitle": "Physiotherapist",
              "address": {"@type": "PostalAddress", "addressLocality": "Chennai", "addressCountry": "IN"},
              "alumniOf": "Saveetha College of Physiotherapy, SIMATS", "email": "mailto:" + C.PERSON["email"]}
    head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{e(DESCRIPTION)}">
<meta name="author" content="Jessie">
<meta name="theme-color" content="#2447df">
<meta property="og:type" content="profile">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{e(DESCRIPTION)}">
<meta property="og:image" content="assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{M.FAVICON}">
<link rel="preload" as="image" href="assets/jessie.webp">
{fonts}
<script type="application/ld+json">{json.dumps(person)}</script>
<style>
{css}
</style>
</head>
<body>'''
    (site / "index.html").write_text(head + M.page("site", "assets/jessie.webp") + scripts + "\n</body>\n</html>\n")

    # --- single-file artifact (wrapped in a skeleton at publish time)
    art = ROOT / "dist" / "artifact"
    if art.exists(): shutil.rmtree(art)
    art.mkdir(parents=True)
    photo = "data:image/webp;base64," + base64.b64encode((SRC / "assets" / "jessie-cutout.webp").read_bytes()).decode()
    shutil.copy(SRC / "assets" / "Jessie-J-Resume-public.pdf", art / RESUME)
    art_head = (f'<title>{TITLE}</title>\n'
                f'<meta name="claude:viewport-fit-sides" content="cover">\n'
                f'<meta name="description" content="{e(DESCRIPTION)}">\n{fonts}\n<style>\n{css}\n</style>\n')
    (art / "index.html").write_text(art_head + M.page("artifact", photo) + scripts + "\n")
    print("built", site / "index.html", art / "index.html")


def make_og(path):
    """Link-preview image: porcelain card with the portrait on a tape-blue panel."""
    from PIL import Image, ImageDraw
    og = Image.new("RGB", (1200, 630), (244, 243, 239))
    d = ImageDraw.Draw(og)
    for x in range(0, 1200, 32): d.line([(x, 0), (x, 630)], fill=(232, 231, 226))
    for y in range(0, 630, 32): d.line([(0, y), (1200, y)], fill=(232, 231, 226))
    d.rounded_rectangle((690, 40, 1160, 670), radius=36, fill=(229, 234, 249))
    ph = Image.open(SRC / "assets" / "jessie-cutout.webp").convert("RGBA")
    ph = ph.resize((470, int(ph.height * 470 / ph.width)))
    og.paste(ph, (690, 630 - ph.height + 30), ph)
    d.rounded_rectangle((60, 520, 520, 560), radius=20, fill=(36, 71, 223))
    d.rounded_rectangle((60, 70, 140, 150), radius=22, fill=(36, 71, 223))
    og.save(path, quality=86)


if __name__ == "__main__":
    build()
