from orobject import OrObject

class OrDict(dict, OrObject):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        OrObject.__init__(self, "[anon]", OrDict)
    
    def ispy(self): return True
    def topy(self): return self
    
    def __repr__(self):
        return "[" + dict(self).__repr__()[1:-1] + "]"
    
    def __str__(self):
        return "[" + dict(self).__str__()[1:-1] + "]"

OrObject.register(OrDict, type({}))
