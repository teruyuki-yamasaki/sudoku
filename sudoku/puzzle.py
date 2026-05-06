from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from .solver import Grid, copy_grid, count_solutions, score_grid_difficulty, solve_grid


@dataclass(frozen=True)
class DifficultyProfile:
    min_nodes: int
    max_nodes: int
    min_clues: int = 24
    removal_attempts: int = 2000
    use_rotational_symmetry: bool = True


TUTORIAL = "tutorial"
EASY = "easy"
MEDIUM = "medium"
HARD = "hard"
EXPERT = "expert"

DIFFICULTY_PROFILES: dict[str, DifficultyProfile] = {
    TUTORIAL: DifficultyProfile(min_nodes=0, max_nodes=20, min_clues=45, removal_attempts=200),
    EASY: DifficultyProfile(min_nodes=0, max_nodes=200, min_clues=34, removal_attempts=1200),
    MEDIUM: DifficultyProfile(min_nodes=200, max_nodes=800, min_clues=30, removal_attempts=1800),
    HARD: DifficultyProfile(min_nodes=800, max_nodes=3000, min_clues=26, removal_attempts=2600),
    EXPERT: DifficultyProfile(
        min_nodes=3000,
        max_nodes=12000,
        min_clues=24,
        removal_attempts=4000,
        use_rotational_symmetry=False,
    ),
}


def generate_solved_grid(seed: int = 0) -> Grid:
    rng = random.Random(seed)
    empty_grid = [[0] * 9 for _ in range(9)]
    solved_grid = solve_grid(empty_grid, rng)
    if solved_grid is None:
        raise RuntimeError("Failed to generate a full solution.")
    return solved_grid


def generate_puzzle(
    seed: int = 0,
    difficulty: str = MEDIUM,
    *,
    target_node_range: Optional[tuple[int, int]] = None,
    min_clues: Optional[int] = None,
    use_rotational_symmetry: Optional[bool] = None,
    removal_attempts: Optional[int] = None,
    score_trials: int = 1,
) -> tuple[Grid, Grid, int]:
    if difficulty not in DIFFICULTY_PROFILES and target_node_range is None:
        raise ValueError(
            f"Unknown difficulty '{difficulty}'. "
            f"Choose from {list(DIFFICULTY_PROFILES)} or pass target_node_range."
        )

    profile = DIFFICULTY_PROFILES.get(difficulty, DifficultyProfile(0, 10**9))
    target_node_range = target_node_range or (profile.min_nodes, profile.max_nodes)
    min_clues = profile.min_clues if min_clues is None else min_clues
    use_rotational_symmetry = (
        profile.use_rotational_symmetry
        if use_rotational_symmetry is None
        else use_rotational_symmetry
    )
    removal_attempts = profile.removal_attempts if removal_attempts is None else removal_attempts

    rng = random.Random(seed)
    solution_grid = generate_solved_grid(seed=seed)
    puzzle_grid = copy_grid(solution_grid)

    cell_positions = [(row_index, column_index) for row_index in range(9) for column_index in range(9)]
    rng.shuffle(cell_positions)

    best_puzzle_grid = copy_grid(puzzle_grid)
    best_score = score_grid_difficulty(best_puzzle_grid, seed=seed + 999, trials=score_trials)

    def count_clues(grid: Grid) -> int:
        return sum(1 for row in grid for value in row if value != 0)

    def distance_to_target_band(score: int, score_range: tuple[int, int]) -> int:
        lower_bound, upper_bound = score_range
        if score < lower_bound:
            return lower_bound - score
        if score > upper_bound:
            return score - upper_bound
        return 0

    for _ in range(removal_attempts):
        row_index, column_index = rng.choice(cell_positions)
        if puzzle_grid[row_index][column_index] == 0:
            continue

        paired_row_index, paired_column_index = (
            (8 - row_index, 8 - column_index)
            if use_rotational_symmetry
            else (row_index, column_index)
        )
        original_value = puzzle_grid[row_index][column_index]
        paired_original_value = puzzle_grid[paired_row_index][paired_column_index]

        puzzle_grid[row_index][column_index] = 0
        puzzle_grid[paired_row_index][paired_column_index] = 0

        if count_clues(puzzle_grid) < min_clues:
            puzzle_grid[row_index][column_index] = original_value
            puzzle_grid[paired_row_index][paired_column_index] = paired_original_value
            continue

        uniqueness_check_grid = copy_grid(puzzle_grid)
        if count_solutions(uniqueness_check_grid, limit=2) != 1:
            puzzle_grid[row_index][column_index] = original_value
            puzzle_grid[paired_row_index][paired_column_index] = paired_original_value
            continue

        score = score_grid_difficulty(puzzle_grid, seed=seed + 1234, trials=score_trials)
        if distance_to_target_band(score, target_node_range) <= distance_to_target_band(
            best_score, target_node_range
        ):
            best_puzzle_grid = copy_grid(puzzle_grid)
            best_score = score

    return best_puzzle_grid, solution_grid, best_score
