#!/usr/bin/python3
#
# Copyright (C) 2019 Steve Cotton (Octalot)
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

try:
    from enum import IntEnum
    import gettext
    import pygame
    from pygame.locals import SRCALPHA
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)

class MultiLineMessageSprite(pygame.sprite.Sprite):
    """General support for showing text on screen"""
    def __init__(self, messages, fontsize=None, firstLineSize=None, fontColor=None):
        """messages should be an array of strings, each string will become one on-screen line. If
        fontsize is given it will override the default size, if firstLineSize is given then it will
        override the default size for the first line only.
        """
        pygame.sprite.Sprite.__init__(self)
        if fontsize is None:
            fontsize = 20
        font = pygame.font.SysFont(None, fontsize)
        if firstLineSize is None:
            firstFont = font
        else:
            firstFont = pygame.font.SysFont(None, firstLineSize)
        if fontColor is None:
            fontColor = (255, 255, 255)
        height = firstFont.get_linesize() + (len(messages) - 1) * font.get_linesize()
        width = firstFont.size(messages[0])[0]
        for x in messages:
            width = max(width, font.size(x)[0])
        self.image = pygame.Surface ((width, height), flags=SRCALPHA)
        self.rect = self.image.get_rect()
        for x in [0]:
            renderedText = firstFont.render (messages[x], True, fontColor)
            self.image.blit(renderedText, (0, 0))
            nextTop = firstFont.get_linesize()
        for x in range(1, len(messages)):
            renderedText = font.render (messages[x], True, fontColor)
            self.image.blit(renderedText, (0, nextTop))
            nextTop += font.get_linesize()

class MessageSprite(MultiLineMessageSprite):
    """A single line of text"""
    def __init__(self, message, fontsize=None):
        if fontsize is None:
            fontsize = 40
        MultiLineMessageSprite.__init__(self, [message], fontsize)

class PlayersCanJoinMessage(MultiLineMessageSprite):
    """The text that any key joins the game is a sprite, when it scrolls off
    screen is the time that players can't join any more

    The background doesn't need to be opaque, as it's easily readable on both
    road and grass scenery.

    There's a variation making the message that joyaxismotion isn't supported larger. That's
    triggered by passing the old PlayersCanJoinMessage as an argument, the new message puts itself
    on screen where the old one was.
    """
    def __init__(self, oldmessage=None):
        anyButton = _("Press any button or any key to get a frog (except escape, which quits)")
        noStick = _("On joysticks, only the buttons are supported, not the sticks or D-pad")
        if oldmessage is None:
            MultiLineMessageSprite.__init__(self, [anyButton, noStick], fontsize=20, firstLineSize=40)
        else:
            MultiLineMessageSprite.__init__(self, [noStick, anyButton], fontsize=20, firstLineSize=40, fontColor=(255, 120, 120))
            self.rect.midtop = oldmessage.rect.midtop

class EachJoiningPlayerMessage(pygame.sprite.Sprite):
    """Shown when a new player joins the game, to show which key or button controls which frog"""
    def __init__(self, frog):
        pygame.sprite.Sprite.__init__(self)
        message = frog.get_name()
        if len (message) == 1:
            fontsize = 50
        else:
            fontsize = 20
        font = pygame.font.SysFont(None, fontsize)
        renderedText = font.render (message, True, frog.get_color())
        with_border = renderedText.get_rect().inflate (10, 10)
        self.image = pygame.Surface (with_border.size, flags=SRCALPHA)
        self.image.fill ((0, 0, 0, 0x20))
        self.image.blit (renderedText, (5, 5))
        self.rect = self.image.get_rect()
        self.rect.centerx = frog.rect.centerx
        self.rect.top = frog.rect.centery

class VictoryMessage(MessageSprite):
    """Shown as the game_over_sprite if someone won a multiplayer game"""
    def __init__(self, victor):
        message = _("Winner: %s") % victor.get_name()
        MessageSprite.__init__(self, message)
