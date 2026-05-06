from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sudoku.config import AppConfig
from sudoku.pdf import PdfRenderSettings


@dataclass(frozen=True)
class GenerationRequest:
    base_directory: Path
    difficulty_name: str
    seed_start: int
    dataset_size: int
    printout_size: int
    export_json_csv: bool
    export_problem_pdf: bool
    export_answer_pdf: bool
    pdf_render_settings: PdfRenderSettings

    @property
    def data_directory(self) -> Path:
        return self.base_directory / "data"

    @property
    def output_directory(self) -> Path:
        return self.base_directory / "output"

    def to_app_config(self) -> AppConfig:
        return AppConfig(
            dataset_size=self.dataset_size,
            printout_size=min(self.printout_size, self.dataset_size),
            seed_start=self.seed_start,
            difficulty_name=self.difficulty_name,
            data_directory=self.data_directory,
            output_directory=self.output_directory,
        )
