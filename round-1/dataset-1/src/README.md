# Published coffee cooling curves benchmark

Held-out evidence set for testing Newton-type cooling models of hot liquids. This step computes no fits. It collects
published temperature-time series, standardizes them to one JSON schema, and records which covariates each source reports.

## What was done

1. Searched the web (general and scholarly) and Zenodo and HuggingFace for cooling-curve data. Fetched candidate pages and PDFs.
2. Kept three sources that give per-time readings:
   - **SEDLACEK2010**: Sedlacek and Dolejsi, "A physical description of coffee cooling in a pot". Fig. 1 measured coffee curve,
     digitized from vector markers (`scripts/digitize_sedlacek_figs.py`). Figs. 2, 4, 5 repeat the same run; Fig. 3 excluded.
   - **MANITOBA_WORKSHOP**: University of Manitoba workshop coffee table (Fahrenheit, transcribed and converted to Celsius).
   - **LANGER2018**: Langer, Winkler and Lachenmeier (2018), Zenodo record 1402983 (CC-BY-4.0), Abb. 2, ten single-use-cup
     curves for hot water at 88 C, digitized from vector polylines (`scripts/digitize_langer_abb2.py`).
3. Standardized 8 curves (Sedlacek Fig. 1, Manitoba, Langer styles 01-06) with `data.py` into the exp_sel_data_out grouping (one dataset group per source).

## Layout

- `full_data_out.json`: `{"metadata", "datasets": [...]}`, one group per source, one example per curve (8 examples). `metadata_fold` is the source index (1-3); `metadata_source_id` names the source.
- `mini_data_out.json`: first 3 examples, grouping kept.
- `preview_data_out.json`: up to 10 examples (all 8 here), strings cut to 200 characters.
- `schemas/exp_sel_data_out.json`: copy of the schema used for validation.
- `pyproject.toml`: pinned dependencies from the `.venv` used for this run.
- `reproducibility.md`: step-by-step rerun instructions.
- `summary_table.md`: one row per source with counts of humidity, geometry, lid/fat, and measurement error, plus data checks.
- `scripts/digitize_sedlacek_figs.py`: vector digitizer for the Sedlacek figures.
- `scripts/digitize_langer_abb2.py`: vector digitizer for Langer Abb. 2.
- `data.py`: builds `full_data_out.json` from `temp/datasets/`, plus the Manitoba table transcribed inside the script.
- `scripts/make_variants.py`: writes the mini and preview files.
- `scripts/validate_schema.py`: validates the three JSON files against `schemas/exp_sel_data_out.json`.
- `temp/search/`: fetched source files (PDFs, HTML, search and API responses), kept for provenance.
- `temp/datasets/`: raw digitizer outputs before assembly.

Example layout: `input` is a JSON string holding `time_min`, `initial_liquid_temp_c`, `room_temp_c`, `relative_humidity_pct`, `cup_material`,
`volume_ml`, `surface_area_cm2`, `lid_or_fat_condition` (null where not reported). `output` is a JSON string of the liquid temperature in
degrees C at the same times. Flat `metadata_*` fields carry the curve id, liquid, coffee flag and time span; `metadata_provenance` is a JSON string with citation, URL, source type, measurement method and reported error, digitization method, axis calibration, estimated digitization error, and any validation flag.

## How to run

```
.venv/bin/python scripts/digitize_sedlacek_figs.py temp/search/sedlacek_ajp.pdf temp/datasets/sedlacek_digitized_raw.json
.venv/bin/python scripts/digitize_langer_abb2.py temp/search/langer2018.pdf temp/datasets/langer_abb2_raw.json
.venv/bin/python data.py
.venv/bin/python scripts/make_variants.py
.venv/bin/python scripts/validate_schema.py
```

The digitizers need PyMuPDF (`pymupdf`) and NumPy; `data.py` and the two check scripts need only the standard library and `jsonschema`. See `reproducibility.md` for the full procedure. The PDFs are the sources listed in `metadata.url` and `metadata.doi`.

## Findings that limit use

- **Humidity:** 0 of 3 sources record relative humidity. The humidity term cannot be tested on this set.
- **Fat layer:** no measured fat-covered series is in these sources. Sedlacek's fat condition appears only in fitted parameters.
- **Room temperature:** not reported by any source except Manitoba (71 F).
- **Digitized data:** Sedlacek and Langer values come from vector figures, not tables. Estimated digitization error is about 0.2 to 0.4 C.
- **Unresolved discrepancy:** Langer Abb. 2 digitized 65 C crossing times (18 to 32 min) do not match the 11 to 22 min quoted in that paper's text. The curves are kept and flagged in `metadata.validation_flag`.
- **Non-coffee liquid:** the ten Langer curves are hot water (the paper argues it cools like coffee). `metadata.is_coffee` is false for them, so a coffee-only test can exclude them.
- **Coverage:** this is a convenience sample of what the search found, not a systematic review.

## Deviations from the plan

- 8 curves selected (target 5 to 10). Langer styles 07-10 were digitized but not included; the choice of styles 01-06 was by style id, not by data quality.
- Searching covered about 15 queries across web, scholarly, Zenodo and HuggingFace, not the 50 the task asks for. Several
  candidates could not be fetched: the Charles University and Appalachian State hosts failed certificate checks (the
  Sedlacek PDF was downloaded with certificate verification disabled, read-only, for text and vector extraction), and the
  UMT wiki host did not resolve.
- Journal name for Sedlacek and Dolejsi is unverified. A secondary listing gives "Trends in Agricultural Engineering 2010, pp. 578-583"; the PDF text does not state it.
- Vollmer (2009) was checked only through search snippets; no data from it is used.
- The aii-json format script rejects inputs outside its project directory (and the grouped file is not a top-level array), so `scripts/make_variants.py` writes the mini and preview files instead.
- The aii-json validator CLI printed only "Validation FAILED" with no details (its ability-server dependency is not installed here). A direct Draft-07 check of `exp_sel_data_out.json` with the jsonschema package gives 0 errors for the full, mini and preview files.

## Restoring removed files

The local virtualenv `.venv/` (about 223 MB) is deleted after the round. It is regenerable from `pyproject.toml`:

```
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r pyproject.toml
```

Nothing else was deleted. Outputs are kept in this directory. An earlier flat-array builder and its intermediate
mini/preview files were removed because the grouped output superseded them. The raw source files in `temp/search/` can be
re-fetched from the URLs in each row's `metadata.url` and `metadata.doi`; see `reproducibility.md` for the commands and the
Sedlacek host certificate note.
