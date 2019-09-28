import pygame
import numpy


def scroll_array(array: numpy.ndarray, dx: int=0, dy: int=0) -> numpy.ndarray:
    """
    Scroll pixels inside a 3d array (RGB values)  
    Use dy to scroll up or down (move the image of dy pixels)
    :param dx: int, Use dx for scrolling right or left (move the image of dx pixels)
    :param dy: int, Use dy to scroll up or down (move the image of dy pixels)
    :param array: numpy.ndarray, return a numpy 3d array (RGB values).
    This will only work on Surfaces that have 24-bit or 32-bit formats.
    Lower pixel formats cannot be referenced with this method
    """
    if not isinstance(dx, int):
        raise TypeError('dx, an integer is required (got type %s)' % type(dx))
    if not isinstance(dy, int):
        raise TypeError('dy, an integer is required (got type %s)' % type(dy))
    if not isinstance(array, numpy.ndarray):
        raise TypeError('array, a numpy.ndarray is required (got type %s)' % type(array))
    if dx != 0:
        array = numpy.roll(array, dx, axis=1)
    if dy != 0:
        array = numpy.roll(array, dy, axis=0)
    return array


def scroll_surface(array: numpy.ndarray, dx: int=0, dy: int=0) -> tuple:
    """
    Scroll pixels inside a 3d array (RGB values) and return a tuple (pygame surface, 3d array).
    Use dy to scroll up or down (move the image of dy pixels)
    :param dx: int, Use dx for scrolling right or left (move the image of dx pixels)
    :param dy: int, Use dy to scroll up or down (move the image of dy pixels)
    :param array: numpy.ndarray such as pygame.surfarray.pixels3d(texture).
    This will only work on Surfaces that have 24-bit or 32-bit formats.
    Lower pixel formats cannot be referenced using this method.
    """
    if not isinstance(dx, int):
        raise TypeError('dx, an integer is required (got type %s)' % type(dx))
    if not isinstance(dy, int):
        raise TypeError('dy, an integer is required (got type %s)' % type(dy))
    if not isinstance(array, numpy.ndarray):
        raise TypeError('array, a numpy.ndarray is required (got type %s)' % type(array))
    if dx != 0:
        array = numpy.roll(array, dx, axis=1)
    if dy != 0:
        array = numpy.roll(array, dy, axis=0)
    return pygame.surfarray.make_surface(array), array


if __name__ == '__main__':
    SCREENRECT = pygame.Rect(0, 0, 800, 800)
    pygame.init()
    screen = pygame.display.set_mode((SCREENRECT.w, SCREENRECT.h))

    # Arrow right
    arrow_right = pygame.image.load('Assets\\chevrons.png').convert()
    w, h = arrow_right.get_size()
    arrow_right = pygame.transform.smoothscale(arrow_right, (120, 60)) 
    arrow_right.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    arrow_right_array = pygame.surfarray.pixels3d(arrow_right)

    # Arrow left
    arrow_left_array = arrow_right_array[::-1]

    # Arrow forward
    arrow_up = pygame.transform.rotozoom(arrow_right, 90, 1)
    arrow_up_array = pygame.surfarray.pixels3d(arrow_up)

    # Arrow down
    arrow_down = pygame.transform.rotozoom(arrow_right, -90, 1)
    arrow_down_array = pygame.surfarray.pixels3d(arrow_down)
    
    speed = 5
    
    GAME = True

    group = pygame.sprite.Group()
    clock = pygame.time.Clock()
    
    while GAME:

        pygame.event.pump()
        screen.fill((10, 10, 10, 0))
        group.draw(screen)
        group.update()

        # scroll to the right
        arrow_right, arrow_right_array = scroll_surface(arrow_right_array, 0, 5)   
        screen.blit(arrow_right, (200, 100), special_flags=pygame.BLEND_RGB_ADD)

        # scroll left
        arrow_left, arrow_left_array = scroll_surface(arrow_left_array, 0, -5)
        screen.blit(arrow_left, (200, 100 + arrow_right.get_height()), special_flags=pygame.BLEND_RGB_ADD)

        # Arrow forward
        arrow_up, arrow_up_array = scroll_surface(arrow_up_array, -5, 0)
        screen.blit(arrow_up, (200, 100 + arrow_right.get_height() * 2), special_flags=pygame.BLEND_RGB_ADD)

        # Arrow down
        arrow_down, arrow_down_array = scroll_surface(arrow_down_array, 5, 0)
        screen.blit(arrow_down, (200, 100 + arrow_right.get_height() * 4), special_flags=pygame.BLEND_RGB_ADD)
        
        pygame.display.flip()
        print(clock.get_fps())
        clock.tick(1000)
