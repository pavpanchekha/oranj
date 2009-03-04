#!/bin/false

import lib
import intplib

def expose(obj):
    return intplib.OrObject.from_py(obj)
    
builtin = intplib.InheritDict()
builtin.update({
        "int": expose(lib.Integer),
        "dec": expose(lib.Decimal),
        
        "term": expose(lib.term),
        "input": expose(lib.input),
        "output": expose(lib.output),
        "error": expose(lib.error),

        "repr": expose(repr),
        "join": expose(lib.join),
        "range": expose(range),
})
