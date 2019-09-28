import pygame
from random import randint, uniform
from math import degrees, atan2
from NetworkBroadcast import Broadcast, RotateSprite, DeleteSpriteCommand

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


# Create an instance and display a shooting stars onto a specific layer
# The sprite is display using blend additive mode and the
# refreshing rate is by default 16ms
class ShootingStar(pygame.sprite.Sprite):

    image = None        # sprite surface (single surface)
    containers = None   # sprite group to use

    def __init__(self,
                 gl_,           # global variables
                 layer_=-4,     # layer where the shooting sprite will be display
                 timing_=16,    # refreshing rate, default is 16ms (60 fps)
                 surface_name_=''
                 ):

        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        # change sprite layer
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.images_copy = ShootingStar.image.copy()
        self.image = self.images_copy[0] if isinstance(ShootingStar.image, list) else self.images_copy
        self.w, self.h = pygame.display.get_surface().get_size()
        self.position = pygame.math.Vector2(randint(0, self.w), randint(-self.h, 0))
        self.rect = self.image.get_rect(midbottom=self.position)
        self.speed = pygame.math.Vector2(uniform(-30, 30), 60)
        self.rotation = -270 - int(degrees(atan2(self.speed.y, self.speed.x)))
        self.image = pygame.transform.rotozoom(self.image, self.rotation, 1)
        self.blend = pygame.BLEND_RGB_ADD
        self.timing = timing_
        self.gl = gl_
        self.dt = 0
        self.surface_name = surface_name_
        self.id_ = id(self)
        self.shooting_star_object = Broadcast(self.make_object())

        Broadcast.add_object_id(self.id_)

    def delete_object(self) -> DeleteSpriteCommand:
        """
        Send a command to kill an object on client side.

        :return: DetectCollisionSprite object
        """
        return DeleteSpriteCommand(frame_=self.gl.FRAME, to_delete_={self.id_: self.surface_name})

    def make_object(self) -> RotateSprite:
        return RotateSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                            layer_=self.layer, blend_=self.blend, rect_=self.rect,
                            rotation_=self.rotation)

    def quit(self) -> None:
        Broadcast.remove_object_id(self.id_)
        obj = Broadcast(self.delete_object())
        obj.queue()
        self.kill()

    def update(self):

        if self.dt > self.timing:

            if self.rect.centery > self.h:
                self.quit()
                return
            self.rect = self.image.get_rect(center=self.position)
            self.position += self.speed
            if self.rect.colliderect(self.gl.SCREENRECT):
                self.shooting_star_object.update({'frame': self.gl.FRAME,
                                                  'rect': self.rect, 'rotation': self.rotation})
                self.shooting_star_object.queue()

            self.dt = 0

        else:
            self.dt += self.gl.TIME_PASSED_SECONDS




