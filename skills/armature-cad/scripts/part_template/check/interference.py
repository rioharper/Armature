"""
check/interference.py — overlap between bodies, one posture or a whole
motion range. Self-tests in interference_checks.py.
"""

from __future__ import annotations


def interference(a, b) -> float:
    """Overlap volume of two shapes in mm^3. 0.0 means they clear.

    Cheap enough to run over a whole motion sweep, which is the point:
    at the kinematics or planning stage the parts are still crude
    envelopes and this is the only clearance check available.
    """
    common = a.intersect(b)
    if common is None:
        return 0.0
    return sum(s.volume for s in common.solids())


def sweep_clearance(pose, qs, ignore=None, min_volume=1e-6) -> list[tuple]:
    """Check every pair of bodies for interference across a motion range.

    Args:
        pose: callable q -> {name: shape}, positioning the bodies at
            posture q. Envelope primitives are fine and preferred here —
            this runs len(qs) * n_pairs booleans.
        qs: the postures to check. Sample the workspace, and include the
            joint limits: interference lives at the extremes.
        ignore: {frozenset({"upper_arm", "forearm"}): threshold_mm3, ...}
            — a pair sharing a joint can overlap there even when nothing
            is wrong (e.g. a base post's radius reaching past the joint
            into the next link, by construction). Give the OVERLAP
            MEASURED AT THE PAIR'S OWN DESIGN/NEUTRAL POSTURE as the
            threshold, not a guessed margin — sweep/bodies.py derives it by
            calling `pose()` once at the home posture and taking
            `interference()` for the ONE pair that fits this mechanism
            (see below — most pairs don't), so the excuse is sized to
            what the envelope actually does at rest, not picked by feel.
            Overlap ABOVE the threshold is reported like any other pair,
            at whatever posture it happens. A blanket "never report this
            pair" is not on offer: a pair sharing a joint also has the
            widest range of legitimate relative motion, so blanketing it
            suppresses the fold-in collision that pair is most likely to
            have — on a 2R arm, exactly the elbow limit you came for.

            A THRESHOLD MEASURED AT ONE POSTURE ONLY FITS A PAIR WHOSE
            OVERLAP DOES NOT CHANGE WITH POSTURE. The sweep template's own
            worked example is the cautionary tale: link1<->link2's overlap
            is 0.0 mm^3 at the neutral posture and GROWS with the elbow's
            bend, so a threshold measured at neutral excuses effectively
            nothing — measured, it flags 98.2% of the swept grid. A pair
            like that needs its excuse built into the GEOMETRY instead —
            sweep/bodies.py's `JOINT_TRIM` sets link2's box back from the
            elbow so it has a real gap to bend through before it overlaps
            at all, which is what a threshold, measured at any single
            posture, cannot give it. Use `ignore` only for a pair you have
            checked behaves like base<->link1 there: the SAME overlap at
            every posture the pair reaches, not merely the smallest one.

            RESIDUAL BLIND SPOT, for a pair that DOES fit `ignore`: it is
            excused up to its threshold volume at EVERY posture in the
            sweep, not only near the joint. A genuine collision whose
            volume is smaller than that pair's own design overlap is
            invisible wherever it occurs. This is harmless for a pair
            whose design overlap is the SAME at every posture that reaches
            it (e.g. one fixed by a rotationally-symmetric envelope, as
            base<->link1 is in the sweep's worked example) — there, the
            threshold can never be smaller than what is already there
            while something else is wrong. It is a real gap for any other
            pair, which is exactly why a growing-overlap pair belongs in
            geometry, not in this dict.

            A GEOMETRIC excuse (a trim, a rounded corner) has a DIFFERENT
            residual blind spot than a threshold, and it is not this one:
            it removes material from the model, so a collision between
            that missing material and ANY body — not only the pair it was
            trimmed for — is invisible, because there is nothing there to
            test. sweep/bodies.py's `JOINT_TRIM` documents this explicitly
            next to where it's applied; a `.py` that adds a geometric excuse
            of its own needs the same disclosure, in that file, not just here.
        min_volume: mm^3 below which an overlap is discarded as a boolean
            sliver — the floor every pair gets, including one named in
            `ignore` with a smaller threshold. NOT a tangency floor — OCC
            reports exact tangency as exactly 0.0 (measured on 0.11.1:
            coincident faces, a touched edge, and a cylinder tangent to a
            plane all return 0.0), so tangency never reaches this test.
            Nor is the default a meaningful envelope filter: 0.0001 mm of
            interpenetration between two 10 mm cubes measures 0.01 mm^3,
            ten thousand times this default, so every real contact is
            reported. It exists only to drop slivers, and it is
            deliberately left where it swallows nothing physical. Raise it
            if you want shallow grazes ignored, and pick the number from
            the graze depth you'll accept. This is the ONLY floor a pair
            with no `ignore` entry gets — a bare `v > min_volume`, not
            doubled.

            A pair NAMED in `ignore` gets `min_volume` a second time, as a
            floating-point slop guard on its threshold: a threshold IS the
            OCC volume measured at one posture, and recomputing "the same"
            boolean at a different posture can differ in the last bits
            (measured on the sweep's base<->link1: +2.18e-11 / -1.46e-11
            mm^3 across 37 samples of the SAME nominal overlap). A bare
            `v > threshold` reports that noise as a collision.
            `min_volume`'s default (1e-6) is ~1e5x that measured noise and
            still ~1e4x below the shallowest real contact this module
            measures (0.01 mm^3, measured in interference_checks.py), so it
            swallows the float noise and nothing physical either way.

    Returns [(q, name_a, name_b, overlap_mm3), ...], worst first.
    """
    ignore = {} if ignore is None else {frozenset(pair): float(v) for pair, v in ignore.items()}
    hits = []
    for q in qs:
        bodies = pose(q)
        names = sorted(bodies)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                v = interference(bodies[a], bodies[b])
                key = frozenset((a, b))
                if key in ignore:
                    # `ignore[key]` IS a measured OCC volume, not an exact
                    # mathematical constant - compare with min_volume's
                    # slop, not bit-exact, or a recomputation of "the same"
                    # overlap a few ULPs off false-reports.
                    threshold = ignore[key] + min_volume
                else:
                    # An ordinary pair keeps exactly min_volume, not
                    # min_volume*2 - there is no separate measurement here
                    # for float noise to creep in between.
                    threshold = min_volume
                if v > threshold:
                    hits.append((q, a, b, v))
    return sorted(hits, key=lambda h: -h[3])
