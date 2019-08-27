

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


from random import randint, choice

try:
    import pygame
except ImportError:
    print("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")
    raise SystemExit

try:
    from NetworkBroadcast import Broadcast, TransformSprite, DetectCollisionSprite, SoundAttr
    from Explosions import Explosion
    from Textures import EXPLOSION1, HALO_SPRITE12, HALO_SPRITE14, \
        MULT_ASTEROID_32, MULT_ASTEROID_64, LAVA
    from Sounds import EXPLOSION_SOUND, IMPACT1, IMPACT
    from CreateHalo import AsteroidHalo
    from GLOBAL import GL
except ImportError:
    print("\nOne or more game libraries is missing on your system."
          "\nDownload the source code from:\n"
          "https://github.com/yoyoberenguer/MultiplayerGameEngine.git")
    raise SystemExit


class Debris(pygame.sprite.Sprite):

    containers = None
    image = None

    def __init__(self,
                 asteroid_name_: str,
                 pos_: tuple,
                 gl_: GL,
                 blend_: int = 0,
                 timing_: int = 16,
                 layer_: int = -2):
        """
        Create debris after asteroid explosion or collision

        :param asteroid_name_: string; Parent name (not used)
        :param pos_: tuple, representing the impact position (x, y)
        :param gl_: class GL, global constants
        :param blend_: integer; Sprite blend effect, must be > 0 or any of the following BLEND_RGBA_ADD,
        BLEND_RGBA_SUB, BLEND_RGBA_MULT, BLEND_RGBA_MIN, BLEND_RGBA_MAX BLEND_RGB_ADD,
        BLEND_RGB_SUB, BLEND_RGB_MULT, BLEND_RGB_MIN, BLEND_RGB_MAX
        :param timing_: integer; Sprite refreshing time in milliseconds, must be >=0
        :param layer_: integer; Sprite layer must be <=0 (0 is the top layer)
        """

        assert isinstance(asteroid_name_, str), \
            "Positional argument <asteroid_name_> is type %s , expecting string." % type(asteroid_name_)
        assert isinstance(pos_, tuple), \
            "Positional argument <pos_> is type %s , expecting tuple." % type(pos_)
        assert isinstance(timing_, int), \
            "Positional argument <timing_> is type %s , expecting integer." % type(timing_)
        assert isinstance(blend_, int), \
            "Positional argument <blend_> is type %s , expecting integer." % type(blend_)
        assert isinstance(layer_, int), \
            "Positional argument <layer_> is type %s , expecting integer." % type(layer_)

        if self.containers is None:
            raise ValueError('Debris.containers is not initialised.\nMake sure to assign the containers to'
                             ' a pygame group prior instantiation.\ne.g: Debris.containers = '
                             'pygame.sprite.Group()')
        if self.image is None:
            raise ValueError("Debris.image is not initialised.\nMake sure to assign a texture to "
                             "prior instantiation.\ne.g: Debris.image = 'CHOOSE_YOUR_TEXTURE'")

        if timing_ < 0:
            raise ValueError('Positional argument timing_ cannot be < 0')
        if blend_ < 0:
            raise ValueError('Positional argument blend_ cannot be < 0')
        if layer_ > 0:
            raise ValueError('Positional argument layer_ cannot be > 0')

        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        # change sprite layer
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.image = Debris.image
        self.images_copy = Debris.image.copy()
        self.rect = self.image.get_rect(center=pos_)
        self.w, self.h = pygame.display.get_surface().get_size()
        self.speed = pygame.math.Vector2(randint(-4, +4), randint(1, +8))
        self.timing = timing_
        self.dt = 0
        self.gl = gl_
        self.asteroid_name = asteroid_name_     # not used
        self.blend = blend_
        self.layer = layer_

    def update(self):
        """
        Update debris sprite
        :return:
        """
        if self.dt > self.timing:

            if self.rect.colliderect(self.gl.SCREENRECT):

                self.rect.move_ip(self.speed)
                self.dt = 0

            else:
                self.kill()

        self.dt += self.gl.TIME_PASSED_SECONDS


