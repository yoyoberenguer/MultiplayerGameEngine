import threading

import pygame
from GLOBAL import GL

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


class DefaultAttr(object):

    def __init__(self, frame_: int = None, id_: int = None):
        """
        DefaultAttr class contains all the default attribute shared by all network objects including : sprite,
        Event and SoundEvent.

        :param frame_: integer > 0; The actual frame number
        :param id_: integer; object memory location
        """
        assert frame_ is not None, "\nframe_ attribute is not initialised."
        self.frame = frame_
        self.id_ = id_ if id_ is not None else id(self)


class EventAttr(DefaultAttr):

    def __init__(self, event_: threading.Event = None, frame_: int = None, id_: int = None):
        """
        EventAttr class contains all the attributes for event type network messages.

        :param event_: threading.Event object status
        :param frame_: integer > 0; The actual frame number
        :param id_: integer; object memory location
        """
        DefaultAttr.__init__(self, frame_=frame_, id_=id_)
        assert event_ is not None, "event_ attribute is not initialised."
        self.event = event_


class SoundAttr(DefaultAttr):

    def __init__(self, frame_: int = None, id_: int = None,
                 sound_name_: str = '', rect_=pygame.Rect(0, 0, 0, 0)):
        """
        SoundAttr class contains all the attributes for sound type network messages.

        :param frame_: integer > 0; The actual frame number
        :param id_: integer; object memory location
        :param sound_name_: string; Sound name. e.g 'EXPLOSION_SOUND'
        :param rect_: pygame.rect; the sound position is used by the SoundServer by the method stereo_panning
        """
        DefaultAttr.__init__(self, frame_=frame_, id_=id_)
        assert sound_name_ != '', "sound_name_ attribute is not initialised."
        self.sound_name = sound_name_
        self.rect = rect_


class StaticSprite(DefaultAttr):

    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None, **kwargs):
        """
        StaticSprite class convert a static sprite object (single surface) into a simple object containing
        similar attributes and values.
        Example of static object : MirroredPlayer1Class (single texture: P1_SURFACE)

        :param frame_: integer > 0; The actual frame number
        :param id_: integer; object memory location
        :param surface_: string; sprite surface name e.g 'P1_SURFACE'
        :param layer_: integer < 0; Sprite layer
        :param blend_: integer > 0; blending mode
        :param rect_: pygame.Rect; position and sprite shapes
        :param kwargs: extra attributes
        """
        assert surface_ != '', "surface_name_ attribute is not initialised."
        DefaultAttr.__init__(self, frame_=frame_, id_=id_)
        self.image = None
        self.surface = surface_
        self.layer = layer_
        self.blend = blend_
        self.rect = rect_
        # add extra attributes if necessary
        for key, value in kwargs.items():
            setattr(self, key, value)


class RotateSprite(StaticSprite):
    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None,
                 rotation_: int = 0):
        """
        RotationSprite class is used for object rotating into the scene.

        :param frame_: integer > 0; The actual frame number
        :param id_: integer; object memory location
        :param surface_:  string; sprite surface name e.g 'P1_SURFACE'
        :param layer_: integer < 0; Sprite layer
        :param blend_: integer > 0; blending mode
        :param rect_: pygame.Rect; position and sprite shapes
        :param rotation_: integer; Object rotation transformation in degrees.
        """
        StaticSprite.__init__(self, frame_=frame_, id_=id_, surface_=surface_,
                              layer_=layer_, blend_=blend_, rect_=rect_)
        self.rotation = rotation_


class ScaleSprite(StaticSprite):
    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None,
                 scale_: int = 1):
        """
        ScaleSprite class is used for object undertaking scaling transformation.

        :param frame_: integer > 0; The actual frame number
        :param id_: integer; object memory location
        :param surface_: string; sprite surface name e.g 'P1_SURFACE'
        :param layer_: integer < 0; Sprite layer
        :param blend_: integer > 0; blending mode
        :param rect_: pygame.Rect; position and sprite shapes
        :param scale_: float; Scaling transformation ]0 , 1] default = 1 (no transformation)
        """
        StaticSprite.__init__(self, frame_=frame_, id_=id_, surface_=surface_,
                              layer_=layer_, blend_=blend_, rect_=rect_)
        self.scale = scale_


class TransformSprite(StaticSprite):
    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None,
                 rotation_: int = 0, scale_: float = 1.0):
        """
        TransformSprite class is used for object undertaking scaling and rotation transformations

        :param frame_: integer > 0; The actual frame number
        :param id_: integer; object memory location
        :param surface_: string; sprite surface name e.g 'P1_SURFACE'
        :param layer_: integer < 0; Sprite layer
        :param blend_: integer > 0; blending mode
        :param rect_: pygame.Rect; position and sprite shapes
        :param rotation_: integer; Object rotation transformation in degrees.
        :param scale_: float or int; Scaling transformation ]0 , 1] default = 1 (no transformation)
        """
        StaticSprite.__init__(self, frame_=frame_, id_=id_, surface_=surface_,
                              layer_=layer_, blend_=blend_, rect_=rect_)
        self.rotation = rotation_
        self.scale = scale_


