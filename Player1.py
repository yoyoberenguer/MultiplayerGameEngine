# encoding: utf-8
import os

from pygame import freetype

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


import random
import socket
import _pickle as cpickle
import threading
import time
import copyreg

try:
    import pygame
except ImportError:
    print("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")
    raise SystemExit

try:
    import lz4.frame
except ImportError:
    print("\n<lz4> library is missing on your system."
          "\nTry: \n   C:\\pip install lz4 on a window command prompt.")
    raise SystemExit

try:

    from CreateHalo import PlayerHalo
    from SoundServer import SoundControl
    from TextureTools import *
    from NetworkBroadcast import Broadcast, EventAttr, StaticSprite, AnimatedSprite, SoundAttr, BlendSprite
    from Explosions import Explosion
    from LayerModifiedClass import LayeredUpdatesModified
    import GLOBAL
    from GLOBAL import GL
    from ShootingStars import ShootingStar
    from AfterBurners import AfterBurner

except ImportError:
    print("\nOne or more game libraries is missing on your system."
          "\nDownload the source code from:\n"
          "https://github.com/yoyoberenguer/MultiplayerGameEngine.git")
    raise SystemExit


# socket.setdefaulttimeout(0)


def unserialize_event(is_set: threading.Event) -> threading.Event:
    """
    Set the internal flag to true. All threads waiting for it to become true are awakened.
    Return a threading event set to True

    :param is_set: threading event
    :return: return a threading event set to true.

    >>> event_ = threading.Event()
    >>> u_event = unserialize_event(event_)
    >>> assert isinstance(u_event, threading.Event)
    >>> event_.set()
    >>> event_.isSet()
    True
    >>> u_event = unserialize_event(event_)
    >>> u_event.isSet()
    True
    >>> event_.clear()
    >>> u_event = unserialize_event(event_)
    >>> u_event.isSet()
    True
    """

    assert isinstance(is_set, threading.Event), \
        print("Positional argument <is_set> is type %s , expecting threading.Event." % type(is_set))
    event_ = threading.Event()
    if is_set:
        event_.set()
    return event_


def serialize_event(e: threading.Event) -> tuple:
    """

    :param e: threading event
    :return: <function unserialize_event>, True or False


    >>> event_ = threading.Event()
    >>> s = serialize_event(event_)
    >>> assert isinstance(s, tuple)
    >>> u, v = list(s)
    >>> assert isinstance(u, type(unserialize_event))
    >>> assert v[0] == False

    >>> event_ = threading.Event()
    >>> event_.set()
    >>> s = serialize_event(event_)
    >>> assert isinstance(s, tuple)
    >>> u, v = list(s)
    >>> assert isinstance(u, type(unserialize_event))
    >>> assert v[0] == True

    """
    assert isinstance(e, threading.Event), \
        print("Positional argument <e> is type %s , expecting threading.Event." % type(e))
    return unserialize_event, (e.isSet(),)


copyreg.pickle(threading.Event, serialize_event)


