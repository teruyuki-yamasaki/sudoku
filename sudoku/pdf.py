from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

try:
    from reportlab.lib.pagesizes import A5
    from reportlab.pdfgen import canvas as reportlab_canvas
except ModuleNotFoundError:
    A5 = (420, 595)
    reportlab_canvas = None

from .config import AppConfig
from .puzzle import DIFFICULTY_PROFILES

DEFAULT_CELL_SIZE = 28
GRID_SIZE = DEFAULT_CELL_SIZE * 9
DEFAULT_MARGIN_X = 40
DEFAULT_MARGIN_Y = 60
TITLE_OFFSET_Y = 10


@dataclass(frozen=True)
class LayoutBlock:
    grid_x: float
    grid_y: float
    title_x: float
    title_y: float
    cell_size: int = DEFAULT_CELL_SIZE


@dataclass(frozen=True)
class PdfRenderSettings:
    page_size_name: str = "A5"
    layout_mode: str = "centered"
    row_count: int = 2
    column_count: int = 1
    gap_x: int = 40
    gap_y: int = 40
    margin_x: int = DEFAULT_MARGIN_X
    margin_y: int = DEFAULT_MARGIN_Y
    show_title: bool = True
    title_font_size: int = 14

    def to_dict(self) -> dict[str, int | str | bool]:
        return {
            "page_size_name": self.page_size_name,
            "layout_mode": self.layout_mode,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "gap_x": self.gap_x,
            "gap_y": self.gap_y,
            "margin_x": self.margin_x,
            "margin_y": self.margin_y,
            "show_title": self.show_title,
            "title_font_size": self.title_font_size,
        }

    @classmethod
    def from_dict(cls, values: dict) -> "PdfRenderSettings":
        return cls(
            page_size_name=values.get("page_size_name", "A5"),
            layout_mode=values.get("layout_mode", "centered"),
            row_count=int(values.get("row_count", 2)),
            column_count=int(values.get("column_count", 1)),
            gap_x=int(values.get("gap_x", 40)),
            gap_y=int(values.get("gap_y", 40)),
            margin_x=int(values.get("margin_x", DEFAULT_MARGIN_X)),
            margin_y=int(values.get("margin_y", DEFAULT_MARGIN_Y)),
            show_title=bool(values.get("show_title", True)),
            title_font_size=int(values.get("title_font_size", 14)),
        )


def draw_grid(pdf_canvas, x: float, y: float, cell_size: int = DEFAULT_CELL_SIZE, base_width: int = 1) -> None:
    grid_size = cell_size * 9
    for line_index in range(10):
        line_width = base_width * 2 if line_index % 3 == 0 else base_width
        pdf_canvas.setLineWidth(line_width)
        pdf_canvas.line(x, y + line_index * cell_size, x + grid_size, y + line_index * cell_size)
        pdf_canvas.line(x + line_index * cell_size, y, x + line_index * cell_size, y + grid_size)


def draw_grid_values(
    pdf_canvas,
    grid_string: str,
    x: float,
    y: float,
    cell_size: int = DEFAULT_CELL_SIZE,
    font_name: str = "Helvetica",
    font_size: int = 16,
) -> None:
    pdf_canvas.setFont(font_name, font_size)
    for index, character in enumerate(grid_string):
        if character == ".":
            continue
        row_index = 8 - index // 9
        column_index = index % 9
        pdf_canvas.drawCentredString(
            x + column_index * cell_size + cell_size / 2,
            y + row_index * cell_size + cell_size / 2 - 4,
            character,
        )


def draw_title(pdf_canvas, text: str, x: float, y: float, font_name: str = "Helvetica-Bold", font_size: int = 14) -> None:
    pdf_canvas.setFont(font_name, font_size)
    pdf_canvas.drawString(x, y, text)


def resolve_page_size(page_size_name: str):
    page_sizes = {
        "A5": A5,
    }
    try:
        from reportlab.lib.pagesizes import A4

        page_sizes["A4"] = A4
    except ModuleNotFoundError:
        page_sizes["A4"] = (595, 842)
    return page_sizes[page_size_name]


def build_layout_factory(render_settings: PdfRenderSettings) -> Callable:
    if render_settings.layout_mode == "centered":
        return lambda size: centered_grid_layout(
            size,
            render_settings.row_count,
            render_settings.column_count,
            gap_x=render_settings.gap_x,
            gap_y=render_settings.gap_y,
        )
    if render_settings.layout_mode == "maximized":
        return lambda size: maximized_grid_layout(
            size,
            render_settings.row_count,
            render_settings.column_count,
            margin_x=render_settings.margin_x,
            margin_y=render_settings.margin_y,
            gap_x=render_settings.gap_x,
            gap_y=render_settings.gap_y,
        )
    raise ValueError(f"Unknown layout mode: {render_settings.layout_mode}")


def build_layout_blocks(render_settings: PdfRenderSettings) -> tuple[tuple[float, float], list[LayoutBlock]]:
    page_size = resolve_page_size(render_settings.page_size_name)
    layout_factory = build_layout_factory(render_settings)
    return page_size, layout_factory(page_size)


def single_puzzle_layout(page_size) -> list[LayoutBlock]:
    x = DEFAULT_MARGIN_X
    y = page_size[1] - GRID_SIZE - DEFAULT_MARGIN_Y
    return [LayoutBlock(grid_x=x, grid_y=y, title_x=x, title_y=y + GRID_SIZE + TITLE_OFFSET_Y)]


