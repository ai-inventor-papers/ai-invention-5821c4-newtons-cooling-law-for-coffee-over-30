#!/usr/bin/env python3
"""Newton-type cooling laws fit on one published coffee curve and scored out of sample.

Models
  C0  Newton's law of cooling, constant rate:  T(t) = Tr + (T0 - Tr) * exp(-k t)
  C1  one-term nonlinear convection law:       dT/dt = -kc * (T - Tr)**x

Protocols
  in_sample_reference  fit C0/C1 on the Sedlacek and Dolejsi china-pot curve, score the same curve (0-30 min)
  A  transfer          fit on Sedlacek only, freeze, score Manitoba table curve and six Langer curves
  B  leave-one-source-out  three folds (Sedlacek / Manitoba / Langer), refit on the other sources, score the held-out source

Ambients
  A  room temperature fixed to each curve's recorded value (default 20 C where none is recorded, flagged)
  B  room temperature freed as one shared fitted parameter, bounded to T_ref +/- 5 K (T_ref = mean room temperature of the fit set)

Only the rate constant kc = a / C is identifiable for C1, so kc and x are fitted, not a and C separately.
The C1 solution is evaluated in closed form (exact for the separable ODE, see `c1_pred`) and cross-checked against
scipy.integrate.solve_ivp (LSODA) at the fitted parameters.

No LLM calls. CPU only.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from loguru import logger
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

WS = Path(__file__).resolve().parent
DEFAULT_DATA = WS / "data" / "full_data_out.json"
RES_DIR = WS / "results"

WINDOW_MIN = 30.0
ROOM_DEFAULT_C = 20.0
N_STARTS = 20
N_BOOT = 1000
BLOCK_LEN = 3
SEED = 0
MODELS = ("C0", "C1")
AMBIENTS = ("A", "B")
SOURCE_BY_FOLD = {1: "Sedlacek", 2: "Manitoba", 3: "Langer"}
LANGER_CROSSING_FLAG = (
    "Langer 65 C crossing times (18-32 min digitized) disagree with the paper's text (11-22 min); "
    "flagged unresolved in the dataset. Not used as a fit or score target; crossing-time comparison absent."
)
# Reference values from the earlier in-sample run, printed beside the new numbers only. They are not benchmarks here.
REFERENCE_IN_SAMPLE_K = {"C0": 1.07, "C1": 0.36}

SHAPE_NAMES = {"C0": ("k",), "C1": ("kc", "x")}
SHAPE_BOUNDS = {"C0": ((1e-4, 1.0),), "C1": ((1e-5, 1.0), (0.5, 2.5))}
DEFAULT_START = {"C0": (0.02,), "C1": (0.02, 1.2)}


@dataclass
class Curve:
    curve_id: str
    fold: int
    source: str
    t: np.ndarray  # in-window times (min), t <= WINDOW_MIN
    T: np.ndarray  # in-window temperatures (C)
    T0: float
    room: float  # room temperature used under ambient A (C)
    room_source: str  # "recorded" or "default_20C"
    digitisation_error_C: float | None
    measurement_error_C: float | None
    full_span_min: float
    partial: bool


# ----------------------------------------------------------------------------- data

def load_curves(path: Path) -> list[Curve]:
    raw = json.loads(path.read_text())
    curves: list[Curve] = []
    for ds in raw["datasets"]:
        for ex in ds["examples"]:
            inp = json.loads(ex["input"])
            T_all = np.asarray(json.loads(ex["output"]), dtype=float)
            t_all = np.asarray(inp["time_min"], dtype=float)
            if len(t_all) != len(T_all):
                raise ValueError(f"{ex['metadata_curve_id']}: time and temperature lengths differ")
            if not np.all(np.isfinite(T_all)):
                raise ValueError(f"{ex['metadata_curve_id']}: non-finite temperature")
            mask = t_all <= WINDOW_MIN + 1e-9
            t, T = t_all[mask], T_all[mask]
            if len(t) < 3:
                raise ValueError(f"{ex['metadata_curve_id']}: fewer than 3 points in window")
            T0 = float(inp["initial_liquid_temp_c"])
            if abs(T0 - T_all[0]) > 0.5:
                logger.warning(f"{ex['metadata_curve_id']}: recorded T0 {T0} differs from first sample {T_all[0]}")
            room_rec = inp.get("room_temp_c")
            if room_rec is None:
                room, room_source = ROOM_DEFAULT_C, "default_20C"
            else:
                room, room_source = float(room_rec), "recorded"
            prov = json.loads(ex["metadata_provenance"])
            digit = prov.get("digitization", {}) or {}
            meas = prov.get("measurement_error_c")
            span = float(t_all.max())
            curves.append(
                Curve(
                    curve_id=ex["metadata_curve_id"],
                    fold=int(ex["metadata_fold"]),
                    source=SOURCE_BY_FOLD[int(ex["metadata_fold"])],
                    t=t,
                    T=T,
                    T0=T0,
                    room=room,
                    room_source=room_source,
                    digitisation_error_C=digit.get("estimated_error_c"),
                    measurement_error_C=meas,
                    full_span_min=span,
                    partial=bool(float(t.max()) < WINDOW_MIN - 1e-9),
                )
            )
    logger.info(f"Loaded {len(curves)} curves from {path.name}")
    return curves


# ----------------------------------------------------------------------------- models

def c0_pred(t: np.ndarray, T0: float, Tr: float, k: float) -> np.ndarray:
    return Tr + (T0 - Tr) * np.exp(-k * t)


def c1_pred(t: np.ndarray, T0: float, Tr: float, kc: float, x: float) -> np.ndarray:
    """Exact solution of dT/dt = -kc (T - Tr)**x with u = T - Tr.

    For x != 1:  u**(1-x) = u0**(1-x) + (x-1) * kc * t, so u = base**(1/(1-x)) with base = u0**(1-x) + (x-1) kc t.
    For x < 1 the base reaches zero at finite time; the body is then at room temperature (u clipped to 0).
    This is the clipping guard for the power's base: T - Tr never goes negative.
    """
    u0 = max(T0 - Tr, 0.0)
    if u0 <= 0.0:
        return np.full_like(t, Tr, dtype=float)
    if abs(x - 1.0) < 1e-9:
        u = u0 * np.exp(-kc * t)
    else:
        base = u0 ** (1.0 - x) + (x - 1.0) * kc * t
        pos = base > 0.0
        u = np.zeros_like(t, dtype=float)
        u[pos] = base[pos] ** (1.0 / (1.0 - x))
    return Tr + u


def predict(model: str, shape: tuple[float, ...], T0: float, t: np.ndarray, Tr: float) -> np.ndarray:
    if model == "C0":
        return c0_pred(t, T0, Tr, shape[0])
    return c1_pred(t, T0, Tr, shape[0], shape[1])


def c1_solve_ivp(T0: float, Tr: float, kc: float, x: float, t: np.ndarray) -> np.ndarray:
    def rhs(_, T):
        return [-kc * max(T[0] - Tr, 0.0) ** x]

    sol = solve_ivp(
        rhs, (0.0, float(t.max())), [T0], method="LSODA", t_eval=t, rtol=1e-8, atol=1e-10
    )
    if not sol.success:
        raise RuntimeError(f"solve_ivp failed: {sol.message}")
    return sol.y[0]


# ----------------------------------------------------------------------------- fitting

def unpack(model: str, amb: str, theta: np.ndarray) -> tuple[tuple[float, ...], float | None]:
    n = len(SHAPE_NAMES[model])
    shape = tuple(float(v) for v in theta[:n])
    tr = float(theta[n]) if amb == "B" else None
    return shape, tr


def residuals(model: str, amb: str, theta: np.ndarray, curves: list[Curve]) -> np.ndarray:
    shape, tr_shared = unpack(model, amb, theta)
    parts = []
    for c in curves:
        Tr = tr_shared if amb == "B" else c.room
        parts.append(predict(model, shape, c.T0, c.t, Tr) - c.T)
    r = np.concatenate(parts)
    return np.nan_to_num(r, nan=1e6, posinf=1e6, neginf=-1e6)


_FIT_COUNTER = {"n": 0}
ALL_ROWS: list[dict] = []


def fit(model: str, amb: str, curves: list[Curve]) -> dict:
    """Multi-start least squares. Returns fitted parameters and convergence count."""
    _FIT_COUNTER["n"] += 1
    rng = np.random.default_rng([SEED, _FIT_COUNTER["n"]])
    lo = [b[0] for b in SHAPE_BOUNDS[model]]
    hi = [b[1] for b in SHAPE_BOUNDS[model]]
    names = list(SHAPE_NAMES[model])
    t_ref = None
    if amb == "B":
        t_ref = float(np.mean([c.room for c in curves]))
        lo.append(t_ref - 5.0)
        hi.append(t_ref + 5.0)
        names.append("Tr")
    lo_a, hi_a = np.array(lo), np.array(hi)

    starts = []
    for _ in range(N_STARTS):
        s = []
        for j, nm in enumerate(names):
            a, b = lo_a[j], hi_a[j]
            if nm in ("k", "kc"):  # rate constants: log-uniform within bounds
                s.append(math.exp(rng.uniform(math.log(a), math.log(b))))
            else:
                s.append(rng.uniform(a, b))
        starts.append(s)
    default = list(DEFAULT_START[model]) + ([t_ref] if amb == "B" else [])
    starts.append(default)

    fits = []
    for s in starts:
        x0 = np.clip(np.asarray(s, dtype=float), lo_a, hi_a)
        try:
            r = least_squares(
                lambda th: residuals(model, amb, th, curves),
                x0,
                bounds=(lo_a, hi_a),
                method="trf",
                xtol=1e-12,
                ftol=1e-12,
                gtol=1e-12,
                max_nfev=5000,
            )
            fits.append((float(r.cost), np.asarray(r.x, dtype=float)))
        except (ValueError, FloatingPointError, RuntimeError) as exc:
            logger.warning(f"{model}/{amb}: start failed ({exc})")
    if not fits:
        raise RuntimeError(f"{model}/{amb}: all starts failed")
    best_cost, best_x = min(fits, key=lambda z: z[0])
    tol = 1e-6 * max(1.0, best_cost)
    n_conv = sum(1 for c, _ in fits if c <= best_cost + tol)
    shape, tr = unpack(model, amb, best_x)
    params = {nm: float(v) for nm, v in zip(SHAPE_NAMES[model], shape)}
    if amb == "B":
        params["Tr_fitted_C"] = float(tr)
        params["Tr_bounds_C"] = [t_ref - 5.0, t_ref + 5.0]
    # Flag any parameter that finished on a bound: the fit is then bound-limited, not identified in the interior
    at_bound = [nm for j, nm in enumerate(names) if abs(best_x[j] - lo_a[j]) < 1e-6 or abs(best_x[j] - hi_a[j]) < 1e-6]
    if at_bound:
        logger.warning(f"{model}/{amb} on {[c.curve_id for c in curves]}: parameters at bound {at_bound}")
    return {
        "params": params,
        "fit_rms_K": float(np.sqrt(np.mean(residuals(model, amb, best_x, curves) ** 2))),
        "starts_total": len(starts),
        "starts_converged": int(n_conv),
        "at_bound": at_bound,
        "theta": best_x,
    }


# ----------------------------------------------------------------------------- scoring

def score_curve(model: str, amb: str, fitted: dict, c: Curve) -> dict:
    shape, tr_shared = unpack(model, amb, fitted["theta"])
    Tr = tr_shared if amb == "B" else c.room
    pred = predict(model, shape, c.T0, c.t, Tr)
    r = pred - c.T  # model minus observed: positive = model above the curve
    early = c.t <= 10.0 + 1e-9
    late = (c.t > 10.0 + 1e-9) & (c.t <= WINDOW_MIN + 1e-9)
    return {
        "resid": r,
        "room_used_C": float(Tr),
        "room_source": ("fitted_shared" if amb == "B" else c.room_source),
        "rms_K": float(np.sqrt(np.mean(r ** 2))),
        "signed_mean_0_10_K": float(np.mean(r[early])) if early.any() else None,
        "signed_mean_10_30_K": float(np.mean(r[late])) if late.any() else None,
        "n_points": int(len(r)),
        "first_time_min": float(c.t.min()),
        "last_time_min": float(c.t.max()),
        "partial": bool(c.partial),
        "residual_vs_time": [
            {"t_min": float(tt), "resid_K": round(float(rr), 4)} for tt, rr in zip(c.t, r)
        ],
    }


# ----------------------------------------------------------------------------- intervals

def curve_boot_ci(vals: np.ndarray, rng: np.random.Generator) -> list[float]:
    n = len(vals)
    idx = rng.integers(0, n, size=(N_BOOT, n))
    means = vals[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def block_idx(m: int, rng: np.random.Generator) -> np.ndarray:
    if m < BLOCK_LEN:
        raise ValueError("series shorter than block length")
    nb = math.ceil(m / BLOCK_LEN)
    starts = rng.integers(0, m - BLOCK_LEN + 1, size=(N_BOOT, nb))
    idx = (starts[:, :, None] + np.arange(BLOCK_LEN)[None, None, :]).reshape(N_BOOT, -1)
    return idx[:, :m]


def block_rms_ci(r: np.ndarray, rng: np.random.Generator) -> list[float]:
    idx = block_idx(len(r), rng)
    vals = np.sqrt(np.mean(r[idx] ** 2, axis=1))
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def block_paired_ci(r1: np.ndarray, r0: np.ndarray, rng: np.random.Generator) -> list[float]:
    idx = block_idx(len(r1), rng)
    d = np.sqrt(np.mean(r1[idx] ** 2, axis=1)) - np.sqrt(np.mean(r0[idx] ** 2, axis=1))
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def summarise(rows: list[dict]) -> dict:
    """rows: one dict per (model, held-out curve) for a single protocol/fold/ambient."""
    rng = np.random.default_rng(SEED)
    out: dict = {}
    curve_ids = sorted({r["curve_id"] for r in rows})
    n_curves = len(curve_ids)
    sources = {r["source"] for r in rows}
    for model in MODELS:
        mr = [r for r in rows if r["model"] == model]
        vals = np.array([r["rms_K"] for r in mr], dtype=float)
        block: dict = {
            "n_curves": n_curves,
            "mean_rms_K": float(vals.mean()),
            "per_curve_rms_K": {r["curve_id"]: round(r["rms_K"], 4) for r in mr},
            "per_source_mean_rms_K": {
                s: float(np.mean([r["rms_K"] for r in mr if r["source"] == s])) for s in sorted(sources)
            },
        }
        if n_curves >= 2:
            block["interval_mean_rms_K_95"] = curve_boot_ci(vals, rng)
            block["interval_method"] = f"bootstrap over {n_curves} curves, {N_BOOT} resamples, seed {SEED}"
        else:
            block["interval_mean_rms_K_95"] = block_rms_ci(mr[0]["_r"], rng)
            block["interval_method"] = (
                f"within-curve block bootstrap over time points, block length {BLOCK_LEN}, "
                f"{N_BOOT} resamples, seed {SEED}; not comparable to between-curve intervals"
            )
        out[model] = block

    # paired C1 minus C0, per curve
    by = {(r["curve_id"], r["model"]): r for r in rows}
    diffs = np.array([by[(c, "C1")]["rms_K"] - by[(c, "C0")]["rms_K"] for c in curve_ids], dtype=float)
    paired: dict = {
        "mean_diff_C1_minus_C0_K": float(diffs.mean()),
        "per_curve_diff_K": {c: round(float(d), 4) for c, d in zip(curve_ids, diffs)},
        "count_curves_C1_lower": int(np.sum(diffs < 0)),
        "n_curves": n_curves,
    }
    if n_curves >= 2:
        paired["interval_mean_diff_95"] = curve_boot_ci(diffs, rng)
        paired["interval_method"] = f"bootstrap over {n_curves} curves, {N_BOOT} resamples, seed {SEED}"
    else:
        c = curve_ids[0]
        paired["interval_mean_diff_95"] = block_paired_ci(
            by[(c, "C1")]["_r"], by[(c, "C0")]["_r"], rng
        )
        paired["interval_method"] = (
            f"within-curve paired block bootstrap, block length {BLOCK_LEN}, {N_BOOT} resamples, seed {SEED}; "
            "not comparable to between-curve intervals"
        )
    out["paired_C1_minus_C0"] = paired
    return out


# ----------------------------------------------------------------------------- orchestration

def strip(row: dict) -> dict:
    return {k: v for k, v in row.items() if not k.startswith("_")}


def run_block(protocol: str, fold_label: str, fit_curves: list[Curve], score_curves: list[Curve], amb: str,
              records: list[dict], fits_out: dict) -> dict:
    """Fit C0 and C1 on fit_curves, score on score_curves. Returns summary for this block."""
    rows = []
    for model in MODELS:
        fitted = fit(model, amb, fit_curves)
        key = f"{protocol}|{fold_label}|{amb}|{model}"
        fits_out[key] = {
            "fit_curves": [c.curve_id for c in fit_curves],
            "params": fitted["params"],
            "fit_rms_on_fit_set_K": round(fitted["fit_rms_K"], 4),
            "starts_total": fitted["starts_total"],
            "starts_converged_within_1e-6": fitted["starts_converged"],
            "parameters_at_bound": fitted["at_bound"],
        }
        logger.info(
            f"{protocol} {fold_label} amb {amb} {model}: params {fitted['params']} "
            f"fit RMS {fitted['fit_rms_K']:.3f} K, converged starts {fitted['starts_converged']}/{fitted['starts_total']}"
        )
        for c in score_curves:
            sc = score_curve(model, amb, fitted, c)
            row = {
                "protocol": protocol,
                "fold": fold_label,
                "ambient": amb,
                "model": model,
                "curve_id": c.curve_id,
                "source": c.source,
                "T0_C": c.T0,
                "room_source_recorded_or_default": c.room_source,
                "fitted_params": fitted["params"],
                "starts_converged": f"{fitted['starts_converged']}/{fitted['starts_total']}",
                "digitisation_error_C": c.digitisation_error_C,
                "measurement_error_C": c.measurement_error_C,
                "is_in_sample": protocol == "in_sample_reference",
                "rms_K": sc["rms_K"],
                "signed_mean_0_10_K": sc["signed_mean_0_10_K"],
                "signed_mean_10_30_K": sc["signed_mean_10_30_K"],
                "room_used_C": sc["room_used_C"],
                "room_source": sc["room_source"],
                "first_time_min": sc["first_time_min"],
                "last_time_min": sc["last_time_min"],
                "n_points": sc["n_points"],
                "partial": sc["partial"],
                "residual_vs_time": sc["residual_vs_time"],
                "_r": sc["resid"],
                "_pred": (sc["resid"] + c.T).tolist(),
            }
            rows.append(row)
    summary = summarise(rows)
    records.extend(strip(r) for r in rows)
    ALL_ROWS.extend(rows)
    return summary


def validate_c1_closed_form(curves: list[Curve]) -> dict:
    """Cross-check the closed-form C1 against solve_ivp at the Sedlacek fit (Ambient A)."""
    sed = [c for c in curves if c.fold == 1]
    f = fit("C1", "A", sed)
    kc, x = f["params"]["kc"], f["params"]["x"]
    worst = 0.0
    per = {}
    for c in curves:
        cf = c1_pred(c.t, c.T0, c.room, kc, x)
        si = c1_solve_ivp(c.T0, c.room, kc, x, c.t)
        d = float(np.max(np.abs(cf - si)))
        per[c.curve_id] = d
        worst = max(worst, d)
    logger.info(f"C1 closed form vs solve_ivp: max abs difference {worst:.2e} K")
    return {"max_abs_diff_K": worst, "per_curve_max_abs_diff_K": per, "kc": kc, "x": x}


def print_table(records: list[dict]) -> None:
    header = f"{'protocol':<26}{'fold':<30}{'amb':<5}{'model':<7}{'curve':<26}{'RMS K':>8}{'early':>9}{'late':>9}"
    logger.info(header)
    for r in records:
        early = r["signed_mean_0_10_K"]
        late = r["signed_mean_10_30_K"]
        logger.info(
            f"{r['protocol']:<26}{r['fold']:<30}{r['ambient']:<5}{r['model']:<7}{r['curve_id']:<26}"
            f"{r['rms_K']:>8.3f}{early:>9.3f}{late:>9.3f}"
        )


def write_method_out(curves: list[Curve], out_dir: Path) -> None:
    """Per-curve predictions in the exp_gen_sol_out shape (datasets -> examples -> input/output/predict_*)."""
    def pred_for(protocol: str, fold: str, model: str, curve_id: str) -> list[float] | None:
        for r in ALL_ROWS:
            if r["protocol"] == protocol and r["fold"] == fold and r["ambient"] == "A" \
                    and r["model"] == model and r["curve_id"] == curve_id:
                return [round(v, 4) for v in r["_pred"]]
        return None

    datasets = []
    for c in curves:
        if c.fold == 1:
            role, loso_fold, a_fold = "in_sample_fit_and_score", "Sedlacek", "Sedlacek"
            a_protocol = "in_sample_reference"
        else:
            role, loso_fold = "held_out", SOURCE_BY_FOLD[c.fold]
            a_protocol, a_fold = "A_transfer", "Sedlacek->Manitoba+Langer"
        example = {
            "input": json.dumps({
                "curve_id": c.curve_id,
                "time_min": [round(float(v), 4) for v in c.t],
                "initial_temperature_C": c.T0,
                "room_temperature_C": c.room,
                "room_temperature_source": c.room_source,
                "window_min": WINDOW_MIN,
            }),
            "output": json.dumps([round(float(v), 4) for v in c.T]),
            "predict_C0_protocolA_ambientA": json.dumps(pred_for(a_protocol, a_fold, "C0", c.curve_id)),
            "predict_C1_protocolA_ambientA": json.dumps(pred_for(a_protocol, a_fold, "C1", c.curve_id)),
            "predict_C0_loso_ambientA": json.dumps(pred_for("B_leave_one_source_out", loso_fold, "C0", c.curve_id)),
            "predict_C1_loso_ambientA": json.dumps(pred_for("B_leave_one_source_out", loso_fold, "C1", c.curve_id)),
            "metadata_fold": c.fold,
            "metadata_source_id": c.source,
            "metadata_curve_id": c.curve_id,
            "metadata_role": role,
            "metadata_partial": c.partial,
            "metadata_digitisation_error_C": c.digitisation_error_C,
            "metadata_measurement_error_C": c.measurement_error_C,
        }
        datasets.append({"dataset": c.source, "examples": [example]})
    doc = {
        "metadata": {
            "method_name": "Newton-type cooling laws C0 (constant rate) and C1 (nonlinear convection)",
            "description": "Observed 0-30 min curve and out-of-sample predictions (ambient A) per curve.",
            "window_min": WINDOW_MIN,
            "predict_fields": "JSON lists aligned to input.time_min; protocolA = fit on Sedlacek; loso = leave-one-source-out fold",
        },
        "datasets": datasets,
    }
    (out_dir / "method_out.json").write_text(json.dumps(doc, indent=1))
    logger.info(f"Wrote {out_dir / 'method_out.json'}")


def main() -> None:
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else RES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    logger.add(WS / "logs" / "run.log", level="DEBUG", rotation="10 MB")

    curves = load_curves(data_path)
    by_fold: dict[int, list[Curve]] = {1: [], 2: [], 3: []}
    for c in curves:
        by_fold[c.fold].append(c)
    sed, man, lang = by_fold[1], by_fold[2], by_fold[3]
    if not sed or not man or not lang:
        raise RuntimeError("expected curves from all three sources")
    logger.info(
        f"Curves: Sedlacek {len(sed)}, Manitoba {len(man)}, Langer {len(lang)}; "
        f"partial curves: {[c.curve_id for c in curves if c.partial]}"
    )
    for c in curves:
        logger.info(
            f"  {c.curve_id}: n={len(c.t)} in window, last t={c.t.max():.1f} min, T0={c.T0:.2f} C, "
            f"room={c.room:.2f} C ({c.room_source}), digitisation err={c.digitisation_error_C}"
        )

    records: list[dict] = []
    fits_out: dict = {}
    blocks: dict = {}

    # In-sample reference: fit and score the Sedlacek curve (0-30 min)
    for amb in AMBIENTS:
        blocks[f"in_sample_reference|Sedlacek|{amb}"] = run_block(
            "in_sample_reference", "Sedlacek", sed, sed, amb, records, fits_out
        )

    # Protocol A: transfer. Fit on Sedlacek, freeze, score Manitoba and Langer.
    heldA = man + lang
    for amb in AMBIENTS:
        blocks[f"A_transfer|Sedlacek->Manitoba+Langer|{amb}"] = run_block(
            "A_transfer", "Sedlacek->Manitoba+Langer", sed, heldA, amb, records, fits_out
        )

    # Protocol B: leave-one-source-out
    folds = [
        ("Sedlacek", man + lang, sed),
        ("Manitoba", sed + lang, man),
        ("Langer", sed + man, lang),
    ]
    for amb in AMBIENTS:
        for name, fit_set, score_set in folds:
            blocks[f"B_loso|{name}|{amb}"] = run_block(
                "B_leave_one_source_out", name, fit_set, score_set, amb, records, fits_out
            )

    validation = validate_c1_closed_form(curves)

    # Pre-registered decision rule (Ambient A is primary; Ambient B reported alongside)
    decisions = {}
    for amb in AMBIENTS:
        A = blocks[f"A_transfer|Sedlacek->Manitoba+Langer|{amb}"]
        a_rows = [r for r in records if r["protocol"] == "A_transfer" and r["ambient"] == amb]
        c0_early = [r["signed_mean_0_10_K"] for r in a_rows if r["model"] == "C0"]
        fold_wins = []
        for name, _, _ in folds:
            s = blocks[f"B_loso|{name}|{amb}"]
            fold_wins.append(s["C1"]["mean_rms_K"] < s["C0"]["mean_rms_K"])
        man_c1 = [r["rms_K"] for r in a_rows if r["model"] == "C1" and r["source"] == "Manitoba"][0]
        lang_c1 = A["C1"]["per_source_mean_rms_K"]["Langer"]
        c0_mean_all = A["C0"]["mean_rms_K"]
        decisions[amb] = {
            "C0_early_residual_positive_on_held_out": {
                "mean_0_10_K": float(np.mean(c0_early)),
                "n_positive": int(sum(v > 0 for v in c0_early)),
                "n_curves": len(c0_early),
                "pass": bool(np.mean(c0_early) > 0),
            },
            "C1_beats_C0_protocol_A": {
                "C0_mean_rms_K": A["C0"]["mean_rms_K"],
                "C1_mean_rms_K": A["C1"]["mean_rms_K"],
                "pass": bool(A["C1"]["mean_rms_K"] < A["C0"]["mean_rms_K"]),
            },
            "C1_beats_C0_in_at_least_2_of_3_folds": {
                "folds_where_C1_lower": {name: bool(w) for (name, _, _), w in zip(folds, fold_wins)},
                "pass": bool(sum(fold_wins) >= 2),
            },
            "accuracy_C1_under_0.5K": {
                "C1_Manitoba_rms_K": float(man_c1),
                "C1_Langer_mean_rms_K": float(lang_c1),
                "pass": bool(man_c1 < 0.5 and lang_c1 < 0.5),
            },
            "C0_already_adequate_under_0.5K_held_out": {
                "C0_protocol_A_mean_rms_K": float(c0_mean_all),
                "adequate": bool(c0_mean_all < 0.5),
            },
        }
        logger.info(f"Decision rule (ambient {amb}): {json.dumps(decisions[amb], indent=1)}")

    fold_summary = {
        "meta": {
            "description": "Out-of-sample transfer of Newton-type cooling laws C0 and C1 on published coffee curves.",
            "window_min": WINDOW_MIN,
            "room_temperature_default_C": ROOM_DEFAULT_C,
            "room_temperature_note": (
                "Sedlacek and Langer report no room temperature; 20 C is used under ambient A and flagged. "
                "Ambient B frees room temperature as a fitted shared parameter (bounds T_ref +/- 5 K)."
            ),
            "T0_note": "T0 is each curve's recorded initial temperature. The Langer recorded T0 is 80.2-82.3 C (not 88 C).",
            "n_starts": N_STARTS,
            "n_bootstrap": N_BOOT,
            "bootstrap_seed": SEED,
            "block_length": BLOCK_LEN,
            "C1_solver": "closed form; cross-checked against scipy solve_ivp LSODA (rtol 1e-8, atol 1e-10)",
            "in_sample_reference_iter1_K": REFERENCE_IN_SAMPLE_K,
            "langer_crossing_time_flag": LANGER_CROSSING_FLAG,
            "humidity": "not recorded by any source; humidity and fat-layer terms are out of scope",
            "llm_calls": 0,
            "spend_usd": 0.0,
        },
        "curves": [
            {
                "curve_id": c.curve_id,
                "source": c.source,
                "fold": c.fold,
                "T0_C": c.T0,
                "room_C": c.room,
                "room_source": c.room_source,
                "digitisation_error_C": c.digitisation_error_C,
                "measurement_error_C": c.measurement_error_C,
                "in_window_points": int(len(c.t)),
                "last_time_min": float(c.t.max()),
                "full_span_min": c.full_span_min,
                "partial": c.partial,
            }
            for c in curves
        ],
        "blocks": blocks,
        "fitted_parameters": fits_out,
        "decision_rule": decisions,
        "c1_closed_form_validation": validation,
        "sample_size_gap": "8 curves from 3 sources; Langer six curves are one lab and one protocol, not six sessions.",
    }

    heldout = {
        "meta": {
            "description": "Per-curve scores for C0 and C1 under each protocol and ambient.",
            "columns": "rms_K over the 0-30 min window; signed residual = model minus observed",
        },
        "rows": records,
    }
    (out_dir / "heldout_scores.json").write_text(json.dumps(heldout, indent=2))
    (out_dir / "fold_summary.json").write_text(json.dumps(fold_summary, indent=2))
    logger.info(f"Wrote {out_dir / 'heldout_scores.json'} and {out_dir / 'fold_summary.json'}")

    write_method_out(curves, out_dir)
    print_table(records)
    logger.info("In-sample reference (iter_1 numbers, for comparison only): C0 1.07 K, C1 0.36 K")


if __name__ == "__main__":
    main()
