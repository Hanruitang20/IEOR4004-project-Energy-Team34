"""Run the current municipal + resident-curbside Gurobi model.

Usage: python run_gurobi.py
Optional flags are passed to run_model.py; use --help for the complete list.
"""
from pathlib import Path
import sys

from run_model import main as run_model


def main() -> None:
    root = Path(__file__).resolve().parent
    args = sys.argv[1:]
    defaults = {
        "--config": root / "config" / "tract_resident_curbside_15m_cap150.json",
        "--output-dir": root / "outputs" / "current_model",
    }
    prefix = []
    for flag, value in defaults.items():
        if not any(arg == flag or arg.startswith(flag + "=") for arg in args):
            prefix.extend([flag, str(value)])
    sys.argv = [sys.argv[0], *prefix, *args]
    run_model()


if __name__ == "__main__":
    main()
