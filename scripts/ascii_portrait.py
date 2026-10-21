"""Turns a background-removed portrait (RGBA PNG) into ASCII rows.

    python scripts/ascii_portrait.py <cutout.png> assets/portrait.txt [cols]

Only the resulting characters are committed; the photo itself never is.
"""
import sys

import numpy as np
from PIL import Image, ImageFilter, ImageOps

RAMP = " .,:;+*?%S#@"
CHAR_ASPECT = 0.55  # glyph width / line height


def convert(path, cols=72):
    im = Image.open(path).convert("RGBA")
    alpha = np.asarray(im.split()[3], dtype=np.float32) / 255
    import cv2
    g = np.asarray(ImageOps.grayscale(im.convert("RGB")), dtype=np.uint8)
    g = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(6, 6)).apply(g)
    lum = g.astype(np.float32) / 255
    inside = lum[alpha > .5]
    lo, hi = np.percentile(inside, 3), np.percentile(inside, 93)
    lum = np.clip((lum - lo) / (hi - lo + 1e-6), 0, 1) ** 0.85
    core = cv2.erode((alpha > .5).astype(np.uint8), np.ones((15, 15), np.uint8))
    edges = cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 40, 110).astype(np.float32) / 255 * core
    rows = int(cols * im.height / im.width * CHAR_ASPECT)
    cw, ch = im.width / cols, im.height / rows
    out = []
    for r in range(rows):
        line = []
        for c in range(cols):
            y0, y1 = int(r * ch), int((r + 1) * ch)
            x0, x1 = int(c * cw), int((c + 1) * cw)
            a = alpha[y0:y1, x0:x1].mean()
            if a < 0.35:
                line.append(" ")
                continue
            v = lum[y0:y1, x0:x1].mean()
            e = edges[y0:y1, x0:x1].mean()
            # keep dark hair/clothes visible as a textured silhouette
            v = 0.08 + 0.92 * min(1.0, v + e * 1.5)
            line.append(RAMP[min(len(RAMP) - 1, max(1, int(v * (len(RAMP) - 1) + 0.5)))])
        out.append("".join(line).rstrip())
    while out and not out[-1].strip():
        out.pop()
    return out


if __name__ == "__main__":
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 72
    rows = convert(sys.argv[1], cols)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    print(f"{len(rows)} rows x {cols} cols")
