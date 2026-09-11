# Executable build recipes (build123d)

Optional companion to a part definition. The `.md` stays the part
definition — the contract, the loads, the rationale. These files make its
**Build recipe** section runnable, so the checks in **Done when** are
things a machine confirms.

What that buys, in order of value:

1. **The inertia loop closes before anyone opens CAD.** Realized mass, COM,
   and inertia against the values `analysis/model/params.py` assumed —
   cross-platform, at sketch grade, no SolidWorks needed.
2. **The recipe self-validates.** A wall that goes negative under a fillet,
   a feature that fails to build, a driven dimension the recipe can't
   survive — found in a second. `rebuild_sweep` catches builds that
   *fail*, not builds that are silently *wrong*; geometry that must stay
   inside other geometry needs `contained()` (its docstring says what it
   catches and how to probe; `part.py` shows the pattern).
3. **Real projected views** for the definition's *At a glance* section,
   from the actual geometry, so they can't drift from the recipe.
   Front/top/right export true 1:1; the iso is orientation only.
4. **Interference sweeps at the kinematics/planning stage**, before parts
   exist, when a self-collision is still a joint limit rather than a
   rebuild. The sweep is a finite grid: it can only be guaranteed to catch
   a collision band wider than its step, and the first interfering sample
   can sit up to one step past the true onset, so a joint limit read off
   it goes at least one step inside. `joint_limits_and_interior`'s
   docstring says how to size the grid; `sweep_clearance`'s says which
   pairs an `ignore` threshold fits and what each kind of excuse hides.

## Files

| File | Role |
|---|---|
| `check/` | Library package. Mass properties in SI, target comparison, parameter-rebuild sweeps, interference, SVG views, one submodule each. **Holds the unit contract — read `check/__init__.py`'s docstring first.** |
| `part.py` | Template for `cad/parts/<PART-ID>.py`. Worked example: the plate-with-a-boss from SKILL.md. Copy and edit. |
| `sweep/` | Template for a planning-stage interference sweep. Worked example: planar 2R arm folding into its base housing. Replace the bodies and `pose()` in `sweep/bodies.py`. |
| `stubs.py` | COTS placeholders for when armature-librarian can't find a vendor STEP. Enforces datasheet provenance; its release gate `still_placeholder()` only sees stubs *this process built* — read its docstring before gating on it. |
| `run_all.py`, `layout.py` | The runner and the code-line budget, the same files armature-derive's model template ships. |

The files follow the plugin's `references/model-layout.md`: each module's
self-tests live one file over in its `*_checks.py` (`part.py` →
`part_checks.py`, copied as `<PART-ID>_checks.py`; `check/mass.py` →
`check/mass_checks.py`), and no module passes 250 code lines. One command
runs every self-test and the budget; the other two run the things
themselves:

```bash
uv run --with 'build123d~=0.11' --with sympy python run_all.py        # every self-test, then the budget
uv run --with 'build123d~=0.11' --with sympy python run_all.py check  # one module or package's self-tests
uv run --with 'build123d~=0.11' --with sympy python part.py           # mass props vs target + SVG views
uv run --with 'build123d~=0.11' --with sympy python -m sweep          # the sweep
python layout.py                                                      # the size table, stdlib only
```

**The exit code is the contract: nonzero means a check failed**, which is
what makes these usable in a pre-commit hook or CI. `sweep/`'s worked 2R
arm genuinely folds into its own base post, so `python -m sweep` prints the
colliding pairs and **exits 1 by design** until the swept range excludes the
collision. `run_all.py`, `part.py`, and `layout.py` exit 0.

`part.py` and `sweep/` both need `--with sympy`, since both import
`analysis/model/params.py`, which imports it. Both locate that file
*relative to their own path* — `../../analysis/model/` from `cad/parts/` —
so keep them two directories below the project root. `part.py`'s mass
target falls back to a budget row when there is no derivation yet, and says
so in its printed provenance line; the sweep's link lengths have no fallback
(a guessed link length hides a real self-collision or invents one), so
running it — its self-tests included — needs `params.py` present: copy it
in, or run the armature-derive milestone that produces it, first. Importing
the package alone never needs it.

## Prerequisite

build123d, which pulls Open Cascade (~hundreds of MB). It is **not** a
plugin dependency. `uv run --with` fetches it on demand and caches it, same
pattern as the SolidWorks MCP server.

**Written and tested against build123d 0.11.1.** The version bound is
deliberate: this code depends on API details that have moved before —
`matrix_of_inertia` is about the COM in mm⁵ (volumetric, density = 1),
`center_of_mass` does not exist (it is `center(CenterOf.MASS)`), and
`intersect` returns `None` rather than an empty result for disjoint shapes.
Before relaxing the bound, re-run `run_all.py`; its self-tests fail loudly
if any of those change.

To install into a project properly:

```bash
uv add 'build123d~=0.11'      # or: pip install 'build123d~=0.11'
```

## The two rules

**Units.** build123d is millimetre-native; `params.py` is SI. `mm()` in
`check/` is the only place a factor of 1000 may appear, and everything
`check/` returns is SI, because the comparison happens in the derivation's
units. The full contract is `check/__init__.py`'s docstring.

**One source of truth.** The `.py` never restates a dimension that lives in
`params.py` or an interface table — it imports them. A `.md` and a `.py`
that disagree about a bolt circle are worse than having no `.py` at all.

## Where this stops

Not a replacement for the CAD package. No assemblies or mates, no
toleranced drawings, no GD&T, no title blocks, no FEA. Release-grade
drawings and the manufacturing deliverable come out of SOLIDWORKS, Fusion,
or Onshape. This is the check that runs before you get there, and the
picture that goes in the definition.
