#!/usr/bin/env python3
"""Digitize the measured coffee-temperature markers from the vector figures of
Sedlacek & Dolejsi, "A physical description of coffee cooling in a pot".

The PDF figures are vector drawings. Each measured point is a 2.4 pt square
marker (a 'qu' drawing item). Axis calibration uses the centres of the numeric
tick labels: a least-squares line maps label position to value. The residual of
that line is reported as the calibration error, and the scatter of the same
measurement across the five figures that show it is reported as the
cross-figure digitization check.

Outputs (under data/digitized/):
  fig{n}_points.csv      t_min, T_C per marker, plus the raw PDF coordinates
  calibration.json       axis fits, residuals, marker counts, exclusions
  china_digitized.csv    primary series (Fig. 1, the measured china-pot curve)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pymupdf
from loguru import logger

WORKSPACE = Path(__file__).resolve().parents[1]
PDF_PATH = WORKSPACE / "data" / "source" / "sedlacek_dolejsi.pdf"
OUT_DIR = WORKSPACE / "data" / "digitized"
LOG_DIR = WORKSPACE / "logs"

X_VALUES = [0, 20, 40, 60, 80, 100, 120, 140, 160]  # minutes
Y_VALUES = [20, 30, 40, 50, 60, 70, 80, 90]  # degrees Celsius
MARKER_SIDE_PT = 2.4
MARKER_TOL_PT = 0.05


@dataclass(frozen=True)
class FigureSpec:
    """Where one figure's markers, x tick labels and y tick labels sit on the page."""

    name: str
    page_index: int
    marker_box: tuple[float, float, float, float]  # x0, y0, x1, y1 in PDF points (top-left origin)
    xlabel_box: tuple[float, float, float, float]
    ylabel_box: tuple[float, float, float, float]
    exclude_boxes: tuple[tuple[float, float, float, float], ...] = ()
    expected_markers: int = 29
    # Tick labels to ignore. In Fig. 3 the printed "0" sits about 4 pt right of
    # its tick, while 20..160 are exactly linear; the first marker sits at t = 0.
    skip_x_values: tuple[int, ...] = ()


FIGURES: tuple[FigureSpec, ...] = (
    FigureSpec(
        name="fig1_china_measured",
        page_index=0,
        marker_box=(60, 560, 300, 672),
        xlabel_box=(60, 664, 300, 676),
        ylabel_box=(50, 566, 68, 664),
    ),
    FigureSpec(
        name="fig2_model1_vs_experiment",
        page_index=1,
        marker_box=(60, 140, 300, 250),
        xlabel_box=(60, 246, 300, 256),
        ylabel_box=(50, 150, 68, 250),
        exclude_boxes=((240, 150, 252, 162),),  # legend symbol
    ),
    FigureSpec(
        name="fig3_model2_vs_experiment",
        page_index=1,
        marker_box=(60, 540, 300, 640),
        xlabel_box=(60, 640, 300, 650),
        ylabel_box=(50, 544, 66, 642),
        exclude_boxes=((240, 546, 252, 557),),  # legend symbol
        skip_x_values=(0,),
    ),
    FigureSpec(
        name="fig4_model3_vs_experiment",
        page_index=1,
        marker_box=(320, 500, 560, 600),
        xlabel_box=(320, 596, 560, 606),
        ylabel_box=(314, 500, 332, 598),
        exclude_boxes=((503, 503, 515, 512),),  # legend symbol
    ),
    FigureSpec(
        name="fig5_model4_vs_experiment",
        page_index=2,
        marker_box=(60, 340, 300, 442),
        xlabel_box=(60, 441, 300, 450),
        ylabel_box=(50, 346, 68, 442),
        exclude_boxes=((240, 350, 252, 360),),  # legend symbol
    ),
)


def _numeric_words(page: pymupdf.Page, box: tuple[float, float, float, float], allowed: list[int]) -> list[tuple[float, float, int]]:
    """Return (centre_x, centre_y, value) for integer tick labels inside a box."""
    x0, y0, x1, y1 = box
    found = []
    for w in page.get_text("words"):
        cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
        if not (x0 <= cx <= x1 and y0 <= cy <= y1):
            continue
        token = w[4]
        if not token.isdigit():
            continue
        value = int(token)
        if value in allowed:
            found.append((cx, cy, value))
    return found


def _fit_axis(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    """Least-squares fit value = a * position + b. Returns (a, b, rms residual in value units)."""
    pos = np.array([p for p, _ in points], dtype=float)
    val = np.array([v for _, v in points], dtype=float)
    a, b = np.polyfit(pos, val, 1)
    resid = val - (a * pos + b)
    rms = float(np.sqrt(np.mean(resid**2)))
    return float(a), float(b), rms


def _in_box(x: float, y: float, box: tuple[float, float, float, float]) -> bool:
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]


def _extract_markers(page: pymupdf.Page, spec: FigureSpec) -> list[tuple[float, float]]:
    centres = []
    for drawing in page.get_drawings():
        items = drawing["items"]
        if len(items) != 1 or items[0][0] != "qu":
            continue
        rect = drawing["rect"]
        if abs(rect.width - MARKER_SIDE_PT) > MARKER_TOL_PT or abs(rect.height - MARKER_SIDE_PT) > MARKER_TOL_PT:
            continue
        cx, cy = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
        if not _in_box(cx, cy, spec.marker_box):
            continue
        if any(_in_box(cx, cy, ex) for ex in spec.exclude_boxes):
            continue
        centres.append((cx, cy))
    centres.sort(key=lambda p: p[0])
    return centres


