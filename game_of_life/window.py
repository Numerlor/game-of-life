import pyglet

from . import CELL_SIZE, HEIGHT, WIDTH, GridManager, SIMULATION_TICK


class ContextMenu:
    BUTTON_HEIGHT = 20
    BUTTON_WIDTH = 50

    def __init__(self, window: pyglet.window.Window, x: int, y: int):
        self.frame = pyglet.gui.Frame(window)
        self.x = x
        self.y = y
        self.button_amount = 0
        self.batch = pyglet.graphics.Batch()

    def add_button(self, pressed, depressed, hover=None, handler=None):
        self.button_amount += 1
        button = pyglet.gui.PushButton(
            self.x,
            self.y-self.BUTTON_HEIGHT*self.button_amount,
            pyglet.resource.image(pressed),
            pyglet.resource.image(depressed),
            hover and pyglet.resource.image(hover),
            self.batch
        )
        button.set_handler("on_press", handler)
        self.frame.add_widget(button)

    def point_intersects(self, x, y) -> bool:
        return (
                self.x < x < self.x + self.BUTTON_WIDTH
                and self.y - self.BUTTON_HEIGHT*self.button_amount < y < self.y
        )


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
        self.context_menu = None

    def on_draw(self) -> None:
        """Clear window and draw grid's batch."""
        self.clear()
        self.grid.batcher.draw()
        if self.context_menu is not None:
            self.context_menu.batch.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Run a single generation when a key is pressed."""
        print(self.grid.changed.__len__())

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Switch cell state on mouse clicks."""
        if button == pyglet.window.mouse.RIGHT:
            self.context_menu = ContextMenu(self, x, y)
            self.context_menu.add_button(
                "placeholder.png",
                "placeholder.png", handler=lambda: pyglet.clock.unschedule(self.grid.run_generation)
            )
            self.context_menu.add_button("placeholder.png", "placeholder.png")
        elif button == pyglet.window.mouse.LEFT:
            if self.context_menu is None:
                self.grid.switch_cell_at(x // CELL_SIZE, y // CELL_SIZE)
            self.context_menu = None
