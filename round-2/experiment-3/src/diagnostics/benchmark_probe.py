"""Diagnostic: C0 and C1 in-window benchmark under T0 and T_room conventions (run to explain the benchmark gate failure)."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
import numpy as np
import method as M
from loguru import logger
logger.remove()
cur = M.load_curves(M.DATA_PATH)
ch = [c for c in cur if c["fold"] == 1][0]
t = ch["t"]; T = ch["T"]; tau = t - t[0]
print("in-window t:", t[t <= 30], "T:", T[t <= 30])
for mode in ("measured", "free"):
    M.T0_MODE = mode
    for Tr in (None, 20.0):
        for label, sel in (("all in-window", t <= 30), ("excl t=0", (t <= 30) & (t > 0))):
            free = ["a"]
            if Tr is None:
                fit_free = ["a", "t_room"]; fixed = {"x": 1.0}
            else:
                fit_free = ["a"]; fixed = {"x": 1.0, "t_room": Tr}
            f = M.fit(tau[sel], T[sel], fit_free, fixed)
            print(f"mode={mode:8s} Tr={'free' if Tr is None else Tr} {label:14s} C0 rms={f['rms']:.3f} params={ {k: round(v,4) for k,v in f['params'].items()} }")
    # C1 free-x variants
    for label, sel in (("all in-window", t <= 30), ("excl t=0", (t <= 30) & (t > 0))):
        f = M.fit(tau[sel], T[sel], ["a", "x"], {"t_room": 20.0})
        print(f"mode={mode:8s} C1 free-x Tr=20 {label:14s} x={f['params']['x']:.3f} rms={f['rms']:.3f}")
        f = M.fit(tau[sel], T[sel], ["a", "x", "t_room"], {})
        print(f"mode={mode:8s} C1 free-x Tr free {label:14s} x={f['params']['x']:.3f} Tr={f['params']['t_room']:.2f} rms={f['rms']:.3f}")
