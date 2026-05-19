from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QMainWindow


def apply_dark_theme(window: QMainWindow) -> None:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#1F2226"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#E6E8EA"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#161A1E"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#1F2226"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#E6E8EA"))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#E6E8EA"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#E6E8EA"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#2A2E33"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#E6E8EA"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#3FE0C5"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1F2226"))
    palette.setColor(QPalette.ColorRole.Link,            QColor("#3FE0C5"))
    window.setPalette(palette)

    window.setStyleSheet("""
/* ── Ventana principal ─────────────────────────────────────────────── */
QMainWindow {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1a1d22, stop:0.5 #1F2226, stop:1 #252930);
}
QWidget#MainContainer {
    background: transparent;
}

/* ── Base ──────────────────────────────────────────────────────────── */
QWidget {
    color: #E6E8EA;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    font-size: 11pt;
}
QLabel { background-color: transparent; }
QStackedWidget { background-color: transparent; }

/* ── Sidebar ───────────────────────────────────────────────────────── */
QWidget#SidebarWidget {
    background-color: rgba(0,0,0,0.30);
    border-right: 1px solid rgba(255,255,255,0.06);
}
QListWidget {
    border: none;
    background-color: transparent;
    outline: 0;
}
QListWidget::item {
    padding: 10px 14px;
    margin: 2px 6px;
    border-radius: 10px;
    color: #7E8A94;
    font-size: 10.5pt;
}
QListWidget::item:selected {
    background-color: rgba(63,224,197,0.12);
    border: 1px solid rgba(63,224,197,0.35);
    color: #3FE0C5;
}
QListWidget::item:hover:!selected {
    background-color: rgba(255,255,255,0.04);
    color: #B0BAC4;
}
QListWidget::item:focus { outline: none; }

/* ── Cards / shells ────────────────────────────────────────────────── */
.content-shell, .card, .login-card, .team-card, .ai-chat-card, .stat-card {
    background-color: rgba(255,255,255,0.03);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.07);
}
.content-shell:hover, .card:hover, .team-card:hover, .stat-card:hover {
    border-color: rgba(63,224,197,0.25);
}

/* ── Labels especiales ──────────────────────────────────────────────── */
QLabel#TitleLabel {
    font-size: 22pt;
    font-weight: 700;
    letter-spacing: 0.3px;
    color: #E6E8EA;
}
QLabel#SubtitleLabel, QLabel#StatLabel, QLabel#TeamRoleLabel {
    color: #7E8A94;
    font-size: 10pt;
}
QLabel#LoginTitle  { font-size: 17pt; font-weight: 700; color: #E6E8EA; }
QLabel#LoginSubtitle { color: #7E8A94; font-size: 10pt; }

/* ── Inputs ─────────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 8px;
    padding: 8px 12px;
    color: #E6E8EA;
    font-size: 10.5pt;
    selection-background-color: rgba(63,224,197,0.3);
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #3FE0C5;
    background-color: rgba(63,224,197,0.04);
}
QLineEdit:disabled, QTextEdit:disabled {
    color: #4A5568;
    background-color: rgba(255,255,255,0.02);
}
QLineEdit[class="login-card"] {
    background-color: rgba(0,0,0,0.22);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 10px 12px;
}

/* ── ComboBox ───────────────────────────────────────────────────────── */
QComboBox { padding-right: 30px; }
QComboBox::drop-down  { border: none; width: 30px; }
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #7E8A94;
    margin-right: 12px;
}
QComboBox QAbstractItemView {
    background-color: #1a1d21;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    selection-background-color: rgba(63,224,197,0.18);
    selection-color: #E6E8EA;
    outline: none;
    padding: 4px;
}
QComboBox QAbstractItemView::item { padding: 8px 12px; border-radius: 6px; }
QDateEdit::drop-down { border: none; width: 30px; }
QDateEdit::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #7E8A94;
    margin-right: 12px;
}

/* ── Botones ────────────────────────────────────────────────────────── */
QPushButton {
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 10.5pt;
    font-weight: 600;
    border: 1px solid transparent;
    background-color: rgba(255,255,255,0.05);
    color: #B0BAC4;
}
QPushButton:hover { background-color: rgba(255,255,255,0.09); color: #E6E8EA; }
QPushButton:pressed { background-color: rgba(255,255,255,0.04); }

/* Primary */
QPushButton.primary, QPushButton[class="primary"] {
    background-color: #3FE0C5;
    color: #111417;
    border: none;
    min-height: 22px;
}
QPushButton.primary:hover, QPushButton[class="primary"]:hover  { background-color: #35cdb4; }
QPushButton.primary:pressed, QPushButton[class="primary"]:pressed { background-color: #29a99a; }
QPushButton.primary:disabled { background-color: rgba(63,224,197,0.25); color: rgba(0,0,0,0.4); }

/* Purple / accent */
.purple-button, QPushButton[class="purple-button"] {
    background-color: #3FE0C5;
    color: #111417;
    border: none;
    font-weight: 700;
    border-radius: 10px;
    padding: 8px 18px;
}
.purple-button:hover { background-color: #35cdb4; }

/* Link */
.link-button, .team-expand {
    background-color: transparent;
    border: none;
    color: #3FE0C5;
    padding: 2px 0;
    font-size: 10pt;
    font-weight: 500;
}
.link-button:hover { color: #E6E8EA; text-decoration: underline; }

/* Dialog buttons */
QDialogButtonBox QPushButton {
    background-color: #3FE0C5;
    color: #111417;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    min-width: 90px;
    font-weight: 700;
}
QDialogButtonBox QPushButton:hover { background-color: #35cdb4; }
QDialogButtonBox QPushButton[text="Cancelar"],
QDialogButtonBox QPushButton[text="Cancel"] {
    background-color: rgba(255,255,255,0.05);
    color: #7E8A94;
    border: 1px solid rgba(255,255,255,0.1);
}
QDialogButtonBox QPushButton[text="Cancelar"]:hover,
QDialogButtonBox QPushButton[text="Cancel"]:hover {
    background-color: rgba(255,255,255,0.1);
    color: #E6E8EA;
}

/* Sidebar toggle */
QPushButton#SidebarToggle {
    background-color: transparent;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 4px 8px;
    color: #7E8A94;
    font-size: 13pt;
}
QPushButton#SidebarToggle:hover {
    border-color: #3FE0C5;
    color: #3FE0C5;
    background-color: rgba(63,224,197,0.06);
}

/* ── Tabla ──────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: rgba(0,0,0,0.30);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    gridline-color: rgba(255,255,255,0.05);
    color: #D1D8E0;
    alternate-background-color: rgba(255,255,255,0.015);
}
QTableWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
QTableWidget::item:hover  { background-color: rgba(63,224,197,0.05); }
QTableWidget::item:selected {
    background-color: rgba(63,224,197,0.12);
    color: #E6E8EA;
}
QHeaderView::section {
    background-color: transparent;
    color: #3FE0C5;
    font-weight: 700;
    font-size: 9.5pt;
    letter-spacing: 0.4px;
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid rgba(63,224,197,0.4);
    text-transform: uppercase;
}

/* ── ScrollBar ─────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.12);
    border-radius: 3px;
    min-height: 28px;
}
QScrollBar::handle:vertical:hover { background: rgba(63,224,197,0.55); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical,  QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: rgba(255,255,255,0.12);
    border-radius: 3px;
    min-width: 28px;
}
QScrollBar::handle:horizontal:hover { background: rgba(63,224,197,0.55); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
QScrollArea, QScrollArea > QWidget > QWidget { background-color: transparent; border: none; }

/* ── ProgressBar ───────────────────────────────────────────────────── */
QProgressBar {
    background-color: rgba(255,255,255,0.06);
    border: none;
    border-radius: 4px;
    height: 5px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #3FE0C5, stop:1 #2B8AF4);
    border-radius: 4px;
}

/* ── CheckBox ──────────────────────────────────────────────────────── */
QCheckBox { color: #9CA3AF; spacing: 8px; font-size: 10pt; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    border: 1.5px solid rgba(255,255,255,0.18);
    border-radius: 4px;
    background: rgba(255,255,255,0.04);
}
QCheckBox::indicator:checked {
    background: #3FE0C5;
    border-color: #3FE0C5;
    image: none;
}
QCheckBox::indicator:hover { border-color: rgba(63,224,197,0.6); }

/* ── Tabs ──────────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #5A6A76;
    padding: 9px 20px;
    font-size: 10pt;
    font-weight: 600;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected { color: #3FE0C5; border-bottom: 2px solid #3FE0C5; }
QTabBar::tab:hover:!selected { color: #9CA3AF; }

/* ── Splitter ──────────────────────────────────────────────────────── */
QSplitter::handle { background: rgba(255,255,255,0.05); }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical   { height: 1px; }

/* ── ToolTip ───────────────────────────────────────────────────────── */
QToolTip {
    background-color: #1a1d22;
    color: #E2E8F0;
    border: 1px solid rgba(63,224,197,0.35);
    border-radius: 6px;
    padding: 5px 9px;
    font-size: 9.5pt;
    opacity: 230;
}

/* ── Dialog / MessageBox ───────────────────────────────────────────── */
QDialog {
    background-color: #18191e;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 12px;
}
QDialog QLabel { color: #D1D8E0; }
QMessageBox {
    background-color: #18191e;
}
QMessageBox QLabel { color: #D1D8E0; font-size: 10.5pt; }
QMessageBox QPushButton { min-width: 80px; }

/* ── FormLayout ────────────────────────────────────────────────────── */
QFormLayout QLabel {
    color: #7E8A94;
    font-size: 10pt;
    font-weight: 500;
}

/* ── Calendario ────────────────────────────────────────────────────── */
QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #1F2226; }
QCalendarWidget QAbstractItemView {
    background-color: #1a1d21;
    selection-background-color: #3FE0C5;
    selection-color: #1F2226;
    gridline-color: rgba(255,255,255,0.06);
}

/* ── Social / Team ─────────────────────────────────────────────────── */
.team-avatar {
    background-color: rgba(255,255,255,0.04);
    border-radius: 40px;
    border: 2px solid rgba(63,224,197,0.6);
}
QLabel#TeamNameLabel, QLabel#StatValue { color: #E6E8EA; font-weight: 700; }
QLabel#StatValue { font-size: 20pt; }
.social-row QPushButton {
    background-color: transparent;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    padding: 3px 8px;
    min-width: 26px;
    color: #7E8A94;
    font-size: 10pt;
}
.social-row QPushButton:hover { border-color: #3FE0C5; color: #3FE0C5; }

/* ── AI chat ───────────────────────────────────────────────────────── */
.ai-bot-msg {
    background-color: rgba(63,224,197,0.12);
    color: #E6E8EA;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 8px;
    border-left: 3px solid #3FE0C5;
}
.ai-user-msg {
    background-color: rgba(255,255,255,0.04);
    color: #E6E8EA;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 8px;
    border-right: 3px solid rgba(255,255,255,0.2);
}
""")
