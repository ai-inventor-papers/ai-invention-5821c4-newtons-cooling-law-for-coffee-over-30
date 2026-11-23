#!/usr/bin/env python3
"""Independent re-derivation of the headline numbers, with placebo checks.

This script does not import digitize_figures, paper_curves, models or analysis.
It works from the raw PDF and from raw arrays by a different path:

  * raw data: 2.4 pt marker squares and tick-label words read directly from the
    PDF with pymupdf, calibrated by a hand-written least-squares fit;
  * ODE solutions by explicit fixed-step RK4 (not the closed form, not solve_ivp);
  * fits by grid search and Nelder-Mead on the RK4 solutions (not least_squares);
  * the published model-1 curve by de Casteljau subdivision of the raw Bezier
    control points (not the Bernstein sampling used in paper_curves.py).

Placebo checks, which must FAIL to reject:
  * C0 against C0 under the block bootstrap of the RMS difference: the interval
    must contain zero;
  * time-permuted temperatures: refitting both models on permuted data must give
    a relative RMS improvement that the real data's improvement exceeds (p <= 0.05).

Writes results/audit.json and prints a comparison with results/analysis_results.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pymupdf
from loguru import logger
from scipy.optimize import minimize

WORKSPACE = Path(__file__).resolve().parents[1]
PDF = WORKSPACE / "data" / "source" / "sedlacek_dolejsi.pdf"
RESULTS = WORKSPACE / "results"
T_ROOM = 20.0
WINDOW = 30.0
TOL_RMS = 0.02  # K, tolerance between independent and original RMS values
RNG = np.random.default_rng(99)


def tick_fit(page, words_box, values, axis: str) -> tuple[float, float]:
    """Least-squares axis fit from tick-label word centres, written independently."""
    x0, y0, x1, y1 = words_box
    pos, val = [], []
    for w in page.get_text("words"):
        cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1 and w[4].isdigit() and int(w[4]) in values:
            pos.append(cx if axis == "x" else cy)
            val.append(int(w[4]))
    A = np.vstack([pos, np.ones(len(pos))]).T
    slope, intercept = np.linalg.lstsq(A, np.array(val, float), rcond=None)[0]
    return float(slope), float(intercept)


def read_fig1_points() -> np.ndarray:
    doc = pymupdf.open(PDF)
    page = doc[0]
    ax, bx = tick_fit(page, (60, 664, 300, 676), [0, 20, 40, 60, 80, 100, 120, 140, 160], "x")
    ay, by = tick_fit(page, (50, 566, 68, 664), [20, 30, 40, 50, 60, 70, 80, 90], "y")
    pts = []
    for d in page.get_drawings():
        r = d["rect"]
        if len(d["items"]) == 1 and d["items"][0][0] == "qu" and abs(r.width - 2.4) < 0.05 and abs(r.height - 2.4) < 0.05:
            cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
            if 60 <= cx <= 300 and 560 <= cy <= 672:
                pts.append((ax * cx + bx, ay * cy + by))
    arr = np.array(sorted(pts))
    arr[:, 0] -= arr[0, 0]  # first marker at t = 0
    return arr


def rk4(rhs, t_eval: np.ndarray, T0: float, dt: float = 0.01) -> np.ndarray:
    out = np.empty_like(t_eval, dtype=float)
    T = T0
    t = 0.0
    for i, te in enumerate(t_eval):
        while t < te - 1e-12:
            h = min(dt, te - t)
            k1 = rhs(T)
            k2 = rhs(T + 0.5 * h * k1)
            k3 = rhs(T + 0.5 * h * k2)
            k4 = rhs(T + h * k3)
            T += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t += h
        out[i] = T
    return out


def c0_path(p, t, T0):
    a = p[0]
    return rk4(lambda T: -a * (T - T_ROOM), t, T0)


def c1_path(p, t, T0):
    a, x = p
    return rk4(lambda T: -a * max(T - T_ROOM, 0.0) ** x, t, T0)


def fit_nm(fun, starts):
    best = None
    for s in starts:
        r = minimize(fun, s, method="Nelder-Mead", options={"xatol": 1e-8, "fatol": 1e-10, "maxiter": 4000})
        if best is None or r.fun < best.fun:
            best = r
    return best


def rms(res: np.ndarray) -> float:
    return float(np.sqrt(np.mean(res**2)))


def block_diff_ci(res_a, res_b, blocks, reps=2000):
    """Interval for RMS(b) - RMS(a) by resampling whole blocks of the same time indices."""
    diffs = np.empty(reps)
    nb = len(blocks)
    for r in range(reps):
        pick = RNG.integers(0, nb, nb)
        idx = np.concatenate([blocks[j] for j in pick])
        diffs[r] = rms(res_b[idx]) - rms(res_a[idx])
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi)


def debezier(points: np.ndarray, t: float) -> np.ndarray:
    """de Casteljau evaluation of one cubic Bezier segment at parameter t."""
    p = points.copy()
    for level in range(1, 4):
        p = (1 - t) * p[:-1] + t * p[1:]
    return p[0]


def published_fig2_curve() -> np.ndarray:
    doc = pymupdf.open(PDF)
    page = doc[1]
    ax, bx = tick_fit(page, (60, 246, 300, 256), [0, 20, 40, 60, 80, 100, 120, 140, 160], "x")
    ay, by = tick_fit(page, (50, 150, 68, 250), [20, 30, 40, 50, 60, 70, 80, 90], "y")
    segs = None
    for d in page.get_drawings():
        r = d["rect"]
        kinds = "".join(it[0] for it in d["items"])
        if kinds == "cc" and 60 <= r.x0 and r.x1 <= 300 and 140 <= r.y0 and r.y1 <= 250 and r.width > 100:
            segs = [np.array([[q.x, q.y] for q in it[1:]]) for it in d["items"]]
            break
    if segs is None:
        raise RuntimeError("model-1 Bezier path not found on page 2")
    curve = []
    for seg in segs:
        for s in np.linspace(0, 1, 400):
            curve.append(debezier(seg, s))
    curve = np.array(curve)
    t = ax * curve[:, 0] + bx
    T = ay * curve[:, 1] + by
    return np.column_stack([t, T])


def main() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    data = read_fig1_points()
    t, T = data[:, 0], data[:, 1]
    T0 = T[0]
    logger.info(f"Independent read: {len(t)} markers, t {t[0]:.2f}..{t[-1]:.2f}, T0 {T0:.2f}")

    w = t <= WINDOW + 1e-9
    tw, Tw = t[w], T[w]
    logger.info(f"window points: {w.sum()}")

    # C0 on the window: grid then refine
    grid = np.linspace(1e-4, 0.1, 2000)
    losses = [np.sum((c0_path([a], tw, T0) - Tw) ** 2) for a in grid]
    a_grid = grid[int(np.argmin(losses))]
    c0 = fit_nm(lambda p: np.sum((c0_path(p, tw, T0) - Tw) ** 2) if p[0] > 0 else 1e9, [[a_grid]])
    res_c0 = c0_path(c0.x, tw, T0) - Tw
    c0_rms = rms(res_c0)

    # C1 on the window
    starts = [[0.0007, 1.9], [0.001, 1.5], [0.0003, 2.2], [0.003, 1.2]]
    c1 = fit_nm(lambda p: np.sum((c1_path(p, tw, T0) - Tw) ** 2) if (p[0] > 0 and 0.3 < p[1] < 3) else 1e9, starts)
    res_c1 = c1_path(c1.x, tw, T0) - Tw
    c1_rms = rms(res_c1)

    # Published model-1 curve on the window, by de Casteljau
    pub = published_fig2_curve()
    # Same origin as the data: subtract the raw time of the first marker.
    raw_t0 = read_first_raw_time()
    pub_t = pub[:, 0] - raw_t0
    order = np.argsort(pub_t)
    pub_on_w = np.interp(tw, pub_t[order], pub[order, 1])
    res_pub = pub_on_w - Tw
    pub_rms = rms(res_pub)

    # Block bootstrap over 5-minute blocks of the window
    bins = np.floor(tw / 5.0).astype(int)
    blocks = [np.where(bins == b)[0] for b in np.unique(bins)]
    real_lo, real_hi = block_diff_ci(res_c0, res_c1, blocks)
    # Placebo 1: C0 against C0 must include zero
    p1_lo, p1_hi = block_diff_ci(res_c0, res_c0, blocks)
    # Placebo 2: permute the measured temperatures across the window's time points, refit C0 and
    # C1 on the permuted data, and record the relative RMS improvement. The real improvement must
    # exceed nearly all permuted ones (permutation p-value below 0.05).
    real_improvement = 1 - c1_rms / c0_rms
    n_perm = 100
    perm_improvements = []
    for _ in range(n_perm):
        Tp = RNG.permutation(Tw)
        f0 = fit_nm(lambda p: np.sum((c0_path(p, tw, T0) - Tp) ** 2) if p[0] > 0 else 1e9, [[c0.x[0]]])
        f1 = fit_nm(lambda p: np.sum((c1_path(p, tw, T0) - Tp) ** 2) if (p[0] > 0 and 0.3 < p[1] < 3) else 1e9, starts)
        r0 = rms(c0_path(f0.x, tw, T0) - Tp)
        r1 = rms(c1_path(f1.x, tw, T0) - Tp)
        perm_improvements.append(1 - r1 / r0)
    perm_improvements = np.array(perm_improvements)
    perm_p = float((np.sum(perm_improvements >= real_improvement) + 1) / (n_perm + 1))
    placebo_false_reject = perm_p
    logger.info(f"permutation placebo: real improvement {real_improvement:.3f}, permuted median {np.median(perm_improvements):.3f}, p={perm_p:.3f}")

    result = {
        "independent_read": {
            "n_markers": int(len(t)),
            "n_window": int(w.sum()),
            "first_marker_raw_time_min": float(raw_t0),
        },
        "C0_rms_30min_K": c0_rms,
        "C0_fit_a_per_min": float(c0.x[0]),
        "C1_rms_30min_K": c1_rms,
        "C1_fit_a_x": [float(c1.x[0]), float(c1.x[1])],
        "published_model1_rms_30min_K": pub_rms,
        "C1_minus_C0_block_ci95": [real_lo, real_hi],
        "placebo_C0_vs_C0_ci95": [p1_lo, p1_hi],
        "real_relative_rms_improvement_C1_over_C0": real_improvement,
        "placebo_permuted_time_improvement_median": float(np.median(perm_improvements)),
        "placebo_permuted_time_improvement_max": float(np.max(perm_improvements)),
        "placebo_permutation_p_value": perm_p,
        "placebo_n_permutations": n_perm,
        "placebo_pass": bool(p1_lo <= 0 <= p1_hi and perm_p <= 0.05),
    }

    orig = json.loads((RESULTS / "analysis_results.json").read_text())
    orig_c = orig["candidates_30min_window"]
    comparison = {
        "C0_rms": {"independent": c0_rms, "original": orig_c["C0"]["rms_30min_K"], "agree": abs(c0_rms - orig_c["C0"]["rms_30min_K"]) < TOL_RMS},
        "C1_rms": {"independent": c1_rms, "original": orig_c["C1"]["rms_30min_K"], "agree": abs(c1_rms - orig_c["C1"]["rms_30min_K"]) < TOL_RMS},
        "published_rms": {"independent": pub_rms, "original": orig_c["published_model1_curve"]["rms_30min_K"], "agree": abs(pub_rms - orig_c["published_model1_curve"]["rms_30min_K"]) < TOL_RMS},
    }
    result["comparison_with_original"] = comparison
    result["all_headline_agree"] = all(v["agree"] for v in comparison.values())
    (RESULTS / "audit.json").write_text(json.dumps(result, indent=2))
    logger.info(json.dumps(comparison, indent=1))
    logger.info(f"placebo_pass={result['placebo_pass']} permutation p={perm_p:.3f} C0-vs-C0 CI [{p1_lo:.3f}, {p1_hi:.3f}]")
    logger.info(f"C1-C0 CI (independent) [{real_lo:.3f}, {real_hi:.3f}]")


def read_first_raw_time() -> float:
    """Raw (uncorrected) time of the first marker on the Fig. 1 calibration."""
    page = pymupdf.open(PDF)[0]
    ax, bx = tick_fit(page, (60, 664, 300, 676), [0, 20, 40, 60, 80, 100, 120, 140, 160], "x")
    xs = []
    for d in page.get_drawings():
        r = d["rect"]
        if len(d["items"]) == 1 and d["items"][0][0] == "qu" and abs(r.width - 2.4) < 0.05 and abs(r.height - 2.4) < 0.05:
            cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
            if 60 <= cx <= 300 and 560 <= cy <= 672:
                xs.append(cx)
    return float(ax * min(xs) + bx)


if __name__ == "__main__":
    main()
