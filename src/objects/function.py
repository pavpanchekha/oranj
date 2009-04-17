from orobject import OrObject
from inheritdict import InheritDict
import functools
import types

class ReturnI(Exception): pass
class Function(OrObject):
    class_name = "fn"

    def __init__(self, intp, arglist=None, block=None, doc="", tags=[]):
        if arglist is None:
            self.fn = intp
            OrObject.__init__(self, self.fn.__name__, Function)
            self.set("$$doc", self.fn.__doc__)
            self.set("$$call", self.__call__)
        else:
            OrObject.__init__(self, "[anon]", Function)
            self.set("$$doc", doc)
            self.set("$$call", self.__call__)
            self.set("$$tags", OrObject.from_py(tags))
            
            self.arglist = arglist
            self.realargs = len([True for i in arglist if i[0] == "ARG"])
            self.block = block
            self.intp = intp
            self.parcntx = self.intp.curr

    def ispy(self): return not hasattr(self, "intp")
    def topy(self): return self.fn if hasattr(self, "fn") else NotImplemented
    
    def __str__(self):
        return "<fn " + self.get("$$name") + ">"
    
    def __repr__(self):
        return "<fn " + self.get("$$name") + ">"
            
    def __call__(self, *args, **kwargs):
        if hasattr(self, "intp"):
            return self._call__(*args, **kwargs)
        else:
            try:
                return self.fn(*args, **kwargs)
            except:
                pass
            
            if all(hasattr(i, "ispy") and i.ispy() for i in args) \
                    and all(hasattr(i, "ispy") and i.ispy() for k, i in kwargs.items()):

                args = [i.topy() for i in args]
                for i in kwargs:
                    kwargs[i] = kwargs[i].topy()

                return OrObject.from_py(self.fn(*args, **kwargs))

            return NotImplemented
    
    def _call__(self, *args, **kwargs):
        cntx = InheritDict(self.parcntx)
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
            skip = len(self.arglist) - len(args)
            
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
            extra = len(self.arglist) - len(args)
            
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

        cntx["block"] = self

        try:
            self.intp.run(self.block)
        except ReturnI, e:
            if e.args:
                a = list(e.args) if len(e.args) > 1 else e.args[0]
                return OrObject.from_py(a)
            else:
                return
        finally:
            self.intp.cntx.pop()

OrObject.register(Function, types.BuiltinFunctionType,
    types.BuiltinMethodType, types.ClassType, types.FunctionType,
    types.GeneratorType, types.LambdaType, types.MethodType,
    types.UnboundMethodType, "a".__add__.__class__) # "a".__add__.__class__ -> method-wrapper type
