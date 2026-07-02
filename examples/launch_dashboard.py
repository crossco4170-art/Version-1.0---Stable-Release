from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_project_path() -> None:
    """Ensure the project root is importable when running this script directly."""
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def main() -> None:
    """Launch the desktop recruiting dashboard example."""
    _bootstrap_project_path()
    from desktop.recruiting_dashboard import run_dashboard

    run_dashboard()


if __name__ == "__main__":
    main()
