# encoding: utf-8
import os
import socket
import sys

import _pickle as cpickle
import threading
import time
import copyreg
import threading

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
    from LifeBar import HorizontalBar, ShowLifeBar
    from Sounds import BLUE_LASER_SOUND, RED_LASER_SOUND, \
        EXPLOSION_SOUND, IMPACT, IMPACT1, IMPACT_SHORT
    from Asteroids import Debris
    from Gems import MakeGems
    from SoundServer import SoundControl
    from random import uniform
    from TextureTools import *
    from NetworkBroadcast import Broadcast, StaticSprite, SoundAttr, EventAttr, BlendSprite
    from Explosions import Explosion
    from MessageSender import SpriteClient
    from GLOBAL import GL
    from LayerModifiedClass import LayeredUpdatesModified
    from AfterBurners import AfterBurner
    from CreateHalo import PlayerHalo, AsteroidHalo
    from Player1 import LaserImpact
    from End import PlayerLost
    from pygame import freetype
    from PlayerScore import DisplayScore
    from CosmicDust import COSMIC_DUST_ARRAY, create_dust, display_dust
    from Textures import *
    from Dialogs import DialogBox

except ImportError:
    print("\nOne or more game libraries is missing on your system."
          "\nDownload the source code from:\n"
          "https://github.com/yoyoberenguer/MultiplayerGameEngine.git")
    raise SystemExit

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


def unserialize_event(isset):
    e = threading.Event()
    if isset:
        e.set()
    return e


def serialize_event(e):
    return unserialize_event, (e.isSet(),)


copyreg.pickle(threading.Event, serialize_event)


class Shot(pygame.sprite.Sprite):
    images = None
    containers = None
    last_shot = 0
    shooting = False
    mask = None

    def __init__(self, parent_, pos_, gl_, timing_, layer_, surface_name_=''):
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
        self.blend = pygame.BLEND_RGB_ADD

        self.mask = Shot.mask
        self.index = 0
        self.parent = parent_
        self.surface_name = surface_name_
        self.id_ = id(self)
        self.shot_sound_object = Broadcast(self.make_sound_object('RED_LASER_SOUND'))
            
        if Shot.shooting and self.is_reloading():
            self.kill()
        else:
            
            self.gl.MIXER.stop_object(id(RED_LASER_SOUND))
            self.gl.MIXER.play(sound_=RED_LASER_SOUND, loop_=False, priority_=0, volume_=1.0,
                               fade_out_ms=0, panning_=True, name_='RED_LASER_SOUND', x_=self.rect.centerx,
                               object_id_=id(RED_LASER_SOUND), screenrect_=self.gl.SCREENRECT)
            self.shot_sound_object.play()
            
            Shot.last_shot = FRAME
            Shot.shooting = True
            
            self.shot_object = Broadcast(self.make_object())
            self.shot_object.queue()

    def make_sound_object(self, sound_name_: str) -> SoundAttr:
        return SoundAttr(frame_=self.gl.FRAME, id_=self.id_, sound_name_=sound_name_, rect_=self.rect)

    def make_object(self) -> StaticSprite:
        shot_obj = StaticSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                                layer_=self.layer, blend_=self.blend, rect_=self.rect)
        return shot_obj

    @staticmethod
    def is_reloading() -> bool:
        if FRAME - Shot.last_shot < 10:
            return True
        else:
            Shot.shooting = False
            return False

    def collide(self, rect_, object_, damage_=100) -> None:
        LaserImpact.containers = self.gl.All
        LaserImpact.images = IMPACT_LASER
        LaserImpact(gl_=self.gl, pos_=rect_.topleft, parent_=object_,
                    timing_=self.timing, blend_=pygame.BLEND_RGBA_ADD, layer_=0)

        Flare.containers = self.gl.All
        Flare.images = FLARE
        Flare(gl_=self.gl, pos_=self.rect.center, timing_=8, layer_=0)

        Light.containers = self.gl.All
        Light.images = LIGHT
        Light(gl_=self.gl, pos_=self.rect.center, timing_=8, layer_=0)

        DisplayAmountDamage.containers = self.gl.All
        DisplayAmountDamage(self.gl, str(damage_), pos_=self.rect.center, timing_=8, layer_=0)
        self.quit()

    def quit(self) -> None:
        self.kill()

    def update(self) -> None:
        if self.dt > self.timing:

            if self.gl.SCREENRECT.colliderect(self.rect):

                # Move the laser
                if self.images != IMPACT_LASER:
                    self.position += self.speed
                    self.rect.center = (self.position.x, self.position.y)

                self.dt = 0
            else:
                self.kill()
                return
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        if self.alive():
            if self.rect.colliderect(self.gl.SCREENRECT):
                self.shot_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
        self.shot_object.queue()


class DisplayAmountDamage(pygame.sprite.Sprite):
    containers = GL.All

    def __init__(self, gl_, text_, pos_, timing_, layer_=0):

        self.layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)

        self.image, self.rect = ARCADE_FONT.render(text_,
                                                   fgcolor=pygame.Color(255, 255, 0), bgcolor=None)
        self.image_copy = self.image.copy()
        self.rect.center = pos_
        self.timing = timing_
        self.gl = gl_
        self.dt = 0
        self.blend = 0  # pygame.BLEND_RGBA_ADD
        self.id_ = id(self)
        self.start = self.gl.FRAME
        # self.dx = 0
        # self.pos = pos_
        # self.w, self.h = self.image.get_size()

    def update(self) -> None:

        if self.dt > self.timing:
            if self.gl.FRAME - self.start > 30:
                self.kill()
            else:
                # self.image = pygame.transform.smoothscale(
                #    self.image_copy, (int(self.w + self.dx), int(self.h + self.dx)))
                # self.rect = self.image.get_rect(center=self.pos)
                # self.dx += 0.5
                ...

        self.dt += self.gl.TIME_PASSED_SECONDS


class Light(pygame.sprite.Sprite):
    images = LIGHT
    containers = None

    def __init__(self, gl_, pos_, timing_, layer_=0):

        self.layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)
        self.images = Light.images
        self.image = Light.images[0]
        self.rect = self.image.get_rect(center=pos_)
        self.pos = pos_
        self.timing = timing_
        self.dim = len(self.images) - 2
        self.gl = gl_
        self.index = 0

        self.dt = 0
        self.blend = pygame.BLEND_RGBA_ADD
        self.id_ = id(self)

    def update(self) -> None:

        if self.dt > self.timing:
            self.image = self.images[self.index]
            self.rect = self.image.get_rect(center=self.pos)
            if self.index > self.dim:
                self.kill()
            self.index += 1

            ...

        self.dt += self.gl.TIME_PASSED_SECONDS


