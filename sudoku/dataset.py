from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(iterable, desc=None):
        del desc
        return iterable

from .config import AppConfig
from .puzzle import DIFFICULTY_PROFILES, MEDIUM, generate_puzzle
from .solver import Grid


@dataclass(frozen=True)
class PuzzleRecord:
    puzzle_id: str
    difficulty: str
    seed: int
    score: int
    puzzle: str
    solution: str
    created_at: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "id": self.puzzle_id,
            "difficulty": self.difficulty,
            "seed": self.seed,
            "score": self.score,
            "puzzle": self.puzzle,
            "solution": self.solution,
            "created_at": self.created_at,
        }


def grid_to_compact_string(grid: Grid) -> str:
    return "".join(str(value) if value != 0 else "." for row in grid for value in row)


def _normalize_output_path(output_path: Path | str) -> Path:
    return Path(output_path)


def _normalize_rows(records: list[PuzzleRecord] | list[dict]) -> list[dict[str, str | int]]:
    if not records:
        return []
    if isinstance(records[0], PuzzleRecord):
        return [record.to_dict() for record in records]
    return records


def save_records_json(records: list[PuzzleRecord] | list[dict], output_path: Path | str) -> None:
    normalized_output_path = _normalize_output_path(output_path)
    normalized_output_path.parent.mkdir(parents=True, exist_ok=True)
    with normalized_output_path.open("w", encoding="utf-8") as file:
        json.dump(_normalize_rows(records), file, ensure_ascii=False, indent=2)


def save_records_csv(records: list[PuzzleRecord] | list[dict], output_path: Path | str) -> None:
    normalized_output_path = _normalize_output_path(output_path)
    normalized_output_path.parent.mkdir(parents=True, exist_ok=True)
    with normalized_output_path.open("w", newline="", encoding="utf-8") as file:
        rows = _normalize_rows(records)
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def generate_dataset(
    problem_count: int = 100,
    difficulty_name: str = MEDIUM,
    seed_start: int = 0,
    **legacy_kwargs,
) -> list[PuzzleRecord]:
    if "n" in legacy_kwargs:
        problem_count = legacy_kwargs["n"]
    if "difficulty" in legacy_kwargs:
        difficulty_name = legacy_kwargs["difficulty"]

    records: list[PuzzleRecord] = []
    progress_label = f"Generating {difficulty_name} problems ..."

    for problem_index in tqdm(range(problem_count), desc=progress_label):
        seed = seed_start + problem_index
        puzzle_grid, solution_grid, score = generate_puzzle(seed=seed, difficulty=difficulty_name)
        records.append(
            PuzzleRecord(
                puzzle_id=f"{difficulty_name}_{problem_index:04d}",
                difficulty=difficulty_name,
                seed=seed,
                score=score,
                puzzle=grid_to_compact_string(puzzle_grid),
                solution=grid_to_compact_string(solution_grid),
                created_at=datetime.utcnow().isoformat(),
            )
        )

    return records


def generate_dataset_from_config(config: AppConfig) -> list[PuzzleRecord]:
    return generate_dataset(
        problem_count=config.dataset_size,
        difficulty_name=config.difficulty_name,
        seed_start=config.seed_start,
    )


def run_dataset_export(config: AppConfig | None = None) -> None:
    config = config or AppConfig()
    for difficulty_name in DIFFICULTY_PROFILES:
        current_config = AppConfig(
            dataset_size=config.dataset_size,
            printout_size=config.printout_size,
            seed_start=config.seed_start,
            difficulty_name=difficulty_name,
            data_directory=config.data_directory,
            output_directory=config.output_directory,
        )
        records = generate_dataset_from_config(current_config)
        save_records_json(records, current_config.json_path)
        save_records_csv(records, current_config.csv_path)
        print(
            f"Generated {difficulty_name} problems.\n"
            f"Saved in:\n - {current_config.json_path}\n - {current_config.csv_path}"
        )
    print("Dataset export completed.")
