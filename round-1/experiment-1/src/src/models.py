"""Cooling models for the coffee-in-a-pot screen.

Temperatures are in degrees Celsius, time in minutes. The heat capacity of the
liquid is absorbed into the fitted coefficients, so every coefficient is a
rate (1/min for the linear law) and not a physical heat-transfer coefficient.

Models
------
C0  Newton's law, constant rate:      dT/dt = -a (T - Tr)
C1  one-term nonlinear convection:    dT/dt = -a (T - Tr)^x
C2  convection plus evaporation,
    plan form (ambient-subtracted):   dT/dt = -[a (T - Tr)^x + b (T^z - Tr^z)]
C2p source form (no ambient term):    dT/dt = -[a (T - Tr)^x + b T^z]

The source paper (Sedlacek and Dolejsi) uses the convective exponent x = 1.34
and an evaporation power z = 3.73 in its fourth model, but that model also
contains pot and radiation terms that the text does not parameterize. C2 and
C2p are therefore reduced forms of the source model, not reproductions of it.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

T_ROOM_DEFAULT_C = 20.0
SOLVER_RTOL = 1e-9
SOLVER_ATOL = 1e-11


def c0_closed_form(t: np.ndarray, t0: float, a: float, t_room: float = T_ROOM_DEFAULT_C) -> np.ndarray:
    """Analytic solution of Newton's law: T(t) = Tr + (T0 - Tr) exp(-a t)."""
    return t_room + (t0 - t_room) * np.exp(-a * t)


def c1_closed_form(t: np.ndarray, t0: float, a: float, x: float, t_room: float = T_ROOM_DEFAULT_C) -> np.ndarray:
    """Analytic solution of dT/dt = -a u^x with u = T - Tr, for x != 1.

    (u^(1-x))' = (1-x) u^(-x) u' = (x-1) a, so u^(1-x)(t) = u0^(1-x) + (x-1) a t.
    """
    u0 = t0 - t_room
    if abs(x - 1.0) < 1e-9:
        return c0_closed_form(t, t0, a, t_room)
    inner = u0 ** (1.0 - x) + (x - 1.0) * a * t
    if np.any(inner <= 0):
        raise ValueError("C1 closed form left the physical domain (u reached zero)")
    return t_room + inner ** (1.0 / (1.0 - x))


def _rhs_factory(kind: str, params: tuple[float, ...], t_room: float):
    if kind == "C1":
        a, x = params

        def rhs(_t, T):
            u = max(float(T[0]) - t_room, 0.0)
            return [-a * u**x]

    elif kind == "C2":
        a, x, b, z = params

        def rhs(_t, T):
            Tv = max(float(T[0]), 0.0)
            u = max(Tv - t_room, 0.0)
            return [-(a * u**x + b * (Tv**z - t_room**z))]

    elif kind == "C2p":
        a, x, b, z = params

        def rhs(_t, T):
            Tv = max(float(T[0]), 0.0)
            u = max(Tv - t_room, 0.0)
            return [-(a * u**x + b * Tv**z)]

    else:
        raise ValueError(f"unknown model kind {kind}")
    return rhs


def integrate(kind: str, params: tuple[float, ...], t_eval: np.ndarray, t0: float, t_room: float = T_ROOM_DEFAULT_C) -> np.ndarray:
    """Solve the ODE with the first measured temperature as the initial condition."""
    if kind == "C1":
        a, x = params
        return c1_closed_form(t_eval, t0, a, x, t_room)
    rhs = _rhs_factory(kind, params, t_room)
    t_span = (0.0, float(t_eval[-1]))
    sol = solve_ivp(
        rhs,
        t_span,
        [t0],
        t_eval=t_eval,
        method="LSODA",
        rtol=SOLVER_RTOL,
        atol=SOLVER_ATOL,
    )
    if not sol.success or sol.y.shape[1] != len(t_eval):
        raise RuntimeError(f"ODE solver failed for {kind}: {sol.message}")
    return sol.y[0]
