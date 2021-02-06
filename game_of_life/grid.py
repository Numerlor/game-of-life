import itertools
import random
import typing

import pyglet

from game_of_life import CELL_SIZE, WIDTH, HEIGHT, Cell


class GridManager:
    """Manages grid of `Cell`s and simulates the game of life with them."""

    def __init__(self):
        self.batcher = pyglet.graphics.Batch()
        self.cells: list[Cell] = []
        self.changed: typing.Union[list[Cell], set[Cell]] = self.cells
        self.row_count = HEIGHT // CELL_SIZE
        self.col_count = WIDTH // CELL_SIZE

    def create(self) -> None:
        """Init cell objects for whole grid and populate roughly third of grid."""
        for col, row in itertools.product(range(self.col_count), range(self.row_count)):
            cell = Cell(col, row, self.batcher)
            self.cells.append(cell)
            if random.random() < .33:
                cell.switch()

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

    def switch_cell_at(self, col, row):
        cell = self.get_cell_at(col, row)
        self.changed.update(self.get_cell_neighbors(cell))
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
        for col in (
                (cell.col-1) % self.col_count,
                cell.col,
                (cell.col+1) % self.col_count,
        ):
            for row in (
                    (cell.row-1) % self.row_count,
                    cell.row,
                    (cell.row+1) % self.row_count,
            ):
                yield self.cells[row*self.row_count+col]
