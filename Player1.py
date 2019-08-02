# encoding: utf-8
import random

import math

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


import pygame
import socket
import _pickle as cpickle
import _pickle as cpickle
import threading
import lz4.frame
import time
import copyreg
from SoundServer import SoundControl

# socket.setdefaulttimeout(1)


def unserialize_event(isset):
    e = threading.Event()
    if isset:
        e.set()
    return e


def serialize_event(e):
    return unserialize_event, (e.isSet(),)


copyreg.pickle(threading.Event, serialize_event)


# LayerUpdate method modified for blending effect
class LayeredUpdatesModified(pygame.sprite.LayeredUpdates):

    def __init__(self):
        pygame.sprite.LayeredUpdates.__init__(self)

    def draw(self, surface_):
        """draw all sprites in the right order onto the passed surface

        LayeredUpdates.draw(surface): return Rect_list

        """
        spritedict = self.spritedict
        surface_blit = surface_.blit
        dirty = self.lostsprites
        self.lostsprites = []

        # self.sprites() returns a ordered list of sprites (first back, last top).
        for spr in self.sprites():
            # spritedict  {<Broadcast sprite(in 1 groups)>: <rect(0, 0, 0, 0)>, ...
            # <Broadcast sprite(in 1 groups)>: <rect(0, 0, 0, 0)>}
            rec = spritedict[spr]
            if hasattr(spr, '_blend') and spr._blend is not None:
                newrect = surface_blit(spr.image, spr.rect, special_flags=spr._blend)

            else:
                newrect = surface_blit(spr.image, spr.rect)

            spritedict[spr] = newrect

        return dirty

    def empty(self):
        """remove all sprites
        Group.empty(): return None
        Removes all the sprites from the group.

        """
        for s in self.sprites():
            self.remove_internal(s)
            s.remove_internal(self)


class GL:
    STOP_GAME = False                       # Self explanatory
    TIME_PASSED_SECONDS = 0                 # Last clock tick in ms
    KEYS = None                             # Contains all pygame key events
    SPEED_FACTOR = 0                        # Speed variable for aircraft
    All = LayeredUpdatesModified()          # Pygane sprite group containing all sprites
    P1CS_STOP = False                       # Variable used to stop the game main loop (local main loop)
    NetGroupAll = LayeredUpdatesModified()  # Layer update pygame group capable of blit sprites
    # with given blend mode. This group contains every sprites sent by the clients over the network.
    SCREENRECT = None                       # Pygame Rect with screen dimension
    NEXT_FRAME = threading.Event()          # Threading Event sent to the client(s) to notify them
    # to process the next frame (basic synchronization)
    MIXER = None                            # Mixer, Sound controller. This instance control all sounds being played
    BYTES_SENT = []                         # Monitoring bytes sent to the client
    BYTES_RECEIVED = []                     # Monitoring bytes received from the client (values
    # should be identical to values BYTES_SENT)
    FRAME = 0                               # FRAME number, actual frame number being played in the game loop
    SIGNAL = threading.Event()              # Starting signal for sending player 2 data to the network
    FPS = []                                # List containing fps values for monitoring
    JOYSTICK = None                         # Joystick object
    CONNECTION = False                      # True | False if a client is connected to socket
    SPRITESERVER_STOP = False               # STOP the SpriteServer thread
    SPRITECLIENT_STOP = False               # STOP the SpriteClient thread
    RETRY = 5                               # Attempts before terminating network threads
    BUFFER = 2048


# Draw backgrounds
class Background(pygame.sprite.Sprite):

    containers = None   # pygame group
    image = None        # surface to display (can be a list of Surface or a single pygame.Surface)

    def __init__(self,
                 vector_: pygame.math.Vector2,       # background speed vector (pygame.math.Vector2)
                 position_: tuple,     # original position (tuple)
                 gl_: GL,              # global variables  (GL class)
                 layer_: int = -8,       # layer used default is -8 (int <= 0)
                 blend_: int = 0,        # pygame blend effect (e.g pygame.BLEND_RGB_ADD, or int)
                 event_name_: str = ''   # event name (str)
                 ):

        self._layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        # change sprite layer
        if isinstance(self.containers, pygame.sprite.LayeredUpdates):
            self.containers.change_layer(self, layer_)

        self.images_copy = Background.image.copy()
        self.image = self.images_copy[0] if isinstance(Background.image, list) else self.images_copy
        self.rect = self.image.get_rect(topleft=position_)
        self.position = position_
        self.vector = vector_
        self.gl = gl_
        self._blend = blend_
        self.event_name = event_name_

    def update(self):

        self.rect.move_ip(self.vector)

        if self.event_name == 'CL1':
            if self.rect.y > 1023:
                self.rect.y = random.randint(-1024, -CL1.get_height())
                self.rect.x = random.randint(-400, 400)
            Broadcast(self, 'CL1').move()
        elif self.event_name == 'CL2':
            if self.rect.y > 1023:
                self.rect.y = random.randint(-1024, -CL2.get_height())
                self.rect.x = random.randint(-400, 400)
            Broadcast(self, 'CL2').move()
        else:
            if self.rect.y > 1023:
                self.rect.y = -1024
            if self.event_name == 'BACK1_S':
                Broadcast(self, 'BACK1_S').move()
            else:
                Broadcast(self, 'BACK2_S').move()


