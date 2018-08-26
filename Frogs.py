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

        The colors will be distinguishable from green (the color of the grass).
        """
        number = 0
        if self.event_type == KEYDOWN:
            number = self.key
        elif self.event_type == MOUSEBUTTONDOWN:
            number = self.button
        elif self.event_type == JOYBUTTONDOWN:
            number = self.button * 14 + self.joy

        # Either red or blue or both must be present, so that the color isn't green
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
    """Common class for both player-controlled frogs and AI-controlled frogs

    Each frog will have a team-color. Player frogs also have key or button to make them jump.
    """

    class State(Enum):
        """A still frog is not moving. A jumping frog moves based on self.stateStep and GameConstants.frog_jump_movement"""
        still = 1
        jump = 2

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
        self.image = TeamColorPainter.load_image(__class__.sprites_files[0], team_color)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        screen = pygame.display.get_surface()
        self.state = Frog.State.still
        self.stateStep = 0;
        self.stateNext = Frog.State.still

        # Place the frog on screen.  The game aligns everything vertically to (top of screen + a
        # multiple of jump_length), newly-created frogs start at a vertically-aligned point.
        if placement_hint == Frog.PlacementHint.player:
            # Player frogs start on-screen, about a jump from the bottom of the screen.
            self.rect.top = distance_align + (int (screen.get_rect().height / GameConstants.jump_length) - 1) * GameConstants.jump_length
        else:
            # AI frogs start off-screen, and so will be jump_forced() on to the screen
            self.rect.top = distance_align + (int (screen.get_rect().height / GameConstants.jump_length) + 1) * GameConstants.jump_length

        # Place the frog horizontally.  The screen is split vertically in to the left 25% (left AI
        # area), middle 50% (player area) and right 25% (right AI area).  Player frogs go in the
        # middle area, AI frogs go in the left and right margins, so both groups have an area that's
        # 50% of the screen width.  If there's an absurd number of players, the algorithm starts
        # putting them on the left again.
        frog_width = self.rect.width
        placement_area_width = int (screen.get_rect().width / 2) - frog_width
        frog_placement = self.rect.width * column % placement_area_width
        # The boundary between the left AI area and the player area
        player_area_left = int (screen.get_rect().width / 4)
        screen_centerx = int (screen.get_rect().width / 2)
        if placement_hint == Frog.PlacementHint.player:
            self.rect.left = player_area_left + frog_placement
        else:
            if frog_placement + frog_width < player_area_left:
                self.rect.left = frog_placement
            else:
                self.rect.left = screen_centerx + frog_placement

    def update(self):
        """If the frog is jumping, move and update the state. If not jumping (or at the end of a
        jump), change to the next state (which may be the same as the current state.

        If the state is State.still after this method returns, subclasses are allowed to call it a
        multiple times.  Particularly the way that AiFrog uses it is allowed.
        """

        if self.state == Frog.State.jump and self.stateStep < len(GameConstants.frog_jump_movement):
            # The scrolling code should keep frogs on screen
            self.rect.move_ip (0, GameConstants.frog_jump_movement[self.stateStep])
            self.stateStep = self.stateStep + 1
        else:
            self.state = self.stateNext
            self.stateStep = 0

    def get_name(self):
        return self.name

    def jump(self):
        """Change to a different sprite, and move up the screen"""
        self.stateNext = Frog.State.jump

    def jump_forced(self):
        """Make a single jump, but do not change self.stateNext, so frogs in State.still will stop
        after one jump.

        Frogs at the back of the screen are forced to jump so that they don't scroll off the bottom.

        The AiFrog also uses this function to jump once, so the frog doesn't jump a second time
        until triggered again by the AI logic.
        """
        self.state = Frog.State.jump
        self.stateStep = 0
        # Does not change self.stateNext, State.still frogs will stop after one jump

    def rest(self):
        self.stateNext = Frog.State.still

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

    def update(self):
        Frog.update(self)
        if self.state == Frog.State.still:
            if Frog.State.jump == self.random_number_generator.choice ((Frog.State.still, Frog.State.jump)):
                self.jump_forced()
                Frog.update(self)

    def test_input_matches(self, event):
        return False

if __name__ == '__main__':
    from DartingFrogs import main
    # Do the import before the print, because it also sets up gettext
    print (_("Hint: the main file is DartingFrogs.py"))
    main()
