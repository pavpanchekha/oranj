from orobject import OrObject

class Module(OrObject):
    class_name = "module"

    def __init__(self, dict, name="???", path="py://"):
        OrObject.__init__(self, name, Module)
        self.dict.update(dict)
        
        if path:
            self.dict["$$path"] = path

    def ispy(self): return False
    def topy(self): return NotImplemented

    @staticmethod
    def from_py(mod):
        d = mod.__dict__
        
        if "__package__" in d:
            p = d["__package__"]
            del d["__package__"]
            d["$$package"] = p
        if "__doc__" in d:
            p = d["__doc__"]
            del d["__doc__"]
            d["$$doc"] = p
        
        n = d["__name__"]
        del d["__name__"]
        
        p = mod.__path__[0] if "__path__" in d else "py://"
        if "__path__" in d:
            del d["__path__"]
        
        return Module(d, n, p)

OrObject.register(type(OrObject))
