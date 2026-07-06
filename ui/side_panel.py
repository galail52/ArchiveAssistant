from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QGridLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.status_card import StatusCard


class SidePanel(QWidget):
    def __init__(self, keyboard_help=""):
        super().__init__()

        self.keyboard_help = keyboard_help

        self.zoom = StatusCard("🔎 Zoom")
        self.pan = StatusCard("↔ Pan")
        self.rotation = StatusCard("↻ Orientation")
        self.back = StatusCard("📄 Back")
        self.favorite = StatusCard("⭐ Favorite")
        self.restore = StatusCard("🛠 Restore")
        self.research = StatusCard("🔍 Research")
        self.delete = StatusCard("🗑 Delete")

        self.build_ui()
        self.update_status()

    def build_ui(self):
        self.setFixedWidth(390)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(6)

        title = QLabel("Review")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:18pt;
            font-weight:bold;
        """)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(7)

        for index, card in enumerate(self.status_cards):
            card.setMinimumHeight(48)
            card.setMaximumHeight(54)
            grid.addWidget(card, index // 2, index % 2)

        layout.addLayout(grid)

        keyboard_title = QLabel("Keyboard")
        keyboard_title.setAlignment(Qt.AlignCenter)
        keyboard_title.setStyleSheet("""
            font-size:13pt;
            font-weight:bold;
            margin-top:5px;
        """)
        layout.addWidget(keyboard_title)

        keyboard = QLabel(self.keyboard_help)
        keyboard.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        keyboard.setStyleSheet("""
            font-family:Consolas, monospace;
            font-size:9.5pt;
            line-height:100%;
            color:#d0d0d0;
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(keyboard)
        scroll.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        layout.addWidget(scroll, 1)
        self.setLayout(layout)

    @property
    def status_cards(self):
        return [
            self.zoom,
            self.pan,
            self.rotation,
            self.back,
            self.favorite,
            self.restore,
            self.research,
            self.delete,
        ]

    def rotation_label(self, rotation):
        return {
            0: "Normal",
            90: "Right",
            180: "Upside Down",
            270: "Left",
        }.get(rotation, str(rotation))

    def update_status(
        self,
        rotation=0,
        back=False,
        favorite=False,
        restore=False,
        research=False,
        delete=False,
        view_state=None,
    ):
        if view_state is None:
            zoom_label = "Fit"
            pan_label = "0, 0"
            is_zoomed = False
            is_panned = False
        else:
            zoom_label = view_state.zoom_label()
            pan_label = view_state.pan_label()
            is_zoomed = not view_state.is_fit
            is_panned = view_state.pan_x != 0 or view_state.pan_y != 0
            rotation = view_state.rotation

        self.zoom.set_value(zoom_label, is_zoomed, "#7fc8ff")
        self.pan.set_value(pan_label, is_panned, "#7fc8ff")
        self.rotation.set_value(
            self.rotation_label(rotation),
            rotation != 0,
            "#7fc8ff",
        )
        self.back.set_value("YES" if back else "NO", back, "#55ff55")
        self.favorite.set_value("YES" if favorite else "NO", favorite, "#ffd54a")
        self.restore.set_value("YES" if restore else "NO", restore, "#ffb347")
        self.research.set_value("YES" if research else "NO", research, "#b388ff")
        self.delete.set_value("YES" if delete else "NO", delete, "#ff6666")