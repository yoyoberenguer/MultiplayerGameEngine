import numpy
import pygame
import math
import random



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


def spread_sheet_per_pixel(file_: str, chunk: int, rows_: int, columns_: int) -> list:
    """ Not to be used with asymetric surface """
    surface = pygame.image.load(file_)
    buffer_ = surface.get_view('2')

    w, h = surface.get_size()
    source_array = numpy.frombuffer(buffer_, dtype=numpy.uint8).reshape((h, w, 4))
    animation = []

    for rows in range(rows_):
        for columns in range(columns_):

            array1 = source_array[rows * chunk:(rows + 1) * chunk,
                         columns * chunk:(columns + 1) * chunk, :]

            # surface_ = pygame.image.frombuffer(array1.copy(order='C'),
            #                      (tuple(array1.shape[:2])), 'RGBA').convert_alpha()

            surface_ = pygame.image.frombuffer(numpy.ascontiguousarray(array1),
                                  (array1.shape[0], array1.shape[1]), 'RGBA')

            animation.append(surface_.convert(32, pygame.SWSURFACE | pygame.RLEACCEL | pygame.SRCALPHA))

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



def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
    # Cannot get here



def shift_hue(r, g, b, shift_):
    """ hue shifting algorithm
        Transform an RGB color into its hsv equivalent and rotate color with shift_ parameter
        then transform hsv back to RGB."""
    # The HSVA components are in the ranges H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100].
    h, s, v, a = pygame.Color(int(r), int(g), int(b)).hsva
    # shift the hue and revert back to rgb
    rgb_color = colorsys.hsv_to_rgb((h + shift_) * 0.002777, s * 0.01, v * 0.01) # (1/360, 1/100, 1/100)
    return rgb_color[0] * 255, rgb_color[1] * 255, rgb_color[2] * 255


def hue_surface(surface_: pygame.Surface, shift_: int):
    """
    Only surface with 32 - 24 bits depth color are compatible.
    Change colors from a given pygame surface and returns a surface with
    color values shifted.

    :param surface_: pygame.Surface to use for shifting colors (hue)
    :param shift_:  value 0 to 360 degrees
    :return: returns a pygame.surface with colors values shifted
    """
    rgb_array = pygame.surfarray.pixels3d(surface_)
    alpha_array = pygame.surfarray.pixels_alpha(surface_)

    vectorize_ = numpy.vectorize(shift_hue)
    source_array_ = vectorize_(rgb_array[:, :, 0], rgb_array[:, :, 1], rgb_array[:, :, 2], shift_)

    source_array_ = numpy.array(source_array_).transpose(1, 2, 0)
    #array = make_array(source_array_, alpha_array)
    #return make_surface(array).convert_alpha()
    array = numpy.dstack((source_array_, alpha_array))
    return pygame.image.frombuffer((array.transpose(1, 0, 2)).copy(order='C').astype(numpy.uint8),
                                   (array.shape[:2][0], array.shape[:2][1]), 'RGBA').convert_alpha()


def shift_lightness(r, g, b, shift_):
    """ image lightness shifting algorithm
        Transform an RGB color into hsl (hue, saturation, lightness) values and adjust
        pixels intensity
        then transform hsv back to RGB."""
    h, s, l, a = pygame.Color(int(r), int(g), int(b)).hsla
    # shift the hue
    h, s, l = (
                h * 0.002777,               # H Hue
                s * 0.01 ,                  # S Saturation
                min((l + shift_) * 0.01, 1) # L lightness, cap the value to 1
               )  # (1/360, 1/100, 1/100)
    rgb_color = colorsys.hsv_to_rgb(h, s, l)
    return rgb_color[0] * 255, rgb_color[1] * 255, rgb_color[2] * 255


