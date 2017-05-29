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

"""This is intended to allow as many players as required.  While the frogs are still on the first screen,
pressing any normal key adds a frog that will jump when that key is pressed
again.
"""
try:
    import sys
    import random
    import pygame
    from pygame.locals import *
    from GameConstants import GameConstants
    from Hazards import Road
    from Utils import *
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

class InputTest:
    """An instance of this can be created for any key or button, the matches() function will then
    return true if a new event happens on the same key or button. It's a comparison ignoring whether
    the event type is an UP or DOWN event.
    """
    def getDownType(event):
        if event.type == KEYUP:
            return KEYDOWN
        elif event.type == MOUSEBUTTONUP:
            return MOUSEBUTTONDOWN
        elif event.type == JOYBUTTONUP:
            return JOYBUTTONDOWN
        else:
            return event.type

    def __init__(self, event):
        self.event_type = __class__.getDownType (event)
        if self.event_type == KEYDOWN:
            self.key = event.key
        elif event.type == MOUSEBUTTONDOWN:
            self.button = event.button
        elif event.type == JOYBUTTONDOWN:
            self.joy = event.joy
            self.button = event.button
        else:
            raise RuntimeError ("Uncontrolled frog (no associated keyboard key, mouse button or joystick button")

    def matches(self, event):
        if self.event_type != __class__.getDownType (event):
            return False
        elif self.event_type == KEYDOWN:
            return self.key == event.key
        elif self.event_type == MOUSEBUTTONDOWN:
            return self.button == event.button
        elif self.event_type == JOYBUTTONDOWN:
            return self.joy == event.joy and self.button == event.button
        else:
            return False

    def describe_name(self):
        if self.event_type == KEYDOWN:
            return pygame.key.name (self.key)
        elif self.event_type == MOUSEBUTTONDOWN:
            return "mouse button %d" % self.button
        elif self.event_type == JOYBUTTONDOWN:
            return "joystick %d button %d" % (self.joy, self.button)
        else:
            raise RuntimeError ("Uncontrolled frog (no associated keyboard key, mouse button or joystick button")

    def get_team_color(self):
        """A very weak hash-like function, which returns a Color representing this input; this is
        intended to be used for the frog colors, so that the same key or button gets the same color
        of frog across games.

        The colors will distinguishable from green.
        """
        number = 0
        if self.event_type == KEYDOWN:
            number = self.key
        elif self.event_type == MOUSEBUTTONDOWN:
            number = self.button
        elif self.event_type == JOYBUTTONDOWN:
            number = self.button * 14 + self.joy

        # Either red or blue or both must be present, so the color isn't green
        red, blue = 0, 0
        if number % 5 == 0:
            red = 0xc0
        elif number % 5 == 1:
            blue = 0xc0
        elif number % 5 == 2:
            red = 0x80
        elif number % 5 == 3:
            blue = 0x80
        else:
            red = 0x60
            blue = 0x60
        green = 0x40 + 0x10 * (number % 8)

        return pygame.Color (red, green, blue, 255)

class Frog(pygame.sprite.Sprite):
    """Each frog will have a key or button to make it jump, and a team-color"""

    sprites_files = ['frog_resting.png', 'frog_jump.png']

    def __init__(self, input_event, team_color=None, column=0, distance_align=0):
        pygame.sprite.Sprite.__init__(self)
        self.input_test = InputTest (input_event)
        self.name = self.input_test.describe_name()
        team_color = self.input_test.get_team_color()
        print ("Creating a new frog for input", self.input_test.describe_name(), "in column", column)
        self.image, self.rect = load_png(__class__.sprites_files[0], team_color)
        self.mask = pygame.mask.from_surface(self.image)
        screen = pygame.display.get_surface()
        self.state = "still"
        self.stateStep = 0;
        self.stateNext = "still";
        # The game aligns everything to (top of screen + a multiple of jump_length), frogs start
        # at an aligned point that's about a jump from the bottom of the screen.
        self.rect.top = distance_align + ((screen.get_rect().height / GameConstants.jump_length) - 1) * GameConstants.jump_length
        # The frogs should be in the center vertically, not at the left or right.  If there's an
        # absurd number of players, the modulus puts them back to the left.
        self.rect.centerx = screen.get_rect().width / 4 + self.rect.width * column % (screen.get_rect().width / 2)

    def update(self):
        if self.state == "jump" and self.stateStep < len(GameConstants.frog_jump_movement):
            # The scrolling code should keep frogs on screen
            self.rect.move_ip (0, GameConstants.frog_jump_movement[self.stateStep])
            self.stateStep = self.stateStep + 1
        else:
            self.state = self.stateNext
            self.stateStep = 0

    def test_input_matches(self, event):
        return self.input_test.matches (event)

    def get_name(self):
        return self.name

    def jump(self):
        """Change to a different sprite, and move up the screen"""
        self.stateNext = "jump"

    def jump_forced(self):
        """Frogs at the back of the screen are forced to jump so that they don't scroll off the
        bottom."""
        self.state = "jump"
        self.stateStep = 0
        # Does not change self.stateNext, "still" frogs will stop after one jump

    def rest(self):
        self.stateNext = "still"

