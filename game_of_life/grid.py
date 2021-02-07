import itertools
import random
import typing
import functools

import pyglet

from game_of_life import CELL_SIZE, SIMULATION_TICK, Cell


class GridManager:
    """Manages grid of `Cell`s and simulates the game of life with them."""

    def __init__(self, start_grid, height, width):
        self.batcher = pyglet.graphics.Batch()
        self.cells: list[Cell] = []
        self.changed: typing.Union[list[Cell], set[Cell]] = self.cells
        self.row_count = height // CELL_SIZE
        self.col_count = width // CELL_SIZE

        self.create(start_grid)

    def create(self, start_grid: typing.Optional[list]) -> None:
        """Init cell objects for whole grid and populate roughly third of grid."""
        if start_grid is None:
            for y, x in itertools.product(range(self.row_count), range(self.col_count)):
                cell = Cell(x, y, self.batcher)
                self.cells.append(cell)
                if random.random() < .33:
                    cell.switch()
        else:
            for y, row in enumerate(start_grid):
                for x, state in enumerate(row):
                    cell = Cell(x, y, self.batcher)
                    self.cells.append(cell)
                    if state:
                        cell.switch()

        pyglet.clock.schedule_interval(self.run_generation, SIMULATION_TICK)

    def run_generation(self, _dt: typing.Optional[float] = None) -> None:
        """Run a single generation."""
        if self.changed:
            cells_to_update = []
            changed = set()
            for cell in self.changed:
                neighbors = self.get_cell_neighbors(cell)
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

    def get_cell_at(self, x: int, y: int) -> Cell:
        """
        Get the `Cell` object at `x` and y`.

        Valid values are assumed to be passed.
        """
        return self.cells[y*self.col_count+x]

    def get_cell_indices(self, x, y):
        return (
            ((y - 1) % self.row_count) * self.col_count + (x - 1) % self.col_count,
            ((y - 1) % self.row_count) * self.col_count + x,
            ((y - 1) % self.row_count) * self.col_count + (x + 1) % self.col_count,

            y * self.col_count + (x - 1) % self.col_count,
            y * self.col_count + x,
            y * self.col_count + (x + 1) % self.col_count,

            ((y + 1) % self.row_count) * self.col_count + (x - 1) % self.col_count,
            ((y + 1) % self.row_count) * self.col_count + x,
            ((y + 1) % self.row_count) * self.col_count + (x + 1) % self.col_count,

        )

    @functools.cache
    def get_cell_neighbors(self, cell: Cell) -> typing.Iterator[Cell]:
        """Yield `cell` and all of its neighbors."""
        return tuple(self.cells[index] for index in self.get_cell_indices(cell.x, cell.y))
