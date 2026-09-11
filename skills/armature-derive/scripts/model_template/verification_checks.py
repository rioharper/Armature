"""
verification_checks.py — Milestone 3's self-tests, beside verification.py.
"""

import numpy as np

from params import N
from kinematics import fk_num
from verification import inverse_kinematics


def test_ik_roundtrip(trials=5, tol=1e-4):
    """FK -> IK -> FK must return to the same end-effector position."""
    rng = np.random.default_rng(3)
    for _ in range(trials):
        q_true = rng.uniform(-1.0, 1.0, N)
        target = np.asarray(fk_num(*q_true), dtype=float)[:3, 3]
        seed = q_true + rng.uniform(-0.2, 0.2, N)   # near a valid branch
        q_sol, _ok, res = inverse_kinematics(target, q0=seed)
        p = np.asarray(fk_num(*q_sol), dtype=float)[:3, 3]
        assert np.linalg.norm(p - target) < tol, \
            f"IK position residual {res:.2e} at target {target}"
    print("  [PASS] SciPy IK round-trips against FK")
