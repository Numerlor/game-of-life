import itertools
import random
import typing

import pyglet

from game_of_life import Cell


class GridManager:
    """Manages grid of `Cell`s and simulates the game of life with them."""

    def __init__(self, width: int, height: int, cell_size: int):
        self.batcher = pyglet.graphics.Batch()
        self.cells: list[Cell] = []
        self.cell_size = cell_size
        self.row_count = height // cell_size
        self.col_count = width // cell_size

    def create(self) -> None:
        """Init cell objects for whole grid and populate roughly third of grid."""
        for col, row in itertools.product(range(self.col_count), range(self.row_count)):
            cell = Cell(self.cell_size, col, row, self.batcher)
            self.cells.append(cell)
            if random.random() < .33:
                cell.show()
            else:
                cell.hide()
        pyglet.clock.schedule_interval(self.run_generation, 0.075)

    def run_generation(self, _dt: typing.Optional[float] = None) -> None:
        """Run a single generation."""
        cells_to_kill = []
        cells_to_create = []
        for index, cell in enumerate(self.cells):
            alive_neighbors = self.get_cell_neighbors(index, cell.col, cell.row)
            if cell.is_alive:
                if alive_neighbors not in {2, 3}:
                    cells_to_kill.append(cell)
            else:
                if alive_neighbors == 3:
                    cells_to_create.append(cell)

        for cell in cells_to_kill:
            cell.hide()
        for cell in cells_to_create:
            cell.show()

    def get_cell_at(self, col: int, row: int) -> Cell:
        """
        Get the `Cell` object at `col` and row`.

        Valid values are assumed to be passed.
        """
        assert row < self.row_count and col < self.col_count
        return self.cells[col + self.col_count * row]

    def get_cell_neighbors(self, cell_index: int, cell_x: int, cell_y: int) -> int:
        """
        Get count of alive neighbors of cell at cell_index.

        `cell_x` and `cell_y` are used to determine whether the cell is at the edge.
        """
        alive = 0
        x_offsets = [0]
        if cell_x != 0:
            x_offsets.append(-1)
        if cell_x != self.col_count - 1:
            x_offsets.append(1)

        y_offsets = [0]
        if cell_y != 0:
            y_offsets.append(-self.col_count)
        if cell_y != self.row_count - 1:
            y_offsets.append(self.col_count)

        for x_offset in x_offsets:
            for y_offset in y_offsets:
                index = cell_index + x_offset + y_offset
                if index != cell_index:
                    alive += self.cells[index].is_alive
        return alive
