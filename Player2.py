# encoding: utf-8

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


import pygame
import socket
import _pickle as cpickle
import threading
import lz4.frame
import time
import copyreg
from SoundServer import SoundControl
import random


def unserialize_event(isset):
    e = threading.Event()
    if isset:
        e.set()
    return e


def serialize_event(e):
    return unserialize_event, (e.isSet(),)


copyreg.pickle(threading.Event, serialize_event)


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
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]

            if hasattr(spr, '_blend') and spr._blend is not None:
                newrect = surface_blit(spr.image, spr.rect, special_flags=spr._blend)

            else:
                newrect = surface_blit(spr.image, spr.rect)

            if rec is init_rect:
                dirty_append(newrect)

            else:

                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))

                else:
                    dirty_append(newrect)
                    dirty_append(rec)

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
        self._blend = pygame.BLEND_RGB_ADD
        self.parent = parent_
        if Shot.shooting and self.is_reloading():
            self.kill()
        else:
            if self.gl.MIXER.get_identical_id(id(RED_LASER_SOUND)):
                self.gl.MIXER.stop_object(id(RED_LASER_SOUND))

            self.gl.MIXER.play(sound_=RED_LASER_SOUND, loop_=False, priority_=0, volume_=1.0,
                               fade_out_ms=0, panning_=True, name_='RED_LASER_SOUND', x_=self.rect.centerx,
                               object_id_=id(RED_LASER_SOUND), screenrect_=self.gl.SCREENRECT)
            Shot.last_shot = FRAME
            Shot.shooting = True
            # update the sprite position to the remote display
            # index_=0 Sound not played yet on the client side
            Broadcast(self, 'RED_LASER').shoot(index_=0)

    @staticmethod
    def is_reloading():

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
        # index_ = 1 (Laser sound already played)
        Broadcast(self, 'RED_LASER').shoot(index_=1)
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


