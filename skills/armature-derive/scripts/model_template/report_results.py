"""
report_results.py — prints what the milestone notes cite instead of pasting:
the long symbolic results and 03_results.md's tables.

    python analysis/model/report_results.py

A report renderer is never a milestone module — discovery skips `report.py`
and `report_*.py` — so table formatting never inflates the files a red-team
pass reads to check the equations. A plan task's tables get a `report_<task>.py`
of their own.
"""

import numpy as np

from params import N
from kinematics import J, T_EE
from dynamics.lagrangian import G_SYM, M_SYM
from dynamics.statics import static_torques
from verification import worst_case_static_torque

print("\n01_kinematics.md")
print("  T_0_ee =", T_EE)
print("  J =", J)

print("\n02_dynamics.md")
print("  M(q) =", M_SYM)
print("  g(q) =", G_SYM)

print("\n03_results.md: static holding torque, outstretched (q = 0) [N m]")
print("  ", static_torques(np.zeros(N)))

# The worst static torque anywhere in the workspace, not just at one posture.
wt, wq = worst_case_static_torque()
print("\n03_results.md: worst-case static torque over the workspace")
print(f"  {'joint':<7}{'|tau| [N m]':>12}  posture [rad]")
for j in range(N):
    print(f"  {j + 1:<7}{wt[j]:>12.3f}  {np.round(wq[j], 3)}")
