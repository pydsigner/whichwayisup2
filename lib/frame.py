import pygame

from .locals import *
from .log import error_message
from .data import picpath


class Frame:
    def __init__(self, object, anim_name, frameno, frame_length):
        try:
            self.image = pygame.image.load(picpath(object, anim_name, frameno)).convert()
        except pygame.error:
            try:
                self.image = pygame.image.load(picpath("brown", anim_name, frameno)).convert() #Fallback to brown tileset
            except pygame.error:
                self.image = pygame.image.load(picpath("object", "idle", 0)).convert() #Fallback to default object image
                error_message("Object graphic missing: " + object + "_" +  anim_name + "_" + str(frameno))
        self.frame_length = frame_length
        
        # Hack for existing graphics
        self.image.set_colorkey((255,0,255))
        if MULTIPLIER == 2:
            # special case doubling!
            self.image = pygame.transform.scale2x(self.image)
        elif MULTIPLIER != 1:
            w, h = self.image.get_size()
            self.image = pygame.transform.smoothscale(self.image, (MULT(w), MULT(h)))

    def get_image(self):
        return self.image

    def get_time(self):
        return self.frame_length
