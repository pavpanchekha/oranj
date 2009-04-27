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
        return Module(mod.__dict__, mod.__name__)

OrObject.register(type(OrObject))
