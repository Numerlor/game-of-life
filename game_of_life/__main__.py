import json
import sys

import pyglet

from game_of_life import GameOfLifeWindow
from .utils import load_grid_from_file, pad_grid

start_grid = None
if len(sys.argv) > 1:
    start_grid = load_grid_from_file(sys.argv[1])
    pad_grid(start_grid, 1)
window = GameOfLifeWindow(start_grid)
pyglet.app.run()
