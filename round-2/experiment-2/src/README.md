# Newton-type cooling laws on held-out coffee curves

Question: how accurately does Newton's law of cooling predict the temperature of a cup of coffee over 30 minutes, compared with published measurements?

## What was done

- Two models fitted to the first 30 min of one curve and scored, with frozen parameters, on other published curves:
  - **C0**: Newton's law with a constant rate, `T(t) = Tr + (T0 - Tr) exp(-k t)`.
  - **C1**: one-term nonlinear convection law, `dT/dt = -kc (T - Tr)^x`. Only `kc = a/C` is identifiable, so `kc` and `x` are fitted.
- Fit: multi-start `scipy.optimize.least_squares` (20 random starts plus a default start), bounds as in the plan.
- Protocols:
  - **In-sample reference**: fit and score the Sedlacek and Dolejsi china-pot curve.
  - **A (transfer)**: fit on Sedlacek; score the Manitoba table curve and six Langer curves.
  - **B (leave-one-source-out)**: three folds, each refitting on the other two sources.
- Two room-temperature ambients: **A** uses each curve's recorded room temperature (20 C default where none is recorded, flagged); **B** frees room temperature as a shared fitted parameter bounded to the fit set's reference temperature +/- 5 K.
- Intervals: curve-level bootstrap where a set has 2 or more curves; within-curve block bootstrap (block length 3) for single-curve sets, labelled as not comparable. 1000 resamples, seed 0.
- No LLM calls, no new measurements, CPU only. Runtime about 12 s.

## Results (RMS over 0-30 min, K; ambient A unless noted)

| Setting | C0 (Newton) | C1 (convection) |
|---|---|---|
| In-sample, Sedlacek | 1.26 [0.94, 1.37] | 0.33 [0.05, 0.46] |
| Protocol A, Manitoba (held out) | 3.45 | 2.66 |
| Protocol A, Langer mean (6 curves) | 9.15 | 9.06 |
| Protocol A, all 7 held-out curves | 8.33 [6.54, 9.93] | 8.14 [5.93, 9.96] |
| Fold Sedlacek (fit Manitoba + Langer) | 7.21 | 7.20 |
| Fold Manitoba (fit Sedlacek + Langer) | 10.77 | 11.04 |
| Fold Langer (fit Sedlacek + Manitoba) | 11.23 | 10.73 |

- Ambient B gives the same ordering: Protocol A Manitoba 2.89 (C0) vs 1.88 (C1); Langer mean 9.15 vs 9.05.
- Reference from the earlier in-sample run (iter_1, printed for comparison only): C0 1.07 K, C1 0.36 K. The C1 value reproduces; **C0 does not** (1.26 K here, 1.12 K with ambient B). The difference comes from the room-temperature treatment, not checked further.

## Pre-registered decision rule (outcome)

- Early residual sign for C0 positive (0-10 min) on held-out curves: **not supported**. Mean early residual -3.2 K over the 7 held-out curves; positive only for Manitoba.
- C1 lower than C0 under Protocol A: **yes, marginally** (8.14 vs 8.33 K); the paired difference is -0.19 K with interval [-0.44, -0.00]; C1 is lower on 5 of 7 curves. A sign-flip placebo on the same per-curve differences gives p = 0.0625 for the mean difference, and the chance of C1 being lower on at least 5 of 7 curves with no real difference is 0.23 (`audit/rederive_output.txt`). The advantage is therefore not statistically supported.
- C1 lower in at least 2 of 3 folds: **formally yes** (Sedlacek and Langer), but the Sedlacek difference is 0.01 K with an interval spanning zero, and Manitoba is worse under C1.
- C1 under 0.5 K on Manitoba and on the Langer mean: **no** (2.66 K and 9.06 K).
- C0 adequate (under 0.5 K on held-out curves): **no**.

