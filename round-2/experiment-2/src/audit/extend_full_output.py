#!/usr/bin/env python3
"""Sensitivity extension: score all ten digitized Langer curves with the frozen planned parameters.

The plan's held-out set uses six Langer curves. The dataset's raw digitization (data/langer_abb2_raw.json)
holds ten. The four extra curves are scored here with the parameters already fitted by method.py (no refit),
so the planned headline numbers are unchanged. Output: results/sensitivity_langer10.json and an
exp_gen_sol_out file with 8 planned examples + 4 sensitivity examples (12 total).

Initial temperature for the four extra curves is not recorded in the dataset; the first sample (t = 1 min)
is used as T0, which is how the six planned curves' recorded initial temperatures relate to their first samples.
Room temperature is not recorded: the 20 C default is used, flagged.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS))
import method as M  # noqa: E402  (same module that produced the planned results)

RAW_LANGER = json.loads((WS / "data" / "langer_abb2_raw.json").read_text())
FULL = json.loads((WS / "data" / "full_data_out.json").read_text())
STORED = json.loads((WS / "results" / "heldout_scores.json").read_text())["rows"]
SUMMARY = json.loads((WS / "results" / "fold_summary.json").read_text())

planned = M.load_curves(WS / "data" / "full_data_out.json")
planned_langer_ids = {c.curve_id for c in planned if c.fold == 3}
langer_err = next(
    json.loads(e["metadata_provenance"])["digitization"]["estimated_error_c"]
    for ds in FULL["datasets"] for e in ds["examples"] if e["metadata_fold"] == 3
)


def frozen(protocol: str, fold: str, model: str, ambient: str = "A") -> dict:
    for r in STORED:
        if r["protocol"] == protocol and r["fold"] == fold and r["model"] == model and r["ambient"] == ambient:
            return r
    raise KeyError((protocol, fold, model, ambient))


def predict_with(row_params: dict, model: str, c: M.Curve) -> np.ndarray:
    if model == "C0":
        return M.c0_pred(c.t, c.T0, c.room, row_params["k"])
    return M.c1_pred(c.t, c.T0, c.room, row_params["kc"], row_params["x"])


# Extra Langer curves (not in the planned set): same window, same ambient-A room default.
extra: list[M.Curve] = []
for c in RAW_LANGER["curves"]:
    cid = f"LANGER2018_{c['style_id'].replace('Abb2-style-', 'Abb2-')}"
    if cid in planned_langer_ids:
        continue
    t = np.asarray(c["time_min"], float)
    T = np.asarray(c["temp_c"], float)
    m = t <= M.WINDOW_MIN + 1e-9
    extra.append(M.Curve(
        curve_id=cid, fold=3, source="Langer", t=t[m], T=T[m], T0=float(T[0]),
        room=M.ROOM_DEFAULT_C, room_source="default_20C", digitisation_error_C=float(langer_err),
        measurement_error_C=None, full_span_min=float(t.max()), partial=bool(t[m].max() < M.WINDOW_MIN - 1e-9),
    ))
print(f"planned Langer curves: {sorted(planned_langer_ids)}")
print(f"sensitivity-only Langer curves: {[c.curve_id for c in extra]}")

rows_out = []
all_curves = planned + extra
for c in all_curves:
    role = "planned" if c.curve_id in planned_langer_ids or c.fold != 3 else "sensitivity_excluded_from_planned_set"
    if c.fold == 1:
        role = "in_sample_fit_and_score"
    for model in ("C0", "C1"):
        if c.fold == 1:
            p = frozen("in_sample_reference", "Sedlacek", model)["fitted_params"]
        else:
            p = frozen("A_transfer", "Sedlacek->Manitoba+Langer", model)["fitted_params"]
        pred = predict_with(p, model, c)
        r = pred - c.T
        loso_fold = {1: "Sedlacek", 2: "Manitoba", 3: "Langer"}[c.fold]
        p_loso = frozen("B_leave_one_source_out", loso_fold, model)["fitted_params"]
        pred_loso = predict_with(p_loso, model, c)
        rows_out.append({
            "curve_id": c.curve_id, "source": c.source, "role": role, "model": model,
            "rms_K": float(np.sqrt(np.mean(r ** 2))),
            "signed_mean_0_10_K": float(np.mean(r[c.t <= 10 + 1e-9])),
            "signed_mean_10_30_K": float(np.mean(r[c.t > 10 + 1e-9])),
            "n_points": int(len(c.t)), "T0_C": c.T0, "room_C": c.room, "room_source": c.room_source,
            "pred_protocolA": pred.tolist(), "pred_loso": pred_loso.tolist(),
            "rms_loso_K": float(np.sqrt(np.mean((pred_loso - c.T) ** 2))),
        })

# Consistency check: planned rows must equal the stored headline values.
max_dev = 0.0
for r in rows_out:
    if r["role"] == "sensitivity_excluded_from_planned_set":
        continue
    stored = next(x for x in STORED if x["curve_id"] == r["curve_id"] and x["model"] == r["model"]
                  and x["protocol"] in ("A_transfer", "in_sample_reference") and x["ambient"] == "A")
    max_dev = max(max_dev, abs(stored["rms_K"] - r["rms_K"]))
print(f"max deviation of planned rows from stored headline values: {max_dev:.2e} K")

lang_ext = [r for r in rows_out if r["role"] == "sensitivity_excluded_from_planned_set" and r["model"] == "C0"]
lang_all = [r for r in rows_out if r["source"] == "Langer" and r["model"] == "C0"]
summary = {}
for model in ("C0", "C1"):
    vals6 = [r["rms_K"] for r in rows_out if r["source"] == "Langer" and r["model"] == model
             and r["role"] == "planned"]
    vals10 = [r["rms_K"] for r in rows_out if r["source"] == "Langer" and r["model"] == model]
    vals_loso10 = [r["rms_loso_K"] for r in rows_out if r["source"] == "Langer" and r["model"] == model]
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(vals10), size=(1000, len(vals10)))
    means = np.array(vals10)[idx].mean(axis=1)
    summary[model] = {
        "langer_mean_rms_planned6_K": float(np.mean(vals6)),
        "langer_mean_rms_all10_K": float(np.mean(vals10)),
        "langer_all10_interval_95_bootstrap_over_curves": [float(np.percentile(means, 2.5)),
                                                          float(np.percentile(means, 97.5))],
        "langer_mean_rms_loso_fold_all10_K": float(np.mean(vals_loso10)),
    }
    print(model, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in summary[model].items()
                  if not isinstance(v, list)}, "interval", [round(x, 3) for x in summary[model][
                      "langer_all10_interval_95_bootstrap_over_curves"]])

out_dir = WS / "results"
(out_dir / "sensitivity_langer10.json").write_text(json.dumps({
    "description": "Protocol A, ambient A, frozen parameters from method.py. Four digitized Langer curves beyond the plan's six are scored as a sensitivity check; they are not in the planned headline set.",
    "bootstrap": {"n": 1000, "seed": 0, "unit": "curves"},
    "t0_note": "extra curves: T0 = first sample (t = 1 min); recorded initial temperature not in the raw digitization",
    "room_note": "extra curves: 20 C default (room temperature not recorded)",
    "summary": summary,
    "rows": rows_out,
}, indent=1))

# exp_gen_sol_out file with 8 planned + 4 sensitivity examples
datasets = []
for c in all_curves:
    rr = {r["model"]: r for r in rows_out if r["curve_id"] == c.curve_id}
    example = {
        "input": json.dumps({
            "curve_id": c.curve_id,
            "time_min": [round(float(v), 4) for v in c.t],
            "initial_temperature_C": c.T0,
            "room_temperature_C": c.room,
            "room_temperature_source": c.room_source,
            "window_min": M.WINDOW_MIN,
        }),
        "output": json.dumps([round(float(v), 4) for v in c.T]),
        "predict_C0_protocolA_ambientA": json.dumps([round(v, 4) for v in rr["C0"]["pred_protocolA"]]),
        "predict_C1_protocolA_ambientA": json.dumps([round(v, 4) for v in rr["C1"]["pred_protocolA"]]),
        "predict_C0_loso_ambientA": json.dumps([round(v, 4) for v in rr["C0"]["pred_loso"]]),
        "predict_C1_loso_ambientA": json.dumps([round(v, 4) for v in rr["C1"]["pred_loso"]]),
        "metadata_fold": c.fold,
        "metadata_source_id": c.source,
        "metadata_curve_id": c.curve_id,
        "metadata_role": rr["C0"]["role"],
        "metadata_partial": c.partial,
        "metadata_digitisation_error_C": c.digitisation_error_C,
        "metadata_measurement_error_C": c.measurement_error_C,
    }
    datasets.append({"dataset": c.source, "examples": [example]})
doc = {
    "metadata": {
        "method_name": "Newton-type cooling laws C0 (constant rate) and C1 (nonlinear convection)",
        "description": "Observed 0-30 min curve and out-of-sample predictions for each curve. 8 planned examples plus 4 sensitivity-only Langer curves; predictions use frozen parameters from method.py.",
        "window_min": M.WINDOW_MIN,
        "predict_fields": "JSON lists aligned to input.time_min; protocolA = fit on Sedlacek; loso = leave-one-source-out fold",
    },
    "datasets": datasets,
}
text = json.dumps(doc, indent=1)
(out_dir / "full_method_out.json").write_text(text)
(WS / "full_method_out.json").write_text(text)
print(f"wrote {len(datasets)} examples to full_method_out.json")
