import orobject

OrObject = orobject.OrObject

module_cache = {}

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
        if "$$name" in mod.__dict__: # If it doesn't have a name, I've already played with it
            return module_cache[mod.__dict__["$$name"]]
        
        d = mod.__dict__
        
        if "__package__" in d:
            p = d["__package__"]
            d["$$package"] = p
        if "__doc__" in d:
            p = d["__doc__"]
            d["$$doc"] = p
        
        if d["__name__"].startswith("pystdlib.") and d["__name__"].endswith("_or"):
            d["__name__"] = d["__name__"][9:-3]
        
        n = d["$$name"] = d["__name__"]
        p = mod.__path__[0] if "__path__" in d else "py://"
        
        ret = Module(d, n, p)
        module_cache[n] = ret
        return ret

OrObject.register(Module.from_py, type(orobject))
