from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QSizePolicy, QWidget


class ImagePanel(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session
        self.current_pixmap: QPixmap | None = None

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

    def sizeHint(self):
        return QSize(900, 600)

    def minimumSizeHint(self):
        return QSize(300, 220)

    def load_image(self, filename: Path):
        self.current_pixmap = QPixmap(str(filename))
        self.update()

    def transformed_pixmap(self):
        if self.current_pixmap is None:
            return None

        view = self.session.view_state

        pixmap = self.current_pixmap.transformed(
            QTransform().rotate(view.rotation),
            Qt.SmoothTransformation,
        )

        if view.is_fit:
            return pixmap.scaled(
                self.size() * 0.96,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

        return pixmap.scaled(
            int(pixmap.width() * view.zoom_scale),
            int(pixmap.height() * view.zoom_scale),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

    def clamp_pan(self):
        pixmap = self.transformed_pixmap()
        view = self.session.view_state

        if pixmap is None:
            view.reset_pan()
            return

        max_x = max(0, (pixmap.width() - self.width()) // 2)
        max_y = max(0, (pixmap.height() - self.height()) // 2)

        view.set_pan(
            max(-max_x, min(view.pan_x, max_x)),
            max(-max_y, min(view.pan_y, max_y)),
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1f1f1f"))

        pixmap = self.transformed_pixmap()

        if pixmap is None:
            return

        self.clamp_pan()

        view = self.session.view_state

        x = (self.width() - pixmap.width()) // 2 - view.pan_x
        y = (self.height() - pixmap.height()) // 2 - view.pan_y

        painter.drawPixmap(x, y, pixmap)

    def resizeEvent(self, event):
        self.clamp_pan()
        self.update()
        super().resizeEvent(event)