class Flare(pygame.sprite.Sprite):
    images = FLARE
    containers = None

    def __init__(self, gl_, pos_, timing_, layer_=0):

        self.layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)
        self.images = Flare.images
        self.image = Flare.images[0]
        self.rect = self.image.get_rect(center=pos_)
        self.timing = timing_
        self.dim = len(self.images) - 2

        self.gl = gl_
        self.index = 0

        self.dt = 0
        self.blend = pygame.BLEND_RGBA_ADD
        self.id_ = id(self)

    def update(self) -> None:

        if self.dt > self.timing:
            self.image = self.images[self.index]

            if self.index > self.dim:
                self.kill()
            self.index += 1

            ...

        self.dt += self.gl.TIME_PASSED_SECONDS


class Player2(pygame.sprite.Sprite):
    containers = None
    image = None
    mask = None

    def __init__(self, gl_, timing_, pos_, layer_=0):

        self.layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, self.layer)

        self.image = Player2.image
        # self.image_ = memoryview(self.image)
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect(center=pos_)
        self.timing = timing_
        self.surface_name = 'P2_SURFACE'
        self.gl = gl_
        self.dt = 0
        self.speed = 600
        self.blend = 0
        self.previous_pos = pygame.math.Vector2()  # previous position
        self.life = 200
        self.max_life = 200
        self.eng_right = self.right_engine()
        self.eng_left = self.left_engine()
        # todo test if convert_alpha otherwise this is useless
        self.mask = pygame.mask.from_surface(self.image)  # Image have to be convert_alpha compatible
        self.damage = 800
        self.id_ = id(self)
        self.player_object = Broadcast(self.make_object())
        self.impact_sound_object = Broadcast(self.make_sound_object('IMPACT'))
        self.impact_sound_object_short = Broadcast(self.make_sound_object('IMPACT_SHORT'))

        self.update_score = self.gl.P2_SCORE.score_update

    def make_sound_object(self, sound_name_: str) -> SoundAttr:
        return SoundAttr(frame_=self.gl.FRAME, id_=self.id_, sound_name_=sound_name_, rect_=self.rect)
    
    def make_object(self) -> StaticSprite:
        # Only attributes self.gl.FRAME, self.rect are changing over the time.
        return StaticSprite(
                frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                layer_=self.layer, blend_=self.blend, rect_=self.rect, life=self.life,
                damage=self.damage)

    def player_lost(self) -> None:
        self.gl.All.add(LOST)

    def explode(self) -> None:

        if self.alive():
            Explosion.images = PLAYER_EXPLOSION2
            Explosion.containers = self.gl.All
            Explosion(self, self.rect.center, self.gl,
                      8, self.layer, texture_name_='PLAYER_EXPLOSION2')
            PlayerHalo.images = HALO_SPRITE13
            PlayerHalo.containers = self.gl.All
            PlayerHalo(texture_name_='HALO_SPRITE13', object_=self, timing_=8)
            # self.player_lost() -> this is done in the main loop
            self.kill()

    def collide(self, damage_) -> None:

        if self.alive():
            self.life -= damage_

            if damage_ > 10:
                # player loud impact sound locally
                self.gl.MIXER.play(sound_=IMPACT, loop_=False, priority_=0,
                                   volume_=1.0, fade_out_ms=0, panning_=True,
                                   name_='IMPACT', x_=self.rect.centerx,
                                   object_id_=id(IMPACT),
                                   screenrect_=self.gl.SCREENRECT)
                # Broadcast loud impact sound
                self.impact_sound_object.play()

            else:
                # player short impact sound locally (for small object collision)
                self.gl.MIXER.play(sound_=IMPACT_SHORT, loop_=False, priority_=0,
                                   volume_=1.0, fade_out_ms=0, panning_=True,
                                   name_='IMPACT', x_=self.rect.centerx,
                                   object_id_=id(IMPACT),
                                   screenrect_=self.gl.SCREENRECT)
                # Broadcast short impact sound to client
                self.impact_sound_object_short.play()

    # def hit(self, damage_):
    #    if self.alive():
    #        self.life -= damage_

    def left_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl,
                           (-5, 38), 8, pygame.BLEND_RGB_ADD, self.layer - 1, texture_name_='EXHAUST')

    def right_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl, (5, 38),
                           8, pygame.BLEND_RGB_ADD, self.layer - 1, texture_name_='EXHAUST')

    def get_centre(self) -> tuple:
        return self.rect.center

    def disruption(self) -> None:
        index = (FRAME >> 1) % len(DISRUPTION) - 1
        self.image.blit(DISRUPTION[index], (-20, -20), special_flags=pygame.BLEND_RGB_ADD)

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

    def contain_sprite(self, move_: tuple) -> bool:
        """
        Check if the player can move toward the screen edges
        Return True if the movement is allowed else False
        :param move_: Tuple; player movement
        :return: True if the movement is allowed else return False
        """
        rect_copy = self.rect.copy()
        rect_copy.x += move_[0]
        rect_copy.y += move_[1]
        if self.gl.SCREENRECT.contains(rect_copy):
            return True
        else:
            return False

    def update(self) -> None:

        self.rect.clamp_ip(SCREENRECT)

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            if self.life < 1:
                self.explode()

            displacement = self.speed * self.gl.SPEED_FACTOR
            if self.gl.KEYS[pygame.K_UP]:
                if self.contain_sprite((0, -displacement)):
                    self.rect.move_ip(0, -displacement)

            if self.gl.KEYS[pygame.K_DOWN]:
                if self.contain_sprite((0, displacement)):
                    self.rect.move_ip(0, displacement)

            if self.gl.KEYS[pygame.K_LEFT]:
                if self.contain_sprite((-displacement, 0)):
                    self.rect.move_ip(-displacement, 0)

            if self.gl.KEYS[pygame.K_RIGHT]:
                if self.contain_sprite((displacement, 0)):
                    self.rect.move_ip(displacement, 0)

            if self.gl.KEYS[pygame.K_SPACE]:
                if not Shot.is_reloading():
                    self.shooting_effect()
                    Shot(self, self.rect.center, self.gl, 0,
                         self.layer - 1, surface_name_='RED_LASER')

            if joystick is not None:
                self.rect.move_ip(JL3.x * self.gl.SPEED_FACTOR * self.speed,
                                  JL3.y * self.gl.SPEED_FACTOR * self.speed)

            if self.previous_pos == self.rect.center:
                self.rect.centerx += random.randint(-1, 1)
                self.rect.centery += random.randint(-1, 1)

            if self.gl.FRAME < 100:
                self.rect.centery -= 6

            self.previous_pos = self.rect.center

            self.dt = 0

        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        # !UPDATE the <follower> sprites with the new player position.
        self.eng_left.update()
        self.eng_right.update()

        # Broadcast the spaceship position every frames
        self.player_object.update({'frame': self.gl.FRAME,
                                   'rect': self.rect,
                                   'life': self.life})
        self.player_object.queue()

        self.disruption()


