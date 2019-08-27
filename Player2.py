# encoding: utf-8


import pygame
import socket
import _pickle as cpickle
import threading
import lz4.frame
import time
import copyreg
from SoundServer import SoundControl
import random
from random import uniform
from TextureTools import *
from NetworkBroadcast import Broadcast, StaticSprite, SoundAttr, EventAttr
from Explosions import Explosion
from MessageSender import SpriteClient
from GLOBAL import GL
from LayerModifiedClass import LayeredUpdatesModified
from AfterBurners import AfterBurner
from CreateHalo import PlayerHalo, AsteroidHalo
from Player1 import LaserImpact


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
        self.mask = pygame.mask.from_surface(self.image)  # Image have to be convert_alpha compatible
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
    def is_reloading():
        if FRAME - Shot.last_shot < 10:
            return True
        else:
            Shot.shooting = False
            return False

    def collide(self, rect_, object_) -> None:
        LaserImpact.containers = self.gl.All
        LaserImpact.images = IMPACT_LASER
        LaserImpact(gl_=self.gl, pos_=rect_.topleft, parent_=object_,
                    timing_=self.timing, blend_=pygame.BLEND_RGBA_ADD, layer_=0)
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

        if self.rect.colliderect(self.gl.SCREENRECT):
            self.shot_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
            self.shot_object.queue()

        self.dt += self.gl.TIME_PASSED_SECONDS


