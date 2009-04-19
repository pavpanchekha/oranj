# -*- coding: utf-8 -*-
# The definition of an OrObject

class OrObject(object):
    overrides = {}

    def __init__(self, name="[anon]", classobj=None):
        assert type(name) == type(""), "Name must be a string"

        self.dict = {}

        self.set("$$name", name)
        self.set("$$class", classobj)

    def ispy(self):
        return "$$python" in self.dict

    def topy(self):
        try:
            return self.dict["$$python"]
        except KeyError:
            return NotImplemented

    def tagged(self, tag):
        return self.has("$$tags") and tag in self.get("$$tags")

    def get(self, key):
        try:
            v = self.dict[key]
        except KeyError:
            if self.ispy():
                try:
                    return getattr(self.topy(), key)
                except:
                    pass
            raise AttributeError(key + " is not an attribute of " + repr(self))
        else:
            if self.ispy() or key in ("$$class", ) or not callable(v) or not isinstance(v, OrObject):
                return v
            else:
                if v.tagged("static"):
                    return v
                elif v.tagged("class"):
                    def classmethod_wrapper(*args, **kwargs):
                        return v(v.get("$$class"), *args, **kwargs)
                    return classmethod_wrapper
                else:
                    def instancemethod_wrapper(*args, **kwargs):
                        return v(self, *args, **kwargs)
                    return instancemethod_wrapper

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
        elif self.has("$$str"):
            return str(self.get("$$str")())
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
        elif self.has("$$repr"):
            return str(self.get("$$repr")())
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
            for i in [j for j in dir(obj) if j.startswith("__") and j.endswith("__") and not hasattr(cls, j) and j not in ("__class__", "__name__", "__dict__", "__weakref__")]:
                setattr(cls, i, mk_method(i))

        np.set("$$python", obj)
        return np

def mk_method(name):
    def method_wrapper(self, *args):
        if self.ispy() and hasattr(self.topy(), name) and all(not hasattr(i, "ispy") or i.ispy() for i in args):
            return getattr(self.topy(), name)(*map(lambda x: x.topy() if hasattr(x, "ispy") else x, args))
        else:
            if "attr" in name: # NotImplemented stupidly evaluates to True
                raise AttributeError("Object does not support this operation")
            else:
                return NotImplemented

    return method_wrapper