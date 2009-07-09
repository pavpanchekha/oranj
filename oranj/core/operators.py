#!/usr/bin/env python
# -*- coding: utf-8 -*-

from objects.orobject import OrObject
import operator, types

def __mk_op(f, name, try_noconv=True):
    def t(*args):
        try:
            try:
                return OrObject.from_py(args[0].get("$$" + name)(*args[1:]))
            except AttributeError:
                args2 = [args[0]] + list(args[2:])
                return OrObject.from_py(args[1].get("$$r_" + name)(*args2))
        except (AttributeError, IndexError, TypeError):
            try:
                return OrObject.from_py(f(*args))
            except TypeError:
                if all(not hasattr(i, "ispy") or i.ispy() for i in args):
                    args = [i.topy() if i.ispy() else i for i in args]
                    return OrObject.from_py(f(*args))
                else:
                    return NotImplemented
    return t

add = __mk_op(operator.add, "add")
sub = __mk_op(operator.sub, "sub")
mul = __mk_op(operator.mul, "mul")
div = __mk_op(operator.div, "div")
exp = __mk_op(operator.pow, "exp")
floor = __mk_op(operator.floordiv, "floor")
mod = __mk_op(operator.mod, "mod")
divis = __mk_op(lambda x, y: y % x == 0, "divis")
or_ = __mk_op(operator.or_, "or")
and_ = __mk_op(operator.and_, "and")
not_ = __mk_op(operator.not_, "not")
in_ = __mk_op(lambda x, y: x in y, "in")
lt = __mk_op(operator.lt, "lt")
gt = __mk_op(operator.gt, "gt")
le = __mk_op(operator.le, "le")
ge = __mk_op(operator.ge, "ge")
ne = __mk_op(operator.ne, "ne")
eq = __mk_op(operator.eq, "eq")
input = __mk_op(lambda x, y: x.input(y), "input")
output = __mk_op(lambda x, y: x.output(y), "output")
uplus = __mk_op(operator.pos, "uplus")
uminus = __mk_op(operator.neg, "uminus")

def is_(obj, cls):
    if hasattr(cls, "ispy") and cls.ispy():
        cls = cls.topy()
    
    if type(cls) == type(""):
        if hasattr(obj.get("$$class"), "has") and type(obj.get("$$class").has) != types.UnboundMethodType and obj.get("$$class").has("$$tags"):
            return cls.topy() in obj.get("$$class").get("$$tags")
        else:
            return False
    
    try:
        r = isinstance(obj, cls)
    except TypeError:
        r = False

    if not r and hasattr(obj, "ispy") and obj.ispy():
        try:
            return isinstance(obj.topy(), cls)
        except TypeError:
            pass

    if hasattr(obj, "has") and obj.has("$$class"):
        return obj.get("$$class") == cls

    return r

def call(obj, *args, **kwargs):
    try:
        return OrObject.from_py(obj.get("$$call")(*args, **kwargs))
    except (AttributeError, TypeError):
        if all(not hasattr(i, "ispy") or i.ispy() for i in args) and all(not hasattr(i, "ispy") or i.ispy() for k, i in kwargs.items()) and obj.ispy():
            args = [i.topy() if i.ispy() else i for i in args]
            for i in kwargs:
                kwargs[i] = kwargs[i].topy() if kwargs[i].ispy() else kwargs[i]
            obj = obj.topy()

            return OrObject.from_py(obj(*args, **kwargs))
        else:
            raise TypeError(str(obj) + " is not callable")

def getattr_(x, y):
    if x.has("$$getattr"):
        return x.get("$$getattr", y)
    else:
        return OrObject.from_py(x.get(y))

def indexer(x, y):
    if type(x) in map(type, ((), [], {})):
        return map(lambda y: x[y], y)

    return x[y]

getindex_ = __mk_op(indexer, "getindex")

op_names = {
    "+": add, "-": sub,
    "*": mul, "/": div, "//": floor, "MOD": mod,
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
