
import pygame
from NetworkBroadcast import Broadcast, AnimatedSprite, DeleteSpriteCommand
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
                    return

                self.dt = 0
                self.player_halo_object.update({'frame': self.gl.FRAME,
                                                'rect': self.rect, 'index': self.index})

            else:
                self.kill()
                return
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        self.player_halo_object.queue()


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

        Broadcast.add_object_id(self.id_)

    def delete_object(self) -> DeleteSpriteCommand:
        """
        Send a command to kill an object on client side.

        :return: DetectCollisionSprite object
        """
        return DeleteSpriteCommand(frame_=self.gl.FRAME, to_delete_={self.id_: self.texture_name})

    def make_object(self) -> AnimatedSprite:
        return AnimatedSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.texture_name,
                              layer_=self.layer, blend_=self.blend, rect_=self.rect,
                              index_=self.index)

    def quit(self) -> None:
        Broadcast.remove_object_id(self.id_)
        obj = Broadcast(self.delete_object())
        obj.queue()
        self.kill()

    def update(self) -> None:

        if self.dt > self.timing:

            if self.object.rect.colliderect(self.gl.SCREENRECT):

                self.image = self.images_copy[self.index]
                self.rect = self.image.get_rect(center=self.object.rect.center)
                self.index += 1
                if self.index > self.length:
                    self.quit()
                    return

                self.asteroidHalo_object.update(
                    {'frame': self.gl.FRAME, 'rect': self.rect, 'index': self.index})
                self.asteroidHalo_object.queue()

                self.dt = 0

            else:
                self.quit()
                return
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS


