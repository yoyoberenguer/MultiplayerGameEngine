# encoding: utf-8

from copy import deepcopy
from random import randint

from TextureTools import spread_sheet_per_pixel, spread_sheet_fs8
from TextureTools import hue_surface, wave_x, hge

__author__ = "Yoann Berenguer"
__copyright__ = "Copyright 2007, Cobra Project"
__credits__ = ["Yoann Berenguer"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"

import pygame
from pygame import freetype
import os
from numpy import linspace, repeat, newaxis, dstack, uint8


class LayeredUpdatesModified(pygame.sprite.LayeredUpdates):

    def __init__(self):
        pygame.sprite.LayeredUpdates.__init__(self)

    def draw(self, surface_):
        """draw all sprites in the right order onto the passed surface

        LayeredUpdates.draw(surface): return Rect_list

        """
        spritedict = self.spritedict
        surface_blit = surface_.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]

            if hasattr(spr, '_blend') and spr._blend is not None:
                newrect = surface_blit(spr.image, spr.rect, special_flags=spr._blend)
            else:
                newrect = surface_blit(spr.image, spr.rect)

            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty


class GL:
    buffers = {}
    ...


class PlayerLost(pygame.sprite.Sprite):
    containers = None
    DIALOGBOX_READOUT_RED = None
    SKULL = None

    def __init__(self, gl_, font_, image_, layer_, timing_=15):

        self._layer = layer_
        pygame.sprite.Sprite.__init__(self, PlayerLost.containers)

        self.screen = pygame.display.get_surface()
        self.screenrect = self.screen.get_rect()
        self.image = image_
        self.image_copy = image_
        self.rect = self.image.get_rect(
            topleft=((self.screenrect.w >> 1) - (self.image.get_width() >> 1),
                     (self.screenrect.h >> 1) - (self.image.get_height() >> 1)))
        self.inc = 0
        self.red = pygame.Color(255, 24, 18, 0)
        self.red_rect = self.rect.copy()
        self.red_rect1 = self.rect.copy()
        self.red_rect1.inflate_ip(-100, -100)
        self.red_rect2 = self.rect.copy()
        self.red_rect2.inflate_ip(-200, -200)
        self.red_rect_default = self.red_rect1.copy()
        self.dt = 0
        self.timing = timing_
        self.gl = gl_

        # Load the buffered image
        if 'PlayerLost' in gl_.buffers:
            self.image = gl_.buffers['PlayerLost']
            self.glitch = gl_.buffers['PLAYERLOST_GLITCH']
        else:
            self.font = font_
            self.w2, self.h2 = self.screenrect.w >> 1, self.screenrect.h >> 1
            self.image.blit(PlayerLost.SKULL, (self.rect.w // 2 - PlayerLost.SKULL.get_width() // 2,
                                               self.rect.h // 2 - PlayerLost.SKULL.get_height() // 2),
                            special_flags=pygame.BLEND_RGBA_ADD)
            self.image_rescale = pygame.transform.smoothscale(self.image,
                                                              (self.image.get_width() >> 1,
                                                               self.image.get_height() >> 1))
            self.glitch = hge(self.image_rescale, 0.1, 0.1, 10).convert()
            self.glitch.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
            self.glitch = pygame.transform.scale2x(self.glitch)
            rect1 = self.font.get_rect("game over", style=freetype.STYLE_NORMAL, size=35)
            self.font.render_to(self.image, (self.rect.w // 2 - rect1.w // 2, 125), "game over",
                                fgcolor=pygame.Color(220, 30, 25), size=35)
            # put the processed images into a buffer
            gl_.buffers['PlayerLost'] = memoryview(self.image.copy().get_view('3'))
            gl_.buffers['PLAYERLOST_GLITCH'] = memoryview(self.glitch.copy().get_view('3'))

    def update(self):

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            self.image.blit(PlayerLost.DIALOGBOX_READOUT_RED[self.inc % len(PlayerLost.DIALOGBOX_READOUT_RED) - 1],
                            (80, 105), special_flags=pygame.BLEND_RGB_ADD)

            pygame.draw.rect(self.screen, self.red, self.red_rect, 2)
            pygame.draw.rect(self.screen, self.red, self.red_rect1, 2)
            pygame.draw.rect(self.screen, self.red, self.red_rect2, 2)

            if not self.screenrect.contains(self.red_rect):
                self.red_rect = self.red_rect_default.copy()

            if not self.screenrect.contains(self.red_rect1):
                self.red_rect1 = self.red_rect_default.copy()

            if not self.screenrect.contains(self.red_rect2):
                self.red_rect2 = self.red_rect_default.copy()

            self.red_rect.inflate_ip(4, 4)
            self.red_rect1.inflate_ip(4, 4)
            self.red_rect2.inflate_ip(4, 4)

            self.image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

            if randint(0, 1000) > 950:
                self.image = self.glitch

            self.inc += 1
            self.dt = 0

        else:
            self.dt += self.gl.TIME_PASSED_SECONDS


class PlayerWin(pygame.sprite.Sprite):
    containers = None

    def __init__(self, font_, image_, layer_):

        self._layer = layer_
        pygame.sprite.Sprite.__init__(self, PlayerWin.containers)

        self.screen = pygame.display.get_surface()
        self.screenrect = self.screen.get_rect()
        self.image = image_
        self.image_copy = image_
        self.rect = self.image.get_rect(
            topleft=((self.screenrect.w >> 1) - (self.image.get_width() >> 1),
                     (self.screenrect.h >> 1) - (self.image.get_height() >> 1)))
        self.inc = 0
        self.green = pygame.Color(25, 124, 88, 0)
        self.red_rect = self.rect.copy()
        self.red_rect1 = self.rect.copy()
        self.red_rect1.inflate_ip(-100, -100)
        self.red_rect2 = self.rect.copy()
        self.red_rect2.inflate_ip(-200, -200)
        self.red_rect_default = self.red_rect1.copy()
        self.font = font_
        self.w2, self.h2 = self.screenrect.w >> 1, self.screenrect.h >> 1

    def update(self):

        self.image = self.image_copy.copy()

        self.image.blit(DIALOGBOX_READOUT[self.inc % len(DIALOGBOX_READOUT) - 1],
                        (80, 105), special_flags=pygame.BLEND_RGB_ADD)

        pygame.draw.rect(self.screen, self.green, self.red_rect, 2)
        pygame.draw.rect(self.screen, self.green, self.red_rect1, 2)
        pygame.draw.rect(self.screen, self.green, self.red_rect2, 2)

        if not self.screenrect.contains(self.red_rect):
            self.red_rect = self.red_rect_default.copy()

        if not self.screenrect.contains(self.red_rect1):
            self.red_rect1 = self.red_rect_default.copy()

        if not self.screenrect.contains(self.red_rect2):
            self.red_rect2 = self.red_rect_default.copy()

        self.red_rect.inflate_ip(4, 4)
        self.red_rect1.inflate_ip(4, 4)
        self.red_rect2.inflate_ip(4, 4)

        rect1 = self.font.get_rect("stage clear", style=freetype.STYLE_NORMAL, size=35)
        self.font.render_to(self.image, (self.rect.w // 2 - rect1.w // 2, 125), "stage clear",
                            fgcolor=pygame.Color(60, 205, 64), size=35)
        xx = 200
        x = self.rect.left + 100
        self.font.render_to(self.image, (100, xx), "clear bonus",
                            fgcolor=pygame.Color(247, 255, FRAME % 156), size=18)
        xx += 50
        self.font.render_to(self.image, (100, xx), "kill ratio",
                            fgcolor=pygame.Color(247, 255, FRAME % 156), size=18)
        xx += 50
        self.font.render_to(self.image, (100, xx), "gems collected",
                            fgcolor=pygame.Color(247, 255, FRAME % 156), size=18)
        xx += 50
        self.font.render_to(self.image, (100, xx), "life remaining",
                            fgcolor=pygame.Color(247, 255, FRAME % 156), size=18)
        xx += 50
        self.font.render_to(self.image, (100, xx), "bombs remaining",
                            fgcolor=pygame.Color(247, 255, FRAME % 156), size=18)
        xx += 50
        self.image.blit(GR_LINE, (100, xx))
        xx += 50
        self.font.render_to(self.image, (100, xx), "total",
                            fgcolor=pygame.Color(247, 255, FRAME % 156), size=18)

        # self.image = hge(self.image, 0.1, 0.1, 20).convert()
        self.image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

        self.inc += 1


if __name__ == '__main__':

    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    GL.SCREENRECT = SCREENRECT
    # globalisation

    pygame.display.init()
    SCREEN = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)
    GL.screen = SCREEN
    pygame.init()
    clock = pygame.time.Clock()
    BACKGROUND = pygame.image.load('Assets\\background.jpg').convert()
    BACKGROUND = pygame.transform.smoothscale(BACKGROUND, (SCREENRECT.w, SCREENRECT.h))

    SKULL = pygame.image.load('Assets\\toxigineSkull_.png').convert()
    SKULL = pygame.transform.smoothscale(
        SKULL, (int(SKULL.get_width() * .8), int(SKULL.get_height() * .8)))
    SKULL.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    FINAL_MISSION = pygame.image.load('Assets\\container.png').convert()
    FINAL_MISSION = pygame.transform.smoothscale(
        FINAL_MISSION, (int(FINAL_MISSION.get_width() * .8), int(FINAL_MISSION.get_height() * .8)))
    FINAL_MISSION.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

    DIALOGBOX_READOUT = spread_sheet_fs8('Assets\\Readout_512x512_6x6_.png', 512, 6, 6)
    i = 0
    for surface in DIALOGBOX_READOUT:
        # surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
        DIALOGBOX_READOUT[i] = pygame.transform.smoothscale(
            surface, (FINAL_MISSION.get_width() - 150, FINAL_MISSION.get_height() - 150))
        DIALOGBOX_READOUT[i] = pygame.transform.flip(DIALOGBOX_READOUT[i], True, True)
        i += 1
    DIALOGBOX_READOUT_RED = spread_sheet_fs8('Assets\\Readout_512x512_6x6_red_.png', 512, 6, 6)
    i = 0
    for surface in DIALOGBOX_READOUT_RED:
        # surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
        DIALOGBOX_READOUT_RED[i] = pygame.transform.smoothscale(
            surface, (FINAL_MISSION.get_width() - 150, FINAL_MISSION.get_height() - 150))
        DIALOGBOX_READOUT_RED[i] = pygame.transform.flip(DIALOGBOX_READOUT_RED[i], True, True)
        i += 1

    line = pygame.Rect(0, 0, 700, 4)
    GR_LINE = pygame.Surface(line.size, depth=32, flags=(pygame.SWSURFACE | pygame.SRCALPHA))
    GR_LINE.fill((255, 255, 255, 255))
    rgb_array = pygame.surfarray.pixels3d(GR_LINE)
    gradient = linspace(255, 0, line.w)
    row = repeat(gradient[:, newaxis], [line.h], 1)

    array = dstack((rgb_array, row)).astype(dtype=uint8)
    # Create a line with alpha value coded in linear gradient degradation
    GR_LINE = pygame.image.frombuffer((array.transpose(1, 0, 2)).copy(order='C').astype(uint8),
                                      (array.shape[:2][0], array.shape[:2][1]), 'RGBA')
    GR_LINE = pygame.transform.smoothscale(GR_LINE, (380, GR_LINE.get_height()))
    i = 0
    FRAME = 0
    GL.FRAME = FRAME
    GL.PLAYER_GROUP = 0
    STOP_GAME = False
    QUIT = False

    font = freetype.Font('Assets\\Fonts\\Gtek Technology.ttf', size=14)

    All = LayeredUpdatesModified()

    PlayerLost.containers = All
    PlayerLost.DIALOGBOX_READOUT_RED = DIALOGBOX_READOUT_RED
    PlayerLost.SKULL = SKULL
    PlayerLost(gl_=GL, font_=font, image_=FINAL_MISSION, layer_=0)

    while not STOP_GAME:

        SCREEN.fill((0, 0, 0, 0))
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            STOP_GAME = True

        SCREEN.blit(BACKGROUND, (0, 0))

        All.update()
        All.draw(SCREEN)

        pygame.display.flip()
        TIME_PASSED_SECONDS = clock.tick(250)
        GL.TIME_PASSED_SECONDS = TIME_PASSED_SECONDS
        GL.FRAME = FRAME
        print(clock.get_fps())
        FRAME += 1

    pygame.quit()
