
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


pygame.init()
pygame.mixer.init()


BLUE_LASER_SOUND = pygame.mixer.Sound('Assets\\heavylaser1.ogg')
RED_LASER_SOUND = pygame.mixer.Sound('Assets\\fire_bolt_micro.ogg')
EXPLOSION_SOUND = pygame.mixer.Sound('Assets\\explosion_11.ogg')
IMPACT = pygame.mixer.Sound('Assets\\Impact.ogg')
IMPACT1 = pygame.mixer.Sound('Assets\\boom1.ogg')


if __name__ == '__main__':
    ...
