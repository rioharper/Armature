"""
dynamics/lagrangian.py — 02_dynamics.md §1–2: T, V, and M(q) q̈ + C q̇ + g = τ.

Builds the Euler-Lagrange equations on kinematics.py's frames and lambdifies
them against params.PARAMS. Self-tests in lagrangian_checks.py.
"""

import numpy as np
import sympy as sp
from sympy import Matrix

from params import (COM_LOCAL, INERTIA, MASSES, GRAVITY_VEC, N, t,
                    q, qd, qdd, QS, QDS, SUB_Q, SUB_P)
from kinematics import FRAMES


def lagrangian_dynamics(frames):
    """Euler-Lagrange. Returns (M, C, gvec, V) with tau = M qdd + C qd + g.

    C is the Christoffel form, the one the skew-symmetry check needs. V is
    returned so energy is checked as KE + V directly, not through a work
    integral.
    """
    KE = sp.S.Zero
    PE = sp.S.Zero
    for i in range(N):
        T_i = frames[i]
        R_i = T_i[:3, :3]
        p_com = T_i[:3, 3] + R_i * COM_LOCAL[i]
        v_com = p_com.diff(t)
        # angular velocity from R' = [w]x R  ->  [w]x = R' R^T
        Wx = sp.trigsimp(R_i.diff(t) * R_i.T)
        w = Matrix([Wx[2, 1], Wx[0, 2], Wx[1, 0]])
        I_base = R_i * INERTIA[i] * R_i.T
        KE += (MASSES[i] * (v_com.T * v_com)[0]
               + (w.T * I_base * w)[0]) / 2
        PE += -MASSES[i] * (GRAVITY_VEC.T * p_com)[0]

    L = sp.trigsimp(KE - PE)
    eqs = Matrix([sp.diff(sp.diff(L, qd[i]), t) - sp.diff(L, q[i])
                  for i in range(N)])
    eqs = sp.expand(sp.trigsimp(eqs))

    M = eqs.jacobian(qdd)
    gvec = eqs.subs([(v, 0) for v in qdd]).subs([(v, 0) for v in qd])
    Cqd = sp.simplify(eqs - M * qdd - gvec)   # Coriolis+centrifugal * qd
    Cmat = sp.zeros(N, N)
    for k in range(N):
        for j in range(N):
            Cmat[k, j] = sum(
                sp.Rational(1, 2)
                * (sp.diff(M[k, j], q[i]) + sp.diff(M[k, i], q[j])
                   - sp.diff(M[i, j], q[k])) * qd[i]
                for i in range(N))
    Cmat = sp.simplify(Cmat)
    assert sp.simplify(Cmat * qd - Cqd) == sp.zeros(N, 1), \
        "Christoffel C inconsistent with E-L expansion"
    return sp.simplify(M), Cmat, sp.simplify(gvec), sp.simplify(PE)


print("Building symbolic dynamics ...")
M_SYM, C_SYM, G_SYM, V_SYM = lagrangian_dynamics(FRAMES)
print("  Dynamics built.")

# --- numeric functions, lambdified, parameterized by params.PARAMS ---
M_num = sp.lambdify(QS, M_SYM.subs(SUB_Q).subs(SUB_P), "numpy")
C_num = sp.lambdify(QS + QDS, C_SYM.subs(SUB_Q).subs(SUB_P), "numpy")
g_num = sp.lambdify(QS, G_SYM.subs(SUB_Q).subs(SUB_P), "numpy")
V_num = sp.lambdify(QS, V_SYM.subs(SUB_Q).subs(SUB_P), "numpy")


def total_energy(q_vals, qd_vals):
    """Total mechanical energy E = KE + V [J] at a state."""
    Mn = np.asarray(M_num(*q_vals), dtype=float)
    ke = 0.5 * np.asarray(qd_vals) @ Mn @ np.asarray(qd_vals)
    pe = float(np.asarray(V_num(*q_vals), dtype=float))
    return ke + pe
