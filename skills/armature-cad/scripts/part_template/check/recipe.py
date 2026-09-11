"""
check/recipe.py — the recipe actually builds: features stay inside their
parent, and driven parameters rebuild. Self-tests in recipe_checks.py.
"""

from __future__ import annotations


def contained(inner, outer, tol: float = 1e-6) -> bool:
    """True if `inner` lies entirely inside `outer`.

    This is the check `rebuild_sweep` alone cannot make. A feature that
    escapes its parent — a bolt hole hanging off a plate edge, a boss
    overhanging its flange — still produces one valid solid with the same
    bounding box, and a hole that's half outside removes LESS material, so
    volume goes up rather than down. Nothing about the build fails. The
    part is simply wrong.

    Call it in the recipe on a SOLID probe of the feature: the shape that
    has to BE metal, extruded. Prefer a probe that stays valid against the
    FINISHED part — part.py's `_assert_pattern_fits` probes the RING of
    metal around each bolt hole rather than a disc over it, and so runs
    after every cut. A probe only valid against the blank has to run before
    the cut, and nothing in the code can say so: that unstated ordering is
    what let a bolt circle whose holes sat inside the bore pass.

    `inner` must be a solid. This measures the leaked VOLUME, and a sketch,
    face or wire has none, so a flat probe would read as contained from
    500 mm away. That is why it raises rather than returning True.

    tol is the leak volume in mm^3 tolerated as boolean noise. Measured on
    build123d 0.11.1 / OCCT: a probe whose face is coincident with an R6
    fillet — plus both flat faces — leaks EXACTLY 0.0 mm^3. The noise floor
    at a filleted corner is zero, not merely small, so the 1e-6 default is
    absorbing nothing and nothing measured here argues for a larger one.
    Keep it small for that reason: every mm^3 of tol is a real escape this
    would not report (recipe_checks.py measures both).
    """
    if inner.volume <= 0:
        raise ValueError(
            "contained(): `inner` has no volume, so there is nothing to test - "
            "pass a solid probe of the feature, not a sketch, face or wire."
        )
    leak = inner.cut(outer)
    if leak is None:
        return True
    return sum(s.volume for s in leak.solids()) <= tol


def rebuild_sweep(build, cases: dict[str, list]) -> list[str]:
    """"The model rebuilds cleanly after changing each driven parameter."

    `build` is a callable taking keyword overrides and returning the part.
    `cases` maps a driven parameter name to the values to try. Each value
    is built on its own; a build that raises, returns None, or produces
    zero volume is a recipe that only works at its nominal numbers.

    Returns a list of failures; empty means every driven parameter rebuilds.
    """
    fails = []
    for name, values in cases.items():
        for value in values:
            try:
                part = build(**{name: value})
            except Exception as exc:  # noqa: BLE001 - any failure is the finding
                fails.append(f"{name}={value}: rebuild raised {type(exc).__name__}: {exc}")
                continue
            if part is None or part.volume <= 0:
                fails.append(f"{name}={value}: rebuilt to empty geometry")
    return fails
