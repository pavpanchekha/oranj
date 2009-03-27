#!/usr/bin/env python

from objects.number import Number

def join(arr, s):
    return s.join(map(str, arr))

def toint(x):
    return int(Number(x)._val)
