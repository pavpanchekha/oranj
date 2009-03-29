from orobject import OrObject
from inheritdict import InheritDict
import types

class ReturnI(Exception): pass
class Function(OrObject):
    class_name = "fn"
    
    def __init__(self, intp, arglist=None, block=None, doc="", rettype=""):
        if arglist is None:
            self.fn = intp
            OrObject.__init__(self, self.fn.__name__, Function)
            self.set("$$doc", self.fn.__doc__)
            self.set("$$call", self.fn)
        else:
            OrObject.__init__(self, "[anon]", Function)
            self.set("$$doc", doc)
            self.set("$$call", self._call__)
            
            self.arglist = arglist
            self.realargs = len([True for i in arglist if i[0] == "ARG"])
            self.rettype = rettype
            self.block = block
            self.intp = intp
            self.cntx = InheritDict(intp.curr)

    def __call__(self, *args, **kwargs):
        if hasattr(self, "intp"):
            return self._call__(*args, **kwargs)
        else:
            return self.fn(*args, **kwargs)
    
    def _call__(self, *args, **kwargs):
        self.intp.cntx.append(self.cntx)
        
        argp = 0
        
        if len(args) == self.realargs:
            # Yay, easy scenario
            for i in self.arglist:
                if i[0] == "ARG":
                    if len(i) in (2, 4):
                        self.cntx[i[1][1]] = args[argp]
                    elif len(i) in (3, 5):
                        self.cntx[i[2][1]] = args[argp]
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
                        self.cntx[i[1][1]] = args[argp]
                    elif len(i) in (3, 5):
                        self.cntx[i[2][1]] = args[argp]
                    argp += 1
        else:
            # Also awww
            extra = len(arglist) - len(args)
            
            for i in self.arglist:
                if i[0] == "ARG":
                    if len(i) in (2, 4):
                        self.cntx[i[1][1]] = args[argp]
                    elif len(i) in (3, 5):
                        self.cntx[i[2][1]] = args[argp]
                    argp += 1
                elif i[0] == "UNWRAPABLE":
                    self.cntx[i[1][1]] = args[argp:argp+extra]
                    argp += extra
        
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
    types.UnboundMethodType)