def lightness(surface_: pygame.Surface, shift_: int):
    """
    Only surface with 32 - 24 bits depth color are compatible.
    Change an image intensity using hsl method

    :param surface_: pygame.Surface
    :param shift_:  value 0 to 200 representing the image intensity
    :return: returns a pygame.surface with a different intensity
    """
    rgb_array = pygame.surfarray.pixels3d(surface_)
    alpha_array = pygame.surfarray.pixels_alpha(surface_)

    vectorize_ = numpy.vectorize(shift_lightness)
    source_array_ = vectorize_(rgb_array[:, :, 0], rgb_array[:, :, 1], rgb_array[:, :, 2], shift_)

    source_array_ = numpy.array(source_array_).transpose(1, 2, 0)
    array = make_array(source_array_, alpha_array)
    return make_surface(array)


def smi_gradient(value, index_):
    """ Create a gradient array and get a specific gradient value from it """

    diff_ = numpy.array((0, 255, 0) - numpy.array((255, 0, 0)))
    row = numpy.arange(value, dtype='float') / value
    row = numpy.repeat(row[:, numpy.newaxis], [3], 1)
    diff_ = numpy.repeat(diff_[numpy.newaxis, :], [value], 0)
    row = numpy.add(numpy.array((255, 0, 0), numpy.float), numpy.array((diff_ * row), numpy.float),
                    dtype=numpy.float)
    return row[index_ % value]


# Slow algorithm converting color surface into greyscale
# iterate over all pixels from the surface with the method
# get_pixel, set_pixel
# This method determine the greyscale from the RGB values.
# Alpha channel (alpha transparency and per-pixels method will be ignored.
# The final result is a surface containing all pixels represented
# by a shade of gray colors. The final surface may differ from the original
# surface (especially for surface containing per-pixel transparency).
# Pixels around object edges tend to be slightly more transparent, used for
# anti-aliases effect but also to soften the image around the edges
# Using this method will cancel those effect and will show every pixels.
# Compatible with 8, 24, 32 bits depth surfaces with or without alpha
# transparency.
def greyscale_pixels(image):
    w, h = image.get_size()
    new = pygame.Surface((w, h))
    for i in range(w):
        for j in range(h):
          red, green, blue, alpha = image.get_at((i, j))
          grey= int((red + green + blue) * 0.33)
          new.set_at((i, j),(grey, grey, grey))

    # Use the pygame method convert_alpha() in order to restore
    # the per-pixel transparency, otherwise use set_colorkey() or set_alpha()
    # methods to restore alpha transparency before blit.
    return new


# Decompose a surface in multiple array representing
# red, green, blue colors and process the grey values.
# This algorithm transfer the alpha channel in
# the final result.
# This method is compatible only for 32 bit surface containing
# an alpha channel transparency.
def greyscale_rgb(image:pygame.Surface):
  alpha = pygame.surfarray.pixels_alpha(image)
  red = pygame.surfarray.pixels_red(image) /3
  green = pygame.surfarray.pixels_green(image) /3
  blue = pygame.surfarray.pixels_blue(image) /3
  grey = numpy.add(red,green,blue)
  grey = numpy.repeat(grey[:,:, numpy.newaxis], 3, 2)
  array = make_array(grey, alpha)
  return make_surface(array)


# Use the vectorize method to change a colored
# surface into a greyscale surface
# This algorithm transfer the alpha channel in
# the final result.
# This method is compatible only for 32 bit surface containing
# an alpha channel transparency.
def grayscale(red, green, blue):
    gray = int(red * 0.299 + green * 0.587 + blue * 0.114)
    return gray, gray, gray

def greyscale_vectorize(image:pygame.Surface):
    rgb_array = pygame.surfarray.pixels3d(image)
    alpha_array = pygame.surfarray.pixels_alpha(image)

    vectorize_ = numpy.vectorize(grayscale)
    source_array_ = vectorize_(rgb_array[:, :, 0], rgb_array[:, :, 1], rgb_array[:, :, 2])

    source_array_ = numpy.array(source_array_).transpose(1, 2, 0)
    array = make_array(source_array_, alpha_array)
    return make_surface(array)


