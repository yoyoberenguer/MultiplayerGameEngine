
import pygame
from random import randint

from numpy import linspace

from TextureTools import *
import os

pygame.init()
pygame.display.set_mode((800, 1024))

__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


BACK = pygame.image.load('Assets\\BACK1.png') \
    .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)


# Display pixels on the background surfaces
def create_stars(surface_) -> None:
    w, h = surface_.get_size()
    surface_.lock()
    for r in range(3000):
        rand = randint(0, 1000)
        # yellow
        if rand > 950:
            color = pygame.Color(255, 255, randint(1, 255), randint(1, 255))
        # red
        elif rand > 995:
            color = pygame.Color(randint(1, 255), 0, 0, randint(1, 255))
        # blue
        elif rand > 998:
            color = pygame.Color(0, 0, randint(1, 255), randint(1, 255))
        else:
            avg = randint(128, 255)
            color = pygame.Color(avg, avg, avg, randint(1, 255))
        coords = (randint(0, w - 1), randint(0, h - 1))
        color_org = surface_.get_at(coords)[:3]
        if sum(color_org) < 384:
            surface_.set_at(coords, color)
    surface_.unlock()


create_stars(BACK)

BACK_ARRAY = pygame.surfarray.array3d(BACK)
BACK1 = BACK_ARRAY[:800, 0:1024]
BACK1_S = pygame.surfarray.make_surface(BACK1)
BACK1_S.convert(32, pygame.RLEACCEL)
# pygame.image.save(BACK1_S, 'Background1.png')
BACK2 = BACK_ARRAY[:800, 1024:2048]
BACK2_S = pygame.surfarray.make_surface(BACK2)
BACK2_S.convert(32, pygame.RLEACCEL)
# pygame.image.save(BACK2_S, 'Background2.png')
BACK3 = pygame.image.load('Assets\\BACK2.png').convert(32, pygame.RLEACCEL)

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

BLUE_LASER = pygame.image.load('Assets\\lzrfx021.png').convert_alpha()
BLUE_LASER = pygame.transform.rotate(BLUE_LASER, 90)
BLUE_LASER = pygame.transform.smoothscale(BLUE_LASER, (24, 35))

RED_LASER = pygame.image.load('Assets\\lzrfx033.png').convert(32, pygame.RLEACCEL)
RED_LASER = pygame.transform.rotate(RED_LASER, 90)
RED_LASER = pygame.transform.smoothscale(RED_LASER, (24, 35))

IMPACT_LASER = spread_sheet_fs8('Assets\\impact_blue_128x128_6x3.png', 128, 3, 6)

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

EXHAUST2 = spread_sheet_fs8('Assets\\Exhaust7_6x6_256x256.png', 256, 6, 6)
i = 0
for surface in EXHAUST2:
    surface = pygame.transform.smoothscale(surface, (60, 90))
    EXHAUST2[i] = surface
    i += 1

DISRUPTION = spread_sheet_fs8('Assets\\Blurry_Water1_256x256_6x6_1.png', 256, 6, 6)
DISRUPTION_ORG = DISRUPTION.copy()
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
EXPLOSION2 = spread_sheet_fs8('Assets\\Explosion16_512x512_.png', 512, 6, 8)

GRID = pygame.image.load('Assets\\grid2.png').convert()
GRID = pygame.transform.smoothscale(GRID, (64, 64))

DEIMOS = pygame.image.load('Assets\\DEIMOS.png').convert_alpha()
EPIMET = pygame.image.load('Assets\\EPIMET.png').convert_alpha()

MULT_ASTEROID_512 = spread_sheet_per_pixel_fs8('Assets\\DEIMOS_512x512.png', 512, 5, 6)
MULT_ASTEROID_64 = []
MULT_ASTEROID_32 = []
i = 0
for surface in MULT_ASTEROID_512:
    MULT_ASTEROID_64.append(pygame.transform.smoothscale(surface, (32, 32)))
    MULT_ASTEROID_32.append(pygame.transform.smoothscale(surface, (16, 16)))
    i += 1

TRANSPORT = pygame.image.load('Assets\\Transport.png').convert_alpha()
# TRANSPORT.set_colorkey((0, 0, 0, 0))

