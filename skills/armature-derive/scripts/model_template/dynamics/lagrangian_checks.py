"""
dynamics/lagrangian_checks.py — self-tests for lagrangian.py, 02_dynamics.md §1–2.
"""

import numpy as np
import sympy as sp

from params import N, t
from dynamics.lagrangian import M_SYM, C_SYM, M_num, C_num, g_num, total_energy


def test_mass_matrix_properties(trials=5, tol=1e-9):
    rng = np.random.default_rng(1)
    for _ in range(trials):
        qv = rng.uniform(-np.pi, np.pi, N)
        Mn = np.asarray(M_num(*qv), dtype=float)
        assert np.allclose(Mn, Mn.T, atol=tol), "M not symmetric"
        assert np.all(np.linalg.eigvalsh(Mn) > 0), "M not positive definite"
    print("  [PASS] M(q) symmetric positive-definite")


def test_skew_symmetry(tol=1e-8):
    """Mdot - 2C must be skew-symmetric (Christoffel C)."""
    Mdot = M_SYM.diff(t)
    S = sp.simplify(Mdot - 2 * C_SYM)
    assert sp.simplify(S + S.T) == sp.zeros(N, N), "Mdot-2C not skew"
    print("  [PASS] Mdot - 2C skew-symmetric")


def test_energy_conservation(T_end=2.0, tol_rel=1e-4):
    """Unforced, gravity-on dynamics conserve total mechanical energy.

    RK45 at tight tolerances from a nonzero posture at rest, E(T) against
    E(0): one check that exercises the numeric M, C, g and V together.
    """
    from scipy.integrate import solve_ivp

    def rhs(_t, s):
        qv, qdv = s[:N], s[N:]
        Mn = np.asarray(M_num(*qv), dtype=float)
        Cn = np.asarray(C_num(*qv, *qdv), dtype=float)
        gn = np.asarray(g_num(*qv), dtype=float).flatten()
        qddv = np.linalg.solve(Mn, -(Cn @ qdv) - gn)
        return np.concatenate([qdv, qddv])

    q0 = np.zeros(N)
    if N >= 1:
        q0[0] = 0.3
    if N >= 2:
        q0[1] = -0.4
    s0 = np.concatenate([q0, np.zeros(N)])
    E0 = total_energy(s0[:N], s0[N:])
    sol = solve_ivp(rhs, (0.0, T_end), s0, method="RK45",
                    rtol=1e-10, atol=1e-12, max_step=1e-2)
    assert sol.success, f"integration failed: {sol.message}"
    sf = sol.y[:, -1]
    E1 = total_energy(sf[:N], sf[N:])
    scale = max(abs(E0), 1e-6)
    assert abs(E1 - E0) / scale < tol_rel, \
        f"Energy drift {(E1 - E0) / scale:.2e} exceeds {tol_rel}"
    print("  [PASS] total energy conserved under SciPy integration")
