import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sudoku.puzzle import HARD, generate_puzzle
from sudoku.solver import print_grid


def main() -> None:
    puzzle, solution, score = generate_puzzle(
        seed=42,
        difficulty=HARD,
        score_trials=1,
        use_rotational_symmetry=True,
    )
    print("Puzzle (score nodes =", score, ")")
    print_grid(puzzle)
    print("\nSolution")
    print_grid(solution)


if __name__ == "__main__":
    main()
