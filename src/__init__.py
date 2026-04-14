from __future__ import annotations

import sys
from pathlib import Path

# Support module execution style:
#   python -m src.steel_connections.run <case.json>
# by ensuring "steel_connections" (inside this directory) is importable.
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
