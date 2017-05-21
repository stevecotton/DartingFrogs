#!/usr/bin/python3
#
# GPL, taking code from Tom Chance's PyGame tutorial

"""This is intended to allow as many players as required. Pressing any normal
key adds a frog that will jump when that key is pressed again.
"""
try:
    import sys
    import random
    import math
    import os
    import getopt
    import pygame
    from pygame.locals import *
    from Hazards import Road
    from Utils import *
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

class Frog(pygame.sprite.Sprite):
    """Each frog will have a key to make it jump, and a team-color"""

    # todo: make the frog end their move aligned to a road, instead of having a collision box
    # that's on two lanes of the road
    jump_movement = [-5, -5, -5, -5, -4, -4, -4, -2, -2, -2, -2, -2, -1, -1, -1]
    sprites_files = ['frog_resting.png', 'frog_jump.png']
    
    def __init__(self, key, team_color=None, column=0):
        """The key is the keyboard key used to make the frog jump"""
        pygame.sprite.Sprite.__init__(self)
        print ("Creating a new frog for key ", key, " in column ", column)
        self.key = key
        if (column % 2):
            team_color=pygame.Color (0x80, 0x20 * ((7 - column) % 8), 0, 255)
        else:
            team_color=pygame.Color (0, 0x20 * ((7 - column) % 8), 0x80, 255)
        self.image, self.rect = load_png(__class__.sprites_files[0], team_color)
        self.mask = pygame.mask.from_surface(self.image)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.state = "still"
        self.stateStep = 0;
        self.stateNext = "still";
        self.rect.bottom = screen.get_rect().bottom - 100;
        self.rect.centerx = screen.get_rect().width / 4 + self.rect.width * column
        print ("Frog rect: ", self.rect)

    def update(self):
        if self.state == "jump":
            if self.stateStep < len(__class__.jump_movement):
                newpos = self.rect.move (0, __class__.jump_movement[self.stateStep])
                if self.area.contains (newpos):
                    self.rect = newpos
                self.stateStep = self.stateStep + 1
            else:
                self.state = self.stateNext
                self.stateStep = 0


    def getJumpKey(self):
        return self.key
    
    def jump(self):
        """Change to a different sprite, and move up the screen"""
        # Hammering the jump key will move faster than just keeping it pressed.
        # todo: add joystick support to prevent hardware damage
        self.state = "jump"
        self.stateStep = 0
        self.stateNext = "jump"

    def jump_forced(self):
        """Frogs at the back of the screen are forced to jump so that they don't scroll off the
        bottom."""
        self.state = "jump"
        self.stateStep = 0
        # Does not change self.stateNext, "still" frogs will stop after one jump

    def rest(self):
        self.stateNext = "still"

def main():
    # Initialise screen
    pygame.init()
    camera_area = pygame.Rect (0, 0, 1024, 700)
    screen = pygame.display.set_mode((camera_area.width, camera_area.height))
    pygame.display.set_caption('Multiplayer frog selection')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0x40, 0x80, 0x40))

    # Initialise players
    players = []

    # Initialise sprite groups
    playersprites = pygame.sprite.Group(players)
    # Scenery isn't dangerous (but includes roads, which spawn hazards)
    scenerysprites = pygame.sprite.Group()
    # Hazard sprites are the ones that will kill colliding frogs
    hazardsprites = pygame.sprite.Group()

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialise clock and RNG
    clock = pygame.time.Clock()
    random_number_generator = random.Random()

    # Event loop
    while 1:
        # Make sure game doesn't run at more than 60 frames per second
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                already_controls_a_frog = False
                for player in players:
                    if event.key == player.getJumpKey():
                        already_controls_a_frog = True
                        player.jump()
                if not already_controls_a_frog:
                    frog = Frog (key=event.key, column=len(players))
                    players.append (frog)
                    playersprites.add (frog)
                    frog.jump()

            elif event.type == KEYUP:
                for player in players:
                    if event.key == player.getJumpKey():
                        player.rest()

        # Find out where the frogs are, calculate whether the screen should scroll
        screen_scroll = 0
        bounds = get_bounding_box (playersprites)
        if bounds != None:
            # Scroll if no-one's near the bottom
            if bounds.bottom < 0.8 * camera_area.height:
                screen_scroll += 1
            # Scroll if anyone is ahead
            if bounds.top < 0.5 * camera_area.height:
                screen_scroll += 1
            # Scroll faster if someone is far ahead
            if bounds.top < 0.2 * camera_area.height:
                screen_scroll += 2

        # Screen scroll is really moving everything downwards
        for entity in playersprites:
            entity.rect.move_ip (0, screen_scroll)
        for entity in scenerysprites:
            entity.rect.move_ip (0, screen_scroll)
        for entity in hazardsprites:
            entity.rect.move_ip (0, screen_scroll)

        # If any frogs are at the back of the screen, move them
        if screen_scroll:
            for player in players:
                if player.rect.bottom + screen_scroll >= camera_area.height:
                    player.jump_forced()

        # Scrolling the screen may introduce a new hazard or hazard-spawning scenery
        bounds = get_bounding_box (hazardsprites, scenerysprites)
        if bounds == None or bounds.top > 100:
            speed = random_number_generator.randint (-5, 5)
            if speed != 0:
                road = Road (hazardsprites, Rect(0, -100, camera_area.width, 64), speed)
                scenerysprites.add (road)

        hazardsprites.update()
        scenerysprites.update()
        playersprites.update()

        offscreenRemoval = []
        for entity in scenerysprites:
            if entity.rect.top > camera_area.height:
                offscreenRemoval.append (entity)
        for entity in hazardsprites:
            if entity.rect.top > camera_area.height:
                offscreenRemoval.append (entity)
        for entity in offscreenRemoval:
            print ("Removing hazard or scenery at ", entity.rect)
            entity.kill()

        # Now check for collisions
        for player in playersprites:
            hit = pygame.sprite.spritecollide (player, hazardsprites, False, collided=pygame.sprite.collide_mask)
            if (hit):
                print ("Frog hit hazard")

        screen.blit(background, (0, 0))
        scenerysprites.draw(screen)
        hazardsprites.draw(screen)
        playersprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__': main()
