
import pygame
from NetworkBroadcast import Broadcast, StaticSprite
from random import randint
from Textures import CL1, CL2

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


# Draw backgrounds
class Background(pygame.sprite.Sprite):

    containers = None   # pygame group
    image = None        # surface to display (can be a list of Surface or a single pygame.Surface)

    def __init__(self,
                 vector_: pygame.math.Vector2,       # background speed vector (pygame.math.Vector2)
                 position_: pygame.Vector2,          # original position (tuple)
                 gl_,                    # global variables  (GL class)
                 layer_: int = -8,       # layer used default is -8 (int <= 0)
                 blend_: int = 0,        # pygame blend effect (e.g pygame.BLEND_RGB_ADD, or int)
                 event_name_: str = ''   # event name (str)
                 ):

        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        # change sprite layer
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.images_copy = Background.image.copy()
        self.image = self.images_copy[0] if isinstance(Background.image, list) else self.images_copy
        self.rect = self.image.get_rect(topleft=position_)
        self.position = position_
        self.vector = vector_
        self.gl = gl_
        self.blend = blend_
        self.event_name = event_name_
        self.id_ = id(self)
        self.background_object = Broadcast(self.make_object())

    def make_object(self) -> StaticSprite:
        return StaticSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.event_name,
                            layer_=self.layer, blend_=self.blend, rect_=self.rect)

    def update(self):

        self.rect.move_ip(self.vector)

        if self.event_name == 'CL1':
            if self.rect.y > 1023:
                self.rect.y = randint(-1024, - CL1.get_height())
                self.rect.x = randint(-400, 400)
            self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
            self.background_object.queue()

        elif self.event_name == 'CL2':
            if self.rect.y > 1023:
                self.rect.y = randint(-1024, - CL2.get_height())
                self.rect.x = randint(-400, 400)
            self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
            self.background_object.queue()
        else:
            if self.rect.y > 1023:
                self.rect.y = -1024
            if self.event_name == 'BACK1_S':
                self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
                self.background_object.queue()
            else:
                self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
                self.background_object.queue()
