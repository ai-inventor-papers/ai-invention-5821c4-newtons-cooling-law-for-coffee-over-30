"""Digitise Fig. 1 (china-pot coffee cooling) of Sedlacek & Dolejsi from vector markers in the PDF.

Calibration: centres of the tick-label text boxes (x: 0..160 min, y: 20..90 C).
Markers: small white-filled squares with a stroke, inside the plot area.
"""
import json
import sys
from pathlib import Path

import pymupdf

PDF = Path(sys.argv[1])
OUT = Path(sys.argv[2])
doc = pymupdf.open(PDF)
page = doc[0]
PLOT = pymupdf.Rect(60, 560, 300, 680)   # plot area incl. margin; legend box excluded below
FIG = pymupdf.Rect(40, 540, 310, 690)

spans = []
for b in page.get_text("dict", clip=FIG)["blocks"]:
    for ln in b.get("lines", []):
        for s in ln["spans"]:
            t = s["text"].strip()
            if t:
                spans.append((t, pymupdf.Rect(s["bbox"])))

def centre_of(label, pred):
    cands = [r for t, r in spans if t == label and pred(r)]
    if len(cands) != 1:
        raise SystemExit(f"calibration label {label!r}: {len(cands)} candidates")
    r = cands[0]
    return (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2

# x tick labels sit on one baseline (y ~ 670); y tick labels in one column (x ~ 60).
x_pts = {v: centre_of(v, lambda r: r.y0 > 665 and r.y0 < 675) for v in ["0", "20", "40", "60", "80", "100", "120", "140", "160"]}
y_pts = {v: centre_of(v, lambda r: r.x0 < 62 and r.x0 > 58 and r.y0 > 560) for v in ["20", "30", "40", "50", "60", "70", "80", "90"]}

def fit(pairs):
    n = len(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    rmax = max(abs(r) for r in resid)
    return a, b, rmax

ax, bx, rx = fit([(float(v), c[0]) for v, c in x_pts.items()])        # pdf x = ax + bx * minutes
ay, by, ry = fit([(float(v), c[1]) for v, c in y_pts.items()])  # pdf y = ay + by * temperature

markers = []
for d in page.get_drawings():
    r = d["rect"]
    if not PLOT.contains(r):
        continue
    w, h = r.width, r.height
    if 2.0 < w < 2.8 and 2.0 < h < 2.8 and d.get("fill") is not None:
        markers.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))

rows = []
for cx, cy in sorted(markers):
    t = (cx - ax) / bx
    T = (cy - ay) / by
    rows.append({"time_min": round(t, 2), "temp_C": round(T, 2), "marker_pdf_xy": [round(cx, 2), round(cy, 2)]})

report = {
    "pdf_sha256_note": "downloaded from ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf",
    "calibration_x": {"a_pt": round(ax, 4), "b_pt_per_min": round(bx, 5), "max_residual_pt": round(rx, 3), "labels": {k: round(v[0], 2) for k, v in x_pts.items()}},
    "calibration_y": {"a_pt": round(ay, 4), "b_pt_per_C": round(by, 5), "max_residual_pt": round(ry, 3), "labels": {k: round(v[1], 2) for k, v in y_pts.items()}},
    "n_markers": len(rows),
    "points": rows,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != "points"}, indent=2))
for r in rows:
    print(r["time_min"], r["temp_C"])
