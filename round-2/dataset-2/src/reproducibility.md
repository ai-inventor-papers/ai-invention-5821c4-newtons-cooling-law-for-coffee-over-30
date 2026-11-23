# Reproducing the coffee-cooling dataset

What this folder contains: one measured cooling curve (china pot, coffee) digitised from Fig. 1 of Sedlacek & Dolejsi, standardised to `exp_sel_data_out`, plus a search log for humidity or cup-mass series (none found).

## 0. Getting this artifact

The workspace is published as one folder of a public GitHub repository. Clone the repository, then `cd` into this folder (`gen_art_dataset_2/`). Every path below is relative to that folder.

## 1. Environment

- Python 3.12 (the run used CPython 3.12.14).
- No GPU, no API keys, no OpenRouter spend. The whole pipeline is CPU work and runs in seconds.
- Packages are pinned in `pyproject.toml`: `pymupdf==2.0`, `jsonschema==4.26.0`, plus the transitive pins from `uv pip freeze`.

```
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r pyproject.toml
```

Or install the pins directly: `uv pip install --python .venv/bin/python "pymupdf==2.0" "jsonschema==4.26.0"`.

Note on the platform: the run was executed on macOS (Apple silicon, Darwin 25.4), not on Ubuntu. The commands are plain Python and should work on Ubuntu, but that has not been tested here.

## 2. Input download (not published)

The source PDF is kept in `raw/sedlacek_pdf/` (140 KB, under the auto-keep floor). If it is missing, fetch it:

```
mkdir -p raw/sedlacek_pdf
curl -sSL --insecure -o raw/sedlacek_pdf/sedlacek_ajp.pdf https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf
```

The host serves an incomplete certificate chain, so the download needs `--insecure`. Check the file's SHA-256 against `a0bbc421f62f4ac0110dff03780b19aaa8d8a2fe421eaf7319f1b414953b8d13`. The download is unverified because TLS verification is off.

No user-uploaded inputs were used. No other artifact's output was read.

## 3. Commands, in order

```
# (a) digitise Fig. 1 from the PDF's vector markers; writes calibration and 29 points
.venv/bin/python scripts/digitise_fig1.py raw/sedlacek_pdf/sedlacek_ajp.pdf raw/sedlacek_pdf/fig1_digitised_raw.json

# (b) standardise to exp_sel_data_out; writes data/full_data_out.json and data/series/
uv run data.py

# (c) mini (first 3 examples) and preview (strings truncated to 200 characters)
.venv/bin/python scripts/make_variants.py

# (d) schema check with jsonschema against scripts/exp_sel_data_out.json (copy of aii-json schema)
.venv/bin/python scripts/validate_schema.py data/full_data_out.json
.venv/bin/python scripts/validate_schema.py data/mini_data_out.json
.venv/bin/python scripts/validate_schema.py data/preview_data_out.json
```

Set `AII_JSON_SCHEMA=/path/to/aii-json/schemas/exp_sel_data_out.json` to validate against another copy of the schema.

The aii-json CLI scripts were tried and refused the workspace path. They returned "Validation FAILED" with no details, and the format script refused its input path. The results above therefore come from the local scripts, not from the aii-json CLI.

Seeds: none (no randomness). Hardware: CPU only. Runtime: under 10 seconds in total.

## 4. What a reader should get

- `raw/sedlacek_pdf/fig1_digitised_raw.json`: 29 points (time in min, temperature in C). Calibration residuals: x 0.084 pt (0.06 min), y 0.262 pt (0.21 C).
- `data/full_data_out.json`: 29 examples in one dataset group, `sedlacek_dolejsi_2010_fig1_china_pot`. Each example: `input` (JSON string with time and null fields for initial temperature, room temperature, humidity, mass, geometry), `output` (liquid temperature as a string), `metadata_*` fields.
- `data/mini_data_out.json` and `data/preview_data_out.json`: first 3 examples.
- `variables_per_series.md`: accept or reject reason for each source read. Only one series is accepted.
- `search_log.md`: 14 queries, 6 sources read, 4 blocked (HTTP 403).

Expected checks: 29 examples; 7 points in the first 30 minutes; 0 schema errors in all three files.

## 5. Use in a paper

No paper or figure in this run uses these numbers yet. When one does, cite the source paper (Sedlacek & Dolejsi), not the digitisation.

## Limits

- Fig. 1 is the only published measured curve in the PDF. The metal-pot, vacuum-pot and water-with-fat series are not published as curves, so they are not in the data.
- No humidity, cup-mass or initial-temperature values are available in any accepted series.
- The earlier china-pot digitisation was not compared (its workspace was not available).
