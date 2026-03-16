from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class LoginScreen(QWidget):
    def __init__(self, on_register: Callable[[], None], on_recover: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # self.setProperty("class", "content-shell")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Centrar vertical y horizontalmente el panel de login
        layout.addStretch(1)

        from PyQt6.QtWidgets import QLineEdit, QHBoxLayout

        center_wrapper = QWidget()
        center_layout = QVBoxLayout(center_wrapper)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(18)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        login_card_inner = QWidget()
        login_card_inner.setObjectName("LoginCardInner")
        login_card_inner.setProperty("class", "login-card")
        login_layout = QVBoxLayout(login_card_inner)
        login_layout.setContentsMargins(32, 28, 32, 28)
        login_layout.setSpacing(6)
        login_card_inner.setMinimumWidth(380)

        login_icon = QLabel("🔐")
        login_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_icon.setFont(QFont("Segoe UI Emoji", 32))

        login_title = QLabel("Inicio de sesión")
        login_title.setObjectName("LoginTitle")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        login_subtitle = QLabel("Accede al panel de simulación de phishing.")
        login_subtitle.setObjectName("LoginSubtitle")
        login_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_subtitle.setWordWrap(True)

        user_label = QLabel("Usuario corporativo")
        pass_label = QLabel("Contraseña")

        user_input = QLineEdit()
        user_input.setPlaceholderText("usuario@empresa.com")
        user_input.setClearButtonEnabled(True)

        pass_input = QLineEdit()
        pass_input.setPlaceholderText("••••••••")
        pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Iniciar sesión")
        login_button.setObjectName("PrimaryButton")
        login_button.setProperty("class", "primary")

        links_row = QWidget()
        links_layout = QHBoxLayout(links_row)
        links_layout.setContentsMargins(0, 0, 0, 0)
        links_layout.setSpacing(12)

        register_button = QPushButton("Registrarse")
        register_button.setProperty("class", "link-button")
        register_button.clicked.connect(on_register)

        recover_button = QPushButton("Recuperar contraseña")
        recover_button.setProperty("class", "link-button")
        recover_button.clicked.connect(on_recover)

        links_layout.addWidget(register_button)
        links_layout.addWidget(recover_button)
        links_layout.addStretch(1)

        login_layout.addWidget(login_icon)
        login_layout.addWidget(login_title)
        login_layout.addWidget(login_subtitle)
        login_layout.addSpacing(20)
        login_layout.addWidget(user_label)
        login_layout.addWidget(user_input)
        login_layout.addSpacing(16)
        login_layout.addWidget(pass_label)
        login_layout.addWidget(pass_input)
        login_layout.addSpacing(28)
        login_layout.addWidget(login_button)
        login_layout.addSpacing(12)
        login_layout.addWidget(links_row, alignment=Qt.AlignmentFlag.AlignHCenter)

        description = QLabel(
            "Centraliza el acceso seguro de los analistas de seguridad para lanzar campañas "
            "de simulación de phishing, monitorear cuentas vulnerables y analizar resultados."
        )
        description.setWordWrap(True)
        description.setObjectName("SubtitleLabel")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setMaximumWidth(800)

        center_layout.addWidget(login_card_inner)
        center_layout.addSpacing(12)
        center_layout.addWidget(description)

        layout.addWidget(center_wrapper, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)