steps = numpy.array([0., 0.03333333, 0.06666667, 0.1, 0.13333333,
                     0.16666667, 0.2, 0.23333333, 0.26666667, 0.3,
                     0.33333333, 0.36666667, 0.4, 0.43333333, 0.46666667,
                     0.5, 0.53333333, 0.56666667, 0.6, 0.63333333,
                     0.66666667, 0.7, 0.73333333, 0.76666667, 0.8,
                     0.83333333, 0.86666667, 0.9, 0.93333333, 0.96666667])

HALO_SPRITE12 = [pygame.transform.smoothscale(
    load_per_pixel('Assets\\Halo11.png'), (128, 128))] * 30

for number in range(len(HALO_SPRITE12)):
    rgb = pygame.surfarray.array3d(HALO_SPRITE12[number])
    alpha = pygame.surfarray.array_alpha(HALO_SPRITE12[number])
    image = add_transparency_all(rgb, alpha, int(255 * steps[number]))
    # image size is x2 (last sprite)
    surface1 = pygame.transform.smoothscale(image, (
        int(image.get_width() * (1 + (number / 10))),
        int(image.get_height() * (1 + (number / 10)))))
    # Do not convert surface to fast blit
    HALO_SPRITE12[number] = surface1.convert_alpha()


HALO_SPRITE13 = [pygame.transform.smoothscale(
    load_per_pixel('Assets\\Halo11.png'), (256, 256))] * 30

for number in range(len(HALO_SPRITE13)):
    rgb = pygame.surfarray.array3d(HALO_SPRITE13[number])
    alpha = pygame.surfarray.array_alpha(HALO_SPRITE13[number])
    image = add_transparency_all(rgb, alpha, int(255 * steps[number]))
    # image size is x2 (last sprite)
    surface1 = pygame.transform.smoothscale(image, (
        int(image.get_width() * (1 + (number / 10))),
        int(image.get_height() * (1 + (number / 10)))))
    # Do not convert surface to fast blit
    HALO_SPRITE13[number] = surface1.convert_alpha()

HALO_SPRITE14 = [pygame.transform.smoothscale(
    load_per_pixel('Assets\\Halo13.png'), (128, 128))] * 30
for number in range(len(HALO_SPRITE14)):
    rgb = pygame.surfarray.array3d(HALO_SPRITE14[number])
    alpha = pygame.surfarray.array_alpha(HALO_SPRITE14[number])
    image = add_transparency_all(rgb, alpha, int(255 * steps[number]))
    # image size is x2 (last sprite)
    surface1 = pygame.transform.smoothscale(image, (
        int(image.get_width() * (1 + (number / 10))),
        int(image.get_height() * (1 + (number / 10)))))
    # Do not convert surface to fast blit
    HALO_SPRITE14[number] = surface1.convert_alpha()

FIRE_PARTICLES = spread_sheet_fs8('Assets\\Particles_128x128_.png', 128, 6, 6)

LAVA = spread_sheet_fs8('Assets\\Laval2_256_6x6_.png', 256, 6, 6)

del steps

SHOOTING_STAR = pygame.image.load('Assets\\shooting_star.png')\
        .convert(32, pygame.HWSURFACE | pygame.HWACCEL | pygame.RLEACCEL)
SHOOTING_STAR = pygame.transform.smoothscale(SHOOTING_STAR, (25, 80))

BACKGROUND = pygame.image.load('Assets\\Background.jpg').convert()
BACKGROUND = pygame.transform.smoothscale(BACKGROUND, (800, 1024))

FRAME = pygame.Surface((760, 460), depth=32, flags=(pygame.SWSURFACE | pygame.SRCALPHA))
FRAME.convert_alpha()
FRAME.fill((10, 15, 10, 200))

FRAMEBORDER = pygame.image.load('Assets\\FrameBorder.png')
FRAMEBORDER = pygame.transform.smoothscale(FRAMEBORDER, (800, FRAMEBORDER.get_height()))
FRAMEBORDER.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
SKULL = pygame.image.load('Assets\\toxigineSkull_.png').convert()
SKULL = pygame.transform.smoothscale(
    SKULL, (int(SKULL.get_width() * .8), int(SKULL.get_height() * .8)))
SKULL.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)


SKULL_64x64 = pygame.transform.smoothscale(
    pygame.image.load('Assets\\toxigineSkull_.png'), (64, 64))


FINAL_MISSION = pygame.image.load('Assets\\container.png').convert()
FINAL_MISSION = pygame.transform.smoothscale(
    FINAL_MISSION, (int(FINAL_MISSION.get_width() * .8), int(FINAL_MISSION.get_height() * .8)))
