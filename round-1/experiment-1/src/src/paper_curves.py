#!/usr/bin/env python3
"""Digitize the model curves that the source paper draws over its data.

The source reports chi2/NDF = 32.1, 2.4, 81.3 and 1.0 for its four models but
gives no residual table. Its plotted model curves are vector Bezier paths, so
they can be sampled and scored against the digitized measurements. This
separates two possible causes of a reproduction gap: the paper's fitted curves
differ from its own quoted statistics, or the digitized data differ from the
paper's data.

Outputs (under data/digitized/):
  paper_model_curves.csv   sampled (t_min, T_C) points for each drawn curve
  paper_curve_scores.json  RSS/NDF of each drawn curve against the digitized data
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
from loguru import logger

import digitize_figures as dg

WORKSPACE = dg.WORKSPACE
OUT_DIR = dg.OUT_DIR

# Model curve drawings per figure, identified by their bounding boxes on the page.
# Each entry: (figure spec name, paper model label, reported chi2/NDF, reported parameter count).
CURVE_SPECS = {
    "fig2_model1_vs_experiment": [("model 1", 32.1, 1, "Bezier 'cc' drawn in the model-1 panel")],
    "fig3_model2_vs_experiment": [
        ("model 1 (repeat)", 32.1, 1, "first 'cc' path in the Fig. 3 box"),
        ("model 2", 2.4, 2, "'ccc' path in the Fig. 3 box"),
    ],
    "fig4_model3_vs_experiment": [("model 3", 81.3, 6, "'cc' path in the Fig. 4 box")],
    "fig5_model4_vs_experiment": [("model 4", 1.0, 7, "'cc' path in the Fig. 5 box")],
}


def _bezier_points(segments: list[tuple], samples: int = 400) -> np.ndarray:
    """Sample a sequence of cubic Bezier segments (each with 4 control points) into a polyline."""
    out = []
    for seg in segments:
        p0, p1, p2, p3 = (np.array([q.x, q.y]) for q in seg)
        s = np.linspace(0.0, 1.0, samples)[:, None]
        pts = (1 - s) ** 3 * p0 + 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s**2 * p2 + s**3 * p3
        out.append(pts)
    return np.vstack(out)


def _curve_paths(page: pymupdf.Page, box: tuple[float, float, float, float]) -> list[list[tuple]]:
    """Return the Bezier segment lists of every multi-segment curve path inside a box."""
    x0, y0, x1, y1 = box
    paths = []
    for drawing in page.get_drawings():
        r = drawing["rect"]
        if not (r.x0 >= x0 and r.x1 <= x1 and r.y0 >= y0 and r.y1 <= y1):
            continue
        kinds = [it[0] for it in drawing["items"]]
        if not kinds or any(k != "c" for k in kinds):
            continue
        if r.width < 100:
            continue
        paths.append([tuple(it[1:]) for it in drawing["items"]])
    return paths


def _interp_curve(curve_t: np.ndarray, curve_T: np.ndarray, t_query: np.ndarray) -> np.ndarray:
    order = np.argsort(curve_t)
    return np.interp(t_query, curve_t[order], curve_T[order])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(WORKSPACE / "logs" / "paper_curves.log", level="DEBUG")

    doc = pymupdf.open(dg.PDF_PATH)
    data = pd.read_csv(OUT_DIR / "china_digitized.csv").sort_values("t_min")
    t_data = data["t_min"].to_numpy()
    T_data = data["T_C"].to_numpy()

    curve_rows = []
    scores = {}
    for spec in dg.FIGURES:
        if spec.name not in CURVE_SPECS:
            continue
        page = doc[spec.page_index]
        cal = dg.digitize_figure(doc, spec)  # re-derive the same axis calibration used for markers
        ax, bx = cal["x_calibration"]["min_per_pt"], cal["x_calibration"]["offset"]
        ay, by = cal["y_calibration"]["C_per_pt"], cal["y_calibration"]["offset"]

        paths = _curve_paths(page, spec.marker_box)
        logger.info(f"{spec.name}: {len(paths)} curve paths found")
        expected = CURVE_SPECS[spec.name]
        if len(paths) < len(expected):
            raise ValueError(f"{spec.name}: expected {len(expected)} curve paths, found {len(paths)}")

        for path_index, (label, reported, n_params, how) in enumerate(expected):
            # 'cc' in Fig. 3 is model 1 and 'ccc' is model 2; order the paths by segment count.
            candidates = sorted(paths, key=lambda p: len(p))
            path = candidates[path_index] if spec.name != "fig3_model2_vs_experiment" else (
                [p for p in paths if len(p) == 2][0] if path_index == 0 else [p for p in paths if len(p) == 3][0]
            )
            pts = _bezier_points(path)
            t_curve = ax * pts[:, 0] + bx
            T_curve = ay * pts[:, 1] + by
            pred = _interp_curve(t_curve, T_curve, t_data)
            resid = pred - T_data  # model minus data
            rss = float(np.sum(resid**2))
            ndf = len(t_data) - n_params
            scores[label] = {
                "figure": spec.name,
                "reported_chi2_per_ndf": reported,
                "n_params_reported_or_assumed": n_params,
                "digitized_rss_K2": rss,
                "digitized_rss_over_ndf_K2": rss / ndf,
                "ratio_to_reported": (rss / ndf) / reported,
                "curve_t_range_min": [float(t_curve.min()), float(t_curve.max())],
                "how_identified": how,
                "mean_residual_first_10min_K": float(resid[t_data < 10].mean()),
                "mean_residual_after_20min_K": float(resid[t_data >= 20].mean()),
            }
            logger.info(
                f"{label}: digitized RSS/NDF {rss / ndf:.2f} vs reported {reported} "
                f"(ratio {(rss / ndf) / reported:.2f}); curve t-range {t_curve.min():.1f}-{t_curve.max():.1f} min"
            )
            for t, T in zip(t_curve[::8], T_curve[::8]):
                curve_rows.append({"model": label, "figure": spec.name, "t_min": round(float(t), 4), "T_C": round(float(T), 4)})

    pd.DataFrame(curve_rows).to_csv(OUT_DIR / "paper_model_curves.csv", index=False)
    (OUT_DIR / "paper_curve_scores.json").write_text(json.dumps(scores, indent=2))
    logger.info("Wrote data/digitized/paper_curve_scores.json")


if __name__ == "__main__":
    main()
