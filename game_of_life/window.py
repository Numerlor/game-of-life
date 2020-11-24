import pyglet

from . import GridManager


class GameOfLifeWindow(pyglet.window.Window):
    """Window managing the game of life."""

    def __init__(self, cell_size: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = GridManager(self.width, self.height, cell_size)
        self.cell_size = cell_size
        self.grid.create()

    def on_draw(self) -> None:
        """Clear window and draw grid's batch."""
        self.clear()
        self.grid.batcher.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Run a single generation when a key is pressed."""
        self.grid.run_generation()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Switch cell state on mouse clicks."""
        cell = self.grid.get_cell_at(x // self.cell_size, y // self.cell_size)
        if cell.is_alive:
            cell.hide()
        else:
            cell.show()
