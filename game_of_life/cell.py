import pyglet


class Cell:
    """
    Represents a cell.

    Either `hide` or `diplsay` must be called on the cell to add it to the batch to be displazed

    `hide` hides the cell bz setting it to black, `show` creates a white cell
    """

    __slots__ = ("size", "row", "col", "batch", "vertex", "is_alive")

    def __init__(self, size: int, row: int, col: int, batch: pyglet.graphics.Batch):
        self.size = size
        self.row = row
        self.col = col
        self.batch = batch
        self.vertex = None
        self.is_alive = False

    def hide(self) -> None:
        """Delete previous vertex, display black cell and set `is_alive` to False."""
        if self.vertex is not None:
            self.vertex.delete()
        self.display(0)
        self.is_alive = False

    def show(self) -> None:
        """Delete previous vertex, display white cell and set `is_alive` to True."""
        if self.vertex is not None:
            self.vertex.delete()
        self.display(255)
        self.is_alive = True

    def display(self, color: int) -> None:
        """
        Create and add cell vertex list to batch.

        The resulting graphic is a square of `color` with a grey outline.
        """
        x_base = self.size * self.col
        x_offset = x_base + self.size

        y_base = self.size * self.row
        y_offset = y_base + self.size

        grid_size = 1

        self.vertex = self.batch.add_indexed(
            8,
            pyglet.gl.GL_TRIANGLES,
            None,
            [
                0, 1, 2,
                0, 2, 3,

                4, 5, 6,
                4, 6, 7,
            ],
            (
                "v2i", (
                    x_base, y_base,
                    x_offset, y_base,
                    x_offset, y_offset,
                    x_base, y_offset,

                    x_base + grid_size, y_base + grid_size,
                    x_offset - grid_size, y_base + grid_size,
                    x_offset - grid_size, y_offset - grid_size,
                    x_base + grid_size, y_offset - grid_size,
                )
            ),
            ("c3B", (180,) * 3 * 4 + (color,) * 3 * 4)

        )

    def __repr__(self):
        return f"<Cell row={self.row}, column={self.col}, alive={self.is_alive}>"
