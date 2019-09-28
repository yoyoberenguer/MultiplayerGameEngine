
from Textures import VOICE_MODULATION, DIALOGBOX_READOUT, NAMIKO, FRAMEBORDER

__author__ = "Yoann Berenguer"
__copyright__ = "Copyright 2007, Cobra Project"
__credits__ = ["Yoann Berenguer"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"
__status__ = "Demo"

from numpy import linspace
from random import randint

try:
    import pygame
    from pygame import freetype
except ImportError:
    print("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")
    raise SystemExit


class DialogBox(pygame.sprite.Sprite):
    """
    Create a dialog box and display text vertically.
    You can display a dialog box with a variable alpha transparency values through your game
    The dialog box can be move around adjusting its coordinates.
    e.g :
    masako = DialogBox(gl_=GL, location_=(-DIALOG.get_width(), 50),
                       speed_=15, layer_=-3, voice_=True, scan_=True)
    """
    images = None
    character = None
    containers = None
    active = False
    inventory = []
    text = []
    FONT = None
    # Voice modulation representation
    voice_modulation = None
    # random char animation in the background
    readout = None
    scan_image = None

    def __new__(cls,
                gl_,
                location_: tuple,
                speed_: int = 30,
                layer_: int = -3,
                voice_: bool=True,
                scan_: bool=True,
                start_: int=0,
                direction_: str = 'RIGHT',
                text_color_=pygame.Color(149, 119, 236, 245),
                fadein_=100,
                fadeout_=1000,
                *args, **kwargs):

        # return if an instance already exist.
        if DialogBox.active is None:
            return
        else:
            return super().__new__(cls, *args, **kwargs)

    def __init__(self,
                 gl_,                       # global variable
                 location_: tuple,          # position to display the dialog box (x, y)
                 speed_: int = 15,          # Refreshing time 15ms
                 layer_: int = 0,           # Layer to display the dialog box, choose carefully otherwise the dialog box
                                            # might be invisible (underneath other sprites)
                 voice_: bool=True,         # Create a voice sprite fx (voice modulation effect)
                 scan_: bool=True,          # scan effect (lateral scanning fx)
                 start_: int =0,            # Frame number when the frame is triggered.
                 direction_: str='RIGHT',   # moving direction
                 text_color_=pygame.Color(149, 119, 236, 245),  # Text color
                 fadein_=100,               # fade in effect starting frame
                 fadeout_=1000,             # fadout fx starting frame number
                 ):

        assert isinstance(location_, tuple), \
            'Expecting tuple for argument location_ got %s ' % type(location_)
        assert isinstance(speed_, int), \
            'Expecting int for argument speed_ got %s ' % type(speed_)
        assert isinstance(layer_, int), \
            'Expecting int for argument layer_ got %s ' % type(layer_)
        assert DialogBox.images is not None, '\n[-]DialogBox.images must be initialised.'
        assert DialogBox.voice_modulation is not None, '\n[-]DialogBox.voice_modulation must be initialised.'
        assert isinstance(DialogBox.images, pygame.Surface), '\n[-]DialogBox.images must be a pygame.Surface type.'
        # assert DialogBox.character is not None, '\n[-]DialogBox.character must be initialised.'
        assert DialogBox.containers is not None, '\n[-]DialogBox.containers must be initialised.'
        assert DialogBox.FONT is not None, '\n[-]DialogBox.Font must be initialised.'
        # assert len(DialogBox.inventory) == 0, ' \n[-]DialogBox.inventory is not empty.'
        assert DialogBox.readout is not None, '\n[-]DialogBox.readout must be initialised.'

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.gl = gl_
        self.text = DialogBox.text
        self.image = DialogBox.images.copy()
        self.image_copy = self.image.copy()
        self.location = location_
        self.rect = self.image.get_rect(topleft=(self.location[0], self.location[1]))
        self.direction = direction_
        self.text_origin = 150
        self.dt = 0
        self.index = 0
        DialogBox.active = True
        self.timing = speed_
        self.max_width, self.max_height = self.image.get_size()
        DialogBox.FONT.antialiased = True
        # Voice modulation representation index
        self.voice_module_index = 0
        self.readout_index = 0
        self.scan_background_surface = self.scan_image
        self.scan_background_surface = pygame.transform.smoothscale(
            self.scan_background_surface, (60, self.max_height - 15))
        self.scan_index = 0
        self.character = DialogBox.character
        self.voice = voice_
        self.scan = scan_
        self.count = 0
        # Frame number when the dialog box is active.
        # Nothing will happen before frame 100
        self.start_dialog_box = start_
        self.text_color = text_color_
        # dialog box start at frame self.start_dialog_box and zero indicate no delay
        self.start_moving = self.start_dialog_box + 0
        # stop moving 200 frames after self.start_dialog_box
        self.stop_moving = self.start_dialog_box + 200
        self.acceleration = linspace(12, 0, self.stop_moving)
        self.move_counter = 0
        diff = self.stop_moving - self.start_moving
        # Fade in alpha values ( 0 -> 255) for diff values
        self.fade_in = linspace(0, 255,  diff)
        self.fade_in_counter = 0
        # Fade out alpha values ( 255 -> 0) for diff values
        self.fade_out = linspace(255, 0, diff)  # fade out
        # Frame number when the fading out effect is starting
        self.start_fadeout = fadeout_
        self.start_fadein = fadein_
        self.fade_out_counter = 0

        DialogBox.inventory.append(self)

    def move_right(self) -> None:
        """
        Move the dialog box toward the display (left to right)
        self.start_moving variable determine when the dialog box is starting moving
        self.stop_moving variable is the opposite.
        The velocity is control via the variable self.acceleration (deceleration), you can
        change the values for exponential deceleration if you wish.

        :return: None
        """
        if self.rect.left < 10:
            if self.start_moving < self.gl.FRAME < self.stop_moving:
                self.rect.move_ip(self.acceleration[self.move_counter % len(self.acceleration) - 1], 0)
                self.move_counter += 1
            # Continue pushing the dialog box if not
            # fully visible after 100 frames (low fps)
            else:
                if self.gl.FRAME > self.stop_moving:
                    self.rect.move_ip(2, 0)

    def move_left(self) -> None:
        """
        Move the dialog box toward the display (left to right)
        self.start_moving variable determine when the dialog box is starting moving
        self.stop_moving variable is the opposite.
        The velocity is control via the variable self.acceleration (deceleration), you can
        change the values for exponential deceleration if you wish.

        :return: None
        """
        if self.rect.right > self.gl.SCREENRECT.w - 10:
            if self.start_moving < self.gl.FRAME < self.stop_moving:
                self.rect.move_ip(-self.acceleration[self.move_counter % len(self.acceleration) - 1], 0)
                self.move_counter += 1
            # Continue pushing the dialog box if not
            # fully visible after 100 frames (low fps)
            else:
                if self.gl.FRAME > self.stop_moving:
                    self.rect.move_ip(-2, 0)

    def alpha_in(self) -> None:
        """
        Create a fade-in effect for the dialog box, start with the min alpha values 0 and
        fade in to the max value 255
        self.start_moving variable determine the fade in starting frame number
        self.stop_moving variable is the opposite (stop the effect)

        :return: None
        """
        if self.fade_in_counter < len(self.fade_in) - 1:
            if self.start_fadein < self.gl.FRAME < self.stop_moving:
                self.image.set_alpha(self.fade_in[self.fade_in_counter % len(self.fade_in) - 1])
                self.fade_in_counter += 1
        else:
            self.image.set_alpha(255)

    def alpha_out(self) -> None:
        """
        Create a fading out effect of the dialog box.
        Start the effect when frame number is over self.start_fadeout (adjust the variable if necessary)
        Start with the highest value 255 and fade toward 0.
        When the alpha value 0 is reached, the sprite is killed (removed from all groups)
        :return: None
        """
        if self.gl.FRAME > self.start_fadeout:
            self.image.set_alpha(self.fade_out[self.fade_out_counter])
            self.fade_out_counter += 1
        if self.fade_out_counter > len(self.fade_out) - 1:
            self.destroy()

    @staticmethod
    def destroy():
        for instance in DialogBox.inventory:
            DialogBox.inventory.remove(instance)
            if hasattr(instance, 'kill'):
                instance.kill()

    def display_text(self, image_):
        """
        Scroll the dialogs vertically (moving up)
        You can control the text color (RGBA), adjust fgcolor=pygame.Color(149, 119, 236, 245),
        text style : here freetype.STYLE_STRONG
        text size : size=16
        variable y is increment with 25 every lines (vertical spacing)

        :param image_: Correspond to the dialog box image (most likely to be self.image)
                       It is necessary to create a copy of self.image prior passing it as an
                       positional argument in the display_text such as self.display_text(self.image.copy())
                       If omitted, the dialog box image will draw over the previous change and so on.
        :return: pygame.Surface
        """
        if isinstance(self.text, list):
            if len(self.text) != 0:
                x = 120
                y = self.text_origin
                for sentence in self.text:
                    if y > 10:
                        DialogBox.FONT.render_to(
                            image_, (x, y), sentence, fgcolor=self.text_color,
                            style=freetype.STYLE_STRONG, size=16)
                    y += 25
        self.text_origin -= 0.2
        return image_

    def update(self) -> None:
        if self.gl.FRAME > self.start_dialog_box:
            if self.dt > self.timing:

                self.image = self.image_copy.copy()
                # self.rect = self.image.get_rect(topleft=(self.location[0], self.location[1]))

                if self.character is not None and isinstance(self.character, list):
                    self.image.blit(self.character[self.index], (8, 20), special_flags=pygame.BLEND_RGB_ADD)

                    # skip the last sprite from the sprite list,
                    # last sprite is the glitch effect
                    if self.index < len(self.character) - 2:
                        if self.count > 20:
                            self.index += 1
                            self.count = 0
                    else:
                        self.index = 0

                    # display the glitch
                    if randint(0, 100) >= 98:
                        self.image.blit(self.character[-1], (10, 20))

                if self.scan:
                    if self.scan_index < self.max_width - 65:
                        # scan effect speed 4 pixels / frame
                        self.scan_index += 4
                    else:
                        self.scan_index = 15

                self.image.blit(
                    DialogBox.readout[int(self.readout_index)
                                      % len(DialogBox.readout) - 1], (100, 0),
                    special_flags=pygame.BLEND_RGBA_ADD)

                if self.voice:
                    self.image.blit(
                        DialogBox.voice_modulation[int(self.voice_module_index)
                                                   % len(DialogBox.voice_modulation) - 1], (0, 160),
                        special_flags=pygame.BLEND_RGBA_ADD)

                # scan effect
                if self.scan:
                    self.image.blit(self.scan_background_surface, (self.scan_index, 12),
                                    special_flags=pygame.BLEND_RGB_ADD)

                    if self.scan_index < self.max_width:
                        self.scan_index += 0.1
                    else:
                        self.scan_index = 0

                self.voice_module_index += 0.2
                self.readout_index += 1

                self.dt = 0
                self.image = self.display_text(self.image.copy())
                self.image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
                self.alpha_in()

                if self.gl.FRAME > self.start_fadeout:
                    self.alpha_out()

                if self.direction is 'RIGHT':
                    self.move_right()
                else:
                    self.move_left()

                self.count += 1

            self.dt += self.gl.TIME_PASSED_SECONDS


class GL:
    FRAME = 0


if __name__ == '__main__':

    pygame.init()
    freetype.init(cache_size=64, resolution=72)
    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)
    BACKGROUND = pygame.image.load('Assets\\background.jpg').convert()
    BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREENRECT.size))
    BACKGROUND.set_alpha(None)
    # FONT = freetype.Font(os.path.join('Assets\\Fonts\\', 'Gtek Technology.ttf'), size=12)
    # print(pygame.font.get_fonts(), pygame.font.match_font('bitstreamverasans'))
    FONT = freetype.Font('C:\\Windows\\Fonts\\Arial.ttf')
    FONT.antialiased = False
    clock = pygame.time.Clock()
    screen.blit(BACKGROUND, (0, 0))
    sprite_group = pygame.sprite.Group()
    All = pygame.sprite.RenderUpdates()


    class Player:
        def __init__(self):
            pass

        def alive(self):
            return True


    player = Player()

    FRAMESURFACE = pygame.Surface((FRAMEBORDER.get_width() - 20, FRAMEBORDER.get_height() - 20),
                                  pygame.RLEACCEL).convert()
    FRAMESURFACE.fill((10, 10, 18, 200))
    FRAMEBORDER.blit(FRAMESURFACE, (10, 15))
    DIALOG = FRAMEBORDER
    del FRAMEBORDER, FRAMESURFACE

    DialogBox.containers = sprite_group, All
    DialogBox.images = DIALOG
    DialogBox.character = NAMIKO
    DialogBox.voice_modulation = VOICE_MODULATION
    DialogBox.readout = DIALOGBOX_READOUT
    DialogBox.FONT = FONT
    DialogBox.text = ["Protect the transport and reach out ", "Altera the green planet outside the", "asteroid belt.",
                      "There are huge asteroids ahead, focus ", "and dodge them carefully.", "Have fun and good luck.",
                      " ", "Over and out!", "Masako"]
    im = pygame.image.load("Assets\\icon_glareFx_blue.png").convert()
    DialogBox.scan_image = pygame.image.load("Assets\\icon_glareFx_blue.png").convert()
    DialogBox.scan_image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

    TIME_PASSED_SECONDS = 0
    FRAME = 0
    GL.TIME_PASSED_SECONDS = TIME_PASSED_SECONDS
    GL.FRAME = FRAME
    GL.SCREENRECT = SCREENRECT

    masako = DialogBox(gl_=GL, location_=(-DIALOG.get_width(), 50),
                       speed_=15, layer_=-3, voice_=True, scan_=True, direction_='RIGHT',
                       text_color_=pygame.Color(149, 119, 236, 245), fadein_=500, fadeout_=1000)

    cobra = pygame.image.load('Assets\\Cobra.png').convert()
    cobra.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    cobra = pygame.transform.smoothscale(cobra, (100, 170))
    DialogBox.character = [cobra, cobra]
    DialogBox.text = ["Don't worry, it won't take long", "before I wreck everything.", " "]
    DialogBox.images = pygame.transform.smoothscale(DIALOG, (400, 200))
    DialogBox.scan_image = pygame.image.load("Assets\\icon_glareFx_red.png").convert()
    DialogBox.scan_image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

    cob = DialogBox(gl_=GL, location_=(SCREENRECT.w + DialogBox.images.get_width(), 500),
                    speed_=15, layer_=-3, voice_=True, scan_=True, start_=500, direction_='LEFT',
                    text_color_=pygame.Color(249, 254, 56, 245), fadein_=500, fadeout_=1100)

    STOP_GAME = False

    while not STOP_GAME:

        for event in pygame.event.get():  # User did something
            keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT:
                print('Quitting')
                STOP_GAME = True

            if keys[pygame.K_SPACE]:
                pass

            if keys[pygame.K_ESCAPE]:
                STOP_GAME = True

        # screen.fill((0,0,0))
        screen.blit(BACKGROUND, (0, 0))
        All.update()

        All.draw(screen)
        # dirty = All.draw(screen)
        # pygame.display.update(dirty)

        TIME_PASSED_SECONDS = clock.tick(60)
        GL.TIME_PASSED_SECONDS = TIME_PASSED_SECONDS
        pygame.display.flip()
        FRAME += 1
        GL.FRAME = FRAME

        # print(clock.get_fps())

    pygame.quit()
