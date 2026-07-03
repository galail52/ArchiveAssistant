from dataclasses import dataclass


@dataclass
class ReviewState:
    rotation: int = 0
    has_back: bool = False
    favorite: bool = False
    needs_restore: bool = False
    delete: bool = False

    def reset(self):
        self.rotation = 0
        self.has_back = False
        self.favorite = False
        self.needs_restore = False
        self.delete = False

    def rotate_left(self):
        self.rotation = (self.rotation - 90) % 360

    def rotate_right(self):
        self.rotation = (self.rotation + 90) % 360

    def toggle_back(self):
        self.has_back = not self.has_back

    def toggle_favorite(self):
        self.favorite = not self.favorite

    def toggle_restore(self):
        self.needs_restore = not self.needs_restore

    def toggle_delete(self):
        self.delete = not self.delete

    def as_dict(self):
        return {
            "rotation": self.rotation,
            "back": self.has_back,
            "favorite": self.favorite,
            "restore": self.needs_restore,
            "delete": self.delete,
        }