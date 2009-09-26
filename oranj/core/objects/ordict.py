from orobject import OrObject

class OrDict(dict, OrObject):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        OrObject.__init__(self, "[anon]", OrDict)
    
    def ispy(self): return True
    def topy(self): return self
    
    def __repr__(self):
        if len(self):
            return "[" + dict(self).__repr__()[1:-1] + "]"
        else:
            return "[:]"
    
    def __str__(self):
        if len(self):
            return "[" + dict(self).__str__()[1:-1] + "]"
        else:
            return "[:]"

OrObject.register(OrDict, type({}))
