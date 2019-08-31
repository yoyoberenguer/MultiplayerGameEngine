
import pygame
from random import randint
from TextureTools import *


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
BACK2 = BACK_ARRAY[:800, 1024:2048]
BACK2_S = pygame.surfarray.make_surface(BACK2)

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

RED_LASER = pygame.image.load('Assets\\lzrfx033.png').convert()
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
SHOOTING_STAR = pygame.transform.scale(SHOOTING_STAR, (25, 80))

BACKGROUND = pygame.image.load('Assets\\Background.jpg').convert()
BACKGROUND = pygame.transform.scale(BACKGROUND, (800, 1024))

FRAME = pygame.Surface((760, 460), depth=32, flags=(pygame.SWSURFACE | pygame.SRCALPHA))
FRAME.convert_alpha()
FRAME.fill((10, 15, 10, 200))

FRAMEBORDER = pygame.image.load('Assets\\FrameBorder.png')
FRAMEBORDER = pygame.transform.scale(FRAMEBORDER, (800, FRAMEBORDER.get_height()))
FRAMEBORDER.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
SKULL = pygame.image.load('Assets\\toxigineSkull_.png').convert()
SKULL = pygame.transform.smoothscale(
    SKULL, (int(SKULL.get_width() * .8), int(SKULL.get_height() * .8)))
SKULL.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
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




