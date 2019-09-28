# encoding: utf-8

import warnings
import numpy
from numpy import array, arange, repeat, newaxis, linspace
import pygame
import random
from random import randint

from TextureTools import make_array, make_surface
from Textures import LIFE_HUD, LIFE_HUD_DEAD, VARIABLE_TEXTURE

warnings.filterwarnings('ignore')


class HorizontalBar:

    def __init__(self,
                 start_color: pygame.Color,  # pygame.Color (left color on the gradient bar)
                 end_color: pygame.Color,    # pygame.Color (right color on the gradient bar)
                 max_: int,                  # Max value (e.g maximum life, maximum energie etc)
                 min_: int,                  # Min value (e.g minimum life etc)
                 value_: int,                # Actual value
                 start_color_vector: tuple,  # Allow color variations on RGG,
                 # (1, 0, 0) -> Allow red color variations over the time
                 end_color_vector: tuple,    # Allow color variations on RGB
                 alpha: bool,                # bool, allow bar transparency
                 height: int,                # bar's height
                 xx: int,                    # bar's length
                 scan: bool = True):         # Scan effect True | False
        """

        :param start_color:
        :param end_color:
        :param max_:
        :param min_:
        :param value_:
        :param start_color_vector:
        :param end_color_vector:
        :param alpha:
        :param height:
        :param xx:
        :param scan:
        """
        self.START_COLOR = pygame.math.Vector3(*start_color[:3])
        self.END_COLOR = pygame.math.Vector3(*end_color[:3])
        if max_ == 0:
            raise ValueError('Positional argument max_ value is incorrect, got %s ' % max_)
        self.MAX = max_
        self.MIN = min_
        self.VALUE = value_
        self.height = height
        if xx == 0:
            raise ValueError('Positional argument xx value is incorrect, got %s ' % xx)
        self.FACTOR = self.MAX / xx
        self.start_color_vector = pygame.math.Vector3(*start_color_vector)
        self.end_color_vector = pygame.math.Vector3(*end_color_vector)
        self.alpha_value = alpha
        self.display_color = pygame.Color(255, 255, 255, 255)
        pygame.font.init()
        self.font_ = pygame.font.SysFont("arial", 10, 'bold')
        self.logic_compilation = []
        self.scan = scan

        if self.start_color_vector.length() != 0:
            self.start_variance = True
        else:
            self.start_variance = False
        if self.end_color_vector.length() != 0:
            self.end_variance = True
        else:
            self.end_variance = False

        self.scan_index = randint(0, 20)
        self.scan_surface = pygame.image.load('Assets\\icon_glareFx.png')
        self.scan_surface = pygame.transform.smoothscale(self.scan_surface, (50, self.height))
        self.scan_surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
        self.orange = pygame.Color(255, 132, 64, 255)
        self.red = pygame.Color(255, 0, 0, 255)
        self.white = pygame.Color(255, 255, 255, 255)
        self.w, self.h = self.VALUE // self.FACTOR, self.height
        self.alpha_array = self.alpha()

    def horizontal_gradient(self) -> numpy.ndarray:
        """
        Create a radiant of RGB values from two given colors (start_color, end_color)

        :return: numpy.ndarray, Array containing RGB values that can be converted into
            a pygame surface
        """
        # todo if end_Color and start_color stay the same over the time then
        #  color_diff should be declare in the contructor

        # substract two colors of type pygame.math.Vector3d (R, G, B, A)
        # Result correpond to the color difference between start en end
        # When VALUE equal MAX then diff_ is unchanged and correspond to the color shift.
        # If VALUE equal 1/2 MAX then diff_ values are divided by 2 etc..
        # e.g start[255, 0, 0] - end[0, 255, 0] -> diff_ = [-255, 255, 0]
        color_diff = (array(self.END_COLOR) -
                      array(self.START_COLOR)) * self.VALUE / self.MAX
        self.w, self.h = self.VALUE // self.FACTOR, self.height
        if self.w == 0:
            return numpy.ndarray((0, 0))
        row = arange(self.w) / self.w
        row = repeat(row[:, newaxis], [3], 1)
        diff_ = repeat(color_diff[newaxis, :], [self.w], 0)
        row = array(self.START_COLOR) + (diff_ * row)
        row = row[:, newaxis, :]
        rgb_array = repeat(row[:, :], [self.h], 1)
        return rgb_array

    def alpha(self) -> numpy.ndarray:
        """

        :return: numpy.ndarray, Array containing alpha values that can be converted to a pygame surface
        when assembling rgb_array and alpha values
        """
        # create gradiant alpha values from 255 to 50 (full opacity 255 to the
        # left and minimal transparency to the right (50)
        row = linspace(255, 50, int(self.w), dtype=float)
        row = repeat(row[:, newaxis], [1], 0)
        row = row[:, newaxis, :]
        alpha_array = repeat(row[:, :], [self.h], 1)
        return alpha_array

    def display_value(self) -> pygame.Surface:
        """
        This creates a new Surface with the specified text rendered on it.

        :return: pygame.Surface, render(text, antialias, color, background=None)
        This creates a new Surface with the specified text rendered on it.
        """
        half_max = self.MAX / 2

        if half_max < self.VALUE < self.MAX:
            self.display_color = self.orange

        elif self.MIN < self.VALUE < half_max:
            self.display_color = self.red

        else:
            self.display_color = self.white

        # draw text on a new surface render(text, antialias, color, background=None)
        return self.font_.render(str(self.VALUE), False, self.display_color)

    def display_gradient(self) -> pygame.Surface:
        """
        Return a pygame.Surface representing the player life/energy progress bar

        Surface length is relative to the player's life or energy values.
        if value is < or equal to zero, return an empty surface.
        The bar can be transparent or opaque, control the setting with positional argument alpha.
        You can add an animated blend scan effect to the bar with the optional argument scan.
        Start color (left side of the bar) and end color (right side of the bar) car varies over the
        time by adjusting the positional color vectors self.start_color_vector and self.end_color_vector
        e.g start color (255, 0, 0) and ending color (0, 255, 0) by adjusting end_color_vector=(0, 1, 0)
        you will allow only the green color to change over the time. Setting the end_color_vector = (0, 0, 0),
        cancel all variations (this is also true for start_color_vector = (0, 0, 0))

        :return: Return a pygame.Surface representing the player life/energy progress bar
        """

        if self.VALUE > 1:

            # Get the array
            rgb_array = self.horizontal_gradient()

            # checking the array shape
            if not (rgb_array.shape[0] > 0 and rgb_array.shape[1] > 0):
                # array shape is too small, leaving
                return pygame.Surface((0, 0))

            if self.start_variance:
                if self.START_COLOR.length() > 0:
                    if self.START_COLOR.x > 255 or self.START_COLOR.x < 0:
                        self.start_color_vector.x *= -1
                    if self.START_COLOR.y > 255 or self.START_COLOR.y < 0:
                        self.start_color_vector.y *= -1
                    if self.START_COLOR.z > 255 or self.START_COLOR.z < 0:
                        self.start_color_vector.z *= -1
                self.START_COLOR += self.start_color_vector

            if self.end_variance:
                if self.END_COLOR.length() > 0:
                    if self.END_COLOR.x > 255 or self.END_COLOR.x < 0:
                        self.end_color_vector.x *= -1
                    if self.END_COLOR.y > 255 or self.END_COLOR.y < 0:
                        self.end_color_vector.y *= -1
                    if self.END_COLOR.z > 255 or self.END_COLOR.z < 0:
                        self.end_color_vector.z *= -1
                self.END_COLOR += self.end_color_vector

            if self.scan:
                if self.scan_index < rgb_array.shape[0] - 1:
                    self.scan_index += 2
                else:
                    self.scan_index = 0

            # The bar is translucent.
            # We are using the algorithm make_surface to
            # combine alpha values and rgb values into a surface.
            if self.alpha_value:
                surface_array = make_array(rgb_array, self.alpha_array[:rgb_array.shape[0]])
                bar = make_surface(surface_array).convert_alpha()

                if self.scan:
                    bar.blit(self.scan_surface, (self.scan_index, 0), special_flags=pygame.BLEND_RGB_ADD)

            # The bar is not translucent,
            else:
                bar = pygame.surfarray.make_surface(rgb_array)
                bar.convert(32, pygame.RLEACCEL)
                if self.scan:
                    bar.blit(self.scan_surface,
                             (self.scan_index, 0), special_flags=pygame.BLEND_RGB_ADD)

            return bar

        else:
            return pygame.Surface((0, 0))


