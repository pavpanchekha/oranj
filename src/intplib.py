#!/usr/bin/env python

class ReturnI(Exception): pass

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
    def __init__(self, name="", classobj=None):
        self.dict = {}

        if name:
            self.set("$$name", name)
        if classobj:
            self.set("$$class", classobj)

    def ispy(self):
        return "$$python" in self.dict
    
    def get(self, key):
        if key in self.dict:
            return self.dict[key]
        elif self.ispy():
            return getattr(self.get("$$python"), key)

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
            if i.startswith("_") or i.startswith("im_") or i == "mro" or i.startswith("func_"):
                continue
            
            np.set(i, cls.from_py(getattr(obj, i)))
        
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
                raise AttributeError("Key not in InheritDict: " + key)

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
    if all(hasattr(i, "dict") and "$$python" in i.dict for i in args) and all("$$python" in i.dict for k, i in kwargs.items()) and obj.ispy():
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

op_names = {
    "+": add,
    "-": sub,
    "*": mul,
    "^": exp,
    "/": div,
    "//": floor,
    "|": divis,
    "mod": mod,
    "OR": or_,
    "AND": and_,
    "NOT": not_,
    "IN": in_,
    "NOT IN": not_in,
    "IS": is_,
    "IS NOT": is_not,
    "<": lt,
    ">": gt,
    "<=": le,
    ">=": ge,
    "=>": ge,
    "=<": le,
    "==": eq,
    "!=": ne,
    "<<": output,
    ">>": input,
    "U+": uplus,
    "U-": uminus,
    "GETATTR": getattr_,
    "GETINDEX": getindex_,
}

class Function(OrObject):
    def __init__(self, intp, arglist, block, doc="", rettype=""):
        OrObject.__init__(self)
        self.set("$$doc", doc)
        self.set("$$call", self.__call__)
        self.set("$$class", "fn")
        self.set("$$name", "[anon]")
        
        self.arglist = arglist
        self.realargs = len([True for i in arglist if i[0] == "ARG"])
        self.rettype = rettype
        self.block = block
        self.intp = intp
    
    def __call__(self, *args, **kwargs):
        cntx = InheritDict(self.intp.cntx[-1])
        self.intp.cntx.append(cntx)
        
        argp = 0
        
        if len(args) == self.realargs:
            # Yay, easy scenario
            for i in self.arglist:
                if i[0] == "ARG":
                    if len(i) in (2, 4):
                        cntx[i[1][1]] = args[argp]
                    elif len(i) in (3, 5):
                        cntx[i[2][1]] = args[argp]
                    argp += 1
        elif len(args) < self.realargs:    
            # Awww
            skip = len(arglist) - len(args)
            
            for i in self.arglist:
                if i[0] == "ARG":
                    if len(i) in (4, 5) and skip:
                        skip -= 1
                        continue
                    elif len(i) in (2, 4):
                        cntx[i[1][1]] = args[argp]
                    elif len(i) in (3, 5):
                        cntx[i[2][1]] = args[argp]
                    argp += 1
        else:
            # Also awww
            extra = len(arglist) - len(args)
            
            for i in self.arglist:
                if i[0] == "ARG":
                    if len(i) in (2, 4):
                        cntx[i[1][1]] = args[argp]
                    elif len(i) in (3, 5):
                        cntx[i[2][1]] = args[argp]
                    argp += 1
                elif i[0] == "UNWRAPABLE":
                    cntx[i[1][1]] = args[argp:argp+extra]
                    argp += extra
        
        try:
            self.intp.run(self.block)
        except ReturnI, e:
            if e.args:
                a = list(e.args) if len(e.args) > 1 else e.args[0]
                return OrObject.from_py(a)
            else:
                return
