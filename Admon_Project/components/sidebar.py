from typing import Callable, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QWidget


class Sidebar(QWidget):
    def __init__(self, section_titles: Sequence[str], on_index_changed: Callable[[int], None] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.section_titles = section_titles
        self.on_index_changed = on_index_changed
        self.setObjectName("SidebarWidget")
        self.setFixedWidth(260)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(16)

        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        logo_icon = QLabel("🛡️")
        logo_icon.setFont(QFont("Segoe UI Emoji", 20))
        logo_label = QLabel("Phishing Shield")
        logo_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch(1)

        self.layout.addLayout(logo_layout)

        subtitle = QLabel("Panel de ciberseguridad")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        self.layout.addWidget(subtitle)

        self.layout.addSpacing(10)

        self.menu_list = QListWidget()
        self.menu_list.setSpacing(4)
        self.menu_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.menu_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.update_menu(initial=True)

        if on_index_changed is not None:
            self.menu_list.currentRowChanged.connect(self._handle_row_changed)

        self.layout.addWidget(self.menu_list, 1)

        footer = QLabel("© 2026 Equipo de Seguridad")
        footer.setObjectName("SubtitleLabel")
        footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(footer)

        # Mapeo de índices reales
        self.real_indices = list(range(len(section_titles)))

    def update_menu(self, role: str = "guest", initial: bool = False) -> None:
        self.menu_list.clear()
        self.real_indices = []

        for i, title in enumerate(self.section_titles):
            # Lógica de filtrado
            if role == "admin":
                # Admin ve todo excepto "Inicio de sesión" después de entrar
                if i == 0 and not initial: continue
                self.menu_list.addItem(QListWidgetItem(title))
                self.real_indices.append(i)
            elif role == "guest":
                # Solo ve Inicio de sesión y Sobre nosotros
                if i in [0, 1]:
                    self.menu_list.addItem(QListWidgetItem(title))
                    self.real_indices.append(i)
            elif role == "analyst":
                # Analista ve Sobre nosotros y Detector de vulnerabilidades, oculta phishing(3) y stats(4)
                if i in [1, 2]:
                    self.menu_list.addItem(QListWidgetItem(title))
                    self.real_indices.append(i)
            else:
                # Otros roles (marketing, etc.)
                if i == 2:
                    self.menu_list.addItem(QListWidgetItem(title))
                    self.real_indices.append(i)
        
        if not initial:
            # Seleccionar por defecto la primera opción disponible
            self.menu_list.setCurrentRow(0)

    def _handle_row_changed(self, row: int) -> None:
        if 0 <= row < len(self.real_indices):
            real_index = self.real_indices[row]
            if self.on_index_changed:
                self.on_index_changed(real_index)

