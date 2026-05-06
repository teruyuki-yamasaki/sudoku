from sudoku.puzzle import (
    DIFFICULTY_PROFILES as PRESETS,
    EASY,
    EXPERT,
    HARD,
    MEDIUM,
    TUTORIAL,
    DifficultyProfile,
    generate_puzzle,
    generate_solved_grid,
)
from sudoku.solver import (
    Grid,
    SolveStats,
    copy_grid as deep_copy,
    count_solutions,
    find_min_candidate_cell as find_mrv_cell,
    format_grid_for_console,
    get_candidates as candidates,
    print_grid,
    score_grid_difficulty as difficulty_score,
    solve_grid as solve_one,
)


def box_index(row_index: int, column_index: int) -> int:
    return (row_index // 3) * 3 + (column_index // 3)


def generate_full_solution(seed: int = 0) -> Grid:
    return generate_solved_grid(seed=seed)


def generate_puzzle(
    seed: int = 0,
    difficulty: str = MEDIUM,
    *,
    target_nodes=None,
    min_clues=None,
    symmetry=None,
    removal_attempts=None,
    score_trials: int = 1,
):
    return __import__("sudoku.puzzle", fromlist=["generate_puzzle"]).generate_puzzle(
        seed=seed,
        difficulty=difficulty,
        target_node_range=target_nodes,
        min_clues=min_clues,
        use_rotational_symmetry=symmetry,
        removal_attempts=removal_attempts,
        score_trials=score_trials,
    )


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
