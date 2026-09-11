"""
check/views_checks.py — self-tests for views.py.
"""

import math
import re
import tempfile
from pathlib import Path

from build123d import Box, Location

from check.views import write_views


def test_principal_views_are_one_to_one():
    # The PRINCIPAL views (front/top/right) are 1:1, so a shared dimension
    # measures the same in each — not the iso, which foreshortens, which is
    # why the set below is two principal views. Rescaling each view by its
    # own extent draws this part's 80 mm width as 100.09 mm and its one
    # 16 mm height as two different numbers. Off-origin on purpose: that is
    # what tilts a camera aimed by direction alone, and a tilted view is
    # not 1:1 either.
    tall = Box(80, 75, 16).locate(Location((0, 0, 8)))
    with tempfile.TemporaryDirectory() as tmp:
        size = {}
        for path in write_views(tall, str(Path(tmp) / "v"), views=("front", "right")):
            # The DECLARED size, not the viewBox: the viewBox stays in model
            # units whatever `scale` is, so it is exactly the number that
            # cannot catch this bug.
            wh = re.search(r'width="([\d.]+)mm"\s+height="([\d.]+)mm"', Path(path).read_text())
            size[Path(path).stem.split("-")[-1]] = tuple(float(v) for v in wh.groups())
    pad = 0.09  # ExportSVG fit_to_stroke pads the box by one line weight
    assert math.isclose(size["front"][0], 80 + pad, abs_tol=0.01), size
    assert math.isclose(size["right"][0], 75 + pad, abs_tol=0.01), size
    # The SAME 16 mm dimension, measured off two different views.
    assert math.isclose(size["front"][1], size["right"][1], abs_tol=1e-6), size
    assert math.isclose(size["front"][1], 16 + pad, abs_tol=0.01), size
    print("  [PASS] principal views true 1:1, one scale across the set")