# Fastest algorithm for converting a
# colored surface into greyscale
# This algorithm transfer the alpha channel in
# the final result.
# This method is compatible only for 32 bit surface containing
# an alpha channel transparency.
def fast_greyscale(image):
    array = pygame.surfarray.pixels3d(image)
    alpha = pygame.surfarray.pixels_alpha(image)
    grey = (array[:,:, 0] * 0.299 + array[:,:, 1] * 0.587 + array[:, :, 2] * 0.114)
    array[:, :, 0], array[:, :, 1], array[:, :, 2] = grey, grey, grey
    return make_surface(make_array(array, alpha))

# Darker a given pygame surface (shadow effect)
# The surface must be 32bit with transparency layer
def shadow(image):
    assert image.get_bitsize() is 32, \
        'Surface pixel format is not 32 bit, got %s ' % image.get_bitsize()
    array = pygame.surfarray.pixels3d(image)
    alpha = pygame.surfarray.pixels_alpha(image)
    grey = (array[:,:, 0] + array[:,:, 1] + array[:, :, 2]) * 0.01
    array[:, :, 0], array[:, :, 1], array[:, :, 2] = grey, grey, grey
    return make_surface(make_array(array, alpha))

# Shadow effect.
# darker a pygame 24 bit surface without alpha per pixel transparency
def shadow_24bit(image):
    assert image.get_bitsize() is 24, \
        'Surface pixel format is not 24 bit, got %s ' % image.get_bitsize()
    array = pygame.surfarray.pixels3d(image)
    # alpha = pygame.surfarray.array_colorkey(image)
    grey = (array[:,:, 0] + array[:,:, 1] + array[:, :, 2]) * 0.01
    array[:, :, 0], array[:, :, 1], array[:, :, 2] = grey, grey, grey
    return pygame.surfarray.make_surface(array)

# Invert a 32 bit surface colors
def invert_surface_32bit(image):
    assert image.get_bitsize() is 32, \
        'Surface pixel format is not 32 bit, got %s ' % image.get_bitsize()
    array = pygame.surfarray.pixels3d(image)
    alpha = pygame.surfarray.pixels_alpha(image)
    array = numpy.invert(numpy.array(array, dtype=numpy.uint8))
    return make_surface(make_array(array, alpha))

# Invert a 24 bit surface colors
def invert_surface_24bit(image):
    assert image.get_bitsize() is 24, \
        'Surface pixel format is not 24 bit, got %s ' % image.get_bitsize()
    array = pygame.surfarray.pixels3d(image)
    array = numpy.invert(numpy.array(array, dtype=numpy.uint8))
    return pygame.surfarray.make_surface(array)


# Horizontal glitch effect
def hge(texture_, rad1_, frequency_, amplitude_):
    w, h = texture_.get_size()
    w2, h2 = w >> 1, h >> 1
    vector = pygame.math.Vector2(x=0, y=-1)
    position = pygame.math.Vector2(x=w >> 1, y=h - 1)
    rad = math.pi / 180
    angle, angle1 = 0, 0
    glitch = pygame.Surface((w, h), pygame.SRCALPHA)
    glitch.lock()
    while position.y > 0:
        for x in range(-w2 + amplitude_, w2 - amplitude_):
            glitch.set_at((int(position.x + x), int(position.y)),
                          texture_.get_at((int(position.x + x + math.cos(angle) * amplitude_),
                                           int(position.y))))
        position += vector
        angle1 += frequency_ * rad
        angle += rad1_ * rad + random.uniform(-angle1, angle1)
    glitch.unlock()
    return glitch


# Vertical glitch effect
def vge(texture_, rad1_, frequency_, amplitude_):
    w, h = texture_.get_size()
    w2, h2 = w >> 1, h >> 1
    vector = pygame.math.Vector2(x=0, y=-1)
    position = pygame.math.Vector2(x=w >> 1, y=h - 1)
    rad = math.pi / 180
    angle, angle1 = 0, 0
    glitch = pygame.Surface((w, h), pygame.SRCALPHA)
    glitch.lock()
    while position.y > amplitude_:
        for x in range(-w2 + amplitude_, w2 - amplitude_):
            glitch.set_at((int(position.x + x), int(position.y)),
                          texture_.get_at((int(position.x + x),
                                           int(position.y - abs(math.sin(angle) * amplitude_)))))

        position += vector
        angle1 += frequency_ * rad
        angle += rad1_ * rad + random.uniform(-angle1, angle1)
    glitch.unlock()
    return glitch

