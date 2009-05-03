#!/bin/false
# -*- coding: utf-8 -*-

from objects.orobject import OrObject
from objects.function import Function
from objects.number import Number
from objects.file import File
from objects.inheritdict import InheritDict
from objects.ordict import OrDict
from objects.orddict import ODict
import objects.console as console
import objects.exception as exception
import objects.orstring as orstring
import types
import lib

def expose(r, n=""):
    v = OrObject.from_py(r)
    if n:
        v.name = n
    return v

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
    "endl": expose("\n"),

    "repr": expose(repr),
    "join": expose(lib.join),
    "range": expose(range),
    "type": expose(lib.typeof, "type"),

    "dir": expose(lib.dirof, "dir"),
    "attrs": expose(lib.attrsof, "attrs"),
    "reverse": expose(reversed),
    "sort": expose(sorted),
    "chr": expose(unichr),

    "Exception": expose(Exception),
})

stolen_builtins = [
    'abs', 'all', 'any', 'bool', 'callable', #buffer
    'cmp', #chr (not as unichr)
    'dict', 'divmod', 'enumerate', #delattr
    'exit', 'filter', # frozenset
    'hash', 'id', #get/hasattr
    'iter', 'len', 'list',
    'map', 'max', 'min', 'ord', # object
    'range', 'repr', #property
    'round', 'set', 'slice', #setattr
    'str', 'sum', 'unicode', #super
    'zip'
]

for i in stolen_builtins:
    builtin[i] = expose(__builtins__[i])