FINAL_MISSION.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

DIALOGBOX_READOUT = spread_sheet_fs8('Assets\\Readout_512x512_6x6_.png', 512, 6, 6)
i = 0
for surface in DIALOGBOX_READOUT:
    # surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    DIALOGBOX_READOUT[i] = pygame.transform.smoothscale(
        surface, (FINAL_MISSION.get_width() - 150, FINAL_MISSION.get_height() - 150))
    DIALOGBOX_READOUT[i] = pygame.transform.flip(DIALOGBOX_READOUT[i], True, True)
    i += 1
DIALOGBOX_READOUT_RED = spread_sheet_fs8('Assets\\Readout_512x512_6x6_red_.png', 512, 6, 6)
i = 0
for surface in DIALOGBOX_READOUT_RED:
    # surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    DIALOGBOX_READOUT_RED[i] = pygame.transform.smoothscale(
        surface, (FINAL_MISSION.get_width() - 150, FINAL_MISSION.get_height() - 150))
    DIALOGBOX_READOUT_RED[i] = pygame.transform.flip(DIALOGBOX_READOUT_RED[i], True, True)
    i += 1

x = 15
y = 15
# Size change according to value
GEM_SPRITES = []
for i in range(1, 21):

    GEM_SPRITES.append(
        pygame.transform.smoothscale(
            pygame.image.load('Assets\\Gems\\Gem' + str(i) + '.png').convert_alpha(), (x, y)))
    if i % 2:
        x += 1
        y += 1
del (x, y)

# NOT USE YET
# GEM_ASSIMILATION = spread_sheet_per_pixel('Assets\\GemAssimilation_128x128_9x2.png', 128, 2, 9)

COSMIC_DUST1 = pygame.image.load('Assets\\stars_.png')
COSMIC_DUST1.convert(32, pygame.RLEACCEL)
COSMIC_DUST1 = pygame.transform.smoothscale(COSMIC_DUST1, (2, 5))
COSMIC_DUST1.set_alpha(255)

COSMIC_DUST2 = pygame.image.load('Assets\\fx_.png')
COSMIC_DUST2.convert(32, pygame.RLEACCEL)
COSMIC_DUST2 = pygame.transform.smoothscale(COSMIC_DUST2, (4, 10))
COSMIC_DUST2.set_alpha(255)

STATION = pygame.image.load('Assets\\Station.png').convert()
STATION = pygame.transform.smoothscale(STATION, (300, 300))
STATION.set_colorkey((0, 0, 0), pygame.RLEACCEL)

BLUE_PLANET = pygame.image.load('Assets\\blueplanet_.png')
BLUE_PLANET.convert(32, pygame.RLEACCEL)

# GREEN_PLANET = pygame.image.load('Assets\\greenplanet.png')
# GREEN_PLANET = pygame.transform.smoothscale(GREEN_PLANET, (500, 500))
# GREEN_PLANET.convert()

MAJOR_ASTEROID = pygame.image.load('Assets\\Aster2.png').convert_alpha()


VOICE_MODULATION = []
VOICE_MODULATION.extend((pygame.image.load('Assets\\techAudio_.png').convert(),
                         pygame.image.load('Assets\\techAudio1_.png').convert(),
                         pygame.image.load('Assets\\techAudio2_.png').convert(),
                         pygame.image.load('Assets\\techAudio3_.png').convert(),
                         pygame.image.load('Assets\\techAudio4_.png').convert()))
i = 0
for surface in VOICE_MODULATION:
    surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    VOICE_MODULATION[i] = surface
    i += 1

DIALOGBOX_READOUT = spread_sheet_fs8('Assets\\Readout_256x256_.png', 256, 6, 6)
i = 0
for surface in DIALOGBOX_READOUT:
    surface.convert()
    surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
    surface = pygame.transform.flip(surface, True, True)
    DIALOGBOX_READOUT[i] = pygame.transform.smoothscale(surface, (400, 250))
    i += 1

