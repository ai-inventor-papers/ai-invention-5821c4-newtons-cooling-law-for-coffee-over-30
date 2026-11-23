# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Standardise the digitised Sedlacek & Dolejsi Fig. 1 series into exp_sel_data_out JSON.

Input:  raw/sedlacek_pdf/fig1_digitised_raw.json   (written by scripts/digitise_fig1.py)
Output: data/full_data_out.json                    (one example per digitised time point)
        data/series/<source_id>.json               (same series with its provenance)

Only one series exists in the source PDF, so the output has one dataset group.
Fields the source does not state are null, never estimated.
Run with:  uv run data.py
"""

import json
from pathlib import Path

WS = Path(__file__).resolve().parent
RAW = WS / "raw" / "sedlacek_pdf" / "fig1_digitised_raw.json"
OUT = WS / "data"
SOURCE_ID = "sedlacek_dolejsi_2010_fig1_china_pot"
MEASUREMENT_ERR_C = 0.3


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    digi_err_c = round(abs(raw["calibration_y"]["max_residual_pt"]) / abs(raw["calibration_y"]["b_pt_per_C"]), 2)
    digi_err_min = round(abs(raw["calibration_x"]["max_residual_pt"]) / abs(raw["calibration_x"]["b_pt_per_min"]), 2)

    provenance = {
        "citation": "Sedlacek J., Dolejsi J. (2010). A physical description of coffee cooling in a pot. American Journal of Physics (preprint PDF; journal volume not verified from this run).",
        "url": "https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf",
        "source_type": "peer-reviewed article, figure-digitised (vector markers on PDF page 1, Fig. 1)",
        "pdf_tls_note": "The host serves an incomplete certificate chain; the PDF was fetched with TLS verification disabled. SHA-256 is recorded in README.md.",
        "measurement_error_C": MEASUREMENT_ERR_C,
        "measurement_error_source": "paper text: 'estimated error of our measurement is about 0.3 C' (mercury thermometer)",
        "digitisation_method": "PyMuPDF vector drawings; 29 white-filled square markers on page 1; axes calibrated from centres of tick-label text boxes (x 0-160 min, y 20-90 C); overlay check passed",
        "digitisation_error_C": digi_err_c,
        "digitisation_error_min": digi_err_min,
        "digitisation_error_basis": "max residual of the tick-label linear calibration (y 0.262 pt over 1.258 pt per C; x 0.084 pt over 1.383 pt per min)",
        "digitisation_acceptance": f"accepted: {digi_err_c} C <= 0.5 C threshold",
        "stated_in_source": {
            "time_sampling": "'in every five minutes' (text); read spacing 1-6 min",
            "initial_liquid_temperature_C": "not stated in text",
            "room_temperature_C": "not stated in text",
            "relative_humidity": "not stated in text",
            "cup_mass_or_evaporation_rate": "not stated per time point; Table I gives fitted parameters only",
            "pot_geometry": "not stated in text (china pot shown in Fig. 7, raster)",
            "lid_or_fat_layer": "not stated for this series",
        },
        "series_scope_note": "The only measured curve in the PDF is Fig. 1. Metal-pot, vacuum-pot and water-with-fat series are not published as curves (Table I gives fitted parameters only), so they are not digitised.",
        "earlier_artifact_comparison": "Not performed: the earlier china-pot digitisation (art_-CfKbDAPDpKm) was not available to this executor, so the 0.2 C agreement check was not run.",
        "langer_2018_note": "Langer et al. 2018 (Zenodo 1402983, CC BY 4.0): no raw time series attached; not included. The 65 C crossing-time conflict is not addressed here.",
    }

    examples = []
    for i, p in enumerate(raw["points"]):
        examples.append({
            "input": json.dumps({
                "time_min": p["time_min"],
                "room_temperature_C": None,
                "relative_humidity_pct": None,
                "cup_mass_g": None,
                "pot": "china pot",
                "pot_diameter_cm": None,
                "pot_height_cm": None,
                "pot_volume_ml": None,
                "initial_liquid_temperature_C": None,
                "lid": None,
                "fat_layer": None,
            }, ensure_ascii=False),
            "output": str(p["temp_C"]),
            "metadata_fold": SOURCE_ID,
            "metadata_row_index": i,
            "metadata_task_type": "regression",
            "metadata_time_uncertainty_min": digi_err_min,
            "metadata_output_uncertainty_C": digi_err_c,
            "metadata_measurement_error_C": MEASUREMENT_ERR_C,
            "metadata_time_flag": "t<0: first marker reads 0.3 min before the t=0 tick; kept as read" if p["time_min"] < 0 else "",
        })

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "series").mkdir(exist_ok=True)
    doc = {
        "metadata": {
            "title": "Coffee cooling data from more pots (one measured series)",
            "provenance": provenance,
            "n_series": 1,
            "n_points": len(examples),
            "points_first_30_min": sum(1 for p in raw["points"] if p["time_min"] <= 30),
        },
        "datasets": [{"dataset": SOURCE_ID, "examples": examples}],
    }
    (OUT / "full_data_out.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "series" / f"{SOURCE_ID}.json").write_text(
        json.dumps({"source_id": SOURCE_ID, "provenance": provenance, "points": raw["points"]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"wrote {len(examples)} examples to {OUT / 'full_data_out.json'}")


if __name__ == "__main__":
    main()
