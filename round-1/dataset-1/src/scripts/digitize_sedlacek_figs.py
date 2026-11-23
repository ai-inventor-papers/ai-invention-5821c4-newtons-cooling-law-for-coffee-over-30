"""Digitize measured-data markers from the vector figures of Sedlacek & Dolejsi (A physical description of coffee cooling in a pot).

The figures are vector graphics. Measured points are drawn as 2.4 x 2.4 pt square paths. Axis calibration uses the
centres of the numeric tick labels (time 0 and 160 on the x-axis; temperature 20 and 90 on the y-axis), taken from the
PDF text layer. Each figure's calibration is hard-coded from the text-layer coordinates printed by PyMuPDF.

Usage: python -I digitize_sedlacek_figs.py <sedlacek_ajp.pdf> <out.json>
"""
import json
import sys
from pathlib import Path

import pymupdf

# Figure calibration: page index (0-based); label-centre coordinates in PDF points.
# x0/x1 = centre of "0" and "160" tick labels; y20/y90 = centre of "20" and "90" tick labels.
FIGURES = [
    {"fig": "Fig. 1", "page": 0, "x0": 70.3, "x1": 291.6, "y20": 661.99, "y90": 573.8,
     "caption": "measured cooling of coffee in a china pot on a table"},
    {"fig": "Fig. 2", "page": 1, "x0": 70.8, "x1": 292.1, "y20": 245.25, "y90": 155.05,
     "caption": "time-dependent temperature from the experiment (second model figure)"},
    {"fig": "Fig. 3", "page": 1, "x0": 71.1, "x1": 292.2, "y20": 638.5, "y90": 549.7,
     "caption": "measured temperature and the both models"},
    {"fig": "Fig. 4", "page": 1, "x0": 332.85, "x1": 554.85, "y20": 593.0, "y90": 506.1,
     "caption": "measured temperature and the third model"},
    {"fig": "Fig. 5", "page": 2, "x0": 70.3, "x1": 292.3, "y20": 439.55, "y90": 353.6,
     "caption": "measured temperature and the fourth model"},
]

MARKER = 2.4
TOL = 0.25


def is_marker(rect):
    return abs(rect.width - MARKER) < TOL and abs(rect.height - MARKER) < TOL


def digitize(doc, fig):
    page = doc[fig["page"]]
    sx = 160.0 / (fig["x1"] - fig["x0"])
    pt_per_c = (fig["y20"] - fig["y90"]) / 70.0
    x_lo, x_hi = fig["x0"] - 3, fig["x1"] + 3
    y_hi, y_lo = fig["y20"] + 4, fig["y90"] - 4  # y increases downward in PDF space
    seen = set()
    pts = []
    for dr in page.get_drawings():
        r = dr["rect"]
        if not is_marker(r):
            continue
        cx = (r.x0 + r.x1) / 2
        cy = (r.y0 + r.y1) / 2
        if not (x_lo <= cx <= x_hi and y_lo <= cy <= y_hi):
            continue
        key = (round(cx, 2), round(cy, 2))
        if key in seen:  # each marker is drawn twice in the content stream
            continue
        seen.add(key)
        t_min = (cx - fig["x0"]) * sx
        temp_c = 20.0 + (fig["y20"] - cy) / pt_per_c
        pts.append({"time_min": round(t_min, 2), "temp_c": round(temp_c, 2)})
    pts.sort(key=lambda p: p["time_min"])
    return pts


def main() -> None:
    pdf_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    doc = pymupdf.open(str(pdf_path))
    result = {}
    for fig in FIGURES:
        pts = digitize(doc, fig)
        result[fig["fig"]] = {"caption": fig["caption"], "n_points": len(pts), "points": pts}
        print(fig["fig"], "points:", len(pts),
              "t range:", (pts[0]["time_min"], pts[-1]["time_min"]) if pts else None)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
