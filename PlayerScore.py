import pygame
import os
from numpy import linspace


class DisplayScore(pygame.sprite.Sprite):

    images = None
    containers = None

    def __init__(self, gl_, timing_=15):

        assert isinstance(timing_, type(timing_)), \
            "Positional argument <timing_> must be an integer, got %s instead " % type(timing_)
        if timing_ < 0:
            raise ValueError('Argument timing must be >= 0')

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = self.images
        self.rect = self.image.get_rect().move(300, 10)
        self.timing = timing_
        self.font = pygame.font.Font(os.path.join('', "Assets\\Fonts", 'ARCADE_R.ttf'), 15)
        self.gl = gl_
        self.score = 0
        self.old_score = 0
        self.cache_animation = []
        self.i = 0
        self.dt = 0
        zoom1 = linspace(1, 1.5, 16)
        zoom2 = linspace(1.5, 1, 16)
        self.zoom = [*zoom1, *zoom2]

    def score_update(self, points_: int) -> None:
        assert isinstance(points_, int), \
            "Positional argument <points_> must be type integer got %s " % type(points_)
        if points_ <= 0:
            raise ValueError("points_ must be >= 0 got %s " % points_)

        self.score += points_

    def update(self) -> None:

        if self.dt > self.timing:

            if self.old_score == self.score:
                self.i += 1
            else:
                self.cache_animation = [*[self.font.render('Score ' + str(self.score), True, (255, 255, 0))] * 32]

                i = 0
                for surface in self.cache_animation:
                    self.cache_animation[i] = pygame.transform.rotozoom(surface, 0, self.zoom[i])
                    i += 1

            self.image = self.cache_animation[self.i] if len(self.cache_animation) > 0 else \
                self.font.render('Score ' + str(self.score), True, (255, 255, 0))

            self.rect = self.image.get_rect()
            self.rect.topleft = ((pygame.display.get_surface().get_width() >> 1) - (self.image.get_width() >> 1), 15)

            if self.i >= len(self.cache_animation) - 1:
                self.i = 0
                self.cache_animation = []

            self.dt = 0

        self.old_score = self.score
        self.dt += self.gl.TIME_PASSED_SECONDS
