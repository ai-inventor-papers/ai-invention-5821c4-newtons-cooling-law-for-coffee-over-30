# Reproducing the cooling-exponent profile (experiment gen_art_experiment_3)

This describes what was actually run to produce the outputs in this folder. Platform: macOS on Apple silicon, CPU only.
Python 3.12. No GPU is used, no API key is needed, and no paid API is called.

## 1. Getting the artifact

This folder is one folder of a public GitHub repository. Clone the repository, then enter this artifact's folder:

```
git clone <URL-of-the-published-repository> cooling-exponent
cd cooling-exponent/<this-artifact-folder>
```

Every path below is relative to this folder. Run all commands from inside it.

## 2. System packages and Python

- Python 3.12 (`requires-python = "==3.12.*"`). Install with `uv`, which can fetch Python 3.12 itself, or with
  `sudo apt install python3.12 python3.12-venv` on Ubuntu.
- `uv` (any recent version): `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- `curl`, to fetch the source PDF (step 4). No compiler, no database.

## 3. Virtual environment and pinned libraries

```
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r pyproject.toml
```

`pyproject.toml` pins the direct dependencies to the exact versions in the run's `.venv`:
`numpy==2.5.5`, `scipy==1.18.1`, `loguru==0.8.0`, `jsonschema==4.26.0`, `pymupdf==2.1`.
The full resolved set from `uv pip freeze --python .venv/bin/python` (for an exact match) was:

```
attrs==26.1.0  flatbuffers==25.12.19  jsonschema==4.26.0  jsonschema-specifications==2025.9.1
loguru==0.8.0  networkx==3.7  numpy==2.5.5  onnxruntime==1.32.0  packaging==26.3  protobuf==7.36.2
psutil==7.2.2  pymupdf==2.1  pymupdf-layout==2.1  pymupdf4llm==2.1  pyyaml==6.0.4  referencing==0.37.0
rpds-py==2026.9.1  scipy==1.18.1  tabulate==0.10.0  typing-extensions==4.16.0
```

`uv pip` was used because the venv has no `pip`. `method.py` and `diagnostics/` use only numpy, scipy, loguru,
jsonschema and pymupdf.

## 4. Inputs, downloads and credentials

- Input dataset: `full_data_out.json` (8 curves in 3 source folds; this run adds the four digitized Langer curves from `temp/datasets/langer_abb2_raw.json`, styles 07-10, copied into `temp/datasets/`, to reach 12 examples), copied into this folder from the dataset artifact
  `art_-CfKbDAPDpKm`. In the published repository that artifact is a sibling folder; a reader can copy its
  `full_data_out.json` here if the file is absent. `data.py` and `reproducibility.md` in the dataset folder regenerate it
  from the digitized sources (see that folder's own instructions).
- Gate check: `method.py` fetches the Sedlacek and Dolejsi PDF from the URL stored in the dataset's provenance block into
  `temp/source/sedlacek_ajp.pdf`. If the fetch fails it copies `temp/search/sedlacek_ajp.pdf` when present. The fetch uses
  `curl -sSL -k` because the host's certificate was not trusted in the run. This is a public read-only download.
- No environment variables and no keys are needed. Nothing is written outside this folder.
- The output schema `schemas/exp_gen_sol_out.json` is copied into this folder from the aii-json skill.

## 5. Commands, in order

Run from this folder, after steps 2 to 4.

```
# 5.1 Analysis: benchmark and synthetic checks, fixed-x fits, x profile, bootstrap, held-out scoring,
#     gate provenance, and writing of results/ and method_out.json (+ mini and preview variants)
.venv/bin/python method.py            # about 5 to 6 minutes on CPU; writes logs/run.log

# 5.2 Benchmark convention probe (diagnostic, used to debug the benchmark gate)
.venv/bin/python diagnostics/benchmark_probe.py > results/benchmark_probe.txt

# 5.3 Independent re-derivation of the headline numbers (ODE integration and Nelder-Mead, not the closed form)
.venv/bin/python diagnostics/audit_headline.py > results/audit_headline.json
```

Seeds: the bootstrap uses `numpy.random.default_rng(20260523)`; the shuffled placebo in 5.3 uses seed 7. There is no
other randomness. Hardware: CPU only (Apple silicon). Runtime: `method.py` about 5 to 6 minutes; the audit about 1 minute.

Expected numbers (check against `results/`):

- Benchmark: C0 in-window RMS 1.261 K (planned T0 convention; the prior-round target 1.07 K was NOT reproduced, see
  `results/benchmark_probe.txt`). Free-x in-window x = 2.18, RMS 0.33 K (prior-round target 1.94 NOT reproduced).
- Profile minimum on the 1.00 to 3.00 grid: x = 2.18. Δχ² = 3.84 interval (sigma 0.3 C): [1.95, 2.42].
- Bootstrap (200 moving blocks of 3): median 2.21, 95% percentile interval [2.03, 2.36], 0% degenerate.
- Held-out: Manitoba S1 RMS 3.66 K (C0), 2.82 K (x = 2.18). S2 mean RMS over 11 usable curves: C0 0.64 K, x = 2.18 0.60 K.
- Synthetic recovery: x within 0.1 in 94% (x_true 1.25) and 98% (x_true 1.94) of 50 draws. Closed form vs `solve_ivp`:
  about 3e-10 K.
- Gate: 32.1, 2.4 and 1.0 found near "chi" in the PDF text; 81.3 not near "chi" (unverified); gate status conditional.
- `results/audit_headline.json`: independent recomputation agrees with `method.py` (C0 RMS within 0.02 K, free x within
  0.05); placebo (shuffled times) C0 RMS 13.5 K.

## 6. Output files and where they go

- `results/exponent_profile.json`: fixed-x table with residuals against time, profile over x, free-x fits, bootstrap,
  and comparison with prior-round values (cited, not recomputed). Use for the benchmark and profile sections.
- `results/heldout_scores.json`: S1 and S2 per curve for C0 (x = 1) and C1 at each x, with the C1 minus C0 summary and
  sign counts. Use for the held-out section.
- `results/gate_provenance.json`: gate values with page and quote, status per value. Use for the reproduction-gate note.
- `results/benchmark_checks.json`: synthetic recovery, closed form vs `solve_ivp`, and the benchmark under both T0
  conventions. Use for the testing section.
- `results/benchmark_probe.txt`, `results/audit_headline.json`: diagnostic and audit outputs.
- `method_out.json` (validated against `schemas/exp_gen_sol_out.json`, 0 errors), with `full_method_out.json` (same
  content), `mini_method_out.json` (first example of each source) and `preview_method_out.json` (mini, strings cut at 200
  characters).

## 7. Known limits that affect a rerun

- The china-pot curve is digitized from a figure. The dataset records 0.4 C digitization error (the earlier round
  cited about 0.15 C). Re-digitizing from a different PDF rendering can change the in-window numbers.
- The benchmark targets from the prior round were not reproduced, and the cause is not established. Do not treat the
  in-window numbers here as validated against that round.
- Seven in-window points: the x interval is wide and the profile is weakly identified.
- The Langer 65 C crossing-time conflict in the dataset is unresolved and is not used as a check.
