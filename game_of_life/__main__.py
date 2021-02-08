# Game-of-life
# Copyright (C) 2021 Numerlor
#
# Auto_Neutron is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Game-of-life is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Game-of-life.  If not, see <https://www.gnu.org/licenses/>.

import sys
from pathlib import Path

import pyglet

from game_of_life import GameOfLifeWindow
from .utils import load_grid_from_file, pad_grid

pyglet.resource.path.append("../resources")
pyglet.resource.reindex()

start_grid = None
if len(sys.argv) > 1:
    start_grid = load_grid_from_file(Path(sys.argv[1]))
    pad_grid(start_grid, 1)
window = GameOfLifeWindow(start_grid)
pyglet.app.run()
