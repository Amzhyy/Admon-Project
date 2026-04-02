from PyQt6.QtCore import Qt, QTimer
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

from database.campaigns import obtener_campanas


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

        self.stats_data = {
            "Total Campañas": "0",
            "Activas": "0",
            "Finalizadas": "0",
            "Clics Totales": "0"
        }
        
        self.stats_widgets = {}

        stats_base = [
            ("Total Campañas", "✉"),
            ("Activas", "⏱"),
            ("Finalizadas", "✓"),
            ("Clics Totales", "🖱"),
        ]

        for lbl, icon_text in stats_base:
            card = QWidget()
            card.setProperty("class", "stat-card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)

            icon_lbl = QLabel(icon_text)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            val_lbl = QLabel("0")
            val_lbl.setObjectName("StatValue")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text_lbl = QLabel(lbl)
            text_lbl.setObjectName("StatLabel")
            text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(icon_lbl)
            card_layout.addSpacing(10)
            card_layout.addWidget(val_lbl)
            card_layout.addWidget(text_lbl)

            self.stats_widgets[lbl] = val_lbl
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

        self.campaign_table = campaign_table
        table_layout.addWidget(self.campaign_table)

        layout.addWidget(table_card, 1)

        # Load campaigns directly on init
        self.load_campaigns()

        # Timer for auto-refresh (every 5 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_campaigns)
        self.refresh_timer.start(5000)  # 5 seconds

    def load_campaigns(self):
        campanas = obtener_campanas()
        
        self.campaign_table.setRowCount(0)
        
        total = len(campanas)
        activas = sum(1 for c in campanas if c.get("estado") == "active")
        finalizadas = sum(1 for c in campanas if c.get("estado") == "finished")
        clics_totales = sum(c.get("clicks") or 0 for c in campanas)
        
        self.stats_widgets["Total Campañas"].setText(str(total))
        self.stats_widgets["Activas"].setText(str(activas))
        self.stats_widgets["Finalizadas"].setText(str(finalizadas))
        self.stats_widgets["Clics Totales"].setText(str(clics_totales))
        
        self.campaign_table.setRowCount(total)
        
        for r, cmp in enumerate(campanas):
            # mapping values
            id_text = f"CAM-{cmp.get('id_campaign', 0):03d}"
            nombre = cmp.get("name", "N/A")
            
            tipo_map = {
                "password_reset": "Credenciales",
                "urgent_request": "Urgencia",
                "survey_reward": "Incentivo",
                "attachment_malware": "Malware"
            }
            tipo = tipo_map.get(cmp.get("attack_type", ""), "Credenciales")
            
            estado = "Activa" if cmp.get("estado") == "active" else "Finalizada"
            usuarios = str(cmp.get("usuarios", 0))
            
            # Percentages
            usuarios_int = cmp.get("usuarios") or 0
            aperturas = cmp.get("aperturas") or 0
            clicks = cmp.get("clicks") or 0
            
            pct_aperturas = int((aperturas / usuarios_int * 100)) if usuarios_int > 0 else 0
            pct_clics = int((clicks / usuarios_int * 100)) if usuarios_int > 0 else 0
            
            estr_pct_ap = f"{pct_aperturas}%"
            estr_pct_cl = f"{pct_clics}%"
            reportes = str(cmp.get("reportes") or 0)
            
            row_data = [
                id_text, nombre, tipo, estado, usuarios, estr_pct_ap, estr_pct_cl, reportes
            ]
            
            for c, text in enumerate(row_data):
                item = QTableWidgetItem(text)

                if c == 0:  # ID
                    item.setForeground(QColor("#60A5FA"))
                elif c == 3:  # Estado
                    if text == "Finalizada":
                        item.setForeground(QColor("#9CA3AF"))
                    else:
                        item.setForeground(QColor("#34D399"))
                elif c == 6:  # Clics
                    # color por %
                    if pct_clics > 15:
                        item.setForeground(QColor("#F97316"))
                elif c == 7:  # Reportes
                    item.setForeground(QColor("#34D399"))

                if c >= 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

                self.campaign_table.setItem(r, c, item)

