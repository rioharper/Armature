"""
kinematics_checks.py — Milestone 1's self-tests, beside kinematics.py.

Discovered through kinematics.py by `run_all.py`; pytest never collects this
file directly (it doesn't match `test_*.py`), so `test_derivation.py` stays
the one bridge and the two entry points cannot disagree.
"""

import numpy as np

from params import N
from kinematics import J_num, fk_num


def test_jacobian_vs_finite_difference(trials=5, h=1e-7, tol=1e-5):
    rng = np.random.default_rng(0)
    for _ in range(trials):
        qv = rng.uniform(-np.pi, np.pi, N)
        Jn = np.asarray(J_num(*qv), dtype=float)[:3, :]   # linear part
        for i in range(N):
            dq = np.zeros(N); dq[i] = h
            p1 = np.asarray(fk_num(*(qv + dq)), dtype=float)[:3, 3]
            p0 = np.asarray(fk_num(*(qv - dq)), dtype=float)[:3, 3]
            fd = (p1 - p0) / (2 * h)
            assert np.allclose(Jn[:, i], fd, atol=tol), \
                f"Jacobian col {i} mismatch at q={qv}"
    print("  [PASS] Jacobian matches finite-difference FK")
