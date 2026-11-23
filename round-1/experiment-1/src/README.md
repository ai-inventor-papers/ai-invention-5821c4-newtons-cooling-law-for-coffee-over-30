# Newton's law of cooling on published coffee-cooling curves

**Question.** How accurately does Newton's law of cooling predict the temperature of a cup of coffee over 30 minutes, compared with published measurements?

**Short answer.** On the one published china-pot curve we could digitize, the constant-rate Newton law (C0) fitted to the first 30 minutes has an in-sample RMS error of about 1.1 K (95% block-bootstrap interval 0.6–1.5 K). Its errors are systematic: it underpredicts heat loss early (mean model-minus-data +0.6 K over the first 10 min) and overpredicts it late (−0.9 K over 20+ min). The source's own drawn model-1 curve (a Newton fit by the authors, presumably over the whole record) has a 30-minute RMS of 2.4 K when scored here. A nonlinear convection law (C1, exponent about 1.9 in the window, 1.7 over the full record) reduces the in-sample RMS to 0.36 K.

**The source's own statistics do not reproduce.** The reproduction gate failed (see *Reproduction gate*). The pre-registered selection rule was therefore **not applied**; the C1 result above is descriptive and in-sample only.

Source: Sedláček and Dolejší, "A physical description of coffee cooling in a pot" (4 pages), <https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf>. No new laboratory data were collected. CPU only; no GPU was used.

## What was done

1. **Digitization** (`src/digitize_figures.py`). The source's figures are vector PDF drawings. Each measured point is a 2.4 pt square marker, so its centre is read exactly and mapped to (t, T) by least-squares fits to the tick-label centres.
   - Fig. 1 (the china-pot curve, markers only): 29 points, t from 0 to 138.9 min, T from 79.7 to 27.9 °C.
   - Axis calibration residuals: 0.03 min in time and 0.07 °C in temperature.
   - Cross-check: the same 29 measurements are plotted in Figs. 2–5. Median RMS disagreement against Fig. 1 is 0.15 °C (per-figure RMS 0.01–0.25 °C). This is below the stated 0.3 °C thermometer error, so σ = 0.3 °C is used throughout.
   - The first marker is placed at t = 0 (a −0.30 min calibration offset is removed).
2. **Source model curves** (`src/paper_curves.py`). The source's drawn model curves (Bezier paths in Figs. 2–5) were sampled and scored against the digitized data. This separates a problem in the source's statistics from a problem in our data.
3. **Candidate models** (`src/models.py`, `src/analysis.py`), fitted on the first 30 minutes:
   - **C0** constant-rate Newton law, `dT/dt = −a (T − T_room)`, closed form.
   - **C1** nonlinear convection, `dT/dt = −a (T − T_room)^x`, closed form (checked against `solve_ivp`).
   - **C2** convection plus evaporation, plan form, `dT/dt = −[a (T − T_room)^x + b (T^z − T_room^z)]`.
   - **C2p** the source's evaporation form, `b T^z` with no ambient term.
   - **C2_fixed_x** C2 with x fixed at 1.25 (fallback F4).
   - **C3** humidity-deficit evaporation: *not testable*. The source does not record humidity.
   - **C4** surface-to-volume geometry check: *not testable*. Pot dimensions are not given in the text, and the metal and vacuum curves are not published as data.
4. **Uncertainty** (`analysis.py`). Residual block bootstrap over 5-minute blocks, 2000 repeats, no refit. The 30-minute window contains only **6 blocks**, so these intervals are rough.
5. **Validation tests** (`src/run_tests.py`, results in `results/tests.json`). See *Checks*.
6. **Figures** (`src/make_figures.py`), rendered with the aii-data-fig-gen generator from JSON specs in `figures/specs/`.
7. **Output** `method_out.json` in the `exp_gen_sol_out` format. It validates against that schema. The 29 measured points are the examples, and all metrics are in `metadata`.

## Results

### 30-minute window (0–30 min, 7 points, last point at 25.9 min)

The window holds 7 points, not 30 min of measurements. The next digitized point is at 30.7 min. All numbers are in-sample.

| Model | Params | RMS 30 min (K) | 95% block-boot. CI (K) | Mean resid. 0–10 min (K) | Mean resid. ≥20 min (K) | χ²/NDF (σ=0.3 °C) | AIC | BIC |
|---|---|---|---|---|---|---|---|---|
| C0 constant-rate (baseline) | 1 | **1.07** | 0.60–1.53 | +0.62 | −0.87 | 14.8 | 2.9 | 2.9 |
| C1 nonlinear convection | 2 | 0.36 | 0.10–0.56 | −0.11 | +0.09 | 2.0 | −10.3 | −10.4 |
| C2 plan form (b → 0) | 4 | 0.36 | 0.10–0.56 | −0.11 | +0.09 | 3.3 | −6.3 | −6.6 |
| C2_fixed_x (x = 1.25; a at lower bound, b ≈ 0) | 3 | 0.37 | 0.11–0.58 | −0.12 | +0.08 | 2.7 | −7.8 | −7.9 |
| C2p source evaporation form (b → 0) | 4 | 0.36 | 0.10–0.56 | −0.11 | +0.09 | 3.3 | −6.3 | −6.6 |
| Source's drawn model 1 (Fig. 2, not refit) | 1 | 2.42 | — | +0.99 | +2.49 | 76.0 | 14.4 | 14.3 |

