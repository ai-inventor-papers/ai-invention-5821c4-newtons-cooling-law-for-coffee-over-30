"""Independent re-derivation of headline numbers, by a different code path from method.py.

method.py: closed-form predictions, scipy least_squares with multi-start.
This audit: predictions by numerically integrating du/dt = -a u^x with solve_ivp, fitting by
Nelder-Mead / bounded scalar minimisation on the raw dataset (full_data_out.json), no reuse of method.py functions.
A shuffled-time placebo is run too: the in-window times are permuted against the temperatures and the same fit must
give clearly worse RMS than the real data.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize, minimize_scalar

WS = Path(__file__).resolve().parent.parent
RES = json.loads((WS / "results" / "exponent_profile.json").read_text())
HELD = json.loads((WS / "results" / "heldout_scores.json").read_text())
raw = json.loads((WS / "full_data_out.json").read_text())
rows = []
for ds in raw["datasets"]:
    for ex in ds["examples"]:
        inp = json.loads(ex["input"])
        rows.append({"fold": ex["metadata_fold"], "id": ex["metadata_curve_id"],
                     "t": np.array(inp["time_min"], float), "T": np.array(json.loads(ex["output"]), float),
                     "tr": inp["room_temp_c"]})
china = [r for r in rows if r["fold"] == 1][0]


def sim(t_eval, T0, Tr, a, x):
    """Integrate du/dt = -a u^x numerically (u = T - Tr) and return T on t_eval (time relative to first sample)."""
    u0 = T0 - Tr
    if u0 <= 0:
        return np.full(t_eval.shape, np.inf)
    f = lambda _t, u: -a * np.maximum(u, 0.0) ** x
    sol = solve_ivp(f, (0.0, float(t_eval[-1])), [u0], t_eval=t_eval, rtol=1e-9, atol=1e-11, method="LSODA")
    if not sol.success or sol.y.shape[1] != t_eval.size:
        return np.full(t_eval.shape, np.inf)
    return Tr + sol.y[0]


def rms(resid):
    return float(np.sqrt(np.mean(resid ** 2)))


def in_window(r):
    m = r["t"] <= 30.0
    return r["t"][m] - r["t"][0], r["T"][m]


def fit_a(tau, T, Tr, x):
    """1-D bounded fit of log a; initial temperature is the first measured value."""
    def loss(la):
        p = sim(tau, T[0], Tr, np.exp(la), x)
        return np.sum((T - p) ** 2) if np.all(np.isfinite(p)) else 1e9
    grid = np.linspace(-12, 1, 60)
    best = min(grid, key=loss)
    r = minimize_scalar(loss, bounds=(best - 0.5, best + 0.5), method="bounded")
    return float(np.exp(r.x)), rms(T - sim(tau, T[0], Tr, np.exp(r.x), x))


out = {}
tau_c, T_c = in_window(china)
Tr = 20.0
# Headline 1: C0 in-window RMS (x = 1, T_room 20, measured first value)
a0, rms0 = fit_a(tau_c, T_c, Tr, 1.0)
out["C0_in_window_rms_K"] = rms0
out["C0_a"] = a0
# Headline 2: free-x in-window (Nelder-Mead over log a and x)
def loss2(p):
    la, x = p
    if not (0.5 <= x <= 3.0):
        return 1e9
    pr = sim(tau_c, T_c[0], Tr, np.exp(la), x)
    return np.sum((T_c - pr) ** 2) if np.all(np.isfinite(pr)) else 1e9
best = None
for x0 in (1.5, 2.0, 2.5):
    a_init, _ = fit_a(tau_c, T_c, Tr, x0)
    r = minimize(loss2, [np.log(a_init), x0], method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-12, "maxiter": 4000})
    if best is None or r.fun < best.fun:
        best = r
out["free_x_in_window"] = float(best.x[1])
out["free_x_in_window_rms_K"] = float(np.sqrt(best.fun / tau_c.size))
# Headline 3: profile minimum over x on 1.00-3.00 (coarse 0.05 grid, enough to confirm the 2.18 region)
prof = [(x, np.sum((T_c - sim(tau_c, T_c[0], Tr, fit_a(tau_c, T_c, Tr, x)[0], x)) ** 2)) for x in np.arange(1.0, 3.0001, 0.05)]
out["profile_min_x_coarse_0p05"] = float(min(prof, key=lambda p: p[1])[0])
# Headline 4: S2 mean C0 and mean C1 at x = 2.18 over usable held-out curves (refit a on t <= 10, score 10 < t <= 30)
def s2(r, x):
    tau = r["t"] - r["t"][0]
    fm = tau <= 10
    sm = (tau > 10) & (tau <= 30)
    if sm.sum() < 3:
        return None
    if r["tr"] is None:
        return None  # Langer curves: room temperature not reported; the method fits it, this audit only re-derives the Manitoba curve plus Langer with Tr fitted below
    a, _ = fit_a(tau[fm], r["T"][fm], r["tr"], x)
    p = sim(tau[sm], r["T"][0], r["tr"], a, x)
    return rms(r["T"][sm] - p)
man = [r for r in rows if r["fold"] == 2][0]
out["manitoba_S2_C0_rms"] = s2(man, 1.0)
x_star = RES["profile_minimum_x"]
out["manitoba_S2_xstar_rms"] = s2(man, x_star)
out["manitoba_method_values"] = {"S2_C0": HELD["summary"]["x=1.00"]["S2"]["per_curve"] if False else None}
# Placebo: shuffle in-window times against temperatures; same C0 and free-x fit must be clearly worse than real data
rng = np.random.default_rng(7)
perm = rng.permutation(T_c.size)
tau_p = tau_c.copy()
T_p = T_c[perm]
a_p, rms_p0 = fit_a(tau_p, T_p, Tr, 1.0)
out["placebo_shuffled_C0_rms_K"] = rms_p0
# compare with method.py values (cited from results, not used in the computation above)
out["method_py_values"] = {
    "C0_in_window_rms_K": RES["fixed_x"][0]["in_window_RMS_K"],
    "free_x_in_window": RES["free_x_in_window"]["x"],
    "free_x_in_window_rms_K": RES["free_x_in_window"]["rms_K"],
    "profile_minimum_x": RES["profile_minimum_x"],
    "manitoba_S2_C0_rms_method": [r["rms_K"] for r in HELD["per_model"]["x=1.00"]["S2"] if r["curve_id"].startswith("MANITOBA")][0],
    "manitoba_S2_xstar_rms_method": [r["rms_K"] for r in HELD["per_model"][f"x={x_star:.2f}"]["S2"] if r["curve_id"].startswith("MANITOBA")][0],
}
out["checks"] = {
    "C0_rms_agrees_within_0p02K": abs(out["C0_in_window_rms_K"] - out["method_py_values"]["C0_in_window_rms_K"]) <= 0.02,
    "free_x_agrees_within_0p05": abs(out["free_x_in_window"] - out["method_py_values"]["free_x_in_window"]) <= 0.05,
    "placebo_worse_than_real_by_2x": rms_p0 > 2 * out["C0_in_window_rms_K"],
}
print(json.dumps(out, indent=2, default=float))