class Asteroid(pygame.sprite.Sprite):

    containers = None
    image = None

    def __init__(self,
                 asteroid_name_: str,
                 gl_,
                 blend_: int = 0,
                 rotation_: int = 0,
                 scale_: int = 1,
                 timing_: int = 16,
                 layer_: int = 0):
        """

        :param asteroid_name_: strings, Asteroid name
        :param gl_: class GL (contains all the game constant)
        :param blend_: integer, Sprite blend effect, must be > 0
        :param rotation_: integer, Object rotation in degrees
        :param scale_: integer, Object scale value, default 1 -> no transformation. must be > 0
        :param timing_: integer; Refreshing time in milliseconds, must be > 0
        :param layer_: integer; Layer used. must be <= 0 (0 is the top layer)
        """

        assert isinstance(asteroid_name_, str), \
            "Positional argument <asteroid_name_> is type %s , expecting string." % type(asteroid_name_)
        assert isinstance(blend_, int), \
            "Positional argument <blend_> is type %s , expecting integer." % type(blend_)
        if blend_ < 0:
            raise ValueError('Positional attribute blend_ must be > 0')
        assert isinstance(rotation_, int), \
            "Positional argument <rotation_> is type %s , expecting integer." % type(rotation_)
        assert isinstance(scale_, float), \
            "Positional argument <scale_> is type %s , expecting float." % type(scale_)
        if scale_ < 0:
            raise ValueError('Positional attribute scale_ must be > 0')
        assert isinstance(timing_, int), \
            "Positional argument <timing_> is type %s , expecting integer." % type(timing_)
        if timing_ < 0:
            raise ValueError('Positional attribute timing_ must be >= 0')

        assert isinstance(layer_, int), \
            "Positional argument <layer_> is type %s , expecting integer." % type(layer_)
        if layer_ > 0:
            raise ValueError('Positional attribute layer_ must be <= 0')

        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        # change sprite layer
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.images_copy = Asteroid.image.copy()
        self.image = self.images_copy[0] if isinstance(Asteroid.image, list) else self.images_copy
        self.w, self.h = pygame.display.get_surface().get_size()
        self.rect = self.image.get_rect(
            center=(randint(0, self.w), -randint(0, self.h) - self.image.get_height()))
        self.speed = pygame.math.Vector2(
            randint(-2, +2), randint(1, +8))
        self.timing = timing_
        self.rotation = rotation_
        self.scale = scale_
        self.dt = 0
        self.gl = gl_
        self.asteroid_name = asteroid_name_
        self.blend = blend_
        self.mask = pygame.mask.from_surface(self.image)
        self.life = randint(self.rect.w,
                            max(self.rect.w, (self.rect.w >> 1) * 10))
        self.damage = self.life >> 1
        self.layer = layer_
        self.index = 0
        self.has_been_hit = False
        self.id_ = id(self)
        self.asteroid_object = Broadcast(self.make_object())
        self.explosion_sound_object = Broadcast(self.make_sound_object('EXPLOSION_SOUND'))
        self.impact_sound_object = Broadcast(self.make_sound_object('IMPACT'))

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

    def make_object(self) -> DetectCollisionSprite:
        """
        Create a network sprite object

        :return: DetectCollisionSprite object
        """
        return DetectCollisionSprite(
                frame_=self.gl.FRAME, id_=self.id_, surface_=self.asteroid_name,
                layer_=self.layer, blend_=self.blend, rect_=self.rect,
                rotation_=self.rotation, scale_=self.scale, damage_=self.damage, life_=self.life)

    def make_debris(self) -> None:
        """
        Create sprite debris (different sizes 32x32, 64x64 pixels)

        :return:None
        """

        size_x, size_y = self.image.get_size()
        if size_x > 128:
            aster = MULT_ASTEROID_64
            name = 'MULT_ASTEROID_64'
        else:
            aster = MULT_ASTEROID_32
            name = 'MULT_ASTEROID_32'

        length = len(aster) - 1
        for r in range(8 if size_x > 255 else 6):
            Debris.containers = self.gl.All
            element = randint(0, length)
            Debris.image = aster[element]
            Debris(asteroid_name_=name + '[' + str(element) + ']',
                   pos_=self.rect.center, gl_=self.gl,
                   blend_=0, timing_=16, layer_=-2)

    def explode(self) -> None:
        """
        Create an explosion sprite when asteroid life points < 1

        :return: None
        """
        if self.alive():
            # Create queue sprite
            Explosion.images = EXPLOSION1
            Explosion(self, self.rect.center,
                      self.gl, self.timing, 0, texture_name_='EXPLOSION1')  # self.layer)

            self.gl.MIXER.play(sound_=EXPLOSION_SOUND, loop_=False, priority_=0,
                               volume_=1.0, fade_out_ms=0, panning_=True,
                               name_='EXPLOSION_SOUND', x_=self.rect.centerx,
                               object_id_=id(EXPLOSION_SOUND),
                               screenrect_=self.gl.SCREENRECT)           
            self.explosion_sound_object.play()

            # Create Halo sprite
            AsteroidHalo.images = choice([HALO_SPRITE12, HALO_SPRITE14])
            AsteroidHalo.containers = self.gl.All
            AsteroidHalo(texture_name_='HALO_SPRITE12'
                         if AsteroidHalo.images == HALO_SPRITE12 else 'HALO_SPRITE14',
                         object_=self, timing_=10)

            self.make_debris()
            self.kill()

    def hit(self, damage_: int) -> None:
        """
        Check asteroid life after laser collision.

        :param damage_: integer; Damage received
        :return: None
        """
        assert isinstance(damage_, int), \
            "Positional argument <damage_> is type %s , expecting integer." % type(damage_)
        if damage_ < 0:
            raise ValueError('positional argument damage_ cannot be < 0')

        self.life -= damage_
        self.has_been_hit = True

        if self.life < 1:
            self.explode()

    def collide(self, damage_) -> None:
        """
        Check asteroid life after collision with players or transport

        :param damage_:
        :return: None
        """
        assert isinstance(damage_, int), \
            "Positional argument <damage_> is type %s , expecting integer." % type(damage_)
        if damage_ < 0:
            raise ValueError('positional argument damage_ cannot be < 0')

        self.life -= damage_
        # play the impact sound locally
        self.gl.MIXER.play(sound_=IMPACT1, loop_=False, priority_=0,
                           volume_=1.0, fade_out_ms=0, panning_=True,
                           name_='IMPACT', x_=self.rect.centerx,
                           object_id_=id(IMPACT1),
                           screenrect_=self.gl.SCREENRECT)
        self.impact_sound_object.play()

        if self.life < 1:
            self.make_debris()
            self.kill()
        ...

    def update(self) -> None:
        """
        Update asteroid sprites.

        :return: None
        """

        if self.dt > self.timing:

            # self.image = self.images_copy.copy()
            if self.has_been_hit:
                self.image.blit(LAVA[self.index % len(LAVA) - 1],
                                (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                self.index += 1
                self.has_been_hit = False
                # if self.index > len(LAVA) - 2:
                #    self.has_been_hit = False
                #    self.index = 0

            # self.image = self.images_copy.copy()
            if self.rotation != 0:
                self.mask = pygame.mask.from_surface(self.image)

            if self.rect.midbottom[1] > 0:
                if not self.rect.colliderect(self.gl.SCREENRECT):
                    self.kill()

            self.rect.move_ip(self.speed)
            self.dt = 0

        if self.rect.colliderect(self.gl.SCREENRECT) and self.alive():
            
            self.asteroid_object.update({'frame': self.gl.FRAME, 'rect': self.rect, 'life': self.life})
            self.asteroid_object.queue()

        self.dt += self.gl.TIME_PASSED_SECONDS
