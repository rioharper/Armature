"""
stubs.py — envelope-correct placeholders for COTS parts, for when the
armature-librarian agent can't find a vendor STEP model.

The geometry here is trivial: a bearing is two cylinders, a motor flange is
a disc with a bolt circle. If that were all this module did it would be
five lines inline in the part file and not worth importing.

What it actually enforces is the thing that goes wrong with placeholders:
a stub that outlives its excuse. A rough bearing modeled to "about 22 mm"
gets used for a clearance check, then a stack-up, then a drawing, and by
then nobody remembers it was a guess. So every builder here REQUIRES a
`source` — the datasheet P/N and the row it came from — labels the shape
`PLACEHOLDER <p/n>` so it announces itself in any assembly or export, and
can emit its own `cad/ots-parts/index.md` row.

Placeholders are good for: envelope and clearance checks, motion sweeps,
mass estimates, deciding whether a part fits before you buy it.
They are NOT good for: mating geometry in a released assembly, tolerance
stack-ups on a fit, or anything that leaves CAD. Before release grade,
every stub is replaced by vendor geometry or by a drawing dimensioned
from the datasheet — that is what `still_placeholder()` is for, subject to
the one thing it cannot see: it only knows about stubs built in its own
process, so read its docstring before trusting an empty list.
"""

from __future__ import annotations

from build123d import BuildPart, Cylinder, Hole, Mode, PolarLocations

PLACEHOLDER_COLOR = (1.0, 0.4, 0.0, 0.6)  # orange, translucent: "not real yet"

_REGISTRY: list[tuple[str, str]] = []


def _stamp(shape, part_number: str, source: str):
    if not source:
        raise ValueError(
            f"{part_number}: a placeholder without a datasheet source is a "
            "guess with a part number on it. Pass source='<datasheet row / "
            "docs/datasheets/index.md entry>', or fetch the real model with "
            "the armature-librarian agent."
        )
    shape.label = f"PLACEHOLDER {part_number}"
    shape.color = PLACEHOLDER_COLOR
    # Append-only would list the same stub twice (a bearing used at both
    # ends of a shaft, a recipe re-run in the same process) in index_rows()
    # and twice again in the release gate. Dedupe on the
    # WHOLE entry, not on the P/N: the same P/N cited to two different
    # datasheet rows is a provenance disagreement worth seeing, not a
    # duplicate to silently collapse onto whichever source ran last.
    entry = (part_number, source)
    if entry not in _REGISTRY:
        _REGISTRY.append(entry)
    return shape


def bearing(bore: float, od: float, width: float, *, part_number: str, source: str):
    """Deep-groove ball bearing envelope, mm. Origin at the bore centre,
    axis along Z. Races and shields are not modeled — this is an envelope.
    """
    with BuildPart() as bp:
        Cylinder(od / 2, width)
        Cylinder(bore / 2, width, mode=Mode.SUBTRACT)
    return _stamp(bp.part, part_number, source)


def flange(
    od: float,
    thickness: float,
    bolt_circle: float,
    bolt_count: int,
    bolt_dia: float,
    pilot_dia: float = 0.0,
    *,
    part_number: str,
    source: str,
):
    """Actuator/gearbox output flange envelope, mm. Origin at the flange
    face centre, axis along Z, body extending in -Z.

    bolt_circle is the BCD (diameter, not radius) — the single most
    commonly transposed number in a mating interface, which is why it is
    named for the datasheet's own term.
    """
    with BuildPart() as bp:
        Cylinder(od / 2, thickness)
        with PolarLocations(bolt_circle / 2, bolt_count):
            Hole(bolt_dia / 2)
        if pilot_dia:
            Hole(pilot_dia / 2)
    return _stamp(bp.part, part_number, source)


def index_rows() -> str:
    """Emit the `cad/ots-parts/index.md` rows for every stub built so far,
    so the index can't silently fall behind the geometry."""
    if not _REGISTRY:
        return ""
    lines = ["| model | P/N | source | status |", "|---|---|---|---|"]
    lines += [
        # ASCII only: this string gets printed, and a Windows cp1252
        # console garbles an em dash into a replacement character.
        f"| (build123d stub) | {pn} | {src} | PLACEHOLDER - replace before release |"
        for pn, src in _REGISTRY
    ]
    return "\n".join(lines)


def still_placeholder() -> list[str]:
    """Every stub built IN THIS PROCESS. Call from a release-grade check:
    a non-empty list is a release gate failure, because a placeholder has
    reached a point where money is about to move.

    WHAT THIS CANNOT TELL YOU. `_REGISTRY` is filled by the builders
    above as they run, so this reports on the parts THIS process actually
    built and on nothing else. An empty list therefore means one of two
    very different things:

      * every part was built here and none of them is a placeholder, or
      * nothing was built here at all.

    The second is the dangerous one, and it is also the default: a release
    script that imports this module and calls `still_placeholder()` without
    building anything gets `[]` and passes, forever, no matter how many
    stubs are sitting in the assembly. An empty list is evidence of a clean
    release ONLY from a process that has already built every part in the
    release — run the release check in the same process as the build (or
    import every `cad/parts/<PART-ID>.py` first, which is the same thing),
    and assert on the count of parts built as well as on this list.

    Deduped: building the same stub twice reports it once (see `_stamp`).
    """
    # dict.fromkeys, not set(): preserves build order, which is the order
    # index_rows() prints and the order a reader will look for them in.
    return list(dict.fromkeys(pn for pn, _ in _REGISTRY))
