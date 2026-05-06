from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.models import GenerationRequest
from sudoku.puzzle import DIFFICULTY_PROFILES, MEDIUM


class GenerationTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.output_directory_edit = QLineEdit(str(Path.cwd()))
        self.browse_button = QPushButton("参照...")

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(DIFFICULTY_PROFILES.keys())
        self.difficulty_combo.setCurrentText(MEDIUM)

        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 10**9)
        self.seed_spin.setValue(1000)

        self.dataset_size_spin = QSpinBox()
        self.dataset_size_spin.setRange(1, 1000)
        self.dataset_size_spin.setValue(60)

        self.printout_size_spin = QSpinBox()
        self.printout_size_spin.setRange(1, 1000)
        self.printout_size_spin.setValue(60)

        self.export_dataset_checkbox = QCheckBox("JSON / CSV を生成")
        self.export_dataset_checkbox.setChecked(True)

        self.export_problem_pdf_checkbox = QCheckBox("問題PDFを生成")
        self.export_problem_pdf_checkbox.setChecked(True)

        self.export_answer_pdf_checkbox = QCheckBox("解答PDFを生成")
        self.export_answer_pdf_checkbox.setChecked(True)

        self.start_button = QPushButton("生成開始")
        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        self.open_directory_button = QPushButton("出力先を開く")

        self.status_label = QLabel("待機中")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self._build_layout()
        self._connect_signals()

    def _build_layout(self) -> None:
        directory_row = QHBoxLayout()
        directory_row.addWidget(self.output_directory_edit, stretch=1)
        directory_row.addWidget(self.browse_button)

        directory_group = QGroupBox("保存先")
        directory_layout = QVBoxLayout(directory_group)
        directory_layout.addLayout(directory_row)

        settings_group = QGroupBox("基本設定")
        settings_form = QFormLayout(settings_group)
        settings_form.addRow("難易度", self.difficulty_combo)
        settings_form.addRow("シード開始値", self.seed_spin)
        settings_form.addRow("生成件数", self.dataset_size_spin)
        settings_form.addRow("PDF出力件数", self.printout_size_spin)

        output_group = QGroupBox("出力オプション")
        output_layout = QVBoxLayout(output_group)
        output_layout.addWidget(self.export_dataset_checkbox)
        output_layout.addWidget(self.export_problem_pdf_checkbox)
        output_layout.addWidget(self.export_answer_pdf_checkbox)

        action_row = QHBoxLayout()
        action_row.addWidget(self.start_button)
        action_row.addWidget(self.stop_button)
        action_row.addWidget(self.open_directory_button)
        action_row.addStretch(1)

        action_group = QGroupBox("実行")
        action_layout = QVBoxLayout(action_group)
        action_layout.addLayout(action_row)

        progress_group = QGroupBox("進捗")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(directory_group)
        root_layout.addWidget(settings_group)
        root_layout.addWidget(output_group)
        root_layout.addWidget(action_group)
        root_layout.addWidget(progress_group)
        root_layout.addStretch(1)

    def _connect_signals(self) -> None:
        self.browse_button.clicked.connect(self.select_output_directory)
        self.dataset_size_spin.valueChanged.connect(self._sync_printout_limit)

    def select_output_directory(self) -> None:
        selected_directory = QFileDialog.getExistingDirectory(
            self,
            "保存先フォルダを選択",
            self.output_directory_edit.text(),
        )
        if selected_directory:
            self.output_directory_edit.setText(selected_directory)

    def _sync_printout_limit(self, dataset_size: int) -> None:
        self.printout_size_spin.setMaximum(dataset_size)
        if self.printout_size_spin.value() > dataset_size:
            self.printout_size_spin.setValue(dataset_size)

    def build_request(self) -> GenerationRequest:
        return GenerationRequest(
            base_directory=Path(self.output_directory_edit.text()).expanduser(),
            difficulty_name=self.difficulty_combo.currentText(),
            seed_start=self.seed_spin.value(),
            dataset_size=self.dataset_size_spin.value(),
            printout_size=self.printout_size_spin.value(),
            export_json_csv=self.export_dataset_checkbox.isChecked(),
            export_problem_pdf=self.export_problem_pdf_checkbox.isChecked(),
            export_answer_pdf=self.export_answer_pdf_checkbox.isChecked(),
        )

    def set_running_state(self, is_running: bool) -> None:
        self.output_directory_edit.setEnabled(not is_running)
        self.browse_button.setEnabled(not is_running)
        self.difficulty_combo.setEnabled(not is_running)
        self.seed_spin.setEnabled(not is_running)
        self.dataset_size_spin.setEnabled(not is_running)
        self.printout_size_spin.setEnabled(not is_running)
        self.export_dataset_checkbox.setEnabled(not is_running)
        self.export_problem_pdf_checkbox.setEnabled(not is_running)
        self.export_answer_pdf_checkbox.setEnabled(not is_running)
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)

    def set_status(self, message: str) -> None:
        self.status_label.setText(message)

    def set_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)