class MirroredAsteroidClass(pygame.sprite.Sprite):

    containers = None

    def __init__(self, sprite_):

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.rect = sprite_.rect
        self.image = sprite_.image
        self.mask = pygame.mask.from_surface(self.image)
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        self.id_ = sprite_.id_
        self.frame = sprite_.frame
        self.surface = sprite_.surface
        self.gl = GL
        assert hasattr(sprite_, 'life'), \
            "MirroredAsteroidClass broadcast object is missing <life> attribute."
        assert hasattr(sprite_, 'damage'), \
            "MirroredAsteroidClass broadcast object is missing <damage> attribute."
        assert hasattr(sprite_, 'points'), \
            "MirroredAsteroidClass broadcast object is missing <points> attribute."
        self.life = sprite_.life
        self.damage = sprite_.damage
        self.points = sprite_.points
        self.lava_length = len(LAVA) - 1
        self.index = 0
        self.fxdt = 15
        self.dt = 0
        self.timing = 0  # let the server decide the FPS

        self.vertex_array = []

    def show_attributes(self):
        if hasattr(self, '__dict__'):
            print('\n\n')
            for attr, value in self.__dict__.items():
                print('Sprite id %s has attribute : %s %s' % (id(self), attr, value))
        else:
            raise AttributeError('Sprite id %s does not have attribute __dict__.' % id(self))

    def add_particle(self) -> None:
        angle = math.radians(uniform(0, 359))
        self.asteroid_particles_fx(position_=pygame.math.Vector2(self.rect.center),
                                   vector_=pygame.math.Vector2(
                                       math.cos(angle) * randint(5, 10), math.sin(angle) * randint(5, 10)),
                                   images_=FIRE_PARTICLES.copy(),
                                   layer_=self.layer, blend_=pygame.BLEND_RGB_ADD)

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
                              layer_=-1,   # Layer used to display the particles (int)
                              blend_=pygame.BLEND_RGB_ADD  # Blend mode (int)
                              ) -> None:
        # Create asteroid tail particles debris

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

    def blend_(self) -> None:
        if not globals().__contains__('LAVA'):
            raise NameError('Texture LAVA is missing!'
                            '\nCheck file Texture.py for LAVA assigment. ')
        if isinstance(self.image, pygame.Surface):
            self.image.blit(LAVA[self.index % self.lava_length],
                            (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        else:
            print(self.image)
            raise AttributeError('self.image is not a pygame.Surface, got %s ' % type(self.image))

        self.index += 1

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
                number_ = randint(3, 15)
                for _ in range(number_):
                    if _ < number_:
                        MakeGems.inventory = set()
                    MakeGems(gl_=self.gl,
                             player_=player_,
                             object_=self,
                             ratio_=1.0,
                             timing_=8,
                             offset_=pygame.Rect(
                                 self.rect.centerx, self.rect.centery, randint(-100, 100), randint(-100, 20)))

    def explode(self) -> None:
        # Add fire particles effect
        self.add_particle()
        self.kill()

    def hit(self, player_=None, damage_: int = 0) -> None:
        """
        Asteroid hit by a laser
        """

        if hasattr(self, 'life'):
            self.life -= damage_
        else:
            # object already killed
            """
            print(self.id_ if hasattr(self, 'id_') else 'no self.id_')
            if hasattr(self, 'show_attributes'):
                self.show_attributes()
            raise AttributeError('self is missing attribute life, type %s alive %s group %s id %s'
                                 % (type(self), self.alive(), self.groups(), id(self)))
            """
            return

        if self.life < 1:
            # make sure the asteroid belongs to a group
            # otherwise the asteroid has been delete prior accessing
            # the method (e.g parallel delete from a different thread)
            if self.alive():    
                if player_ is not None:
                    player_.update_score(self.points)

                    # Create gems only for two asteroid types
                    if self.surface in ('DEIMOS', 'EPIMET'):
                        self.create_gems(player_)
            # self.make_debris()   # this is done by the server
            self.explode()
        else:
            if self.surface != 'MAJOR_ASTEROID':
                self.blend_()
        ...

    def collide(self, player_=None, damage_: int = 0) -> None:

        if not globals().__contains__('IMPACT1'):
            raise NameError("Sound IMPACT1 is missing!"
                            "\nCheck file Sounds.py for IMPACT1 assigment. ")

        if hasattr(self, 'life'):
            self.life -= damage_
        else:
            # object already killed
            """
            print(self.id_ if hasattr(self, 'id_') else 'no self.id_')
            if hasattr(self, 'show_attributes'):
                self.show_attributes()
            raise AttributeError('self is missing attribute life, type %s alive %s group %s'
                                 % (type(self), self.alive(), self.groups()))
            """
            return
        # Play the sound locally only, 
        self.gl.MIXER.play(sound_=IMPACT1, loop_=False, priority_=0,
                           volume_=1.0, fade_out_ms=0, panning_=True,
                           name_='IMPACT1', x_=self.rect.centerx,
                           object_id_=id(IMPACT1),
                           screenrect_=self.gl.SCREENRECT)
        
        if self.life < 1:
            if player_ is not None:
                player_.update_score(self.points)
            # self.make_debris()   # this is done on the server
            for _ in range(3):
                self.add_particle()
            self.kill()
        ...

    def update(self) -> None:
        if self.dt > self.timing:
            if hasattr(self, 'life'):
                if self.life < 1:
                    self.kill()
            self.dt = 0
            
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS


class MirroredPlayer1Class(pygame.sprite.Sprite):

    containers = None

    def __init__(self, sprite_):
        
        # No sprite group assignment in the constructor
        pygame.sprite.Sprite.__init__(self, self.containers)

        # GL.NetGroupAll.change_layer(self, sprite_.layer)

        self.rect = sprite_.rect
        self.image = sprite_.image
        self.mask = pygame.mask.from_surface(self.image)
        self.image_copy = sprite_.image.copy()
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        self.id_ = sprite_.id_
        self.frame = sprite_.frame
        self.surface = sprite_.surface
        self.damage = sprite_.damage
        self.gl = GL
        self.dt = 0
        self.timing = 15  # 60 fps

    def show_attributes(self) -> None:
        if hasattr(self, '__dict__'):
            print('\n\n')
            for attr, value in self.__dict__.items():
                print('Sprite id %s has attribute : %s %s' % (id(self), attr, value))
        else:
            raise AttributeError('Sprite id %s does not have attribute __dict__.' % id(self))

    def disruption(self) -> None:

        if FRAME is None:
            raise ValueError("FRAME cannot be None!")

        if DISRUPTION is None:
            raise ValueError("Texture DISRUPTION is missing!")

        index = (FRAME >> 1) % len(DISRUPTION) - 1
        self.image.blit(DISRUPTION[index], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def update(self) -> None:

        if self.dt > self.timing:
            
            self.image = self.image_copy.copy()
            self.disruption()
            ...
            self.dt = 0
            
        else:
            self.dt += self.gl.TIME_PASSED_SECONDS


class MirroredTransportClass(pygame.sprite.Sprite):

    containers = None

    def __init__(self, sprite_):
        # No sprite group assignment in the constructor
        pygame.sprite.Sprite.__init__(self, self.containers)

        # GL.NetGroupAll.change_layer(self, sprite_.layer)

        self.rect = sprite_.rect
        self.image = sprite_.image
        self.mask = pygame.mask.from_surface(self.image)
        self.image_copy = self.image.copy()
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        assert hasattr(sprite_, 'impact'), \
            "MirroredTransportClass broadcast object is missing <impact> attribute."
        self.impact = sprite_.impact
        self.id_ = sprite_.id_
        self.frame = sprite_.frame
        self.surface = sprite_.surface
        self.gl = GL
        self.index = 0
        self.dt = 0
        self.fxdt = 0
        self.max_life = 5000
        self.half_life = self.max_life >> 1
        assert hasattr(sprite_, 'life'), \
            "MirroredTransportClass broadcast object is missing <life> attribute."
        assert hasattr(sprite_, 'damage'), \
            "MirroredTransportClass broadcast object is missing <damage> attribute."
        self.life = sprite_.life
        self.damage = sprite_.damage
        self.vertex_array = []
        half = self.gl.SCREENRECT.w >> 1
        self.safe_zone = pygame.Rect(half - 200, half, 400, self.gl.SCREENRECT.bottom - half)
        self.timing = 15  # 60 FPS

    def show_attributes(self) -> None:
        if hasattr(self, '__dict__'):
            print('\n\n')
            for attr, value in self.__dict__.items():
                print('Sprite id %s has attribute : %s %s' % (id(self), attr, value))
        else:
            raise AttributeError('Sprite id %s does not have attribute __dict__.' % id(self))

    def display_fire_particle_fx(self) -> None:
        # Display fire particles when the player has taken bad hits
        # Use the additive blend mode.
        if self.fxdt > self.timing - 8:     # 8 ms
            for p_ in self.vertex_array:

                # queue the particle in the vector direction
                p_.rect.move_ip(p_.vector)
                p_.image = p_.images[p_.index]
                if p_.index > len(p_.images) - 2:
                    p_.kill()
                    self.vertex_array.remove(p_)

                p_.index += 1
            self.fxdt = 0
            
        else:
            self.fxdt += self.gl.TIME_PASSED_SECONDS

    def fire_particles_fx(self,
                          position_,  # particle starting location (tuple or pygame.math.Vector2)
                          vector_,    # particle speed, pygame.math.Vector2
                          images_,    # surface used for the particle, (list of pygame.Surface)
                          layer_=0,   # Layer used to display the particles (int)
                          blend_=pygame.BLEND_RGB_ADD  # Blend mode (int)
                          ) -> None:
        # Create fire particles around the aircraft hull when player is taking serious damages

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
        sprite_.vector = vector_  # vector
        sprite_.index = 0
        # assign update method to self.display_fire_particle_fx
        # (local method to display the particles)
        sprite_.update = self.display_fire_particle_fx
        self.vertex_array.append(sprite_)

    def update(self) -> None:

        # Line below can be skipped
        # self.rect.clamp_ip(self.safe_zone)

        self.image = self.image_copy.copy()

        # in the 16ms area (60 FPS)
        if self.dt > self.timing:

            if self.life < self.half_life:
                position = pygame.math.Vector2(randint(-50, 50), randint(-100, 100))
                self.fire_particles_fx(position_=position + pygame.math.Vector2(self.rect.center),
                                       vector_=pygame.math.Vector2(uniform(-1, 1), uniform(+1, +3)),
                                       images_=FIRE_PARTICLES,
                                       layer_=0, blend_=pygame.BLEND_RGB_ADD)
            elif self.life < 1:
                self.kill()

            self.dt = 0

        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        # outside the 60 FPS area.
        # Below code processed every frames.
        if self.impact:
            self.image.blit(DISRUPTION_ORG[self.index % len(DISRUPTION_ORG) - 1],
                            (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            self.index += 1
            if self.index > len(DISRUPTION_ORG) - 2:
                self.impact = False
                self.index = 0


class SpriteServer(threading.Thread):

    def __init__(self,
                 gl_,  # Global variables
                 host_,  # host address
                 port_,  # port value
                 ):

        threading.Thread.__init__(self)

        try:

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as error:
            print('\n[-]SpriteServer - ERROR 0, socket: %s ' % error)
            gl_.P2CS_STOP = True

        try:

            self.sock.bind((host_, port_))
            self.sock.listen(1)

        except socket.error as error:
            print('\n[-]SpriteServer - ERROR 1, socket: %s ' % error)
            gl_.P2CS_STOP = True

        self.host = host_
        self.port = port_
        self.buf = gl_.BUFFER
        self.totalbytes = 0
        self.gl = gl_
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
            print("\n[-]SpriteServer - Lost connection with Server...")
            print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
            self.gl.P2CS_STOP = True

        while not (self.gl.P2CS_STOP or self.gl.SPRITE_SERVER_STOP):
            # try:

            while not (self.gl.P2CS_STOP or self.gl.SPRITE_SERVER_STOP):

                # Receive data from the socket, writing it into buffer instead
                # of creating a new string. The return value is a pair (nbytes, address)
                # where nbytes is the number of bytes received and address is the address
                # of the socket sending the data.

                try:
                    nbytes, sender = connection.recvfrom_into(self.view, self.buf)
                except socket.error as error:
                    print("\n[-]SpriteServer - Lost connection with Server...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    self.gl.SPRITE_SERVER_STOP = True
                    nbytes = 0

                buffer = self.view.tobytes()[:nbytes]

                try:

                    connection.sendall(buffer)

                except ConnectionResetError as error:
                    print("\n[-]SpriteServer - Lost connection with Server...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    self.gl.SPRITE_SERVER_STOP = True

                try:

                    # Decompress the data frame
                    decompress_data = lz4.frame.decompress(buffer)
                    data = cpickle.loads(decompress_data)

                except Exception as e:
                    # Player 1 (is gone) server is dead!.
                    # The decompression error can also happen when
                    # the bytes stream sent is larger than the buffer size.
                    # raise RuntimeError('Problem during decompression/un-pickling')
                    print(e)
                    print('Problem during decompression/un-pickling, '
                          'packet size %s, buffer size %s at frame %s'
                          % (nbytes, len(buffer) if buffer is not None else None, self.gl.FRAME))
                    # self.gl.SPRITE_SERVER_STOP
                    data = None
                    self.gl.SPRITE_SERVER_STOP = True
                    self.gl.SPRITE_CLIENT_STOP = True
                    self.gl.STOP_GAME = True

                # if data is not None:
                #    print('\n[-]packet size %s %s' % (len(data), len(data) * 56))

                delete_group = set()
                insert_group = set()
                sprite_group = {}
                alpha = {}

                if isinstance(data, list):

                    # Goes through the list of elements/sprites
                    for sprite_ in data:

                        if isinstance(sprite_, set):
                            self.gl.GROUP_ALIVE = sprite_
                            continue

                        """
                        # LOGGING 
                        if not f.closed:
                            f.write('\n' + str(sprite_.frame) +
                                    ' sizeof ' + str(sys.getsizeof(sprite_)) +
                                    ' data_length ' + str(len(data)) +
                                    ' id: ' + str(sprite_.id_) +
                                    ' name ' + str(sprite_.surface) if hasattr(sprite_, 'surface') else '' +
                                    ' life ' + str(sprite_.life) if hasattr(sprite_, 'life') else '')
                        """

                        # extract the frame number (server frame number)
                        # As we are iterating over all sprites
                        # self.gl.REMOTE_FRAME value will be equal to the
                        # sprite__.frame value of the last iterated element.
                        self.gl.REMOTE_FRAME = sprite_.frame

                        # EVENT
                        # event does not have all attributes 
                        if hasattr(sprite_, 'event'):

                            # Process broadcast event
                            # Trigger next frame
                            if sprite_.event.isSet():
                                self.gl.NEXT_FRAME.set()
                            else:
                                self.gl.NEXT_FRAME.clear()

                            # Avoiding below code
                            continue

                        # SOUND
                        elif hasattr(sprite_, 'sound_name'):
                            try:

                                sound = eval(sprite_.sound_name)

                            except NameError:
                                raise NameError("\n[-]SpriteServer - Sound effect "
                                                "'%s' does not exist " % sprite_.sound_name)

                            # play the sound locally
                            self.gl.MIXER.play(sound_=sound, loop_=False, priority_=0,
                                               volume_=1.0, fade_out_ms=0, panning_=True,
                                               name_=sprite_.sound_name, x_=sprite_.rect.centerx,
                                               object_id_=id(sound),
                                               screenrect_=self.gl.SCREENRECT)

                            # Avoiding below code
                            continue

                        # DELETE
                        # gather all delete sprite ids to process at the end of the iteration
                        elif hasattr(sprite_, 'to_delete'):
                            # to_delete{'1235456': DEIMOS, '54545465': DEIMOS .....}
                            for obj_id, surface_ in sprite_.to_delete.items():
                                delete_group.add(obj_id)
                                alpha[obj_id] = surface_

                        # SPRITES
                        else:

                            try:

                                sprite_.image = eval(sprite_.surface)  # load surface

                            except NameError:
                                # A texture is not present on the client side,
                                # it is worth checking into the Asset directory to make
                                # sure the image is present and the texture loaded into memory
                                raise NameError("\n[-]SpriteServer - Surface "
                                                "'%s' does not exist " % sprite_.surface)

                            # Check if the sprite is an image or an animation
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
                                        cache_image_, cache_rotation_ = self.gl.XTRANS_ROTATION[sprite_.id_]

                                        if cache_rotation_ == sprite_.rotation:
                                            sprite_.image = self.gl.XTRANS_ROTATION[sprite_.id_]

                                        else:
                                            sprite_.image = pygame.transform.rotate(
                                                sprite_.image, sprite_.rotation)
                                            self.gl.XTRANS_ROTATION.update(
                                                {sprite_.id_: (sprite_.image, sprite_.rotation)})

                                    else:
                                        sprite_.image = pygame.transform.rotate(
                                            sprite_.image, sprite_.rotation)
                                        self.gl.XTRANS_ROTATION.update(
                                            {sprite_.id_: (sprite_.image, sprite_.rotation)})

                            if hasattr(sprite_, 'scale'):
                                if sprite_.scale != 1:
                                    if sprite_.id_ in self.gl.XTRANS_SCALE.keys():

                                        sprite_.image = self.gl.XTRANS_SCALE[sprite_.id_]

                                    else:
                                        sprite_.image = pygame.transform.scale(sprite_.image, (
                                            int(sprite_.image.get_size()[0] * sprite_.scale),
                                            int(sprite_.image.get_size()[1] * sprite_.scale)))

                                        self.gl.XTRANS_SCALE.update({sprite_.id_: sprite_.image})

                            # Add the sprite into self.gl.ASTEROID with the class MirroredAsteroidClass.
                            # GL.ASTEROID group is used for collision detection purpose only.
                            # MirroredAsteroidClass class has also some methods that can be triggered from client side
                            # such as queue and debris methods for localised special effects.
                            # The asteroid life points variable is broadcast from the server every
                            # frames, and should be considered as read only variable on the client side.

                            # ASTEROID (catch only asteroid sprite with names below)
                            if sprite_.surface.split('[')[0] in (
                                    'DEIMOS', 'EPIMET', 'MULT_ASTEROID_32',
                                    'MULT_ASTEROID_64', 'MAJOR_ASTEROID'):

                                sprite_found = None
                                for spr_ in self.gl.ASTEROID:
                                    if sprite_.id_ == spr_.id_:
                                        sprite_found = spr_
                                        break
                                # Sprite not found in self.gl.ASTEROID
                                if sprite_found is None:
                                    # todo create a __new___ method for class MirroredAsteroidClass and a python
                                    MirroredAsteroidClass.containers = self.gl.ASTEROID
                                    sprite_group[sprite_.id_] = MirroredAsteroidClass(sprite_)
                                    insert_group.add(sprite_.id_)

                                # Asteroid sprite already exist in GL.ASTEROID group
                                # UPDATING ALL ATTRIBUTES
                                # todo check if necessary to update all attrs
                                else:
                                    sprite_found.frame = sprite_.frame
                                    sprite_found.rect = sprite_.rect
                                    sprite_found.surface = sprite_.surface
                                    sprite_found.image = sprite_.image
                                    sprite_found.blend = sprite_.blend
                                    sprite_found.layer = sprite_.layer
                                    sprite_found.life = sprite_.life
                                    sprite_found.damage = sprite_.damage

                            # PLAYER1
                            elif sprite_.surface == 'P1_SURFACE':

                                    MirroredPlayer1Class.containers = self.gl.P1
                                    sprite_group[sprite_.id_] = MirroredPlayer1Class(sprite_)
                                    insert_group.add(sprite_.id_)
                                    # The GroupSingle container only holds a single Sprite.
                                    # When a new Sprite is added, the old one is removed.
                                    # -> update the group with latest sprite changes. GL.P1 is used for
                                    # collision detection


                            # TRANSPORT
                            # find the MirroredTransportClass message and create a local instance (if still alive)
                            elif sprite_.surface == 'TRANSPORT':

                                    MirroredTransportClass.containers = self.gl.TRANSPORT
                                    sprite_group[sprite_.id_] = MirroredTransportClass(sprite_)
                                    insert_group.add(sprite_.id_)
                                    # The GroupSingle container only holds a single Sprite.
                                    # When a new Sprite is added, the old one is removed.
                                    # -> update the group with latest sprite changes.
                                    # GL.TRANSPORT is used for collision detection

                            else:

                                # GENERIC
                                # Generic sprite (without methods).
                                generic = pygame.sprite.Sprite()
                                generic.frame = sprite_.frame
                                generic.rect = sprite_.rect
                                generic.surface = sprite_.surface
                                generic.image = sprite_.image
                                generic.blend = sprite_.blend
                                generic.layer = sprite_.layer
                                generic.id_ = sprite_.id_

                                sprite_group[sprite_.id_] = generic
                                insert_group.add(generic.id_)

                    to_insert = insert_group - delete_group
                    self.insert_sprite(to_insert, sprite_group)
                    # !!! DELETING SPRITE IN PARALLEL MIGHT CAUSE ISSUE
                    # WHEN USING SPRITE ATTRIBUTES IN THE MAIN LOOP...
                    self.delete_sprite(delete_group)

                    # END OF for sprite_ in data:

                    """
                    # LOGGING
                    if not f.closed:
                        f.write('\n' + str(self.gl.FRAME) +
                                '\ninsert_group ' + str(to_insert) +
                                '\nsprite_group ' + str(sprite_group) +
                                '\ndelete_group ' + str(delete_group) +
                                '\nalpha        ' + str(alpha) +
                                '\nNetGroupAll ' + str(list((spr.life if hasattr(spr, 'life')
                                                             else '') for spr in self.gl.NetGroupAll.sprites())))
                    """

                buffer = b''
                break
            # self.view = memoryview(bytearray(self.buf))
            # pygame.time.wait(1)

        print('\n[-]SpriteServer is now terminated...')

    def insert_sprite(self, insert_group_, sprite_group_) -> None:
        # INSERT
        for id__ in insert_group_:
            for id_, sprite_ in sprite_group_.items():
                if id__ == id_:
                    has_ = False
                    for spr_ in self.gl.NetGroupAll:
                        # sprite exists, updating rect and attributes
                        if spr_.id_ == sprite_.id_:
                            has_ = True
                            spr_.rect = sprite_.rect
                            spr_.image = sprite_.image
                            spr_.frame = sprite_.frame
                            if hasattr(sprite_, 'life'):
                                spr_.life = sprite_.life
                            if hasattr(sprite_, 'impact'):
                                spr_.impact = sprite_.impact
                            if hasattr(sprite_, 'surface'):
                                spr_.surface = sprite_.surface
                            if hasattr(sprite_, 'blend'):
                                spr_.blend = sprite_.blend
                            if hasattr(sprite_, 'layer'):
                                spr_.layer = sprite_.layer
                            if hasattr(sprite_, 'id_'):
                                spr_.id_ = sprite_.id_

                            break
                        # sprite does not exist, insert sprite
                    if not has_:
                        self.gl.NetGroupAll.add(sprite_)
                        # !! Assign the sprite to the correct layer
                        # LayeredUpdates.change_layer(sprite, new_layer): return None
                        self.gl.NetGroupAll.change_layer(sprite_, sprite_.layer)

    def delete_sprite(self, delete_group_) -> None:
        # DELETE
        # NOT RECOMMENDED TO DELETE SPRITE IN PARALLEL OF GAME LOOP
        # IMPLEMENT BELOW CODE FROM MAIN LOOP
        for obj_id in delete_group_:

            for spr__ in self.gl.NetGroupAll:

                if obj_id == spr__.id_:

                    spr__.kill()
                    spr__.remove(self.gl.All, self.gl.NetGroupAll, self.gl.ASTEROID)

                    if spr__.surface == 'TRANSPORT':
                        self.gl.TRANSPORT.empty()

                    if spr__.surface == 'P1_SURFACE':
                        self.gl.P1.empty()

                    if obj_id in GL.XTRANS_SCALE.keys():
                        self.gl.XTRANS_SCALE.pop(spr__.id_)

                    if obj_id in GL.XTRANS_ROTATION.keys():
                        self.gl.XTRANS_ROTATION.pop(spr__.id_)

                    break


# function used for terminating SERVER/ CLIENT threads listening (blocking socket)
def force_quit(host_: str, port_: int) -> None:
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

    transport_ = None
    player1 = None

    if GL.TRANSPORT is not None and \
            isinstance(GL.TRANSPORT, pygame.sprite.GroupSingle):
        if len(GL.TRANSPORT) > 0:
            transport_ = GL.TRANSPORT.sprites()[0]

        # Use collision mask for collision detection
        # It is compulsory to have sprite textures with alpha transparency information
        # in order to check for collision otherwise the collision will be ignored.
        # Check collisions between transport and asteroids

        if transport_ is not None:

            if transport_.alive():

                collision = pygame.sprite.spritecollideany(transport_,
                                                           GL.ASTEROID, collided=pygame.sprite.collide_mask)

                if collision is not None:
                    if collision in GL.ASTEROID:
                        if hasattr(collision, 'collide'):
                            collision.collide(None, transport_.damage)
                        else:
                            print(type(collision))
                            raise AttributeError

                ...
    if GL.P1 is not None and \
            isinstance(GL.P1, pygame.sprite.GroupSingle):
        if len(GL.P1) > 0:
            player1 = GL.P1.sprites()[0]

        # Detect player 1 shots
        p1_shots = pygame.sprite.Group()  # Player shots

        for sprite_ in GL.NetGroupAll:
            if sprite_.surface == "BLUE_LASER":
                p1_shots.add(sprite_)

        # Check player 1 shots collision with asteroids
        if player1 is not None and player1.alive():
            for shots, asteroids in pygame.sprite.groupcollide(
                    p1_shots, GL.ASTEROID, 1, 0).items():  # ,collided=pygame.sprite.collide_mask).items():
                if asteroids is not None:
                    for aster in asteroids:
                        if aster in GL.ASTEROID:
                            if hasattr(aster, 'hit'):
                                aster.hit(None, 100)  # -> check if asteroid explode otherwise blend the asteroid

    # Use collision mask for collision detection
    # Check collision between Player 2 and asteroids
    if P2 is not None and P2.alive():
        collision = pygame.sprite.spritecollideany(P2, GL.ASTEROID, collided=pygame.sprite.collide_mask)
        if collision is not None:
            if collision in GL.ASTEROID:
                if hasattr(collision, 'damage'):
                    P2.collide(collision.damage)    # -> send damage to player 2
                    collision.collide(P2, P2.damage)

        # check collision between player 2 shots and asteroids
        # delete the sprite sprite after collision.
        # pygame.sprite.groupcollide(groupa, groupb, dokilla, dokillb): return dict

        for shots, asteroids in pygame.sprite.groupcollide(GL.PLAYER_SHOTS, GL.ASTEROID, 1, 0).items():
            if asteroids is not None:
                for aster in asteroids:
                    if hasattr(aster, 'hit'):
                        aster.hit(P2, 100)  # -> check if asteroid explode otherwise blend the asteroid
                        new_rect = shots.rect.clamp(aster.rect)
                        # shots.collide(rect_=new_rect, object_=aster, damage_=100)
                    else:
                        print(type(aster))
                        raise AttributeError


if __name__ == '__main__':

    pygame.init()
    pygame.mixer.init()

    SERVER = '127.0.0.1'
    CLIENT = '127.0.0.1'
    # SERVER = '192.168.1.106'
    # CLIENT = '192.168.1.106'

    position = (0, 0)
    DRIVER = 'windib'  # 'windib' | 'directx'
    os.environ['SDL_VIDEODRIVER'] = DRIVER
    os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])

    GL = GL.__copy__(GL())

    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    GL.SCREENRECT = SCREENRECT
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)
    pygame.display.set_caption('PLAYER 2')

    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    # background vector
    vector1 = pygame.math.Vector2(x=0, y=0)
    vector2 = pygame.math.Vector2(x=0, y=-1024)

    # ********************************************************************
    # NETWORK SERVER / CLIENT

    # SpriteServer -> receive multi-player(s) positions
    # 1) Start the Server to receive multiplayer(s) position(s)
    # If no connection is made, the thread will remains listening/running
    # in the background, except if an error is raised.
    server = SpriteServer(GL, CLIENT, 1024)
    server.start()

    # SpriteClient -> forward all sprites positions
    # 2) Start the Client to send all sprites positions to multiplayer(s)
    client = SpriteClient(gl_=GL, host_=SERVER, port_=1025)
    client.start()
    # client.join()

    # Killing threads if no client connected
    if not client.is_alive() or GL.CONNECTION is False:
        print('Server is not running...')
        GL.SPRITE_CLIENT_STOP = True
        GL.SPRITE_SERVER_STOP = True
        force_quit(CLIENT, 1024)

    # *********************************************************************

    GL.All = LayeredUpdatesModified()
    PLAYER = pygame.sprite.GroupSingle()
    GL.PLAYER_SHOTS = pygame.sprite.Group()
    GL.ASTEROID = pygame.sprite.Group()

    Player2.image = P2_SURFACE
    Player2.containers = PLAYER, GL.All

    Shot.images = RED_LASER
    Shot.containers = GL.All, GL.PLAYER_SHOTS
    Shot.mask = pygame.mask.from_surface(RED_LASER)

    Explosion.containers = GL.All
    AfterBurner.containers = GL.All

    DisplayScore.containers = GL.All
    DisplayScore.images = pygame.Surface((10, 10))
    GL.P2_SCORE = DisplayScore(gl_=GL, timing_=8)

    MakeGems.containers = GL.All

    P2 = Player2(GL, 0, (screen.get_size()[0] // 2 + 220, SCREENRECT.h))

    transport_life_bar = HorizontalBar(start_color=pygame.Color(255, 7, 15, 0),
                                       end_color=pygame.Color(12, 12, 255, 0),
                                       max_=5000, min_=0,
                                       value_=5000,
                                       start_color_vector=(0, 0, 0),
                                       end_color_vector=(0, 0, 0),
                                       alpha=False, height=32,
                                       xx=180,
                                       scan=True)
    life = transport_life_bar.display_gradient()
    w, h = life.get_size()
    surf = pygame.Surface((w, h)).convert()
    surf.fill((0, 0, 0, 0))

    ShowLifeBar.containers = GL.All
    ShowLifeBar(gl_=GL, player_=P2, left_gradient_=pygame.Color(0, 7, 255, 0),
                right_gradient=pygame.Color(120, 255, 255, 0), pos_=(10, 10), timing_=8, scan_=True)

    PlayerLost.containers = GL.All
    PlayerLost.DIALOGBOX_READOUT_RED = DIALOGBOX_READOUT_RED
    PlayerLost.SKULL = SKULL
    font_ = freetype.Font('Assets\\Fonts\\Gtek Technology.ttf', size=14)
    ARCADE_FONT = freetype.Font(os.path.join('Assets\\Fonts\\', 'ARCADE_R.ttf'), size=9)
    ARCADE_FONT.antialiased = True

    LOST = PlayerLost(gl_=GL, font_=font_, image_=FINAL_MISSION, layer_=1)
    WIN = None

    GL.All.remove(LOST)

    GL.TIME_PASSED_SECONDS = 0

    clock = pygame.time.Clock()
    GL.STOP_GAME = False

    FRAME = 0
    GL.FRAME = 0

    f = open('P2_log.txt', 'w')
    text_size = 120
    half_frame = 0

    pygame.mixer.music.load('Assets\\MUSIC_1.mp3')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.5)

    # DIALOGBOX
    FRAMEBORDER.blit(FRAMESURFACE, (10, 15))
    DIALOG = FRAMEBORDER

    DialogBox.containers = GL.All
    DialogBox.images = DIALOG
    DialogBox.character = NAMIKO
    DialogBox.voice_modulation = VOICE_MODULATION
    DialogBox.readout = DIALOGBOX_READOUT
    FONT = freetype.Font('C:\\Windows\\Fonts\\Arial.ttf')
    FONT.antialiased = False
    DialogBox.FONT = FONT
    DialogBox.text = ["Protect the transport and reach out ", "Altera the green planet outside the", "asteroid belt.",
                      "There are huge asteroids ahead, focus ", "and dodge them carefully.", "Have fun and good luck.",
                      " ", "Over and out!", "Masako"]
    im = pygame.image.load("Assets\\icon_glareFx_blue.png").convert()
    DialogBox.scan_image = pygame.image.load("Assets\\icon_glareFx_blue.png").convert()
    DialogBox.scan_image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

    TIME_PASSED_SECONDS = 0
    FRAME = 0
    GL.FRAME = FRAME

    masako = DialogBox(gl_=GL, location_=(-DIALOG.get_width(), 150),
                       speed_=0, layer_=0, voice_=True, scan_=True, start_=0, direction_='RIGHT',
                       text_color_=pygame.Color(149, 119, 236, 245), fadein_=500, fadeout_=1000)

    cobra = pygame.image.load('Assets\\Cobra.png').convert()
    cobra.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    cobra = pygame.transform.smoothscale(cobra, (100, 170))
    DialogBox.character = [cobra, cobra]
    DialogBox.text = ["Don't worry, it won't take long", "before I wreck everything.", " "]
    DialogBox.images = pygame.transform.smoothscale(DIALOG, (400, 200))
    DialogBox.scan_image = pygame.image.load("Assets\\icon_glareFx_red.png").convert()
    DialogBox.scan_image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

    cob = DialogBox(gl_=GL, location_=(SCREENRECT.w + DialogBox.images.get_width(), 650),
                    speed_=0, layer_=-3, voice_=True, scan_=True, start_=500, direction_='LEFT',
                    text_color_=pygame.Color(249, 254, 56, 245), fadein_=500, fadeout_=1100)

    GL.MIXER = SoundControl(30)

    # transport hud 
    TRANS_HUD = LIFE_HUD.copy()

    while not GL.STOP_GAME:

        event_obj = EventAttr(event_='', frame_=GL.FRAME)
        Broadcast(event_obj).next_frame()

        # print('Server frame # %s, Client frame %s, difference %s %s %s'
        #      % (GL.REMOTE_FRAME, FRAME, GL.REMOTE_FRAME - FRAME, vector1, vector2))

        diff = GL.REMOTE_FRAME - FRAME

        # todo :
        #   Check if the correction is necessary since the background
        #   position is sent via network message and should get the correct
        #   x, y values as long as the connection status is up to date.
        #   Relaying on the network message to display background surface is
        #   not ideal in the eventuality of packets dropped, delays or network drops-out
        #   will create jerky movement and animation.
        """
        if diff != 0:

            vector1 = pygame.math.Vector2(x=0, y=0)
            vector2 = pygame.math.Vector2(x=0, y=0)

            div = GL.REMOTE_FRAME / 1024  # 0 - 1024 = 1025
            remaining = div - GL.REMOTE_FRAME // 1024
            # -1 because we are incrementing the vector1 & vector2 position down below
            # and doing it twice will offset the positions.
            frac = remaining * 1024

            if (GL.REMOTE_FRAME // 1024) % 2 == 0:
                vector1.y = frac
                vector2.y = frac - 1024
            else:
                vector1.y = -1024 + frac
                vector2.y = frac
            # FRAME number is now updated and background
            # sprite should be at the exact same position.
            # todo if server does not send package then FRAME 
            #   is null
            FRAME = GL.REMOTE_FRAME
        """
        # threading event lock with a timeout of 2ms
        # The game loop wait for a signal from the master game loop.
        # If nothing is received in less than 2ms, the lock is release and the scene is display as normal.
        # A non blocking lock guarantee a smoother animation and provides a good synchronisation when
        # all the network messages are received.
        # ** Only client(s) own a lock
        GL.NEXT_FRAME.wait()  # 0.002)
        GL.NEXT_FRAME.clear()
        GL.SIGNAL.clear()

        # Create cosmic dust
        if GL.FRAME % 10 == 0:
            if len(COSMIC_DUST_ARRAY) < 15:
                create_dust(GL)

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
                pygame.image.save(screen, 'P2_screenshot.png')

            if event.type == pygame.MOUSEMOTION:
                GL.MOUSE_POS = pygame.math.Vector2(event.pos)
            
        GL.All.update()

        if len(GL.NetGroupAll) > 0:
            GL.NetGroupAll.update()     # -> run all the update method
            GL.NetGroupAll.draw(screen)

        GL.All.draw(screen)

        # Update the sound Controller
        GL.MIXER.update()

        collision_detection()

        # Authorize Player 2 to send data to the server
        # Allowing to send only one set of data every frame.
        # The clear method is used in the class SpriteClient
        # right after receiving the Event
        GL.SIGNAL.set()

        # dust particles (show on the top of all other sprites)
        if len(COSMIC_DUST_ARRAY) > 0:
            display_dust(GL)

        if GL.TRANSPORT is not None and \
                isinstance(GL.TRANSPORT, pygame.sprite.GroupSingle):
            if len(GL.TRANSPORT) > 0:
                transport = GL.TRANSPORT.sprites()[0]

                if transport.alive():

                    if hasattr(transport, 'life'):
                        if transport.life > 1:
                            transport_life_bar.VALUE = int(transport.life)
                            life = transport_life_bar.display_gradient()
                            if life is not None:
                                TRANS_HUD.blit(surf, (83, 21))
                                TRANS_HUD.blit(life, (83, 21))
                                TRANS_HUD.blit(transport_life_bar.display_value(), (84, 29))
                                screen.blit(TRANS_HUD, (SCREENRECT.w // 2 + 120, 5))
        if FRAME < 200:
            if FRAME % 2 == 0:
                half_frame += 1
            size__ = max(35, text_size - half_frame if FRAME < text_size else 35)

            rect1 = font_.get_rect("get ready", style=freetype.STYLE_NORMAL,
                                   size=size__)
            font_.render_to(screen, ((SCREENRECT.w >> 1) - (rect1.w >> 1), (SCREENRECT.h >> 1)),
                            "get ready", fgcolor=pygame.Color(255, 244, 78),
                            size=size__)

        GL.TIME_PASSED_SECONDS = clock.tick(70)
        GL.SPEED_FACTOR = GL.TIME_PASSED_SECONDS / 1000
        GL.FPS.append(clock.get_fps())

        pygame.display.flip()

        FRAME += 1
        GL.FRAME = FRAME
        Broadcast.empty()

        def my_timer():
            timer = time.time()
            while time.time() - timer < 5:
                time.sleep(0.01)
            GL.All.add(LOST)

        # Check if Player 1 is still alive otherwise display 'mission fail'
        if not GL.All.has(P2):
            if not GL.All.has(LOST):
                t = threading.Thread(target=my_timer, args=())
                t.start()

        # Delete sprite from GL.NetGroupAll if it doesn't exist on the server side
        # f.write('\nGROUP_ALIVE ' + str(GL.GROUP_ALIVE))
        for spr_ in GL.NetGroupAll:
            if hasattr(spr_, 'id_'):
                if spr_.id_ not in GL.GROUP_ALIVE:
                    spr_.remove(GL.All, GL.NetGroupAll, GL.ASTEROID)
                    if hasattr(spr_, 'surface'):
                        # Also remove the sprite from its specific group if
                        # the sprite is the Transport
                        if spr_.surface == 'TRANSPORT':
                            GL.TRANSPORT.empty()
                        # Also remove the sprite from its specific group if
                        # the sprite is the PLAYER1
                        if spr_.surface == 'P1_SURFACE':
                            GL.P1.empty()
                    # f.write('\nDelete sprite from group alive : '
                    #         + str(spr_.id_) + ' surface ' + str(spr_.surface))

    f.close()

    GL.SPRITE_CLIENT_STOP = True
    GL.SPRITE_SERVER_STOP = True
    force_quit(CLIENT, 1024)

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
