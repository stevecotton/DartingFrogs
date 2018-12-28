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

"""Handling for the frog sprites and player inputs."""

try:
    from enum import Enum
    import sys
    import random
    import pygame
    from pygame.locals import *
    from GameConstants import GameConstants
    from Utils import TeamColorPainter
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
            return _("mouse button %d") % self.button
        elif self.event_type == JOYBUTTONDOWN:
            return _("joystick %d button %d") % (self.joy, self.button)
        else:
            raise RuntimeError ("Uncontrolled frog (no associated keyboard key, mouse button or joystick button")

    def get_team_color(self):
        """A very weak hash-like function, which returns a Color representing this input; this is
        intended to be used for the frog colors, so that the same key or button gets the same color
        of frog across games.

        The colors will be distinguishable from dark-green (the color of the grass).
        """
        number = 0
        if self.event_type == KEYDOWN:
            number = self.key
        elif self.event_type == MOUSEBUTTONDOWN:
            number = self.button
        elif self.event_type == JOYBUTTONDOWN:
            number = self.button * 14 + self.joy

        hashtool = random.Random(number)
        hue = hashtool.randint(0, 359)
        # Around green (hue=120), use only bright colors with low saturation
        if 60 < hue and hue < 180:
            saturation = hashtool.randint(0, 40)
            value = hashtool.randint(70, 100)
        else:
            saturation = hashtool.randint(50, 100)
            value = hashtool.randint(50, 90)
        color = pygame.Color(0, 0, 0, 255)
        color.hsva = (hue, saturation, value, 100)

        return color

class Frog(pygame.sprite.Sprite):
    """Common class for both player-controlled frogs and AI-controlled frogs

    Each frog will have a team-color. Player frogs also have key or button to make them jump.
    """

    class State(Enum):
        """A still frog is not moving. A frog in either of the jump_ states moves."""
        still = 1
        jump_repeat = 2 # when this jump finishes, jump again until rest() is called
        jump_and_stop = 3 # when this jump finishes, change to State.still

    class PlacementHint(Enum):
        """The players need to be able to see cars coming from both left and right, so
        player-controlled frogs should be in the center vertically.  AI frogs can see cars
        offscreen, so can be in the left and right margins.
        """
        player = 1
        ai = 2

    sprites_files = ['frog_resting.png', 'frog_jump.png']

    def __init__(self, name, team_color, placement_hint, column=0, distance_align=0):
        pygame.sprite.Sprite.__init__(self)
        print ("Creating a new frog for", name, "in column", column)
        self.name = name
        self.team_color = team_color
        self.image = TeamColorPainter.load_image(__class__.sprites_files[0], team_color)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        screen = pygame.display.get_surface()
        self.state = Frog.State.still
        self.stateStep = 0;

        # Place the frog on screen.  The game aligns everything vertically to (top of screen + a
        # multiple of jump_length), newly-created frogs start at a vertically-aligned point.
        if placement_hint == Frog.PlacementHint.player:
            # Player frogs start on-screen, about a jump from the bottom of the screen.
            self.rect.top = distance_align + (int (screen.get_rect().height / GameConstants.jump_length) - 1) * GameConstants.jump_length
        else:
            # AI frogs start off-screen, and so will be jump_forced() on to the screen
            self.rect.top = distance_align + (int (screen.get_rect().height / GameConstants.jump_length) + 1) * GameConstants.jump_length

        # Place the frog horizontally.  There are four placement areas: left AI area, left player
        # area, right player area, right AI area. The "/ 5" is because keeping all players in the
        # middle 40% of the screen lets the players at the edge see more.  If there's an absurd
        # number of players, the algorithm starts putting them near the center again.
        frog_width = self.rect.width
        placement_area_width = int (screen.get_rect().width / 5) - frog_width
        use_left_side = column % 2
        offset_from_center = (frog_width * int (column / 2)) % placement_area_width
        screen_centerx = int (screen.get_rect().width / 2)
        if placement_hint == Frog.PlacementHint.ai:
            offset_from_center += placement_area_width
        if use_left_side:
            self.rect.left = screen_centerx + offset_from_center
        else:
            self.rect.left = screen_centerx - offset_from_center - frog_width

    def update(self):
        """If the frog is jumping, move and update the state. Each jump is handled by multiple calls
        to update(), which is tracked by the self.stateStep and GameConstants.frog_jump_movement.

        If the state is State.still after this method returns, subclasses are allowed to call it a
        multiple times.  Particularly the way that AiFrog uses it is allowed.
        """

        if self.state in (Frog.State.jump_and_stop, Frog.State.jump_repeat) and self.stateStep < len(GameConstants.frog_jump_movement):
            # The scrolling code should keep frogs on screen
            self.rect.move_ip (0, GameConstants.frog_jump_movement[self.stateStep])
            self.stateStep = self.stateStep + 1
        elif self.state == Frog.State.jump_repeat:
            self.stateStep = 0
        elif self.state == Frog.State.jump_and_stop:
            self.state = Frog.State.still
            self.stateStep = 0

    def get_name(self):
        return self.name

    def get_color(self):
        return self.team_color

    def jump(self):
        """Start moving, and keep moving until rest() is called. Change to a different sprite, and
        move up the screen. The logic may be deferred until the update() method.
        """
        self.state = Frog.State.jump_repeat

    def jump_forced(self):
        """Jump, but stop after one jump (unless the frog is already in jump_repeat state).

        Frogs at the back of the screen are forced to jump so that they don't scroll off the bottom.

        The AiFrog also uses this function to jump once, so the frog doesn't jump a second time
        until triggered again by the AI logic.
        """
        if self.state == Frog.State.still:
            self.state = Frog.State.jump_and_stop
            self.stateStep = 0

    def rest(self):
        if self.state == Frog.State.jump_repeat:
            self.state = Frog.State.jump_and_stop

class PlayerFrog(Frog):
    """A frog controlled by a player (instead of a computer-controlled frog)"""
    def __init__(self, input_event, column=0, distance_align=0):
        input_test = InputTest (input_event)
        name = input_test.describe_name()
        team_color = input_test.get_team_color()
        Frog.__init__(self, name, team_color, Frog.PlacementHint.player, column, distance_align)
        self.input_test = input_test

    def test_input_matches(self, event):
        return self.input_test.matches (event)

class AiFrog(Frog):
    """A computer-controlled frog"""
    def __init__(self, input_event, column=0, distance_align=0):
        name = _("AI %d") % column
        team_color = pygame.Color (255, 0, 255, 255)
        Frog.__init__(self, name, team_color, Frog.PlacementHint.ai, column, distance_align)
        self.random_number_generator = random.Random()
        self.ai_pause = 0

    def update(self):
        Frog.update(self)
        if self.state == Frog.State.still:
            if self.ai_pause == 0:
                self.ai_pause = self.random_number_generator.randint (1, 5)
                self.jump_forced()
                Frog.update(self)
            else:
                self.ai_pause -= 1

    def test_input_matches(self, event):
        return False

if __name__ == '__main__':
    from DartingFrogs import main
    # Do the import before the print, because it also sets up gettext
    print (_("Hint: the main file is DartingFrogs.py"))
    main()
