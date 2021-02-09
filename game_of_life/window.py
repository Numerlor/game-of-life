# This file is part of Game-of-life.
# Copyright (C) 2021  Numerlor

import typing
from pathlib import Path

import pyglet

from . import CELL_SIZE, GameOfLife, Grid, HEIGHT, WIDTH
from .constants import BACKGROUND, FOREGROUND, MIDDLEGROUND
from .utils import load_grids_from_file, pad_grid

MAX_PAGE = 2


class ContextMenu:
    """Context menu with a simpler interface for adding widgets."""

    BUTTON_HEIGHT = 20
    BUTTON_WIDTH = 50

    def __init__(self, window: pyglet.window.Window, x: int, y: int, batch: pyglet.graphics.Batch):
        self.frame = pyglet.gui.Frame(window)
        self.x = x
        self.y = y
        self.button_amount = 0
        self.batch = batch

    def add_button(
            self,
            pressed: str,
            depressed: str,
            hover: typing.Optional[str] = None,
            handler: typing.Optional[typing.Callable] = None,
    ) -> None:
        """Add a button with images set to `pressed`, `depressed` and `hover` and link its on_press to the handler."""
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


class GameOfLifeWindow(pyglet.window.Window):
    """Window managing the game of life."""

    def __init__(self, start_grid: list[list[int]], *args, **kwargs):
        if start_grid is not None:
            height = len(start_grid) * CELL_SIZE
            width = len(start_grid[0]) * CELL_SIZE
        else:
            height = HEIGHT
            width = WIDTH
        super().__init__(width, height, *args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        grid = Grid(0, 0, CELL_SIZE, start_grid, height=height, width=width, batch=self.batch, group=BACKGROUND)
        self.game = GameOfLife(grid)
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
        """
        Handle mouse press events.

        If the right mouse button was clicked, open a context menu.

        If a left right mouse was clicked:
            * if no context menu is open switch the cell under the cursor
            * reset the context menu instance to None

            * if a template is active, set the cells under it to its state and reset the tempalte and grid
        """
        if button == pyglet.window.mouse.RIGHT:
            self.construct_context_menu(x, y)
        elif button == pyglet.window.mouse.LEFT:
            if self.context_menu is None:
                self.game.switch_cell_at(x // CELL_SIZE, y // CELL_SIZE)
            self.context_menu = None
            if self.template:
                for cell in self.grid.cells:
                    cell.delete()
                for cell_y, row in enumerate(self.template):
                    for cell_x, state in enumerate(row):
                        self.game.set_cell_state_at(x // CELL_SIZE + cell_x, y // CELL_SIZE + cell_y, bool(state))
                self.template = None
                self.grid = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """If we have an active template, keep the grid at the mouse's position."""
        if self.template is not None:
            self.grid.move_grid(x // CELL_SIZE, y // CELL_SIZE)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        """When the mouse is dragged, fill cells. If ctrl is held the cells are killed instead."""
        if buttons == pyglet.window.mouse.LEFT:
            self.game.set_cell_state_at(x//CELL_SIZE, y//CELL_SIZE, not modifiers & pyglet.window.key.MOD_CTRL)

    def set_grid(self, grid: list[list[int]]) -> None:
        """Set the template to the received grid."""
        self.template = grid
        self.grid = Grid(0, 0, CELL_SIZE, self.template, batch=self.batch, group=MIDDLEGROUND)

    def show_popup(self) -> None:
        """Show the template selection popup; stop the game if it's running."""
        pyglet.clock.unschedule(self.game.run_generation)
        SelectionPopup(self.set_grid)
        self.game.running = False

    def construct_context_menu(self, x: int, y: int) -> None:
        """Create a context menu."""
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
            handler=self.game.clear
        )


class TemplateWidget(pyglet.gui.WidgetBase):
    """
    Widget holding a grid template.

    If static is True, the grid template is a Grid instance, otherwise
    a GameOfLife instance is used and ran.

    When the mouse is pressed inside the widget, the widget calls its callback with the grid.
    """

    def __init__(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            template: list[list[int]],
            name: str,
            *,
            static: bool,
            batch: pyglet.graphics.Batch,
            callback: typing.Callable
    ):
        super().__init__(x, y, width, height)
        self.template = template
        self.static = static
        self.callback = callback
        self.grid_lines = []

        grid_width = len(template[0]) * 5
        grid_height = len(template)*5

        self.grid = Grid(
                x+width//2-grid_width//2,
                y+height//2-grid_height//2,
                5,
                template,
                batch=batch,
                group=MIDDLEGROUND
        )
        if not static:
            self.game = GameOfLife(self.grid)
        self.name = name.title() if not name.isupper() else name
        self.label = pyglet.text.Label(self.name, x=x+50, y=y-20, width=100, batch=batch, anchor_x="center")
        self.construct_outline(x, y, width, height, batch)

    def on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
        """If we received a mouse press event, call the callback. The parent will handle the destruction."""
        self.callback(self.template)

    def construct_outline(self, x: int, y: int, width: int, height: int, batch: pyglet.graphics.Batch) -> None:
        """Create square outline with `width` and `height` at (`x`, `y`)."""
        lines = (
            ((x, y), (x+width, y)),
            ((x+width, y), (x+width, y+height,)),
            ((x+width, y+height,), (x, y+height)),
            ((x, y+height), (x, y)),
        )
        for (x1, y1), (x2, y2) in lines:
            self.grid_lines.append(
                pyglet.shapes.Line(x1, y1, x2, y2, 2, color=(0,)*3, batch=batch)
            )

    def destroy(self) -> None:
        """Stop running game and delete all opengl vertices."""
        if not self.static:
            pyglet.clock.unschedule(self.game.run_generation)
            for cell in self.game.grid.cells:
                cell.delete()
            for line in self.game.grid.grid_lines:
                line.delete()
        else:
            for cell in self.grid.cells:
                cell.delete()
            for line in self.grid.grid_lines:
                line.delete()
        for line in self.grid_lines:
            line.delete()
        self.label.delete()


class SelectionPopup(pyglet.window.Window):
    """
    A popup with grid templates.

    All templates from the templates directory are collected and paginated
    according to their set PAGE numbers.

    When a template is selected, the `pattern_callback` is called with its grid and the window is closed.
    """

    def __init__(self, pattern_callback: typing.Callable, *args, **kwargs):
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

    def add_buttons(self) -> None:
        """Add next and previous page buttons to the button frame."""
        def load_next_page(*args) -> None:
            if self.current_page != MAX_PAGE:
                self.current_page += 1
                self.load_page()

        def load_prev_page(*args) -> None:
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

    def load_page(self) -> None:
        """
        Load a page of templates.

        First all the previous templates widgets are destroyed,
        then all templates are searched and the ones matching the current page
        number are displayed.
        """
        self.destroy_widgets()
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

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """If the click was in a tempalte widget, close the window."""
        if self.frame._cells.get(self.frame._hash(x, y)):
            self.close()

    def destroy_widgets(self) -> None: # noqa D102
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()

    def on_close(self) -> None:
        """When the window is closed destroy all widgets."""
        self.destroy_widgets()
        self.frame = pyglet.gui.Frame(self, cell_size=1)
        self.widgets.clear()
        super().on_close()

    def on_draw(self): # noqa D102
        pyglet.gl.glClearColor(44/255, 47/255, 51/255, 1)

        self.clear()
        self.batch.draw()
