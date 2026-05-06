from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget


class LogTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)

        self.clear_button = QPushButton("クリア")
        self.save_button = QPushButton("保存")
        self.save_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_output)

    def append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)

    def clear_logs(self) -> None:
        self.log_output.clear()
