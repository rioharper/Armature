"""
check/report.py — prints one part's result. A renderer: it checks nothing,
and discovery never takes it for a module with checks of its own.
"""

from __future__ import annotations

from check.mass import about_label


def report(name: str, props: dict, fails: list[str]) -> bool:
    """Print one part's result. Returns True if it passed."""
    print(f"--- {name}")
    print(f"    mass      {props['mass'] * 1000:9.2f} g")
    print("    com       " + "  ".join(f"{c * 1000:8.2f}" for c in props["com"]) + "  mm")
    print(f"    inertia about {about_label(props['about'])} [kg m^2]:")
    for row in props["inertia"]:
        print("      " + "  ".join(f"{v: .4e}" for v in row))
    if fails:
        print(f"    FAIL ({len(fails)}):")
        for f in fails:
            print(f"      - {f}")
    else:
        print("    ok")
    return not fails
