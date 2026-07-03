class Navigator:
    def __init__(self, image_manager):
        self.images = image_manager

    def move(self, offset: int):
        if self.images.count == 0 or offset == 0:
            return

        self.jump_to(self.images.index + offset)

    def jump_to(self, index: int):
        if self.images.count == 0:
            return

        index = max(0, min(index, self.images.count - 1))
        self.images.jump_to(index)

    def first(self):
        self.jump_to(0)

    def last(self):
        self.jump_to(self.images.count - 1)