from typing import Callable

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

from database.login import validar_usuario


class LoginScreen(QWidget):
    login_success = pyqtSignal(str, str)   # email, role

    def __init__(
        self,
        on_register: Callable[[], None],
        on_recover: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addStretch(1)

        # ── Card central ──────────────────────────────────────────────
        card = QWidget()
        card.setProperty("class", "login-card")
        card.setFixedWidth(400)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(36, 32, 36, 32)
        card_lay.setSpacing(0)

        # Ícono y título
        icon = QLabel("🛡️")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 28))

        title = QLabel("Phishing Shield")
        title.setObjectName("LoginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        title.setStyleSheet("color: #E6E8EA; margin-top: 6px;")

        subtitle = QLabel("Panel de gestión de seguridad")
        subtitle.setObjectName("LoginSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #5A6A76; font-size: 10pt; margin-bottom: 26px;")

        card_lay.addWidget(icon)
        card_lay.addWidget(title)
        card_lay.addWidget(subtitle)

        # ── Email ─────────────────────────────────────────────────────
        lbl_email = QLabel("Correo corporativo")
        lbl_email.setStyleSheet("color: #7E8A94; font-size: 9.5pt; font-weight: 600; margin-bottom: 3px;")
        card_lay.addWidget(lbl_email)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("usuario@empresa.com")
        self.user_input.setClearButtonEnabled(True)
        self.user_input.returnPressed.connect(self._focus_password)
        card_lay.addWidget(self.user_input)
        card_lay.addSpacing(14)

        # ── Contraseña + mostrar/ocultar ──────────────────────────────
        lbl_pwd = QLabel("Contraseña")
        lbl_pwd.setStyleSheet("color: #7E8A94; font-size: 9.5pt; font-weight: 600; margin-bottom: 3px;")
        card_lay.addWidget(lbl_pwd)

        pwd_row = QWidget()
        pwd_row_lay = QHBoxLayout(pwd_row)
        pwd_row_lay.setContentsMargins(0, 0, 0, 0)
        pwd_row_lay.setSpacing(6)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("••••••••")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.returnPressed.connect(self._on_login)

        self._show_pwd_btn = QPushButton("👁")
        self._show_pwd_btn.setFixedSize(36, 36)
        self._show_pwd_btn.setCheckable(True)
        self._show_pwd_btn.setToolTip("Mostrar / ocultar contraseña")
        self._show_pwd_btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); "
            "border-radius: 8px; font-size: 13pt; }"
            "QPushButton:checked { background: rgba(63,224,197,0.12); border-color: rgba(63,224,197,0.4); }"
            "QPushButton:hover { background: rgba(255,255,255,0.08); }"
        )
        self._show_pwd_btn.toggled.connect(self._toggle_pwd_visibility)

        pwd_row_lay.addWidget(self.pass_input, 1)
        pwd_row_lay.addWidget(self._show_pwd_btn)
        card_lay.addWidget(pwd_row)
        card_lay.addSpacing(6)

        # ── Mensaje de error inline ───────────────────────────────────
        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet(
            "color: #EF4444; font-size: 9pt; background: rgba(239,68,68,0.08); "
            "border-radius: 6px; padding: 6px 10px;"
        )
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setVisible(False)
        card_lay.addWidget(self._error_lbl)
        card_lay.addSpacing(20)

        # ── Botón login ───────────────────────────────────────────────
        self._login_btn = QPushButton("Iniciar sesión")
        self._login_btn.setProperty("class", "primary")
        self._login_btn.setFixedHeight(42)
        self._login_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._login_btn.clicked.connect(self._on_login)
        card_lay.addWidget(self._login_btn)
        card_lay.addSpacing(16)

        # ── Links ─────────────────────────────────────────────────────
        links = QWidget()
        links_lay = QHBoxLayout(links)
        links_lay.setContentsMargins(0, 0, 0, 0)

        reg_btn = QPushButton("Crear cuenta")
        reg_btn.setProperty("class", "link-button")
        reg_btn.clicked.connect(on_register)

        rec_btn = QPushButton("Olvidé mi contraseña")
        rec_btn.setProperty("class", "link-button")
        rec_btn.clicked.connect(on_recover)

        links_lay.addWidget(reg_btn)
        links_lay.addStretch(1)
        links_lay.addWidget(rec_btn)
        card_lay.addWidget(links)

        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addSpacing(20)

        # Tagline debajo
        tagline = QLabel(
            "Centraliza campañas de simulación de phishing,\n"
            "monitoreo de exposición y análisis de riesgo."
        )
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("color: #3A4A56; font-size: 9.5pt; line-height: 1.5;")
        root.addWidget(tagline)
        root.addStretch(1)

    # ── Lógica ────────────────────────────────────────────────────────
    def _focus_password(self) -> None:
        self.pass_input.setFocus()

    def _toggle_pwd_visibility(self, visible: bool) -> None:
        mode = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.pass_input.setEchoMode(mode)

    def _show_error(self, msg: str) -> None:
        self._error_lbl.setText(f"⚠  {msg}")
        self._error_lbl.setVisible(True)
        # Auto-ocultar tras 5 s
        QTimer.singleShot(5000, lambda: self._error_lbl.setVisible(False))

    def _set_loading(self, loading: bool) -> None:
        self._login_btn.setEnabled(not loading)
        self._login_btn.setText("Verificando…" if loading else "Iniciar sesión")

    def _on_login(self) -> None:
        self._error_lbl.setVisible(False)
        email    = self.user_input.text().strip()
        password = self.pass_input.text()

        if not email:
            self._show_error("Ingresa tu correo corporativo.")
            self.user_input.setFocus()
            return
        if not password:
            self._show_error("Ingresa tu contraseña.")
            self.pass_input.setFocus()
            return

        self._set_loading(True)
        try:
            role = validar_usuario(email, password)
        except Exception as e:
            self._set_loading(False)
            self._show_error(f"Error de conexión: {e}")
            return

        self._set_loading(False)
        if role:
            self.pass_input.clear()
            self.login_success.emit(email, role)
        else:
            self._show_error("Credenciales incorrectas. Verifica tu correo y contraseña.")
            self.pass_input.selectAll()
            self.pass_input.setFocus()

    def reset(self) -> None:
        """Limpia el formulario al cerrar sesión."""
        self.user_input.clear()
        self.pass_input.clear()
        self._error_lbl.setVisible(False)
