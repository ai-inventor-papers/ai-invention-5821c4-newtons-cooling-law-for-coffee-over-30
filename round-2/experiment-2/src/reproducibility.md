# Reproducing the Newton-type cooling results

This folder is one artifact of a public repository. Every path below is relative to this folder.

## 1. Getting the artifact

Clone the public repository and `cd` into this artifact's folder (the folder that contains `method.py`). All paths in this file are relative to it.

## 2. System and Python

- Python 3.12 (the run used CPython 3.12.10). Install it with `uv python install 3.12` or your package manager.
- `uv` (any recent version). The run used uv 0.6.14. Do not use `pip` for installation.
- No GPU, no system packages, no compiler needed. CPU only.
- The run was executed on macOS (Darwin 25.4, Apple silicon). **Ubuntu has not been tested.** The code uses only numpy, scipy and loguru, so it should run unchanged on Linux, but this has not been verified.

## 3. Environment

```
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
```

`requirements.txt` and `pyproject.toml` pin the exact versions installed in the run's `.venv`: numpy 2.2.6, scipy 1.18.1, loguru 0.8.0, plus pandas 3.1.1 and pydantic 2.14.4 (installed but not used by `method.py`) and their transitive dependencies.

## 4. Inputs

- `data/full_data_out.json` (also `data/mini_data_out.json`, `data/preview_data_out.json`). These are copies of the published hot-liquid cooling curves from dataset artifact **`art_-CfKbDAPDpKm`** (folder `gen_art_dataset_1` in the same repository, published as a sibling folder). The copy is included here so the artifact runs without the sibling folder.
- No user-uploaded files are used.
- No downloads, no model weights, no network access.
- No environment variables or API keys are needed. No LLM calls were made (spend: $0).

## 5. Commands, in order

```
# Full run (about 12 s on the run's machine)
.venv/bin/python method.py data/full_data_out.json results

# Smoke test on the mini variant (writes to a scratch folder)
.venv/bin/python method.py data/mini_data_out.json logs/mini_results

# Independent re-derivation of headline numbers and placebo checks
.venv/bin/python audit/rederive.py

# Sensitivity extension: score all ten digitized Langer curves with the frozen planned parameters
# (writes results/sensitivity_langer10.json and the 12-example full_method_out.json; headline numbers unchanged)
.venv/bin/python audit/extend_full_output.py
```

Seeds: the bootstrap and multi-start seed is 0 (`SEED` in `method.py`). Each least-squares fit draws its starts from `default_rng([0, fit_index])`, so the run is deterministic. Bootstrap replicate count: 1000. Multi-start: 20 random starts plus the default start per fit.

The C1 closed form is cross-checked against `scipy.integrate.solve_ivp` (LSODA, rtol 1e-8, atol 1e-10) at the fitted parameters. The maximum difference was 1.6e-6 K (recorded in `results/fold_summary.json`, key `c1_closed_form_validation`).

## 6. Outputs and where they appear

Run outputs (in `results/`; kept on the run's volume, not in the published repository. Regenerate them with the commands above):

- `results/heldout_scores.json`: one row per protocol, fold, ambient, model and curve. Includes fitted parameters, RMS (K) over 0-30 min, signed mean residuals over 0-10 and 10-30 min, the residual against time, and the starts-converged count.
- `results/fold_summary.json`: block-level means, intervals, paired C1 minus C0 differences, fitted parameters, the pre-registered decision rule, metadata (seed, bootstrap count, Langer crossing-time flag, digitisation errors per curve), and the C1 closed-form check.
- `results/method_out.json` (plus `full_method_out.json`, identical, and `mini_method_out.json` and `preview_method_out.json`): per-curve observed data and predictions, in the `exp_gen_sol_out` shape.
- `logs/full_run_stdout.txt`: the printed 30-minute RMS table.

Headline numbers (ambient A, values as recomputed in `audit/rederive_output.txt`):

| Quantity | Value (K) |
|---|---|
| In-sample RMS, Sedlacek, C0 / C1 | 1.26 / 0.33 |
| Held-out Manitoba RMS, C0 / C1 | 3.45 / 2.66 |
| Held-out Langer mean RMS, C0 / C1 | 9.15 / 9.06 |
| Protocol A, all 7 held-out curves, C0 / C1 | 8.33 / 8.14 |
| Paired C1 minus C0 (Protocol A) | -0.19 (interval -0.44 to -0.00) |

The earlier in-sample reference (C0 1.07 K, C1 0.36 K) is printed for comparison only. C1 reproduces it; C0 does not (1.26 K here).

## 7. Reading the outputs

- The pre-registered decision rule is in `fold_summary.json` (`decision_rule`). Read it with its caveats: the paired C1 advantage is not significant under the sign-flip placebo (p = 0.0625; probability 0.23 of "C1 lower on at least 5 of 7 curves" under no difference). See `audit/rederive_output.txt`.
- Several fits end on a parameter bound; the run log names them.

## 8. Restoring removed files

The `.venv/` folder is deleted after the round. To recreate it, run section 3 above.
