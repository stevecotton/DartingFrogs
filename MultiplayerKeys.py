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

class Frog(pygame.sprite.Sprite):
    """Each frog will have a key to make it jump, and a team-color"""

    jumpMovement = [-5, -5, -5, -5, -5, -4, -4, -4, -4, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -1, -1, -1]
    
    def __init__(self, key, team_color=None, column=0):
        """The key is the keyboard key used to make the frog jump"""
        print ("Creating a new frog for key ", key, " in column ", column)
        self.key = key
        pygame.sprite.Sprite.__init__(self)
        self.sprites = ['frog_resting.png', 'frog_jump.png']
        if (column % 2):
            team_color=pygame.Color (0x80, 0x20 * ((7 - column) % 8), 0, 255)
        else:
            team_color=pygame.Color (0, 0x20 * ((7 - column) % 8), 0x80, 255)
        self.image, self.rect = load_png(self.sprites[0], team_color)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.state = "still"
        self.stateStep = 0;
        self.stateNext = "still";
        self.rect.move_ip (self.rect.width * column, 0)
        print ("Frog rect: ", self.rect)

    def update(self):
        if self.state == "jump":
            if self.stateStep < len(__class__.jumpMovement):
                newpos = self.rect.move (0, __class__.jumpMovement[self.stateStep])
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

    def rest(self):
        self.stateNext = "still"

def main():
    # Initialise screen
    pygame.init()
    camera_area = pygame.Rect (0, 0, 640, 480)
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Multiplayer frog selection')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0x40, 0x80, 0x40))

    # Initialise players
    players = []
    players.append (Frog(key=K_UP, column=0))
    players.append (Frog(key=K_a, column=1))

    # Initialise sprites
    playersprites = pygame.sprite.RenderPlain(players)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialise clock
    clock = pygame.time.Clock()

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

        for player in players:
            screen.blit(background, player.rect, player.rect)

        # Find out where the frogs are, calculate whether the screen should scroll
        screen_scroll = 0
        if len (players) > 0:
            make_slow_frogs_jump = False
            front, back = camera_area.height, 0
            for player in players:
                front = min (front, player.rect.y)
                back = max (back, player.rect.bottom)
            if back < 0.8 * camera_area.height:
                screen_scroll += 1
            if front < 0.5 * camera_area.height:
                screen_scroll += 1
            if front < 0.2 * camera_area.height:
                screen_scroll += 2

        # Screen scroll is really moving everything downwards
        for entity in playersprites:
            entity.rect.move_ip (0, screen_scroll)

        # If any frogs are at the back of the screen, move them
        if screen_scroll:
            for player in players:
                if player.rect.bottom + screen_scroll > 0.95 * camera_area.height:
                    player.jump()

        playersprites.update()

        playersprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__': main()