class Player2(pygame.sprite.Sprite):
    containers = None
    image = None

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
        self.speed = 300
        self.blend = None
        self.previous_pos = pygame.math.Vector2()  # previous position
        self.life = 1000
        self.eng_right = self.right_engine()
        self.eng_left = self.left_engine()
        # todo test if convert_alpha otherwise this is useless
        self.mask = pygame.mask.from_surface(self.image)  # Image have to be convert_alpha compatible
        self.damage = 900
        self.id_ = id(self)
        self.player_object = Broadcast(self.make_object())
        self.impact_sound_object = Broadcast(self.make_sound_object('IMPACT'))
        
    def make_sound_object(self, sound_name_: str) -> SoundAttr:
        return SoundAttr(frame_=self.gl.FRAME, id_=self.id_, sound_name_=sound_name_, rect_=self.rect)
    
    def make_object(self):
        # Only attributes self.gl.FRAME, self.rect are changing over the time.
        return StaticSprite(
                frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                layer_=self.layer, blend_=self.blend, rect_=self.rect)

    def explode(self):

        if self.alive():
            Explosion.images = EXPLOSION2
            Explosion.containers = self.gl.All
            Explosion(self, self.rect.center, self.gl,
                      self.timing, self.layer, texture_name_='EXPLOSION2')
            PlayerHalo.images = HALO_SPRITE13
            PlayerHalo.containers = self.gl.All
            PlayerHalo(texture_name_='HALO_SPRITE13', object_=self, timing_=10)

    def collide(self, damage_):
        if self.alive():
            self.life -= damage_
            self.gl.MIXER.play(sound_=IMPACT, loop_=False, priority_=0,
                               volume_=1.0, fade_out_ms=0, panning_=True,
                               name_='IMPACT', x_=self.rect.centerx,
                               object_id_=id(IMPACT),
                               screenrect_=self.gl.SCREENRECT)
            self.impact_sound_object.play()

    def hit(self, damage_):
        if self.alive():
            self.life -= damage_

    def left_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl,
                           (-5, 38), self.timing, pygame.BLEND_RGB_ADD, self.layer - 1, texture_name_='EXHAUST')

    def right_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl, (5, 38),
                           self.timing, pygame.BLEND_RGB_ADD, self.layer - 1, texture_name_='EXHAUST')

    def get_centre(self):
        return self.rect.center

    @staticmethod
    def disruption(image_) -> pygame.Surface:
        index = (FRAME >> 1) % len(DISRUPTION) - 1
        # Broadcast(self.gl.FRAME, self, 'DISRUPTION').animation(
        #    index, (self.rect.topleft[0], self.rect.topleft[1]),
        #    pygame.BLEND_RGB_ADD, parent_='P2_SURFACE', blend_pos_=(-20, -20))
        image_.blit(DISRUPTION[index], (-20, -20), special_flags=pygame.BLEND_RGB_ADD)
        return image_

    def shooting_effect(self) -> pygame.Surface:
        self.image.blit(GRID, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        # Broadcast(self.gl.FRAME, self, 'GRID').singleton(self.rect.topleft,
        #                                  pygame.BLEND_RGB_ADD, parent_='P2_SURFACE', blend_pos_=(0, 0))
        return self.image

    def update(self):

        self.rect.clamp_ip(SCREENRECT)

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            if self.life < 1:
                self.explode()
                self.kill()

            if self.gl.KEYS[pygame.K_UP]:
                self.rect.move_ip(0, -self.speed * self.gl.SPEED_FACTOR)

            if self.gl.KEYS[pygame.K_DOWN]:
                self.rect.move_ip(0, +self.speed * self.gl.SPEED_FACTOR)

            if self.gl.KEYS[pygame.K_LEFT]:
                self.rect.move_ip(-self.speed * self.gl.SPEED_FACTOR, 0)

            if self.gl.KEYS[pygame.K_RIGHT]:
                self.rect.move_ip(+self.speed * self.gl.SPEED_FACTOR, 0)

            if self.gl.KEYS[pygame.K_SPACE]:
                if not Shot.is_reloading():
                    self.shooting_effect()
                    Shot(self, self.rect.center, self.gl, self.timing, self.layer - 1, surface_name_='RED_LASER')

            # Broadcast the spaceship position every frames
            self.player_object.update({'frame': self.gl.FRAME, 'rect': self.rect})
            self.player_object.queue()

            if joystick is not None:
                self.rect.move_ip(JL3.x * self.gl.SPEED_FACTOR * self.speed,
                                  JL3.y * self.gl.SPEED_FACTOR * self.speed)

            if self.previous_pos == self.rect.center:
                self.rect.centerx += random.randint(-1, 1)
                self.rect.centery += random.randint(-1, 1)

            self.previous_pos = self.rect.center

            # !UPDATE the <follower> sprites with the new player position.
            self.eng_left.update()
            self.eng_right.update()

        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        self.image = self.disruption(self.image)


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, sprite_):
        # No sprite group assignment in the constructor
        pygame.sprite.Sprite.__init__(self)
        self.rect = sprite_.rect
        self.image = sprite_.image
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        self.id_ = sprite_.id_
        self.frame = sprite_.frame
        self.surface = sprite_.surface
        self.gl = GL
        assert hasattr(sprite_, 'life'), \
            "Asteroid broadcast object is missing <life> attribute."
        assert hasattr(sprite_, 'damage'), \
            "Asteroid broadcast object is missing <damage> attribute."
        self.life = sprite_.life
        self.damage = sprite_.damage

        self.index = 0

    def blend_(self):
        self.image.blit(LAVA[self.index % len(LAVA) - 1],
                        (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.index += 1

    def make_debris(self):
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

    def explode(self):
        # This is done on the server side
        """
        Explosion.images = EXPLOSION2
        Explosion(self, self.rect.center,
                  self.gl, 16, self.layer, texture_name_='EXPLOSION1')
        # Create Halo sprite
        AsteroidHalo.images = random.choice([HALO_SPRITE12, HALO_SPRITE14])
        AsteroidHalo.containers = self.gl.All
        AsteroidHalo(texture_name_='HALO_SPRITE12'
                     if AsteroidHalo.images == HALO_SPRITE12 else 'HALO_SPRITE14',
                     object_=self, timing_=10)
        """
        self.kill()

    def hit(self, damage_):

        self.life -= damage_

        if self.life < 1:
            self.make_debris()
            self.explode()
        else:
            self.blend_()

    def collide(self, damage_):

        self.life -= damage_
        # Play the sound locally only, the server is doing the same
        self.gl.MIXER.play(sound_=IMPACT1, loop_=False, priority_=0,
                           volume_=1.0, fade_out_ms=0, panning_=True,
                           name_='IMPACT1', x_=self.rect.centerx,
                           object_id_=id(IMPACT1),
                           screenrect_=self.gl.SCREENRECT)

        if self.life < 1:
            self.make_debris()
            self.explode()
        ...

    def update(self):
        ...


class Player1(pygame.sprite.Sprite):

    def __init__(self, sprite_):
        # No sprite group assignment in the constructor
        pygame.sprite.Sprite.__init__(self)
        self.rect = sprite_.rect
        self.image = sprite_.image
        self.image_copy = sprite_.image.copy()
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        self.id_ = sprite_.id_
        self.frame = sprite_.frame
        self.surface = sprite_.surface
        self.gl = GL
        self.index = 0

    def disruption(self):
        index = (FRAME >> 1) % len(DISRUPTION) - 1
        self.image.blit(DISRUPTION[index], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def update(self):
        self.image = self.image_copy.copy()
        self.disruption()
        ...


class Transport(pygame.sprite.Sprite):

    def __init__(self, sprite_):
        # No sprite group assignment in the constructor
        pygame.sprite.Sprite.__init__(self)
        self.rect = sprite_.rect
        self.image = sprite_.image
        self.image_copy = self.image.copy()
        self.blend = sprite_.blend
        self.layer = sprite_.layer
        assert hasattr(sprite_, 'impact'), \
            "Transport broadcast object is missing <impact> attribute."
        self.impact = sprite_.impact
        self.id_ = sprite_.id_
        self.frame = sprite_.frame
        self.surface = sprite_.surface
        self.gl = GL
        self.index = 0
        assert hasattr(sprite_, 'life'), \
            "Transport broadcast object is missing <life> attribute."
        assert hasattr(sprite_, 'damage'), \
            "Transport broadcast object is missing <damage> attribute."
        self.life = sprite_.life
        self.damage = sprite_.damage
        self.vertex_array = []

    def display_fire_particle_fx(self) -> None:
        # Display fire particles when the player has taken bad hits
        # Use the additive blend mode.

        for p_ in self.vertex_array:

            # queue the particle in the vector direction
            p_.rect.move_ip(p_.vector)
            p_.image = p_.images[p_.index]
            if p_.index > len(p_.images) - 2:
                p_.kill()
                self.vertex_array.remove(p_)

            p_.index += 1

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
        # self.gl.FIRE_PARTICLES_FX.add(sprite_)
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

    def update(self):

        self.image = self.image_copy.copy()

        if self.life < 2000:
            position = pygame.math.Vector2(randint(-50, 50), randint(-100, 100))
            self.fire_particles_fx(position_=position + pygame.math.Vector2(self.rect.center),
                                   vector_=pygame.math.Vector2(uniform(-1, 1), uniform(+1, +3)),
                                   images_=FIRE_PARTICLES,
                                   layer_=0, blend_=pygame.BLEND_RGB_ADD)
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
                    self.gl.SPRITE_SERVER_STOP
                    nbytes = 0

                buffer = self.view.tobytes()[:nbytes]

                try:

                    connection.sendall(buffer)

                except ConnectionResetError as error:
                    print("\n[-]SpriteServer - Lost connection with Server...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    self.gl.SPRITE_SERVER_STOP

                try:

                    # Decompress the data frame
                    decompress_data = lz4.frame.decompress(buffer)
                    data = cpickle.loads(decompress_data)

                except Exception:
                    # The decompression error can also happen when
                    # the bytes stream sent is larger than the buffer size.
                    # raise RuntimeError('Problem during decompression/un-pickling')
                    print('Problem during decompression/un-pickling, '
                          'packet size %s, buffer size %s at frame %s'
                          % (nbytes, len(buffer) if buffer is not None else None, self.gl.FRAME))
                    # self.gl.SPRITE_SERVER_STOP
                    data = None

                # Clearing the transport group is essential in order
                # to make sure that the transport sprite is still alive on the server side.
                # When the transport sprite is killed on the server side, a network message is broadcast
                # to the client(s) with the latest attributes values (e.g life value) and will remain
                # in the GL.TRANSPORT regardless of its status on the server.
                # We could check the transport's life points to determine if it is still alive or not and implement
                # a method to remove the sprite from the group, but the simplest way is to assume that if there
                # is no more coming transport network messages, it must be because it has been already killed.
                # The down side would be to see the sprite flickering when the connection is lost between the server
                # and the client.
                # GL.TRANSPORT = pygame.sprite.GroupSingle()

                # Clear the group asteroids. (same principle than above)
                self.gl.ASTEROID = pygame.sprite.Group()

                if isinstance(data, list):

                    data_set = set()

                    # Goes through the list of elements/sprites
                    for sprite_ in data:

                        # extract the frame number (server frame number)
                        # As we are iterating over all sprites
                        # self.gl.REMOTE_FRAME value will be equal to the
                        # sprite_.frame value of the last iterated element.
                        self.gl.REMOTE_FRAME = sprite_.frame

                        # Check if sprite is an event.
                        # event does not have all attributes 
                        if hasattr(sprite_, 'event'):

                            # Process broadcasted event
                            # Trigger next frame
                            if sprite_.event.isSet():
                                self.gl.NEXT_FRAME.set()
                            else:
                                self.gl.NEXT_FRAME.clear()

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

                            try:
                                
                                sprite_.image = eval(sprite_.surface)  # load surface
                                
                            except NameError:
                                # A texture is not present on the client side,
                                # it is worth checking into the Asset directory to make
                                # sure the image is present and the texture loaded into memory
                                raise RuntimeError("\n[-]SpriteServer - Surface "
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
                            # Add the sprite into the Asteroid group only.
                            # self.gl.ASTEROID group is null before the server broadcast
                            # Use the Asteroid group for collision detection mainly.
                            # Asteroid class has also some methods that can be triggered from client side
                            # such as queue and debris methods for localised special effects.
                            # The asteroid life points variable is broadcast from the server every
                            # frames, and should be considered as read only variable on the client side.
                            if sprite_.surface in ('DEIMOS', 'EPIMET'):
                                if sprite_.life > 0:
                                    # todo create a new_method for class Asteroid with id inventory
                                    s = Asteroid(sprite_)
                                    self.gl.ASTEROID.add(s)
                                else:
                                    ...

                            # Find Player 1 message and create a local instance (if still alive)
                            elif sprite_.surface == 'P1_SURFACE':
                                if sprite_.life > 0:
                                    s = Player1(sprite_)
                                    # The GroupSingle container only holds a single Sprite.
                                    # When a new Sprite is added, the old one is removed.
                                    # -> update the group with latest sprite changes. GL.P1 is used for
                                    # collision detection
                                    self.gl.P1.add(s)
                                else:
                                    # Removes all Sprites from this Group.
                                    self.gl.P1.empty()

                            # find the Transport message and create a local instance (if still alive)
                            elif sprite_.surface == 'TRANSPORT':
                                if sprite_.life > 0:
                                    s = Transport(sprite_)
                                    # The GroupSingle container only holds a single Sprite.
                                    # When a new Sprite is added, the old one is removed.
                                    # -> update the group with latest sprite changes.
                                    # GL.TRANSPORT is used for collision detection
                                    self.gl.TRANSPORT.add(s)
                                else:
                                    # Removes all Sprites from this Group.
                                    self.gl.TRANSPORT.empty()

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

                            # Add broadcast sprites to data_set (reset every time a message from server is received).
                            # data_set contains all sprites sent by the server for a specific frame number.
                            # The data_set cannot contains duplicates. The id attribute (memory location)
                            # is used as unique identification number to store sprites in the data_set.
                            # The element in data set represent all active (alive) sprites display on the
                            # server side (before server collision detection). 
                            data_set.add(sprite_.id_)
                            
                            # Add the sprite in self.gl.NetGroupAll (if not already in the group) or
                            # update attributes e.g position, texture.
                            # NetGroupAll, will be used in the main loop (locally) to display
                            # all the sprites broadcast from a specific frame number.
                            # If a sprite is not added to that group, it will be ignored
                            # and not display on the client side. 
                            if len(self.gl.NetGroupAll) > 0:
                                has_ = False
                                for sprites in self.gl.NetGroupAll:
                                    if sprites.id_ == s.id_:
                                        has_ = True
                                        sprites.rect = s.rect
                                        sprites.image = sprite_.image
                                        sprites.frame = sprite_.frame
                                        if hasattr(sprite_, 'life'):
                                            sprites.life = sprite_.life
                                        if hasattr(sprite_, 'impact'):
                                            sprites.impact = sprite_.impact
                                        break

                                if not has_:
                                    self.gl.NetGroupAll.add(s)

                            else:
                                self.gl.NetGroupAll.add(s)

                    # Compare NetGroupAll group to data_set and delete sprite(s)
                    # accordingly. Sprites in NetGroupAll and not in data_set will
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
                break
            # self.view = memoryview(bytearray(self.buf))
            # pygame.time.wait(1)

        print('\n[-]SpriteServer is now terminated...')


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

    transport = None
    player1 = None

    if GL.TRANSPORT is not None and \
            isinstance(GL.TRANSPORT, pygame.sprite.GroupSingle):
        if len(GL.TRANSPORT) > 0:
            transport = GL.TRANSPORT.sprites()[0]

        # Use collision mask for collision detection
        # It is compulsory to have sprite textures with alpha transparency information
        # in order to check for collision otherwise the collision will be ignored.
        # Check collisions between transport and asteroids

        if transport is not None:

            if transport.alive():

                collision = pygame.sprite.spritecollideany(
                    transport, GL.ASTEROID, collided=pygame.sprite.collide_mask)

                if collision is not None:
                    if hasattr(collision, 'collide'):
                        collision.collide(transport.damage)
                    else:
                        print(type(collision))
                        raise AttributeError

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
                    p1_shots, GL.ASTEROID, 0, 0).items():  # ,collided=pygame.sprite.collide_mask).items():
                if asteroids is not None:
                    for aster in asteroids:
                        if hasattr(aster, 'hit'):
                            aster.hit(100)  # -> check if asteroid explode otherwise blend the asteroid

    # Use collision mask for collision detection
    # Check collision between Player 2 and asteroids
    if P2 is not None and P2.alive():
        collision = pygame.sprite.spritecollideany(P2, GL.ASTEROID, collided=pygame.sprite.collide_mask)
        if collision is not None:
            P2.collide(collision.damage)    # -> send damage to player 2
            collision.collide(P2.damage)

        # check collision between player 2 shots and asteroids
        # delete the sprite after collision.
        collision = pygame.sprite.groupcollide(GL.PLAYER_SHOTS, GL.ASTEROID, 1, 0)
        if collision is not None:
            for asteroid in collision.values():
                for aster in asteroid:
                    if hasattr(aster, 'hit'):
                        aster.hit(100)  # -> check if asteroid explode otherwise blend the asteroid


if __name__ == '__main__':

    pygame.init()
    pygame.mixer.init()

    SERVER = '127.0.0.1'
    CLIENT = '127.0.0.1'
    # SERVER = '192.168.1.106'
    # CLIENT = '192.168.1.106'

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

    from Textures import *
    from Sounds import BLUE_LASER_SOUND, RED_LASER_SOUND, EXPLOSION_SOUND, IMPACT, IMPACT1
    from Asteroids import Debris

    # background vector
    vector1 = pygame.math.Vector2(x=0, y=0)
    vector2 = pygame.math.Vector2(x=0, y=-1024)

    # ********************************************************************
    # NETWORK SERVER / CLIENT

    # SpriteServer -> receive multiplayer(s) positions
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
        # todo write : to start the server first etc
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
    Explosion.containers = GL.All
    AfterBurner.containers = GL.All

    P2 = Player2(GL, 15, (screen.get_size()[0] // 2, screen.get_size()[1] // 2))
    # P2 = None
    GL.TIME_PASSED_SECONDS = 0

    clock = pygame.time.Clock()
    GL.STOP_GAME = False

    FRAME = 0
    GL.FRAME = 0

    f = open('P2_log.txt', 'w')

    GL.MIXER = SoundControl(20)

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

            if event.type == pygame.MOUSEMOTION:
                GL.MOUSE_POS = pygame.math.Vector2(event.pos)
            
        GL.All.update()

        if len(GL.NetGroupAll) > 0:
            GL.NetGroupAll.update()     # -> run all the update method
            GL.NetGroupAll.draw(screen)

        GL.All.draw(screen)

        # Authorize Player 2 to send data to the server
        # Allowing to send only one set of data every frame.
        # The clear method is used in the class SpriteClient
        # right after receiving the Event
        GL.SIGNAL.set()

        # Update the sound Controller
        GL.MIXER.update()

        collision_detection()

        GL.TIME_PASSED_SECONDS = clock.tick(70)
        GL.SPEED_FACTOR = GL.TIME_PASSED_SECONDS / 1000
        GL.FPS.append(clock.get_fps())
        pygame.display.flip()

        FRAME += 1
        GL.FRAME = FRAME
        Broadcast.empty()

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
