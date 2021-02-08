from pathlib import Path

import pyglet

from . import CELL_SIZE, HEIGHT, WIDTH, GameOfLife, SIMULATION_TICK, Grid
from .utils import load_grid_from_file, pad_grid
from .constants import BACKGROUND, FOREGROUND


class ContextMenu:
    BUTTON_HEIGHT = 20
    BUTTON_WIDTH = 50

    def __init__(self, window: pyglet.window.Window, x: int, y: int, batch):
        self.frame = pyglet.gui.Frame(window)
        self.x = x
        self.y = y
        self.button_amount = 0
        self.batch = batch

    def add_button(self, pressed, depressed, hover=None, handler=None):
        self.button_amount += 1
        button = pyglet.gui.PushButton(
            self.x,
            self.y-self.BUTTON_HEIGHT*self.button_amount,
            pyglet.resource.image(pressed),
            pyglet.resource.image(depressed),
            hover and pyglet.resource.image(hover),
            self.batch,
            FOREGROUND
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
        self.batch = pyglet.graphics.Batch()
        self.game = GameOfLife(
            0,
            0,
            start_grid,
            CELL_SIZE,
            height=height,
            width=width,
            batch=self.batch,
            group=BACKGROUND,
        )
        pyglet.clock.unschedule(self.game.run_generation)
        self.context_menu = None

    def on_draw(self) -> None:
        """Clear window and draw grid's batch."""
        self.clear()
        self.batch.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Run a single generation when a key is pressed."""
        print(self.grid.changed.__len__())

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Switch cell state on mouse clicks."""
        if button == pyglet.window.mouse.RIGHT:
            self.context_menu = ContextMenu(self, x, y, self.batch)
            self.context_menu.add_button(
                "placeholder.png",
                "placeholder.png",
                handler=lambda: pyglet.clock.unschedule(self.game.run_generation)
            )
            self.context_menu.add_button(
                "placeholder.png",
                "placeholder.png",
                handler=self.show_popup,
            )
        elif button == pyglet.window.mouse.LEFT:
            if self.context_menu is None:
                self.game.switch_cell_at(x // CELL_SIZE, y // CELL_SIZE)
            self.context_menu = None

    def show_popup(self):
        SelectionPopup(self.show_grid)

    def show_grid(self, grid):
        print(grid)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons == pyglet.window.mouse.LEFT:
            self.game.set_cell_state_at(x//CELL_SIZE, y//CELL_SIZE, not modifiers & pyglet.window.key.MOD_CTRL)


class TemplateWidget(pyglet.gui.WidgetBase):
    def __init__(self, x, y, width, height, grid, name, *, static, batch, callback):
        super().__init__(x, y, width, height)
        grid_width = len(grid[0]) * 5
        grid_height = len(grid)*5
        self.grid = grid
        if static:
            Grid(
                x+width//2-grid_width//2,
                y+height//2-grid_height//2,
                5,
                grid,
                batch=batch,
                group=FOREGROUND
            )
        else:
            GameOfLife(
                x+width//2-grid_width//2+1,
                y+height//2-grid_height//2+1,
                grid,
                5,
                batch=batch,
                tick=1/10,
                group=FOREGROUND
            )
        self.name = name.title() if not name.isupper() else name
        self.callback = callback
        self.label = pyglet.text.Label(self.name, x=x+50, y=y-20, width=100, batch=batch, anchor_x="center")
        self.construct_outline(x, y, width, height, batch)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.callback(self.grid)

    def __repr__(self):
        return f"<TemplateWidget {self.name=} {self.x=}, {self.y=}, {self.width=}, {self.height=}>"

    def construct_outline(self,x, y, width, height, batch):
        self.lines = []
        lines = (
            ((x, y), (x+width, y)),
            ((x+width, y), (x+width, y+height,)),
            ((x+width, y+height,), (x, y+height)),
            ((x, y+height), (x, y)),
        )
        for (x1, y1), (x2, y2) in lines:
            self.lines.append(
                pyglet.shapes.Line(x1, y1, x2, y2, 2, color=(0,)*3, batch=batch)
            )


class SelectionPopup(pyglet.window.Window):
    def __init__(self,pattern_callback, *args, **kwargs):
        self.clear()
        super().__init__(*args, **kwargs)
        self.frame = pyglet.gui.Frame(self, cell_size=1)
        self.batch = pyglet.graphics.Batch()
        y = self.height
        for directory in Path().glob("templates/*"):
            files = list(directory.glob("*"))
            x = (self.width-100*len(files))//2
            y = y-150
            for file in files:
                grid = load_grid_from_file(file)
                if "still" in str(file):
                    static = True
                else:
                    static = False
                pad_grid(grid, 1)
                grid_widget = TemplateWidget(
                    x,
                    y,
                    100,
                    100,
                    grid,
                    file.stem,
                    static=static,
                    batch=self.batch,
                    callback=pattern_callback
                )
                self.frame.add_widget(grid_widget)
                x += 100

    def on_draw(self):
        pyglet.gl.glClearColor(44/255, 47/255, 51/255, 1)

        self.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.frame._cells.get(self.frame._hash(x, y)):
            self.close()
