# Reproducing the published hot-liquid cooling curves benchmark

This file describes what was actually run to produce the outputs in this folder. The work ran on a macOS (Apple silicon)
machine. The procedure below is written for Ubuntu; it has not been run on Ubuntu, and the one pinned package with a
platform-specific build (onnxruntime, pulled in by pymupdf) is the most likely place to differ.

## 1. Getting the artifact

The folder is one folder of a public GitHub repository. Clone the repository, then enter this artifact's folder:

```
git clone <URL-of-the-published-repository> cooling-benchmark
cd cooling-benchmark/<this-artifact-folder>
```

Every path below is relative to this folder. Run all commands from inside it.

## 2. System packages and Python

- Python 3.12 (the run used 3.12.10). On Ubuntu: `sudo apt install python3.12 python3.12-venv`, or install `uv`, which can fetch Python 3.12 itself.
- `uv` (the run used uv 0.6.14): `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- `curl` (to re-fetch sources). No compiler, no GPU, no database.

## 3. Virtual environment and pinned libraries

```
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r pyproject.toml
```

`pyproject.toml` pins every package that was present in the `.venv` used for the run (output of `uv pip freeze`). The
direct dependencies are `numpy==2.2.6`, `pymupdf==2.0` (which pulls in `pymupdf4llm`, `pymupdf-layout` and `onnxruntime`
as listed), and `jsonschema==4.26.0`. `data.py` itself uses only the Python standard library.

Note: the `.venv` was created with `uv venv`, which does not ship `pip`. The `pip freeze` step was done with
`uv pip freeze --python .venv/bin/python`.

## 4. Downloads and credentials

- No API keys, tokens or environment variables are needed. No paid API was called.
- Source files are already in `temp/search/` (published with the repository). Re-fetching them is optional. The exact
  commands used were:

```
curl -sSL -o temp/search/sedlacek_ajp.pdf -k https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf
curl -sSL -o temp/search/manitoba.pdf -k https://server.math.umanitoba.ca/~coopers5/pastcourses_unl_materials/project1_coffee_data.pdf
curl -sSL -o temp/search/langer2018.pdf "https://zenodo.org/api/records/1402983/files/Hei%C3%9Fgetr%C3%A4nke%20Abk%C3%BChlverhalten%20Krebsrisiko.pdf/content"
```

  The `-k` flag turns off TLS certificate verification. It was needed because the Charles University host and the
  Manitoba host presented certificates that the run's curl did not trust. The files are public, read-only downloads
  used for text and vector extraction. Check the downloaded files against `temp/search/` if you need to confirm them.
- The Manitoba table is transcribed inside `data.py` (Fahrenheit values from the handout). `data.py` does not read the PDF.

## 5. Commands, in order

Run from this artifact's folder, after steps 2 to 4.

```
# 5.1 Digitize the Sedlacek and Dolejsi Fig. 1 to 5 markers (vector extraction)
.venv/bin/python scripts/digitize_sedlacek_figs.py temp/search/sedlacek_ajp.pdf temp/datasets/sedlacek_digitized_raw.json

# 5.2 Digitize the Langer et al. Abb. 2 polylines (vector extraction)
.venv/bin/python scripts/digitize_langer_abb2.py temp/search/langer2018.pdf temp/datasets/langer_abb2_raw.json

# 5.3 Build the grouped benchmark file (8 curves: Sedlacek Fig. 1, Manitoba, Langer styles 01-06)
.venv/bin/python data.py

# 5.4 Write the mini and preview variants
.venv/bin/python scripts/make_variants.py

# 5.5 Validate all three JSON files against schemas/exp_sel_data_out.json
.venv/bin/python scripts/validate_schema.py
```

Expected results: step 5.3 prints `wrote full_data_out.json: 3 datasets, 8 examples, excluded ['Abb2-style-07', ..., 'Abb2-style-10']`.
Step 5.5 prints `schema_errors=0` for each file. The digitizers write the raw curves; `data.py` rounds them to 2 decimals.
On the run's machine, the full chain (5.3 to 5.5) took under one second; the digitizers take a few seconds each.
Re-running `data.py` gives a byte-identical `full_data_out.json`.

Seeds, configs and hardware: none are used. There is no randomness and no model training. Hardware: CPU only.

Not used: the aii-json `aii_json_format_mini_preview.py` script could not be run on these files (it accepts only inputs under
the project directory or `/tmp`, and it expects a top-level array). `scripts/make_variants.py` replaces it. The aii-json
validator CLI also did not give details here, so `scripts/validate_schema.py` runs the same schema with `jsonschema`.

## 6. What a reader should get, and where it appears

- `full_data_out.json`: 8 curves in 3 source groups (`SEDLACEK2010` 1 curve, `MANITOBA_WORKSHOP` 1, `LANGER2018` 6).
  Each example's `input` and `output` are JSON strings: `input` holds `time_min`, initial temperature, room temperature
  (null where not reported), cup and volume fields; `output` holds the liquid temperature in degrees C.
- `summary_table.md`: one row per source with the counts used in the decision rule. Sources that record relative humidity:
  0 of 3. Sources that record a measured fat-layer condition: 0 of 3.
- Each example's `metadata_provenance` gives the citation, URL, measurement error and digitization method and error.
- `README.md`: the findings and the deviations from the plan (curve selection, the unresolved Langer discrepancy, the
  search coverage, and the unverified journal name for Sedlacek and Dolejsi).
- No paper or figure uses these numbers yet. The next iteration's held-out test would read `full_data_out.json`
  directly, with `metadata_fold` (the source index) as the fold key.

## 7. Known limits that affect a rerun

- The Langer curves are digitized from vector paths. The paper's text gives 11 to 22 min for the 65 C crossing; the
  digitized curves give 18 to 32 min. This is unresolved and flagged in `metadata_provenance`.
- The Sedlacek Fig. 1 curve has about 5-min spacing and a digitization error estimated at about 0.4 C. The Manitoba
  table is in whole degrees Fahrenheit.
- Re-digitizing from a different PDF rendering, or a different PyMuPDF version, can change the last decimal places.
