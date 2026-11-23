#!/usr/bin/env python3
"""Write chart specs from the analysis outputs and render them with aii-data-fig-gen.

Every figure is rendered by the skill's chart_gen.py from a JSON spec, so the
drawing follows the house style and the numbers in the spec are the numbers drawn.
Specs are kept in figures/specs/ so the figures can be regenerated.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "src"))

from models import c0_closed_form, integrate  # noqa: E402

PYTHON = WORKSPACE / ".venv" / "bin" / "python"

DIGI = WORKSPACE / "data" / "digitized"
RESULTS = WORKSPACE / "results"
FIG_DIR = WORKSPACE / "figures"
SPEC_DIR = FIG_DIR / "specs"

def find_chart_gen() -> Path:
    """Locate the aii-data-fig-gen generator without hard-coding a machine path.

    Order: the AII_DATA_FIG_GEN environment variable, then a .claude/skills tree
    found by walking up from the workspace.
    """
    import os

    env = os.environ.get("AII_DATA_FIG_GEN")
    if env:
        return Path(env)
    for parent in [WORKSPACE, *WORKSPACE.parents]:
        candidate = parent / ".claude" / "skills" / "aii-data-fig-gen" / "scripts" / "chart_gen.py"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("set AII_DATA_FIG_GEN to the path of chart_gen.py")

T_ROOM = 20.0
SHIFT = 0.0


def round_list(values, nd: int = 3) -> list[float]:
    return [round(float(v), nd) for v in values]


def build_specs() -> dict[str, dict]:
    analysis = json.loads((RESULTS / "analysis_results.json").read_text())
    china = pd.read_csv(DIGI / "china_digitized.csv").sort_values("t_min")
    SHIFT = -float(china["t_min"].iloc[0])  # same offset as analysis.load_china (raw t -> t from first marker)
    china["t_min"] = china["t_min"] + SHIFT
    t_all = china["t_min"].to_numpy()
    T_all = china["T_C"].to_numpy()
    t0 = float(T_all[0])
    win = t_all <= 30.0 + 1e-9
    t_w = t_all[win]
    T_w = T_all[win]

    cand = analysis["candidates_30min_window"]
    c0_a = cand["C0"]["params"]["a_per_min"]
    c1_a = cand["C1"]["params"]["a_per_min"]
    c1_x = cand["C1"]["params"]["x"]

    # Residual time series (model minus data) on the window.
    grid_w = np.linspace(0, 30, 121)
    res_series = []
    for label, pred in [
        ("C0 constant-rate Newton law", c0_closed_form(grid_w, t0, c0_a, T_ROOM)),
        ("C1 nonlinear convection", integrate("C1", (c1_a, c1_x), grid_w, t0, T_ROOM)),
    ]:
        data_interp = np.interp(grid_w, t_w, T_w)
        res_series.append({"label": label, "x": round_list(grid_w, 2), "values": round_list(pred - data_interp, 3)})
    pub = pd.read_csv(DIGI / "paper_model_curves.csv")
    pub1 = pub[pub["model"] == "model 1"].sort_values("t_min")
    pub_grid = np.interp(grid_w, pub1["t_min"].to_numpy() + SHIFT, pub1["T_C"].to_numpy())
    res_series.append({"label": "source's drawn model 1 (Fig. 2)", "x": round_list(grid_w, 2), "values": round_list(pub_grid - np.interp(grid_w, t_w, T_w), 3)})
    residual_spec = {
        "type": "line",
        "title": "Residual of each model against the digitized china curve",
        "show_title": False,
        "xlabel": "Time (min)",
        "ylabel": "Model minus data (K)",
        "aspect": "16:9",
        "series": res_series,
    }

    # 30-minute RMS with a 95% block-bootstrap interval (half-width shown symmetrically).
    rows = [("C0 constant-rate", "C0"), ("C1 nonlinear convection", "C1"), ("C2 two-term, plan form", "C2"),
            ("C2 two-term, x = 1.25 fixed", "C2_fixed_x"), ("C2p two-term, source form", "C2p")]
    cats, vals, errs = [], [], []
    for label, key in rows:
        m = cand[key]
        lo, hi = m["bootstrap"]["rms_K_ci95"]
        cats.append(label)
        vals.append(round(m["rms_30min_K"], 3))
        errs.append(round((hi - lo) / 2, 3))
    forest_spec = {
        "type": "forest",
        "null_line": 0.0,
        "title": "30-minute RMS error by model (in-sample)",
        "show_title": False,
        "xlabel": "RMS error, 0-30 min (K); bars: 95% block-bootstrap half-widths",
        "aspect": "4:3",
        "categories": cats,
        "series": [{"label": "RMS (K)", "values": vals, "errors": errs}],
    }

    # Data and fits over the full record.
    fit_grid = np.linspace(0, 139, 140)
    full_series = [
        {"label": "measured (digitized Fig. 1)", "x": round_list(t_all, 2), "values": round_list(T_all, 2)},
        {"label": "C0 fitted on 0-30 min", "x": round_list(fit_grid, 1), "values": round_list(c0_closed_form(fit_grid, t0, c0_a, T_ROOM), 2)},
        {"label": "C1 fitted on 0-30 min", "x": round_list(fit_grid, 1), "values": round_list(integrate("C1", (c1_a, c1_x), fit_grid, t0, T_ROOM), 2)},
        {"label": "source's drawn model 1 (Fig. 2)", "x": round_list(pub1["t_min"].to_numpy()[::10] + SHIFT, 2), "values": round_list(pub1["T_C"].to_numpy()[::10], 2)},
    ]
    data_spec = {
        "type": "line",
        "title": "Measured and modelled coffee temperature",
        "show_title": False,
        "xlabel": "Time (min)",
        "ylabel": "Temperature (°C)",
        "aspect": "16:9",
        "series": full_series,
    }
    return {"residual_vs_time": residual_spec, "rms_30min_forest": forest_spec, "data_and_fits": data_spec}


def render(name: str, spec: dict) -> None:
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    spec_path = SPEC_DIR / f"{name}.json"
    spec_path.write_text(json.dumps(spec, indent=2))
    cmd = [str(PYTHON), str(find_chart_gen()), "--spec", str(spec_path), "--out", str(FIG_DIR / name)]
    logger.info(f"Rendering {name}")
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        logger.error(f"chart_gen failed for {name}: {proc.stderr.strip()[:2000]}")
        raise RuntimeError(f"figure {name} refused by chart_gen")
    logger.info(f"Wrote figures/{name}.pdf and .png")


def main() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    specs = build_specs()
    for name, spec in specs.items():
        render(name, spec)


if __name__ == "__main__":
    main()
