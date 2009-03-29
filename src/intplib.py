#!/usr/bin/env python

from objects.orobject import OrObject
from objects.function import Function, ReturnI
from objects.inheritdict import InheritDict
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

def simpleop(f, name):
    def t(*args):
        try:
            try:
                return args[0].get("$$" + name)(*args[1:])
            except KeyError:
                args2 = [args[0]] + list(args[2:])
                return args[1].get("$$r_" + name)(*args2)
        except:
            raise
            if all(isinstance(i, OrObject) and i.ispy() for i in args):
                try:
                    return f(*args)
                except:
                    raise
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
is_ = simpleop(isinstance, "is")
lt = simpleop(operator.lt, "lt")
gt = simpleop(operator.gt, "gt")
le = simpleop(operator.le, "le")
ge = simpleop(operator.ge, "ge")
ne = simpleop(operator.ne, "ne")
eq = simpleop(operator.eq, "eq")
input = simpleop(lambda x, y: x.input(y), "input")
output = simpleop(lambda x, y: x.output(y), "output")
uplus = simpleop(operator.pos, "uplus")
uminus = simpleop(operator.neg, "uminus")

def call(obj, *args, **kwargs):
    try:
        return obj.get("$$call")(*args, **kwargs)
    except:
        if all(hasattr(i, "ispy") and i.ispy() for i in args) and all(hasattr(i, "ispy") and i.ispy() for k, i in kwargs.items()) and obj.ispy():
            args = [i.topy() for i in args]
            for i in kwargs:
                kwargs[i] = kwargs[i].topy()
            obj = obj.topy()
            
            return OrObject.from_py(obj(*args, **kwargs))

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
