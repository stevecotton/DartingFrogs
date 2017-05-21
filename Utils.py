#!/usr/bin/python3
#
# Copyright (C) 2017 Steve Cotton (Octalot)
# Based on code from Tom Chance's PyGame tutorial
# Copyright (C) 2003-2016 Tom Chance
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


try:
    import sys
    import os
    import pygame
    from pygame.locals import *
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

def load_png(name, team_color=None):
    """ Load image and return image object"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        if team_color:
            pxarray = pygame.PixelArray (image)
            for x in range (40, 240, 40):
                magenta = pygame.Color (x, 0, x, 255)
                replacement = pygame.Color (int (x * team_color.r / 255), int (x * team_color.g / 255), int (x * team_color.b / 255), 255)
                pxarray.replace (magenta, replacement);
            del pxarray
    except pygame.error as message:
        print ('Cannot load image:', fullname)
        raise SystemExit (message)
    return image, image.get_rect()

def get_bounding_box(*groups):
    """Returns the smallest Rect containing all of the sprites in a pygame.sprite.Group, or None
    for an empty group."""
    result = None
    for group in groups:
        for entity in group:
            if result == None:
                result = entity.rect.copy()
            else:
                result.union_ip (entity.rect)
    return result