class ShowLifeBar(pygame.sprite.Sprite, HorizontalBar):
    containers = None
    life_hud = LIFE_HUD

    def __init__(self,
                 gl_,  # class game global variables
                 player_,  # player instance
                 left_gradient_,  # pygame.Color
                 right_gradient,  # pygame.Color
                 scan_: bool = True,  # True | False
                 pos_: tuple = (0, 0),  # position (x, y) where the bar will be display
                 timing_: int = 15,  # timing/refreshing time 15ms is 60FPS
                 ):
        assert isinstance(timing_, int), \
            print('Positional argument <timing_> expecting integer, got %s ' % type(timing_))
        if timing_ < 0:
            raise ValueError('Positional argument timing_ cannot be < 0')

        assert isinstance(pos_, tuple), \
            print('Positional argument <pos_> should be a tuple, got %s ' % type(pos_))
        if not (isinstance(pos_[0], int) or isinstance(pos_[1])):
            raise ValueError('Positional argument <pos_> has incorrect values, expecting int got %s ' % pos_)
        if not gl_.SCREENRECT.collidepoint(pos_):
            raise ValueError('Lifebar cannot be display outside the active display.')

        pygame.sprite.Sprite.__init__(self, self.containers)
        HorizontalBar.__init__(self,
                               start_color=left_gradient_,
                               end_color=right_gradient,
                               max_=player_.max_life, min_=0,
                               value_=player_.life,
                               start_color_vector=(0, 0, 0),
                               end_color_vector=(0, 0, 0),
                               alpha=False,
                               height=32,       # bar width
                               xx=180,          # Bar length
                               scan=scan_)

        self.VALUE = player_.life
        self.image = self.display_gradient()
        w, h = self.image.get_size()
        surf = pygame.Surface((w, h)).convert()
        surf.fill((0, 0, 0, 0))
        self.surf = surf
        self.life_hud = ShowLifeBar.life_hud
        self.life_hud_copy = self.life_hud.copy()
        self.rect = self.image.get_rect(topleft=pos_)
        self.player = player_
        self.gl = gl_
        self.dt = 0
        self.timing = timing_
        self.pos = pos_
        self.counter = 0
        self.dim = len(VARIABLE_TEXTURE) - 1

    def update(self):

        if self.dt > self.timing:

            self.image = self.life_hud_copy.copy()

            if self.player.alive():
                self.VALUE = self.player.life
                self.image.blit(self.surf, (83, 21))
                self.image.blit(self.display_gradient(), (83, 21))
                self.image.blit(self.display_value(), (84, 29))

                if self.image is not None:
                    self.rect = self.image.get_rect(topleft=self.pos)
                else:
                    self.image = LIFE_HUD_DEAD.copy()

            else:
                self.image = LIFE_HUD_DEAD.copy()

            # Create a flame effect on the life_hud skin
            self.image.blit(
                VARIABLE_TEXTURE[self.counter % self.dim], (0, 0))

            self.dt = 0
            self.counter += 1
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS


