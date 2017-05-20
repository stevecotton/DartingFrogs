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

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print ('Cannot load image:', fullname)
        raise SystemExit (message)
    return image, image.get_rect()

class Frog(pygame.sprite.Sprite):
    """Each frog will have a key to make it jump, and a team-color"""
    
    def __init__(self, key, team_color="green", column=0):
        """The key is the keyboard key used to make the frog jump"""
        print ("Creating a new frog for key ", key, " in column ", column)
        self.key = key
        pygame.sprite.Sprite.__init__(self)
        self.sprites = ['frog_resting.png', 'frog_jump.png']
        self.image, self.rect = load_png(self.sprites[0])
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.state = "still"
        self.movepos = 0;
        self.rect.move_ip (self.rect.width * column, 0)
        print ("Frog rect: ", self.rect)

    def update(self):
        newpos = self.rect.move (0, self.movepos)
        if self.area.contains (newpos):
            self.rect = newpos
        else:
            self.movepos = - self.movepos
        pygame.event.pump()

    def getJumpKey(self):
        return self.key
    
    def jump(self):
        """Change to a different sprite, and move up the screen"""
        self.movepos = -1
        self.state = "jump"

    def rest(self):
        self.movepos = 0
        self.state = "still"

def main():
    # Initialise screen
    pygame.init()
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
        playersprites.update()
        playersprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__': main()
