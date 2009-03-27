from orobject import OrObject
from inheritdict import InheritDict
import types

class ReturnI(Exception): pass
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

    @classmethod
    def new(cls, fnc):
        b = OrObject()
        b.fnc = fnc
        b.set("$$doc", fnc.__doc__)
        b.set("$$call", fnc)
        b.set("$$python", fnc)
        b.set("$$class", "fn")
        b.set("$$name", fnc.__name__)
        
        return b

OrObject.register(Function.new, types.BuiltinFunctionType,
    types.BuiltinMethodType, types.ClassType, types.FunctionType,
    types.GeneratorType, types.LambdaType, types.MethodType,
    types.UnboundMethodType)
