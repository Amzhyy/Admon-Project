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

        # Card 2
        k_card2 = QWidget()
        k_card2.setProperty("class", "stat-card")
        kl2 = QVBoxLayout(k_card2)
        kl2.addWidget(QLabel("Tasa de clics"))
        self.kpi_clicks = QLabel("0%")
        self.kpi_clicks.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        kl2.addWidget(self.kpi_clicks)
        kpi_layout.addWidget(k_card2)

        summary_layout.addLayout(kpi_layout)

        # AI Analysis Box
        ai_box = QWidget()
        ai_box.setProperty("class", "ai-analysis-box")
        ai_layout = QVBoxLayout(ai_box)

        self.ai_text = QLabel("<b>Análisis IA:</b> Cargando recomendaciones...")
        self.ai_text.setWordWrap(True)
        ai_layout.addWidget(self.ai_text)

        summary_layout.addWidget(ai_box)
        layout.addWidget(summary_card)

        # --- PREDICTOR DE RIESGO IA (REAL) ---
        ai_card = QWidget()
        ai_card.setProperty("class", "card")
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setContentsMargins(20, 20, 20, 20)
        ai_layout.setSpacing(16)

        ai_header = QHBoxLayout()
        ai_header.addWidget(QLabel("🧠 Predictor de Vulnerabilidad IA", font=QFont("Segoe UI", 12, QFont.Weight.DemiBold)))
        ai_header.addStretch()
        ai_layout.addLayout(ai_header)

        # Formulario de Predicción
        form_layout = QHBoxLayout()
        v_form = QVBoxLayout()
        
        v_form.addWidget(QLabel("Seleccionar Usuario:", objectName="SubtitleLabel"))
        self.cmb_ai_user = QComboBox()
        self.cmb_ai_user.setMinimumWidth(250)
        v_form.addWidget(self.cmb_ai_user)

        v_form.addWidget(QLabel("Hipótesis de Ataque:", objectName="SubtitleLabel"))
        self.cmb_ai_attack = QComboBox()
        self.cmb_ai_attack.addItems(["Credenciales", "Urgencia", "Incentivo", "Malware"])
        v_form.addWidget(self.cmb_ai_attack)

        btn_row = QHBoxLayout()
        self.btn_predict = QPushButton("🎯 Calcular Probabilidad")
        self.btn_predict.setProperty("class", "purple-button")
        self.btn_predict.clicked.connect(self.calculate_ia_risk)
        
        self.btn_worst = QPushButton("⚠️ Hallar Más Vulnerable")
        self.btn_worst.setProperty("class", "card-button") # Usar un estilo secundario
        self.btn_worst.setStyleSheet("background-color: #334155; color: white; border-radius: 6px; padding: 10px; font-weight: bold;")
        self.btn_worst.clicked.connect(self.find_most_vulnerable)
        
        btn_row.addWidget(self.btn_predict)
        btn_row.addWidget(self.btn_worst)
        v_form.addLayout(btn_row)

        self.res_ia_lbl = QLabel("Resultado: Pendiente")
        self.res_ia_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.res_ia_lbl.setStyleSheet("color: #94A3B8; margin-top: 10px;")
        v_form.addWidget(self.res_ia_lbl)
        
        self.res_ia_desc = QLabel("Seleccione un usuario para proyectar su nivel de vulnerabilidad.")
        self.res_ia_desc.setWordWrap(True)
        v_form.addWidget(self.res_ia_desc)
        
        form_layout.addLayout(v_form, 1)

        # Gráfico Sigmoide en Tiempo Real
        self.fig3 = Figure(figsize=(4, 3), facecolor='none')
        self.ax3 = self.fig3.add_subplot(111)
        self.canvas3 = FigureCanvas(self.fig3)
        self.canvas3.setStyleSheet("background-color:transparent;")
        self.canvas3.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.canvas3.setFixedHeight(220)
        form_layout.addWidget(self.canvas3, 1)

        ai_layout.addLayout(form_layout)
        layout.addWidget(ai_card)

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
        
        click_rate = (total_clicks / total_users * 100) if total_users > 0 else 0

        self.kpi_executed.setText(str(total_campaigns))
        self.kpi_clicks.setText(f"{click_rate:.1f}%")
        
        # --- Obtención de Recomendación IA Dinámica ---
        from database.campaigns import obtener_tendencia_peligrosa
        cat_peligrosa, riesgo_avg = obtener_tendencia_peligrosa()
        
        if cat_peligrosa:
            self.ai_text.setText(
                f"<b>💡 Recomendación IA:</b> Se ha detectado que la campaña más factible para que los usuarios caigan es "
                f"<span style='color:#F59E0B;'>'{cat_peligrosa}'</span> con un riesgo promedio organizacional del "
                f"<span style='color:#EF4444;'>{riesgo_avg:.1f}%</span>. Se sugiere priorizar esta temática en la siguiente simulación."
            )
        else:
            self.ai_text.setText("<b>Análisis IA:</b> No hay datos suficientes para generar una tendencia. Realice más simulaciones.")

        # Poblar filtros de campañas
        self.cmb_filter.blockSignals(True)
        self.cmb_filter.clear()
        self.cmb_filter.addItem("Todas las campañas", -1)
        for c in self.campaign_data:
            self.cmb_filter.addItem(f"{c['name']} ({c['attack_type']})", c['id_campaign'])
        self.cmb_filter.blockSignals(False)
        
        # Poblar Filtro de Usuarios para IA
        from database.campaigns import obtener_usuarios
        users = obtener_usuarios()
        self.cmb_ai_user.clear()
        for u in users:
            self.cmb_ai_user.addItem(f"{u['name']} ({u['email']})", u['id_user'])
            
        self.update_charts()
        self.update_sigmoid_chart(None, None)

    def calculate_ia_risk(self):
        """Calcula el riesgo para el usuario seleccionado."""
        from database.campaigns import predecir_riesgo_ia
        
        user_id = self.cmb_ai_user.currentData()
        if user_id is None: return
        
        attack_idx = self.cmb_ai_attack.currentIndex() 
        
        prob, clics = predecir_riesgo_ia(user_id, attack_idx)
        
        if prob is None:
            self.res_ia_lbl.setText("Error en IA")
            self.res_ia_desc.setText(f"Detalle: {clics}")
            return

        color = "#10B981" if prob < 30 else "#F59E0B" if prob < 60 else "#EF4444"
        self.res_ia_lbl.setText(f"Probabilidad de Caída: {prob:.1f}%")
        self.res_ia_lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14pt; margin-top: 10px;")
        
        user_name = self.cmb_ai_user.currentText().split(" (")[0]
        at_name = self.cmb_ai_attack.currentText()
        
        self.res_ia_desc.setText(
            f"El usuario <b>{user_name}</b> tiene un historial de <b>{clics} clics en esta categoría</b>. "
            f"Ante un ataque de tipo <b>{at_name}</b>, el modelo estima una vulnerabilidad del {prob:.1f}%."
        )
        
        self.update_sigmoid_chart(prob, clics)

    def find_most_vulnerable(self):
        """Busca al usuario con el porcentaje más alto en la base de datos."""
        from database.campaigns import obtener_usuarios, predecir_riesgo_ia
        users = obtener_usuarios()
        if not users: return
        
        attack_idx = self.cmb_ai_attack.currentIndex()
        max_prob = -1
        best_user = None
        best_clics = 0
        
        for u in users:
            p, c = predecir_riesgo_ia(u['id_user'], attack_idx)
            if p is not None and p > max_prob:
                max_prob = p
                best_user = u
                best_clics = c
                
        if best_user:
            idx = self.cmb_ai_user.findData(best_user['id_user'])
            self.cmb_ai_user.setCurrentIndex(idx)
            
            color = "#EF4444" if max_prob > 50 else "#F59E0B"
            self.res_ia_lbl.setText(f"CRÍTICO: {max_prob:.1f}%")
            self.res_ia_lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14pt; margin-top: 10px;")
            self.res_ia_desc.setText(
                f"🚨 Usuario con mayor riesgo en esta categoría: <b>{best_user['name']}</b>. "
                f"Probabilidad de {max_prob:.1f}% basada en {best_clics} clics previos en '{self.cmb_ai_attack.currentText()}'."
            )
            self.update_sigmoid_chart(max_prob, best_clics)

    def update_sigmoid_chart(self, current_prob, clics):
        self.ax3.clear()
        self.ax3.set_facecolor('none')
        self.ax3.spines["top"].set_visible(False)
        self.ax3.spines["right"].set_visible(False)
        self.ax3.spines["bottom"].set_color((1, 1, 1, 0.1))
        self.ax3.spines["left"].set_color((1, 1, 1, 0.1))
        self.ax3.tick_params(axis="both", colors="#94A3B8", labelsize=7)
        self.ax3.set_title("Curva de Probabilidad IA", color="#E2E8F0", fontsize=9, fontweight="bold")

        # Generar Curva Sigmoide teórica (0 a 15 clics)
        x = np.linspace(0, 15, 100)
        # Una sigmoide simple para representación visual (ajustada para que se vea bien)
        y = 1 / (1 + np.exp(-(0.5 * x - 2)))
        
        self.ax3.plot(x, y, color="#60A5FA", alpha=0.4, linewidth=2)
        
        if current_prob is not None:
            # Dibujar el punto del usuario actual
            # clics es el eje X, prob/100 es el eje Y
            p_y = current_prob / 100
            color = "#10B981" if current_prob < 30 else "#F59E0B" if current_prob < 60 else "#EF4444"
            self.ax3.plot([clics], [p_y], marker="o", markersize=10, markerfacecolor=color, markeredgecolor="white")
            self.ax3.annotate(f"{current_prob:.0f}%", (clics, p_y), textcoords="offset points", xytext=(0,10), 
                             ha='center', color=color, weight='bold', fontsize=8)

        self.canvas3.draw()

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