class LaserImpact(pygame.sprite.Sprite):

    containers = None
    images = None

    def __init__(self, gl_, pos_, parent_, timing_=16, blend_=0, layer_=0):
        """
        Create an impact sprite effect (absorption effect) where the laser is colliding.

        :param gl_: class GL (contains all the game global variables)
        :param pos_: tuple of the impact position (x:int, y:int)
        :param parent_: parent object (Player1 class instance)
        :param timing_: integer; refreshing time in milliseconds (default 16ms is 60FPS)
        :param blend_: integer; blend effect to apply to the sprite, default pygame.BLEND_RGB_ADD = 0
        :param layer_: integer < 0; represent the sprite layer. default = 0


        """

        assert isinstance(pos_, tuple), \
            "Positional argument <pos_> is type %s , expecting tuple." % type(pos_)
        assert isinstance(parent_,  Asteroid), \
            "Positional argument <parent_> is type %s , expecting class Player1 instance." % type(parent_)
        assert isinstance(timing_, int), \
            "Positional argument <timing_> is type %s , expecting integer." % type(timing_)
        assert isinstance(blend_, int), \
            "Positional argument <blend_> is type %s , expecting integer." % type(blend_)
        assert isinstance(layer_, int), \
            "Positional argument <layer_> is type %s , expecting integer." % type(layer_)

        if self.containers is None:
            raise ValueError('LaserImpact.containers is not initialised.\nMake sure to assign the containers to'
                             ' a pygame group prior instantiation.\ne.g: LaserImpact.containers = '
                             'pygame.sprite.Group()')
        if self.images is None:
            raise ValueError("LaserImpact.images is not initialised.\nMake sure to assign a texture to "
                             "prior instantiation.\ne.g: LaserImpact.images = 'P1_SURFACE'")

        if timing_ < 0:
            raise ValueError('Positional argument timing_ cannot be < 0')

        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(self.containers, pygame.sprite.LayeredUpdates):
            if layer_:
                self.containers.change_layer(self, layer_)

        assert isinstance(self.images, (list, pygame.Surface))
        self.image = self.images[0] if isinstance(self.images, list) else self.images
        self.rect = self.image.get_rect(center=pos_)
        self.timing = timing_
        self.dt = 0
        self.index = 0
        self.gl = gl_
        self.blend = blend_
        self.layer = layer_
        self.length = len(self.images) - 1
        self.parent_ = parent_
        self.surface_name = 'IMPACT_LASER'
        self.id_ = id(self)
        self.impact_object = Broadcast(self.make_object())

    def make_object(self) -> AnimatedSprite:
        """
        Create an AnimatedSprite message object (see NetworkBroadcast library)
        :return: AnimatedSprite instance
        """
        # Only attributes self.gl.FRAME change, self.rect and self.index are changing over the time.
        return AnimatedSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                              layer_=self.layer, blend_=self.blend, rect_=self.rect,
                              index_=self.index)

    def update(self):

        if self.dt > self.timing:

            if self.rect.colliderect(self.gl.SCREENRECT):

                if isinstance(self.images, list):
                    self.image = self.images[self.index % self.length]

                # follow the parent object with half of its speed
                self.rect.move_ip(self.parent_.speed // 2)

                self.index += 1

                if self.index > self.length:
                    self.kill()

                self.dt = 0
                
            else:
                self.kill()

        if self.rect.colliderect(self.gl.SCREENRECT):
            self.impact_object.update({'frame': self.gl.FRAME, 'rect': self.rect, 'index': self.index})
            self.impact_object.queue()
            
        self.dt += self.gl.TIME_PASSED_SECONDS

    
class Shot(pygame.sprite.Sprite):
    images = None
    containers = None
    last_shot = 0
    shooting = False

    def __init__(self, parent_, pos_, gl_, timing_=0, layer_=-1, surface_name_=''):
        """
        Create a sprite shoot

        :param parent_: parent object class Player
        :param pos_: tuple (x:int, y:int); sprite shoot position (start position)
        :param gl_: Constants (class GL)
        :param timing_: integer; sprite refreshing time FPS, e.g 16ms is 60FPS
        :param layer_: integer; sprite layer (default 0 top layer)
        :param surface_name_: string; surface name e.g 'BLUE_LASER'; surface = eval(BLUE_LASER')
        """
        assert isinstance(parent_, Player1), \
            "Positional argument <parent_> is type %s , expecting class Player1 instance." % type(parent_)
        assert isinstance(pos_, tuple), \
            "Positional argument <pos_> is type %s , expecting tuple." % type(pos_)
        assert isinstance(timing_, int), \
            "Positional argument <timing_> is type %s , expecting integer." % type(timing_)
        assert isinstance(layer_, int), \
            "Positional argument <layer_> is type %s , expecting integer." % type(layer_)
        assert isinstance(surface_name_, str), \
            "Positional argument <surface_name_> is type %s , " \
            "expecting python string." % type(surface_name_)

        if self.containers is None:
            raise ValueError('Shot.containers is not initialised.\nMake sure to assign the containers to'
                             ' a pygame group prior instantiation.\ne.g: Shot.containers = pygame.sprite.Group()')
        if self.images is None:
            raise ValueError("Shot.images is not initialised.\nMake sure to assign a texture to "
                             "prior instantiation.\ne.g: Shot.images = 'P1_SURFACE'")
        if timing_ < 0:
            raise ValueError('Positional argument timing_ cannot be < 0')

        self.layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)

        self.images = Shot.images
        self.image = self.images[0] if isinstance(self.images, list) else self.images
        self.speed = pygame.math.Vector2(0, -35)
        self.timing = timing_
        self.pos = pos_
        self.gl = gl_
        self.position = pygame.math.Vector2(*self.pos)
        self.rect = self.image.get_rect(center=self.pos)
        self.dt = 0
        self.blend = 0  # pygame.BLEND_RGBA_ADD

        # todo test if convert_alpha otherwise this is useless
        self.mask = pygame.mask.from_surface(self.image)  # Image have to be convert_alpha compatible
        self.index = 0
        self.parent = parent_
        self.surface_name = surface_name_
        self.id_ = id(self)

        if Shot.shooting and self.is_reloading(self.gl.FRAME):
            self.kill()

        else:
            self.gl.MIXER.stop_object(id(BLUE_LASER_SOUND))
            self.gl.MIXER.play(sound_=BLUE_LASER_SOUND, loop_=False, priority_=0, volume_=1.0,
                               fade_out_ms=0, panning_=True, name_='BLUE_LASER_SOUND', x_=self.rect.centerx,
                               object_id_=id(BLUE_LASER_SOUND), screenrect_=self.gl.SCREENRECT)
            
            self.sound_object = Broadcast(self.make_sound_object('BLUE_LASER_SOUND'))
            self.sound_object.play()

            Shot.last_shot = FRAME
            Shot.shooting = True
            # Create a network object         
            self.shot_object = Broadcast(self.make_object())
            self.shot_object.queue()

    def make_sound_object(self, sound_name_: str) -> SoundAttr:
        """
        Create a sound object for network broadcasting.
        :param sound_name_: string; representing the texture to use e.g 'BLUE_LASER_SOUND"
        :return: Sound object, SoundAttr instance.
        """
        assert isinstance(sound_name_, str), \
            "Positional argument <sound_name_> is type %s , expecting python string." % type(sound_name_)

        if sound_name_ not in globals():
            raise NameError('Sound %s is not define.' % sound_name_)

        return SoundAttr(frame_=self.gl.FRAME, id_=self.id_, sound_name_=sound_name_, rect_=self.rect)
            
    def make_object(self) -> StaticSprite:
        """
        Create a StaticSprite message object (see NetworkBroadcast library)
        :return: StaticSprite object
        """
        # Only attributes self.gl.FRAME change and self.rect are changing over the time.
        return StaticSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                            layer_=self.layer, blend_=self.blend, rect_=self.rect)

    @staticmethod
    def is_reloading(frame_: int) -> bool:
        """
        Check if the player is shooting or reloading.

        Compare the actual FRAME number to the latest Shot frame number.
        Shot.last_shot default value is set to 0 during instantiation.
        Reloading time is hard encoded to 10 frames interval.
        When the player is ready to shoot, the shooting flag is set to false, otherwise stays True

        :frame_: integer; must be > 0 (Actual frame number)
        :return: True or False. True player is reloading, False player is ready to shoot

        >>> Shot.shooting = True
        >>> Shot.last_shot = 0
        >>> Shot.is_reloading(9)
        True
        >>> assert Shot.shooting is True

        >>> Shot.is_reloading(10)
        False
        >>> Shot.is_reloading(-1)
        Traceback (most recent call last):
           ...
        ValueError: frame_ must be >= 0

        """

        assert isinstance(frame_, int), \
            "argument frame_ should be integer got %s" % type(frame_)

        if not frame_ >= 0:
            raise ValueError("frame_ must be >= 0")

        assert hasattr(Shot, 'last_shot'), 'Class Shot is missing attribute <last_shot>.'
        assert hasattr(Shot, 'shooting'), 'Class Shot is missing attribute <shooting>.'
        assert isinstance(Shot.last_shot, int), \
            "last_shot variable should be integer got %s" % type(Shot.last_shot)
        assert frame_ >= Shot.last_shot, \
            "Game constant frame_ value:%s should be > or equal to %s " % (frame_, Shot.last_shot)

        if frame_ - Shot.last_shot < 10:
            # still reloading
            return True
        else:
            # ready to shoot
            Shot.shooting = False
            return False

    def collide(self, rect_: pygame.Rect, object_) -> None:
        """
        Create a laser impact sprite

        :param rect_: pygqme.Rect object
        :param object_: object colliding with the rectangle
        :return: None
        """
        assert isinstance(rect_, pygame.Rect), \
            'Positional argument rect_ should be a <pygame.Rect> type got %s ' % type(rect_)
        assert object_ is not None, 'Positional argument object_ cannot be None'

        # if sprite belongs to any group(s)
        if self.alive():
            LaserImpact.containers = self.gl.All
            LaserImpact.images = IMPACT_LASER
            LaserImpact(gl_=self.gl, pos_=rect_.topleft, parent_=object_,
                        timing_=self.timing, blend_=pygame.BLEND_RGBA_ADD, layer_=0)
            self.kill()

    def update(self) -> None:
        """
        Update shot sprites whereabouts.

        sprite position is given by its rectangle.
        The position changed by incrementing the position with its speed vector (self.speed)
        if the sprite belongs to the screen dimensions, a message is broadcast to the client
        :return: None
        """
        if self.dt > self.timing:

            if self.gl.SCREENRECT.colliderect(self.rect):

                # Move the laser sprite
                if self.images != IMPACT_LASER:
                    self.position += self.speed
                    self.rect.center = (self.position.x, self.position.y)
                self.dt = 0               
            else:
                self.kill()

        # broadcast network message
        if self.rect.colliderect(self.gl.SCREENRECT):
            self.shot_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
            self.shot_object.queue()

        self.dt += self.gl.TIME_PASSED_SECONDS


