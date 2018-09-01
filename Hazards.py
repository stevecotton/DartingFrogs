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


"""Obstacles and hazards that the frogs have to avoid"""

try:
    import sys
    import random
    import pygame
    from pygame.locals import *
    from Utils import ImageCache
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

class CenterPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Car(pygame.sprite.Sprite):
    """Cars (including trucks) that travel on a road"""

    # The sprite is chosen simply by choosing one of these at random, so repeating an entry makes it
    # more likely to be chosen.
    fast_car_sprites = [
        "cars/GalardB.png",
        "cars/SuperB.png",
        "cars/GalardB.png",
        "cars/SuperB.png",
        "cars/GalardB.png",
        "cars/SuperB.png",
        "cars/BuickerB.png",
        "cars/JeepB.png",
        "cars/RamB.png",
    ]
    car_sprites = [
        "cars/GalardB.png",
        "cars/SuperB.png",
        "cars/BuickerB.png",
        "cars/JeepB.png",
        "cars/RamB.png",
    ]
    slow_car_sprites = [
        "cars/BuickerB.png",
        "cars/JeepB.png",
        "cars/RamB.png",
        "trashmaster.png",
    ]

    image_cache = ImageCache()

    def __init__(self, start_point, kill_point, speed=1):
        """The car spawns with its center at start_point, which should be off-screen.

        Positive speeds make the car travel left-to-right, negative means right-to-left.
        When the center of the car reaches kill_point, the sprite is removed
        """
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed

        spritefile = None
        if abs (speed) > 4:
            spritefile = random.Random().choice (__class__.fast_car_sprites)
        elif abs (speed) > 2:
            spritefile = random.Random().choice (__class__.car_sprites)
        else:
            spritefile = random.Random().choice (__class__.slow_car_sprites)

        # The car images are loaded pointing north
        if speed > 0:
            self.image = __class__.image_cache.load_rotated_image (spritefile, -90)
        else:
            self.image = __class__.image_cache.load_rotated_image (spritefile, 90)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = start_point.x, start_point.y
        self.kill_point = kill_point

    def update(self):
        self.rect.move_ip (self.speed, 0)
        if self.kill_point > 0 and self.rect.left > self.kill_point:
            self.kill()
        elif self.kill_point < 0 and self.rect.right < self.kill_point:
            self.kill()

    def kill(self):
        super().kill()

class TiledBackground(pygame.sprite.Sprite):
    """Common code for roads and grass areas that will be drawn with lots of copies of a single image."""

    image_cache = ImageCache()

    def __init__(self, rect, imagefile):
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.image = __class__.image_cache.load_tiled_image (imagefile, rect.width, rect.height)

class Grass(TiledBackground):
    """Grass is not hazardous, but it's here to use the TiledBackground"""

    background_images = [
        "terrain/meadow1_00.png",
        "terrain/meadow2_00.png",
        "terrain/meadow3_00.png",
        "terrain/meadow4_00.png",
    ]

    def __init__(self, rect):
        TiledBackground.__init__(self, rect, random.Random().choice(__class__.background_images))

class Road(TiledBackground):
    """A road is both a background, and a monsterspawn for cars."""

    random_speeds = [1, 2, 3, 3, 3, 4, 4, 4, 5, 5, 8, -1, -2, -3, -3, -3, -4, -4, -4, -5, -5, -8]
    random_spawn_range = [300, 1000]

    background_images = [
        "terrain/road1.png",
        "terrain/road2.png",
    ]

    def __init__(self, car_sprite_group, rect, speed=0):
        """The cars on a road all travel at the same speed

        speed=0 means to randomly generate a speed.

        Spawned cars will be added to the car_sprite_group passed to the
        constructor, collision detection will treat sprites in the
        car_sprite_group as deadly hazards.
        """
        TiledBackground.__init__(self, rect, random.Random().choice(__class__.background_images))
        self.car_sprite_group = car_sprite_group
        self.random = random.Random()
        self.rect = rect
        if speed:
            self.speed = speed
        else:
            self.speed = self.random.choice (__class__.random_speeds)
        self.min_spawn_ticks = int (__class__.random_spawn_range[0] / abs (self.speed))
        self.max_spawn_ticks = int (__class__.random_spawn_range[1] / abs (self.speed))
        # Cars are created in the middle (vertically) of the road at x=spawnx, and disappear at killx
        if self.speed < 0:
            self.spawnx = self.rect.width + 100
            self.killx = -100
        else:
            self.spawnx = -100
            self.killx = self.rect.width + 100
        # Put some cars on the road during the first update() call
        self.ticks_until_next_spawn = -1

    def update(self):
        # Negative ticks_until_next_spawn mean this is the first update() for this road, and it will
        # still be off-screen.  Spawn a car that's already on the road, so that the roads don't
        # start empty.
        if self.ticks_until_next_spawn < 0:
            spawnx = self.killx
            if self.speed < 0:
                while spawnx < self.spawnx:
                    spawnx -= self.speed * random.randrange (self.min_spawn_ticks, self.max_spawn_ticks)
                    self.spawn_car(spawnx)
            else:
                while spawnx > self.spawnx:
                    spawnx -= self.speed * random.randrange (self.min_spawn_ticks, self.max_spawn_ticks)
                    self.spawn_car(spawnx)
            self.ticks_until_next_spawn = random.randrange (self.min_spawn_ticks, self.max_spawn_ticks)
            self.ticks_until_next_spawn += int (abs (spawnx - self.spawnx) / abs (self.speed))
        elif self.ticks_until_next_spawn == 0:
            self.spawn_car (self.spawnx)
            self.ticks_until_next_spawn = random.randrange (self.min_spawn_ticks, self.max_spawn_ticks)
        else:
            self.ticks_until_next_spawn -= 1

    def spawn_car(self, spawnx):
        start_point = CenterPoint (spawnx, self.rect.centery)
        car = Car (start_point, self.killx, self.speed)
        self.car_sprite_group.add (car)
