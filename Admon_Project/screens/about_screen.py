from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QGridLayout,
    QPushButton,
)


class AboutScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # self.setObjectName("content-shell")
        # self.setProperty("class", "content-shell")

        # Usamos un área con scroll para poder ver todos los integrantes
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(18)

        # Tarjeta introductoria
        intro_inner = QWidget()
        intro_layout = QVBoxLayout(intro_inner)
        intro_layout.setSpacing(10)

        title = QLabel("Sobre nosotros")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))

        body = QLabel(
            "Somos un equipo multidisciplinario enfocado en ciberseguridad y simulación de ataques "
            "de phishing. Combinamos experiencia técnica y visión operativa para construir "
            "herramientas que eleven la cultura de seguridad dentro de las organizaciones."
        )
        body.setWordWrap(True)
        body.setObjectName("SubtitleLabel")

        intro_layout.addWidget(title)
        intro_layout.addWidget(body)

        intro_card = self._wrap_card(intro_inner)

        # Rejilla de integrantes (9 miembros, 3 x 3)
        team_inner = QWidget()
        team_layout = QGridLayout(team_inner)
        team_layout.setSpacing(18)

        team_members = [
            ("Integrante 1", "Rol principal"),
            ("Integrante 2", "Rol principal"),
            ("Integrante 3", "Rol principal"),
            ("Integrante 4", "Rol principal"),
            ("Integrante 5", "Rol principal"),
            ("Integrante 6", "Rol principal"),
            ("Integrante 7", "Rol principal"),
            ("Integrante 8", "Rol principal"),
            ("Integrante 9", "Rol principal"),
        ]

        for index, (name, role) in enumerate(team_members):
            row = index // 3
            col = index % 3

            member_card = QWidget()
            member_card.setProperty("class", "card")
            member_layout = QVBoxLayout(member_card)
            member_layout.setContentsMargins(14, 16, 14, 16)
            member_layout.setSpacing(8)
            member_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            avatar = QLabel()
            avatar.setProperty("class", "team-avatar")
            avatar.setFixedSize(80, 80)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setText("IT")

            name_label = QLabel(name)
            name_label.setObjectName("TeamNameLabel")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            role_label = QLabel(role)
            role_label.setObjectName("TeamRoleLabel")
            role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Fila de iconos de redes sociales
            social_row = QWidget()
            social_row.setProperty("class", "social-row")
            from PyQt6.QtWidgets import QHBoxLayout

            social_layout = QHBoxLayout(social_row)
            social_layout.setContentsMargins(0, 4, 0, 0)
            social_layout.setSpacing(6)
            social_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            btn_linkedin = QPushButton("🔗")
            btn_github = QPushButton("💻")
            btn_x = QPushButton("𝕏")

            social_layout.addWidget(btn_linkedin)
            social_layout.addWidget(btn_github)
            social_layout.addWidget(btn_x)

            # Texto colapsable tipo biografía
            bio = QLabel(
                "Breve descripción del integrante, su experiencia en seguridad y "
                "participación en campañas de simulación."
            )
            bio.setWordWrap(True)
            bio.setProperty("class", "team-bio")
            bio.setVisible(False)

            expand_btn = QPushButton("Ver más ▾")
            expand_btn.setProperty("class", "team-expand")

            def make_toggle(label: QLabel, button: QPushButton) -> None:
                def _toggle() -> None:
                    visible = not label.isVisible()
                    label.setVisible(visible)
                    button.setText("Ver menos ▴" if visible else "Ver más ▾")

                button.clicked.connect(_toggle)

            make_toggle(bio, expand_btn)

            member_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)
            member_layout.addSpacing(4)
            member_layout.addWidget(name_label)
            member_layout.addWidget(role_label)
            member_layout.addWidget(social_row)
            member_layout.addWidget(bio)
            member_layout.addWidget(expand_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

            team_layout.addWidget(member_card, row, col)

        team_card = self._wrap_card(team_inner)

        layout.addWidget(intro_card)
        layout.addWidget(team_card)
        layout.addStretch(1)

        scroll.setWidget(content)

        scroll_layout = QVBoxLayout(self)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(scroll)

    def _wrap_card(self, inner: QWidget) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(inner)
        return card

