"""
stubs_checks.py — self-tests for stubs.py: envelopes, the provenance
stamp, the release gate, and dedupe.
"""

from stubs import bearing, flange, index_rows, still_placeholder


def test_envelopes_and_provenance_stamp():
    b = bearing(22, 44, 12, part_number="6004-2RS", source="docs/datasheets/index.md#6004")
    assert abs(b.volume - (3.14159 * (22**2 - 11**2) * 12)) / b.volume < 1e-3
    assert b.label.startswith("PLACEHOLDER")

    f = flange(
        60, 6, 45, 4, 4.5, pilot_dia=22,
        part_number="AK80-9", source="docs/datasheets/index.md#ak80-9",
    )
    # Four bolt holes and one pilot bore removed from the disc.
    solid = 3.14159 * 30**2 * 6
    assert f.volume < solid, "holes were not cut"
    assert f.volume > solid * 0.7

    try:
        bearing(10, 20, 5, part_number="X", source="")
    except ValueError:
        pass
    else:
        raise AssertionError("empty source must be rejected")

    assert still_placeholder() == ["6004-2RS", "AK80-9"]
    assert "PLACEHOLDER" in index_rows()
    print("  [PASS] envelopes, provenance stamp, release gate")


def test_registry_dedupes_but_keeps_conflicting_sources():
    # An append-only registry lists a stub built twice in one process — a
    # bearing at both ends of a shaft, a recipe re-run in the same
    # interpreter — twice in the index and twice in the release gate.
    # Identical P/N AND source is one entry, however often it is built.
    for _ in range(2):
        bearing(22, 44, 12, part_number="6004-2RS", source="docs/datasheets/index.md#6004")
    assert index_rows().count("6004-2RS") == 1, index_rows()
    assert still_placeholder().count("6004-2RS") == 1, still_placeholder()
    # ...but the SAME P/N citing a DIFFERENT datasheet row is two conflicting
    # provenance claims, not a duplicate. Both rows stay in the index so the
    # disagreement is visible, while the gate still names the part once.
    bearing(22, 44, 12, part_number="6004-2RS", source="docs/datasheets/index.md#6004-alt")
    assert index_rows().count("6004-2RS") == 2, index_rows()
    assert still_placeholder().count("6004-2RS") == 1, still_placeholder()
    print("  [PASS] registry dedupes a repeat, keeps a conflicting source visible")
