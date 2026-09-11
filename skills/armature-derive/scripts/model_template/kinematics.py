"""
kinematics.py — Milestone 1: forward kinematics and the geometric Jacobian.

Mirrors 01_kinematics.md; its self-tests are in kinematics_checks.py. Imports
only params.py, so a red-team pass on Milestone 1 reads this file, its checks,
and the parameter block. Check it alone: `python run_all.py kinematics`.

Modified DH (Craig). Keep the structure if the note uses another convention:
symbolic build -> numeric functions.
"""

import sympy as sp
from sympy import cos, sin, Matrix

from params import DH, T_TOOL, q, QS, SUB_Q, SUB_P

# Run order and heading for `run_all.py`, which discovers this module
# by the `test_*` callables in kinematics_checks.py, not by name.
MILESTONE = (1, "Milestone 1: kinematics")


def dh_transform(alpha, a, d, theta):
    """Modified DH single-link transform (Craig, eq. 3.6)."""
    ca, sa, ct, st = cos(alpha), sin(alpha), cos(theta), sin(theta)
    return Matrix([
        [ct,      -st,      0,   a],
        [st * ca,  ct * ca, -sa, -sa * d],
        [st * sa,  ct * sa,  ca,  ca * d],
        [0,        0,        0,   1],
    ])


def forward_kinematics():
    """Returns (list of T_0_i for each link frame, T_0_ee)."""
    T = sp.eye(4)
    frames = []
    for row in DH:
        T = T * dh_transform(*row)
        frames.append(sp.trigsimp(T))
    T_ee = sp.trigsimp(T * T_TOOL)
    return frames, T_ee


def geometric_jacobian(frames, T_ee):
    """6xN geometric Jacobian of the end-effector, base frame."""
    p_ee = T_ee[:3, 3]
    cols = []
    for i, row in enumerate(DH):
        # Modified DH (Craig): joint i acts about z of frame {i}, and the
        # origin of frame {i} lies on that axis. (Standard DH would use
        # frame {i-1} here — adjust if you change conventions.)
        T_i = frames[i]
        z = T_i[:3, 2]
        p = T_i[:3, 3]
        is_prismatic = not row[3].has(q[i])   # q in d_i => prismatic
        if is_prismatic:
            Jv, Jw = z, Matrix([0, 0, 0])
        else:
            Jv, Jw = z.cross(p_ee - p), z
        cols.append(Jv.col_join(Jw))
    return sp.trigsimp(Matrix.hstack(*cols))


print("Building symbolic kinematics ...")
FRAMES, T_EE = forward_kinematics()
J = geometric_jacobian(FRAMES, T_EE)
print("  FK and Jacobian built.")

# --- numeric functions, lambdified, parameterized by params.PARAMS ---
fk_num = sp.lambdify(QS, T_EE.subs(SUB_Q).subs(SUB_P), "numpy")
J_num = sp.lambdify(QS, J.subs(SUB_Q).subs(SUB_P), "numpy")
