#!/usr/bin/env python

from __future__ import division

class ContinueI(Exception): pass
class BreakI(Exception): pass

def orpy(name):
    def dec(f):
        def t(self, *args, **kwargs):
            if "$$python" in self.dict:
                f(self.get("$$python"), *args, **kwargs)
            else:
                return getattr(self, name)(*args, **kwargs)
        return t
    return dec

def clear_screen():
    import os
    if os.name == "posix":
        # Unix/Linux/MacOS/BSD/etc
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        # DOS/Windows
        os.system('CLS')
    else:
        # Fallback for other operating systems.
        print '\n' * 100

class OrObject(object):
    py2np = {
        "__init__": "$$new",
        "__del__": "$$del",
        # Implement __str__ somehow
        "__lt__": "$$lt",
        "__le__": "$$le",
        "__gt__": "$$gt",
        "__ge__": "$$ge",
        "__eq__": "$$eq",
        "__ne__": "$$ne",
        "__call__": "$$call",
        "__contains__": "$$in",
        "__add__": "$$add",
        "__sub__": "$$sub",
        "__mul__": "$$mus",
        "__pow__": "$$exp",
        "__truediv__": "$$div",
        "__floordiv__": "$$floor",
        "__mod__": "$$mod",
        "read": "$$output",
        "write": "$$input",
    }

    def __init__(self, name="", classobj=None):
        self.dict = {}

        if name:
            self.set("$$name", name)
        if classobj:
            self.set("$$class", classobj)

    def __getattr__(self, name):
        return self.__dict__["dict"][name]

    def get(self, key):
        return self.dict[key]

    def set(self, key, value):
        self.dict[key] = value

    def __str__(self):
        if "$$python" in self.dict:
            return str(self.get("$$python"))
        else:
            return "<" + str(self.get("$$class")) + " " + self.get("$$name") + ">"

    def __repr__(self):
        if "$$python" in self.dict:
            return repr(self.get("$$python"))
        else:
            return "<" + str(self.get("$$class")) + " " + self.get("$$name") + ">"

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
            # TODO: implement iter
            pass
        
    @classmethod
    def from_py(cls, obj, override=False):
        if isinstance(obj, cls) and not override: return obj
        
        if hasattr(obj, "__name__"):
            n = obj.__name__
        else:
            n = ""

        if hasattr(obj, "__class__"):
            c = obj.__class__
        else:
            c = None

        np = cls(n, c)

        for i in dir(obj):
            if i in ("__name__", "__class__"):
                continue
            elif i in cls.py2np:
                np.set(cls.py2np[i], getattr(obj, i))
            elif i.startswith("__") and i.endswith("__"):
                np.set("$$" + i[2:-2], getattr(obj, i))
            else:
                #TODO: make this recursive
                np.set(i, getattr(obj, i))
        np.set("$$python", obj)
        return np

class InheritDict:
    def __init__(self, parent=None):
        self.parent = parent
        self.dict = {}

    def update(self, keys={}):
        self.dict.update(keys)

    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        else:
            try:
                a = self.parent[key]
                self[key] = a # Cache lookup
                return a
            except TypeError:
                raise AttributeError("Key not in InheritDict")

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __delitem__(self, key):
        del self.dict[key]

    def __contains__(self, key):
        return key in self.dict or self.parent and key in self.parent

    def keys(self):
        if self.parent:
            return list(self.dict.keys()) + self.parent.keys()
        else:
            return list(self.dict.keys())

def simpleop(f, name):
    def t(*args, **kwargs):
        if all(hasattr(i, "dict") and "$$python" in i.dict for i in args):
            args = [i.get("$$python") for i in args]
            for i in kwargs:
                kwargs[i] = kwargs[i].get("$$python")
            return OrObject.from_py(f(*args, **kwargs))
        elif any(not hasattr(i, "dict") for i in args):
            return OrObject.from_py(f(*args, **kwargs))
        else:
            print args[0]
            try:
                return args[0].get("$$" + name)(*args[1:], **kwargs)
            except:
                args2 = [args[0]] + list(args[2:])
                return args[1].get("$$r_" + name)(*args2, **kwargs)
    return t

add = simpleop(lambda x, y: x + y, "add")
sub = simpleop(lambda x, y: x - y, "sub")
mul = simpleop(lambda x, y: x * y, "mul")
div = simpleop(lambda x, y: x / y, "div")
exp = simpleop(lambda x, y: x ** y, "exp")
floor = simpleop(lambda x, y: x // y, "floor")
mod = simpleop(lambda x, y: x % y, "mod")
divis = simpleop(lambda x, y: y % x == 0, "divis")
or_ = simpleop(lambda x, y: x or y, "or")
and_ = simpleop(lambda x, y: x and y, "and")
not_ = simpleop(lambda x: not x, "not")
in_ = simpleop(lambda x, y: x in y, "in")
not_in = simpleop(lambda x, y: x not in y, "not_in")
is_ = simpleop(lambda x, y: isinstance(x, y), "is")
is_not = simpleop(lambda x, y: not isinstance(x, y), "is_not")
lt = simpleop(lambda x, y: x < y, "lt")
gt = simpleop(lambda x, y: x > y, "gt")
le = simpleop(lambda x, y: x <= y, "le")
ge = simpleop(lambda x, y: x >= y, "ge")
ne = simpleop(lambda x, y: x != y, "ne")
eq = simpleop(lambda x, y: x == y, "eq")
input = simpleop(lambda x, y: x.read(y), "input")
output = simpleop(lambda x, y: x.write(y), "output")
uplus = simpleop(lambda x: +x, "uplus")
uminus = simpleop(lambda x: -x, "uminus")

def call(obj, *args, **kwargs):
    if all(hasattr(i, "dict") and "$$python" in i.dict for i in args) and all("$$python" in i.dict for k, i in kwargs.items()):
        args = [i.get("$$python") for i in args]
        for i in kwargs:
            kwargs[i] = kwargs[i].get("$$python")
        obj = obj.get("$$python")
        
        return OrObject.from_py(obj(*args, **kwargs))
    else:
        return obj.get("$$call")(*args, **kwargs)

def getattr_(x, y):
    return OrObject.from_py(x.get(y))

def indexer(x, y):
    if type(y) == type(()):
        return map(lambda y: x[y], y)
    else:
        return x[y]

getindex_ = simpleop(indexer, "getindex")
