#!/usr/bin/env python3
"""Screen cooling models on the digitized china-pot coffee curve.

Pipeline
  1. Load the digitized china curve (Fig. 1 markers) and the digitization
     cross-check written by digitize_figures.py.
  2. Benchmark reproduction (gate): reproduce the source's chi2/NDF for its
     models 1 and 2 by refitting, and score the source's own drawn curves for
     all four models against the digitized data.
  3. Candidate fits on the first 30 minutes (primary window): C0 baseline,
     C1 one-term nonlinear convection, C2 convection plus evaporation (plan
     form, plus a fixed-exponent variant for the fallback F4), and C2p (source
     evaporation form, descriptive). C3 and C4 are recorded as not testable.
  4. Metrics: chi2/NDF (sigma 0.3 C and the source's unit-sigma convention),
     30-minute RMS in kelvin, residual series (model minus data), early versus
     late mean residual, AIC and BIC.
  5. Uncertainty: block bootstrap over 5-minute time blocks inside the window
     (residual resampling, no refit), 2000 repeats.
  6. Sensitivity: ambient temperature free for C0 and C1; forecast check
     (fit to 15 min, score 15-30 min).
  7. Selection rule: applied only if the reproduction gate passes. Otherwise a
     descriptive ranking is written and labelled as not selected.

Writes results/method_out.json and results/analysis_tables.csv.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from scipy.optimize import least_squares

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "src"))

from models import T_ROOM_DEFAULT_C, c0_closed_form, integrate  # noqa: E402

DIGI = WORKSPACE / "data" / "digitized"
RESULTS = WORKSPACE / "results"
LOGS = WORKSPACE / "logs"

WINDOW_MIN = 30.0
SIGMA_MEAS_C = 0.3
BOOT_REPS = 2000
BLOCK_MIN = 5.0
RNG_SEED = 20260523
GATE_TOL = 0.30
T_ROOM = T_ROOM_DEFAULT_C
RMS_EFFECT_THRESHOLD = 0.25  # relative RMS improvement over C0 required by the selection rule


def load_china() -> tuple[np.ndarray, np.ndarray, float]:
    df = pd.read_csv(DIGI / "china_digitized.csv").sort_values("t_min").reset_index(drop=True)
    t = df["t_min"].to_numpy(dtype=float)
    T = df["T_C"].to_numpy(dtype=float)
    # The time axis calibration puts the first marker at -0.3 min. The measurement starts
    # at t = 0, so shift the series to start there (documented in the README).
    shift = t[0]
    t = t - shift
    return t, T, shift


def fit_c0(t: np.ndarray, T: np.ndarray, t0: float, t_room: float) -> dict:
    res = least_squares(lambda p: c0_closed_form(t, t0, p[0], t_room) - T, x0=[0.02], bounds=([1e-6], [2.0]), x_scale="jac")
    return {"params": {"a_per_min": float(res.x[0]), "t_room_C": float(t_room)}, "n_params": 1, "at_bounds": bool(np.any(np.isclose(res.x, [1e-6, 2.0])))}


def _multi_start(kind: str, starts: list[list[float]], lb: list[float], ub: list[float], t: np.ndarray, T: np.ndarray, t0: float, t_room: float) -> tuple[np.ndarray, float]:
    best = None
    for s in starts:
        def resid(p, _s=s):
            return integrate(kind, tuple(p), t, t0, t_room) - T
        try:
            r = least_squares(resid, x0=s, bounds=(lb, ub), x_scale="jac", max_nfev=2000)
        except (RuntimeError, ValueError) as exc:
            logger.debug(f"{kind} start {s} failed: {exc}")
            continue
        if best is None or r.cost < best.cost:
            best = r
    if best is None:
        raise RuntimeError(f"all starts failed for {kind}")
    return best.x, float(np.sum(best.fun**2))


def fit_c1(t, T, t0, t_room, free_room: bool = False) -> dict:
    starts = [[0.01, 1.0], [0.03, 1.3], [0.02, 1.6], [0.005, 1.2]]
    lb, ub = [1e-6, 0.3], [5.0, 3.0]
    if free_room:
        def resid(p):
            return integrate("C1", (p[0], p[1]), t, t0, p[2]) - T
        best = None
        for s in starts:
            r = least_squares(resid, x0=[s[0], s[1], t_room], bounds=([1e-6, 0.3, 0.0], [5.0, 3.0, 30.0]), x_scale="jac")
            if best is None or r.cost < best.cost:
                best = r
        params = {"a_per_min": float(best.x[0]), "x": float(best.x[1]), "t_room_C": float(best.x[2])}
        rss = float(np.sum(best.fun**2))
        at_b = bool(np.isclose(best.x[1], 0.3) or np.isclose(best.x[1], 3.0))
        return {"params": params, "rss": rss, "n_params": 3, "at_bounds": at_b}
    x, rss = _multi_start("C1", starts, lb, ub, t, T, t0, t_room)
    at_b = bool(np.isclose(x[1], 0.3) or np.isclose(x[1], 3.0) or np.isclose(x[0], 1e-6))
    return {"params": {"a_per_min": float(x[0]), "x": float(x[1]), "t_room_C": float(t_room)}, "rss": rss, "n_params": 2, "at_bounds": at_b}


def fit_c2(t, T, t0, t_room, kind: str = "C2", fix_x: float | None = None) -> dict:
    """Convection plus evaporation. Parameters (a, x, log b, z); b is log-parameterized because b*T^z is tiny."""
    z_starts = [3.0, 3.73, 4.5]
    lb = [1e-6, 0.5, -40.0, 1.0]
    ub = [5.0, 3.0, 2.0, 6.0]
    starts = [[a0, x0, lb0, z0] for a0 in [0.01, 0.03] for x0 in [1.0, 1.34] for lb0 in [-18.0, -20.0] for z0 in z_starts]
    if fix_x is not None:
        lb[1] = fix_x - 1e-9
        ub[1] = fix_x + 1e-9
        starts = [[s[0], fix_x, s[2], s[3]] for s in starts]
    best = None
    for s in starts:
        def resid(p, _kind=kind):
            pp = (p[0], p[1], float(np.exp(p[2])), p[3])
            return integrate(_kind, pp, t, t0, t_room) - T
        try:
            r = least_squares(resid, x0=s, bounds=(lb, ub), x_scale="jac", max_nfev=1500)
        except (RuntimeError, ValueError) as exc:
            logger.debug(f"{kind} start {s} failed: {exc}")
            continue
        if best is None or r.cost < best.cost:
            best = r
    if best is None:
        raise RuntimeError(f"all starts failed for {kind}")
    p = best.x
    params = {"a_per_min": float(p[0]), "x": float(p[1]), "b_evap": float(np.exp(p[2])), "z": float(p[3]), "t_room_C": float(t_room)}
    at_b = bool(np.isclose(p[0], 1e-6) or np.isclose(p[1], lb[1]) or np.isclose(p[1], ub[1]) or np.isclose(p[2], lb[2]) or np.isclose(p[2], ub[2]) or np.isclose(p[3], 1.0) or np.isclose(p[3], 6.0))
    n_params = 3 if fix_x is not None else 4
    return {"params": params, "rss": float(np.sum(best.fun**2)), "n_params": n_params, "at_bounds": at_b, "fixed_x": fix_x}


def predict_candidate(name: str, fit: dict, t: np.ndarray, t0: float, t_room: float) -> np.ndarray:
    p = fit["params"]
    if name == "C0":
        return c0_closed_form(t, t0, p["a_per_min"], p["t_room_C"])
    if name == "C1":
        return integrate("C1", (p["a_per_min"], p["x"]), t, t0, p["t_room_C"])
    if name in ("C2", "C2p", "C2_fixed_x"):
        kind = "C2p" if name == "C2p" else "C2"
        return integrate(kind, (p["a_per_min"], p["x"], p["b_evap"], p["z"]), t, t0, p["t_room_C"])
    raise ValueError(name)


def metrics(resid: np.ndarray, n_params: int, sigma: float) -> dict:
    n = len(resid)
    rss = float(np.sum(resid**2))
    ndf = max(n - n_params, 1)
    return {
        "n_points": n,
        "n_params": n_params,
        "rms_K": float(np.sqrt(np.mean(resid**2))),
        "chi2_sigma_0p3_per_ndf": float(np.sum((resid / sigma) ** 2) / ndf),
        "rss_per_ndf_K2_sourceConvention": float(rss / ndf),
        "AIC": float(n * np.log(rss / n) + 2 * n_params),
        "BIC": float(n * np.log(rss / n) + n_params * np.log(n)),
    }


def block_bootstrap(residual_sets: dict[str, np.ndarray], blocks: list[np.ndarray], reps: int, rng: np.random.Generator) -> dict:
    """Resample whole 5-minute blocks of residuals (no refit) and recompute RMS per model.

    Returns intervals for each model's RMS and for each model's RMS minus the baseline C0.
    """
    nb = len(blocks)
    rms_draws = {k: np.empty(reps) for k in residual_sets}
    for r in range(reps):
        pick = rng.integers(0, nb, size=nb)
        idx = np.concatenate([blocks[i] for i in pick])
        for k, res in residual_sets.items():
            rms_draws[k][r] = np.sqrt(np.mean(res[idx] ** 2))
    out = {}
    for k in residual_sets:
        lo, hi = np.percentile(rms_draws[k], [2.5, 97.5])
        out[k] = {"rms_K_ci95": [float(lo), float(hi)], "rms_K_boot_mean": float(rms_draws[k].mean())}
    base = rms_draws["C0"]
    for k in residual_sets:
        if k == "C0":
            continue
        d = rms_draws[k] - base
        lo, hi = np.percentile(d, [2.5, 97.5])
        out[k]["rms_minus_C0_ci95"] = [float(lo), float(hi)]
        out[k]["rms_minus_C0_excludes_zero"] = bool(lo > 0 or hi < 0)
        out[k]["relative_rms_improvement_vs_C0_point"] = float(1 - np.sqrt(np.mean(residual_sets[k] ** 2)) / np.sqrt(np.mean(residual_sets["C0"] ** 2)))
    return out


def load_paper_curve_scores() -> dict:
    return json.loads((DIGI / "paper_curve_scores.json").read_text())


def paper_curve_rms(t_win: np.ndarray, T_win: np.ndarray, shift: float) -> dict[str, np.ndarray]:
    """Residuals of the source's drawn model-1 curve (Fig. 2) over the window.

    The drawn curve was calibrated with the same axis fit as the markers, so it
    carries the same time offset; subtract the measured-series shift so both share t = 0 at the first marker.
    """
    cv = pd.read_csv(DIGI / "paper_model_curves.csv")
    g = cv[cv["model"] == "model 1"].sort_values("t_min")
    pred = np.interp(t_win, g["t_min"].to_numpy() - shift, g["T_C"].to_numpy())
    return {"published_model1_curve": pred - T_win}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(LOGS / "analysis.log", level="DEBUG")

    t_all, T_all, shift = load_china()
    t0 = float(T_all[0])
    logger.info(f"Loaded {len(t_all)} china points, t from {t_all[0]:.2f} to {t_all[-1]:.2f} min; T0 = {t0:.2f} C; time shift {shift:.3f} min")

    cross = json.loads((DIGI / "calibration.json").read_text())["cross_figure_check_vs_fig1"]
    digi_err_C = float(np.median([v["rms_dT_C"] for v in cross.values()]))
    logger.info(f"Median across-figure RMS disagreement {digi_err_C:.3f} C (digitization error estimate)")

    # ---------- 2. Benchmark reproduction ----------
    logger.info("Benchmark reproduction on the full digitized curve")
    full = {}
    m1_fit_full = fit_c0(t_all, T_all, t0, T_ROOM)
    res_m1 = c0_closed_form(t_all, t0, m1_fit_full["params"]["a_per_min"], T_ROOM) - T_all
    full["model1_C0_Tr20"] = {"params": m1_fit_full["params"], "rss_per_ndf_K2": float(np.sum(res_m1**2) / (len(t_all) - 1))}
    m2_fit_full = fit_c1(t_all, T_all, t0, T_ROOM)
    full["model2_C1_Tr20"] = {"params": m2_fit_full["params"], "rss_per_ndf_K2": float(m2_fit_full["rss"] / (len(t_all) - 2))}
    m1_free = fit_c1(t_all, T_all, t0, T_ROOM, free_room=True)  # ambient free, sensitivity only
    full["model2_C1_TrFree"] = {"params": m1_free["params"], "rss_per_ndf_K2": float(m1_free["rss"] / (len(t_all) - 3))}
    m0_free_room = None
    # Ambient-free C0 (model 1 with free ambient) for sensitivity.
    res_c0free = least_squares(lambda p: c0_closed_form(t_all, t0, p[0], p[1]) - T_all, x0=[0.02, 20.0], bounds=([1e-6, 0.0], [2.0, 35.0]), x_scale="jac")
    full["model1_C0_TrFree"] = {"params": {"a_per_min": float(res_c0free.x[0]), "t_room_C": float(res_c0free.x[1])}, "rss_per_ndf_K2": float(np.sum(res_c0free.fun**2) / (len(t_all) - 2))}

    c2_full = fit_c2(t_all, T_all, t0, T_ROOM, kind="C2")
    full["model_C2_plan_form_full_range_diagnostic"] = {"params": c2_full["params"], "rss_per_ndf_K2": float(c2_full["rss"] / (len(t_all) - c2_full["n_params"])), "at_bounds": c2_full["at_bounds"]}
    c2p_full = fit_c2(t_all, T_all, t0, T_ROOM, kind="C2p")
    full["model_C2p_source_form_full_range_diagnostic"] = {"params": c2p_full["params"], "rss_per_ndf_K2": float(c2p_full["rss"] / (len(t_all) - c2p_full["n_params"])), "at_bounds": c2p_full["at_bounds"]}
    logger.info(f"Full-range C2 (plan form): {c2_full['params']}, RSS/NDF {full['model_C2_plan_form_full_range_diagnostic']['rss_per_ndf_K2']:.3f}")

    paper_scores = load_paper_curve_scores()
    reported = {"model 1": 32.1, "model 2": 2.4, "model 3": 81.3, "model 4": 1.0}
    gate_rows = {}
    for label, rep in reported.items():
        key = "model 1" if label == "model 1" else label
        if key in paper_scores:
            ratio = paper_scores[key]["ratio_to_reported"]
            gate_rows[label] = {"reported_chi2_per_ndf": rep, "digitized_drawn_curve_rss_per_ndf": paper_scores[key]["digitized_rss_over_ndf_K2"], "ratio": ratio}
    gate_rows["model 1 (own refit, Tr=20)"] = {"reported_chi2_per_ndf": 32.1, "digitized_drawn_curve_rss_per_ndf": full["model1_C0_Tr20"]["rss_per_ndf_K2"], "ratio": full["model1_C0_Tr20"]["rss_per_ndf_K2"] / 32.1}
    gate_rows["model 2 (own refit, Tr=20)"] = {"reported_chi2_per_ndf": 2.4, "digitized_drawn_curve_rss_per_ndf": full["model2_C1_Tr20"]["rss_per_ndf_K2"], "ratio": full["model2_C1_Tr20"]["rss_per_ndf_K2"] / 2.4}
    gate_pass = all(abs(v["ratio"] - 1.0) <= GATE_TOL for v in gate_rows.values())
    logger.info(f"Reproduction gate (tolerance {GATE_TOL:.0%}): {'PASS' if gate_pass else 'FAIL'}")
    for k, v in gate_rows.items():
        logger.info(f"  {k}: digitized {v['digitized_drawn_curve_rss_per_ndf']:.3f} vs reported {v['reported_chi2_per_ndf']} (ratio {v['ratio']:.2f})")

    # ---------- 3. Candidates on the 30-minute window ----------
    win = t_all <= WINDOW_MIN + 1e-9
    t_w, T_w = t_all[win], T_all[win]
    n_w = len(t_w)
    logger.info(f"30-minute window: {n_w} points, t up to {t_w[-1]:.2f} min")
    if n_w < 6:
        raise RuntimeError("fewer than 6 points in the 30-minute window; fallback F5 applies")

    fits: dict[str, dict] = {}
    fits["C0"] = fit_c0(t_w, T_w, t0, T_ROOM)
    fits["C1"] = fit_c1(t_w, T_w, t0, T_ROOM)
    fits["C2"] = fit_c2(t_w, T_w, t0, T_ROOM, kind="C2")
    fits["C2p"] = fit_c2(t_w, T_w, t0, T_ROOM, kind="C2p")
    fits["C2_fixed_x"] = fit_c2(t_w, T_w, t0, T_ROOM, kind="C2", fix_x=1.25)
    logger.info("Fits on the 30-minute window:")
    for k, v in fits.items():
        logger.info(f"  {k}: {v['params']} at_bounds={v['at_bounds']}")

    names = ["C0", "C1", "C2", "C2p", "C2_fixed_x"]
    pred_w = {n: predict_candidate(n, fits[n], t_w, t0, T_ROOM) for n in names}
    resid_w = {n: pred_w[n] - T_w for n in names}

    cand_metrics = {}
    for n in names:
        m = metrics(resid_w[n], fits[n]["n_params"], SIGMA_MEAS_C)
        early = resid_w[n][t_w < 10]
        late = resid_w[n][t_w >= 20]
        m["mean_resid_first_10min_K"] = float(early.mean()) if len(early) else float("nan")
        m["mean_resid_last_20min_K"] = float(late.mean()) if len(late) else float("nan")
        m["params"] = fits[n]["params"]
        m["at_bounds"] = fits[n]["at_bounds"]
        m["rms_30min_K"] = m["rms_K"]
        cand_metrics[n] = m

    # Source's drawn model-1 curve (published, not refit) on the same window.
    pub = paper_curve_rms(t_w, T_w, shift)["published_model1_curve"]
    cand_metrics["published_model1_curve"] = metrics(pub, 1, SIGMA_MEAS_C)
    cand_metrics["published_model1_curve"]["rms_30min_K"] = cand_metrics["published_model1_curve"]["rms_K"]
    cand_metrics["published_model1_curve"]["mean_resid_first_10min_K"] = float(pub[t_w < 10].mean())
    cand_metrics["published_model1_curve"]["mean_resid_last_20min_K"] = float(pub[t_w >= 20].mean())
    cand_metrics["published_model1_curve"]["at_bounds"] = False
    cand_metrics["published_model1_curve"]["params"] = {"note": "curve digitized from Fig. 2 of the source, not refit"}
    resid_w["published_model1_curve"] = pub

    # ---------- 5. Block bootstrap (residual blocks in 5-min bins) ----------
    rng = np.random.default_rng(RNG_SEED)
    bins = np.floor(t_w / BLOCK_MIN).astype(int)
    uniq = np.unique(bins)
    blocks = [np.where(bins == b)[0] for b in uniq]
    logger.info(f"Block bootstrap: {len(blocks)} blocks of 5 min in the window, {BOOT_REPS} repeats")
    boot = block_bootstrap({n: resid_w[n] for n in names}, blocks, BOOT_REPS, rng)
    for n in names:
        cand_metrics[n]["bootstrap"] = boot[n]

    # ---------- 6. Sensitivity and forecast check ----------
    sens = {}
    sens["C0_ambient_free_window"] = {"params": None}
    c0f = least_squares(lambda p: c0_closed_form(t_w, t0, p[0], p[1]) - T_w, x0=[0.02, 20.0], bounds=([1e-6, 0.0], [2.0, 35.0]), x_scale="jac")
    rf = c0_closed_form(t_w, t0, c0f.x[0], c0f.x[1]) - T_w
    sens["C0_ambient_free_window"] = {"params": {"a_per_min": float(c0f.x[0]), "t_room_C": float(c0f.x[1])}, "rms_30min_K": float(np.sqrt(np.mean(rf**2))), "n_params": 2}
    c1f = fit_c1(t_w, T_w, t0, T_ROOM, free_room=True)
    rc1f = integrate("C1", (c1f["params"]["a_per_min"], c1f["params"]["x"]), t_w, t0, c1f["params"]["t_room_C"]) - T_w
    sens["C1_ambient_free_window"] = {"params": c1f["params"], "rms_30min_K": float(np.sqrt(np.mean(rc1f**2))), "n_params": 3}

    # Forecast check: fit on t <= 15, score on 15 < t <= 30.
    fit_mask = t_w <= 15.0
    fc_mask = (t_w > 15.0) & (t_w <= 30.0)
    fc = {}
    if fc_mask.sum() >= 2:
        f0 = fit_c0(t_w[fit_mask], T_w[fit_mask], t0, T_ROOM)
        p0 = c0_closed_form(t_w[fc_mask], t0, f0["params"]["a_per_min"], T_ROOM) - T_w[fc_mask]
        f1 = fit_c1(t_w[fit_mask], T_w[fit_mask], t0, T_ROOM)
        p1 = integrate("C1", (f1["params"]["a_per_min"], f1["params"]["x"]), t_w[fc_mask], t0, T_ROOM) - T_w[fc_mask]
        fc = {
            "n_fit_points": int(fit_mask.sum()),
            "n_forecast_points": int(fc_mask.sum()),
            "C0_forecast_rms_K": float(np.sqrt(np.mean(p0**2))),
            "C1_forecast_rms_K": float(np.sqrt(np.mean(p1**2))),
            "note": "exploratory, few points",
        }

    # ---------- 7. Selection rule ----------
    best_chi2 = min(cand_metrics[n]["chi2_sigma_0p3_per_ndf"] for n in names)
    eligible = [n for n in names if cand_metrics[n]["chi2_sigma_0p3_per_ndf"] <= best_chi2 + 1.0]
    survivor = min(eligible, key=lambda n: cand_metrics[n]["rms_30min_K"]) if eligible else None
    rule_pass = False
    if survivor is not None and survivor != "C0":
        rel = boot[survivor]["relative_rms_improvement_vs_C0_point"]
        rule_pass = rel >= RMS_EFFECT_THRESHOLD and boot[survivor]["rms_minus_C0_excludes_zero"]
    descriptive_best = min(names, key=lambda n: cand_metrics[n]["rms_30min_K"])

    # ---------- Digitization error and noise floor ----------
    noise_floor = {
        "digitization_error_C_median_across_figures": digi_err_C,
        "measurement_error_C_stated": SIGMA_MEAS_C,
        "sigma_used_C": max(SIGMA_MEAS_C, digi_err_C),
        "note": "digitization error is below the stated measurement error, so sigma = 0.3 C is used",
    }

    # ---------- Output tables ----------
    rows = []
    for n in names + ["published_model1_curve"]:
        m = cand_metrics[n]
        row = {"model": n, "n_params": m["n_params"], "rms_30min_K": m["rms_30min_K"],
               "chi2_sigma0p3_per_ndf": m["chi2_sigma_0p3_per_ndf"], "AIC": m["AIC"], "BIC": m["BIC"],
               "mean_resid_first10_K": m["mean_resid_first_10min_K"], "mean_resid_last20_K": m["mean_resid_last_20min_K"],
               "at_bounds": m["at_bounds"]}
        if n in boot:
            row["rms_ci95_low"] = boot[n]["rms_K_ci95"][0]
            row["rms_ci95_high"] = boot[n]["rms_K_ci95"][1]
        rows.append(row)
    pd.DataFrame(rows).to_csv(RESULTS / "analysis_tables.csv", index=False)

    # Per-point residual series in the window and the full curve for each model
    residual_series = []
    for i in range(n_w):
        entry = {"t_min": float(t_w[i]), "T_data_C": float(T_w[i])}
        for n in names:
            entry[f"resid_{n}_K"] = float(resid_w[n][i])
        entry["resid_published_model1_curve_K"] = float(pub[i])
        residual_series.append(entry)

    results = {
        "model_fit_window_min": WINDOW_MIN,
        "t_room_fixed_C": T_ROOM,
        "T0_C": t0,
        "time_shift_min": float(shift),
        "digitization_noise_floor": noise_floor,
        "reproduction_gate": {
            "tolerance": GATE_TOL,
            "pass": bool(gate_pass),
            "rows": gate_rows,
            "full_curve_refits": full,
        },
        "candidates_30min_window": cand_metrics,
        "residual_series_window": residual_series,
        "sensitivity": sens,
        "forecast_check": fc,
        "selection": {
            "rule": "lowest 30-min RMS among candidates with chi2/NDF (sigma 0.3 C) within 1 of best, and relative RMS improvement over C0 >= 25% with bootstrap interval excluding zero",
            "applied": bool(gate_pass),
            "survivor": survivor,
            "rule_pass": bool(rule_pass),
            "descriptive_lowest_30min_RMS": descriptive_best,
            "eligible_by_chi2": eligible,
        },
        "not_testable": {
            "C3_humidity_deficit_evaporation": "humidity not recorded in the source",
            "C4_geometry_S_over_V": "pot diameter, height and fill are not given in the source text; metal and vacuum curves are not published as data",
            "cross_pot_check": "only the china curve has measured points; metal and vacuum pots appear only as fitted parameters in Table I",
            "fat_covered_control": "the source reports a fitted evaporation coefficient for water with fat (Table I) but no fat-covered curve",
        },
        "bootstrap": {"reps": BOOT_REPS, "block_minutes": BLOCK_MIN, "n_blocks_in_window": len(blocks), "seed": RNG_SEED, "method": "residual block bootstrap, no refit"},
    }

    (RESULTS / "analysis_results.json").write_text(json.dumps(results, indent=2, default=float))
    logger.info(f"Saved analysis results. Reproduction gate: {'PASS' if gate_pass else 'FAIL'}; descriptive lowest 30-min RMS: {descriptive_best}")


if __name__ == "__main__":
    main()
