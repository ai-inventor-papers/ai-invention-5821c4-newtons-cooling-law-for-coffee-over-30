# Reproducing the results

This folder is one artifact of a public repository. Everything here is relative to this folder; no step needs a machine-specific path.

**Platform used for the published run.** macOS 25 on Apple silicon, CPU only (no GPU, no `mps`). The run did not use a GPU; the GPU profile offered for this artifact was not needed. The steps below were run on macOS. A Ubuntu reader should be able to run the same CPU commands, but this has not been tested on Ubuntu.

## 1. Get the artifact

Clone the repository that publishes this artifact, then change into this folder:

```bash
git clone <repository-url> && cd <repository-name>/<this-artifact-folder>
```

The folder contains `method.py`, `src/`, `install.sh`, `run_all.sh`, `pyproject.toml`, `requirements.txt`, `README.md`, and the outputs in `results/`, `figures/`, `data/digitized/`.

## 2. Python and environment

- Python 3.12 (the run used 3.12.10, installed by `uv`).
- `uv` (the run used `uv` 0.6.14). **Do not use `pip`**; install with `uv pip`.

```bash
./install.sh
```

`install.sh` runs `uv venv .venv --python=3.12` and then `uv pip install -r requirements.txt`. The exact versions installed are pinned in `requirements.txt` (30 packages) and mirrored with `==` pins in `pyproject.toml`. The main ones are `numpy==2.5.5`, `scipy==1.18.1`, `pandas==3.1.1`, `matplotlib==3.11.2`, `loguru==0.8.0`, and `pymupdf==2.1`.

The published repository does not include `.venv/` (it is listed in `.aii/manifest.yaml` as regenerable).

## 3. Inputs, downloads and environment variables

- **Source PDF.** `install.sh` downloads `data/source/sedlacek_dolejsi.pdf` from `https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf` with `curl -k`. The `-k` (skip certificate check) was needed on the run machine, because its certificate chain could not be verified. Remove `-k` if your machine verifies it.
- **Uploaded reference materials.** A user uploads folder was checked; it was empty, so no private inputs were used.
- **Environment variables.** None are required. Optionally, `AII_DATA_FIG_GEN` may point to the `chart_gen.py` script of the `aii-data-fig-gen` figure generator. If it is unset, `src/make_figures.py` searches upward from this folder for `.claude/skills/aii-data-fig-gen/scripts/chart_gen.py`. **The figure step needs that generator; the repository does not include it.** Without it, `src/make_figures.py` fails and everything else still runs.
- **No API keys or model downloads.**

## 4. Commands, in order

The full pipeline runs in a few minutes on CPU:

```bash
./install.sh
.venv/bin/python method.py        # same steps as ./run_all.sh
```

`method.py` runs these steps in order, each with fixed seeds (`RNG_SEED = 20260523` in `src/analysis.py`, `default_rng(7)` in `src/run_tests.py`, `default_rng(99)` in `src/audit_headline_numbers.py`):

1. `src/digitize_figures.py`: reads the vector markers and tick labels of the source PDF (Figs. 1–5) and writes `data/digitized/`.
2. `src/paper_curves.py`: samples the source's drawn model curves and scores them against the digitized data.
3. `src/analysis.py`: reproduction gate, candidate fits on the first 30 minutes, metrics, 2000-repeat block bootstrap, sensitivity, selection rule. Writes `results/analysis_results.json` and `results/analysis_tables.csv`.
4. `src/run_tests.py`: validation checks T1–T7, writes `results/tests.json`.
5. `src/make_figures.py`: writes the chart specs and renders three figures (needs the generator, see section 3).
6. `src/write_method_out.py`: writes `method_out.json`.
7. `src/format_outputs.py`: writes `full_method_out.json`, `mini_method_out.json`, `preview_method_out.json`.
8. `src/audit_headline_numbers.py`: independent re-derivation of the headline numbers and placebo checks, writes `results/audit.json`.

Run time on the run machine: the digitization and analysis steps are seconds; the audit's placebo permutation step takes about two minutes.

## 5. Expected outputs and where they appear

| Output | Content | Where in the write-up |
|---|---|---|
| `results/analysis_tables.csv` | 30-minute RMS, bootstrap intervals, χ²/NDF, AIC, BIC per model | results table of the README |
| `results/analysis_results.json` | gate, fits, parameters, residual series, sensitivity, forecast check, selection outcome | the README's tables; the reproduction gate section |
| `results/tests.json` | T1–T7 outcomes (T3, T5, T6 fail, see README) | the README's checks table |
| `results/audit.json` | independent RMS values, C1 minus C0 interval, placebo results | the audit paragraph of the README |
| `method_out.json` (and full/mini/preview) | `exp_gen_sol_out` output: 29 measured points, predictions, all metrics in `metadata` | the machine-readable deliverable |
| `figures/residual_vs_time.pdf` | residual (model minus data) against time, per model | residual figure |
| `figures/rms_30min_forest.pdf` | 30-minute RMS per model with bootstrap half-widths | RMS figure |
| `figures/data_and_fits.pdf` | digitized measurements, fitted curves, drawn curve of the source | data figure |
| `data/digitized/china_digitized.csv` | the primary digitized series (29 points) | input to every number |

Headline values a reader should get (rounded):

- Constant-rate Newton law, 30-minute RMS: 1.07 K; 95% block-bootstrap interval 0.60–1.53 K.
- Nonlinear convection, 30-minute RMS: 0.36 K (in-sample).
- The source's drawn model-1 curve, 30-minute RMS: 2.42 K (not refit).
- Reproduction gate of the source's χ²/NDF: **failed** (the digitized values are 0.03–0.29 of the reported ones). The selection rule was therefore not applied.

## 6. Digitization error

The digitized Fig. 1 series is compared with the same measurements in Figs. 2–5 (`data/digitized/calibration.json`). The median disagreement is 0.15 °C, below the stated 0.3 °C thermometer error, so the 0.3 °C value is used as σ.

## 7. Known limits of this reproduction

- Only the china-pot curve is published as data. The metal and vacuum pots, the fat-covered curve, humidity and pot geometry are not available, so those checks are marked not testable.
- Ambient temperature is not in the source; it is fixed at 20 °C, with a free-ambient sensitivity reported.
- The 30-minute window holds 7 points.
- The block bootstrap uses about 6 blocks in the window, so its intervals are rough. Check T5 (coverage 0.77 for the 3-point blocks) fails, so the intervals should be read as likely too narrow.
- The source's reported χ²/NDF values do not reproduce from its own drawn curves or from refits.