# Create an instance and display a shooting stars onto a specific layer
# The sprite is display using blend additive mode and the
# refreshing rate is by default 16ms
class ShootingStar(pygame.sprite.Sprite):

    image = None        # sprite surface (single surface)
    containers = None   # sprite group to use

    def __init__(self,
                 gl_,           # global variables
                 layer_=-1,     # layer where the shooting sprite will be display
                 timing_=16     # refreshing rate, default is 16ms (60 fps)
                 ):

        if layer_:
            self._layer = layer_

        pygame.sprite.Sprite.__init__(self, self.containers)

        # change sprite layer
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.images_copy = ShootingStar.image.copy()
        self.image = self.images_copy[0] if isinstance(ShootingStar.image, list) else self.images_copy
        self.w, self.h = pygame.display.get_surface().get_size()
        self.position = pygame.math.Vector2(random.randint(0, self.w), random.randint(-self.h, 0))
        self.rect = self.image.get_rect(midbottom=self.position)
        self.speed = pygame.math.Vector2(random.uniform(-30, 30), 60)
        self.rotation = -270 - math.degrees(math.atan2(self.speed.y, self.speed.x))
        self.image = pygame.transform.rotozoom(self.image, self.rotation, 1)
        self._blend = pygame.BLEND_RGB_ADD
        self.timing = timing_
        self.gl = gl_
        self.dt = 0

    def update(self):

        if self.dt > self.timing:

            if self.rect.centery > self.h:
                self.kill()
            self.rect = self.image.get_rect(center=self.position)
            self.position += self.speed
            self.dt = 0

        if self.rect.colliderect(SCREENRECT):
            Broadcast(self, 'SHOOTING_STAR', rotation_=self.rotation).move()
        self.dt += self.gl.TIME_PASSED_SECONDS


class Shot(pygame.sprite.Sprite):
    images = None
    containers = None
    last_shot = 0
    shooting = False

    def __init__(self, parent_, pos_, gl_, timing_, layer_):

        self._layer = layer_
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
        self._blend = pygame.BLEND_RGBA_ADD

        self.parent = parent_
        if Shot.shooting and self.is_reloading():
            self.kill()
        else:

            if self.gl.MIXER.get_identical_id(id(BLUE_LASER_SOUND)):
                self.gl.MIXER.stop_object(id(BLUE_LASER_SOUND))

            self.gl.MIXER.play(sound_=BLUE_LASER_SOUND, loop_=False, priority_=0, volume_=1.0,
                               fade_out_ms=0, panning_=True, name_='BLUE_LASER_SOUND', x_=self.rect.centerx,
                               object_id_=id(BLUE_LASER_SOUND), screenrect_=self.gl.SCREENRECT)
            Shot.last_shot = FRAME
            Shot.shooting = True
            # update the sprite position to the remote display
            # index_=0 Sound not played yet on the client side
            Broadcast(self, 'BLUE_LASER').shoot(index_=0)

    @staticmethod
    def is_reloading() -> bool:
        if FRAME - Shot.last_shot < 10:
            return True
        else:
            Shot.shooting = False
            return False

    def update(self):
        if self.dt > self.timing:
            self.position += self.speed
            self.rect.center = (self.position.x, self.position.y)

            if not self.gl.SCREENRECT.colliderect(self.rect):
                self.kill()
            self.dt = 0
            # update the sprite position to the remote display
            # index_=1 Sound already played.

        Broadcast(self, 'BLUE_LASER').shoot(index_=1)
        self.dt += self.gl.TIME_PASSED_SECONDS