def two_puzzle_layout(page_size) -> list[LayoutBlock]:
    page_width, page_height = page_size
    del page_width
    top_y = page_height - GRID_SIZE - DEFAULT_MARGIN_Y
    bottom_y = top_y - GRID_SIZE - 40
    return [
        LayoutBlock(
            grid_x=DEFAULT_MARGIN_X,
            grid_y=top_y,
            title_x=DEFAULT_MARGIN_X,
            title_y=top_y + GRID_SIZE + TITLE_OFFSET_Y,
        ),
        LayoutBlock(
            grid_x=DEFAULT_MARGIN_X,
            grid_y=bottom_y,
            title_x=DEFAULT_MARGIN_X,
            title_y=bottom_y + GRID_SIZE + TITLE_OFFSET_Y,
        ),
    ]


def centered_grid_layout(page_size, row_count: int, column_count: int, gap_x: int = 40, gap_y: int = 40) -> list[LayoutBlock]:
    page_width, page_height = page_size
    total_width = column_count * GRID_SIZE + (column_count - 1) * gap_x
    total_height = row_count * GRID_SIZE + (row_count - 1) * gap_y

    if total_width > page_width or total_height > page_height:
        raise ValueError("Layout exceeds page size.")

    start_x = (page_width - total_width) / 2
    start_y = (page_height + total_height) / 2 - GRID_SIZE
    blocks: list[LayoutBlock] = []

    for row_index in range(row_count):
        for column_index in range(column_count):
            x = start_x + column_index * (GRID_SIZE + gap_x)
            y = start_y - row_index * (GRID_SIZE + gap_y)
            blocks.append(LayoutBlock(grid_x=x, grid_y=y, title_x=x, title_y=y + GRID_SIZE + TITLE_OFFSET_Y))

    return blocks


def maximized_grid_layout(
    page_size,
    row_count: int,
    column_count: int,
    margin_x: int = 40,
    margin_y: int = 60,
    gap_x: int = 20,
    gap_y: int = 40,
) -> list[LayoutBlock]:
    page_width, page_height = page_size
    usable_width = page_width - 2 * margin_x - (column_count - 1) * gap_x
    usable_height = page_height - 2 * margin_y - (row_count - 1) * gap_y - TITLE_OFFSET_Y

    cell_size = int(min(usable_width / column_count, usable_height / row_count) / 9)
    grid_size = cell_size * 9
    total_width = column_count * grid_size + (column_count - 1) * gap_x
    total_height = row_count * grid_size + (row_count - 1) * gap_y

    start_x = (page_width - total_width) / 2
    start_y = (page_height + total_height) / 2 - grid_size
    blocks: list[LayoutBlock] = []

    for row_index in range(row_count):
        for column_index in range(column_count):
            x = start_x + column_index * (grid_size + gap_x)
            y = start_y - row_index * (grid_size + gap_y)
            blocks.append(LayoutBlock(grid_x=x, grid_y=y, title_x=x, title_y=y + grid_size + TITLE_OFFSET_Y, cell_size=cell_size))

    return blocks


def load_puzzle_records(json_path: Path | str) -> list[dict]:
    normalized_json_path = Path(json_path)
    with normalized_json_path.open(encoding="utf-8") as file:
        return json.load(file)


def make_pdf_document(
    puzzles: list[dict],
    pdf_path: Path | str,
    page_size=A5,
    layout_factory: Callable = lambda size: centered_grid_layout(size, 2, 1),
    show_solution: bool = False,
    render_settings: PdfRenderSettings | None = None,
) -> None:
    if reportlab_canvas is None:
        raise ModuleNotFoundError("reportlab is required to generate PDF files.")

    if render_settings is not None:
        page_size = resolve_page_size(render_settings.page_size_name)
        layout_factory = build_layout_factory(render_settings)

    normalized_pdf_path = Path(pdf_path)
    normalized_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_canvas = reportlab_canvas.Canvas(str(normalized_pdf_path), pagesize=page_size)
    layout_blocks = layout_factory(page_size)
    problem_number = 1
    puzzle_index = 0

    while puzzle_index < len(puzzles):
        for block in layout_blocks:
            if puzzle_index >= len(puzzles):
                break

            puzzle_record = puzzles[puzzle_index]
            title = f"No.{problem_number}  Level: {puzzle_record['difficulty']}"
            if render_settings is None or render_settings.show_title:
                draw_title(
                    pdf_canvas,
                    title,
                    block.title_x,
                    block.title_y,
                    font_size=14 if render_settings is None else render_settings.title_font_size,
                )
            draw_grid(pdf_canvas, block.grid_x, block.grid_y, cell_size=block.cell_size)

            grid_string = puzzle_record["solution"] if show_solution else puzzle_record["puzzle"]
            draw_grid_values(pdf_canvas, grid_string, block.grid_x, block.grid_y, cell_size=block.cell_size)

            puzzle_index += 1
            problem_number += 1

        pdf_canvas.showPage()

    pdf_canvas.save()


def run_pdf_export(config: AppConfig | None = None) -> None:
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
        puzzles = load_puzzle_records(current_config.json_path)[: current_config.printout_size]
        make_pdf_document(puzzles, pdf_path=current_config.problems_pdf_path, show_solution=False)
        make_pdf_document(puzzles, pdf_path=current_config.answers_pdf_path, show_solution=True)
        print(f"Generated problem and answer PDFs for {difficulty_name}.")
