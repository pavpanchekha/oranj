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
            raise NotImplementedError

    def isnil(self):
        return self.ispy() and self.topy() is None

    def tagged(self, tag):
        return self.has("$$tags") and tag in self.get("$$tags")

    def get(self, key):
        if key == "$$dict":
            return OrObject.from_py(self.dict)
        elif key in self.dict:
            val = self.dict[key]
        elif self.ispy() and hasattr(self.topy(), key):
            return getattr(self.topy(), key)
        else:
            raise AttributeError(key + " is not an attribute of " + repr(self))

        if self.ispy() or not isinstance(val, OrObject) or key in ("$$class", ) or not callable(val):
            return val
        elif val.tagged("Static"):
            return val
        elif val.tagged("Class"):
            if isinstance(self.get("$$class"), OrObject):
                def classmethod_wrapper(*args, **kwargs):
                    return val(self.get("$$class"), *args, **kwargs)
            else:
                def classmethod_wrapper(*args, **kwargs):
                    return val(self, *args, **kwargs)
            return classmethod_wrapper
        elif isinstance(self.get("$$class"), OrObject):
            def instancemethod_wrapper(*args, **kwargs):
                return val(self, *args, **kwargs)
            return instancemethod_wrapper
        else:
            return val

    def set(self, key, value):
        self.dict[key] = value

    def delete(self, key):
        try:
            del self.dict[key]
        except KeyError:
            delattr(self.topy(), key)

    def has(self, key):
        return key in self.dict or self.ispy() and hasattr(self.topy(), key)

    def __str__(self):
        if self.has("$$str"):
            return str(self.get("$$str")())
        elif self.ispy():
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
        if isinstance(self.get("$$class"), OrObject) and \
            self.get("$$class").has("$$repr"):
            return str(self.get("$$class").get("$$repr")(self))
        elif self.has("$$repr"):
            return str(self.get("$$repr")())
        elif self.ispy():
            return repr(self.topy())
        else:
            return self.__str__()

    def __eq__(self, other):
        a = self.topy() if self.ispy() else self
        b = other.topy() if hasattr(other, "ispy") and other.ispy() else other

        return a == b

    def __hash__(self):
        if self.ispy():
            try:
                return hash(self.topy())
            except TypeError:
                return id(self.topy())
        else:
            return id(self)

    def del_(self):
        if self.ispy() and hasattr(self.topy(), "__del__"):
            return self.topy().__del__
        elif self.has("$$del"):
            return self.get("$$del")()

    def __iter__(self):
        if self.ispy() and hasattr(self.topy(), "__iter__"):
            import itertools
            return itertools.imap(OrObject.from_py, self.topy().__iter__())
        elif self.has("$$iter"):
            return self.get("$$iter")()
        else:
            return AttributeError("Iteration not supported by %s" % repr(self))

    def __nonzero__(self):
        if self.ispy():
            return bool(self.topy())
        elif self.has("$$bool"):
            return self.get("$$bool")()
        else:
            return True
    
    def __getattr__(self, key):
        if key in self.__dict__ and key.startswith("__") and \
            key not in ("__class__", "__name__",
            "__dict__", "__weakref__", "__getattr__", "__setattr__",
            "__delattr__"):
            
            setattr(OrObject, key, mk_method(key))
            
            def wrap_method(*args, **kwargs):
                return getattr(OrObject, key)(self, *args, **kwargs)
            
            return wrap_method
        elif key in self.__dict__:
            return self.__dict__(key)
        else:
            raise AttributeError

    @classmethod
    def register(cls, new, *args):
        for i in args:
            cls.overrides[i] = new

    @staticmethod
    def from_py(obj):
        if isinstance(obj, OrObject): return obj

        if type(obj) in OrObject.overrides:
            return OrObject.overrides[type(obj)](obj)

        n = obj.__name__ if hasattr(obj, "__name__") else "[anon]"
        c = type(obj) if hasattr(obj, "__class__") else None
        np = OrObject(n, c)

        np.set("$$python", obj)
        return np

def mk_method(name):
    def method_wrapper(self, *args):
        if self.ispy() and hasattr(self.topy(), name) and all(not hasattr(i, "ispy") or i.ispy() for i in args):
            args = map(lambda x: x.topy() if hasattr(x, "ispy") else x, args)
            obj = getattr(self.topy(), name)
            return obj(*args)
        else:
            if "attr" in name:
                raise AttributeError("Object does not support this operation")
            elif name == "__nonzero__":
                return True
            else:
                raise NotImplementedError

    return method_wrapper
