"""PyInstaller entry point for SpaceLoom desktop.

PyInstaller runs the target script as ``__main__``, so relative imports fail.
This wrapper imports the real package and launches the desktop window.
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from src.main import run_desktop

if __name__ == "__main__":
    run_desktop()
