import threading
from random import randint

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
        self.sound_name = sound_name_
        self.rect = rect_


class DeleteSpriteCommand(object):

    def __init__(self, frame_: int, to_delete_: dict):
        """
        Delete one or many sprites from the client(s) display.

        :param frame_: integer > 0; The actual frame number
        :to_delete_: dict; contains all the id (sprite memory location, or unique
        identification number) used for deleting sprite(s) on the client side.
        {'12354565', 'surface1', 465456212':'surface2' ...]
        """
        self.id_ = id(self)
        self.frame = frame_
        self.to_delete = to_delete_


class StaticSprite(DefaultAttr):

    def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                 layer_: int = None, blend_: int = None, rect_: pygame.Rect = None,
                 damage_: int = None, life_: int = None, impact_: int=None, **kwargs):
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
        DefaultAttr.__init__(self, frame_=frame_, id_=id_)
        self.image = None
        self.surface = surface_
        self.layer = layer_
        self.blend = blend_
        self.rect = rect_
        self.damage = damage_
        self.life = life_
        self.impact = impact_
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
    live_object_inventory = set()      # contains all id (all the living objects)

    def __init__(self, object_):

        if isinstance(object_, (DefaultAttr, EventAttr, SoundAttr, StaticSprite,
                                AnimatedSprite, DetectCollisionSprite, BlendSprite, DeleteSpriteCommand)):

            # object_.__init__(self)

            try:
                if hasattr(object_, '__dict__'):
                    for attr, value in object_.__dict__.items():
                        setattr(self, attr, value)
                else:
                    raise AssertionError('Python object missing __dict__ attribute')

            except AttributeError as description:
                raise AttributeError(description)

        else:
            raise AssertionError(
                'Broadcast object %s not recognize type:%s' % (object_, type(object_)))

    @staticmethod
    def has(element_) -> bool:
        if element_ in Broadcast.MessageQueue:
            return True
        else:
            return False

    def update(self, attribute_to_change_: dict):
        try:
            for attr, new_value in attribute_to_change_.items():
                assert hasattr(self, attr), "Object does not have current attribute %s " % attr
                setattr(self, attr, new_value)

        except AttributeError as description:
            raise AttributeError(description)

    @staticmethod
    def sort_message_queue():
        """
        Sort all network messages from MessageQueue.
        Regroup all DeleteSpriteCommand messages into a single unit
        referencing all the sprite to be delete.
        """

        dels_ = {}      # dict containing the sprite id and surface name like {'id':'surface', ...}
        others = set()  # set containing all network messages e.g DefaultAttr, EventAttr, SoundAttr, StaticSprite etc
        alive_ = None   # Ideally a set that will contains all the sprite id display on the server side (alive sprite)

        # todo need to check the frame ??
        for network_object in Broadcast.MessageQueue:

            if isinstance(network_object, DeleteSpriteCommand):
                dels_.update(network_object.to_delete)
                continue
            if isinstance(network_object, set):
                alive_ = network_object
                continue
            else:
                others.add(network_object)

        # Make it new
        Broadcast.MessageQueue = []
        # Add all the network message at once
        Broadcast.MessageQueue.extend(list(others))
        # Add the sprite to be delete
        if dels_:
            Broadcast.MessageQueue.append(DeleteSpriteCommand(GL.FRAME, to_delete_=dels_))

        # Add the set <live_object_inventory> to the broadcast message.
        # The set contains only id numbers like id(self).
        # The set will be used on the client side to determine if an object broadcast via the server
        # is dead or alive (ghost sprite, static sprite...see below for more info).

        # A delete broadcast message can be sent to the client(s) and can be omitted (networks drop or other factors...)
        # In such cases the client will not kill the instance associated to that specific sprite and a ghost
        # sprite will remains on the client display (static sprite, still responding to collisions etc).
        # To avoid that situation, the client checks every frames if any of the its sprites
        # contains in GL.All are still alive by comparing ids from GL.NetGroupAll and the set (see below code)

        # for spr_ in GL.NetGroupAll:
        #     if hasattr(spr_, 'id_'):
        #         if spr_.id_ not in GL.GROUP_ALIVE:    -> GL.GROUP_ALICE is equivalent to live_object_inventory
        #             spr_.remove(GL.All, GL.NetGroupAll, GL.ASTEROID)
        #             print('force kill %s id %s ' % (spr_.surface, spr_.id_))

        # A sprite id is inserted into live_object_inventory every new instance (as long as the sprite
        # needs to be broadcast to the client(s)).
        # An id is removed from the set when the sprite is delete (killed /collide etc).
        # Instances' s update method is call every 60 fps and sometimes below 30 fps.
        # Frequency discrepancy compare to the main loop speed,  will cause unusual effects such as :
        # - network messages and sprite object information behind what the server is displaying
        #   (causing ghost sprite on client display),
        # - object exploding on the server side and still showing on client sides etc.
        # - object dead on server side and still alive on client sides producing gems or sparks when hit by lasers
        # - object dead on server and object still taking damage on the client sides (when the object is killed
        #   on the server side, it will stop to be broadcast). This means that the client will stop receiving info/attributes
        #   concerning its life values and position.
        # To avoid those issues, we are inserting the code below in the server main loop:

        # Broadcast.live_object_inventory = set()
        # for sprite_ in GL.All:
        #     if hasattr(sprite_, 'id_'):
        #         Broadcast.live_object_inventory.add(sprite_.id_)
        # Broadcast.MessageQueue.append(Broadcast.live_object_inventory)

        # Add the set containing all the sprite(s) id display on the server (inventory)
        if alive_:
            Broadcast.MessageQueue.append(alive_)

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
    def _add(self) -> None:
        """
        Put a network object in the queue, ready to be sent
        :return: None
        """
        Broadcast.MessageQueue.append(self)

    # Indirectly assign a sprite to the internal queue
    def queue(self) -> None:
        """
        Put a network object in the queue, ready to be sent
        :return: None
        """
        self._add()

    # Broadcast message to release the waiting client lock
    def next_frame(self) -> None:
        """
        Next frame command
        :return: None
        """
        self._add()

    # Broadcast Sound messages
    def play(self) -> None:
        """
        Play a sound on the client side
        :return: None
        """
        self._add()

    @staticmethod
    def remove_object_id(id_) -> None:
        """
        Remove object from the set.
        When an object is killed, it is compulsory to remove it
        from the set <make_list> in order to inform the client to
        remove it from its display (locally killed).
        :param id_: object id (memory location)
        :return: None
        """
        if id_ in Broadcast.live_object_inventory:
            Broadcast.live_object_inventory.remove(id_)
            
    @staticmethod
    def add_object_id(id_) -> None:
        """
        Add living object into a list,
        The set <make_list> reference all the living object on the
        server. That list will be compared every frames on the client
        side to make sure, no objects are frozen on the display.
        :param id_: object id (memory location)
        :return: None
        """
        if id_ not in Broadcast.live_object_inventory:
            Broadcast.live_object_inventory.add(id_)

    @staticmethod
    def clear_list() -> None:
        """
        Clear the list of all living object
        :return: None
        """
        Broadcast.live_object_inventory = set()

    # Empty the queue
    @staticmethod
    def empty() -> None:
        """
        Clear the list (no messages will be broadcast)
        Always empty the list prior the next frame, otherwise
        the list w will build up and unnecessary objects will be send to clients
        :return:
        """
        Broadcast.MessageQueue = []

    # Push the signal to be broadcast immediately.
    # On the client side the signal will be retrieved and
    # processed but the changes will display onto the screen
    # only after sending (by the server) next_frame signal,
    # see method next_frame above for more information
    @staticmethod
    def push_message() -> None:
        GL.SIGNAL.set()


