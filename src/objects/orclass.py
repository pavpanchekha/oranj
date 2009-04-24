# -*- coding: utf-8 -*-
from orobject import OrObject
from inheritdict import InheritDict
import types

class OrClass(OrObject):
    class_name = "class"

    def __init__(self, intp, parents=None, tags=None, block=None, doc=""):
        if parents is None:
            # Native python class
            pass
        else:
            OrObject.__init__(self)
            self.dict = InheritDict(*(list(i.dict for i in parents if hasattr(i, "dict"))))
            self.set("$$name", "[anon]")
            self.set("$$class", OrClass)
            self.set("$$doc", doc)
            self.set("$$call", self.__call__)
            self.set("$$tags", OrObject.from_py(tags))
            intp.cntx.append(self.dict)

            self.intp = intp

            try:
                intp.run(block)
            except:
                raise
            finally:
                intp.cntx.pop()

    def ispy(self): return False
    def topy(self): return NotImplemented

    def __call__(self, *args, **kwargs):
        if "$$init" in self.dict:
            x = OrObject()
            x.dict = InheritDict(self.dict)
            x.set("$$name", "[anon]")
            x.set("$$class", self)

            cntx = InheritDict(self.intp.curr)
            # Strange as it is, a constructor is called in
            # the context of the call.
            # There's a thin layer for the special variables
            # this and block

            fn = self.dict["$$init"]
            cntx["block"] = self
            self.intp.cntx.append(cntx)
            fn(x, *args, **kwargs)
            return x
        else:
            x = OrObject()
            x.dict = InheritDict(self.dict)
            x.set("$$name", "[anon]")
            x.set("$$class", self)
            return x

