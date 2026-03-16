from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class Header(QWidget):
    def __init__(self, on_toggle_sidebar: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        toggle_button = QPushButton("☰")
        toggle_button.setObjectName("SidebarToggle")
        toggle_button.setFixedSize(32, 32)
        toggle_button.clicked.connect(on_toggle_sidebar)

        top_layout.addWidget(toggle_button)
        top_layout.addStretch(1)

        title = QLabel("Sistema Inteligente de Simulación de Phishing")
        title.setObjectName("TitleLabel")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        layout.addWidget(top_bar)
        layout.addWidget(title)

