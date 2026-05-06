from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from gui.models import GenerationRequest
from sudoku.dataset import PuzzleRecord, grid_to_compact_string, save_records_csv, save_records_json
from sudoku.pdf import make_pdf_document
from sudoku.puzzle import generate_puzzle


class GenerationWorker(QObject):
    progress_changed = Signal(int)
    status_changed = Signal(str)
    log_message = Signal(str)
    finished = Signal(dict)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, request: GenerationRequest) -> None:
        super().__init__()
        self.request = request
        self._cancel_requested = False
        self._cancel_emitted = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def _emit_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_message.emit(f"{timestamp} {message}")

    def _check_cancelled(self) -> bool:
        if self._cancel_requested:
            if not self._cancel_emitted:
                self.status_changed.emit("キャンセルされました")
                self._emit_log("Generation cancelled.")
                self.cancelled.emit()
                self._cancel_emitted = True
            return True
        return False

    @Slot()
    def run(self) -> None:
        try:
            if not any(
                [
                    self.request.export_json_csv,
                    self.request.export_problem_pdf,
                    self.request.export_answer_pdf,
                ]
            ):
                raise ValueError("少なくとも1つは出力オプションを有効にしてください。")

            app_config = self.request.to_app_config()
            records = self._generate_records(app_config.dataset_size)
            if self._check_cancelled():
                return

            artifacts = {
                "json": None,
                "csv": None,
                "problem_pdf": None,
                "answer_pdf": None,
            }

            if self.request.export_json_csv:
                self.status_changed.emit("JSON / CSV を保存しています")
                self.progress_changed.emit(70)
                self._emit_log("Saving dataset files...")
                save_records_json(records, app_config.json_path)
                save_records_csv(records, app_config.csv_path)
                artifacts["json"] = str(app_config.json_path)
                artifacts["csv"] = str(app_config.csv_path)
                self._emit_log(f"Saved JSON: {app_config.json_path}")
                self._emit_log(f"Saved CSV: {app_config.csv_path}")

            if self._check_cancelled():
                return

            puzzle_rows = [record.to_dict() for record in records[: app_config.printout_size]]

            if self.request.export_problem_pdf:
                self.status_changed.emit("問題PDFを生成しています")
                self.progress_changed.emit(85)
                self._emit_log("Rendering problem PDF...")
                make_pdf_document(puzzle_rows, app_config.problems_pdf_path, show_solution=False)
                artifacts["problem_pdf"] = str(app_config.problems_pdf_path)
                self._emit_log(f"Saved problem PDF: {app_config.problems_pdf_path}")

            if self._check_cancelled():
                return

            if self.request.export_answer_pdf:
                self.status_changed.emit("解答PDFを生成しています")
                self.progress_changed.emit(95)
                self._emit_log("Rendering answer PDF...")
                make_pdf_document(puzzle_rows, app_config.answers_pdf_path, show_solution=True)
                artifacts["answer_pdf"] = str(app_config.answers_pdf_path)
                self._emit_log(f"Saved answer PDF: {app_config.answers_pdf_path}")

            self.progress_changed.emit(100)
            self.status_changed.emit("完了")
            self._emit_log("Generation completed successfully.")
            self.finished.emit(artifacts)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _generate_records(self, problem_count: int) -> list[PuzzleRecord]:
        self.status_changed.emit("問題を生成しています")
        self.progress_changed.emit(0)
        self._emit_log(
            f"Start generation: difficulty={self.request.difficulty_name}, "
            f"seed_start={self.request.seed_start}, count={problem_count}"
        )

        records: list[PuzzleRecord] = []
        for problem_index in range(problem_count):
            if self._check_cancelled():
                return records

            seed = self.request.seed_start + problem_index
            puzzle_grid, solution_grid, score = generate_puzzle(
                seed=seed,
                difficulty=self.request.difficulty_name,
            )
            records.append(
                PuzzleRecord(
                    puzzle_id=f"{self.request.difficulty_name}_{problem_index:04d}",
                    difficulty=self.request.difficulty_name,
                    seed=seed,
                    score=score,
                    puzzle=grid_to_compact_string(puzzle_grid),
                    solution=grid_to_compact_string(solution_grid),
                    created_at=datetime.utcnow().isoformat(),
                )
            )

            progress = int(((problem_index + 1) / problem_count) * 60)
            self.progress_changed.emit(progress)
            if problem_index == 0 or (problem_index + 1) == problem_count or (problem_index + 1) % 10 == 0:
                self._emit_log(f"Generated {problem_index + 1} / {problem_count}")

        return records
