from .variables import variables
from .locals import *
from .data import levelpath


class World:
    def __init__(self, world_index=0):
        self.level_index = 0
        self.levels = []
        self.name = WORLDS[world_index]
        self.number = world_index + 1

        #Parsing config:
        conffile = open(levelpath(self.name))
        for line in conffile:
            if line.strip() != "":
                values = line.split()
                if values[0] == "level":
                    self.levels.append(values[1])

        self.level_count = len(self.levels)

    def is_next_level(self):
        return self.level_index < len(self.levels)
    
    def get_level(self, index=None):
        level = ""
        
        if index != None:
            self.level_index = index
        level = self.levels[self.level_index]
        
        #Unlocking the next level of this world
        if variables["unlocked" + self.name] < self.level_index:
            variables["unlocked" + self.name] = self.level_index
        self.level_index += 1
        
        return level
