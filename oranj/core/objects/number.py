# -*- coding: utf-8 -*-
from orobject import OrObject
import decimal
import operator

defaults = decimal.getcontext()
defaults.prec = 28
defaults.rounding = decimal.ROUND_HALF_EVEN
defaults.capitals = 0

class Number(OrObject):
    class_name = "num"

    def is_inf(self):
        return self._val in (decimal._Infinity, decimal._NegativeInfinity, decimal._NaN)

    def is_nan(self):
        return self._val == decimal._NaN

    def __init__(self, value, base=10, intonlystr=False):
        OrObject.__init__(self, "", Number)
        self._val = 0

        if type(value) == type(""):
            value = value.replace(" ", "")

            if "." in value or "e" in value or value in ("Infinity", "-Infinity", "NaN"):
                if intonlystr:
                    raise TypeError(repr(value) + " not integral")
                else:
                    self._val = decimal.Decimal(value)
            else:
                self._val = int(value, base)
        elif hasattr(value, "_val"):
            self._val = value._val
        elif type(value) in (type(1), type(1L), decimal.Decimal):
            self._val = value
        elif type(value) == type(0.1):
            self._val = decimal.Decimal(str(value))
        else:
            raise TypeError("How am I supposed to make " + repr(value) + " a Number?")

        try:
            if int(self._val) == self._val or intonlystr:
                self._val = int(self._val)
        except OverflowError:
            pass

    def ispy(self): return True
    def topy(self):
        if type(self._val) == decimal.Decimal:
            return float(self._val)
        else:
            return self._val

    def __nonzero__(self):
        return self != 0

    def __cmp__(self, other):
        if type(other) != Number:
            try:
                other = Number(other)
            except TypeError:
                return NotImplemented
        try:
            return self._val.__cmp__(other._val)
        except:
            return -(other.__cmp__(self._val))

    def __div__(self, other):
        if not hasattr(other, "_val"):
            other = Number(other)
        
        s = self._val
        o = other._val
        a = s / o
        if type(a) == decimal.Decimal:
            return Number(a)
        else:
            return Number(decimal.Decimal(s) / o)

    def __len__(self):
        return self

    def __iter__(self):
        return xrange(self).__iter__()

    def __repr__(self):
        return str(self)

    def __str__(self):
        if type(self._val) == decimal.Decimal:
            if self.is_nan():
                return "NaN"
            elif self.is_inf():
                return ("-" if self._val < 0 else "") + "inf"

            s = str(self._val)

            if "e" not in s:
                ipart = s[:s.find(".")]
                fpart = s[s.find("."):]
                epart = ""
            else:
                ipart = s[:s.find(".")]
                fpart = s[s.find("."):s.find("e")]
                epart = s[s.find("e"):]

            fpart = fpart[:7]

            return ipart + fpart + epart
        else:
            s = str(self._val)
            if s[-1] == "L":
                s = s[:-1]
            return s

    def __index__(self):
        return int(self)

    def __int__(self):
        return int(self._val)

    def __hash__(self):
        return hash(self._val)

convtypes = map(type, (0.5, 1, 1L)) + [Number, decimal.Decimal]

def add_func(i):
    def t(*args):
        c = i

        argf = [x._val if type(x) == Number else x for x in args]
        
        if c in __builtins__:
            fn = __builtins__[c]
        else:
            if hasattr(operator, c + "_"):
                c += "_"
            try:
                fn = getattr(operator, c)
            except AttributeError:
                return NotImplemented

        try:
            s = fn(*argf)
        except TypeError:
            return NotImplemented
        else:
            try:
                return Number(s if type(s) in (int, long) else round(s, 28))
            except TypeError:
                return OrObject.from_py(s)
    return t

for i in ["abs", "add", "and", "divmod", "float", "floordiv", "index", \
          "invert", "lshift", "mod", "mul", "neg", "or", "pos", "pow", "radd", "rand", \
          "rdivmod", "rfloordiv", "rlshift", "rmod", "rmul", "ror", "rpow", \
          "rrshift", "rshift", "rsub", "rxor", "sub", "xor"]:

    setattr(Number, "__%s__" % i, add_func(i))

inf = Number("Infinity")

OrObject.register(Number, type(1), type(1L), decimal.Decimal, type(0.1))
