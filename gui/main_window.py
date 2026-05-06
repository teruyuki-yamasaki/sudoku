from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
)
from PySide6.QtCore import QUrl

from gui.tabs.pdf_settings_tab import PdfSettingsTab
from gui.tabs.generation_tab import GenerationTab
from gui.tabs.log_tab import LogTab
from gui.workers import GenerationWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sudoku Generator")
        self.resize(760, 620)

        self.generation_thread: QThread | None = None
        self.generation_worker: GenerationWorker | None = None

        self.generation_tab = GenerationTab()
        self.log_tab = LogTab()
        self.pdf_settings_tab = PdfSettingsTab()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.generation_tab, "生成")
        self.tabs.addTab(self.pdf_settings_tab, "PDF設定")
        self.tabs.addTab(self.log_tab, "ログ")

        self.setCentralWidget(self.tabs)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.generation_tab.start_button.clicked.connect(self.start_generation)
        self.generation_tab.stop_button.clicked.connect(self.stop_generation)
        self.generation_tab.open_directory_button.clicked.connect(self.open_output_directory)
        self.log_tab.clear_button.clicked.connect(self.log_tab.clear_logs)
        self.log_tab.save_button.clicked.connect(self.save_logs)

    def start_generation(self) -> None:
        request = self.generation_tab.build_request(self.pdf_settings_tab.build_settings())
        if not request.base_directory:
            QMessageBox.warning(self, "入力エラー", "保存先フォルダを指定してください。")
            return

        request.base_directory.mkdir(parents=True, exist_ok=True)

        self.log_tab.save_button.setEnabled(False)
        self.generation_tab.set_progress(0)
        self.generation_tab.set_status("開始準備中")
        self.generation_tab.set_running_state(True)
        self.pdf_settings_tab.set_running_state(True)
        self.tabs.setCurrentWidget(self.generation_tab)

        self.generation_thread = QThread(self)
        self.generation_worker = GenerationWorker(request)
        self.generation_worker.moveToThread(self.generation_thread)

        self.generation_thread.started.connect(self.generation_worker.run)
        self.generation_worker.progress_changed.connect(self.generation_tab.set_progress)
        self.generation_worker.status_changed.connect(self.generation_tab.set_status)
        self.generation_worker.log_message.connect(self.log_tab.append_log)
        self.generation_worker.finished.connect(self._on_generation_finished)
        self.generation_worker.failed.connect(self._on_generation_failed)
        self.generation_worker.cancelled.connect(self._on_generation_cancelled)

        self.generation_worker.finished.connect(self.generation_thread.quit)
        self.generation_worker.failed.connect(self.generation_thread.quit)
        self.generation_worker.cancelled.connect(self.generation_thread.quit)
        self.generation_thread.finished.connect(self._cleanup_generation)
        self.generation_thread.start()

    def stop_generation(self) -> None:
        if self.generation_worker is not None:
            self.generation_worker.request_cancel()

    def open_output_directory(self) -> None:
        output_path = Path(self.generation_tab.output_directory_edit.text()).expanduser()
        output_path.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_path)))

    def save_logs(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "ログを保存",
            str(Path(self.generation_tab.output_directory_edit.text()) / "generation.log"),
            "Log Files (*.log);;Text Files (*.txt)",
        )
        if not file_path:
            return

        Path(file_path).write_text(self.log_tab.log_output.toPlainText(), encoding="utf-8")

    def _on_generation_finished(self, artifacts: dict) -> None:
        self.log_tab.save_button.setEnabled(True)
        self.tabs.setCurrentWidget(self.log_tab)
        summary_lines = [path for path in artifacts.values() if path]
        message = "生成が完了しました。"
        if summary_lines:
            message += "\n\n" + "\n".join(summary_lines)
        QMessageBox.information(self, "完了", message)

    def _on_generation_failed(self, error_message: str) -> None:
        self.log_tab.append_log(f"ERROR {error_message}")
        self.log_tab.save_button.setEnabled(True)
        self.generation_tab.set_status("エラー")
        QMessageBox.critical(self, "生成失敗", error_message)

    def _on_generation_cancelled(self) -> None:
        self.log_tab.save_button.setEnabled(True)
        QMessageBox.information(self, "停止", "生成を停止しました。")

    def _cleanup_generation(self) -> None:
        self.generation_tab.set_running_state(False)
        self.pdf_settings_tab.set_running_state(False)
        if self.generation_thread is not None:
            self.generation_thread.deleteLater()
        if self.generation_worker is not None:
            self.generation_worker.deleteLater()
        self.generation_thread = None
        self.generation_worker = None
