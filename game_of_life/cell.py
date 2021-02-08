import pyglet


class Cell:
    """
    Represents a cell.

    Holds the cell's rect and manages its alive state.
    """
    __slots__ = ("rect", "is_alive")

    def __init__(self, cell_size, x: int, y: int, batch: pyglet.graphics.Batch, group):
        self.rect = pyglet.shapes.Rectangle(x*cell_size, y*cell_size, cell_size, cell_size, (0,)*3, batch, group=group)
        self.is_alive = False

    def switch(self) -> None:
        """Switch current color and is_alive to opposite value."""
        self.is_alive = not self.is_alive
        self.rect.color = (255,)*3 if self.is_alive else (0,)*3

    @property
    def delete(self):
        return self.rect.delete

    @property
    def x(self):
        return self.rect.x // self.rect.width

    @property
    def y(self):
        return self.rect.y // self.rect.height

    def move(self, x, y):
        self.rect.x = x * self.rect.width
        self.rect.y = y * self.rect.width

    def __repr__(self):
        return f"<Cell x={self.x}, y={self.y}, alive={self.is_alive}>"