# horizontal glitch effect with blur
def hge_blur(texture_, rad1_, frequency_, amplitude_):
    w, h = texture_.get_size()
    w2, h2 = w >> 1, h >> 1
    vector = pygame.math.Vector2(x=0, y=-1)
    position = pygame.math.Vector2(x=w >> 1, y=h - 1)
    rad = math.pi / 180
    angle = 0
    angle1 = 0
    glitch = pygame.Surface((w, h), pygame.SRCALPHA)
    # Kernel 5x5
    kernel_size = 7
    kernel_half = 3
    glitch.lock()
    while position.y > 5:
        for x in range(-w2 + amplitude_, w2 - amplitude_):
            glitch.set_at((int(position.x + x), int(position.y)),
                                pygame.transform.average_color(texture_,
                                                               (int(position.x + x + math.cos(
                                                                   angle) * amplitude_ - kernel_half),
                                                                int(position.y - kernel_half),
                                                                kernel_size, kernel_size)))
        position += vector
        angle1 += frequency_ * rad
        angle += rad1_ * rad + random.uniform(-angle1, angle1)
    glitch.unlock()
    return glitch

# vertical glitch effect with blur
def vge_blur(texture_, rad1_, frequency_, amplitude_):
    w, h = texture_.get_size()
    w2, h2 = w >> 1, h >> 1
    vector = pygame.math.Vector2(x=0, y=-1)
    position = pygame.math.Vector2(x=w >> 1, y=h - 1)
    rad = math.pi / 180
    angle = 0
    angle1 = 0
    glitch = pygame.Surface((w, h), pygame.SRCALPHA)
    # Kernel 5x5
    kernel_size = 7
    kernel_half = 3
    glitch.lock()
    while position.y > 5:
        for x in range(-w2 + amplitude_, w2 - amplitude_):
            glitch.set_at((int(position.x + x), int(position.y)),
                                pygame.transform.average_color(texture_,
                                                               (int(position.x + x - kernel_half),
                                                                int(position.y - kernel_half + abs(
                                                                    math.sin(angle)) * amplitude_),
                                                                kernel_size, kernel_size)))

        position += vector
        angle1 += frequency_ * rad
        angle += rad1_ * rad + random.uniform(-angle1, angle1)
    glitch.unlock()
    return glitch


# Wave algorithm both direction x, y
def wave_xy(texture_, rad1_, amplitude_):
    w, h = texture_.get_size()
    xblocks = range(0, w, amplitude_)
    yblocks = range(0, h, amplitude_)
    glitch = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in xblocks:
        xpos = (x + (math.sin(rad1_ + x * 1 / (amplitude_ ** 2)) * amplitude_)) + amplitude_
        for y in yblocks:
            ypos = (y + (math.sin(rad1_ + y * 1 / (amplitude_ ** 2)) * amplitude_)) + amplitude_
            glitch.blit(texture_, (0 + x, 0 + y), (xpos, ypos, amplitude_, amplitude_))

    return glitch.convert_alpha()


# Wave algorithm direction y
def wave_y(texture_, rad1_, amplitude_):
    w, h = texture_.get_size()
    yblocks = range(0, h, amplitude_)
    glitch = pygame.Surface((w, h), pygame.SRCALPHA)
    vector = pygame.math.Vector2(x=1, y=0)
    position = pygame.math.Vector2(x=0, y=0)
    while position.x < w:
        for y in yblocks:
            ypos = (y + (math.sin(rad1_ + y * 1 / (amplitude_ ** 2)) * amplitude_)) + amplitude_
            glitch.blit(texture_, (0 + position.x, 0 + y), (position.x, ypos, 1, amplitude_))
        position += vector

    return glitch.convert_alpha()

