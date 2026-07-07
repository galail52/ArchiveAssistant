from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QGridLayout,
    QVBoxLayout,
    QWidget,
)
from pathlib import Path

from core.metadata_summary import metadata_summary_lines
from ui.widgets.status_card import StatusCard


class SidePanel(QWidget):
    def __init__(self, review_actions=None):
        super().__init__()

        self.review_actions = review_actions or {}

        self.zoom = StatusCard(" Zoom")
        self.pan = StatusCard("↔ Pan")
        self.rotation = StatusCard("↻ Orientation")
        self.back = StatusCard(" Back")
        self.favorite = StatusCard("⭐ Favorite")
        self.restore = StatusCard(" Restore")
        self.research = StatusCard(" Research")
        self.delete = StatusCard(" Delete")

        self.metadata_summary = QLabel("No metadata")
        self._metadata_summary_text = "No metadata"
        self.metadata_summary.setWordWrap(True)
        self.metadata_summary.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.relationship_summary = QLabel("No relationships")
        self._relationship_summary_text = "No relationships"
        self.relationship_summary.setWordWrap(True)
        self.relationship_summary.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.build_ui()
        self.connect_review_actions()
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

        metadata_title = QLabel("Metadata")
        metadata_title.setAlignment(Qt.AlignCenter)
        metadata_title.setStyleSheet("""
            font-size:13pt;
            font-weight:bold;
            margin-top:5px;
        """)
        layout.addWidget(metadata_title)

        self.metadata_summary.setStyleSheet("""
            font-size:10pt;
            color:#d0d0d0;
            background-color:#303030;
            border:1px solid #4a4a4a;
            border-radius:8px;
            padding:8px;
        """)
        layout.addWidget(self.metadata_summary)

        relationship_title = QLabel("Relationships")
        relationship_title.setAlignment(Qt.AlignCenter)
        relationship_title.setStyleSheet("""
            font-size:13pt;
            font-weight:bold;
            margin-top:5px;
        """)
        layout.addWidget(relationship_title)

        self.relationship_summary.setStyleSheet("""
            font-size:10pt;
            color:#d0d0d0;
            background-color:#303030;
            border:1px solid #4a4a4a;
            border-radius:8px;
            padding:8px;
        """)
        layout.addWidget(self.relationship_summary)

        layout.addStretch(1)

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

    def connect_review_actions(self):
        card_actions = {
            self.back: "back",
            self.favorite: "favorite",
            self.restore: "restore",
            self.research: "research",
            self.delete: "delete",
        }

        for card, action_name in card_actions.items():
            callback = self.review_actions.get(action_name)

            if callback is None:
                continue

            card.set_clickable(True)
            card.clicked.connect(callback)

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
        metadata=None,
        relationships=None,
        current_image_id=None,
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

        self.update_metadata_summary(metadata)
        self.update_relationship_summary(relationships, current_image_id)

    def update_metadata_summary(self, metadata=None):
        rows = metadata_summary_lines(metadata)
        text = "\n".join(rows) if rows else "No metadata"

        if text == self._metadata_summary_text:
            return

        self._metadata_summary_text = text
        self.metadata_summary.setText(text)

    def update_relationship_summary(self, relationships=None, current_image_id=None):
        rows = []
        current_image_id = str(current_image_id or "")

        for relationship in relationships or []:
            related = relationship.target_image_id

            if relationship.target_image_id == current_image_id:
                related = relationship.source_image_id

            relationship_label = relationship.relationship_type.value.replace(
                "_",
                " ",
            ).title()
            rows.append(f"{relationship_label}: {Path(related).name}")

        text = "\n".join(rows) if rows else "No relationships"

        if text == self._relationship_summary_text:
            return

        self._relationship_summary_text = text
        self.relationship_summary.setText(text)