def digitize_figure(doc: pymupdf.Document, spec: FigureSpec) -> dict:
    page = doc[spec.page_index]
    xlabels = [lab for lab in _numeric_words(page, spec.xlabel_box, X_VALUES) if lab[2] not in spec.skip_x_values]
    ylabels = _numeric_words(page, spec.ylabel_box, Y_VALUES)
    if len(xlabels) < 6 or len(ylabels) < 6:
        raise ValueError(f"{spec.name}: too few tick labels found (x={len(xlabels)}, y={len(ylabels)})")

    ax, bx, x_rms_pt = _fit_axis([(cx, v) for cx, _, v in xlabels])
    ay, by, y_rms_pt = _fit_axis([(cy, v) for _, cy, v in ylabels])

    markers = _extract_markers(page, spec)
    if len(markers) != spec.expected_markers:
        raise ValueError(
            f"{spec.name}: found {len(markers)} markers, expected {spec.expected_markers}"
        )

    rows = []
    for cx, cy in markers:
        t_min = ax * cx + bx
        temp_c = ay * cy + by
        rows.append({"t_min": t_min, "T_C": temp_c, "pdf_x": cx, "pdf_y": cy})

    # Calibration residual in the value units of the axes (minutes, degrees C).
    x_rms_min = x_rms_pt * abs(ax)
    y_rms_c = y_rms_pt * abs(ay)
    logger.info(
        f"{spec.name}: {len(rows)} markers, x-calib RMS {x_rms_min:.3f} min, y-calib RMS {y_rms_c:.3f} C, "
        f"x-scale {1/ax:.4f} pt/min, y-scale {1/ay:.4f} pt/C"
    )
    return {
        "name": spec.name,
        "page": spec.page_index + 1,
        "n_markers": len(rows),
        "x_calibration": {"min_per_pt": ax, "offset": bx, "label_rms_min": x_rms_min, "labels": len(xlabels)},
        "y_calibration": {"C_per_pt": ay, "offset": by, "label_rms_C": y_rms_c, "labels": len(ylabels)},
        "points": rows,
    }


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(LOG_DIR / "digitize.log", level="DEBUG")

    doc = pymupdf.open(PDF_PATH)
    results = {}
    try:
        for spec in FIGURES:
            results[spec.name] = digitize_figure(doc, spec)
    except (ValueError, RuntimeError) as exc:
        logger.error(f"Digitization failed: {exc}")
        raise

    # Write per-figure point files.
    for name, res in results.items():
        lines = ["t_min,T_C,pdf_x,pdf_y"]
        for p in res["points"]:
            lines.append(f"{p['t_min']:.4f},{p['T_C']:.4f},{p['pdf_x']:.3f},{p['pdf_y']:.3f}")
        (OUT_DIR / f"{name}_points.csv").write_text("\n".join(lines) + "\n")

    # Primary series = Fig. 1 (the measured china-pot curve, no model overlay).
    primary = results["fig1_china_measured"]["points"]
    china_lines = ["t_min,T_C"] + [f"{p['t_min']:.4f},{p['T_C']:.4f}" for p in primary]
    (OUT_DIR / "china_digitized.csv").write_text("\n".join(china_lines) + "\n")

    # Cross-figure check: for each other figure, compare to Fig. 1 by matching times.
    ref = np.array([[p["t_min"], p["T_C"]] for p in primary])
    cross = {}
    for name, res in results.items():
        if name == "fig1_china_measured":
            continue
        other = np.array([[p["t_min"], p["T_C"]] for p in res["points"]])
        dt, dT = [], []
        for t, T in other:
            i = int(np.argmin(np.abs(ref[:, 0] - t)))
            dt.append(t - ref[i, 0])
            dT.append(T - ref[i, 1])
        dt, dT = np.array(dt), np.array(dT)
        cross[name] = {
            "n": int(len(other)),
            "median_abs_dt_min": float(np.median(np.abs(dt))),
            "max_abs_dt_min": float(np.max(np.abs(dt))),
            "median_abs_dT_C": float(np.median(np.abs(dT))),
            "rms_dT_C": float(np.sqrt(np.mean(dT**2))),
            "max_abs_dT_C": float(np.max(np.abs(dT))),
        }
        logger.info(
            f"cross-check {name} vs fig1: median |dT| {cross[name]['median_abs_dT_C']:.3f} C, "
            f"RMS dT {cross[name]['rms_dT_C']:.3f} C, median |dt| {cross[name]['median_abs_dt_min']:.3f} min"
        )

    summary = {
        "source_pdf": str(PDF_PATH.relative_to(WORKSPACE)),
        "method": "vector marker centres (2.4 pt squares) mapped with least-squares fits to tick-label centres",
        "figures": {k: {kk: vv for kk, vv in v.items() if kk != "points"} for k, v in results.items()},
        "cross_figure_check_vs_fig1": cross,
    }
    (OUT_DIR / "calibration.json").write_text(json.dumps(summary, indent=2))
    logger.info("Wrote digitized outputs to data/digitized")


if __name__ == "__main__":
    main()
