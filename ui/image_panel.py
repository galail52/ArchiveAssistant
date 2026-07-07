from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QSizePolicy, QWidget


class ImagePanel(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session
        self.current_pixmap: QPixmap | None = None
        self.current_filename: Path | None = None
        self._transformed_pixmap: QPixmap | None = None
        self._transform_cache_key = None

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )
        self.setFocusPolicy(Qt.StrongFocus)

    def sizeHint(self):
        return QSize(900, 600)

    def minimumSizeHint(self):
        return QSize(300, 220)

    def load_image(self, filename: Path):
        if self.current_filename == filename:
            return False

        self.current_filename = filename
        self.current_pixmap = QPixmap(str(filename))
        self.clear_transform_cache()
        self.update()
        return True

    def clear_image(self):
        if self.current_filename is None and self.current_pixmap is None:
            return False

        self.current_filename = None
        self.current_pixmap = None
        self.clear_transform_cache()
        self.update()
        return True

    def clear_transform_cache(self):
        self._transformed_pixmap = None
        self._transform_cache_key = None

    def transform_cache_key(self):
        view = self.session.view_state

        return (
            self.current_filename,
            self.size().width(),
            self.size().height(),
            view.rotation,
            view.is_fit,
            view.zoom_scale,
        )

    def transformed_pixmap(self):
        if self.current_pixmap is None:
            return None

        view = self.session.view_state
        cache_key = self.transform_cache_key()

        if (
            self._transformed_pixmap is not None
            and self._transform_cache_key == cache_key
        ):
            return self._transformed_pixmap

        pixmap = self.current_pixmap.transformed(
            QTransform().rotate(view.rotation),
            Qt.SmoothTransformation,
        )

        if view.is_fit:
            transformed = pixmap.scaled(
                self.size() * 0.96,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        else:
            transformed = pixmap.scaled(
                int(pixmap.width() * view.zoom_scale),
                int(pixmap.height() * view.zoom_scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

        self._transformed_pixmap = transformed
        self._transform_cache_key = cache_key
        return transformed

    def clamp_pan(self):
        pixmap = self.transformed_pixmap()
        self.clamp_pan_for_pixmap(pixmap)

    def clamp_pan_for_pixmap(self, pixmap):
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

        self.clamp_pan_for_pixmap(pixmap)

        view = self.session.view_state

        x = (self.width() - pixmap.width()) // 2 - view.pan_x
        y = (self.height() - pixmap.height()) // 2 - view.pan_y

        painter.drawPixmap(x, y, pixmap)

    def resizeEvent(self, event):
        self.clamp_pan()
        self.clear_transform_cache()
        self.update()
        super().resizeEvent(event)
