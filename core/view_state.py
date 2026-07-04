from dataclasses import dataclass


@dataclass
class ViewState:
    zoom_mode: str = "fit"
    zoom_percent: int = 100
    pan_x: int = 0
    pan_y: int = 0
    rotation: int = 0

    @property
    def is_fit(self):
        return self.zoom_mode == "fit"

    @property
    def zoom_scale(self):
        if self.is_fit:
            return None

        return self.zoom_percent / 100

    def reset(self):
        self.zoom_mode = "fit"
        self.zoom_percent = 100
        self.pan_x = 0
        self.pan_y = 0
        self.rotation = 0

    def set_rotation(self, rotation: int):
        self.rotation = rotation % 360
        self.reset_pan()

    def set_fit(self):
        self.zoom_mode = "fit"
        self.zoom_percent = 100
        self.reset_pan()

    def set_zoom_percent(self, percent: int):
        self.zoom_mode = "percent"
        self.zoom_percent = max(10, min(int(percent), 800))
        self.reset_pan()

    def zoom_in(self):
        if self.is_fit:
            self.set_zoom_percent(100)
            return

        self.set_zoom_percent(self.zoom_percent + 25)

    def zoom_out(self):
        if self.is_fit:
            return

        self.set_zoom_percent(self.zoom_percent - 25)

    def pan(self, dx: int, dy: int):
        if self.is_fit:
            return

        self.pan_x += dx
        self.pan_y += dy

    def set_pan(self, x: int, y: int):
        self.pan_x = int(x)
        self.pan_y = int(y)

    def reset_pan(self):
        self.pan_x = 0
        self.pan_y = 0

    def as_dict(self):
        return {
            "zoom_mode": self.zoom_mode,
            "zoom_percent": self.zoom_percent,
            "pan_x": self.pan_x,
            "pan_y": self.pan_y,
            "rotation": self.rotation,
        }

    def zoom_label(self):
        if self.is_fit:
            return "Fit"

        return f"{self.zoom_percent}%"

    def pan_label(self):
        return f"{self.pan_x}, {self.pan_y}"