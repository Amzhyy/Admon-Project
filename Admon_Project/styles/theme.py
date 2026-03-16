from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QMainWindow


def apply_dark_theme(window: QMainWindow) -> None:
    base_color = QColor(31, 34, 38)  # #1F2226
    accent_color = QColor(63, 224, 197)  # #3FE0C5
    text_color = QColor(230, 232, 234)  # #E6E8EA
    secondary_text = QColor(170, 180, 190)  # #AAB4BE

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, base_color)
    palette.setColor(QPalette.ColorRole.WindowText, text_color)
    palette.setColor(QPalette.ColorRole.Base, QColor(42, 46, 51))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(31, 34, 38))
    palette.setColor(QPalette.ColorRole.ToolTipBase, text_color)
    palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
    palette.setColor(QPalette.ColorRole.Text, text_color)
    palette.setColor(QPalette.ColorRole.Button, QColor(58, 63, 68))
    palette.setColor(QPalette.ColorRole.ButtonText, text_color)
    palette.setColor(QPalette.ColorRole.Highlight, accent_color)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(31, 34, 38))

    window.setPalette(palette)

    window.setStyleSheet(
        """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1F2226, stop:0.35 #2A2E33, stop:0.7 #3A3F44, stop:1 #6F7E85);
        }
        QWidget#MainContainer {
            background: qradialgradient(cx:0.2, cy:0.1, radius:0.4, fx:0.2, fy:0.1, stop:0 rgba(63,224,197,0.15), stop:1 rgba(63,224,197,0));
        }
        QWidget#SidebarWidget {
            background-color: rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        QWidget {
            color: #E6E8EA;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
        }
        QLabel {
            background-color: transparent;
        }
        QScrollArea, QScrollArea > QWidget > QWidget {
            background-color: transparent;
            border: none;
        }
        QScrollArea QWidget#qt_scrollarea_viewport {
            background-color: transparent;
        }
        QStackedWidget {
            background-color: transparent;
        }
        QListWidget {
            border: none;
            background-color: transparent;
            outline: 0;
        }
        QListWidget::item {
            padding: 10px 14px;
            margin: 2px 4px;
            border-radius: 14px;
            color: #AAB4BE;
        }
        QListWidget::item:selected {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid #3FE0C5;
            color: #E6E8EA;
        }
        QListWidget::item:hover:!selected {
            background-color: rgba(255, 255, 255, 0.05);
        }
        QListWidget::item:focus {
            outline: none;
        }
        QLabel#TitleLabel {
            font-size: 22pt;
            font-weight: 600;
            letter-spacing: 0.5px;
            color: #E6E8EA;
        }
        QLabel#SubtitleLabel, QLabel#StatLabel, QLabel#TeamRoleLabel {
            color: #AAB4BE;
        }
        QPushButton.primary, .purple-button, QDialogButtonBox QPushButton {
            background-color: #3FE0C5;
            color: #1F2226;
            border-radius: 10px;
            padding: 8px 16px;
            min-height: 24px;
            font-weight: bold;
            border: none;
        }
        QPushButton.primary:hover, .purple-button:hover, QDialogButtonBox QPushButton:hover {
            background-color: #35cbb2;
        }
        QPushButton.primary:pressed, .purple-button:pressed, QDialogButtonBox QPushButton:pressed {
            background-color: #2daea0;
        }
        QDialogButtonBox QPushButton[text="Cancelar"], QDialogButtonBox QPushButton[text="Cancel"] {
            background-color: rgba(255, 255, 255, 0.05);
            color: #AAB4BE;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        QDialogButtonBox QPushButton[text="Cancelar"]:hover, QDialogButtonBox QPushButton[text="Cancel"]:hover {
            background-color: rgba(255, 255, 255, 0.1);
            color: #E6E8EA;
        }
        QPushButton#SidebarToggle {
            background-color: transparent;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 4px 8px;
            color: #AAB4BE;
        }
        QPushButton#SidebarToggle:hover {
            border: 1px solid #3FE0C5;
            color: #3FE0C5;
        }
        .content-shell {
            background: transparent;
            padding: 30px;
        }
        .content-shell, .card, .login-card, .team-card, .ai-chat-card, .stat-card {
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .content-shell:hover, .card:hover, .team-card:hover, .stat-card:hover {
            border: 1px solid rgba(63, 224, 197, 0.3);
        }
        .login-card QLineEdit {
            background-color: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 10px;
            font-size: 11pt;
            color: #E6E8EA;
            border-radius: 6px;
        }
        .login-card QLineEdit:focus {
            border: 1px solid #3FE0C5;
        }
        QFormLayout QLabel {
            color: #AAB4BE;
            font-size: 10pt;
            font-weight: 500;
        }
        .login-card QLabel#LoginTitle {
            color: #E6E8EA;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }
        QDialog {
            background-color: #1a1d21;
        }
        QDialog QLabel {
            color: #E6E8EA;
        }
        QLineEdit, QComboBox, QDateEdit, QTextEdit {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            color: #E6E8EA;
            font-size: 10pt;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
            border: 1px solid #3FE0C5;
            background-color: rgba(63, 224, 197, 0.05);
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #AAB4BE;
            margin-right: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #1F2226;
            border: 1px solid rgba(255, 255, 255, 0.1);
            selection-background-color: rgba(63, 224, 197, 0.2);
            selection-color: #E6E8EA;
            outline: none;
            border-radius: 8px;
        }
        QCalendarWidget QWidget#qt_calendar_navigationbar {
            background-color: #1F2226;
        }
        QCalendarWidget QAbstractItemView {
            background-color: #1a1d21;
            selection-background-color: #3FE0C5;
            selection-color: #1F2226;
        }
        QDateEdit::drop-down {
            border: none;
            width: 30px;
        }
        QDateEdit::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #AAB4BE;
            margin-right: 12px;
        }
        .login-card QLabel#LoginSubtitle {
            color: #AAB4BE;
        }
        .link-button, .team-expand {
            background-color: transparent;
            border: none;
            color: #3FE0C5;
            padding: 2px 0;
            font-size: 10pt;
            text-align: left;
        }
        .link-button:hover, .team-expand:hover {
            color: #E6E8EA;
            text-decoration: underline;
        }
        .team-avatar {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 40px;
            border: 2px solid rgba(63, 224, 197, 0.7);
        }
        QLabel#TeamNameLabel, QLabel#StatValue {
            color: #E6E8EA;
            font-weight: bold;
        }
        QLabel#StatValue {
            font-size: 20pt;
        }
        .social-row QPushButton {
            background-color: transparent;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 4px 8px;
            min-width: 28px;
            color: #AAB4BE;
            font-size: 10pt;
        }
        .social-row QPushButton:hover {
            border-color: #3FE0C5;
            color: #3FE0C5;
        }
        .social-row QPushButton:pressed {
            background-color: rgba(63, 224, 197, 0.1);
        }
        .team-bio {
            color: #AAB4BE;
            font-size: 9pt;
        }
        .ai-bot-msg {
            background-color: rgba(63, 224, 197, 0.15);
            color: #E6E8EA;
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 8px;
            border-left: 3px solid #3FE0C5;
        }
        .ai-user-msg {
            background-color: rgba(255, 255, 255, 0.05);
            color: #E6E8EA;
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 8px;
            text-align: right;
            border-right: 3px solid #AAB4BE;
        }
        .ai-input, QLineEdit, QTextEdit, QComboBox, QDateEdit {
            background-color: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            color: #E6E8EA;
            padding: 10px;
            font-size: 11pt;
        }
        .ai-input:focus, QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
            border: 1px solid #3FE0C5;
        }
        QTableWidget {
            background-color: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            gridline-color: rgba(255, 255, 255, 0.08);
            color: #E6E8EA;
        }
        QTableWidget::item {
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        QHeaderView::section {
            background-color: transparent;
            color: #3FE0C5;
            font-weight: bold;
            padding: 8px 12px;
            border: none;
            border-bottom: 2px solid rgba(63, 224, 197, 0.5);
            text-align: left;
        }
        """
    )