NAMIKO = [pygame.transform.smoothscale(pygame.image.load('Assets\\Namiko1_.png').convert(), (100, 180)),
          pygame.transform.smoothscale(pygame.image.load('Assets\\Namiko6_.png').convert(), (100, 180)),
          pygame.transform.smoothscale(pygame.image.load('Assets\\Namiko2_.png').convert(), (100, 180)),
          pygame.transform.smoothscale(pygame.image.load('Assets\\Namiko7_.png').convert(), (100, 180)),
          pygame.transform.smoothscale(pygame.image.load('Assets\\Namiko3_.png').convert(), (100, 180)),
          pygame.transform.smoothscale(pygame.image.load('Assets\\Namiko5_.png').convert(), (100, 180)),
          pygame.transform.smoothscale(pygame.image.load('Assets\\Namiko4_.png').convert(), (100, 180))]
for image in NAMIKO:
    image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

FRAMEBORDER = pygame.image.load('Assets\\FrameBorder_.png').convert()
FRAMEBORDER.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
FRAMEBORDER = pygame.transform.smoothscale(FRAMEBORDER, (430, 250))
FRAMEBORDER = pygame.transform.smoothscale(FRAMEBORDER, (FRAMEBORDER.get_width(), FRAMEBORDER.get_height() - 40))
FRAMESURFACE = pygame.Surface((FRAMEBORDER.get_width() - 15, FRAMEBORDER.get_height() - 20),
                                  pygame.RLEACCEL).convert()
FRAMESURFACE.fill((10, 10, 18, 200))

LIFE_HUD = pygame.image.load('Assets\\lifehud_275x80.png').convert_alpha()
w, h = LIFE_HUD.get_size()
# LIFE_HUD = pygame.transform.smoothscale(LIFE_HUD, (int(w * 1.2), h))
# LIFE_HUD.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

LIFE_HUD_DEAD = pygame.image.load('Assets\\lifehud_275x80.png').convert_alpha()
LIFE_HUD_DEAD.blit(SKULL_64x64, (w // 2 - 32, h // 2 - 32), special_flags=pygame.BLEND_RGB_ADD)

VARIABLE_TEXTURE = spread_sheet_per_pixel_fs8('Assets\\Blurry_Water1_256x256_6x6_2_alpha.png', 256, 6, 6)

FLARE = pygame.image.load('Assets\\flare1_.png').convert()
FLARE = pygame.transform.smoothscale(FLARE, (600, 35))
FLARE.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
FLARE = [FLARE] * 5

LIGHT = pygame.image.load('Assets\\radial5_.png').convert()
LIGHT.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
LIGHT1 = pygame.transform.smoothscale(LIGHT, (100, 100))
LIGHT2 = pygame.transform.smoothscale(LIGHT, (250, 250))
LIGHT3 = pygame.transform.smoothscale(LIGHT, (400, 400))

LIGHT = [LIGHT1, LIGHT2, LIGHT3]


PLAYER_EXPLOSION1 = spread_sheet_fs8('Assets\\Atomic_skull_256x256_1.png', 256, 8, 11)

grows = linspace(1, 5, 66)
decrease = linspace(5, 1, 22)
full = [*grows, *decrease]
i = 0
for surface in PLAYER_EXPLOSION1:
    w, h = surface.get_size()
    ww, hh = int(w * full[i]), int(h * full[i])
    PLAYER_EXPLOSION1[i] = pygame.transform.smoothscale(surface, (ww, hh))
    i += 1


PLAYER_EXPLOSION2 = spread_sheet_fs8('Assets\\Bomb_5_512x512_4x11_.png', 512, 4, 11)

grows = linspace(1, 4, 66)
decrease = linspace(4, 1, 22)
full = [*grows, *decrease]
i = 0
for surface in PLAYER_EXPLOSION2:
    w, h = surface.get_size()
    ww, hh = int(w * full[i]), int(h * full[i])
    PLAYER_EXPLOSION2[i] = pygame.transform.smoothscale(surface, (ww, hh))
    i += 1

NEBULA = pygame.image.load('Assets\\Nebula red.png').convert()
NEBULA = pygame.transform.smoothscale(NEBULA, (2048, 2048))
array = pygame.surfarray.pixels3d(NEBULA)
NEBULA2 = pygame.surfarray.make_surface(array[0:1024, 0:1024])
NEBULA1 = pygame.surfarray.make_surface(array[0:1024, 1024:2048])

ARROW_RIGHT = pygame.image.load('Assets\\chevrons.png').convert()
ARROW_RIGHT = pygame.transform.smoothscale(ARROW_RIGHT, (101, 74))
ARROW_RIGHT.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

