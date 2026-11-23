# Coffee cooling data: one measured series, and a search for humidity or mass series

## What was done

1. **Digitised the only measured curve in the Sedlacek & Dolejsi PDF.** Fig. 1 (china pot, coffee, read every ~5 min, stated thermometer error 0.3 C) is drawn as vector markers, so 29 points were recovered directly from the PDF drawing data. The axes were calibrated from the tick labels. The overlay on the rendered figure confirms every point sits on the curve. Digitisation error is 0.21 C (y) and 0.06 min (x).
2. **Searched for humidity or cup-mass series.** 14 queries, 6 sources read, 4 blocked (HTTP 403). None qualified (see below).
3. **Standardised to `exp_sel_data_out`** and validated against the schema. There is one example per time point. Inputs the source does not state are `null`, not estimated.

## Corrections to the plan's premise

- The plan expected metal-pot, vacuum-pot and water-with-fat curves in the PDF figures. They are **not**. The paper gives only fitted parameters for those (Table I). Figs. 6 and 7 are raster and not time series. Those series are therefore not in this dataset.
- The paper gives no initial liquid temperature, no room temperature, no relative humidity, no cup mass per time point and no pot geometry. Those fields are `null` in the data.
- The earlier china-pot digitisation (`art_-CfKbDAPDpKm`) was not available to this executor, so the 0.2 C agreement check was **not** run. The series here is an independent re-digitisation.

## Layout

- `data/full_data_out.json`: all 29 points in `exp_sel_data_out` form, with the provenance block in top-level `metadata`.
- `data/mini_data_out.json`: first 3 examples.
- `data/preview_data_out.json`: mini with strings truncated to 200 characters.
- `data/series/sedlacek_dolejsi_2010_fig1_china_pot.json`: the same series with its provenance, one file per accepted series.
- `variables_per_series.md`: one row per source or series read, with variables, points in the first 30 min, digitisation error and the accept or reject reason.
- `search_log.md`: the 14 queries and the sources read or blocked.
- `raw/sedlacek_pdf/fig1_digitised_raw.json`: the digitised points and calibration residuals (kept).
- `raw/sedlacek_pdf/sedlacek_text.txt`: extracted PDF text (kept).
- `raw/sedlacek_pdf/render/`: rendered figure and overlay check (small PNGs).
- `scripts/digitise_fig1.py`: vector-marker digitiser. Usage: `python scripts/digitise_fig1.py <pdf> <out.json>`.
- `data.py` (repo root, uv inline script): standardises the digitised points into `data/full_data_out.json` and the per-series file. Run with `uv run data.py`.
- `scripts/make_variants.py`: builds mini and preview from the full file.
- aii-json CLI note: the `aii_json_validate_schema.py` and `aii_json_format_mini_preview.py` scripts refuse paths outside the project directory and /tmp, and the validator returned FAILED with no detail. Validation and variants were therefore done with `scripts/validate_schema.py` and `scripts/make_variants.py`, which use the same schema file and the same rules.
- `scripts/validate_schema.py`: schema check with `jsonschema` against `scripts/exp_sel_data_out.json`, a copy of the aii-json schema.
- `scripts/exp_sel_data_out.json`: schema copy used by the validator.

## Run steps

```
# 1. digitise from the kept PDF (raw/sedlacek_pdf/; re-fetch if missing, see "Restoring removed files")
python scripts/digitise_fig1.py raw/sedlacek_pdf/sedlacek_ajp.pdf raw/sedlacek_pdf/fig1_digitised_raw.json
# 2. build, make variants, validate
uv run data.py
python scripts/make_variants.py
python scripts/validate_schema.py data/full_data_out.json
```

Use an environment with `pymupdf` and `jsonschema`.

## Statement on humidity and mass

**No series found in 14 queries among 6 sources read (4 further sources were blocked with HTTP 403).** No accepted series records relative humidity, vapour pressure, evaporation rate or cup mass per time point. This is an absence in what was searched. It is not a claim that none exists. The IOP full texts (two DOIs) and the ScienceDirect paper-cup study may hold such data. They could not be read from here.

## Limits

- Times are read from the figure. The first marker reads -0.3 min, so the t=0 point is about 0.3 min early. It is kept as read and flagged per example. The time spacing jitters by up to about 1 min around the 5-min sampling.
- The temperature uncertainty of 0.21 C comes from the calibration residual. Read as a digitisation error, it is well under the 0.5 C cut-off.
- Only the china-pot curve is accepted. It is a single series, below the plan's target of 6 datasets.
- The Langer 2018 Zenodo record (CC BY 4.0) has no raw series attached, so it is not included. The Manitoba coffee table series was not re-fetched. The plan marked both optional. The Langer 65 C crossing-time conflict is not resolved here.

## Restoring removed files

- `.venv/` (regenerable, excluded from the repository):
  ```
  uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r pyproject.toml
  ```

The source PDF `raw/sedlacek_pdf/sedlacek_ajp.pdf` (140 KB) is under the auto-keep floor and is kept in place, so it needs no restore step. If it is missing, re-fetch it with `curl -sSL --insecure -o raw/sedlacek_pdf/sedlacek_ajp.pdf https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf`. The host's certificate chain is incomplete, so verified downloads fail. The SHA-256 of the copy used here is `a0bbc421f62f4ac0110dff03780b19aaa8d8a2fe421eaf7319f1b414953b8d13`.

## Provenance

- Sedlacek J., Dolejsi J., "A physical description of coffee cooling in a pot" (AJP preprint PDF). URL: https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf. The journal volume was not verified from this run.
- Figure-digitised series. Measurement error 0.3 C, from the paper's text.
