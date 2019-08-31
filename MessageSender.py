import pygame
import threading
import socket
from NetworkBroadcast import Broadcast
import time
import _pickle as cpickle
import lz4.frame
from GLOBAL import GL

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


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

    def __init__(self, gl_, host_: str, port_: int):
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
        self.sock = None
        retry = 1
        self.gl.CONNECTION = False
        self.gl.SPRITE_CLIENT_STOP = False

        for r in range(self.gl.RETRY):
            try:

                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.gl.CONNECTION = True
                self.gl.SPRITE_CLIENT_STOP = False
                break

            except:
                print('\n[+]Waiting for client(s) to connect...attempt # %s/%s ' % (retry, self.gl.RETRY))
                retry += 1
                time.sleep(2)
                self.gl.CONNECTION = False
                self.gl.SPRITE_CLIENT_STOP = True

        if self.gl.CONNECTION:

            print('\n[+]Player 2 is connected from %s port %s...' % (self.host, self.port))
            self.gl.CLIENTS.update({self.host: self.port})

        else:
            print('\n[+]Player 2 is not connected after 5 attempts...')

        # self.gl.CLIENTS.update({'127.0.0.80': 1025})

    def run(self):

        old_data = Broadcast.MessageQueue

        # todo self.gl.P1CS_STOP is for MirroredPlayer1Class what about MirroredPlayer2Class
        while not self.gl.P1CS_STOP and not self.gl.SPRITE_CLIENT_STOP:

            # check for the signal.
            # if signal is set, sending data to multi-players
            if self.gl.SIGNAL.isSet():

                self.gl.SIGNAL.clear()

                buffer_ = self.gl.BUFFER
                # todo check if data are different
                data = Broadcast.MessageQueue
                try:
                    if data is not None and len(data) > 0:
                        pickle_data = cpickle.dumps(data)
                        # The compress() function reads the input data and compresses it and returns a LZ4 frame.
                        # A frame consists of a header, and a sequence of blocks of compressed data, and a frame
                        # end marker (and optionally a checksum of the uncompressed data). The decompress() function
                        # takes a full LZ4 frame, decompresses it (and optionally verifies the uncompressed data
                        # against the stored checksum), and returns the uncompressed data.
                        compress_data = lz4.frame.compress(pickle_data,
                                                           compression_level=lz4.frame.COMPRESSIONLEVEL_MAX)
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
                    print('\n[-]SpriteClient - ERROR @ frame: %s : %s %s' % (self.gl.FRAME, error, time.ctime()))

            # 1ms delay will create large fps oscillation for
            # frame rate e.g 300fps. For 70 fps the fluctuating will be marginal
            pygame.time.wait(1)

        print("\n[+]SpriteClient - is now closed...")
        self.sock.close()
