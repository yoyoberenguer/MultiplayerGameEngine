# encoding: utf-8

import warnings
warnings.filterwarnings('ignore')

import numpy
from numpy import array, arange, repeat, newaxis, linspace
import pygame
import random

from TextureTools import make_array, make_surface


class HorizontalBar:

    def __init__(self, start_color, end_color, max_, min_, value_,
                 start_color_vector, end_color_vector, alpha, height, xx, scan=True):

        self.START_COLOR = pygame.math.Vector3(*start_color[:3])
        self.END_COLOR = pygame.math.Vector3(*end_color[:3])
        self.MAX = max_
        self.MIN = min_
        self.VALUE = value_
        self.height = height
        self.FACTOR = self.MAX / xx
        self.start_color_vector = pygame.math.Vector3(*start_color_vector)
        self.end_color_vector = pygame.math.Vector3(*end_color_vector)
        self.alpha_value = alpha
        self.display_color = pygame.Color(255, 255, 255, 255)
        pygame.font.init()
        self.font_ = pygame.font.SysFont("arial", 10, 'bold')
        self.logic_compilation = []
        self.scan = scan

        # ----------------------------------------------------------------
        # Real time scan effect
        self.scan_index = random.randint(0, 20)
        self.scan_surface = pygame.image.load('Assets\\icon_glareFx.png').convert()
        self.scan_surface = pygame.transform.smoothscale(self.scan_surface, (50, self.height))
        # ----------------------------------------------------------------

    def horizontal_gradient(self):

        diff_ = (array(self.END_COLOR[:3]) - array(self.START_COLOR[:3])) * self.VALUE / self.MAX
        w, h = self.VALUE // self.FACTOR, self.height
        row = arange(w, dtype='float') / w
        row = repeat(row[:, newaxis], [3], 1)
        diff_ = repeat(diff_[newaxis, :], [w], 0)
        row = array(self.START_COLOR[:3]) + (diff_ * row).astype(dtype=numpy.float)
        row = row.astype(dtype=numpy.uint8)[:, newaxis, :]
        row = repeat(row[:, :], [h], 1)
        return row

    def display_value(self):
        if 500 < self.VALUE < 1000:
            self.display_color = pygame.Color(255, 132, 64, 255)
        elif 0 < self.VALUE < 500:
            self.display_color = pygame.Color(255, 0, 0, 255)
        else:
            self.display_color = pygame.Color(255, 255, 255, 255)
        return self.font_.render(str(self.VALUE), False, self.display_color)

    def alpha(self):
        w, h = self.VALUE // self.FACTOR, self.height
        row = linspace(255, self.alpha_value, self.VALUE / self.FACTOR, dtype='float')
        row = repeat(row[:, newaxis], [1], 0)
        row = row.astype(dtype=numpy.uint8)[:, newaxis, :]
        row = repeat(row[:, :], [h], 1)
        return row

    def display_gradient(self):
        if self.VALUE > 1:

            # Get the array
            row_ = self.horizontal_gradient()

            # checking the array shape
            if not (row_.shape[0] > 0 and row_.shape[1] > 0):
                # array shape is too small, leaving
                return None

            if self.START_COLOR.length() > 0:
                if self.START_COLOR.x > 255 or self.START_COLOR.x < 0:
                    self.start_color_vector.x *= -1
                if self.START_COLOR.y > 255 or self.START_COLOR.y < 0:
                    self.start_color_vector.y *= -1
                if self.START_COLOR.z > 255 or self.START_COLOR.z < 0:
                    self.start_color_vector.z *= -1
            if self.END_COLOR.length() > 0:
                if self.END_COLOR.x > 255 or self.END_COLOR.x < 0:
                    self.end_color_vector.x *= -1
                if self.END_COLOR.y > 255 or self.END_COLOR.y < 0:
                    self.end_color_vector.y *= -1
                if self.END_COLOR.z > 255 or self.END_COLOR.z < 0:
                    self.end_color_vector.z *= -1

            self.START_COLOR += self.start_color_vector
            self.END_COLOR += self.end_color_vector

            if self.scan_index < row_.shape[0] - 1:
                self.scan_index += 2
            else:
                self.scan_index = 0

            # The bar is translucent.
            # We are using the algorithm make_surface to
            # combine alpha values and rgb values into a surface.
            if self.alpha_value:
                rgba_array = make_array(row_, self.alpha())
                bar = make_surface(rgba_array).convert_alpha()

                if self.scan:
                    bar.blit(self.scan_surface, (self.scan_index, 0), special_flags=pygame.BLEND_RGB_ADD)

            # The bar is not translucent,
            else:
                bar = pygame.surfarray.make_surface(row_).convert()
                if self.scan:
                    bar.blit(self.scan_surface,
                             (self.scan_index, 0), special_flags=pygame.BLEND_RGB_ADD)

            return bar

        else:
            return None


if __name__ == '__main__':

    pygame.init()
    SCREENRECT = pygame.Rect(0, 0, 1024, 1024)
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)

    life_bar = HorizontalBar(start_color=pygame.Color(0, 7, 255, 0),
                             end_color=pygame.Color(120, 255, 255, 0),
                             max_=5000, min_=0,
                             value_=2500,
                             start_color_vector=(0, 1, 0), end_color_vector=(0, 0, 0), alpha=False, height=32, xx=500,
                             scan=True)

    clock = pygame.time.Clock()

    # sprite_group = pygame.sprite.Group()
    # All = pygame.sprite.RenderUpdates()

    TIME_PASSED_SECONDS = 0

    STOP_GAME = False

    FRAME = 0
    life_ = 2500
    while not STOP_GAME:

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT:
                print('Quitting')
                STOP_GAME = True

            if keys[pygame.K_SPACE]:
                pass
            if event.type == pygame.MOUSEMOTION:
                MOUSE_POS = event.pos

        life_bar.VALUE = life_
        life = life_bar.display_gradient()
        screen.blit(life, (SCREENRECT.w >> 1, SCREENRECT.h >> 1))
        screen.blit(life_bar.display_value(),
                    (SCREENRECT.w >> 1, SCREENRECT.h >> 1))

        TIME_PASSED_SECONDS = clock.tick(300)
        # print(clock.get_fps())

        pygame.display.flip()
        FRAME += 1
        #life_ += 1
    pygame.quit()
