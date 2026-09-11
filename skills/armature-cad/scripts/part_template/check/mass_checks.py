"""
check/mass_checks.py — self-tests for mass.py: the unit conversions against
a closed-form box, and an assertion behind every guard in compare_to_target,
each written to FAIL if the guard it covers is removed.
"""

import math

from build123d import Box, Cylinder, Location, Axis

from check.mass import compare_to_target, mass_properties

RHO = 2700.0  # aluminium 6061


def _raises(fn, *args, **kwargs) -> bool:
    """A check handed nothing must say so, not report green."""
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def _box():
    """The 10x20x30 mm box of the unit contract's sanity line: (props, m, ixx)."""
    m = 10 * 20 * 30 * 1e-9 * RHO
    return mass_properties(Box(10, 20, 30), RHO), m, m / 12 * (0.020**2 + 0.030**2)


def test_units_against_closed_form_box():
    props, m, ixx = _box()
    assert math.isclose(props["mass"], m, rel_tol=1e-9), props["mass"]
    assert math.isclose(props["inertia"][0][0], ixx, rel_tol=1e-9), props["inertia"][0][0]

    # Parallel axis: shifting to a point 50 mm off in x must not change
    # Ixx (the offset is along x) but must add m*d^2 to Iyy and Izz.
    off = mass_properties(Box(10, 20, 30), RHO, about=(50, 0, 0))
    assert math.isclose(off["inertia"][0][0], ixx, rel_tol=1e-9)
    iyy = m / 12 * (0.010**2 + 0.030**2) + m * 0.050**2
    assert math.isclose(off["inertia"][1][1], iyy, rel_tol=1e-9), off["inertia"][1][1]

    # Translating the part must not change its COM-referenced inertia.
    moved = mass_properties(Box(10, 20, 30).locate(Location((7, -3, 11))), RHO)
    assert math.isclose(moved["inertia"][0][0], ixx, rel_tol=1e-9)
    assert math.isclose(moved["com"][0], 0.007, abs_tol=1e-12)
    print("  [PASS] units and parallel axis against a closed-form box")


def test_diagonal_is_never_scale_relative():
    # A slender body — every robot link — has an axial moment legitimately
    # far below its transverse ones. Gating the DIAGONAL against the trace
    # scale, the treatment off-diagonal products need, buys it an absolute
    # tolerance bigger than the term itself. This 400x8x8 bar target vs a
    # realized 30 mm OD tube is 20x wrong on Ixx (7.37e-07 against
    # 1.49e-05) and a scale-relative diagonal returns [].
    bar = mass_properties(Box(400, 8, 8), RHO)
    tube = Cylinder(15, 400).cut(Cylinder(14.3, 400)).rotate(Axis.Y, 90)
    tube_props = mass_properties(tube, RHO)
    assert tube_props["inertia"][0][0] / bar["inertia"][0][0] > 20
    slender = compare_to_target(tube_props, {"inertia": bar["inertia"], "about": None})
    assert any("inertia[0][0]" in f for f in slender), slender

    # THE THIN ROD, the standard idealization an armature-derive derivation
    # hands you for a link: I_axial = 0 EXACTLY, I_transverse = m*L^2/12.
    # An absolute floor for a zero diagonal grants the axial term
    # tol * max(diagonal) — 10% of the TRANSVERSE moment, orders of
    # magnitude above the axial term — so the realized tube's 1.49e-05
    # against a target of 0.0 reports clean. It must fail instead.
    transverse = tube_props["mass"] * 0.400**2 / 12
    rod = [[0.0, 0.0, 0.0], [0.0, transverse, 0.0], [0.0, 0.0, transverse]]
    rod_fails = compare_to_target(tube_props, {"inertia": rod, "about": None})
    assert any("inertia[0][0]" in f for f in rod_fails), rod_fails
    # ...and only that term: the transverse pair really does match a rod.
    assert len(rod_fails) == 1, rod_fails

    # ...while an off-diagonal product still gets its absolute tolerance,
    # which is the whole reason that branch exists.
    near_zero = [row[:] for row in bar["inertia"]]
    # Guard the guard: this only proves anything while the realized Ixy is
    # nonzero (OCC leaves ~1e-22). If a future OCCT returns an exact 0.0 the
    # control would pass vacuously, comparing 0.0 against 0.0.
    assert bar["inertia"][0][1] != 0.0
    near_zero[0][1] = near_zero[1][0] = 0.0
    assert compare_to_target(bar, {"inertia": near_zero, "about": None}) == []
    print("  [PASS] diagonal fractional at any size, off-diagonal absolute")


def test_targets_that_check_nothing_raise():
    props, m, _ixx = _box()
    assert compare_to_target(props, {"mass": m}) == []
    assert compare_to_target(props, {"mass": m * 1.5}) != []

    # A target that can check nothing is a permanently green gate.
    assert _raises(compare_to_target, props, {})
    assert _raises(compare_to_target, props, {"masss": 0.0001})
    assert _raises(compare_to_target, props, {"com_tol": 0.001})
    assert _raises(compare_to_target, props, {"mass": m, "com_tol": 0.001})
    assert _raises(compare_to_target, props, {"mass": m, "about": None})
    # An inertia target with no `about` is compared against whatever point
    # the props happened to use, with nothing asserting the two agree.
    assert _raises(compare_to_target, props, {"inertia": props["inertia"]})
    # A tensor that isn't 3x3 used to die on a bare IndexError/TypeError,
    # which no caller can distinguish from a bug in this module.
    assert _raises(compare_to_target, props, {"inertia": props["inertia"][:2], "about": None})
    assert _raises(compare_to_target, props, {"inertia": [0.0] * 9, "about": None})

    # zip() truncates, so a short com would check x and silently skip y, z.
    assert _raises(compare_to_target, props, {"com": (0.0,)})
    assert compare_to_target(props, {"com": props["com"]}) == []
    print("  [PASS] target validation: every silent-green target raises")


def test_about_is_a_point_not_a_string():
    # `about` is a structural point, not a formatted string. A target
    # written (50, 0, 0) has to match a tensor taken about (50.0, 0, 0);
    # compared as text those render differently and false-FAIL, and the
    # commented template in part.py suggests exactly that text.
    off = mass_properties(Box(10, 20, 30), RHO, about=(50, 0, 0))
    assert off["about"] == (50.0, 0.0, 0.0)
    assert compare_to_target(off, {"inertia": off["inertia"], "about": (50, 0, 0)}) == []
    assert compare_to_target(off, {"inertia": off["inertia"], "about": [50.0, 0, 0]}) == []
    # A genuine mismatch — COM tensor vs joint-origin tensor — still fails.
    assert compare_to_target(off, {"inertia": off["inertia"], "about": None}) != []
    # The old string form is rejected loudly, not compared as an opaque blob.
    assert _raises(compare_to_target, off, {"inertia": off["inertia"], "about": "com"})
    print("  [PASS] `about` compared as a point")
