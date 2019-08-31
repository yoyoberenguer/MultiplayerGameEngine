
class Gems(pygame.sprite.Sprite):
    containers = None
    GEM_VALUE = numpy.array(list(range(1, 22))) * 22

    def __init__(self, player_, object_, ratio_,
                 timing_: int = 15, offset_: pygame.Rect = None, layer_=-1):

        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(GL.All, pygame.sprite.LayeredUpdates):
            GL.All.change_layer(self, layer_)

        self.object_ = object_
        self.timing = timing_
        self.offset = offset_
        self.player = player_

        gem_number = randint(0, len(GEM_SPRITES) - 1)
        self.value = self.GEM_VALUE[gem_number]
        self.image = GEM_SPRITES[gem_number]
        self.image_copy = self.image.copy()
        # modified the surface orientation
        self.image = pygame.transform.rotate(self.image, randint(0, 360))

        self.ratio = ratio_

        if self.offset is not None:
            # display the sprite at a specific location.
            self.rect = self.image.get_rect(center=self.offset.center)
        else:
            # use player location
            self.rect = self.image.get_rect(center=self.object_.rect.center)

        self.speed = pygame.math.Vector2(0, randint(3, 9))

        self.dt = 0
        self.theta = 0

    def adjust_vector(self):
        """ return a vector corresponding to the angle"""
        angle_radian = -atan2(self.player.rect.centery - self.rect.centery,
                              self.player.rect.centerx - self.rect.centerx)
        return cos(angle_radian) * self.speed.length(), -sin(angle_radian) * self.speed.length()

    def update(self):

        if self.dt > self.timing:

            if SCREENRECT.contains(self.rect):

                self.image = pygame.transform.rotozoom(self.image_copy, self.theta, self.ratio)
                self.rect = self.image.get_rect(center=self.rect.center)
                # Change the gem vector direction automatically in order
                # to collide with the player sprite.
                # Mistaken gems for enemy projectile
                # if bool(GL.PLAYER_GROUP) and self.player.alive():
                #    self.rect.move_ip(self.adjust_vector())
                # else:
                self.rect.move_ip(self.speed.x, self.speed.y)

                self.theta += 2
                if self.theta > 359:
                    self.theta = 0

            else:
                self.kill()

            self.dt = 0

        self.dt += GL.TIME_PASSED_SECONDS
