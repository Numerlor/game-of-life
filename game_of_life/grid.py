# This file is part of Game-of-life.
# Copyright (C) 2021  Numerlor

import functools
import itertools
import random
import typing

import pyglet

from game_of_life import Cell, FOREGROUND, SIMULATION_TICK


class Grid:
    """Grid of `Cell`s."""

    def __init__(
            self,
            x: int,
            y: int,
            cell_size: int,
            start_grid: typing.Optional[list[list[int]]],
            *,
            height: typing.Optional[int] = None,
            width: typing.Optional[int] = None,
            batch: pyglet.graphics.Batch,
            group: pyglet.graphics.Group,
    ):
        self.cells: list[Cell] = []
        self.cell_size = cell_size
        if start_grid:
            self.row_count = len(start_grid)
            self.col_count = len(start_grid[0])
        else:
            self.row_count = height // cell_size
            self.col_count = width // cell_size
        self.x = x // cell_size
        self.y = y // cell_size
        self.grid_lines = []
        self.create(start_grid, batch, group)

    def create(self, start_grid: list[list[int]], batch: pyglet.graphics.Batch, group: pyglet.graphics.Group) -> None:
        """
        Init cell objects for whole grid.

        If a starting grid is not passed, a third of the grid is populated randomly.
        """
        if start_grid is None:
            for y, x in itertools.product(range(self.row_count), range(self.col_count)):
                cell = Cell(self.cell_size, self.x + x, self.y + y, batch, group)
                self.cells.append(cell)
                if random.random() < .33:
                    cell.switch()
        else:
            for y, row in enumerate(start_grid):
                for x, state in enumerate(row):
                    cell = Cell(self.cell_size, self.x + x, self.y + y, batch, group)
                    self.cells.append(cell)
                    if state:
                        cell.switch()

    def create_grid(self, batch) -> None:
        """Create grid from lines."""
        pyglet.gl.glLineWidth(1)
        for y in range(self.row_count + 1):
            self.grid_lines.append(
                batch.add(
                    2, pyglet.gl.GL_LINES, FOREGROUND,
                    (
                        "v2i/static",
                        (
                            self.x * self.cell_size, (self.y + y) * self.cell_size,
                            (self.x + self.col_count) * self.cell_size, (self.y + y) * self.cell_size,
                        ),
                    ),
                    ("c3B", (180,) * 3 * 2)
                )
            )
        for x in range(self.col_count + 1):
            self.grid_lines.append(
                batch.add(
                    2, pyglet.gl.GL_LINES, FOREGROUND,
                    (
                        "v2i/static",
                        (
                            (self.x + x) * self.cell_size, self.y * self.cell_size,
                            (self.x + x) * self.cell_size, (self.y + self.row_count) * self.cell_size,
                        )
                    ),
                    ("c3B", (180,) * 3 * 2)

                )
            )

    def move_grid(self, x_target: int, y_target: int) -> None:
        """Move self to x_target, y_target."""
        x_dist = x_target - self.x
        y_dist = y_target - self.y
        for cell in self.cells:
            cell.move(cell.x + x_dist, cell.y + y_dist)
        self.x = x_target
        self.y = y_target

    def get_cell_at(self, x: int, y: int) -> Cell:
        """
        Get the `Cell` object at `x` and y`.

        Valid values are assumed to be passed.
        """
        x = x - self.x
        y = y - self.y
        return self.cells[y * self.col_count + x]

    def get_neighbor_indices(self, x: int, y: int) -> typing.Tuple[int, ...]:
        """Get indices of all cells around x,y."""
        x = x - self.x
        y = y - self.y
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


class GameOfLife:
    """Manages grid of `Cell`s and simulates the game of life with them."""

    def __init__(
            self,
            x: int,
            y: int,
            start_grid: list[list[int]],
            cell_size: int,
            *,
            height: typing.Optional[int] = None,
            width: typing.Optional[int] = None,
            batch: pyglet.graphics.Batch,
            group: pyglet.graphics.Group,
            tick: float = SIMULATION_TICK,
    ):
        self.grid = Grid(x, y, cell_size, start_grid, height=height, width=width, batch=batch, group=group)
        self.grid.create_grid(batch)
        self.changed: typing.Union[set[Cell]] = set(self.grid.cells)
        self.running = True
        pyglet.clock.schedule_interval(self.run_generation, tick)

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

    def switch_cell_at(self, col: int, row: int) -> None:
        """Switch the state of the cell at col, row."""
        cell = self.grid.get_cell_at(col, row)
        self.changed.update(self.get_cell_neighbors(cell))
        cell.switch()

    def set_cell_state_at(self, col: int, row: int, state: bool) -> None:
        """
        Set state of cell at col, row to state.

        If the desired state and the cell's current state match, this is a noop.
        """
        cell = self.grid.get_cell_at(col, row)
        if cell.is_alive is not state:
            self.changed.update(self.get_cell_neighbors(cell))
            cell.switch()

    @functools.cache
    def get_cell_neighbors(self, cell: Cell) -> typing.Iterator[Cell]:
        """Yield `cell` and all of its neighbors."""
        return tuple(self.grid.cells[index] for index in self.grid.get_neighbor_indices(cell.x, cell.y))

    def start_stop(self, tick: float = SIMULATION_TICK) -> None:
        """Stop the game if it is running, stop it otherwise."""
        if self.running:
            pyglet.clock.unschedule(self.run_generation)
        else:
            pyglet.clock.schedule_interval(self.run_generation, tick)
        self.running = not self.running

    def clear(self) -> None:
        """Kill all cells."""
        for cell in self.grid.cells:
            if cell.is_alive:
                cell.switch()
