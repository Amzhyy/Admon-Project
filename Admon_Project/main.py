import sys
import os
import traceback

# Asegurar que el directorio base y base/database estén en el PYTHONPATH
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
    QMessageBox
)

from components.header import Header
from components.sidebar import Sidebar
from screens.about_screen import AboutScreen
from screens.login_screen import LoginScreen
from screens.phishing_screen import PhishingScreen
from screens.statistics_screen import StatisticsScreen
from screens.vulnerability_screen import VulnerabilityScreen
from styles.theme import apply_dark_theme
from database.connection import conectar


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
        self.reset_password_page_index: int | None = None
        self.temp_recovery_email: str | None = None

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
        self.login_page = LoginScreen(on_register=self._show_register_page, on_recover=self._show_recover_page)
        self.login_page.login_success.connect(self._handle_login_success)
        
        about_page = AboutScreen()
        vuln_page = VulnerabilityScreen()
        self.phishing_page = PhishingScreen(on_new_campaign=self._open_new_campaign_dialog)
        stats_page = StatisticsScreen()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(about_page)
        self.stack.addWidget(vuln_page)
        self.stack.addWidget(self.phishing_page)
        self.stack.addWidget(stats_page)

        # Páginas adicionales para registro y recuperación de contraseña
        self.register_page_index = self.stack.addWidget(self._build_register_page())
        self.recover_page_index = self.stack.addWidget(self._build_recover_page())
        self.reset_password_page_index = self.stack.addWidget(self._build_reset_password_page())

        shell_layout.addWidget(self.stack, 1)

        layout.addWidget(shell, 1)

        return container

    def _handle_login_success(self, email: str, role: str) -> None:
        try:
            # Actualizar el sidebar según el rol
            if self.sidebar:
                self.sidebar.update_menu(role)
            
            # El índice de "Detector de vulnerabilidades" es 2 en SECTION_TITLES
            # En el stack, login es 0, about es 1, vuln es 2...
            self.stack.setCurrentIndex(2)
            
        except Exception as e:
            print(f"Error al procesar el inicio de sesión: {e}")
            import traceback
            traceback.print_exc()

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
        
        role_label = QLabel("Selecciona tu rol:")
        role_input = QComboBox()
        role_input.addItems(["Analista", "Administrador", "Marketing"])

        password_input = QLineEdit()
        password_input.setPlaceholderText("Contraseña")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)

        confirm_input = QLineEdit()
        confirm_input.setPlaceholderText("Confirmar contraseña")
        confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        def handle_register():
            from database.register import registrar_usuario
            name = name_input.text()
            email = email_input.text()
            role = role_input.currentText()
            pwd = password_input.text()
            conf = confirm_input.text()
            
            if not name or not email or not pwd:
                QMessageBox.warning(self, "Campos Vacíos", "Todos los campos son obligatorios.")
                return
            if pwd != conf:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
                return
            
            success, msg = registrar_usuario(name, email, role, pwd)
            if success:
                QMessageBox.information(self, "Éxito", msg)
                self.stack.setCurrentIndex(0)
            else:
                QMessageBox.critical(self, "Error", msg)

        create_btn = QPushButton("Registrar usuario")
        create_btn.setProperty("class", "primary")
        create_btn.clicked.connect(handle_register)

        back_btn = QPushButton("Volver a inicio de sesión")
        back_btn.setProperty("class", "link-button")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        form_layout.addWidget(name_input)
        form_layout.addWidget(email_input)
        form_layout.addSpacing(5)
        form_layout.addWidget(role_label)
        form_layout.addWidget(role_input)
        form_layout.addSpacing(5)
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

        def handle_recover():
            from database.restorepassword import enviar_codigo_recuperacion
            email = email_input.text()
            if not email:
                QMessageBox.warning(self, "Campo Vacío", "Por favor ingresa tu correo.")
                return
            
            success, msg = enviar_codigo_recuperacion(email)
            if success:
                self.temp_recovery_email = email
                QMessageBox.information(self, "Código Enviado", "Se ha enviado un código de seguridad a tu correo.")
                if self.reset_password_page_index is not None:
                    self.stack.setCurrentIndex(self.reset_password_page_index)
            else:
                QMessageBox.warning(self, "Error", msg)

        send_btn = QPushButton("Enviar código de recuperación")
        send_btn.setProperty("class", "primary")
        send_btn.clicked.connect(handle_recover)

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

    def _build_reset_password_page(self) -> QWidget:
        page = QWidget()
        page.setProperty("class", "content-shell")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 40, 0, 40)
        wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("Restablecer Contraseña")
        title.setObjectName("TitleLabel")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        subtitle = QLabel("Ingresa el código enviado a tu correo y tu nueva clave.")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_card = QWidget()
        form_card.setProperty("class", "login-card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(32, 28, 32, 28)
        form_layout.setSpacing(12)
        form_card.setMinimumWidth(380)

        code_input = QLineEdit()
        code_input.setPlaceholderText("Código de 6 dígitos")
        
        new_pwd = QLineEdit()
        new_pwd.setPlaceholderText("Nueva contraseña")
        new_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        conf_pwd = QLineEdit()
        conf_pwd.setPlaceholderText("Confirmar contraseña")
        conf_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        def handle_reset():
            from database.restorepassword import verificar_codigo_y_cambiar_password
            code = code_input.text()
            pwd = new_pwd.text()
            conf = conf_pwd.text()
            email = self.temp_recovery_email

            if not code or not pwd or not email:
                QMessageBox.warning(self, "Error", "Faltan datos obligatorios.")
                return
            if pwd != conf:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
                return
            
            success, msg = verificar_codigo_y_cambiar_password(email, code, pwd)
            if success:
                QMessageBox.information(self, "Éxito", msg)
                self.stack.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Error", msg)

        reset_btn = QPushButton("Cambiar Contraseña")
        reset_btn.setProperty("class", "primary")
        reset_btn.clicked.connect(handle_reset)

        form_layout.addWidget(code_input)
        form_layout.addWidget(new_pwd)
        form_layout.addWidget(conf_pwd)
        form_layout.addSpacing(20)
        form_layout.addWidget(reset_btn)

        wrapper_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        wrapper_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
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

        html_input = QTextEdit()
        html_input.setPlaceholderText("Pega el código HTML de tu plantilla aquí (Opcional)...")
        html_input.setMaximumHeight(150)

        form_layout.addRow("Nombre:", name_input)
        form_layout.addRow("Tipo de ataque:", type_input)
        form_layout.addRow("Fecha de inicio:", start_date)
        form_layout.addRow("Fecha de fin (duración):", end_date)
        form_layout.addRow("Usuarios objetivo:", users_input)
        form_layout.addRow("Plantilla HTML:", html_input)

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
            from database.campaigns import crear_campana
            
            name = name_input.text()
            attack_type = type_input.currentText()
            start = start_date.date()
            end = end_date.date()
            emails = users_input.toPlainText()
            html_template = html_input.toPlainText().strip()
            
            if not name or not emails:
                QMessageBox.warning(self, "Campos Incompletos", "El nombre de la campaña y los usuarios objetivo son obligatorios.")
                return
                
            success, result_or_error = crear_campana(
                name, attack_type, start, end, emails,
                qdate_to_str=lambda qd: qd.toString("yyyy-MM-dd"),
                html_template=html_template if html_template else None
            )
            
            if success:
                QMessageBox.information(self, "Éxito", f"Campaña '{name}' creada exitosamente.\nSe enviaron simulaciones a {result_or_error} usuario(s) válido(s).")
                if hasattr(self, 'phishing_page'):
                    self.phishing_page.load_campaigns()
            else:
                QMessageBox.critical(self, "Error de Sistema", f"No se pudo crear la campaña:\n{result_or_error}")

def main() -> None:
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

