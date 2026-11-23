"""Digitize the cooling curves of Abb. 2 (237 mL single-use cups) in Langer, Winkler & Lachenmeier (2018),
Z. Lebensm. Unters. Forsch. / DLR Lebensmittel-Forschung... (Zenodo record 1402983, CC-BY 4.0).

The figure is vector graphics: each cup's inner-temperature curve is one long polyline. Each polyline is
identified by its stroke colour and dash pattern. The legend in the figure gives the cup categories, but the
mapping of line styles to legend entries is NOT established here, so curves are identified by style id only.

Axis calibration uses the centres of the numeric tick labels in the PDF text layer:
x: "0" and "20" minutes; y: "20" and "90" degrees C (the y label centres are on the same page).

Usage: python -I digitize_langer_abb2.py <langer2018.pdf> <out.json>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pymupdf

PAGE_INDEX = 3  # page 4 of the PDF, Abb. 2
# Calibration from text-layer label centres (PDF points)
X0_CENTRE = (77.3 + 81.6) / 2     # "0" min
X20_CENTRE = (172.3 + 180.8) / 2  # "20" min
Y20_CENTRE = (721.8 + 732.3) / 2  # "20" C
Y90_CENTRE = (521.2 + 531.7) / 2  # "90" C
REGION = (76.0, 520.0, 250.0, 732.0)  # x0, y0, x1, y1 of the Abb. 2 plot area
MIN_ITEMS = 1000


def style_key(dr):
    col = tuple(round(c, 2) for c in (dr.get("color") or ()))
    dash = str(dr.get("dashes") or "")
    return (col, dash)


def polyline_points(dr):
    pts = []
    for it in dr["items"]:
        if it[0] != "l":
            continue
        p1, p2 = it[1], it[2]
        if not pts:
            pts.append((p1.x, p1.y))
        pts.append((p2.x, p2.y))
    return np.array(pts)


def to_units(pts):
    minutes = (pts[:, 0] - X0_CENTRE) / ((X20_CENTRE - X0_CENTRE) / 20.0)
    pt_per_c = (Y20_CENTRE - Y90_CENTRE) / 70.0
    temp = 20.0 + (Y20_CENTRE - pts[:, 1]) / pt_per_c
    return minutes, temp


def main() -> None:
    doc = pymupdf.open(sys.argv[1])
    page = doc[PAGE_INDEX]
    x0, y0, x1, y1 = REGION
    chosen = {}
    for dr in page.get_drawings():
        if len(dr["items"]) < MIN_ITEMS:
            continue
        r = dr["rect"]
        if not (r.x0 >= x0 - 1 and r.x1 <= x1 + 1 and r.y0 >= y0 - 1 and r.y1 <= y1 + 1):
            continue
        key = style_key(dr)
        if key not in chosen or len(dr["items"]) > len(chosen[key]["items"]):
            chosen[key] = dr

    grid = np.arange(0.0, 33.0 + 1e-9, 1.0)  # 1-min grid, covers the 20-min minimum with margin
    curves = []
    for idx, (key, dr) in enumerate(sorted(chosen.items(), key=lambda kv: str(kv[0]))):
        pts = polyline_points(dr)
        minutes, temp = to_units(pts)
        order = np.argsort(minutes)
        minutes, temp = minutes[order], temp[order]
        valid = (minutes >= 0) & (minutes <= 33.5)
        if valid.sum() < 2:
            continue
        m, t = minutes[valid], temp[valid]
        sampled = np.interp(grid, m, t, left=np.nan, right=np.nan)
        ok = ~np.isnan(sampled)
        curves.append({
            "style_id": f"Abb2-style-{idx + 1:02d}",
            "stroke_colour_rgb": list(key[0]),
            "dash_pattern": key[1],
            "n_vertices": int(len(pts)),
            "time_min": [float(x) for x in grid[ok]],
            "temp_c": [round(float(x), 2) for x in sampled[ok]],
            "t_range_min": [float(m.min()), float(m.max())],
        })
    out = {
        "figure": "Abb. 2 (single-use cups, 237 mL)",
        "n_curves": len(curves),
        "curves": curves,
    }
    Path(sys.argv[2]).write_text(json.dumps(out, indent=2), encoding="utf-8")
    for c in curves:
        print(c["style_id"], "vertices", c["n_vertices"], "t_range", [round(v, 2) for v in c["t_range_min"]],
              "T start/end", c["temp_c"][0], c["temp_c"][-1])


if __name__ == "__main__":
    main()
