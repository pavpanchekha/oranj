# -*- coding: utf-8 -*-
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
            self.block = block
            self.intp = intp
            self.parcntx = self.intp.curr

            self.argtypes = [i[0] for i in arglist]
            self.argnames = [i[1] for i in arglist if not i[0].startswith("UNWRAPPABLE")]
            self.simpleargs = [i[1] for i in arglist if i[0] == "ARG"]

    def ispy(self): return not hasattr(self, "intp")
    def topy(self): return self.fn if hasattr(self, "fn") else NotImplemented

    def __str__(self):
        return "<fn " + str(self.get("$$name")) + ">"

    def __repr__(self):
        return str(self)

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

        extra_args = len(args) + len([i for i in kwargs if i in self.simpleargs]) - len(self.simpleargs)
        if "UNWRAPPABLE" in self.argtypes:
            # *args have higher priority than arg=stuff
            # So just stick the extra args into the first
            # UNWRAPPABLE we find

            argp = 0
            for i in self.arglist:
                if i[0] == "ARG":
                    if i[1] in kwargs:
                        cntx[i[1]] = kwargs[i[1]]
                        del kwargs[i[1]]
                    else:
                        cntx[i[1]] = args[argp]
                        argp += 1
                elif i[0] == "DEFARG":
                    if i[1] in kwargs:
                        cntx[i[1]] = kwargs[i[1]]
                        del kwargs[i[1]]
                    else:
                        cntx[i[1]] = self.intp.run(i[2])
                elif i[0] == "UNWRAPPABLE":
                    if extra_args >= 0:
                        cntx[i[1]] = OrObject.from_py(args[argp:argp+extra_args])
                        argp += extra_args
                        extra_args = -1
        else:
            argp = 0
            for i in self.arglist:
                if i[0] == "ARG":
                    if i[1] in kwargs:
                        cntx[i[1]] = kwargs[i[1]]
                        del kwargs[i[1]]
                    else:
                        cntx[i[1]] = args[argp]
                        argp += 1
                elif i[0] == "DEFARG":
                    if i[1] in kwargs:
                        cntx[i[1]] = kwargs[i[1]]
                        del kwargs[i[1]]
                    elif extra_args > 0:
                        cntx[i[1]] = args[argp]
                        argp += 1
                        extra_args -= 1
                elif i[0] == "UNWRAPPABLE":
                    cntx[i[1]] = OrObject.from_py([])

        for i in (arg[1] for arg in self.arglist if arg[0] == "UNWRAPPABLEKW"):
            cntx[i] = kwargs.copy()

        if self.intp.opts["logger"]:
            summary = ": " + str(self.get("$$doc"))
            args = cntx.dict
            arglist = ["%s=%s" % (i, cntx[i]) for i in sorted([i for i in cntx.dict.keys() if i != "block"], key=lambda x: self.argnamelist.index(x))]
            summary = "%s(%s)%s" % (str(self), ", ".join(arglist), summary)
            
            self.intp.opts["logger"].push(summary)
        
        self.intp.level += 1
        #self.intp.stmtstack.append(self.intp.cstmt)
        try:
            c = self.intp.run(self.block)
        except ReturnI, e:
            if self.intp.opts["logger"]: self.intp.opts["logger"].pop()
            
            if e.args:
                a = list(e.args) if len(e.args) > 1 else e.args[0]
                return OrObject.from_py(a)
            else:
                return
        finally:
            if self.intp.opts["logger"]: self.intp.opts["logger"].pop(certain=False)
            self.intp.level -= 1
            self.intp.cntx.pop()
        return OrObject.from_py(c)

OrObject.register(Function, types.BuiltinFunctionType,
    types.BuiltinMethodType, types.ClassType, types.FunctionType,
    types.GeneratorType, types.LambdaType, types.MethodType,
    types.UnboundMethodType, "a".__add__.__class__) # "a".__add__.__class__ -> method-wrapper type
