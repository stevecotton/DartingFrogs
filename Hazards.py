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
    from Utils import *
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

class CenterPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class ImageCache:
    cache = {}

    def __init__(self):
        pass

    def load_rotated_image (self, filename, rotation):
        key = (filename, rotation)
        if key in __class__.cache:
            print ("Cache hit for ", key)
            return __class__.cache[key]
        image, ignored_rect = load_png(filename)
        if rotation != 0:
            image = pygame.transform.rotate (image, rotation)
        __class__.cache[key] = image
        return image

class Car(pygame.sprite.Sprite):
    """Cars (including trucks) that travel on a road"""

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
        print ("Spawning car at ", self.rect, " with speed ", speed)

    def update(self):
        self.rect.move_ip (self.speed, 0)
        if self.kill_point > 0 and self.rect.left > self.kill_point:
            self.kill()
        elif self.kill_point < 0 and self.rect.right < self.kill_point:
            self.kill()

    def kill(self):
        print ("Despawning car at ", self.rect)
        super().kill()

class Road(pygame.sprite.Sprite):
    """A road is both a background, and a monsterspawn for cars. Spawned cars
    will be added to the car_sprite_group"""

    random_speeds = [1, 2, 3, 3, 3, 4, 4, 4, 5, 5, 8, -1, -2, -3, -3, -3, -4, -4, -4, -5, -5, -8]

    def __init__(self, car_sprite_group, rect, speed=0):
        """The cars on a road all travel at the same speed

        speed=0 means to randomly generate a speed"""
        pygame.sprite.Sprite.__init__(self)
        self.car_sprite_group = car_sprite_group
        self.random = random.Random()
        self.rect = rect
        self.image = pygame.Surface ((rect.width, rect.height))
        self.image.fill (pygame.Color (40, 40, 40, 255))
        if speed:
            self.speed = speed
        else:
            self.speed = self.random.choice (__class__.random_speeds)
        # Cars are created in the middle of the road at x=spawnx, and disappear at killx
        if self.speed < 0:
            self.spawnx = self.rect.width + 100
            self.killx = -100
        else:
            self.spawnx = -100
            self.killx = self.rect.width + 100
        # Put some cars on the road during the first update() call
        self.ticks_until_next_spawn = -1
        print ("New road with speed ", self.speed, " and spawnx ", self.spawnx)

    def update(self):
        # Negative ticks_until_next_spawn mean this is the first update() for
        # this road, and it will still be off-screen.
        if self.ticks_until_next_spawn < 0:
            spawnx = self.random.randrange (self.rect.width)
            self.spawn_car(spawnx)
        elif self.ticks_until_next_spawn == 0:
            self.spawn_car (self.spawnx)
        else:
            self.ticks_until_next_spawn -= 1

    def spawn_car(self, spawnx):
        start_point = CenterPoint (self.spawnx, self.rect.centery)
        car = Car (start_point, self.killx, self.speed)
        self.car_sprite_group.add (car)
        self.ticks_until_next_spawn = random.randrange (300, 1000) / abs (self.speed)
