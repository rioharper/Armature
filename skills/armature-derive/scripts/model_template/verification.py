"""
verification.py — Milestone 3: numeric IK and worst-case actuator sizing.

Mirrors 03_results.md; self-tests in verification_checks.py, and the tables
the note cites are printed by report_results.py. Depends on kinematics.py
(fk_num) and dynamics/statics.py (static_torques).
"""

import numpy as np
from scipy.optimize import least_squares

from params import N
from kinematics import fk_num
from dynamics.statics import static_torques

# Run order and heading for `run_all.py`, which discovers this module
# by the `test_*` callables in verification_checks.py, not by name.
MILESTONE = (3, "Milestone 3: verification")


def inverse_kinematics(target_xyz, q0=None, tol=1e-12):
    """Numeric position IK via SciPy least-squares.

    Returns (q, converged, residual_norm). Position only (3 residuals);
    append an orientation error to `resid` for full-pose IK. The seed q0
    selects the branch when several postures reach the point.
    """
    target = np.asarray(target_xyz, dtype=float).flatten()[:3]
    if q0 is None:
        q0 = np.zeros(N)

    def resid(qv):
        p = np.asarray(fk_num(*qv), dtype=float)[:3, 3]
        return p - target

    sol = least_squares(resid, np.asarray(q0, dtype=float),
                        xtol=tol, ftol=tol)
    return sol.x, bool(np.linalg.norm(sol.fun) < 1e-8), float(np.linalg.norm(sol.fun))


def worst_case_static_torque(samples=5000, seed=0, limits=None):
    """Largest-magnitude static torque per joint over the joint space, and
    the posture producing it — the number to size actuators against.

    Sampled, not guessed: a spatial mechanism's worst gravity posture is not
    always the outstretched one. `limits` is a (lo, hi) per joint in rad or m,
    default [-pi, pi]. Returns (worst_tau [N m], worst_q: a posture row per joint).
    """
    rng = np.random.default_rng(seed)
    if limits is None:
        limits = [(-np.pi, np.pi)] * N
    lo = np.array([a for a, _ in limits])
    hi = np.array([b for _, b in limits])
    Q = lo + (hi - lo) * rng.random((samples, N))
    worst_tau = np.zeros(N)
    worst_q = np.zeros((N, N))
    for qv in Q:
        tau = np.abs(static_torques(qv))
        upd = tau > worst_tau
        worst_tau = np.where(upd, tau, worst_tau)
        for j in np.where(upd)[0]:
            worst_q[j] = qv
    return worst_tau, worst_q
