"""Merge Latin glyphs from Nunito (SIL OFL 1.1, (c) 2014 The Nunito Project Authors,
https://github.com/googlefonts/nunito) into the built TTFs.
Usage: python3 build_latin.py path/to/Nunito[wght].ttf   (run after build_ttf.py)"""
import sys
from fontTools.merge import Merger
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.varLib import instancer
from fontTools import subset

WANT = (list(range(0x21, 0x7F)) + list(range(0xA1, 0x100)) +
        [0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x20AC])
DIGITS = set(range(0x30, 0x3A))   # use Nunito digits so mixed text matches

for style, wght in (("Regular", 400), ("Bold", 700)):
    path = f"dist/ttf/ThaanaNoor-{style}.ttf"
    base = TTFont(path)
    for t in base["cmap"].tables:
        for u in DIGITS: t.cmap.pop(u, None)
    base.save("/tmp/_base.ttf")
    have = set(TTFont("/tmp/_base.ttf").getBestCmap())
    n = instancer.instantiateVariableFont(TTFont(sys.argv[1]), {"wght": wght})
    scale_upem(n, 2048)
    o = subset.Options(); o.layout_features = ["kern", "liga"]; o.drop_tables += ["DSIG", "STAT"]
    s = subset.Subsetter(o); s.populate(unicodes=[u for u in WANT if u not in have]); s.subset(n)
    n.save("/tmp/_latin.ttf")
    f = Merger().merge(["/tmp/_base.ttf", "/tmp/_latin.ttf"])
    f["OS/2"].fsType = 0
    f.save(path)
    f.flavor = "woff2"; f.save(f"dist/webfonts/ThaanaNoor-{style}.woff2")
