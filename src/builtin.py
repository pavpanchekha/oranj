#!/bin/false

from objects.orobject import OrObject
from objects.function import Function
from objects.number import Number
from objects.file import File
import objects.console as console
import types
import intplib
import lib

def expose(obj):
    if hasattr(obj, "__call__"):
        return Function.new(obj)
    else:
        return OrObject.from_py(obj)
    
builtin = intplib.InheritDict()
builtin.update({
        "int": expose(lib.toint),
        "num": expose(Number),
        
        "io": console.io,
        "file": expose(File),
        "input": Function.new(console.input),
        "output": Function.new(console.output),
        "error": Function.new(console.error),

        "repr": expose(repr),
        "join": expose(lib.join),
        "range": expose(range),
        "pytype": expose(type),
})
