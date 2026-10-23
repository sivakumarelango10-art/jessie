"""Regenerates the self-hosted fonts in src/assets/fonts from the Fontsource npm packages.

  npm i @fontsource-variable/bricolage-grotesque @fontsource-variable/plus-jakarta-sans @fontsource/ibm-plex-mono
  pip install fonttools brotli
  python3 scripts/make_fonts.py path/to/node_modules

Bricolage Grotesque keeps its weight (400-800) and width (75-100) axes; optical size is fixed at 60, which suits the
display sizes it is used at and halves the file. All three are subset to Latin, Latin-1 and the punctuation the site uses.
"""
import os, sys
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer

NM = sys.argv[1] if len(sys.argv) > 1 else "node_modules"
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "assets", "fonts")
UNI = "U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201D,U+2022,U+2026,U+2190-2193,U+2212,U+00B0"


def save_subset(font, name):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "tnum", "lnum", "case", "ccmp", "locl", "mark", "mkmk"]
    opts.name_IDs = ["*"]
    s = subset.Subsetter(opts)
    s.populate(unicodes=subset.parse_unicodes(UNI))
    s.subset(font)
    font.flavor = "woff2"
    path = os.path.join(OUT, name)
    font.save(path)
    print(f"{name}: {os.path.getsize(path) // 1024} KB")


os.makedirs(OUT, exist_ok=True)
b = TTFont(f"{NM}/@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-standard-normal.woff2")
save_subset(instancer.instantiateVariableFont(b, {"opsz": 60, "wght": (400, 800), "wdth": (75, 100)}), "bricolage-grotesque.woff2")
save_subset(TTFont(f"{NM}/@fontsource-variable/plus-jakarta-sans/files/plus-jakarta-sans-latin-wght-normal.woff2"), "plus-jakarta-sans.woff2")
save_subset(TTFont(f"{NM}/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2"), "ibm-plex-mono-500.woff2")
