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
    """There's no separate title screen, it's just something that's shown on top of the grass area
    before any players join.
    """
    def __init__(self, messages, fontsize=None, firstLineSize=None):
        pygame.sprite.Sprite.__init__(self)
        if fontsize is None:
            fontsize = 20
        font = pygame.font.SysFont(None, fontsize)
        if firstLineSize is None:
            firstFont = font
        else:
            firstFont = pygame.font.SysFont(None, firstLineSize)
        height = firstFont.get_linesize() + (len(messages) - 1) * font.get_linesize()
        width = 0
        for x in messages:
            width = max(width, font.size(x)[0])
        self.image = pygame.Surface ((width, height), flags=SRCALPHA)
        self.rect = self.image.get_rect()
        for x in [0]:
            renderedText = firstFont.render (messages[x], True, (255, 255, 255))
            self.image.blit(renderedText, (0, 0))
            nextTop = firstFont.get_linesize()
        for x in range(1, len(messages)):
            renderedText = font.render (messages[x], True, (255, 255, 255))
            self.image.blit(renderedText, (0, nextTop))
            nextTop += font.get_linesize()

class MessageSprite(MultiLineMessageSprite):
    """A single line of text"""
    def __init__(self, message, fontsize=None):
        if fontsize is None:
            fontsize = 40
        MultiLineMessageSprite.__init__(self, [message], fontsize)

class PlayersCanJoinMessage(MessageSprite):
    """The text that any key joins the game is a sprite, when it scrolls off
    screen is the time that players can't join any more

    The background doesn't need to be opaque, as it's easily readable on both
    road and grass scenery.
    """
    def __init__(self):
        message = _("Press any button or any key to get a frog (except escape, which quits)")
        MessageSprite.__init__(self, message)

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
        self.image = font.render (message, True, frog.get_color())
        self.rect = self.image.get_rect()
        self.rect.centerx = frog.rect.centerx
        self.rect.top = frog.rect.centery

class VictoryMessage(MessageSprite):
    """Shown as the game_over_sprite if someone won a multiplayer game"""
    def __init__(self, victor):
        message = _("Winner: %s") % victor.get_name()
        MessageSprite.__init__(self, message)