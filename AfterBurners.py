

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"

try:
    import pygame
except ImportError:
    print("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")
    raise SystemExit

try:
    from NetworkBroadcast import Broadcast, AnimatedSprite
except ImportError:
    print("\nOne or more game libraries is missing on your system."
          "\nDownload the source code from:\n"
          "https://github.com/yoyoberenguer/MultiplayerGameEngine.git")
    raise SystemExit


class AfterBurner(pygame.sprite.Sprite):

    containers = None
    images = None

    def __init__(self, parent_, gl_, offset_,
                 timing_=16, blend_=0, layer_=0, texture_name_='EXHAUST'):
        """
        Create an exhaust effect for the player's

        :param parent_: Player's instance (Player1 or Player2)
        :param gl_: Class GL (contains all the game constants
        :param offset_: tuple, offset location of the afterburner sprite (offset from the center)
        :param timing_: integer; Sprite refreshing time must be > 0
        :param blend_: integer; Sprite blending effect, must be > 0 or any of the following BLEND_RGBA_ADD,
        BLEND_RGBA_SUB, BLEND_RGBA_MULT, BLEND_RGBA_MIN, BLEND_RGBA_MAX BLEND_RGB_ADD,
        BLEND_RGB_SUB, BLEND_RGB_MULT, BLEND_RGB_MIN, BLEND_RGB_MAX
        :param layer_: integer; must be <= 0 (0 is the top layer)
        :param texture_name_: string corresponding to the texture used.
        """

        if parent_ is None:
            raise ValueError('Positional argument <parent_> cannot be None.')
        if gl_ is None:
            raise ValueError('Positional argument <gl_> cannot be None.')
        if offset_ is None:
            raise ValueError('Positional argument <offset_> cannot be None.')

        assert isinstance(offset_, tuple), \
            "Positional argument <offset_> is type %s , expecting tuple." % type(offset_)
        assert isinstance(timing_, int), \
            "Positional argument <timing_> is type %s , expecting integer." % type(timing_)
        assert isinstance(blend_, int), \
            "Positional argument <blend_> is type %s , expecting integer." % type(blend_)
        assert isinstance(layer_, int), \
            "Positional argument <layer_> is type %s , expecting integer." % type(layer_)
        assert isinstance(texture_name_, str), \
            "Positional argument <texture_name_> is type %s , expecting str." % type(texture_name_)

        if self.containers is None:
            raise ValueError('AfterBurner.containers is not initialised.\nMake sure to assign the containers to'
                             ' a pygame group prior instantiation.\ne.g: AfterBurner.containers = '
                             'pygame.sprite.Group()')
        if self.images is None:
            raise ValueError("AfterBurner.images is not initialised.\nMake sure to assign a texture to "
                             "prior instantiation.\ne.g: AfterBurner.images = 'EXHAUST'")

        if timing_ < 0:
            raise ValueError('Positional argument timing_ cannot be < 0')

        self.layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)

        self.images = AfterBurner.images
        self.image = self.images[0] if isinstance(self.images, list) else self.images
        self.parent = parent_
        self.offset = offset_
        x, y = self.parent.rect.centerx + self.offset[0], self.parent.rect.centery + self.offset[1]
        self.rect = self.image.get_rect(center=(x, y))
        self.timing = timing_
        self.dt = 0
        self.index = 0
        self.gl = gl_
        self.blend = blend_
        self.texture_name = texture_name_
        self.id_ = id(self)
        self.afterburner_object = Broadcast(self.make_object())

    def make_object(self) -> AnimatedSprite:
        """
        Create a network object (AnimatedSprite)
        :return: AnimatedSprite
        """
        return AnimatedSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.texture_name,
                              layer_=self.layer, blend_=self.blend, rect_=self.rect,
                              index_=self.index)
        
    def update(self) -> None:
        """
        Update the sprite.

        :return: None
        """
        if self.dt > self.timing:

            # checking if Player1 is still alive
            if self.parent.alive():

                # display animation if self.images is a list.
                if isinstance(self.images, list):
                    self.image = self.images[self.index % len(self.images) - 1]

                x, y = self.parent.rect.centerx + self.offset[0], self.parent.rect.centery + self.offset[1]
                self.rect.center = (x, y)

                self.dt = 0
                self.index += 1
            else:
                self.kill()

        # Create a network object if parent is alive and if sprite
        # position is still in the display 'self.gl.SCREENRECT'
        if self.parent.alive():
            if self.rect.colliderect(self.gl.SCREENRECT):
                self.afterburner_object.update({'frame': self.gl.FRAME, 'rect': self.rect, 'index': self.index})
                self.afterburner_object.queue()
                ...

        self.dt += self.gl.TIME_PASSED_SECONDS
