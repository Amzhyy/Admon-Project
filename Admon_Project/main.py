import sys
import os
import traceback

# El directorio base es Admon_Project/. El proyecto raíz (donde vive `database/`
# y `modelo_phishing.pkl`) es el padre. Agregamos ambos a sys.path.
base_dir     = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDateEdit, QDialog,
    QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QSplashScreen,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget,
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
    "Detector OSINT",
    "Simulador de Phishing",
    "Estadísticas",
]

IDX_LOGIN = 0
IDX_ABOUT = 1
IDX_VULN  = 2
IDX_PHISH = 3
IDX_STATS = 4


class DashboardWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Phishing Shield — Sistema de Simulación y Análisis")
        self.resize(1440, 860)
        self.setMinimumSize(1100, 650)

        self._current_email: str = ""
        self._current_role:  str = ""
        self._recovery_email: str = ""
        self._sidebar_collapsed = False

        apply_dark_theme(self)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("MainContainer")
        rl = QHBoxLayout(root)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        content = self._build_content()
        self.sidebar = Sidebar(SECTION_TITLES, on_index_changed=self._on_menu_changed)
        rl.addWidget(self.sidebar)
        rl.addWidget(content, 1)
        self.setCentralWidget(root)

    def _build_content(self) -> QWidget:
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(20, 16, 20, 20)
        lay.setSpacing(14)

        self.header = Header(on_toggle_sidebar=self._toggle_sidebar)
        self.header.logout_requested.connect(self._handle_logout)
        lay.addWidget(self.header)

        self.stack = QStackedWidget()

        self.login_page    = LoginScreen(on_register=self._show_register, on_recover=self._show_recover)
        self.about_page    = AboutScreen()
        self.vuln_page     = VulnerabilityScreen()
        self.phishing_page = PhishingScreen(on_new_campaign=self._open_campaign_dialog)
        self.stats_page    = StatisticsScreen()

        self.login_page.login_success.connect(self._handle_login_success)

        for page in [self.login_page, self.about_page, self.vuln_page,
                     self.phishing_page, self.stats_page]:
            self.stack.addWidget(page)

        self._reg_idx   = self.stack.addWidget(self._build_register_page())
        self._rec_idx   = self.stack.addWidget(self._build_recover_page())
        self._reset_idx = self.stack.addWidget(self._build_reset_page())

        lay.addWidget(self.stack, 1)
        return container

    # ── Sesión ────────────────────────────────────────────────────────────────
    def _handle_login_success(self, email: str, role: str) -> None:
        self._current_email = email
        self._current_role  = role
        self.header.set_user(email, role)
        self.sidebar.update_menu(role)
        self.stack.setCurrentIndex(IDX_ABOUT)

    def _handle_logout(self) -> None:
        if QMessageBox.question(
            self, "Cerrar sesión", "¿Deseas cerrar la sesión actual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        self._current_email = ""
        self._current_role  = ""
        self.header.clear_user()
        self.sidebar.update_menu("guest")
        self.login_page.reset()
        self.stack.setCurrentIndex(IDX_LOGIN)

    # ── Navegación ────────────────────────────────────────────────────────────
    def _on_menu_changed(self, index: int) -> None:
        if not self._current_role and index not in (IDX_LOGIN, IDX_ABOUT):
            self.stack.setCurrentIndex(IDX_LOGIN)
            return
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            if index == IDX_PHISH:
                self.phishing_page.load_campaigns()
            elif index == IDX_STATS:
                try:
                    self.stats_page.load_data()
                except Exception:
                    pass

    def _toggle_sidebar(self) -> None:
        if self._sidebar_collapsed:
            self.sidebar.setFixedWidth(260)
            self.sidebar.show()
        else:
            self.sidebar.setFixedWidth(0)
            self.sidebar.hide()
        self._sidebar_collapsed = not self._sidebar_collapsed

    def _show_register(self) -> None:
        self.stack.setCurrentIndex(self._reg_idx)

    def _show_recover(self) -> None:
        self.stack.setCurrentIndex(self._rec_idx)

    # ── Registro ──────────────────────────────────────────────────────────────
    def _build_register_page(self) -> QWidget:
        page, wrapper = self._aux_page_skeleton(
            "Crear nueva cuenta",
            "Registra un analista, administrador o usuario de marketing."
        )
        card = self._form_card(460)
        fl = QVBoxLayout(card)
        fl.setContentsMargins(36, 28, 36, 28)
        fl.setSpacing(0)

        name_in  = self._input("Nombre completo")
        email_in = self._input("correo@empresa.com")
        pwd_in   = self._input("Contraseña (mín. 8 caracteres)", password=True)
        conf_in  = self._input("Confirmar contraseña", password=True)

        # Tab navigation entre campos
        name_in.returnPressed.connect(email_in.setFocus)
        email_in.returnPressed.connect(pwd_in.setFocus)
        pwd_in.returnPressed.connect(conf_in.setFocus)

        role_lbl = self._field_label("Rol")
        role_combo = QComboBox()
        role_combo.addItems(["Analista", "Administrador", "Marketing"])
        role_combo.setStyleSheet(
            "QComboBox { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); "
            "border-radius: 8px; padding: 8px 12px; font-size: 10.5pt; }"
            "QComboBox::drop-down { border: none; width: 28px; }"
            "QComboBox QAbstractItemView { background: #1F2226; border: 1px solid rgba(255,255,255,0.12); }"
        )

        strength_bar = QWidget()
        strength_bar.setFixedHeight(3)
        strength_bar.setStyleSheet("border-radius: 2px; background: #1E293B;")
        strength_lbl = QLabel("")
        strength_lbl.setStyleSheet("font-size: 8.5pt; color: #475569;")

        def update_strength(text: str) -> None:
            score = sum([
                len(text) >= 8,
                any(c.isupper() for c in text),
                any(c.isdigit() for c in text),
                any(c in "!@#$%^&*()-_=+[]{}|;':\",./<>?" for c in text),
            ])
            colors = ["#1E293B", "#EF4444", "#F59E0B", "#3B82F6", "#10B981"]
            labels = ["", "Débil", "Regular", "Buena", "Fuerte ✓"]
            pct    = [0, 25, 50, 75, 100]
            strength_bar.setStyleSheet(
                f"border-radius: 2px; "
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {colors[score]}, stop:{pct[score]/100:.2f} {colors[score]}, "
                f"stop:{min(pct[score]/100+0.01, 1):.2f} #1E293B, stop:1 #1E293B);"
            )
            strength_lbl.setText(labels[score])
            strength_lbl.setStyleSheet(f"font-size: 8.5pt; color: {colors[score]};")

        pwd_in.textChanged.connect(update_strength)

        err_lbl = self._error_label()
        ok_btn  = self._primary_btn("Registrar usuario")
        ok_btn.setEnabled(False)

        def validate_fields(*_):
            ok_btn.setEnabled(
                bool(name_in.text().strip())
                and bool(email_in.text().strip())
                and len(pwd_in.text()) >= 8
                and pwd_in.text() == conf_in.text()
            )

        for w in [name_in, email_in, pwd_in, conf_in]:
            w.textChanged.connect(validate_fields)

        def do_register() -> None:
            from database.register import registrar_usuario
            name  = name_in.text().strip()
            email = email_in.text().strip()
            role  = role_combo.currentText()
            pwd   = pwd_in.text()
            conf  = conf_in.text()
            if pwd != conf:
                self._show_inline_error(err_lbl, "Las contraseñas no coinciden.")
                return
            ok_btn.setEnabled(False)
            ok_btn.setText("Registrando…")
            ok, msg = registrar_usuario(name, email, role, pwd)
            ok_btn.setEnabled(True)
            ok_btn.setText("Registrar usuario")
            if ok:
                QMessageBox.information(
                    self, "Usuario registrado",
                    f"La cuenta de {name} fue creada exitosamente.\nRol asignado: {role}."
                )
                for f in [name_in, email_in, pwd_in, conf_in]:
                    f.clear()
                self.stack.setCurrentIndex(IDX_LOGIN)
            else:
                self._show_inline_error(err_lbl, msg)

        ok_btn.clicked.connect(do_register)
        conf_in.returnPressed.connect(do_register)

        back = self._link_btn("← Volver al inicio de sesión")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(IDX_LOGIN))

        # Construir el formulario ordenadamente
        fields = [
            ("Nombre completo", name_in),
            ("Correo corporativo", email_in),
        ]
        for label_text, widget in fields:
            fl.addWidget(self._field_label(label_text))
            fl.addWidget(widget)
            fl.addSpacing(12)

        fl.addWidget(role_lbl)
        fl.addWidget(role_combo)
        fl.addSpacing(12)

        fl.addWidget(self._field_label("Contraseña"))
        fl.addWidget(pwd_in)
        fl.addSpacing(4)
        fl.addWidget(strength_bar)
        fl.addSpacing(2)
        fl.addWidget(strength_lbl)
        fl.addSpacing(10)

        fl.addWidget(self._field_label("Confirmar contraseña"))
        fl.addWidget(conf_in)
        fl.addSpacing(10)

        fl.addWidget(err_lbl)
        fl.addSpacing(14)
        fl.addWidget(ok_btn)
        fl.addSpacing(10)
        fl.addWidget(back, alignment=Qt.AlignmentFlag.AlignHCenter)

        wrapper.addWidget(card)
        return page

    # ── Recuperación ──────────────────────────────────────────────────────────
    def _build_recover_page(self) -> QWidget:
        page, wrapper = self._aux_page_skeleton(
            "Recuperar contraseña",
            "Ingresa tu correo y recibirás un código de 6 dígitos (válido 15 min)."
        )
        card = self._form_card(420)
        fl = QVBoxLayout(card)
        fl.setContentsMargins(36, 28, 36, 28)
        fl.setSpacing(0)

        email_in = self._input("correo@empresa.com")
        err_lbl  = self._error_label()
        ok_btn   = self._primary_btn("Enviar código de seguridad")

        def do_send() -> None:
            from database.restorepassword import enviar_codigo_recuperacion
            email = email_in.text().strip()
            if not email:
                self._show_inline_error(err_lbl, "Ingresa tu dirección de correo.")
                return
            ok_btn.setEnabled(False)
            ok_btn.setText("Enviando…")
            ok, msg = enviar_codigo_recuperacion(email)
            ok_btn.setEnabled(True)
            ok_btn.setText("Enviar código de seguridad")
            if ok:
                self._recovery_email = email
                QMessageBox.information(
                    self, "Código enviado",
                    f"Se envió un código a:\n{email}\n\nExpira en 15 minutos."
                )
                self.stack.setCurrentIndex(self._reset_idx)
            else:
                self._show_inline_error(err_lbl, msg)

        ok_btn.clicked.connect(do_send)
        email_in.returnPressed.connect(do_send)
        back = self._link_btn("← Volver al inicio de sesión")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(IDX_LOGIN))

        fl.addWidget(self._field_label("Correo corporativo"))
        fl.addWidget(email_in)
        fl.addSpacing(10)
        fl.addWidget(err_lbl)
        fl.addSpacing(14)
        fl.addWidget(ok_btn)
        fl.addSpacing(10)
        fl.addWidget(back, alignment=Qt.AlignmentFlag.AlignHCenter)

        wrapper.addWidget(card)
        return page

    # ── Reset contraseña ──────────────────────────────────────────────────────
    def _build_reset_page(self) -> QWidget:
        page, wrapper = self._aux_page_skeleton(
            "Nueva contraseña",
            "Ingresa el código recibido y elige una nueva contraseña."
        )
        card = self._form_card(420)
        fl = QVBoxLayout(card)
        fl.setContentsMargins(36, 28, 36, 28)
        fl.setSpacing(0)

        code_in = self._input("Código de 6 dígitos")
        code_in.setMaxLength(6)
        pwd_in  = self._input("Nueva contraseña", password=True)
        conf_in = self._input("Confirmar nueva contraseña", password=True)

        # Tab navigation
        code_in.returnPressed.connect(pwd_in.setFocus)
        pwd_in.returnPressed.connect(conf_in.setFocus)

        err_lbl = self._error_label()
        ok_btn  = self._primary_btn("Cambiar contraseña")

        def do_reset() -> None:
            from database.restorepassword import verificar_codigo_y_cambiar_password
            code = code_in.text().strip()
            pwd  = pwd_in.text()
            conf = conf_in.text()
            if not code or not pwd:
                self._show_inline_error(err_lbl, "Completa todos los campos.")
                return
            if pwd != conf:
                self._show_inline_error(err_lbl, "Las contraseñas no coinciden.")
                return
            if len(pwd) < 8:
                self._show_inline_error(err_lbl, "La contraseña debe tener al menos 8 caracteres.")
                return
            ok_btn.setEnabled(False)
            ok_btn.setText("Cambiando…")
            ok, msg = verificar_codigo_y_cambiar_password(self._recovery_email, code, pwd)
            ok_btn.setEnabled(True)
            ok_btn.setText("Cambiar contraseña")
            if ok:
                QMessageBox.information(
                    self, "Contraseña actualizada",
                    "Tu contraseña fue cambiada exitosamente.\nInicia sesión con la nueva clave."
                )
                for f in [code_in, pwd_in, conf_in]:
                    f.clear()
                self.stack.setCurrentIndex(IDX_LOGIN)
            else:
                self._show_inline_error(err_lbl, msg)

        ok_btn.clicked.connect(do_reset)
        conf_in.returnPressed.connect(do_reset)

        back = self._link_btn("← Pedir un nuevo código")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(self._rec_idx))

        for label_text, widget in [
            ("Código de verificación", code_in),
            ("Nueva contraseña", pwd_in),
            ("Confirmar contraseña", conf_in),
        ]:
            fl.addWidget(self._field_label(label_text))
            fl.addWidget(widget)
            fl.addSpacing(12)

        fl.addWidget(err_lbl)
        fl.addSpacing(14)
        fl.addWidget(ok_btn)
        fl.addSpacing(10)
        fl.addWidget(back, alignment=Qt.AlignmentFlag.AlignHCenter)

        wrapper.addWidget(card)
        return page

    # ── Diálogo de nueva campaña ───────────────────────────────────────────────
    def _open_campaign_dialog(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Nueva Campaña de Simulación")
        dlg.setMinimumWidth(520)
        dlg.setStyleSheet("QDialog { background: #18191e; }")

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        hdr = QLabel("Nueva Campaña")
        hdr.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lay.addWidget(hdr)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.06);")
        lay.addWidget(sep)

        # ── Campos ────────────────────────────────────────────────────────────
        def row(label_text: str, widget: QWidget) -> None:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #7E8A94; font-size: 9.5pt; font-weight: 600;")
            lay.addWidget(lbl)
            lay.addWidget(widget)

        name_in = QLineEdit()
        name_in.setPlaceholderText("Ej. Suplantación TI — Q2 2025")
        row("Nombre de la campaña", name_in)

        type_combo = QComboBox()
        type_combo.addItems(["Credenciales", "Urgencia", "Incentivo", "Malware"])
        row("Tipo de ataque", type_combo)

        date_row = QWidget()
        date_lay = QHBoxLayout(date_row)
        date_lay.setContentsMargins(0, 0, 0, 0)
        date_lay.setSpacing(12)

        start_dt = QDateEdit(QDate.currentDate())
        start_dt.setCalendarPopup(True)
        start_dt.setMinimumDate(QDate.currentDate())
        start_dt.setDisplayFormat("dd/MM/yyyy")

        end_dt = QDateEdit(QDate.currentDate().addDays(7))
        end_dt.setCalendarPopup(True)
        end_dt.setDisplayFormat("dd/MM/yyyy")

        def update_end_min(d: QDate) -> None:
            end_dt.setMinimumDate(d.addDays(1))
            if end_dt.date() <= d:
                end_dt.setDate(d.addDays(1))

        start_dt.dateChanged.connect(update_end_min)

        for label_text, widget in [("Inicio", start_dt), ("Fin", end_dt)]:
            grp = QVBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #7E8A94; font-size: 9pt; font-weight: 600;")
            grp.addWidget(lbl)
            grp.addWidget(widget)
            date_lay.addLayout(grp)

        lay.addWidget(date_row)

        users_in = QTextEdit()
        users_in.setPlaceholderText(
            "Correos separados por coma:\nana@empresa.com, carlos@empresa.com, …"
        )
        users_in.setFixedHeight(72)
        row("Usuarios objetivo (correos)", users_in)

        # ── Selector de plantilla HTML (auto-detecta archivos en email_templates/) ──
        from database.template_loader import list_templates, get_templates_folder

        templates_folder = get_templates_folder()

        # Etiqueta con la ruta de la carpeta (siempre visible)
        templates_label = QLabel("Plantilla HTML")
        templates_label.setStyleSheet("color: #7E8A94; font-size: 9.5pt; font-weight: 600;")
        lay.addWidget(templates_label)

        # Fila: combo + botón recargar
        template_row = QWidget()
        tr_lay = QHBoxLayout(template_row)
        tr_lay.setContentsMargins(0, 0, 0, 0)
        tr_lay.setSpacing(8)

        template_combo = QComboBox()
        reload_tpl_btn = QPushButton("↺")
        reload_tpl_btn.setFixedSize(32, 32)
        reload_tpl_btn.setToolTip("Recargar plantillas desde la carpeta")
        reload_tpl_btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.04); color: #94A3B8; "
            "border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; font-size: 13pt; }"
            "QPushButton:hover { background: rgba(63,224,197,0.10); color: #3FE0C5; "
            "border-color: rgba(63,224,197,0.25); }"
        )

        tr_lay.addWidget(template_combo, 1)
        tr_lay.addWidget(reload_tpl_btn)
        lay.addWidget(template_row)

        # Nota informativa con la ruta de la carpeta
        folder_hint = QLabel(
            f"Las plantillas se leen automáticamente de: <code>{templates_folder}</code>"
        )
        folder_hint.setStyleSheet(
            "color: #475569; font-size: 8pt; font-family: 'Segoe UI'; "
            "padding: 4px 0 2px 0;"
        )
        folder_hint.setWordWrap(True)
        folder_hint.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(folder_hint)

        # Preview pequeña que muestra los primeros caracteres de la plantilla seleccionada
        preview_lbl = QLabel("")
        preview_lbl.setStyleSheet(
            "color: #5A6A76; font-size: 8.5pt; font-style: italic; "
            "background: rgba(255,255,255,0.02); border-radius: 6px; padding: 8px 10px;"
        )
        preview_lbl.setWordWrap(True)
        preview_lbl.setVisible(False)
        lay.addWidget(preview_lbl)

        def _on_template_changed(idx: int) -> None:
            tpl = template_combo.itemData(idx)
            if tpl is None:
                preview_lbl.setVisible(False)
                return
            preview = tpl.content[:180].replace("<", "‹").replace(">", "›")
            preview_lbl.setText(f"Vista previa: {preview}…")
            preview_lbl.setVisible(True)

        template_combo.currentIndexChanged.connect(_on_template_changed)

        def _reload_templates() -> None:
            """Re-escanea la carpeta y actualiza el combo sin cerrar el diálogo."""
            template_combo.blockSignals(True)
            template_combo.clear()
            template_combo.addItem("Sin plantilla (correo simple en texto plano)", userData=None)
            tpls_now = list_templates()
            for tpl in tpls_now:
                template_combo.addItem(f"  {tpl.name}  ·  {tpl.size_kb} KB", userData=tpl)
            template_combo.setToolTip(
                f"{len(tpls_now)} plantilla(s) detectada(s) en:\n{templates_folder}"
                if tpls_now else
                f"No se encontraron plantillas HTML en:\n{templates_folder}\n"
                "Agrega archivos .html en esa carpeta para que aparezcan aquí."
            )
            template_combo.blockSignals(False)
            if tpls_now:
                template_combo.setCurrentIndex(1)
            else:
                template_combo.setCurrentIndex(0)

        reload_tpl_btn.clicked.connect(_reload_templates)
        _reload_templates()   # Carga inicial

        # ── Error inline ──────────────────────────────────────────────────────
        dlg_err = QLabel("")
        dlg_err.setStyleSheet(
            "color: #EF4444; font-size: 9pt; background: rgba(239,68,68,0.08); "
            "border-radius: 6px; padding: 6px 10px;"
        )
        dlg_err.setVisible(False)
        dlg_err.setWordWrap(True)
        lay.addWidget(dlg_err)

        # ── Botones ───────────────────────────────────────────────────────────
        btn_row_w = QWidget()
        btn_row_l = QHBoxLayout(btn_row_w)
        btn_row_l.setContentsMargins(0, 0, 0, 0)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #64748B; border: 1px solid #1E293B; "
            "border-radius: 8px; padding: 8px 20px; font-size: 10pt; }"
            "QPushButton:hover { border-color: #334155; color: #94A3B8; }"
        )
        cancel_btn.clicked.connect(dlg.reject)

        create_btn = QPushButton("Crear campaña")
        create_btn.setProperty("class", "purple-button")
        create_btn.setMinimumWidth(140)

        btn_row_l.addStretch(1)
        btn_row_l.addWidget(cancel_btn)
        btn_row_l.addWidget(create_btn)
        lay.addWidget(btn_row_w)

        def do_create() -> None:
            name   = name_in.text().strip()
            emails = users_in.toPlainText().strip()

            if not name:
                dlg_err.setText("⚠  El nombre de la campaña es obligatorio.")
                dlg_err.setVisible(True)
                return
            if not emails:
                dlg_err.setText("⚠  Agrega al menos un correo objetivo.")
                dlg_err.setVisible(True)
                return
            if end_dt.date() <= start_dt.date():
                dlg_err.setText("⚠  La fecha de fin debe ser posterior a la de inicio.")
                dlg_err.setVisible(True)
                return

            # Estado de carga
            create_btn.setEnabled(False)
            create_btn.setText("Creando…")
            cancel_btn.setEnabled(False)
            dlg_err.setVisible(False)
            QApplication.processEvents()

            # ── Ejecutar en background para no congelar la UI ──────────────
            from PyQt6.QtCore import QThread, pyqtSignal
            from PyQt6.QtWidgets import QProgressDialog
            from database.campaigns import crear_campana

            tpl_data = template_combo.currentData()
            tpl_html = tpl_data.content if tpl_data is not None else None

            class _CampaignWorker(QThread):
                progress = pyqtSignal(str, int, int)
                done     = pyqtSignal(bool, object)

                def run(self):
                    try:
                        ok, result = crear_campana(
                            name,
                            type_combo.currentText(),
                            start_dt.date(),
                            end_dt.date(),
                            emails,
                            qdate_to_str=lambda d: d.toString("yyyy-MM-dd"),
                            html_template=tpl_html,
                            progress_cb=lambda msg, v, t: self.progress.emit(msg, v, t),
                        )
                        self.done.emit(ok, result)
                    except Exception as ex:
                        self.done.emit(False, str(ex))

            worker = _CampaignWorker(self)

            # Diálogo de progreso modal con cancelación visual
            prog = QProgressDialog("Iniciando campaña…", "Cancelar", 0, 100, self)
            prog.setWindowTitle("Creando campaña")
            prog.setWindowModality(Qt.WindowModality.WindowModal)
            prog.setMinimumDuration(0)
            prog.setAutoClose(False)
            prog.setAutoReset(False)
            prog.setValue(0)
            prog.show()

            def _on_progress(msg: str, value: int, total: int):
                if total > 0:
                    prog.setMaximum(total)
                prog.setValue(value)
                prog.setLabelText(msg)

            def _on_done(ok: bool, result):
                prog.close()
                create_btn.setEnabled(True)
                create_btn.setText("Crear campaña")
                cancel_btn.setEnabled(True)
                if ok:
                    dlg.accept()
                    QMessageBox.information(
                        self, "Campaña creada",
                        f"«{name}» creada exitosamente.\n"
                        f"Correos de simulación enviados: {result} usuario(s)."
                    )
                    self.phishing_page.load_campaigns()
                else:
                    dlg_err.setText(f"⚠  {result}")
                    dlg_err.setVisible(True)

            worker.progress.connect(_on_progress)
            worker.done.connect(_on_done)
            # Si el usuario cancela el diálogo, terminamos el worker.
            # Nota: crear_campana no es interrumpible a mitad-de-loop, pero al
            # menos el hilo se descarta tras la operación corriente.
            prog.canceled.connect(lambda: worker.requestInterruption())
            worker.start()

        create_btn.clicked.connect(do_create)
        name_in.returnPressed.connect(do_create)
        dlg.exec()

    # ── Helpers reutilizables ─────────────────────────────────────────────────
    @staticmethod
    def _aux_page_skeleton(title: str, subtitle: str) -> tuple:
        page = QWidget()
        pl = QVBoxLayout(page)
        pl.setContentsMargins(0, 0, 0, 0)
        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(0, 40, 0, 40)
        wrapper.setSpacing(12)
        wrapper.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s = QLabel(subtitle)
        s.setObjectName("SubtitleLabel")
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wrapper.addWidget(t)
        wrapper.addWidget(s)
        pl.addLayout(wrapper)
        return page, wrapper

    @staticmethod
    def _form_card(width: int = 420) -> QWidget:
        c = QWidget()
        c.setProperty("class", "login-card")
        c.setFixedWidth(width)
        return c

    @staticmethod
    def _field_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "color: #7E8A94; font-size: 9.5pt; font-weight: 600; margin-bottom: 3px;"
        )
        return lbl

    @staticmethod
    def _input(placeholder: str, password: bool = False) -> QLineEdit:
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        if password:
            w.setEchoMode(QLineEdit.EchoMode.Password)
        return w

    @staticmethod
    def _error_label() -> QLabel:
        lbl = QLabel("")
        lbl.setStyleSheet(
            "color: #EF4444; font-size: 9pt; background: rgba(239,68,68,0.08); "
            "border-radius: 6px; padding: 6px 10px;"
        )
        lbl.setWordWrap(True)
        lbl.setVisible(False)
        return lbl

    @staticmethod
    def _show_inline_error(lbl: QLabel, msg: str) -> None:
        lbl.setText(f"⚠  {msg}")
        lbl.setVisible(True)
        QTimer.singleShot(6000, lambda: lbl.setVisible(False))

    @staticmethod
    def _primary_btn(text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", "primary")
        btn.setFixedHeight(42)
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        return btn

    @staticmethod
    def _link_btn(text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", "link-button")
        return btn


# ── Arranque con health-check de DB ───────────────────────────────────────────
def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Phishing Shield")
    app.setApplicationVersion("3.1")

    # Verificar conexión DB antes de mostrar la ventana principal
    try:
        from database.connection import test_connection
        db_ok, db_msg = test_connection()
        if not db_ok:
            QMessageBox.critical(
                None,
                "Error de base de datos",
                f"No se pudo conectar a la base de datos:\n\n{db_msg}\n\n"
                "Verifica tu archivo .env y que MySQL esté corriendo.\n"
                "La aplicación se iniciará en modo limitado.",
            )
    except Exception:
        pass  # Sin MySQL instalado, continuar de todas formas

    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
