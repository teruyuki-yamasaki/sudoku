from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

Grid = list[list[int]]
CellCandidate = tuple[int, int, list[int]]


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def get_candidates(grid: Grid, row_index: int, column_index: int) -> list[int]:
    if grid[row_index][column_index] != 0:
        return []

    used_values = set(grid[row_index])
    used_values |= {grid[row][column_index] for row in range(9)}

    box_row_start = (row_index // 3) * 3
    box_column_start = (column_index // 3) * 3
    used_values |= {
        grid[row][column]
        for row in range(box_row_start, box_row_start + 3)
        for column in range(box_column_start, box_column_start + 3)
    }
    return [value for value in range(1, 10) if value not in used_values]


def find_min_candidate_cell(grid: Grid) -> Optional[CellCandidate]:
    best_position: Optional[tuple[int, int]] = None
    best_candidates: Optional[list[int]] = None

    for row_index in range(9):
        for column_index in range(9):
            if grid[row_index][column_index] != 0:
                continue

            candidates = get_candidates(grid, row_index, column_index)
            if not candidates:
                return (row_index, column_index, [])
            if best_position is None or len(candidates) < len(best_candidates):
                best_position = (row_index, column_index)
                best_candidates = candidates
                if len(best_candidates) == 1:
                    return (row_index, column_index, best_candidates)

    if best_position is None:
        return None

    return (best_position[0], best_position[1], best_candidates)


@dataclass
class SolveStats:
    nodes: int = 0
    backtracks: int = 0


def solve_grid(
    grid: Grid,
    rng: random.Random,
    stats: Optional[SolveStats] = None,
) -> Optional[Grid]:
    next_cell = find_min_candidate_cell(grid)
    if next_cell is None:
        return copy_grid(grid)

    row_index, column_index, candidates = next_cell
    if not candidates:
        return None

    if stats is not None:
        stats.nodes += 1

    rng.shuffle(candidates)
    for value in candidates:
        grid[row_index][column_index] = value
        solved_grid = solve_grid(grid, rng, stats)
        if solved_grid is not None:
            grid[row_index][column_index] = 0
            return solved_grid

        if stats is not None:
            stats.backtracks += 1
        grid[row_index][column_index] = 0

    return None


def count_solutions(grid: Grid, limit: int = 2) -> int:
    solution_count = 0

    def search() -> None:
        nonlocal solution_count
        if solution_count >= limit:
            return

        next_cell = find_min_candidate_cell(grid)
        if next_cell is None:
            solution_count += 1
            return

        row_index, column_index, candidates = next_cell
        if not candidates:
            return

        for value in candidates:
            grid[row_index][column_index] = value
            search()
            grid[row_index][column_index] = 0
            if solution_count >= limit:
                return

    search()
    return solution_count


def score_grid_difficulty(grid: Grid, seed: int = 0, trials: int = 1) -> int:
    total_nodes = 0
    for trial_index in range(trials):
        rng = random.Random(seed + trial_index)
        working_grid = copy_grid(grid)
        solve_stats = SolveStats()
        solved_grid = solve_grid(working_grid, rng, solve_stats)
        if solved_grid is None:
            return 10**9
        total_nodes += solve_stats.nodes
    return total_nodes // trials


def format_grid_for_console(grid: Grid) -> str:
    lines: list[str] = []
    for row_index in range(9):
        row_values: list[str] = []
        for column_index in range(9):
            value = grid[row_index][column_index]
            row_values.append(str(value) if value else ".")
            if column_index in (2, 5):
                row_values.append("|")
        lines.append(" ".join(row_values))
        if row_index in (2, 5):
            lines.append("-" * 21)
    return "\n".join(lines)


def print_grid(grid: Grid) -> None:
    print(format_grid_for_console(grid))
