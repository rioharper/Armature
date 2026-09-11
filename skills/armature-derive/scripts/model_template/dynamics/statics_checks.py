"""
dynamics/statics_checks.py — self-tests for statics.py, 02_dynamics.md §3.
"""

import numpy as np

from params import N, PARAMS
from dynamics.statics import static_torques


def test_static_torques_match_moment_arms(tol=1e-9):
    """At q = 0 the arm lies along x: each joint holds the weight outboard of
    it times that weight's lever arm. Hand-written for the 2R example —
    replace with your mechanism's moment-arm calculation."""
    p = PARAMS
    by_hand = p["g"] * np.array([p["m1"] * p["lc1"] + p["m2"] * (p["l1"] + p["lc2"]),
                                 p["m2"] * p["lc2"]])
    tau = static_torques(np.zeros(N))
    assert np.allclose(tau, by_hand, atol=tol), \
        f"g(0) = {tau} disagrees with the moment-arm calculation {by_hand}"
    print("  [PASS] static torques match the moment-arm calculation")
