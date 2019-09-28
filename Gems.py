import math
import pygame
from numpy import array
from random import randint, uniform
from Textures import GEM_SPRITES
from math import cos, sin, atan2


class MakeGems(pygame.sprite.Sprite):

    containers = None
    GEM_VALUE = array(list(range(1, 22))) * 22
    inventory = set()

    def __new__(cls, gl_,
                player_,
                object_,
                ratio_: float = 1.0,
                timing_: int = 15,
                offset_: pygame.Rect = None,
                layer_: int = -1, *args, **kwargs):

        if id(object_) in cls.inventory:
            return
        else:
            return super().__new__(cls, *args, **kwargs)

    def __init__(self,
                 gl_,
                 player_,
                 object_,
                 ratio_: float = 1.0,
                 timing_: int = 15,
                 offset_: pygame.Rect = None,
                 layer_: int = -1):
        """

        :param gl_: GL class contains all the game constants
        :param player_: Player instance P1 or P2
        :param object_: Object being destroyed producing gems
        :param ratio_: float, must be > 0.Surface ration. 1.0 normal size
        :param timing_: integer; must be > 0. Refreshing rate e.g 15ms 60 fps
        :param offset_: pygame.Rect; Offset from the object center
        :param layer_:  integer; must be < 0. Layer used by the gems
        """

        if type(object_).__name__ not in ('Asteroid', 'MirroredAsteroidClass'):
            raise TypeError('Positional argument <object_> must be a class Asteroid, got %s ' % type(object_))
        assert isinstance(ratio_, float), \
            'Positional argument <ratio_> must be an float type, got %s ' % type(ratio_)
        if ratio_ <= 0:
            raise ValueError("Positional argument <ratio_> must be > 0, got %s " % ratio_)
        assert isinstance(offset_, pygame.Rect), \
            'Positional argument <offset_> must be a pygame.Rect type, got %s ' % type(offset_)
        assert isinstance(layer_, int), \
            'Positional argument <layer_> must be an integer type, got %s ' % type(layer_)
        if layer_ > 0:
            raise ValueError("Positional argument <layer_> must be < 0, got %s " % layer_)
        assert isinstance(timing_, int), \
            'Positional argument <timing_> must be an integer type, got %s ' % type(timing_)
        if timing_ < 0:
            raise ValueError("Positional argument <timing_> must be > 0, got %s " % timing_)

        self.gl = gl_
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(self.gl.All, pygame.sprite.LayeredUpdates):
            self.gl.All.change_layer(self, layer_)

        self.object_ = object_
        self.timing = timing_
        self.offset = offset_
        self.player = player_

        gem_number = randint(0, len(GEM_SPRITES) - 1)
        self.value = int(self.GEM_VALUE[gem_number])
        self.image = GEM_SPRITES[gem_number]
        self.image_copy = self.image.copy()

        # randomly modify the surface orientation
        self.image = pygame.transform.rotate(self.image, randint(0, 360))
        # todo create all mask and put them into a list prior instantiation
        self.mask = pygame.mask.from_surface(self.image)

        self.ratio = ratio_

        if self.offset is not None:
            # display the sprite at a specific location.
            self.rect = self.image.get_rect(center=self.offset.center)
        else:
            # use player location
            self.rect = self.image.get_rect(center=self.object_.rect.center)

        self.speed = pygame.math.Vector2(0, randint(25, 35))

        self.dt = 0
        self.theta = 0
        self.blend = 0
        angle = math.radians(uniform(0, 359))
        self.vector = pygame.math.Vector2(
            math.cos(angle) * randint(10, 20),
            math.sin(angle) * randint(10, 20))

        self.inventory.add(id(object_))

    def adjust_vector(self) -> tuple:
        # return a tuple (x:float, y:float); vector direction
        angle_radian = -atan2(self.player.rect.centery - self.rect.centery,
                              self.player.rect.centerx - self.rect.centerx)
        return cos(angle_radian) * self.speed.length(), -sin(angle_radian) * self.speed.length()

    def quit(self) -> None:
        if id(self.object_) in self.inventory:
            self.inventory.remove(id(self.object_))
        self.kill()

    def update(self) -> None:

        if self.player.alive():

            if self.dt > self.timing:

                if self.gl.SCREENRECT.colliderect(self.rect):

                    # self.image = pygame.transform.rotozoom(self.image_copy, self.theta, self.ratio)
                    self.image = pygame.transform.rotate(self.image_copy, self.theta)
                    self.rect = self.image.get_rect(center=self.rect.center)

                    # self.rect.move_ip(self.speed.x, self.speed.y)

                    # gems follow player
                    if self.vector.length() < 2:
                        self.rect.move_ip(self.adjust_vector())
                    # Gems spread 360 degrees
                    else:
                        self.rect.move_ip((self.vector.x, self.vector.y))
                        self.vector *= 0.95     # deceleration/ reduction

                    self.theta += 2
                    self.theta %= 359

                else:
                    
                    self.quit()
                    return
                """
                if pygame.sprite.collide_mask(self, self.player):
                    self.player.update_score(self.value)
                    self.kill()
                    return
                """
                if self.rect.colliderect(self.player):
                    if hasattr(self.player, 'update_score'):
                        self.player.update_score(self.value)
                    self.quit()
                    return
                self.dt = 0

            else:
                self.dt += self.gl.TIME_PASSED_SECONDS
        else:
            self.quit()
