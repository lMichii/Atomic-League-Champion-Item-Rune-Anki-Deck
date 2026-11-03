"""Portable checkout entry point, including Python safe-path environments."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lol_anki.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
