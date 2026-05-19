from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from database.campaigns import obtener_campanas


class PhishingScreen(QWidget):
    def __init__(self, on_new_campaign: callable, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── Cabecera ─────────────────────────────────────────────────────────
        header_w = QWidget()
        header_lay = QHBoxLayout(header_w)
        header_lay.setContentsMargins(0, 0, 0, 0)

        titles = QVBoxLayout()
        titles.setSpacing(3)
        t = QLabel("Simulaciones de Phishing")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        s = QLabel("Gestiona campañas de simulación y analiza resultados de clic")
        s.setObjectName("SubtitleLabel")
        titles.addWidget(t)
        titles.addWidget(s)
        header_lay.addLayout(titles)
        header_lay.addStretch(1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        refresh_btn = QPushButton("↺  Actualizar")
        refresh_btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.05); color: #94A3B8; "
            "border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; "
            "padding: 7px 14px; font-size: 9.5pt; }"
            "QPushButton:hover { background: rgba(255,255,255,0.10); color: #E2E8F0; }"
        )
        refresh_btn.clicked.connect(self.load_campaigns)

        create_btn = QPushButton("＋  Nueva Campaña")
        create_btn.setProperty("class", "purple-button")
        create_btn.clicked.connect(on_new_campaign)

        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(create_btn)
        header_lay.addLayout(btn_row)
        layout.addWidget(header_w)

        # ── Stat cards ────────────────────────────────────────────────────────
        stats_w = QWidget()
        stats_lay = QHBoxLayout(stats_w)
        stats_lay.setContentsMargins(0, 0, 0, 0)
        stats_lay.setSpacing(14)

        self._stat_labels: dict[str, QLabel] = {}

        for icon, label, color in [
            ("✉", "Total Campañas", "#3B82F6"),
            ("⏱", "Activas",        "#10B981"),
            ("✓", "Finalizadas",    "#6B7280"),
            ("🖱", "Clics Totales",  "#F59E0B"),
            ("⚑", "Reportes",       "#A78BFA"),
        ]:
            card = QWidget()
            card.setProperty("class", "stat-card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 16, 18, 16)
            cl.setSpacing(4)

            icon_lbl = QLabel(icon)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(f"font-size: 16pt; color: {color};")

            val_lbl = QLabel("—")
            val_lbl.setObjectName("StatValue")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {color};")

            txt_lbl = QLabel(label)
            txt_lbl.setObjectName("StatLabel")
            txt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            cl.addWidget(icon_lbl)
            cl.addWidget(val_lbl)
            cl.addWidget(txt_lbl)

            self._stat_labels[label] = val_lbl
            stats_lay.addWidget(card)

        layout.addWidget(stats_w)

        # ── Tabla de campañas ─────────────────────────────────────────────────
        table_card = QWidget()
        table_card.setProperty("class", "card")
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(18, 16, 18, 18)
        tl.setSpacing(12)

        thead = QHBoxLayout()
        tl.addLayout(thead)
        tcard_title = QLabel("Historial de Campañas")
        tcard_title.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        thead.addWidget(tcard_title)
        thead.addStretch(1)

        self._last_update_lbl = QLabel("")
        self._last_update_lbl.setStyleSheet("color: #475569; font-size: 8.5pt;")
        thead.addWidget(self._last_update_lbl)

        # FIXED: tabla inicializada sin filas (antes era QTableWidget(4, 8))
        self.campaign_table = QTableWidget(0, 8)
        self.campaign_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo de Ataque", "Estado",
            "Usuarios", "Aperturas", "% Clics", "Reportes",
        ])
        hdr = self.campaign_table.horizontalHeader()
        # FIXED: modo correcto — stretch para columna de nombre, resto ResizeToContents
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.campaign_table.verticalHeader().setVisible(False)
        self.campaign_table.setShowGrid(False)
        # FIXED: SelectRows (antes era NoSelection, imposible interactuar)
        self.campaign_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.campaign_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.campaign_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.campaign_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.campaign_table.setAlternatingRowColors(True)
        self.campaign_table.setStyleSheet(
            "QTableWidget { background: transparent; gridline-color: #1E293B; border: none; }"
            "QTableWidget::item:alternate { background: rgba(255,255,255,0.02); }"
            "QTableWidget::item:selected { background: rgba(59,130,246,0.18); color: #E2E8F0; }"
            "QHeaderView::section { background: #111827; color: #475569; border: none; "
            "padding: 8px 6px; font-size: 9pt; font-weight: 600; "
            "border-bottom: 1px solid #1E293B; }"
        )
        tl.addWidget(self.campaign_table)

        # Estado vacío
        self._empty_lbl = QLabel("No hay campañas registradas. Crea una con el botón «＋ Nueva Campaña».")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setStyleSheet("color: #334155; font-size: 10pt; padding: 40px;")
        self._empty_lbl.setVisible(False)
        tl.addWidget(self._empty_lbl)

        layout.addWidget(table_card, 1)

        # ── Timer de auto-refresco ─────────────────────────────────────────────
        # FIXED: 30s en lugar de 5s para no saturar la DB
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.load_campaigns)
        self._timer.start(30_000)

        self.load_campaigns()

    # ─────────────────────────────────────────────────────────────────────────
    def load_campaigns(self) -> None:
        try:
            campanas = obtener_campanas()
        except Exception as e:
            self._last_update_lbl.setText(f"Error de conexión: {e}")
            return

        self.campaign_table.setRowCount(0)

        total      = len(campanas)
        activas    = sum(1 for c in campanas if c.get("estado") == "active")
        fin        = sum(1 for c in campanas if c.get("estado") == "finished")
        clics      = sum(c.get("clicks") or 0  for c in campanas)
        reportes   = sum(c.get("reportes") or 0 for c in campanas)

        self._stat_labels["Total Campañas"].setText(str(total))
        self._stat_labels["Activas"].setText(str(activas))
        self._stat_labels["Finalizadas"].setText(str(fin))
        self._stat_labels["Clics Totales"].setText(str(clics))
        self._stat_labels["Reportes"].setText(str(reportes))

        # Mostrar estado vacío si no hay campañas
        self._empty_lbl.setVisible(total == 0)
        self.campaign_table.setVisible(total > 0)

        _TIPO = {
            "password_reset":    "Credenciales",
            "urgent_request":    "Urgencia",
            "survey_reward":     "Incentivo",
            "attachment_malware":"Malware",
        }

        self.campaign_table.setRowCount(total)
        for r, c in enumerate(campanas):
            usuarios_int  = c.get("usuarios")  or 0
            aperturas_int = c.get("aperturas") or 0
            clicks_int    = c.get("clicks")    or 0
            rep_int       = c.get("reportes")  or 0

            pct_clics = round(clicks_int / usuarios_int * 100) if usuarios_int else 0
            estado_str = "Activa" if c.get("estado") == "active" else "Finalizada"

            row = [
                f"CAM-{c.get('id_campaign', 0):03d}",
                c.get("name", "—"),
                _TIPO.get(c.get("attack_type", ""), "—"),
                estado_str,
                str(usuarios_int),
                str(aperturas_int),
                f"{pct_clics}%",
                str(rep_int),
            ]

            for col, text in enumerate(row):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                if col == 0:   # ID
                    item.setForeground(QColor("#60A5FA"))
                elif col == 3: # Estado
                    item.setForeground(QColor("#10B981") if estado_str == "Activa" else QColor("#475569"))
                elif col == 6: # % Clics — rojo si alto
                    if pct_clics > 30:
                        item.setForeground(QColor("#EF4444"))
                    elif pct_clics > 15:
                        item.setForeground(QColor("#F59E0B"))
                elif col == 7: # Reportes — verde
                    item.setForeground(QColor("#10B981"))

                if col >= 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.campaign_table.setItem(r, col, item)

        from PyQt6.QtCore import QDateTime
        self._last_update_lbl.setText(
            f"Actualizado: {QDateTime.currentDateTime().toString('HH:mm:ss')}"
        )
