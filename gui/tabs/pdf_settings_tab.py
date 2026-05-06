from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from sudoku.pdf import PdfRenderSettings, build_layout_blocks


class PdfPreviewWidget(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(260)
        self.setFrameShape(QFrame.StyledPanel)
        self._settings = PdfRenderSettings()

    def set_settings(self, settings: PdfRenderSettings) -> None:
        self._settings = settings
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f7f3eb"))

        page_size, blocks = build_layout_blocks(self._settings)
        page_width, page_height = page_size

        content_rect = self.rect().adjusted(16, 16, -16, -16)
        scale = min(content_rect.width() / page_width, content_rect.height() / page_height)
        scaled_width = page_width * scale
        scaled_height = page_height * scale
        origin_x = content_rect.x() + (content_rect.width() - scaled_width) / 2
        origin_y = content_rect.y() + (content_rect.height() - scaled_height) / 2

        page_rect = content_rect.adjusted(
            int((content_rect.width() - scaled_width) / 2),
            int((content_rect.height() - scaled_height) / 2),
            -int((content_rect.width() - scaled_width) / 2),
            -int((content_rect.height() - scaled_height) / 2),
        )
        page_rect.setWidth(int(scaled_width))
        page_rect.setHeight(int(scaled_height))

        painter.setPen(QPen(QColor("#4a4035"), 2))
        painter.setBrush(QColor("#fffdf8"))
        painter.drawRect(page_rect)

        grid_pen = QPen(QColor("#24577a"), 1)
        title_pen = QPen(QColor("#8b3d2f"), 1)

        for block in blocks:
            grid_x = origin_x + block.grid_x * scale
            grid_y = origin_y + (page_height - (block.grid_y + block.cell_size * 9)) * scale
            grid_size = block.cell_size * 9 * scale

            if self._settings.show_title:
                painter.setPen(title_pen)
                title_height = max(6, self._settings.title_font_size * 0.7)
                painter.drawLine(
                    int(grid_x),
                    int(grid_y - title_height),
                    int(grid_x + grid_size * 0.7),
                    int(grid_y - title_height),
                )

            painter.setPen(grid_pen)
            painter.setBrush(QColor(36, 87, 122, 25))
            painter.drawRect(int(grid_x), int(grid_y), int(grid_size), int(grid_size))

        painter.end()


class PdfSettingsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.settings_file_path = self._default_settings_path()

        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A5", "A4"])
        self.page_size_combo.setCurrentText("A5")

        self.layout_mode_combo = QComboBox()
        self.layout_mode_combo.addItem("中央配置", userData="centered")
        self.layout_mode_combo.addItem("最大化配置", userData="maximized")

        self.row_count_spin = QSpinBox()
        self.row_count_spin.setRange(1, 4)
        self.row_count_spin.setValue(2)

        self.column_count_spin = QSpinBox()
        self.column_count_spin.setRange(1, 4)
        self.column_count_spin.setValue(1)

        self.gap_x_spin = QSpinBox()
        self.gap_x_spin.setRange(0, 200)
        self.gap_x_spin.setValue(40)

        self.gap_y_spin = QSpinBox()
        self.gap_y_spin.setRange(0, 200)
        self.gap_y_spin.setValue(40)

        self.margin_x_spin = QSpinBox()
        self.margin_x_spin.setRange(0, 200)
        self.margin_x_spin.setValue(40)

        self.margin_y_spin = QSpinBox()
        self.margin_y_spin.setRange(0, 200)
        self.margin_y_spin.setValue(60)

        self.show_title_checkbox = QCheckBox("タイトルを表示する")
        self.show_title_checkbox.setChecked(True)

        self.title_font_size_spin = QSpinBox()
        self.title_font_size_spin.setRange(8, 36)
        self.title_font_size_spin.setValue(14)

        self.save_settings_button = QPushButton("設定を保存")
        self.restore_settings_button = QPushButton("保存設定を復元")
        self.reset_settings_button = QPushButton("初期値に戻す")

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.preview_widget = PdfPreviewWidget()

        self._build_layout()
        self._connect_signals()
        self.load_saved_settings(show_message=False)
        self._update_summary()
        self._update_enabled_state()

    def _build_layout(self) -> None:
        layout_group = QGroupBox("ページと配置")
        layout_form = QFormLayout(layout_group)
        layout_form.addRow("ページサイズ", self.page_size_combo)
        layout_form.addRow("配置方式", self.layout_mode_combo)
        layout_form.addRow("行数", self.row_count_spin)
        layout_form.addRow("列数", self.column_count_spin)
        layout_form.addRow("横間隔", self.gap_x_spin)
        layout_form.addRow("縦間隔", self.gap_y_spin)
        layout_form.addRow("左右余白", self.margin_x_spin)
        layout_form.addRow("上下余白", self.margin_y_spin)

        title_group = QGroupBox("タイトル")
        title_form = QFormLayout(title_group)
        title_form.addRow(self.show_title_checkbox)
        title_form.addRow("フォントサイズ", self.title_font_size_spin)

        button_row = QHBoxLayout()
        button_row.addWidget(self.save_settings_button)
        button_row.addWidget(self.restore_settings_button)
        button_row.addWidget(self.reset_settings_button)
        button_row.addStretch(1)

        storage_group = QGroupBox("設定の保存")
        storage_layout = QVBoxLayout(storage_group)
        storage_layout.addLayout(button_row)
        storage_layout.addWidget(QLabel(f"保存先: {self.settings_file_path}"))

        summary_group = QGroupBox("概要")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_label)

        preview_group = QGroupBox("プレビュー")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.addWidget(self.preview_widget)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(layout_group)
        root_layout.addWidget(title_group)
        root_layout.addWidget(storage_group)
        root_layout.addWidget(summary_group)
        root_layout.addWidget(preview_group)
        root_layout.addStretch(1)

    def _connect_signals(self) -> None:
        self.page_size_combo.currentIndexChanged.connect(self._update_summary)
        self.page_size_combo.currentIndexChanged.connect(self._update_preview)
        self.layout_mode_combo.currentIndexChanged.connect(self._update_summary)
        self.layout_mode_combo.currentIndexChanged.connect(self._update_enabled_state)
        self.layout_mode_combo.currentIndexChanged.connect(self._update_preview)
        self.row_count_spin.valueChanged.connect(self._update_summary)
        self.row_count_spin.valueChanged.connect(self._update_preview)
        self.column_count_spin.valueChanged.connect(self._update_summary)
        self.column_count_spin.valueChanged.connect(self._update_preview)
        self.gap_x_spin.valueChanged.connect(self._update_summary)
        self.gap_x_spin.valueChanged.connect(self._update_preview)
        self.gap_y_spin.valueChanged.connect(self._update_summary)
        self.gap_y_spin.valueChanged.connect(self._update_preview)
        self.margin_x_spin.valueChanged.connect(self._update_summary)
        self.margin_x_spin.valueChanged.connect(self._update_preview)
        self.margin_y_spin.valueChanged.connect(self._update_summary)
        self.margin_y_spin.valueChanged.connect(self._update_preview)
        self.show_title_checkbox.checkStateChanged.connect(self._update_enabled_state)
        self.show_title_checkbox.checkStateChanged.connect(self._update_summary)
        self.show_title_checkbox.checkStateChanged.connect(self._update_preview)
        self.title_font_size_spin.valueChanged.connect(self._update_summary)
        self.title_font_size_spin.valueChanged.connect(self._update_preview)
        self.save_settings_button.clicked.connect(self.save_current_settings)
        self.restore_settings_button.clicked.connect(self.load_saved_settings)
        self.reset_settings_button.clicked.connect(self.reset_to_defaults)

    def _update_enabled_state(self) -> None:
        is_maximized = self.layout_mode_combo.currentData() == "maximized"
        self.margin_x_spin.setEnabled(is_maximized)
        self.margin_y_spin.setEnabled(is_maximized)
        self.title_font_size_spin.setEnabled(self.show_title_checkbox.isChecked())

    def _update_summary(self) -> None:
        layout_name = self.layout_mode_combo.currentText()
        total_per_page = self.row_count_spin.value() * self.column_count_spin.value()
        title_text = (
            f"タイトルあり・{self.title_font_size_spin.value()}pt"
            if self.show_title_checkbox.isChecked()
            else "タイトルなし"
        )
        summary = (
            f"{self.page_size_combo.currentText()} / {layout_name} / "
            f"1ページ {total_per_page} 問 "
            f"({self.row_count_spin.value()}行 x {self.column_count_spin.value()}列)\n"
            f"横間隔 {self.gap_x_spin.value()} / 縦間隔 {self.gap_y_spin.value()} / "
            f"左右余白 {self.margin_x_spin.value()} / 上下余白 {self.margin_y_spin.value()}\n"
            f"{title_text}"
        )
        self.summary_label.setText(summary)
        self._update_preview()

    def _update_preview(self) -> None:
        self.preview_widget.set_settings(self.build_settings())

    def build_settings(self) -> PdfRenderSettings:
        return PdfRenderSettings(
            page_size_name=self.page_size_combo.currentText(),
            layout_mode=self.layout_mode_combo.currentData(),
            row_count=self.row_count_spin.value(),
            column_count=self.column_count_spin.value(),
            gap_x=self.gap_x_spin.value(),
            gap_y=self.gap_y_spin.value(),
            margin_x=self.margin_x_spin.value(),
            margin_y=self.margin_y_spin.value(),
            show_title=self.show_title_checkbox.isChecked(),
            title_font_size=self.title_font_size_spin.value(),
        )

    def apply_settings(self, settings: PdfRenderSettings) -> None:
        self.page_size_combo.setCurrentText(settings.page_size_name)
        layout_index = self.layout_mode_combo.findData(settings.layout_mode)
        if layout_index >= 0:
            self.layout_mode_combo.setCurrentIndex(layout_index)
        self.row_count_spin.setValue(settings.row_count)
        self.column_count_spin.setValue(settings.column_count)
        self.gap_x_spin.setValue(settings.gap_x)
        self.gap_y_spin.setValue(settings.gap_y)
        self.margin_x_spin.setValue(settings.margin_x)
        self.margin_y_spin.setValue(settings.margin_y)
        self.show_title_checkbox.setChecked(settings.show_title)
        self.title_font_size_spin.setValue(settings.title_font_size)
        self._update_enabled_state()
        self._update_summary()

    def save_current_settings(self) -> None:
        self.settings_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_file_path.write_text(
            json.dumps(self.build_settings().to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        QMessageBox.information(self, "設定保存", "PDF設定を保存しました。")

    def load_saved_settings(self, show_message: bool = True) -> None:
        if not self.settings_file_path.exists():
            if show_message:
                QMessageBox.information(self, "設定復元", "保存済みのPDF設定はまだありません。")
            return

        settings_data = json.loads(self.settings_file_path.read_text(encoding="utf-8"))
        self.apply_settings(PdfRenderSettings.from_dict(settings_data))
        if show_message:
            QMessageBox.information(self, "設定復元", "保存済みのPDF設定を読み込みました。")

    def reset_to_defaults(self) -> None:
        self.apply_settings(PdfRenderSettings())

    @staticmethod
    def _default_settings_path() -> Path:
        base_dir = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        if not base_dir:
            return Path.cwd() / ".gui_settings" / "pdf_settings.json"
        return Path(base_dir) / "pdf_settings.json"

    def set_running_state(self, is_running: bool) -> None:
        self.page_size_combo.setEnabled(not is_running)
        self.layout_mode_combo.setEnabled(not is_running)
        self.row_count_spin.setEnabled(not is_running)
        self.column_count_spin.setEnabled(not is_running)
        self.gap_x_spin.setEnabled(not is_running)
        self.gap_y_spin.setEnabled(not is_running)
        self.margin_x_spin.setEnabled(not is_running and self.layout_mode_combo.currentData() == "maximized")
        self.margin_y_spin.setEnabled(not is_running and self.layout_mode_combo.currentData() == "maximized")
        self.show_title_checkbox.setEnabled(not is_running)
        self.title_font_size_spin.setEnabled(not is_running and self.show_title_checkbox.isChecked())
        self.save_settings_button.setEnabled(not is_running)
        self.restore_settings_button.setEnabled(not is_running)
        self.reset_settings_button.setEnabled(not is_running)