Fitted values: C0 has a = 0.0263 min⁻¹ with T_room = 20 °C. C1 has a = 7.1 × 10⁻⁴ and x = 1.94. In C2 the evaporation coefficient collapses to zero; the exponent and rate are the same as C1, so evaporation is not identifiable from this window.

Reading the table: AIC and BIC favour C1 over C0 by about 13 units, the same ranking as χ²/NDF. Both rest on seven points.

### Full record (reproduction and sensitivity; 29 points, 0–139 min)

| Fit | Result | RSS/NDF (K²) |
|---|---|---|
| C0, T_room = 20 °C | a = 0.0198 min⁻¹ | 9.18 |
| C0, T_room free | T_room = 28.4 °C, a = 0.0298 min⁻¹ | 0.84 |
| C1, T_room = 20 °C | x = 1.68 | 0.072 |
| C1, T_room free | x = 1.82, T_room = 17.9 °C | 0.066 |
| C2 plan form | b → 0, z at bound 6 | 0.065 |

With σ = 0.3 °C, the full-record C1 gives χ²/NDF ≈ 0.8, consistent with the measurement error. The free-ambient C0 fits well only with an unphysical ambient of 28 °C. The 30-minute constant-rate misfit therefore depends on the assumed ambient temperature and on whether the exponent is free. Ambient temperature is not identifiable from the 30-minute window alone (fitting it there drives it to its 35 °C bound).

### Forecast check (exploratory)

Fit on t ≤ 15 min (4 points), predict 15–30 min (3 points): C0 RMS 2.9 K, C1 RMS 0.9 K. This is too few points to support a ranking.

## Reproduction gate (FAILED)

The plan required the source's χ²/NDF values (32.1, 2.4, 81.3, 1.0) to be reproduced within 30% before candidates were ranked. They were not:

| Check | Digitized value | Source value | Ratio |
|---|---|---|---|
| Model 1, drawn curve, RSS/NDF | 3.24 | 32.1 | 0.10 |
| Model 2, drawn curve | 0.69 | 2.4 | 0.29 |
| Model 3, drawn curve | 8.08 | 81.3 | 0.10 |
| Model 4, drawn curve | 0.25 | 1.0 | 0.25 |
| Model 1, own refit (T_room = 20 °C) | 9.18 | 32.1 | 0.29 |
| Model 2, own refit (T_room = 20 °C) | 0.072 | 2.4 | 0.03 |

The source's own drawn curves, digitized from its figures, do not reproduce its reported χ²/NDF under the stated convention (sum of squared residuals over degrees of freedom, unit σ). The ratio is not constant across models, so no single rescaling explains the gap. The likely causes are a different χ² definition, different ambient temperature or initial value in the source's spreadsheet, or different data. The source gives none of these, so the gap cannot be resolved from the paper alone.

Because the gate failed, the **selection rule was not applied**. For transparency, the rule was evaluated anyway: C1 would pass it (lowest 30-min RMS among candidates within χ²/NDF 1 of the best, 66% RMS reduction over C0, bootstrap interval for the difference excludes zero). It is reported as descriptive only.

## Checks

| Test | Result | Note |
|---|---|---|
| T1 synthetic recovery of the baseline rate | pass | recovers a within 0.1%; 96% of estimates within 2 SD |
| T2 sign convention | pass | under a nonlinear truth (x = 1.34), the constant-rate law is positive early and negative late, as expected |
| T3 reproduction gate | **FAIL** | see above |
| T4 solver vs closed form | pass | max relative error 1 × 10⁻⁹ |
| T5 block-bootstrap coverage | **FAIL** | 0.77 coverage with 3-point blocks under AR(1) ρ = 0.6 (target 0.95); iid bootstrap 0.65. Window intervals are therefore likely too narrow |
| T6 C0 residual vs digitization error | **FAIL** | C0 RMS is 7× the 0.15 °C digitization error. We interpret this as the constant-rate law's real misfit, since the source's own drawn curve shows the same early-under, late-over pattern. Digitization is not the cause (see cross-check). This is a deviation from the plan's reading of T6 |
| T7 selection dry run | pass | forcing all extensions equal to C0 returns C0 |

