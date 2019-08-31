
import pygame
from NetworkBroadcast import Broadcast, AnimatedSprite, SoundAttr
from Sounds import EXPLOSION_SOUND


__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


class Explosion(pygame.sprite.Sprite):
    images = None
    containers = None

    def __init__(self, parent_, pos_,
                 gl_, timing_, layer_, texture_name_, mute_=False):

        self.layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)

        self.images_copy = Explosion.images.copy()
        self.image = self.images_copy[0] if isinstance(self.images_copy, list) else self.images_copy
        self.timing = timing_
        self.length = len(self.images) - 1
        self.pos = pos_
        self.gl = gl_
        self.position = pygame.math.Vector2(*self.pos)
        self.rect = self.image.get_rect(center=self.pos)
        self.dt = 0
        self.blend = pygame.BLEND_RGB_ADD
        self.parent = parent_
        self.index = 0
        self.id_ = id(self)
        self.texture_name = texture_name_
        self.mute = mute_
        # Create the network object
        self.explosion_object = Broadcast(self.make_object())
        # Create sound object
        self.explosion_sound_object = Broadcast(self.make_sound_object('EXPLOSION_SOUND'))

    def play_explosion_sound(self) -> None:
        """
        Play the sound explosion locally and forward the sound object to the client(s).

        :return: None
        """

        # play the sound locally
        self.gl.MIXER.play(sound_=EXPLOSION_SOUND, loop_=False, priority_=0,
                           volume_=1.0, fade_out_ms=0, panning_=True,
                           name_='EXPLOSION_SOUND', x_=self.rect.centerx,
                           object_id_=id(EXPLOSION_SOUND),
                           screenrect_=self.gl.SCREENRECT)
        # Add the sound object to the queue
        self.explosion_sound_object.play()

    def make_sound_object(self, sound_name_: str) -> SoundAttr:
        """
        Create a network sound object

        :param sound_name_: string; represent the sound name e.g 'EXPLOSION_SOUND"
        :return: SoundAttr object
        """
        assert isinstance(sound_name_, str), \
            "Positional argument <sound_name_> is type %s , expecting string." % type(sound_name_)

        if sound_name_ not in globals():
            raise NameError('Sound %s is not define.' % sound_name_)

        return SoundAttr(frame_=self.gl.FRAME, id_=self.id_, sound_name_=sound_name_, rect_=self.rect)

    def make_object(self) -> AnimatedSprite:
        return AnimatedSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.texture_name,
                              layer_=self.layer, blend_=self.blend, rect_=self.rect,
                              index_=self.index)
        
    def update(self):

        if self.dt > self.timing:

            if self.rect.colliderect(self.gl.SCREENRECT):

                if self.index == 0 and not self.mute:
                    self.play_explosion_sound()

                self.image = self.images_copy[self.index]
                self.rect = self.image.get_rect(center=self.rect.center)
                self.index += 1

                if self.index > self.length:
                    self.kill()

                self.dt = 0

            else:
                self.kill()

        # update the network object every frames to avoid flickering appearance
        # on client side.
        if self.rect.colliderect(self.gl.SCREENRECT):
            self.explosion_object.update({'frame': self.gl.FRAME,
                                          'rect': self.rect,
                                          'index': self.index,
                                          'blend': self.blend})
            self.explosion_object.queue()

        self.dt += self.gl.TIME_PASSED_SECONDS
