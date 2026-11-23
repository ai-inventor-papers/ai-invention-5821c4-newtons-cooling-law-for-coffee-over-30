# Testing the cooling exponent for coffee

Question: how accurately does Newton's law of cooling (C0) predict the temperature of a cup of coffee over 30 minutes,
compared with published measurements? This artifact tests whether the fitted exponent x of the one-term nonlinear
cooling law dT/dt = -a (T - T_room)^x / C is a stable quantity or an artifact of a free power fitted to about seven
in-window points. C0 is the x = 1 member of that family.

**Status: the benchmark gate failed.** The in-window numbers from the prior round were not reproduced (see
"Benchmark gate" below). The results here are reported with that failure stated. They should not be read as
validated against the prior round.

## What was done

1. Loaded the eight curves in `full_data_out.json` by their schema field names, plus the four digitized Langer curves
   (styles 07-10) that the dataset artifact left out. Total 12 curves in 3 source folds: Sedlacek and Dolejsi china pot,
   Manitoba workshop, and ten Langer et al. 2018 cups. The four extra curves come from `temp/datasets/langer_abb2_raw.json`,
   processed as `data.py` does.
2. Took the china-pot in-window set (t <= 30 min): 7 points, last at 25.59 min.
3. Fitted fixed-x models (x = 1.00, 1.25, 1.34, 1.50) on the in-window points, with T_room = 20 C.
4. Profiled x on a 0.01 grid, and fitted x freely (in-window, with T_room freed, and on the full record).
5. Ran a 200-replicate moving-block bootstrap (block length 3) of the free-x in-window residuals.
6. Scored the fixed-x models on the held-out curves under two schemes:
   - **S1 (strict transfer):** a from the china-pot fit, applied unchanged to each held-out curve with its own T_room
     and first temperature. RMS over 0 < t <= 30 min.
   - **S2 (per-curve scale):** a refit on each held-out curve's first 10 minutes (T_room from metadata when reported,
     otherwise fitted), scored on 10 < t <= 30 min. This is out of sample in time, but the scale is fitted on the same
     curve, so S2 cannot show the exponent is right, only that the shape fits.
7. Checked the reproduction-gate values (chi2/NDF 32.1, 2.4, 81.3, 1.0) against the source PDF text.

## Layout

| Path | What it is |
|---|---|
| `method.py` | The whole analysis. Writes everything under `results/`, `method_out.json`, `mini_method_out.json`, `preview_method_out.json`, and `logs/run.log`. |
| `data.py` | Dataset generator from the dependency artifact (copied; not run here). Its output is `full_data_out.json`. |
| `full_data_out.json`, `mini_data_out.json`, `preview_data_out.json` | Input dataset (copied from the dependency artifact). |
| `reproducibility.md` | Rerun steps for the dataset (copied). |
| `pyproject.toml` | Exact-version pins for `.venv` (see reproducibility.md). |
| `full_method_out.json` | Full output (same content as `method_out.json`). |
| `schemas/exp_gen_sol_out.json` | Output schema used for validation (copied from aii-json). |
| `diagnostics/audit_headline.py` | Independent re-derivation of headline numbers (ODE integration) with a shuffled placebo. |
| `results/audit_headline.json` | Output of that audit. |
| `results/exponent_profile.json` | Fixed-x table with residuals against time, the x profile, free-x fits, bootstrap, comparison with prior values. |
| `results/heldout_scores.json` | S1 and S2 per curve for each x, with a summary (mean RMS, C1 minus C0 per curve, sign counts). |
| `results/gate_provenance.json` | Gate values grepped in the source PDF text, with page and quote, or marked unverified. |
| `results/benchmark_checks.json` | Synthetic recovery, closed form against solve_ivp, benchmark targets under both T0 conventions. |
| `results/benchmark_probe.txt` | Output of `diagnostics/benchmark_probe.py`: C0 and C1 benchmark under the T0 and T_room variants tried while debugging. |
| `diagnostics/benchmark_probe.py` | Script behind `results/benchmark_probe.txt`. |
| `method_out.json` | Output in the `exp_gen_sol_out` schema (validated, 0 errors): each curve with `predict_C0_newton` and `predict_C1_profile_x`. |
| `mini_method_out.json`, `preview_method_out.json` | First example of each source (mini), and mini with strings truncated to 200 characters (preview). |
| `logs/run.log` | Run log. |
| `temp/source/sedlacek_ajp.pdf` | Source PDF used for the gate check (fetched; can be removed and refetched). |
| `.venv/` | Python environment (removed after the round; see the manifest). |

## How to run

```
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml
uv pip install --python .venv/bin/python pymupdf
.venv/bin/python method.py          # about 4 minutes on CPU
.venv/bin/python diagnostics/benchmark_probe.py > results/benchmark_probe.txt
```

No API calls, no GPU, no randomness beyond the seeded bootstrap (seed 20260523).

## Results

Numbers are for the china-pot in-window fit (7 points, T_room 20 C, T0 = first measured value).

**Fixed x, in-window RMS.** C0 (x = 1.00): a = 0.0265 per min, RMS 1.26 K. x = 1.25: 1.00 K. x = 1.34: 0.91 K.
x = 1.50: 0.75 K. The residuals are in `results/exponent_profile.json`.

**Profile over x.** On the planned 1.00 to 2.00 grid the minimum is at the edge (x = 2.00), so the grid was extended to
3.00 (a deviation from the plan). On the extended grid the minimum is at **x = 2.18**. The Δχ² = 3.84 interval (sigma =
0.3 C) is **[1.95, 2.42]**. The interval is wide for seven points, and the profile is weakly identified in its upper
part.

