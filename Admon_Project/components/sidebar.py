from typing import Callable, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QWidget


class Sidebar(QWidget):
    def __init__(self, section_titles: Sequence[str], on_index_changed: Callable[[int], None] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("SidebarWidget")
        self.setFixedWidth(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        logo_icon = QLabel("🛡️")
        logo_icon.setFont(QFont("Segoe UI Emoji", 20))
        logo_label = QLabel("Phishing Shield")
        logo_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch(1)

        layout.addLayout(logo_layout)

        subtitle = QLabel("Panel de ciberseguridad")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        self.menu_list = QListWidget()
        self.menu_list.setSpacing(4)
        # Desactivar la barra horizontal que aparece en la parte inferior
        self.menu_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Evitar el borde de foco interno (nos quedamos solo con el borde exterior blanco)
        self.menu_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for title in section_titles:
            item = QListWidgetItem(title)
            self.menu_list.addItem(item)

        if on_index_changed is not None:
            self.menu_list.currentRowChanged.connect(on_index_changed)

        self.menu_list.setCurrentRow(0)

        layout.addWidget(self.menu_list, 1)

        footer = QLabel("© 2026 Equipo de Seguridad")
        footer.setObjectName("SubtitleLabel")
        footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(footer)

