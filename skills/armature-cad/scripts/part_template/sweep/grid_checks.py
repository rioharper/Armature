"""
sweep/grid_checks.py — self-tests for grid.py: the default step is fine
enough for the worked example's narrowest band, and the step a report
quotes never under-warns.
"""

import math

from check import interference
from sweep import bodies
from sweep.grid import grid_steps, joint_limits_and_interior


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def test_grid_needs_both_limits():
    # n<2 is a bare ZeroDivisionError (n=1: division by n-1=0) unless
    # guarded; it must raise a clear error instead.
    assert _raises(joint_limits_and_interior, 1)
    assert _raises(joint_limits_and_interior, 0)
    print("  [PASS] a grid too small to hold both limits raises")


def test_default_step_finer_than_the_narrowest_band():
    bodies.ensure_geometry()
    # Re-measure base<->link2's band near the folded limit at 1 deg,
    # instead of trusting the docstring's number, so a geometry change
    # that moves the band fails THIS assertion first.
    def band_reach(sign):
        """Degrees inward from the +-180 deg endpoint that base<->link2
        stays interfering, at 1 deg steps."""
        for deg in range(1, 30):
            p = bodies.pose((0.0, math.radians(sign * (180 - deg))))
            if interference(p["link2"], p["base"]) <= 0.0:
                return deg - 1
        raise AssertionError("band wider than the scanned range")

    assert band_reach(1) == band_reach(-1) == 11
    step = 360.0 / (37 - 1)
    assert step < 11, f"resolution step {step} deg can step over the 11 deg band"
    print("  [PASS] default 10 deg step finer than the measured 11 deg band")


def test_step_is_the_largest_gap():
    # The caveat says the true onset lies up to ONE STEP before the first
    # interfering sample, so a non-uniform grid's step must be its LARGEST
    # gap; the smallest would under-warn.
    ragged = [(0.0, math.radians(d)) for d in (0.0, 1.0, 91.0)]
    assert math.isclose(grid_steps(ragged)[1], 90.0), grid_steps(ragged)
    print("  [PASS] reported step is the largest gap")
