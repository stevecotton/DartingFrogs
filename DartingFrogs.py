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

"""A multiplayer frog-racing game.

This is intended to allow as many players as required.  While the frogs are
still on the first screen, pressing any normal key adds a frog that will jump
when that key is pressed again.
"""

try:
    import gettext
    import sys
    import random
    import pygame
    from pygame.locals import *
    from GameConstants import GameConstants
    from Hazards import Road
    from Utils import *
    from Frogs import PlayerFrog
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

gettext.install ('DartingFrogs', 'data/locale')

class MessageSprite(pygame.sprite.Sprite):
    """A single line of text"""
    def __init__(self, message):
        pygame.sprite.Sprite.__init__(self)
        font = pygame.font.SysFont(None, 40)
        self.image = font.render (message, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.rect.centerx = screen.get_size()[0] / 2

class PlayersCanJoinMessage(MessageSprite):
    """The text that any key joins the game is a sprite, when it scrolls off
    screen is the time that players can't join any more
    """
    def __init__(self):
        message = _("Press any button or any key to get a frog (except escape, which quits)")
        MessageSprite.__init__(self, message)

class EachJoiningPlayerMessage(MessageSprite):
    """Shown when a new player joins the game, to show which key or button controls which frog"""
    def __init__(self, frog):
        pygame.sprite.Sprite.__init__(self)
        message = frog.get_name()
        if len (message) == 1:
            font = pygame.font.SysFont(None, 50)
        else:
            font = pygame.font.SysFont(None, 20)
        self.image = font.render (message, True, frog.get_color())
        self.rect = self.image.get_rect()
        self.rect.centerx = frog.rect.centerx
        self.rect.top = frog.rect.centery

class VictoryMessage(MessageSprite):
    """Shown as the game_over_sprite if someone won a multiplayer game"""
    def __init__(self, victor):
        message = _("Winner: %s") % victor.get_name()
        MessageSprite.__init__(self, message)

def main():
    # Initialise screen
    pygame.init()
    pygame.font.init()
    if not pygame.font.get_init():
        print ("Could not initialize fonts")
    camera_area = pygame.Rect (0, 0, 1024, 700)
    screen = pygame.display.set_mode((camera_area.width, camera_area.height))
    pygame.display.set_caption(_('Darting Frogs'))

    # Initialise joysticks
    print ("Joystick count:", pygame.joystick.get_count())
    for i in range (pygame.joystick.get_count()):
        pygame.joystick.Joystick(i).init()

    play_again = True
    while play_again:
        play_again = multiplayer_race (screen, camera_area)

def multiplayer_race (screen, camera_area) -> bool:
    """Each call of this function runs one complete game, from waiting for
    players until game over.

    Returns true if there should be another game. When the escape key is
    pressed, this returns false.
    """
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0x40, 0x80, 0x40))

    # Initialise players
    players = []
    new_players_can_join = PlayersCanJoinMessage()
    game_over_sprite = None
    distance_covered = 0
    distance_until_next_hazard = GameConstants.road_width
    # The text saying how far the frogs have gone
    next_milestone = GameConstants.milestone_distance

    # Initialise sprite groups
    frog_sprites = pygame.sprite.Group(players)
    # Scenery isn't dangerous (but includes roads, which spawn hazards)
    scenery_sprites = pygame.sprite.Group()
    # Hazard sprites are the ones that will kill colliding frogs
    hazard_sprites = pygame.sprite.Group()
    # Message sprites are overlayed over everything else
    message_sprites = pygame.sprite.Group()
    message_sprites.add (new_players_can_join)

    # Initialise clock and RNG
    clock = pygame.time.Clock()
    random_number_generator = random.Random()

    # For the first screen, generate some roads
    grass = random_number_generator.randint (1, 4)
    for x in range (1, 4):
        if x != grass:
            road = Road (hazard_sprites, Rect(0, x * GameConstants.road_width, camera_area.width, GameConstants.road_width))
            scenery_sprites.add (road)
            road.update()

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Event loop
    while 1:
        # Make sure game doesn't run at more than 60 frames per second
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    return False
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN or event.type == JOYBUTTONDOWN:
                already_controls_a_frog = False
                for player in players:
                    if player.test_input_matches (event):
                        already_controls_a_frog = True
                        player.jump()
                if not already_controls_a_frog:
                    if new_players_can_join.alive():
                        frog = PlayerFrog (input_event=event, column=len(players), distance_align=-distance_until_next_hazard)
                        players.append (frog)
                        frog_sprites.add (frog)
                        frog.jump()
                        message_sprites.add (EachJoiningPlayerMessage (frog))
                    else:
                        # todo: show that the new-player phase has ended
                        pass

            elif event.type == KEYUP or event.type == MOUSEBUTTONUP or event.type == JOYBUTTONUP:
                for player in players:
                    if player.test_input_matches (event):
                        player.rest()

        # Find out where the frogs are, calculate whether the screen should scroll
        screen_scroll = 0
        bounds = get_bounding_box (frog_sprites)
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
            # Jumpy scroll if someone is almost off-screen
            if bounds.top < GameConstants.furthest_single_tick_jump:
                screen_scroll += GameConstants.furthest_single_tick_jump - bounds.top
        # In a single-player game, the screen always scrolls
        if len (frog_sprites) == 1 and screen_scroll == 0 and not new_players_can_join.alive():
            screen_scroll = 1
        # When the game over message is being displayed, the screen scrolls continually. This
        # scrolls at a fixed speed, it's no problem if a frog jumps off the top of the screen.
        if game_over_sprite != None:
            screen_scroll = 3

        # Screen scroll is really moving everything downwards
        for entity in frog_sprites:
            entity.rect.move_ip (0, screen_scroll)
        for entity in scenery_sprites:
            entity.rect.move_ip (0, screen_scroll)
        for entity in hazard_sprites:
            entity.rect.move_ip (0, screen_scroll)
        for entity in message_sprites:
            entity.rect.move_ip (0, screen_scroll)

        # If any frogs are at the back of the screen, move them
        if screen_scroll:
            distance_covered += screen_scroll
            distance_until_next_hazard -= screen_scroll
            for player in players:
                if player.rect.bottom + screen_scroll >= camera_area.height:
                    player.jump_forced()

        # Scrolling the screen may introduce a new hazard or hazard-spawning scenery
        if distance_until_next_hazard <= 0:
            distance_until_next_hazard += GameConstants.road_width
            hazard = random_number_generator.choice (("grass", "road", "road"))
            if hazard == "road":
                road = Road (hazard_sprites, Rect(0, -distance_until_next_hazard, camera_area.width, GameConstants.road_width))
                scenery_sprites.add (road)

        if distance_covered >= next_milestone:
            milestone = MessageSprite (_("Distance: %d") % next_milestone)
            message_sprites.add (milestone)
            next_milestone += GameConstants.milestone_distance

        message_sprites.update()
        hazard_sprites.update()
        scenery_sprites.update()
        frog_sprites.update()

        offscreenRemoval = []
        for entity in scenery_sprites:
            if entity.rect.top > camera_area.height:
                offscreenRemoval.append (entity)
        for entity in hazard_sprites:
            if entity.rect.top > camera_area.height:
                offscreenRemoval.append (entity)
        for entity in message_sprites:
            if entity.rect.top > camera_area.height:
                offscreenRemoval.append (entity)
        for entity in offscreenRemoval:
            entity.kill()
        if game_over_sprite and not game_over_sprite.alive():
            return True

        # Now check for collisions
        for player in frog_sprites:
            hit = pygame.sprite.spritecollide (player, hazard_sprites, False, collided=pygame.sprite.collide_mask)
            if (hit):
                player.kill()
                new_players_can_join.kill()
        # Check for game over
        if (not frog_sprites) and (not new_players_can_join.alive()):
            if not game_over_sprite:
                game_over_sprite = MessageSprite (_("GAME OVER (distance %d)") % distance_covered)
                message_sprites.add (game_over_sprite)
        # Check for victory in multiplayer, if there is exactly one frog still alive
        if len (frog_sprites) == 1 and len (players) > 1:
            if not game_over_sprite:
                for player in players:
                    if player.alive():
                        game_over_sprite = VictoryMessage (player)
                        message_sprites.add (game_over_sprite)

        screen.blit(background, (0, 0))
        scenery_sprites.draw(screen)
        hazard_sprites.draw(screen)
        frog_sprites.draw(screen)
        message_sprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
