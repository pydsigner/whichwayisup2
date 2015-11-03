import pygame


class RenderCog(object):
    def __init__(self, res, flags=0):
        """
        @res:       The display width per tile, in pixels.
        @flags:     Flags passed to pygame.display.set_mode().
        """
        self.set_flags(flags)
        self.set_resolution(res, first=True)
    
    def set_fps(self, fps):
        self.fps = fps
        # Paranoia in case we got input that wasn't nicely divisible. Ensure 
        # also that we don't accidentally round down to 0, which would cause 
        # div/0 problems.
        self.draw_interval = int(round(self.engine.fps / float(fps))) or 1
    
    def set_flags(self, flags=0):
        self.fullscreen = flags & pygame.FULLSCREEN
        self.flags = flags
    
    def set_fullscreen(self, state):
        if self.fullscreen == state:
            return
        
        self.fullscreen = not self.fullscreen
        self.flags ^= pygame.FULLSCREEN
        self.rebuild_screen()
    
    def set_resolution(self, res, first=False):
        # We utilize Python's lazy resolution here to avoid an error the first 
        # time this function is run
        if not first and res == self.res:
            return
        self.res = res
        
        self.gfx.set_resolution(res)
        
        self.screen_res = (ACTION_BOX_X * res, ACTION_BOX_Y * res)
        self.rebuild_screen()
    
    def rebuild_screen(self):
        self.screen = pygame.display.set_mode(self.screen_res, self.flags)
        self.rect = self.screen.get_rect()
        self.bg_cache = pygame.Surface(self.screen_res)
        
        self.draw_counter = 0
        self.draw(True)
    
    def draw(self, dirty_bg=False):
        tileset = self.state.level.get_tileset()
        self.gfx.set_tileset(tileset)
        if dirty_bg:
            # TODO: May switch to just using (0, 0) here instead of a rect
            self.bg_cache.blit(self.gfx.get_bg(), self.rect)
            for tile in self.state.level.get_tiles():
                ...
        self.screen.blit(self.bg_cache, self.rect)


class ActionCog(object):
    def __init__(self, fps):
        """
        @fps:       The physics framerate. Should divide into the engine 
                    framerate evenly.
        """


class StatefulEngine(object):
    def __init__(self, fps):
        """
        @fps:       The base engine framerate. Cogs will be updated once each 
                    frame.
        """
