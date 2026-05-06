import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sudoku.dataset import run_dataset_export


def main() -> None:
    run_dataset_export()


if __name__ == "__main__":
    main()