## Not testable, and deviations from the plan

- **Cross-pot check and C4 geometry.** The source publishes measured curves only for the china pot. Metal and vacuum pots appear only as fitted parameters in its Table I. Pot dimensions are not given, so S/V cannot be computed. Not testable here.
- **Fat-covered control.** The source reports a fitted evaporation coefficient for water with fat (Table I: v = 1.94 vs 15.8 × 10⁻¹¹ for coffee), but no fat-covered curve. We did not test it. The source's parameters are quoted only for context.
- **C3 humidity.** Not testable; humidity is not recorded.
- **Window.** The 30-minute window has 7 points, ending at 25.9 min.
- **Ambient temperature.** Not reported in the source. Fixed at 20 °C (the lower axis limit), with a free-ambient sensitivity. The 30-minute result depends on this choice.
- **Source model 3 and 4 curves.** The source's full model includes pot and radiation terms whose constants are not in the text. Our C2 and C2p are reduced forms, not reproductions.
- **Initial value.** T0 is the first measured temperature, not a fitted parameter.
- **Heat capacity.** Absorbed into the fitted coefficients, so C0 and C1 coefficients are rates, not physical heat-transfer coefficients.

## Layout

| Path | Contents |
|---|---|
| `src/digitize_figures.py` | vector marker digitization and axis calibration |
| `src/paper_curves.py` | sampling and scoring of the source's drawn model curves |
| `src/models.py` | C0, C1 and C2 ODEs; closed forms; solver |
| `src/analysis.py` | reproduction gate, candidate fits, metrics, bootstrap, selection rule |
| `src/run_tests.py` | validation checks T1–T7 |
| `src/make_figures.py` | chart specs and rendering with the aii-data-fig-gen generator |
| `src/write_method_out.py` | writes `method_out.json` |
| `src/format_outputs.py` | writes full, mini and preview versions of the output |
| `src/audit_headline_numbers.py` | independent re-derivation and placebo checks (`results/audit.json`) |
| `method.py` | entry point: runs all steps in order |
| `reproducibility.md` | step-by-step reproduction |
| `pyproject.toml` | project metadata with pinned dependencies |
| `data/source/sedlacek_dolejsi.pdf` | source PDF (fetched from the URL above) |
| `data/digitized/` | `china_digitized.csv` (primary series), `fig{1..5}_*_points.csv`, `calibration.json`, `paper_model_curves.csv`, `paper_curve_scores.json` |
| `method_out.json` | `exp_gen_sol_out` output: 29 examples, all metrics in `metadata` (schema-valid) |
| `full_method_out.json`, `mini_method_out.json`, `preview_method_out.json` | full copy, first 3 examples, and preview with strings cut at 200 characters |
| `results/audit.json` | independent re-derivation of headline numbers, with placebo checks |
| `results/analysis_results.json` | full analysis output (gate, fits, residual series, bootstrap, sensitivity) |
| `results/analysis_tables.csv` | summary table of the window metrics |
| `results/tests.json` | outcomes of checks T1–T7 |
| `figures/` | `residual_vs_time`, `rms_30min_forest`, `data_and_fits` (PDF and PNG) and `specs/` (JSON specs) |
| `logs/` | run logs |
| `run_all.sh`, `method.py` | run the full pipeline (a few minutes on CPU) |
| `install.sh` | restores the environment (`.venv`) and the source PDF |
| `requirements.txt` | pinned Python packages |
| `.aii/manifest.yaml` | storage decisions for heavy paths |

## How to run

```bash
./install.sh              # creates .venv and downloads the source PDF
.venv/bin/python method.py # digitize, score, fit, test, figure, format, audit
```

See `reproducibility.md` for the exact steps, versions and seeds.

## Independent audit

`src/audit_headline_numbers.py` re-reads the PDF directly, solves the models by fixed-step RK4 and Nelder-Mead rather than the closed form and `least_squares`, and rebuilds the published curve by de Casteljau subdivision. The 30-minute RMS values agree with the main analysis to within 0.003 K: constant-rate law 1.067 vs 1.067 K, nonlinear convection 0.359 vs 0.359 K, published curve 2.419 vs 2.422 K.

Placebo checks: C0 against itself gives a block-bootstrap difference interval of [0, 0]. Permuting the measured temperatures across the window and refitting both models gives a median relative RMS improvement of 0.03 (maximum 0.19), against 0.66 for the real data (permutation p = 0.01).

## Restoring removed files

Heavy paths marked `delete` in `.aii/manifest.yaml` can be restored as follows.

- `.venv/` (Python environment, regenerable): `./install.sh`, or `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.txt`
- `src/__pycache__/` (bytecode cache, regenerable): produced automatically when `./run_all.sh` runs
