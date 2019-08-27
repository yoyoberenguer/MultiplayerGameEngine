import pygame


__author__ = "Yoann Berenguer"
__credits__ = ["Yoann Berenguer"]
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"


# LayerUpdate method modified for blending effect
class LayeredUpdatesModified(pygame.sprite.LayeredUpdates):

    def __init__(self):
        pygame.sprite.LayeredUpdates.__init__(self)

    def draw(self, surface_):
        """draw all sprites in the right order onto the passed surface

        LayeredUpdates.draw(surface): return Rect_list

        """
        spritedict = self.spritedict
        surface_blit = surface_.blit
        dirty = self.lostsprites
        self.lostsprites = []

        # self.sprites() returns a ordered list of sprites (first back, last top).
        for spr in self.sprites():
            if spr.alive():
                rec = spritedict[spr]
                if hasattr(spr, 'blend') and spr.blend is not None:
                    newrect = surface_blit(spr.image, spr.rect, special_flags=spr.blend)

                else:
                    newrect = surface_blit(spr.image, spr.rect)

                spritedict[spr] = newrect

        return dirty

    def empty(self):
        """remove all sprites
        Group.empty(): return None
        Removes all the sprites from the group.

        """
        for s in self.sprites():
            self.remove_internal(s)
            s.remove_internal(self)