#!/usr/bin/python3
#
# Copyright (C) 2017-2019 Steve Cotton (Octalot)
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

"""Utility functions for DartingFrogs"""

try:
    import sys
    import os
    import pygame
    from pygame.locals import *
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

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

class ImageCache:
    """Caching image loader, each call to one of the load_*_image functions with the same arguments
    will return the same instance of pygame.Surface.

    Each instance of ImageCache has its own cache, which is not shared with other instances; the
    caller is expected to share the instance appropriately. For example, all instances of the Car
    class share Car.image_cache.
    """
    _code_dir = os.path.abspath(os.path.dirname(__file__))
    _data_dir = os.path.normpath(os.path.join(_code_dir, 'data'))

    def __init__(self):
        self._cache = {}
        pass

    def _load_from_file(self, name):
        fullname = os.path.join(self._data_dir, name)
        try:
            image = pygame.image.load(fullname)
            if image.get_alpha() is None:
                image = image.convert()
            else:
                image = image.convert_alpha()
        except pygame.error as message:
            print ('Cannot load image:', fullname)
            raise SystemExit (message)
        return image

    def load_image(self, filename):
        return self.load_rotated_image (filename, 0)

    def load_rotated_image (self, filename, rotation):
        key = (filename, rotation)
        if key in self._cache:
            return self._cache[key]
        image = self._load_from_file(filename)
        if rotation != 0:
            image = pygame.transform.rotate (image, rotation)
        self._cache[key] = image
        return image

class TeamColorPainter:
    """The game only has one set of frog images, and uses palette shifting to
    generate the multiple colors.  The base image has magenta coloration.

    For a description with examples, see Wesnoth's Wiki:
    https://wiki.wesnoth.org/Team_Color_Shifting
    """

    # The base image is cached, but a copy is made for each recoloration
    image_cache = ImageCache()

    def load_image(name, team_color):
        image = __class__.image_cache.load_image(name).copy()
        pxarray = pygame.PixelArray (image)
        for x in range (40, 241, 40):
            magenta = pygame.Color (x, 0, x, 255)
            replacement = pygame.Color (int (x * team_color.r / 255), int (x * team_color.g / 255), int (x * team_color.b / 255), 255)
            pxarray.replace (magenta, replacement)
        del pxarray
        return image
