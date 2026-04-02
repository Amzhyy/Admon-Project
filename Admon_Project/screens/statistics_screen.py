import numpy as np
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QComboBox,
    QLineEdit,
)

from database.campaigns import obtener_campanas


class StatisticsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.campaign_data = []

        # Usamos un QScrollArea ya que el contenido será extenso
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(24)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("Reportes")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        subtitle = QLabel("Análisis y resúmenes ejecutivos de las campañas de simulación")
        subtitle.setObjectName("SubtitleLabel")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)

        self.export_btn = QPushButton("↓ Exportar PDF")
        self.export_btn.setProperty("class", "purple-button")
        self.export_btn.clicked.connect(self.export_to_pdf)
        header_layout.addWidget(self.export_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header_layout)

        # --- FILTRO ---
        filter_card = QWidget()
        filter_card.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_lbl = QLabel("▽ Filtrar por campaña:")
        filter_lbl.setObjectName("SubtitleLabel")
        self.cmb_filter = QComboBox()
        self.cmb_filter.setFixedWidth(200)
        self.cmb_filter.currentIndexChanged.connect(self.update_charts)
        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(self.cmb_filter)
        filter_layout.addStretch(1)
        layout.addWidget(filter_card)

        # --- GRÁFICOS MATPLOTLIB NEON ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)

        # Gráfico 1: Barras Agrupadas
        chart1_card = QWidget()
        chart1_card.setProperty("class", "card")
        chart1_layout = QVBoxLayout(chart1_card)

        self.fig1 = Figure(figsize=(5, 4), facecolor='none')
        self.ax1 = self.fig1.add_subplot(111)
        
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setStyleSheet("background-color:transparent;")
        self.canvas1.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.canvas1.setMinimumHeight(250)

        chart1_layout.addWidget(self.canvas1)
        charts_layout.addWidget(chart1_card, 1)

        # Gráfico 2: Líneas (Tendencia)
        chart2_card = QWidget()
        chart2_card.setProperty("class", "card")
        chart2_layout = QVBoxLayout(chart2_card)

        self.fig2 = Figure(figsize=(5, 4), facecolor='none')
        self.ax2 = self.fig2.add_subplot(111)
        
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.setStyleSheet("background-color:transparent;")
        self.canvas2.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.canvas2.setMinimumHeight(250)

        chart2_layout.addWidget(self.canvas2)
        charts_layout.addWidget(chart2_card, 1)

        layout.addLayout(charts_layout)

        # --- RESUMEN EJECUTIVO AUTOMÁTICO & ANÁLISIS IA ---
        summary_card = QWidget()
        summary_card.setProperty("class", "card")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(20, 20, 20, 20)
        summary_layout.setSpacing(16)

        sum_title = QLabel("📄 Resumen Ejecutivo Automático")
        sum_title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        summary_layout.addWidget(sum_title)

        # Mini KPIs
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)

        # Config KPI Cards
        # Card 1
        k_card1 = QWidget()
        k_card1.setProperty("class", "stat-card")
        kl1 = QVBoxLayout(k_card1)
        kl1.addWidget(QLabel("Campañas ejecutadas"))
        self.kpi_executed = QLabel("0")
        self.kpi_executed.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        kl1.addWidget(self.kpi_executed)
        kpi_layout.addWidget(k_card1)

        # Card 2
        k_card2 = QWidget()
        k_card2.setProperty("class", "stat-card")
        kl2 = QVBoxLayout(k_card2)
        kl2.addWidget(QLabel("Tasa de clics"))
        self.kpi_clicks = QLabel("0%")
        self.kpi_clicks.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        kl2.addWidget(self.kpi_clicks)
        kpi_layout.addWidget(k_card2)

        # Card 3
        k_card3 = QWidget()
        k_card3.setProperty("class", "stat-card")
        kl3 = QVBoxLayout(k_card3)
        kl3.addWidget(QLabel("Tasa de reporte"))
        self.kpi_reports = QLabel("0%")
        self.kpi_reports.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        kl3.addWidget(self.kpi_reports)
        kpi_layout.addWidget(k_card3)

        summary_layout.addLayout(kpi_layout)

        # AI Analysis Box
        ai_box = QWidget()
        ai_box.setProperty("class", "ai-analysis-box")
        ai_layout = QVBoxLayout(ai_box)

        self.ai_text = QLabel("<b>Análisis IA:</b> Cargando datos...")
        self.ai_text.setWordWrap(True)
        ai_layout.addWidget(self.ai_text)

        summary_layout.addWidget(ai_box)
        layout.addWidget(summary_card)

        # --- INTERACCIÓN CON IA ---
        ai_chat_card = QWidget()
        ai_chat_card.setProperty("class", "ai-chat-card")
        chat_layout = QVBoxLayout(ai_chat_card)
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(16)

        chat_header = QHBoxLayout()
        chat_icon = QLabel("🤖")
        chat_icon.setFont(QFont("Segoe UI", 16))
        chat_title = QLabel("Asistente de Inteligencia Artificial")
        chat_title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        chat_header.addWidget(chat_icon)
        chat_header.addWidget(chat_title)
        chat_header.addStretch(1)
        chat_layout.addLayout(chat_header)

        chat_history = QScrollArea()
        chat_history.setWidgetResizable(True)
        chat_history.setStyleSheet("background-color: transparent; border: none;")
        chat_history.setFixedHeight(180)

        chat_content = QWidget()
        history_layout = QVBoxLayout(chat_content)
        history_layout.setSpacing(10)
        history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        initial_msg = QLabel(
            "Hola, soy tu asistente de ciberseguridad. Basado en los datos de la última campaña, "
            "noto que hay vulnerabilidades críticas. ¿Te gustaría que genere "
            "una campaña específica para mitigarlas o tienes otra consulta?"
        )
        initial_msg.setWordWrap(True)
        initial_msg.setProperty("class", "ai-bot-msg")
        history_layout.addWidget(initial_msg)

        chat_history.setWidget(chat_content)
        chat_layout.addWidget(chat_history)

        chat_input_layout = QHBoxLayout()
        chat_input = QLineEdit()
        chat_input.setProperty("class", "ai-input")
        chat_input.setPlaceholderText("Ej. ¿Qué temática recomiendas para la próxima campaña?")

        send_btn = QPushButton("Preguntar")
        send_btn.setProperty("class", "purple-button")

        def _simulate_send() -> None:
            text = chat_input.text().strip()
            if not text:
                return

            user_lbl = QLabel(text)
            user_lbl.setWordWrap(True)
            user_lbl.setProperty("class", "ai-user-msg")
            history_layout.addWidget(user_lbl)

            bot_lbl = QLabel("Generando recomendación analítica... (Simulación de IA)")
            bot_lbl.setWordWrap(True)
            bot_lbl.setProperty("class", "ai-bot-msg")
            history_layout.addWidget(bot_lbl)

            chat_input.clear()

            # Auto scroll to bottom
            scroll_bar = chat_history.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

        send_btn.clicked.connect(_simulate_send)
        chat_input.returnPressed.connect(_simulate_send)

        chat_input_layout.addWidget(chat_input)
        chat_input_layout.addWidget(send_btn)

        chat_layout.addLayout(chat_input_layout)
        layout.addWidget(ai_chat_card)

        layout.addStretch(1)

        scroll.setWidget(page)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        # Cargar datos iniciales
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def load_data(self):
        self.campaign_data = obtener_campanas()
        
        total_campaigns = len(self.campaign_data)
        total_users = sum(c['usuarios'] for c in self.campaign_data)
        total_clicks = sum(c['clicks'] for c in self.campaign_data)
        total_reports = sum(c['reportes'] for c in self.campaign_data)
        
        click_rate = (total_clicks / total_users * 100) if total_users > 0 else 0
        report_rate = (total_reports / total_users * 100) if total_users > 0 else 0

        self.kpi_executed.setText(str(total_campaigns))
        self.kpi_clicks.setText(f"{click_rate:.1f}%")
        self.kpi_reports.setText(f"{report_rate:.1f}%")
        
        if total_campaigns > 0:
            self.ai_text.setText(
                f"<b>Análisis IA:</b> Con base en {total_campaigns} campañas evaluadas, "
                f"la tasa de clics general es del <span style='color:#F59E0B;'>{click_rate:.1f}%</span>. "
                "Se recomienda continuar la concientización en áreas con mayor interacción y mejorar "
                "los filtros preventivos para minimizar la exposición de los usuarios."
            )
        else:
            self.ai_text.setText("<b>Análisis IA:</b> No existen campañas previas. Realice campañas de prueba para obtener información predictiva.")

        self.cmb_filter.blockSignals(True)
        self.cmb_filter.clear()
        self.cmb_filter.addItem("Todas las campañas", -1)
        for c in self.campaign_data:
            self.cmb_filter.addItem(f"{c['name']} ({c['attack_type']})", c['id_campaign'])
        self.cmb_filter.blockSignals(False)
        
        self.update_charts()

    def update_charts(self):
        self.ax1.clear()
        self.ax2.clear()

        # Config ax1
        self.ax1.set_facecolor('none')
        self.ax1.set_title("Resultados por Campaña", color="#E6E8EA", fontsize=12, pad=15, fontweight="bold")
        self.ax1.spines["top"].set_visible(False)
        self.ax1.spines["right"].set_visible(False)
        self.ax1.spines["bottom"].set_color((1, 1, 1, 0.08))
        self.ax1.spines["left"].set_color((1, 1, 1, 0.08))
        self.ax1.grid(axis="y", color="white", linestyle="--", alpha=0.08, zorder=0)

        # Config ax2
        self.ax2.set_facecolor('none')
        self.ax2.set_title("Evolución de Tasa de Clics (%)", color="#E6E8EA", fontsize=12, pad=15, fontweight="bold")
        self.ax2.spines["top"].set_visible(False)
        self.ax2.spines["right"].set_visible(False)
        self.ax2.spines["bottom"].set_color((1, 1, 1, 0.08))
        self.ax2.spines["left"].set_color((1, 1, 1, 0.08))
        self.ax2.grid(color="white", linestyle="--", alpha=0.08, zorder=0)

        selected_id = self.cmb_filter.currentData()
        
        if selected_id == -1 or selected_id is None:
            # Seleccionar las últimas 6 campañas para mostrar si hay demasiadas
            data_to_show = self.campaign_data[-6:]
        else:
            data_to_show = [c for c in self.campaign_data if c['id_campaign'] == selected_id]

        if not data_to_show:
            self.canvas1.draw()
            self.canvas2.draw()
            return
            
        categorias = [(c['name'][:10]+"...") if len(c['name'])>10 else c['name'] for c in data_to_show]
        aperturas = [c['aperturas'] for c in data_to_show]
        clics = [c['clicks'] for c in data_to_show]
        reportes = [c['reportes'] for c in data_to_show]

        x = np.arange(len(categorias))
        width = 0.25

        for i, (data, col) in enumerate(zip([aperturas, clics, reportes], ["#60A5FA", "#F59E0B", "#3FE0C5"])):
            self.ax1.bar(x + (i - 1) * width, data, width, color=col, alpha=0.3, edgecolor="none", linewidth=0, capstyle="round")
            self.ax1.bar(x + (i - 1) * width, data, width * 0.8, color=col, edgecolor="none", zorder=3)
        
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(categorias, color="#AAB4BE", fontsize=8, rotation=25, ha='right')
        self.ax1.tick_params(axis="y", colors="#AAB4BE")

        legend_elements = [
            mpatches.Patch(color="#60A5FA", label="Aperturas"),
            mpatches.Patch(color="#F59E0B", label="Clics"),
            mpatches.Patch(color="#3FE0C5", label="Reportes"),
        ]
        leg = self.ax1.legend(handles=legend_elements, loc="upper left", frameon=False, ncol=3, fontsize=9, bbox_to_anchor=(0, -0.15))
        for text in leg.get_texts():
            text.set_color("#AAB4BE")

        self.fig1.tight_layout()
        self.canvas1.draw()

        # Update Line Chart (Evolution)
        # Mostramos la tendencia historica en cualquier caso, resaltando si hay una seleccionada
        historico_data = self.campaign_data
        meses = []
        valores = []
        
        for c in historico_data:
            if c['start_date']:
                date_lbl = c['start_date'].strftime("%d/%m")
            else:
                date_lbl = "S/F"
            meses.append(date_lbl)
            rate = (c['clicks'] / c['usuarios'] * 100) if c['usuarios'] > 0 else 0
            valores.append(rate)

        if historico_data:
            self.ax2.plot(meses, valores, color="#3FE0C5", alpha=0.3, linewidth=6)
            self.ax2.plot(meses, valores, color="#3FE0C5", marker="o", markersize=6, markerfacecolor="#1F2226", markeredgewidth=2, linewidth=2, zorder=3)
            
            if selected_id != -1 and selected_id is not None:
                # Highlight selected point
                for idx, c in enumerate(historico_data):
                    if c['id_campaign'] == selected_id:
                        self.ax2.plot([meses[idx]], [valores[idx]], marker="o", markersize=10, 
                                      markerfacecolor="#F59E0B", markeredgewidth=2, color="#F59E0B", zorder=4)

            self.ax2.tick_params(axis="x", colors="#AAB4BE", rotation=0, labelsize=9)
            self.ax2.tick_params(axis="y", colors="#AAB4BE")
            max_val = max(valores) if valores else 0
            self.ax2.set_ylim(0, max(max_val + 10, 60))
        else:
            self.ax2.set_xticks([])
            self.ax2.set_yticks([])

        self.fig2.tight_layout()
        self.canvas2.draw()

    def export_to_pdf(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtGui import QPdfWriter, QPainter, QPageSize
        from PyQt6.QtCore import Qt
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", "Reporte_Campanas.pdf", "PDF (*.pdf)")
        if not file_path:
            return
            
        try:
            pixmap = self.grab()
            
            pdf_writer = QPdfWriter(file_path)
            pdf_writer.setResolution(200)
            pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            painter = QPainter(pdf_writer)
            
            rect = painter.viewport()
            size = pixmap.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            QMessageBox.information(self, "Éxito", f"Reporte exportado exitosamente a:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Hubo un error al exportar:\n{e}")
