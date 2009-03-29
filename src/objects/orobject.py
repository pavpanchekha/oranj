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

    def __str__(self):
        if "$$python" in self.dict:
            return str(self.get("$$python"))
        else:
            return "<" + \
                (str(self.get("$$class").__name__) + " ") if "$$class" in self.dict else "" + \
                (str(self.get("$$name")) if "$$name" in self.dict else "") + \
                ">"

    def __repr__(self):
        if "$$python" in self.dict:
            return repr(self.get("$$python"))
        else:
            return self.__str__()

    def __nonzero__(self):
        try:
            return bool(self.get("$$python"))
        except KeyError:
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
                setattr(np, i, print_wrapper(getattr(obj, i)))
        
        np.set("$$python", obj)
        return np

def print_wrapper(f):
    def x(*args, **kwargs):
        print f, args, kwargs
        return f(*args, **kwargs)
    return x
