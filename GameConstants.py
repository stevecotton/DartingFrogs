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

    road_width = 64
    jump_length = 64

    # todo: make the frog end their move aligned to a road, instead of having a collision box
    # that's on two lanes of the road
    # This adds up to -64, or a road width
    frog_jump_movement = [-6, -6, -6, -5, -5, -5, -5, -4, -4, -4, -3, -3, -3, -2, -2, -1]
