"""Main application entry point."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from cli.generate import main

if __name__ == "__main__":
    main()
