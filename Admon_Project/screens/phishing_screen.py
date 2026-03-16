from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class PhishingScreen(QWidget):
    def __init__(self, on_new_campaign: callable, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # self.setProperty("class", "content-shell")

        layout = QVBoxLayout(self)
        layout.setSpacing(24)

        # Header
        header_inner = QWidget()
        header_layout = QHBoxLayout(header_inner)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        title = QLabel("Simulaciones de Phishing")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        subtitle = QLabel("Crea y gestiona campañas de simulación de correos de phishing")
        subtitle.setObjectName("SubtitleLabel")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)

        create_button = QPushButton("+ Nueva Campaña")
        create_button.setProperty("class", "purple-button")
        create_button.clicked.connect(on_new_campaign)
        header_layout.addWidget(create_button, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addWidget(header_inner)

        # Stat cards
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(16)

        stats_data = [
            ("4", "Total Campañas", "✉"),
            ("2", "Activas", "⏱"),
            ("2", "Finalizadas", "✓"),
            ("63", "Clics Totales", "🖱"),
        ]

        for val, lbl, icon_text in stats_data:
            card = QWidget()
            card.setProperty("class", "stat-card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)

            icon_lbl = QLabel(icon_text)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            val_lbl = QLabel(val)
            val_lbl.setObjectName("StatValue")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text_lbl = QLabel(lbl)
            text_lbl.setObjectName("StatLabel")
            text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(icon_lbl)
            card_layout.addSpacing(10)
            card_layout.addWidget(val_lbl)
            card_layout.addWidget(text_lbl)

            stats_layout.addWidget(card)

        layout.addWidget(stats_widget)

        # Table region
        table_card = QWidget()
        table_card.setProperty("class", "card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(16)

        table_title = QLabel("Campañas")
        table_title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        table_layout.addWidget(table_title)

        campaign_table = QTableWidget(4, 8)
        campaign_table.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Tipo", "Estado", "Usuarios", "% Aperturas", "% Clics", "Reportes"]
        )

        # Adjust table behavior
        campaign_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        campaign_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        campaign_table.verticalHeader().setVisible(False)
        campaign_table.setShowGrid(False)
        campaign_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        campaign_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        campaign_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        mock_data = [
            ("CAM-001", "Suplantación de TI - Reset Password", "Credenciales", "Finalizada", "45", "32", "18", "5"),
            ("CAM-002", "Actualización de nómina urgente", "Urgencia", "Activa", "30", "22", "8", "3"),
            ("CAM-003", "Premio de fin de año - Encuesta", "Incentivo", "Finalizada", "60", "48", "25", "7"),
            ("CAM-004", "Verificación de cuenta Office 365", "Credenciales", "Activa", "50", "35", "12", "8"),
        ]

        for r, row_data in enumerate(mock_data):
            for c, text in enumerate(row_data):
                item = QTableWidgetItem(text)

                # Styling for specific columns
                if c == 0:  # ID
                    item.setForeground(QColor("#60A5FA"))
                elif c == 3:  # Estado
                    # Usar "pastilla" decorativa
                    if text == "Finalizada":
                        item.setForeground(QColor("#9CA3AF"))
                    else:
                        item.setForeground(QColor("#34D399"))
                elif c == 6:  # Clics (orange/red for high)
                    item.setForeground(QColor("#F97316"))
                elif c == 7:  # Reportes (green for good)
                    item.setForeground(QColor("#34D399"))

                # Center align numbers
                if c >= 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

                campaign_table.setItem(r, c, item)

        table_layout.addWidget(campaign_table)

        layout.addWidget(table_card, 1)