class AfterBurner(pygame.sprite.Sprite):

    containers = None
    images = None

    def __init__(self, parent_, gl_, offset_, timing_=16, blend_=0, layer_=0):

        self._layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(self.containers, pygame.sprite.LayeredUpdates):
            if layer_:
                self.containers.change_layer(self, layer_)

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
        self._blend = blend_

    def update(self):
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

        x, y = self.parent.rect.topleft[0] + self.offset[0] + 12, \
            self.parent.rect.topleft[1] + self.offset[1] + 12
        Broadcast(self, 'EXHAUST').animation(self.index, (x, y), pygame.BLEND_RGB_ADD)
        self.dt += self.gl.TIME_PASSED_SECONDS


class Explosion(pygame.sprite.Sprite):
    images = None
    containers = None

    def __init__(self, parent_, pos_, gl_, timing_, layer_):

        self._layer = layer_
        pygame.sprite.Sprite.__init__(self, self.containers)
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)

        self.images = Explosion.images
        self.n_ima = len(self.images) - 1
        self.image = self.images[0] if isinstance(self.images, list) else self.images
        self.timing = timing_
        self.pos = pos_
        self.gl = gl_
        self.position = pygame.math.Vector2(*self.pos)
        self.rect = self.image.get_rect(center=self.pos)
        self.dt = 0
        self._blend = pygame.BLEND_RGB_ADD
        self.parent = parent_
        self.i = 0

    def update(self):
        if self.dt > self.timing:

            if self.i < self.n_ima:

                self.image = self.images[self.i]
                if not self.gl.SCREENRECT.colliderect(self.rect):
                    self.kill()

                self.dt = 0
                self.i += 1
                # update the sprite to the remote display
            else:
                self.kill()

        Broadcast(self, 'EXPLOSION1').explosion(self.i)
        self.dt += self.gl.TIME_PASSED_SECONDS


