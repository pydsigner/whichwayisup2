from .event_scripting import EventFrame, add_from_scope


class Player(object):
    functions = ['load', 'speech', 'face']
    
    def __init__(self, player, i18n):
        self.player = player
        self.i18n = i18n
        
    def load(self, scope, coords):
        
    
    def face(self, scope, direction):
        self.player.face(direction)
    
    def speech(self, scope, text):
        
