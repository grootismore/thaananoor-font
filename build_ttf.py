"""Convert the OTF/CFF masters to TrueType, set open embedding, add invisible format characters."""
import sys
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph

def convert(src, dst):
    f = TTFont(src)
    order = f.getGlyphOrder(); gs = f.getGlyphSet()
    glyf = newTable("glyf"); glyf.glyphOrder = order; glyf.glyphs = {}
    for n in order:
        pen = TTGlyphPen(gs); gs[n].draw(Cu2QuPen(pen, 1.0, reverse_direction=True)); glyf.glyphs[n] = pen.glyph()
    f["glyf"] = glyf; f["loca"] = newTable("loca")
    del f["CFF "]; f.sfntVersion = "\x00\x01\x00\x00"
    if "VORG" in f: del f["VORG"]
    maxp = f["maxp"]; maxp.tableVersion = 0x00010000
    for a in ("maxZones","maxTwilightPoints","maxStorage","maxFunctionDefs","maxInstructionDefs","maxStackElements","maxSizeOfInstructions","maxComponentElements"): setattr(maxp, a, 0)
    maxp.maxZones = 1; maxp.maxComponentDepth = 0
    f["head"].glyphDataFormat = 0
    f["post"].formatType = 2.0; f["post"].extraNames = []; f["post"].mapping = {}; f["post"].glyphOrder = order
    # invisible characters
    cmap = {c: n for c, n in f.getBestCmap().items()}
    new = {"nbspace": (0xA0, f["hmtx"][cmap[0x20]][0]), "zwnj": (0x200C, 0), "zwj": (0x200D, 0), "lrm": (0x200E, 0), "rlm": (0x200F, 0)}
    for name, (cp, w) in new.items():
        order.append(name); glyf.glyphs[name] = Glyph(); f["hmtx"][name] = (w, 0)
        for t in f["cmap"].tables:
            if t.isUnicode(): t.cmap[cp] = name
    glyf.glyphOrder = order; f.setGlyphOrder(order); maxp.numGlyphs = len(order)
    f["OS/2"].fsType = 0           # installable embedding: free to embed in apps/websites
    f["hhea"].numberOfHMetrics = len(order)
    f.save(dst)
    w = TTFont(dst); w.flavor = "woff2"; w.save(dst.replace("/ttf/","/webfonts/").replace(".ttf", ".woff2"))

if __name__ == "__main__":
    for st in ("Regular", "Bold"):
        convert(f"src_masters/ThaanaNoor-{st}.otf", f"dist/ttf/ThaanaNoor-{st}.ttf")
