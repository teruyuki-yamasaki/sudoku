from pathlib import Path

from sudoku.config import AppConfig as Config
from sudoku.pdf import (
    A5,
    centered_grid_layout as layout_nxm_centered,
    draw_grid,
    draw_grid_values as draw_numbers,
    draw_title,
    load_puzzle_records as _load_puzzle_records,
    make_pdf_document as _make_pdf_document,
    maximized_grid_layout as layout_nxm_maximized,
    run_pdf_export,
    single_puzzle_layout as layout_single_page,
    two_puzzle_layout as layout_two_per_page,
)
from sudoku.puzzle import DIFFICULTY_PROFILES as PRESETS


def load_puzzles_json(path: str | Path) -> list[dict]:
    return _load_puzzle_records(path)


def load_puzzles(path: str | Path) -> list[dict]:
    return _load_puzzle_records(path)


def make_pdf(
    puzzles,
    pdf_path,
    page_size=A5,
    layout_func=lambda size: layout_nxm_centered(size, 2, 1),
    show_solution=False,
):
    return _make_pdf_document(
        puzzles,
        pdf_path=pdf_path,
        page_size=page_size,
        layout_factory=layout_func,
        show_solution=show_solution,
    )


def main() -> None:
    run_pdf_export()


if __name__ == "__main__":
    main()
