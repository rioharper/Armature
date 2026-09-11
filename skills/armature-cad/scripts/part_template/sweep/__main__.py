"""`python -m sweep`: sweep the default grid, print the summary, exit 1 on a collision."""

import sys

from sweep.summary import main

sys.exit(main())
