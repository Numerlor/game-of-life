import json
import sys

import pyglet

from game_of_life import GameOfLifeWindow

start_grid = None
sys.argv.append("templates/spinner.json")
if len(sys.argv) > 1:
    with open(sys.argv[1], encoding="utf8") as file:
        start_grid = json.load(file)
        # Add padding on direct whole grid loads
        for row in start_grid:
            row[:] = [0, *row, 0]
        row_len = len(start_grid[0])
        start_grid[:] = [[0]*row_len, *reversed(start_grid), [0]*row_len]
window = GameOfLifeWindow(start_grid)
pyglet.app.run()
