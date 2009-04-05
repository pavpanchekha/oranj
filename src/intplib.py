#!/usr/bin/env python

from objects.orobject import OrObject
from objects.function import Function, ReturnI
import operator

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

def simpleop(f, name, try_noconv=True):
    def t(*args):
        try:
            try:
                return OrObject.from_py(args[0].get("$$" + name)(*args[1:]))
            except AttributeError:
                args2 = [args[0]] + list(args[2:])
                return args[1].get("$$r_" + name)(*args2)
        except (AttributeError, IndexError, TypeError):
            try:
                return f(*args)
            except TypeError:
                if all(hasattr(i, "ispy") and i.ispy() for i in args):
                    args = [i.topy() for i in args]
                    return OrObject.from_py(f(*args))
                else:
                    return NotImplemented
    return t

add = simpleop(operator.add, "add")
sub = simpleop(operator.sub, "sub")
mul = simpleop(operator.mul, "mul")
div = simpleop(operator.div, "div")
exp = simpleop(operator.pow, "exp")
floor = simpleop(operator.floordiv, "floor")
mod = simpleop(operator.mod, "mod")
divis = simpleop(lambda x, y: y % x == 0, "divis")
or_ = simpleop(operator.or_, "or")
and_ = simpleop(operator.and_, "and")
not_ = simpleop(operator.not_, "not")
in_ = simpleop(lambda x, y: x in y, "in")
lt = simpleop(operator.lt, "lt", False)
gt = simpleop(operator.gt, "gt", False)
le = simpleop(operator.le, "le", False)
ge = simpleop(operator.ge, "ge", False)
ne = simpleop(operator.ne, "ne", False)
eq = simpleop(operator.eq, "eq", False)
input = simpleop(lambda x, y: x.input(y), "input")
output = simpleop(lambda x, y: x.output(y), "output")
uplus = simpleop(operator.pos, "uplus")
uminus = simpleop(operator.neg, "uminus")

def is_(obj, cls):
    if cls.ispy() and type(cls.topy()) == type(""):
        if hasattr(obj.get("$$class"), "has") and obj.get("$$class").has("$$tags"):
            return cls.topy() in obj.get("$$class").get("$$tags")
        else:
            return False

    if hasattr(cls, "ispy") and cls.ispy():
        cls = cls.topy()

    try:
        r = isinstance(obj, cls)
    except TypeError:
        r = False

    if not r and hasattr(obj, "ispy") and obj.ispy():
        try:
            return isinstance(obj.topy(), cls)
        except TypeError:
            pass

    if obj.has("$$class"):
        return obj.get("$$class") == cls
    
    return r

def call(obj, *args, **kwargs):
    try:
        return OrObject.from_py(obj.get("$$call")(*args, **kwargs))
    except AttributeError:
        if all(hasattr(i, "ispy") and i.ispy() for i in args) and all(hasattr(i, "ispy") and i.ispy() for k, i in kwargs.items()) and obj.ispy():
            args = [i.topy() for i in args]
            for i in kwargs:
                kwargs[i] = kwargs[i].topy()
            obj = obj.topy()
            
            return OrObject.from_py(obj(*args, **kwargs))
        else:
            raise
            raise TypeError(str(obj) + " is not callable")
        
def getattr_(x, y):
    return OrObject.from_py(x.get(y))

def indexer(x, y):
    if type(y) == type(()):
        return map(lambda y: x[y], y)
    else:
        return x[y]

getindex_ = simpleop(indexer, "getindex")

op_names = {
    "+": add, "-": sub,
    "*": mul, "/": div, "//": floor, "mod": mod,
    "^": exp,
    "|": divis,
    "OR": or_, "AND": and_, "NOT": not_,
    "IN": in_,
    "IS": is_,
    "<": lt, ">": gt, "<=": le, ">=": ge, "=>": ge, "=<": le, "==": eq, "!=": ne,
    "<<": output, ">>": input,
    "U+": uplus, "U-": uminus,
    "GETATTR": getattr_,
    "GETINDEX": getindex_,
}