class AnimatedSprite(StaticSprite):
    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None,
                 index_: int = 0, rotation_: int = 0, scale_: int = 1):
        """

        :param frame_:
        :param id_:
        :param surface_:
        :param layer_:
        :param blend_:
        :param rect_:
        :param index_:
        :param rotation_:
        :param scale_:
        """
        StaticSprite.__init__(self, frame_=frame_, id_=id_, surface_=surface_,
                              layer_=layer_, blend_=blend_, rect_=rect_)
        self.index = index_
        self.rotation = rotation_
        self.scale = scale_


class DetectCollisionSprite(AnimatedSprite):
    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None,
                 index_: int = 0, rotation_: int = 0, scale_: int = 1, damage_: int = 0,
                 life_: int = 0, points_: int = 0):
        """

        :param frame_:
        :param id_:
        :param surface_:
        :param layer_:
        :param blend_:
        :param rect_:
        :param index_:
        :param rotation_:
        :param scale_:
        :param damage_:
        :param life_:
        :param points_:
        """
        AnimatedSprite.__init__(self, frame_=frame_, id_=id_, surface_=surface_,
                                layer_=layer_, blend_=blend_, rect_=rect_, index_=index_,
                                rotation_=rotation_, scale_=scale_)
        self.damage = damage_
        self.life = life_
        self.points = points_


class BlendSprite(object):
    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None,
                 parent_=None, pos_=(0, 0), index_=0, **kwargs):
        """

        :param frame_:
        :param id_:
        :param surface_:
        :param layer_:
        :param blend_:
        :param rect_:
        :param parent_:
        :param pos_:
        :param index_:
        :param kwargs:
        """
        assert parent_ is not None, "parent_ attribute is not initialised."
        self.frame = frame_
        self.id_ = id_
        self.image = None
        self.surface = surface_
        self.parent = parent_
        self.layer = layer_
        self.blend = blend_
        self.rect = rect_
        self.pos = pos_
        self.index = index_
        for key, value in kwargs.items():
            setattr(self, key, value)


class Broadcast(object):

    MessageQueue = []

    def __init__(self, object_):

        if isinstance(object_, (DefaultAttr, EventAttr, SoundAttr, StaticSprite,
                                AnimatedSprite, DetectCollisionSprite, BlendSprite)):
            try:
                if hasattr(object, '__dict__'):
                    for attr, value in object_.__dict__.items():
                        setattr(self, attr, value)
                else:
                    raise AssertionError('Python object missing __dict__ attribute')

            except AttributeError as description:
                raise AttributeError(description)
        else:
            raise AssertionError(
                'Broadcast object %s not recognize type:%s' % (object_, type(object_)))

    def update(self, attribute_to_change_: dict):
        try:

            for attr, new_value in attribute_to_change_.items():
                assert hasattr(self, attr), "Object does not have current attribute <%s> " % attr
                setattr(self, attr, new_value)

        except AttributeError as description:
            raise AttributeError(description)

    @staticmethod
    def show(object_: dict):
        try:

            for attr, new_value in object_.__dict__.items():
                print(attr, ' : ', new_value)

        except AttributeError as description:
            raise AttributeError(description)

    @staticmethod
    def get_flag(sprite_: pygame.sprite.Sprite) -> str:
        # set the default value 'RGB'
        format_ = 'RGB'
        if hasattr(sprite_, 'image'):
            flags = sprite_.image.get_flags()
            # Check if the surface uses source alpha blending
            if flags & pygame.SRCALPHA == pygame.SRCALPHA:
                format_ = 'RGBA'
            else:
                format_ = 'RGB'
        return format_

    # Extract the layer from the sprite.
    # if the sprite does not have a layer attribute
    # return 0, the sprite will be at the top level.
    @staticmethod
    def get_layer(sprite_: pygame.sprite.Sprite) -> int:
        if hasattr(sprite_, 'layer'):
            layer = sprite_.layer
        else:
            layer = 0
        return layer

    # Add sprite messages to the queue
    def add(self) -> None:
        Broadcast.MessageQueue.append(self)

    # Indirectly assign a sprite to the internal queue
    def queue(self) -> None:
        self.add()

    # Broadcast message to release the waiting client lock
    def next_frame(self) -> None:
        self.add()

    # Broadcast Sound messages
    def play(self) -> None:
        self.add()

    # Empty the queue
    @staticmethod
    def empty() -> None:
        Broadcast.MessageQueue = []

    # Push the signal to be broadcast immediately.
    # On the client side the signal will be retrieved and
    # processed but the changes will display onto the screen
    # only after sending (by the server) next_frame signal,
    # see method next_frame above for more information
    @staticmethod
    def push_message() -> None:
        GL.SIGNAL.set()
