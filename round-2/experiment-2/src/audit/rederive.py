#!/usr/bin/env python3
"""Independent re-derivation of the headline numbers.

Different code path from method.py:
  - reads the raw temperatures straight from data/full_data_out.json (no method.py loader);
  - reads only the fitted parameters and the stored room temperature from results/heldout_scores.json;
  - predicts C0 with its closed form and C1 by numerically integrating the ODE with scipy solve_ivp (LSODA),
    not with the closed form used in method.py;
  - recomputes RMS, signed early/late residuals and the headline means from those predictions.
Then a placebo: the paired C1-vs-C0 claim is re-tested with random label swaps (sign flips) on the
same per-curve differences. A real effect should be unusual under the placebo; a placebo that also
passes would mean the claim is not supported.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

WS = Path(__file__).resolve().parent.parent
RAW = json.loads((WS / "data" / "full_data_out.json").read_text())
STORED = json.loads((WS / "results" / "heldout_scores.json").read_text())["rows"]
SUMMARY = json.loads((WS / "results" / "fold_summary.json").read_text())

# raw curves keyed by curve id, read straight from the dataset file
curves = {}
for ds in RAW["datasets"]:
    for ex in ds["examples"]:
        inp = json.loads(ex["input"])
        t = np.array(inp["time_min"], float)
        T = np.array(json.loads(ex["output"]), float)
        m = t <= 30.0 + 1e-9
        curves[ex["metadata_curve_id"]] = dict(t=t[m], T=T[m], T0=float(inp["initial_liquid_temp_c"]),
                                               room=inp["room_temp_c"])


def predict_c0(t, T0, Tr, k):
    return Tr + (T0 - Tr) * np.exp(-k * t)


def predict_c1_ode(t, T0, Tr, kc, x):
    def rhs(_, y):
        return [-kc * max(y[0] - Tr, 0.0) ** x]
    sol = solve_ivp(rhs, (0.0, float(t.max())), [T0], method="LSODA", t_eval=t, rtol=1e-8, atol=1e-10)
    assert sol.success, sol.message
    return sol.y[0]


def recompute(row):
    c = curves[row["curve_id"]]
    p = row["fitted_params"]
    Tr = p["Tr_fitted_C"] if row["ambient"] == "B" else (c["room"] if c["room"] is not None else 20.0)
    if row["model"] == "C0":
        pred = predict_c0(c["t"], c["T0"], Tr, p["k"])
    else:
        pred = predict_c1_ode(c["t"], c["T0"], Tr, p["kc"], p["x"])
    r = pred - c["T"]
    early = c["t"] <= 10 + 1e-9
    late = (c["t"] > 10 + 1e-9)
    return dict(rms=float(np.sqrt(np.mean(r ** 2))), early=float(r[early].mean()), late=float(r[late].mean()))


# 1. recompute every stored row and compare
max_dev = {"rms": 0.0, "early": 0.0, "late": 0.0}
n_checked = 0
for row in STORED:
    re = recompute(row)
    if row["protocol"] == "B_leave_one_source_out" and False:
        continue
    for key, stored in (("rms", row["rms_K"]), ("early", row["signed_mean_0_10_K"]), ("late", row["signed_mean_10_30_K"])):
        if stored is None:
            continue
        max_dev[key] = max(max_dev[key], abs(re[key] - stored))
    n_checked += 1
print(f"Recomputed {n_checked} rows. Max abs deviation from stored values: "
      + ", ".join(f"{k} {v:.2e}" for k, v in max_dev.items()))

# 2. headline numbers from the recomputed values
def rows_for(protocol, amb, model, fold=None):
    out = []
    for row in STORED:
        if row["protocol"] == protocol and row["ambient"] == amb and row["model"] == model:
            if fold is None or row["fold"] == fold:
                out.append((row["curve_id"], row["source"], recompute(row)["rms"]))
    return out


a0 = rows_for("A_transfer", "A", "C0")
a1 = rows_for("A_transfer", "A", "C1")
print("\nProtocol A, ambient A (recomputed):")
print(f"  C0 mean over {len(a0)} curves: {np.mean([v for _, _, v in a0]):.3f} K")
print(f"  C1 mean over {len(a1)} curves: {np.mean([v for _, _, v in a1]):.3f} K")
man0 = [v for _, s, v in a0 if s == "Manitoba"][0]
man1 = [v for _, s, v in a1 if s == "Manitoba"][0]
lang0 = np.mean([v for _, s, v in a0 if s == "Langer"])
lang1 = np.mean([v for _, s, v in a1 if s == "Langer"])
print(f"  Manitoba C0 {man0:.3f}, C1 {man1:.3f}; Langer mean C0 {lang0:.3f}, C1 {lang1:.3f}")
diffs = np.array([v1 - v0 for (_, _, v0), (_, _, v1) in zip(a0, a1)])
print(f"  paired C1-C0 mean {diffs.mean():.3f} K, C1 lower on {int((diffs < 0).sum())} of {len(diffs)} curves")

ins0 = rows_for("in_sample_reference", "A", "C0")[0][2]
ins1 = rows_for("in_sample_reference", "A", "C1")[0][2]
print(f"\nIn-sample Sedlacek (ambient A): C0 {ins0:.3f} K, C1 {ins1:.3f} K")

# 3. placebo for the paired claim: random label swaps (sign flips) of per-curve differences
n = len(diffs)
signs = np.array(list(itertools.product([-1, 1], repeat=n)))  # all 2^n swap patterns, exact
perm_means = (signs * diffs).mean(axis=1)
p_mean = float(np.mean(perm_means <= diffs.mean() + 1e-12))
count_lower_obs = int((diffs < 0).sum())
# probability under a fair coin of C1 being lower on >= observed count curves
from math import comb
p_count = sum(comb(n, k) for k in range(count_lower_obs, n + 1)) / 2 ** n
print(f"\nPlacebo (exact sign-flip over {2**n} patterns):")
print(f"  one-sided p for mean difference <= observed {diffs.mean():.3f}: {p_mean:.4f}")
print(f"  P(C1 lower on >= {count_lower_obs} of {n} curves | no difference) = {p_count:.3f}")

# 4. shuffled-input placebo: destroy the time order of observations and check the RMS of the same predictions
rng = np.random.default_rng(0)
shuf_rms = []
for name in ("MANITOBA_WORKSHOP_coffee",):
    c = curves[name]
    row = [r for r in STORED if r["curve_id"] == name and r["protocol"] == "A_transfer"
           and r["ambient"] == "A" and r["model"] == "C1"][0]
    base = recompute(row)["rms"]
    for _ in range(200):
        Tshuf = rng.permutation(c["T"])
        shuf_rms.append(float(np.sqrt(np.mean((predict_c1_ode(c["t"], c["T0"], row["room_used_C"],
                                                              row["fitted_params"]["kc"],
                                                              row["fitted_params"]["x"]) - Tshuf) ** 2))))
    print(f"\nShuffled-observation placebo on Manitoba (C1 predictions vs permuted observations, 200 draws):")
    print(f"  real RMS {base:.3f} K; shuffled median {np.median(shuf_rms):.3f} K "
          f"(fraction of shuffles with RMS below real: {np.mean(np.array(shuf_rms) <= base):.3f})")

# 5. stored summary cross-check
print("\nStored fold_summary headline (for reference):")
b = SUMMARY["blocks"]["A_transfer|Sedlacek->Manitoba+Langer|A"]
print(f"  C0 {b['C0']['mean_rms_K']:.3f}, C1 {b['C1']['mean_rms_K']:.3f}, "
      f"paired {b['paired_C1_minus_C0']['mean_diff_C1_minus_C0_K']:.3f}, "
      f"count {b['paired_C1_minus_C0']['count_curves_C1_lower']}/{b['paired_C1_minus_C0']['n_curves']}")
