"""
part_checks.py — the recipe's self-tests: an assertion behind every guard
in part.py, each written to FAIL if the guard it covers is removed.

Copy beside the part as `cad/parts/<PART-ID>_checks.py`. The line below
loads the part by this file's own name, because a part ID like ARM-BRK-001
is a file name `import` cannot spell.

The geometry assertions are about the WORKED EXAMPLE. When you replace the
recipe, replace them with the same question asked about your part — they are
the only thing standing between a silently wrong dimension and a green run.
"""

import importlib
import inspect
import math
import sys
import tempfile
from pathlib import Path

from build123d import Axis

from check import compare_to_target, contained, mass_properties

part = importlib.import_module(Path(__file__).stem.removesuffix("_checks"))


def _raised(exc_type, fn, *args, **kwargs):
    """The exception `fn` raised, or None. A check that cannot fail is
    not a check, so every use of this is asserted truthy."""
    try:
        fn(*args, **kwargs)
    except exc_type as exc:
        return exc
    return None


def _resolve_with(params_src, key, allow=True):
    """Resolve a target against a params.py written to a temp dir, and
    return (target, provenance, that temp params.py).

    EVERY directory on sys.path that holds a params.py is dropped for
    the duration, not just PARAMS_DIR: `import params` searches the
    whole path, including the part's own directory, so a project that
    keeps params.py beside the part file would otherwise have its real
    one answer the case that is meant to test having none.
    """
    saved = sys.path[:]
    with tempfile.TemporaryDirectory() as tmp:
        if params_src is not None:
            Path(tmp, "params.py").write_text(params_src)
        sys.path[:] = [tmp] + [p for p in saved if not Path(p or ".", "params.py").exists()]
        sys.modules.pop("params", None)
        importlib.invalidate_caches()
        try:
            return part._resolve_target(key, allow_fallback=allow) + (Path(tmp, "params.py"),)
        finally:
            sys.path[:] = saved
            sys.modules.pop("params", None)


def test_target_provenance_is_the_truth():
    renamed = "PARAMS = {'m_link1': 1.20}\n"  # what a re-derivation does
    # params.py present, key gone. Swallowing that substitutes a hand-typed
    # 0.105 kg, prints "no analysis/model/params.py yet" with params.py
    # sitting right there, and exits 0.
    assert _raised(KeyError, _resolve_with, renamed, "m1")
    # A missing PARAMS table and a params.py whose own imports fail are the
    # same class of event, and must not fail three different ways.
    assert _raised(AttributeError, _resolve_with, "MASSES = {}\n", "m1")
    assert _raised(ModuleNotFoundError, _resolve_with, "import no_such_module_xyz\n", "m1")

    target, prov, real = _resolve_with("PARAMS = {'m1': 0.104}\n", "m1")
    assert target == {"mass": 0.104}
    # The line must name the file that was actually imported, not the
    # directory the template HOPED to read: the module here is loaded from
    # a temp dir, so naming PARAMS_DIR would be exactly that false credit.
    assert prov == f"target driven from {real}[m1]", prov

    # The fallback: opt-in, and honest about which of the two reasons it is.
    target, prov, _ = _resolve_with(None, "m1")
    assert target == {"mass": part.BUDGET_MASS} and "FALLBACK" in prov, prov
    assert _raised(RuntimeError, _resolve_with, None, "m1", False)
    # An unset PARAM_KEY falls back even though params.py is RIGHT THERE,
    # so the line must not claim the file is missing. Spelled out rather
    # than read from PARAM_KEY, which you are expected to set.
    target, prov, _ = _resolve_with(renamed, "<params key for this body>")
    assert "FALLBACK" in prov and "placeholder" in prov, prov
    assert "no params.py" not in prov, prov
    # Whatever the fallback produces still has to be a target check/ will
    # accept — it raises on an empty one, and an empty one is a green gate.
    assert isinstance(compare_to_target(mass_properties(part.build(), part.DENSITY), target), list)
    print("  [PASS] target provenance: fallback opt-in and honest, broken links raise")


def test_boss_follows_the_bore():
    def boss_wall(solid, bore):
        """Wall read off the finished part: its top face is the boss
        annulus, area pi/4 * (od^2 - bore^2)."""
        area = solid.faces().sort_by(Axis.Z)[-1].area
        return (math.sqrt(4 * area / math.pi + bore**2) - bore) / 2

    for bore in (part.BORE, 24.0):
        # Frozen at module scope this reads 5.00 mm at a 24 mm bore, and a
        # wall <= 0 guard fires nowhere in the swept range.
        assert math.isclose(boss_wall(part.build(bore=bore), bore), part.BOSS_WALL, abs_tol=1e-9)
    print("  [PASS] boss wall measured off the solid, at two bores")


def test_bolt_pattern_probe_sees_bore_and_edge():
    for bc in (22.0, 26.0):  # holes inside the bore / breaking into it
        assert "bore" in str(_raised(ValueError, part.build, bolt_circle=bc))
    # Measured: a 28.6 mm bore builds clean on a 2.70 mm boss wall, with
    # the bolt holes 1.05 mm into it.
    assert "bore" in str(_raised(ValueError, part.build, bore=28.6))
    # Ordering cannot change the answer: the ring probe is contained in the
    # FINISHED part, where a disc probe leaks its own holes.
    assert contained(part._pattern_probe(part.BOLT_CIRCLE), part.build())

    # The code applies the rule its comment states: EDGE_DIST of metal
    # beyond the hole WALL, not from its centre. Both bounds are spelled out
    # from the rule rather than from EDGE_REACH, so a probe measuring from
    # the centre instead (limit 59.0 mm, not 54.5) fails the second one
    # rather than moving with it. 1 mm inside the limit, as main()'s sweep
    # is: at exactly 54.5 the probe's outer face lands on the plate edge,
    # and betting a self-check on an OCCT boolean returning 0.0 rather than
    # 1e-9 is a coin toss.
    part.build(bolt_circle=part.PLATE_W - part.BOLT_CLEARANCE - 2 * part.EDGE_DIST - 1.0)  # 53.5
    assert "plate" in str(_raised(ValueError, part.build, bolt_circle=part.PLATE_W - 2 * part.EDGE_DIST - 1))
    print("  [PASS] bolt pattern probe sees the bore and the plate edge")


def test_no_dimension_is_both_parameter_and_constant():
    assert set(inspect.signature(part.build).parameters) == {"bolt_circle", "bore"}
    assert _raised(TypeError, part.build, plate_t=3.0)  # not a parameter at all
    print("  [PASS] only driven dimensions are parameters")
