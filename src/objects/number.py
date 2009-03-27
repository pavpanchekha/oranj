from orobject import OrObject
import decimal
import operator

class Number(OrObject):
    def __init__(self, value, base=10):
        OrObject.__init__(self)
        self.set("$$class", "num")
        
        if type(value) == type(""):
            value = value.replace(" ", "")
            
            if "." in value or "e" in value:
                self._val = decimal.Decimal(value)
            else:
                self._val = int(value, base)
        elif hasattr(value, "_val"):
            self._val = value._val
        elif type(value) in (type(1), type(1L), decimal.Decimal):
            self._val = value
            if int(self._val) == self._val:
                self._val = int(self._val)
        elif type(value) == type(0.1):
            self._val = decimal.Decimal(str(value))
            if int(self._val) == self._val:
                self._val = int(self._val)
        else:
            raise TypeError("How am I supposed to make " + repr(value) + " a Number?")
    
    def ispy(self): return True
    def topy(self): return self._val

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
            s = str(self._val)
            
            if "." not in s:
                if "e" not in s:
                    ipart = s
                    fpart = ".000"
                    epart = ""
                else:
                    ipart = s[:s.find("e")]
                    fpart = ".000"
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
        else:
            s = str(self._val)
            if s[-1] == "L":
                s = s[:-1]
            return s
    
    def __index__(self):
        return int(self)
    
    def __int__(self):
        return self._val

def add_func(i):
    def t(*args):
        if any(type(i) != Number for i in args):
            return NotImplemented
    
        c = i
        args = map(lambda x: x._val, args)

        if not hasattr(operator, c):
            c += "_"

        try:
            s = getattr(operator, c)(*args)
            return Number(s)
        except:
            raise
            return NotImplemented
    return t
    
for i in ["abs", "add", "and", "divmod", "float", "floordiv", "index", \
          "invert", "lshift", "mod", "mul", "neg", "or", "pos", "pow", "radd", "rand", \
          "rdivmod", "rfloordiv", "rlshift", "rmod", "rmul", "ror", "rpow", \
          "rrshift", "rshift", "rsub", "rxor", "sub", "xor", "int"]:

    setattr(Number, "__%s__" % i, add_func(i))

class Infinity(Number):
    def __init__(self):
        self._val = decimal.Decimal("Infinity")
    
    def __str__(self):
        return "inf"

OrObject.register(Number, type(1), type(1L), decimal.Decimal, type(0.1))
