"""
sweep/summary.py — main(): sweep the grid, collapse the hits to one row per
pair, print them (sweep/report.py), and exit nonzero on a collision.
Self-tests in summary_checks.py.
"""

from __future__ import annotations

from check import sweep_clearance
from sweep import bodies
from sweep.grid import joint_limits_and_interior
from sweep.report import print_summary


def summarize(hits, qs):
    """Collapse sweep_clearance's per-posture hits to one row per pair -
    its FIRST INTERFERING SAMPLE (smallest overlap among the hits: nearest
    to clear where overlap grows monotonically away from the clear region,
    which a mechanism need not do) and its WORST (largest overlap).

    Per PAIR, not per posture: printing every posture buries the two facts
    a reader needs behind noise that isn't even independent information -
    the worked example's link1<->link2 overlap does not depend on q1 at
    all, so its 666 raw hits are 18 distinct q2 values times 37 REDUNDANT
    q1 copies of the same finding. Reporting reported-postures as a
    FRACTION of swept ones never fixes that, because the redundancy scales
    with however fine the other, irrelevant axis is sampled. The row count
    here is bounded by the number of pairs, never by grid resolution.

    An axis a pair interferes at EVERY sampled value of contributes
    nothing to the finding, and is reported as `any` rather than as one
    arbitrary sample of it - that is what `free` carries. `qs` is passed
    in for exactly that comparison.

    Returns [(name_a, name_b, count, first_q, first_vol, worst_q,
    worst_vol, free), ...], worst-first by `worst_vol`.
    """
    swept = [{q[k] for q in qs} for k in range(len(qs[0]))]
    by_pair = {}
    for q, a, b, vol in hits:
        by_pair.setdefault((a, b), []).append((q, vol))
    rows = []
    for (a, b), entries in by_pair.items():
        entries.sort(key=lambda e: e[1])
        first_q, first_vol = entries[0]
        worst_q, worst_vol = entries[-1]
        # An axis is only "free" if it was actually VARIED. Without the
        # len > 1 guard, an axis held at a single value trivially matches
        # the swept set and prints `any` - claiming coverage of an axis
        # that was never swept, which is the one thing this sweep exists
        # not to do.
        free = tuple(
            len(swept[k]) > 1 and {q[k] for q, _ in entries} == swept[k]
            for k in range(len(swept))
        )
        rows.append((a, b, len(entries), first_q, first_vol, worst_q, worst_vol, free))
    return sorted(rows, key=lambda r: -r[6])


def main(qs=None, verbose=True) -> int:
    """Sweep `qs` (default: `joint_limits_and_interior()`) and report hits.

    `qs` is a parameter so the checks can exercise this function's real
    print/return-code behaviour against a couple of cheap hand-picked
    postures instead of paying for the full ~1400-posture default grid;
    `verbose=False` silences the printing for exactly that use.
    """
    bodies.ensure_geometry()
    if qs is None:
        qs = joint_limits_and_interior()
    if not qs:
        raise ValueError(
            "main(): no postures to sweep. An empty grid reports 'swept 0 "
            "postures, 0 interfering' and exits 0 - a clean bill of health "
            "for a mechanism nothing looked at."
        )
    hits = sweep_clearance(bodies.pose, qs, ignore=bodies.ADJACENT)
    if verbose:
        print_summary(hits, summarize(hits, qs), qs)

    # A colliding mechanism must not exit 0. The README states the
    # template's exit-code contract (nonzero means a check failed), so
    # returning 0 unconditionally here is a green CI gate on a mechanism
    # that folds into itself. Advisory-only was considered and rejected: a
    # self-collision is exactly the kind of finding "fail loud" exists for.
    return 1 if hits else 0