if __name__ == '__main__':
    import pygame
    import sys


    class DefaultAttr(object):

        # __slots__ = ['frame', 'id_']

        def __init__(self, frame_: int = None, id_: int = None):
            """
            DefaultAttr class contains all the default attribute shared by all network objects including : sprite,
            Event and SoundEvent.

            :param frame_: integer > 0; The actual frame number
            :param id_: integer; object memory location
            """
            self.frame = frame_
            self.id_ = id_ if id_ is not None else id(self)


    class StaticSprite(DefaultAttr):

        # __slots__ = ['frame', 'id_', 'image', 'surface', 'layer', 'blend', 'rect']

        def __init__(self, frame_: int = None, id_: int = None, surface_: str = '',
                     layer_: int = None, blend_: int = None, rect_: pygame.Rect = None):

            DefaultAttr.__init__(self, frame_=frame_, id_=id_)

            self.image = None
            self.surface = surface_
            self.layer = layer_
            self.blend = blend_
            self.rect = rect_

    myrect = pygame.Rect(0, 0, 0, 0)

    sprite__ = StaticSprite(frame_=0, id_=10000, surface_='TEST', layer_=0, blend_=0, rect_=myrect)
    print(sys.getsizeof(sprite__))
    print(hasattr(sprite__, 'frame'))
    print(hasattr(sprite__, 'id_'))
    print(hasattr(sprite__, 'surface'))
    print(hasattr(sprite__, 'layer'))
    # print(sprite__.__slots__)

    class Toto(object):
        def __init__(self):
            self.a = 10

    b = Toto()
    print(sys.getsizeof(b))

    for r in range(10):
        Broadcast.MessageQueue.append(
            DeleteSpriteCommand(0, {str(randint(0, 10000000)): 'surface1', str(randint(0, 10000000)): 'surface2'}))
        Broadcast.MessageQueue.append(
            StaticSprite(frame_=0, id_=10000, surface_='TEST', layer_=0, blend_=0, rect_=myrect))

    print(Broadcast.MessageQueue)
    Broadcast.sort_message_queue()
    print(Broadcast.MessageQueue)

    for msg in Broadcast.MessageQueue:
        if isinstance(msg, DeleteSpriteCommand):
            print(msg.to_delete)

    import timeit

    s = timeit.timeit('Broadcast.sort_message_queue()',
                      'from __main__ import Broadcast', number=1000000)
    print(s)
