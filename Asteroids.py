import sys

import math

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


from random import randint, choice, uniform

try:
    import pygame
except ImportError:
    print("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")
    raise SystemExit

try:
    from NetworkBroadcast import Broadcast, TransformSprite, \
        DetectCollisionSprite, SoundAttr, DeleteSpriteCommand
    from Explosions import Explosion
    from Textures import EXPLOSION1, HALO_SPRITE12, HALO_SPRITE14, \
        MULT_ASTEROID_32, MULT_ASTEROID_64, LAVA, FIRE_PARTICLES, COSMIC_DUST2, COSMIC_DUST1
    from Sounds import EXPLOSION_SOUND, IMPACT1, IMPACT
    from CreateHalo import AsteroidHalo
    from GLOBAL import GL
    from Gems import MakeGems
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
                 layer_: int = -2,
                 particles_: bool = True
                 ):
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
        :param particles_: bool; Particles effect after asteroid desintegration
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
        assert isinstance(particles_, bool), \
            "Positional argument <particles_> is type %s , expecting boolean." % type(particles_)

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
        self.rect = self.image.get_rect(center=pos_)
        self.speed = pygame.math.Vector2(uniform(-10, +10), uniform(-8, +8))
        self.damage = randint(5, 15)
        self.timing = timing_
        self.dt = 0
        self.fxdt = 0
        self.gl = gl_
        self.asteroid_name = asteroid_name_     # not used
        self.blend = blend_
        self.layer = layer_

        self.life = self.damage
        self.points = self.life
        self.rotation = 0
        self.scale = 1.0
        self.id_ = id(self)
        self.asteroid_object = Broadcast(self.make_object())

        self.vertex_array = []

        # todo create instances in the vertex_array (declare in global)
        #  before instanciating debris.
        #  make a copy of the vertex_array and goes through the list changing arguments:
        #  position_, vector_. Assign the list to self.vertex_array
        if particles_:      
            angle = math.radians(uniform(0, 359))
            self.asteroid_particles_fx(position_=pygame.math.Vector2(self.rect.center),
                                       vector_=pygame.math.Vector2(
                                           math.cos(angle) * randint(5, 10), math.sin(angle) * randint(5, 10)),
                                       images_=FIRE_PARTICLES.copy(),
                                       layer_=self.layer, blend_=pygame.BLEND_RGB_ADD)
        Broadcast.add_object_id(self.id_)

    def delete_object(self) -> DeleteSpriteCommand:
        """
        Send a command to kill an object on client side.

        :return: DetectCollisionSprite object
        """
        return DeleteSpriteCommand(frame_=self.gl.FRAME, to_delete_={self.id_: self.asteroid_name})

    def make_object(self) -> DetectCollisionSprite:
        """
        Create a network sprite object.

        :return: DetectCollisionSprite object
        """
        return DetectCollisionSprite(
                frame_=self.gl.FRAME, id_=self.id_, surface_=self.asteroid_name,
                layer_=self.layer, blend_=self.blend, rect_=self.rect,
                rotation_=self.rotation, scale_=self.scale, damage_=self.damage,
                life_=self.life, points_=self.points)

    def remove_particle(self, p_) -> None:
        """
        Remove the sprite from the group it belongs to and remove
        the object from the vertex_array
        :param p_: pygame.sprite.Sprite
        :return: None
        """
        p_.kill()
        if p_ in self.vertex_array:
            self.vertex_array.remove(p_)

    def display_asteroid_particles_fx(self) -> None:
        # Display asteroid tail debris.
        if self.fxdt > self.timing - 8:     # 8 ms

            for p_ in self.vertex_array:

                p_.image = p_.images[p_.index % p_.length]      # load the next surface
                p_.rect.move_ip(p_.vector)                      # Move the particle
                p_.vector *= 0.9999                             # particle deceleration / attenuation
                rect_centre = p_.rect.center                    # rect centre after deceleration

                next_image = p_.images[(p_.index + 1) % p_.length]  # Load the next image
                # Decrease image dimensions (re-scale)
                try:
                    particle_size = pygame.math.Vector2(p_.w - p_.index * 4, p_.h - p_.index * 4)
                    # transform next image (re-scale)
                    p_.images[(p_.index + 1) % p_.length] = \
                        pygame.transform.scale(next_image, (int(particle_size.x), int(particle_size.y)))
                    # Redefine the rectangle after transformation to avoid a collapsing movement
                    # to the right
                    p_.rect = p_.images[(p_.index + 1) % p_.length].get_rect(center=rect_centre)

                    # delete the particle before exception
                    if particle_size.length() < 25:
                        self.remove_particle(p_)

                except (ValueError, IndexError):
                    self.remove_particle(p_)

                if not p_.rect.colliderect(self.gl.SCREENRECT) or p_.vector.length() < 1:
                    self.remove_particle(p_)

                p_.index += 1
            self.fxdt = 0
        else:
            self.fxdt += self.gl.TIME_PASSED_SECONDS

    def asteroid_particles_fx(self,
                              position_,  # particle starting location (tuple or pygame.math.Vector2)
                              vector_,    # particle speed, pygame.math.Vector2
                              images_,    # surface used for the particle, (list of pygame.Surface)
                              layer_=0,   # Layer used to display the particles (int)
                              blend_=pygame.BLEND_RGB_ADD  # Blend mode (int)
                              ) -> None:
        """
        Create bright debris after explosion or asteroid collision
        """
        # Cap the number of particles to avoid lag
        # if len(self.gl.FIRE_PARTICLES_FX) > 100:
        #    return
        # Create fire particles when the aircraft is disintegrating
        sprite_ = pygame.sprite.Sprite()
        self.gl.All.add(sprite_)
        # self.gl.FIRE_PARTICLES_FX.add(sprite__)
        # assign the particle to a specific layer
        if isinstance(self.gl.All, pygame.sprite.LayeredUpdates):
            self.gl.All.change_layer(sprite_, layer_)
        sprite_.layer = layer_
        sprite_.blend = blend_  # use the additive mode
        sprite_.images = images_
        sprite_.image = images_[0]
        sprite_.rect = sprite_.image.get_rect(center=position_)
        sprite_.vector = vector_    # vector
        sprite_.w, sprite_.h = sprite_.image.get_size()
        sprite_.index = 0
        sprite_.length = len(sprite_.images) - 1
        # assign update method to self.display_fire_particle_fx
        # (local method to display the particles)
        sprite_.update = self.display_asteroid_particles_fx
        self.vertex_array.append(sprite_)

    def collide(self, player_=None,  damage_: int = 0) -> None:
        """

        :return:
        """
        self.quit()
        ...

    def hit(self, player_=None, damage_: int = 0) -> None:
        """
        Check asteroid life after laser collision.

        :param player_: Player instance
        :param damage_: integer; Damage received
        :return: None
        """
        self.quit()
        ...
        
    def quit(self) -> None:
        Broadcast.remove_object_id(self.id_)
        obj = self.delete_object()
        broadcast_object = Broadcast(obj)
        broadcast_object.queue()
        self.kill()
        ...

    def update(self) -> None:
        """
        Update debris sprite
        :return:
        """
        # Inside the 60FPS Area
        if self.dt > self.timing:

            if self.rect.colliderect(self.gl.SCREENRECT):
                self.rect.move_ip(self.speed)
            else:
                self.quit()
                return

            self.asteroid_object.update({'frame': self.gl.FRAME,
                                         'id_': self.id_,
                                         'rect': self.rect,
                                         'life': self.life})
            self.asteroid_object.queue()
            self.dt = 0
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        # Outside the 60FPS area


