#!/usr/bin/env python3
"""Validation checks T1-T7 from the artifact plan, run on CPU.

Each check writes its outcome to results/tests.json. A failed check is reported,
not hidden; the README lists them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from loguru import logger
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "src"))

from models import _rhs_factory, c0_closed_form, integrate  # noqa: E402

RESULTS = WORKSPACE / "results"
RNG = np.random.default_rng(7)
T_ROOM = 20.0


def fit_c0_params(t: np.ndarray, T: np.ndarray, t0: float) -> float:
    r = least_squares(lambda p: c0_closed_form(t, t0, p[0], T_ROOM) - T, x0=[0.02], bounds=([1e-6], [2.0]), x_scale="jac")
    return float(r.x[0])


def block_bootstrap_ci(resid: np.ndarray, blocks: list[np.ndarray], reps: int, rng: np.random.Generator) -> tuple[float, float]:
    nb = len(blocks)
    means = np.empty(reps)
    for i in range(reps):
        pick = rng.integers(0, nb, size=nb)
        idx = np.concatenate([blocks[j] for j in pick])
        means[i] = resid[idx].mean()
    return tuple(np.percentile(means, [2.5, 97.5]))


def t1_synthetic_recovery() -> dict:
    t = np.array([0, 2.8, 4.7, 9.7, 14.7, 20.6, 25.6])
    k_true = 0.03
    t0 = 80.0
    estimates = []
    for _ in range(300):
        y = c0_closed_form(t, t0, k_true, T_ROOM) + RNG.normal(0, 0.3, size=t.size)
        estimates.append(fit_c0_params(t, y, t0))
    est = np.array(estimates)
    within = float(np.mean(np.abs(est - k_true) < 2 * est.std()))
    return {
        "k_true": k_true,
        "mean_estimate": float(est.mean()),
        "sd_estimate": float(est.std()),
        "fraction_within_2sd": within,
        "pass": bool(abs(est.mean() - k_true) < 0.1 * k_true),
    }


def t2_sign_check() -> dict:
    t = np.linspace(0, 30, 13)
    t0 = 80.0
    # Truth: nonlinear convection with x = 1.34, rate chosen to match a similar early cooling.
    truth = integrate("C1", (0.0035, 1.34), t, t0, T_ROOM)
    noisy = truth + RNG.normal(0, 0.05, size=t.size)
    k = fit_c0_params(t, noisy, t0)
    model = c0_closed_form(t, t0, k, T_ROOM)
    resid = model - noisy  # model minus data
    early = float(resid[t < 10].mean())
    late = float(resid[t >= 20].mean())
    return {
        "truth": "C1, x = 1.34",
        "early_mean_resid_K": early,
        "late_mean_resid_K": late,
        "sign_convention": "model minus data",
        "pass": bool(early > 0 and late < 0),
        "note": "early positive and late negative: the constant-rate law underpredicts early loss and overpredicts late loss, the pattern the source describes for its model 1",
    }


def t4_solver_vs_closed_form() -> dict:
    a, t0, tr = 0.02, 80.0, T_ROOM
    t_eval = np.linspace(0, 60, 61)
    rhs = _rhs_factory("C1", (a, 1.0), tr)
    sol = solve_ivp(rhs, (0, 60), [t0], t_eval=t_eval, method="LSODA", rtol=1e-9, atol=1e-11)
    closed = c0_closed_form(t_eval, t0, a, tr)
    rel = float(np.max(np.abs(sol.y[0] - closed) / np.abs(closed)))
    return {"max_relative_error": rel, "pass": bool(rel < 1e-6)}


def t5_bootstrap_coverage() -> dict:
    rng = np.random.default_rng(11)
    reps = 200
    n = 30
    rho = 0.6
    t = np.arange(n) * 1.0
    blocks = [np.arange(i, min(i + 3, n)) for i in range(0, n, 3)]  # 3-point blocks
    cov_block, cov_iid = 0, 0
    for _ in range(reps):
        e = np.zeros(n)
        eps = rng.normal(0, 1, n)
        for i in range(n):
            e[i] = (rho * e[i - 1] if i > 0 else 0.0) + np.sqrt(1 - rho**2) * eps[i]
        # true mean is 0; the 95% interval should contain 0 about 95% of the time
        lo, hi = block_bootstrap_ci(e, blocks, 400, rng)
        cov_block += int(lo <= 0.0 <= hi)
        iid_blocks = [np.array([i]) for i in range(n)]
        lo2, hi2 = block_bootstrap_ci(e, iid_blocks, 400, rng)
        cov_iid += int(lo2 <= 0.0 <= hi2)
    return {
        "reps": reps,
        "autocorrelation_rho": rho,
        "coverage_block_bootstrap": cov_block / reps,
        "coverage_iid_bootstrap": cov_iid / reps,
        "pass": bool(abs(cov_block / reps - 0.95) < 0.05),
        "note": "the 3-point block bootstrap is compared with the naive iid bootstrap under AR(1) residuals",
    }


def t6_c0_residual_vs_digitization() -> dict:
    analysis = json.loads((RESULTS / "analysis_results.json").read_text())
    c0_rms = analysis["candidates_30min_window"]["C0"]["rms_30min_K"]
    dig = analysis["digitization_noise_floor"]["digitization_error_C_median_across_figures"]
    ratio = c0_rms / dig
    return {
        "C0_rms_30min_K": c0_rms,
        "digitization_error_C": dig,
        "ratio": ratio,
        "pass": False,
        "interpretation": (
            "Plan expected the C0 RMS to be near the digitization error. It is about "
            f"{ratio:.1f} times larger. Across-figure digitization agreement is {dig:.2f} C, and the source's "
            "own drawn model-1 curve shows the same early-under, late-over pattern, so the excess is "
            "the constant-rate law's misfit and not digitization error. Recorded as a deviation from T6."
        ),
    }


def t7_selection_dry_run() -> dict:
    # Force every extension to equal C0; the selection rule must not choose an extension.
    c0_rms = 1.0
    cands = {"C0": {"rms": c0_rms, "chi2": 10.0}, "C1": {"rms": c0_rms, "chi2": 10.0}, "C2": {"rms": c0_rms, "chi2": 10.0}}
    best_chi2 = min(v["chi2"] for v in cands.values())
    eligible = [n for n, v in cands.items() if v["chi2"] <= best_chi2 + 1.0]
    survivor = min(eligible, key=lambda n: cands[n]["rms"])
    rel_improvement = 1 - cands[survivor]["rms"] / c0_rms
    rule_pass = survivor != "C0" and rel_improvement >= 0.25
    return {"survivor": survivor, "rule_pass": bool(rule_pass), "pass": bool(survivor == "C0" and not rule_pass)}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    out = {}
    out["T1_synthetic_recovery"] = t1_synthetic_recovery()
    out["T2_sign_check"] = t2_sign_check()
    out["T4_solver_vs_closed_form"] = t4_solver_vs_closed_form()
    out["T5_bootstrap_coverage"] = t5_bootstrap_coverage()
    out["T6_c0_residual_vs_digitization"] = t6_c0_residual_vs_digitization()
    out["T7_selection_dry_run"] = t7_selection_dry_run()
    out["T3_reproduction_gate"] = {
        "pass": bool(json.loads((RESULTS / "analysis_results.json").read_text())["reproduction_gate"]["pass"]),
        "note": "see analysis_results.json; the digitized drawn curves and refits disagree with the reported chi2/NDF by more than 30%",
    }
    for k, v in out.items():
        logger.info(f"{k}: pass={v.get('pass')}  {({kk: vv for kk, vv in v.items() if kk not in ('interpretation', 'note')})}")
    (RESULTS / "tests.json").write_text(json.dumps(out, indent=2))
    logger.info("Saved results/tests.json")


if __name__ == "__main__":
    main()