class Player2(pygame.sprite.Sprite):
    containers = None
    image = None

    def __init__(self, gl_, timing_, pos_, layer_=0):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self._layer = -1
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, self._layer)
        self.image = Player2.image
        # self.image_ = memoryview(self.image)
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect(center=pos_)
        self.timing = timing_
        self.gl = gl_
        self.dt = 0
        self.speed = 300
        self.layer = layer_
        self._blend = None
        self.previous_pos = pygame.math.Vector2()  # previous position
        self.life = 100
        self.eng_right = self.right_engine()
        self.eng_left = self.left_engine()

    def left_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl, (-5, 38), self.timing, pygame.BLEND_RGB_ADD, self.layer - 1)

    def right_engine(self) -> AfterBurner:
        AfterBurner.images = EXHAUST
        return AfterBurner(self, self.gl, (5, 38), self.timing, pygame.BLEND_RGB_ADD, self.layer - 1)

    def get_centre(self):
        return self.rect.center

    def disruption(self, image) -> pygame.Surface:
        index = (FRAME >> 1) % len(DISRUPTION) - 1
        Broadcast(self, 'DISRUPTION').animation(
            index, (self.rect.topleft[0], self.rect.topleft[1]),
            pygame.BLEND_RGB_ADD, parent_='P2_SURFACE', blend_pos_=(-20, -20))
        image.blit(DISRUPTION[index], (-20, -20), special_flags=pygame.BLEND_RGB_ADD)
        return image

    def shooting_effect(self) -> pygame.Surface:
        self.image.blit(GRID, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        Broadcast(self, 'GRID').singleton(self.rect.topleft,
                                          pygame.BLEND_RGB_ADD, parent_='P2_SURFACE', blend_pos_=(0, 0))
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

            if self.gl.KEYS[pygame.K_SPACE]:
                if not Shot.is_reloading():
                    self.shooting_effect()
                    Shot(self, self.rect.center, self.gl, self.timing, self.layer - 1)

            # Broadcast the spaceship position every frames
            Broadcast(self, 'P2_SURFACE').move()

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
        self.format = self.get_flag(sprite_)    # fetch the image format from the given sprite
        if hasattr(sprite_, '_blend'):
            self._blend = sprite_._blend
        if hasattr(sprite_, 'rect'):
            self.rect = sprite_.rect.copy()
        # Override the attribute image as we
        # do not want to send the image over the network
        self.image = None
        self.surface = surface_name_
        # surface is rotated from its original
        # position angle
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
        self._blend = blend_
        self.parent = parent_
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
        self._blend = blend_
        self.parent = parent_
        self.blend_pos = blend_pos_
        self.add()

    # Method used for sending a signal to the clients to tell them to process the next frame.
    # On the client side the main loop is waiting for that specific threading.Event lock mechanism
    # to synchronize the client display with the Server.
    def next_frame(self):
        # Push a threading event (next frame event)
        # on the client side.
        self.event = GL.NEXT_FRAME
        self.add()

    @staticmethod
    def empty():
        Broadcast.msg = []


class GL:
    STOP_GAME = False
    TIME_PASSED_SECONDS = 0                 # Last clock tick in ms
    KEYS = None                             # Contains all pygame key events
    SPEED_FACTOR = 0                        # Speed variable for aircraft
    All = LayeredUpdatesModified()          # Pygane sprite group containing all sprites
    P2CS_STOP = False                       # Variable used to stop the game main loop (local main loop)
    NetGroupAll = LayeredUpdatesModified()
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
    JOYSTICK = None                         # Joystick object reference
    CONNECTION = False                      # True | False if a client is connected to socket
    SPRITESERVER_STOP = False               # STOP the SpriteServer thread
    SPRITECLIENT_STOP = False               # STOP the SpriteClient thread
    REMOTE_FRAME = 0                        # Server frame number (Master frame number)
    RETRY = 5
    BUFFER = 2048


# This function send data to a distant computer located
# on the same network.
# socket.sendall is a high-level Python-only method that sends the entire buffer
# you pass or throws an exception. It does that by calling socket.send until
# everything has been sent or an error occurs.
# If you're using TCP with blocking sockets and don't want to be bothered by
# internals (this is the case for most simple network applications), use sendall.
class SpriteClient(threading.Thread):

    def __init__(self, gl_, host_, port_):
        """
            :param gl_  : global variables class
            :param host_: ip address (string)
            :param port_: port to connect to (integer)
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
                print('\n[-]Server is not responding...attempt # %s/%s ' % (retry, self.gl.RETRY))
                retry += 1
                time.sleep(2)
                self.gl.CONNECTION = False
                self.gl.SPRITECLIENT_STOP = True
        if self.gl.CONNECTION:
            print('\n[+]Connected to server %s port %s...' % (host_, port_))
        else:
            print('\n[+]Server is not responding after 5 attempts...')

    def run(self):

        old_data = Broadcast.msg

        while not self.gl.P2CS_STOP and not self.gl.SPRITECLIENT_STOP:

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
                                                               compression_level=lz4.frame.COMPRESSIONLEVEL_MAX)  #_MINHC)
                            # send the entire buffer
                            self.sock.sendall(compress_data)

                            # todo counting total bytes sent
                            data_received = self.sock.recv(buffer_)
                            # print('\nFrame # %s , data sent %s, data received %s '
                            #      % (FRAME, len(compress_data), len(data_received)))
                            GL.BYTES_SENT.append(len(compress_data))
                            GL.BYTES_RECEIVED.append(len(data_received))

                            old_data = data

                except (socket.error, cpickle.UnpicklingError) as error:
                    print('\n[-]sprite_client - Error @ frame: %s : %s %s' % (FRAME, error, time.ctime()))

            # 1ms delay will create large fps oscillation for
            # highest frame frame rate e.g 300fps. For 70 fps the fluctuating will be marginal
            pygame.time.wait(1)

        print("\n[+]SpriteClient - is now closed...")
        self.sock.close()


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

        while not (self.gl.P2CS_STOP or self.gl.SPRITESERVER_STOP):
            # try:

            while not (self.gl.P2CS_STOP or self.gl.SPRITESERVER_STOP):

                # Receive data from the socket, writing it into buffer instead
                # of creating a new string. The return value is a pair (nbytes, address)
                # where nbytes is the number of bytes received and address is the address
                # of the socket sending the data.

                try:
                    nbytes, sender = connection.recvfrom_into(self.view, self.buf)
                except socket.error as error:
                    print("\n[-]SpriteServer - Lost connection with Server...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    self.gl.SPRITESERVER_STOP
                    nbytes = 0

                buffer = self.view.tobytes()[:nbytes]

                try:
                    connection.sendall(self.view.tobytes()[:nbytes])
                except ConnectionResetError as error:
                    print("\n[-]SpriteServer - Lost connection with Server...")
                    print("\n[-]SpriteServer - ERROR %s %s" % (error, time.ctime()))
                    self.gl.SPRITESERVER_STOP

                try:
                    # Decompress the data frame
                    decompress_data = lz4.frame.decompress(buffer)
                    data = cpickle.loads(decompress_data)
                except Exception:
                    # The decompression error can also happen when
                    # the bytes stream sent is larger than the buffer size.
                    # raise RuntimeError('Problem during decompression/un-pickling')
                    print('Problem during decompression/un-pickling')
                    # self.gl.SPRITESERVER_STOP
                    data = None

                modified_surface = {}
                self.gl.NetGroupAll = LayeredUpdatesModified()

                if isinstance(data, list):

                    for sprite_ in data:

                        if not hasattr(sprite_, 'event'):

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
                                        surf1 = eval(spr.surface)  # load parent surface
                                        # Blend parent surface with child
                                        surf1.blit(sprite_.image,
                                                   sprite_.blend_pos, special_flags=sprite_._blend)
                                        # parent sprite is updated ** (see above)
                                        spr.image = surf1
                                        if sprite_ in data:
                                            data.remove(sprite_)
                            else:
                                continue

                        else:
                            # ** BELOW CODE ONLY FOR CLIENTS
                            if sprite_.event.isSet():
                                self.gl.NEXT_FRAME.set()
                            else:
                                self.gl.NEXT_FRAME.clear()

                            if sprite_ in data:
                                data.remove(sprite_)

                    # Goes through the list of sprites and apply transformation(s)
                    for sprite_ in data:

                        self.gl.REMOTE_FRAME = sprite_.frame

                        if not hasattr(sprite_, 'event'):

                            try:
                                sprite_.image = eval(sprite_.surface)  # load surface
                            except NameError:
                                raise RuntimeError("\n[-]SpriteServer - Surface "
                                                   "'%s' does not exist " % sprite_.surface)

                            if isinstance(sprite_.image, list):
                                sprite_.image = sprite_.image[sprite_.index % len(sprite_.image) - 1]

                            if sprite_.surface == 'BLUE_LASER' and sprite_.index == 0:
                                self.gl.MIXER.stop_object(id(BLUE_LASER_SOUND))
                                self.gl.MIXER.play(sound_=BLUE_LASER_SOUND, loop_=False, priority_=0,
                                                   volume_=1.0, fade_out_ms=0, panning_=True,
                                                   name_='BLUE_LASER_SOUND', x_=sprite_.rect.centerx,
                                                   object_id_=id(BLUE_LASER_SOUND),
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
                buffer = b''
                # pygame.time.wait(1)
                break

            pygame.time.wait(1)
            """
            except Exception as error:
                print('\n[-]SpriteServer - Error @ frame: %s : %s %s' % (FRAME, error, time.ctime()))

            finally:
                # Clean up the connection
                if 'connection' in globals() and connection is not None:
                    connection.close()
            """
        print('\n[-]SpriteServer is now terminated...')


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
    # CLIENT = '192.168.1.106'

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

    BACK = pygame.image.load('Assets\\BACK1.png').convert()

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
    vector1 = pygame.math.Vector2(x=0, y=0)
    vector2 = pygame.math.Vector2(x=0, y=-1024)

    CL1 = pygame.image.load('Assets\\cloud22_.png') \
        .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)
    CL1 = pygame.transform.smoothscale(CL1, (800, 800))
    CL2 = pygame.image.load('Assets\\cloud11_.png') \
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

    EXPLOSION1 = spread_sheet_fs8('Assets\\explosion1_.png', 256, 7, 5)

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

    GRID = pygame.image.load('Assets\\grid2.png').convert()
    GRID = pygame.transform.smoothscale(GRID, (64, 64))

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
        GL.SPRITECLIENT_STOP = True
        GL.SPRITESERVER_STOP = True
        force_quit(CLIENT, 1024)

    # *********************************************************************

    GL.All = LayeredUpdatesModified()
    PLAYERS = pygame.sprite.Group()
    SHOTS = pygame.sprite.Group()

    Player2.image = P2_SURFACE
    Player2.containers = PLAYERS, GL.All
    Shot.images = RED_LASER
    Shot.containers = SHOTS, GL.All
    Explosion.containers = GL.All
    AfterBurner.containers = GL.All

    SHOOTING_STAR = pygame.image.load('Assets\\shooting_star.png') \
        .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)
    SHOOTING_STAR = pygame.transform.scale(SHOOTING_STAR, (25, 80))

    P2 = Player2(GL, 15, (screen.get_size()[0] // 2, screen.get_size()[1] // 2))

    GL.TIME_PASSED_SECONDS = 0

    clock = pygame.time.Clock()
    GL.STOP_GAME = False

    FRAME = 0

    GL.MIXER = SoundControl(20)

    while not GL.STOP_GAME:

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

        # threading event lock with a timeout of 2ms
        # The game loop wait for a signal from the master game loop.
        # If nothing is received in less than 2ms, the lock is release and the scene is display as normal.
        # A non blocking lock guarantee a smoother animation and provides a good synchronisation when
        # all the network messages are received.
        # ** Only client(s) own a lock
        GL.NEXT_FRAME.wait(0.001)  # 0.002)
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
            GL.NetGroupAll.draw(screen)

        GL.All.draw(screen)

        # Authorize Player 2 to send data to the server
        # Allowing to send only one set of data every frame.
        # The clear method is used in the class SpriteClient
        # right after receiving the Event
        GL.SIGNAL.set()

        # Update the sound Controller
        GL.MIXER.update()

        GL.TIME_PASSED_SECONDS = clock.tick(70)
        GL.SPEED_FACTOR = GL.TIME_PASSED_SECONDS / 1000
        pygame.display.flip()

        Broadcast.empty()

        FRAME += 1
        GL.FRAME = FRAME
        GL.FPS.append(clock.get_fps())

    GL.SPRITECLIENT_STOP = True
    GL.SPRITESERVER_STOP = True
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
