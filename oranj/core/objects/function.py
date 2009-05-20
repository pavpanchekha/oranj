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

            argtypes = [i[0] for i in arglist]
            self.argtypes = [argtypes.count("ARG"), argtypes.count("DEFARG"), argtypes.count("UNWRAPABLE"), argtypes.count("UNWRAPABLEKW")]
            self.realargs = self.argtypes[0] + self.argtypes[1]
            self.argnamelist = [i[1] for i in arglist]

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
            for i in self.arglist:
                if i[0] == "ARG":
                    cntx[i[-1]] = args[argp]
                    argp += 1
                elif i[0] == "DEFARG":
                    cntx[i[-2]] = args[argp]
                    argp += 1
                if i[0] == "UNWRAPABLE":
                    cntx[i[-1]] = OrObject.from_py([])
                # TODO: Multiple dispatch
        elif self.argtypes[0] <= len(args) < self.realargs:
            # We don't have enough arguments,
            # So we'll take defaults for the other arguments

            defeat = self.argtypes[1] - (self.realargs - len(args))
            for i in self.arglist:
                if i[0] == "ARG":
                    cntx[i[-1]] = args[argp]
                    argp += 1
                elif i[0] == "DEFARG":
                    if defeat:
                        cntx[i[-2]] = args[argp]
                        argp += 1
                        defeat -= 1
                    else:
                        cntx[i[-2]] = self.intp.run(i[-1])
                if i[0] == "UNWRAPABLE":
                    cntx[i[-1]] = OrObject.from_py([])
        elif len(args) > self.realargs and self.argtypes[2] > 0:
            # We've got too many arguments, so we'll have to eat some
            extra = len(args) - self.realargs
            for i in self.arglist:
                if i[0] == "ARG":
                    cntx[i[-1]] = args[argp]
                    argp += 1
                elif i[0] == "DEFARG":
                    cntx[i[-2]] = args[argp]
                    argp += 1
                elif i[0] == "UNWRAPABLE":
                    l = []
                    while extra > 0:
                        l.append(args[argp])
                        argp += 1
                        extra -= 1
                    cntx[i[-1]] = OrObject.from_py(l)
        else:
            raise TypeError("Wrong number of arguments")
            # TODO: make less stupid error message

        # TODO: keyword arguments

        cntx["block"] = self

        if self.intp.opts["logger"]:
            summary = ": " + str(self.get("$$doc"))
            args = cntx.dict
            arglist = ["%s=%s" % (i, cntx[i]) for i in sorted([i for i in cntx.dict.keys() if i != "block"], key=lambda x: self.argnamelist.index(x))]
            summary = "%s(%s)%s" % (str(self), ", ".join(arglist), summary)
            
            self.intp.opts["logger"].push(summary)
        
        self.intp.level += 1
        #self.intp.stmtstack.append(self.intp.cstmt)
        try:
            self.intp.run(self.block)
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

OrObject.register(Function, types.BuiltinFunctionType,
    types.BuiltinMethodType, types.ClassType, types.FunctionType,
    types.GeneratorType, types.LambdaType, types.MethodType,
    types.UnboundMethodType, "a".__add__.__class__) # "a".__add__.__class__ -> method-wrapper type
