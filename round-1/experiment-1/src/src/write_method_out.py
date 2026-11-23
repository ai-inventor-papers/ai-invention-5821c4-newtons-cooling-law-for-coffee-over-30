#!/usr/bin/env python3
"""Write results/method_out.json in the exp_gen_sol_out format.

One dataset (the digitized china-pot curve, 29 measured points). Each example is
one measured time point: input is the time, output is the measured temperature,
and predict_* fields hold each model's prediction as a string. All metrics,
parameters, intervals, gate results and not-testable flags go under the
top-level metadata object, which the schema allows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "src"))

from models import c0_closed_form, integrate  # noqa: E402

DIGI = WORKSPACE / "data" / "digitized"
RESULTS = WORKSPACE / "results"
T_ROOM = 20.0


def main() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    analysis = json.loads((RESULTS / "analysis_results.json").read_text())
    tests = json.loads((RESULTS / "tests.json").read_text())
    china = pd.read_csv(DIGI / "china_digitized.csv").sort_values("t_min").reset_index(drop=True)
    shift = float(china["t_min"].iloc[0])
    t = china["t_min"].to_numpy() - shift
    T = china["T_C"].to_numpy()
    t0 = float(T[0])
    pub = pd.read_csv(DIGI / "paper_model_curves.csv")
    pub1 = pub[pub["model"] == "model 1"].sort_values("t_min")
    pub_pred = np.interp(t, pub1["t_min"].to_numpy() - shift, pub1["T_C"].to_numpy())

    cand = analysis["candidates_30min_window"]
    c0_a = cand["C0"]["params"]["a_per_min"]
    c1_a, c1_x = cand["C1"]["params"]["a_per_min"], cand["C1"]["params"]["x"]
    c0_pred = c0_closed_form(t, t0, c0_a, T_ROOM)
    c1_pred = integrate("C1", (c1_a, c1_x), t, t0, T_ROOM)

    examples = []
    for i in range(len(t)):
        examples.append(
            {
                "input": f"Time since first measurement: {t[i]:.2f} min",
                "output": f"Measured coffee temperature: {T[i]:.2f} C",
                "predict_C0_constant_rate_window_fit": f"{c0_pred[i]:.2f} C",
                "predict_C1_nonlinear_convection_window_fit": f"{c1_pred[i]:.2f} C",
                "predict_source_drawn_model1_curve": f"{pub_pred[i]:.2f} C",
                "metadata_in_30min_window": bool(t[i] <= 30.0),
                "metadata_residual_C0_model_minus_data_K": round(float(c0_pred[i] - T[i]), 4),
                "metadata_residual_C1_model_minus_data_K": round(float(c1_pred[i] - T[i]), 4),
                "metadata_residual_source_model1_model_minus_data_K": round(float(pub_pred[i] - T[i]), 4),
            }
        )

    metadata = {
        "method_name": "Screen of cooling models on the digitized china-pot coffee curve (Sedlacek and Dolejsi)",
        "description": (
            "Constant-rate Newton law (C0) as baseline, nonlinear convection (C1), two-term convection plus evaporation "
            "(C2, C2p, C2_fixed_x), with the source's drawn model-1 curve scored as published. In-sample 30-minute window. "
            "Reproduction gate of the source's chi2/NDF values FAILED, so the pre-registered selection rule was not applied."
        ),
        "data_source": "Sedlacek and Dolejsi, 'A physical description of coffee cooling in a pot', Fig. 1 vector markers (29 points)",
        "digitization": {
            "method": "PDF vector marker centres mapped by least-squares axis fits to tick-label centres",
            "across_figure_median_disagreement_C": analysis["digitization_noise_floor"]["digitization_error_C_median_across_figures"],
            "sigma_used_C": analysis["digitization_noise_floor"]["sigma_used_C"],
        },
        "assumptions": {
            "T_room_C": T_ROOM,
            "T_room_source": "not reported in the source; fixed at 20 C (lower axis limit of the source's figures); free-ambient sensitivity reported",
            "T0_C": t0,
            "time_origin": "first marker at t = 0 (shift of %.3f min applied)" % (-shift),
            "heat_capacity": "absorbed into fitted coefficients; rates, not physical heat-transfer coefficients",
            "residual_sign": "model minus data",
        },
        "reproduction_gate": analysis["reproduction_gate"],
        "candidates_30min_window": cand,
        "sensitivity": analysis["sensitivity"],
        "forecast_check": analysis["forecast_check"],
        "selection": analysis["selection"],
        "bootstrap": analysis["bootstrap"],
        "tests": tests,
        "not_testable": analysis["not_testable"],
        "answer_summary": {
            "C0_30min_rms_K_in_sample": cand["C0"]["rms_30min_K"],
            "C0_30min_rms_K_ci95_block_bootstrap": cand["C0"]["bootstrap"]["rms_K_ci95"],
            "published_model1_30min_rms_K": cand["published_model1_curve"]["rms_30min_K"],
            "C1_30min_rms_K_in_sample": cand["C1"]["rms_30min_K"],
        },
    }
    out = {"metadata": metadata, "datasets": [{"dataset": "sedlacek_dolejsi_china_pot_fig1_digitized", "examples": examples}]}
    path = WORKSPACE / "method_out.json"
    path.write_text(json.dumps(out, indent=2, default=float))
    logger.info(f"Wrote method_out.json with {len(examples)} examples")


if __name__ == "__main__":
    main()
