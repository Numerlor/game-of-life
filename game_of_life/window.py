import pyglet

from . import CELL_SIZE, HEIGHT, WIDTH, GridManager, SIMULATION_TICK


class GameOfLifeWindow(pyglet.window.Window):
    """Window managing the game of life."""

    def __init__(self, start_grid, *args, **kwargs):
        if start_grid is not None:
            height = len(start_grid) * CELL_SIZE
            width = len(start_grid[0]) * CELL_SIZE
        else:
            height = HEIGHT
            width = WIDTH
        super().__init__(width, height, *args, **kwargs)
        self.grid = GridManager(start_grid, height, width)

    def on_draw(self) -> None:
        """Clear window and draw grid's batch."""
        self.clear()
        self.grid.batcher.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Run a single generation when a key is pressed."""
        print(self.grid.changed.__len__())

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Switch cell state on mouse clicks."""
        self.grid.switch_cell_at(x // CELL_SIZE, y // CELL_SIZE)