# Wave algorithm direction y
def wave_x(texture_, rad1_, amplitude_):
    w, h = texture_.get_size()
    yblocks = range(0, h, amplitude_)
    glitch = pygame.Surface((w, h), pygame.SRCALPHA)
    vector = pygame.math.Vector2(x=1, y=0)
    position = pygame.math.Vector2(x=0, y=0)
    while position.x < w:
        for y in yblocks:
            ypos = (y + (math.sin(rad1_ + y * 1 / (amplitude_ ** 2)) * amplitude_)) + amplitude_
            glitch.blit(texture_, (0 + position.x, 0 + y), (position.x, ypos, amplitude_, amplitude_))
        position += vector

    return glitch.convert_alpha()


def fish_eye(image):
    """ Fish eye algorithm """
    w, h = image.get_size()
    w2 = w / 2
    h2 = h / 2
    image_copy = pygame.Surface((w, h), flags=pygame.RLEACCEL).convert()
    for y in range(h):
        # Normalize every pixels along y axis
        # when y = 0 --> ny = -1
        # when y = h --> ny = +1
        ny = ((2 * y) / h) - 1
        # ny * ny pre calculated
        ny2 = ny ** 2
        for x in range(w):
            # Normalize every pixels along x axis
            # when x = 0 --> nx = -1
            # when x = w --> nx = +1
            nx = ((2 * x) / w) - 1
            # pre calculated nx * nx
            nx2 = nx ** 2

            # calculate distance from center (0, 0)
            r = math.sqrt(nx2 + ny2)

            # discard pixel if r below 0.0 or above 1.0
            if 0.0 <= r <= 1.0:

                nr = (r + 1 - math.sqrt(1 - r ** 2)) / 2
                if nr <= 1.0:

                    theta = math.atan2(ny, nx)
                    nxn = nr * math.cos(theta)
                    nyn = nr * math.sin(theta)
                    x2 = int(nxn * w2 + w2)
                    y2 = int(nyn * h2 + h2)

                    if 0 <= int(y2 * w + x2) < w * h:

                        pixel = image.get_at((x2, y2))
                        image_copy.set_at((x, y), pixel)

    return image_copy


def rotate_inplace(image: pygame.Surface, angle: int):
    w, h = image.get_size()
    w2, h2 = w / 2, h / 2
    rgb = numpy.zeros((w, h, 3))
    rgb_ = pygame.surfarray.pixels3d(image)
    for ix in range(w):
        nx = ((2 * ix) / w) - 1
        for iy in range(h):
            ny = ((2 * iy) / h) - 1
            radius = math.sqrt(nx ** 2 + ny ** 2)
            if radius > 1:
                continue
            alpha = -math.atan2(ny, nx) + angle * math.pi/180
            x = min(math.floor(math.cos(alpha) * radius * w2 + w2), w - 1)
            y = min(math.floor(math.sin(alpha) * radius * h2 + h2), h - 1)
            pixel = rgb_[ix, h - 1 - iy]
            rgb[x, y] = pixel
            # rgb[x - 1, y] = pixel

    return pygame.surfarray.make_surface(rgb)


def rotate_(image: pygame.Surface, angle: int):
    image_copy = image.copy()
    image_copy.fill((0, 0, 0, 0))
    width, height = image.get_size()
    msin = []
    mcos = []
    for i in range(360):
        rad = math.radians(-i)
        msin.append(math.sin(rad))
        mcos.append(math.cos(rad))
    hwidth = width // 2
    hheight = height // 2

    for x in range(0, width):
        for y in range(0, height):

            xt = x - hwidth
            yt = y - hheight

            sinma = msin[angle]
            cosma = mcos[angle]

            xs = round((cosma * xt - sinma * yt) + hwidth)
            ys = round((sinma * xt + cosma * yt) + hheight)

            if 0 <= xs < width and 0 <= ys < height:
                image_copy.set_at((x,y), image.get_at((xs,ys)))

    return image_copy


if __name__ == '__main__':
    ...
