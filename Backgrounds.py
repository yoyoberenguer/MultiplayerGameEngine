
import pygame
from NetworkBroadcast import Broadcast, StaticSprite, RotateSprite, TransformSprite
from random import randint
from Textures import CL1, CL2, STATION, BLUE_PLANET

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
                 position_: pygame.math.Vector2,          # original position (tuple)
                 gl_,                    # global variables  (GL class)
                 layer_: int = -8,       # layer used default is -8 (int <= 0)
                 blend_: int = 0,        # pygame blend effect (e.g pygame.BLEND_RGB_ADD, or int)
                 event_name_: str = '',  # event name (str)
                 timing_=0
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
        self.rotation = 0
        self.timing = timing_
        self.dt = 0
        if self.event_name == 'STATION':
            self.rotation = 0
            self.background_object = Broadcast(self.make_rotation_object())
        else:
            self.background_object = Broadcast(self.make_object())

    def make_object(self) -> StaticSprite:
        return StaticSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.event_name,
                            layer_=self.layer, blend_=self.blend, rect_=self.rect)

    def make_rotation_object(self) -> RotateSprite:
        return RotateSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.event_name,
                            layer_=self.layer, blend_=self.blend, rect_=self.rect, rotation_=self.rotation)

    def process(self):

        if self.event_name == 'CL1':
            self.rect.move_ip(self.vector)
            if self.rect.y > 1023:
                self.rect.y = randint(-1024, - CL1.get_height())
                self.rect.x = randint(-400, 400)
            self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
            self.background_object.queue()

        elif self.event_name == 'CL2':
            self.rect.move_ip(self.vector)
            if self.rect.y > 1023:
                self.rect.y = randint(-1024, - CL2.get_height())
                self.rect.x = randint(-400, 400)
            self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
            self.background_object.queue()

        elif self.event_name == 'BLUE_PLANET':
            self.rect.move_ip(self.vector)
            if self.rect.y > 1023:
                self.rect.y = randint(-1024, - BLUE_PLANET.get_height())
                self.rect.x = randint(-400, 400)
            self.background_object.update({'frame': self.gl.FRAME,
                                           'rect': self.rect})
            self.background_object.queue()

        elif self.event_name == 'STATION':
            # below 8192 frames the station is not on sight

            if self.gl.FRAME < 12280:
                self.rect.move_ip(self.vector)

            # no need to rotate station if not on sight
            if self.rect.colliderect(self.gl.SCREENRECT):
                centre = self.rect.center
                self.image = pygame.transform.rotate(self.images_copy.copy(), self.rotation)
                self.rect = self.image.get_rect(center=centre)
                self.background_object.update({'frame': self.gl.FRAME,
                                               'rect': self.rect,
                                               'rotation': self.rotation})
                self.background_object.queue()
                self.rotation += 0.2

        else:
            if self.event_name in ('BACK1_S', 'BACK2_S'):
                self.rect.move_ip(self.vector)
                if self.rect.y > 1023:
                    self.rect.y = -1024

                self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
                self.background_object.queue()

            elif self.event_name == 'BACK3':
                if self.gl.FRAME < 12288:
                    self.rect.move_ip(self.vector)

                # if self.gl.FRAME > 12288:
                #    self.rect.y = 0

                self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
                self.background_object.queue()

            # Any other background type
            else:
                self.rect.move_ip(self.vector)
                if self.rect.y > 1023:
                    self.rect.y = -1024
                    self.rect.x = 0
                self.background_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
                self.background_object.queue()

    def update(self):

        if self.timing != 0:
            # update frequently
            if self.dt > self.timing:
                self.process()
                self.dt = 0
            else:
                self.dt += self.gl.TIME_PASSED_SECONDS

        # update every frames
        else:
            self.process()

