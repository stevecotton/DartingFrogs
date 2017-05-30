#!/usr/bin/python3
#
# Copyright (C) 2017 Steve Cotton (Octalot)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class GameConstants:
    """Constants such as speeds for the Darting Frogs game"""

    # If these two numbers are not the same then the game is much harder. It has two names simply
    # because some locations are more readable with one name or the other.
    road_width = 64
    jump_length = 64

    # Individual steps of a jump - on each clock tick, the frog moves forward (or down, as these
    # numbers are negative) this many pixels.  This adds up to -jump_length, or -road_width.
    frog_jump_movement = [-6, -6, -6, -5, -5, -5, -5, -4, -4, -4, -3, -3, -3, -2, -2, -1]

    # The furthest a frog can move in a single clock tick, equivalent to
    # max (abs (frog_jump_movement))
    furthest_single_tick_jump = 6

    # How far apart the "distance 1000" messages are
    milestone_distance = 2500
