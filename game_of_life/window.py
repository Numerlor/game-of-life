from pathlib import Path

import pyglet

from . import CELL_SIZE, HEIGHT, WIDTH, GameOfLife, SIMULATION_TICK, Grid
from .utils import load_grids_from_file, pad_grid
from .constants import BACKGROUND, FOREGROUND, MIDDLEGROUND

MAX_PAGE = 2


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
        self.context_menu = None
        self.template = None
        self.grid = None

    def on_draw(self) -> None:
        """Clear window and draw grid's batch."""
        self.clear()
        self.batch.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Run a single generation when a key is pressed."""
        if symbol == pyglet.window.key.SPACE:
            self.game.run_generation(0)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Switch cell state on mouse clicks."""
        if button == pyglet.window.mouse.RIGHT:
            self.context_menu = ContextMenu(self, x, y, self.batch)
            image = "stop" if self.game.running else "start"
            self.context_menu.add_button(
                f"{image}_depressed.png",
                f"{image}_depressed.png",
                f"{image}_hover.png",
                handler=self.game.start_stop
            )
            self.context_menu.add_button(
                "templates_depressed.png",
                "templates_depressed.png",
                "templates_hover.png",
                handler=self.show_popup,
            )
            self.context_menu.add_button(
                "clear_depressed.png",
                "clear_depressed.png",
                "clear_hover.png",
                handler=self.clear_game
            )
        elif button == pyglet.window.mouse.LEFT:
            if self.context_menu is None:
                self.game.switch_cell_at(x // CELL_SIZE, y // CELL_SIZE)
            self.context_menu = None
            if self.template:
                for cell in self.grid.cells:
                    cell.vertex.delete()
                    for cell_y, row in enumerate(self.template):
                        for cell_x, state in enumerate(row):
                            self.game.set_cell_state_at(x // CELL_SIZE + cell_x, y // CELL_SIZE + cell_y, bool(state))
                self.template = None
                self.grid = None

    def clear_game(self):
        for y in range(0, self.height//CELL_SIZE):
            for x in range(0, self.width//CELL_SIZE):
                self.game.set_cell_state_at(x, y, False)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.template is not None:
            if self.grid is not None:
                for cell in self.grid.cells:
                    cell.vertex.delete()
            self.grid = Grid(x, y, CELL_SIZE, self.template, batch=self.batch, group=MIDDLEGROUND)

    def show_popup(self):
        pyglet.clock.unschedule(self.game.run_generation)
        SelectionPopup(self.show_grid)
        self.game.running = False

    def show_grid(self, grid):
        self.template = grid

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
            self.game = Grid(
                x+width//2-grid_width//2,
                y+height//2-grid_height//2,
                5,
                grid,
                batch=batch,
                group=MIDDLEGROUND
            )
            self.game.create_grid()
        else:
            self.game = GameOfLife(
                x+width//2-grid_width//2+1,
                y+height//2-grid_height//2+1,
                grid,
                5,
                batch=batch,
                tick=1/10,
                group=MIDDLEGROUND
            )
        self.name = name.title() if not name.isupper() else name
        self.callback = callback
        self.label = pyglet.text.Label(self.name, x=x+50, y=y-20, width=100, batch=batch, anchor_x="center")
        self.construct_outline(x, y, width, height, batch)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.callback(self.grid)

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

    def destroy(self):
        if isinstance(self.game, GameOfLife):
            pyglet.clock.unschedule(self.game.run_generation)
            for cell in self.game.grid.cells:
                cell.delete()
            for line in self.game.grid.grid_lines:
                line.delete()
        else:
            for cell in self.game.cells:
                cell.delete()
            for line in self.game.grid_lines:
                line.delete()
        for line in self.lines:
            line.delete()
        self.label.delete()


class SelectionPopup(pyglet.window.Window):
    def __init__(self, pattern_callback, *args, **kwargs):
        self.clear()
        super().__init__(*args, **kwargs)
        self.frame = pyglet.gui.Frame(self, cell_size=1)
        self.batch = pyglet.graphics.Batch()
        self.button_frame = pyglet.gui.Frame(self)

        self.callback = pattern_callback
        self.current_page = 1
        self.add_buttons()
        self.widgets = []
        self.load_page()

    def add_buttons(self):
        def load_next_page(*args):
            if self.current_page != MAX_PAGE:
                self.current_page += 1
                self.load_page()

        def load_prev_page(*args):
            if self.current_page != 1:
                self.current_page -= 1
                self.load_page()

        self.prev_button = pyglet.gui.PushButton(
            20,
            self.height // 2,
            pyglet.resource.image("left_arrow.png"),
            pyglet.resource.image("left_arrow.png"),
            pyglet.resource.image("left_arrow_hover.png"),
            self.batch,
        )
        self.prev_button.set_handler("on_mouse_press", load_prev_page)

        self.next_button = pyglet.gui.PushButton(
            self.width - 50,
            self.height // 2,
            pyglet.resource.image("right_arrow.png"),
            pyglet.resource.image("right_arrow.png"),
            pyglet.resource.image("right_arrow_hover.png"),
            self.batch,
        )
        self.next_button.set_handler("on_mouse_press", load_next_page)
        self.button_frame.add_widget(self.prev_button)
        self.button_frame.add_widget(self.next_button)

    def load_page(self):
        for widget in self.widgets:
            widget.destroy()
            self.frame = pyglet.gui.Frame(self, cell_size=1)
        self.widgets = []
        y = self.height
        for file in Path().glob("templates/*"):
            grids_data = load_grids_from_file(file)
            if grids_data["PAGE"] != self.current_page:
                continue
            x = (self.width-100*len(grids_data["templates"]))//2
            y = y-150
            for name, grid in grids_data["templates"].items():
                pad_grid(grid, 1)
                grid_widget = TemplateWidget(
                    x,
                    y,
                    100,
                    100,
                    grid,
                    name,
                    static=grids_data["STATIC"],
                    batch=self.batch,
                    callback=self.callback
                )
                self.frame.add_widget(grid_widget)
                self.widgets.append(grid_widget)
                x += 100

    def on_draw(self):
        pyglet.gl.glClearColor(44/255, 47/255, 51/255, 1)

        self.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.frame._cells.get(self.frame._hash(x, y)):
            self.close()
