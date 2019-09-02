
import pygame
from random import choice, randint, uniform
from Textures import COSMIC_DUST1, COSMIC_DUST2
import time

# Vertex array for dust particles
COSMIC_DUST_ARRAY = []


def dust_alpha(image):
    alpha: int = image.get_alpha()
    new_alpha = alpha - 5
    if new_alpha < 0:
        new_alpha = 255
    image.set_alpha(new_alpha)
    return image


def display_dust(gl_):

    for sprite in COSMIC_DUST_ARRAY:

        if sprite is not None:

            if sprite.image is not None:
                screen = pygame.display.get_surface()
                screen.blit(sprite.image, sprite.rect.center)

            if sprite.stars:
                sprite.vector *= 0.3

            sprite.image = dust_alpha(sprite.image)

            sprite.rect.move_ip(sprite.speed * gl_.ACCELERATION + sprite.vector)

            if sprite.rect.top > gl_.SCREENRECT.h:

                COSMIC_DUST_ARRAY.remove(sprite)

                if hasattr(sprite, 'kill'):
                    sprite.kill()


def create_dust(gl_):

    cosmic_sprite = pygame.sprite.Sprite()
    cosmic_sprite.image = choice([COSMIC_DUST2.copy(), COSMIC_DUST1.copy()])

    cosmic_sprite.rect = cosmic_sprite.image.get_rect(midtop=(randint(0, gl_.SCREENRECT.w), -10))
    cosmic_sprite._layer = 0
    cosmic_sprite.stars = choice([True, False])
    cosmic_sprite.start = uniform(0, 5)
    cosmic_sprite.spawn = time.time()
    cosmic_sprite.vector = pygame.math.Vector2()

    if cosmic_sprite.stars:
        cosmic_sprite.speed = pygame.math.Vector2(0, randint(10, 15))
    else:
        cosmic_sprite.speed = pygame.math.Vector2(0, randint(15, 25))

    COSMIC_DUST_ARRAY.append(cosmic_sprite)

