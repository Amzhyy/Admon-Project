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


class StatisticsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # self.setProperty("class", "content-shell")

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

        export_btn = QPushButton("↓ Exportar PDF")
        export_btn.setProperty("class", "purple-button")
        header_layout.addWidget(export_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header_layout)

        # --- FILTRO ---
        filter_card = QWidget()
        filter_card.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_lbl = QLabel("▽ Filtrar por campaña:")
        filter_lbl.setObjectName("SubtitleLabel")
        cmb_filter = QComboBox()
        cmb_filter.addItems(["Todas las campañas", "Reset Password", "Nómina urgente", "Premio encuesta"])
        cmb_filter.setFixedWidth(200)
        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(cmb_filter)
        filter_layout.addStretch(1)
        layout.addWidget(filter_card)

        # --- GRÁFICOS MATPLOTLIB NEON ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)

        # Gráfico 1: Barras Agrupadas
        chart1_card = QWidget()
        chart1_card.setProperty("class", "card")
        chart1_layout = QVBoxLayout(chart1_card)

        fig1 = Figure(figsize=(5, 4), facecolor='none')
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor('none')

        categorias = ["Reset Password", "Nómina urgente", "Premio encuesta"]
        aperturas = [32, 18, 45]
        clics = [18, 7, 25]
        reportes = [5, 2, 9]

        x = np.arange(len(categorias))
        width = 0.25

        # Efecto glow de barras (dibujar rectángulos opacos un poco más anchos de fondo)
        for i, (data, col) in enumerate(zip([aperturas, clics, reportes], ["#60A5FA", "#F59E0B", "#3FE0C5"])):
            ax1.bar(x + (i - 1) * width, data, width, color=col, alpha=0.3, edgecolor="none", linewidth=0, capstyle="round")
            ax1.bar(x + (i - 1) * width, data, width * 0.8, color=col, edgecolor="none", zorder=3)

        ax1.set_title("Resultados por Campaña", color="#E6E8EA", fontsize=12, pad=15, fontweight="bold")
        ax1.set_xticks(x, categorias, color="#AAB4BE", fontsize=9)
        ax1.tick_params(axis="y", colors="#AAB4BE")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.spines["bottom"].set_color((1, 1, 1, 0.08))
        ax1.spines["left"].set_color((1, 1, 1, 0.08))
        ax1.grid(axis="y", color="white", linestyle="--", alpha=0.08, zorder=0)

        # Leyenda personalizada integrada en la gráfica
        legend_elements = [
            mpatches.Patch(color="#60A5FA", label="Aperturas"),
            mpatches.Patch(color="#F59E0B", label="Clics"),
            mpatches.Patch(color="#3FE0C5", label="Reportes"),
        ]
        leg = ax1.legend(
            handles=legend_elements,
            loc="upper left",
            frameon=False,
            ncol=3,
            fontsize=9,
            bbox_to_anchor=(0, -0.15),
        )
        for text in leg.get_texts():
            text.set_color("#AAB4BE")

        fig1.tight_layout()
        canvas1 = FigureCanvas(fig1)
        canvas1.setStyleSheet("background-color:transparent;")
        canvas1.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        canvas1.setMinimumHeight(250)

        chart1_layout.addWidget(canvas1)
        charts_layout.addWidget(chart1_card, 1)

        # Gráfico 2: Líneas (Tendencia)
        chart2_card = QWidget()
        chart2_card.setProperty("class", "card")
        chart2_layout = QVBoxLayout(chart2_card)

        fig2 = Figure(figsize=(5, 4), facecolor='none')
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor('none')

        meses = ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar"]
        valores = [52, 48, 45, 42, 33, 28]

        # Glow effect (línea gruesa transparente debajo + línea finita brillante arriba)
        ax2.plot(meses, valores, color="#3FE0C5", alpha=0.3, linewidth=6)
        ax2.plot(
            meses,
            valores,
            color="#3FE0C5",
            marker="o",
            markersize=6,
            markerfacecolor="#1F2226",
            markeredgewidth=2,
            linewidth=2,
            zorder=3,
        )

        ax2.set_title("Evolución de Tasa de Clics (%)", color="#E6E8EA", fontsize=12, pad=15, fontweight="bold")
        ax2.tick_params(axis="x", colors="#AAB4BE")
        ax2.tick_params(axis="y", colors="#AAB4BE")
        ax2.set_ylim(0, 60)

        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.spines["bottom"].set_color((1, 1, 1, 0.08))
        ax2.spines["left"].set_color((1, 1, 1, 0.08))
        ax2.grid(color="white", linestyle="--", alpha=0.08, zorder=0)

        fig2.tight_layout()
        canvas2 = FigureCanvas(fig2)
        canvas2.setStyleSheet("background-color:transparent;")
        canvas2.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        canvas2.setMinimumHeight(250)

        chart2_layout.addWidget(canvas2)
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

        kpis = [
            ("Campañas ejecutadas", "4", ""),
            ("Reducción de clics", "-24%", "vs. periodo anterior (color:#3FE0C5)"),
            ("Tasa de reporte", "23%", "mejora del 8% (color:#3FE0C5)"),
        ]

        for title_str, val_str, sub_str in kpis:
            k_card = QWidget()
            k_card.setProperty("class", "stat-card")
            kl = QVBoxLayout(k_card)

            t = QLabel(title_str)

            v = QLabel(val_str)
            v.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

            kl.addWidget(t)
            kl.addWidget(v)
            if sub_str:
                s = QLabel(sub_str.replace("(color:#3FE0C5)", ""))
                kl.addWidget(s)

            kpi_layout.addWidget(k_card)

        summary_layout.addLayout(kpi_layout)

        # AI Analysis Box
        ai_box = QWidget()
        ai_box.setProperty("class", "ai-analysis-box")
        ai_layout = QVBoxLayout(ai_box)

        ai_text = QLabel(
            "<b>Análisis IA:</b> Durante el periodo evaluado (Octubre 2025 - Marzo 2026), se observa una "
            "<span style='color:#10B981;'>tendencia positiva</span> en la reducción de interacciones con correos de phishing simulados. "
            "La tasa de clics disminuyó de 52% a 28%, representando una mejora del 46%. Sin embargo, el "
            "<span style='color:#F59E0B;'>departamento de Contabilidad</span> continúa siendo el área de mayor riesgo con un score promedio de 89/100. "
            "Se recomienda intensificar las campañas de awareness en esta área y considerar la implementación obligatoria de MFA para todos los usuarios. "
            'Las campañas de tipo "Credenciales" muestran la mayor efectividad en detección de vulnerabilidades, seguidas por las de tipo "Urgencia".'
        )
        ai_text.setWordWrap(True)
        ai_layout.addWidget(ai_text)

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
            "noto que Contabilidad tiene una vulnerabilidad del 60%. ¿Te gustaría que genere "
            "una campaña específica para ellos o tienes otra consulta?"
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

