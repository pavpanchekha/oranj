#!/usr/bin/env python

class OrPython(OrObject):
    def __init__(self, obj):
        if hasattr(obj, "__name__"):
            n = obj.__name__
        else:
            n = ""

        if hasattr(obj, "__class__"):
            c = obj.__class__
        else:
            c = None
        
        OrObject.__init__(self, n, c)

        self.set(obj)

obj = OrObject("obj", None)

class int(OrObject):
    name = "int"
    class = int
