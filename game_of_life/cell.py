import pyglet
from . import CELL_SIZE


class Cell:
    """
    Represents a cell.

    Either `hide` or `diplsay` must be called on the cell to add it to the batch to be displazed

    `hide` hides the cell bz setting it to black, `show` creates a white cell
    """
    __slots__ = ("x", "y", "batch", "vertex", "is_alive")

    def __init__(self, x: int, y: int, batch: pyglet.graphics.Batch, group):
        self.x = x
        self.y = y
        self.batch = batch
        self.vertex = self.create_vertex(group)
        self.is_alive = False

    def switch(self) -> None:
        """Delete previous vertex, display black cell and set `is_alive` to False."""
        self.is_alive = not self.is_alive
        self.vertex.colors[12:] = (255,)*3*4 if self.is_alive else (0,)*3*4

    def create_vertex(self, group) -> pyglet.graphics.vertexdomain.IndexedVertexList:
        """
        Create and add cell vertex list to batch.

        The resulting graphic is a square of `color` with a grey outline.
        """
        x_base = CELL_SIZE * self.x
        x_offset = x_base + CELL_SIZE

        y_base = CELL_SIZE * self.y
        y_offset = y_base + CELL_SIZE

        grid_size = 0.5

        return self.batch.add_indexed(
            8,
            pyglet.gl.GL_TRIANGLES,
            group,
            [
                0, 1, 2,
                0, 2, 3,

                4, 5, 6,
                4, 6, 7,
            ],
            (
                "v2f/static", (
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
            ("c3B", (180,) * 3 * 4 + (0,) * 3 * 4)

        )

    def __repr__(self):
        return f"<Cell x={self.x}, y={self.y}, alive={self.is_alive}>"
