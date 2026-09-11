"""
check/interference_checks.py — self-tests for interference.py, each written
to FAIL if the guard it covers is removed.
"""

import math

from build123d import Box, Location

from check.interference import interference, sweep_clearance


def test_interference_overlap_disjoint_touching():
    a = Box(10, 10, 10)
    assert math.isclose(interference(a, Box(10, 10, 10).locate(Location((5, 0, 0)))), 500.0)
    assert interference(a, Box(1, 1, 1).locate(Location((100, 0, 0)))) == 0.0
    assert interference(a, Box(10, 10, 10).locate(Location((10, 0, 0)))) == 0.0

    # min_volume is NOT a tangency floor. These two measurements are
    # exactly what sweep_clearance's docstring claims — tangency reads as
    # 0.0 (above), and the shallowest real interpenetration reads four
    # orders ABOVE the 1e-6 default, so the default filters nothing
    # physical. If either number moves, that docstring has gone stale.
    grazed = interference(a, Box(10, 10, 10).locate(Location((10 - 1e-4, 0, 0))))
    assert 0.009 < grazed < 0.011, grazed  # 0.0001 mm deep over 10x10 mm
    print("  [PASS] interference: overlap, disjoint, touching, graze")


def test_ignore_is_a_threshold_not_a_skip():
    # sweep_clearance's `ignore` is a per-pair THRESHOLD, not a blanket
    # "always skip". Two 10 mm boxes overlapping 200 mm^3 at their design
    # offset must clear; the SAME pair overlapping 500 mm^3 at a bigger
    # offset must still be reported — a blanket skip could not do that
    # once a pair was listed.
    def two_boxes(offset):
        return {
            "a": Box(10, 10, 10),
            "b": Box(10, 10, 10).locate(Location((10 - offset, 0, 0))),
        }

    design_overlap = interference(two_boxes(2.0)["a"], two_boxes(2.0)["b"])
    assert math.isclose(design_overlap, 200.0), design_overlap
    pair_ignore = {frozenset(("a", "b")): design_overlap}
    hits = sweep_clearance(two_boxes, [2.0, 5.0], ignore=pair_ignore)
    assert len(hits) == 1 and hits[0][1:3] == ("a", "b") and math.isclose(hits[0][3], 500.0), hits
    # A pair with no entry in `ignore` gets only the ordinary min_volume
    # floor, not the pair's design overlap — the same 200 mm^3 that was
    # excused above is reported here.
    hits = sweep_clearance(two_boxes, [2.0], ignore={})
    assert len(hits) == 1 and hits[0][1:3] == ("a", "b") and math.isclose(hits[0][3], 200.0), hits

    # A threshold IS a measured OCC volume, and recomputing "the same"
    # boolean elsewhere can differ by float noise (measured on the sweep's
    # base<->link1: ~2e-11 mm^3). A threshold a hair BELOW what gets
    # measured at the excused posture must not cause a false report —
    # min_volume's slop absorbs it.
    noisy_ignore = {frozenset(("a", "b")): design_overlap - 1e-10}
    assert sweep_clearance(two_boxes, [2.0], ignore=noisy_ignore) == []
    print("  [PASS] sweep_clearance: ignore is a slop-guarded threshold")
