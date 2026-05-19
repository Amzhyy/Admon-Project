from typing import Callable, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget,
)


class Sidebar(QWidget):
    def __init__(
        self,
        section_titles: Sequence[str],
        on_index_changed: Callable[[int], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.section_titles   = list(section_titles)
        self.on_index_changed = on_index_changed
        self._current_role    = "guest"
        self.real_indices: list[int] = []

        self.setObjectName("SidebarWidget")
        self.setFixedWidth(260)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        logo_icon  = QLabel("🛡️")
        logo_icon.setFont(QFont("Segoe UI Emoji", 20))
        logo_label = QLabel("Phishing Shield")
        logo_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch(1)
        main_layout.addLayout(logo_layout)

        subtitle = QLabel("Panel de ciberseguridad")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        main_layout.addWidget(subtitle)

        # Badge de rol activo
        self.role_badge = QLabel("Sin sesión")
        self.role_badge.setStyleSheet(
            "color: #AAB4BE; font-size: 9pt; padding: 2px 8px; "
            "background: rgba(255,255,255,0.05); border-radius: 8px;"
        )
        main_layout.addWidget(self.role_badge)
        main_layout.addSpacing(6)

        self.menu_list = QListWidget()
        self.menu_list.setSpacing(4)
        self.menu_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.menu_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.update_menu(initial=True)

        if on_index_changed is not None:
            self.menu_list.currentRowChanged.connect(self._handle_row_changed)

        main_layout.addWidget(self.menu_list, 1)

        footer = QLabel("© 2026 Equipo de Seguridad")
        footer.setObjectName("SubtitleLabel")
        footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        main_layout.addWidget(footer)

    def update_menu(self, role: str = "guest", initial: bool = False) -> None:
        """
        Actualiza el menu lateral segun el rol del usuario.

        Roles:
          guest    → Solo: Inicio de sesion, Sobre nosotros
          admin    → Todo excepto Inicio de sesion
          analyst  → Sobre nosotros, Detector de vulnerabilidades
          marketing→ Solo Detector de vulnerabilidades
        """
        self._current_role = role
        self.menu_list.clear()
        self.real_indices = []

        role_normalized = role.strip().lower()

        # Etiqueta de rol en el badge
        role_labels = {
            "admin":     ("Administrador", "#3FE0C5"),
            "analyst":   ("Analista",      "#3B82F6"),
            "marketing": ("Marketing",     "#F59E0B"),
            "guest":     ("Sin sesion",    "#AAB4BE"),
        }
        label_text, label_color = role_labels.get(role_normalized, ("Desconocido", "#AAB4BE"))
        self.role_badge.setText(f"Rol: {label_text}")
        self.role_badge.setStyleSheet(
            f"color: {label_color}; font-size: 9pt; font-weight: bold; padding: 2px 8px; "
            f"background: rgba(255,255,255,0.05); border-radius: 8px;"
        )

        # Indices visibles por rol
        visible_indices: set[int] = set()

        if role_normalized == "admin":
            # Admin ve todo menos la pantalla de login
            visible_indices = {1, 2, 3, 4}
        elif role_normalized == "analyst":
            visible_indices = {1, 2}
        elif role_normalized == "marketing":
            visible_indices = {2}
        else:  # guest
            visible_indices = {0, 1}

        # Al inicio (antes de login) siempre mostrar login
        if initial:
            visible_indices = {0, 1}

        for i, title in enumerate(self.section_titles):
            if i in visible_indices:
                self.menu_list.addItem(QListWidgetItem(title))
                self.real_indices.append(i)

        if not initial:
            self.menu_list.setCurrentRow(0)

    def _handle_row_changed(self, row: int) -> None:
        if 0 <= row < len(self.real_indices):
            real_index = self.real_indices[row]
            if self.on_index_changed:
                self.on_index_changed(real_index)