class MessageSprite(pygame.sprite.Sprite):
    """A single line of text"""
    def __init__(self, message):
        pygame.sprite.Sprite.__init__(self)
        font = pygame.font.SysFont(None, 40)
        self.image = font.render (message, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.rect.centerx = screen.get_size()[0] / 2

class NewPlayersJoinMessage(MessageSprite):
    """The text that any key joins the game is a sprite, when it scrolls off
    screen is the time that players can't join any more
    """
    def __init__(self):
        message = "Press any button or any key to get a frog (except escape, which quits)"
        MessageSprite.__init__(self, message)

class VictoryMessage(MessageSprite):
    """Shown as the game_over_sprite if someone won a multiplayer game"""
    def __init__(self, victor):
        message = "Winner: %s" % victor.get_name()
        MessageSprite.__init__(self, message)

def main():
    # Initialise screen
    pygame.init()
    pygame.font.init()
    if not pygame.font.get_init():
        print ("Could not initialize fonts")
    camera_area = pygame.Rect (0, 0, 1024, 700)
    screen = pygame.display.set_mode((camera_area.width, camera_area.height))
    pygame.display.set_caption('Multiplayer frog race')

    # Initialise joysticks
    print ("Joystick count:", pygame.joystick.get_count())
    for i in range (pygame.joystick.get_count()):
        pygame.joystick.Joystick(i).init()

    play_again = True
    while play_again:
        play_again = multiplayer_race (screen, camera_area)

def multiplayer_race (screen, camera_area) -> bool:
    """One complete loop of the game, until game over.
    Returns true if there should be another game"""
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0x40, 0x80, 0x40))

    # Initialise players
    players = []
    new_players_can_join = NewPlayersJoinMessage()
    game_over_sprite = None
    distance_covered = 0
    distance_until_next_hazard = GameConstants.road_width
    # The text saying how far the frogs have gone
    next_milestone = GameConstants.milestone_distance

    # Initialise sprite groups
    player_sprites = pygame.sprite.Group(players)
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
                        frog = Frog (input_event=event, column=len(players), distance_align=-distance_until_next_hazard)
                        players.append (frog)
                        player_sprites.add (frog)
                        frog.jump()
                    else:
                        # todo: show that the new-player phase has ended
                        pass

            elif event.type == KEYUP or event.type == MOUSEBUTTONUP or event.type == JOYBUTTONUP:
                for player in players:
                    if player.test_input_matches (event):
                        player.rest()

        # Find out where the frogs are, calculate whether the screen should scroll
        screen_scroll = 0
        bounds = get_bounding_box (player_sprites)
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
        if game_over_sprite != None:
            screen_scroll = 3

        # Screen scroll is really moving everything downwards
        for entity in player_sprites:
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
            milestone = MessageSprite ("Distance: %d" % next_milestone)
            message_sprites.add (milestone)
            next_milestone += GameConstants.milestone_distance

        message_sprites.update()
        hazard_sprites.update()
        scenery_sprites.update()
        player_sprites.update()

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
        for player in player_sprites:
            hit = pygame.sprite.spritecollide (player, hazard_sprites, False, collided=pygame.sprite.collide_mask)
            if (hit):
                player.kill()
                new_players_can_join.kill()
        if (not player_sprites) and (not new_players_can_join.alive()):
            if not game_over_sprite:
                game_over_sprite = MessageSprite ("GAME OVER (distance %d)" % distance_covered)
                message_sprites.add (game_over_sprite)
        # Check for victory in multiplayer, if there is one frog still alive
        if len (player_sprites) == 1 and len (players) > 1:
            if not game_over_sprite:
                for player in players:
                    if player.alive():
                        game_over_sprite = VictoryMessage (player)
                        message_sprites.add (game_over_sprite)

        screen.blit(background, (0, 0))
        scenery_sprites.draw(screen)
        hazard_sprites.draw(screen)
        player_sprites.draw(screen)
        message_sprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__': main()
