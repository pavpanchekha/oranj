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
        if self.ispy():
            return self.dict["$$python"]
        else:
            print self, self.dict
            return NotImplemented()
    
    def get(self, key):
        if key in self.dict:
            return self.dict[key]
        elif self.ispy():
            try:
                return getattr(self.topy(), key)
            except:
                pass
        raise AttributeError(key + " is not an attribute of " + repr(self))

    def set(self, key, value):
        self.dict[key] = value

    def __str__(self):
        if "$$python" in self.dict:
            return str(self.get("$$python"))
        else:
            return "<" + str(self.get("$$class")) + " " + self.get("$$name") + ">"

    def __repr__(self):
        return self.__str__()

    def __nonzero__(self):
        if "$$python" in self.dict:
            return bool(self.get("$$python"))
        else:
            # TODO: implement bool
            return True

    def __iter__(self):
        if "$$python" in self.dict:
            return iter(self.get("$$python"))
        else:
            raise TypeError("object is not iterable")
    
    def __call__(self, *args, **kwargs):
        if "$$python" in self.dict:
            return self.get("$$python")(*args, **kwargs)
        else:
            raise TypeError("object is not callable")
    
    @classmethod
    def register(cls, new, *args):
        for i in args:
            cls.overrides[i] = new
    
    @classmethod
    def from_py(cls, obj, override=False):
        if isinstance(obj, cls) and not override: return obj
        if type(obj) in cls.overrides:
            return cls.overrides[type(obj)](obj)
        
        n = obj.__name__ if hasattr(obj, "__name__") else ""
        c = obj.__class__ if hasattr(obj, "__class__") else ""
        np = cls(n, c)

        for i in dir(obj):
            if not any(map(i.startswith, ("_", "im_", "func_"))) and i != "mro":
                np.set(i, cls.from_py(getattr(obj, i)))
        
        np.set("$$python", obj)
        return np