class Player1(pygame.sprite.Sprite):
    containers = None
    image = None

    def __init__(self, gl_, timing_, pos_, layer_=0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = Player1.image
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect(center=pos_)
        self.timing = timing_
        self.gl = gl_
        self.dt = 0
        self.speed = 300
        self.layer = layer_
        self._blend = 0
        self.shooting = False
        self.previous_pos = pygame.math.Vector2()  # previous position
        self.life = 100  # player's life
        self.eng_right = self.right_engine()    # instance for right engine
        self.eng_left = self.left_engine()      # isntance for left engine

    def left_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl, (-22, 38), self.timing, pygame.BLEND_RGB_ADD, self.layer - 1)

    def right_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl, (22, 38), self.timing, pygame.BLEND_RGB_ADD, self.layer - 1)

    def get_centre(self) -> tuple:
        return self.rect.center

    def disruption(self, image) -> pygame.Surface:
        index = (FRAME >> 1) % len(DISRUPTION) - 1
        Broadcast(self, 'DISRUPTION').animation(
            index, (self.rect.topleft[0], self.rect.topleft[1]),
            pygame.BLEND_RGB_ADD, parent_='P1_SURFACE', blend_pos_=(-20, -20))
        image.blit(DISRUPTION[index], (-20, -20), special_flags=pygame.BLEND_RGB_ADD)
        return image

    def shooting_effect(self) -> pygame.Surface:
        self.image.blit(GRID, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        Broadcast(self, 'GRID').singleton(self.rect.topleft,
                                          pygame.BLEND_RGB_ADD, parent_='P1_SURFACE', blend_pos_=(0, 0))
        return self.image

    def update(self):

        self.rect.clamp_ip(SCREENRECT)

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            if self.life < 1:
                Explosion.images = EXPLOSION1
                Explosion(self, self.rect.center, self.gl, self.timing, self.layer)
                self.kill()

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
                Shot(self, self.rect.center, self.gl, 0, self.layer - 1)

            if joystick is not None:
                self.rect.move_ip(JL3.x * self.gl.SPEED_FACTOR * self.speed,
                                  JL3.y * self.gl.SPEED_FACTOR * self.speed)

            # Broadcast the spaceship position every frames
            Broadcast(self, 'P1_SURFACE').move()

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


# This method send data to remote computer(s) using TCP protocol (assuming client(s) can be reachable
# through firewall and through the network).
# This method is running in parallel to the game main loop using the threading library
# to send formatted data to available client(s).
# The data are pickled and compressed with Lz4 algorithm before being sent to the client.
# socket.sendall is a high-level Python-only method that sends the entire buffer
# you pass or throws an exception. It does that by calling socket.send until
# everything has been sent or an error occurs.
# If you're using TCP with blocking sockets and don't want to be bothered by
# internals (this is the case for most simple network applications), use sendall.
class SpriteClient(threading.Thread):

    def __init__(self, gl_, host_, port_):
        """
            :param gl_  : global variables class
            :param host_: ip address, client address (string)
            :param port_: client port to connect to (integer)
            :return: None
        """
        threading.Thread.__init__(self)
        self.gl = gl_
        self.host = host_
        self.port = port_
        retry = 1
        self.gl.CONNECTION = False
        self.gl.SPRITECLIENT_STOP = False
        for r in range(self.gl.RETRY):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.gl.CONNECTION = True
                self.gl.SPRITECLIENT_STOP = False
                break
            except Exception:
                print('\n[+]Waiting for client(s) to connect...attempt # %s/%s ' % (retry, self.gl.RETRY))
                retry += 1
                time.sleep(2)
                self.gl.CONNECTION = False
                self.gl.SPRITECLIENT_STOP = True
        if self.gl.CONNECTION:
            print('\n[+]Player 2 is connected from %s port %s...' % (host_, port_))
        else:
            print('\n[+]Player 2 is not connected after 5 attempts...')

    def run(self):

        old_data = Broadcast.msg

        while not self.gl.P1CS_STOP and not self.gl.SPRITECLIENT_STOP:

            # check for the signal.
            # if signal is set, sending data to multi-players
            if self.gl.SIGNAL.isSet():

                self.gl.SIGNAL.clear()

                buffer_ = self.gl.BUFFER
                # todo check if data are different
                data = Broadcast.msg
                try:
                    if data is not None and len(data) > 0:

                        pickle_data = cpickle.dumps(data)
                        # The compress() function reads the input data and compresses it and returns a LZ4 frame.
                        # A frame consists of a header, and a sequence of blocks of compressed data, and a frame
                        # end marker (and optionally a checksum of the uncompressed data). The decompress() function
                        # takes a full LZ4 frame, decompresses it (and optionally verifies the uncompressed data
                        # against the stored checksum), and returns the uncompressed data.
                        compress_data = lz4.frame.compress(pickle_data,
                                                           compression_level=lz4.frame.COMPRESSIONLEVEL_MAX) # _MINHC)
                        # send the entire buffer bytes like data
                        self.sock.sendall(compress_data)

                        # todo counting total bytes sent
                        data_received = self.sock.recv(buffer_)
                        # print('\nFrame # %s , data sent %s, data received %s '
                        #      % (FRAME, len(compress_data), len(data_received)))
                        GL.BYTES_SENT.append(len(compress_data))
                        GL.BYTES_RECEIVED.append(len(data_received))

                        old_data = data

                except (socket.error, cpickle.UnpicklingError) as error:
                    print('\n[-]SpriteClient - ERROR @ frame: %s : %s %s' % (FRAME, error, time.ctime()))

            # 1ms delay will create large fps oscillation for
            # highest frame frame rate e.g 300fps. For 70 fps the fluctuating will be marginal
            pygame.time.wait(1)

        print("\n[+]SpriteClient - is now closed...")
        self.sock.close()


class SpriteServer(threading.Thread):

    def __init__(self,
                 gl_,    # Global variables class
                 host_,  # host address (string)
                 port_,  # port value (integer)
                 ):

        threading.Thread.__init__(self)

        self.gl = gl_
        self.gl.SPRITESERVER_STOP = False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as error:
            print('\n[-]SpriteServer - ERROR : %s %s' % (error, time.ctime()))
            gl_.P1CS_STOP = True
            self.gl.SPRITESERVER_STOP = True

        try:
            self.sock.bind((host_, port_))
            self.sock.listen(1)
        except socket.error as error:
            print('\n[-]SpriteServer - ERROR : %s %s' % (error, time.ctime()))
            gl_.P1CS_STOP = True
            self.gl.SPRITESERVER_STOP = True

        self.buf = self.gl.BUFFER
        self.totalbytes = 0
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

        while not self.gl.P1CS_STOP and not self.gl.SPRITESERVER_STOP:
            # try:

            while not self.gl.P1CS_STOP and not self.gl.SPRITESERVER_STOP:

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
                    self.gl.P1CS_STOP = True
                    nbytes = 0

                buffer = self.view.tobytes()[:nbytes]
                try:
                    connection.sendall(self.view.tobytes()[:nbytes])
                except ConnectionResetError as error:
                    print("\n[-]SpriteServer - Lost connection with Player 2 ...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    # todo need to remove player 2 sprite
                    # signal to kill both threads SpriteServer and SpriteClient
                    self.gl.P1CS_STOP = True

                try:
                    # Decompress the data frame
                    decompress_data = lz4.frame.decompress(buffer)
                    data = cpickle.loads(decompress_data)
                except Exception:
                    # The decompression error can also happen when
                    # the bytes stream sent is larger than the buffer size.
                    # todo need to remove player 2 sprite
                    # signal to kill both threads SpriteServer and SpriteClient
                    self.gl.P1CS_STOP = True
                    data = None

                modified_surface = {}
                # todo check if self.gl.NetGroupAll.empty() is faster
                self.gl.NetGroupAll = LayeredUpdatesModified()

                if isinstance(data, list):

                    for sprite_ in data:

                        if sprite_.surface == 'dummy':
                            continue
                        try:
                            sprite_.image = eval(sprite_.surface)  # load surface
                        except NameError:
                            raise RuntimeError("\n[-]SpriteServer - Surface "
                                               "'%s' does not exist " % sprite_.surface)

                        if isinstance(sprite_.image, list):
                            sprite_.image = sprite_.image[sprite_.index % len(sprite_.image) - 1]

                        # check if the sprite need to be blend with parent ?
                        # Goes through all sprites and select only the ones that blends with parent(s)
                        if hasattr(sprite_, 'parent') and sprite_.parent is not None:
                            # looking for parent sprite
                            for spr in data:

                                if spr.surface == sprite_.parent:

                                    # Save parent surface in dict.
                                    # Check if the sprite surface is already saved
                                    # **Single copy to avoid duplicating surface changes
                                    if spr.surface not in modified_surface:
                                        modified_surface[spr.surface] = eval(spr.surface).copy()

                                    # load parent surface
                                    surf1 = eval(spr.surface)   # load parent surface
                                    # Blend both sprites
                                    surf1.blit(sprite_.image,
                                               sprite_.blend_pos, special_flags=sprite_._blend)
                                    # parent sprite is updated ** (see above)
                                    spr.image = surf1

                                    if sprite_ in data:
                                        data.remove(sprite_)
                        else:
                            continue

                    # Goes through the list of sprites and apply transformation(s)
                    for sprite_ in data:

                        try:
                            sprite_.image = eval(sprite_.surface)  # load surface
                        except NameError:
                            raise RuntimeError("\n[-]SpriteServer - Surface "
                                               "'%s' does not exist " % sprite_.surface)

                        if isinstance(sprite_.image, list):
                            sprite_.image = sprite_.image[sprite_.index % len(sprite_.image) - 1]

                        if sprite_.surface == 'RED_LASER' and sprite_.index == 0:

                            self.gl.MIXER.stop_object(id(RED_LASER_SOUND))
                            self.gl.MIXER.play(sound_=RED_LASER_SOUND, loop_=False, priority_=0,
                                               volume_=1.0, fade_out_ms=0, panning_=True,
                                               name_='RED_LASER_SOUND', x_=sprite_.rect.centerx,
                                               object_id_=id(RED_LASER_SOUND),
                                               screenrect_=self.gl.SCREENRECT)
                        # Apply transformation
                        # rotation attribute is a class default attributes,(no need to check on it)
                        if sprite_.rotation is not None and sprite_.rotation != 0:
                            sprite_.image = pygame.transform.rotozoom(sprite_.image, sprite_.rotation, 1)

                        s = pygame.sprite.Sprite()
                        s.rect = sprite_.rect
                        s.image = sprite_.image
                        s._blend = sprite_._blend
                        s._layer = sprite_._layer

                        self.gl.NetGroupAll.add(s)

                    # Reload original texture
                    for pair in modified_surface.items():
                        globals()[pair[0]] = pair[1]

                # data fully received breaking the loop, clear the buffer
                break

            pygame.time.wait(1)
            """
            except Exception as error:
                print('\n[-]SpriteServer - ERROR @ frame: %s : %s %s' % (FRAME, error, time.ctime()))

            finally:
                # Clean up the connection
                if 'connection' in globals() and connection is not None:
                    connection.close()
            """
        print('\n[-]SpriteServer is now terminated...')


# the object and minimizing the packets size.
class Broadcast(object):

    msg = []

    def __init__(self, sprite_: pygame.sprite.Sprite,
                 surface_name_: str,
                 rotation_: int = 0,
                 index_: int = 0,
                 ):

        # Attributes :       
        self.frame = FRAME                      # Put the actual frame number
        self._layer = self.get_layer(sprite_)   # fetch the layer from the sprite

        if hasattr(sprite_, '_blend'):
            self._blend = sprite_._blend
        if hasattr(sprite_, 'rect'):
            self.rect = sprite_.rect.copy()

        self.surface = surface_name_
        self.rotation = rotation_
        self.index = index_

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

    @staticmethod
    def get_layer(sprite_: pygame.sprite.Sprite) -> int:
        if hasattr(sprite_, '_layer'):
            layer = sprite_._layer
        else:
            layer = 0
        return layer

    def add(self):
        Broadcast.msg.append(self)

    # move a sprite/surface to a new position on the client display
    def move(self):
        self.add()

    # Put a bullet sprite on the client display
    # mirroring bullets on local display
    def shoot(self, index_=1):
        self.index = index_
        self.add()

    def explosion(self, index_):
        self.index = index_
        self.add()

    def singleton(self, pos_, blend_=0, parent_=None, blend_pos_=(0, 0)):
        self.rect.topleft = pos_
        if parent_ is not None:
            self.parent = parent_
        if blend_ != 0:
            self._blend = blend_
            self.blend_pos = blend_pos_

        self.add()

    # Convert a sprite animation into a list of surfaces with attributes.
    # The sprite animation is played on the server and decompose into an object
    # containing the current surface being display. It also contains all the attributes
    # in order to place and display the surfaces at the right location on the client display.
    # If the blend mode is used, the client needs to know the parent surface that needs to blend
    # with the current surface (parent surface)
    # index provide the element number from the list being played.
    # blend_pos is position of the blend inside the texture/surface e.g
    # surface.blit(surf, blend_pos, special_flags = _blend)
    def animation(self, index_, pos_, blend_=0, parent_=None, blend_pos_=(0, 0)):
        self.parent = parent_
        self.index = index_
        self.rect.topleft = pos_

        if blend_ != 0:
            self._blend = blend_
            self.blend_pos = blend_pos_
        if parent_ is not None:
            self.parent = parent_

        self.add()

    # Method used for sending a signal to the clients to tell them to process the next frame.
    # On the client side the main loop is waiting for that specific threading.Event lock mechanism
    # to synchronize the client display with the Server.   
    def next_frame(self):
        # Push a threading event (next frame event)
        # on the client side.
        self.del_attributes(['rotation', 'index', '_layer', 'surface', 'rect'])
        self.event = GL.NEXT_FRAME
        self.add()

    @staticmethod
    def empty():
        Broadcast.msg = []

    def del_attributes(self, attributes_):
        if attributes_ is not None:
            for attr in attributes_:
                if hasattr(self, attr):
                    delattr(self, attr)
        return self


# function used for terminating SERVER/ CLIENT threads listening (blocking socket)
def force_quit(host_: str, port_: int) -> None:
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


def spread_sheet_fs8(file: str, chunk: int, rows_: int, columns_: int, tweak_: bool = False, *args) -> list:
    """ surface fs8 without per pixel alpha channel """
    assert isinstance(file, str), 'Expecting string for argument file got %s: ' % type(file)
    assert isinstance(chunk, int), 'Expecting int for argument number got %s: ' % type(chunk)
    assert isinstance(rows_, int) and isinstance(columns_, int), 'Expecting int for argument rows_ and columns_ ' \
                                                                 'got %s, %s ' % (type(rows_), type(columns_))
    image_ = pygame.image.load(file)
    try:
        array = pygame.surfarray.pixels3d(image_)
    except Exception:
        array = pygame.surfarray.array3d(image_)

    animation = []
    animation_append = animation.append
    pygame_surfarray_make_surface = pygame.surfarray.make_surface
    # split sprite-sheet into many sprites
    for rows in range(rows_):
        for columns in range(columns_):
            if tweak_:
                chunkx = args[0]
                chunky = args[1]
                array1 = array[columns * chunkx:(columns + 1) * chunkx, rows * chunky:(rows + 1) * chunky, :]
            else:
                array1 = array[columns * chunk:(columns + 1) * chunk, rows * chunk:(rows + 1) * chunk, :]
            surface_ = pygame_surfarray_make_surface(array1)
            animation_append(surface_.convert())
    return animation


if __name__ == '__main__':

    pygame.init()
    pygame.mixer.init()

    SERVER = '127.0.0.1'
    CLIENT = '127.0.0.1'
    # SERVER = '192.168.1.106'
    # CLIENT = '192.168.1.112'

    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    GL.SCREENRECT = SCREENRECT
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)
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
    # *********************************************************************

    BACK = pygame.image.load('Assets\\BACK1.png')\
        .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)

    # Display pixels on the background surfaces
    def create_stars(surface_) -> None:
        w, h = surface_.get_size()
        surface_.lock()
        for r in range(3000):
            rand = random.randint(0, 1000)
            # yellow
            if rand > 950:
                color = pygame.Color(255, 255, random.randint(1, 255), random.randint(1, 255))
            # red
            elif rand > 995:
                color = pygame.Color(random.randint(1, 255), 0, 0, random.randint(1, 255))
            # blue
            elif rand > 998:
                color = pygame.Color(0, 0, random.randint(1, 255), random.randint(1, 255))
            else:
                avg = random.randint(128, 255)
                color = pygame.Color(avg, avg, avg, random.randint(1, 255))
            coords = (random.randint(0, w - 1), random.randint(0, h - 1))
            color_org = surface_.get_at(coords)[:3]
            if sum(color_org) < 384:
                surface_.set_at(coords, color)
        surface_.unlock()

    create_stars(BACK)

    BACK_ARRAY = pygame.surfarray.array3d(BACK)
    BACK1 = BACK_ARRAY[:800, 0:1024]
    BACK1_S = pygame.surfarray.make_surface(BACK1)
    BACK2 = BACK_ARRAY[:800, 1024:2048]
    BACK2_S = pygame.surfarray.make_surface(BACK2)
    # background vector
    vector1 = pygame.math.Vector2(x=0, y=0)
    vector2 = pygame.math.Vector2(x=0, y=-1024)

    CL1 = pygame.image.load('Assets\\cloud22_.png')\
        .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)
    CL1 = pygame.transform.smoothscale(CL1, (800, 800))
    CL2 = pygame.image.load('Assets\\cloud11_.png')\
        .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)
    CL2 = pygame.transform.smoothscale(CL2, (800, 800))

    P1_SURFACE = pygame.image.load('Assets\\Eigle_90x123.png').convert_alpha()
    P1_SURFACE = pygame.transform.smoothscale(P1_SURFACE, (64, 64))
    P2_SURFACE = pygame.image.load('Assets\\Raven_128x128_red.png').convert_alpha()
    P2_SURFACE = pygame.transform.smoothscale(P2_SURFACE, (64, 64))

    BLUE_LASER = pygame.image.load('Assets\\lzrfx021.png').convert()
    BLUE_LASER = pygame.transform.rotate(BLUE_LASER, 90)
    BLUE_LASER = pygame.transform.smoothscale(BLUE_LASER, (24, 35))
    BLUE_LASER_SOUND = pygame.mixer.Sound('Assets\\heavylaser1.ogg')

    RED_LASER = pygame.image.load('Assets\\lzrfx033.png').convert()
    RED_LASER = pygame.transform.rotate(RED_LASER, 90)
    RED_LASER = pygame.transform.smoothscale(RED_LASER, (24, 35))
    RED_LASER_SOUND = pygame.mixer.Sound('Assets\\fire_bolt_micro.ogg')

    EXHAUST = spread_sheet_fs8('Assets\\Exhaust2_.png', 128, 8, 8)
    i = 0
    for surface in EXHAUST:
        surface = pygame.transform.smoothscale(surface, (40, 40))
        EXHAUST[i] = surface
        i += 1

    EXHAUST1 = spread_sheet_fs8('Assets\\Exhaust5_64x64_5x5.png', 64, 5, 5)
    i = 0
    for surface in EXHAUST1:
        surface = pygame.transform.smoothscale(surface, (30, 35))
        EXHAUST1[i] = surface
        i += 1

    DISRUPTION = spread_sheet_fs8('Assets\\Blurry_Water1_256x256_6x6_1.png', 256, 6, 6)
    i = 0
    for surface in DISRUPTION:
        surface = pygame.transform.smoothscale(surface, (120, 120))
        DISRUPTION[i] = surface
        i += 1

    DISRUPTION1 = spread_sheet_fs8('Assets\\Electric_effect_256x256_6x6.png', 256, 6, 6)
    i = 0
    for surface in DISRUPTION1:
        surface = pygame.transform.smoothscale(surface, (64, 64))
        DISRUPTION1[i] = surface
        i += 1

    EXPLOSION1 = spread_sheet_fs8('Assets\\explosion1_.png', 256, 7, 5)

    GRID = pygame.image.load('Assets\\grid2.png').convert()
    GRID = pygame.transform.smoothscale(GRID, (64, 64))

    # ********************************************************************
    # NETWORK SERVER / CLIENT

    # SpriteServer -> receive multiplayer(s) positions
    # 1) Start the Server to receive multiplayer(s) position(s)
    # If no connection is made, the thread will remains listening/running
    # in the background, except if an error is raised.
    server = SpriteServer(GL, SERVER, 1025)
    server.start()

    # SpriteClient -> forward all sprites positions
    # 2) Start the Client to send all sprites positions to multiplayer(s) 
    client = SpriteClient(gl_=GL, host_=CLIENT, port_=1024)
    client.start()
    # client.join()

    # Killing threads if no client connected
    if not client.is_alive() or GL.CONNECTION is False:
        print('No player detected')
        GL.SPRITECLIENT_STOP = True
        GL.SPRITESERVER_STOP = True
        force_quit(SERVER, 1025)

    # *********************************************************************

    GL.All = LayeredUpdatesModified()

    Player1.image = P1_SURFACE
    Player1.containers = GL.All
    Shot.images = BLUE_LASER
    Shot.containers = GL.All
    Explosion.containers = GL.All
    Background.containers = GL.All
    AfterBurner.containers = GL.All

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
               position_=pygame.math.Vector2(x=random.randint(0, 800), y=200),
               gl_=GL, layer_=-2, blend_=pygame.BLEND_RGB_ADD, event_name_='CL2')

    SHOOTING_STAR = pygame.image.load('Assets\\shooting_star.png')\
        .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)
    SHOOTING_STAR = pygame.transform.scale(SHOOTING_STAR, (25, 80))
    ShootingStar.containers = GL.All
    ShootingStar.image = SHOOTING_STAR

    P1 = Player1(GL, 15, (screen.get_size()[0] // 2, screen.get_size()[1] // 2))

    GL.TIME_PASSED_SECONDS = 0

    clock = pygame.time.Clock()
    GL.STOP_GAME = False

    FRAME = 0

    GL.MIXER = SoundControl(20)

    while not GL.STOP_GAME:

        # print('Server frame # %s vector1 %s vector2 %s' % (FRAME, vector1, vector2))

        # Send an event to the client triggering the next frame
        GL.NEXT_FRAME.set()     # set the event
        Broadcast(pygame.sprite.Sprite(), 'dummy').next_frame()

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

        if random.randint(0, 1000) > 985:
            shoot = ShootingStar(gl_=GL, layer_=0, timing_=16)

        # update sprites positions and add sprites transformation
        # At this stage no sprites are display onto the screen. Therefore,
        # sprite's methods blitting directly surface or image onto the screen
        # will takes the risk to see their surfaces overlay by another sprites surface while calling
        # any group's draw methods (see below)
        GL.All.update()

        # Authorize Player 1 to send data to the server
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
        #  the display to avoid filling up the group of new instances.

        GL.All.draw(screen)

        # Draw the network sprite above the background
        if GL.CONNECTION:
            GL.NetGroupAll.draw(screen)

        # *************************************************************
        # Draw here all the other sprites that does not belongs to
        # common groups (GL.All & GL.NetGroupAll).
        # Sprite last blit onto the display are at the top layer.
        # Be aware that any surface(s) blit with blend attribute will
        # also blend with the entire sprite scene (blending with
        # sprites from all layers)
        # What to blit in this location?
        # -> Drawing GUI and life/energy sprite bars, screen bullet impacts
        # special effects, final score, ending screen and text inputs etc.

        # Update the sound Controller
        GL.MIXER.update()

        GL.TIME_PASSED_SECONDS = clock.tick(70)
        GL.SPEED_FACTOR = GL.TIME_PASSED_SECONDS / 1000
        GL.FPS.append(clock.get_fps())
        pygame.display.flip()

        FRAME += 1
        GL.FRAME = FRAME
        Broadcast.empty()

    GL.SPRITECLIENT_STOP = True
    GL.SPRITESERVER_STOP = True
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

