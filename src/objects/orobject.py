# The definition of an OrObject

class OrObject(object):
    overrides = {}

    def __init__(self, name="", classobj=None):
        self.dict = {}

        if name:
            self.set("$$name", name)
        if classobj:
            self.set("$$class", classobj)

    def ispy(self):
        return "$$python" in self.dict

    def topy(self):
        try:
            return self.dict["$$python"]
        except KeyError:
            return NotImplemented
    
    def get(self, key):
        try:
            return self.dict[key]
        except KeyError:
            if self.ispy():
                try:
                    return OrObject.from_py(getattr(self.topy(), key))
                except:
                    pass
            raise AttributeError(key + " is not an attribute of " + repr(self))

    def set(self, key, value):
        self.dict[key] = value
    
    def delete(self, key):
        try:
            del self.dict[key]
        except KeyError:
            delattr(self.topy(), key)
    
    def has(self, key):
        return key in self.dict or hasattr(self.topy(), key)

    def __str__(self):
        if self.ispy():
            return str(self.topy())
        else:
            s = "<"
            
            if self.has("$$class"):
                if isinstance(self.get("$$class"), OrObject) and self.get("$$class").has("$$name"):
                    s += str(self.get("$$class").get("$$name")) + " "
                elif hasattr(self.get("$$class"), "__name__"):
                    if hasattr(self.get("$$class"), "class_name"):
                        s += self.get("$$class").class_name + " "
                    else:
                        s += str(self.get("$$class").__name__) + " "
            
            if self.has("$$name"):
                s += str(self.get("$$name"))
            
            return s + ">"

    def __repr__(self):
        if self.ispy():
            return repr(self.topy())
        else:
            return self.__str__()
    
    @classmethod
    def register(cls, new, *args):
        for i in args:
            cls.overrides[i] = new
    
    @classmethod
    def from_py(cls, obj, rich=True):
        """ rich means that __x__ methods will be copied """
        if isinstance(obj, cls): return obj
        
        if type(obj) in cls.overrides:
            return cls.overrides[type(obj)](obj)

        n = obj.__name__ if hasattr(obj, "__name__") else ""
        c = type(obj) if hasattr(obj, "__class__") else ""
        np = cls(n, c)

        if rich:
            for i in [j for j in dir(obj) if j.startswith("__") and j.endswith("__") and j not in ("__class__", "__name__", "__dict__", "__weakref__")]:
                setattr(np, i, getattr(obj, i))
        
        np.set("$$python", obj)
        return np