if __name__ == '__main__':

    pygame.init()
    SCREENRECT = pygame.Rect(0, 0, 600, 600)
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)

    life_bar = HorizontalBar(start_color=pygame.Color(255, 0, 0, 0),
                             end_color=pygame.Color(0, 255, 0, 0),
                             max_=5000, min_=0,
                             value_=5000,
                             start_color_vector=(0, 0, 0), end_color_vector=(0, 0, 0), alpha=False, height=32, xx=220,
                             scan=True)

    clock = pygame.time.Clock()

    # sprite_group = pygame.sprite.Group()
    # All = pygame.sprite.RenderUpdates()

    TIME_PASSED_SECONDS = 0

    STOP_GAME = False

    FRAME = 0
    life_ = 5000
    while not STOP_GAME:

        screen.fill((128, 128, 130, 0))
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT:
                print('Quitting')
                STOP_GAME = True

            if keys[pygame.K_LEFT]:
                life_ -= 10 if life_ >= 10 else 0

            if keys[pygame.K_RIGHT]:
                life_ += 10 if life_ <= 5000 - 10 else 0

            if keys[pygame.K_SPACE]:
                pass

            if event.type == pygame.MOUSEMOTION:
                MOUSE_POS = event.pos

        life_bar.VALUE = life_
        life = life_bar.display_gradient()
        if life is not None:
            screen.blit(life, (0, 0))
            screen.blit(life_bar.display_value(),
                        (SCREENRECT.w >> 1, SCREENRECT.h >> 1))

        TIME_PASSED_SECONDS = clock.tick(300)
        # print(clock.get_fps())

        pygame.display.flip()
        FRAME += 1
        # life_ += 1
    pygame.quit()
