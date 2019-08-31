import threading
import pygame
from LayerModifiedClass import LayeredUpdatesModified


class GL(object):

    STOP_GAME = False                       # Self explanatory
    TIME_PASSED_SECONDS = 0                 # Last clock tick in ms
    KEYS = None                             # Contains all pygame key events
    SPEED_FACTOR = 0                        # Speed variable for aircraft
    SCREEN = None

    All = LayeredUpdatesModified()          # containing all sprites
    NetGroupAll = LayeredUpdatesModified()  # Layer update pygame group capable of blit sprites
    ASTEROID = pygame.sprite.Group()
    PLAYER_SHOTS = pygame.sprite.Group()
    TRANSPORT = pygame.sprite.GroupSingle()  # Not used by Player 2

    P1CS_STOP = False                       # Variable stop player 1 game loop
    P2CS_STOP = False                       # Variable stop player 2 game loop

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
    SPRITE_SERVER_STOP = False               # STOP the SpriteServer thread
    SPRITE_CLIENT_STOP = False               # STOP the SpriteClient thread
    RETRY = 100                              # Attempts before terminating network threads
    BUFFER = 2048

    REMOTE_FRAME = 0                        # Server frame number (Master frame number)
    INSPECT = set()
    XTRANS_SCALE = {}
    XTRANS_ROTATION = {}

    P1 = pygame.sprite.GroupSingle()        # Player 1 instance
    P2 = pygame.sprite.GroupSingle()        # Player 2 instance
    P1_SCORE = None                         # Player 1 score instance
    P2_SCORE = None                         # Player 2 score instance

    CLIENTS = {}                            # contains all the client connected to the server

    buffers = {}                            # buffer containing images already processed. 

    def __init__(self):
        ...

    def __copy__(self):
        return GL()


if __name__ == '__main__':
    a = GL()
    print(hasattr(a, 'BUFFER'), a.BUFFER)
    b = GL().__copy__()
    b.RETRY = 10
