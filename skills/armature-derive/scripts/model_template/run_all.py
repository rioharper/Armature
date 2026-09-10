"""
run_all.py — every milestone's self-tests, in order, end to end.

Two commands run this model's checks, and both find their work here:

    python analysis/model/run_all.py    # the milestone checkpoint command
    pytest                              # through test_derivation.py

Discovery is by shape, not by name: any module in this directory that defines
callables named `test_*` is a milestone module, and each of those callables is
one check. Nothing in this file lists modules or tests, so a module added
later — a `spring.py` for a plan task, a `thermal.py` — is collected the
moment it lands, and so is a test added to a module that already exists.

That is deliberate. A hardcoded list is a list you forget to add to, and the
self-tests you forget are exactly the ones that then never run.

During development prefer running a milestone's module on its own
(`python analysis/model/kinematics.py`): it runs the same discovered checks
for that one module and prints its symbolic results, without rebuilding the
symbolic models of the milestones it isn't checking.
"""

import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Run order and headings come from each module's optional module-level
# MILESTONE tuple, (order, title): the int orders the run, the string titles
# it. A module without one still runs — last, titled by its own file name —
# so the cost of forgetting the constant is a worse heading, never a check
# that silently doesn't run.
DEFAULT_ORDER = float("inf")


def checks_in(module):
    """
    Every self-test defined in `module`, in the order the file defines them.

    Filtering on `__module__` keeps a self-test *imported* from an earlier
    milestone (`from kinematics import test_...`) from being counted, and
    run, a second time here.
    """
    return [obj for name, obj in vars(module).items()
            if name.startswith("test_")
            and callable(obj)
            and getattr(obj, "__module__", None) == module.__name__]


def discover_milestones():
    """
    Every milestone module in this directory, in run order, as
    `(title, module, checks)` triples.

    Skipped: this file, `test_*.py` (pytest's own files, which would import
    back into here), and anything underscore-prefixed. `params.py` and report
    scripts need no skipping — they define no `test_*`, so they aren't
    milestone modules.
    """
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))

    found = []
    for path in sorted(HERE.glob("*.py")):
        name = path.stem
        if name == Path(__file__).stem or name.startswith(("_", "test_")):
            continue
        module = importlib.import_module(name)
        checks = checks_in(module)
        if not checks:
            continue
        order, title = getattr(module, "MILESTONE", (DEFAULT_ORDER, name))
        found.append((order, title, module, checks))

    found.sort(key=lambda entry: (entry[0], entry[1]))
    return [(title, module, checks) for _order, title, module, checks in found]


def run_module(module):
    """
    Run one module's self-tests — what each milestone module's `__main__`
    block calls, so a test added to that file runs the moment it is written.
    """
    _order, title = getattr(module, "MILESTONE",
                            (DEFAULT_ORDER, module.__name__))
    checks = checks_in(module)
    assert checks, f"{title}: no test_* callables defined in this module"
    _run(title, checks)
    print(f"{title} self-tests passed.\n")


def _run(title, checks):
    print(f"=== {title} ===")
    for check in checks:
        check()


def main():
    """Run every milestone in order; the first failing check raises."""
    milestones = discover_milestones()
    assert milestones, f"no milestone modules found in {HERE}"
    for title, _module, checks in milestones:
        _run(title, checks)
        print("")
    print("All self-tests passed across all milestones.")


if __name__ == "__main__":
    main()
