from random import randint, uniform

import pygame
from NetworkBroadcast import Broadcast, StaticSprite, SoundAttr, DetectCollisionSprite
from Textures import EXPLOSION1, EXHAUST2, DISRUPTION_ORG, FIRE_PARTICLES
from Sounds import IMPACT1
from Explosions import Explosion
from AfterBurners import AfterBurner


__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


class Transport(pygame.sprite.Sprite):
    containers = None
    image = None

    def __init__(self, gl_, timing_, pos_, surface_name_, layer_=0):

        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            if layer_:
                gl_.All.change_layer(self, layer_)

        self.image = Transport.image
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect(center=pos_)
        self.timing = timing_
        self.gl = gl_
        self.dt = 0
        self.layer = layer_
        self.blend = 0
        self.previous_pos = pygame.math.Vector2()            # previous position
        self.life = 1000                                     # Transport max hit points
        self.damage = 10000                                  # Damage transfer after collision
        self.mask = pygame.mask.from_surface(self.image)     # Image have to be convert_alpha compatible
        self.pos = pos_
        self.index = 0
        self.impact = False
        self.vertex_array = []
        self.engine = self.engine_on()
        self.surface_name = surface_name_
        self.id_ = id(self)
        self.transport_object = Broadcast(self.make_object())
        self.impact_sound_object = Broadcast(self.make_sound_object('IMPACT'))
        half = self.gl.SCREENRECT.w >> 1
        self.safe_zone = pygame.Rect(half - 200, half, 400, self.gl.SCREENRECT.bottom - half)

    def make_sound_object(self, sound_name_: str) -> SoundAttr:
        return SoundAttr(frame_=self.gl.FRAME, id_=self.id_, sound_name_=sound_name_, rect_=self.rect)
    
    def make_object(self) -> StaticSprite:
        return StaticSprite(frame_=self.gl.FRAME, id_=self.id_, surface_=self.surface_name,
                            layer_=self.layer, blend_=self.blend, rect_=self.rect,
                            damage=self.damage, life=self.life, impact=self.impact)

    def engine_on(self) -> AfterBurner:
        AfterBurner.images = EXHAUST2
        calc_pos = (self.pos[0] - 400, self.pos[1] - 205)   # Top left corner position
        return AfterBurner(self, self.gl,
                           calc_pos, self.timing, pygame.BLEND_RGB_ADD,
                           self.layer - 1, texture_name_='EXHAUST2')

    def explode(self):
        if self.alive():
            Explosion.images = EXPLOSION1
            Explosion(self, self.rect.center, self.gl,
                      self.timing, self.layer, texture_name_='EXPLOSION1')
            self.kill()

    def collide(self, damage_):
        if self.alive():
            self.impact = True
            self.index = 0
            self.life -= damage_

            self.gl.MIXER.play(sound_=IMPACT1, loop_=False, priority_=0,
                               volume_=1.0, fade_out_ms=0, panning_=True,
                               name_='IMPACT1', x_=self.rect.centerx,
                               object_id_=id(IMPACT1),
                               screenrect_=self.gl.SCREENRECT)
            self.impact_sound_object.play()
            
    def hit(self, damage_):
        if self.alive():
            self.life -= damage_

    def get_centre(self) -> tuple:
        return self.rect.center

    def display_fire_particle_fx(self) -> None:
        # Display fire particles when the player has taken bad hits
        # Use the additive blend mode.

        for p_ in self.vertex_array:

            # queue the particle in the vector direction
            p_.rect.move_ip(p_.vector)
            p_.image = p_.images[p_.index]
            if p_.index > len(p_.images) - 2:
                p_.kill()
                self.vertex_array.remove(p_)

            p_.index += 1

    def fire_particles_fx(self,
                          position_,  # particle starting location (tuple or pygame.math.Vector2)
                          vector_,    # particle speed, pygame.math.Vector2
                          images_,    # surface used for the particle, (list of pygame.Surface)
                          layer_=0,   # Layer used to display the particles (int)
                          blend_=pygame.BLEND_RGB_ADD  # Blend mode (int)
                          ) -> None:
        # Create fire particles around the aircraft hull when player is taking serious damages

        # Cap the number of particles to avoid lag
        # if len(self.gl.FIRE_PARTICLES_FX) > 100:
        #    return
        # Create fire particles when the aircraft is disintegrating
        sprite_ = pygame.sprite.Sprite()
        self.gl.All.add(sprite_)
        # self.gl.FIRE_PARTICLES_FX.add(sprite_)
        # assign the particle to a specific layer
        if isinstance(self.gl.All, pygame.sprite.LayeredUpdates):
            self.gl.All.change_layer(sprite_, layer_)
        sprite_.layer = layer_
        sprite_.blend = blend_  # use the additive mode
        sprite_.images = images_
        sprite_.image = images_[0]
        sprite_.rect = sprite_.image.get_rect(center=position_)
        sprite_.vector = vector_  # vector
        sprite_.index = 0
        # assign update method to self.display_fire_particle_fx
        # (local method to display the particles)
        sprite_.update = self.display_fire_particle_fx
        self.vertex_array.append(sprite_)

    def update(self):

        self.rect.clamp_ip(self.safe_zone)

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            if self.life < 2000:
                position = pygame.math.Vector2(randint(-50, 50), randint(-100, 100))
                self.fire_particles_fx(position_=position + pygame.math.Vector2(self.rect.center),
                                       vector_=pygame.math.Vector2(uniform(-1, 1), uniform(+1, +3)),
                                       images_=FIRE_PARTICLES,
                                       layer_=0, blend_=pygame.BLEND_RGB_ADD)
            if self.life < 1:
                Explosion.images = EXPLOSION1
                Explosion(self, self.rect.center, self.gl,
                          self.timing, self.layer, texture_name_='EXPLOSION1')
                self.kill()

            if self.impact:
                self.image.blit(DISRUPTION_ORG[self.index % len(DISRUPTION_ORG) - 1],
                                (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                self.index += 1
                if self.index > len(DISRUPTION_ORG) - 2:
                    self.impact = False
                    self.index = 0

            # if self.alive():
            # Broadcast the spaceship position every frames
            self.transport_object.update(
                {'frame': self.gl.FRAME, 'rect': self.rect,
                 'damage': self.damage, 'life': self.life, 'impact': self.impact})
            self.transport_object.queue()

            if self.previous_pos == self.rect.center:
                self.rect.centerx += randint(-1, 1)
                self.rect.centery += randint(-1, 1)

            self.previous_pos = self.rect.center
            self.engine.update()

        else:
            self.dt += self.gl.TIME_PASSED_SECONDS