class Player1(pygame.sprite.Sprite):

    containers = None
    image = None

    def __init__(self, gl_, timing_=15, pos_: tuple = (0, 0), layer_=0):
        """

        :param gl_: Game constants (GL class) see GLOBAL library for more details
        :param timing_: integer; default 15ms (60 FPS)
        :param pos_: tuple; (x:int, y:int) representing player 1 position (default x=0, y=0)
        :param layer_: Sprite layer used by player 1
        """

        assert isinstance(timing_, int), \
            "Positional argument <timing_> is type %s , expecting integer." % type(timing_)
        assert isinstance(pos_, tuple), \
            "Positional argument <pos_> is type %s , expecting tuple." % type(pos_)
        assert isinstance(layer_, int), \
            "Positional argument <layer_> is type %s , expecting integer." % type(layer_)

        if self.containers is None:
            raise ValueError('Player1.containers is not initialised.\nMake sure to assign the containers to'
                             ' a pygame group prior instantiation.\ne.g: Player1.containers = pygame.sprite.Group()')
        if self.image is None:
            raise ValueError("Player1.image is not initialised.\nMake sure to assign a texture to "
                             "prior instantiation.\ne.g: Player1.image = 'P1_SURFACE'")

        pygame.sprite.Sprite.__init__(self, self.containers)

        assert isinstance(Player1.image, (pygame.Surface, list)), \
            "image is not a pygame.Surface or a list, got %s instead" % type(Player1.image)

        if timing_ < 0:
            raise ValueError('Positional argument timing_ cannot be < 0')

        self.image = Player1.image
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect(center=pos_)
        self.timing = timing_
        self.surface_name = 'P1_SURFACE'
        self.gl = gl_
        self.dt = 0
        self.speed = 300
        self.layer = layer_
        self.blend = 0
        self.shooting = False
        self.previous_pos = pygame.math.Vector2()           # previous position
        self.life = 200                                     # player's life
        self.eng_right = self.right_engine()                # instance for right engine
        self.eng_left = self.left_engine()                  # isntance for left engine
        # todo test if convert_alpha otherwise this is useless
        self.mask = pygame.mask.from_surface(self.image)    # Image have to be convert_alpha compatible
        self.damage = 800   # -> gives 800 hit point of damage after collision
        self.id_ = id(self)
        self.player_object = Broadcast(self.make_object())
        self.impact_sound_object = Broadcast(self.make_sound_object('IMPACT'))

        self.disruption_object = Broadcast(BlendSprite(frame_=self.gl.FRAME, id_=self.id_, surface_="",
                                                       layer_=self.layer, blend_=pygame.BLEND_RGB_ADD, rect_=self.rect,
                                                       parent_=self.surface_name, pos_=(-20, -20), index_=0))

    def make_sound_object(self, sound_name_: str)->SoundAttr:
        """
        Create a sound object for network broadcasting.
        :param sound_name_: string; representing the texture to use e.g 'BLUE_LASER_SOUND"
        :return: Sound object, SoundAttr instance.

        """
        assert isinstance(sound_name_, str), \
            'Positional argument sound_name_ is not a string type, got %s ' % type(sound_name_)

        if sound_name_ not in globals():
            raise NameError('Sound %s is not define.' % sound_name_)

        return SoundAttr(frame_=self.gl.FRAME, id_=self.id_, sound_name_=sound_name_, rect_=self.rect)

    def make_object(self) -> StaticSprite:
        """
        Create a sprite object for network broadcast similar to Player1
        :return: StaticSprite object (see NetworkBroadcast library for more details)
        """
        # Only attributes self.gl.FRAME, self.rect are changing over the time.
        return StaticSprite(
                frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                layer_=self.layer, blend_=self.blend, rect_=self.rect, life=self.life)

    def explode(self) -> None:
        """
        Player explosion sprites and halo
        :return: None
        """
        if self.alive():
            Explosion.images = EXPLOSION2
            Explosion(self, self.rect.center,
                      self.gl, self.timing, self.layer, texture_name_='EXPLOSION2')
            PlayerHalo.images = HALO_SPRITE13
            PlayerHalo.containers = self.gl.All
            PlayerHalo(texture_name_='HALO_SPRITE13', object_=self, timing_=10)
            self.kill()

    def collide(self, damage_: int) -> None:
        """
        Player1 collide with object, transfer the damage and play the collision sound locally
        if life < 1, trigger player1 explosion.

        :param damage_: integer; must be > 0 (total damage transferred to the player after collision.)
        :return: None
        """
        assert isinstance(damage_, int), \
            'Positional argument damage_ is not an int, got %s instead.' % type(damage_)
        assert damage_ > 0, 'damage_ argument should be > 0 '
        print(self.life, damage_, self.life - damage_)
        if self.alive():
            self.life -= damage_
            self.gl.MIXER.play(sound_=IMPACT, loop_=False, priority_=0,
                               volume_=1.0, fade_out_ms=0, panning_=True,
                               name_='IMPACT', x_=self.rect.centerx,
                               object_id_=id(IMPACT),
                               screenrect_=self.gl.SCREENRECT)         
            self.impact_sound_object.play()
    """
    def hit(self, damage_: int) -> None:
        
        #Transfer damage to the player after being hit.

        #:param damage_: integer > 0, damage transfer to the player
        #:return: None

        assert isinstance(damage_, int), \
            'Positional argument damage_ is not an int, got %s instead.' % type(damage_)
        assert damage_ > 0, 'damage_ argument should be > 0 '

        if self.alive():
            self.life -= damage_
    """
    def left_engine(self) -> AfterBurner:
        """
        Create a sprite for the left engine
        :return: AfterBurner instance
        """
        if EXHAUST:
            AfterBurner.images = EXHAUST
        else:
            raise NameError('EXHAUST is not defined.')
        return AfterBurner(self, self.gl, (-22, 38),
                           self.timing, pygame.BLEND_RGB_ADD, self.layer - 1, texture_name_='EXHAUST')

    def right_engine(self) -> AfterBurner:
        """
        Create a sprite for the right engine
        :return: AfterBurner instance
        """
        if EXHAUST:
            AfterBurner.images = EXHAUST
        else:
            raise NameError('EXHAUST is not defined.')
        return AfterBurner(self, self.gl, (22, 38),
                           self.timing, pygame.BLEND_RGB_ADD, self.layer - 1, texture_name_='EXHAUST')

    def get_centre(self) -> tuple:
        """
        Get Player1 position.

        :return: tuple representing Player1 rect centre
        """
        return self.rect.center

    def disruption(self) -> None:
        """
        Create an electric effect on Player1 hull.
        :return: None
        """
        if 'DISRUPTION' in globals():
            if isinstance(DISRUPTION, list):
                index = (FRAME >> 1) % len(DISRUPTION) - 1
            else:
                raise ValueError('DISRUPTION is not a list, got %s instead.' % type(DISRUPTION))
        else:
            raise NameError('DISRUPTION is not defined.')

        self.image.blit(DISRUPTION[index], (-20, -20), special_flags=pygame.BLEND_RGB_ADD)

        # self.disruption_object.update({'frame': self.gl.FRAME, 'surface': 'DISRUPTION',
        #                                'rect': self.rect, 'index': index})
        # self.disruption_object.show(self.disruption_object)
        # self.disruption_object.queue()

    def shooting_effect(self) -> pygame.Surface:
        """
        Apply a special effect on the aircraft hull when firing.
        :return: pygame.Surface
        """
        if 'GRID' in globals():
            self.image.blit(GRID, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        else:
            raise NameError('GRID is not defined.')
        return self.image

    def update(self) -> None:
        """
        Update Player1 sprite

        :return: None
        """

        self.rect.clamp_ip(self.gl.SCREENRECT)

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            if self.life < 1:
                self.explode()

            if self.gl.KEYS[pygame.K_UP]:
                self.rect.move_ip(0, -self.speed * self.gl.SPEED_FACTOR)

            if self.gl.KEYS[pygame.K_DOWN]:
                self.rect.move_ip(0, +self.speed * self.gl.SPEED_FACTOR)

            if self.gl.KEYS[pygame.K_LEFT]:
                self.rect.move_ip(-self.speed * self.gl.SPEED_FACTOR, 0)

            if self.gl.KEYS[pygame.K_RIGHT]:
                self.rect.move_ip(+self.speed * self.gl.SPEED_FACTOR, 0)

            # if self.gl.JOYSTICK is not None and self.gl.JOYSTICK.PRESENT:
            #    x, y = self.gl.JOYSTICK.axes_status[0]

            if self.gl.KEYS[pygame.K_SPACE]:
                self.shooting_effect()
                Shot(self, self.rect.center, self.gl, 0, self.layer - 1, surface_name_='BLUE_LASER')

            if joystick is not None:
                self.rect.move_ip(JL3.x * self.gl.SPEED_FACTOR * self.speed,
                                  JL3.y * self.gl.SPEED_FACTOR * self.speed)

            if self.alive():
                # Broadcast the spaceship position every frames
                self.player_object.update({'frame': self.gl.FRAME,
                                           'rect': self.rect,
                                           'life': self.life})
                self.player_object.queue()

            if self.previous_pos == self.rect.center:
                self.rect.centerx += random.randint(-1, 1)
                self.rect.centery += random.randint(-1, 1)

            self.previous_pos = self.rect.center

            # !UPDATE the <follower> sprites with the new player position.
            self.eng_left.update()
            self.eng_right.update()
            
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        self.disruption()


class Player2(pygame.sprite.Sprite):

    def __init__(self, sprite_):
        """
        Create an instance of Player2 on the server
        :param sprite_: object containing all attributes

        >>> import pygame
        >>> attributes = {'rect': pygame.Rect(0, 0, 0, 0),
        ...     'image':None, 'blend':0, 'layer':-1, 'id_':35555, 'surface':'P1_SURFACE', 'damage': 800, 'life': 200}
        >>> sprite_ = pygame.sprite.Sprite()
        >>> for attr, value in attributes.items():
        ...     setattr(sprite_, attr, value)
        >>> spr = Player2(sprite_)
        >>> spr.update()
        >>> print(spr.surface)
        P1_SURFACE

        """
        assert sprite_ is not None, 'Positional argument sprite_ is None.'
        attributes = ['rect', 'image', 'blend', 'layer', 'id_', 'surface']
        for attr in attributes:
            assert hasattr(sprite_, attr),\
                'Positional argument sprite_ is missing attribute %s ' % attr

        pygame.sprite.Sprite.__init__(self)

        self.rect = sprite_.rect
        self.image = sprite_.image
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        self.id_ = sprite_.id_
        self.surface = sprite_.surface
        self.damage = sprite_.damage
        self.life = sprite_.life

    def update(self) -> None:
        ...


class P2Shot(pygame.sprite.Sprite):

    def __init__(self, gl_, sprite_, timing_=0):
        """

        :param gl_: class GL (Constants)
        :param sprite_: object containing all the original sprite attributes
        :param timing_: integer > 0 representing the refreshing time.

        """

        assert isinstance(gl_, type(GL)), \
            "Positional argument <gl_> is type %s , expecting class GL instance." % type(gl_)

        assert sprite_ is not None, 'Positional argument sprite_ is None.'

        attributes = ['rect', 'image', 'blend', 'layer', 'id_', 'surface']
        for attr in attributes:
            assert hasattr(sprite_, attr), \
                'Positional argument sprite_ is missing attribute %s ' % attr

        if timing_ < 0:
            raise ValueError('argument timing_ must be > 0')

        pygame.sprite.Sprite.__init__(self)

        self.rect = sprite_.rect
        self.image = sprite_.image
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        self.id_ = sprite_.id_
        self.surface = sprite_.surface
        self.gl = gl_
        self.timing = timing_

    def collide(self, rect_, object_) -> None:
        # todo check here if it should be hit class instead
        """

        :param rect_: pygame.Rect type
        :param object_:
        :return:
        """

        if hasattr(GL, 'All'):
            LaserImpact.containers = GL.All
        else:
            raise AttributeError('Class GL missing attribute All.')

        if IMPACT_LASER:
            LaserImpact.images = IMPACT_LASER
        else:
            raise NameError('IMPACT_LASER is not define.')

        LaserImpact(gl_=self.gl, pos_=rect_.topleft, parent_=object_,
                    timing_=self.timing, blend_=pygame.BLEND_RGBA_ADD, layer_=0)

    def update(self) -> None:
        ...


class SpriteServer(threading.Thread):

    def __init__(self,
                 gl_,    # Global variables class
                 host_: str,  # host address (string)
                 port_: int,  # port value (integer)
                 ):
        """

        :param gl_:  class GL
        :param host_: string; ip address
        :param port_: integer; port to use
        """
        assert isinstance(host_, str), \
            "Positional argument <host_> is type %s , expecting string." % type(host_)
        assert isinstance(port_, int), \
            "Positional argument <port_> is type %s , expecting integer" % type(port_)

        threading.Thread.__init__(self)

        self.gl = gl_
        self.gl.SPRITE_SERVER_STOP = False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as error:
            print('\n[-]SpriteServer - ERROR : %s %s' % (error, time.ctime()))
            gl_.P1CS_STOP = True
            self.gl.SPRITE_SERVER_STOP = True

        try:
            self.sock.bind((host_, port_))
            self.sock.listen(1)
        except socket.error as error:
            print('\n[-]SpriteServer - ERROR : %s %s' % (error, time.ctime()))
            gl_.P1CS_STOP = True
            self.gl.SPRITE_SERVER_STOP = True

        self.buf = self.gl.BUFFER
        self.total_bytes = 0
        self.view = memoryview(bytearray(self.buf))

    def run(self):

        # Accept a connection. The socket must be bound to
        # an address and listening for connections.
        # The return value is a pair (conn, address) where
        # conn is a new socket object usable to send and receive
        # data on the connection, and address is the address
        # bound to the socket on the other end of the connection.
        connection = None
        try:
            # The thread will be stopped here until first connection
            connection, client_address = self.sock.accept()

        except socket.error as error:
            print("\n[-]SpriteServer - Lost connection with Player 2 ...")
            print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
            self.gl.P1CS_STOP = True

        while not self.gl.P1CS_STOP and not self.gl.SPRITE_SERVER_STOP:
            # try:

            while not self.gl.P1CS_STOP and not self.gl.SPRITE_SERVER_STOP:

                # Receive data from the socket, writing it into buffer instead
                # of creating a new string. The return value is a pair (nbytes, address)
                # where nbytes is the number of bytes received and address is the address
                # of the socket sending the data.
                try:

                    nbytes, sender = connection.recvfrom_into(self.view, self.buf)

                except socket.error as error:
                    print("\n[-]SpriteServer - Lost connection with Player 2 ...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    # signal to kill both threads SpriteServer and SpriteClient
                    # todo need to remove player 2 sprite
                    self.gl.SPRITE_SERVER_STOP = True
                    nbytes = 0

                buffer = self.view.tobytes()[:nbytes]
                try:
                    connection.sendall(self.view.tobytes()[:nbytes])
                except ConnectionResetError as error:
                    print("\n[-]SpriteServer - Lost connection with Player 2 ...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    # todo need to remove player 2 sprite
                    # signal to kill both threads SpriteServer and SpriteClient
                    self.gl.SPRITE_SERVER_STOP = True
                try:
                    # Decompress the data frame
                    decompress_data = lz4.frame.decompress(buffer)
                    data = cpickle.loads(decompress_data)
                except Exception:
                    # The decompression error can also happen when
                    # the bytes stream sent is larger than the buffer size.
                    # todo need to remove player 2 sprite
                    # signal to kill both threads SpriteServer and SpriteClient
                    self.gl.SPRITE_SERVER_STOP = True
                    self.gl.SPRITE_CLIENT_STOP = True
                    data = None

                # todo check if self.gl.NetGroupAll.empty() is faster
                # self.gl.NetGroupAll = LayeredUpdatesModified()
                data_set = set()

                if isinstance(data, list):

                    for sprite_ in data:

                        # print(GL.FRAME, sprite_.id_, sprite_.surface if hasattr(sprite_, "surface") else None)

                        if hasattr(sprite_, 'event'):
                            continue

                        elif hasattr(sprite_, 'sound_name'):

                            sound = eval(sprite_.sound_name)
                            self.gl.MIXER.stop_object(id(sound))
                            self.gl.MIXER.play(sound_=sound, loop_=False, priority_=0,
                                               volume_=1.0, fade_out_ms=0, panning_=True,
                                               name_=sprite_.sound_name, x_=sprite_.rect.centerx,
                                               object_id_=id(sound),
                                               screenrect_=self.gl.SCREENRECT)
                            # data.remove(sprite_)

                        else:

                            assert hasattr(sprite_, 'surface'), "\nBroadcast message is missing <surface> attribute."

                            try:

                                sprite_.image = eval(sprite_.surface)  # load surface

                            except (NameError, AttributeError):
                                raise RuntimeError("\n[-]SpriteServer - Surface "
                                                   "'%s' does not exist " % sprite_.surface)

                            if isinstance(sprite_.image, list):
                                sprite_.image = sprite_.image[sprite_.index % len(sprite_.image) - 1]

                            # --- Apply transformation ---
                            # Apply transformation to texture rotation/scale and
                            # store the transformation inside a buffer
                            # Check if the texture has been already transformed and use
                            # the buffer transformation instead (for best performance).
                            if hasattr(sprite_, 'rotation'):
                                if sprite_.rotation is not None and sprite_.rotation != 0:
                                    if sprite_.id_ in self.gl.XTRANS_ROTATION.keys():

                                        sprite_.image = self.gl.XTRANS_ROTATION[sprite_.id_]
                                    else:
                                        sprite_.image = pygame.transform.rotate(
                                            sprite_.image, sprite_.rotation)

                                        self.gl.XTRANS_ROTATION.update({sprite_.id_: sprite_.image})

                            if hasattr(sprite_, 'scale'):
                                if sprite_.scale != 1:
                                    if sprite_.id_ in self.gl.XTRANS_SCALE.keys():

                                        sprite_.image = self.gl.XTRANS_SCALE[sprite_.id_]
                                    else:
                                        sprite_.image = pygame.transform.scale(sprite_.image, (
                                            int(sprite_.image.get_size()[0] * sprite_.scale),
                                            int(sprite_.image.get_size()[1] * sprite_.scale)))

                                        self.gl.XTRANS_SCALE.update({sprite_.id_: sprite_.image})

                            s = None
                            # find Player 2
                            if sprite_.surface == 'P2_SURFACE':
                                s = Player2(sprite_)

                            # find player 2 shots
                            elif sprite_.surface == "RED_LASER":
                                s = P2Shot(self.gl, sprite_, 16)

                            # generic sprite that doesn't have
                            # to be instantiated with specific methods
                            else:

                                # Generic sprite (without methods)
                                s = pygame.sprite.Sprite()
                                s.frame = sprite_.frame
                                s.rect = sprite_.rect
                                s.surface = sprite_.surface
                                s.image = sprite_.image
                                s.blend = sprite_.blend
                                s.layer = sprite_.layer
                                s.id_ = sprite_.id_
                                if hasattr(sprite_, 'life'):
                                    s.life = sprite_.life
                                if hasattr(sprite_, 'damage'):
                                    s.damage = sprite_.damage

                            # Add broadcast sprites to DATA_SET (reset every time a message from client is received).
                            # DATA_SET contains all sprites sent by the client for a specific frame number.
                            # The DATA_SET cannot contains duplicates. The id attribute (memory location)
                            # is used as unique identification number to store sprites in the DATA_SET.
                            # The element in data set represent all active (alive) sprites display on the
                            # client side (before client collision detection).

                            data_set.add(sprite_.id_)

                            # Add the sprite in self.gl.NetGroupAll (if not already in the group) or
                            # update position and texture.
                            # NetGroupAll, will be used in the main loop (locally) to display
                            # all the sprites broadcast from a specific frame number.
                            # If a sprite is not added to that group, it will be ignored
                            # and not display on the client side.

                            if s is not None and len(self.gl.NetGroupAll) > 0:
                                has_ = False
                                for sprites in self.gl.NetGroupAll:
                                    if sprites.id_ == s.id_:
                                        has_ = True
                                        sprites.rect = s.rect
                                        sprites.image = sprite_.image
                                        sprites.frame = sprite_.frame
                                        break

                                if not has_:
                                    self.gl.NetGroupAll.add(s)

                            else:
                                self.gl.NetGroupAll.add(s)

                    # Compare NetGroupAll group to DATA_SET and delete sprite(s)
                    # accordingly. Sprites in NetGroupAll and not in DATA_SET will
                    # be killed and remove from every groups they are belonging to.
                    # When a sprite is deleted, the transformation/scale buffer associated
                    # to it will be deleted (using its id).
                    for spr_ in self.gl.NetGroupAll:
                        if spr_.id_ not in data_set:
                            spr_.kill()

                            if spr_.id_ in self.gl.XTRANS_SCALE.keys():
                                self.gl.XTRANS_SCALE.pop(spr_.id_)
                            if spr_.id_ in self.gl.XTRANS_ROTATION.keys():
                                self.gl.XTRANS_ROTATION.pop(spr_.id_)

                    # Reload original texture
                    # for pair in modified_surface.items():
                    #    globals()[pair[0]] = pair[1]

                buffer = b''
                # data fully received breaking the loop, clear the buffer
                break

            # pygame.time.wait(1)
            """
            except Exception as error:
                print('\n[-]SpriteServer - ERROR @ frame: %s : %s %s' % (FRAME, error, time.ctime()))

            finally:
                # Clean up the connection
                if 'connection' in globals() and connection is not None:
                    connection.close()
            """
        print('\n[-]SpriteServer is now terminated...')


def force_quit(host_: str, port_: int) -> None:
    """
    function used for terminating SERVER/ CLIENT threads listening (blocking socket)

    :param host_: string; ip address
    :param port_: integer; port to use
    :return: None
    """
    assert isinstance(host_, str), \
        "Positional argument <host_> is type %s , expecting string." % type(host_)
    assert isinstance(port_, int), \
        "Positional argument <port_> is type %s , expecting integer." % type(port_)
    # todo port should be > 1024
    sock = None
    try:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host_, port_))
        data = cpickle.dumps(b"QUIT")
        sock.sendall(data)
        print("\n[+]Termination signal sent to SpriteServer...")

    except Exception as error:

        print("\n[-]Cannot send termination signal to SpriteServer...")
        print("\n[-]ERROR %s " % error)

    finally:

        if 'sock' in globals() and isinstance(sock, socket.socket):
            sock.close()


def collision_detection():

    p2_shots = pygame.sprite.Group()
    p2 = None

    for sprite_ in GL.NetGroupAll:

        # detect player sprite
        if hasattr(sprite_, 'surface'):

            if sprite_.surface == "P2_SURFACE":
                p2 = sprite_
                continue
            # detect player 2 shots and add them to a specific
            # group p2_shots. p2_shots has to be destroyed before
            # leaving the function.
            elif sprite_.surface == "RED_LASER":
                p2_shots.add(sprite_)

    if P1 is not None and P1.alive():

        # Player 1 collision with asteroid
        # Use collision mask for collision detection
        # It is compulsory to have sprite textures with alpha transparency information
        # in order to check for collision otherwise the collision will be ignored.
        collision = pygame.sprite.spritecollideany(P1, GL.ASTEROID, collided=pygame.sprite.collide_mask)
        if collision is not None:
            P1.collide(collision.damage)
            if hasattr(collision, 'collide'):
                collision.collide(P1.damage)
            else:
                print(type(collision))
                raise AttributeError

        # Player 1 shots collision with asteroids
        # same than above
        for shots, asteroids in pygame.sprite.groupcollide(
                GL.PLAYER_SHOTS, GL.ASTEROID, 0, 0, collided=pygame.sprite.collide_mask).items():

            if asteroids is not None:
                for aster in asteroids:
                    if hasattr(aster, 'hit'):
                        aster.hit(100)
                        new_rect = shots.rect.clamp(aster.rect)  # todo need to make sure shots is not a list
                        shots.collide(rect_=new_rect, object_=aster)
                    else:
                        print(type(aster))
                        raise AttributeError

    # Player 2 shots colliding with asteroid
    if p2 is not None and p2.alive():
        for shots, asteroids in pygame.sprite.groupcollide(
                p2_shots, GL.ASTEROID, 0, 0).items():  # ,collided=pygame.sprite.collide_mask).items():
            if asteroids is not None:
                for aster in asteroids:
                    if hasattr(aster, 'hit'):
                        aster.hit(100)
                        new_rect = shots.rect.clamp(aster.rect)  # todo need to make sure shots is not a list
                        shots.collide(rect_=new_rect, object_=aster)
                    else:
                        print(type(aster))
                        raise AttributeError
                    
            for spr in GL.NetGroupAll:
                if spr.id_ == shots.id_:
                    spr.kill()

    # Use collision mask for collision detection
    # Check collision between Player 2 and asteroids
    if p2 is not None and p2.alive():
        collision = pygame.sprite.spritecollideany(p2, GL.ASTEROID, collided=pygame.sprite.collide_mask)
        if collision is not None:
            # Cannot send damage to player 2, this
            # is done on the remote host in the collision detection section
            # Pass only damage to the asteroid
            collision.collide(p2.damage)

    # Transport collision with asteroid
    if T1 is not None and T1.alive():
        # todo check collision masks
        collision = pygame.sprite.spritecollideany(T1, GL.ASTEROID, collided=pygame.sprite.collide_mask)
        if collision is not None:
            T1.collide(collision.damage)
            if hasattr(collision, 'collide'):
                collision.collide(T1.damage)
            else:
                print(type(collision))
                raise AttributeError

    p2_shots.remove()
    p2_shots.empty()
    del p2_shots


def window():
    scrw_half = SCREENRECT.w >> 1
    scrh_half = SCREENRECT.h >> 1
    w, h = FRAMEBORDER.get_size()
    screen.blit(BACKGROUND, (0, 0))
    screen.blit(FRAMEBORDER, (scrw_half - (w >> 1), scrh_half - (h >> 1)))
    font = freetype.Font(os.path.join('Assets\\Fonts\\', 'ARCADE_R.ttf'), size=15)
    frame_ = FRAME.copy()
    rect = font.get_rect("Waiting for connection...")
    font.render_to(frame_, ((frame_.get_width() - rect.w) // 2,
                            (frame_.get_height() - rect.h) // 2),
                   "Waiting for connection...",
                   fgcolor=pygame.Color(255, 255, 255), size=15)
    screen.blit(frame_, (scrw_half - (w >> 1) + 20, scrh_half - (h >> 1) + 40))

    clock = pygame.time.Clock()
    frame = 0

    while GL.CONNECTION is False:

        screen.blit(BACKGROUND, (0, 0))

        pygame.event.pump()
        Square()
        GL.All.update()
        GL.All.draw(screen)
        screen.blit(frame_, (scrw_half - (w >> 1) + 20, scrh_half - (h >> 1) + 40))
        GL.TIME_PASSED_SECONDS = clock.tick(70)
        frame += 1
        pygame.display.flip()
    """
    frame = 0
    frame_ = FRAME.copy()
    for s, t in GL.CLIENTS.items():
        font.render_to(frame_, ((frame_.get_width() - rect.w) // 2,
                       (frame_.get_height() - rect.h) // 2),
                       'Client connected : ' + str(s) + ':' + str(t),
                       fgcolor=pygame.Color(255, 255, 255), size=15)
    while 1:
        pygame.event.pump()
        screen.blit(BACKGROUND, (0, 0))
        screen.blit(frame_, (scrw_half - (w >> 1) + 20, scrh_half - (h >> 1) + 40))
        GL.TIME_PASSED_SECONDS = clock.tick(70)
        frame += 1
        pygame.display.flip()
        ...
    """


class Square(pygame.sprite.Sprite):
    def __init__(self):

        self.layer = -1
        pygame.sprite.Sprite.__init__(self, GL.All)

        if isinstance(GL.All, pygame.sprite.LayeredUpdates):
            if self.layer:
                GL.All.change_layer(self, self.layer)

        self.image = pygame.Surface((randint(200, 500), randint(200, 500)))
        self.image.fill((10, 15, 25, 15))
        self.image.convert(32, pygame.RLEACCEL)
        self.rect = self.image.get_rect(center=(randint(0, SCREENRECT.w),
                                        randint(0, SCREENRECT.h)))
        self.dt = 0
        self.blend = pygame.BLEND_RGBA_ADD
        self.i = 128

    def update(self):

        self.image.set_alpha(self.i)
        self.i -= 10
        if self.i < 0:
            self.kill()


if __name__ == '__main__':

    RECT = pygame.sprite.Group()

    import doctest

    doctest.testmod()

    SERVER = '127.0.0.1'
    CLIENT = '127.0.0.1'
    # SERVER = '192.168.0.1'
    # CLIENT = '192.168.0.4'

    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    GL.SCREENRECT = SCREENRECT
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)
    GL.SCREEN = screen
    pygame.display.set_caption('PLAYER 1')

    # *********************************************************************
    # JOYSTICK 
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    GL.JOYSTICK = joystick

    from Textures import *
    from Sounds import BLUE_LASER_SOUND, RED_LASER_SOUND, EXPLOSION_SOUND, IMPACT, IMPACT1
    from Backgrounds import Background
    from Asteroids import Asteroid
    from MessageSender import SpriteClient
    from Transports import Transport
    # background vector
    vector1 = pygame.math.Vector2(x=0, y=0)
    vector2 = pygame.math.Vector2(x=0, y=-1024)

    # ********************************************************************
    # NETWORK SERVER / CLIENT

    # SpriteServer -> receive client(s) positions
    # 1) Start the Server to receive client(s) position(s)
    # If no connection is made, the thread will remains listening/running
    # in the background, except if an error is raised.
    server = SpriteServer(GL, SERVER, 1025)
    server.start()

    # SpriteClient -> forward all sprites positions
    # 2) Start the Client to send all sprites positions to client(s)
    client = SpriteClient(gl_=GL, host_=CLIENT, port_=1024)
    client.start()

    # Killing threads if no client connected
    if not client.is_alive() or GL.CONNECTION is False:
        print('No player detected')
        GL.SPRITE_CLIENT_STOP = True
        GL.SPRITE_SERVER_STOP = True
        force_quit(SERVER, 1025)


    window()

    # *********************************************************************

    GL.All = LayeredUpdatesModified()
    GL.ASTEROID = pygame.sprite.Group()
    GL.PLAYER_SHOTS = pygame.sprite.Group()
    GL.TRANSPORT = pygame.sprite.GroupSingle()

    Player1.image = P1_SURFACE
    Player1.containers = GL.All
    Shot.images = BLUE_LASER
    Shot.containers = GL.All, GL.PLAYER_SHOTS
    Explosion.containers = GL.All
    Background.containers = GL.All
    AfterBurner.containers = GL.All
    Asteroid.containers = GL.All, GL.ASTEROID
    Asteroid.image = DEIMOS
    Transport.image = TRANSPORT
    Transport.containers = GL.All, GL.TRANSPORT

    Background.image = BACK1_S
    Background(vector_=pygame.math.Vector2(0, 1), position_=vector2, gl_=GL, layer_=-2, event_name_='BACK1_S')
    Background.image = BACK2_S
    Background(vector_=pygame.math.Vector2(0, 1), position_=vector1, gl_=GL, layer_=-2, event_name_='BACK2_S')
    Background.image = CL1
    Background(vector_=pygame.math.Vector2(0, 2.5),
               position_=pygame.math.Vector2(x=0, y=-480),
               gl_=GL, layer_=-2, blend_=pygame.BLEND_RGB_ADD, event_name_='CL1')
    Background.image = CL2
    Background(vector_=pygame.math.Vector2(0, 2.5),
               position_=pygame.math.Vector2(x=randint(0, 800), y=200),
               gl_=GL, layer_=-2, blend_=pygame.BLEND_RGB_ADD, event_name_='CL2')

    ShootingStar.containers = GL.All
    ShootingStar.image = SHOOTING_STAR

    P1 = Player1(GL, 15, (screen.get_size()[0] // 2, screen.get_size()[1] // 2))
    # P1 = None
    T1 = Transport(gl_=GL, timing_=15,
                   pos_=(SCREENRECT.w >> 1,
                         (SCREENRECT.h >> 1) - 100), surface_name_='TRANSPORT', layer_=0)

    GL.TIME_PASSED_SECONDS = 0

    clock = pygame.time.Clock()
    GL.STOP_GAME = False

    FRAME = 0
    GL.FRAME = 0

    GL.MIXER = SoundControl(20)

    f = open('P1_log.txt', 'w')

    while not GL.STOP_GAME:

        pygame.event.pump()

        # print('Server frame # %s vector1 %s vector2 %s' % (FRAME, vector1, vector2))

        # Send an event to the client triggering the next frame
        GL.NEXT_FRAME.set()     # set the event
        event_obj = EventAttr(event_=GL.NEXT_FRAME, frame_=GL.FRAME)
        Broadcast(event_obj).next_frame()

        if len(GL.ASTEROID) < 25:
            asteroid = random.choices(['DEIMOS', 'EPIMET'])[0]
            scale = random.uniform(0.1, 0.5)
            rotation = random.randint(0, 360)
            Asteroid.image = pygame.transform.rotozoom(eval(asteroid).copy(), rotation, scale)
            GL.ASTEROID.add(Asteroid(asteroid_name_=asteroid,
                                     gl_=GL, blend_=0, rotation_=rotation,
                                     scale_=scale, timing_=16, layer_=-2))
        
        if joystick is not None:
            JL3 = pygame.math.Vector2(joystick.get_axis(0), joystick.get_axis(1))

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            GL.KEYS = keys

            if event.type == pygame.QUIT:
                print('Quitting')
                GL.STOP_GAME = True

            if keys[pygame.K_ESCAPE]:
                GL.STOP_GAME = True

            if keys[pygame.K_F8]:
                pygame.image.save(screen, 'dump0.png')

            if event.type == pygame.MOUSEMOTION:
                GL.MOUSE_POS = pygame.math.Vector2(event.pos)

        if random.randint(0, 1000) > 985:
            shoot = ShootingStar(gl_=GL, layer_=0, timing_=16, surface_name_='SHOOTING_STAR')

        # update sprites positions and add sprites transformation
        # At this stage no sprites are display onto the screen. Therefore,
        # sprite's methods blit directly surface or image onto the screen
        # will takes the risk to see their surfaces overlay by another sprites surface while calling
        # any group's draw methods (see below)
        GL.All.update()

        # Authorize Player 1 to send data to the client.
        # Allowing to send only one set of data every frame.
        # The clear method is used in the class SpriteClient
        # right after receiving the Event
        GL.SIGNAL.set()

        # Always display the group GL.All first has it contains the background surfaces
        # Any sprite attached to the group GL.All and blit directly to the screen surface
        # will be override by the network sprite if sprites occupy the same location..
        # Ideally all sprites should be on the same group in order to draw them ordered by
        # their layer number.
        # Todo :
        #  create single group type pygame.sprite.layerUpdatesModified() group by adding network sprites directly
        #  into the GL.All group (also pygame.sprite.layerUpdatesModified())
        #  Note, all network sprites added to the GL.All group have to be killed after being blit onto
        #  the display to avoid filling up the group of new instances (Broadcast class calls will add a
        #  new sprite instances to the group GL.All each frames without killing the previous one, with the
        #   effect of slowing down the game loop and displaying un-necessary sprites.

        GL.All.draw(screen)

        # Draw the network sprite above the background
        if GL.CONNECTION:
            GL.NetGroupAll.draw(screen)

        # *************************************************************
        # Draw here all the other sprites that does not belongs to
        # common groups (GL.All & GL.NetGroupAll).
        # Sprite blit last onto the display are at the top layer.
        # Be aware that any surface(s) blit with blend attribute will
        # also blend with the entire sprite scene (blending with
        # sprites from all layers)
        # e.g Drawing GUI and life/energy sprite bars, screen bullet impacts
        # special effects, final score, ending screen and text inputs etc.

        # Update the sound Controller
        GL.MIXER.update()

        collision_detection()

        GL.TIME_PASSED_SECONDS = clock.tick(70)
        GL.SPEED_FACTOR = GL.TIME_PASSED_SECONDS / 1000
        GL.FPS.append(clock.get_fps())

        # half = SCREENRECT.w >> 1
        # safe_zone = pygame.Rect(half - 200, half, 400, SCREENRECT.bottom - half)
        # pygame.draw.rect(screen, pygame.Color(255, 0, 0, 0), safe_zone, 1)

        pygame.display.flip()

        FRAME += 1
        GL.FRAME = FRAME
        Broadcast.empty()

        # for r in GL.All:
        #    print(r)
        """
        print(GL.FRAME)
        for r in GL.NetGroupAll:
            f.write('\n NETGROUPALL  ' + str(GL.FRAME) + " ")
            f.write(' Surface: ' + str(r.surface) if hasattr(r, 'surface') else str(r))
            f.write(' Rect: ' + str(r.rect) if hasattr(r, 'rect') else '')
            f.write(' id: ' + str(r.id_))
        for r in GL.All:
            f.write('\n GL.All  ' + str(GL.FRAME) + ' ')
            f.write(' Surface: ' + str(r.surface) if hasattr(r, 'surface') else str(r))
            f.write(' Rect: ' + str(r.rect) if hasattr(r, 'rect') else '')
            f.write(' id: ' + str(r.id_) if hasattr(r, 'id_') else '')
        """

    f.close()

    GL.SPRITE_CLIENT_STOP = True
    GL.SPRITE_SERVER_STOP = True
    force_quit(SERVER, 1025)
    import matplotlib.pyplot as plt

    plt.title("FPS ")

    # plt.plot(GL.BYTES_SENT)
    plt.plot(GL.FPS)
    plt.draw()
    plt.show()

    plt.title("BYTES RECEIVED")
    plt.plot(GL.BYTES_RECEIVED)
    plt.draw()
    plt.show()
    pygame.quit()

