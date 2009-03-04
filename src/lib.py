#!/usr/bin/env python

import sys
import decimal

class Inputable(object):
    def read(valid_f=None, coerce_f=None): pass

class Outputable(object):
    def write(*args): pass
    def error(*args): pass

class Terminal(Inputable, Outputable, object):
    def read(self, prompt="", valid_f=None, coerce_f=None):
        """
        Get user input, validate, and coerce it if necessary.

        prompt: User prompt
        valid_f: the validation function. Should throw exception if input is invalid
        coerce_f: the coersion function. Should return coerced value.

        If only one function is passed (valid_f is given, coerce_f is not),
        valid_f is assumed to return coerced value.
        """

        txt = raw_input(prompt)

        if valid_f is None and coerce_f is None:
            return txt
        elif coerce_f is None:
            try:
                return valid_f(txt)
            except:
                print "Invalid input; please try again."
                return input(prompt, valid_f, coerce_f)
        else:
            try:
                valid_f(txt)
            except:
                print "Invalid input; please try again."
                return input(prompt, valid_f, coerce_f)
            else:
                return coerce_f(txt)

    def write(self, *args, **kwargs):
        """
        Print *args to file standard output.

        @param sep: Separator between args. Default " "
        @type sep: C{str}
        @param end: Appended to string. Default "\n"
        @type end: C{str}
        """

        p = {
            "sep": " ",
            "end": "\n"
        }

        p.update(kwargs)

        f = sys.stdin
        sep = p["sep"]
        end = p["end"]

        sys.stdout.write(sep.join(map(str, args)))
        sys.stdout.write(str(end))
        return self

    def error(self, *args):
        sys.stderr.write("\n".join(map(repr, args)) + "\n")
        return self

term = Terminal()
input = term.read
output = term.write
error = term.error

def join(arr, s):
    return s.join(map(str, arr))

class Integer(long):
    def __init__(self, value, base=10):
        if type(value) == type(""):
            value = value.replace(" ", "")

            self._val = int(value, base)
        else:
            self._val = value

    def __cmp__(self, other):
        if type(other) != Integer:
            return self._val.__cmp__(other)
        return self._val.__cmp__(other._val)
        
    def __div__(self, other):
        return Decimal(self._val) / Decimal(other._val)

    def __rdiv__(self, other):
        return Integer.__div__(other, self)

    def __truediv__(self, other):
        return Integer.__div__(self, other)

    def __rtruediv__(self, other):
        return Integer.__div__(other, self)
        
    def __len__(self):
        return self

    def __iter__(self):
        return xrange(self).__iter__()
    
    def __str__(self):
        s = super(Integer, self).__str__()
        if s.endswith("L"):
            s = s[:-1]
        return s

    def __coerce__(self, other):
        return other.__coerce__(self)

def get_val(i):
    if hasattr(i, "_val"):
        return i._val
    else:
        return i
    
def add_func_int(i):
    i = "__%s__" % i

    def t(*args, **kwargs):
        args = map(get_val, args)

        try:
            return Integer(getattr(int, i)(*args, **kwargs))
        except:
            try:
                return Integer(getattr(long, i)(*args, **kwargs))
            except:
                return NotImplemented
    
    setattr(Integer, i, t)
    
for i in ["abs", "add", "and", "divmod", "float", "floordiv", "index", \
          "invert", "lshift", "mod", "mul", "neg", "or", "pos", "pow", "radd", "rand", \
          "rdivmod", "rfloordiv", "rlshift", "rmod", "rmul", "ror", "rpow", \
          "rrshift", "rshift", "rsub", "rxor", "sub", "xor"]:

    add_func_int(i)

defaults = decimal.getcontext()
defaults.prec = 28
defaults.rounding = decimal.ROUND_HALF_EVEN
defaults.capitals = 0

Infinity = decimal.Inf

class Decimal(decimal.Decimal):
    def __init__(self, value):
        if type(value) == type(""):
            value = value.replace(" ", "")
        elif hasattr(value, "_val"):
            value = value._val
        
        decimal.Decimal.__init__(self, value)

    def __sub__(self, other):
        s = super(Decimal, self)
        o = super(Decimal, other)
        return Decimal(s - o)

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        s = super(Decimal, self).__str__()
        
        if "." not in s:
            if "e" not in s:
                ipart = s
                fpart = ""
                epart = ""
            else:
                ipart = s[:s.find("e")]
                fpart = ""
                epart = s[s.find("e"):]
        else:
            if "e" not in s:
                ipart = s[:s.find(".")]
                fpart = s[s.find("."):][:4]
                epart = ""
            else:
                ipart = s[:s.find(".")]
                fpart = s[s.find("."):s.find("e")][:5]
                epart = s[s.find("e"):]

        if len(fpart) > 4:
            fpart = fpart[:4]
        elif fpart.startswith(".") and len(fpart) < 4:
            fpart += "0" * (4 - len(fpart))
        
        return ipart + fpart + epart

    def __coerce__(self, other):
        if type(other) == Integer:
            return (self, Decimal(other._val))
        else:
            return (self, Decimal(other))

def add_func_dec(i):
    i = "__%s__" % i

    def t(*args, **kwargs):
        args = map(get_val, args)

        try:
            return Decimal(getattr(decimal.Decimal, i)(*args, **kwargs))
        except:
            return NotImplemented
    
    setattr(Decimal, i, t)
    
for i in ["abs", "add", "div", "divmod", "floordiv", "mod", "mul", "neg", "pos", "pow", \
              "sub", "radd", "rdiv", "rdivmod", "rfloordiv", "rmod", "rmul", "rpow", \
              "rsub", "rtruediv"]:

    add_func_dec(i)
