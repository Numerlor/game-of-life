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
                cell.switch()

        self.changed = self.cells
        pyglet.clock.schedule_interval(self.run_generation, 1/60)

    def run_generation(self, _dt: typing.Optional[float] = None) -> None:
        """Run a single generation."""
        if self.changed:
            cells_to_update = []
            changed = set()
            for cell in self.changed:
                neighbors = list(self.get_cell_neighbors(cell))
                alive_neighbors = sum(cell.is_alive for cell in neighbors) - cell.is_alive
                if cell.is_alive and alive_neighbors not in {2, 3} or not cell.is_alive and alive_neighbors == 3:
                    cells_to_update.append(cell)
                    changed.update(neighbors)

            self.changed = changed
            for cell in cells_to_update:
                cell.switch()


    def get_cell_at(self, col: int, row: int) -> Cell:
        """
        Get the `Cell` object at `col` and row`.

        Valid values are assumed to be passed.
        """
        assert row < self.row_count and col < self.col_count
        return self.cells[col + self.col_count * row]

    def get_cell_neighbors(self, cell: Cell) -> typing.Iterator[Cell]:
        """Yield `cell` and all of its neighbors."""
        cell_index = cell.row*self.row_count+cell.col
        x_offsets = [0]
        if cell.col != 0:
            x_offsets.append(-1)
        if cell.col != self.col_count - 1:
            x_offsets.append(1)

        y_offsets = [0]
        if cell.row != 0:
            y_offsets.append(-self.col_count)
        if cell.row != self.row_count - 1:
            y_offsets.append(self.col_count)

        for x_offset in x_offsets:
            for y_offset in y_offsets:
                index = cell_index + x_offset + y_offset
                yield self.cells[index]
