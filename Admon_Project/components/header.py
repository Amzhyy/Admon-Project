from typing import Callable
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QWidget,
)


class Header(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, on_toggle_sidebar: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Toggle sidebar
        self._toggle_btn = QPushButton("☰")
        self._toggle_btn.setObjectName("SidebarToggle")
        self._toggle_btn.setFixedSize(34, 34)
        self._toggle_btn.setToolTip("Contraer / expandir panel lateral")
        self._toggle_btn.clicked.connect(on_toggle_sidebar)
        layout.addWidget(self._toggle_btn)

        # Título
        title = QLabel("Phishing Shield")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #3FE0C5; letter-spacing: 0.5px;")
        layout.addWidget(title)

        # Versión
        ver = QLabel("v3.0")
        ver.setStyleSheet("color: #3A4A56; font-size: 8pt; margin-top: 4px;")
        layout.addWidget(ver)

        layout.addStretch(1)

        # Indicador de sesión (oculto hasta login)
        self._session_dot = QLabel("●")
        self._session_dot.setStyleSheet("color: #3FE0C5; font-size: 8pt;")
        self._session_dot.setVisible(False)

        self._user_lbl = QLabel("")
        self._user_lbl.setStyleSheet("color: #7E8A94; font-size: 9.5pt;")
        self._user_lbl.setVisible(False)

        self._role_badge = QLabel("")
        self._role_badge.setStyleSheet(
            "color: #3FE0C5; font-size: 8pt; font-weight: bold; "
            "background: rgba(63,224,197,0.10); border-radius: 6px; padding: 2px 8px;"
        )
        self._role_badge.setVisible(False)

        self._logout_btn = QPushButton("Cerrar sesión")
        self._logout_btn.setStyleSheet(
            "QPushButton { background: rgba(239,68,68,0.12); color: #EF4444; border: 1px solid "
            "rgba(239,68,68,0.25); border-radius: 8px; padding: 5px 14px; font-size: 9.5pt; font-weight: 600; }"
            "QPushButton:hover { background: rgba(239,68,68,0.22); border-color: #EF4444; }"
        )
        self._logout_btn.setVisible(False)
        self._logout_btn.clicked.connect(self.logout_requested)

        layout.addWidget(self._session_dot)
        layout.addWidget(self._user_lbl)
        layout.addWidget(self._role_badge)
        layout.addSpacing(8)
        layout.addWidget(self._logout_btn)

        # Separador inferior
        self.setStyleSheet(
            "Header { border-bottom: 1px solid rgba(255,255,255,0.06); "
            "background: transparent; }"
        )

    def set_user(self, email: str, role: str) -> None:
        """Muestra la info de sesión tras el login."""
        role_labels = {
            "admin":     ("Administrador", "#3FE0C5"),
            "analyst":   ("Analista",      "#3B82F6"),
            "marketing": ("Marketing",     "#F59E0B"),
        }
        label, color = role_labels.get(role.lower(), ("Usuario", "#7E8A94"))

        self._user_lbl.setText(email)
        self._role_badge.setText(label)
        self._role_badge.setStyleSheet(
            f"color: {color}; font-size: 8pt; font-weight: bold; "
            f"background: rgba(255,255,255,0.05); border-radius: 6px; padding: 2px 8px;"
        )
        for w in [self._session_dot, self._user_lbl, self._role_badge, self._logout_btn]:
            w.setVisible(True)

    def clear_user(self) -> None:
        """Oculta la info de sesión al cerrar sesión."""
        for w in [self._session_dot, self._user_lbl, self._role_badge, self._logout_btn]:
            w.setVisible(False)
        self._user_lbl.setText("")
