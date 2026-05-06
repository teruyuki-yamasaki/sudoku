from pathlib import Path

from sudoku.config import AppConfig as Config
from sudoku.dataset import (
    PuzzleRecord,
    generate_dataset as _generate_dataset,
    generate_dataset_from_config as _generate_dataset_from_config,
    grid_to_compact_string as grid_to_string,
    run_dataset_export,
    save_records_csv as _save_records_csv,
    save_records_json as _save_records_json,
)
from sudoku.puzzle import DIFFICULTY_PROFILES as PRESETS, EASY, EXPERT, HARD, MEDIUM


def generate_dataset(n=100, difficulty=MEDIUM, seed_start=0) -> list[dict]:
    records = _generate_dataset(problem_count=n, difficulty_name=difficulty, seed_start=seed_start)
    return [record.to_dict() for record in records]


def generate_dataset_cfg(cfg: Config) -> list[dict]:
    records = _generate_dataset_from_config(cfg)
    return [record.to_dict() for record in records]


def save_json(records: list[dict] | list[PuzzleRecord], path: str | Path) -> None:
    _save_records_json(records, path)


def save_csv(records: list[dict] | list[PuzzleRecord], path: str | Path) -> None:
    _save_records_csv(records, path)


def main() -> None:
    run_dataset_export()


if __name__ == "__main__":
    main()
