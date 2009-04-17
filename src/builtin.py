#!/bin/false

from objects.orobject import OrObject
from objects.function import Function
from objects.number import Number
from objects.file import File
from objects.inheritdict import InheritDict
from objects.ordict import OrDict
from objects.orddict import ODict
import objects.console as console
import objects.exception as exception
import types
import lib

expose = OrObject.from_py
builtin = InheritDict()
builtin.update({
    "int": expose(lib.toint),
    "num": expose(Number),
    "dict": expose(OrDict),
    "odict": expose(ODict),
    "set": expose(set),
    
    "io": expose(console.io),
    "file": expose(File),
    "input": expose(console.input),
    "output": expose(console.output),
    "error": expose(console.error),

    "repr": expose(repr),
    "join": expose(lib.join),
    "range": expose(range),
    "type": expose(lib.typeof),
    
    "dir": expose(lib.dirof),
    "reverse": expose(reversed),
    "sort": expose(sorted),
    "chr": expose(unichr),
    
#    "Exception": expose(exception.OrException)
    "Exception": expose(Exception),
})

stolen_builtins = [
    'abs', 'all', 'any', 'bool', 'callable', #buffer
    'classmethod', 'cmp', 'coerce', #chr (not as unichr)
    'dict', 'divmod', 'enumerate', #delattr
    'exit', 'filter', # frozenset
    'hash', 'id', #get/hasattr
    'iter', 'len', 'list',
    'map', 'max', 'min', 'ord', # object
    'range', 'repr', #property
    'round', 'set', 'slice', 'staticmethod', #setattr
    'str', 'sum', 'unicode', #super
    'zip'
]

for i in stolen_builtins:
    builtin[i] = expose(__builtins__[i])
