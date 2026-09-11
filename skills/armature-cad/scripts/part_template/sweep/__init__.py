"""
sweep — interference checking across a motion range, for the kinematics and
planning stages.

This runs BEFORE any part exists. The point is that a self-collision is a
kinematics finding, not a CAD finding: if the forearm hits the base post at
q2 = -2.4 rad, the fix is a joint limit or a link length in `params.py`,
and the cheapest moment to learn that is while those are still just numbers
in a derivation. Learning it from a rebuilt assembly two weeks later costs
the rebuild.

So the bodies are deliberately crude — boxes and cylinders sized from the
link lengths already in `analysis/model/params.py`. An envelope that is 20%
too fat is the right fidelity: it finds the collisions that matter and costs
nothing to write. Do not model features here.

    bodies.py    the envelopes, pose(), and the pair excuses — replace these
    grid.py      the postures to sweep, and the grid's resolution
    summary.py   main(): sweep, summarize one row per pair, exit code
    report.py    prints the summary

Run it from `cad/parts/` (needs `check/` beside this package):

    uv run --with 'build123d~=0.11' --with sympy python -m sweep
    uv run --with 'build123d~=0.11' --with sympy python run_all.py sweep   # self-tests

Needs analysis/model/params.py on sys.path for the link lengths (hence
--with sympy, which params.py imports) - there is no placeholder fallback
for a link length (see bodies._resolve_lengths): a guessed one could hide a
real self-collision or invent one that isn't there.

The worked example is the planar 2R arm from the armature-derive template,
with a base post it can fold back into. Replace the bodies and pose() in
bodies.py with your mechanism; keep the shape of the package.
"""
