from orobject import OrObject

class String(str, OrObject):
    def __init__(self, *args, **kwargs):
        str.__init__(self)
        OrObject.__init__(self, "[anon]", String)
    
    def ispy(self): return True
    def topy(self): return self
    
    def __repr__(self):
        return "\"" + super(String, self).__repr__()[1:-1] + "\""

#OrObject.register(String, type(""))
