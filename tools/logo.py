#!/usr/bin/env python3
"""Draws the Shabakah logo on a square Kufic grid.

The full mark spells شبكة in square Kufic: the three teeth of ش and the tooth
of ب on one baseline, the tall stem of ك with its arm, and the closed loop of
ة. Stroke and gap are one grid unit each, so the letters read as a network of
equal links. The small mark is ش alone, for favicons and tight spaces.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE = "#0033A0"

# Rows top to bottom, columns left to right. X is ink.
WORD = [
    ".XXXX.....X..",
    "....X........",
    "X.X.X....X.X.",
    "....X........",
    "XXX.X.X.X.X.X",
    "X.X.X.X.X.X.X",
    "XXXXXXXXXXXXX",
    ".............",
    "......X......",
]

SHEEN = [
    "..X..",
    ".....",
    ".X.X.",
    ".....",
    "X.X.X",
    "X.X.X",
    "XXXXX",
]


def path(grid, unit=10, ox=0, oy=0):
    """One path of horizontal runs, so shapes join without hairline seams."""
    d = []
    for r, row in enumerate(grid):
        c = 0
        while c < len(row):
            if row[c] == "X":
                start = c
                while c < len(row) and row[c] == "X":
                    c += 1
                x, y, w = ox + start * unit, oy + r * unit, (c - start) * unit
                d.append("M%g %gh%gv%gh-%gz" % (x, y, w, unit, w))
            else:
                c += 1
    return "".join(d)


def svg(grid, unit=10, pad=0, color=BLUE, extra=""):
    w = len(grid[0]) * unit + pad * 2
    h = len(grid) * unit + pad * 2
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g"%s><path fill="%s" d="%s"/></svg>'
            % (w, h, extra, color, path(grid, unit, pad, pad)))


def favicon():
    # ش in white on the project blue, centred on a 32 unit tile.
    unit = 3.4
    gw, gh = len(SHEEN[0]) * unit, len(SHEEN) * unit
    ox, oy = (32 - gw) / 2, (32 - gh) / 2
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="%s"/>'
            '<path fill="#fff" d="%s"/></svg>' % (BLUE, path(SHEEN, unit, ox, oy)))


def inline_word(height_attr=True):
    """The word mark for inline use in the page header (aria hidden)."""
    return svg(WORD, extra=' aria-hidden="true" class="mark"')


def main():
    out = os.path.join(ROOT, "docs")
    open(os.path.join(out, "logo.svg"), "w").write(svg(WORD) + "\n")
    open(os.path.join(out, "logo-mark.svg"), "w").write(svg(SHEEN) + "\n")
    open(os.path.join(out, "favicon.svg"), "w").write(favicon() + "\n")
    print("wrote docs/logo.svg, docs/logo-mark.svg, docs/favicon.svg")


if __name__ == "__main__":
    main()