class Asteroid(pygame.sprite.Sprite):

    containers = None
    image = None

    def __init__(self,
                 asteroid_name_: str,
                 gl_,
                 blend_: int = 0,
                 rotation_: int = 0,
                 scale_: int = 1,
                 timing_: int = 8,
                 layer_: int = 0):
        """

        :param asteroid_name_: strings, MirroredAsteroidClass name
        :param gl_: class GL (contains all the game constant)
        :param blend_: integer, Sprite blend effect, must be > 0
        :param rotation_: integer, Object rotation in degrees
        :param scale_: integer, Object scale value, default 1 -> no transformation. must be > 0
        :param timing_: integer; Refreshing time in milliseconds, must be > 0
        :param layer_: integer; Layer used. must be <= 0 (0 is the top layer)
        """
        """
        assert isinstance(asteroid_name_, str), \
            "Positional argument <asteroid_name_> is type %s , expecting string." % type(asteroid_name_)
        assert isinstance(blend_, int), \
            "Positional argument <blend_> is type %s , expecting integer." % type(blend_)
        if blend_ < 0:
            raise ValueError('Positional attribute blend_ must be > 0')
        assert isinstance(rotation_, (float, int)), \
            "Positional argument <rotation_> is type %s , expecting float or integer." % type(rotation_)
        assert isinstance(scale_, (float, int)), \
            "Positional argument <scale_> is type %s , expecting float or integer." % type(scale_)
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
        """
        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        # change sprite layer
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.images_copy = Asteroid.image.copy()
        self.image = self.images_copy[0] if isinstance(Asteroid.image, list) else self.images_copy
        self.w, self.h = pygame.display.get_surface().get_size()

        self.appearance_frame = 0  # randint(100, 100240)  # When the asteroid start moving

        if asteroid_name_ == 'MAJOR_ASTEROID':
            self.speed = pygame.math.Vector2(0, 1)
            self.rect = self.image.get_rect(
                center=((self.w >> 1), -self.image.get_height()))
            # MirroredAsteroidClass life points (proportional to its size)
            self.life = 5000
            self.damage = self.life * 2
        else:

            self.rect = self.image.get_rect(
                 center=(randint(0, self.w), -randint(0, self.h) - self.image.get_height()))
            # self.rect = self.image.get_rect(center=(self.w // 2, - self.image.get_height()))

            self.speed = pygame.math.Vector2(0,
                                             uniform(+4, +8))  # * round(self.appearance_frame / 4000))

            if self.speed.length() == 0:
                self.speed = pygame.math.Vector2(0, 1)

            # MirroredAsteroidClass life points (proportional to its size)
            self.life = randint(self.rect.w,
                                max(self.rect.w, (self.rect.w >> 1) * 10))
            # Collision damage, how much life point
            # will be removed from players and transport in case of collision
            self.damage = self.life >> 1

        self.timing = timing_
        self.rotation = rotation_
        self.scale = scale_
        self.dt = 0
        self.gl = gl_
        self.asteroid_name = asteroid_name_
        self.blend = blend_
        # No need to pre-calculate the mask as all asteroid instanciation is
        # done before the main loop
        self.mask = pygame.mask.from_surface(self.image)

        # MirroredAsteroidClass value in case of destruction.
        self.points = self.life

        self.layer = layer_
        self.index = 0
        self.has_been_hit = False
        self.id_ = id(self)
        self.asteroid_object = Broadcast(self.make_object())
        self.impact_sound_object = Broadcast(self.make_sound_object('IMPACT'))

        Broadcast.add_object_id(self.id_)

    def delete_object(self) -> DeleteSpriteCommand:
        """
        Send a command to kill an object on client side.

        :return: DetectCollisionSprite object
        """
        return DeleteSpriteCommand(frame_=self.gl.FRAME, to_delete_={self.id_: self.asteroid_name})

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
                rotation_=self.rotation, scale_=self.scale, damage_=self.damage,
                life_=self.life, points_=self.points)

    def create_gems(self, player_) -> None:
        """
        Create collectable gems after asteroid disintegration.
        :param player_: player causing asteroid explosion
        :return: None
        """
        if player_ is None:
            raise ValueError("Argument player_ cannot be none!.")
        if hasattr(player_, 'alive'):
            if player_.alive():
                number = randint(3, 15)
                for _ in range(number):
                    if _ < number:
                        MakeGems.inventory = set()
                    MakeGems(gl_=self.gl,
                             player_=player_,
                             object_=self,
                             ratio_=1.0,
                             timing_=8,
                             offset_=pygame.Rect(
                                 self.rect.centerx, self.rect.centery, randint(-100, 100), randint(-100, 20)))

    def make_debris(self) -> None:
        """
        Create sprite debris (different sizes 32x32, 64x64 pixels)
        :return:None
        """

        if not globals().__contains__('MULT_ASTEROID_64'):
            raise NameError("Texture MULT_ASTEROID_64 is missing!"
                            "\nCheck file Texture.py for MULT_ASTEROID_64 assigment. ")

        if not globals().__contains__('MULT_ASTEROID_32'):
            raise NameError("Texture MULT_ASTEROID_32 is missing!"
                            "\nCheck file Texture.py for MULT_ASTEROID_32 assigment. ")

        size_x, size_y = self.image.get_size()

        if size_x > 128:
            aster = MULT_ASTEROID_64
            name = 'MULT_ASTEROID_64'

        else:
            aster = MULT_ASTEROID_32
            name = 'MULT_ASTEROID_32'

        length = len(aster) - 1
        if self.asteroid_name != 'MAJOR_ASTEROID':
            Debris.containers = self.gl.All, self.gl.ASTEROID
            for _ in range(8 if size_x > 255 else 6):
                element = randint(0, length)
                Debris.image = aster[element]
                Debris(asteroid_name_=name + '[' + str(element) + ']',
                       pos_=self.rect.center, gl_=self.gl,
                       blend_=0, timing_=16, layer_=-2, particles_=True)
        else:
            Debris.containers = self.gl.All, self.gl.ASTEROID
            aster = MULT_ASTEROID_64
            name = 'MULT_ASTEROID_64'
            length = len(aster) - 1
            for _ in range(10):
                element = randint(0, length)
                Debris.image = aster[element]
                Debris(asteroid_name_=name + '[' + str(element) + ']',
                       pos_=(self.rect.centerx + randint(-size_x, size_y),
                             self.rect.centery + randint(-size_x, size_y)), gl_=self.gl,
                       blend_=0, timing_=20, layer_=randint(-2, 0), particles_=False)

            aster = MULT_ASTEROID_32
            name = 'MULT_ASTEROID_32'
            length = len(aster) - 1
            for _ in range(10):
                element = randint(0, length)
                Debris.image = aster[element]
                Debris(asteroid_name_=name + '[' + str(element) + ']',
                       pos_=(self.rect.centerx + randint(-size_x, size_y),
                             self.rect.centery + randint(-size_x, size_y)), gl_=self.gl,
                       blend_=0, timing_=8, layer_=randint(-2, 0), particles_=False)

    def explode(self, player_) -> None:
        """
        Create an explosion sprite when asteroid life points < 1
        :param player_: Player causing asteroid explosion
        :return: None
        """

        if not globals().__contains__('EXPLOSION1'):
            raise NameError("Texture EXPLOSION1 is missing!"
                            "\nCheck file Texture.py for EXPLOSION1 assigment. ")
        # Create queue sprite
        Explosion.images = EXPLOSION1
        Explosion(self, self.rect.center,
                  self.gl, 8, 0, texture_name_='EXPLOSION1')  # self.layer)

        if not globals().__contains__('HALO_SPRITE12'):
            raise NameError("Texture HALO_SPRITE12 is missing!"
                            "\nCheck file Texture.py for HALO_SPRITE12 assigment. ")

        if not globals().__contains__('HALO_SPRITE14'):
            raise NameError("Texture HALO_SPRITE14 is missing!"
                            "\nCheck file Texture.py for HALO_SPRITE14 assigment. ")

        # Create Halo sprite
        AsteroidHalo.images = choice([HALO_SPRITE12, HALO_SPRITE14])
        AsteroidHalo.containers = self.gl.All
        AsteroidHalo(texture_name_='HALO_SPRITE12'
                     if AsteroidHalo.images is HALO_SPRITE12 else 'HALO_SPRITE14',
                     object_=self, timing_=8)

        self.make_debris()
        if player_ is not None:
            self.create_gems(player_)
        self.quit()

    def hit(self, player_=None, damage_: int = 0) -> None:
        """
        Check asteroid life after laser collision.

        :param player_: Player instance
        :param damage_: integer; Damage received
        :return: None
        """
        assert isinstance(damage_, int), \
            "Positional argument <damage_> is type %s , expecting integer." % type(damage_)
        if damage_ < 0:
            raise ValueError('positional argument damage_ cannot be < 0')

        self.life -= damage_
        self.has_been_hit = True if self.asteroid_name != 'MAJOR_ASTEROID' else False

        if self.life < 1:
            if player_ is not None:
                if hasattr(player_, 'update_score'):
                    player_.update_score(self.points)
            self.explode(player_)

    def collide(self, player_=None,  damage_: int = 0) -> None:
        """
        Check asteroid life after collision with players or transport

        :param player_: Player instance or transport
        :param damage_: integer; Damage received
        :return: None
        """
        assert isinstance(damage_, int), \
            "Positional argument <damage_> is type %s , expecting integer." % type(damage_)
        if damage_ < 0:
            raise ValueError('positional argument damage_ cannot be < 0')

        if not globals().__contains__('IMPACT1'):
            raise NameError("Sound IMPACT1 is missing!"
                            "\nCheck file Sounds.py for IMPACT1 assigment. ")
        if hasattr(self, 'life'):
            self.life -= damage_    # transfer damage to the asteroid (decrease life)
        else:
            raise AttributeError('self %s, %s does not have attribute life ' % (self, type(self)))

        # play asteroid burst sound locally
        self.gl.MIXER.play(sound_=IMPACT1, loop_=False, priority_=0,
                           volume_=1.0, fade_out_ms=0, panning_=True,
                           name_='IMPACT1', x_=self.rect.centerx,
                           object_id_=id(IMPACT1),
                           screenrect_=self.gl.SCREENRECT)

        # broadcast asteroid burst sound
        self.impact_sound_object.play()

        # check if asteroid life is still > 0
        if self.life < 1:

            # check who is colliding with the asteroid
            # if not colliding with transport, transfer score to player.
            if not type(player_).__name__ == 'Transport':
                if player_ is not None:
                    # player has collide with asteroid, player1 or player 2 get the points
                    player_.update_score(self.points)
            else:
                # Transport does not get points
                ...
            # Split asteroid
            self.make_debris()
            self.quit()
        ...

    def quit(self) -> None:
        Broadcast.remove_object_id(self.id_)
        obj = Broadcast(self.delete_object())
        obj.queue()
        self.kill()

    def update(self) -> None:
        """
        Update asteroid sprites.

        :return: None
        """

        if self.gl.FRAME > self.appearance_frame:

            # start to move asteroid when frame number is over
            # self.appearance_frame (random frame number)
            self.rect.move_ip(self.speed)

            # asteroid is moving but not visible yet?
            # The rectangle bottom edge must be > 0 to start the code below
            if self.rect.midbottom[1] > 0:

                # Inside the 60 FPS Area
                if self.dt > self.timing:

                    # self.image = self.images_copy.copy()
                    if self.has_been_hit:
                        if not globals().__contains__('LAVA'):
                            raise NameError("Texture LAVA not available")
                        self.image.blit(LAVA[self.index % len(LAVA) - 1],
                                        (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                        self.index += 1
                        self.has_been_hit = False

                    # if self.rotation != 0:
                    #    self.mask = pygame.mask.from_surface(self.image)

                    self.asteroid_object.update({'frame': self.gl.FRAME,
                                                 'rect': self.rect,
                                                 'life': self.life})
                    self.asteroid_object.queue()

                    self.dt = 0

                else:
                    self.dt += self.gl.TIME_PASSED_SECONDS

            if self.rect.midtop[1] > self.gl.SCREENRECT.h:
                self.quit()

            # Outside the 60 FPS Area
            # The code below will be processed every frames.


