from random import randint, uniform

import pygame
from pygame import freetype

from CreateHalo import PlayerHalo
from NetworkBroadcast import Broadcast, StaticSprite, SoundAttr, DeleteSpriteCommand
from Textures import EXHAUST2, DISRUPTION_ORG, FIRE_PARTICLES, EXPLOSION2, HALO_SPRITE13, \
    DIALOGBOX_READOUT_RED, SKULL, FINAL_MISSION
from Sounds import IMPACT1
from Explosions import Explosion
from AfterBurners import AfterBurner
from End import PlayerLost


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
        self.fxdt = 0
        self.layer = layer_
        self.blend = 0
        self.previous_pos = pygame.math.Vector2()            # previous position
        self.max_life = 5000
        self.life = 5000                                     # MirroredTransportClass max hit points
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
        self.half_life = (self.max_life >> 1)

        Broadcast.add_object_id(self.id_)   # this is now obsolete since it is done from main loop

    def delete_object(self) -> DeleteSpriteCommand:
        """
        Send a command to kill an object on client side.

        :return: DetectCollisionSprite object
        """
        return DeleteSpriteCommand(frame_=self.gl.FRAME, to_delete_={self.id_: self.surface_name})

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
                           calc_pos, 8, pygame.BLEND_RGB_ADD,
                           self.layer - 1, texture_name_='EXHAUST2')

    def player_lost(self) -> None:
        PlayerLost.containers = self.gl.All
        PlayerLost.DIALOGBOX_READOUT_RED = DIALOGBOX_READOUT_RED
        PlayerLost.SKULL = SKULL
        font = freetype.Font('Assets\\Fonts\\Gtek Technology.ttf', size=14)
        PlayerLost(gl_=self.gl, font_=font, image_=FINAL_MISSION, layer_=0)
        # todo kill player 1 and 2 game is over

    def explode(self):
        Explosion.images = EXPLOSION2
        for i in range(10):
            Explosion(self, (self.rect.centerx + randint(-400, 400),
                             self.rect.centery + randint(-400, 400)),
                      self.gl, 8, self.layer,
                      texture_name_='EXPLOSION2', mute_=False if i > 0 else True)

        PlayerHalo.images = HALO_SPRITE13
        PlayerHalo.containers = self.gl.All
        PlayerHalo(texture_name_='HALO_SPRITE13', object_=self, timing_=8)
        self.quit()

    def collide(self, damage_: int)-> None:
        """
        Asteroid collide with object (e.g Asteroids)
        :param damage_: int; damage transfer to the transport (damage must be positive)
        :return: None
        """
        assert isinstance(damage_, int), \
            'Positional arguement damage_, expecting int type got %s ' % type(damage_)
        if self.alive():
            if damage_ is None or damage_ < 0:
                raise ValueError('positional arguement damage_ cannot be None or < 0.')
            self.impact = True      # variable used for blending, (electric effect on the transport's hull )
            self.index = 0
            self.life -= damage_    # Transport life decrease
            # Play an impact sound locally
            self.gl.MIXER.play(sound_=IMPACT1, loop_=False, priority_=0,
                               volume_=1.0, fade_out_ms=0, panning_=True,
                               name_='IMPACT1', x_=self.rect.centerx,
                               object_id_=id(IMPACT1),
                               screenrect_=self.gl.SCREENRECT)
            # Play impact sound on client computer.
            self.impact_sound_object.play()
        else:
            self.quit()
            
    def hit(self, damage_):
        if self.alive():
            self.life -= damage_
        else:
            self.quit()

    def get_centre(self) -> tuple:
        return self.rect.center

    def display_fire_particle_fx(self) -> None:
        # Display fire particles when the player has taken bad hits
        # Use the additive blend mode.
        if self.fxdt > self.timing:
            for p_ in self.vertex_array:

                # queue the particle in the vector direction
                p_.rect.move_ip(p_.vector)
                p_.image = p_.images[p_.index]
                if p_.index > len(p_.images) - 2:
                    p_.kill()
                    self.vertex_array.remove(p_)

                p_.index += 1
            self.fxdt = 0
        else:
            self.fxdt += self.gl.TIME_PASSED_SECONDS

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
        # self.gl.FIRE_PARTICLES_FX.add(sprite__)
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

    def quit(self) -> None:
        Broadcast.remove_object_id(self.id_)
        obj = Broadcast(self.delete_object())
        obj.queue()
        self.kill()

    def update(self):

        self.rect.clamp_ip(self.safe_zone)

        self.image = self.image_copy.copy()

        # in the 16ms area (60 FPS)
        if self.dt > self.timing:

            if self.life < self.half_life:
                position = pygame.math.Vector2(randint(-50, 50), randint(-100, 100))
                self.fire_particles_fx(position_=position + pygame.math.Vector2(self.rect.center),
                                       vector_=pygame.math.Vector2(uniform(-1, 1), uniform(+1, +3)),
                                       images_=FIRE_PARTICLES,
                                       layer_=0, blend_=pygame.BLEND_RGB_ADD)
            if self.life < 1:
                self.explode()
                return

            if self.previous_pos == self.rect.center:
                self.rect.centerx += randint(-1, 1)
                self.rect.centery += randint(-1, 1)

            if self.gl.FRAME < 100:
                self.rect.centery -= 3

            self.previous_pos = self.rect.center
            self.engine.update()

            self.transport_object.update(
                {'frame': self.gl.FRAME, 'rect': self.rect,
                 'damage': self.damage, 'life': self.life, 'impact': self.impact})
            # Broadcast the spaceship position
            self.transport_object.queue()
            self.dt = 0

        else:
            self.dt += self.gl.TIME_PASSED_SECONDS

        # outside the 60 FPS area.
        # Below code processed every frames.
        if self.impact:
            self.image.blit(DISRUPTION_ORG[self.index % len(DISRUPTION_ORG) - 1],
                            (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            self.index += 1
            if self.index > len(DISRUPTION_ORG) - 2:
                self.impact = False
                self.index = 0
