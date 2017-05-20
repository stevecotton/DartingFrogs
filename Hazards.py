#!/usr/bin/python3
#
# GPLv2+

"""Obstacles and hazards that the frogs have to avoid"""

try:
    import sys
    import random
    import math
    import os
    import getopt
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

class Car(pygame.sprite.Sprite):
    """Cars (including trucks) that travel on a road"""

    fast_car_sprites = [
        "cars/GalardB.png",
        "cars/SuperB.png",
    ]
    car_sprites = [
        "cars/BuickerB.png",
        "cars/JeepB.png",
        "cars/RamB.png",
        "trashmaster.png",
    ]

    def __init__(self, start_point, speed=1):
        """The car spawns with its center at start_point, which should be off-screen.
        
        Positive speeds make the car travel left-to-right, negative means right-to-left
        """
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed

        # todo: pick a random sprite
        spritefile = __class__.car_sprites[0]
        if abs (speed) > 3:
            spritefile = __class__.fast_car_sprites[0]

        # The car images are loaded pointing north
        north_image, north_rect = load_png(spritefile)
        if speed > 0:
            self.image = pygame.transform.rotate (north_image, -90)
        else:
            self.image = pygame.transform.rotate (north_image, -90)
        self.rect = self.image.get_rect()
        self.rect.center = start_point.x, start_point.y
        screen = pygame.display.get_surface()

    def update(self):
        self.rect.move_ip (self.speed, 0);

class Road(pygame.sprite.Sprite):
    """A road is both a background, and a monsterspawn for cars. Spawned cars
    will be added to the car_sprite_group"""

    def __init__(self, car_sprite_group, rect, speed=1):
        """The cars all travel at the same speed"""
        pygame.sprite.Sprite.__init__(self)
        self.car_sprite_group = car_sprite_group
        self.speed = speed
        self.random = random.Random()
        self.rect = rect
        self.image = pygame.Surface ((rect.width, rect.height))
        self.image.fill (pygame.Color (40, 40, 40, 255))
        # For the initial spawn, it should have a high probability of happening immediately
        self.ticks_since_last_spawn = 1000

    def update(self):
        self.ticks_since_last_spawn += 1
        if self.ticks_since_last_spawn * self.speed > random.randrange (100, 2000):
            self.spawn_car()

    def spawn_car(self):
        start_point = None
        if self.speed > 0:
            start_point = CenterPoint(-100, self.rect.centery)
        else:
            start_point = CenterPoint(self.rect.width + 100, self.rect.centery)
        self.car_sprite_group.add (Car (start_point, self.speed))
        self.ticks_since_last_spawn = 0