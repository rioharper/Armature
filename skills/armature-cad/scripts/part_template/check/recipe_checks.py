"""
check/recipe_checks.py — self-tests for recipe.py, each written to FAIL if
the guard it covers is removed.
"""

from build123d import Axis, Box, Cylinder, Location, Rectangle

from check.recipe import contained, rebuild_sweep


def _raises(fn, *args, **kwargs) -> bool:
    """A check handed nothing must say so, not report green."""
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def test_contained_catches_an_escaped_feature():
    plate = Box(80, 50, 6)
    assert contained(Box(4, 4, 6).locate(Location((20, 0, 0))), plate)
    assert not contained(Box(4, 4, 6).locate(Location((20, 27, 0))), plate)
    # A feature that escapes still builds one valid solid — which is the
    # whole reason this function has to exist.
    escaped = plate.cut(Box(4, 4, 6).locate(Location((20, 27, 0))))
    assert len(escaped.solids()) == 1 and escaped.volume > 0

    # contained() sums leak.solids(), and a sketch, face or wire has none —
    # so a flat probe would read as contained from 500 mm away. It must
    # raise instead, because a zero-volume probe checked nothing.
    assert _raises(contained, Rectangle(4, 4).locate(Location((500, 0, 0))), plate)
    assert _raises(contained, plate.faces().sort_by(Axis.Z)[-1], plate)
    print("  [PASS] contained() catches an escape and refuses a flat probe")


def test_contained_tol_sits_above_the_fillet_sliver():
    # Is tol=1e-6 mm^3 actually above OCC's sliver noise? The worked
    # example never drives a probe at the filleted corners, which is where
    # booleans leave slivers, so measure it here. This probe's cylindrical
    # face is coincident with the R6 fillet AND its flat faces are coplanar
    # with the plate's — the worst tangency this template can produce.
    rounded = Box(80, 50, 6)
    rounded = rounded.fillet(6.0, rounded.edges().filter_by(Axis.Z))
    flush = Cylinder(6, 6).locate(Location((80 / 2 - 6, 50 / 2 - 6, 0)))
    spill = flush.cut(rounded)
    sliver = 0.0 if spill is None else sum(s.volume for s in spill.solids())
    # Measured, build123d 0.11.1 / OCCT: exactly 0.0 mm^3 — the floor is
    # zero, not merely small, so tol is doing no work here and must not be
    # raised to where it starts swallowing real escapes like the one below.
    assert sliver < 1e-9, f"OCC sliver at an R6 fillet is {sliver} mm^3, above tol"
    assert contained(flush, rounded)
    # .located(), not .locate(): the latter moves `flush` in place, which
    # would make this block depend on the order its assertions run in.
    assert not contained(flush.located(Location((80 / 2 - 5.9, 50 / 2 - 5.9, 0))), rounded)
    print("  [PASS] contained() tol above the measured fillet sliver")


def test_rebuild_sweep_reports_a_recipe_that_breaks():
    assert rebuild_sweep(lambda w: Box(w, 10, 10), {"w": [5, 10, 20]}) == []
    assert rebuild_sweep(lambda w: Box(w, 10, 10), {"w": [5, -1]}) != []
    print("  [PASS] rebuild_sweep reports a driven value that breaks the build")
