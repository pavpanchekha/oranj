#!/usr/bin/env python

import sys
import decimal

class Inputable(object):
    def read(valid_f=None, coerce_f=None): pass

class Outputable(object):
    def write(*args): pass
    def error(*args): pass

class Terminal(Inputable, Outputable, object):
    def read(self, prompt="", valid_f=None, coerce_f=None):
        """
        Get user input, validate, and coerce it if necessary.

        prompt: User prompt
        valid_f: the validation function. Should throw exception if input is invalid
        coerce_f: the coersion function. Should return coerced value.

        If only one function is passed (valid_f is given, coerce_f is not),
        valid_f is assumed to return coerced value.
        """

        txt = raw_input(prompt)

        if valid_f is None and coerce_f is None:
            return txt
        elif coerce_f is None:
            try:
                return valid_f(txt)
            except:
                print "Invalid input; please try again."
                return input(prompt, valid_f, coerce_f)
        else:
            try:
                valid_f(txt)
            except:
                print "Invalid input; please try again."
                return input(prompt, valid_f, coerce_f)
            else:
                return coerce_f(txt)

    def write(self, *args, **kwargs):
        """
        Print *args to file standard output.

        @param sep: Separator between args. Default " "
        @type sep: C{str}
        @param end: Appended to string. Default "\n"
        @type end: C{str}
        """

        p = {
            "sep": " ",
            "end": "\n"
        }

        p.update(kwargs)

        f = sys.stdin
        sep = p["sep"]
        end = p["end"]

        sys.stdout.write(sep.join(map(str, args)))
        sys.stdout.write(str(end))

    def error(self, *args):
        sys.stderr.write("\n".join(map(repr, args)) + "\n")

term = Terminal()
input = term.read
output = term.write
error = term.error

def join(arr, s):
    return s.join(map(str, arr))

class Integer(long):
    def __init__(self, value):
        if type(value) == type(""):
            value = value.replace(" ", "")
        long.__init__(self, value)

    def __len__(self):
        return self

    def __iter__(self):
        return xrange(self).__iter__()
    
    def __str__(self):
        s = super(Integer, self).__str__()
        if s.endswith("L"):
            s = s[:-1]
        return s

defaults = decimal.getcontext()
defaults.prec = 28
defaults.rounding = decimal.ROUND_HALF_EVEN
defaults.capitals = 0

Infinity = decimal.Inf

class Decimal(decimal.Decimal):
    def __init__(self, value):
        if type(value) == type(""):
            value = value.replace(" ", "")
        decimal.Decimal.__init__(self, value)
    
    def __str__(self):
        s = super(Decimal, self).__str__()
        
        if "." not in s:
            if "e" not in s:
                ipart = s
                fpart = ""
                epart = ""
            else:
                ipart = s[:s.find("e")]
                fpart = ""
                epart = s[s.find("e"):]
        else:
            if "e" not in s:
                ipart = s[:s.find(".")]
                fpart = s[s.find("."):][:4]
                epart = ""
            else:
                ipart = s[:s.find(".")]
                fpart = s[s.find("."):s.find("e")][:5]
                epart = s[s.find("e"):]
        
        return ipart + fpart + epart
