# This file is part of Game-of-life.
# Copyright (C) 2021  Numerlor

import pyglet

CELL_SIZE = 7
HEIGHT = 500
WIDTH = 500
SIMULATION_TICK = 1/20
BACKGROUND = pyglet.graphics.OrderedGroup(0)
MIDDLEGROUND = pyglet.graphics.OrderedGroup(1)
FOREGROUND = pyglet.graphics.OrderedGroup(2)
