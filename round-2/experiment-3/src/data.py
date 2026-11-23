# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Standardize the hot-liquid cooling curves to the exp_sel_data_out schema.

Grouping: one dataset group per independent source (held-out fold unit).
Example: one cooling curve (one measured trace). Input and output are JSON strings
(the schema requires strings). Per-example metadata uses flat metadata_* fields.

Sources (inputs in temp/datasets/ and the transcribed Manitoba table below):
  SEDLACEK2010   Fig. 1 measured coffee curve, digitized from vector markers (scripts/digitize_sedlacek_figs.py)
  MANITOBA_WORKSHOP  coffee workshop table, Fahrenheit transcribed from temp/search/manitoba.pdf
  LANGER2018     Abb. 2 single-use-cup curves, digitized from vector polylines (scripts/digitize_langer_abb2.py)

Selection to 8 curves (plan target 5-10): Sedlacek Fig. 1 (1) + Manitoba (1) + Langer Abb. 2 styles 01-06 (6).
Langer styles 07-10 are kept in temp/datasets/langer_abb2_raw.json and listed as excluded in the output metadata.

Run:  uv run data.py
"""

import json
from pathlib import Path

WS = Path(__file__).resolve().parent
RAW = WS / "temp" / "datasets"
OUT = WS / "full_data_out.json"

MANITOBA_F = [(0, 186), (1, 179), (2, 175), (3, 171), (8, 156), (13, 144), (18, 135), (23, 127),
              (28, 120), (33, 116), (38, 111), (43, 107), (48, 104)]
MANITOBA_ROOM_F = 71
LANGER_KEEP_STYLE_IDS = {f"Abb2-style-{i:02d}" for i in range(1, 7)}
LANGER_EXCLUDED_NOTE = "not in the 8-curve selection (cap at target); full digitization kept in temp/datasets/langer_abb2_raw.json"


def f_to_c(f: float) -> float:
    return round((f - 32.0) * 5.0 / 9.0, 2)


def make_example(curve_index: int, fold: int, source_id: str, time_min: list, temp_c: list,
                 input_meta: dict, meta: dict) -> dict:
    assert len(time_min) == len(temp_c) >= 10, f"{source_id}: bad lengths"
    assert all(a < b for a, b in zip(time_min, time_min[1:])), f"{source_id}: time not increasing"
    t = [round(float(x), 2) for x in time_min]
    T = [round(float(x), 2) for x in temp_c]
    inp = {
        "time_min": t,
        "initial_liquid_temp_c": T[0],
        "room_temp_c": input_meta.get("room_temp_c"),
        "relative_humidity_pct": None,
        "cup_material": input_meta.get("cup_material"),
        "volume_ml": input_meta.get("volume_ml"),
        "surface_area_cm2": None,
        "lid_or_fat_condition": input_meta.get("lid_or_fat_condition"),
    }
    return {
        "input": json.dumps(inp, ensure_ascii=False),
        "output": json.dumps(T),
        "metadata_fold": fold,
        "metadata_source_id": source_id,
        "metadata_curve_id": meta.pop("curve_id"),
        "metadata_curve_index": curve_index,
        "metadata_liquid": meta["liquid"],
        "metadata_is_coffee": meta["is_coffee"],
        "metadata_time_span_min": [t[0], t[-1]],
        "metadata_n_points": len(t),
        "metadata_provenance": json.dumps(meta, ensure_ascii=False),
    }


def sedlacek_examples() -> list:
    raw = json.loads((RAW / "sedlacek_digitized_raw.json").read_text(encoding="utf-8"))
    pts = raw["Fig. 1"]["points"]
    # First marker sits at -0.36 min from axis-calibration error; clamp to 0.
    t = [max(0.0, p["time_min"]) for p in pts]
    T = [p["temp_c"] for p in pts]
    meta = {
        "curve_id": "SEDLACEK2010_Fig1",
        "liquid": "coffee", "is_coffee": True,
        "source_type": "article (venue unverified; secondary listing Trends in Agricultural Engineering 2010, pp. 578-583)",
        "citation": "Sedlacek J., Dolejsi J. A physical description of coffee cooling in a pot.",
        "url": "https://ipnp-web.troja.mff.cuni.cz/~dolejsi/outreach/sedlacek_ajp.pdf",
        "figure": "Fig. 1 measured cooling of coffee in a china pot on a table",
        "cup_material": "china pot", "volume_ml": None, "room_temp_c": None,
        "lid_or_fat_condition": "open; no measured fat-layer series",
        "room_temp_note": "not reported", "humidity_note": "not reported",
        "sampling_interval_min": "about 5 (stated); digitized marker times",
        "measurement_method": "mercury thermometer (stated)",
        "measurement_error_c": 0.3,
        "digitization": {
            "method": "vector marker extraction, scripts/digitize_sedlacek_figs.py",
            "axis_calibration": "tick-label centres: t=0 and 160 min; T=20 and 90 C",
            "estimated_error_c": 0.4,
        },
        "validation": "Figs 2, 4, 5 repeat this run (mean abs diff 0.02-0.16 C); Fig 3 excluded (different trace, irregular times)",
    }
    return [make_example(1, 1, "SEDLACEK2010", t, T,
                         {"room_temp_c": None, "cup_material": "china pot", "volume_ml": None,
                          "lid_or_fat_condition": "open; no measured fat-layer series"}, meta)]


def manitoba_examples() -> list:
    t = [float(a) for a, _ in MANITOBA_F]
    T = [f_to_c(b) for _, b in MANITOBA_F]
    meta = {
        "curve_id": "MANITOBA_WORKSHOP_coffee",
        "liquid": "coffee", "is_coffee": True,
        "source_type": "teaching lab report / workshop handout (not peer reviewed)",
        "citation": "University of Manitoba, Project 1: Measuring Temperature & Newton's Law of Cooling, Coffee Experiment Data.",
        "url": "https://server.math.umanitoba.ca/~coopers5/pastcourses_unl_materials/project1_coffee_data.pdf",
        "figure": "table",
        "cup_material": "not reported", "volume_ml": None,
        "room_temp_c": f_to_c(MANITOBA_ROOM_F),
        "lid_or_fat_condition": "not reported",
        "room_temp_note": "71 F, converted with C = (F - 32) x 5/9",
        "humidity_note": "not reported",
        "sampling_interval_min": "steps of 1, 1, 1, then 5 min",
        "measurement_method": "not reported",
        "measurement_error_c": 0.28,
        "measurement_error_note": "whole degrees F; half-degree quantization (not stated by source)",
        "unit_conversion": "T_C = (T_F - 32) * 5 / 9",
    }
    return [make_example(1, 2, "MANITOBA_WORKSHOP", t, T,
                         {"room_temp_c": f_to_c(MANITOBA_ROOM_F), "cup_material": "not reported",
                          "volume_ml": None, "lid_or_fat_condition": "not reported"}, meta)]


def langer_examples() -> tuple[list, list]:
    raw = json.loads((RAW / "langer_abb2_raw.json").read_text(encoding="utf-8"))
    kept, excluded = [], []
    for idx, c in enumerate(raw["curves"], start=1):
        if c["style_id"] not in LANGER_KEEP_STYLE_IDS:
            excluded.append(c["style_id"])
            continue
        meta = {
            "curve_id": c["style_id"].replace("Abb2-style", "LANGER2018_Abb2"),
            "liquid": "hot water dispensed at 88 C (not coffee)", "is_coffee": False,
            "source_type": "peer-reviewed article (Deutsche Lebensmittel-Rundschau 114, July 2018)",
            "citation": "Langer T., Winkler G., Lachenmeier D.W. (2018). Untersuchungen zum Abkuehlverhalten von Heissgetraenken vor dem Hintergrund des temperaturbedingten Krebsrisikos.",
            "doi": "10.5281/zenodo.1402983 (CC-BY-4.0)",
            "url": "https://zenodo.org/records/1402983",
            "figure": "Abb. 2 single-use cups, 237 mL",
            "cup_material": "single-use cup class per legend; per-curve mapping not established",
            "volume_ml": 237,
            "room_temp_c": None,
            "lid_or_fat_condition": "not mapped per curve",
            "room_temp_note": "not reported",
            "humidity_note": "not reported",
            "sampling_interval_min": "not reported (logger Voltcraft K204 via SE309)",
            "measurement_method": "3 probes inside cup, Voltcraft K204, 0.1 C resolution",
            "measurement_error_note": "logger accuracy +/-3% of reading; single trace, no replicate statistics in figure",
            "digitization": {
                "method": "vector polyline extraction, scripts/digitize_langer_abb2.py",
                "axis_calibration": "tick-label centres: t=0 and 20 min; T=20 and 90 C",
                "estimated_error_c": 0.2,
            },
            "style": {"stroke_colour_rgb": c["stroke_colour_rgb"], "dash_pattern": c["dash_pattern"]},
            "validation_flag": "digitized 65 C crossing 18-32 min disagrees with 11-22 min in paper text; unresolved",
        }
        t = c["time_min"]
        T = c["temp_c"]
        kept.append(make_example(idx, 3, "LANGER2018", t, T,
                                 {"room_temp_c": None, "cup_material": meta["cup_material"],
                                  "volume_ml": 237, "lid_or_fat_condition": meta["lid_or_fat_condition"]}, meta))
    return kept, excluded


def main() -> None:
    langer, excluded = langer_examples()
    datasets = [
        {"dataset": "SEDLACEK2010", "examples": sedlacek_examples()},
        {"dataset": "MANITOBA_WORKSHOP", "examples": manitoba_examples()},
        {"dataset": "LANGER2018", "examples": langer},
    ]
    out = {
        "metadata": {
            "title": "Published hot-liquid cooling curves benchmark",
            "unit_time": "min",
            "unit_temperature": "degC",
            "selection": "8 curves from 3 sources",
            "excluded_langer_styles": excluded,
            "excluded_note": LANGER_EXCLUDED_NOTE,
            "humidity_reporting_sources": 0,
            "fold_convention": "metadata_fold is the source index (1-3); metadata_source_id names the source",
        },
        "datasets": datasets,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    n = sum(len(d["examples"]) for d in datasets)
    print(f"wrote {OUT.name}: {len(datasets)} datasets, {n} examples, excluded {excluded}")


if __name__ == "__main__":
    main()
