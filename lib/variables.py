'''A very, very simple module for storing config.
Separated from the util module to avoid import loops.'''

class Variables(object):
    vdict = {}
    
    def __getitem__(self, key):
        return self.vdict[key]
    
    def __setitem__(self, key, value):
        self.vdict[key] = value
    
    def __contains__(self, key):
        return key in self.vdict
  
variables = Variables()