**Free x.** In-window with T_room 20 C: x = 2.18 (RMS 0.33 K). With T_room freed: x = 1.20 with T_room at its upper
bound (40 C), so the T_room-freed exponent is not identified. On the full 29-point record: x = 1.75.

**Bootstrap** (200 moving-block replicates, free x): median 2.21, 95% percentile interval **[2.03, 2.36]**. No replicate
hit a parameter bound.

**Held-out scoring.** Only one held-out curve is usable under S1 (Manitoba). The Langer curves do not report room
temperature, so under S1 they are marked not scorable, as the fallback plan requires.

| Model | S1 Manitoba RMS (K) | S2 mean RMS over 11 usable curves (K) | S2: curves where C1 beats C0 |
|---|---|---|---|
| C0 (x = 1.00) | 3.66 | 0.64 | — |
| x = 1.25 | 3.39 | 0.64 | 3 of 11 |
| x = 1.34 | 3.30 | 0.67 | 4 of 11 |
| x = 1.50 | 3.17 | 0.67 | 4 of 11 |
| x = 2.18 (profile minimum) | 2.82 | 0.60 | 2 of 11 |

The S2 mean at x = 2.18 is lower than C0 only by a small margin, and it is driven by the Manitoba curve (C0 5.30 K
versus 0.77 K at x = 2.18). For the ten Langer cups at x = 2.18, C1 has the lower RMS on only one curve (Abb2-05); it is
worse on the other nine. The Langer cups have RMS 0.03 to 1.42 K across models, so the per-curve pattern is not stable. S2 is only a shape-fit
check. It does not show the exponent is right.

**Synthetic recovery** (50 noise draws each, 0.3 C noise, 5-min sampling over 0 to 30 min): the free-x fit recovers
x within 0.1 in 94% of draws for x_true = 1.25, and 98% for x_true = 1.94. The closed form agrees with `solve_ivp` to
3e-10 K. So the fitter works when the model is right. The instability on the real curve is therefore a misfit or
digitization effect, not a fitting failure.

**Reproduction gate (`results/gate_provenance.json`).** Text grep of the source PDF (4 pages). 32.1, 2.4 and 1.0 appear
near "chi" (pages 2, 2 and 3). 81.3 appears in the PDF but not near "chi", so it is **unverified**. The Fig. 1 and
Fig. 2 captions were not found in the extracted text. The gate status is **conditional**. The PDF text grep does not
confirm that these values are the source's own gate statistic.

## Benchmark gate (failed)

The plan requires the C0 in-window RMS to be about 1.07 K (accept 0.95 to 1.20 K) and free-x C1 to be about 0.36 K at
x near 1.94 (accept 1.8 to 2.1). Neither benchmark was met under the planned convention:

- Initial temperature fixed to the first measurement (plan STEP 3): C0 RMS 1.26 K; free-x C1 RMS 0.33 K at x = 2.18.
- Initial temperature also fitted: C0 RMS 1.01 K (within 0.06 K of the target, outside the stated 0.05 K); free-x x = 2.19.

`results/benchmark_probe.txt` lists the variants tried (with and without the t = 0 point, T_room fixed or freed).
None reproduces the prior round. The prior round's code is not a dependency and was not used. The likely causes are
the digitization of the china-pot curve (the dataset records 0.4 C estimated error; the plan cites 0.15 C from the prior
round) and the window selection. This is not resolved. The planned stop-and-debug rule was applied as far as it could be
here. The analysis was then completed, and every in-window number is reported with this failure attached.

## Deviations from the plan

- Profile grid extended from 1.00 to 2.00 to 1.00 to 3.00, because the planned-grid minimum sat at the edge. The
  planned-grid minimum (2.00, at the edge) is recorded in `results/exponent_profile.json`.
- The Langer 30-minute start check: the plan expected curves near 88 C. The digitized curves start at t = 1 min at
  80.2 to 82.3 C. The 88 C figure is the dispensed temperature, so the check was replaced with the observed range.
- The china-pot digitization error: the dataset gives 0.4 C (the plan cited 0.15 C). This artifact uses 0.4 C.
- The C0 model is the x = 1 member of the family, so it is the same fit, not a separate method.

## Limits (stated, not tested)

- Seven in-window points: any interval on x is wide, and the profile is weakly identified.
- Three sources and twelve curves (eight in the dataset artifact plus four digitized Langer curves added here). No humidity, no measured fat-layer series, no cup-geometry variation. These are
  untested, not claimed.
- Only the china-pot curve covers the full 30-minute window. The held-out curves have different start temperatures,
  cup sizes and heat capacities. Differences in x may reflect scale, not physics. Fixed parameters are scale-dependent,
  so a fitted a does not transfer across cups without a per-curve scale. The scale is refit in S2 and fixed in S1.
- The evaporation term is not modelled. The exponent may absorb it. The fat-covered control cannot be run here.
- The Langer 65 C crossing-time conflict (digitized 18 to 32 min, paper text 11 to 22 min) is unresolved. It is not used
  as a validation check.

## Restoring removed files

- `.venv/` (regenerable): `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r pyproject.toml && uv pip install --python .venv/bin/python pymupdf`
- `temp/` (optional, not a delete entry; refetch only if the source PDF is missing): `mkdir -p temp/source && curl -sSL -k -o temp/source/sedlacek_ajp.pdf https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf`

Nothing in `results/` is deleted. It stays on the run's storage volume, not in the published repository, because it is
the only copy of the profile and scores and the analysis cannot be rerun without its inputs.
