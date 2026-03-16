import sys

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFormLayout,
    QDateEdit,
    QDialogButtonBox,
    QLineEdit,
    QComboBox,
    QTextEdit,
)

from components.header import Header
from components.sidebar import Sidebar
from screens.about_screen import AboutScreen
from screens.login_screen import LoginScreen
from screens.phishing_screen import PhishingScreen
from screens.statistics_screen import StatisticsScreen
from screens.vulnerability_screen import VulnerabilityScreen
from styles.theme import apply_dark_theme


SECTION_TITLES = [
    "Inicio de sesión",
    "Sobre nosotros",
    "Detector de vulnerabilidades",
    "Simulador de phishing",
    "Estadísticas",
]


class DashboardWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sistema Inteligente de Simulación de Phishing")
        # Permitir que la aplicación use toda la pantalla y sea responsive
        self.resize(1400, 800)

        # Índices de páginas especiales
        self.register_page_index: int | None = None
        self.recover_page_index: int | None = None

        # Estado de colapso del panel lateral
        self._sidebar_collapsed = False
        self.sidebar: QWidget | None = None

        apply_dark_theme(self)

        container = QWidget()
        container.setObjectName("MainContainer")
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Importante: construir primero el contenido para que self.stack exista
        # antes de conectar las señales del menú lateral.
        content = self._build_content()
        self.sidebar = Sidebar(SECTION_TITLES, on_index_changed=self._on_menu_changed)

        container_layout.addWidget(self.sidebar)
        container_layout.addWidget(content, 1)

        self.setCentralWidget(container)

    def _toggle_sidebar(self) -> None:
        if not self.sidebar:
            return
        if self._sidebar_collapsed:
            self.sidebar.show()
            self.sidebar.setFixedWidth(260)
            self._sidebar_collapsed = False
        else:
            self.sidebar.setFixedWidth(0)
            self.sidebar.hide()
            self._sidebar_collapsed = True

    def _build_content(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Contenedor principal con efecto de panel "flotante"
        shell = QWidget()
        shell.setObjectName("ContentShell")
        shell.setProperty("class", "content-shell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(24, 18, 24, 24)
        shell_layout.setSpacing(16)

        header = Header(on_toggle_sidebar=self._toggle_sidebar)
        shell_layout.addWidget(header)

        self.stack = QStackedWidget()

        # Páginas principales
        login_page = LoginScreen(on_register=self._show_register_page, on_recover=self._show_recover_page)
        about_page = AboutScreen()
        vuln_page = VulnerabilityScreen()
        phishing_page = PhishingScreen(on_new_campaign=self._open_new_campaign_dialog)
        stats_page = StatisticsScreen()

        self.stack.addWidget(login_page)
        self.stack.addWidget(about_page)
        self.stack.addWidget(vuln_page)
        self.stack.addWidget(phishing_page)
        self.stack.addWidget(stats_page)

        # Páginas adicionales para registro y recuperación de contraseña
        self.register_page_index = self.stack.addWidget(self._build_register_page())
        self.recover_page_index = self.stack.addWidget(self._build_recover_page())

        shell_layout.addWidget(self.stack, 1)

        layout.addWidget(shell, 1)

        return container

    def _on_menu_changed(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

    def _show_register_page(self) -> None:
        if self.register_page_index is not None:
            self.stack.setCurrentIndex(self.register_page_index)

    def _show_recover_page(self) -> None:
        if self.recover_page_index is not None:
            self.stack.setCurrentIndex(self.recover_page_index)

    def _build_register_page(self) -> QWidget:
        page = QWidget()
        page.setProperty("class", "content-shell")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 40, 0, 40)
        wrapper_layout.setSpacing(18)
        wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("Crear nueva cuenta")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        subtitle = QLabel(
            "Registra un nuevo analista o administrador para acceder al simulador de phishing."
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setMaximumWidth(720)

        form_card = QWidget()
        form_card.setProperty("class", "login-card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(32, 28, 32, 28)
        form_layout.setSpacing(12)
        form_card.setMinimumWidth(380)

        from PyQt6.QtWidgets import QLineEdit

        name_input = QLineEdit()
        name_input.setPlaceholderText("Nombre completo")
        email_input = QLineEdit()
        email_input.setPlaceholderText("correo@empresa.com")
        role_input = QLineEdit()
        role_input.setPlaceholderText("Rol (Analista / Administrador)")

        password_input = QLineEdit()
        password_input.setPlaceholderText("Contraseña")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)

        confirm_input = QLineEdit()
        confirm_input.setPlaceholderText("Confirmar contraseña")
        confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        create_btn = QPushButton("Registrar usuario")
        create_btn.setProperty("class", "primary")

        back_btn = QPushButton("Volver a inicio de sesión")
        back_btn.setProperty("class", "link-button")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        form_layout.addWidget(name_input)
        form_layout.addWidget(email_input)
        form_layout.addWidget(role_input)
        form_layout.addWidget(password_input)
        form_layout.addWidget(confirm_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(create_btn)
        form_layout.addSpacing(8)
        form_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        wrapper_layout.addWidget(title)
        wrapper_layout.addWidget(subtitle)
        wrapper_layout.addWidget(form_card)

        layout.addWidget(wrapper)

        return page

    def _build_recover_page(self) -> QWidget:
        page = QWidget()
        page.setProperty("class", "content-shell")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 40, 0, 40)
        wrapper_layout.setSpacing(18)
        wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("Recuperar contraseña")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        subtitle = QLabel(
            "Ingresa tu correo corporativo y te enviaremos instrucciones para restablecer tu contraseña."
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setMaximumWidth(720)

        form_card = QWidget()
        form_card.setProperty("class", "login-card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(32, 28, 32, 28)
        form_layout.setSpacing(12)
        form_card.setMinimumWidth(380)

        from PyQt6.QtWidgets import QLineEdit

        email_input = QLineEdit()
        email_input.setPlaceholderText("correo@empresa.com")

        send_btn = QPushButton("Enviar enlace de recuperación")
        send_btn.setProperty("class", "primary")

        back_btn = QPushButton("Volver a inicio de sesión")
        back_btn.setProperty("class", "link-button")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        form_layout.addWidget(email_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(send_btn)
        form_layout.addSpacing(8)
        form_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        wrapper_layout.addWidget(title)
        wrapper_layout.addWidget(subtitle)
        wrapper_layout.addWidget(form_card)

        layout.addWidget(wrapper)

        return page

    def _open_new_campaign_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Campaña")
        dialog.setMinimumWidth(450)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Crear Nueva Campaña")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(16)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Ej. Suplantación de TI")

        type_input = QComboBox()
        type_input.addItems(["Credenciales", "Urgencia", "Incentivo", "Malware"])

        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate())

        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate().addDays(7))

        users_input = QTextEdit()
        users_input.setPlaceholderText("Correos de los usuarios (separados por coma)")
        users_input.setMaximumHeight(80)

        form_layout.addRow("Nombre:", name_input)
        form_layout.addRow("Tipo de ataque:", type_input)
        form_layout.addRow("Fecha de inicio:", start_date)
        form_layout.addRow("Fecha de fin (duración):", end_date)
        form_layout.addRow("Usuarios objetivo:", users_input)

        layout.addLayout(form_layout)
        layout.addSpacing(10)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Crear Campaña")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setProperty("default", True)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Lógica para agregar la campaña a la tabla iría aquí.
            pass


def main() -> None:
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

