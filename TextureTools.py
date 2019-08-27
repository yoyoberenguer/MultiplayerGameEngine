import numpy
import pygame


__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


def load_per_pixel(file: str) -> pygame.Surface:
    """ Not compatible with 8 bit depth color surface"""

    assert isinstance(file, str), 'Expecting path for argument <file> got %s: ' % type(file)
    try:
        surface_ = pygame.image.load(file)
        buffer_ = surface_.get_view('2')
        w, h = surface_.get_size()
        source_array = numpy.frombuffer(buffer_, dtype=numpy.uint8).reshape((w, h, 4))

        surface_ = pygame.image.frombuffer(source_array.copy(order='C'),
                                           (tuple(source_array.shape[:2])), 'RGBA').convert_alpha()
        return surface_
    except pygame.error:
        raise SystemExit('\n[-] Error : Could not load image %s %s ' % (file, pygame.get_error()))


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


def spread_sheet_per_pixel_fs8(file: str, chunk: int, rows_: int, columns_: int, tweak_: bool = False, *args) -> list:

    assert isinstance(file, str), 'Expecting string for argument file got %s: ' % type(file)
    assert isinstance(chunk, int), 'Expecting int for argument number got %s: ' % type(chunk)
    assert isinstance(rows_, int) and isinstance(columns_, int), 'Expecting int for argument rows_ and columns_ ' \
                                                                 'got %s, %s ' % (type(rows_), type(columns_))
    image_ = pygame.image.load(file)
    try:
        surface_ = pygame.surfarray.pixels3d(image_)
        alpha_ = pygame.surfarray.pixels_alpha(image_)
    except Exception:
        surface_ = pygame.surfarray.array3d(image_)
        alpha_ = pygame.surfarray.array_alpha(image_)

    # Make a surface containing RGB and alpha values
    array = make_array(surface_, alpha_)
    animation = []
    # split sprite-sheet into many sprites
    for rows in range(rows_):
        for columns in range(columns_):
            if tweak_:
                chunkx = args[0]
                chunky = args[1]
                array1 = array[columns * chunkx:(columns + 1) * chunkx, rows * chunky:(rows + 1) * chunky, :]
            else:
                array1 = array[columns * chunk:(columns + 1) * chunk, rows * chunk:(rows + 1) * chunk, :]
            surface_ = make_surface(array1)
            surface__ = pygame.Surface((array1.shape[0], array1.shape[1]),
                                       depth=32, flags=(pygame.SWSURFACE | pygame.RLEACCEL | pygame.SRCALPHA))
            surface__.blit(surface_, (0, 0))
            animation.append(surface__)
    return animation

def make_array(rgb_array_: numpy.ndarray, alpha_: numpy.ndarray) -> numpy.ndarray:
    """
    This function is used for 24-32 bit pygame surface with pixel alphas transparency layer
    make_array(RGB array, alpha array) -> RGBA array
    Return a 3D numpy (numpy.uint8) array representing (R, G, B, A)
    values of all pixels in a pygame surface.
    :param rgb_array_: 3D array that directly references the pixel values in a Surface.
                       Only work on Surfaces that have 24-bit or 32-bit formats.
    :param alpha_:     2D array that directly references the alpha values (degree of transparency) in a Surface.
                       alpha_ is created from a 32-bit Surfaces with a per-pixel alpha value.
    :return:           Return a numpy 3D array (numpy.uint8) storing a transparency value for every pixel
                       This allow the most precise transparency effects, but it is also the slowest.
                       Per pixel alphas cannot be mixed with pygame method set_colorkey (this will have
                       no effect).
    """
    return numpy.dstack((rgb_array_, alpha_))


def make_surface(rgba_array: numpy.ndarray) -> pygame.Surface:
    """
    This function is used for 24-32 bit pygame surface with pixel alphas transparency layer
    make_surface(RGBA array) -> Surface
    Argument rgba_array is a 3d numpy array like (width, height, RGBA)
    This method create a 32 bit pygame surface that combines RGB values and alpha layer.
    :param rgba_array: 3D numpy array created with the method surface.make_array.
                       Combine RGB values and alpha values.
    :return:           Return a pixels alpha surface.This surface contains a transparency value
                       for each pixels.
    """
    return pygame.image.frombuffer((rgba_array.transpose([1, 0, 2])).copy(order='C').astype(numpy.uint8),
                                   (rgba_array.shape[:2][0], rgba_array.shape[:2][1]), 'RGBA').convert_alpha()


def blend_texture(surface_, interval_, color_) -> pygame.Surface:
    """
    Compatible with 24-32 bit pixel alphas texture.
    Blend two colors together to produce a third color.
    Alpha channel of the source image will be transfer to the destination surface (no alteration
    of the alpha channel)
    :param surface_: pygame surface
    :param interval_: number of steps or intervals, int value
    :param color_: Destination color. Can be a pygame.Color or a tuple
    :return: return a pygame.surface supporting per-pixels transparency only if the surface passed
                    as an argument has been created with convert_alpha() method.
                    Pixel transparency of the source array will be unchanged.
    """

    source_array = pygame.surfarray.pixels3d(surface_)
    alpha_channel = pygame.surfarray.pixels_alpha(surface_)
    diff = (numpy.full_like(source_array.shape, color_[:3]) - source_array) * interval_
    rgba_array = numpy.dstack((numpy.add(source_array, diff), alpha_channel)).astype(dtype=numpy.uint8)
    return pygame.image.frombuffer(rgba_array.transpose([1, 0, 2]).copy(order='C').astype(numpy.uint8),
                                   (rgba_array.shape[:2][0], rgba_array.shape[:2][1]), 'RGBA').convert_alpha()


# Add transparency value to all pixels including black pixels
def add_transparency_all(rgb_array: numpy.ndarray, alpha_: numpy.ndarray, value: int) -> pygame.Surface:
    """
    Increase transparency of a surface
    This method is equivalent to pygame.Surface.set_alpha() but conserve the per-pixel properties of a texture
    All pixels will be update with a new transparency value.
    If you need to increase transparency on visible pixels only, prefer the method add_transparency instead.
    :param rgb_array:
    :param alpha_:
    :param value:
    :return:
    """
    # if not 0 <= value <= 255:
    #     raise ERROR('\n[-] invalid value for argument value, should be 0 < value <=255 got %s '
    #                 % value)
    # method 1
    """
    mask = (alpha_ >= value)
    mask_zero = (alpha_ < value)
    alpha_[:][mask_zero] = 0
    alpha_[:][mask] -= value
    return make_surface(make_array(rgb_array, alpha_.astype(numpy.uint8)))
    """
    # method 2
    alpha_ = alpha_.astype(numpy.int16)
    alpha_ -= value
    numpy.putmask(alpha_, alpha_ < 0, 0)

    return make_surface(make_array(rgb_array, alpha_.astype(numpy.uint8))).convert_alpha()