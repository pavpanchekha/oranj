#!/usr/bin/env python
# -*- coding: utf-8 -*-

from objects.number import Number

def join(arr, s):
    return s.join(map(str, arr))

def toint(x): #int
    return Number(x, intonlystr=True)

def typeof(x): #type
    try:
        a = x.get("$$class")
    except AttributeError:
        return type(x.topy()).__name__
    else:
        if hasattr(a, "class_name"):
            return a.class_name
        else:
            return a.__name__

def dirof(x): #dir
    return x.dict