**Reading:** the Newton-type laws fit one coffee curve well (C1 in-sample 0.33 K), but they do not transfer. Langer's hot-water curves cool much more slowly than the china-pot coffee and are off by about 9 K over 30 min for both models. Even with room temperature freed, the Langer fold's fitted room temperature sits on a bound (C0 at the upper bound, C1 at the lower bound). The claim that can be made is narrow: a single-curve fit does not predict other published curves at the 0.5 K level.

## Caveats

- Eight curves from three sources; Langer's six curves are one lab and one protocol, not six sessions.
- Sedlacek and Langer report no room temperature; 20 C is the default under ambient A. The Sedlacek in-sample fit under ambient B pushes room temperature to the 25 C bound, so the default is a real constraint.
- Several fits end on a bound (see `fold_summary.json`, `blocks[*].fitted_parameters` and the run log). Those fits are bound-limited, not interior optima.
- The Langer 65 C crossing-time disagreement is not used as a target (the dataset flags it as unresolved).
- Humidity and fat-layer effects are out of scope; no source records them, so the evaporation claim is not tested.
- Single-curve intervals are within-curve only and not comparable to between-curve intervals.
- Langer recorded initial temperatures are 80.2-82.3 C, not the 88 C in the source text. The recorded values were used.
- C1 is evaluated in closed form (exact for this separable ODE). It matches `scipy.integrate.solve_ivp` (LSODA) at the fitted parameters to 1.6e-6 K, recorded in `fold_summary.json`.

## Layout

- `method.py`: full pipeline (loading, fitting, protocols, intervals, outputs). Run: `.venv/bin/python method.py data/full_data_out.json results`
- `data/full_data_out.json`: the eight curves (copied from the dataset artifact `gen_art_dataset_1`); `mini_` and `preview_` variants alongside.
- `results/heldout_scores.json`: one row per (protocol, fold, ambient, model, curve): fitted parameters, RMS, signed early and late residuals, residual-vs-time series, partial flag, starts converged.
- `results/fold_summary.json`: per-block means, intervals, paired C1 minus C0 differences, fitted parameters, decision rule, C1 closed-form check, metadata (seeds, replicate count, Langer crossing-time flag, digitisation errors).
- `results/method_out.json` (`mini_` and `preview_` variants): per-curve observed data and predictions in the exp_gen_sol_out shape (datasets, examples, `predict_*`).
- `logs/run.log`, `logs/full_run_stdout.txt`: run logs.
- `requirements.txt`: pinned packages (numpy, scipy, pandas, pydantic, loguru).
- `.aii/manifest.yaml`: keep and delete decisions.

## How to run

```
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python method.py data/full_data_out.json results
```

## Restoring removed files

- `.venv/` (regenerable): `uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt`

Files in `results/` are kept on the run's volume and are not in the published repository. Their paths relative to this workspace are `results/heldout_scores.json`, `results/fold_summary.json`, and `results/method_out.json`.

## Not done

- `aii-json` validator: rejected every path in this environment, including `/tmp`, so no schema result comes from it. Schema validation was done with jsonschema directly against `exp_gen_sol_out` for `method_out.json`: 0 errors, and no empty `predict_*` fields. `heldout_scores.json` and `fold_summary.json` are analysis outputs with their own structure, not `exp_gen_sol_out`.
- The mini and preview variants of `method_out.json` were built by hand, since the formatter accepts only a top-level array.
- No figures were produced.

## Sensitivity extension (added after the planned run)

`audit/extend_full_output.py` scores the four digitized Langer curves that the plan excluded (Abb2-07 to Abb2-10), using the frozen planned parameters (no refit). The full output `full_method_out.json` therefore has 12 examples: the 8 planned curves plus these 4, marked `metadata_role = sensitivity_excluded_from_planned_set`. The planned headline numbers are unchanged. Across all ten Langer curves, the C0 mean RMS is 9.17 K and C1 is 9.05 K; the planned six give 9.15 K and 9.06 K. The extra curves' initial temperature is taken as their first sample, and room temperature is the 20 C default. Results are in `results/sensitivity_langer10.json`.

