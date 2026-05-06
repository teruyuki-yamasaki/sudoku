from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .puzzle import MEDIUM


@dataclass
class AppConfig:
    dataset_size: int = 60
    printout_size: int = 60
    seed_start: int = 1000
    difficulty_name: str = MEDIUM
    data_directory: Path = Path("./data")
    output_directory: Path = Path("./output")

    @property
    def base_filename(self) -> str:
        return f"{self.difficulty_name}_seed{int(self.seed_start)}"

    @property
    def json_path(self) -> Path:
        return self.data_directory / f"{self.base_filename}.json"

    @property
    def csv_path(self) -> Path:
        return self.data_directory / f"{self.base_filename}.csv"

    @property
    def problems_pdf_path(self) -> Path:
        return self.output_directory / f"{self.base_filename}_problems.pdf"

    @property
    def answers_pdf_path(self) -> Path:
        return self.output_directory / f"{self.base_filename}_answers.pdf"

    @property
    def basename(self) -> str:
        return self.base_filename

    @property
    def data_dir(self) -> str:
        return str(self.data_directory)

    @property
    def output_dir(self) -> str:
        return str(self.output_directory)

    @property
    def problems_pdf(self) -> str:
        return str(self.problems_pdf_path)

    @property
    def answers_pdf(self) -> str:
        return str(self.answers_pdf_path)

    @property
    def diff(self) -> str:
        return self.difficulty_name

    @diff.setter
    def diff(self, value: str) -> None:
        self.difficulty_name = value

    @property
    def n_problems_generate(self) -> int:
        return self.dataset_size

    @n_problems_generate.setter
    def n_problems_generate(self, value: int) -> None:
        self.dataset_size = value

    @property
    def n_problems_printout(self) -> int:
        return self.printout_size

    @n_problems_printout.setter
    def n_problems_printout(self, value: int) -> None:
        self.printout_size = value
