
import pygame
from NetworkBroadcast import Broadcast, AnimatedSprite
from Textures import HALO_SPRITE12, HALO_SPRITE14, HALO_SPRITE13

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


class PlayerHalo(pygame.sprite.Sprite):

    images = []
    containers = None

    def __init__(self, texture_name_, object_, timing_, layer_=0):

        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(object_.gl.All, pygame.sprite.LayeredUpdates):
            object_.gl.All.change_layer(self, object_.layer)

        self.object = object_

        if isinstance(self.images, pygame.Surface):
            self.images = [self.images] * 30

        self.images_copy = self.images.copy()
        self.image = self.images_copy[0]

        self.rect = self.image.get_rect(center=object_.rect.center)
        self.dt = 0
        self.index = 0
        self.gl = object_.gl
        self.length = len(self.images) - 1
        self.blend = 0
        self.timing = timing_
        self.texture_name = texture_name_
        self.id_ = id(self)
        self.player_halo_object = Broadcast(self.make_object())

    def make_object(self) -> AnimatedSprite:
        return AnimatedSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.texture_name,
                              layer_=self.layer, blend_=self.blend, rect_=self.rect,
                              index_=self.index)

    def update(self):

        if self.dt > self.timing:

            if self.object.rect.colliderect(self.gl.SCREENRECT):

                self.image = self.images_copy[self.index]
                self.rect = self.image.get_rect(center=self.object.rect.center)
                self.index += 1
                if self.index > self.length:
                    self.kill()

                self.dt = 0

            else:
                self.kill()

        if self.rect.colliderect(self.gl.SCREENRECT):
            self.player_halo_object.update({'frame': self.gl.FRAME, 'rect': self.rect, 'index': self.index})
            self.player_halo_object.queue()

        self.dt += self.gl.TIME_PASSED_SECONDS


class AsteroidHalo(pygame.sprite.Sprite):

    images = []
    containers = None

    def __init__(self, texture_name_, object_, timing_, layer_=0):

        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(object_.gl.All, pygame.sprite.LayeredUpdates):
            object_.gl.All.change_layer(self, object_.layer)

        self.object = object_

        if isinstance(self.images, pygame.Surface):
            self.images = [self.images] * 30

        self.images_copy = self.images.copy()
        self.image = self.images_copy[0]

        if not id(AsteroidHalo.images) == id(eval(texture_name_)):
            raise ValueError("Asteroid image does not match with its surface name.")

        self.rect = self.image.get_rect(center=object_.rect.center)
        self.dt = 0
        self.index = 0
        self.gl = object_.gl
        self.length = len(self.images) - 1
        self.blend = 0
        self.timing = timing_
        self.texture_name = texture_name_
        self.id_ = id(self)
        self.asteroidHalo_object = Broadcast(self.make_object())

    def make_object(self) -> AnimatedSprite:
        return AnimatedSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.texture_name,
                              layer_=self.layer, blend_=self.blend, rect_=self.rect,
                              index_=self.index)

    def update(self) -> None:

        if self.dt > self.timing:

            if self.object.rect.colliderect(self.gl.SCREENRECT):

                self.image = self.images_copy[self.index]
                self.rect = self.image.get_rect(center=self.object.rect.center)
                self.index += 1
                if self.index > self.length:
                    self.kill()

                self.dt = 0

            else:
                self.kill()

        if self.rect.colliderect(self.gl.SCREENRECT):
            self.asteroidHalo_object.update(
                {'frame': self.gl.FRAME, 'rect': self.rect, 'index': self.index})
            self.asteroidHalo_object.queue()

        self.dt += self.gl.TIME_PASSED_SECONDS
